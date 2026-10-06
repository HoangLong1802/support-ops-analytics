# Project Handoff

## Current Status
Python analysis, Markdown portfolio and real Excel output are validated. GitHub is the primary cross-machine recovery source. All synthetic data is committed; raw generation is already complete and frozen.

## Last Completed Work
Delivered the 14-sheet, 4-chart Excel workbook and processed-source BI specification. Versioned continuity files and historical evidence, pushed the checkpoint, then validated a fresh GitHub clone with Windows core.autocrlf=true.

## Latest Validation
23 unit tests passed from a fresh GitHub clone; all 42 Excel KPIs matched Python and saved exports. All 23 data artifact SHA256 values matched the pre-output baseline; the clone stayed clean. Evidence: continuity_validation.json, test_results.json, output_validation.json and output_baseline.json. Runtime: Python 3.12.13, pandas 3.0.6, NumPy 2.5.3, openpyxl 3.1.5. Native M/DAX/MySQL execution remains pending.

## Key KPI Results
14,774 tickets; 14,196 completed; 578 backlog. First-response SLA 87.93%, resolution SLA 76.19%, overall SLA 67.66% (each excludes its own pending cases). CSAT 4.07/5 from 7,431 responses; Reopen Rate 8.35%; productive utilization 68.74%. Resolution mean 117.05 hours, median 6.22 hours, P95 48.75 hours. Reopen Rate is not FCR; elapsed resolution is not handling effort.

## Files / Outputs
Data: data/raw (5 CSVs), data/processed (5), data/quarantine (4), data/analytics (9 CSV/JSON artifacts). Generation/validation tools are in tools; analysis in src and tests; SQL in database and sql; reports in docs. Workbook: output/customer_support_analysis.xlsx (192,140 bytes; SHA256 3e76cc70f6fb052c336e0cda49996318518807eac72d4318a51f60e6a7d5deed).

## Power BI Status
SPEC ONLY. powerbi/processed_queries.pq, data_model.md, measures.dax and dashboard_spec.md are ready for Desktop implementation. No PBIX or screenshots. Use processed CSVs as the primary source and set ProjectFolder to the new clone location.

## Git Status
Repository: https://github.com/HoangLong1802/support-ops-analytics.git

Current branch: main

Latest commit at handoff update: be72f2982869a328483a6fa505a9f527d0ee0bd5 - checkpoint: preserve cross-machine project continuity

Push status: PUSHED (all 118 remote blob hashes verified for that checkpoint).

This record describes the last verified push when written. Use git log -1 --oneline and git status -sb for the current checkout, including the commit that saves this handoff. Do not treat historical publication JSON as live Git status.

## Next Task
On the home PC, clone this repository (or git pull --ff-only), read STATE.md and current_plan.md, then build and reconcile the genuine three-page Power BI report.

Install Python 3.12+ and dependencies without copying this PC's temporary packages:

```powershell
git clone https://github.com/HoangLong1802/support-ops-analytics.git
cd support-ops-analytics
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe .agent/verify_continuity.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

For intentional analytical refreshes use python src/run_pipeline.py in the environment. Do not run the raw stage or historical one-time scripts just to resume.

## Manual Tasks Remaining
1. In Power BI Desktop, create the named queries from processed_queries.pq, configure relationships, add measures and reconcile KPIs to data/analytics/verified_kpis.csv and Excel Executive_KPIs.
2. Build the three specified pages; save powerbi/customer_support_analytics.pbix and real exports under output/dashboard/{executive_overview,operations_analysis,agent_team_performance}.png. Commit/push after validation; use Git LFS if the genuine PBIX exceeds GitHub's ordinary file limit.
3. Execute/reconcile the MySQL scripts using docs/sql_analysis_guide.md. Answer HUMAN_REVIEW.md personally before presenting the portfolio.
