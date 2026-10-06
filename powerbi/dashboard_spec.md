# Dashboard specification

Exactly three report pages. Use a restrained navy/teal palette, red for breaches, amber for pending, readable labels and consistent percentage denominators. Display a visible Synthetic data label and the fixed snapshot. No PBIX or screenshots are supplied. Build the report in Desktop using data_model.md and measures.dax, then capture actual screenshots in images/dashboard/.

## Page 1 — Executive Overview

Purpose: assess demand, service and customer experience.

| Visual | Fields/measures | Decision supported |
|---|---|---|
| KPI strip | Total Tickets, Overall SLA Compliance %, Average Resolution Hours, Average CSAT, Backlog, Reopen Rate | Identify service risks; tooltips show eligible and respondent counts |
| Monthly demand line | month_start, Total Tickets, Previous Month Tickets | Review demand changes across full months |
| SLA outcome columns | FR/Resolution/Overall MET, BREACHED, PENDING | Distinguish overdue work from undecided cases |
| Category contribution bars | category, tickets and resolution breaches | Prioritize high-contribution cohorts |
| Channel mix bars | channel, Total Tickets and share | Review contact mix |
| Snapshot backlog summary | status and Backlog >24/48/72 Hours | Review aging cases at the fixed snapshot |

Use date, channel, priority and category slicers. Backlog thresholds are nested counts, not mutually exclusive bands. Resolution averages include legitimate long waits; show the median/P95 from the verified export in a tooltip or reference annotation.

## Page 2 — Operations Analysis

Purpose: locate demand concentrations and service bottlenecks.

| Visual | Fields/measures | Decision supported |
|---|---|---|
| Weekday demand bars | weekday_name, average tickets per calendar day | Compare weekdays fairly using available dates |
| Local-hour arrival bars | local_created_hour, Total Tickets | Review demand timing; no exact staffing-gap claim |
| Category/subcategory matrix | category, subcategory, Total Tickets | Identify specific routing/training review areas |
| Priority comparison | priority, FR/Resolution SLA Compliance % | Compare outcomes against priority-specific targets |
| Breach contribution bars | category, Resolution SLA Breached, share of total breaches | Separate volume contribution from breach rate |
| Resolution distribution | resolution_minutes / 60 in explicit elapsed-time bands | Show long-tail delays; never label this handling time |
| Snapshot aging bands | <=24h, 24–48h, 48–72h, >72h | Review mutually exclusive backlog age cohorts |

All hourly/weekday labels use Asia/Ho_Chi_Minh. Completed-only resolution distributions exclude unresolved cases and therefore have censoring limitations. Tooltips show denominator and retained sample size.

## Page 3 — Agent & Team Performance

Purpose: review effort, capacity and service outcomes with case mix.

| Visual | Fields/measures | Decision supported |
|---|---|---|
| Handling effort bars | handling agent/team, Handling Hours | Review effort concentration |
| Utilization matrix | agent/team/work date, Utilization % | Identify daily capacity pressure; null at zero capacity |
| Final ownership bars | final owner/team, Total Tickets | Review ownership distribution |
| Owner SLA comparison | owner, Overall SLA Compliance %, eligible count | Review outcomes with sufficient observations |
| CSAT table | owner, Average CSAT, CSAT Responses, CSAT Response Rate | Expose nonresponse and small samples |
| Reopen comparison | owner, Reopen Rate, ticket count | Review rework associations; not FCR |
| Case-mix matrix | owner/team, category, priority, ticket count | Interpret differences in assignment complexity proxies |

Agent/team and work/creation-date slicers filter shared dimensions. Category/channel/priority interactions apply to ticket outcome visuals only; keep full-capacity effort visuals explicitly scoped. Daily staffing estimates may appear in the utilization tooltip with the 85% assumption, without adding a fourth page. Avoid a single agent league table based on raw ticket counts.

After building: check unfiltered cards against verified_kpis.csv, test slicers and relationship direction, inspect missing values and partial date windows, and save real screenshots. This document specifies the intended report; it does not claim a rendered dashboard exists.

