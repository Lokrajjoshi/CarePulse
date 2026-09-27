def business_recommendations(cases):
    total = len(cases)
    denominator = total or 1
    missed = [c for c in cases if any(not p.promise_met for p in c.promises)]
    transferred = [c for c in cases if sum(i.transfer_flag for i in c.interactions) >= 2]
    evidence = "Strong pattern" if total >= 100 else "Directional pattern" if total >= 30 else "Early signal"
    return [
        {"observation": f"{len(missed)/denominator*100:.1f}% of cases include a missed promise.", "impact": "Missed commitments are a visible trust and communication risk.", "action": "Review promise-setting and proactive update workflows.", "cases_affected": len(missed), "sample_size": total, "evidence": evidence, "measure": "Promise reliability and DSAT"},
        {"observation": f"{len(transferred)/denominator*100:.1f}% of cases have two or more transfers.", "impact": "Handoffs can increase customer effort and repeated explanation.", "action": "Investigate routing and ownership rules for high-transfer categories.", "cases_affected": len(transferred), "sample_size": total, "evidence": evidence, "measure": "Customer effort and repeat contact"},
    ]
