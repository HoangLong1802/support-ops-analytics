# SQL Analysis

Read the model and shared definitions first, then follow the business questions in each analysis file.

| File | Business purpose |
|---|---|
| [01_data_model.sql](01_data_model.sql) | Separate ticket outcomes, actual handling effort and daily capacity; enforce dimensional keys |
| [02_kpi_definitions.sql](02_kpi_definitions.sql) | Classify snapshot service outcomes and calculate the executive KPIs |
| [03_operations_analysis.sql](03_operations_analysis.sql) | Locate demand peaks, breach contributions, long waits and aged backlog |
| [04_customer_analysis.sql](04_customer_analysis.sql) | Compare survey participation, elapsed resolution, CSAT and reopens |
| [05_workforce_analysis.sql](05_workforce_analysis.sql) | Compare handlers, capacity, final owners and case mix without duplicating facts |

All 23 existing business queries are retained in these files; additional cohort comparisons support the published insights. CTEs, LAG, rolling averages and rankings serve those questions rather than stand-alone syntax examples.

**Status: reviewed source, not executed in MySQL.** Python exports provide the current measured results. [Import and validation steps](../docs/sql_analysis_guide.md) use `database/import.sql` and `database/validation.sql`; the former schema, views and analysis paths are compatibility entrypoints. Run SOURCE commands from the repository root.
