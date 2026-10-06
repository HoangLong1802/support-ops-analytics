# Data lineage

Synthetic Operational Source → Raw CSV → Data Quality Assessment → Cleaning Decisions → Processed Data → Relational Model → SQL Analysis → Power BI → Business Insights → Recommendations

| Layer | Artifact | Purpose |
|---|---|---|
| Synthetic operational source | src/generate_dataset.py | Seeded arrivals, lifecycles, routing, effort and workforce; pristine validation before intentional defects |
| Raw CSV | data/raw/ | Five immutable operational extracts; generation report records SHA256 |
| Quality assessment | src/assess_data_quality.py; docs/data_quality_report.md | Independently profile values, keys, types, relationships and operational rules |
| Cleaning decisions | docs/cleaning_decisions.md | Explain evidence, business impact, safe fixes and exclusions |
| Processed data | data/processed/; data/quarantine/ | Canonical records plus preserved exclusions; complete row reconciliation |
| Relational model | database/schema.sql; import.sql | Seven tables, dimensional keys, foreign keys and useful indexes |
| SQL analysis | database/views.sql; analysis.sql | Canonical service fields and business questions; execution status in sql_analysis_guide.md |
| Power BI | powerbi/; derived CSVs in data/analytics/ | Shared dimensions, consistent measures and three-page report specification |
| Business insights | docs/insights.md; verified_kpis.csv | Executed Python evidence with denominators and limitations |
| Recommendations | docs/insights.md | Specific operational review actions supported by the observed synthetic cohorts |

src/verified_metrics.py is the canonical executed snapshot KPI layer. SQL views implement the same component outcomes and denominators. Power BI imports the executed derived ticket fields and uses measures for filter-aware aggregation. src/staffing_analysis.py uses handling-agent/day effort and recorded productive capacity; it does not treat resolution waiting as handling effort.

Raw SHA256 is checked before and after assessment, cleaning and analytics. Independent assessment never uses generated bad-record identifiers or expected defect counts to detect issues. Exact copies are separated from conflicting keys before downstream joins; exclusions preserve original source row numbers and reasons.

Creation-date trends describe arriving ticket cohorts. Backlog is known only at the fixed snapshot. SQL and Power BI execution require their native tools; the supplied sources do not imply execution or rendered report creation.

