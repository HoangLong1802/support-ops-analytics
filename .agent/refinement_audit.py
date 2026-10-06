"""Internal measured evidence for the portfolio refinement."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import numpy as np
import pandas as pd
from contract import DAYS, hashes, read_tables, validation_errors
from assess_data_quality import assess
from clean_data import clean
from verified_metrics import summarize, ticket_metrics, workforce_metrics
from staffing_analysis import estimate

phase = sys.argv[1]
raw = read_tables()
data = read_tables('processed')
assert not validation_errors(data)
metadata = json.loads((ROOT / 'data/analytics/generation_metadata.json').read_text())
assert hashes() == metadata['hashes']
cleaned, quarantine, cleaning = clean(raw)
for name in data:
    pd.testing.assert_frame_equal(cleaned[name].reset_index(drop=True), data[name], check_dtype=False)
_, issues, profiles = assess(raw)
kpis = summarize(data)
saved = pd.read_csv(ROOT / 'data/analytics/verified_kpis.csv').set_index('metric').value
for key, value in kpis.items():
    assert np.isclose(value, saved[key], equal_nan=True), key
t = ticket_metrics(data['tickets'], data['sla_policies'])
w = workforce_metrics(data)
breach = t.resolution_sla_outcome.eq('BREACHED')
tech = t.category.eq('technical_support')
backlog = t.loc[~t.completed]
reopened = t.reopen_count.gt(0)
longest = t.loc[t.resolution_minutes.idxmax()]
daily = t.groupby('local_created_date').size().reindex(DAYS, fill_value=0)
staffing = estimate(data)
eligible = staffing.forecast_handling_minutes.notna()
segments = {
    'technical_tickets': int(tech.sum()),
    'technical_ticket_share': float(tech.mean()),
    'technical_resolution_breaches': int((tech & breach).sum()),
    'technical_resolution_breach_share': float((tech & breach).sum() / breach.sum()),
    'weekday_average_arrivals': float(daily[DAYS.dayofweek < 5].mean()),
    'weekend_average_arrivals': float(daily[DAYS.dayofweek >= 5].mean()),
    'morning_09_11_tickets': int(t.local_created_hour.between(9, 11).sum()),
    'morning_09_11_share': float(t.local_created_hour.between(9, 11).mean()),
    'peak_hour': int(t.local_created_hour.value_counts().idxmax()),
    'reopened_csat': float(t.loc[reopened, 'csat_score'].mean()),
    'reopened_responses': int(t.loc[reopened, 'csat_score'].count()),
    'not_reopened_csat': float(t.loc[~reopened, 'csat_score'].mean()),
    'not_reopened_responses': int(t.loc[~reopened, 'csat_score'].count()),
    'backlog_resolution_breached': int(backlog.resolution_sla_outcome.eq('BREACHED').sum()),
    'backlog_by_category': {str(key): int(value) for key, value in backlog.category.value_counts().items()},
    'backlog_over48_by_category': {str(key): int(value) for key, value in backlog.loc[backlog.backlog_age_minutes.gt(2880)].category.value_counts().items()},
    'longest_ticket': str(longest.ticket_id),
    'longest_resolution_hours': float(longest.resolution_minutes / 60),
    'longest_created_at': str(longest.created_at),
    'longest_resolved_at': str(longest.resolved_at),
    'staffing_eligible_team_days': int(eligible.sum()),
    'positive_gap_team_days': int(staffing.loc[eligible, 'staffing_gap_fte'].gt(0).sum()),
    'maximum_estimated_gap_fte': float(staffing.loc[eligible, 'staffing_gap_fte'].max()),
    'agent_days_over100_utilization': int(w.utilization.gt(1).sum()),
}
ticket_reasons = quarantine['tickets'].quarantine_reason.str.split(';').explode()
evidence = {
    'raw_hashes': hashes(), 'kpis': kpis, 'cleaning': cleaning,
    'quality_issues': issues, 'source_profiles': profiles, 'segments': segments,
    'conflicting_ticket_ids': int(quarantine['tickets'].loc[quarantine['tickets'].quarantine_reason.eq('conflicting_key'), 'ticket_id'].nunique()),
    'source_data_hashes': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT / 'data').rglob('*')) if p.is_file()},
}
if phase == 'after':
    previous = json.loads((ROOT / '.agent/refinement_before.json').read_text())
    for field in ('raw_hashes', 'cleaning', 'quality_issues', 'source_profiles', 'segments'):
        assert previous[field] == evidence[field], field
    for key, value in kpis.items():
        assert np.isclose(value, previous['kpis'][key], equal_nan=True), key
    assert previous['source_data_hashes'] == evidence['source_data_hashes'], 'Data artifact bytes changed'
(ROOT / f'.agent/refinement_{phase}.json').write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'phase': phase, 'validation': 'PASS', 'kpis': kpis, 'cleaning': cleaning, 'segments': segments, 'conflicting_ticket_ids': evidence['conflicting_ticket_ids']}, indent=2))
