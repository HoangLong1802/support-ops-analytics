# Bàn giao / Delivery Report

Cập nhật local ngày 08/10/2026 theo yêu cầu tiếp tục: giữ scope và bộ 42 KPI; không sửa CV, không push/deploy/publish. Năm raw CSV frozen không thay đổi. Không có database bên ngoài bị sửa.

## Kết quả thực tế của lần tiếp tục

| Phần | Đã thực hiện | Trạng thái nghiệm thu |
|---|---|---|
| MySQL | Kiểm tra PATH, service, common install paths, cổng 3306, Docker; gọi runner không dry-run, lưu exit/error. Runner bổ sung database mới dành riêng và automatic reconciliation. | BLOCKED trước kết nối: thiếu client/server khả dụng. Không có SQL execution hoặc MySQL version. |
| Power BI | Thử Computer Use thật; rà M/model/DAX; sửa zero-cohort count; thu spec về đúng 2 trang, hướng dẫn dựng và 41 filter checks. | BLOCKED trước chọn cửa sổ. Chưa dựng model/report hoặc chạy M/DAX; không có PBIX/screenshot. |
| Kiểm tra độc lập | Tính tay 5 raw tickets + 1 case quarantine; oracle thư viện chuẩn, 41 cohorts, category/SLA/daily demand, risky join và zero-day perturbation; audit tests cũ. | PASS cho phần arithmetic/Python đã chạy. Không thay thế SQL hoặc Desktop engine validation. |
| Excel native | EXCEL.EXE tồn tại; thử native window inventory thất bại. Parser/workbook tests và checklist native có sẵn. | Chưa mở/kiểm tra filter/chart/display trong Excel thật; chưa có native screenshot. |

Evidence mới: [independent receipt](../output/independent_validation.json), [independent tests](../output/independent_tests.txt), [full 31-test log](../output/regression_validation.txt), [MySQL execution receipt](../output/mysql/execution_receipt.json), [MySQL actual attempt](../output/mysql/attempt.txt), [runtime probe](../output/runtime_probe.json), [native probe](../output/native_probe.json). Các receipt giữ trạng thái chưa chạy riêng với kết quả arithmetic PASS.

## Kiểm tra độc lập và phát hiện

[Phép tính tay, source records và audit tests](independent_validation.md) mô tả toàn bộ arithmetic. Năm raw tickets retained không có transformation hoặc duplicate, cover đúng hạn, breach, chưa đóng, missing events và missing CSAT; TKT000161 status resolved thiếu resolved_at được quarantine.

Oracle csv/datetime không dùng production contract/cleaning/summarize để tính expected. Full counts, 9 SLA outcome counts, eligible/compliance, 5 category breakdown và weekday/weekend daily demand khớp outputs. Cả 41 acceptance cohorts khớp. Tests riêng so oracle với live summarize và frozen hand values với live ticket_metrics. Tolerance 1e-9, counts đúng tuyệt đối.

Join ticket LEFT JOIN logs tạo 17.931 rows thay cho 14.774; breaches bị tính 4.483 thay cho 3.514. TKT000002 minh họa 2 logs, một ticket breach, effort 60+33=93 phút. Preaggregate logs theo ticket giữ 14.774 rows và 1.211.023 handling minutes. Đã thêm test phát hiện cả inflated count và numerator, không chỉ distinct total.

Calendar thực có 365 ngày, 261 weekday/104 weekend, actual zero-ticket days = 0. Fixture trong memory bỏ tất cả arrivals của ngày đầu vẫn giữ denominator 261 và tạo đúng 1 zero weekday; oracle và live pipeline khớp. Không sửa source hoặc báo fixture thành dữ liệu thật.

Audit xác định workbook parity/KPI export/contract checks chủ yếu dùng lại production helpers, không đủ là oracle độc lập. Existing literal deadline fixtures và future-input staffing perturbation có giá trị độc lập. Bổ sung 6 independent tests và 2 MySQL runner safety/comparator tests; toàn bộ suite 31 tests OK, sau các chỉnh sửa cuối đã rerun 6 independent và 2 runner tests, đều OK. Runner tests không thực thi SQL.

