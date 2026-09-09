SELECT c.case_id, COUNT(i.interaction_id) AS interactions, SUM(CASE WHEN i.transfer_flag=1 THEN 1 ELSE 0 END) AS transfers FROM cases c JOIN interactions i ON i.case_id=c.case_id GROUP BY c.case_id;

