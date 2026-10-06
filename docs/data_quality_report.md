# Data quality report

Five synthetic operational sources are profiled before any cleaning. Checks use source records, the approved schema and business rules. Optional lifecycle timestamps and CSAT nulls are profiled separately from contract errors.

Workflow: understand grain → profile values → validate rules → check relationships → classify impact → recommend treatment.

## Source profiles

| Dataset | Key/grain | Rows | Columns | Missing cells | Exact copies | Key unique | Unique affected rows |
|---|---|---:|---:|---:|---:|---|---:|
| agents | agent_id | 18 | 3 | 0 | 0 | True | 0 |
| sla_policies | policy_id | 16 | 5 | 0 | 0 | True | 0 |
| tickets | ticket_id | 15,105 | 14 | 8,273 | 75 | False | 534 |
| ticket_work_logs | work_log_id | 18,278 | 5 | 0 | 36 | False | 101 |
| workforce_daily | agent_id, work_date | 6,327 | 5 | 0 | 0 | True | 9 |

Missing cells above include legitimate optional values; they are not counts of invalid rows. Unique affected rows use the union of rule masks rather than the sum of overlapping issues.

## Issue registry

Secondary field counts exclude exact copies and conflicting-key records to avoid duplicated diagnoses. Conflicting-key counts include every ambiguous version.

| Dataset | Issue | Rows | % of raw rows | Severity | Impact | Treatment |
|---|---|---:|---:|---|---|---|
| tickets | exact_duplicate | 75 | 0.50% | HIGH | Repeated records inflate volume or effort. | AUTO-FIX |
| tickets | conflicting_key | 60 | 0.40% | CRITICAL | Identity is ambiguous; joins cannot select a reliable version. | QUARANTINE |
| tickets | missing_hierarchy | 120 | 0.79% | HIGH | Unknown demand categories affect routing and mix reporting. | REVIEW |
| tickets | invalid_hierarchy | 60 | 0.40% | HIGH | Contract violation can distort service, workload or relationship reporting. | QUARANTINE |
| tickets | channel_format | 120 | 0.79% | LOW | Formatting splits channel groups without changing their meaning. | AUTO-FIX |
| tickets | unknown_owner | 15 | 0.10% | HIGH | Contract violation can distort service, workload or relationship reporting. | QUARANTINE |
| tickets | response_order | 23 | 0.15% | CRITICAL | Contract violation can distort service, workload or relationship reporting. | QUARANTINE |
| tickets | completed_missing_fields | 38 | 0.25% | CRITICAL | Completed lifecycle lacks evidence needed for service metrics. | QUARANTINE |
| tickets | invalid_csat | 23 | 0.15% | MEDIUM | Out-of-domain scores bias satisfaction. | AUTO-FIX |
| ticket_work_logs | exact_duplicate | 36 | 0.20% | HIGH | Repeated records inflate volume or effort. | AUTO-FIX |
| ticket_work_logs | unknown_ticket | 65 | 0.36% | HIGH | Handling refers to a missing or ambiguous ticket. | QUARANTINE |
| ticket_work_logs | invalid_handling | 27 | 0.15% | HIGH | Contract violation can distort service, workload or relationship reporting. | QUARANTINE |
| workforce_daily | invalid_capacity | 9 | 0.14% | CRITICAL | Invalid productive capacity distorts utilization and staffing. | QUARANTINE |

## Types, domains and relationships

Validation includes timestamp/date parsing, integer domains, category/subcategory pairs, policy/channel/priority agreement, agent hire dates, ticket lifecycle, workforce composite keys and handling against physical attendance. String casing is measured before normalization. Completed tickets require owner, response and resolution; unresolved tickets cannot contain resolution or CSAT.

### Date coverage

Active-agent calendar pairs expected: 6,327; missing: 0; extra: 0. Off days are present with zero minutes; pre-hire dates are outside coverage.

## Statistical observations

Logical errors are excluded from duration profiling. Long valid records remain statistical observations and are retained.

| Measure | N | Median | P90 | P95 | P99 | Maximum |
|---|---:|---:|---:|---:|---:|---:|
| First response minutes | 14,908 | 18.00 | 143.00 | 220.00 | 469.93 | 1931.00 |
| Resolution minutes | 14,322 | 373.00 | 1786.80 | 2925.00 | 260887.80 | 506509.00 |
| Snapshot backlog age minutes | 587 | 143878.05 | 350436.97 | 392356.55 | 455481.10 | 506168.53 |
| Handling minutes per entry | 18,215 | 57.00 | 127.00 | 159.00 | 223.00 | 375.00 |

## Integrity evidence

Raw SHA256 before and after assessment: identical.

| File | SHA256 |
|---|---|
| agents.csv | 42a9c17ee4a3a69a9fa7869a9cb6fe529a35e512847830714a7cd582b27ff89d |
| sla_policies.csv | 54dcbf5887fe5237776eb5465407349983dc622ad122c2cbc2792272721acde8 |
| tickets.csv | 8fe7a644d3d21e18fc8df4be6d381640af2fce11cf13412215d5dc9dc2a025a6 |
| ticket_work_logs.csv | 1f427ed46af6f95ddd060c2d4a4721c1ddb8040a31a2588dc70c0f6d00c57efa |
| workforce_daily.csv | 40a666c87c3083c1544fdaed881ecaddd2766d1c6eb8240c8f2ba78fb1a483ac |
