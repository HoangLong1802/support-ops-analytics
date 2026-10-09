# Kiểm tra claim cũ

| Claim | Tính lại từ pipeline | Cách sử dụng |
|---|---|---|
| 5 support datasets | 5 raw CSV, 5 processed CSV | Ghi rõ synthetic datasets |
| 14,774 cleaned tickets | {{total_tickets:,}} unique retained ticket IDs | Đúng; không gọi là ticket doanh nghiệp thực |
| Workbook 14 sheet | Đọc actual workbook trong validation receipt | Không dùng đếm từ source code để xác nhận file |
| Technical = 50.09% resolution breaches | {{technical_breaches:,}}/{{resolution_sla_breached:,}} = {{technical_breach_share:.2%}} | Đúng với contribution share; volume {{technical_ticket_share:.2%}}, within-group rate {{technical_breach_rate:.2%}} |
| Weekday demand = 1.92x weekend | ({{weekday_tickets:,}}/{{weekday_days:,}}) / ({{weekend_tickets:,}}/{{weekend_days:,}}) = {{weekday_weekend_ratio:.2f}}x | Đúng với average daily arrivals; total ratio {{total_demand_ratio:.2f}}x là chỉ số khác |

[Code](../src/case_study.py) · [SQL](../sql/06_claim_verification.sql) · [Full precision output](../data/analytics/case_study_claims.json).

Simulation contract xác định 365 coverage dates; có {{zero_ticket_days:,}} zero-ticket days, vẫn giữ trong denominator.

## Claim CV cần cập nhật

Nhiệm vụ này không sửa CV. Cách viết phù hợp: “Phân tích 5 synthetic support datasets; làm sạch và reconcile 14,774 tickets; xây pipeline Python, SQL MySQL và workbook Excel 14 sheet.” Chỉ dùng số sheet khi receipt xác nhận. Chưa ghi “built Power BI dashboard” hoặc “SQL tested on MySQL”. Không ghi tác động giảm SLA/staffing/CSAT khi chưa triển khai thử nghiệm. Technical breach share và daily demand ratio phải giữ đúng mẫu số.
