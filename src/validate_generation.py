"""Recreate pristine simulation in memory and verify frozen raw artifacts."""
import json
from contract import ROOT, COLUMNS, SANITY, hashes, read_tables, validation_errors
from generate_dataset import simulate, inject_defects, fingerprints
from verified_metrics import summarize

def main():
    manifest = json.loads((ROOT/"data/analytics/generation_metadata.json").read_text())
    assert hashes()==manifest["hashes"], "Frozen raw hashes differ"
    pristine = simulate(manifest["parameters"])
    assert not validation_errors(pristine), validation_errors(pristine)
    metrics = summarize(pristine)
    for key,(lo,hi) in SANITY.items():
        assert lo<=metrics[key]<=hi, f"{key}: {metrics[key]} outside {lo}..{hi}"
    assert len(pristine["tickets"])==15000
    assert pristine["tickets"].ticket_id.tolist()==[f"TKT{i:06d}" for i in range(1,15001)]
    assert pristine["tickets"].created_at.is_monotonic_increasing
    raw,_ = inject_defects(pristine)
    assert fingerprints(raw)==manifest["hashes"], "Saved raw differs from deterministic generation"
    actual = read_tables()
    assert len(actual["tickets"])==15105
    assert actual["tickets"].duplicated().sum()==75
    for name in COLUMNS:
        assert list(actual[name].columns)==COLUMNS[name]
    print("Pristine contract, sanity ranges, deterministic reproduction and saved raw hashes: PASS")

if __name__=="__main__":
    main()


