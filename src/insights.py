def business_recommendations(cases):
    total = len(cases) or 1
    missed = [c for c in cases if any(not p.promise_met for p in c.promises)]
    transferred = [c for c in cases if sum(i.transfer_flag for i in c.interactions) >= 2]
    return [
        {"observation": f"{len(missed)/total*100:.1f}% of cases include a missed promise.", "impact": "Missed commitments are a visible trust and communication risk.", "action": "Review promise-setting and proactive update workflows."},
        {"observation": f"{len(transferred)/total*100:.1f}% of cases have two or more transfers.", "impact": "Handoffs can increase customer effort and repeated explanation.", "action": "Investigate routing and ownership rules for high-transfer categories."},
    ]

