---
name: study
version: "6.1"
description: >
  Source-grounded visual tutoring with an autonomous Study Manager and a fail-closed
  local Host. Use when the user invokes /study, /study-n, /study-e, /study-d,
  /study-q, /study-c, or /study-m to learn books, GitHub chapters, PDFs, and
  technical documents. Preserve source coverage, atomic units, visual and
  interactive explanations, real verification and recoverable progress.
---

# Study V6.1 — Agent Entry Point

Keep this entry lightweight. V6.0 Agent Manager and G1–G6 Host remain the execution base. V6.1 restores V3.5 named learner profiles, first-use intake, scoped understanding evidence and cross-session recovery. Load references only for the relevant operation.

## Commands (only 7)

| User command | Contract | Local Runtime |
|---|---|---|
| `/study <source>` | Read full selected source, atomize Learning Points, review outline, deliver overview ONLY | `v6_agent.py run --mode study` |
| `/study-n` | Advance exactly one Unit, preserving progress and requiring independent review and browser QA | `v6_ops.py study-n` (then host confirmation) |
| `/study-e <topic>` | Re-explain current gap, with intuition, simple/Agent/engineering examples and return point | `v6_ops.py study-e --topic` |
| `/study-d <topic>` | Complete LP inventory → frozen outline → one mechanism/decision/case per page → hidden microquestions → independent review → page-by-page delivery | `v6_agent.py run --mode study-d` |
| `/study-q <topic>` | Entire 6–10-question (at least five) multi-angle exam; first HTML hides answer key | `v6_ops.py study-q --topic` |
| `/study-c <topic>` | One expanded HTML of all GENERATED matching material, question answers, exam keys and feedback; fully visible core content | `v6_ops.py study-c --topic` |
| `/study-m` | Source-grounded Learning Point/Unit map, relations and progress | `v6_ops.py study-m` |

## V6.1 host handoff (mandatory for all deliveries)

- A generated or reviewed HTML file is **prepared**, not yet delivered. After the host makes the exact file accessible in a learner-facing response, call `runtime/v6_ops.py confirm-delivery --workspace WORKSPACE --file FILE` for standard Units, explanations and exams.
- Deep module pages use `runtime/v6_agent.py deliver-next --workspace DEEP_WORKSPACE` to prepare **one** pending HTML, and `runtime/v6_agent.py confirm-delivery --workspace DEEP_WORKSPACE --file FILE` only after the host presents that exact page. Preparing the same page again before confirmation is idempotent.
- Only confirmed delivery advances the Unit/deep page cursor. Never advance by file creation, review, a tool's successful return, or the existence of a generated link. A missing host delivery capability leaves the item pending. Hash mismatch blocks confirmation.
- Capture actual learner exam answers from a learner message or explicitly supplied file and call `runtime/v6_ops.py study-q-submit --workspace WORKSPACE --topic TOPIC --answers-file ANSWERS.json`. The independent reviewer grades answers against the original source/rubrics and stores scoped evidence in the canonical course `study-state.json`. HTML selection/click alone cannot promote mastery.
- Re-entering an existing Study-D branch preserves `next_page` and `main_return`. Pause/resolve an active branch explicitly before selecting another branch. Confirm one delivered page at a time.

All commands accept a stable persistent `--workspace`. Keep `source.json`, `plan.json`, `reviews/`, `drafts/`, execution state and artifacts. The learner's profile and canonical course evidence live **outside** the Skill installation. Do not write personal learning records into public GitHub repositories.

## V6.1 learner continuity — mandatory for new learners and returning courses

1. New `/study`: read `references/first-use.md` and `schemas/learner-profile.md`. Reuse a confirmed English alias if already supplied; otherwise ask for one. Bind with `runtime/v61_learner.py bind` or `v6_agent.py run --learner-name NAME`. Explicit `--temporary` is the opt-out for profile storage.
2. Follow name → profile → goal → preliminary source-grounded map → relevant prerequisite/target familiarity → finalized overview. `/study` still delivers **overview only**; `/study-n` starts Unit 1 after intake is finalized. Use `v61_learner.py intake` for goal/familiarity readback.
3. V3.5 `study-state.json` schema 3.0 is canonical for LP understanding and actual answer evidence. V6 Host `state.json` is authoritative for execution gates. `v61_learner.py` bridges both without replacing legacy keys. Read `references/learning-loop.md` for stage assessment and course-to-profile chapter summary.
4. Before `/study-n`, resume the verified saved Unit position and pending `/study-d` branch. Page delivery never promotes mastery. For `/study-e` or `/study-q`, register the generated artifact; real independently reviewed answers are required for `understood`/`applied` status. Read `references/learner-adaptation.md` only if it improves the current teaching decision.
5. Preserve V3.5 existing `study_home.py`, `study_check.py`, `study_quiz_check.py`, `first-use.md`, learner state schemas and records when integrating into an existing repository. Use `scripts/merge_into_repo.py` for a dry-run additive merge, not a blanket overwrite.

## Required loading sequence

1. Before using a source read `references/source-adapters.md`, `references/source-planning.md`; verify actual source text, not a filename or title.
2. Before manager execution read `references/v6-agent-runtime.md`. Host executes `runtime/v6_agent.py`, not a Chat-only simulation of the gates.
3. For Unit authoring read `references/lesson-teaching.md`, `references/writing-clarity.md`, `references/visual-semantics.md`, `references/interaction-design.md`.
4. For deep multi-page authoring additionally read `references/deep-module.md` and `references/storm-questioning.md` selectively for complex topics.
5. For exam or consolidation read `references/review-quiz.md` or `references/consolidation.md` on demand.
6. Before claiming verification read `references/presentation-qa.md` and inspect actual runtime receipts; tests must execute on the GENERATED HTML.

## Agent autonomy vs Host authority

- Manager decides the next allowed action after observing state and failures. Workers are isolated source reader, planner, tutor, visual builder, independent reviewer and browser checker tasks.
- Host exposes the allowed tool set per state; it rejects unapproved actions and enforces G1–G6 gates. Manager cannot self-approve its own syllabus.
- Plan failure routes to Planner; explanation gap to Tutor; rendering/interaction error to Visual/QA. Bound retries and persist all receipts.
- `/study-d` on a dense source requires user approval of the current reviewed outline before publishing pages.
- Maintain one HTML link per separate user-visible delivery message. `deliver-next` advances exactly one page per call; no automated host messages across turns.
- Preserve English technical terms, code, API names and parameters. First occurrence gets a concise Chinese explanation. Distinguish source claims from instructional inference and simulation.
- A page view or button click never constitutes mastery. Keep source anchors and verified learner evidence distinct.
- When no model provider or browser is available, stop with explicit blocked/unverified status. Never label fixture/demo execution as a live Agent run.

## Quality contracts

- G1: source extraction complete within selected scope, with stable hash and span anchors.
- G2: all important spans mapped to atomic LPs, no overloaded pages, independent outline review; owner approval where required.
- G3: each required fact/condition/exception/example represented in a complete content draft and visible HTML.
- G4: isolated independent technical/pedagogical review rejects omissions and wrong reasoning.
- G5: generated HTML actually rendered and interacted with in browser (keyboard, mobile, reset, feedback, JS-off core).
- G6: artifact exists, hash matches, queued one link per turn, progress persists.

The first two Chapter 8 HTML files under `examples/chapter8-preview/` are model-authored acceptance previews. Their source coverage and browser behavior were tested; the full live model-driven manager loop remains a separate acceptance step requiring configured API credentials.

V6.1 learner compatibility is tested with temporary local profiles. Real external model-driven chapter generation and cross-device sync remain separate validation tasks.
