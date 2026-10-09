# Customer Support Operations Analytics

This case study examines support demand, service level agreement (SLA) outcomes, snapshot backlog, customer satisfaction and daily handling capacity. Five synthetic datasets cover eighteen agents in three teams from October 2025 to September 2026. Python validates and cleans the records, preserves exclusions in quarantine, and produces reproducible analytical outputs. MySQL scripts describe the same model and business questions. The Excel workbook contains measured results, definitions, cohort sample sizes and charts. The analysis separates final ticket ownership from actual handling, breach contribution from within-group breach rate, and elapsed resolution time from effort. These observations demonstrate analytical choices on simulated data and do not establish business impact. Power BI queries, DAX and acceptance references are included; native report completion is tracked separately.

## Tổng quan / Overview

Project giúp support manager đọc nhu cầu ticket, SLA breaches, aged backlog và workload/capacity trước khi điều chỉnh coverage. Tôi xây pipeline kiểm tra → cleaning/quarantine → KPI → SQL/Excel với **5 nguồn mô phỏng, {{total_tickets:,}} cleaned tickets**. [Nguồn và quyền sử dụng](docs/data_source.md)

## Sản phẩm / Deliverables

| Sản phẩm | Mở ở đâu | Trạng thái |
|---|---|---|
| SQL MySQL | [Schema, import, validation và analysis](sql/README.md) | Source hoàn chỉnh; chưa chạy native MySQL |
| Excel | [customer_support_analysis.xlsx](output/customer_support_analysis.xlsx) | Workbook thực, 14 sheet; summary tĩnh, refresh bằng script |
| Data Quality | [Báo cáo và reconciliation](docs/data_quality_report.md) | Tính từ dữ liệu trong repo |
| Power BI | [M, DAX, model và hướng dẫn](powerbi/README.md) | Implementation package; chưa có PBIX/dashboard đã kiểm thử |
| Ảnh workbook | [Preview và nguồn render](images/workbook/README.md) | Render trực tiếp XLSX bằng Artifact Tool; chưa capture trong Excel |
| Portfolio | [Case study để tích hợp](docs/portfolio_case_study.md) | Việt/Anh, có evidence links |

## Câu hỏi phân tích / Business Questions

- Technical chiếm bao nhiêu volume, bao nhiêu breaches và có breach rate bao nhiêu trong chính nhóm?
- Weekday demand khác weekend theo average daily arrivals như thế nào?
- Backlog đã già đến mức nào; CSAT phản ánh bao nhiêu completed tickets?
- Final-owner outcomes khác actual-handler workload ra sao?

## Kết quả chính / Key Findings

- **Technical:** {{technical_ticket_share:.2%}} ticket volume, {{technical_breach_share:.2%}} resolution breaches; within-group breach rate **{{technical_breach_rate:.2%}}**. [Evidence](data/analytics/category_service_summary.csv)
- **Demand:** weekday {{weekday_average:.2f}} ticket/ngày, weekend {{weekend_average:.2f}}, ratio **{{weekday_weekend_ratio:.2f}}x**; mẫu số là {{weekday_days:,}} và {{weekend_days:,}} calendar days. [Evidence](data/analytics/demand_day_type.csv)
- **SLA:** response compliance {{fr_sla_compliance:.2%}}, resolution {{resolution_sla_compliance:.2%}}, overall {{overall_sla_compliance:.2%}}; mỗi KPI có eligible denominator riêng. [Definitions](docs/kpi_definitions.md)
- **Backlog:** {{backlog_over_48_hours:,}}/{{backlog:,}} ticket >48h tại snapshot; không phải historical backlog trend. [Analysis](sql/03_operations_analysis.sql)
- **CSAT:** {{average_csat:.2f}}/5 từ {{csat_responses:,}} survey, response rate {{csat_response_rate:.2%}}. [Evidence](data/analytics/verified_kpis.csv)

[5 phát hiện và 3 đề xuất](docs/05_business_insights.md) phân biệt quan sát với giả thuyết. Simulation không chứng minh tác động kinh doanh; case mix và nonresponse giới hạn so sánh agent.

## Chất lượng dữ liệu / Data Quality

Từ 15,105 raw ticket rows, pipeline bỏ 75 exact copies, quarantine 256 rows và giữ 14,774 ticket. Chuẩn hóa 120 channel values, phục hồi 60 category từ subcategory xác định duy nhất, đặt 23 CSAT ngoài phạm vi thành null. Không điền missing timestamps, không bỏ valid long durations và không join unaggregated work logs vào ticket KPIs. [Báo cáo đầy đủ](docs/data_quality_report.md)

## Hướng dẫn chạy / How to Run

Python 3.12+, pandas 3.x, NumPy 2.x và openpyxl 3.x. Không cần tạo lại raw.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src/run_pipeline.py
```

[Hướng dẫn chi tiết và lỗi thường gặp](docs/how_to_run.md) · [KPI definitions](docs/kpi_definitions.md) · [Kiểm tra claim cũ](docs/claim_verification.md)

Power BI và MySQL cần kiểm thử native riêng. Chưa có screenshot Power BI. Preview workbook ghi đúng nguồn render. [Trạng thái bàn giao](docs/delivery_report.md)
