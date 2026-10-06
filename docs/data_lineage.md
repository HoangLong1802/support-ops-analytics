# Data Lineage

```text
Business Question & Source Understanding
                 ↓
Synthetic Source → Raw CSV
                 ↓
Data Quality Assessment
                 ↓
Cleaning Decisions → Processed Data + Quarantine
                 ↓
Data Model → MySQL / SQL
                 ↓
Power BI Specification
                 ↓
Insights & Recommendations
```

| Step | Read | Run / inspect |
|---|---|---|
| Business problem | [Business Context](01_business_context.md) | Questions that determine reporting scope |
| Source understanding | [Data Dictionary](data_dictionary.md) | Five source grains, optional fields and relationships |
| Synthetic operational source | [Generation evidence](generation_report.md) | tools/synthetic_data_generator.py; tools/validate_generation.py |
| Raw data | Five unchanged extracts | data/raw/ |
| Quality assessment | [Data Quality](02_data_quality.md); detailed report | src/assess_data_quality.py; data/analytics/quality_audit.json |
| Cleaning decisions | [Cleaning Decisions](03_cleaning_decisions.md) | src/clean_data.py; cleaning_report.md |
| Processed data | Valid observations and preserved exclusions | data/processed/; data/quarantine/; src/validate_clean_data.py |
| Data model | [Analytical Model](04_data_model.md) | sql/01_data_model.sql; database/import.sql |
| SQL analysis | [SQL guide](../sql/README.md) | sql/02–05; database/validation.sql |
| Power BI | [Model](../powerbi/data_model.md); [report questions](../powerbi/dashboard_spec.md) | measures.dax; analytical CSV imports |
| Insights and actions | [Business Insights](05_business_insights.md) | src/verified_metrics.py; src/build_portfolio.py |
| Daily capacity planning | [Workforce Methodology](workforce_methodology.md) | src/staffing_analysis.py; staffing_daily.csv |

The synthetic operational source makes the project reproducible. Assessment detects defects from records and business rules, independently of generated defect identifiers. Raw SHA256 values are checked before and after the analytical steps.

Python provides the executed KPI and cohort evidence. SQL and Power BI are the prepared reporting path; native query, DAX and rendered-report validation remain pending. [Shared KPI definitions](kpi_definitions.md) make that boundary explicit.

Creation-date trends describe arriving ticket cohorts. Backlog is known only at the fixed snapshot. Final ticket ownership and actual handling effort have different meanings and stay separate through the model.
