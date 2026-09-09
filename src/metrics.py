from datetime import datetime
from .models import Case

def minutes_between(start, end):
    return round(max(0, (end - start).total_seconds() / 60), 1) if start and end else 0

def first_response_minutes(case: Case):
    return minutes_between(case.created_at, case.first_response_at)

def resolution_minutes(case: Case):
    return minutes_between(case.created_at, case.resolved_at)

def silent_wait_minutes(case: Case):
    updates = [i.timestamp for i in case.interactions if i.meaningful_update_flag]
    if not updates:
        return resolution_minutes(case) or minutes_between(case.created_at, datetime.utcnow())
    end = case.resolved_at or max(i.timestamp for i in case.interactions)
    points = [case.created_at] + sorted(updates) + [end]
    return round(max((points[i+1] - points[i]).total_seconds() / 60 for i in range(len(points)-1)), 1)

def customer_effort(case: Case):
    transfers = sum(i.transfer_flag for i in case.interactions)
    repeats = sum(i.repeat_explanation_flag for i in case.interactions)
    repeat_contact = bool(case.feedback and case.feedback.repeat_contact_flag)
    missed = sum(not p.promise_met for p in case.promises)
    score = 1 + transfers * 2 + repeats * 2 + (3 if repeat_contact else 0) + missed * 3 + min(silent_wait_minutes(case) / 60, 8)
    return round(min(score, 20), 1)

