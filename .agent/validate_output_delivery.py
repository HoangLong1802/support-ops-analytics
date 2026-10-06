"""Record executed output checks separately from unexecuted native BI validation."""
from pathlib import Path
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from contract import read_tables, validation_errors
from export_excel import OUTPUT, SHEETS, verified_inputs, validate_workbook

baseline = json.loads((ROOT / '.agent/output_baseline.json').read_text())
current = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT / 'data').rglob('*')) if p.is_file()}
assert baseline['data_hashes'] == current, 'A data artifact changed'
data = read_tables('processed')
assert not validation_errors(data)
kpis = verified_inputs(data)
for key, value in kpis.items():
    assert abs(value - baseline['kpis'][key]) < 1e-9, key
result = validate_workbook(OUTPUT, kpis)
public = [ROOT / 'README.md']
for name in ['docs', 'src', 'tools', 'powerbi', 'sql', 'database', 'tests', 'images']:
    public.extend(p for p in (ROOT / name).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix in {'.md','.py','.dax','.sql','.pq'})
bad_links, trace = [], []
pattern = re.compile(r'\b(?:Codex|ChatGPT|AI agents?|agent handoff|owner authorization|phase gates?|prompts?)\b|\.agent/|STATE\.md|AGENTS\.md|_backups/', re.I)
for path in public:
    text = path.read_text(encoding='utf-8-sig')
    if pattern.search(text):
        trace.append(path.relative_to(ROOT).as_posix())
    if path.suffix == '.md':
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
            target = target.split('#')[0]
            if target and not re.match(r'\w+://', target) and not (path.parent / target).exists():
                bad_links.append((path.name, target))
    elif path.suffix == '.py':
        compile(text, str(path), 'exec')
assert not trace, trace
assert not bad_links, bad_links
assert not any(p.suffix.lower() in {'.docx','.doc','.pdf'} for p in (ROOT / 'output').rglob('*'))
assert not any('python-docx' in p.read_text(encoding='utf-8-sig') or 'from docx ' in p.read_text(encoding='utf-8-sig') for p in (ROOT / 'src').glob('*.py'))
for path in [ROOT / 'powerbi/customer_support_analytics.pbix', ROOT / 'output/dashboard/executive_overview.png', ROOT / 'output/dashboard/operations_analysis.png', ROOT / 'output/dashboard/agent_team_performance.png']:
    assert not path.exists(), 'Unexpected unvalidated dashboard asset'
spec = (ROOT / 'powerbi/dashboard_spec.md').read_text()
assert len(re.findall(r'^## Page [123] ', spec, re.M)) == 3
readme = (ROOT / 'README.md').read_text()
assert '## Project Outputs' in readme and 'output/customer_support_analysis.xlsx' in readme
assert 'Excel Analytical Output' in readme and 'Processed Data' in readme
result.update(status='PASS', sheets=SHEETS, workbook=str(OUTPUT), workbook_sha256=hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
              workbook_bytes=OUTPUT.stat().st_size, data_artifacts_unchanged=len(current), processed_validation='PASS',
              kpi_consistency='PASS: Python/saved results/Excel; core DAX source contract checked by tests',
              native_m_dax_sql='NOT EXECUTED', pbix='MANUAL POWER BI DESKTOP STEP REQUIRED', screenshots='NOT YET AVAILABLE',
              markdown_links='PASS', public_trace='PASS', readme_words=len(readme.split()))
(ROOT / '.agent/output_validation.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, indent=2))

path = ROOT / 'requirements.txt'
path.write_bytes(path.read_text(encoding='utf-8-sig').encode('utf-8'))
