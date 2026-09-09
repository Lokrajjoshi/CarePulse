import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

NEUTRAL_ACKS = {"ok", "okay", "k", "hmm", "hm", "right", "noted", "fine", "sure", "yes", "yep", "understood"}
NEGATIVE_CUES = ("still waiting", "no update", "again", "third time", "frustrated", "ridiculous", "unacceptable", "disappointed", "angry")
POSITIVE_CUES = ("thank you", "thanks", "helpful", "appreciate", "resolved", "that helps", "great")

def classify(message: str, source: str = "chat"):
    cleaned = " ".join(message.lower().strip().split())
    normalized_words = re.sub(r"[^a-z\s]", " ", cleaned).split()
    if cleaned in NEUTRAL_ACKS or (len(normalized_words) <= 3 and normalized_words and all(word in NEUTRAL_ACKS for word in normalized_words)):
        return {"label": "neutral", "score": 0.0, "confidence": 0.58, "explanation": "Short acknowledgement or hesitation; keep the case open for more context.", "source": source}
    if any(cue in cleaned for cue in NEGATIVE_CUES):
        return {"label": "negative", "score": -0.65, "confidence": 0.78, "explanation": "The message contains a frustration, delay, or repeat-contact cue.", "source": source}
    if any(cue in cleaned for cue in POSITIVE_CUES):
        return {"label": "positive", "score": 0.65, "confidence": 0.76, "explanation": "The message contains an appreciation, helpfulness, or resolution cue.", "source": source}
    score = analyzer.polarity_scores(message)["compound"]
    label = "positive" if score >= 0.2 else "negative" if score <= -0.2 else "neutral"
    return {"label": label, "score": score, "confidence": min(0.9, round(0.5 + abs(score) * 0.45, 2)), "explanation": "Local VADER lexical analysis; use the surrounding conversation and survey outcome as context.", "source": source}
