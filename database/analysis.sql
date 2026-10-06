USE customer_support_analytics;

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

-- How does monthly demand change?
WITH months AS (
 SELECT d.month_start,COUNT(t.ticket_id) AS tickets
 FROM dim_date d LEFT JOIN fact_tickets t ON t.local_created_date=d.date_key GROUP BY d.month_start
), changes AS (
 SELECT *,LAG(tickets) OVER(ORDER BY month_start) AS previous_month FROM months
)
SELECT *, (tickets-previous_month)/NULLIF(previous_month,0) AS mom_change FROM changes ORDER BY month_start;

-- Which local weekdays have the highest average daily demand? Include zero days.
WITH daily AS (
 SELECT d.date_key,d.weekday_number,d.weekday_name,COUNT(t.ticket_id) AS tickets
 FROM dim_date d LEFT JOIN fact_tickets t ON t.local_created_date=d.date_key
 GROUP BY d.date_key,d.weekday_number,d.weekday_name
)
SELECT weekday_number,weekday_name,SUM(tickets) AS tickets,COUNT(*) AS days,AVG(tickets) AS average_daily
FROM daily GROUP BY weekday_number,weekday_name ORDER BY weekday_number;

-- Which local arrival hours concentrate demand? This does not estimate hourly staffing gaps.
SELECT local_created_hour,COUNT(*) AS tickets FROM vw_ticket_service_metrics
GROUP BY local_created_hour ORDER BY local_created_hour;

-- What is the channel mix and first-response performance?
SELECT channel,COUNT(*) AS tickets,COUNT(*)/SUM(COUNT(*)) OVER() AS share,
 AVG(first_response_minutes) AS average_response,
 SUM(fr_sla_outcome='MET')/NULLIF(SUM(fr_sla_outcome<>'PENDING'),0) AS fr_sla_compliance
FROM vw_ticket_service_metrics GROUP BY channel ORDER BY tickets DESC;

-- Which categories and subcategories dominate volume and resolution breaches?
SELECT category,subcategory,COUNT(*) AS tickets,
 SUM(resolution_sla_outcome='BREACHED') AS resolution_breaches,
 SUM(resolution_sla_outcome='BREACHED')/NULLIF(SUM(resolution_sla_outcome<>'PENDING'),0) AS resolution_breach_rate
FROM vw_ticket_service_metrics GROUP BY category,subcategory ORDER BY tickets DESC;

-- How does priority affect service outcomes?
SELECT priority,COUNT(*) AS tickets,AVG(first_response_minutes) AS average_response_minutes,
 SUM(fr_sla_outcome='MET')/NULLIF(SUM(fr_sla_outcome<>'PENDING'),0) AS fr_sla_compliance,
 SUM(resolution_sla_outcome='MET')/NULLIF(SUM(resolution_sla_outcome<>'PENDING'),0) AS resolution_sla_compliance,
 SUM(overall_sla_outcome='MET')/NULLIF(SUM(overall_sla_outcome<>'PENDING'),0) AS overall_sla_compliance
FROM vw_ticket_service_metrics GROUP BY priority;

-- How many MET, BREACHED and PENDING cases exist for each SLA component?
SELECT 'First response' AS component,fr_sla_outcome AS outcome,COUNT(*) AS tickets
FROM vw_ticket_service_metrics GROUP BY fr_sla_outcome
UNION ALL SELECT 'Resolution',resolution_sla_outcome,COUNT(*) FROM vw_ticket_service_metrics GROUP BY resolution_sla_outcome
UNION ALL SELECT 'Overall',overall_sla_outcome,COUNT(*) FROM vw_ticket_service_metrics GROUP BY overall_sla_outcome;

-- Which categories contribute the most resolution breaches, relative to their demand share?
WITH mix AS (
 SELECT category,COUNT(*) AS tickets,SUM(resolution_sla_outcome='BREACHED') AS breaches
 FROM vw_ticket_service_metrics GROUP BY category
)
SELECT *,tickets/SUM(tickets) OVER() AS ticket_share,
 breaches/NULLIF(SUM(breaches) OVER(),0) AS breach_share FROM mix ORDER BY breaches DESC;

-- What do first-response and resolution distributions look like beyond their means?
WITH durations AS (
 SELECT ticket_id,'First response minutes' AS measure,first_response_minutes AS duration FROM vw_ticket_service_metrics WHERE first_response_at IS NOT NULL
 UNION ALL SELECT ticket_id,'Resolution hours',resolution_minutes/60 FROM vw_ticket_service_metrics WHERE resolved_at IS NOT NULL
), ordered AS (
 SELECT *,ROW_NUMBER() OVER(PARTITION BY measure ORDER BY duration,ticket_id) AS rn,
 COUNT(*) OVER(PARTITION BY measure) AS n FROM durations
)
SELECT measure,AVG(duration) AS mean,
 AVG(CASE WHEN rn IN (FLOOR((n+1)/2),FLOOR((n+2)/2)) THEN duration END) AS median,
 MAX(CASE WHEN rn=CEIL(n*.90) THEN duration END) AS p90_nearest_rank,
 MAX(CASE WHEN rn=CEIL(n*.95) THEN duration END) AS p95_nearest_rank,
 MAX(duration) AS maximum FROM ordered GROUP BY measure;

