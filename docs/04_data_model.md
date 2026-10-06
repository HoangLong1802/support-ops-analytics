# Analytical Data Model

The model separates service outcomes from the effort and capacity used to deliver support. Shared dimensions allow comparisons by date and agent without treating each handling entry as another ticket.

## Facts and grain

| Fact | Grain / key | Analytical purpose |
|---|---|---|
| fact_tickets | One retained ticket snapshot / ticket_id | Demand, final ownership, SLA outcomes, elapsed durations, CSAT, reopens and snapshot backlog |
| fact_work_logs | One ticket/actual-handler/local-date entry / work_log_id; unique ticket_id + agent_id + work_date | Actual handling effort across agents and days |
| fact_workforce_daily | One agent/local date / agent_id + work_date | Scheduled, absent and shrinkage minutes; productive capacity |

The processed sources contain **14,774 tickets, 17,901 work-log entries and 6,318 workforce rows**. SQL derives workload through a view. Power BI imports the processed facts and derives service/capacity fields in Power Query; DAX handling sums `fact_work_logs` and capacity comes from workforce. Excel presents the verified results and does not supply the BI model.

## Supporting dimensions

| Dimension | Grain | Links |
|---|---|---|
| dim_date | One local reporting date | Ticket creation date and log/workforce work dates |
| dim_agents | One support agent | Ticket final owner, actual log handler and workforce agent |
| dim_categories | One approved category/subcategory pair | Ticket category_key |
| dim_sla_policies | One channel/priority policy | Ticket policy_id and matching channel/priority |

Dates and category pairs are derived dimensions, not additional raw sources. The agent dimension describes the team stored in the agent extract; historical team transfers are unavailable.

## Why outcomes and effort are separate

Resolution duration measures elapsed time between creation and completion, including waiting. Handling minutes measure logged work. A ticket can span several days and handlers, so using elapsed resolution as workload would materially overstate required capacity.

**Ticket ownership does not necessarily identify the handling agent.** Ticket outcomes are associated with the final snapshot owner; workload belongs to the agent named in each log. This supports fairer interpretation of workload distribution while acknowledging that owner-level outcomes do not establish individual causal performance.

Joining ticket rows directly to all logs repeats ticket facts. I aggregate each fact at the required grain before combining ownership and effort. Workforce capacity is counted once per agent/day, rather than once per ticket handled.

## Reporting relationships

Power BI uses active one-to-many, single-direction relationships from dimensions to facts. It has no active fact-to-fact relationships. Date filters select ticket creation cohorts and work dates separately; a backlog card always refers to the fixed snapshot, not a historical daily balance.

Category, priority and channel filter ticket outcomes; they do not allocate full agent/day capacity to that ticket cohort. Optional cohort handling uses a separate measure, while utilization keeps its stated handler/date scope.

[The SQL model](../sql/01_data_model.sql) enforces keys and relationships. [The Power BI model](../powerbi/data_model.md) provides file mappings, relationships and filter rules. [KPI definitions](kpi_definitions.md) show the common aggregation logic and the remaining native-tool validation work.
