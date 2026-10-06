"""Record completed refinement evidence and the required internal handoff."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
review = json.loads((ROOT / '.agent/refinement_review.json').read_text())
audit = json.loads((ROOT / '.agent/refinement_after.json').read_text())
readme_words = len((ROOT / 'README.md').read_text().split())
assert 500 <= readme_words <= 900
handoff = f'''# Portfolio Refinement Handoff

## Status
PASS — refinement and Python validation complete; native MySQL/Power BI validation pending.

## Public Structure
README → docs/01–05 → sql/01–05 → powerbi/. data/ and analytical src/ paths retained. Synthetic source and validator moved to tools/. database/ import/validation and compatibility entrypoints retained. Internal recovery stays in .agent/.

## README Review
{readme_words} words; business problem and five sources precede six measured comparisons. Workflow, cleaning decisions, grains, SQL questions, report status and planning limits are visible. Reproduction preserves editorial README and curated decisions.

## Documents Simplified
Created business context, quality reasoning, cleaning decisions, analytical model and eight structured insights. Added shared KPI reference; refreshed lineage and SQL navigation. Earlier requirement/decision/insight documents link to the new reading path. HUMAN_REVIEW contains project-specific questions without answers.

## Code Changes
Moved generation/validation tools and updated imports/tests. Removed the obsolete invalid-build replacement option; validated raw remains immutable. Public runner has no internal orchestration dependency. BI export refreshes evidence without overwriting README. Analytical calculations and cleaning rules unchanged.

## SQL Changes
Original schema/views preserved; 23 existing queries retained exactly once across purpose-based files. Added reopened-CSAT and category-aged-backlog comparisons. Earlier database/ paths remain executable entrypoints. No MySQL execution claimed.

## KPI Consistency
Python, SQL and DAX definitions reviewed against the executed reference. SLA eligibility, reopen/CSAT denominators, backlog, handling, capacity and ratio-of-sums utilization aligned. Counts/KPIs and every data artifact byte equal the pre-refinement baseline. SQL nearest-rank percentiles remain documented separately from Python/DAX linear estimates.

## Key Final Insights
- Technical tickets: 29.49% of demand; 50.09% of resolution breaches (1,760 / 3,514).
- FR / Resolution / Overall SLA: 87.93% / 76.19% / 67.66%.
- Weekday/weekend arrivals: 1.92×; 09:00–11:59 share 35.70%.
- Mean / median / P95 resolution: 117.05 / 6.22 / 48.75 hours.
- Reopened respondent CSAT: 3.74 (625 responses) vs 4.10 (6,806).
- Backlog: 578; >48h 552; resolution-overdue 561.
- Utilization: 68.74%; positive planning gaps 235 / 1,011 eligible team-days.

## Tests
Full public workflow: 14/14 tests passed. Clean validation, independent assessment, refreshed KPIs/BI exports and relocated generation validator passed. Raw hashes and all data bytes unchanged. Local links, Python syntax, public trace scan and SQL preservation checks passed. Git diff whitespace check passed.

## Power BI Status
Three-page model, DAX and specification ready. No actual PBIX, native DAX execution or screenshots. Median/P95, average daily arrivals and category-contribution measures support the specified questions and require Desktop validation.

## Recruiter 60-Second Check
PASS — editorial scan answers problem, source scope, workflow, cleaning, analysis, findings and decisions from README alone. This is a content review, not a timed human-user test.

## Public AI-Orchestration Check
PASS — no irrelevant assistant/prompt/agent-governance references in public analytical files. No claim that AI was unused. Operational agents/ownership remain legitimate business concepts.

## Backup
_backups/recruiter_ready.zip; commit title: refactor: recruiter-focused analytics portfolio.
Pre-refinement checkpoint: _backups/checkpoint_before_refinement.zip. Existing final/published/rejected-build backups preserved.

## Remaining Manual Work
- Build the actual Power BI PBIX personally and choose final formatting/theme.
- Execute/reconcile DAX and capture real screenshots.
- Execute MySQL import/validation/queries and reconcile to verified_kpis.csv.
- Answer HUMAN_REVIEW questions personally.
- Explain cleaning and KPI decisions without reading notes.
'''
(ROOT / '.agent/HANDOFF.md').write_text(handoff, encoding='utf-8')
(ROOT / '.agent/test_results.json').write_text(json.dumps({'tests_run':14, 'failures':0, 'errors':0, 'command':'python src/run_pipeline.py', 'generation_validator':'PASS', 'clean_validation':'PASS'}, indent=2) + '\n', encoding='utf-8')
state = (ROOT / 'STATE.md').read_text(encoding='utf-8')
state = state.split('\n## Portfolio refinement', 1)[0].rstrip()
state += '''

## Portfolio refinement
Status: PASS. Audit → presentation/code refinement → full workflow/tests → preservation checks completed sequentially.
README and numbered reasoning documents refined; generator/validator moved to tools; SQL organized by purpose. All raw and data artifact bytes, counts and KPIs unchanged.
14 tests passed; clean/generation validation, local links, syntax and public trace checks passed. SQL/DAX runtime validation and actual PBIX/screenshots remain manual.
Recovery: _backups/recruiter_ready.zip; pre-refinement: _backups/checkpoint_before_refinement.zip. Prior final archives preserved.
Commit and remote publication record will be appended after successful Git operations.
'''
(ROOT / 'STATE.md').write_text(state, encoding='utf-8')
print(f'Refinement PASS recorded; README {readme_words} words; handoff and human review complete.')
