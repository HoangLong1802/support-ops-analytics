USE support_ops_verify_20261008_followup;
-- Counts must equal docs/cleaning_report.md; detail queries must return zero rows.
SELECT 'agents' AS dataset,COUNT(*) AS rows_loaded FROM dim_agents
UNION ALL SELECT 'sla_policies',COUNT(*) FROM dim_sla_policies
UNION ALL SELECT 'categories',COUNT(*) FROM dim_categories
UNION ALL SELECT 'dates',COUNT(*) FROM dim_date
UNION ALL SELECT 'tickets',COUNT(*) FROM fact_tickets
UNION ALL SELECT 'work_logs',COUNT(*) FROM fact_work_logs
UNION ALL SELECT 'workforce',COUNT(*) FROM fact_workforce_daily;

SELECT ticket_id FROM fact_tickets
WHERE first_response_at<created_at OR resolved_at<first_response_at
   OR first_response_at>'2026-09-30 17:00:00' OR resolved_at>'2026-09-30 17:00:00'
   OR (status IN ('open','pending') AND (resolved_at IS NOT NULL OR csat_score IS NOT NULL))
   OR (status IN ('resolved','closed') AND (assigned_agent_id IS NULL OR first_response_at IS NULL OR resolved_at IS NULL));

SELECT t.ticket_id FROM fact_tickets t JOIN dim_agents a ON a.agent_id=t.assigned_agent_id
WHERE t.local_created_date<a.hire_date;

SELECT l.work_log_id FROM fact_work_logs l
JOIN fact_tickets t ON t.ticket_id=l.ticket_id
JOIN dim_agents a ON a.agent_id=l.agent_id
WHERE l.work_date<t.local_created_date
   OR l.work_date>DATE(DATE_ADD(COALESCE(t.resolved_at,'2026-09-30 17:00:00'),INTERVAL 7 HOUR))
   OR l.work_date<a.hire_date OR l.handling_minutes<=0;

SELECT w.agent_id,w.work_date FROM fact_workforce_daily w JOIN dim_agents a ON a.agent_id=w.agent_id
WHERE w.work_date<a.hire_date OR w.absence_minutes+w.shrinkage_minutes>w.scheduled_minutes;

SELECT w.agent_id,w.work_date,SUM(l.handling_minutes) AS handling,w.scheduled_minutes-w.absence_minutes AS attendance
FROM fact_workforce_daily w JOIN fact_work_logs l ON l.agent_id=w.agent_id AND l.work_date=w.work_date
GROUP BY w.agent_id,w.work_date,w.scheduled_minutes,w.absence_minutes
HAVING handling>attendance;

SELECT COUNT(*) AS classified_tickets,
 SUM(fr_sla_outcome IN ('MET','BREACHED','PENDING')) AS fr_classified,
 SUM(resolution_sla_outcome IN ('MET','BREACHED','PENDING')) AS resolution_classified,
 SUM(overall_sla_outcome IN ('MET','BREACHED','PENDING')) AS overall_classified
FROM vw_ticket_service_metrics;


-- Expected counts; any mismatch requires investigating import before interpreting KPIs.
SELECT expected.dataset,expected.expected_rows,actual.rows_loaded,
 actual.rows_loaded=expected.expected_rows AS count_matches
FROM (
 SELECT 'agents' AS dataset,18 AS expected_rows UNION ALL SELECT 'policies',16
 UNION ALL SELECT 'categories',18 UNION ALL SELECT 'dates',365
 UNION ALL SELECT 'tickets',14774 UNION ALL SELECT 'work_logs',17901 UNION ALL SELECT 'workforce',6318
) expected
JOIN (
 SELECT 'agents' AS dataset,COUNT(*) AS rows_loaded FROM dim_agents
 UNION ALL SELECT 'policies',COUNT(*) FROM dim_sla_policies
 UNION ALL SELECT 'categories',COUNT(*) FROM dim_categories
 UNION ALL SELECT 'dates',COUNT(*) FROM dim_date
 UNION ALL SELECT 'tickets',COUNT(*) FROM fact_tickets
 UNION ALL SELECT 'work_logs',COUNT(*) FROM fact_work_logs
 UNION ALL SELECT 'workforce',COUNT(*) FROM fact_workforce_daily
) actual USING(dataset);

-- Zero rows expected: policy/domain/local-date/reference consistency.
SELECT t.ticket_id FROM fact_tickets t
LEFT JOIN dim_sla_policies p ON p.policy_id=t.policy_id
LEFT JOIN dim_categories c ON c.category_key=t.category_key
LEFT JOIN dim_agents a ON a.agent_id=t.assigned_agent_id
LEFT JOIN dim_date d ON d.date_key=t.local_created_date
WHERE p.policy_id IS NULL OR c.category_key IS NULL OR d.date_key IS NULL
 OR (t.assigned_agent_id IS NOT NULL AND a.agent_id IS NULL)
 OR t.channel<>p.channel OR t.priority<>p.priority
 OR t.local_created_date<>DATE(DATE_ADD(t.created_at,INTERVAL 7 HOUR))
 OR t.resolved_at<t.created_at OR t.reopen_count<0
 OR (t.csat_score IS NOT NULL AND t.csat_score NOT BETWEEN 1 AND 5);

-- A ticket join to dimensions must retain grain and rows, including null unresolved owners.
SELECT COUNT(*) AS joined_rows,COUNT(DISTINCT t.ticket_id) AS distinct_tickets,
 (SELECT COUNT(*) FROM fact_tickets) AS tickets_before_join
FROM fact_tickets t
LEFT JOIN dim_sla_policies p ON p.policy_id=t.policy_id
LEFT JOIN dim_categories c ON c.category_key=t.category_key
LEFT JOIN dim_agents a ON a.agent_id=t.assigned_agent_id
LEFT JOIN dim_date d ON d.date_key=t.local_created_date;

-- Zero rows expected: log references survive even if FK checks were disabled externally.
SELECT l.work_log_id FROM fact_work_logs l
LEFT JOIN fact_tickets t ON t.ticket_id=l.ticket_id
LEFT JOIN dim_agents a ON a.agent_id=l.agent_id
LEFT JOIN fact_workforce_daily w ON w.agent_id=l.agent_id AND w.work_date=l.work_date
WHERE t.ticket_id IS NULL OR a.agent_id IS NULL OR w.agent_id IS NULL;

-- Zero rows expected: all outcomes partition ticket counts; component Pending differs from status.
SELECT ticket_id FROM vw_ticket_service_metrics
WHERE fr_sla_outcome NOT IN ('MET','BREACHED','PENDING')
 OR resolution_sla_outcome NOT IN ('MET','BREACHED','PENDING')
 OR overall_sla_outcome NOT IN ('MET','BREACHED','PENDING');
