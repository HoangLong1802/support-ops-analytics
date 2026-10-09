# Kiểm tra độc lập từ raw records

Thực hiện ngày 08/10/2026, giữ nguyên KPI và raw CSV. [Receipt](../output/independent_validation.json) lưu records/policies đầy đủ, dòng CSV, phép tính, expected values và sai lệch. [Oracle](../src/independent_validation.py) chỉ dùng thư viện chuẩn csv/datetime/Counter; không import contract, cleaning hoặc verified_metrics để tính expected. [Tests](../tests/test_independent.py) đối chiếu expected với pipeline đang chạy.

## Tính tay các ticket đã chọn

Timestamps là UTC; snapshot 2026-09-30 17:00 UTC = 2026-10-01 00:00 UTC+7. SLA đo elapsed time liên tục. Có event đúng deadline → MET; thiếu event đúng deadline → PENDING; quá deadline → BREACHED. Overall MET yêu cầu completed và cả hai component MET.

| Raw ticket | Phép tính từ timestamps / policy | FR / Resolution / Overall |
|---|---|---|
| TKT000001, resolved, thiếu CSAT | 17:45:38 → 18:23:38 = 38 phút ≤ 240. Đến 05:11:38 hôm sau = 686 phút ≤ 1.440. CSAT blank không tính 0. | MET / MET / MET |
| TKT000002, resolved | 01:04:53 → 01:43:53 = 39 phút ≤ 60. Đến 10:25:53 = 561 phút > 480. CSAT = 4. | MET / BREACHED / BREACHED |
| TKT000531, pending, chưa đóng | 04:51:28 → 05:04:28 = 13 phút ≤ 20. Chưa resolved; age tới snapshot = 30.370.112 giây (351 ngày + 12:08:32), lớn hơn 1.440 phút. | MET / BREACHED / BREACHED |
| TKT014997, pending, thiếu cả response/resolution | Created 2026-09-30 14:13:22; snapshot age = 02:46:38 = 9.998 giây, nhỏ hơn cả 720 và 2.880 phút. Thiếu events hợp lệ của ticket chưa đóng. | PENDING / PENDING / PENDING |
| TKT014933, pending | Response sau 573 phút ≤ 720. Chưa resolved; age tới snapshot 32:33:20 = 117.200 giây < 2.880 phút. | MET / PENDING / PENDING |
| TKT000161, status resolved nhưng thiếu resolved_at | Raw dòng 162: completed lifecycle thiếu timestamp bắt buộc. Không tính duration hoặc SLA bằng age như một ticket hợp lệ; ticket nằm trong quarantine completed_missing_fields, không có trong processed. | Loại khỏi KPI |

Năm ticket được giữ ở trên đều trùng nguyên record raw, không có transformation hoặc duplicate. Tính tay trên riêng mẫu này: total 5, completed 2, backlog 3; FR MET/BREACHED/PENDING = 4/0/1, eligible 4, compliance 100%; resolution và overall = 1/2/2, eligible 3, compliance 1/3. CSAT mean 4 với survey N=1, response rate 1/2; blank score của TKT000001 được loại khỏi mean. Đây là số của mẫu kiểm tra, không thay thế KPI toàn project.

## Đối chiếu toàn bộ processed và bộ số theo filter

Oracle đọc CSV đã làm sạch, tra policies từ raw, so timestamp với deadline bằng datetime và đếm từng ticket. Đây không phải audit lại toàn bộ quyết định cleaning; sáu raw cases ở trên kiểm tra trực tiếp phần đó.

- 14.774 tickets; completed 14.196; backlog 578.
- FR MET/BREACHED/PENDING 12.990/1.783/1.
- Resolution 11.243/3.514/17; overall 9.986/4.772/16.
- Cả 5 category breakdown và 41 cohort All/category/priority/owner/month khớp reference; count sai lệch 0, floating difference dưới 1e-9.
- Technical: 4.357 tickets, 4.352 resolution eligible, 1.760 breaches.
- Weekday 12.240/261 = 46,8965517241/ngày; weekend 2.534/104 = 24,3653846154/ngày; ratio 1,9247203549.

