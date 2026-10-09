USE support_ops_verify_20261008_followup;

-- What handling effort and capacity belong to each handling agent?
SELECT agent_id,team,SUM(handling_minutes)/60 AS handling_hours,
 SUM(productive_minutes)/60 AS capacity_hours,
 SUM(handling_minutes)/NULLIF(SUM(productive_minutes),0) AS utilization
FROM vw_agent_daily_workload GROUP BY agent_id,team ORDER BY handling_hours DESC;

-- Which teams carry the largest daily workload and capacity pressure?
SELECT team,work_date,SUM(handling_minutes) AS handling_minutes,
 SUM(productive_minutes) AS productive_minutes,
 SUM(handling_minutes)/NULLIF(SUM(productive_minutes),0) AS utilization
FROM vw_agent_daily_workload GROUP BY team,work_date ORDER BY work_date,team;

-- How do final owners perform with sample size, case mix and handling effort context?
-- Ownership metrics and handling-agent workload are aggregated separately to avoid fanout.
WITH ownership AS (
 SELECT assigned_agent_id,COUNT(*) AS tickets,SUM(completed) AS completed,COUNT(csat_score) AS survey_responses,
 SUM(category='technical_support')/COUNT(*) AS technical_share,
 SUM(priority IN ('high','urgent'))/COUNT(*) AS elevated_priority_share,
 SUM(overall_sla_outcome='MET')/NULLIF(SUM(overall_sla_outcome<>'PENDING'),0) AS overall_sla_compliance,
 AVG(csat_score) AS average_csat,AVG(reopen_count>0) AS reopen_rate
 FROM vw_ticket_service_metrics GROUP BY assigned_agent_id
), effort AS (
 SELECT agent_id,SUM(handling_minutes)/60 AS handling_hours,
 SUM(handling_minutes)/NULLIF(SUM(productive_minutes),0) AS utilization FROM vw_agent_daily_workload GROUP BY agent_id
)
SELECT a.agent_id,a.team,o.*,e.handling_hours,e.utilization FROM dim_agents a
LEFT JOIN ownership o ON o.assigned_agent_id=a.agent_id LEFT JOIN effort e ON e.agent_id=a.agent_id;

-- How does case mix differ by owner and team?
SELECT team,assigned_agent_id,category,priority,COUNT(*) AS tickets
FROM vw_ticket_service_metrics GROUP BY team,assigned_agent_id,category,priority ORDER BY team,assigned_agent_id,tickets DESC;

-- Is handling workload imbalanced within teams? Interpret with hire dates and available capacity.
WITH agents AS (
 SELECT agent_id,team,SUM(handling_minutes) AS handling,SUM(productive_minutes) AS productive
 FROM vw_agent_daily_workload GROUP BY agent_id,team
)
SELECT *,handling/NULLIF(AVG(handling) OVER(PARTITION BY team),0) AS handling_vs_team_average,
 handling/NULLIF(productive,0) AS utilization,
 RANK() OVER(PARTITION BY team ORDER BY handling DESC) AS workload_rank FROM agents;
