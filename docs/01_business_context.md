# Business Context

## Business Problem

A support operation needs a reliable view of service performance before deciding which queues to investigate and how to allocate capacity. Ticket volume alone does not explain missed commitments: case mix, waiting, repeated resolutions and available productive time all matter.

This project identifies service risks and translates them into targeted review actions. All records are synthetic; the findings demonstrate an analytical workflow rather than a real company's results.

## Stakeholders

Support leadership needs a concise service overview. Operations managers and team leads need queue, category and priority comparisons. Workforce planners need daily handling demand relative to productive capacity. Reporting analysts need traceable definitions and reconciled records.

## Business Questions

- Which categories contribute more resolution breaches than their share of demand?
- When do tickets arrive, and which channels and priorities drive the mix?
- Does a good response SLA hide weak resolution performance?
- What remains unresolved at the snapshot, and how old is it?
- How do survey participation, resolution duration and reopens relate to CSAT?
- How do handling effort and capacity vary across agents, teams and days?
- Under the stated utilization assumption, which team-days warrant a capacity review?

## Core KPIs

| KPI | Business meaning |
|---|---|
| Ticket volume | Retained ticket snapshots in the selected creation cohort |
| First Response / Resolution SLA | Share meeting the relevant target among MET + BREACHED; PENDING excluded |
| Overall SLA | Both stages met on a completed ticket; either breach makes the ticket breached |
| Resolution duration | Elapsed time from creation to completion, including waiting |
| CSAT / response rate | Mean valid score / completed tickets with a valid score divided by completed tickets |
| Reopen Rate | Tickets with at least one recorded reopen divided by all retained tickets |
| Backlog | Open or pending tickets at the fixed snapshot |
| Handling / productive capacity | Actual effort / scheduled time less absence and shrinkage |
| Utilization | Total handling divided by total productive capacity; null at zero capacity |
| Estimated FTE gap | Required equivalent FTE minus available equivalent capacity |

## Dataset Scope

Five sources contain agents, SLA policies, ticket snapshots, handling logs and daily workforce. The source covers 18 agents in three teams and 365 local dates from 2025-10-01 through 2026-09-30. Timestamps are stored in UTC; operational dates and arrival hours use Asia/Ho_Chi_Minh.

Cleaning retains 14,774 tickets, 17,901 handling entries and 6,318 workforce rows. The analytical snapshot is **2026-10-01 00:00 Asia/Ho_Chi_Minh**. Each ticket has a final owner; work logs identify actual handlers.

## Known Limitations

Synthetic relationships cannot establish real operational causes or forecast intervention benefits. A single snapshot cannot reconstruct backlog history, owner transfers or all customer contacts. Reopen Rate is not FCR. Resolution duration is not handling effort. Quarantine changes cohort coverage, and survey nonresponse limits CSAT comparisons. Daily capacity supports planning estimates, not exact hourly schedules. MySQL and Power BI require native execution before their outputs can be considered validated.
