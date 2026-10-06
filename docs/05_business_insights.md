# Business insights

Evidence comes from executed Python calculations on retained processed data. All data is synthetic; these findings demonstrate analytical decisions rather than real company results. Rates use the denominators in verified_kpis.csv.

### Finding 1

Technical cases contribute disproportionate resolution breaches.

**Evidence**

Technical Support is 29.49% of retained tickets and 50.09% of resolution SLA breaches (1,760 of 3,514).

**Interpretation**

The cohort warrants a service-path review because its breach contribution exceeds its demand share.

**Recommendation**

Review technical integration/bug queues, escalation handoffs and dependency aging before changing coverage; compare subcategory samples and priority targets.

**Limitation**

The simulation encodes harder technical cases. Contribution is not proof of a staffing or agent cause.

### Finding 2

Weekday and morning arrivals concentrate demand.

**Evidence**

Average local weekday demand is 1.92 times weekend demand. The 09:00–11:59 interval contains 35.70% of tickets; peak hour starts at 10:00.

**Interpretation**

Demand is uneven across days and arrival hours.

**Recommendation**

Review weekday assignment coverage and morning triage availability; validate arrival/handling lag with operational records before setting shifts.

**Limitation**

Arrival hours do not establish hourly workload or staffing gaps; all grouping uses Asia/Ho_Chi_Minh.

### Finding 3

Overall SLA requires reviewing both service stages.

**Evidence**

First-response compliance is 87.93% (14,773 eligible); resolution is 76.19% (14,757); overall is 67.66% (14,758).

**Interpretation**

A ticket can meet response targets and still fail on resolution, so a single stage KPI misses operational exposure.

**Recommendation**

Use component-level breach queues and priority-specific targets; review combined breaches without summing overlapping component counts.

**Limitation**

Pending cases are excluded separately from each denominator; unresolved overdue cases remain breaches.

### Finding 4

The mean resolution duration hides a large long tail.

**Evidence**

Completed-ticket mean resolution is 117.05 hours versus median 6.22, P90 29.73 and P95 48.75 hours.

**Interpretation**

A small number of long waits strongly affect the mean, while most tickets resolve much sooner.

**Recommendation**

Report median and tail percentiles beside the mean; separately review external-dependency waits with named follow-up owners.

**Limitation**

Elapsed resolution includes waiting. Completed-ticket statistics exclude unresolved cases and must not estimate handling effort.

### Finding 5

CSAT needs response-rate and duration-cohort context.

**Evidence**

Mean CSAT is 4.07/5 from 7,431 valid responses, a 52.35% response rate among 14,196 completed tickets. Respondent averages are 4.20 for <=4h and 3.55 for >72h resolution.

**Interpretation**

Overall satisfaction can hide respondent and case-mix differences.

**Recommendation**

Monitor survey participation alongside CSAT; inspect waiting-related communication in long-duration respondent cohorts without ranking agents on small survey samples.

**Limitation**

Nonresponse, category and priority confound the observed association; no causal improvement estimate is supported.

### Finding 6

Snapshot backlog is mainly aged work.

**Evidence**

The snapshot contains 578 unresolved tickets; 549 are older than 72 hours and 561 have breached resolution SLA.

**Interpretation**

Aged unresolved cases require review distinct from the routine arrival queue.

**Recommendation**

Create an aging review list by category and final owner, confirm dependencies and next actions, and track future snapshots prospectively.

**Limitation**

A single snapshot cannot show historical backlog growth or establish whether long waits are avoidable.

### Finding 7

Reopened tickets have lower respondent satisfaction.

**Evidence**

1,234 tickets reopened (8.35% of retained tickets). Respondent CSAT averages 3.74/5 from 625 responses, compared with 4.10/5 from 6,806 responses for tickets with no recorded reopen.

**Interpretation**

The reopened cohort is a useful starting sample for reviewing repeated effort and customer communication.

**Recommendation**

Review integration/bug and repeated-reopen examples with documented context; compare category and priority cohorts before revising knowledge articles.

**Limitation**

Category, severity and survey nonresponse may explain the difference. Reopen Rate is not FCR; contact history is unavailable.

### Finding 8

Daily capacity pressure differs from overall utilization.

**Evidence**

Aggregate handling/productive utilization is 68.74%; full-year agent ratios range from 56.28% to 85.02%. Four-weekday planning estimates show positive gaps on 235 of 1,011 eligible team-days; maximum estimated gap is 2.92 equivalent FTE.

**Interpretation**

Annual averages can conceal daily pressure and assignment differences.

**Recommendation**

Review repeated positive-gap weekdays by team under the 85% planning assumption, validate recorded absences and work-log completeness, then consider cross-training or daily reassignment.

**Limitation**

FTE gaps are retrospective estimates, not hiring requirements or exact shifts; hire dates, case mix and quarantine change comparisons.
