# CarePulse

CarePulse is a synthetic, industry-neutral customer-experience intervention prototype. It asks three questions: what is happening to the customer, what is happening right now, and what should the business improve?

## What is included

- FastAPI backend with SQLite demo mode and PostgreSQL-compatible SQLAlchemy configuration.
- Jinja customer, agent, case explorer, and executive dashboard pages.
- 3,000 fixed-seed synthetic cases across eight industries, with interactions, sentiment journeys, promises, interventions, and feedback.
- Explainable silent-wait, customer-effort, experience-risk, recovery, and next-best-care calculations.
- Offline CX Intelligence Assistant, sentiment signal workflow, and event-driven Integration Simulator.
- SQL learning queries, analytics exports, Power BI model/DAX/setup assets, Postman collection, Java/Selenium starter suite, and Azure architecture notes.

## Quick setup

```powershell
cd "C:\Users\Namraj Joshi\Desktop\CarePulse"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts\reset_demo.py
python -m pytest
python -m uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Full beginner instructions are in `RUN_PROJECT.md`.

## Important limitations

The data is synthetic and deliberately patterned for learning. Associations are not causal evidence. VADER is a lightweight demonstration, not a reliable measure of emotion. The production-style recommendation remains rule-based. No `.pbix` file is fabricated; build instructions and exports are in `powerbi/`.

## Architecture

Browser -> FastAPI/Jinja -> SQLAlchemy -> SQLite or PostgreSQL. Analytics modules consume the same relational records. See `docs/ARCHITECTURE.md`.

## Zero-cost baseline

The complete local project runs for free with Python, FastAPI, SQLite, and open-source libraries. It does not require an external LLM or paid API. See `docs/ZERO_COST_ARCHITECTURE.md` and `docs/PUBLIC_DEMO.md`.
