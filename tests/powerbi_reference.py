"""Independent (stdlib-only) recomputation of Power BI KPIs from data/processed CSVs.

Writes output/powerbi_reference.json. Compared with DAX results in docs/test_report.md.
"""
import csv
import json
import statistics
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAP = datetime(2026, 9, 30, 17, 0)


def rows(name):
    with open(ROOT / "data" / "processed" / f"{name}_clean.csv", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).replace(tzinfo=None) if s else None


tickets, logs, wf = rows("tickets"), rows("ticket_work_logs"), rows("workforce_daily")
pol = {p["policy_id"]: p for p in rows("sla_policies")}
for t in tickets:
    p = pol[t["policy_id"]]
    t["c"], t["fr"], t["rs"] = ts(t["created_at"]), ts(t["first_response_at"]), ts(t["resolved_at"])
    t["done"] = t["status"] in ("resolved", "closed")
    t["frt"], t["rst"] = float(p["first_response_target_minutes"]), float(p["resolution_target_minutes"])


def outcome(event, created, target):
    if event is None:
        return "B" if (SNAP - created).total_seconds() / 60 > target else "P"
    return "M" if (event - created).total_seconds() / 60 <= target else "B"


for t in tickets:
    t["fro"], t["rso"] = outcome(t["fr"], t["c"], t["frt"]), outcome(t["rs"], t["c"], t["rst"])


def rate(ts_, k):
    m = sum(t[k] == "M" for t in ts_)
    b = sum(t[k] == "B" for t in ts_)
    return m / (m + b) if m + b else None


done = [t for t in tickets if t["done"]]
backlog = [t for t in tickets if not t["done"]]
age_h = [(SNAP - t["c"]).total_seconds() / 3600 for t in backlog]
csat = [float(t["csat_score"]) for t in done if t["csat_score"]]
res_h = [(t["rs"] - t["c"]).total_seconds() / 3600 for t in tickets if t["rs"]]
sept = [t for t in tickets if (t["c"] + timedelta(hours=7)).strftime("%Y-%m") == "2026-09"]
agents = {t["assigned_agent_id"] for t in tickets if t["assigned_agent_id"]}
hand = sum(float(r["handling_minutes"]) for r in logs)
sched = sum(float(r["scheduled_minutes"]) for r in wf)

ref = {
    "total_tickets": len(tickets),
    "completed_tickets": len(done),
    "backlog": len(backlog),
    "backlog_gt_24h": sum(a > 24 for a in age_h),
    "backlog_gt_48h": sum(a > 48 for a in age_h),
    "backlog_gt_72h": sum(a > 72 for a in age_h),
    "resolution_sla_compliance": rate(tickets, "rso"),
    "fr_sla_compliance": rate(tickets, "fro"),
    "average_csat": statistics.mean(csat),
    "csat_responses": len(csat),
    "low_csat_responses": sum(c <= 2 for c in csat),
    "csat_response_rate": len(csat) / len(done),
    "median_resolution_hours": statistics.median(res_h),
    "average_resolution_hours": statistics.mean(res_h),
    "reopen_rate": sum(int(t["reopen_count"]) > 0 for t in tickets) / len(tickets),
    "average_backlog_age_hours": statistics.mean(age_h),
    "median_backlog_age_hours": statistics.median(age_h),
    "active_agents": len(agents),
    "tickets_per_agent": sum(1 for t in tickets if t["assigned_agent_id"]) / len(agents),
    "handling_hours_per_agent": hand / 60 / len({r["agent_id"] for r in logs}),
    "handling_minutes_per_ticket": hand / len({r["ticket_id"] for r in logs}),
    "absence_rate": sum(float(r["absence_minutes"]) for r in wf) / sched,
    "shrinkage_rate": sum(float(r["shrinkage_minutes"]) for r in wf) / sched,
    "sept_2026_tickets": len(sept),
    "sept_2026_resolution_sla": rate(sept, "rso"),
    "duplicate_ticket_ids": len(tickets) - len({t["ticket_id"] for t in tickets}),
    "tickets_unknown_policy": sum(t["policy_id"] not in pol for t in tickets),
    "tickets_null_agent": sum(not t["assigned_agent_id"] for t in tickets),
    "log_ticket_orphans": len({r["ticket_id"] for r in logs} - {t["ticket_id"] for t in tickets}),
}
(ROOT / "output" / "powerbi_reference.json").write_text(json.dumps(ref, indent=2), encoding="utf-8")
print(json.dumps(ref, indent=2))
