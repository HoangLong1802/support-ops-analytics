# Dựng và kiểm thử trong Power BI Desktop

Trạng thái 08/10/2026: chưa mở được Desktop. Bị chặn ngay ở sky.list_apps trước khi chọn cửa sổ: Computer Use native pipe is unavailable ... The system cannot find the file specified (os error 2). Common executable paths không có; WindowsApps EPERM nên không kết luận Power BI chưa cài trên toàn máy. Chưa có PBIX, M/DAX execution hoặc screenshot Power BI. Hướng dẫn dưới đây là việc người dùng cần thực hiện.

## 1. Mở Desktop và nạp M

1. Mở Power BI Desktop trên Windows tương tác; tạo Blank report. Nếu chưa có, cài Desktop rồi mở. Không cần Power BI Service.
2. Home → Transform data → New Source → Blank Query; View → Advanced Editor. Mở processed_queries.pq bằng text editor.
3. Tạo từng query theo tên ở comment Query:, chỉ paste biểu thức của block đó. Thứ tự: ProjectFolder, ReadProcessed, dim_agents, dim_sla_policies, fact_tickets, dim_categories, fact_work_logs, fact_workforce_daily, dim_date.
4. ProjectFolder dùng "D:\Project\DA\support-ops-analytics" hoặc checkout thật. Disable Enable load cho ProjectFolder và ReadProcessed; giữ 7 model tables còn lại loaded. Source là 5 processed CSV, không import workbook.
5. Close & Apply. Trong Table view kiểm tra tickets 14.774, logs 17.901, workforce 6.318; agents 18, policies 16, categories 18, dates 365. Không tiếp tục khi query error/row count sai. Kiểm tra UTC instants và local_created_date của TKT000001 = 01/10/2025.

## 2. Tạo relationships

Model view → Manage relationships: bỏ relationship auto-detect sai, tạo đúng 8 relationships trong data_model.md. Mỗi relation Active, One-to-many (1:*), Cross filter direction Single, dimension phía 1 và fact phía *.

| Dimension | Fact / column |
|---|---|
| dim_date.date_key | fact_tickets.local_created_date |
| dim_date.date_key | fact_work_logs.work_date |
| dim_date.date_key | fact_workforce_daily.work_date |
| dim_agents.agent_id | fact_tickets.assigned_agent_id |
| dim_agents.agent_id | fact_work_logs.agent_id |
| dim_agents.agent_id | fact_workforce_daily.agent_id |
| dim_categories.category_key | fact_tickets.category_key |
| dim_sla_policies.policy_id | fact_tickets.policy_id |

Không tạo active fact-to-fact hoặc Both direction. Mark dim_date as date table → date_key; sort weekday_name by weekday_number. Date/time source events giữ UTC, local_created_date/work_date là Date. Xác nhận dim keys unique trước khi đặt cardinality; xem [Microsoft relationship guidance](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-create-and-manage-relationships).

## 3. Thêm measures hiện có

Modeling → New measure: paste riêng từng definition từ measures.dax (không paste toàn file một lần). Có thể đặt Home table fact_tickets. Counts Whole number, durations decimal có unit, fractions Percentage. Chỉ dùng measures đã có; không tạo KPI mới.

Total Tickets đã sửa COALESCE(COUNTROWS(...),0) cho empty cohorts; xác nhận trên Desktop. Rate DIVIDE denominator=0 → BLANK. Resolution SLA eligible trên visuals hiển thị hai counts Met và Breached nếu không có measure eligible riêng.

## 4. Dựng đúng hai trang

Canvas 16:9, nền sáng, navy title, ghi Synthetic data; kỳ 01/10/2025–30/09/2026; backlog snapshot 01/10/2026 00:00 UTC+7.

