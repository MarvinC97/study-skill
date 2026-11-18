# Study V6.5 — Design-First Teaching Contract

Study's objective is learner understanding and usable transfer. LP count,
generated HTML count, word count and valid JSON shape are intermediate measures.
This reference is mandatory for all NEW pages in ordinary `/study` and `/study-d`.

## V6.5 storyboard composition and rendered-page review

For NEW course plans, set `render_contract: storyboard-v1`. This adds a
genuinely independent storyboard review after design-check and before the
full lesson draft. The Designer chooses 2–7 scene modules from eight vetted
teaching components and a layout shell (overview, exploration or evidence).
The scenes declare actual learner actions, expected transitions/formulas,
original LP/fact IDs and a final changed-condition checkpoint.

After content review and actual Chromium testing, the reviewer must inspect
the rendered HTML and 390/1280 screenshots before a page can be published.
Run `storyboard-check` before drafting and `render-review-check` before G6.
See `storyboard-components.md` for full data and review contracts.

## One public Skill, three internal roles

1. `agents/curriculum-planner.md`: read the actual source and create the complete
   anchored LP / experiment / prerequisite map; group into standard Units or
   focused deep pages. Preserve V3.5 LP IDs and the existing course state.
2. `agents/lesson-designer.md`: design ONE page as a teachable mechanism, experiment,
   comparison, mathematical explanation or failure case before writing a full
   lesson. Save `lesson-specs/<page-id>.json`.
3. `agents/independent-reviewer.md`: use a genuinely isolated host context to
   review source fidelity, teaching sequence, visual meaning, worked example,
   changed-condition checkpoint and cognitive load. Persist `reviews/design/<page-id>.json`.

These are internal task roles; the Codex/DSH host actually invokes them.
Markdown files by themselves do not start autonomous processes. Study continues
to use the host's connected model with no Study-specific API keys.

## Required execution order

`G1 source → G2 complete, approved curriculum → lesson-spec JSON →
separate design review → design-check → lesson draft → separate G4 review →
lesson-type HTML rendering → real Chromium G5 → real G6 delivery`.

The host uses `v6_agent.py design-check --workspace WORKSPACE --page-id PAGE`
before writing the teaching draft. G3 rejects missing lesson design; G4
rejects content review for another design hash. Source/plan revisions
invalidate the matching receipts. No separate model-client call is made.

## Minimal lesson-spec JSON

All fields below have functional meaning. Use actual page/LP/fact IDs and
grounded source terms. This example is illustrative:

```json
{
  "schema_version": "lesson-design-v1",
  "page_id": "P001",
  "lesson_kind": "mechanism",
  "lp_ids": ["LP001", "LP002"],
  "objective": "Trace how observations, actions and rewards form one learning cycle.",
  "central_question": "How does an observed transition change future decisions?",
  "insight": "Actions cause state transitions and reward feedback; both inform future policy.",
  "misconception": "Immediate positive reward always proves a good long-term policy.",
  "source_fact_ids": ["F001", "F002"],
  "teaching_moves": [
    {"kind":"intuition","focus":"Start by tracing an agent's single action in a small game.","fact_ids":["F001"]},
    {"kind":"mechanism","focus":"Connect observed state, selected action, environment transition and feedback.","fact_ids":["F001","F002"]},
    {"kind":"worked_example","focus":"Walk through one concrete state transition with a delayed reward.","fact_ids":["F001","F002"]},
    {"kind":"boundary","focus":"Show when immediate reward conflicts with a later goal.","fact_ids":["F002"]}
  ],
  "visual": {
    "kind":"process",
    "purpose":"Explain the causal sequence from current state to action to feedback using labelled transitions.",
    "nodes":[
      {"id":"s","label":"Current state","meaning":"The information available when choosing a move"},
      {"id":"a","label":"Chosen action","meaning":"The policy produces one permitted operation"},
      {"id":"r","label":"New state and reward","meaning":"The environment executes the move and returns observations"}
    ],
    "edges":[
      {"from":"s","to":"a","label":"Policy uses observations to choose the next action"},
      {"from":"a","to":"r","label":"Environment applies action and produces a reward"}
    ]
  },
  "checkpoint": {
    "question":"Why could taking a small penalty now improve expected long-term return?",
    "changed_condition":"A larger delayed reward becomes reachable only after taking the penalty.",
    "expected_reasoning":"Cumulative return includes the expected future benefit, which can outweigh an immediate cost.",
    "rubric":"Distinguish immediate reward from discounted or cumulative future return and explain the changed condition.",
    "fact_ids":["F001","F002"]
  }
}
```

