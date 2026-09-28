# Deployment and rollback

`main` is the only release branch. GitHub Actions are intentionally not used. PACK infrastructure owns Nginx, systemd, credentials, and host data.

Before release, run compilation, Ruff, all tests and coverage, dependency audit, and desktop/mobile smoke checks. Confirm no email log, credential, generated plot, or cache is tracked. Record the current VM SHA.

Fast-forward `/srv/apps/ethyleneprediction` to the exact reviewed SHA, install `requirements.lock` with hashes, restart only `ethyleneprediction.service`, and confirm `http://127.0.0.1:8002/health` and `https://pack.atb-potsdam.de/ethyleneprediction/health` return `status=ok` and the exact SHA.

On failure, preserve bounded redacted logs, restore the previous SHA and its locked dependencies, restart the same service, and repeat both checks. Never delete or rewrite the production email log.
