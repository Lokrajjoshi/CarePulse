SELECT c.case_id, c.issue_category, f.csat_score FROM cases c JOIN feedback f ON f.case_id=c.case_id WHERE f.dsat_flag=1 ORDER BY f.csat_score;