`lesson_kind` accepts: `concept`, `mechanism`, `algorithm`, `math`,
`experiment`, `failure_case`, `comparison`, and `decision`.

- Mechanism/algorithm: meaning-labelled cause/process/decision diagram.
- Math: the source-grounded formula, variables and a worked calculation.
- Experiment: actual setup, comparison, result table, source provenance and
  extrapolation limit. If no value is reported, state that explicitly.
- Failure case: first wrong action, subsequent consequences, a narrow fix and
  independent holdout check, shown on a timeline.
- Comparison/decision: controlled variables and why one branch fits.
- Simple concept: concise text if a diagram would add noise.

`visual.kind` accepts: `text`, `process`, `decision`, `comparison`,
`experiment`, `timeline`, `math` or `concept_map`. Any visual must explain
a relationship; it must not be a decorative arrow sequence.

## Reviewer receipt

The independent reviewer produces `reviews/design/P001.json` with exact:
`contract,review_mode,writer_context_id,reviewer_context_id,page_id,
source_sha256,plan_sha256,lesson_spec_sha256,checked_fact_ids,approved,issues`.

The `checks` array must have all six dimensions:
`objective,causal_explanation,visual_fit,example,checkpoint_transfer,
source_fidelity`. Each provides `dimension,passed,reason` tied to the actual
source and design. The two context IDs must differ and originate in actual
isolated host execution. Use `v6_agent.py hash-json --file FILE` for digest
values; never copy hashes from another revision.

Content G4 receipts ALSO include the accepted `lesson_spec_sha256` and
the actual draft hash. Semantic accuracy needs genuine separate review;
receipt syntax and hash matching alone cannot prove it.

## Teaching content and accessible renderer

After `design-check` passes, the Designer writes the existing structured
`drafts/P001.json` with original teaching explanations and examples.
`draft.checkpoint.question` must match the reviewed transfer question.
The type-aware renderer places a meaningful visual before causal teaching,
keeps one complete worked example, explains limits, and hides extra paragraphs
behind an optional disclosure. Source quotations remain accessible in a
separate evidence section, and never replace authored explanation.

HTML is self-contained, responsive and keyboard-operable. The native
`details` questions can be revealed without JavaScript. Clicks or page visits
never promote learner mastery; actual learner replies and rubric evidence do.

## Pilot before large-scale chapter generation

After the complete G2 source/outline review, produce three representative
pages: (1) causal mechanism, (2) experiment comparison, (3) failure timeline.
For each: design → independent design review → draft → G4 → actual HTML →
desktop/mobile Chromium → genuine learner-facing inspection. Fix patterns
causing poor explanations or visuals before expanding generation.

Use a source-aware negative fixture that looks superficially complete (three
generic paragraphs, correct Fact IDs and clickable buttons) but has no
lesson spec, meaningful visual or transfer question. This must fail.
Do not represent fixture reviewer responses as actual educational success.

## Cost, revision and continuity

Reuse unchanged review and Chromium receipts by exact content hashes.
Rework only the failed page and any truly dependent artifacts. Record first
pass versus revised acceptances, concrete rejection categories, G5 cache hits,
confirmed deliveries and independent learner transfer outcomes. No single
count is a teaching-quality proxy.

V3.5 learner profile, study-state.json, prior answers, seven slash commands
and branch/Unit cursors stay intact. Historical 99-page drafts remain
recoverable for rebuilding, but a newly verified V6.5 page must satisfy
the design-first contract. Windows uses ordinary Python and Chromium;
no WSL2 or second model provider is required.
