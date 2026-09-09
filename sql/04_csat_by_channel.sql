SELECT c.channel, AVG(f.csat_score) AS avg_csat FROM cases c JOIN feedback f ON f.case_id=c.case_id GROUP BY c.channel;

