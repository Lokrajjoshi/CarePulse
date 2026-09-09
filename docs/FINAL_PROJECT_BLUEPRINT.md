# CarePulse Final Project Blueprint

## Project identity

**CarePulse: Customer Experience Intervention & Intelligence Platform**

CarePulse is an industry-neutral intelligence layer that sits beside a company's existing customer-support systems. It uses operational journey data to detect experience deterioration before a final CSAT or DSAT survey arrives, explain why the case is risky, recommend a transparent care action, and show management which processes deserve improvement.

CarePulse is not a replacement for a CRM, ticketing system, chat system, or survey platform. It is the analytical and intervention layer between those systems and the people who need to act on the experience.

## Why this project exists

Organizations often learn that a customer was unhappy only after the interaction is complete. The ticket may show a delay, but the business may not know which other cases are deteriorating, why the pattern is repeating, or which intervention is appropriate.

The project explores a practical question:

> Can operational signals identify a deteriorating customer experience early enough to support a better action and a better business decision?

## Who benefits

**Primary beneficiary: the organization.** It receives earlier visibility into process friction and can measure improvement.

**Operational beneficiary: the agent.** The agent receives prioritization, reasons, and next-best-care guidance instead of manually interpreting every signal alone.

**Experience beneficiary: the customer.** The customer may receive clearer ownership, proactive updates, realistic expectations, and fewer repeated explanations.

## What makes it different

An experienced agent can recognize that one case is delayed. CarePulse adds four capabilities around that human judgment:

1. **Prioritization:** compare many active cases and surface which need attention first.
2. **Explainability:** show the measurable drivers behind risk instead of a black-box label.
3. **Action:** recommend an appropriate service-recovery step and record the intervention.
4. **Learning:** aggregate many cases so the organization can investigate routing, promises, waiting, and repeat-contact processes.

## How it would work in an organization

```text
Chat / Email / Voice transcript / CRM / Survey system
                         |
                  Internal connector
                         |
              CarePulse private API/service
                         |
       Risk, sentiment, effort, promise and recovery logic
                         |
      Agent workspace / manager dashboard / Power BI / alerts
```

The customer or agent should not manually copy every interaction. A real deployment would use internal APIs, webhooks, scheduled exports, or event streams. Depending on privacy policy, the company could send metadata only, redacted text, or process the text locally and store only derived signals.

## What the prototype proves

The local reference version proves the product logic using synthetic data:

- 3,000 synthetic cases across multiple industries and channels
- SQLite demo database with PostgreSQL-compatible SQLAlchemy configuration
- FastAPI REST API and Swagger documentation
- Customer, agent, executive, journey, risk, sentiment, recovery, and analytics views
- Rule-based Experience Risk engine
- Transparent Customer Effort and Silent Wait formulas
- Local sentiment demonstration for chat, email text, and voice transcript text
- Business recommendations and experimental ML benchmark
- Postman, SQL, Power BI, Selenium, and Azure preparation assets

It does **not** claim to be connected to Dell or any real company. It does not use real customer data or external AI APIs.

## Technology summary

| Area | Technology | Why it is used |
|---|---|---|
| Backend | Python, FastAPI | REST API, validation, Swagger, web routes |
| Web UI | Jinja2, HTML, CSS | Understandable server-rendered enterprise interface |
| Database | SQLite demo, PostgreSQL target | Easy local learning plus production path |
| ORM | SQLAlchemy | Relational models and parameterized queries |
| Analytics | Pandas, Python | KPI calculations, exports, grouping, analysis |
| Sentiment | VADER plus business rules | Local, explainable sentiment demonstration |
| ML benchmark | scikit-learn Logistic Regression | Experimental DSAT comparison, not production authority |
| Testing | pytest | Python unit and API-oriented validation |
| API testing | Postman | Repeatable REST endpoint checks |
| UI automation | Java, Selenium, Maven, JUnit | Browser automation learning path |
| BI | Power BI-ready CSV, DAX, model docs | Management reporting preparation |
| Cloud | Azure architecture | App Service/Container Apps, PostgreSQL, monitoring |

## Core measures

- Silent Wait: longest interval without a meaningful update
- Promise Reliability: fulfilled commitments divided by all commitments
- Customer Effort: transparent combination of transfers, repeat explanation, repeat contact, missed promises, and waiting
- Experience Risk: explainable score with visible drivers and LOW/MEDIUM/HIGH bands
- Sentiment Journey: changes across messages, not only a final label
- Recovery: whether a negative journey later returns to neutral or positive

## Proper usage path

1. Connect approved events from existing support systems.
2. Minimize or redact sensitive fields.
3. Calculate journey signals while the case is active.
4. Prioritize cases for the agent.
5. Recommend and record a care action.
6. Compare the early signal with the later survey outcome.
7. Aggregate patterns for process investigation.
8. Measure whether the change improves promise reliability, effort, repeat contact, recovery, or DSAT.

## Production roadmap

**Phase 1: reference prototype.** Synthetic data, SQLite, explainable rules, local UI, tests, and documentation.

**Phase 2: private pilot.** One organization, approved metadata, internal connector, PostgreSQL, authentication, audit logs, human review, and shadow-mode evaluation.

**Phase 3: operational rollout.** Agent workflow integration, survey calibration, alerts, Power BI, monitoring, privacy review, and model-performance monitoring.

**Phase 4: scale.** Multiple teams or tenants, configurable policies, language support, drift monitoring, and governed intervention experiments.

## One-minute explanation

> CarePulse is a customer-experience intelligence layer for existing support systems. It looks at operational signals such as silent waiting, missed promises, repeat contact, transfers, and sentiment while a case is still active. It prioritizes which customers need attention, explains why, recommends a transparent recovery action, and compares the early signal with the later survey outcome. The prototype runs locally on synthetic data, while the production design supports private internal deployment and secure connectors rather than sending confidential conversations to a public AI tool.

