# Cleaning report

Every source row is retained, removed as a redundant exact copy, or quarantined. Field transformations do not reduce row counts.

| Dataset | Raw | Exact copies removed | Quarantined | Processed | Reconciled |
|---|---:|---:|---:|---:|---|
| agents | 18 | 0 | 0 | 18 | PASS |
| sla_policies | 16 | 0 | 0 | 16 | PASS |
| tickets | 15,105 | 75 | 256 | 14,774 | PASS |
| ticket_work_logs | 18,278 | 36 | 341 | 17,901 | PASS |
| workforce_daily | 6,327 | 0 | 9 | 6,318 | PASS |

## Safe field transformations

- channel_normalized: 120
- category_restored: 60
- invalid_csat_set_null: 23
- unique_transformed_ticket_rows: 203

## Quarantine reasons

Reason counts may overlap; quarantine totals above count distinct source rows. Original values, source CSV row number (header = row 1) and all detected reasons are preserved.

| Dataset | Reason | Rows |
|---|---|---:|
| tickets | conflicting_key | 60 |
| tickets | invalid_hierarchy | 60 |
| tickets | completed_missing_fields | 38 |
| tickets | missing_hierarchy | 60 |
| tickets | unknown_owner | 15 |
| tickets | response_order | 23 |
| ticket_work_logs | unknown_ticket | 295 |
| ticket_work_logs | missing_workforce | 46 |
| ticket_work_logs | invalid_handling | 27 |
| workforce_daily | invalid_capacity | 9 |

## Validation

PASS: unique keys, canonical domains, valid hierarchy, foreign keys, UTC timestamp order, snapshot lifecycle, CSAT, integer reopens, workforce capacity and handling feasibility. Dependent logs losing a clean parent are quarantined. Legitimate extreme durations are retained.

Raw SHA256 before and after cleaning: identical.
