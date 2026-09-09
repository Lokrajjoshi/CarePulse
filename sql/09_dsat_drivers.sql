SELECT c.issue_category, AVG(CASE WHEN f.dsat_flag=1 THEN 1.0 ELSE 0.0 END)*100 AS dsat_pct FROM cases c JOIN feedback f ON f.case_id=c.case_id GROUP BY c.issue_category ORDER BY dsat_pct DESC;

