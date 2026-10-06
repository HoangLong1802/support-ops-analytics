"""Record immutable data and KPI evidence before adding presentation outputs."""
from pathlib import Path
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
paths = sorted(p for p in (ROOT / 'data').rglob('*') if p.is_file())
values = {row['metric']: float(row['value']) for row in csv.DictReader((ROOT / 'data/analytics/verified_kpis.csv').open(encoding='utf-8-sig'))}
baseline = {'data_hashes': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}, 'kpis': values}
(ROOT / '.agent/output_baseline.json').write_text(json.dumps(baseline, indent=2) + '\n', encoding='utf-8')
print(f'Baseline saved: {len(paths)} data artifacts and {len(values)} verified KPIs.')
