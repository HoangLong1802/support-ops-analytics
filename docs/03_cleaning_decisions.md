# Cleaning Decisions

The cleaning strategy prioritizes traceability and avoids inventing values that cannot be supported by the source data.

I repair only values whose meaning is recoverable from the record or approved hierarchy. Ambiguous identities and hard errors remain available in quarantine with their source row number and reasons. Statistical extremes remain in the analytical population when logically valid.

| Issue | Decision | Why | Analytical impact |
|---|---|---|---|
| Exact duplicates | **REMOVE** 75 ticket copies and 36 log copies | Every source field repeats the same observation | Prevent inflated volume and handling; retain one observation |
| Channel whitespace/case | **NORMALIZE** 120 rows using strip/lowercase | Formatting does not change channel identity | Restore channel comparisons and policy checks |
| Conflicting ticket IDs | **QUARANTINE** all 60 versions across 30 IDs | No source precedence or history identifies a winner | Avoid ambiguous outcomes and join multiplication |
| Missing category with a uniquely mapped subcategory | **DERIVE** 60 categories from the approved hierarchy | The known subcategory has exactly one parent | Retain supported case-mix detail without guessing |
| Missing subcategory or both hierarchy fields | **QUARANTINE** | A category can contain several subcategories | Avoid invented routing and case mix; 60 hierarchy rows remain excluded after derivation |
| Invalid category/subcategory pair | **QUARANTINE** 60 rows | Neither conflicting field proves which one is correct | Prevent misclassified breach contribution |
| Invalid CSAT | **NULL** 23 scores; retain the otherwise valid ticket | Values outside integer 1–5 cannot be recovered or clamped | Preserve service facts; exclude invalid survey values from CSAT and response counts |
| Completed ticket missing resolved_at | **QUARANTINE**; also require response and owner | The status alone cannot supply an event timestamp | Keep incomplete lifecycle evidence out of SLA and duration calculations |
| First response before creation | **QUARANTINE**; also reject events after the snapshot | The event order is impossible under the source definition | Prevent negative or future elapsed durations |
| Unknown agent reference | **QUARANTINE**; unresolved tickets may legitimately have no owner | An unknown ID differs from an optional null | Keep ownership, hire-date and capacity comparisons consistent |
| Invalid/orphan work logs | **QUARANTINE** after checking retained parents | Logs need a known ticket, handler, workforce day, valid date and positive integer effort | Exclude 341 entries; do not transfer their effort to another handler |
| Agent/day handling above physical attendance | **QUARANTINE** the offending day's log entries if detected | Physical attendance bounds recorded effort; productive capacity is a different denominator | Enforce feasibility without capping utilization at 100%; no such errors remain in clean data |
| Invalid workforce row | **QUARANTINE** 9 rows | Absence plus shrinkage cannot exceed scheduled time | Avoid invalid productive capacity; quarantine logs losing their workforce parent |
| Legitimate long duration | **KEEP** when all rules pass | Unusual elapsed time can include waiting; no supported replacement exists | Preserve service tails and report median/P90/P95 alongside mean |

The ticket lifecycle also rejects unresolved tickets carrying resolution or CSAT, invalid domains, policy mismatches, invalid reopen counts and pre-hire ownership. Log checks enforce lifecycle dates, hire dates and the ticket/handler/date grain. These rules remain explicit even when the current source contains no affected records.

## Reconciliation and traceability

| Source | Raw | Exact copies removed | Quarantined | Processed |
|---|---:|---:|---:|---:|
| Agents | 18 | 0 | 0 | 18 |
| SLA policies | 16 | 0 | 0 | 16 |
| Tickets | 15,105 | 75 | 256 | 14,774 |
| Work logs | 18,278 | 36 | 341 | 17,901 |
| Daily workforce | 6,327 | 0 | 9 | 6,318 |

Transformations affect **203 distinct ticket rows** and do not themselves remove observations. Quarantine reason counts can overlap; the reconciliation counts each excluded source row once. [The executed cleaning report](cleaning_report.md) and [audit JSON](../data/analytics/cleaning_audit.json) retain the counts. The five raw files remain unchanged.
