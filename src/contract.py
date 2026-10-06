"""Approved source contract and snapshot conventions shared by analytical layers."""
from pathlib import Path
import hashlib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ZONE = "Asia/Ho_Chi_Minh"
START_LOCAL = pd.Timestamp("2025-10-01")
END_LOCAL = pd.Timestamp("2026-10-01")
START_UTC = START_LOCAL.tz_localize(ZONE).tz_convert("UTC")
SNAPSHOT = END_LOCAL.tz_localize(ZONE).tz_convert("UTC")
DAYS = pd.date_range(START_LOCAL, END_LOCAL, inclusive="left")
SEED = 42
COLUMNS = {
    "agents": ["agent_id", "team", "hire_date"],
    "sla_policies": ["policy_id", "channel", "priority", "first_response_target_minutes", "resolution_target_minutes"],
    "tickets": ["ticket_id", "assigned_agent_id", "policy_id", "channel", "priority", "customer_type", "category", "subcategory", "created_at", "first_response_at", "resolved_at", "status", "reopen_count", "csat_score"],
    "ticket_work_logs": ["work_log_id", "ticket_id", "agent_id", "work_date", "handling_minutes"],
    "workforce_daily": ["agent_id", "work_date", "scheduled_minutes", "absence_minutes", "shrinkage_minutes"],
}
KEYS = {"agents": ["agent_id"], "sla_policies": ["policy_id"], "tickets": ["ticket_id"], "ticket_work_logs": ["work_log_id"], "workforce_daily": ["agent_id", "work_date"]}
HIERARCHY = {
    "technical_support": {"login_authentication": .26, "performance": .20, "integration": .24, "bug_error": .30},
    "billing": {"payment_failed": .30, "refund": .24, "invoice": .18, "subscription": .28},
    "account_access": {"password_reset": .38, "account_locked": .28, "verification": .22, "profile": .12},
    "product_service_inquiry": {"feature_question": .45, "pricing": .35, "availability": .20},
    "service_request": {"configuration": .42, "upgrade": .33, "cancellation": .25},
}
PAIRS = {(category, sub) for category, subs in HIERARCHY.items() for sub in subs}
TEAMS = ["general_support", "technical_support", "billing_account"]
CHANNELS = ["email", "chat", "phone", "web"]
PRIORITIES = ["low", "medium", "high", "urgent"]
CUSTOMERS = ["standard", "premium", "vip"]
STATUSES = ["open", "pending", "resolved", "closed"]
TARGETS = {
    "phone": [(15, 2880), (10, 1440), (5, 480), (2, 240)],
    "chat": [(30, 2880), (20, 1440), (10, 480), (5, 240)],
    "email": [(480, 2880), (240, 1440), (60, 480), (30, 240)],
    "web": [(720, 2880), (360, 1440), (120, 480), (60, 240)],
}
SANITY = {
    "fr_breach_rate": (.10, .20), "resolution_breach_rate": (.15, .28),
    "overall_breach_rate": (.20, .35), "reopen_rate": (.08, .15),
    "csat_response_rate": (.45, .60), "average_csat": (3.8, 4.4),
    "backlog_rate": (.03, .06), "weekday_weekend_ratio": (1.7, 2.2),
    "median_team_day_utilization": (.65, .85),
}

def timestamps(series):
    return pd.to_datetime(series, utc=True, errors="coerce", format="mixed")

def dates(series):
    return pd.to_datetime(series, errors="coerce", format="mixed").dt.normalize()

def read_tables(layer="raw"):
    suffix = "_clean" if layer == "processed" else ""
    return {name: pd.read_csv(ROOT / "data" / layer / f"{name}{suffix}.csv") for name in COLUMNS}

def hashes():
    return {name: hashlib.sha256((ROOT / "data/raw" / f"{name}.csv").read_bytes()).hexdigest() for name in COLUMNS}

def write_table(path, frame):
    path.parent.mkdir(parents=True, exist_ok=True)
    out = frame.copy()
    for col in ["created_at", "first_response_at", "resolved_at"]:
        if col in out:
            out[col] = timestamps(out[col]).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    for col in ["hire_date", "work_date"]:
        if col in out:
            out[col] = dates(out[col]).dt.strftime("%Y-%m-%d")
    out.to_csv(path, index=False, lineterminator="\n")

