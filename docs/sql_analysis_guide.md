# SQL MySQL / Hướng dẫn thực thi và đối chiếu

Ngày 08/10/2026 đã gọi runner thực, exit 1 trước khi kết nối vì mysql client unavailable: MYSQL_EXE unset and mysql not in PATH. Không có database được tạo/import, không có query chạy trên engine, không có MySQL version để báo cáo. [Attempt](../output/mysql/attempt.txt), [execution receipt](../output/mysql/execution_receipt.json), [runtime probe](../output/runtime_probe.json).

Kiểm tra PATH mysql/mysqld/docker đều exit 1: Could not find files for the given pattern(s). Docker executable common path ENOENT; service inventory không có MySQL/MariaDB/Docker; 127.0.0.1:3306 ECONNREFUSED. Common MySQL install paths ENOENT. Đây là bằng chứng về môi trường đã kiểm tra, không khẳng định mọi custom path hoặc port trên máy đều không có MySQL.

## Bước người dùng cần thực hiện

1. Cài hoặc chỉ đường dẫn MySQL Server + mysql client 8.0.16 trở lên; khởi động dedicated local development instance. Nếu bạn có instance ở custom port/path thì dùng instance đó với quyền chỉ cho database dự án mới.
2. Server của instance dùng cho project cần cho phép local_infile; client runner dùng --local-infile=1. Không đổi server-global setting của một instance dùng chung. Xem [MySQL LOCAL requirements](https://dev.mysql.com/doc/refman/8.4/en/mysql-command-options.html).
3. Cấu hình private credentials trong phiên local, không gửi password vào repo/chat/screenshot. Account cần quyền tạo database dự án, CREATE TABLE/VIEW, SELECT, INSERT. Runner không tạo account hoặc sửa quyền.
4. Chạy từ repo root:

```powershell
$env:MYSQL_EXE = "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
$env:MYSQL_HOST = "127.0.0.1"
$env:MYSQL_PORT = "3306"  # đổi nếu dedicated instance dùng port khác
$env:MYSQL_USER = "support_analyst"
# Đặt MYSQL_PWD riêng trong phiên local, không in giá trị.
python src/run_mysql.py --database support_ops_verify_20261008_run1
```

Tên database bắt buộc có prefix support_ops_verify_ và chỉ lowercase/digit/underscore, tối đa 64 ký tự. Runner kiểm tra information_schema trước mọi DDL và từ chối database đã tồn tại, kể cả rỗng. Dùng tên mới như run2 khi chạy lại; runner không DROP/TRUNCATE hoặc sửa database khác. Không dùng compatibility SOURCE wrappers để chạy lần này vì wrappers có tên database mặc định cũ.

--no-defaults tránh config client tự động dẫn sang instance khác; --host/port/user lấy từ env. MYSQL_PWD không có trong argv/log. Runner không tự load mysql.env.example.

## Scripts thực thi

| Thứ tự | Source |
|---|---|
| 1 | sql/01_data_model.sql: schema, CHECK/FK, keys |
| 2 | database/import.sql: 5 processed CSV, date/category dimensions |
| 3 | sql/02_kpi_definitions.sql: views và snapshot KPI |
| 4 | database/validation.sql: counts, lifecycle, references, grains, capacity |
| 5 | sql/03_operations_analysis.sql: demand, SLA, duration, backlog |
| 6 | sql/04_customer_analysis.sql: CSAT/reopen cohorts |
| 7 | sql/05_workforce_analysis.sql: workload/capacity/owner outcomes |
| 8 | sql/06_claim_verification.sql: category denominators, calendar daily demand |

[run_mysql.py](../src/run_mysql.py) thay tên database và __PROJECT_ROOT__ trong memory trước khi gửi từng script vào mysql stdin. UTF-8, stored timestamps UTC DATETIME, reporting UTC+7. Sau 8 scripts, runner chạy ba queries reconciliation, lưu 33 giá trị đối chiếu về ticket count, 9 SLA outcome counts, 5 category ticket/eligible/breach sets và weekday/weekend volume/calendar/zero days/average daily demand.

Expected được tính bằng [oracle độc lập](../src/independent_validation.py), đã đối chiếu live Python pipeline. Runner lưu client/server versions, argv không secret, script exit/results và differences vào output/mysql/execution_receipt.json; result sets từng script vào *.txt. Reconcile PASS khi đủ 33 values và differences ≤1e-9. SLA rates/category shares/weekday ratio kiểm tra từ numerator và denominator đã đối chiếu, không chỉ rounded cards.

python src/run_mysql.py --dry-run --database support_ops_verify_20261008_run1 chỉ chuẩn bị paths trong output/mysql/*.sql, không chạy SQL. Các prepared files có tên DB của dry-run và không phải execution results.

## Điều kiện nghiệm thu

Expected rows: agents 18, policies 16, categories 18, dates 365, tickets 14.774, logs 17.901, workforce 6.318. Các detail queries trong validation.txt phải 0 rows; count_matches đều 1; joined_rows=distinct_tickets=tickets_before_join=14.774; các SLA classified counts 14.774. Import SHOW WARNINGS phải không có warning; LOAD DATA LOCAL có thể chuyển lỗi thành warning nên exit 0 chưa đủ.

Receipt EXECUTED_RECONCILED chỉ nói 8 scripts exit 0 và 33 values khớp. validation_detail_review vẫn PENDING cho tới khi đọc tất cả detail results và import warnings. Không ghi full MySQL PASS chỉ từ process exit hoặc comparator.

Unfiltered FR M/B/P 12.990/1.783/1, resolution 11.243/3.514/17, overall 9.986/4.772/16. Technical volume 4.357, eligible 4.352, breaches 1.760. Weekday 12.240/261 và weekend 2.534/104; actual zero days 0. SQL P90/P95 dùng inclusive linear interpolation; snapshot age bins half-open. Xem [independent validation](independent_validation.md).

## Khi lỗi

- mysql client unavailable: sửa MYSQL_EXE tới executable thực. mysql --version kiểm tra client; không thay server bằng SQLite/MariaDB.
- Connection refused: khởi động instance và đúng port; không có engine thì không thể chạy scripts.
- Access denied: người dùng cấu hình account/password/quyền cho database prefix dự án; không đoán credential.
- LOCAL INFILE disabled: cấu hình dedicated instance cho phép LOCAL; không tự sửa instance dùng chung.
- Target database already exists: chọn tên mới, không xóa database cũ.
- Warning/constraint/FK/count mismatch: lưu lỗi, dừng nghiệm thu, điều tra source/import, không disable FK/CHECK.
