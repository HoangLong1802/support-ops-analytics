"""Final acceptance is kept outside public analytical artifacts."""
import json
import re
from pathlib import Path
import pandas as pd
from contract import ROOT,COLUMNS,SANITY,read_tables,hashes,validation_errors
from verified_metrics import summarize

def main():
    required=[
        "README.md","requirements.txt",".gitignore","AGENTS.md","STATE.md",
        ".agent/HANDOFF.md",".agent/HUMAN_REVIEW.md",".agent/current_plan.md",
        *[f"src/{name}.py" for name in ["generate_dataset","validate_generation","assess_data_quality","clean_data","validate_clean_data","verified_metrics","staffing_analysis"]],
        *[f"database/{name}.sql" for name in ["schema","import","validation","views","analysis"]],
        *[f"docs/{name}.md" for name in ["business_requirements","data_dictionary","data_lineage","generation_report","data_quality_report","cleaning_decisions","cleaning_report","sql_analysis_guide","workforce_methodology","insights"]],
        "powerbi/data_model.md","powerbi/measures.dax","powerbi/dashboard_spec.md",
        "data/analytics/verified_kpis.csv","data/analytics/staffing_daily.csv",
        *[f"data/processed/{name}_clean.csv" for name in COLUMNS],
        *[f"data/quarantine/{name}_quarantine.csv" for name in ["tickets","ticket_work_logs","workforce_daily"]],
    ]
    for path in required:
        assert (ROOT/path).is_file(), f"Missing required artifact: {path}"
    raw=read_tables()
    assert {p.name for p in (ROOT/"data/raw").iterdir() if p.is_file()}=={f"{name}.csv" for name in COLUMNS}
    assert len(raw["agents"])==18 and len(raw["sla_policies"])==16
    assert len(raw["tickets"])==15105 and raw["tickets"].ticket_id.nunique()==15000
    manifest=json.loads((ROOT/"data/analytics/generation_metadata.json").read_text())
    assert manifest["pristine_validation"]=="PASS" and manifest["reproducibility"]=="PASS"
    assert hashes()==manifest["hashes"]
    for key,(lo,hi) in SANITY.items():
        assert lo<=manifest["pristine_metrics"][key]<=hi,key
    assert not validation_errors(read_tables("processed"))
    audit=json.loads((ROOT/"data/analytics/cleaning_audit.json").read_text())
    for name in COLUMNS:
        assert audit["raw"][name]==audit["processed"][name]+audit["quarantined"][name]+audit["exact_copies_removed"][name]
    quality=json.loads((ROOT/"data/analytics/quality_audit.json").read_text())
    assert quality["hashes"]==hashes(),"Independent quality assessment hashes differ"
    tests=json.loads((ROOT/".agent/test_results.json").read_text())
    assert tests["tests_run"]>=14 and tests["failures"]==0 and tests["errors"]==0
    staff=pd.read_csv(ROOT/"data/analytics/staffing_daily.csv")
    assert len(staff)==365*3
    assert staff[["team","work_date"]].duplicated().sum()==0
    assert staff.forecast_handling_minutes.notna().sum()==(365-28)*3
    assert not list(ROOT.rglob("*.pbix"))
    assert not [p for p in (ROOT/"images/dashboard").iterdir() if p.suffix.lower() in [".png",".jpg",".jpeg"]]
    spec=(ROOT/"powerbi/dashboard_spec.md").read_text(encoding="utf-8-sig")
    assert len(re.findall(r"^## Page [123] ",spec,re.M))==3
    forbidden=re.compile(r"\b(?:Codex|ChatGPT|AI agent|owner authorization|agent handoff|prompt|phase gate)\b",re.I)
    paths=[ROOT/"README.md"]
    for directory in ["src","docs","database","powerbi"]:
        paths.extend(p for p in (ROOT/directory).rglob("*") if p.suffix in [".py",".md",".sql",".dax"])
    for path in paths:
        assert not forbidden.search(path.read_text(encoding="utf-8-sig")), f"Unnecessary public orchestration language: {path}"
    result={"status":"PASS","raw_hashes_unchanged":True,"raw_counts":{n:len(f) for n,f in raw.items()},
        "processed_counts":audit["processed"],"quarantine_counts":audit["quarantined"],"tests":tests,
        "sql":"Scripts Ready Only","power_bi":"Model, DAX, CSVs and three-page specification; Desktop execution pending",
        "public_trace_check":"PASS","kpis":summarize(read_tables("processed"))}
    (ROOT/".agent/acceptance_results.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print("Final analytical acceptance: PASS; SQL and Power BI native execution remain explicitly pending")

if __name__=="__main__":
    main()
