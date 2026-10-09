# Support Operations Analytics

[![MySQL Validation](https://github.com/HoangLong1802/support-ops-analytics/actions/workflows/mysql-validation.yml/badge.svg)](https://github.com/HoangLong1802/support-ops-analytics/actions/workflows/mysql-validation.yml)

**English** | [Tiếng Việt](README.vi.md)

A customer support analytics project: Python for cleaning, MySQL and Excel for analysis, and a five-page Power BI report on top. It looks at ticket demand, SLA performance, backlog, customer satisfaction and agent workload.

> **The data is synthetic.** I generated it (seed 42, see [docs/data_source.md](docs/data_source.md)) so I could practise on realistic mess: duplicates, bad dates, inconsistent categories. Patterns such as "technical support is the weak spot" come from the simulation, not from a real company, so none of the findings are business results.

## The data

Five tables: tickets, agents, SLA policies, daily work logs and shifts. 18 agents in 3 teams, tickets from 1 Oct 2025 to 30 Sep 2026. Backlog is a snapshot at 1 Oct 2026 00:00 (UTC+7).

Of 15,105 raw ticket rows I dropped 75 exact duplicates, quarantined 256 rows that could not be trusted, and kept 14,774. Details are in [docs/data_quality_report.md](docs/data_quality_report.md).

## What I found

- **Technical support** has 29% of tickets but half of all resolution SLA breaches. Within the category, 40% of tickets breach. The technical support team's resolution SLA is 63.6% against about 81% for the other two teams.
- **Weekdays** average 46.9 tickets a day, weekends 24.4 (1.9x).
- **Backlog** is 578 open or pending tickets, and 552 of them are older than 48 hours.
- **SLA:** first-response compliance is 87.9%, resolution compliance 76.2%.
- **CSAT** averages 4.07 / 5, but only 52% of completed tickets have a rating, so I would not read much into it.

More detail and caveats: [docs/05_business_insights.md](docs/05_business_insights.md).

## Power BI report

![Overview](images/powerbi/operations_overview.png)
![SLA and demand](images/powerbi/sla_demand.png)
![Workforce](images/powerbi/workforce_performance.png)
![Customer experience](images/powerbi/customer_experience.png)
![Backlog](images/powerbi/backlog_operational_risk.png)

The report is in [powerbi/customer_support_operations.pbix](powerbi/customer_support_operations.pbix). The screenshots were captured from Power BI Desktop. More in [powerbi/README.md](powerbi/README.md).

## Checks

I recomputed the main KPIs in plain Python and compared them with the DAX results. 19 of 21 checks matched; two time-based measures (rolling 30-day average, month-over-month change) were not independently recomputed. See [docs/test_report.md](docs/test_report.md).

The MySQL scripts are written but I have not run them against a real MySQL server.

## Run it

Python 3.12+ with pandas, NumPy and openpyxl.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src/run_pipeline.py
```

More: [docs/how_to_run.md](docs/how_to_run.md).

## Layout

| Folder | Contents |
|---|---|
| `data/` | raw, processed and analytics CSVs |
| `src/` | cleaning, validation and export scripts |
| `sql/` | MySQL schema and analysis queries |
| `output/` | Excel workbook |
| `powerbi/` | PBIX, Power Query (M) and DAX |
| `docs/` | data dictionary, KPI definitions, data quality, test report, case study |
| `tests/` | pipeline tests and the Python reference for Power BI |
