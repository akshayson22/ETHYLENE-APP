# Private VM deployment

The production application is served at `https://digifruitconsole.com/researchapplications/ethyleneprediction/`. The PACK infrastructure repository owns its Nginx route, locked non-root container, five-minute Git update timer, health verification, and rollback. This repository owns only application code and locked dependencies.

Push a reviewed fast-forward commit to `main`; no interactive VM login is required. The email access gate stores a versioned acknowledgement in SQLite for a bounded retention period (30 days by default, maximum 90). Configure `PRIVACY_DB_PATH` on persistent encrypted storage and `PRIVACY_RETENTION_DAYS`; do not use plaintext email logs. Contact: `contact@digifruitconsole.com`, Berlin, Germany.

Keep the public frontend factual and neutral. Do not add invented company, register, VAT, certification, affiliation, or postal-address details; publish verified legal-controller details only after review.
