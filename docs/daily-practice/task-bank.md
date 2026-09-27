# CarePulse Task Bank

Pick one small task per day. Each task should be possible in 10-15 minutes and should improve either the project, the explanation, or the understanding of the system.

## Product and business understanding

- Explain why missed follow-ups create customer risk.
- Add a short note about silent waiting time and why it matters.
- Describe how recovery actions help support teams close the loop.
- Improve the explanation of customer-effort and experience-risk signals.
- Add a short example of how a manager would use the dashboard.
- Write a simple interview answer for why CarePulse exists.

## Backend and data

- Read one FastAPI route and summarize what request it handles.
- Inspect a SQLAlchemy model and note what real-world object it represents.
- Add or improve a validation message for one form or API input.
- Review the demo reset script and explain what data it creates.
- Add a small test case for a risk or analytics helper.
- Document the difference between SQLite demo mode and PostgreSQL production setup.

## Analytics and risk logic

- Inspect `src/metrics.py` and explain one metric in plain language.
- Inspect `src/risk_engine.py` and note what raises customer risk.
- Inspect `src/analytics.py` and connect one calculation to a business question.
- Add one clear comment or documentation note for a complex calculation.
- Create one example case showing low, medium, and high risk behavior.

## User experience

- Improve one empty state or helper message on a dashboard page.
- Make one label clearer for a support or manager workflow.
- Check one page on a small screen and note any layout issue.
- Improve wording around recovery actions or follow-up ownership.
- Add a small documentation note for demo login behavior.

## Testing and tools

- Run or review a pytest check and explain what it protects.
- Review the Postman collection and note one API flow.
- Review the Java/Selenium starter suite and identify one browser action it tests.
- Add a short note about how Power BI exports support reporting.
- Add one production-readiness note about secrets, backups, monitoring, or access control.

## Suggested commit message style

- `Day N: explain customer recovery workflow`
- `Day N: improve risk signal notes`
- `Day N: clarify dashboard follow-up wording`
- `Day N: add analytics test note`
- `Day N: document demo data setup`
