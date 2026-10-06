# Data Quality Assessment

## What I checked

I checked source grain, required versus optional values, domains, duplicate keys, relationships, event order and workforce consistency. Null response timestamps on unresolved tickets and absent CSAT responses are legitimate; a missing completion timestamp on a completed ticket is not.

The five sources are profiled independently of the defect-generation metadata. [The detailed report](data_quality_report.md) contains every detected issue and distribution; [the dictionary](data_dictionary.md) defines source meaning.

## Key findings

Counts below come from the executed raw assessment. Secondary field issues exclude exact copies and conflicting identities. Counts can overlap and must not be summed as distinct excluded rows.

| Issue | Count | Risk to analysis | Treatment |
|---|---:|---|---|
| Exact ticket / log copies | 75 / 36 | Inflated demand and handling totals | Remove redundant copies |
| Conflicting ticket identity | 60 versions, 30 IDs | Ambiguous service facts and joins | Quarantine every version |
| Noncanonical channel formatting | 120 tickets | Split channel groups | Normalize spaces and case |
| Missing category or subcategory | 120 tickets | Incomplete case-mix comparisons | Derive category for 60; quarantine the other 60 |
| Invalid category/subcategory pair | 60 tickets | Misclassified routing and breach contribution | Quarantine |
| Invalid CSAT | 23 tickets | Biased satisfaction and response counts | Set score to null |
| Missing required completed-ticket fields | 38 tickets | Unusable completion or ownership evidence | Quarantine |
| Invalid response sequence | 23 tickets | Impossible response durations and SLA outcomes | Quarantine |
| Unknown ticket owner | 15 tickets | Invalid owner comparisons | Quarantine |
| Missing or ambiguous ticket parent in raw logs | 65 logs | Handling cannot be assigned to a reliable ticket | Quarantine; reassess after parent exclusions |
| Invalid handling value | 27 logs | Distorted workload and utilization | Quarantine |
| Absence + shrinkage exceeds schedule | 9 workforce rows | Invalid productive capacity | Quarantine and exclude dependent logs |

After safe transformations and dependent checks, exclusions total **256 ticket rows, 341 logs and 9 workforce rows**. The final log audit identifies 295 unknown-ticket references and 46 missing workforce references; some rows also have another reason. The initial 65 raw parent failures and final 295 are different stages of the same assessment, because additional ticket parents are removed during cleaning.

## Duplicate reasoning

An exact duplicate repeats the same business observation in every source field. Keeping one copy preserves that observation while removing inflation: 75 ticket copies and 36 work-log copies are removed.

A conflicting duplicate shares a business key but disagrees on facts. The 30 ambiguous ticket IDs have two distinct versions each. Choosing the first, latest or most complete row would invent a canonical record without event history or source precedence. All 60 versions are preserved in quarantine; their logs cannot remain attached to an uncertain ticket.

## Hard errors vs anomalies

A response before creation is a hard lifecycle error: elapsed response time cannot be negative. By contrast, retained ticket **TKT000178** was created at `2025-10-05T04:57:12Z` and resolved at `2026-09-21T22:46:12Z`, an elapsed **8,441.82 hours**. Its ordered events fall within the snapshot and pass the full validation rules.

The duration is extreme, but the snapshot offers no evidence that it is wrong. I keep it and report median and tail percentiles beside the mean. Removing it solely for being unusual would hide long waits and make resolution performance look better. The data cannot establish its actual waiting cause.

## Downstream impact

Duplicate tickets inflate volume; duplicate logs inflate handling and utilization. Conflicting IDs can multiply joins or misstate SLA evidence. Invalid lifecycles distort service durations and backlog classification. Incorrect channel and hierarchy values fragment operational segments. Invalid scores distort CSAT, while quarantine and nulling affect survey denominators. Invalid workforce rows corrupt capacity; their removal also requires dependent-log checks.

Source rows reconcile as **raw = processed + exact copies removed + quarantine**. Assessment and cleaning preserve all five raw SHA256 values. [Cleaning decisions](03_cleaning_decisions.md) explain why each repair or exclusion is justified.