-- Which cohorts have poor satisfaction or low survey participation?
SELECT category,COUNT(*) AS tickets,SUM(completed) AS completed,COUNT(csat_score) AS responses,
 AVG(csat_score) AS average_csat,COUNT(csat_score)/NULLIF(SUM(completed),0) AS response_rate
FROM vw_ticket_service_metrics GROUP BY category;

-- Is elapsed resolution associated with survey scores? Nonresponse and case mix limit interpretation.
SELECT CASE WHEN resolution_minutes<=240 THEN '01 <=4h'
 WHEN resolution_minutes<=1440 THEN '02 4-24h' WHEN resolution_minutes<=4320 THEN '03 24-72h' ELSE '04 >72h' END AS duration_band,
 COUNT(*) AS completed,COUNT(csat_score) AS survey_responses,AVG(csat_score) AS average_csat,
 COUNT(csat_score)/COUNT(*) AS response_rate
FROM vw_ticket_service_metrics WHERE completed GROUP BY duration_band ORDER BY duration_band;

-- Which case types reopen more often? Reopen Rate is not FCR.
SELECT category,subcategory,COUNT(*) AS tickets,SUM(reopen_count>0) AS reopened,
 AVG(reopen_count>0) AS reopen_rate FROM vw_ticket_service_metrics
GROUP BY category,subcategory ORDER BY reopen_rate DESC;

-- What does the snapshot backlog contain?
SELECT status,priority,COUNT(*) AS backlog,AVG(backlog_age_minutes)/60 AS average_age_hours,
 SUM(resolution_sla_outcome='BREACHED') AS overdue_resolution
FROM vw_ticket_service_metrics WHERE NOT completed GROUP BY status,priority;

-- How old is backlog at the fixed snapshot? These are not historical backlog trends.
SELECT CASE WHEN backlog_age_minutes<=1440 THEN '01 <=24h'
 WHEN backlog_age_minutes<=2880 THEN '02 24-48h'
 WHEN backlog_age_minutes<=4320 THEN '03 48-72h' ELSE '04 >72h' END AS age_band,
 COUNT(*) AS backlog FROM vw_ticket_service_metrics WHERE NOT completed GROUP BY age_band ORDER BY age_band;

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

-- How does demand change week over week? Flag partial boundary weeks.
WITH weeks AS (
 SELECT DATE_SUB(d.date_key,INTERVAL WEEKDAY(d.date_key) DAY) AS week_start,
 COUNT(DISTINCT d.date_key) AS covered_days,COUNT(t.ticket_id) AS tickets
 FROM dim_date d LEFT JOIN fact_tickets t ON t.local_created_date=d.date_key GROUP BY week_start
), changes AS (
 SELECT *,LAG(tickets) OVER(ORDER BY week_start) AS previous_week,
 LAG(covered_days) OVER(ORDER BY week_start) AS previous_covered_days FROM weeks
)
SELECT *,CASE WHEN covered_days=7 AND previous_covered_days=7 THEN (tickets-previous_week)/NULLIF(previous_week,0) END AS wow_change
FROM changes ORDER BY week_start;

-- What is the calendar-day rolling trend? Early windows disclose their coverage.
WITH daily AS (
 SELECT d.date_key,COUNT(t.ticket_id) AS tickets FROM dim_date d
 LEFT JOIN fact_tickets t ON t.local_created_date=d.date_key GROUP BY d.date_key
)
SELECT *,AVG(tickets) OVER(ORDER BY date_key ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_7_day_average,
 COUNT(*) OVER(ORDER BY date_key ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS days_in_window FROM daily ORDER BY date_key;

-- Which categories should be reviewed first for operational risk?
-- Rankings order absolute breach contribution; they are not a causal or weighted quality score.
WITH risks AS (
 SELECT category,COUNT(*) AS tickets,SUM(overall_sla_outcome='BREACHED') AS breached,
 SUM(NOT completed) AS backlog,AVG(reopen_count>0) AS reopen_rate,
 AVG(csat_score) AS average_csat,COUNT(csat_score) AS survey_responses
 FROM vw_ticket_service_metrics GROUP BY category
)
SELECT *,DENSE_RANK() OVER(ORDER BY breached DESC) AS review_rank FROM risks ORDER BY review_rank;

