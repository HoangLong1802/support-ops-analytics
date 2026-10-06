"""Seeded operational simulation; validated pristine records precede defect injection."""
import argparse
import io
import json
import platform
import numpy as np
import pandas as pd
from contract import ROOT, COLUMNS, HIERARCHY, TEAMS, CHANNELS, PRIORITIES, CUSTOMERS, TARGETS, DAYS, ZONE, START_LOCAL, SNAPSHOT, SEED, SANITY, hashes, write_table, validation_errors
from verified_metrics import summarize

CATEGORY_SCALE = [1.35, 1.00, .80, .70, 1.10]
SUB_SCALE = {
    "login_authentication": .80, "performance": 1.05, "integration": 1.20, "bug_error": 1.25,
    "payment_failed": .90, "refund": 1.15, "invoice": .75, "subscription": 1.05,
    "password_reset": .65, "account_locked": .95, "verification": 1.10, "profile": .70,
    "feature_question": 1.05, "pricing": .80, "availability": .75,
    "configuration": 1.15, "upgrade": 1., "cancellation": .85,
}
ROUTING = np.array([[.10, .82, .08], [.12, .06, .82], [.15, .05, .80], [.86, .08, .06], [.80, .14, .06]])
DEFAULTS = {"response_scale": 1., "response_sigma": .85, "resolution_scale": 1.12, "handling_scale": 1., "csat_center": 4.30}

def streams():
    return [np.random.Generator(np.random.PCG64(s)) for s in np.random.SeedSequence(SEED).spawn(5)]

def agents_and_policies(rng):
    agents = []
    ranges = [("2020-10-01", "2023-09-30")] * 3 + [("2024-04-01", "2025-09-30")] * 2 + [("2025-10-15", "2026-03-31")]
    for team in TEAMS:
        for lower, upper in ranges:
            lo, hi = pd.Timestamp(lower), pd.Timestamp(upper)
            agents.append([f"AGT{len(agents)+1:03d}", team, (lo + pd.Timedelta(days=int(rng.integers(0, (hi-lo).days+1)))).strftime("%Y-%m-%d")])
    policies = [[f"POL{c.upper()}{p.upper()}", c, p, *TARGETS[c][i]] for c in CHANNELS for i, p in enumerate(PRIORITIES)]
    return pd.DataFrame(agents, columns=COLUMNS["agents"]), pd.DataFrame(policies, columns=COLUMNS["sla_policies"])

def workforce(agents, rng):
    rows = []
    hires = pd.to_datetime(agents.hire_date)
    for day in DAYS:
        for team in TEAMS:
            indexes = agents.index[agents.team.eq(team) & hires.le(day)].to_numpy()
            working = rng.random(len(indexes)) < (.84 if day.dayofweek < 5 else .53)
            minimum = min(3 if day.dayofweek < 5 else 2, len(indexes))
            if working.sum() < minimum:
                working[rng.choice(np.flatnonzero(~working), minimum-int(working.sum()), replace=False)] = True
            for i, on in zip(indexes, working):
                scheduled = int(rng.choice([450,480,510], p=[.15,.75,.10])) if on else 0
                absence = 0
                if scheduled:
                    absence = scheduled if rng.random() < .018 else (int(rng.choice([30,60,120])) if rng.random() < .055 else 0)
                shrinkage = min(scheduled-absence, round(scheduled*rng.uniform(.15,.28))) if absence < scheduled else 0
                rows.append([agents.loc[i,"agent_id"],day.strftime("%Y-%m-%d"),scheduled,absence,shrinkage])
    return pd.DataFrame(rows, columns=COLUMNS["workforce_daily"])

