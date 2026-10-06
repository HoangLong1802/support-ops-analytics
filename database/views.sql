USE customer_support_analytics;
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

