"""Evidence-based normalization, exclusion reconciliation and dependent quarantine."""
import json
from collections import Counter
import numpy as np
import pandas as pd
from contract import ROOT, COLUMNS, KEYS, HIERARCHY, read_tables, hashes, rule_masks, conflict_mask, write_table, validation_errors

def clean(raw):
    data={name:frame.copy() for name,frame in raw.items()}
    quarantines={name:[] for name in COLUMNS}
    removed, fixes, reason_counts = {}, {}, {}
    for name,frame in data.items():
        removed[name]=int(frame.duplicated().sum())
        data[name]=frame.drop_duplicates().copy()
        data[name]["_source_row"]=data[name].index+2
        conflict=conflict_mask(data[name].drop(columns="_source_row"),KEYS[name])
        if conflict.any():
            rejected=data[name].loc[conflict].copy()
            rejected["quarantine_reason"]="conflicting_key"
            quarantines[name].append(rejected)
            data[name]=data[name].loc[~conflict].copy()
    t=data["tickets"]
    original=t.copy()
    t["channel"]=t.channel.astype("string").str.strip().str.lower()
    category_lookup={sub:category for category,subs in HIERARCHY.items() for sub in subs}
    infer=t.category.isna() & t.subcategory.isin(category_lookup)
    t.loc[infer,"category"]=t.loc[infer,"subcategory"].map(category_lookup)
    bad_csat=t.csat_score.notna() & (~t.csat_score.between(1,5) | t.csat_score.mod(1).ne(0))
    t.loc[bad_csat,"csat_score"]=np.nan
    fixes["channel_normalized"]=int(original.channel.ne(t.channel).sum())
    fixes["category_restored"]=int(infer.sum())
    fixes["invalid_csat_set_null"]=int(bad_csat.sum())
    fixes["unique_transformed_ticket_rows"]=int((original.channel.ne(t.channel) | infer | bad_csat).sum())
    def public_data():
        return {name:frame[COLUMNS[name]] for name,frame in data.items()}
    def reject(name,ignored=()):
        rules=rule_masks(public_data())[name]
        selected={rule:mask for rule,mask in rules.items() if rule not in ignored and mask.any()}
        if not selected:
            return
        table=pd.DataFrame(selected,index=data[name].index).fillna(False)
        bad=table.any(axis=1)
        rejected=data[name].loc[bad].copy()
        rejected["quarantine_reason"]=table.loc[bad].apply(lambda row:";".join(row.index[row]),axis=1)
        quarantines[name].append(rejected)
        data[name]=data[name].loc[~bad].copy()
    reject("agents")
    reject("sla_policies")
    reject("workforce_daily")
    reject("tickets")
    # Parent exclusions precede log checks so lost workforce/ticket links are explicit.
    reject("ticket_work_logs",ignored=("exceeds_attendance",))
    reject("ticket_work_logs")
    clean_data=public_data()
    errors=validation_errors(clean_data)
    if errors:
        raise ValueError("Clean validation failed: "+str(errors))
    q={}
    for name in COLUMNS:
        q[name]=pd.concat(quarantines[name],ignore_index=True) if quarantines[name] else pd.DataFrame(columns=COLUMNS[name]+["_source_row","quarantine_reason"])
        reasons=Counter(reason for row in q[name].quarantine_reason for reason in row.split(";"))
        reason_counts[name]=dict(reasons)
        assert len(raw[name])==removed[name]+len(q[name])+len(clean_data[name]), f"{name}: source-row reconciliation failed"
    report={"raw":{n:len(f) for n,f in raw.items()},"exact_copies_removed":removed,
        "transformations":fixes,"quarantined":{n:len(f) for n,f in q.items()},
        "processed":{n:len(f) for n,f in clean_data.items()},"reason_counts":reason_counts,"validation":"PASS"}
    return clean_data,q,report

