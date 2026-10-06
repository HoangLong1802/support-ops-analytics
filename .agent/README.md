# Continuity files and historical evidence

Read ../STATE.md, HANDOFF.md and current_plan.md first. HUMAN_REVIEW.md contains the personal interview questions. GitHub is the primary recovery source; installed packages and duplicate ZIP archives are disposable local aids.

verify_continuity.py is a read-only check of required artifacts, raw/data/workbook hashes, ignore rules and recognizable secret formats. The public analytical workflow is ../src/run_pipeline.py; the full test command is python -m unittest discover -s tests -v. Install ../requirements.txt in your own virtual environment.

The other Python helpers are historical, one-time scripts from build, recovery, refinement and output delivery. Keep them for provenance; do not replay finalize*, record*, refine*, normalize*, write_output_docs.py, finish_structure.py or capture_output_baseline.py to resume. They can rewrite documents, outputs and historical status. Historical JSON records apply to the checkpoint/phase stated inside them; earlier 14-test results do not supersede the later 23-test suite. Absolute paths in those records describe the original PC, not required locations on another PC.

prepare_github.py describes the recruiter-facing artifact manifest, not the complete Git continuity tree; its optional ZIP is secondary. Current truth is git log, git status and the verified remote ref/tree. The source files and committed evidence allow continuation without any local ZIP or chat history.
