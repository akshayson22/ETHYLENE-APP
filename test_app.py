from __future__ import annotations

import math

import pytest

import app as webapp
from calculations import run_simulation


VALID_FORM = {
    "collector_email": "researcher@example.org",
    "privacy_notice_ack": "on",
    "privacy_notice_version": "2026-10-01",
    "Wp": "1",
    "StorageTemperature": "5",
    "Perforationdiamicron": "100",
    "NumberofPerfo": "2",
    "mryan": "1",
    "Vl": "2",
    "Test_days": "0.001",
}


def test_scientific_regression_contract():
    result = run_simulation({key: float(value) for key, value in VALID_FORM.items()
                             if key not in {"collector_email", "privacy_notice_ack", "privacy_notice_version"}})
    assert result["errors"] == []
    assert len(result["TimesInDays"]) == 87
    assert float(result["Oxy_pct"][-1]) == pytest.approx(20.8322469399)
    assert float(result["CO2_pct"][-1]) == pytest.approx(0.0575773996)
    assert float(result["FinalEthy_ppm"][-1]) == pytest.approx(0.0067764988)
    assert math.isfinite(result["qryanmax_ppm"])


def test_health_route_and_security_headers(monkeypatch):
    monkeypatch.setenv("APP_RELEASE_SHA", "ethylene-test-release")
    response = webapp.app.test_client().get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "release_sha": "ethylene-test-release"}
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "SAMEORIGIN"


def test_valid_request_records_bounded_privacy_decision(tmp_path, monkeypatch):
    database = tmp_path / "privacy.sqlite3"
    monkeypatch.setenv("PRIVACY_DB_PATH", str(database))
    response = webapp.app.test_client().post("/", data=VALID_FORM)
    assert response.status_code == 200
    assert b"data:image/png;base64" in response.data
    import sqlite3
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT email, notice_version, purpose FROM privacy_decisions").fetchone() == (
            "researcher@example.org", "2026-10-01", "analysis_access")


def test_invalid_request_does_not_log_email(tmp_path, monkeypatch):
    database = tmp_path / "privacy.sqlite3"
    monkeypatch.setenv("PRIVACY_DB_PATH", str(database))
    invalid = dict(VALID_FORM, collector_email="not-an-email", Wp="invalid")
    response = webapp.app.test_client().post("/", data=invalid)
    assert response.status_code == 200
    assert b"valid email address" in response.data
    assert not database.exists()


def test_privacy_notice_is_required(tmp_path, monkeypatch):
    database = tmp_path / "privacy.sqlite3"
    monkeypatch.setenv("PRIVACY_DB_PATH", str(database))
    form = dict(VALID_FORM)
    form.pop("privacy_notice_ack")
    response = webapp.app.test_client().post("/", data=form)
    assert response.status_code == 200
    assert b"acknowledge the current privacy notice" in response.data
    assert not database.exists()


def test_body_and_rate_limits(monkeypatch):
    monkeypatch.setattr(webapp, "request_limiter", webapp.BoundedRateLimiter(max_clients=4))
    client = webapp.app.test_client()
    oversized = client.post("/", data=b"x" * (webapp.app.config["MAX_CONTENT_LENGTH"] + 1))
    assert oversized.status_code == 413
    for _ in range(11):
        assert client.post("/", data={"collector_email": "bad"}).status_code == 200
    limited = client.post("/", data={"collector_email": "bad"})
    assert limited.status_code == 429
    assert limited.headers["Retry-After"] == "60"


def test_rate_limit_uses_proxy_appended_client_address(monkeypatch):
    monkeypatch.setattr(webapp, "request_limiter", webapp.BoundedRateLimiter(max_clients=4))
    client = webapp.app.test_client()
    first_client = {"X-Forwarded-For": "spoofed, 198.51.100.10"}
    for _ in range(12):
        assert client.post("/", data={}, headers=first_client).status_code == 200
    assert client.post("/", data={}, headers=first_client).status_code == 429
    assert client.post(
        "/", data={}, headers={"X-Forwarded-For": "spoofed, 198.51.100.11"}
    ).status_code == 200


def test_route_contract():
    routes = sorted(
        (rule.rule, tuple(sorted(rule.methods - {"HEAD", "OPTIONS"})))
        for rule in webapp.app.url_map.iter_rules()
        if rule.endpoint != "static"
    )
    assert routes == [("/", ("GET", "POST")), ("/health", ("GET",))]
