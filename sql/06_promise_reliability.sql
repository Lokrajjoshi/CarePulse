SELECT AVG(CASE WHEN promise_met=1 THEN 1.0 ELSE 0.0 END)*100 AS promise_reliability_pct FROM promises;

