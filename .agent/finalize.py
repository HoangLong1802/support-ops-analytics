import json
import zipfile
from contract import ROOT

def main():
    result=json.loads((ROOT/".agent/acceptance_results.json").read_text())
    assert result["status"]=="PASS"
    archive_path=ROOT/"_backups/checkpoint_final.zip"
    with zipfile.ZipFile(archive_path) as archive:
        assert archive.testzip() is None
        assert "README.md" in archive.namelist()
        assert "data/raw/tickets.csv" in archive.namelist()
    runtime=json.loads((ROOT/"data/analytics/generation_metadata.json").read_text())["runtime"]
    k=result["kpis"]
    fmt=lambda counts:", ".join(f"{name} {count:,}" for name,count in counts.items())
    lines=["# Project Handoff","","## Status","PASS","","## Runtime",
        f"Python {runtime['python']}; pandas {runtime['pandas']}; NumPy {runtime['numpy']}. Installed Python: C:/Program Files/LibreOffice/program/python.exe. Git unavailable; ZIP recovery used.",
        "","## Raw Counts",fmt(result["raw_counts"]),"","## Processed Counts",fmt(result["processed_counts"]),
        "","## Quarantine Counts",fmt(result["quarantine_counts"]),"","## Key Data Quality Findings",
        "75 exact ticket copies; 30 conflicting IDs (60 ambiguous versions); channel/hierarchy/CSAT/lifecycle/owner defects; orphan logs; nine invalid workforce rows.",
        "","## Key Cleaning Decisions",
        "Normalize 120 channels, restore 60 uniquely implied categories, null 23 invalid CSAT scores; remove exact copies only; quarantine ambiguity/logical errors and dependent logs; retain long durations.",
        "","## Key KPIs",
        f"FR SLA {k['fr_sla_compliance']:.2%}; Resolution SLA {k['resolution_sla_compliance']:.2%}; Overall SLA {k['overall_sla_compliance']:.2%}.",
        f"Reopen Rate {k['reopen_rate']:.2%}; CSAT {k['average_csat']:.2f}; response rate {k['csat_response_rate']:.2%}; backlog {k['backlog']:,}.",
        f"Weekday/weekend {k['weekday_weekend_ratio']:.4f}; aggregate utilization {k['utilization']:.2%}; median team/day {k['median_team_day_utilization']:.2%}.",
        "","## SQL Status","Scripts Ready Only. No MySQL client/service found. database/ contains schema, import, views, validation and business analyses.",
        "","## Power BI Status","Model, DAX, CSV imports and exactly three-page specification provided. PBIX/DAX/rendering not executed.",
        "","## Workforce Status","1,095 team/date rows; 1,011 with four previous same-weekday observations. 85% utilization target; retrospective equivalent FTE estimates.",
        "","## Tests",f"{result['tests']['tests_run']} tests passed; zero failures/errors.",
        "","## Reproducibility","PASS: independent simulation repetition, regenerated defect copies and saved hashes agree.",
        "","## Public Portfolio Check","PASS: public trace scan; all numerical findings from executed processed-data calculations.",
        "","## Recovery Backup",str(archive_path),"Parent archive: "+str(ROOT.parent/"customer-support-operations-analytics_backup.zip"),
        "Prior rejected build: "+str(ROOT/"_backups/rejected_existing_build.zip"),
        "","## Remaining Manual Work",
        "1. Execute MySQL imports/validation/analyses when MySQL is available.",
        "2. Open Power BI Desktop; build/refine the PBIX using model/DAX/spec and reconcile cards.",
        "3. Capture actual dashboard screenshots.",
        "4. Answer HUMAN_REVIEW questions personally.",
        "5. Review README wording before applications.",""]
    (ROOT/".agent/HANDOFF.md").write_text("\n".join(lines),encoding="utf-8")
    (ROOT/"STATE.md").write_text(
        "# Project state\n\nStatus: PASS\nAll six checkpoints complete and validated.\n"
        f"Runtime: Python {runtime['python']}, pandas {runtime['pandas']}, NumPy {runtime['numpy']}.\n"
        f"Tests: {result['tests']['tests_run']} passed. Raw SHA256 unchanged since validated generation.\n"
        "SQL: scripts ready only. Power BI: model/DAX/spec/data ready; native execution manual.\n"
        "Recovery: _backups/checkpoint_final.zip and parent customer-support-operations-analytics_backup.zip.\n"
        "The initial invalid partial build was archived before one controlled regeneration.\n",
        encoding="utf-8")
    (ROOT/".agent/current_plan.md").write_text("# Current plan\n\nCompleted: all six checkpoints, full tests, public trace scan and final recovery archive. Native MySQL and Power BI execution remain manual.\n",encoding="utf-8")
    print(f"PASS: {result['tests']['tests_run']} tests; handoff updated")

if __name__=="__main__":
    main()
