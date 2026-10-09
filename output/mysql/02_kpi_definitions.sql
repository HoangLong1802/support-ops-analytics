USE support_ops_verify_20261008_followup;
CREATE OR REPLACE VIEW vw_ticket_service_metrics AS
WITH durations AS (
    SELECT t.*,c.category,c.subcategory,a.team,
        TIMESTAMPDIFF(SECOND,t.created_at,t.first_response_at)/60.0 AS first_response_minutes,
        TIMESTAMPDIFF(SECOND,t.created_at,t.resolved_at)/60.0 AS resolution_minutes,
        TIMESTAMPDIFF(SECOND,t.created_at,'2026-09-30 17:00:00')/60.0 AS snapshot_age_minutes,
        HOUR(DATE_ADD(t.created_at,INTERVAL 7 HOUR)) AS local_created_hour,
        WEEKDAY(t.local_created_date) AS local_created_weekday,
        t.status IN ('resolved','closed') AS completed,
        p.first_response_target_minutes,p.resolution_target_minutes
    FROM fact_tickets t
    JOIN dim_sla_policies p ON p.policy_id=t.policy_id
    JOIN dim_categories c ON c.category_key=t.category_key
    LEFT JOIN dim_agents a ON a.agent_id=t.assigned_agent_id
), components AS (
    SELECT d.*,
        CASE WHEN first_response_at IS NOT NULL AND first_response_minutes <= first_response_target_minutes THEN 'MET'
             WHEN COALESCE(first_response_minutes,snapshot_age_minutes) > first_response_target_minutes THEN 'BREACHED'
             ELSE 'PENDING' END AS fr_sla_outcome,
        CASE WHEN resolved_at IS NOT NULL AND resolution_minutes <= resolution_target_minutes THEN 'MET'
             WHEN COALESCE(resolution_minutes,snapshot_age_minutes) > resolution_target_minutes THEN 'BREACHED'
             ELSE 'PENDING' END AS resolution_sla_outcome
    FROM durations d
)
SELECT components.*,
    CASE WHEN fr_sla_outcome='BREACHED' OR resolution_sla_outcome='BREACHED' THEN 'BREACHED'
         WHEN completed AND fr_sla_outcome='MET' AND resolution_sla_outcome='MET' THEN 'MET'
         ELSE 'PENDING' END AS overall_sla_outcome,
    CASE WHEN NOT completed THEN snapshot_age_minutes END AS backlog_age_minutes
FROM components;

CREATE OR REPLACE VIEW vw_agent_daily_workload AS
SELECT w.*,a.team,
    w.scheduled_minutes-w.absence_minutes AS physical_attendance_minutes,
    w.scheduled_minutes-w.absence_minutes-w.shrinkage_minutes AS productive_minutes,
    COALESCE(l.handling_minutes,0) AS handling_minutes,
    COALESCE(l.handling_minutes,0)/NULLIF(w.scheduled_minutes-w.absence_minutes-w.shrinkage_minutes,0) AS utilization
FROM fact_workforce_daily w JOIN dim_agents a ON a.agent_id=w.agent_id
LEFT JOIN (
    SELECT agent_id,work_date,SUM(handling_minutes) AS handling_minutes
    FROM fact_work_logs GROUP BY agent_id,work_date
) l ON l.agent_id=w.agent_id AND l.work_date=w.work_date;

-- What is the executive snapshot of demand, service and satisfaction?
SELECT COUNT(*) AS total_tickets,SUM(completed) AS completed_tickets,
 SUM(NOT completed) AS backlog,
 SUM(fr_sla_outcome='MET')/NULLIF(SUM(fr_sla_outcome<>'PENDING'),0) AS fr_sla_compliance,
 SUM(resolution_sla_outcome='MET')/NULLIF(SUM(resolution_sla_outcome<>'PENDING'),0) AS resolution_sla_compliance,
 SUM(overall_sla_outcome='MET')/NULLIF(SUM(overall_sla_outcome<>'PENDING'),0) AS overall_sla_compliance,
 AVG(first_response_minutes) AS average_first_response_minutes,
 AVG(resolution_minutes)/60 AS average_resolution_hours,
 AVG(csat_score) AS average_csat,
 COUNT(csat_score)/NULLIF(SUM(completed),0) AS csat_response_rate,
 AVG(reopen_count>0) AS reopen_rate
FROM vw_ticket_service_metrics;

-- How many MET, BREACHED and PENDING cases exist for each SLA component?
SELECT 'First response' AS component,fr_sla_outcome AS outcome,COUNT(*) AS tickets
FROM vw_ticket_service_metrics GROUP BY fr_sla_outcome
UNION ALL SELECT 'Resolution',resolution_sla_outcome,COUNT(*) FROM vw_ticket_service_metrics GROUP BY resolution_sla_outcome
UNION ALL SELECT 'Overall',overall_sla_outcome,COUNT(*) FROM vw_ticket_service_metrics GROUP BY overall_sla_outcome;
