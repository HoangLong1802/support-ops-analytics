# Data dictionary

Exactly five raw datasets. Timestamps are UTC instants serialized as YYYY-MM-DDTHH:MM:SSZ; dates are local Asia/Ho_Chi_Minh dates. Blank CSV cells represent null. Numeric inputs must be integers; CSAT may serialize as 4.0 but must have an integer-valued score.

| Dataset | Grain / key |
|---|---|
| agents | One agent; agent_id |
| sla_policies | One channel/priority policy; policy_id, alternate unique (channel, priority) |
| tickets | One ticket snapshot; ticket_id |
| ticket_work_logs | One ticket/handler/local-date entry; work_log_id, alternate (ticket_id, agent_id, work_date) |
| workforce_daily | One hired agent/local date, including off days; (agent_id, work_date) |

| Dataset | Field | Type / nullable | Meaning and rule |
|---|---|---|---|
| agents | agent_id | Text / no | AGT001–AGT018 |
| agents | team | Text / no | general_support, technical_support, billing_account |
| agents | hire_date | Local Date / no | Employment begins; tenure is derived and never stored raw |
| sla_policies | policy_id | Text / no | Stable policy key |
| sla_policies | channel | Text / no | email, chat, phone, web |
| sla_policies | priority | Text / no | low, medium, high, urgent |
| sla_policies | first_response_target_minutes | Integer / no | Positive elapsed response target |
| sla_policies | resolution_target_minutes | Integer / no | Positive elapsed resolution target |
| tickets | ticket_id | Text / no | TKT000001–TKT015000 before duplicated copies |
| tickets | assigned_agent_id | Text / unresolved only | Final snapshot owner; known, hired agent; required for completed |
| tickets | policy_id | Text / no | Known policy, matching channel/priority |
| tickets | channel | Text / no | Contact channel; safe case/space normalization allowed |
| tickets | priority | Text / no | Priority domain above |
| tickets | customer_type | Text / no | standard, premium, vip |
| tickets | category | Text / no in clean | Approved hierarchy below |
| tickets | subcategory | Text / no in clean | Must form valid pair with category |
| tickets | created_at | UTC Timestamp / no | Creation inside the local coverage window |
| tickets | first_response_at | UTC Timestamp / unresolved only | >= created_at, <= snapshot; completed requires response |
| tickets | resolved_at | UTC Timestamp / unresolved only | >= first_response_at and <= snapshot; unresolved requires null |
| tickets | status | Text / no | open/pending unresolved; resolved/closed completed |
| tickets | reopen_count | Integer / no | >=0; only observed events before snapshot |
| tickets | csat_score | Integer / yes | 1–5, completed only; null means no valid response |
| ticket_work_logs | work_log_id | Text / no | Unique effort entry identifier |
| ticket_work_logs | ticket_id | Text / no | Known retained ticket |
| ticket_work_logs | agent_id | Text / no | Actual handler; may differ from final owner |
| ticket_work_logs | work_date | Local Date / no | Within coverage, hire date and ticket lifecycle; workforce row required |
| ticket_work_logs | handling_minutes | Integer / no | >0 actual effort; agent/day sum <= physical attendance |
| workforce_daily | agent_id | Text / no | Known hired agent |
| workforce_daily | work_date | Local Date / no | Active-agent coverage day |
| workforce_daily | scheduled_minutes | Integer / no | 0 off, or 450/480/510 |
| workforce_daily | absence_minutes | Integer / no | >=0; full absence may equal schedule |
| workforce_daily | shrinkage_minutes | Integer / no | >=0; absence + shrinkage <= schedule |

Approved pairs:

| Category | Subcategories |
|---|---|
| technical_support | login_authentication, performance, integration, bug_error |
| billing | payment_failed, refund, invoice, subscription |
| account_access | password_reset, account_locked, verification, profile |
| product_service_inquiry | feature_question, pricing, availability |
| service_request | configuration, upgrade, cancellation |

SLA targets in minutes, shown as first response / resolution:

| Channel | Low | Medium | High | Urgent |
|---|---|---|---|---|
| phone | 15/2880 | 10/1440 | 5/480 | 2/240 |
| chat | 30/2880 | 20/1440 | 10/480 | 5/240 |
| email | 480/2880 | 240/1440 | 60/480 | 30/240 |
| web | 720/2880 | 360/1440 | 120/480 | 60/240 |

Derived fields are absent from raw tickets. The processed and analytical layers add SLA outcomes, elapsed durations, local creation attributes, backlog age and dimensional keys. Observed event at target equality = MET. Missing event at snapshot age equality = PENDING; strictly beyond target = BREACHED. Overall breaches if either component breaches; MET requires completed and both components MET. Compliance = MET/(MET+BREACHED).

Productive capacity = scheduled − absence − shrinkage. Physical attendance = scheduled − absence. Handling may exceed productive capacity but never physical attendance; zero productive capacity gives null utilization.

Quarantine files preserve source columns plus _source_row (original CSV row number) and quarantine_reason (possibly multiple reasons). The cleaning audit distinguishes exact copies removed, transformed retained rows and excluded rows. Staffing outputs contain observed handling/capacity, four-weekday forecasts, assumptions, required/available equivalent FTE and gap.

