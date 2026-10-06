"""Export BI tables and measured insights while preserving editorial documentation."""
import json
import numpy as np
import pandas as pd
from contract import ROOT, DAYS, HIERARCHY, ZONE, read_tables, hashes, write_table
from verified_metrics import summarize, ticket_metrics, workforce_metrics

def main():
    before=hashes()
    data=read_tables("processed")
    k=summarize(data)
    saved=pd.read_csv(ROOT/"data/analytics/verified_kpis.csv").set_index("metric").value
    for key,value in k.items():
        assert np.isclose(saved[key],value,equal_nan=True), f"Verified KPI mismatch: {key}"
    t=ticket_metrics(data["tickets"],data["sla_policies"])
    t["category_key"]=t.category+"|"+t.subcategory
    t["local_created_date"]=t.local_created_date.dt.strftime("%Y-%m-%d")
    write_table(ROOT/"data/analytics/ticket_service_metrics.csv",t)
    w=workforce_metrics(data)
    write_table(ROOT/"data/analytics/agent_daily_workload.csv",w)
    categories=pd.DataFrame([[f"{cat}|{sub}",cat,sub] for cat,subs in HIERARCHY.items() for sub in subs],columns=["category_key","category","subcategory"])
    categories.to_csv(ROOT/"data/analytics/dim_categories.csv",index=False)
    calendar=pd.DataFrame({"date_key":DAYS.strftime("%Y-%m-%d"),"calendar_year":DAYS.year,"calendar_month":DAYS.month,
        "month_start":DAYS.to_period("M").to_timestamp().strftime("%Y-%m-%d"),"weekday_number":DAYS.dayofweek,
        "weekday_name":DAYS.day_name(),"is_weekend":DAYS.dayofweek>=5})
    calendar.to_csv(ROOT/"data/analytics/dim_date.csv",index=False)
    tech=t.category.eq("technical_support")
    breach=t.resolution_sla_outcome.eq("BREACHED")
    tech_share=float(tech.mean())
    tech_breach=float((tech & breach).sum()/breach.sum())
    hours=t.groupby("local_created_hour").size().sort_values(ascending=False)
    top_hour=int(hours.index[0])
    peak_share=float(t.local_created_hour.between(9,11).mean())
    bands=pd.cut(t.resolution_minutes,[-np.inf,240,1440,4320,np.inf],labels=["<=4h","4-24h","24-72h",">72h"])
    satisfaction=t.groupby(bands,observed=True).agg(completed=("ticket_id","size"),responses=("csat_score","count"),csat=("csat_score","mean"))
    oldest=int(t.backlog_age_minutes.gt(4320).sum())
    overdue=int((~t.completed & t.resolution_sla_outcome.eq("BREACHED")).sum())
    staffing=pd.read_csv(ROOT/"data/analytics/staffing_daily.csv")
    available=staffing.forecast_handling_minutes.notna()
    positive=int(staffing.loc[available,"staffing_gap_fte"].gt(0).sum())
    maximum_gap=float(staffing.loc[available,"staffing_gap_fte"].max())
    agent=w.groupby(["agent_id","team"])[["handling_minutes","productive_minutes"]].sum()
    agent["utilization"]=agent.handling_minutes/agent.productive_minutes.replace(0,np.nan)
    low,high=agent.utilization.min(),agent.utilization.max()
    reopened=t.reopen_count.gt(0)
    reopened_csat=t.loc[reopened,"csat_score"]
    other_csat=t.loc[~reopened,"csat_score"]
    findings=[
        ("Technical cases contribute disproportionate resolution breaches",
         f"Technical Support is {tech_share:.2%} of retained tickets and {tech_breach:.2%} of resolution SLA breaches ({int((tech & breach).sum()):,} of {int(breach.sum()):,}).",
         "The cohort warrants a service-path review because its breach contribution exceeds its demand share.",
         "Review technical integration/bug queues, escalation handoffs and dependency aging before changing coverage; compare subcategory samples and priority targets.",
         "The simulation encodes harder technical cases. Contribution is not proof of a staffing or agent cause."),
        ("Weekday and morning arrivals concentrate demand",
         f"Average local weekday demand is {k['weekday_weekend_ratio']:.2f} times weekend demand. The 09:00–11:59 interval contains {peak_share:.2%} of tickets; peak hour starts at {top_hour:02d}:00.",
         "Demand is uneven across days and arrival hours.",
         "Review weekday assignment coverage and morning triage availability; validate arrival/handling lag with operational records before setting shifts.",
         "Arrival hours do not establish hourly workload or staffing gaps; all grouping uses Asia/Ho_Chi_Minh."),
        ("Overall SLA requires reviewing both service stages",
         f"First-response compliance is {k['fr_sla_compliance']:.2%} ({k['fr_sla_eligible']:,} eligible); resolution is {k['resolution_sla_compliance']:.2%} ({k['resolution_sla_eligible']:,}); overall is {k['overall_sla_compliance']:.2%} ({k['overall_sla_eligible']:,}).",
         "A ticket can meet response targets and still fail on resolution, so a single stage KPI misses operational exposure.",
         "Use component-level breach queues and priority-specific targets; review combined breaches without summing overlapping component counts.",
         "Pending cases are excluded separately from each denominator; unresolved overdue cases remain breaches."),
        ("The mean resolution duration hides a large long tail",
         f"Completed-ticket mean resolution is {k['average_resolution_hours']:.2f} hours versus median {k['median_resolution_hours']:.2f}, P90 {k['p90_resolution_hours']:.2f} and P95 {k['p95_resolution_hours']:.2f} hours.",
         "A small number of long waits strongly affect the mean, while most tickets resolve much sooner.",
         "Report median and tail percentiles beside the mean; separately review external-dependency waits with named follow-up owners.",
         "Elapsed resolution includes waiting. Completed-ticket statistics exclude unresolved cases and must not estimate handling effort."),
        ("CSAT needs response-rate and duration-cohort context",
         f"Mean CSAT is {k['average_csat']:.2f}/5 from {k['csat_responses']:,} valid responses, a {k['csat_response_rate']:.2%} response rate among {k['completed_tickets']:,} completed tickets. Respondent averages are {satisfaction.loc['<=4h','csat']:.2f} for <=4h and {satisfaction.loc['>72h','csat']:.2f} for >72h resolution.",
         "Overall satisfaction can hide respondent and case-mix differences.",
         "Monitor survey participation alongside CSAT; inspect waiting-related communication in long-duration respondent cohorts without ranking agents on small survey samples.",
         "Nonresponse, category and priority confound the observed association; no causal improvement estimate is supported."),
        ("Snapshot backlog is mainly aged work",
         f"The snapshot contains {k['backlog']:,} unresolved tickets; {oldest:,} are older than 72 hours and {overdue:,} have breached resolution SLA.",
         "Aged unresolved cases require review distinct from the routine arrival queue.",
         "Create an aging review list by category and final owner, confirm dependencies and next actions, and track future snapshots prospectively.",
         "A single snapshot cannot show historical backlog growth or establish whether long waits are avoidable."),
        ("Reopened tickets have lower respondent satisfaction",
         f"{k['reopened_tickets']:,} tickets reopened ({k['reopen_rate']:.2%} of retained tickets). Respondent CSAT averages {reopened_csat.mean():.2f}/5 from {reopened_csat.count():,} responses, compared with {other_csat.mean():.2f}/5 from {other_csat.count():,} responses for tickets with no recorded reopen.",
         "The reopened cohort is a useful starting sample for reviewing repeated effort and customer communication.",
         "Review integration/bug and repeated-reopen examples with documented context; compare category and priority cohorts before revising knowledge articles.",
         "Category, severity and survey nonresponse may explain the difference. Reopen Rate is not FCR; contact history is unavailable."),
        ("Daily capacity pressure differs from overall utilization",
         f"Aggregate handling/productive utilization is {k['utilization']:.2%}; full-year agent ratios range from {low:.2%} to {high:.2%}. Four-weekday planning estimates show positive gaps on {positive:,} of {int(available.sum()):,} eligible team-days; maximum estimated gap is {maximum_gap:.2f} equivalent FTE.",
         "Annual averages can conceal daily pressure and assignment differences.",
         "Review repeated positive-gap weekdays by team under the 85% planning assumption, validate recorded absences and work-log completeness, then consider cross-training or daily reassignment.",
         "FTE gaps are retrospective estimates, not hiring requirements or exact shifts; hire dates, case mix and quarantine change comparisons."),
    ]
    lines=["# Business insights","","Evidence comes from executed Python calculations on retained processed data. All data is synthetic; these findings demonstrate analytical decisions rather than real company results. Rates use the denominators in verified_kpis.csv.",""]
    for number,(title,evidence,interpretation,recommendation,limitation) in enumerate(findings, start=1):
        lines += [f"### Finding {number}","",title+".","","**Evidence**","",evidence,"","**Interpretation**","",interpretation,"","**Recommendation**","",recommendation,"","**Limitation**","",limitation,""]
    (ROOT/"docs/05_business_insights.md").write_text("\n".join(lines),encoding="utf-8",newline="\n")
    (ROOT/"docs/execution_report.md").write_text(
        "# Execution report\n\n"
        "Pristine generation, sanity calibration and deterministic repetition passed before raw publication. Independent assessment, processed validation and row reconciliation ran successfully; raw SHA256 remained unchanged. KPI and analytical CSV outputs were generated from processed data. See the generation, quality and cleaning reports for executed evidence and counts.\n\n"
        "MySQL: scripts ready only; no client or local service was available. Power BI: import-ready data, semantic model, DAX source and three-page specification; no PBIX, DAX execution or rendered screenshot validation. These native-tool limitations do not imply successful SQL or Power BI execution.\n",
        encoding="utf-8")
    assert before==hashes(),"Portfolio build altered raw files"
    print("BI tables and eight verified insights refreshed; editorial README preserved; KPI agreement and raw hashes: PASS")

if __name__=="__main__":
    main()

