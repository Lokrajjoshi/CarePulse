from datetime import datetime, timedelta
from types import SimpleNamespace

from src.metrics import minutes_between
from src.risk_engine import experience_risk
from src.sentiment import classify


def test_minutes_between():
    start=datetime(2025,1,1); assert minutes_between(start,start+timedelta(minutes=42))==42.0


def test_sentiment_demo():
    assert classify("Thank you for explaining what happened. That helps.")["label"] == "positive"
    assert classify("I have contacted you three times and still no update.")["label"] == "negative"
    assert classify("Hmm, okay")["label"] == "neutral"


def test_missed_promise_adds_explainable_risk():
    now = datetime(2026, 9, 29)
    case = SimpleNamespace(
        created_at=now,
        resolved_at=now,
        interactions=[],
        promises=[SimpleNamespace(promise_met=False)],
        feedback=None,
        escalation_flag=False,
    )

    risk = experience_risk(case)

    assert risk["score"] == 24
    assert {"name": "Missed promised update", "points": 24} in risk["drivers"]
