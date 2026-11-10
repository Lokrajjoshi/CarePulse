# Environment variables

CarePulse reads deployment settings from environment variables. Keep real credentials and signing keys in the hosting platform's managed secret settings, never in source control.

Required production settings:

- `APP_ENV=production`
- `DATABASE_URL` set to the managed PostgreSQL connection string
- `SECRET_KEY` set to a unique random value of at least 32 characters

Optional:

- `SESSION_TTL_HOURS` (defaults to 8)

The built-in demo signing key is for local synthetic demo mode only and is rejected in production mode.
