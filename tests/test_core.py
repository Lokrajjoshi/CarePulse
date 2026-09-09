from datetime import datetime, timedelta
from src.metrics import minutes_between
from src.sentiment import classify

def test_minutes_between():
    start=datetime(2025,1,1); assert minutes_between(start,start+timedelta(minutes=42))==42.0

def test_sentiment_demo():
    assert classify("Thank you for explaining what happened. That helps.")["label"] == "positive"
    assert classify("I have contacted you three times and still no update.")["label"] == "negative"
    assert classify("Hmm, okay")["label"] == "neutral"
