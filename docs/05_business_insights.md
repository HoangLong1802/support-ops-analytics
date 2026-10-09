# Kết quả chính / Key Findings

Toàn bộ kết quả mô tả dữ liệu mô phỏng. Pipeline không đo tác động kinh doanh của thay đổi đã triển khai.

| Phát hiện | Con số và ý nghĩa | Bằng chứng | Giới hạn |
|---|---|---|---|
| Technical tập trung resolution breaches | 4,357 ticket (29.49% volume), 1,760/3,514 breaches (50.09%); rate trong nhóm 40.44% trên 4,352 eligible cases | [Category summary](../data/analytics/category_service_summary.csv), [SQL](../sql/06_claim_verification.sql) | Volume share, breach share và within-group rate là ba phép đo khác nhau; case mix chưa điều chỉnh |
| Weekday demand cao hơn theo ngày | 12,240/261 = 46.90/ngày; weekend 2,534/104 = 24.37/ngày; ratio 1.92x | [Day-type summary](../data/analytics/demand_day_type.csv), [SQL](../sql/06_claim_verification.sql) | Total ratio 4.83x không phải daily demand; chưa biết hourly handling |
| Resolution SLA thấp hơn response SLA | Compliance 76.19% so với 87.93%; overall 67.66% | [KPI output](../data/analytics/verified_kpis.csv), [SLA SQL](../sql/02_kpi_definitions.sql) | Pending loại riêng mỗi mẫu số; breach component counts có overlap |
| Backlog chủ yếu đã già | 552/578 ticket >48h; 561 resolution breaches | [Ticket service facts](../data/analytics/ticket_service_metrics.csv), [Backlog SQL](../sql/03_operations_analysis.sql) | Chỉ snapshot 01/10/2026 00:00 local; không suy dựng historical backlog |
| CSAT cần response-rate context | 4.07/5 từ 7,431/14,196 completed tickets (52.35%) | [Customer SQL](../sql/04_customer_analysis.sql), [KPI output](../data/analytics/verified_kpis.csv) | Người không trả lời có thể khác người trả lời; không kết luận causal |

## Đề xuất / Recommendations

1. **Review technical queues và aged backlog.** Phân tầng theo subcategory, priority và policy, kiểm tra handoff, dependency và next action. Giả thuyết: waiting/handoff góp phần vào breach. Theo dõi within-category resolution breach rate, eligible N và backlog >48h ở snapshot mới; đề xuất chưa phải thành tích.
2. **Thử bố trí triage theo daily demand.** Weekday average là 1.92x weekend. Đối chiếu arrivals với handling timestamps trước khi đổi ca. Giả thuyết: coverage theo thời điểm đến giúp response SLA. Theo dõi FR breach rate, handling/capacity và backlog mới; daily logs không xác định exact hourly staffing gaps.
3. **Đọc CSAT với participation và case mix.** So sánh cùng category/priority, giữ sample counts trên agent/team tables và rà soát reopen. Giả thuyết: communication trong thời gian chờ liên quan CSAT. Theo dõi CSAT, response rate và Reopen Rate; Reopen Rate không phải First Contact Resolution.

Mean resolution 117.05h, median 6.22h và P95 48.75h được giữ trong workbook để mô tả long tail. Elapsed resolution gồm waiting, không phải handling effort.
