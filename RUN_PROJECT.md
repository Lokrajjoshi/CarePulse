# RUN_PROJECT.md

## A. Easy Demo Mode

One-time setup: open PowerShell and run:

```powershell
cd "C:\Users\Namraj Joshi\Desktop\CarePulse"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Every fresh demo reset (deliberate and destructive only to the local synthetic database):

```powershell
python scripts\reset_demo.py
```

Run tests:

```powershell
python -m pytest
```

Start the application:

```powershell
python -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`. Use `/dashboard`, `/story`, `/assistant`, `/simulator`, `/cases`, `/docs`, and a case link. Stop with `Ctrl+C`. The reload server must be started again after you close PowerShell. `START_CAREPULSE.ps1` automates dependency checks, database preparation, and launch without resetting records. `RESET_DEMO.ps1` deliberately regenerates the fixed-seed demo data.

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process Bypass` in that window. If `ModuleNotFoundError` appears, activate `.venv` and rerun the install command. If port 8000 is busy, use `python -m uvicorn app.main:app --reload --port 8001`.

## B. PostgreSQL Mode

Install PostgreSQL 14+ and create a database, for example `carepulse`. Copy `.env.example` to `.env` and set `DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/carepulse` after installing a PostgreSQL driver such as `psycopg[binary]`. Run `python scripts\initialise_database.py`, then `python scripts\reset_demo.py`, then start Uvicorn. `/health` verifies the API; a successful page load verifies the database connection.

## C. Power BI

Power BI Desktop is optional. Start with the CSV exports in `data\exports` and follow `powerbi\POWERBI_SETUP_GUIDE.md`. The supplied model, DAX, Power Query notes, and dashboard specification are intentionally text assets; no genuine `.pbix` is claimed.

## D. Selenium

Install Java 17+, Maven, and Chrome. Start CarePulse first. From `selenium-tests`, run `mvn test`. Tests use Selenium Manager where supported, so a separate driver is normally unnecessary. See `selenium-tests\README.md`.

## E. Postman

Install Postman, import `postman\CarePulse.postman_collection.json`, set `baseUrl` to `http://127.0.0.1:8000`, and send the health, metrics, case, risk, recommendation, assistant, and event requests.

## F. Azure / Cloud

Cloud deployment is optional and needs an Azure account, Azure Database for PostgreSQL, an App Service or Container Apps resource, and secrets configured as environment variables. Local SQLite demo mode does not depend on Azure. Read `cloud\azure\DEPLOYMENT_GUIDE.md`.

## G. GitHub and future changes

GitHub is source control, not hosting by itself. Commit the project, push it to a private or public repository, and use branches for later changes. Never commit `.env`, `.venv`, `*.db`, or real customer conversations; the included `.gitignore` excludes the local database and environment secrets. See `docs\GITHUB_DEPLOYMENT.md`.
