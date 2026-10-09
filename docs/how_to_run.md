# Hướng dẫn chạy / How to Run

## Python và Excel

Chạy tại repository root. Không chạy stage `raw`: năm nguồn mô phỏng đã frozen.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src/run_pipeline.py
```

Để dùng đúng library versions đã kiểm thử, cài `python -m pip install -r requirements-lock.txt`; [lock file](../requirements-lock.txt) ghi phiên bản cụ thể. Pillow dùng để kiểm tra ảnh trong validate_delivery.py.

Requirements: Python 3.12+, pandas >=3.0,<4, NumPy >=2,<3, openpyxl >=3.1,<4. Runtime kiểm thử hiện tại và exit codes nằm trong [validation receipt](../output/validation_receipt.json). Workbook xuất số đã tính bằng Python, không có PivotTable và không gọi exported values là công thức Excel. Mở sheet README để đọc overview, Executive_KPIs để xem 42 KPI.

Thứ tự: raw quality → cleaning/quarantine → processed validation → canonical KPI → staffing → BI tables → case-study claims/docs → workbook → tests. Raw SHA256 phải giữ nguyên. Expected processed rows: 18 agents, 16 policies, 14,774 tickets, 17,901 work logs, 6,318 workforce rows. Ticket → policy/owner joins phải giữ 14,774 rows.

Workbook dùng Artifact Tool nếu Node và package `@oai/artifact-tool` khả dụng; nếu thiếu, backend openpyxl hiện có tạo cùng analytical tables và 5 charts. Artifact Tool là dependency của môi trường Codex, không yêu cầu người dùng tải package không có registry công khai. Python/openpyxl là đường tái chạy độc lập trên máy khác.

Trong Codex Windows, có thể đặt `NODE_EXE` tới Node của runtime và tạo junction `node_modules` tới dependency loader theo hướng dẫn skill. Không commit junction/dependencies. [Builder](../src/workbook_builder.mjs) render previews từ workbook thực khi backend Artifact Tool chạy. Backend openpyxl không cập nhật PNG; khi dùng fallback cần export/capture lại trong Excel, không coi ảnh cũ là ảnh mới.

Các output có thể kiểm tra ngay:
- [Workbook](../output/customer_support_analysis.xlsx), filter/table/freeze panes trên các trang phân tích.
- [42 KPI](../data/analytics/verified_kpis.csv), [claim output](../data/analytics/case_study_claims.json).
- [Data Quality](data_quality_report.md), [cleaning audit](../data/analytics/cleaning_audit.json).
- [Case study](portfolio_case_study.md) và [findings](05_business_insights.md).

Chạy riêng: `python src/case_study.py` cập nhật claim/docs; `python src/export_excel.py` cập nhật Excel; `python -m unittest discover -s tests -v` kiểm tra. Test deterministic generation tạo dữ liệu trong memory, không ghi đè raw, và có thể mất nhiều phút.

## MySQL

Giữ MySQL 8.0.16+ để CHECK constraints được enforce. MySQL native chưa được chạy trong phiên này. [SQL run guide](sql_analysis_guide.md) ghi setup, thứ tự, outputs và lỗi.

## Power BI

[Implementation package](../powerbi/README.md) gồm M queries, model, DAX, report specification và 41 filter reference cases. Chưa có PBIX và chưa native-test M/DAX. Không publish Power BI Service.

## Lỗi thường gặp

| Lỗi | Cách xử lý |
|---|---|
| Python/module không tìm thấy | Dùng .venv Python, cài requirements, chạy tại repo root |
| Frozen raw checksum differs | Khôi phục đúng CSV đã commit; không generate để bỏ qua mismatch |
| Saved KPI differs | Chạy full pipeline theo thứ tự, không sửa số trong workbook |
| Thiếu Artifact Tool | Python fallback tạo XLSX; cần native Excel để tạo ảnh mới |
| Workbook đang mở khi export | Đóng file hoặc lưu bản đang sửa trước; pipeline ghi đúng output path |
| MySQL LOCAL INFILE disabled | Dùng local_infile trên dedicated local database đã cho phép; không đổi cấu hình service công khai |
| Unknown CSV path | Chạy run_mysql.py --dry-run để thay path theo checkout |
| BI refresh báo file missing | Đổi ProjectFolder trong Power Query rồi Refresh; xem data model |
| BI slicer đổi ticket nhưng utilization không đổi | Category/channel chỉ filter ticket fact; capacity là full agent/work-date scope |

Receipt là evidence của phiên bàn giao này. Sau một lần rerun mới, lưu console log bằng `python src/run_pipeline.py 2>&1 | Tee-Object -FilePath output/pipeline_validation.txt` trong PowerShell, rồi chạy `python src/validate_delivery.py --pipeline-log output/pipeline_validation.txt` để kiểm tra persisted outputs. Nếu dùng Python fallback, PNG chưa được cập nhật nên phải tạo lại ảnh trước khi ghi một receipt mới cho ảnh.
