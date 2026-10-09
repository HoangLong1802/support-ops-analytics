"""Independent CSV/datetime oracle; expected values never import production KPI code."""
import csv
import json
import hashlib
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = datetime(2026, 9, 30, 17, tzinfo=timezone.utc)
START, END = date(2025, 10, 1), date(2026, 10, 1)
LOCAL = timezone(timedelta(hours=7))
# Frozen hand-worked raw examples, seconds and labels checked in docs/independent_validation.md.
MANUAL = {
    "TKT000001": (2280, 41160, ("MET", "MET", "MET")),
    "TKT000002": (2340, 33660, ("MET", "BREACHED", "BREACHED")),
    "TKT000531": (780, 30370112, ("MET", "BREACHED", "BREACHED")),
    "TKT014997": (9998, 9998, ("PENDING", "PENDING", "PENDING")),
    "TKT014933": (34380, 117200, ("MET", "PENDING", "PENDING")),
}
def rows(relative):
    with (ROOT / relative).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))

def instant(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")) if value else None

def classify(ticket, policy):
    created = instant(ticket["created_at"])
    labels, seconds = [], []
    for event, target in (("first_response_at", "first_response_target_minutes"),
                          ("resolved_at", "resolution_target_minutes")):
        observed = instant(ticket[event])
        elapsed = int(((observed or SNAPSHOT) - created).total_seconds())
        deadline = int(policy[target]) * 60
        # Compare timestamp instants to deadline (no pandas duration/vectorized rule).
        limit = created + timedelta(seconds=deadline)
        label = ("MET" if observed <= limit else "BREACHED") if observed else (
            "BREACHED" if SNAPSHOT > limit else "PENDING")
        labels.append(label)
        seconds.append(elapsed)
    complete = ticket["status"] in ("resolved", "closed")
    overall = "BREACHED" if "BREACHED" in labels else (
        "MET" if complete and labels == ["MET", "MET"] else "PENDING")
    return (*labels, overall), seconds

def calendar_demand(tickets):
    counts = Counter(instant(t["created_at"]).astimezone(LOCAL).date() for t in tickets)
    assert all(START <= d < END for d in counts)
    result = {}
    coverage = [START + timedelta(days=n) for n in range((END - START).days)]
    for name, weekend in (("Weekday", False), ("Weekend", True)):
        days = [d for d in coverage if (d.weekday() >= 5) == weekend]
        total = sum(counts[d] for d in days)
        result[name] = {"tickets": total, "calendar_days": len(days),
                        "zero_ticket_days": sum(counts[d] == 0 for d in days),
                        "average_daily_tickets": total / len(days)}
    return result

def build():
    tickets = rows("data/processed/tickets_clean.csv")
    policies = {p["policy_id"]: p for p in rows("data/raw/sla_policies.csv")}
    raw = rows("data/raw/tickets.csv")
    ids = {t["ticket_id"] for t in tickets}
    assert len(ids) == len(tickets) == 14774
    measured = {t["ticket_id"]: classify(t, policies[t["policy_id"]])[0] for t in tickets}
    manual = []
    for ticket_id, (fr, res, labels) in MANUAL.items():
        originals = [r for r in raw if r["ticket_id"] == ticket_id]
        assert len(originals) == 1
        r = originals[0]
        actual_labels, elapsed = classify(r, policies[r["policy_id"]])
        assert elapsed == [fr, res] and actual_labels == labels
        kept = next(t for t in tickets if t["ticket_id"] == ticket_id)
        assert kept == r, "Manual sample must be unchanged raw record"
        manual.append({"raw_csv_line": raw.index(r)+2, "raw_record": r,
                       "policy": policies[r["policy_id"]], "elapsed_or_age_seconds": elapsed,
                       "expected_outcomes": labels, "oracle_outcomes": actual_labels})
    invalid = next(r for r in raw if r["ticket_id"] == "TKT000161")
    assert invalid["status"] == "resolved" and invalid["resolved_at"] == ""
    assert invalid["ticket_id"] not in ids
    q = rows("data/quarantine/tickets_quarantine.csv")
    assert any(r["ticket_id"] == invalid["ticket_id"] and
               "completed_missing_fields" in r["quarantine_reason"] for r in q)

    counts = {"total_tickets": len(tickets),
              "completed_tickets": sum(t["status"] in ("resolved","closed") for t in tickets),
              "open_tickets": sum(t["status"] == "open" for t in tickets),
              "pending_tickets": sum(t["status"] == "pending" for t in tickets)}
    counts["backlog"] = counts["open_tickets"] + counts["pending_tickets"]
    for index, prefix in enumerate(("fr", "resolution", "overall")):
        c = Counter(labels[index] for labels in measured.values())
        for label in ("MET", "BREACHED", "PENDING"):
            counts[f"{prefix}_sla_{label.lower()}"] = c[label]
        counts[f"{prefix}_sla_eligible"] = c["MET"] + c["BREACHED"]
        counts[f"{prefix}_sla_compliance"] = c["MET"] / (c["MET"] + c["BREACHED"])
    demand = calendar_demand(tickets)
    counts["weekday_weekend_ratio"] = demand["Weekday"]["average_daily_tickets"] / demand["Weekend"]["average_daily_tickets"]
    saved = {r["metric"]: float(r["value"]) for r in rows("data/analytics/verified_kpis.csv")}
    deltas = {k: counts[k] - saved[k] for k in counts}
    assert all(abs(d) < 1e-9 for d in deltas.values()), deltas

    categories = []
    for cat in sorted({t["category"] for t in tickets}):
        cohort = [t for t in tickets if t["category"] == cat]
        c = Counter(measured[t["ticket_id"]][1] for t in cohort)
        categories.append({"category": cat, "tickets": len(cohort),
                           "ticket_share": len(cohort)/len(tickets),
                           "resolution_eligible": c["MET"]+c["BREACHED"],
                           "resolution_breaches": c["BREACHED"],
                           "resolution_breach_share": c["BREACHED"]/counts["resolution_sla_breached"],
                           "resolution_breach_rate": c["BREACHED"]/(c["MET"]+c["BREACHED"])})
    cat_saved = {r["category"]:r for r in rows("data/analytics/category_service_summary.csv")}
    for c in categories:
        for k,v in c.items():
            if k != "category":
                assert abs(v - float(cat_saved[c["category"]][k])) < 1e-9, (c,k)
    for r in rows("data/analytics/demand_day_type.csv"):
        for k,v in demand[r["day_type"]].items():
            assert abs(v - float(r[k])) < 1e-9

    # Recompute all existing BI acceptance cohorts independently; no M/DAX execution claim.
    cohort_checks = []
    for ref in json.loads((ROOT/"powerbi/acceptance_reference.json").read_text()):
        scope = ref["scope"]
        if scope == "All":
            group = tickets
        else:
            field, value = scope.split("=",1)
            group = [t for t in tickets if (
                instant(t["created_at"]).astimezone(LOCAL).strftime("%Y-%m") if field=="month" else
                t["assigned_agent_id"] or "unassigned" if field=="owner" else t[field]) == value]
        c = Counter(measured[t["ticket_id"]][1] for t in group)
        scores = [float(t["csat_score"]) for t in group if t["csat_score"]]
        complete = sum(t["status"] in ("resolved","closed") for t in group)
        actual = dict(tickets=len(group), completed=complete, backlog=len(group)-complete,
                      resolution_met=c["MET"], resolution_breached=c["BREACHED"],
                      resolution_pending=c["PENDING"], csat_responses=len(scores),
                      average_csat=sum(scores)/len(scores) if scores else None)
        differences = {k: (v-ref[k] if v is not None and ref[k] is not None else
                            0 if v==ref[k] else "NULL mismatch") for k,v in actual.items()}
        assert all(isinstance(d,(int,float)) and abs(d)<1e-9 for d in differences.values()), (scope,differences)
        cohort_checks.append({"scope":scope,"expected":actual,"differences":differences})

    logs = rows("data/processed/ticket_work_logs_clean.csv")
    multiplicities = Counter(l["ticket_id"] for l in logs)
    assert all(l["ticket_id"] in ids for l in logs)
    naive_rows = sum(max(1,multiplicities[t["ticket_id"]]) for t in tickets)
    naive_breaches = sum(max(1,multiplicities[t["ticket_id"]]) for t in tickets
                        if measured[t["ticket_id"]][1] == "BREACHED")
    naive_eligible = sum(max(1,multiplicities[t["ticket_id"]]) for t in tickets
                        if measured[t["ticket_id"]][1] != "PENDING")
    example = next(t for t in tickets if multiplicities[t["ticket_id"]] > 1)
    join = {"left_join_ticket_rows":naive_rows,"distinct_ticket_ids":len(ids),
            "excess_ticket_count":naive_rows-len(ids),
            "naive_resolution_breaches":naive_breaches,
            "correct_resolution_breaches":counts["resolution_sla_breached"],
            "naive_resolution_breach_rate":naive_breaches/naive_eligible,
            "correct_resolution_breach_rate":counts["resolution_sla_breached"]/counts["resolution_sla_eligible"],
            "safe_preaggregated_left_join_rows":len(tickets),
            "handling_minutes_from_logs":sum(int(l["handling_minutes"]) for l in logs),
            "example_ticket":example["ticket_id"],
            "example_work_logs":[l for l in logs if l["ticket_id"]==example["ticket_id"]]}
    assert naive_rows > len(tickets)

    # In-memory perturbation only: remove all arrivals on first local coverage date.
    removed = [t for t in tickets if instant(t["created_at"]).astimezone(LOCAL).date()!=START]
    perturbed = calendar_demand(removed)
    assert perturbed["Weekday"]["calendar_days"] == 261
    assert perturbed["Weekday"]["zero_ticket_days"] == 1
    assert perturbed["Weekend"] == demand["Weekend"]
    return {"status":"PASS","method":"stdlib csv + timestamp deadline comparisons; frozen hand-worked raw samples",
            "scope":"existing KPIs only; not native SQL/M/DAX validation",
            "input_sha256":{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in [*sorted((ROOT/"data/raw").glob("*.csv")),
                                      *sorted((ROOT/"data/processed").glob("*.csv")),
                                      ROOT/"data/analytics/verified_kpis.csv",
                                      ROOT/"powerbi/acceptance_reference.json"]},
            "manual_samples":manual,"invalid_missing_data_sample":invalid,
            "kpi_expected":counts,"kpi_differences":deltas,
            "category_expected":categories,"daily_demand":demand,
            "bi_cohort_checks":cohort_checks,"join_risk":join,
            "zero_day_fixture":{"removed_local_date":str(START),"source_modified":False,"result":perturbed}}

if __name__ == "__main__":
    receipt = build()
    target = ROOT/"output/independent_validation.json"
    target.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f"Independent checks PASS: {len(receipt['manual_samples'])} raw samples, "
          f"{len(receipt['bi_cohort_checks'])} existing cohorts; receipt {target}")
