from .metrics import silent_wait_minutes

def next_best_actions(case):
    actions = []
    if silent_wait_minutes(case) > 60:
        actions.append({"action": "Provide a proactive status update", "why": "The case has a long period without a meaningful update."})
    if any(not p.promise_met for p in case.promises):
        actions.append({"action": "Acknowledge the missed commitment and set a realistic new ETA", "why": "A promised update was missed."})
    if sum(i.transfer_flag for i in case.interactions) >= 2:
        actions.append({"action": "Establish clear case ownership", "why": "Multiple transfers increase effort and repeated explanation."})
    if case.feedback and case.feedback.final_sentiment == "negative":
        actions.append({"action": "Confirm understanding and clarify next steps", "why": "The latest synthetic sentiment signal is negative."})
    if not actions:
        actions.append({"action": "Maintain ownership and provide the next update on schedule", "why": "No dominant friction signal requires escalation."})
    return actions

