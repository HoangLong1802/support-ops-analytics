# Customer Support Operations Analytics

This project compares support service outcomes with daily handling capacity. **All data is synthetic:** five sources cover 18 agents in three teams from October 2025 through September 2026. Cleaning retains 14,774 ticket snapshots for analysis.

## Project Outputs

Open the [Excel analytical workbook](output/customer_support_analysis.xlsx): **14 sheets** expose executive KPIs, demand, SLA, categories, CSAT/reopens, backlog, agent/team outcomes, workforce utilization, staffing estimates, quality findings, cleaning and quarantine summaries. Four charts accompany verified results, definitions and sample sizes.

Power BI [data model](powerbi/data_model.md), [DAX measures](powerbi/measures.dax) and [dashboard specification](powerbi/dashboard_spec.md) are included. The final PBIX must be built manually in Power BI Desktop. **No PBIX or dashboard screenshots exist yet.** Target paths are `powerbi/customer_support_analytics.pbix` and `output/dashboard/`.

## Business Problem

Support managers need to locate weak service, SLA breach contributors, aged backlog and demand peaks, then compare workload with capacity before changing staffing.

## Analytical Workflow

```text
Business Question → Raw Data → Data Quality Assessment → Cleaning Decisions
    → Processed Data → SQL / Python Analysis → Excel Analytical Output
    → Power BI Dashboard → Business Insights → Recommendations
```

Sources are tickets, work logs, daily workforce, agents and SLA policies. Quality checks distinguish repeated observations, ambiguous identities and impossible lifecycles from valid unusual cases. Cleaning produces reconciled processed and quarantine outputs; the model separates ticket outcomes from handling effort. Markdown explains why, Excel exposes measured results, and the prepared Power BI report shows how those results can support decisions visually.

## Key Findings

- **Technical cases merit the first review:** 29.49% of tickets contribute 50.09% of resolution SLA breaches, or 1,760 of 3,514. Investigate technical queues and dependency aging before increasing staffing across all teams.
- **Resolution is the weaker service stage:** first-response compliance is 87.93%, versus 76.19% for resolution and 67.66% overall. Each component excludes its own pending cases.
- **Demand is uneven:** average weekday arrivals are 1.92 times weekend arrivals; 35.70% arrive between 09:00 and 11:59 local time. Review triage availability, then validate handling timing.
- **The mean hides long waits:** completed-ticket resolution averages 117.05 hours, versus a 6.22-hour median and 48.75-hour P95. Elapsed resolution includes waiting.
- **Reopened tickets have lower respondent CSAT:** 3.74/5 versus 4.10/5 for tickets with no recorded reopen. Case mix and nonresponse limit interpretation.
- **Backlog needs an aging review:** 552 of 578 unresolved tickets are older than 48 hours; 561 have breached resolution SLA. Confirm next actions and dependency owners.

[Eight findings](docs/05_business_insights.md) pair evidence with recommendations and limitations. Synthetic associations do not establish causes; Reopen Rate is not FCR.

## Data Quality Decisions

| Data issue | Decision | Reason |
|---|---|---|
| Exact duplicates | Remove 75 ticket copies and 36 log copies | Repeated observations inflate totals |
| Channel formatting | Normalize 120 ticket rows | Case and spaces preserve meaning |
| Conflicting ticket ID | Quarantine 60 versions across 30 IDs | No reliable canonical version |
| Invalid CSAT | Set 23 scores to null | Preserve ticket facts without inventing a score |
| Invalid lifecycle | Quarantine affected tickets | Service timing needs valid ordered events |
| Unknown agent reference | Quarantine affected records | Ownership and capacity require known relationships |
| Extreme duration | Keep logically valid records | Unusual waiting time alone is not an error |

Every source row reconciles to a retained observation, redundant copy or quarantine entry. [Cleaning decisions](docs/03_cleaning_decisions.md) explain the full rules and impact; Excel provides the counts.

## Data Model

`fact_tickets` stores one ticket snapshot; `fact_work_logs` stores one ticket/actual-handler/local-date entry; `fact_workforce_daily` stores one agent/local date. Date, agent, category and SLA-policy dimensions support comparisons. Final ownership can differ from the handler, so outcome and effort facts stay separate to prevent duplicated totals.

## SQL Analysis

The [SQL files](sql/README.md) answer:

- Which categories contribute disproportionately to resolution breaches?
- When does demand peak?
- How do duration and reopens relate to respondent CSAT?
- Where is aged backlog concentrated?
- Which teams carry the most workload relative to capacity?
- How do owner outcomes differ with case mix and sample size?

CTEs, windows, LAG and ranking serve these questions. MySQL execution is pending; published evidence uses executed Python calculations.

## Power BI

Exactly three pages are specified: **Executive Overview**, **Operations Analysis**, and **Agent & Team Performance**. The model imports processed CSVs and derives service fields in Power Query. Excel is a presentation output and is not the BI source. M/DAX runtime reconciliation and real dashboard creation remain Desktop steps.

## Workforce Planning

Work logs measure actual effort. Productive capacity equals schedule minus absence and shrinkage. Required FTE uses four prior matching weekdays, 374.4 productive minutes per FTE and an 85% utilization target; gap equals required minus available equivalent FTE. Observed aggregate utilization is 68.74%. This is daily planning, not exact scheduling or hourly staffing gaps.

## Tools

Python · pandas · NumPy · openpyxl / Excel output · MySQL / SQL · Power BI / DAX

## Repository Guide

Read [business context](docs/01_business_context.md), [data quality](docs/02_data_quality.md), [cleaning](docs/03_cleaning_decisions.md), [model](docs/04_data_model.md) and [insights](docs/05_business_insights.md). [Lineage](docs/data_lineage.md) connects the sources, analytical layers and deliverables.

## Reproduce

From the repository root, use Python 3.12+ in a virtual environment:

```text
python -m pip install -r requirements.txt
python src/run_pipeline.py
```

This refreshes Excel and analytical outputs, validates sources and runs tests without changing raw data or this README. For Excel only, run `python src/export_excel.py`. Native steps: [SQL guide](docs/sql_analysis_guide.md) and [Power BI model](powerbi/data_model.md).
