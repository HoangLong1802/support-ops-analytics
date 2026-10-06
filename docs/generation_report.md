# Generation report

All data is synthetic. Pristine validation ran before defects were injected into independent copies.

Runtime: Python 3.12.13, pandas 3.0.6, NumPy 2.5.3. Seed 42; NumPy PCG64 with independent stage streams.
Creation window: 2025-10-01 inclusive through 2026-10-01 exclusive, Asia/Ho_Chi_Minh. UTC snapshot: 2026-09-30T17:00:00Z.

## Row counts

| Dataset | Pristine | Raw |
|---|---:|---:|
| agents | 18 | 18 |
| sla_policies | 16 | 16 |
| tickets | 15,000 | 15,105 |
| ticket_work_logs | 18,215 | 18,278 |
| workforce_daily | 6,327 | 6,327 |

## Executed pristine checks

| Check | Result | Required range |
|---|---:|---|
| fr_breach_rate | 0.121475 | 0.1–0.2 |
| resolution_breach_rate | 0.238537 | 0.15–0.28 |
| overall_breach_rate | 0.324079 | 0.2–0.35 |
| reopen_rate | 0.083867 | 0.08–0.15 |
| csat_response_rate | 0.525154 | 0.45–0.6 |
| average_csat | 4.070957 | 3.8–4.4 |
| backlog_rate | 0.039267 | 0.03–0.06 |
| weekday_weekend_ratio | 1.927218 | 1.7–2.2 |
| median_team_day_utilization | 0.693542 | 0.65–0.85 |

Pristine schema, keys, lifecycle, relationships, workforce and handling feasibility: PASS. Deterministic repeat: PASS.

## Distributions and service durations

- channel: email 33.89%, chat 29.03%, phone 21.71%, web 15.37%
- priority: medium 51.73%, high 23.21%, low 19.87%, urgent 5.19%
- category: technical_support 29.46%, billing 24.71%, account_access 19.05%, product_service_inquiry 15.15%, service_request 11.63%
- customer_type: standard 70.01%, premium 22.05%, vip 7.93%
- status: resolved 74.95%, closed 21.13%, pending 2.00%, open 1.93%
- Peak local hours: 10:00 (1,849 arrivals), 11:00 (1,813 arrivals), 09:00 (1,699 arrivals)
- fr_sla_met: 13177.000000
- fr_sla_breached: 1822.000000
- fr_sla_pending: 1.000000
- resolution_sla_met: 11409.000000
- resolution_sla_breached: 3574.000000
- resolution_sla_pending: 17.000000
- overall_sla_met: 10128.000000
- overall_sla_breached: 4856.000000
- overall_sla_pending: 16.000000
- average_resolution_hours: 116.819297
- median_resolution_hours: 6.216667
- p90_resolution_hours: 29.750000
- p95_resolution_hours: 48.558333
- handling_hours: 20564.900000
- utilization: 0.699076

## Defects applied

- exact_ticket_copies: 75
- conflicting_ticket_ids: 30
- missing_hierarchy: 120
- invalid_pairs: 60
- channel_format: 120
- invalid_csat: 23
- missing_completed_resolution: 38
- response_before_creation: 23
- unknown_owner: 15
- exact_log_copies: 36
- invalid_logs: 27
- invalid_workforce_rows: 9

## Calibration history

Only global simulation parameters change between complete simulation runs; no ticket is edited to hit a target.
- Attempt 1: parameters {"response_scale": 1.0, "response_sigma": 0.85, "resolution_scale": 1.12, "handling_scale": 1.0, "csat_center": 4.3}; observed {"fr_breach_rate": 0.1214747649843323, "resolution_breach_rate": 0.23853700860975774, "overall_breach_rate": 0.3240790176187934, "reopen_rate": 0.08386666666666667, "csat_response_rate": 0.5251543959475401, "average_csat": 4.07095665961945, "backlog_rate": 0.039266666666666665, "weekday_weekend_ratio": 1.927217973373884, "median_team_day_utilization": 0.6935416571967263}; outside ranges {}.

## Frozen raw SHA256

| File | SHA256 |
|---|---|
| agents.csv | 42a9c17ee4a3a69a9fa7869a9cb6fe529a35e512847830714a7cd582b27ff89d |
| sla_policies.csv | 54dcbf5887fe5237776eb5465407349983dc622ad122c2cbc2792272721acde8 |
| tickets.csv | 8fe7a644d3d21e18fc8df4be6d381640af2fce11cf13412215d5dc9dc2a025a6 |
| ticket_work_logs.csv | 1f427ed46af6f95ddd060c2d4a4721c1ddb8040a31a2588dc70c0f6d00c57efa |
| workforce_daily.csv | 40a666c87c3083c1544fdaed881ecaddd2766d1c6eb8240c8f2ba78fb1a483ac |
