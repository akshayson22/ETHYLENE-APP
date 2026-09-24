# Security policy

Do not commit credentials, email-provider secrets, production logs, or personal contact data. The
production service must run as an unprivileged systemd account on a loopback-only port behind the
PACK HTTPS reverse proxy, with upload limits and existing input validation retained.

Report suspected malicious uploads, credential exposure, or unauthorized access privately to the
repository owner without attaching sensitive samples or secret values. Host containment, rotation,
and rollback are governed by the PACK infrastructure repository.
