-- Start with empty fact tables. Do not use REPLACE or IGNORE to conceal bad imports.
-- Edit the five absolute CSV paths if the repository lives elsewhere.
USE customer_support_analytics;
SET time_zone = '+00:00';

INSERT INTO dim_date
WITH RECURSIVE dates AS (
    SELECT DATE('2025-10-01') AS d
    UNION ALL SELECT d + INTERVAL 1 DAY FROM dates WHERE d < '2026-09-30'
)
SELECT d,YEAR(d),MONTH(d),DATE_SUB(d,INTERVAL DAYOFMONTH(d)-1 DAY),
       WEEKDAY(d),DAYNAME(d),WEEKDAY(d)>=5 FROM dates
WHERE NOT EXISTS (SELECT 1 FROM dim_date existing WHERE existing.date_key=dates.d);

INSERT INTO dim_categories(category_key,category,subcategory) VALUES
('technical_support|login_authentication','technical_support','login_authentication'),
('technical_support|performance','technical_support','performance'),
('technical_support|integration','technical_support','integration'),
('technical_support|bug_error','technical_support','bug_error'),
('billing|payment_failed','billing','payment_failed'),
('billing|refund','billing','refund'),
('billing|invoice','billing','invoice'),
('billing|subscription','billing','subscription'),
('account_access|password_reset','account_access','password_reset'),
('account_access|account_locked','account_access','account_locked'),
('account_access|verification','account_access','verification'),
('account_access|profile','account_access','profile'),
('product_service_inquiry|feature_question','product_service_inquiry','feature_question'),
('product_service_inquiry|pricing','product_service_inquiry','pricing'),
('product_service_inquiry|availability','product_service_inquiry','availability'),
('service_request|configuration','service_request','configuration'),
('service_request|upgrade','service_request','upgrade'),
('service_request|cancellation','service_request','cancellation')
ON DUPLICATE KEY UPDATE category=VALUES(category),subcategory=VALUES(subcategory);

LOAD DATA LOCAL INFILE '__PROJECT_ROOT__/data/processed/agents_clean.csv'
INTO TABLE dim_agents FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n' IGNORE 1 LINES (agent_id,team,hire_date);
SHOW WARNINGS;

LOAD DATA LOCAL INFILE '__PROJECT_ROOT__/data/processed/sla_policies_clean.csv'
INTO TABLE dim_sla_policies FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n' IGNORE 1 LINES
(policy_id,channel,priority,first_response_target_minutes,resolution_target_minutes);
SHOW WARNINGS;

LOAD DATA LOCAL INFILE '__PROJECT_ROOT__/data/processed/workforce_daily_clean.csv'
INTO TABLE fact_workforce_daily FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n' IGNORE 1 LINES
(agent_id,work_date,scheduled_minutes,absence_minutes,shrinkage_minutes);
SHOW WARNINGS;

LOAD DATA LOCAL INFILE '__PROJECT_ROOT__/data/processed/tickets_clean.csv'
INTO TABLE fact_tickets FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n' IGNORE 1 LINES
(ticket_id,@owner,policy_id,channel,priority,customer_type,@category,@subcategory,
 @created,@response,@resolved,status,reopen_count,@csat)
SET assigned_agent_id=NULLIF(@owner,''),
    category_key=CONCAT(@category,'|',@subcategory),
    created_at=STR_TO_DATE(@created,'%Y-%m-%dT%H:%i:%sZ'),
    first_response_at=STR_TO_DATE(NULLIF(@response,''),'%Y-%m-%dT%H:%i:%sZ'),
    resolved_at=STR_TO_DATE(NULLIF(@resolved,''),'%Y-%m-%dT%H:%i:%sZ'),
    local_created_date=DATE(DATE_ADD(STR_TO_DATE(@created,'%Y-%m-%dT%H:%i:%sZ'),INTERVAL 7 HOUR)),
    csat_score=CAST(NULLIF(@csat,'') AS DECIMAL(3,1));
SHOW WARNINGS;

LOAD DATA LOCAL INFILE '__PROJECT_ROOT__/data/processed/ticket_work_logs_clean.csv'
INTO TABLE fact_work_logs FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n' IGNORE 1 LINES
(work_log_id,ticket_id,agent_id,work_date,handling_minutes);
SHOW WARNINGS;

