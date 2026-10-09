# Kết quả chính / Key Findings

Toàn bộ kết quả mô tả dữ liệu mô phỏng. Pipeline không đo tác động kinh doanh của thay đổi đã triển khai.

| Phát hiện | Con số và ý nghĩa | Bằng chứng | Giới hạn |
|---|---|---|---|
| Technical tập trung resolution breaches | {{technical_tickets:,}} ticket ({{technical_ticket_share:.2%}} volume), {{technical_breaches:,}}/{{resolution_sla_breached:,}} breaches ({{technical_breach_share:.2%}}); rate trong nhóm {{technical_breach_rate:.2%}} trên {{technical_eligible:,}} eligible cases | [Category summary](../data/analytics/category_service_summary.csv), [SQL](../sql/06_claim_verification.sql) | Volume share, breach share và within-group rate là ba phép đo khác nhau; case mix chưa điều chỉnh |
| Weekday demand cao hơn theo ngày | {{weekday_tickets:,}}/{{weekday_days:,}} = {{weekday_average:.2f}}/ngày; weekend {{weekend_tickets:,}}/{{weekend_days:,}} = {{weekend_average:.2f}}/ngày; ratio {{weekday_weekend_ratio:.2f}}x | [Day-type summary](../data/analytics/demand_day_type.csv), [SQL](../sql/06_claim_verification.sql) | Total ratio {{total_demand_ratio:.2f}}x không phải daily demand; chưa biết hourly handling |
| Resolution SLA thấp hơn response SLA | Compliance {{resolution_sla_compliance:.2%}} so với {{fr_sla_compliance:.2%}}; overall {{overall_sla_compliance:.2%}} | [KPI output](../data/analytics/verified_kpis.csv), [SLA SQL](../sql/02_kpi_definitions.sql) | Pending loại riêng mỗi mẫu số; breach component counts có overlap |
| Backlog chủ yếu đã già | {{backlog_over_48_hours:,}}/{{backlog:,}} ticket >48h; {{backlog_resolution_breaches:,}} resolution breaches | [Ticket service facts](../data/analytics/ticket_service_metrics.csv), [Backlog SQL](../sql/03_operations_analysis.sql) | Chỉ snapshot 01/10/2026 00:00 local; không suy dựng historical backlog |
| CSAT cần response-rate context | {{average_csat:.2f}}/5 từ {{csat_responses:,}}/{{completed_tickets:,}} completed tickets ({{csat_response_rate:.2%}}) | [Customer SQL](../sql/04_customer_analysis.sql), [KPI output](../data/analytics/verified_kpis.csv) | Người không trả lời có thể khác người trả lời; không kết luận causal |

## Đề xuất / Recommendations

1. **Review technical queues và aged backlog.** Phân tầng theo subcategory, priority và policy, kiểm tra handoff, dependency và next action. Giả thuyết: waiting/handoff góp phần vào breach. Theo dõi within-category resolution breach rate, eligible N và backlog >48h ở snapshot mới; đề xuất chưa phải thành tích.
2. **Thử bố trí triage theo daily demand.** Weekday average là {{weekday_weekend_ratio:.2f}}x weekend. Đối chiếu arrivals với handling timestamps trước khi đổi ca. Giả thuyết: coverage theo thời điểm đến giúp response SLA. Theo dõi FR breach rate, handling/capacity và backlog mới; daily logs không xác định exact hourly staffing gaps.
3. **Đọc CSAT với participation và case mix.** So sánh cùng category/priority, giữ sample counts trên agent/team tables và rà soát reopen. Giả thuyết: communication trong thời gian chờ liên quan CSAT. Theo dõi CSAT, response rate và Reopen Rate; Reopen Rate không phải First Contact Resolution.

Mean resolution {{average_resolution_hours:.2f}}h, median {{median_resolution_hours:.2f}}h và P95 {{p95_resolution_hours:.2f}}h được giữ trong workbook để mô tả long tail. Elapsed resolution gồm waiting, không phải handling effort.
