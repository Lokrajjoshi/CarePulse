def recovery_summary(cases):
    eligible = 0; recovered = 0; times = []
    for case in cases:
        sentiments = [i.sentiment_ground_truth for i in sorted(case.interactions, key=lambda x: x.timestamp)]
        if "negative" in sentiments:
            eligible += 1
            first_negative = sentiments.index("negative")
            later = sentiments[first_negative + 1:]
            if any(s in {"neutral", "positive", "satisfied"} for s in later):
                recovered += 1
    return {"eligible_cases": eligible, "recovered_cases": recovered, "unrecovered_cases": eligible-recovered, "recovery_rate": round(recovered/eligible*100, 1) if eligible else 0}