def main():
    before=hashes()
    raw=read_tables()
    cleaned,quarantine,report=clean(raw)
    for name,frame in cleaned.items():
        write_table(ROOT/"data/processed"/f"{name}_clean.csv",frame)
    for name in ["tickets","ticket_work_logs","workforce_daily"]:
        write_table(ROOT/"data/quarantine"/f"{name}_quarantine.csv",quarantine[name])
    for name in ["agents","sla_policies"]:
        if len(quarantine[name]):
            write_table(ROOT/"data/quarantine"/f"{name}_quarantine.csv",quarantine[name])
    combined = pd.concat([frame.assign(dataset=name) for name,frame in quarantine.items()], ignore_index=True, sort=False)
    write_table(ROOT/"data/quarantine/all_quarantine_records.csv", combined)
    lines=["# Cleaning report","","Every source row is retained, removed as a redundant exact copy, or quarantined. Field transformations do not reduce row counts.","",
        "| Dataset | Raw | Exact copies removed | Quarantined | Processed | Reconciled |","|---|---:|---:|---:|---:|---|"]
    lines += [f"| {n} | {report['raw'][n]:,} | {report['exact_copies_removed'][n]} | {report['quarantined'][n]:,} | {report['processed'][n]:,} | PASS |" for n in COLUMNS]
    lines += ["","## Safe field transformations",""]+[f"- {n}: {count}" for n,count in report["transformations"].items()]
    lines += ["","## Quarantine reasons","","Reason counts may overlap; quarantine totals above count distinct source rows. Original values, source CSV row number (header = row 1) and all detected reasons are preserved.","",
        "| Dataset | Reason | Rows |","|---|---|---:|"]
    lines += [f"| {n} | {reason} | {count} |" for n,reasons in report["reason_counts"].items() for reason,count in reasons.items()]
    lines += ["","## Validation","","PASS: unique keys, canonical domains, valid hierarchy, foreign keys, UTC timestamp order, snapshot lifecycle, CSAT, integer reopens, workforce capacity and handling feasibility. Dependent logs losing a clean parent are quarantined. Legitimate extreme durations are retained.",
        "","Raw SHA256 before and after cleaning: identical."]
    assert before==hashes(),"Cleaning altered raw files"
    (ROOT/"docs/cleaning_report.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    decisions=["# Cleaning decisions","","Decisions use the independent assessment and executed cleaning counts. A source snapshot cannot establish a preferred version of conflicting records.","",
        "| Issue | Evidence | Business impact | Decision | Reason |","|---|---|---|---|"]
    decisions += [
        f"| Exact copies | {sum(report['exact_copies_removed'].values())} redundant rows | Inflated volume/effort | AUTO-FIX | Remove only fully identical copies. |",
        f"| Conflicting keys | {report['reason_counts']['tickets'].get('conflicting_key',0)} ticket versions | Ambiguous joins | QUARANTINE | Preserve every distinct version; no evidence supports a winner. |",
        f"| Channel formatting | {report['transformations']['channel_normalized']} normalized rows | Split channel groups | AUTO-FIX | Case and surrounding spaces do not change meaning. |",
        f"| Missing category, known unique subcategory | {report['transformations']['category_restored']} restored rows | Missing demand classification | AUTO-FIX | Approved hierarchy uniquely determines category. |",
        "| Missing subcategory or both hierarchy fields | See cleaning reason counts | Unknown case mix | QUARANTINE | Category alone cannot identify a subcategory. |",
        "| Invalid category/subcategory pair | See cleaning reason counts | Wrong routing and demand mix | QUARANTINE | Neither field establishes which value is correct. |",
        f"| Invalid CSAT | {report['transformations']['invalid_csat_set_null']} scores replaced by null | Biased satisfaction | AUTO-FIX | Retain the ticket; score cannot be recovered or clamped. |",
        "| Missing completed resolution, invalid event order, unknown owner | See cleaning reason counts | Invalid service timing or ownership | QUARANTINE | Snapshot provides no trustworthy repair evidence. |",
        "| Invalid/orphan work logs and workforce capacity | See cleaning reason counts | Wrong handling and utilization | QUARANTINE | Remove invalid parents before dependent log validation. |",
        "| Long logically valid durations | Duration percentiles in quality report | Long-tail mean bias | KEEP | External dependencies can legitimately delay completion. |",
    ]
    (ROOT/"docs/cleaning_decisions.md").write_text("\n".join(decisions)+"\n",encoding="utf-8")
    (ROOT/"data/analytics/cleaning_audit.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))

if __name__=="__main__":
    main()


