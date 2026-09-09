# DAX measures

```DAX
Total Cases = DISTINCTCOUNT(Cases[case_id])
Average CSAT = AVERAGE(Feedback[csat_score])
DSAT % = DIVIDE(CALCULATE(COUNTROWS(Feedback), Feedback[dsat_flag] = TRUE()), COUNTROWS(Feedback))
Promise Reliability = DIVIDE(CALCULATE(COUNTROWS(Promises), Promises[promise_met] = TRUE()), COUNTROWS(Promises))
Repeat Contact Rate = DIVIDE(CALCULATE(COUNTROWS(Feedback), Feedback[repeat_contact_flag] = TRUE()), COUNTROWS(Feedback))
Escalation Rate = DIVIDE(CALCULATE(COUNTROWS(Cases), Cases[escalation_flag] = TRUE()), [Total Cases])
```

Add average response/resolution/silent-wait columns from the exported analytics view or calculate them in Power Query. Format percentages as percentages, not decimal scores.

