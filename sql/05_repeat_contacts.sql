SELECT c.channel, AVG(CASE WHEN f.repeat_contact_flag=1 THEN 1.0 ELSE 0.0 END)*100 AS repeat_contact_pct FROM cases c JOIN feedback f ON f.case_id=c.case_id GROUP BY c.channel;

