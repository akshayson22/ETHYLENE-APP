# Deployment and rollback

`main` is the only release branch. GitHub Actions are intentionally not used. PACK infrastructure owns Nginx, systemd, credentials, and host data.

Before release, run compilation, Ruff, all tests and coverage, dependency audit, and desktop/mobile smoke checks. Confirm no email log, credential, generated plot, or cache is tracked. Record the current VM SHA.

The PACK-owned VM updater fast-forwards `/srv/digifruit-platform/apps/ethylene` to the reviewed `main` SHA, builds from `requirements.lock` with hashes, replaces only the `ethylene` container, and confirms the local service and `https://digifruitconsole.com/researchapplications/ethyleneprediction/` are healthy.

On failure, preserve bounded redacted logs, restore the previous SHA and its locked dependencies, restart the same service, and repeat both checks. Never delete or rewrite the production email log.
