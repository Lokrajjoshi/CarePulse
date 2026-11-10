# Security notes

CarePulse includes signed session authentication, role-based access checks, organisation-scoped queries, secure production cookie flags, and automated security-focused regression tests.

It is still a production-oriented prototype rather than a completed production deployment. Use HTTPS, private database networking, managed secret settings, least privilege, dependency updates, input validation, backups, monitoring, rate limiting, and an external security review before handling real customer information.

Production mode must use a unique signing key supplied through `SECRET_KEY`; the built-in demo key is rejected when `APP_ENV=production`.
