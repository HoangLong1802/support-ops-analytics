# Power BI semantic model

Implementation status: import-ready CSVs, measure definitions and the dashboard specification are supplied. A PBIX has not been built or validated in Power BI Desktop.

Import the following files with the listed table names. Load dates as Date, UTC instants as Date/Time, numeric durations as Decimal Number, completed as True/False, identifiers as Text, and integer counts as Whole Number. Timestamps ending in Z are UTC; do not convert using the desktop computer's timezone. SLA outcomes and local calendar fields are computed by the executed Python layer; no DAX calculated columns are required.

| Table | Source | Grain |
|---|---|---|
| dim_date | data/analytics/dim_date.csv | Local reporting date |
| dim_agents | data/processed/agents_clean.csv | Support agent |
| dim_categories | data/analytics/dim_categories.csv | Category/subcategory pair |
| dim_sla_policies | data/processed/sla_policies_clean.csv | Channel/priority policy |
| fact_tickets | data/analytics/ticket_service_metrics.csv | Retained ticket snapshot |
| fact_work_logs | data/processed/ticket_work_logs_clean.csv | Ticket/handler/local date |
| fact_workforce_daily | data/analytics/agent_daily_workload.csv | Agent/local date |

Create active 1:* relationships with single-direction filtering **from dimensions to facts**:

| Dimension key | Fact key |
|---|---|
| dim_date.date_key | fact_tickets.local_created_date |
| dim_date.date_key | fact_work_logs.work_date |
| dim_date.date_key | fact_workforce_daily.work_date |
| dim_agents.agent_id | fact_tickets.assigned_agent_id |
| dim_agents.agent_id | fact_work_logs.agent_id |
| dim_agents.agent_id | fact_workforce_daily.agent_id |
| dim_categories.category_key | fact_tickets.category_key |
| dim_sla_policies.policy_id | fact_tickets.policy_id |

Do not add active fact-to-fact relationships or bidirectional filters. The SQL model enforces log parent links, while the BI model avoids ambiguous filter paths. Selected Ticket Handling Hours uses TREATAS when a ticket category/channel cohort must filter effort. Regular Handling Hours and Utilization % describe handlers and their full day-level capacity; category and priority slicers do not filter workforce facts. Disable misleading visual interactions or state this scope in the title.

Agent filters mean **final owner** for ticket outcomes and **actual handler** for handling/capacity. An owner can differ from a handler. This distinction belongs in tooltips and table column labels. Date slicers select ticket creation cohorts and work dates, respectively; they do not select resolution dates. Backlog is always the 2026-10-01 00:00 Asia/Ho_Chi_Minh snapshot, optionally restricted by creation cohort, never historical daily backlog.

Mark dim_date as the date table using date_key; disable automatic date/time. Sort weekday_name by weekday_number and use month_start for monthly trend axes. The calendar contains all 365 coverage dates, including zero-arrival days. Previous-month measures require contiguous date selections. Rolling means include zero days and disclose partial windows during the first six days.

Paste measures individually from measures.dax; set rates to Percentage and durations to explicit minute/hour formats. BLANK at zero denominators is intentional. Compliance denominators are MET + BREACHED; CSAT response denominator is completed tickets; reopen denominator is the retained ticket cohort.

Average Daily Tickets uses the selected calendar-day count, including zero-arrival days. Category contribution measures remove category filters for the denominator while retaining date/channel/priority scope. Median and P95 resolution measures use observed completion durations; P95 uses the inclusive linear estimator matching the Python export. All these measures still require validation in Desktop.

Acceptance in Desktop: with all filters cleared, compare the cards and each SLA outcome count against verified_kpis.csv. Check category, priority, date and agent filtering; confirm the capacity visuals retain their stated scope. Validate zero-capacity BLANK and pending exclusions. DAX execution and rendered report verification remain manual.

Reference: [DAX date windows](https://learn.microsoft.com/en-us/dax/datesinperiod-function-dax).

