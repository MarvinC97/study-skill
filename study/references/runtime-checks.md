# Installed Runtime Checks · Study V3.3

These checks inspect actual files used by the current lesson. They are not a teaching engine, database, semantic grader or authorization service. Use existing host file/tool permissions. Never bypass an environment denial to run a checker.

## When to run

- Start/resume with file access: parse the existing course state with `state`; use `profile` if a profile is present. Inspect the reported scope and any unavailable references before relying on them. Profile absence does not block teaching.
- After a meaningful state edit: check the candidate state; use `--previous` with an actual pre-edit copy when checking historical preservation matters. Keep old bytes until the replacement verifies. Do not manufacture an old snapshot after editing.
- Before delivering generated HTML: use `artifact` against the actual generated file, not the unchanged template. Select `--mode unit`, `deep`, or `consolidated`. Review content and actual interactions separately.
- After saving: reread and parse the saved files, compare intended changes and unchanged history, then check again. At a session-recovery test, a fresh process must read the saved checkpoint. Do not rerun a full integration test on every turn.

Resolve `<skill>` to the actual installed Skill folder and `<data>` to the actual learner-approved study directory; placeholders below are not literal paths. Python 3 uses standard-library modules only.

```
python <skill>/scripts/study_check.py profile <data>/learner-profile.json
python <skill>/scripts/study_check.py state <data>/course/study-state.json
python <skill>/scripts/study_check.py state <data>/course/study-state.json --previous <data>/course/pre-edit-state.json
python <skill>/scripts/study_check.py artifact <data>/course/unit01.html --mode unit
python <skill>/scripts/study_check.py artifact <data>/course/consolidated.html --mode consolidated
```

The checker returns JSON issues and an exit status. Read the full result: a zero exit does not convert warnings, unsupported checks or unavailable artifacts into verification. Resolve reported errors before claiming the affected file/step verified. It is read-only and never repairs user data automatically.

## Three distinct quality decisions

1. **Operational integrity:** readable JSON/HTML, coherent IDs and references, actual save/readback, supported navigation and executed interaction behavior. The supplied checker covers a bounded structural subset; a real browser or equivalent execution is needed for relevant interactive behavior and rendering.
2. **Content correctness:** actual claims, diagrams, examples and answer criteria match the source; inferred illustrations are marked. A manifest, checksum or script PASS cannot prove this.
3. **Teaching suitability:** the actual material reflects relevant learner context, defines unfamiliar terms, provides question premises, and uses an appropriate degree of help. Review what was generated, not an Agent-authored “adapted=true” field.

The checker can require answer/rubric/assistance links; it cannot authenticate answers or decide if an explanation proves understanding. Never mark a semantic check passed merely because required fields exist. For promotion, evaluate the answer against the actual source and objective, then save its honest evidence.

## Fail locally and recover honestly

- Invalid state or unexpected lost history: keep the old file, repair only the demonstrated defect, recheck; do not reset the course.
- Missing profile on first use: follow `first-use.md` to ask the English name, create/read at the fixed root and verify. If persistence is unavailable or explicitly declined, disclose and use the documented temporary/export fallback without inventing background.
- Unavailable artifact: mark the gap; restore or rebuild from reliable material if needed, with provenance. Do not invent its content or claim it was delivered.
- Ambiguous question: invalidate that assessment conclusion, revise the question, retain original answer/revision references.
- Broken interaction: fix and rerun, or explicitly deliver a complete static alternative when that still serves the objective. Static fallback is not interactive PASS.
- Save failure: preserve available teaching, disclose the unsaved update and offer an export. Do not let a profile save failure freeze all learning.
- No Python or no file tools: perform the supported manual checks, state the missing automated/persistence coverage, and continue usable teaching. Do not claim checker execution. No new install/platform is automatically required.

Avoid unbounded polish and checks unrelated to the changed step. A failed check needs new diagnosis or a bounded fallback, not repeated regeneration. Keep concise evidence with the affected course/artifact; do not create a new report for every message.

## Named profile startup · V3.4

Follow `first-use.md` before ordinary course startup. With the supplied English name, run `study_home.py locate --name NAME`, then `init` only to create a missing profile; `--root` names an explicitly established alternative Study directory. Read actual output paths, verify the file and run the profile checker. The helper is not a permissions bypass or account service.

The state checker also validates an optional course `intake` stage: pending familiarity/goal cannot simultaneously record a formally started Unit; readiness requires recorded familiarity or an explicit skip. It checks record consistency, not whether the user really supplied a statement. Read the actual exchange before writing those fields. Legacy states without `intake` are not forced to restart.

## Stage exams and chapter synchronization

Use `scripts/study_quiz_check.py exam EXAM.json --key KEY.json --state COURSE.json` under `quiz-record.md` before rendering a mixed exam. Inspect the actual rendered question text and separate key semantically as well; the checker cannot judge plausible distractors, leakage written in prose, or conceptual correctness.

After actual grading and chapter/profile updates, use `scripts/study_check.py loop COURSE.json --profile PROFILE.json` plus normal state/profile checks. Summary agreement is not proof of mastery; read the underlying answers and criteria.