Rà DAX sửa Total Tickets từ COUNTROWS sang COALESCE(COUNTROWS(...),0), vì empty table trả BLANK theo [Microsoft COUNTROWS](https://learn.microsoft.com/en-us/dax/countrows-function-dax). Đây là sửa measure hiện có cho zero-day/empty-cohort behavior, chưa native-tested. Định nghĩa SLA rates giữ BLANK ở zero eligible denominator. Không tạo KPI mới.

## MySQL: lỗi chính xác và việc cần người dùng làm

Actual command: python src/run_mysql.py --database support_ops_verify_20261008_followup. Exit 1: mysql client unavailable: MYSQL_EXE unset and mysql not in PATH. mysql/mysqld/docker PATH probes đều exit 1 “Could not find files for the given pattern(s)”; Docker common executable ENOENT; không có service MySQL/MariaDB/Docker; localhost:3306 ECONNREFUSED. Version client/server = null, reconciliation NOT_RUN, scripts executed = 0.

[SQL guide](sql_analysis_guide.md) có từng bước: cài/chỉ client và dedicated local instance, khởi động, cấu hình LOCAL trên instance dành riêng, set private env rồi chạy tên database mới. Không cần đưa password vào chat/repo.

Runner chỉ chấp nhận support_ops_verify_<unique>, từ chối database đã tồn tại trước DDL, không DROP/TRUNCATE, không thay server settings. Sau khi engine khả dụng, runner chạy toàn bộ 8 scripts, ghi client/server version, lệnh, từng result set rồi đối chiếu 33 values với oracle đã khớp Python. Missing/duplicate/wrong result groups đều FAIL comparator. Cần đọc import warnings và validation detail queries trước full acceptance; EXECUTED_RECONCILED không tự là full SQL PASS.

Dry-run source đã refresh theo database riêng; vẫn chỉ là prepared SQL. Không dùng các file này làm bằng chứng query đã chạy.

## Power BI: blocker và bàn giao native

sky.list_apps thất bại: Computer Use native pipe is unavailable: failed to connect native pipe: The system cannot find the file specified. (os error 2). Đây là bước inventory trước mở/chọn Power BI window, không phải M/DAX hoặc refresh error. Common Desktop paths ENOENT; WindowsApps EPERM nên không khẳng định toàn máy chưa cài Power BI.

Chỉ giữ Operations Overview và SLA/Demand. [Desktop checklist](../powerbi/desktop_checklist.md) ghi chính xác thứ tự 9 named M blocks (2 helpers disable load, 7 loaded tables), 8 active 1:* single-direction relationships, DAX measures, visual fields, slicers, 41 cohort comparisons, zero-cohort case, save/reopen/refresh và capture thật hai trang. [Model](../powerbi/data_model.md), [M](../powerbi/processed_queries.pq), [DAX](../powerbi/measures.dax), [spec](../powerbi/dashboard_spec.md).

Source review và độc lập Python references đã có; relationships, filter direction, engine measures và report visuals chưa kiểm tra trong Desktop. Không gọi implementation package là dashboard hoàn thành. Chưa có genuine powerbi/customer_support_analytics.pbix hoặc images/powerbi/*.png.

## Excel và workbook renders

output/customer_support_analysis.xlsx vẫn là workbook thật 14 sheets, 42 matched KPI values, 5 Excel chart objects, tables/filters/freeze panes và conditional formatting. Summary tĩnh không có formulas/PivotTables; không tuyên bố native recalculation.

Full tests đã kiểm tra XLSX structure/export/parity. Artifact Tool visual review/render của lần trước vẫn là evidence layout từ workbook, không phải Excel interaction. images/workbook/workbook_overview.png và workbook_demand.png giữ nhãn workbook render.

EXCEL.EXE tồn tại tại Office16; native inventory bị cùng pipe error trước mở workbook. Codex Document Control trả “No connected Codex document sessions were found”, nên không có đường add-in thay thế. CScript “Loading your settings failed (Access is denied)” là probe cũ, không phải lần mở thành công mới. [Excel native checklist](excel_native_checklist.md) ghi cách mở, kiểm tra formula bar, 5 charts, filters/clear filters/freeze, hiển thị, rounding, version và capture thật. Chưa có native Excel screenshot.

## Sản phẩm đã có và lịch sử validation

[SQL source](../sql/README.md) · [Workbook](../output/customer_support_analysis.xlsx) · [Data Quality](data_quality_report.md) · [42 KPI contracts](kpi_definitions.md) · [Workbook renders](../images/workbook/README.md) · [Power BI package](../powerbi/README.md) · [Case study](portfolio_case_study.md).

Trước lần tiếp tục: full pipeline exit 0, 23 tests; 14 sheets/5 charts/42 KPI workbook parity, raw hashes unchanged; portable openpyxl fallback đã kiểm tra. [Historical pipeline log](../output/pipeline_validation.txt), [fallback receipt](../output/fallback_validation.json). Lần tiếp tục chạy regression 31 tests và independent audit, không gọi đó là full pipeline rerun.

Claims không đổi: Technical breaches 1.760/3.514 = 50,09% contribution; volume 4.357/14.774 = 29,49%; within-group 1.760/4.352 = 40,44%. Weekday 12.240/261 = 46,90/ngày; weekend 2.534/104 = 24,37/ngày; daily ratio 1,92x, total ratio 4,83x. Dữ liệu synthetic, không là business impact thật.

Không sửa CV và không thực hiện Git commit/push/deploy. Không công nhận hoàn thành bất cứ phần native nào chưa kiểm thử.
