from datetime import datetime, timedelta, timezone
from pathlib import Path
import os
import re
import sqlite3
import threading
import time
from collections import OrderedDict, deque

from flask import Flask, jsonify, render_template, request
import io
import base64
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from calculations import run_simulation

app = Flask(
    __name__,
    static_url_path="/ethyleneprediction/static"
)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PRIVACY_NOTICE_VERSION = "2026-10-01"
PRIVACY_RETENTION_DAYS = min(max(int(os.environ.get("PRIVACY_RETENTION_DAYS", "30")), 1), 90)
PRIVACY_STORAGE_ENABLED = os.environ.get("PRIVACY_STORAGE_MODE", "sqlite").strip().lower() == "sqlite"


def release_sha():
    configured = os.environ.get("APP_RELEASE_SHA", "").strip()
    if configured:
        return configured
    git_dir = Path(__file__).resolve().parent / ".git"
    try:
        head = (git_dir / "HEAD").read_text(encoding="utf-8").strip()
        if not head.startswith("ref: "):
            return head
        reference = head[5:]
        loose = git_dir / reference
        if loose.is_file():
            return loose.read_text(encoding="utf-8").strip()
        for line in (git_dir / "packed-refs").read_text(encoding="utf-8").splitlines():
            if line.endswith(f" {reference}"):
                return line.split(" ", 1)[0]
    except (OSError, ValueError):
        pass
    return "unknown"


class BoundedRateLimiter:
    def __init__(self, max_clients=2048):
        self.max_clients = max_clients
        self._clients = OrderedDict()
        self._lock = threading.Lock()

    def allow(self, key, limit=12, window_seconds=60):
        now = time.monotonic()
        with self._lock:
            events = self._clients.pop(key, deque())
            while events and now - events[0] >= window_seconds:
                events.popleft()
            allowed = len(events) < limit
            if allowed:
                events.append(now)
            self._clients[key] = events
            while len(self._clients) > self.max_clients:
                self._clients.popitem(last=False)
            return allowed


request_limiter = BoundedRateLimiter()


def request_client_key():
    """Return the client address appended by the directly connected proxy."""
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    if forwarded_for:
        return forwarded_for.rsplit(",", 1)[-1].strip() or "unknown"
    return request.remote_addr or "unknown"


@app.before_request
def enforce_rate_limit():
    if request.method != "POST":
        return None
    client = request_client_key()
    if request_limiter.allow(client):
        return None
    response = jsonify(error="Too many requests. Please wait briefly and try again.")
    response.status_code = 429
    response.headers["Retry-After"] = "60"
    return response


@app.after_request
def apply_security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    return response

def plot_to_base64(figure):
    buf = io.BytesIO()
    figure.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(figure)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

def record_privacy_acknowledgement(email):
    """Store one bounded, structured access decision; never use a plaintext log."""
    if not PRIVACY_STORAGE_ENABLED:
        return
    database = Path(os.environ.get("PRIVACY_DB_PATH", Path(app.instance_path) / "privacy.sqlite3"))
    database.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=PRIVACY_RETENTION_DAYS)
    with sqlite3.connect(database) as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS privacy_decisions ("
            "id INTEGER PRIMARY KEY, email TEXT NOT NULL, notice_version TEXT NOT NULL, "
            "purpose TEXT NOT NULL, acknowledged_at TEXT NOT NULL, withdrawn_at TEXT, expires_at TEXT NOT NULL)"
        )
        connection.execute("DELETE FROM privacy_decisions WHERE expires_at <= ?", (now.isoformat(),))
        connection.execute(
            "INSERT INTO privacy_decisions(email,notice_version,purpose,acknowledged_at,expires_at) "
            "VALUES (?,?,'analysis_access',?,?)",
            (email, PRIVACY_NOTICE_VERSION, now.isoformat(), expires_at.isoformat()),
        )
    try:
        database.chmod(0o600)
    except OSError:
        app.logger.warning("Could not restrict privacy database permissions: %s", database)

