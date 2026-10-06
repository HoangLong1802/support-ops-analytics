-- MySQL 8.0.16+; dedicated project database. Timestamps are UTC DATETIME values.
CREATE DATABASE IF NOT EXISTS customer_support_analytics CHARACTER SET utf8mb4;
USE customer_support_analytics;

CREATE TABLE IF NOT EXISTS dim_agents (
    agent_id VARCHAR(6) PRIMARY KEY,
    team ENUM('general_support','technical_support','billing_account') NOT NULL,
    hire_date DATE NOT NULL
);
CREATE TABLE IF NOT EXISTS dim_categories (
    category_key VARCHAR(100) PRIMARY KEY,
    category VARCHAR(40) NOT NULL,
    subcategory VARCHAR(40) NOT NULL,
    UNIQUE KEY uq_hierarchy (category, subcategory)
);
CREATE TABLE IF NOT EXISTS dim_sla_policies (
    policy_id VARCHAR(30) PRIMARY KEY,
    channel ENUM('email','chat','phone','web') NOT NULL,
    priority ENUM('low','medium','high','urgent') NOT NULL,
    first_response_target_minutes INT NOT NULL CHECK(first_response_target_minutes > 0),
    resolution_target_minutes INT NOT NULL CHECK(resolution_target_minutes > 0),
    UNIQUE KEY uq_policy (channel,priority),
    UNIQUE KEY uq_policy_match (policy_id,channel,priority)
);
CREATE TABLE IF NOT EXISTS dim_date (
    date_key DATE PRIMARY KEY,
    calendar_year SMALLINT NOT NULL,
    calendar_month TINYINT NOT NULL,
    month_start DATE NOT NULL,
    weekday_number TINYINT NOT NULL,
    weekday_name VARCHAR(10) NOT NULL,
    is_weekend BOOLEAN NOT NULL
);
CREATE TABLE IF NOT EXISTS fact_tickets (
    ticket_id VARCHAR(9) PRIMARY KEY,
    assigned_agent_id VARCHAR(6),
    policy_id VARCHAR(30) NOT NULL,
    channel ENUM('email','chat','phone','web') NOT NULL,
    priority ENUM('low','medium','high','urgent') NOT NULL,
    customer_type ENUM('standard','premium','vip') NOT NULL,
    category_key VARCHAR(100) NOT NULL,
    created_at DATETIME NOT NULL,
    first_response_at DATETIME,
    resolved_at DATETIME,
    local_created_date DATE NOT NULL,
    status ENUM('open','pending','resolved','closed') NOT NULL,
    reopen_count INT NOT NULL CHECK(reopen_count >= 0),
    csat_score TINYINT CHECK(csat_score BETWEEN 1 AND 5),
    FOREIGN KEY (assigned_agent_id) REFERENCES dim_agents(agent_id),
    FOREIGN KEY (policy_id,channel,priority) REFERENCES dim_sla_policies(policy_id,channel,priority),
    FOREIGN KEY (category_key) REFERENCES dim_categories(category_key),
    FOREIGN KEY (local_created_date) REFERENCES dim_date(date_key),
    CHECK(created_at >= '2025-09-30 17:00:00' AND created_at < '2026-09-30 17:00:00'),
    CHECK(first_response_at IS NULL OR (first_response_at >= created_at AND first_response_at <= '2026-09-30 17:00:00')),
    CHECK(resolved_at IS NULL OR (resolved_at >= first_response_at AND resolved_at <= '2026-09-30 17:00:00')),
    CHECK((status IN ('resolved','closed') AND first_response_at IS NOT NULL AND resolved_at IS NOT NULL AND assigned_agent_id IS NOT NULL)
        OR (status IN ('open','pending') AND resolved_at IS NULL AND csat_score IS NULL)),
    INDEX ix_created (local_created_date),
    INDEX ix_owner_status (assigned_agent_id,status),
    INDEX ix_category (category_key)
);
CREATE TABLE IF NOT EXISTS fact_workforce_daily (
    agent_id VARCHAR(6) NOT NULL,
    work_date DATE NOT NULL,
    scheduled_minutes INT NOT NULL CHECK(scheduled_minutes IN (0,450,480,510)),
    absence_minutes INT NOT NULL CHECK(absence_minutes >= 0),
    shrinkage_minutes INT NOT NULL CHECK(shrinkage_minutes >= 0),
    PRIMARY KEY (agent_id,work_date),
    FOREIGN KEY (agent_id) REFERENCES dim_agents(agent_id),
    FOREIGN KEY (work_date) REFERENCES dim_date(date_key),
    CHECK(absence_minutes + shrinkage_minutes <= scheduled_minutes)
);
CREATE TABLE IF NOT EXISTS fact_work_logs (
    work_log_id VARCHAR(10) PRIMARY KEY,
    ticket_id VARCHAR(9) NOT NULL,
    agent_id VARCHAR(6) NOT NULL,
    work_date DATE NOT NULL,
    handling_minutes INT NOT NULL CHECK(handling_minutes > 0),
    UNIQUE KEY uq_entry (ticket_id,agent_id,work_date),
    FOREIGN KEY (ticket_id) REFERENCES fact_tickets(ticket_id),
    FOREIGN KEY (agent_id,work_date) REFERENCES fact_workforce_daily(agent_id,work_date),
    FOREIGN KEY (work_date) REFERENCES dim_date(date_key),
    INDEX ix_work_date (work_date)
);

