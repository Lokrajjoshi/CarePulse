from datetime import datetime, timedelta
from pathlib import Path
import random
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sqlalchemy import delete
from src.database import Base, SessionLocal, engine
from src.models import Customer, Agent, Case, Interaction, Promise, Intervention, Feedback, Event

random.seed(42)
Base.metadata.create_all(engine)
session = SessionLocal()
for table in [Event, Interaction, Promise, Intervention, Feedback, Case, Customer, Agent]:
    session.execute(delete(table))
session.commit()
industries = ["Technical Support", "SaaS / Cloud Services", "Banking", "Telecom", "E-commerce", "Retail", "Subscription Services", "General Customer Service"]
channels = ["Email", "Chat", "Phone", "Web"]
issues = ["Technical Issue", "Service Outage", "Account Access", "Billing", "Payment", "Refund", "Delivery Delay", "Subscription", "Product Problem", "General Support", "Cancellation Request", "Service Complaint"]
positive = ["Thanks for keeping me updated.", "Thank you for explaining what happened. That helps."]
neutral = ["Can you confirm when this will be completed?", "Please share the next step."]
negative = ["I have contacted you three times and still have no update.", "I have been waiting since morning and nobody has updated me."]
base = datetime.utcnow() - timedelta(days=180)
for n in range(1, 3001):
    cid, case_id = f"CUS-{n:05d}", f"CP-{n:05d}"
    created = base + timedelta(minutes=random.randint(0, 180*24*60))
    friction = random.random() < .30
    wait = random.randint(10, 360) if friction else random.randint(5, 70)
    transfers = random.randint(0, 3) if friction else random.randint(0, 1)
    repeat = friction and random.random() < .65
    missed = friction and random.random() < .58
    first = created + timedelta(minutes=random.randint(5, 40) if not friction else random.randint(20, 180))
    resolved = created + timedelta(minutes=random.randint(90, 700) if not friction else random.randint(300, 2400))
    session.add(Customer(customer_id=cid, customer_segment=random.choice(["Consumer", "SMB", "Enterprise"]), region=random.choice(["North", "South", "East", "West"]), created_at=created))
    session.add(Case(case_id=case_id, customer_id=cid, industry=random.choice(industries), channel=random.choice(channels), issue_category=random.choice(issues), priority=random.choice(["Low", "Normal", "High", "Urgent"]), created_at=created, first_response_at=first, resolved_at=resolved, status=random.choice(["Resolved", "Resolved", "In Progress"]), escalation_flag=friction and random.random() < .35, current_owner=f"Agent-{random.randint(1, 12):02d}"))
    sentiments = ["neutral", "negative", "positive"] if friction and random.random() < .55 else ["neutral", "positive"]
    for j, sent in enumerate(sentiments):
        ts = created + timedelta(minutes=(j + 1) * wait // 2)
        msg = random.choice(negative if sent == "negative" else positive if sent == "positive" else neutral)
        session.add(Interaction(interaction_id=f"INT-{n:05d}-{j}", case_id=case_id, timestamp=ts, interaction_type="message", actor_type="customer" if j != 2 else "agent", message=msg, sentiment_ground_truth=sent, sentiment_score={"negative": -.7, "neutral": 0.0, "positive": .8}[sent], meaningful_update_flag=(j == 2), transfer_flag=(j > 0 and j <= transfers), repeat_explanation_flag=(j == 1 and transfers > 1)))
    promised = created + timedelta(minutes=wait)
    actual = promised - timedelta(minutes=10) if not missed else promised + timedelta(minutes=random.randint(15, 180))
    session.add(Promise(promise_id=f"PRO-{n:05d}", case_id=case_id, promise_created_at=created, promised_update_at=promised, actual_update_at=actual, promise_met=not missed))
    if friction or random.random() < .3:
        session.add(Intervention(intervention_id=f"ACT-{n:05d}", case_id=case_id, intervention_type=random.choice(["proactive update", "clear ETA", "specialist ownership", "callback", "escalation"]), intervention_at=created + timedelta(minutes=max(15, wait // 2)), reason="synthetic recovery workflow", accepted_flag=random.random() < .8))
    csat = max(1, min(5, int(round(4.5 - wait / 180 - transfers * .35 - (1.0 if missed else 0) + random.uniform(-.7, .7)))))
    session.add(Feedback(feedback_id=f"FDB-{n:05d}", case_id=case_id, csat_score=csat, dsat_flag=csat <= 2, recommendation_score=max(0, min(10, csat * 2 + random.randint(-2, 2))), final_sentiment=sentiments[-1], repeat_contact_flag=repeat))
    if n % 250 == 0:
        session.commit()
session.commit()
for i in range(1, 13):
    session.add(Agent(agent_id=f"Agent-{i:02d}", team=random.choice(["Core Support", "Billing", "Technical"]), experience_band=random.choice(["Developing", "Experienced", "Senior"])))
session.commit()
print("Generated 3,000 synthetic cases in SQLite.")
