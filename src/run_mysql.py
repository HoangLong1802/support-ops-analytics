"""Execute all canonical MySQL scripts in a fresh project-only database.
No DROP/TRUNCATE or server-global changes. Writes execution/reconciliation receipts.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
ORDER = ["sql/01_data_model.sql","database/import.sql","sql/02_kpi_definitions.sql",
         "database/validation.sql","sql/03_operations_analysis.sql","sql/04_customer_analysis.sql",
         "sql/05_workforce_analysis.sql","sql/06_claim_verification.sql"]
DEFAULT_DB = "support_ops_verify_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

def prepared(rel, database=DEFAULT_DB):
    if not re.fullmatch(r"support_ops_verify_[a-z0-9_]+",database) or len(database)>64:
        raise ValueError("Database must use support_ops_verify_ prefix and lowercase letters/digits/underscore; max 64 chars")
    text=(ROOT/rel).read_text(encoding="utf-8-sig")
    return text.replace("I:/DA/data/processed/",ROOT.as_posix()+"/data/processed/").replace(
        "__PROJECT_ROOT__",ROOT.as_posix()).replace("customer_support_analytics",database)

def reconciliation_sql(database):
    sql=f"USE {database};\nSET SESSION div_precision_increment=12;\n"
    queries={"counts":"SELECT 'total_tickets',COUNT(*) FROM vw_ticket_service_metrics",
             "categories":"SELECT category,COUNT(*),SUM(resolution_sla_outcome<>'PENDING'),SUM(resolution_sla_outcome='BREACHED') FROM vw_ticket_service_metrics GROUP BY category ORDER BY category",
             "demand":"""SELECT IF(d.is_weekend,'Weekend','Weekday'),SUM(COALESCE(t.n,0)),COUNT(*),
 SUM(COALESCE(t.n,0)=0),AVG(CAST(COALESCE(t.n,0) AS DECIMAL(30,12)))
 FROM dim_date d LEFT JOIN (SELECT local_created_date,COUNT(*) AS n FROM fact_tickets GROUP BY local_created_date) t
 ON t.local_created_date=d.date_key GROUP BY d.is_weekend ORDER BY d.is_weekend"""}
    for prefix in ("fr","resolution","overall"):
        for outcome in ("met","breached","pending"):
            queries["counts"]+=f" UNION ALL SELECT '{prefix}_sla_{outcome}',SUM({prefix}_sla_outcome='{outcome.upper()}') FROM vw_ticket_service_metrics"
    return {k:sql+v+";\n" for k,v in queries.items()}

def reconcile(outputs):
    from independent_validation import build
    expected=build()
    differences=[]
    expected_keys={"counts":{"total_tickets"}|{f"{p}_sla_{o}" for p in ("fr","resolution","overall") for o in ("met","breached","pending")},
                   "categories":{r["category"] for r in expected["category_expected"]},
                   "demand":set(expected["daily_demand"])}
    for section,keys in expected_keys.items():
        observed=[line.split("\t")[0] for line in outputs[section].splitlines()]
        if len(observed)!=len(set(observed)) or set(observed)!=keys:
            return {"status":"FAIL","error":"Missing, duplicate or unexpected groups in "+section,"differences":[]}
    for line in outputs["counts"].splitlines():
        key,value=line.split("\t")
        differences.append({"scope":key,"expected":expected["kpi_expected"][key],"actual":int(value),
                            "difference":int(value)-expected["kpi_expected"][key]})
    categories={r["category"]:r for r in expected["category_expected"]}
    for line in outputs["categories"].splitlines():
        cat,*values=line.split("\t")
        for key,value in zip(("tickets","resolution_eligible","resolution_breaches"),values):
            differences.append({"scope":cat+"/"+key,"expected":categories[cat][key],"actual":int(value),
                                "difference":int(value)-categories[cat][key]})
    for line in outputs["demand"].splitlines():
        name,*values=line.split("\t")
        for key,value in zip(("tickets","calendar_days","zero_ticket_days","average_daily_tickets"),values):
            expected_value=expected["daily_demand"][name][key]
            differences.append({"scope":name+"/"+key,"expected":expected_value,"actual":float(value),
                                "difference":float(value)-expected_value})
    # Detect missing groups/rows as well as wrong values.
    if len(differences)!=10+15+8 or any(abs(d["difference"])>1e-9 for d in differences):
        return {"status":"FAIL","differences":differences}
    return {"status":"PASS","differences":differences}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--dry-run",action="store_true")
    parser.add_argument("--client",default=os.environ.get("MYSQL_EXE") or shutil.which("mysql"))
    parser.add_argument("--database",default=DEFAULT_DB)
    args=parser.parse_args()
    # Validate identifier before any SQL/client operation.
    prepared(ORDER[0],args.database)
    target=ROOT/"output/mysql"
    target.mkdir(parents=True,exist_ok=True)
    if args.dry_run:
        for rel in ORDER:
            (target/Path(rel).name).write_text(prepared(rel,args.database),encoding="utf-8",newline="\n")
        print("Prepared SQL; NOT executed. Target database: "+args.database)
        return
    receipt={"status":"BLOCKED","database":args.database,"client_version":None,"server_version":None,
             "scripts":[],"reconciliation":{"status":"NOT_RUN"},"commands":[]}
    def save():
        (target/"execution_receipt.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    try:
        if not args.client:
            raise RuntimeError("mysql client unavailable: MYSQL_EXE unset and mysql not in PATH")
        env=os.environ.copy()
        cmd=[args.client,"--no-defaults","--local-infile=1","--default-character-set=utf8mb4",
             "--host="+env.get("MYSQL_HOST","127.0.0.1"),"--port="+env.get("MYSQL_PORT","3306"),
             "--user="+env.get("MYSQL_USER","support_analyst")]
        def execute(sql,label,table=False):
            command=cmd+(["--table"] if table else ["--batch","--raw","--skip-column-names"])
            receipt["commands"].append({"argv":command,"sql_label":label})
            result=subprocess.run(command,input=sql,env=env,capture_output=True,text=True,encoding="utf-8")
            (target/(label+".txt")).write_text(result.stdout+result.stderr,encoding="utf-8")
            if result.returncode:
                raise RuntimeError(f"{label} exit {result.returncode}; see output/mysql/{label}.txt")
            return result.stdout
        version=subprocess.run([args.client,"--no-defaults","--version"],capture_output=True,text=True,encoding="utf-8")
        receipt["client_version"]=version.stdout.strip()
        receipt["commands"].append({"argv":[args.client,"--no-defaults","--version"],"exit":version.returncode})
        if version.returncode:
            raise RuntimeError("mysql --version failed: "+version.stderr.strip())
        receipt["server_version"]=execute("SELECT VERSION();","server_version").strip()
        # Refuse even empty existing schemas before any DDL. Never alter another database.
        exists=execute("SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name='"+args.database+"';","database_preflight").strip()
        if exists!="0":
            raise RuntimeError("Target database already exists. Choose a NEW --database support_ops_verify_<unique>; no data deleted or modified.")
        for rel in ORDER:
            execute(prepared(rel,args.database),Path(rel).stem,table=True)
            receipt["scripts"].append({"script":rel,"exit":0})
            save()
            print("Executed "+rel)
        outputs={k:execute(v,"reconcile_"+k) for k,v in reconciliation_sql(args.database).items()}
        receipt["reconciliation"]=reconcile(outputs)
        receipt["status"]="EXECUTED_RECONCILED" if receipt["reconciliation"]["status"]=="PASS" else "FAIL"
        receipt["validation_detail_review"]="PENDING: inspect validation.txt and import warnings; reconciliation is not full database acceptance"
        save()
        if receipt["status"]=="FAIL":
            raise RuntimeError("SQL/Python reconciliation failed; inspect execution_receipt.json")
        print("All scripts executed and 33 reconciliation values matched. Review validation details and import warnings.")
    except (OSError,RuntimeError) as exc:
        receipt["error"]=str(exc)
        if receipt["scripts"]:
            receipt["status"]="INCOMPLETE_OR_FAILED"
        save()
        raise SystemExit(str(exc))
if __name__=="__main__":
    main()
