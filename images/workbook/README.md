# Ảnh từ workbook thực

Hai PNG được render bằng `@oai/artifact-tool` từ nội dung và native chart objects của workbook đã xuất: [customer_support_analysis.xlsx](../../output/customer_support_analysis.xlsx). Đây là **workbook renders**, chưa phải screenshots capture trong Microsoft Excel. Không dựng HTML/Python dashboard để giả Excel.

![KPI Overview](workbook_overview.png)

Chú ý Resolution SLA compliance thấp hơn First Response. Backlog là snapshot; CSAT phản ánh respondents. Trang này nằm ở sheet README.

![Demand](workbook_demand.png)

Monthly ticket volume đủ 12 tháng; Change_Percent kỳ đầu để trống. Month labels giữ thứ tự thời gian. Weekday/weekend daily ratio nằm trong bảng phía dưới và claim output.

Nguồn số là pipeline Python, exported static results. PNG không thay thế XLSX. Cần capture lại trong Excel native khi công cụ Windows hoạt động; không cập nhật nhãn thành screenshot trước bước đó.
