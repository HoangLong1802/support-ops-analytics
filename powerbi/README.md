# Power BI / Implementation package

**Chưa có PBIX hoặc dashboard native hoàn thành.** Không tìm thấy Power BI Desktop trong các vị trí cài đặt thông thường đã kiểm tra; WindowsApps không đọc được (EPERM), nên không kết luận toàn máy chưa cài; native Windows automation pipe không kết nối. M/DAX chưa được thực thi và ảnh workbook không được dùng làm ảnh Power BI.

Phần đã chuẩn bị:

| File | Mục đích |
|---|---|
| [processed_queries.pq](processed_queries.pq) | 5 processed CSV → 7 model tables; timezone, snapshot SLA, dates, nulls |
| [data_model.md](data_model.md) | Grain, 1:* relationships, single filter direction và model diagram |
| [measures.dax](measures.dax) | Ticket, SLA, CSAT, backlog, workload/capacity, weekday/weekend measures |
| [dashboard_spec.md](dashboard_spec.md) | Hai trang và business question của từng trang |
| [acceptance_reference.json](acceptance_reference.json) | Python reference cho all/category/priority/owner/month cohorts |
| [desktop_checklist.md](desktop_checklist.md) | Quy trình dựng, mở, đổi path, refresh và kiểm thử native |

## Cần thực hiện trong Desktop

1. Cài/mở Power BI Desktop ở máy có hỗ trợ, tạo blank queries từ từng block M. Đặt ProjectFolder tới repo clone; disable load hai helper queries.
2. Load model tables, đánh dấu dim_date, cấu hình single-direction dimensions → facts. Không nối active facts với nhau.
3. Thêm measures riêng lẻ, format counts/rates/hours, tạo hai trang theo spec.
4. Refresh và đối chiếu cả unfiltered counts lẫn cohort references; kiểm tra null owner, zero denominator, date/category/team filters và visual interactions.
5. Save `powerbi/customer_support_analytics.pbix`, reopen và kiểm tra refresh. Capture/export thật hai trang vào `images/powerbi/`; chỉ thêm links vào README sau khi file thực tồn tại và đã kiểm thử.

Không publish lên Power BI Service và không đổi sharing. Mẫu số capacity giữ theo actual handler/work date; category/priority chỉ filter ticket fact. Trong model, tạo labels rõ để tránh hiểu utilization là capacity riêng cho nhóm ticket đang chọn.
