# Power BI

**English** | [Tiếng Việt](README.vi.md)

- `customer_support_operations.pbix`: the report (5 pages) and the model.
- `processed_queries.pq`: the Power Query (M) code. It reads `data/processed/*_clean.csv` through a `ProjectFolder` path; change that path if you clone the repo elsewhere.
- `measures.dax`: DAX measures. All 68 measures; the 13 added later are at the end of the file.
- `acceptance_reference.json`: reference numbers computed in Python.

## Model

Seven tables in a star layout: `fact_tickets`, `fact_work_logs`, `fact_workforce_daily`, `dim_date`, `dim_agents`, `dim_sla_policies` and `dim_categories`. Eight many-to-one relationships, single direction. Facts are not joined to each other. Power BI's automatic date tables are still on.

## Pages

1. Overview: volume, SLA compliance, backlog, CSAT
2. SLA and demand: by priority, weekday and hour of day
3. Workforce: tickets per agent, handling time, absence and shrinkage
4. Customer experience: CSAT and reopen rate by month, category and channel
5. Backlog and risk: how old the unresolved tickets are

## Notes

- Backlog is a snapshot of tickets unresolved on 1 Oct 2026, not a history.
- Resolution SLA compliance = met / (met + breached). Pending tickets are left out of the denominator.
- Ratios at team or total level are recomputed from counts, not averaged.
- Drill-through and custom tooltips are not built.
- I have not published to the Power BI Service. There is no `.pbip` version.
