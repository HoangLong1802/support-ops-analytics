"""Retrospective daily planning estimates using four prior matching weekdays."""
import numpy as np
import pandas as pd
from contract import ROOT, DAYS, TEAMS, read_tables, hashes
from verified_metrics import workforce_metrics

PRODUCTIVE_PER_FTE = 480 * (1-.22)
TARGET_UTILIZATION = .85

def estimate(data):
    w=workforce_metrics(data)
    w["work_date"]=pd.to_datetime(w.work_date)
    grouped=w.groupby(["team","work_date"])[["handling_minutes","productive_minutes"]].sum()
    calendar=pd.MultiIndex.from_product([TEAMS,DAYS],names=["team","work_date"])
    daily=grouped.reindex(calendar,fill_value=0).reset_index().sort_values(["team","work_date"])
    daily["weekday"]=daily.work_date.dt.dayofweek
    daily["forecast_handling_minutes"]=daily.groupby(["team","weekday"]).handling_minutes.transform(lambda s:s.shift(1).rolling(4,min_periods=4).mean())
    daily["forecast_history_days"]=daily.groupby(["team","weekday"]).cumcount().clip(upper=4)
    daily["productive_minutes_per_fte"]=PRODUCTIVE_PER_FTE
    daily["target_utilization"]=TARGET_UTILIZATION
    daily["required_fte"]=daily.forecast_handling_minutes/(PRODUCTIVE_PER_FTE*TARGET_UTILIZATION)
    daily["available_fte"]=daily.productive_minutes/PRODUCTIVE_PER_FTE
    daily["staffing_gap_fte"]=daily.required_fte-daily.available_fte
    return daily

def main():
    before=hashes()
    result=estimate(read_tables("processed"))
    result["work_date"]=result.work_date.dt.strftime("%Y-%m-%d")
    result.to_csv(ROOT/"data/analytics/staffing_daily.csv",index=False)
    (ROOT/"docs/workforce_methodology.md").write_text(
        "# Workforce methodology\n\n"
        "This is a retrospective daily planning estimate by handling team, not an exact schedule. Handling effort comes from work logs; elapsed ticket resolution is not a workload input.\n\n"
        "Forecast handling minutes = the mean handling total from the four previous occurrences of the same weekday within each team. The current day and future days are excluded. The first four matching weekdays have insufficient history and return null forecasts. Calendar dates with zero effort remain in the series.\n\n"
        "Planning assumptions: one FTE schedules 480 minutes, planned shrinkage is 22%, and target productive utilization is 85%. Productive minutes per FTE = 480 × 0.78 = 374.4. Required FTE = forecast handling / (374.4 × 0.85). Available FTE = recorded productive minutes / 374.4. Gap = required − available; a positive value indicates additional equivalent capacity under these assumptions.\n\n"
        "Available FTE is an equivalent capacity measure, not a headcount. Recorded absences and shrinkage make this a retrospective comparison. Daily data cannot support exact hourly gaps, skill coverage, queueing or shift recommendations. Outputs do not forecast arrivals or future-date roster availability.\n\n"
        "Quarantined work logs and capacity rows reduce observed effort and capacity. Short history, synthetic demand, external waiting and ownership transfers limit interpretation. Validate actual handling capture and future rosters before using the method operationally. Review assumptions rather than interpreting fractional FTE as a precise hiring instruction.\n",
        encoding="utf-8")
    assert before==hashes()
    print(f"Daily staffing estimates: {len(result):,} rows; {result.forecast_handling_minutes.notna().sum():,} with four prior matching weekdays")

if __name__=="__main__":
    main()

