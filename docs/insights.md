# Business insights

Evidence comes from executed Python calculations on retained processed data. All data is synthetic; these findings demonstrate analytical decisions rather than real company results. Rates use the denominators in verified_kpis.csv.

## Technical cases contribute disproportionate resolution breaches

**Finding and evidence:** Technical Support is 29.49% of retained tickets and 50.09% of resolution SLA breaches (1,760 of 3,514).

**Business interpretation:** The cohort warrants a service-path review because its breach contribution exceeds its demand share.

**Recommendation:** Review technical integration/bug queues, escalation handoffs and dependency aging before changing coverage; compare subcategory samples and priority targets.

**Limitation:** The simulation encodes harder technical cases. Contribution is not proof of a staffing or agent cause.

## Weekday and morning arrivals concentrate demand

**Finding and evidence:** Average local weekday demand is 1.92 times weekend demand. The 09:00–11:59 interval contains 35.70% of tickets; peak hour starts at 10:00.

**Business interpretation:** Demand is uneven across days and arrival hours.

**Recommendation:** Review weekday assignment coverage and morning triage availability; validate arrival/handling lag with operational records before setting shifts.

**Limitation:** Arrival hours do not establish hourly workload or staffing gaps; all grouping uses Asia/Ho_Chi_Minh.

## Overall SLA requires reviewing both service stages

**Finding and evidence:** First-response compliance is 87.93% (14,773 eligible); resolution is 76.19% (14,757); overall is 67.66% (14,758).

**Business interpretation:** A ticket can meet response targets and still fail on resolution, so a single stage KPI misses operational exposure.

**Recommendation:** Use component-level breach queues and priority-specific targets; review combined breaches without summing overlapping component counts.

**Limitation:** Pending cases are excluded separately from each denominator; unresolved overdue cases remain breaches.

## The mean resolution duration hides a large long tail

**Finding and evidence:** Completed-ticket mean resolution is 117.05 hours versus median 6.22, P90 29.73 and P95 48.75 hours.

**Business interpretation:** A small number of long waits strongly affect the mean, while most tickets resolve much sooner.

**Recommendation:** Report median and tail percentiles beside the mean; separately review external-dependency waits with named follow-up owners.

**Limitation:** Elapsed resolution includes waiting. Completed-ticket statistics exclude unresolved cases and must not estimate handling effort.

## CSAT needs response-rate and duration-cohort context

**Finding and evidence:** Mean CSAT is 4.07/5 from 7,431 valid responses, a 52.35% response rate among 14,196 completed tickets. Respondent averages are 4.20 for <=4h and 3.55 for >72h resolution.

**Business interpretation:** Overall satisfaction can hide respondent and case-mix differences.

**Recommendation:** Monitor survey participation alongside CSAT; inspect waiting-related communication in long-duration respondent cohorts without ranking agents on small survey samples.

**Limitation:** Nonresponse, category and priority confound the observed association; no causal improvement estimate is supported.

## Snapshot backlog is mainly aged work

**Finding and evidence:** The snapshot contains 578 unresolved tickets; 549 are older than 72 hours and 561 have breached resolution SLA.

**Business interpretation:** Aged unresolved cases require review distinct from the routine arrival queue.

**Recommendation:** Create an aging review list by category and final owner, confirm dependencies and next actions, and track future snapshots prospectively.

**Limitation:** A single snapshot cannot show historical backlog growth or establish whether long waits are avoidable.

## Reopened cases form a measurable review cohort

**Finding and evidence:** 1,234 tickets reopened, a 8.35% share of the retained ticket cohort.

**Business interpretation:** Reopened cases indicate repeated lifecycle activity and a useful sample for rework review.

**Recommendation:** Review integration/bug and repeated-reopen examples with documented context; compare category and priority cohorts before revising knowledge articles.

**Limitation:** Reopen Rate is not FCR; the dataset does not contain enough contact history to calculate FCR.

## Daily capacity pressure differs from overall utilization

**Finding and evidence:** Aggregate handling/productive utilization is 68.74%; full-year agent ratios range from 56.28% to 85.02%. Four-weekday planning estimates show positive gaps on 235 of 1,011 eligible team-days; maximum estimated gap is 2.92 equivalent FTE.

**Business interpretation:** Annual averages can conceal daily pressure and assignment differences.

**Recommendation:** Review repeated positive-gap weekdays by team under the 85% planning assumption, validate recorded absences and work-log completeness, then consider cross-training or daily reassignment.

**Limitation:** FTE gaps are retrospective estimates, not hiring requirements or exact shifts; hire dates, case mix and quarantine change comparisons.
