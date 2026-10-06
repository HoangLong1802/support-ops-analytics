"""Canonical snapshot SLA outcomes and verified KPIs from processed records."""
import json
import numpy as np
import pandas as pd
from contract import ROOT, ZONE, DAYS, SNAPSHOT, timestamps, read_tables, hashes

def ticket_metrics(tickets, policies):
    out = tickets.merge(policies, on="policy_id", how="left", validate="many_to_one", suffixes=("", "_policy"))
    for col in ["created_at", "first_response_at", "resolved_at"]:
        out[col] = timestamps(out[col])
    out["completed"] = out.status.isin(["resolved", "closed"])
    out["first_response_minutes"] = (out.first_response_at - out.created_at).dt.total_seconds() / 60
    out["resolution_minutes"] = (out.resolved_at - out.created_at).dt.total_seconds() / 60
    age = (SNAPSHOT - out.created_at).dt.total_seconds() / 60
    for prefix, event, duration, target in [
        ("fr", "first_response_at", "first_response_minutes", "first_response_target_minutes"),
        ("resolution", "resolved_at", "resolution_minutes", "resolution_target_minutes"),
    ]:
        elapsed = out[duration].where(out[event].notna(), age)
        # An unobserved event at exactly the deadline remains pending.
        out[f"{prefix}_sla_outcome"] = np.select(
            [out[event].notna() & elapsed.le(out[target]), elapsed.gt(out[target])],
            ["MET", "BREACHED"], default="PENDING")
    breach = out.fr_sla_outcome.eq("BREACHED") | out.resolution_sla_outcome.eq("BREACHED")
    met = out.completed & out.fr_sla_outcome.eq("MET") & out.resolution_sla_outcome.eq("MET")
    out["overall_sla_outcome"] = np.select([breach, met], ["BREACHED", "MET"], default="PENDING")
    local = out.created_at.dt.tz_convert(ZONE)
    out["local_created_date"] = local.dt.tz_localize(None).dt.normalize()
    out["local_created_hour"] = local.dt.hour
    out["local_created_weekday"] = local.dt.dayofweek
    out["backlog_age_minutes"] = age.where(~out.completed)
    return out

def workforce_metrics(data):
    workforce = data["workforce_daily"].copy()
    workforce["productive_minutes"] = workforce.scheduled_minutes - workforce.absence_minutes - workforce.shrinkage_minutes
    workforce["physical_attendance_minutes"] = workforce.scheduled_minutes - workforce.absence_minutes
    handling = data["ticket_work_logs"].groupby(["agent_id", "work_date"]).handling_minutes.sum().rename("handling_minutes")
    workforce = workforce.merge(handling, on=["agent_id", "work_date"], how="left", validate="one_to_one").fillna({"handling_minutes": 0})
    workforce["utilization"] = workforce.handling_minutes / workforce.productive_minutes.replace(0, np.nan)
    return workforce.merge(data["agents"][["agent_id", "team"]], on="agent_id", validate="many_to_one")

def ratio(numerator, denominator):
    return float(numerator / denominator) if denominator else np.nan

def summarize(data):
    t = ticket_metrics(data["tickets"], data["sla_policies"])
    w = workforce_metrics(data)
    completed = t.completed.sum()
    daily = t.groupby("local_created_date").size().reindex(DAYS, fill_value=0)
    td = w.groupby(["team", "work_date"])[["handling_minutes", "productive_minutes"]].sum()
    td["utilization"] = td.handling_minutes / td.productive_minutes.replace(0, np.nan)
    result = {
        "total_tickets": len(t), "completed_tickets": int(completed),
        "open_tickets": int(t.status.eq("open").sum()), "pending_tickets": int(t.status.eq("pending").sum()),
        "average_first_response_minutes": float(t.first_response_minutes.mean()),
        "average_resolution_hours": float(t.resolution_minutes.mean() / 60),
        "median_resolution_hours": float(t.resolution_minutes.median() / 60),
        "p90_resolution_hours": float(t.resolution_minutes.quantile(.9) / 60),
        "p95_resolution_hours": float(t.resolution_minutes.quantile(.95) / 60),
        "average_csat": float(t.csat_score.mean()),
        "csat_responses": int(t.csat_score.notna().sum()),
        "csat_response_rate": ratio(t.csat_score.notna().sum(), completed),
        "reopened_tickets": int(t.reopen_count.gt(0).sum()), "reopen_rate": float(t.reopen_count.gt(0).mean()),
        "backlog": int((~t.completed).sum()), "backlog_rate": float((~t.completed).mean()),
        "weekday_weekend_ratio": ratio(daily[DAYS.dayofweek < 5].mean(), daily[DAYS.dayofweek >= 5].mean()),
        "handling_hours": float(w.handling_minutes.sum() / 60),
        "productive_capacity_hours": float(w.productive_minutes.sum() / 60),
        "utilization": ratio(w.handling_minutes.sum(), w.productive_minutes.sum()),
        "median_team_day_utilization": float(td.utilization.median()),
    }
    for prefix in ["fr", "resolution", "overall"]:
        outcomes = t[f"{prefix}_sla_outcome"]
        for label in ["met", "breached", "pending"]:
            result[f"{prefix}_sla_{label}"] = int(outcomes.eq(label.upper()).sum())
        eligible = result[f"{prefix}_sla_met"] + result[f"{prefix}_sla_breached"]
        result[f"{prefix}_sla_eligible"] = eligible
        result[f"{prefix}_sla_compliance"] = ratio(result[f"{prefix}_sla_met"], eligible)
        result[f"{prefix}_breach_rate"] = ratio(result[f"{prefix}_sla_breached"], eligible)
    for hours in [24, 48, 72]:
        result[f"backlog_over_{hours}_hours"] = int(t.backlog_age_minutes.gt(hours * 60).sum())
    return result

def main():
    before = hashes()
    data = read_tables("processed")
    from contract import validation_errors
    errors = validation_errors(data)
    if errors:
        raise ValueError(errors)
    result = summarize(data)
    rates = [key for key in result if any(word in key for word in ["rate", "compliance", "utilization"])]
    definitions = {
        "csat_response_rate": "Completed tickets with valid CSAT / completed tickets",
        "reopen_rate": "Tickets with reopen_count > 0 / all retained tickets; not FCR",
        "weekday_weekend_ratio": "Average local weekday arrivals / average local weekend arrivals; zero days included",
        "utilization": "Handling / productive minutes, ratio of sums; null at zero capacity",
        "median_team_day_utilization": "Median of team/day handling / productive capacity; zero capacity excluded",
    }
    rows = []
    for key, value in result.items():
        unit = "fraction" if key in rates else "value"
        definition = definitions.get(key, "MET / (MET + BREACHED); PENDING excluded" if key.endswith("compliance") else key.replace("_", " "))
        rows.append({"metric": key, "value": value, "unit": unit, "definition": definition})
    target = ROOT / "data/analytics/verified_kpis.csv"
    target.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(target, index=False)
    assert before == hashes(), "Raw files changed"
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()

