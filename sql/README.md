# SQL / MySQL

Chạy tại repository root theo thứ tự file đánh số 01 → 06. MySQL 8.0.16+; native execution chưa được kiểm thử trong phiên này.

1. [Schema](01_data_model.sql)
2. [Import processed CSV](../database/import.sql), chuẩn bị path bằng `python src/run_mysql.py --dry-run`
3. [Views và KPI definitions](02_kpi_definitions.sql)
4. [Validation](../database/validation.sql)
5. [Operations](03_operations_analysis.sql)
6. [Customer / CSAT](04_customer_analysis.sql)
7. [Workforce / Staffing](05_workforce_analysis.sql)
8. [Kiểm tra claim cũ](06_claim_verification.sql)

Grain: ticket snapshot; actual ticket/handler/date work log; agent/date capacity. Outcome/effort facts được aggregate riêng để không double-count. Query comments giải thích business question; run guide nêu denominator, cách đọc và giới hạn theo nhóm.
