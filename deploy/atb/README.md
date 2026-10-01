# Stateless ATB deployment

This profile serves the application at `/ethyleneprediction/` while keeping all analysis request data in memory only. `PRIVACY_STORAGE_MODE=disabled` validates the access email and notice acknowledgement but does not write them to SQLite, logs, or another service. Nginx access logging is disabled for the route.

The service binds only to `127.0.0.1:8002`, runs without privileges, and receives writable temporary space only through systemd `PrivateTmp`. It must not receive a database volume, analytics integration, email exporter, or persistent upload directory.

Release procedure: fast-forward `main`, install `requirements.lock` with hashes into the existing virtual environment, restart only `ethyleneprediction.service`, verify `http://127.0.0.1:8002/health`, validate Nginx, and then verify the public route. Do not modify the host certificate, accounts, monitoring, or other applications.
