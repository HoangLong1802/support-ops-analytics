USE customer_support_analytics;
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

