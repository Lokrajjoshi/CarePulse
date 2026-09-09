# Deployment guide

Create an Azure resource group, PostgreSQL Flexible Server, and App Service or Container App. Set `DATABASE_URL` and `APP_ENV` as application settings. Deploy from a Git repository or container, run `python scripts/initialise_database.py`, and verify `/health`. A subscription and network/security configuration are required; no cloud deployment was performed for this local prototype.

