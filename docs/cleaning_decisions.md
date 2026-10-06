# Cleaning decisions

Decisions use the independent assessment and executed cleaning counts. A source snapshot cannot establish a preferred version of conflicting records.

| Issue | Evidence | Business impact | Decision | Reason |
|---|---|---|---|
| Exact copies | 111 redundant rows | Inflated volume/effort | AUTO-FIX | Remove only fully identical copies. |
| Conflicting keys | 60 ticket versions | Ambiguous joins | QUARANTINE | Preserve every distinct version; no evidence supports a winner. |
| Channel formatting | 120 normalized rows | Split channel groups | AUTO-FIX | Case and surrounding spaces do not change meaning. |
| Missing category, known unique subcategory | 60 restored rows | Missing demand classification | AUTO-FIX | Approved hierarchy uniquely determines category. |
| Missing subcategory or both hierarchy fields | See cleaning reason counts | Unknown case mix | QUARANTINE | Category alone cannot identify a subcategory. |
| Invalid category/subcategory pair | See cleaning reason counts | Wrong routing and demand mix | QUARANTINE | Neither field establishes which value is correct. |
| Invalid CSAT | 23 scores replaced by null | Biased satisfaction | AUTO-FIX | Retain the ticket; score cannot be recovered or clamped. |
| Missing completed resolution, invalid event order, unknown owner | See cleaning reason counts | Invalid service timing or ownership | QUARANTINE | Snapshot provides no trustworthy repair evidence. |
| Invalid/orphan work logs and workforce capacity | See cleaning reason counts | Wrong handling and utilization | QUARANTINE | Remove invalid parents before dependent log validation. |
| Long logically valid durations | Duration percentiles in quality report | Long-tail mean bias | KEEP | External dependencies can legitimately delay completion. |