@app.route("/", methods=["GET", "POST"])
def index():
    # Default (empty) inputs
    fields = {
        "Wp": "",  # kg
        "StorageTemperature": "",
        "Perforationdiamicron": "",
        "NumberofPerfo": "",
        "mryan": "",
        "Vl": "",
        "Test_days": ""
    }

    errors = []
    plot1_b64 = None
    plot2_b64 = None
    extra_info = {}

    if request.method == "POST":
        # Reset action
        if "reset" in request.form:
            return render_template("index.html", fields=fields, errors=[], plot1_b64=None, plot2_b64=None,
                                   extra_info=extra_info, privacy_notice_version=PRIVACY_NOTICE_VERSION,
                                   privacy_retention_days=PRIVACY_RETENTION_DAYS,
                                   privacy_storage_enabled=PRIVACY_STORAGE_ENABLED)

        # Collect values
        try:
            collector_email = request.form.get("collector_email", "").strip()
            if len(collector_email) > 254 or not EMAIL_RE.fullmatch(collector_email):
                raise ValueError("A valid email address is required before updating plots.")
            if request.form.get("privacy_notice_ack") != "on" or request.form.get("privacy_notice_version") != PRIVACY_NOTICE_VERSION:
                raise ValueError("Please acknowledge the current privacy notice before running the analysis.")

            fields["Wp"] = request.form.get("Wp", "").strip()
            fields["StorageTemperature"] = request.form.get("StorageTemperature", "").strip()
            fields["Perforationdiamicron"] = request.form.get("Perforationdiamicron", "").strip()
            fields["NumberofPerfo"] = request.form.get("NumberofPerfo", "").strip()
            fields["mryan"] = request.form.get("mryan", "").strip()
            fields["Vl"] = request.form.get("Vl", "").strip()
            fields["Test_days"] = request.form.get("Test_days", "").strip()

            # Convert to floats (validation will happen in run_simulation too)
            params = {
                "Wp": float(fields["Wp"]),
                "StorageTemperature": float(fields["StorageTemperature"]),
                "Perforationdiamicron": float(fields["Perforationdiamicron"]),
                "NumberofPerfo": float(fields["NumberofPerfo"]),
                "mryan": float(fields["mryan"]),
                "Vl": float(fields["Vl"]),
                "Test_days": float(fields["Test_days"]),
            }

            result = run_simulation(params)
            errors = result.get("errors", [])

            if not errors:
                record_privacy_acknowledgement(collector_email)
                # Plot 1: O2 + CO2
                fig1 = plt.figure(figsize=(6, 4))
                ax1 = fig1.add_subplot(111)
                ax1.plot(result["TimesInDays"], result["Oxy_pct"], label="Predicted O₂")
                ax1.plot(result["TimesInDays"], result["CO2_pct"], label="Predicted CO₂")
                ax1.set_ylim(0, 24)
                ax1.set_xlim(0, result["xlim_days"])
                ax1.set_xlabel("Time, days")
                ax1.set_ylabel("O₂ and CO₂, %")
                ax1.legend(loc="upper right")
                ax1.set_facecolor("#DFF6FF")
                fig1.tight_layout()
                plot1_b64 = plot_to_base64(fig1)

                # Plot 2: Ethylene
                fig2 = plt.figure(figsize=(6, 4))
                ax3 = fig2.add_subplot(111)
                ax3.plot(result["TimesInDays"], result["FinalEthy_ppm"], label="Predicted C₂H₄")
                ax3.set_ylim(0, 5)
                ax3.set_xlim(0, result["xlim_days"])
                ax3.set_xlabel("Time, days")
                ax3.set_ylabel("C₂H₄, ppm")
                ax3.legend(loc="upper right")
                ax3.set_facecolor("#DFF6FF")
                fig2.tight_layout()
                plot2_b64 = plot_to_base64(fig2)                

        except ValueError as ve:
            errors = [str(ve)]
        except Exception:
            app.logger.exception("Unexpected simulation request failure")
            errors = ["Unexpected server error while running the simulation."]

    return render_template(
        "index.html",
        fields=fields,
        errors=errors,
        plot1_b64=plot1_b64,
        plot2_b64=plot2_b64,
        extra_info=extra_info,
        privacy_notice_version=PRIVACY_NOTICE_VERSION,
        privacy_retention_days=PRIVACY_RETENTION_DAYS,
        privacy_storage_enabled=PRIVACY_STORAGE_ENABLED,
    )


@app.get("/health")
def health():
    return jsonify(status="ok", release_sha=release_sha())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

