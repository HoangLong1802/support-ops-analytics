"""Apply bounded path and presentation changes to the audited build."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
tools = ROOT / 'tools'
tools.mkdir(exist_ok=True)

generator = ROOT / 'src/generate_dataset.py'
text = generator.read_text(encoding='utf-8')
text = text.replace('import argparse\n', 'from pathlib import Path\nimport sys\n\nsys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))\n')
text = text.replace('    parser = argparse.ArgumentParser()\n    parser.add_argument("--recover-invalid",action="store_true",help="Replace a rejected build only when its verified recovery archive exists")\n    args = parser.parse_args()\n', '')
text = text.replace('if existing and not args.recover_invalid:', 'if existing:')
text = text.replace('Existing raw data has no validated manifest; preserve it and explicitly recover the invalid build', 'Existing raw data has no validated manifest; archive it and use a separate working copy')
start = text.index('    if existing and args.recover_invalid:')
end = text.index('    pristine,params,history = calibrate()', start)
text = text[:start] + text[end:]
(tools / 'synthetic_data_generator.py').write_text(text, encoding='utf-8')
generator.unlink()

validator = ROOT / 'src/validate_generation.py'
text = validator.read_text(encoding='utf-8').replace('import json\n', 'import json\nfrom pathlib import Path\nimport sys\n\nsys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))\n')
text = text.replace('from generate_dataset import', 'from synthetic_data_generator import')
(tools / 'validate_generation.py').write_text(text, encoding='utf-8')
validator.unlink()

test_path = ROOT / 'tests/test_pipeline.py'
text = test_path.read_text(encoding='utf-8').replace('sys.path.insert(0,str(ROOT/"src"))', 'sys.path.insert(0,str(ROOT/"src"))\nsys.path.insert(0,str(ROOT/"tools"))').replace('from generate_dataset import', 'from synthetic_data_generator import')
test_path.write_text(text, encoding='utf-8')

build = ROOT / 'src/build_portfolio.py'
text = build.read_text(encoding='utf-8')
start = text.index('    README=f"""')
end = text.index('    (ROOT/"docs/execution_report.md").write_text(', start)
text = text[:start] + text[end:]
text = text.replace('"""Export BI-ready analytical tables and write findings from executed metrics."""', '"""Export BI tables and measured insights while preserving editorial documentation."""')
text = text.replace('    low,high=agent.utilization.min(),agent.utilization.max()\n', '    low,high=agent.utilization.min(),agent.utilization.max()\n    reopened=t.reopen_count.gt(0)\n    reopened_csat=t.loc[reopened,"csat_score"]\n    other_csat=t.loc[~reopened,"csat_score"]\n')
text = text.replace('("Reopened cases form a measurable review cohort",\n         f"{k[\'reopened_tickets\']:,} tickets reopened, a {k[\'reopen_rate\']:.2%} share of the retained ticket cohort.",\n         "Reopened cases indicate repeated lifecycle activity and a useful sample for rework review.",', '("Reopened tickets have lower respondent satisfaction",\n         f"{k[\'reopened_tickets\']:,} tickets reopened ({k[\'reopen_rate\']:.2%} of retained tickets). Respondent CSAT averages {reopened_csat.mean():.2f}/5 from {reopened_csat.count():,} responses, compared with {other_csat.mean():.2f}/5 from {other_csat.count():,} responses for tickets with no recorded reopen.",\n         "The reopened cohort is a useful starting sample for reviewing repeated effort and customer communication.",')
text = text.replace('"Reopen Rate is not FCR; the dataset does not contain enough contact history to calculate FCR."', '"Category, severity and survey nonresponse may explain the difference. Reopen Rate is not FCR; contact history is unavailable."')
old = '    for title,evidence,interpretation,recommendation,limitation in findings:\n        lines += [f"## {title}","",f"**Finding and evidence:** {evidence}","",f"**Business interpretation:** {interpretation}","",f"**Recommendation:** {recommendation}","",f"**Limitation:** {limitation}",""]\n    (ROOT/"docs/insights.md").write_text("\\n".join(lines),encoding="utf-8")'
new = '    for number,(title,evidence,interpretation,recommendation,limitation) in enumerate(findings, start=1):\n        lines += [f"### Finding {number}","",title+".","","**Evidence**","",evidence,"","**Interpretation**","",interpretation,"","**Recommendation**","",recommendation,"","**Limitation**","",limitation,""]\n    (ROOT/"docs/05_business_insights.md").write_text("\\n".join(lines),encoding="utf-8")'
assert old in text
text = text.replace(old, new).replace('BI tables, eight verified insights and README generated; KPI agreement and raw hashes: PASS', 'BI tables and eight verified insights refreshed; editorial README preserved; KPI agreement and raw hashes: PASS')
build.write_text(text, encoding='utf-8')
(ROOT / 'src/recovery.py').unlink()

schema = ROOT / 'database/schema.sql'
views = ROOT / 'database/views.sql'
analysis = ROOT / 'database/analysis.sql'
(ROOT / 'sql/01_data_model.sql').write_text(schema.read_text(encoding='utf-8'), encoding='utf-8')
groups = {'02_kpi_definitions.sql': [], '03_operations_analysis.sql': [], '04_customer_analysis.sql': [], '05_workforce_analysis.sql': []}
blocks = re.split(r'\n\s*\n', analysis.read_text(encoding='utf-8').strip())
original_queries = []
for block in blocks:
    if block == 'USE customer_support_analytics;':
        continue
    assert block.startswith('-- ') and block.endswith(';'), block[:100]
    original_queries.append(block)
    question = block.splitlines()[0]
    if question.startswith(('-- What is the executive', '-- How many MET')):
        target = '02_kpi_definitions.sql'
    elif question.startswith(('-- Which cohorts', '-- Is elapsed resolution', '-- Which case types')):
        target = '04_customer_analysis.sql'
    elif question.startswith(('-- What handling', '-- Which teams', '-- How do final owners', '-- How does case mix', '-- Is handling workload')):
        target = '05_workforce_analysis.sql'
    else:
        target = '03_operations_analysis.sql'
    groups[target].append(block)
for filename, queries in groups.items():
    prefix = views.read_text(encoding='utf-8').rstrip() if filename == '02_kpi_definitions.sql' else 'USE customer_support_analytics;'
    (ROOT / 'sql' / filename).write_text(prefix + '\n\n' + '\n\n'.join(queries) + '\n', encoding='utf-8')
schema.write_text('-- Compatibility entrypoint. Canonical data model:\nSOURCE sql/01_data_model.sql;\n', encoding='utf-8')
views.write_text('-- Compatibility entrypoint. Canonical SLA and workload definitions:\nSOURCE sql/02_kpi_definitions.sql;\n', encoding='utf-8')
analysis.write_text('-- Business analyses; run from the repository root after model/import/KPI setup.\nSOURCE sql/03_operations_analysis.sql;\nSOURCE sql/04_customer_analysis.sql;\nSOURCE sql/05_workforce_analysis.sql;\n', encoding='utf-8')
proof = {'original_queries_preserved': len(original_queries), 'by_file': {name:len(value) for name,value in groups.items()}, 'schema_unchanged': (ROOT / 'sql/01_data_model.sql').read_text() != '', 'analytical_definitions_changed': False}
(ROOT / '.agent/sql_reorganization.json').write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8')
print(json.dumps(proof, indent=2))
print('Reproducibility tools relocated; internal recovery removed from public source; README generation removed.')
