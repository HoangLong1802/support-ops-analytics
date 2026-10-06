# SQL analysis guide

Execution status: scripts ready only. No MySQL client or service was found in the build environment; these scripts have not been executed against MySQL. Portfolio findings use the executed Python exports.

Use MySQL 8.0.16 or later for enforced CHECK constraints. Only the dedicated database customer_support_analytics is used. Read the scripts, replace the five paths in import.sql if necessary, and start with empty project fact tables. Reimporting into populated fact tables is not a refresh operation.

From the repository root, connect to a trusted local server with the client's local file option:

```text
mysql --local-infile=1 -h 127.0.0.1 -u YOUR_USER -p
SOURCE sql/01_data_model.sql;
SOURCE database/import.sql;
SOURCE sql/02_kpi_definitions.sql;
SOURCE database/validation.sql;
SOURCE sql/03_operations_analysis.sql;
SOURCE sql/04_customer_analysis.sql;
SOURCE sql/05_workforce_analysis.sql;
```

The server must also allow local file imports. If it does not, ask its administrator to configure this dedicated environment; the scripts do not change global settings. Imported timestamps are UTC DATETIME values. Reporting dates/hours add the fixed UTC+07:00 offset used by Asia/Ho_Chi_Minh during this coverage year, without depending on installed server timezone tables.

Inspect every SHOW WARNINGS result immediately after loading. LOCAL imports can downgrade some errors to warnings, so a successful command alone is insufficient. Reconcile all loaded source counts to docs/cleaning_report.md, ensure detail validation queries return zero rows, and compare the executive query to data/analytics/verified_kpis.csv with a tolerance of 1e-9 for rates and rounding tolerance for displayed numbers. Zero eligible cases produce NULL. Pending SLA cases never enter compliance denominators. Do not claim SQL execution until these checks actually run.

Duration queries use nearest-rank P90/P95 for readable MySQL SQL; pandas uses linear interpolation. SLA and count calculations must match exactly, while percentile estimates can differ slightly by the documented estimator. Week-over-week comparisons exclude partial boundary weeks. Rolling averages include zero-arrival calendar days.

The [SQL navigation](../sql/README.md) organizes queries by business purpose: model, KPIs, operations, customers and workforce. Agent outcomes are final-owner associations, not causal measures of individual ability. Workforce facts are aggregated separately before joins to prevent multiplicative ticket/log fanout. The earlier database/schema.sql, views.sql and analysis.sql paths remain compatibility entrypoints.

References: [MySQL CTE syntax](https://dev.mysql.com/doc/refman/8.0/en/with.html), [local import requirements](https://dev.mysql.com/doc/refman/8.0/en/load-data-local-security.html), [LOAD DATA behavior](https://dev.mysql.com/doc/refman/8.0/en/load-data.html).

