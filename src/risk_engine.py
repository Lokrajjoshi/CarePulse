from .metrics import customer_effort, silent_wait_minutes
from .tenant import risk_thresholds

def experience_risk(case):
    drivers = []
    score = 0
    wait = silent_wait_minutes(case)
    if wait > 120: score += 28; drivers.append(("Long silent wait", 28))
    elif wait > 60: score += 18; drivers.append(("Silent wait over one hour", 18))
    missed = sum(not p.promise_met for p in case.promises)
    if missed: score += 24; drivers.append(("Missed promised update", 24))
    transfers = sum(i.transfer_flag for i in case.interactions)
    if transfers >= 2: score += 14; drivers.append(("Multiple transfers", 14))
    repeat = bool(case.feedback and case.feedback.repeat_contact_flag)
    if repeat: score += 12; drivers.append(("Repeat customer contact", 12))
    if case.escalation_flag: score += 8; drivers.append(("Escalation", 8))
    if case.feedback and case.feedback.final_sentiment == "negative": score += 10; drivers.append(("Negative final sentiment", 10))
    effort = customer_effort(case)
    if effort >= 10: score += 10; drivers.append(("High customer effort", 10))
    score = min(score, 100)
    medium_threshold, high_threshold = risk_thresholds()
    band = "HIGH" if score >= high_threshold else "MEDIUM" if score >= medium_threshold else "LOW"
    return {"score": score, "band": band, "drivers": [{"name": n, "points": p} for n, p in sorted(drivers, key=lambda x: -x[1])]}
