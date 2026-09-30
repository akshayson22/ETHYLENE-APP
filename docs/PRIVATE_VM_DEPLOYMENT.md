# Private VM deployment

The production application is served at `https://digifruitconsole.com/researchapplications/ethyleneprediction/`. The PACK infrastructure repository owns its Nginx route, locked non-root container, five-minute Git update timer, health verification, and rollback. This repository owns only application code and locked dependencies.

Push a reviewed fast-forward commit to `main`; no interactive VM login is required. Secrets are not required by this application, and email-gate records remain disabled with `EMAIL_LOG_PATH=/dev/null`. Contact: `contact@digifruitconsole.com`, Berlin, Germany.
