USE support_ops_verify_20261008_followup;

-- Câu hỏi: Technical góp bao nhiêu volume/breaches, rate trong nhóm là bao nhiêu?
-- Logic: 1 row/ticket, outcome BREACHED; eligible = MET + BREACHED.
-- Đọc kết quả: ticket_share, breach_share và within-group rate có mẫu số khác nhau.
-- Giới hạn: snapshot creation cohort, chưa điều chỉnh case mix; không xếp hạng agent.
WITH cohorts AS (
 SELECT category, COUNT(*) AS tickets,
        SUM(resolution_sla_outcome='BREACHED') AS resolution_breaches,
        SUM(resolution_sla_outcome<>'PENDING') AS resolution_eligible
 FROM vw_ticket_service_metrics GROUP BY category
)
SELECT category,tickets,resolution_breaches,resolution_eligible,
 tickets / SUM(tickets) OVER() AS ticket_share,
 resolution_breaches / NULLIF(SUM(resolution_breaches) OVER(),0) AS resolution_breach_share,
 resolution_breaches / NULLIF(resolution_eligible,0) AS resolution_breach_rate
FROM cohorts ORDER BY resolution_breaches DESC;

-- Câu hỏi: weekday arrivals khác weekend theo ngày hay tổng volume?
-- Logic: calendar left join tickets, COUNT(ticket_id) giữ zero-ticket dates.
-- Đọc: ratio average phải dùng số calendar days, không so tổng 5 ngày với 2 ngày.
-- Giới hạn: coverage từ simulation contract; arrival != hourly handling/staffing.
WITH daily AS (
 SELECT d.date_key,d.is_weekend,COUNT(t.ticket_id) AS tickets
 FROM dim_date d LEFT JOIN fact_tickets t ON t.local_created_date=d.date_key
 GROUP BY d.date_key,d.is_weekend
), segments AS (
 SELECT is_weekend,SUM(tickets) AS tickets,COUNT(*) AS calendar_days,
 SUM(tickets=0) AS zero_ticket_days,AVG(tickets) AS average_daily_tickets
 FROM daily GROUP BY is_weekend
)
SELECT CASE WHEN is_weekend THEN 'Weekend' ELSE 'Weekday' END AS day_type,
 tickets,calendar_days,zero_ticket_days,average_daily_tickets FROM segments ORDER BY is_weekend;

WITH daily AS (
 SELECT d.date_key,d.is_weekend,COUNT(t.ticket_id) AS tickets
 FROM dim_date d LEFT JOIN fact_tickets t ON t.local_created_date=d.date_key
 GROUP BY d.date_key,d.is_weekend
)
SELECT SUM(CASE WHEN NOT is_weekend THEN tickets ELSE 0 END)
       / NULLIF(SUM(CASE WHEN is_weekend THEN tickets ELSE 0 END),0) AS total_ticket_ratio,
 (SUM(CASE WHEN NOT is_weekend THEN tickets ELSE 0 END) / NULLIF(SUM(NOT is_weekend),0))
 / NULLIF(SUM(CASE WHEN is_weekend THEN tickets ELSE 0 END) / NULLIF(SUM(is_weekend),0),0)
 AS average_daily_ratio FROM daily;