def simulate(params=None):
    params = DEFAULTS | (params or {})
    ra, rw, rt, rh, _ = streams()
    agents, policies = agents_and_policies(ra)
    capacity = workforce(agents, rw)
    n = 15000
    day_weight = np.array([2.05,1.95,1.90,1.90,1.80,1.,.95])[DAYS.dayofweek] * rt.lognormal(0,.10,len(DAYS))
    day_index = rt.choice(len(DAYS), n, p=day_weight/day_weight.sum())
    hour_weights = np.array([.12]*6 + [.60]*3 + [2.80]*3 + [1.40]*2 + [2.20]*2 + [1.20]*2 + [.65]*4 + [.25]*2)
    hours = rt.choice(24,n,p=hour_weights/hour_weights.sum())
    local = DAYS[day_index] + pd.to_timedelta(hours*3600+rt.integers(0,3600,n),unit="s")
    order = np.argsort(local,kind="stable")
    local = local[order]
    created = local.tz_localize(ZONE).tz_convert("UTC")
    daily_counts = np.bincount(day_index,minlength=365)
    pressure = np.sqrt(daily_counts[day_index[order]] / (n/365))
    categories = list(HIERARCHY)
    category_idx = []
    subcategories = []
    priorities = []
    customers = rt.choice(CUSTOMERS,n,p=[.70,.22,.08])
    channels = rt.choice(CHANNELS,n,p=[.34,.30,.21,.15])
    for j, moment in enumerate(local):
        weights = np.array([.30,.24,.19,.15,.12])
        if moment.day > moment.days_in_month-3:
            weights[1] *= 1.20
        k = int(rt.choice(5,p=weights/weights.sum()))
        category_idx.append(k)
        subs = HIERARCHY[categories[k]]
        subcategories.append(rt.choice(list(subs),p=list(subs.values())))
        probs = np.array([.20,.52,.23,.05])
        if k == 0:
            probs *= [.92,.93,1.15,1.20]
        if customers[j] == "vip":
            probs *= [.85,.95,1.25,1.10]
        elif customers[j] == "standard":
            probs *= [1.04,1.02,.95,.95]
        priorities.append(rt.choice(PRIORITIES,p=probs/probs.sum()))
    category_idx = np.array(category_idx)
    priorities = np.array(priorities)
    priority_idx = np.array([PRIORITIES.index(p) for p in priorities])
    complexity = np.clip(np.array(CATEGORY_SCALE)[category_idx] * np.array([SUB_SCALE[s] for s in subcategories]) * np.array([.95,1.,1.05,1.10])[priority_idx] * rt.lognormal(0,.40,n),.30,3.50)
    response = np.maximum(1,np.round(
        np.array([dict(phone=4,chat=8,email=60,web=110)[c] for c in channels])
        * np.array([1.50,1.,.60,.28])[priority_idx]
        * np.array([dict(standard=1.,premium=.92,vip=.82)[c] for c in customers])
        * pressure**.22 * params["response_scale"] * rt.lognormal(0,params["response_sigma"],n))).astype(int)
    queue = np.where(rt.random(n)<.12,rt.uniform(60,1440,n),0)
    external = np.where(rt.random(n)<.065,rt.uniform(60,365,n)*1440,0)
    small_effect = rh.uniform(.94,1.06,18)
    resolution = np.maximum(response+1,np.round(
        np.array([420,240,130,90,280])[category_idx] * complexity
        * np.array([1.18,1.,.80,.58])[priority_idx] * pressure**.25
        * params["resolution_scale"] * rt.lognormal(0,.85,n) + queue + external)).astype(int)
    first_resolution = created + pd.to_timedelta(resolution,unit="m")
    probability = np.clip(.080 + .024*(complexity-1) + .018*np.isin(subcategories,["integration","bug_error"]) + .012*(resolution>1440),.04,.22)
    reopened = (rt.random(n)<probability) & (first_resolution<SNAPSHOT)
    reopen_count = np.where(reopened,rt.choice([1,2,3],n,p=[.83,.14,.03]),0)
    resolution += np.round(reopen_count*rt.uniform(120,960,n)).astype(int)
    final_resolution = created + pd.to_timedelta(resolution,unit="m")
    completed = final_resolution <= SNAPSHOT
    responded = created + pd.to_timedelta(response,unit="m")
    response_at = pd.Series(responded).where(responded<=SNAPSHOT)
    resolution_at = pd.Series(final_resolution).where(completed)
    status = np.where(completed,rt.choice(["resolved","closed"],n,p=[.78,.22]),rt.choice(["open","pending"],n,p=[.48,.52]))
    handling = np.maximum(5,np.round(70*complexity*np.array([.96,1.,1.06,1.10])[priority_idx]*(1+.13*reopen_count)*rh.lognormal(0,.22,n)*params["handling_scale"])).astype(int)
    remaining = np.zeros((365,18),dtype=int)
    day_lookup = {day.strftime("%Y-%m-%d"):i for i,day in enumerate(DAYS)}
    for row in capacity.itertuples(index=False):
        remaining[day_lookup[row.work_date],int(row.agent_id[3:])-1] = row.scheduled_minutes-row.absence_minutes
    persistent_weights = rh.uniform(.85,1.15,18)
    owners, log_rows = [], []
    for j in range(n):
        d = (local[j].normalize()-START_LOCAL).days
        wanted_team = int(rh.choice(3,p=ROUTING[category_idx[j]]))
        available = np.flatnonzero(remaining[d]>0)
        if len(available)==0:
            available = np.flatnonzero(pd.to_datetime(agents.hire_date).le(local[j].normalize()).to_numpy())
        preferred = available[available//6 == wanted_team]
        pool = preferred if len(preferred) else available
        weights = persistent_weights[pool]
        owner = int(rh.choice(pool,p=weights/weights.sum()))
        owners.append(f"AGT{owner+1:03d}")
        # A day-level entry can span any portion of the ticket's local lifecycle.
        amount = max(5,round(handling[j]*small_effect[owner]))
        multi = rh.random() < min(.45,.08+.08*complexity[j]+.07*reopen_count[j])
        pieces = {}
        first_piece = True
        while amount>0:
            candidates = np.flatnonzero(remaining[d]>0)
            if len(candidates)==0:
                d += 1
                if d >= 365:
                    raise ValueError("Insufficient physical attendance before snapshot")
                continue
            if first_piece and remaining[d,owner]>0:
                agent = owner
            else:
                preferred = candidates[candidates//6==wanted_team]
                pool = preferred if len(preferred) else candidates
                if multi and len(pool)>1 and owner in pool:
                    pool = pool[pool!=owner]
                agent = int(rh.choice(pool,p=persistent_weights[pool]/persistent_weights[pool].sum()))
            chunk = min(amount,remaining[d,agent])
            if first_piece and multi and chunk==amount:
                chunk = max(1,int(amount*.65))
            remaining[d,agent] -= chunk
            amount -= chunk
            pieces[(agent,d)] = pieces.get((agent,d),0)+chunk
            first_piece = False
        last_day = max(date for _,date in pieces)
        if completed[j] and final_resolution[j].tz_convert(ZONE).normalize().tz_localize(None) < DAYS[last_day]:
            # Capacity overflow delays completion; this is part of the lifecycle simulation.
            updated = (DAYS[last_day]+pd.Timedelta(hours=18)).tz_localize(ZONE).tz_convert("UTC")
            resolution_at.iloc[j] = updated
        for (agent,date),minutes in sorted(pieces.items()):
            log_rows.append([f"WL{len(log_rows)+1:07d}",f"TKT{j+1:06d}",f"AGT{agent+1:03d}",DAYS[date].strftime("%Y-%m-%d"),minutes])
    t = pd.DataFrame({
        "ticket_id":[f"TKT{j+1:06d}" for j in range(n)], "assigned_agent_id":owners,
        "policy_id":[f"POL{c.upper()}{p.upper()}" for c,p in zip(channels,priorities)],
        "channel":channels, "priority":priorities, "customer_type":customers,
        "category":[categories[k] for k in category_idx], "subcategory":subcategories,
        "created_at":created, "first_response_at":response_at, "resolved_at":resolution_at,
        "status":status, "reopen_count":reopen_count, "csat_score":np.nan,
    })[COLUMNS["tickets"]]
    elapsed = (t.resolved_at-t.created_at).dt.total_seconds()/60
    fr_targets = np.array([TARGETS[c][i][0] for c,i in zip(channels,priority_idx)])
    res_targets = np.array([TARGETS[c][i][1] for c,i in zip(channels,priority_idx)])
    score = np.clip(np.rint(params["csat_center"]+rt.normal(0,.85,n)-.18*(response>fr_targets)-.30*(elapsed.fillna(0)>res_targets)-.22*reopen_count-.14*np.minimum(3,np.log1p(elapsed.fillna(0)/1440))),1,5)
    has_score = completed & (rt.random(n)<.525)
    t.loc[has_score,"csat_score"] = score[has_score]
    logs = pd.DataFrame(log_rows,columns=COLUMNS["ticket_work_logs"])
    return dict(agents=agents,sla_policies=policies,tickets=t,ticket_work_logs=logs,workforce_daily=capacity)

def inject_defects(pristine):
    data = {name:frame.copy(deep=True) for name,frame in pristine.items()}
    rng = streams()[4]
    t = data["tickets"]
    available = set(t.index)
    def pick(n,condition=None):
        pool = sorted(available if condition is None else available.intersection(t.index[condition]))
        selected = rng.choice(pool,n,replace=False)
        available.difference_update(selected)
        return selected
    missing = pick(120)
    t.loc[missing[:60],"category"] = np.nan
    t.loc[missing[60:90],"subcategory"] = np.nan
    t.loc[missing[90:],["category","subcategory"]] = np.nan
    invalid_pairs = pick(60)
    t.loc[invalid_pairs,["category","subcategory"]] = ["technical_support","payment_failed"]
    fmt = pick(120)
    for j,i in enumerate(fmt):
        channel = t.loc[i,"channel"]
        t.loc[i,"channel"] = [channel.upper(),channel.title(),f" {channel} "][j%3]
    bad_csat = pick(23,t.status.isin(["resolved","closed"]) & t.csat_score.notna())
    t.loc[bad_csat,"csat_score"] = rng.choice([0,6],23)
    missing_resolution = pick(38,t.status.isin(["resolved","closed"]))
    t.loc[missing_resolution,"resolved_at"] = pd.NaT
    early = pick(23)
    t.loc[early,"first_response_at"] = t.loc[early,"created_at"]-pd.Timedelta(minutes=1)
    owner = pick(15)
    t.loc[owner,"assigned_agent_id"] = "AGT999"
    conflict = t.loc[pick(30)].copy()
    conflict["customer_type"] = conflict.customer_type.map({"standard":"premium","premium":"vip","vip":"standard"})
    exact = t.loc[pick(75)].copy()
    data["tickets"] = pd.concat([t,exact,conflict],ignore_index=True)
    l = data["ticket_work_logs"]
    ndup = max(1,round(len(l)*.002))
    nbad = max(1,round(len(l)*.0015))
    duplicate_logs = l.iloc[rng.choice(len(l),ndup,replace=False)]
    bad_logs = l.iloc[rng.choice(len(l),nbad,replace=False)].copy()
    bad_logs["work_log_id"] = [f"WLD{i+1:07d}" for i in range(nbad)]
    bad_logs["ticket_id"] = "TKT999999"
    bad_logs["handling_minutes"] = -1
    data["ticket_work_logs"] = pd.concat([l,duplicate_logs,bad_logs],ignore_index=True)
    w = data["workforce_daily"]
    bad_capacity = rng.choice(w.index[w.scheduled_minutes.gt(0)],max(1,round(len(w)*.0015)),replace=False)
    w.loc[bad_capacity,"shrinkage_minutes"] = w.loc[bad_capacity,"scheduled_minutes"]-w.loc[bad_capacity,"absence_minutes"]+1
    defects = {"exact_ticket_copies":75,"conflicting_ticket_ids":30,"missing_hierarchy":120,"invalid_pairs":60,"channel_format":120,"invalid_csat":23,"missing_completed_resolution":38,"response_before_creation":23,"unknown_owner":15,"exact_log_copies":ndup,"invalid_logs":nbad,"invalid_workforce_rows":len(bad_capacity)}
    return data,defects

def fingerprints(data):
    import hashlib
    results = {}
    for name,frame in data.items():
        out = frame.copy()
        for col in ["created_at","first_response_at","resolved_at"]:
            if col in out:
                out[col] = pd.to_datetime(out[col],utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        results[name] = hashlib.sha256(out.to_csv(index=False,lineterminator="\n").encode()).hexdigest()
    return results

def calibrate():
    params = DEFAULTS.copy()
    history = []
    for attempt in range(1,6):
        pristine = simulate(params)
        errors = validation_errors(pristine)
        if errors:
            raise ValueError("Pristine contract failed: "+str(errors))
        metrics = summarize(pristine)
        failed = {k:metrics[k] for k,(lo,hi) in SANITY.items() if not lo<=metrics[k]<=hi}
        history.append({"attempt":attempt,"parameters":params.copy(),"metrics":{k:metrics[k] for k in SANITY},"failed":failed})
        print(f"Calibration {attempt}: "+json.dumps(history[-1]["metrics"]),flush=True)
        if not failed:
            return pristine,params,history
        if "fr_breach_rate" in failed:
            params["response_scale"] *= 1.10 if metrics["fr_breach_rate"]<.10 else .90
        if "resolution_breach_rate" in failed or "overall_breach_rate" in failed:
            low = metrics["resolution_breach_rate"]<.15 or metrics["overall_breach_rate"]<.20
            params["resolution_scale"] *= 1.16 if low else .86
        if "median_team_day_utilization" in failed:
            params["handling_scale"] *= .75/metrics["median_team_day_utilization"]
        if "average_csat" in failed:
            params["csat_center"] += 4.05-metrics["average_csat"]
        if any(k in failed for k in ["reopen_rate","csat_response_rate","backlog_rate","weekday_weekend_ratio"]):
            raise RuntimeError("Structural sanity range failed; inspect model before another calibration: "+str(failed))
    raise RuntimeError("BLOCKED: joint calibration failed after five attempts")

def report(pristine,raw,params,history,defects,reproducible):
    metrics = summarize(pristine)
    lines = ["# Generation report","","All data is synthetic. Pristine validation ran before defects were injected into independent copies.","",
        f"Runtime: Python {platform.python_version()}, pandas {pd.__version__}, NumPy {np.__version__}. Seed 42; NumPy PCG64 with independent stage streams.",
        "Creation window: 2025-10-01 inclusive through 2026-10-01 exclusive, Asia/Ho_Chi_Minh. UTC snapshot: 2026-09-30T17:00:00Z.","",
        "## Row counts","","| Dataset | Pristine | Raw |","|---|---:|---:|"]
    lines += [f"| {name} | {len(pristine[name]):,} | {len(raw[name]):,} |" for name in COLUMNS]
    lines += ["","## Executed pristine checks","","| Check | Result | Required range |","|---|---:|---|"]
    lines += [f"| {key} | {metrics[key]:.6f} | {lo}–{hi} |" for key,(lo,hi) in SANITY.items()]
    lines += ["",f"Pristine schema, keys, lifecycle, relationships, workforce and handling feasibility: PASS. Deterministic repeat: {'PASS' if reproducible else 'FAIL'}.",
        "","## Distributions and service durations",""]
    t = pristine["tickets"]
    local = t.created_at.dt.tz_convert(ZONE)
    for col in ["channel","priority","category","customer_type","status"]:
        lines.append(f"- {col}: "+", ".join(f"{k} {v:.2%}" for k,v in t[col].value_counts(normalize=True).items()))
    lines.append("- Peak local hours: "+", ".join(f"{h:02d}:00 ({count:,} arrivals)" for h,count in local.dt.hour.value_counts().head(3).items()))
    for key in ["fr_sla_met","fr_sla_breached","fr_sla_pending","resolution_sla_met","resolution_sla_breached","resolution_sla_pending","overall_sla_met","overall_sla_breached","overall_sla_pending","average_resolution_hours","median_resolution_hours","p90_resolution_hours","p95_resolution_hours","handling_hours","utilization"]:
        lines.append(f"- {key}: {metrics[key]:.6f}")
    lines += ["","## Defects applied",""]+[f"- {k}: {v}" for k,v in defects.items()]
    lines += ["","## Calibration history","", "Only global simulation parameters change between complete simulation runs; no ticket is edited to hit a target."]
    for entry in history:
        lines.append(f"- Attempt {entry['attempt']}: parameters {json.dumps(entry['parameters'])}; observed {json.dumps(entry['metrics'])}; outside ranges {json.dumps(entry['failed'])}.")
    lines += ["","## Frozen raw SHA256","","| File | SHA256 |","|---|---|"]
    lines += [f"| {name}.csv | {digest} |" for name,digest in hashes().items()]
    (ROOT/"docs/generation_report.md").write_text("\n".join(lines)+"\n",encoding="utf-8")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--recover-invalid",action="store_true",help="Replace a rejected build only when its verified recovery archive exists")
    args = parser.parse_args()
    existing = any((ROOT/"data/raw"/f"{n}.csv").exists() for n in COLUMNS)
    manifest_path = ROOT/"data/analytics/generation_metadata.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    if existing and not args.recover_invalid:
        if not manifest_path.exists():
            raise RuntimeError("Existing raw data has no validated manifest; preserve it and explicitly recover the invalid build")
        manifest = json.loads(manifest_path.read_text())
        assert hashes()==manifest["hashes"], "Frozen raw file changed"
        print("Existing validated raw artifacts reused; no data overwritten")
        return
    if existing and args.recover_invalid:
        if manifest_path.exists():
            raise RuntimeError("A validated raw snapshot cannot be overwritten; use a new working copy")
        assert (ROOT/"_backups/rejected_existing_build.zip").exists(), "Recovery archive required"
    pristine,params,history = calibrate()
    repeated = simulate(params)
    assert fingerprints(pristine)==fingerprints(repeated), "Pristine reproducibility failed"
    raw,defects = inject_defects(pristine)
    repeat_raw,repeat_defects = inject_defects(repeated)
    assert fingerprints(raw)==fingerprints(repeat_raw) and defects==repeat_defects, "Defect reproducibility failed"
    for name,frame in raw.items():
        write_table(ROOT/"data/raw"/f"{name}.csv",frame)
    manifest = {"runtime":{"python":platform.python_version(),"pandas":pd.__version__,"numpy":np.__version__},"parameters":params,"history":history,"pristine_metrics":summarize(pristine),"defects":defects,"hashes":hashes(),"reproducibility":"PASS","pristine_validation":"PASS"}
    manifest_path.write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    report(pristine,raw,params,history,defects,True)
    print("Validated, reproducible raw data frozen: "+json.dumps({n:len(f) for n,f in raw.items()}))

if __name__=="__main__":
    main()





