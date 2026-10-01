# Deployment and rollback

`main` is the only release branch. GitHub Actions are intentionally not used. The ATB deployment profile owns the application service definition; shared Nginx, certificates, accounts, monitoring, and unrelated services remain outside this application's release scope.

Before release, run compilation, Ruff, all tests and coverage, dependency audit, and desktop/mobile smoke checks. Confirm no email log, credential, generated plot, or cache is tracked. Record the current VM SHA.

The ATB operator fast-forwards `/srv/apps/ethyleneprediction` to the reviewed `main` SHA, installs `requirements.lock` with hashes, restarts only `ethyleneprediction.service`, and confirms the local health endpoint and `https://pack.atb-potsdam.de/ethyleneprediction/` are healthy.

On failure, preserve bounded redacted logs, restore the previous SHA and its locked dependencies, restart the same service, and repeat both checks. The ATB profile is stateless and must not create an application database, upload store, or email log.
