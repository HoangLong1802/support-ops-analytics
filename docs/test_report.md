# Test Report — Power BI model vs independent Python

Run date: 2026-10-09. Only tests that were executed are listed.

- Python reference: `tests/powerbi_reference.py` (stdlib only, reads `data/processed/*.csv`, writes `output/powerbi_reference.json`).
- DAX results: `dax_query_operations Execute` through Power BI Modeling MCP against the open `customer_support_operations.pbix` (no filters unless stated).

| # | Test | Expected (Python) | Actual (DAX) | Result |
|---|------|-------------------|--------------|--------|
| 1 | Total Tickets | 14,774 | 14,774 | PASS |
| 2 | Completed Tickets | 14,196 | 14,196 | PASS |
| 3 | Backlog (open + pending) | 578 | 578 | PASS |
| 4 | Backlog >24h / >48h / >72h | 559 / 552 / 549 | 559 / 552 / 549 | PASS |
| 5 | Resolution SLA Compliance % (Met/(Met+Breached)) | 76.1876% | 76.1876% | PASS |
| 6 | First Response SLA Compliance % | 87.9307% | 87.9307% | PASS |
| 7 | Average CSAT / CSAT responses | 4.0715 / 7,431 | 4.0715 / 7,431 | PASS |
| 8 | CSAT Response Rate % | 52.3457% | 52.3457% | PASS |
| 9 | Low CSAT Responses (score 1–2) | 265 | 265 | PASS (after fix, see below) |
| 10 | Median / Average Resolution Hours | 6.2167 / 117.0478 | 6.2167 / 117.0478 | PASS |
| 11 | Reopen Rate % | 8.3525% | 8.3525% | PASS |
| 12 | Average / Median Backlog Age (h) | 2798.49 / 2392.24 | 2798.49 / 2392.24 | PASS |
| 13 | Active Agents; Tickets per Agent | 18; 820.78 | 18; 820.78 | PASS |
| 14 | Handling Hours per Agent; Minutes per Ticket | 1121.32; 82.14 | 1121.32; 82.14 | PASS |
| 15 | Absence Rate %; Shrinkage Rate % | 2.5616%; 21.1179% | 2.5616%; 21.1179% | PASS |
| 16 | Sep-2026 tickets / Resolution SLA % (date filter) | 1,216 / 74.9791% | 1,216 / 74.9791% | PASS |
| 17 | Rolling 30D Avg Daily Tickets at 2026-09-30 | 40.533 (expected from earlier DAX, not independently recomputed) | 40.533 | UNVERIFIED independently |
| 18 | Resolution SLA MoM change, Sep-2026 | -2.215 pp (expected from earlier DAX) | -2.215 pp | UNVERIFIED independently |
| 19 | Duplicate ticket_id in processed data | 0 | 0 | PASS |
| 20 | Tickets with unknown policy_id / null agent | 0 / 0 | 0 / 0 | PASS |
| 21 | Work-log tickets missing from tickets | 0 | 0 | PASS |

## Defect found and fixed during testing
`Low CSAT Responses` initially returned 7,431 (= all responses). Cause: the boolean filter `csat_score <= 2` also matches blanks. Fixed with explicit `>= 1` and `<= 2`; result now 265. The first re-run still showed 7,431 until the DAX query cache was cleared (`ClearCache`) — a stale-cache artifact, not a model defect.

## Not executed / limitations
- Refresh behaviour in Desktop (re-run of Power Query) was not re-tested this session.
- SQL (MySQL) is not part of the Power BI tests above. It runs in GitHub Actions on MySQL 8.4 (workflow `mysql-validation.yml`, runs #1 and #2 succeeded); evidence is the `mysql-validation-output` artifact.
- Visual interaction tests (cross-filter, drill-through, tooltips) not executed; pages 3–5 not yet built.
- Data is synthetic (`docs/data_source.md`); results describe the simulated operation only.
- The 13 new measures exist in the open Desktop session; the saved PBIX must be re-saved (Ctrl+S) to persist them.
