import json
import re
from datetime import datetime, timedelta
from uuid import uuid4
from .models import Case, Event, Interaction, Promise
from .sentiment import classify

EVENT_TYPES = {"CASE_CREATED", "CUSTOMER_MESSAGE", "AGENT_MESSAGE", "MEANINGFUL_UPDATE", "PROMISE_MADE", "PROMISE_FULFILLED", "CASE_TRANSFERRED", "CASE_ESCALATED", "INTERVENTION_RECORDED", "STATUS_CHANGED", "CASE_RESOLVED", "CSAT_RECEIVED"}

def ingest_event(db, case: Case, event_type: str, event_timestamp: datetime, actor_type: str, message: str = "", metadata: dict | None = None, actor_id: str | None = None):
    if event_type not in EVENT_TYPES:
        raise ValueError(f"Unsupported event type: {event_type}")
    metadata = metadata or {}
    event = Event(event_id=f"EVT-{uuid4().hex[:10]}", case_id=case.case_id, event_type=event_type, event_timestamp=event_timestamp, actor_type=actor_type, actor_id=actor_id, message=message or None, metadata_json=json.dumps(metadata))
    db.add(event)
    if event_type in {"CUSTOMER_MESSAGE", "AGENT_MESSAGE", "MEANINGFUL_UPDATE"}:
        result = classify(message, metadata.get("channel", "chat"))
        db.add(Interaction(interaction_id=f"INT-{uuid4().hex[:10]}", case_id=case.case_id, timestamp=event_timestamp, interaction_type=event_type.lower(), actor_type=actor_type, message=message, sentiment_ground_truth=result["label"], sentiment_score=result["score"], meaningful_update_flag=event_type in {"AGENT_MESSAGE", "MEANINGFUL_UPDATE"}, transfer_flag=False, repeat_explanation_flag=False))
    if event_type == "CASE_TRANSFERRED":
        db.add(Interaction(interaction_id=f"INT-{uuid4().hex[:10]}", case_id=case.case_id, timestamp=event_timestamp, interaction_type="transfer", actor_type=actor_type, message="Case transferred", sentiment_ground_truth="neutral", sentiment_score=0, meaningful_update_flag=False, transfer_flag=True, repeat_explanation_flag=False))
    if event_type == "CASE_ESCALATED":
        case.escalation_flag = True
    if event_type == "CASE_RESOLVED":
        case.status = "Resolved"; case.resolved_at = event_timestamp
    if event_type == "PROMISE_MADE":
        deadline = metadata.get("promised_update_at")
        if deadline:
            promised = datetime.fromisoformat(deadline)
        else:
            promised = event_timestamp + timedelta(hours=2)
        db.add(Promise(promise_id=f"PRO-{uuid4().hex[:10]}", case_id=case.case_id, promise_created_at=event_timestamp, promised_update_at=promised, actual_update_at=None, promise_met=False))
    if event_type == "PROMISE_FULFILLED":
        promise = sorted(case.promises, key=lambda p: p.promise_created_at)[-1] if case.promises else None
        if promise:
            promise.actual_update_at = event_timestamp; promise.promise_met = event_timestamp <= promise.promised_update_at
    db.commit()
    return event
