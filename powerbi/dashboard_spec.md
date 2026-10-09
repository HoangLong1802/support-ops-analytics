# Thiết kế báo cáo / Dashboard Specification

**Chưa có PBIX, native M/DAX hoặc screenshot Power BI.** Các trang dưới đây là specification cần dựng và kiểm thử trong Desktop. Source là processed CSV, 7 bảng theo [model](data_model.md).

Nhãn cố định: Synthetic data; kỳ 01/10/2025–30/09/2026; backlog snapshot 01/10/2026 00:00 UTC+7. Dùng Arial/Segoe UI, nền sáng, navy headers, xanh cho volume/compliance, amber cho breach/aging. Không thêm visual chỉ để đủ số lượng.

## Operations Overview

Câu hỏi: quy mô support và service stage nào cần review?

| Visual | Fields / measures | Cách đọc |
|---|---|---|
| Compact KPI strip | Total Tickets; Resolution SLA Compliance %; Backlog; Average CSAT | Tooltip: eligible N, CSAT responses và response rate |
| Monthly arrivals line | dim_date.month_start; Total Tickets | Đủ 12 tháng; date là creation cohort |
| SLA outcomes columns | FR / Resolution / Overall Met, Breached, Pending | Không cộng component breach counts |
| Category comparison | dim_categories.category; Ticket Share %, Resolution Breach Share %, Resolution SLA Breach % | Tách contribution khỏi within-group rate; có eligible N |

Date, category, channel, priority slicers chọn ticket cohort. Snapshot backlog không thay theo ngày trên slicer. Không dùng fact category slicer để kiểm tra REMOVEFILTERS(dim_categories) measures.

## SLA & Demand

Câu hỏi: case nào breach và demand đến khi nào?

| Visual | Fields / measures | Cách đọc |
|---|---|---|
| Category/priority matrix | tickets, resolution eligible/breaches/rate | Sample size và SLA policy targets đi cùng rate |
| Weekday bars | weekday_name; Average Daily Tickets | Sort weekday_number; denominator là calendar days |
| Local-hour arrivals | local_created_hour; Total Tickets | Arrival không chứng minh hourly effort |
| Snapshot backlog aging | category; Backlog >24/>48/>72 Hours | Nested thresholds; không stacked thành distinct bins |

Nếu thêm distinct aging bands, dùng half-open: <24h, 24–48h, 48–72h, 3–7d, 7–30d, 30+d. Boundaries khớp workbook/SQL. Không dựng historical backlog. Median/P95 elapsed resolution đặt ở tooltip nếu hữu ích; không gọi duration là handling.

## Mở, refresh và nghiệm thu

Tạo file ở Desktop theo [checklist](desktop_checklist.md). Đổi ProjectFolder, Refresh, kiểm tra row counts và 41 cohort references. Save genuine PBIX, reopen và kiểm tra filters/refresh lần nữa. Sau đó capture thật đúng hai trang vào images/powerbi/operations_overview.png và sla_demand.png. Chưa có các file đó; không link chúng như sản phẩm hoàn thành. Không publish lên Service.
