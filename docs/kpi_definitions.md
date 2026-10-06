# KPI Definitions and Cross-Tool Review

The executed reference is [verified_metrics.py](../src/verified_metrics.py), with values in [verified_kpis.csv](../data/analytics/verified_kpis.csv). [The Excel export](../src/export_excel.py) reuses those functions and validates every Executive_KPIs value. [SQL definitions](../sql/02_kpi_definitions.sql) implement the same snapshot rules. [Power Query](../powerbi/processed_queries.pq) derives service fields from processed CSVs; [DAX](../powerbi/measures.dax) aggregates them.

| KPI | Common definition | Unfiltered Python result |
|---|---|---:|
| First Response SLA | MET / (MET + BREACHED); component PENDING excluded | 12,990 / 14,773 = 87.93% |
| Resolution SLA | MET / (MET + BREACHED); component PENDING excluded | 11,243 / 14,757 = 76.19% |
| Overall SLA | MET / (MET + BREACHED); overall PENDING excluded | 9,986 / 14,758 = 67.66% |
| Reopen Rate | Tickets with reopen_count > 0 / retained tickets | 1,234 / 14,774 = 8.35% |
| CSAT response rate | Completed tickets with valid CSAT / completed tickets | 7,431 / 14,196 = 52.35% |
| Backlog | Open + pending tickets at the fixed snapshot | 282 + 296 = 578 |
| Handling | Sum of retained work-log handling_minutes; divide by 60 for hours | 20,183.72 hours |
| Productive capacity | Sum of scheduled − absence − shrinkage; divide by 60 for hours | 29,361.62 hours |
| Utilization | Total handling / total productive capacity; null at zero capacity | 68.74% |

## Snapshot and boundary rules

Snapshot: **2026-10-01 00:00 Asia/Ho_Chi_Minh**, equivalent to **2026-09-30 17:00 UTC**. Event durations compare UTC instants; local dates and arrival hours use the reporting timezone.

An observed event at or before its target is MET. An event beyond its target is BREACHED. If the event is missing, snapshot age strictly beyond target is BREACHED; age at or below target is PENDING. Overall is BREACHED if either component breaches, MET only if the ticket is completed and both components are MET, and otherwise PENDING.

PENDING is an SLA outcome, distinct from the ticket's `pending` status. An unresolved overdue ticket remains SLA-eligible as a breach. Each component has its own denominator.

## Capacity and filter scope

Productive capacity differs from physical attendance: attendance subtracts absence only. Handling may exceed productive time while remaining within physical attendance, so utilization can exceed 100%. Aggregate utilization is a ratio of sums, not a mean of individual percentages.

Ticket outcome filters use creation cohorts and final owners. Workload/capacity filters use work dates and actual handlers. Category/channel/priority do not filter workforce capacity. Comparing selected-ticket effort to total agent/day capacity requires an explicit scope label.

## Review status

Python tests cover deadline equality, missing events, outcome partitions, denominators, backlog and zero capacity. Output tests reopen the workbook, compare its full-precision values with Python/saved KPIs, and inspect the core DAX source contract. That static check verifies definitions and dependencies; **it does not execute DAX**. M, SQL and DAX native runtime reconciliation remains pending. Workbook comparisons allow 1e-9 absolute numeric tolerance and 1e-12 relative tolerance; percent displays round to two decimals without changing the stored fractions.

SQL duration P90/P95 uses nearest rank, while pandas uses linear interpolation. That documented estimator difference is retained; counts and KPI rates must match. Reopen Rate is not FCR, and no handling measure uses elapsed resolution duration.
