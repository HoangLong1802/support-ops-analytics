# Workforce methodology

This is a retrospective daily planning estimate by handling team, not an exact schedule. Handling effort comes from work logs; elapsed ticket resolution is not a workload input.

Forecast handling minutes = the mean handling total from the four previous occurrences of the same weekday within each team. The current day and future days are excluded. The first four matching weekdays have insufficient history and return null forecasts. Calendar dates with zero effort remain in the series.

Planning assumptions: one FTE schedules 480 minutes, planned shrinkage is 22%, and target productive utilization is 85%. Productive minutes per FTE = 480 × 0.78 = 374.4. Required FTE = forecast handling / (374.4 × 0.85). Available FTE = recorded productive minutes / 374.4. Gap = required − available; a positive value indicates additional equivalent capacity under these assumptions.

Available FTE is an equivalent capacity measure, not a headcount. Recorded absences and shrinkage make this a retrospective comparison. Daily data cannot support exact hourly gaps, skill coverage, queueing or shift recommendations. Outputs do not forecast arrivals or future-date roster availability.

Quarantined work logs and capacity rows reduce observed effort and capacity. Short history, synthetic demand, external waiting and ownership transfers limit interpretation. Validate actual handling capture and future rosters before using the method operationally. Review assumptions rather than interpreting fractional FTE as a precise hiring instruction.
