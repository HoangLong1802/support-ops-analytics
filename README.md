# Customer Support Operations Analytics

A synthetic Data Analyst portfolio project connecting operational data quality to service, customer experience and daily capacity decisions.

## Business problem

Support leaders need to understand demand, SLA risks, snapshot backlog and workload differences before adjusting operations. The analysis uses ticket ownership, actual handling effort and workforce capacity separately, with explicit limits on inference.

## Analytical workflow

Business questions → raw data → independent quality assessment → cleaning decisions → processed data → SQL → Power BI → verified insights and recommendations.

## Dataset

**All data is synthetic.** There are 15,000 logical tickets before defects, 18 agents in three teams and 365 local operational dates. Coverage is 2025-10-01 through 2026-09-30; snapshot is 2026-10-01 00:00 Asia/Ho_Chi_Minh. Stored event timestamps are UTC.

Five raw sources: agents, SLA policies, tickets, ticket work logs and daily workforce. Intentional duplicates and field defects demonstrate the quality workflow. Cleaning retains 14,774 ticket snapshots; exclusions are reconciled in [cleaning_report.md](docs/cleaning_report.md).

## Tech stack and data model

Python 3.12+, pandas 3.x, NumPy 2.x, MySQL 8.0.16+ SQL, and a Power BI semantic-model/DAX specification. The relational model has four dimensions (date, agents, categories, policies) and three facts (tickets, work logs, daily workforce). Categories and dates are derived; no additional raw source is introduced.

## Data quality approach

Separate fully identical copies from conflicting keys; normalize only evidence-backed values; quarantine ambiguous identities and logical errors; preserve legitimate extreme durations. Assessment and cleaning verify immutable raw SHA256. [Quality findings](docs/data_quality_report.md), [decisions](docs/cleaning_decisions.md) and [lineage](docs/data_lineage.md) show the audit trail.

## SQL analysis

[Business queries](database/analysis.sql) cover demand, mix, SLA components, satisfaction, reopens, backlog, case mix and handling/capacity. They use joins, CTEs, conditional aggregation, ranks, LAG and calendar rolling averages. **SQL has not been executed against MySQL in this environment.** [Execution guide](docs/sql_analysis_guide.md) supplies exact import and reconciliation steps. Findings below use executed Python evidence.

## Dashboard

[Model](powerbi/data_model.md), [DAX measures](powerbi/measures.dax), import-ready analytical CSVs and an [exact three-page specification](powerbi/dashboard_spec.md) are included: Executive Overview, Operations Analysis, Agent & Team Performance. The actual PBIX and screenshots remain manual work; DAX has not been executed in Desktop.

## Key findings

| Verified metric | Result |
|---|---:|
| Retained tickets | 14,774 |
| First-response SLA compliance | 87.93% |
| Resolution SLA compliance | 76.19% |
| Overall SLA compliance | 67.66% |
| CSAT / valid completed-ticket response rate | 4.07/5 / 52.35% |
| Reopen Rate | 8.35% |
| Snapshot backlog | 578 |
| Handling / productive utilization | 68.74% |

Technical Support contributes 50.09% of resolution breaches from 29.49% of tickets. Mean resolution is 117.05 hours versus a 6.22-hour median, supporting a separate review of long waits. See [eight evidence-led findings](docs/insights.md) for actions and limitations.

## Workforce planning

[Daily estimates](data/analytics/staffing_daily.csv) use the previous four matching weekdays of handling effort, 374.4 productive minutes per planned FTE and an 85% utilization target. Positive gaps are planning signals; daily data cannot support exact hourly staffing gaps. [Methodology](docs/workforce_methodology.md) explains history requirements and assumptions.

## Repository structure

- data/: immutable raw, processed, quarantine and analytical outputs
- src/: generation, assessment, cleaning, validation, metrics and daily workforce analysis
- database/: MySQL schema, import, validation, views and business queries
- powerbi/: semantic model, measures and report specification
- docs/: requirements, dictionary, lineage, reports, methodology and findings
- tests/: focused generation, quality, lifecycle, SLA, relationship and KPI checks

## Reproduce

Use Python 3.12+ and compatible installed packages, or install requirements in a project virtual environment. From the repository root:

```text
python -m pip install -r requirements.txt
python src/generate_dataset.py
python src/validate_generation.py
python src/assess_data_quality.py
python src/clean_data.py
python src/validate_clean_data.py
python src/verified_metrics.py
python src/staffing_analysis.py
python src/build_portfolio.py
python -m unittest discover -s tests -v
```

Existing validated raw files are reused. To simulate from scratch, use a new working copy with no raw CSVs; never overwrite a validated source snapshot. Analytical metadata records the parameters, checksums and actual runtime. Reproducibility depends on those recorded package versions.

SLA compliance excludes PENDING; Reopen Rate is not FCR; resolution time is not handling time; backlog is a fixed snapshot; correlations do not establish causes.
