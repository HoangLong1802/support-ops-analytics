# What the data says

All figures come from the synthetic dataset (seed 42), so they show how the analysis works, not how a real support team performs. Nothing here measures the effect of a change that was actually made.

## Findings

**1. Technical support causes half of the SLA breaches.**
It handles 29.5% of tickets (4,357) but accounts for 1,760 of the 3,514 resolution breaches (50.1%). Inside the category, 40.4% of eligible tickets breach. These are three different numbers, so quote them separately: share of volume, share of breaches, and breach rate within the category. Case mix (priority, subcategory) is not adjusted for. Sources: [category summary](../data/analytics/category_service_summary.csv), [SQL](../sql/06_claim_verification.sql).

**2. Weekdays are about twice as busy as weekends.**
Weekdays average 46.9 tickets a day (12,240 over 261 days); weekends average 24.4 (2,534 over 104 days), a 1.92x gap. Comparing raw totals (4.83x) overstates it because there are fewer weekend days. Arrival time is not handling time, so this says nothing about staffing gaps yet. Sources: [day-type summary](../data/analytics/demand_day_type.csv), [SQL](../sql/06_claim_verification.sql).

**3. Resolution is the weak SLA, not first response.**
First response is met 87.9% of the time, resolution 76.2%. Priority matters a lot: urgent tickets meet the resolution target only 44.3% of the time, low priority 90.7%. Sources: [KPI output](../data/analytics/verified_kpis.csv), [SLA SQL](../sql/02_kpi_definitions.sql).

**4. The backlog is old.**
578 tickets are unresolved at the 1 Oct 2026 snapshot (282 open, 296 pending). 552 are older than 48 hours and 561 have already breached resolution. Most were created months earlier. That is partly an artifact of the simulation, which never closes some tickets, so treat it as a demonstration of the aging logic. This is a snapshot, not a historical backlog. Sources: [ticket facts](../data/analytics/ticket_service_metrics.csv), [backlog SQL](../sql/03_operations_analysis.sql).

**5. CSAT needs its response rate next to it.**
Average CSAT is 4.07 out of 5, but only 7,431 of 14,196 completed tickets (52.4%) have a score. People who did not answer may feel differently, so the score is not a causal signal. Sources: [customer SQL](../sql/04_customer_analysis.sql), [KPI output](../data/analytics/verified_kpis.csv).

Resolution time has a long tail: mean 117.05 h, median 6.22 h, P95 48.75 h. It is elapsed time including waiting, not effort, so use the median for the typical ticket.

## What I would do next

These are ideas to test, not results.

1. **Review technical queues and the aged backlog.** Split by subcategory and priority, then look at handoffs and what each stuck ticket is waiting for. Track the within-category breach rate and the count of tickets older than 48 hours at the next snapshot.
2. **Check coverage against weekday demand.** Before changing shifts, line up arrivals with when tickets are actually worked. Track first-response breach rate and new backlog.
3. **Read CSAT by category and priority, with sample sizes.** Watch the response rate and reopen rate alongside it. Reopen rate is not first-contact resolution.
