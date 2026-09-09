SELECT issue_category, COUNT(*) AS cases FROM cases GROUP BY issue_category ORDER BY cases DESC;

