# Repository guidance

1. Read STATE.md before substantial work; follow checkpoints sequentially.
2. Never fabricate metrics, validation, or execution results. Numerical public claims require executed evidence.
3. Never silently change the approved five-file raw schema. After successful generation, data/raw is immutable.
4. GitHub is the primary continuity source. Commit AGENTS.md, STATE.md, meaningful .agent files, source, synthetic datasets and real outputs. Keep internal continuity files out of recruiter-facing README navigation; ignore disposable dependencies, caches, secrets and duplicate backup ZIPs.
5. Read only the context needed, avoid unrelated refactoring, and prefer simple, interview-explainable Python and SQL.
6. Correlation is not causation. Reopen Rate is not FCR. Resolution duration is not handling effort.
7. Daily capacity cannot establish exact hourly staffing gaps. Never create fake PBIX files or screenshots.
8. Avoid unnecessary frameworks or infrastructure.
9. Run relevant tests and validation before completing checkpoints; fix causes rather than bypassing failures.
10. Maintain concise .agent/HANDOFF.md and .agent/current_plan.md. Commit and push after successful major checkpoints, preserve the existing valid remote, and verify the remote before ending a session. Never infer push success from a commit alone.
11. Recovery audit completed: the rejected initial build was archived before controlled regeneration, pristine validation and defect injection. The five replacement raw files are frozen; generation_metadata.json contains their SHA256 values. Do not rebuild raw data to resume work or reuse the rejected build's reported PASS.
12. On another machine, clone/pull, read STATE.md and .agent/HANDOFF.md, install requirements in a local virtual environment, then run the recorded validation. The committed CSVs and workbook allow immediate inspection without regeneration.
13. .agent contains historical one-time scripts and evidence. Follow the current handoff and public src/run_pipeline.py; do not replay historical finalization/refinement scripts that overwrite state or deliverables. See .agent/README.md.
