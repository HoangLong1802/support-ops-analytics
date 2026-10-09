# Power BI

[English](README.md) | **Tiếng Việt**

- `customer_support_operations.pbix`: báo cáo (5 trang) và mô hình dữ liệu.
- `processed_queries.pq`: mã Power Query (M). Đọc `data/processed/*_clean.csv` qua đường dẫn `ProjectFolder`; hãy đổi đường dẫn này nếu clone repo sang chỗ khác.
- `measures.dax`: các measure DAX. Gồm cả 68 measure; 13 measure thêm sau nằm cuối file.
- `acceptance_reference.json`: số liệu tham chiếu tính bằng Python.

## Mô hình

Bảy bảng theo dạng star: `fact_tickets`, `fact_work_logs`, `fact_workforce_daily`, `dim_date`, `dim_agents`, `dim_sla_policies` và `dim_categories`. Tám quan hệ nhiều-một, lọc một chiều. Các bảng fact không nối với nhau. Bảng ngày tự động của Power BI vẫn đang bật.

## Các trang

1. Tổng quan: lượng ticket, tuân thủ SLA, backlog, CSAT
2. SLA và nhu cầu: theo priority, thứ trong tuần, giờ trong ngày
3. Nhân sự: ticket mỗi agent, thời gian xử lý, vắng mặt, shrinkage
4. Trải nghiệm khách hàng: CSAT và reopen rate theo tháng, danh mục, kênh
5. Backlog và rủi ro: độ tuổi của ticket chưa giải quyết

## Ghi chú

- Backlog là ảnh chụp ticket chưa giải quyết tại 01/10/2026, không phải lịch sử.
- Tuân thủ SLA giải quyết = đạt / (đạt + vi phạm). Ticket đang chờ không nằm trong mẫu số.
- Tỷ lệ ở cấp team hoặc tổng được tính lại từ số đếm, không lấy trung bình các tỷ lệ.
- Chưa làm drill-through và tooltip tùy chỉnh.
- Chưa publish lên Power BI Service. Chưa có bản `.pbip`.
