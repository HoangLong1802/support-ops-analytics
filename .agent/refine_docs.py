"""Write focused navigation and dashboard questions after the measured audit."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
documents = {
    'docs/business_requirements.md': '''# Business Requirements

Start with [Business Context](01_business_context.md) for the problem, stakeholders, questions, KPIs and limitations. [KPI Definitions](kpi_definitions.md) and [Data Dictionary](data_dictionary.md) provide the detailed reporting and source rules.
''',
    'docs/cleaning_decisions.md': '''# Cleaning Decisions

The analyst's decision table is in [03 — Cleaning Decisions](03_cleaning_decisions.md). It explains what was removed, normalized, derived, nulled, quarantined and retained, and why.

[The executed cleaning report](cleaning_report.md) contains row reconciliation and overlapping quarantine reasons.
''',
    'docs/insights.md': '''# Business Insights

Read [05 — Business Insights](05_business_insights.md) for eight measured findings, each with evidence, interpretation, a specific recommendation and a limitation. All data is synthetic; evidence is calculated from retained processed records.
''',
    'docs/data_lineage.md': '''# Data Lineage

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
''',
    'powerbi/dashboard_spec.md': '''# Dashboard Specification

The intended report has **three pages**. Its purpose is to move from service risk to queue review, then to effort and capacity. The model, import CSVs and DAX source are ready; **no PBIX, executed DAX or screenshots are supplied**. Build and validate the report in Power BI Desktop before capturing real images in `images/dashboard/`.

Use clear titles, explicit units and restrained colors. Final formatting and theme remain the report author's choice. Keep a visible **Synthetic data** label and snapshot **2026-10-01 00:00 Asia/Ho_Chi_Minh**. Use one compact card strip and a small set of question-driven visuals per page.

## Page 1 — Executive Overview

| Visual | Question answered | Fields / measures |
|---|---|---|
| Card strip | How much demand, service risk and unresolved work is present? | Total Tickets; Overall SLA Compliance %; Average CSAT; Backlog; Reopen Rate |
| Monthly demand line | Is the arrival cohort growing or shrinking across full months? | month_start; Total Tickets; MoM Ticket Change % |
| SLA outcome columns | Which service stage misses targets, and how many cases remain pending? | FR / Resolution / Overall MET, BREACHED and PENDING counts |
| Category contribution bars | Which categories contribute more breaches than their share of demand? | category; Ticket Share %; Resolution Breach Share % |
| Backlog status and aging summary | How much unresolved work is already aged at this snapshot? | status; Backlog; Backlog >24 / >48 / >72 Hours |

Tooltips show SLA eligible counts, CSAT responses and CSAT response rate. The backlog thresholds are nested counts, not mutually exclusive bands. Date, channel, priority and category slicers select ticket cohorts; the snapshot itself does not move.

## Page 2 — Operations Analysis

| Visual | Question answered | Fields / measures |
|---|---|---|
| Weekday demand bars | Which weekdays have the highest average arrivals per calendar day? | weekday_name; Average Daily Tickets |
| Local-hour arrival bars | When do tickets arrive during the day? | local_created_hour; Total Tickets |
| Category/subcategory matrix | Which case types combine substantial demand and weak resolution service? | category; subcategory; Total Tickets; Resolution SLA Compliance % |
| Priority and channel comparison | How does service vary against each cohort's policy targets? | priority; channel; FR / Resolution SLA Compliance %; eligible counts |
| Resolution distribution | How large are the long waits compared with typical completion time? | completed-ticket elapsed resolution bands; median and P95 measures in tooltip |
| Snapshot aging bands | Which categories contain backlog older than 48 or 72 hours? | category; mutually exclusive <=24h / 24–48h / 48–72h / >72h bands |

Create resolution and aging bands from the imported duration fields in Power Query. Use <= boundaries for the upper limit of each finite band. Completed-only resolution excludes unresolved cases; never label it handling time. Arrival hours use Asia/Ho_Chi_Minh and cannot establish hourly staffing gaps. Average Daily Tickets includes every selected calendar date, including zero arrivals.

## Page 3 — Agent & Team Performance

| Visual | Question answered | Fields / measures |
|---|---|---|
| Handling effort bars | Which actual handlers and teams carry the most recorded work? | agent/team; Handling Hours |
| Daily utilization matrix | Where does workload press against productive capacity? | agent/team/work date; Utilization %; capacity and effort in tooltip |
| Final-owner service table | Which ownership cohorts warrant review after considering sample size? | final owner; Total Tickets; Overall SLA Compliance %; eligible count |
| Customer outcome table | Which ownership cohorts have poor respondent CSAT or more reopens? | Average CSAT; CSAT Responses; CSAT Response Rate; Reopen Rate; ticket count |
| Case-mix matrix | Could assignment mix help explain differences in owner outcomes? | final owner/team; category; priority; ticket count |

Add the daily staffing estimate to the utilization tooltip for the matching team/work date, with the **85% target** and **four prior matching weekdays** stated. Insufficient history returns blank. FTE gaps are equivalent-capacity planning signals, not headcount or exact shifts.

Shared agent filters represent **final owner** for ticket outcomes and **actual handler** for effort/capacity. Date filters represent creation dates and work dates, respectively. Category/channel/priority affect ticket outcomes only; disable their interactions with full-capacity visuals and label the scope. Avoid a single agent league table that ignores case mix and hire dates.

## Desktop Validation

With filters cleared, reconcile cards and all SLA outcome counts to `data/analytics/verified_kpis.csv`. Test date, category, channel, priority and agent interactions; validate BLANK at zero capacity and exclusion of PENDING from compliance. Check weekday sorting, zero-arrival dates, partial rolling windows and snapshot labels. Save the actual PBIX and capture screenshots only after those checks pass.
''',
    '.agent/HUMAN_REVIEW.md': '''# Human Review

Answer these personally before presenting the portfolio. This file deliberately contains questions only.

1. Why remove 75 exact ticket copies but quarantine all 60 versions of 30 conflicting IDs?
2. Why retain TKT000178 even though its elapsed resolution is 8,441.82 hours?
3. Which actual data-quality issue has the greatest potential impact on SLA, and how would you demonstrate that impact?
4. Why separate ticket resolution duration from handling minutes, and final owners from actual handlers?
5. Why can productive utilization exceed 100% while handling stays within physical attendance?
6. Why is the 8.35% Reopen Rate not FCR?
7. Why use three fact tables and four shared dimensions, and how does that avoid duplicated totals?
8. Which finding would you present first to an Operations Manager, and what action would you propose?
9. What would you change if real event-history data included owner transfers, queue states and repeated contacts?
10. Which limitation of synthetic data matters most when interpreting the technical breach concentration?
11. Why do First Response, Resolution and Overall SLA have different eligible counts?
12. What can and cannot be concluded from reopened-ticket CSAT of 3.74 versus 4.10?
13. Why does the 85% planning assumption yield FTE gaps on some team-days despite 68.74% aggregate utilization?
14. Which Power BI interactions could accidentally compare a filtered ticket cohort with unfiltered daily capacity?
15. How would you reconcile MySQL and Power BI results to Python before claiming native validation?
''',
}
for name, text in documents.items():
    (ROOT / name).write_text(text, encoding='utf-8')

path = ROOT / 'src/clean_data.py'
text = path.read_text(encoding='utf-8')
start = text.index('    decisions=[')
end = text.index('    (ROOT/"data/analytics/cleaning_audit.json")', start)
replacement = '''    (ROOT/"docs/cleaning_decisions.md").write_text(
        "# Cleaning Decisions\\n\\n"
        "Read [03 — Cleaning Decisions](03_cleaning_decisions.md) for the analyst decision table. "
        "[The executed cleaning report](cleaning_report.md) contains reconciliation and reason counts.\\n",
        encoding="utf-8")
'''
path.write_text(text[:start] + replacement + text[end:], encoding='utf-8')
print(f'{len(documents)} navigation, report and review documents updated; curated cleaning table preserved on reruns.')
