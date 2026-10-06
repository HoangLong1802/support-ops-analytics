# Dashboard Specification

The intended report has **three pages**. Its purpose is to move from service risk to queue review, then to effort and capacity. The processed-CSV model, Power Query preparations and DAX source are ready; **no PBIX, executed M/DAX or screenshots are supplied**. Build and validate the report in Power BI Desktop, save `powerbi/customer_support_analytics.pbix`, then capture real images in `output/dashboard/`.

Use clear titles, explicit units and restrained colors. Final formatting and theme remain the report author's choice. Keep a visible **Synthetic data** label and snapshot **2026-10-01 00:00 Asia/Ho_Chi_Minh**. Use one compact card strip and a small set of question-driven visuals per page.

## Page 1 — Executive Overview

| Visual | Question answered | Fields / measures |
|---|---|---|
| Card strip | How much demand, service risk and unresolved work is present? | Total Tickets; Overall SLA Compliance %; Average Resolution Hours; Average CSAT; Backlog; Reopen Rate % |
| Monthly demand line | Is the arrival cohort growing or shrinking across full months? | month_start; Total Tickets; MoM Ticket Change % |
| SLA outcome columns | Which service stage misses targets, and how many cases remain pending? | FR / Resolution / Overall MET, BREACHED and PENDING counts |
| Category contribution bars | Which categories contribute more breaches than their share of demand? | category; Ticket Share %; Resolution Breach Share % |
| Channel mix bars | Which contact channels account for the most demand? | channel; Total Tickets |
| Backlog status and aging summary | How much unresolved work is already aged at this snapshot? | status; Backlog; Backlog >24 / >48 / >72 Hours |

Tooltips show SLA eligible counts, CSAT responses and CSAT response rate. The backlog thresholds are nested counts, not mutually exclusive bands. Date, channel, priority and category slicers select ticket cohorts; the snapshot itself does not move.

## Page 2 — Operations Analysis

| Visual | Question answered | Fields / measures |
|---|---|---|
| Weekday demand bars | Which weekdays have the highest average arrivals per calendar day? | weekday_name; Average Daily Tickets |
| Local-hour arrival bars | When do tickets arrive during the day? | local_created_hour; Total Tickets |
| Category/subcategory matrix | Which case types combine substantial demand and weak resolution service? | category; subcategory; Total Tickets; Resolution SLA Compliance % |
| Priority and channel comparison | How does service vary against each cohort's policy targets? | priority; channel; FR / Resolution SLA Compliance %; eligible counts |
| Resolution distribution | How large are the long waits compared with typical completion time? | completed-ticket elapsed resolution bands; median and P95 measures in tooltip |
| Snapshot aging bands | Which categories contain backlog older than 48 or 72 hours? | category; mutually exclusive <=24h / 24–48h / 48–72h / >72h bands |

Create resolution and aging bands from the imported duration fields in Power Query. Use <= boundaries for the upper limit of each finite band. Completed-only resolution excludes unresolved cases; never label it handling time. Arrival hours use Asia/Ho_Chi_Minh and cannot establish hourly staffing gaps. Average Daily Tickets includes every selected calendar date, including zero arrivals.

## Page 3 — Agent & Team Performance

| Visual | Question answered | Fields / measures |
|---|---|---|
| Handling effort bars | Which actual handlers and teams carry the most recorded work? | agent/team; Handling Hours |
| Daily utilization matrix | Where does workload press against productive capacity? | agent/team/work date; Utilization %; capacity and effort in tooltip |
| Final-owner service table | Which ownership cohorts warrant review after considering sample size? | final owner; Total Tickets; Overall SLA Compliance %; eligible count |
| Customer outcome table | Which ownership cohorts have poor respondent CSAT or more reopens? | Average CSAT; CSAT Responses; CSAT Response Rate %; Reopen Rate %; ticket count |
| Team SLA comparison | Which ownership teams show weak service after considering volume and case mix? | team; FR / Resolution / Overall SLA Compliance %; eligible counts |
| Case-mix matrix | Could assignment mix help explain differences in owner outcomes? | final owner/team; category; priority; ticket count |

Add the daily staffing estimate to the utilization tooltip for the matching team/work date, with the **85% target** and **four prior matching weekdays** stated. Insufficient history returns blank. FTE gaps are equivalent-capacity planning signals, not headcount or exact shifts.

Shared agent filters represent **final owner** for ticket outcomes and **actual handler** for effort/capacity. Date filters represent creation dates and work dates, respectively. Category/channel/priority affect ticket outcomes only; disable their interactions with full-capacity visuals and label the scope. Avoid a single agent league table that ignores case mix and hire dates.

## Desktop Validation

Use 5–7 purposeful visuals per page, including the compact card strip. With filters cleared, reconcile cards and all SLA outcome counts to `data/analytics/verified_kpis.csv` and Excel Executive_KPIs. Test date, category, channel, priority and agent interactions; validate BLANK at zero capacity and exclusion of PENDING from compliance. Check weekday sorting, zero-arrival dates, partial rolling windows and snapshot labels. Save the real PBIX and export executive_overview.png, operations_analysis.png and agent_team_performance.png to `output/dashboard/` only after those checks pass.