Operations Overview:
- 4 cards: Total Tickets, Resolution SLA Compliance %, Backlog, Average CSAT. Tooltip/adjacent counts dùng Resolution SLA Met/Breached, CSAT Responses và CSAT Response Rate %.
- Line chart: dim_date.month_start → Total Tickets, đủ 12 tháng.
- Ba chart nhỏ FR/Resolution/Overall, mỗi chart ba measures Met/Breached/Pending hiện có. Không cộng component breaches.
- Category table: dim_categories.category; Total Tickets; Ticket Share %; Resolution SLA Met; Resolution SLA Breached; Resolution Breach Share %; Resolution SLA Breach %.
- Date slicer dim_date.date_key; category slicer dim_categories.category; channel/priority từ dim_sla_policies. Đặt field slicers từ dimensions để shares REMOVEFILTERS(dim_categories) đúng scope.

SLA/Demand:
- Matrix: category và priority; Total Tickets, Resolution SLA Met/Breached/Pending, Resolution SLA Breach %.
- Weekday bar: dim_date.weekday_name → Average Daily Tickets; sort weekday_number.
- Hour chart: fact_tickets.local_created_hour → Total Tickets, local UTC+7; không suy ra hourly staffing gap.
- Backlog table: category; Backlog, Backlog >24/>48/>72 Hours. Các thresholds lồng nhau, không stacked thành distinct bins.
- Hai cards average weekday/weekend và ratio dùng measures hiện có; calendar counts đặt tooltips.

Sync slicers giữa hai trang. Date chọn creation cohorts, không đổi snapshot cutoff. Không tạo trang thứ ba.

## 5. Đối chiếu filter và measures trong Desktop

1. Clear tất cả filters. So counts bằng đúng, ratios/full precision tolerance 1e-9 với verified_kpis.csv và independent_validation.json. FR M/B/P 12.990/1.783/1; Resolution 11.243/3.514/17; Overall 9.986/4.772/16. Rate hiển thị hai chữ số phần trăm.
2. Technical filter từ dimension: tickets 4.357, resolution MET 2.592, BREACHED 1.760, PENDING 5, eligible 4.352; contribution 50,0853728%, within-group rate 40,4411765%, volume share 29,4909977%.
3. Thử lần lượt cả 41 scopes trong acceptance_reference.json: All, 5 categories, 4 priorities, 18 owners, unassigned, 12 tháng. Native values phải được ghi lại trong bảng so sánh riêng; Python references đã được đối chiếu bằng oracle độc lập, chưa chứng minh DAX đúng.
4. owner=unassigned thực tế 0 tickets; Total Tickets phải 0, Average CSAT và eligible rate BLANK. Dùng filter pane fact_tickets.assigned_agent_id is blank nếu blank dimension member không xuất hiện. Không làm mất ticket hợp lệ vì null-owner behavior.
5. Calendar unfiltered = 365, weekday 261, weekend 104; averages 46,8965517241 và 24,3653846154; ratio 1,9247203549. Current actual dates không có zero-ticket days. Để kiểm tra empty cohort: ngày 01/10/2025 + filter ticket_id=TKT014997 (created 30/09/2026) trong filter pane → Total Tickets 0, Calendar Days 1, Average Daily Tickets 0, SLA rate BLANK. Xóa test filter sau đó. Không sửa source.
6. So cohort month/owner/category propagation qua relationships. Category share denominator bỏ category nhưng giữ date/channel/priority; không dùng fact.category slicer để kiểm tra share.
7. CSAT blank không thành 0; full mean 4,0714574082 với N=7.431 / completed 14.196. Check Median 6,2166666667h, P95 48,75h nếu dùng tooltips.
8. Giữ workload measures trong package nhưng không dựng thêm trang. Nếu kiểm tra measures workload trong Table view/temporary visual: handler/work date scope; category/priority không filter full capacity. Không nối facts để làm filter propagation.

## 6. Lưu và capture thật

File → Save As powerbi/customer_support_analytics.pbix. Đóng, mở lại, Home → Refresh; lặp unfiltered, Technical và 1 month check. Ghi phiên bản Desktop (Help/About), thời điểm refresh, observed values/sai lệch. Save sau khi kiểm thử.

Dùng capture cửa sổ Power BI thật với trang không popup, lưu images/powerbi/operations_overview.png và sla_demand.png, thêm model screenshot nếu có. Không dùng workbook render thay cho report screenshot. Chỉ gọi report hoàn thành sau PBIX, refresh, filters và ảnh thật đã kiểm thử. Không publish Service.