def conflict_mask(frame, keys):
    distinct = frame.drop_duplicates()
    ambiguous = distinct.loc[distinct.duplicated(keys, keep=False), keys].drop_duplicates()
    if ambiguous.empty:
        return pd.Series(False, index=frame.index)
    return pd.Series(pd.MultiIndex.from_frame(frame[keys]).isin(pd.MultiIndex.from_frame(ambiguous)), index=frame.index)

def integer_invalid(series, optional=False, minimum=0, maximum=None):
    number = pd.to_numeric(series, errors="coerce")
    bad = number.isna() | number.lt(minimum) | number.mod(1).ne(0)
    if maximum is not None:
        bad |= number.gt(maximum)
    return bad & series.notna() if optional else bad

def rule_masks(data):
    """Detect errors from records and business rules, without generator evidence."""
    a, p, t, l, w = [data[n] for n in COLUMNS]
    masks = {n: {} for n in COLUMNS}
    for name, frame in data.items():
        masks[name]["exact_duplicate"] = frame.duplicated()
        masks[name]["conflicting_key"] = conflict_mask(frame, KEYS[name])
        masks[name]["missing_key"] = frame[KEYS[name]].isna().any(axis=1)
    hire = dates(a.hire_date)
    masks["agents"].update(invalid_team=~a.team.isin(TEAMS), invalid_hire_date=hire.isna())
    masks["sla_policies"].update(
        invalid_channel=~p.channel.isin(CHANNELS), invalid_priority=~p.priority.isin(PRIORITIES),
        invalid_targets=integer_invalid(p.first_response_target_minutes, minimum=1) | integer_invalid(p.resolution_target_minutes, minimum=1),
        duplicate_channel_priority=p.duplicated(["channel", "priority"], keep=False),
    )
    usable_a = a.loc[~masks["agents"]["conflicting_key"]].drop_duplicates("agent_id")
    hire_map = dates(usable_a.hire_date).set_axis(usable_a.agent_id)
    usable_p = p.loc[~masks["sla_policies"]["conflicting_key"]].drop_duplicates("policy_id").set_index("policy_id")
    created, response, resolved = [timestamps(t[c]) for c in ["created_at", "first_response_at", "resolved_at"]]
    completed = t.status.isin(["resolved", "closed"])
    unresolved = t.status.isin(["open", "pending"])
    channel = t.channel.astype("string").str.strip().str.lower()
    known_pair = pd.Series([pair in PAIRS for pair in zip(t.category, t.subcategory)], index=t.index)
    known_category = t.category.isin(HIERARCHY)
    known_sub = t.subcategory.isin([sub for _, sub in PAIRS])
    mt = masks["tickets"]
    mt.update(
        missing_required=t[["ticket_id", "policy_id", "channel", "priority", "customer_type", "created_at", "status", "reopen_count"]].isna().any(axis=1),
        missing_hierarchy=t[["category", "subcategory"]].isna().any(axis=1),
        invalid_hierarchy=t.category.notna() & t.subcategory.notna() & ~known_pair,
        channel_format=t.channel.notna() & t.channel.ne(channel),
        invalid_channel=~channel.isin(CHANNELS),
        invalid_priority=~t.priority.isin(PRIORITIES),
        invalid_customer_type=~t.customer_type.isin(CUSTOMERS),
        invalid_status=~t.status.isin(STATUSES),
        unknown_owner=t.assigned_agent_id.notna() & ~t.assigned_agent_id.isin(usable_a.agent_id),
        unknown_policy=~t.policy_id.isin(usable_p.index),
        policy_mismatch=t.policy_id.isin(usable_p.index) & (channel.ne(t.policy_id.map(usable_p.channel)) | t.priority.ne(t.policy_id.map(usable_p.priority))),
        invalid_created=created.isna() | created.lt(START_UTC) | created.ge(SNAPSHOT),
        invalid_response_parse=t.first_response_at.notna() & response.isna(),
        invalid_resolution_parse=t.resolved_at.notna() & resolved.isna(),
        response_order=response.notna() & (response.lt(created) | response.gt(SNAPSHOT)),
        resolution_order=resolved.notna() & (resolved.lt(created) | resolved.lt(response) | resolved.gt(SNAPSHOT)),
        completed_missing_fields=completed & (response.isna() | resolved.isna() | t.assigned_agent_id.isna()),
        unresolved_has_resolution=unresolved & t.resolved_at.notna(),
        unresolved_has_csat=unresolved & t.csat_score.notna(),
        invalid_csat=integer_invalid(t.csat_score, optional=True, minimum=1, maximum=5),
        invalid_reopen=integer_invalid(t.reopen_count),
        owner_before_hire=t.assigned_agent_id.isin(hire_map.index) & created.dt.tz_convert(ZONE).dt.tz_localize(None).dt.normalize().lt(t.assigned_agent_id.map(hire_map)),
    )
    work_date = dates(w.work_date)
    mw = masks["workforce_daily"]
    mw.update(
        unknown_agent=~w.agent_id.isin(usable_a.agent_id),
        invalid_date=work_date.isna() | work_date.lt(START_LOCAL) | work_date.ge(END_LOCAL),
        before_hire=work_date.lt(w.agent_id.map(hire_map)),
        invalid_scheduled=integer_invalid(w.scheduled_minutes) | ~w.scheduled_minutes.isin([0, 450, 480, 510]),
        invalid_absence=integer_invalid(w.absence_minutes),
        invalid_shrinkage=integer_invalid(w.shrinkage_minutes),
        invalid_capacity=(w.absence_minutes + w.shrinkage_minutes).gt(w.scheduled_minutes),
        off_day_inconsistent=w.scheduled_minutes.eq(0) & (w.absence_minutes.ne(0) | w.shrinkage_minutes.ne(0)),
    )
    usable_t = t.loc[~mt["conflicting_key"]].drop_duplicates("ticket_id").set_index("ticket_id")
    usable_w = w.loc[~mw["conflicting_key"]].drop_duplicates(["agent_id", "work_date"])
    w_index = pd.MultiIndex.from_frame(usable_w[["agent_id", "work_date"]])
    attendance = pd.Series((usable_w.scheduled_minutes - usable_w.absence_minutes).to_numpy(), index=w_index)
    log_dates = dates(l.work_date)
    log_index = pd.MultiIndex.from_frame(l[["agent_id", "work_date"]])
    creation_dates = timestamps(usable_t.created_at).dt.tz_convert(ZONE).dt.tz_localize(None).dt.normalize()
    ending_dates = timestamps(usable_t.resolved_at).fillna(SNAPSHOT).dt.tz_convert(ZONE).dt.tz_localize(None).dt.normalize()
    distinct_l = l.drop_duplicates()
    day_total = distinct_l.groupby(["agent_id", "work_date"]).handling_minutes.sum()
    day_attendance = attendance.reindex(day_total.index)
    overloaded_keys = day_total.index[day_total.gt(day_attendance)]
    entry_keys = ["ticket_id", "agent_id", "work_date"]
    ambiguous_entries = distinct_l.loc[distinct_l.duplicated(entry_keys, keep=False), entry_keys].drop_duplicates()
    entry_conflicts = pd.MultiIndex.from_frame(l[entry_keys]).isin(pd.MultiIndex.from_frame(ambiguous_entries))
    ml = masks["ticket_work_logs"]
    ml.update(
        unknown_ticket=~l.ticket_id.isin(usable_t.index),
        unknown_agent=~l.agent_id.isin(usable_a.agent_id),
        missing_workforce=~log_index.isin(w_index),
        invalid_date=log_dates.isna() | log_dates.lt(START_LOCAL) | log_dates.ge(END_LOCAL),
        before_hire=log_dates.lt(l.agent_id.map(hire_map)),
        outside_lifecycle=l.ticket_id.isin(usable_t.index) & (log_dates.lt(l.ticket_id.map(creation_dates)) | log_dates.gt(l.ticket_id.map(ending_dates))),
        invalid_handling=integer_invalid(l.handling_minutes, minimum=1),
        exceeds_attendance=log_index.isin(overloaded_keys),
        duplicate_entry=entry_conflicts,
    )
    return {name: {rule: pd.Series(mask, index=data[name].index).fillna(False) for rule, mask in rules.items()} for name, rules in masks.items()}

def validation_errors(data):
    errors = []
    for name, expected in COLUMNS.items():
        if list(data[name].columns) != expected:
            errors.append(f"{name}: schema mismatch")
    if errors:
        return errors
    for name, rules in rule_masks(data).items():
        for rule, mask in rules.items():
            if mask.any():
                errors.append(f"{name}.{rule}: {int(mask.sum())}")
    return errors



