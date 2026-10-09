# Chất lượng dữ liệu / Data Quality

Dữ liệu mô phỏng, kỳ 01/10/2025–30/09/2026 theo Asia/Ho_Chi_Minh. Raw giữ nguyên. Missing hợp lệ được giữ theo lifecycle, không điền timestamp hoặc CSAT bằng mean/zero.

## Grain và reconciliation

| Dataset | Key / grain | Raw | Exact copies removed | Quarantine | Processed |
|---|---|---:|---:|---:|---:|
| agents | agent_id | 18 | 0 | 0 | 18 |
| sla_policies | policy_id | 16 | 0 | 0 | 16 |
| tickets | ticket_id | 15,105 | 75 | 256 | 14,774 |
| ticket_work_logs | work_log_id | 18,278 | 36 | 341 | 17,901 |
| workforce_daily | agent_id, work_date | 6,327 | 0 | 9 | 6,318 |

Mỗi raw row đi vào retained, redundant copy hoặc quarantine. Transformations không phải nhóm cộng thêm; 203 ticket được sửa một hoặc nhiều trường.

## Kiểm tra và cách xử lý

| Kiểm tra | Kết quả / số dòng ảnh hưởng | Cách xử lý | Vấn đề còn lại |
|---|---|---|---|
| tickets.exact_duplicate | 75 source rows | Bỏ bản sao nguyên vẹn, giữ một observation | Tách khỏi conflicting versions |
| tickets.conflicting_key | 60 source rows | Quarantine tất cả phiên bản ambiguous | Không có update timestamp để chọn winner |
| tickets.missing_hierarchy | 120 source rows | Phục hồi category nếu subcategory xác định duy nhất; còn lại quarantine | 60 restored category, 60 ambiguous rows |
| tickets.invalid_hierarchy | 60 source rows | Quarantine nếu vi phạm contract; kiểm tra downstream logs | Reason counts có thể chồng lấp; distinct totals ở reconciliation |
| tickets.channel_format | 120 source rows | Trim và lowercase | 120 ticket được chuẩn hóa |
| tickets.unknown_owner | 15 source rows | Quarantine nếu vi phạm contract; kiểm tra downstream logs | Reason counts có thể chồng lấp; distinct totals ở reconciliation |
| tickets.response_order | 23 source rows | Quarantine nếu vi phạm contract; kiểm tra downstream logs | Reason counts có thể chồng lấp; distinct totals ở reconciliation |
| tickets.completed_missing_fields | 38 source rows | Quarantine nếu vi phạm contract; kiểm tra downstream logs | Reason counts có thể chồng lấp; distinct totals ở reconciliation |
| tickets.invalid_csat | 23 source rows | Đặt score ngoài 1–5 thành null; giữ ticket | 23 score không tham gia CSAT |
| ticket_work_logs.exact_duplicate | 36 source rows | Bỏ bản sao nguyên vẹn, giữ một observation | Tách khỏi conflicting versions |
| ticket_work_logs.unknown_ticket | 65 source rows | Quarantine nếu vi phạm contract; kiểm tra downstream logs | Reason counts có thể chồng lấp; distinct totals ở reconciliation |
| ticket_work_logs.invalid_handling | 27 source rows | Quarantine nếu vi phạm contract; kiểm tra downstream logs | Reason counts có thể chồng lấp; distinct totals ở reconciliation |
| workforce_daily.invalid_capacity | 9 source rows | Quarantine nếu vi phạm contract; kiểm tra downstream logs | Reason counts có thể chồng lấp; distinct totals ở reconciliation |
| Processed schema/types/domains/time/FKs/capacity | 0 violations | Validate contract trên retained data | Không chứng minh tính đại diện của simulation |
| Ticket → policy join | 14,774 trước / 14,774 sau; 0 missing targets | many_to_one, left join | Không join raw logs vào ticket counts |
| Ticket → owner join | 14,774 trước / 14,774 sau; 0 unknown non-null owner | Giữ legitimate null owners cho unresolved cases | Final owner khác actual handler |
| Calendar coverage | 365 ngày; 0 zero-ticket days | Calendar từ simulation contract; giữ ngày zero trong denominator | Sau quarantine thiếu 9 workforce agent-days |

## Missing values

| Trường | Raw missing cells | Cách xử lý |
|---|---:|---|
| tickets.category | 90 | Áp dụng missing_required / missing_hierarchy |
| tickets.subcategory | 60 | Áp dụng missing_required / missing_hierarchy |
| tickets.first_response_at | 1 | Cho phép thiếu khi chưa có event/survey; kiểm tra theo status |
| tickets.resolved_at | 632 | Cho phép thiếu khi chưa có event/survey; kiểm tra theo status |
| tickets.csat_score | 7,490 | Cho phép thiếu khi chưa có event/survey; kiểm tra theo status |

## Ảnh hưởng và vấn đề còn lại

Completed tickets phải có owner, response và resolution. Unresolved tickets không được có resolution hoặc CSAT. Không suy dựng lịch sử trạng thái từ snapshot hiện tại.

Quarantine: 256 ticket, 341 work log, 9 workforce row. Log reason counts là 295 unknown_ticket, 46 missing_workforce và 27 invalid_handling; chồng lấp nên không cộng thành distinct rows. Raw chỉ có 65 unknown_ticket, phần tăng sau cleaning do parent tickets bị loại.

Giữ logically valid long durations; mean resolution vì vậy lớn hơn median. Quarantine làm đổi case mix và capacity quan sát. Null CSAT không phải score 0; nonresponse giới hạn diễn giải. Kiểm tra tự động không đánh giá được mức simulation đại diện doanh nghiệp.

Bằng chứng: [contract](../src/contract.py), [cleaner](../src/clean_data.py), [quality audit](../data/analytics/quality_audit.json), [cleaning audit](../data/analytics/cleaning_audit.json), [quarantine](../data/quarantine/).
