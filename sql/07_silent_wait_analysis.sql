SELECT CASE WHEN i.meaningful_update_flag=0 THEN 'waiting signal' ELSE 'updated' END AS state, COUNT(*) FROM interactions i GROUP BY state;

