# CarePulse

CarePulse is a synthetic, industry-neutral customer-experience intervention prototype. It asks three questions: what is happening to the customer, what is happening right now, and what should the business improve?

## What is included

- FastAPI backend with SQLite demo mode and PostgreSQL-compatible SQLAlchemy configuration.
- Jinja customer, agent, case explorer, and executive dashboard pages.
- 3,000 fixed-seed synthetic cases across eight industries, with interactions, sentiment journeys, promises, interventions, and feedback.
- Explainable silent-wait, customer-effort, experience-risk, recovery, and next-best-care calculations.
- Offline CX Intelligence Assistant, sentiment signal workflow, and event-driven Integration Simulator.
- Signed demo login with Admin, CX Manager, Business Manager, Agent, and Customer roles.
- Organisation-scoped records, configurable risk thresholds, audit events, friendly error states, tracked recovery actions, and CI checks.
- SQL learning queries, analytics exports, Power BI model/DAX/setup assets, Postman collection, Java/Selenium starter suite, and architecture notes.

## Quick setup

```powershell
cd CarePulse
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts\reset_demo.py
python -m pytest
python -m uvicorn app.main:app --reload
```

After the server starts successfully, open the local address shown in the terminal. Full beginner instructions are in `RUN_PROJECT.md`.

## Demo access

CarePulse includes synthetic demo accounts for the main roles. Login details and local demo instructions are documented in `RUN_PROJECT.md`. These accounts only access synthetic data and must not be used for real customer information.

The Admin role can open **Organisation settings** and adjust the medium and high risk thresholds. The Agent workspace records recovery actions with owner, status, outcome, and follow-up notes.

## Production-readiness status

CarePulse is a production-oriented foundation, not a claim that a production deployment is complete. It has signed sessions, role checks, tenant-scoped queries, validation, audit records, configurable thresholds, PostgreSQL-compatible SQLAlchemy configuration, reports, and automated tests.

Before handling real customer information, an organisation still needs managed PostgreSQL, a managed identity provider or hardened account lifecycle, encryption and key management, backups and restore drills, monitoring and alerting, rate limiting at the edge, webhook authentication, retention policy, security review, and validation against labelled conversations and survey outcomes.

Set `APP_ENV=production`, provide a long random `SECRET_KEY`, and set `DATABASE_URL` to the managed PostgreSQL connection string. Never commit these values.

## Important limitations

The data is synthetic and deliberately patterned for learning. Associations are not causal evidence. VADER is a lightweight demonstration, not a reliable measure of emotion. The production-style recommendation remains rule-based. No `.pbix` file is fabricated; build instructions and exports are in `powerbi/`. In `APP_ENV=demo`, reviewers can browse the synthetic workspace without signing in; login and role enforcement remain enabled for `APP_ENV=production`.

## Architecture

Browser -> FastAPI/Jinja -> SQLAlchemy -> SQLite or PostgreSQL. Analytics modules consume the same relational records. See `docs/ARCHITECTURE.md`.

## Zero-cost baseline

The complete local project runs for free with Python, FastAPI, SQLite, and open-source libraries. It does not require an external model or paid API. See `docs/ZERO_COST_ARCHITECTURE.md` and `docs/PUBLIC_DEMO.md`.

## Metrics and security notes

The calculations used by pages, APIs, and reports live in `src/metrics.py`, `src/risk_engine.py`, and `src/analytics.py`. Risk bands use organisation thresholds, while the Assistant is bounded to CarePulse records and returns unsupported-question responses instead of inventing facts. Audit records do not store passwords or message contents.
