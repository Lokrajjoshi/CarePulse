from dataclasses import dataclass
from datetime import date, datetime, timedelta

from .metrics import customer_effort, first_response_minutes, resolution_minutes, silent_wait_minutes
from .recovery import recovery_summary
from .risk_engine import experience_risk


@dataclass(frozen=True)
class Filters:
    days: int = 90
    industry: str = ""
    channel: str = ""
    issue: str = ""
    priority: str = ""
    agent: str = ""
    team: str = ""
    risk: str = ""
    sentiment: str = ""
    start: str = ""
    end: str = ""

    @classmethod
    def from_query(cls, **values):
        try:
            days = max(1, min(int(values.get("days") or 90), 3650))
        except (TypeError, ValueError):
            days = 90
        return cls(days=days, **{key: (values.get(key) or "") for key in ("industry", "channel", "issue", "priority", "agent", "team", "risk", "sentiment", "start", "end")})

    def label(self):
        parts = [f"Last {self.days} days"]
        for key in ("industry", "channel", "issue", "priority", "agent", "team", "risk", "sentiment"):
            if getattr(self, key):
                parts.append(f"{key.title()}: {getattr(self, key)}")
        return " | ".join(parts)


def apply_filters(cases, filters: Filters, agents=None):
    agents = agents or []
    team_by_agent = {a.agent_id: a.team for a in agents}
    today = date.today()
    start = today - timedelta(days=filters.days)
    end = today
    for attr, fallback in (("start", start), ("end", end)):
        value = getattr(filters, attr)
        if value:
            try:
                parsed = date.fromisoformat(value)
                if attr == "start": start = parsed
                else: end = parsed
            except ValueError:
                pass
    selected = []
    for case in cases:
        if not (start <= (case.created_at.date() if isinstance(case.created_at, datetime) else case.created_at) <= end): continue
        if filters.industry and case.industry != filters.industry: continue
        if filters.channel and case.channel != filters.channel: continue
        if filters.issue and case.issue_category != filters.issue: continue
        if filters.priority and case.priority != filters.priority: continue
        if filters.agent and case.current_owner != filters.agent: continue
        if filters.team and team_by_agent.get(case.current_owner) != filters.team: continue
        if filters.risk and experience_risk(case)["band"] != filters.risk: continue
        if filters.sentiment and (not case.feedback or case.feedback.final_sentiment != filters.sentiment): continue
        selected.append(case)
    return selected


def metrics_for_cases(cases):
    feedback = [c.feedback for c in cases if c.feedback]
    promises = [p for c in cases for p in c.promises]
    recovery = recovery_summary(cases)
    if not cases:
        return {"cases": 0, "csat": 0, "dsat_pct": 0, "nps": 0, "first_response": 0, "resolution": 0, "silent_wait": 0, "promise_reliability": 0, "repeat_contact": 0, "transfer_rate": 0, "effort": 0, "recovery_rate": 0, "high_risk": 0}
    return {"cases": len(cases), "csat": round(sum(f.csat_score for f in feedback) / len(feedback), 2) if feedback else 0, "dsat_pct": round(sum(f.dsat_flag for f in feedback) / len(feedback) * 100, 1) if feedback else 0, "nps": round(sum((f.recommendation_score >= 9) - (f.recommendation_score <= 6) for f in feedback) / len(feedback) * 100, 1) if feedback else 0, "first_response": round(sum(first_response_minutes(c) for c in cases) / len(cases), 1), "resolution": round(sum(resolution_minutes(c) for c in cases) / len(cases), 1), "silent_wait": round(sum(silent_wait_minutes(c) for c in cases) / len(cases), 1), "promise_reliability": round(sum(p.promise_met for p in promises) / len(promises) * 100, 1) if promises else 0, "repeat_contact": round(sum(bool(c.feedback and c.feedback.repeat_contact_flag) for c in cases) / len(cases) * 100, 1), "transfer_rate": round(sum(sum(i.transfer_flag for i in c.interactions) > 0 for c in cases) / len(cases) * 100, 1), "effort": round(sum(customer_effort(c) for c in cases) / len(cases), 1), "recovery_rate": recovery["recovery_rate"], "high_risk": sum(experience_risk(c)["band"] == "HIGH" for c in cases)}


def recommendations_for_cases(cases):
    total = len(cases) or 1
    missed = sum(any(not p.promise_met for p in c.promises) for c in cases)
    repeat = sum(bool(c.feedback and c.feedback.repeat_contact_flag) for c in cases)
    return [{"observation": f"{missed / total * 100:.1f}% of filtered cases include a missed promise.", "evidence": f"{missed} of {len(cases)} cases", "impact": "Missed commitments can increase uncertainty and repeat contact.", "action": "Review promise-setting and proactive update workflows.", "measure": "Promise Reliability, DSAT"}, {"observation": f"{repeat / total * 100:.1f}% of filtered cases include repeat contact.", "evidence": f"{repeat} of {len(cases)} cases", "impact": "Repeated contact adds customer effort and queue demand.", "action": "Investigate ownership, routing, and first-contact resolution for this slice.", "measure": "Repeat Contact, Customer Effort"}]


def agent_rows(cases, agents):
    by_id = {a.agent_id: a for a in agents}
    return [{"agent": agent_id, "team": by_id.get(agent_id).team if by_id.get(agent_id) else "Unassigned", "experience": by_id.get(agent_id).experience_band if by_id.get(agent_id) else "Unknown", **metrics_for_cases([c for c in cases if c.current_owner == agent_id])} for agent_id in sorted({c.current_owner for c in cases})]


def team_rows(cases, agents):
    by_id = {a.agent_id: a.team for a in agents}
    return [{"team": team, **metrics_for_cases([c for c in cases if by_id.get(c.current_owner, "Unassigned") == team])} for team in sorted({by_id.get(c.current_owner, "Unassigned") for c in cases})]


def monthly_rows(cases):
    groups = {}
    for case in cases:
        key = case.created_at.strftime("%Y-%m")
        groups.setdefault(key, []).append(case)
    return [{"period": period, **metrics_for_cases(groups[period])} for period in sorted(groups)]


def comparison_metrics(current, previous):
    now, before = metrics_for_cases(current), metrics_for_cases(previous)
    return {key: {"current": now[key], "previous": before[key], "delta": round(now[key] - before[key], 1) if isinstance(now[key], (int, float)) else None} for key in ("cases", "csat", "dsat_pct", "silent_wait", "promise_reliability", "repeat_contact", "recovery_rate")}
