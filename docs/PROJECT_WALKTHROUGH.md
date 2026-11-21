# CarePulse Project Walkthrough

## What problem CarePulse addresses

Support cases can be technically resolved while the customer still has a poor journey. Common causes are long silent waits, handoffs between teams, missed commitments, unclear ownership, and recovery actions that are not followed through.

CarePulse is a working prototype for making those operational signals visible so a support team can decide what to review next.

## A simple demonstration flow

### 1. Start with the executive dashboard

Use the dashboard to identify the cases that need attention and to see how the overall workload is changing. The aim is not only to show a number, but to help a manager decide where to look first.

### 2. Open the risk monitor

The risk monitor puts the highest-priority journeys first. Review the visible signals beside a case rather than treating the risk band as a final answer.

A useful explanation is:

> This case is highlighted because its recorded history contains operational warning signals. The signals help the team review the journey; they do not prove how a customer feels.

### 3. Inspect a case journey

In the case view, follow the sequence of interactions, promises, ownership, resolution status, and recovery actions. This makes it possible to discuss whether a case has moved smoothly or whether it has been waiting, transferred, or left without a clear next step.

### 4. Use the agent workspace

An agent can record a recovery action, its owner, its status, outcome, and follow-up note. This turns a risk signal into an accountable action instead of leaving it only on a dashboard.

### 5. Review controls as an administrator

The administrator can adjust risk thresholds for the demonstration organisation. This shows that operational rules should be reviewable rather than hidden inside the code.

## What the prototype demonstrates

- A Python FastAPI application with Jinja pages and SQLAlchemy data access.
- Separate views for customer, agent, manager, and administrator workflows.
- Explainable operational signals for waiting, commitments, recovery, and case risk.
- Event validation that protects the case timeline and service metrics from impossible or duplicate records.
- A local SQLite demo and PostgreSQL-compatible configuration.

## Important boundary

CarePulse uses fixed synthetic records for demonstration and learning. It is not a live service, and its data must not be presented as evidence about real customers. The signal rules support human review; they do not diagnose a customer's feelings or replace a support professional's judgement.

## How to explain CarePulse in an interview

> CarePulse is a customer-experience support prototype. I designed it around a practical issue: a ticket can be resolved technically but still become a poor customer journey because of waiting, handoffs, unclear ownership, or broken commitments. The application makes those operational signals visible, lets a team review the case history, and records accountable recovery actions. I kept the demo data synthetic and separated the prototype from research evidence so the limits of the system stay clear.
