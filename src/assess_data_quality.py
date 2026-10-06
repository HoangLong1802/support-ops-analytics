"""Independent raw assessment based only on schema, records and operational rules."""
import json
import numpy as np
import pandas as pd
from contract import ROOT, COLUMNS, KEYS, DAYS, ZONE, SNAPSHOT, read_tables, hashes, rule_masks, timestamps, dates
from verified_metrics import ticket_metrics

def assess(data):
    rules = rule_masks(data)
    issues, profiles = [], []
    for name, frame in data.items():
        profiles.append({
            "dataset":name,"grain":", ".join(KEYS[name]),"rows":len(frame),"columns":len(frame.columns),
            "missing_cells":int(frame.isna().sum().sum()),"exact_copies":int(frame.duplicated().sum()),
            "key_unique":bool(not frame.duplicated(KEYS[name]).any()),
            "unique_affected_rows":int(pd.concat(list(rules[name].values()),axis=1).any(axis=1).sum()),
        })
        # Secondary field issues exclude redundant exact copies and ambiguous keys.
        independent = ~rules[name]["exact_duplicate"] & ~rules[name]["conflicting_key"]
        for rule,mask in rules[name].items():
            use = mask if rule in ["exact_duplicate","conflicting_key","missing_key"] else mask & independent
            count = int(use.sum())
            if count == 0:
                continue
            treatment = "AUTO-FIX" if rule in ["exact_duplicate","channel_format","invalid_csat"] else "QUARANTINE"
            if rule=="missing_hierarchy":
                treatment="REVIEW"
            severity = "LOW" if rule=="channel_format" else ("MEDIUM" if rule=="invalid_csat" else "HIGH")
            if rule in ["conflicting_key","response_order","resolution_order","completed_missing_fields","invalid_capacity","exceeds_attendance"]:
                severity="CRITICAL"
            impact = {
                "exact_duplicate":"Repeated records inflate volume or effort.",
                "conflicting_key":"Identity is ambiguous; joins cannot select a reliable version.",
                "channel_format":"Formatting splits channel groups without changing their meaning.",
                "invalid_csat":"Out-of-domain scores bias satisfaction.",
                "missing_hierarchy":"Unknown demand categories affect routing and mix reporting.",
                "invalid_capacity":"Invalid productive capacity distorts utilization and staffing.",
                "exceeds_attendance":"Recorded effort exceeds physical attendance.",
                "missing_workforce":"Handling has no reliable capacity denominator.",
                "unknown_ticket":"Handling refers to a missing or ambiguous ticket.",
                "completed_missing_fields":"Completed lifecycle lacks evidence needed for service metrics.",
            }.get(rule,"Contract violation can distort service, workload or relationship reporting.")
            issues.append({"dataset":name,"issue":rule,"count":count,"percentage":100*count/len(frame),"severity":severity,"business_impact":impact,"treatment":treatment})
    return rules,issues,profiles

def statistical_profiles(data,rules):
    t=data["tickets"]
    valid=~rules["tickets"]["conflicting_key"] & ~rules["tickets"]["exact_duplicate"]
    for rule in ["invalid_created","invalid_response_parse","invalid_resolution_parse","response_order","resolution_order","completed_missing_fields","unresolved_has_resolution"]:
        valid &= ~rules["tickets"][rule]
    tm=ticket_metrics(t.loc[valid],data["sla_policies"])
    logs=data["ticket_work_logs"]
    lvalid=~rules["ticket_work_logs"]["invalid_handling"] & ~rules["ticket_work_logs"]["exact_duplicate"]
    series = {
        "First response minutes":tm.first_response_minutes,
        "Resolution minutes":tm.resolution_minutes,
        "Snapshot backlog age minutes":tm.backlog_age_minutes,
        "Handling minutes per entry":logs.loc[lvalid,"handling_minutes"],
    }
    return {name:{"observations":int(s.notna().sum()),"median":float(s.median()),"P90":float(s.quantile(.9)),"P95":float(s.quantile(.95)),"P99":float(s.quantile(.99)),"max":float(s.max())} for name,s in series.items()}

