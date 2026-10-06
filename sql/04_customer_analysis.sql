USE customer_support_analytics;

-- Do tickets with a recorded reopen have lower respondent satisfaction?
-- Keep survey counts and completed-ticket denominators beside cohort averages.
SELECT CASE WHEN reopen_count>0 THEN 'reopened' ELSE 'no_recorded_reopen' END AS reopen_cohort,
 COUNT(*) AS tickets,SUM(completed) AS completed,COUNT(csat_score) AS survey_responses,
 AVG(csat_score) AS average_csat,
 COUNT(csat_score)/NULLIF(SUM(completed),0) AS response_rate
FROM vw_ticket_service_metrics GROUP BY reopen_cohort;

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
