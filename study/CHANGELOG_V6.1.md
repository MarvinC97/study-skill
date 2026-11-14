# Study V6.1 — V6.0 Agent Runtime + V3.5 Learner Continuity

## Fixed regression

The V6.0 package restored autonomous source-to-course execution but lost V3.5 first-use and learner continuity support. V6.1 is **based on V6.0**, restoring named profiles, learner reports, evidence-based mastery, chapter summaries, stable course IDs and recovery. The existing 7 commands, V6 Manager/Host, LP contracts, G1–G6 quality gates, E5M visual pages and Chapter 8 previews remain unchanged except for explicit learner-aware routing.

## New/updated files

- `runtime/v61_learner.py` — named profile schema 1.0, course state schema 3.0, real answer/rubric evidence, derived chapter snapshots, state resumption, Study-D branch linking.
- `runtime/v6_agent.py` — explicit `--learner-name`, `--study-root`, `--temporary`; avoids mixing a deep module's IDs into the parent LP namespace.
- `runtime/v6_ops.py` — records Unit delivery and generated supplements/exams separately; `/study-c` includes existing actual answers and graded feedback; `/study-m` displays route status separately from understanding.
- `runtime/study_runtime.py` — actual assessed LP evidence bridge, with no page-click mastery promotion.
- `references/first-use.md`, `learner-adaptation.md`, `learning-loop.md` — restored conditional reading and V3.5 learning sequence.
- `schemas/learner-profile.md`, `learning-point.md` — restored storage/LP data boundaries.
- `scripts/study_home.py`, `study_check.py`, `study_quiz_check.py` — compatible entrypoints and validation helpers in the standalone archive.
- `scripts/merge_into_repo.py` — dry-run-by-default overlay for a V3.5 GitHub checkout, preserving original V3.5 reference/schema/script bytes.
- `runtime/v61tests/` — tests for profile compatibility, ID collision resistance, real answer evidence, migration and safe overlay.

## Explicit limitations

- GitHub remote has not been modified: the active connected GitHub account has read-only permission.
- The standalone V6.1 files reproduce V3.5's contract and features; they are not byte-for-byte copies of every V3.5 historical file. **When merging into the existing GitHub repository, the original V3.5 files are preserved exactly.**
- Model test doubles prove control logic, not the quality of a fresh real model. External model API end-to-end chapter run is still outstanding.
- No new cross-device sync service is introduced. File-based learner state is persistent only on the chosen host/storage.