def main():
    before=hashes()
    data=read_tables()
    for name,columns in COLUMNS.items():
        if list(data[name].columns)!=columns:
            raise ValueError(f"{name}: unexpected schema")
    rules,issues,profiles=assess(data)
    statistics=statistical_profiles(data,rules)
    after=hashes()
    assert before==after,"Assessment altered raw data"
    lines=["# Data quality report","","Five synthetic operational sources are profiled before any cleaning. Checks use source records, the approved schema and business rules. Optional lifecycle timestamps and CSAT nulls are profiled separately from contract errors.","",
        "Workflow: understand grain → profile values → validate rules → check relationships → classify impact → recommend treatment.","",
        "## Source profiles","","| Dataset | Key/grain | Rows | Columns | Missing cells | Exact copies | Key unique | Unique affected rows |","|---|---|---:|---:|---:|---:|---|---:|"]
    lines += [f"| {p['dataset']} | {p['grain']} | {p['rows']:,} | {p['columns']} | {p['missing_cells']:,} | {p['exact_copies']} | {p['key_unique']} | {p['unique_affected_rows']:,} |" for p in profiles]
    lines += ["","Missing cells above include legitimate optional values; they are not counts of invalid rows. Unique affected rows use the union of rule masks rather than the sum of overlapping issues.",
        "","## Issue registry","","Secondary field counts exclude exact copies and conflicting-key records to avoid duplicated diagnoses. Conflicting-key counts include every ambiguous version.","",
        "| Dataset | Issue | Rows | % of raw rows | Severity | Impact | Treatment |","|---|---|---:|---:|---|---|---|"]
    lines += [f"| {i['dataset']} | {i['issue']} | {i['count']} | {i['percentage']:.2f}% | {i['severity']} | {i['business_impact']} | {i['treatment']} |" for i in issues]
    lines += ["","## Types, domains and relationships","","Validation includes timestamp/date parsing, integer domains, category/subcategory pairs, policy/channel/priority agreement, agent hire dates, ticket lifecycle, workforce composite keys and handling against physical attendance. String casing is measured before normalization. Completed tickets require owner, response and resolution; unresolved tickets cannot contain resolution or CSAT.",
        "","### Date coverage",""]
    workforce=data["workforce_daily"]
    existing=set(zip(workforce.agent_id,workforce.work_date))
    expected={(row.agent_id,d.strftime("%Y-%m-%d")) for row in data["agents"].itertuples(index=False) for d in DAYS if d>=pd.Timestamp(row.hire_date)}
    lines.append(f"Active-agent calendar pairs expected: {len(expected):,}; missing: {len(expected-existing):,}; extra: {len(existing-expected):,}. Off days are present with zero minutes; pre-hire dates are outside coverage.")
    lines += ["","## Statistical observations","","Logical errors are excluded from duration profiling. Long valid records remain statistical observations and are retained.","",
        "| Measure | N | Median | P90 | P95 | P99 | Maximum |","|---|---:|---:|---:|---:|---:|---:|"]
    lines += [f"| {name} | {p['observations']:,} | {p['median']:.2f} | {p['P90']:.2f} | {p['P95']:.2f} | {p['P99']:.2f} | {p['max']:.2f} |" for name,p in statistics.items()]
    lines += ["","## Integrity evidence","","Raw SHA256 before and after assessment: identical.","","| File | SHA256 |","|---|---|"]
    lines += [f"| {name}.csv | {digest} |" for name,digest in before.items()]
    (ROOT/"docs/data_quality_report.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    (ROOT/"data/analytics/quality_audit.json").write_text(json.dumps({"issues":issues,"profiles":profiles,"statistics":statistics,"hashes":before},indent=2),encoding="utf-8")
    print(f"Independent assessment complete: {len(issues)} findings; raw hashes unchanged")

if __name__=="__main__":
    main()


