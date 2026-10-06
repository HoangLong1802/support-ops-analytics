# Customer Support Operations Analytics

This project examines missed support commitments and daily workload against capacity. **The dataset is synthetic:** five operational sources cover 18 agents across three teams from October 2025 through September 2026. Quality assessment and cleaning retain 14,774 ticket snapshots for operational analysis.

## Business Problem

Support managers need to see where service deteriorates, which segments contribute SLA breaches, where backlog accumulates, when demand arrives, and whether workload aligns with capacity. The aim is to identify queues to investigate before changing staffing.

## Analytical Workflow

**Business Question → Raw Data → Data Quality → Cleaning → Data Model → SQL Analysis → Power BI → Recommendations**

Sources: tickets, work logs, workforce, agents and SLA policies. I establish source meaning before assessing repeated observations, ambiguous identities and impossible lifecycles. Cleaning produces reconciled processed and quarantine outputs while preserving valid unusual cases. The model separates ticket outcomes from handling effort. Python provides executed evidence; SQL and Power BI carry the same definitions into reporting.

## Key Findings

- **Technical cases deserve the first service review.** Technical Support represents **29.49% of tickets but 50.09% of resolution SLA breaches**: 1,760 of 3,514. Review technical queues, escalation transfers and dependencies before increasing staffing across all teams.
- **Resolution is the weaker service stage.** First-response compliance is **87.93%**, compared with **76.19%** for resolution and **67.66%** overall. Track both stages; each excludes its own pending cases.
- **Demand is uneven.** Average weekday arrivals are **1.92 times** weekend arrivals; **35.70%** of tickets arrive between 09:00 and 11:59 local time. Review morning triage coverage, then check when handling actually occurs.
- **The mean hides long waits.** Completed-ticket resolution averages **117.05 hours**, versus a **6.22-hour median** and **48.75-hour P95**. Report typical and tail durations together; elapsed resolution includes waiting.
- **Reopened tickets have lower respondent CSAT.** Scores average **3.74/5**, compared with **4.10/5** for tickets with no recorded reopen. Review repeated-resolution cases; case mix and survey nonresponse limit interpretation.
- **Backlog needs an aging review.** Of **578** unresolved tickets at the snapshot, **552** are older than 48 hours and **561** have breached resolution SLA. Confirm next actions and dependency owners for aged cases.

These are observations from synthetic data, with no causal claims. [Eight findings](docs/05_business_insights.md) include evidence, recommendations and limitations.

## Data Quality Decisions

| Data issue | Decision | Reason |
|---|---|---|
| Exact duplicates | Remove 75 ticket copies and 36 log copies | Repeated observations inflate volume and effort |
| Channel formatting | Normalize 120 ticket rows | Whitespace and case do not change the channel |
| Conflicting ticket ID | Quarantine 60 versions across 30 IDs | The source cannot identify a reliable winner |
| Invalid CSAT | Set 23 scores to null | Preserve the ticket without inventing satisfaction |
| Invalid lifecycle | Quarantine affected tickets | Service timing needs valid ordered events |
| Unknown agent reference | Quarantine affected records | Ownership and capacity need valid relationships |
| Extreme resolution duration | Keep logically valid records | Unusual waiting time alone is not a data error |

Every source row reconciles to a retained record, redundant copy or quarantine entry. [Cleaning decisions](docs/03_cleaning_decisions.md) explain the rules and impact.

## Data Model

`fact_tickets` stores one ticket snapshot; `fact_work_logs` stores one ticket/handler/local-date entry; `fact_workforce_daily` stores one agent/local date. Date, agent, category and SLA-policy dimensions support consistent comparisons. Final ticket ownership can differ from the actual handler, so service outcomes and effort are aggregated separately to avoid duplicated totals.

## SQL Analysis

The [SQL files](sql/README.md) answer:

- Which categories contribute disproportionately to resolution breaches?
- When does ticket demand peak?
- How do resolution duration and reopen behavior relate to CSAT?
- Where is aged backlog concentrated?
- Which teams carry the greatest workload relative to capacity?
- How do owner outcomes differ after considering case mix and sample size?

CTEs, windows, LAG, ranking and conditional aggregation support these questions. **MySQL execution is still pending**; published findings use executed Python calculations.

## Power BI

Three pages are specified: **Executive Overview** for service risks, **Operations Analysis** for demand and queues, and **Agent & Team Performance** for ownership, effort and capacity. The semantic model, DAX measures and dashboard specification are ready for implementation in Power BI Desktop. **No PBIX or screenshots have been created; DAX has not been executed.**

## Workforce Planning

Daily work logs measure workload; scheduled minutes minus absence and shrinkage measure productive capacity. Required FTE uses the previous four matching weekdays of handling, **374.4 productive minutes per FTE** and an **85% target utilization**. Staffing gap is required minus available equivalent FTE. Aggregate observed utilization is **68.74%**, but daily estimates can expose pressure hidden by that average. This is a planning estimate, not exact workforce scheduling or an hourly staffing gap.

## Tools

Python · pandas · NumPy · MySQL / SQL · Power BI / DAX

## Repository Guide

Start with [business context](docs/01_business_context.md), then [data quality](docs/02_data_quality.md), [cleaning decisions](docs/03_cleaning_decisions.md), [data model](docs/04_data_model.md), [SQL](sql/README.md), [Power BI](powerbi/dashboard_spec.md) and [insights](docs/05_business_insights.md). [Lineage](docs/data_lineage.md) links these steps to their source and output files.

## Reproduce

From the repository root, use Python 3.12+ in a virtual environment:

```text
python -m pip install -r requirements.txt
python src/run_pipeline.py
```

This assesses, cleans, validates, refreshes analytical outputs and runs tests against the included raw snapshot, preserving this README. The [SQL guide](docs/sql_analysis_guide.md) covers imports and reconciliation. Synthetic operational source tools in `tools/` provide reproducibility; validated raw files remain unchanged.