Đối chiếu cohort bằng CSV/Python độc lập chưa chứng minh filter propagation hoặc measures chạy trong Desktop.

## Join có nguy cơ double-counting

TKT000002 có hai work logs: AGT013 60 phút và AGT015 33 phút cùng ngày 01/10/2025. Ticket có một resolution breach; join trực tiếp logs rồi COUNT(*)/SUM(breach) sẽ tính nó hai lần. Handling effort vẫn là 93 phút.

Trên toàn dữ liệu, ticket LEFT JOIN logs tạo 17.931 dòng thay cho 14.774 IDs (tăng 3.157). Resolution breaches bị đếm 4.483 thay cho 3.514, breach rate thành 25,0307091% thay cho 23,8124280%. Không dùng COUNT(DISTINCT ticket_id) riêng cho total rồi để numerator nhân theo logs.

Gom logs theo ticket_id trước khi join giữ 14.774 dòng và 1.211.023 handling minutes. Model BI giữ facts riêng, dimension→facts, single direction; không nối active ticket→logs. Tests kiểm tra join lỗi và join đúng bằng pandas, expected được đóng băng từ phép đếm CSV riêng.

## Calendar và ngày không có ticket

datetime tạo 365 local dates [2025-10-01, 2026-10-01), trong đó 261 weekday và 104 weekend. Raw ticket đầu tiên lúc 2025-09-30 17:45:38 UTC thuộc 01/10 local: không được nhóm theo ngày UTC.

Thực tế có 0 zero-ticket days. Kiểm tra không chỉ dựa vào dữ liệu này: fixture trong memory bỏ tất cả ticket tạo ngày 01/10/2025 (thứ Tư). Calendar vẫn 261 weekday/104 weekend, weekday có đúng 1 zero day, denominator không giảm xuống 260; weekend không đổi. Oracle và live summarize khớp ratio sau perturbation. Không sửa CSV và không báo zero day của fixture thành observation thật.

Rà source DAX thấy Total Tickets dùng COUNTROWS trực tiếp, trả BLANK khi cohort rỗng theo [Microsoft COUNTROWS](https://learn.microsoft.com/en-us/dax/countrows-function-dax). Đã sửa measure hiện có thành COALESCE(COUNTROWS(...), 0) để Average Daily Tickets trả 0 cho ngày có coverage nhưng không có arrivals. Chưa thực thi sửa này trong Desktop; cần native empty-cohort check. DIVIDE ở rate vẫn giữ BLANK khi eligible/calendar denominator bằng 0.

## Audit các tests trước đó

| Nhóm kiểm tra | Mức độc lập / giới hạn |
|---|---|
| test_kpi_export_denominators_and_outcome_partitions | summarize so saved KPI do cùng implementation sinh; hữu ích kiểm tra stale output nhưng không là oracle độc lập. Partition/ratio chỉ kiểm tra tính nhất quán. |
| Workbook KPI parity và validate_delivery | Dùng summarize/export helpers chung; kiểm tra đóng gói, không chứng minh arithmetic. |
| test_dax_contract_matches_canonical_formulas | So chuỗi source; có thể PASS khi cùng sai định nghĩa. Không chạy engine DAX. |
| Contract/rule masks và clean comparison | Phần lớn tái dùng rules/clean; kiểm tra tái tạo và consistency, không audit độc lập toàn bộ raw cleaning. |
| SLA deadline fixtures | Expected labels literal, đúng hạn và lệch 1 giây, missing event ở/tới quá deadline: kiểm tra độc lập có giá trị đã có sẵn. |
| Quarantine original fields, FK uniqueness, handler attribution | Có kiểm tra trực tiếp source/grain và literal counts; hữu ích ngoài implementation. |
| Staffing future perturbation | Kiểm tra không dùng future input bằng thay đổi dữ liệu; độc lập về hành vi. |

Bổ sung 6 tests: hand calculations/live pipeline; full aggregate/std-library oracle; risky join và safe grain; calendar zero-day perturbation/live pipeline; 41 cohorts independent; completed missing timestamp excluded. Hai runner tests bổ sung kiểm tra namespace database và comparator phát hiện số sai/thiếu; không thay thế SQL execution.
