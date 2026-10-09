# Case study: where do support tickets break their SLA?

**English** | [Tiếng Việt](portfolio_case_study.vi.md)

Synthetic data, so this shows method rather than business results.

**Question.** A support manager wants to know which part of the operation is failing its SLA, how old the backlog is, and whether staffing lines up with demand.

**What I did.**
1. Checked the keys and grain of five tables, removed exact duplicates and put untrustworthy rows in a quarantine file instead of deleting them.
2. Calculated KPIs in Python and SQL, then in DAX. I kept three things separate: who finally owned a ticket vs. who actually worked on it, a category's share of breaches vs. its own breach rate, and elapsed time vs. effort.
3. Built a 5-page Power BI report and compared the main KPIs against an independent Python calculation.

**What it showed.**
- Technical support is 29% of tickets but 50% of resolution breaches, and its team SLA is 63.6% vs about 81% for the others.
- Weekday volume is 1.9x weekend volume.
- 552 of 578 backlog tickets are older than 48 hours.
- CSAT is 4.07 but only 52% of completed tickets have a rating.

**What I would suggest.** Look at the technical queue (hand-offs, priority mix) first; compare arrivals with handling timestamps before changing shifts; read CSAT together with its response rate. These are hypotheses to test, not claims of improvement.

**Limits.** The patterns were built into the simulation. Reopen rate is not first-contact resolution. Case mix is not adjusted. MySQL scripts run in CI on MySQL 8.4, not on a local server. Two time-based DAX measures were not independently checked.

Links: [KPI definitions](kpi_definitions.md) · [data quality](data_quality_report.md) · [test report](test_report.md) · [Power BI](../powerbi/README.md) · [workbook](../output/customer_support_analysis.xlsx)
