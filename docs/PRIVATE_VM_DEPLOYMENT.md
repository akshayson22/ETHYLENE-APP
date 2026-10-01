# Private VM deployment

The private VM retains a localhost-only rollback copy. Its former public route returns 404 and it is not advertised in the research-applications portal. The PACK infrastructure repository owns that isolation, locked non-root container, five-minute Git update timer, local health verification, and rollback. The public stateless deployment is separately defined under `deploy/atb/`.

Push a reviewed fast-forward commit to `main`; no interactive VM login is required. The email access gate stores a versioned acknowledgement in SQLite for a bounded retention period (30 days by default, maximum 90). Configure `PRIVACY_DB_PATH` on persistent encrypted storage and `PRIVACY_RETENTION_DAYS`; do not use plaintext email logs. Contact: `contact@digifruitconsole.com`, Berlin, Germany.

Keep the public frontend factual and neutral. Do not add invented company, register, VAT, certification, affiliation, or postal-address details; publish verified legal-controller details only after review.
