# Case study: ticket vi phạm SLA ở đâu?

[English](portfolio_case_study.md) | **Tiếng Việt**

Dữ liệu mô phỏng, nên case study thể hiện phương pháp chứ không phải kết quả kinh doanh.

**Câu hỏi.** Một support manager muốn biết phần nào của vận hành đang vi phạm SLA, backlog đã cũ đến đâu và nhân sự có khớp với nhu cầu hay không.

**Tôi đã làm gì.**
1. Kiểm tra khóa và grain của năm bảng, loại các dòng trùng hoàn toàn và đưa dòng không đáng tin vào file cách ly thay vì xóa.
2. Tính KPI bằng Python và SQL, sau đó bằng DAX. Tôi tách riêng ba cặp khái niệm: người sở hữu cuối của ticket và người thực sự xử lý; tỷ trọng vi phạm của một danh mục và tỷ lệ vi phạm trong chính danh mục đó; thời gian trôi qua và công sức xử lý.
3. Dựng báo cáo Power BI 5 trang và so các KPI chính với phép tính Python độc lập.

**Kết quả.**
- Technical support chiếm 29% ticket nhưng 50% vi phạm SLA giải quyết; SLA của team là 63,6%, các team khác khoảng 81%.
- Ngày thường có lượng ticket gấp 1,9 lần cuối tuần.
- 552/578 ticket backlog quá 48 giờ.
- CSAT 4,07 nhưng chỉ 52% ticket hoàn tất có đánh giá.

**Đề xuất.** Xem hàng đợi technical trước (chuyển giao, cơ cấu priority); đối chiếu thời điểm ticket đến với timestamp xử lý trước khi đổi ca; đọc CSAT cùng tỷ lệ phản hồi. Đây là giả thuyết cần kiểm chứng, không phải cải thiện đã đạt được.

**Giới hạn.** Các quy luật được cài sẵn trong mô phỏng. Reopen rate không phải first-contact resolution. Chưa điều chỉnh case mix. Script MySQL chạy trong CI trên MySQL 8.4, không phải server local.

Liên kết: [KPI](kpi_definitions.md) · [chất lượng dữ liệu](data_quality_report.md) · [báo cáo kiểm tra](test_report.md) · [Power BI](../powerbi/README.vi.md) · [workbook](../output/customer_support_analysis.xlsx)
