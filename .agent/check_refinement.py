"""Check navigation, public traces and preservation of the original SQL."""
from pathlib import Path
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
GIT = r'C:\Program Files\Git\cmd\git.exe'
def previous(path):
    return subprocess.check_output([GIT, 'show', '4b4c01b92883b2e0cbfb26e07b06b37a95bf2e70:' + path], cwd=ROOT)

readme = (ROOT / 'README.md').read_text(encoding='utf-8-sig')
word_count = len(readme.split())
assert 500 <= word_count <= 900, word_count
context_words = len((ROOT / 'docs/01_business_context.md').read_text().split())
assert context_words <= 600
headings = re.findall(r'^## (.+)$', readme, re.M)
assert headings == ['Business Problem', 'Analytical Workflow', 'Key Findings', 'Data Quality Decisions', 'Data Model', 'SQL Analysis', 'Power BI', 'Workforce Planning', 'Tools', 'Repository Guide', 'Reproduce'], headings

public_dirs = ['docs', 'src', 'tools', 'database', 'sql', 'powerbi', 'tests', 'images']
files = [ROOT / 'README.md'] + [p for name in public_dirs for p in (ROOT / name).rglob('*') if p.is_file() and p.suffix in {'.md','.py','.sql','.dax'} and '__pycache__' not in p.parts]
trace = re.compile(r'\b(?:Codex|ChatGPT|AI agents?|agent handoff|owner authorization|phase gates?|prompts?|Phase 1[AB]|authorization boundary|binding agent instruction)\b|\.agent/|STATE\.md|AGENTS\.md|_backups/', re.I)
bad_traces, broken_links = [], []
for path in files:
    text = path.read_text(encoding='utf-8-sig')
    for match in trace.finditer(text):
        bad_traces.append((path.relative_to(ROOT).as_posix(), match.group()))
    if path.suffix == '.md':
        for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
            target = link.split('#')[0]
            if target and not re.match(r'\w+://|mailto:', target):
                if not (path.parent / target).exists():
                    broken_links.append((path.relative_to(ROOT).as_posix(), target))
    elif path.suffix == '.py':
        compile(text, str(path), 'exec')
assert not bad_traces, bad_traces
assert not broken_links, broken_links

schema_old = previous('database/schema.sql').decode('utf-8-sig').replace('\r\n','\n').strip()
schema_new = (ROOT / 'sql/01_data_model.sql').read_text(encoding='utf-8-sig').strip()
assert schema_old == schema_new
views_old = previous('database/views.sql').decode('utf-8-sig').replace('\r\n','\n').strip()
views_new = (ROOT / 'sql/02_kpi_definitions.sql').read_text(encoding='utf-8-sig')
assert views_new.startswith(views_old)
original = previous('database/analysis.sql').decode('utf-8-sig').replace('\r\n','\n').strip()
blocks = [b for b in re.split(r'\n\s*\n', original) if not b.startswith('USE ')]
canonical = '\n'.join((ROOT / 'sql' / name).read_text(encoding='utf-8-sig') for name in ['02_kpi_definitions.sql','03_operations_analysis.sql','04_customer_analysis.sql','05_workforce_analysis.sql'])
assert len(blocks) == 23
for block in blocks:
    assert canonical.count(block) == 1, block.splitlines()[0]

byte_styles = {}
for path in ['src/build_portfolio.py', 'src/clean_data.py', 'tests/test_pipeline.py', 'README.md']:
    before, after = previous(path), (ROOT / path).read_bytes()
    byte_styles[path] = {'before_crlf': before.count(b'\r\n'), 'after_crlf': after.count(b'\r\n'), 'before_crcrlf': before.count(b'\r\r\n'), 'after_crcrlf': after.count(b'\r\r\n')}
result = {'status': 'PASS', 'readme_words': word_count, 'business_context_words': context_words, 'local_links': 'PASS', 'public_traces': 'PASS', 'python_syntax': 'PASS', 'unchanged_sql_schema': True, 'unchanged_sql_views': True, 'original_queries_preserved_once': len(blocks), 'line_endings': byte_styles}
(ROOT / '.agent/refinement_review.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, indent=2))
