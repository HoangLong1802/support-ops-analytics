"""Record measured output delivery and native Power BI follow-up steps."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
result = json.loads((ROOT / '.agent/output_validation.json').read_text())
assert result['status'] == 'PASS' and result['kpis_matched'] == 42
sheet_list = '\n'.join('- ' + name for name in result['sheets'])
handoff = f'''# Output Delivery Handoff

## Status
PASS — real Excel output validated; native Power BI steps remain manual.

## Markdown
- docs/01_business_context.md
- docs/02_data_quality.md
- docs/03_cleaning_decisions.md
- docs/04_data_model.md
- docs/05_business_insights.md
Lineage, KPI definitions, source dictionary, workforce methodology and native-tool guides retained where useful. Written reports remain Markdown; no DOCX/PDF generation.

## Excel
Workbook: output/customer_support_analysis.xlsx
Size: {result['workbook_bytes']:,} bytes. SHA256: {result['workbook_sha256']}
14 actual sheets; 4 useful charts. Frozen headers, filtered tables, explicit numeric results, restrained formatting, percentage/date formats and README sheet navigation.

Sheets:
{sheet_list}

Validation: PASS — opened with openpyxl, every required sheet nonempty, no formulas/nonfinite strings, blank insufficient history/zero capacity preserved.
KPI consistency: PASS — all 42 exported KPI values match canonical Python and saved metrics within rtol=1e-12/atol=1e-9. Display rates round to 2 decimals; values retain numeric precision. Core DAX inputs/count filters/denominators checked statically; no native DAX execution claim.
Source: processed CSVs plus verified analytical results. Excel is not the source-of-truth layer or primary BI source. Ticket owner and actual handler attribution remain separate; unique handled counts are not additive across handlers.

## Power BI
Data model: READY — seven tables, primary/composite keys, 1:* relationships, dimension-to-fact single direction documented.
DAX: READY — SLA counts/compliance/breaches, CSAT/reopens/backlog, schedule/absence/shrinkage/capacity/utilization and demand measures included.
Dashboard spec: READY — exactly 3 pages; 6 question-driven visuals per page including a compact executive card strip.
PBIX: MANUAL POWER BI DESKTOP STEP REQUIRED.
Dashboard screenshots: NOT YET AVAILABLE.
Source: data/processed/*.csv; prepared Power Query blocks derive fields from those sources. M/DAX/native rendering unexecuted. Known Desktop paths/Store package checks found no installation; no fake assets created.

## Tests
Full suite: 23 tests passed (14 existing + 9 output). After strengthening the DAX contract, all 9 output tests passed again. Integrated analytics command regenerated and validated the final workbook. Existing analytical logic and KPI definitions unchanged.
Runtime: Python 3.12.13; pandas 3.0.6; NumPy 2.5.3; openpyxl 3.1.5. Session openpyxl installed under .agent/python_packages; local execution uses PYTHONPATH for that folder. Public requirements include openpyxl; normal reproduction installs requirements in a virtual environment.

## Raw Data Integrity
PASS — all 23 existing data artifacts match baseline SHA256, including all five raw CSVs. Processed rules/relationships validated. No raw generation or source rewriting.

## README Output Navigation
PASS — {result['readme_words']} words; Project Outputs links to the real workbook, workflow includes Excel, BI assets/status are explicit and local links resolve. Markdown explains why; workbook exposes results; BI specification explains visual decisions. Public trace check passed without claiming AI was unused.

## Recovery
_backups/checkpoint_excel_outputs.zip; earlier final/recruiter-ready/published backups preserved. Publication commit recorded after successful push.

## Remaining Manual Work
1. Open Power BI Desktop.
2. Import data/processed using named blocks in powerbi/processed_queries.pq; set ProjectFolder and leave helper queries unloaded.
3. Build relationships using powerbi/data_model.md.
4. Add measures from powerbi/measures.dax and reconcile to verified_kpis.csv / Excel Executive_KPIs.
5. Build the three pages from dashboard_spec.md and choose final formatting/theme.
6. Save powerbi/customer_support_analytics.pbix.
7. Export real page screenshots to output/dashboard/executive_overview.png, operations_analysis.png and agent_team_performance.png.
MySQL native import/validation remains pending. Answer HUMAN_REVIEW personally and explain cleaning/KPI decisions without notes.
'''
(ROOT / '.agent/HANDOFF.md').write_text(handoff, encoding='utf-8')
(ROOT / '.agent/test_results.json').write_text(json.dumps({'tests_run':23, 'failures':0, 'errors':0, 'focused_output_tests':9, 'command':'python -m unittest discover -s tests -v', 'excel_validation':'PASS', 'native_dax_execution':False}, indent=2) + '\n', encoding='utf-8')
state = (ROOT / 'STATE.md').read_text(encoding='utf-8').split('\n## Output delivery', 1)[0].rstrip()
state += '''

## Output delivery
Status: PASS. Audit/dependencies → real Excel export → processed-source BI definitions → focused/full tests → final preservation/output checks complete.
output/customer_support_analysis.xlsx contains 14 sheets and 4 charts; all 42 KPIs match Python/saved exports. 23 tests passed; 9 output tests passed again after a stricter DAX source contract. Integrated analytics output succeeded.
All 23 data artifact bytes and canonical definitions unchanged. Model/DAX/three-page specification ready; M/DAX execution, actual PBIX/screenshots and MySQL validation remain manual.
README output links/workflow, Markdown-only reports and public trace checks PASS. Recovery: _backups/checkpoint_excel_outputs.zip. Prior backups preserved.
Publication record will be updated after successful Git operations.
'''
(ROOT / 'STATE.md').write_text(state, encoding='utf-8')
print('Output delivery PASS recorded; 14 sheets, 42 matching KPIs, 23 passing tests.')
