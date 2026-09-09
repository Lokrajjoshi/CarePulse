from .care_actions import next_best_actions
from .metrics import customer_effort, silent_wait_minutes
from .risk_engine import experience_risk

SUPPORTED = ("why", "risk", "high risk", "action", "what should", "silent wait", "effort", "recommendation", "summary", "dsat")

def answer(query: str, case=None, overview_data=None):
    q = query.lower().strip()
    if not any(term in q for term in SUPPORTED):
        return {"supported": False, "answer": "I can only answer questions grounded in CarePulse intelligence, such as risk drivers, silent wait, customer effort, recommendations, DSAT patterns, or case summaries."}
    if case is not None:
        risk = experience_risk(case)
        if "why" in q or "risk" in q:
            drivers = ", ".join(f"{d['name']} (+{d['points']})" for d in risk["drivers"]) or "no dominant driver"
            return {"supported": True, "answer": f"{case.case_id} is {risk['band']} risk at {risk['score']}/100. Main drivers: {drivers}.", "evidence": risk["drivers"]}
        if "action" in q or "what should" in q or "recommend" in q:
            action = next_best_actions(case)[0]
            return {"supported": True, "answer": f"Recommended action: {action['action']}. Why: {action['why']}", "evidence": [action]}
        if "silent" in q or "wait" in q:
            return {"supported": True, "answer": f"The calculated Silent Wait for {case.case_id} is {silent_wait_minutes(case)} minutes. This is the longest interval without a meaningful update.", "evidence": [{"silent_wait_minutes": silent_wait_minutes(case)}]}
        if "effort" in q:
            return {"supported": True, "answer": f"The CarePulse Customer Effort Indicator is {customer_effort(case)} out of 20, based on transfers, repeat contact, missed promises, repeated explanation, and silent wait.", "evidence": [{"customer_effort": customer_effort(case)}]}
        return {"supported": True, "answer": f"{case.case_id} is {case.status}, owned by {case.current_owner}, with {len(case.interactions)} recorded interactions and {len(case.promises)} promise records."}
    if overview_data is not None:
        return {"supported": True, "answer": f"The current CarePulse dataset contains {overview_data['total_cases']} cases, average CSAT {overview_data['csat']}, DSAT {overview_data['dsat_pct']}%, and {overview_data['high_risk_cases']} high-risk cases."}
    return {"supported": False, "answer": "No CarePulse case or dataset context was supplied for that question."}
