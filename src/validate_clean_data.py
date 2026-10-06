"""Validate clean records, persisted reconciliation and frozen source checksums."""
import json
from contract import ROOT, COLUMNS, read_tables, hashes, validation_errors

def main():
    data=read_tables("processed")
    errors=validation_errors(data)
    report=json.loads((ROOT/"data/analytics/cleaning_audit.json").read_text())
    for name in COLUMNS:
        if report["raw"][name]!=report["processed"][name]+report["quarantined"][name]+report["exact_copies_removed"][name]:
            errors.append(f"{name}: counts do not reconcile")
        if len(data[name])!=report["processed"][name]:
            errors.append(f"{name}: persisted clean count differs")
    manifest=json.loads((ROOT/"data/analytics/generation_metadata.json").read_text())
    if hashes()!=manifest["hashes"]:
        errors.append("Raw SHA256 mismatch")
    if errors:
        raise ValueError("\n".join(errors))
    print("Clean schemas, rules, relationships, feasibility, reconciliation and immutable raw: PASS")

if __name__=="__main__":
    main()


