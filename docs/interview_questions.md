# Năm câu hỏi manager có thể hỏi

| Câu hỏi | Ý chính để luyện trả lời | Vị trí bằng chứng |
|---|---|---|
| Vì sao không xóa mọi missing/duplicate? | Null timestamp/survey có thể đúng theo lifecycle; exact copy khác ambiguous identity. Giữ facts hợp lệ, quarantine phần không xác định được. | [Data Quality](data_quality_report.md), [cleaner](../src/clean_data.py), cleaning_audit.json |
| Technical 50,09% có nghĩa đội Technical kém nhất không? | Đây là contribution share; volume 29,49%, within-group rate 40,44%. Case mix và policy targets chưa điều chỉnh, simulation mã hóa độ khó khác nhau. | [Category output](../data/analytics/category_service_summary.csv), [SQL claim](../sql/06_claim_verification.sql) |
| Vì sao weekday/weekend 1,92x chứ không 4,83x? | Average daily: 12,240/261 và 2,534/104; total ratio chịu số ngày 5/2. Coverage 365 ngày từ contract, giữ zero dates. | [Daily output](../data/analytics/demand_day_type.csv), [claim generator](../src/case_study.py) |
| Làm sao tránh double-count và hiểu nhầm utilization? | Ticket outcomes theo final owner; handling theo actual handler/date. Aggregate facts riêng, dimensions filter facts một chiều; capacity không thuộc category. | [Model](../powerbi/data_model.md), [KPI code](../src/verified_metrics.py), output tests |
| Dự án đã thực sự làm được gì, còn thiếu gì? | Python, cleaning/quarantine, SQL source, workbook và renders đã có; native MySQL/M/DAX/PBIX/screenshots chưa kiểm thử. Đề xuất chưa phải business impact. | [Receipt](../output/validation_receipt.json), [delivery report](delivery_report.md), [Desktop checklist](../powerbi/desktop_checklist.md) |

Không học thuộc claim thành trải nghiệm làm việc tại công ty. Dùng code/output để giải thích lựa chọn và giới hạn.
