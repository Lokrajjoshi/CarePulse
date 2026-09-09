SELECT intervention_type, COUNT(*) AS actions, AVG(CASE WHEN accepted_flag=1 THEN 1.0 ELSE 0.0 END)*100 AS accepted_pct FROM interventions GROUP BY intervention_type;

