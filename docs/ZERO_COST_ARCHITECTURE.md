# Zero-Cost Architecture

## Cost commitment

**TOTAL REQUIRED PROJECT COST: ₹0**

CarePulse can be built, tested, demonstrated, and explored locally without a payment card, cloud subscription, paid API, paid database, paid monitoring service, paid domain, or paid authentication provider.

## Completely free local components

- Python 3.11+ and the local virtual environment
- FastAPI, Uvicorn, SQLAlchemy, Jinja2, Pandas, scikit-learn, VADER, pytest, and openpyxl
- SQLite demo database
- Fixed-seed synthetic data generator
- Rule-based risk, effort, promise, recovery, and care-action logic
- Local sentiment baseline; no OpenAI, Anthropic, Gemini, or other LLM API
- Local browser UI, REST API, Swagger, Postman collection, and SQL files
- Java/Selenium/Maven assets, when the free open-source tools are installed locally

## Privacy and zero-cost intelligence

The baseline assistant is deterministic and grounded in CarePulse metrics. It does not call an external AI service. The sentiment baseline uses local rules and VADER. A real organization could run the same service inside its own private network and store derived signals rather than raw messages.

## Public deployment

No public deployment is claimed in this repository. A safe public demo should use synthetic data only. Free hosting providers and free-tier rules change frequently; many require sleep limits, usage limits, or a billing card. Do not activate billing merely to host CarePulse.

For a no-cost demonstration, use one of these safer approaches:

1. Run locally and screen-share the browser.
2. Share over the same trusted Wi-Fi network using the computer's private IP.
3. Use a temporary tunnel only after reviewing its current terms and ensuring no sensitive data is present.
4. Use a genuinely no-card free host only after checking its current policy yourself.

The application remains fully useful without a public URL.

## Azure status

Azure documentation is retained for future learning only. Azure App Service, Container Apps, PostgreSQL, Monitor, and Application Insights can create charges and are not required here. No Azure resource or billing activation was performed.

## What changes in production

Production deployment may introduce infrastructure cost for private hosting, managed PostgreSQL, monitoring, identity, storage, bandwidth, or a domain. Those are optional operational decisions and are outside the required ₹0 local project.

## Free-tier caveat

Free-tier availability, limits, and card requirements can change. Re-check the provider's current pricing and cancellation terms before deploying. Never place real customer data on an unapproved public free host.

