# Study V6.5 — Storyboard-Driven Teaching Components

## Mission and boundaries

Keep the seven learner commands, V3.5 learner profile/course evidence and
the host's already-connected Codex/DSH model. The designer defines a learning
action and a scene sequence; Python safely assembles tested components.
Learning is measured through actual assessed answers, separately from
generation, HTML interactions, and delivery receipts.

## New-course execution order (mandatory)

1. G1/G2: read the source and produce the complete reviewed LP plan. Add
   `"render_contract": "storyboard-v1"` to `plan.json`. Preserve all LP IDs and
   experiments. A Study-D plan still requires explicit learner approval.
2. G3 design: author `lesson-specs/<page>.json` and obtain a genuine isolated
   independent reviewer in `reviews/design/<page>.json`. Run
   `v6_agent.py design-check --workspace WS --page-id PAGE`.
3. G3 storyboard: author `storyboards/<page>.json` with 2–7 scenes, an
   intentional layout, learning action, module-specific input data, LP/fact
   anchors and final transfer check. Independent review is saved to
   `reviews/storyboard/<page>.json`. Run `v6_agent.py storyboard-check`.
4. G4: author `drafts/<page>.json` only after both design gates. Reviewer
   checks source fidelity, actual teaching and the exact approved design.
   The content review page entry binds `lesson_spec_sha256`,
   `storyboard_sha256` and `draft_sha256`.
5. Render: Python composes the approved modules in the storyboard's order.
   G5 tests real browser interaction, computes actual HTML hashes, and
   captures `reports/screens/<page>-390.png` and `-1280.png`.
6. Render Review: an actually isolated reviewer inspects HTML, screenshots,
   source and storyboard. Save `reviews/render/<page>.json`, run
   `v6_agent.py render-review-check --workspace WS --page-id PAGE`.
7. G6: only then publish, present the exact HTML to the learner and commit
   confirmed delivery. Learner understanding remains a separate evidence state.

For incremental `study-d`, the first `stage-next-page` call may generate the
HTML/screenshots and return `G5 RENDER_REVIEW_PENDING`; perform a genuine
review and rerun the command to publish **the same reviewed bytes**.

## Three layout shells

- `overview` — compact, responsive two-column overview and comparison.
- `exploration` — single-column progressive mechanism/variable exploration.
- `evidence` — experiment or failure evidence takes priority; follow with
  explanation and changed-condition transfer.

Scene order belongs to the Lesson Designer. All layouts become one column
on small screens. Page layout and teaching component are separate choices.

## Eight reusable components

| Module | Learning operation | Required data |
|---|---|---|
| `causal-flow` | Select steps and inspect causal edges | nodes with ID/label/meaning; labelled edges |
| `decision-explorer` | Choose real branches and trace the decision path | start node, decision nodes with options/targets/reasons, terminal outcomes |
| `variable-lab` | Change parameters and recompute numeric results | a named formula and bounded slider controls |
| `math-stepper` | Reveal reasoning and calculation step by step | formula and expression/reason steps |
| `experiment-comparator` | Highlight controlled experimental conditions | comparable table, source provenance, interpretation |
| `trace-debugger` | Locate the first bad action and see its consequences | ordered steps, exactly one first error, repair, holdout |
| `worked-example` | Follow input → calculation/decision → output | scenario, input, reasoning steps and outcome |
| `transfer-checkpoint` | Predict a changed-condition result | question, changed condition, 3–4 options, explanation, rubric |

Use 2–7 purposeful scenes with exactly ONE `transfer-checkpoint` as the
last scene. Every scene maps to actual approved source facts/LP IDs. A module
is appropriate only when it supports a concrete learning action; a clear
paragraph is preferable to decorative interaction.

`variable-lab` uses a whitelist of deterministic equations:
- `pass-at-k` — `p` and integer `k`: `1−(1−p)^k`, assuming independent samples.
- `q-learning` — `q,alpha,reward,gamma,next_q`:
  `q+alpha*(reward+gamma*next_q−q)`.
- `ppo-clip` — `ratio,advantage,epsilon`:
  `min(ratio*advantage,clip(ratio,1−epsilon,1+epsilon)*advantage)`.

No arbitrary formula evaluation, untrusted HTML, or source-supplied JavaScript.
New equations require a separately tested component-library extension.

## Minimal storyboard shape

```json
{
  "schema_version": "lesson-storyboard-v1",
  "page_id": "P001",
  "lesson_spec_sha256": "<exact approved lesson spec hash>",
  "layout": "exploration",
  "learning_action": "compute",
  "narrative": "Predict the effect of independent sample count on success.",
  "scenes": [
    {
      "id": "probability",
      "module": "variable-lab",
      "purpose": "Change sample count and observe the actual pass-at-k probability.",
      "lp_ids": ["LP001"], "fact_ids": ["F001"],
      "props": {
        "formula": "pass-at-k",
        "question": "How does success probability change when k increases?",
        "interpretation": "Additional independent samples provide diminishing gains.",
        "controls": [
          {"id":"p","label":"Single attempt success","min":0.05,"max":0.95,"step":0.05,"default":0.25},
          {"id":"k","label":"Independent samples","min":1,"max":16,"step":1,"default":3}
        ]
      }
    },
    {
      "id":"transfer",
      "module":"transfer-checkpoint",
      "purpose":"Predict a result after the input condition changes.",
      "lp_ids":["LP001"],"fact_ids":["F001"],
      "props":{
        "question":"<exact approved lesson-spec checkpoint question>",
        "changed_condition":"More independent attempts become possible.",
        "rubric":"Explain independence and complement probability.",
        "options":[
          {"label":"Probability falls","correct":false,"reason":"All-fail probability shrinks."},
          {"label":"Probability rises with diminishing gains","correct":true,"reason":"One minus all-fail probability grows."},
          {"label":"Probability remains fixed","correct":false,"reason":"Adding samples changes all-fail probability."}
        ]
      }
    }
  ]
}
```

Use actual source/plan LP IDs, source facts and lesson-spec hash. This is
illustrative, not a substitute for a reviewer or source verification.

## Two genuine independent reviews

Storyboard review (`reviews/storyboard/<page>.json`):
`contract=lesson-storyboard-v1`, `review_mode=isolated_host_agent`, real
distinct writer/reviewer context IDs, source/plan/spec/storyboard hashes,
`approved`, `issues`, plus `scene_audits` containing one grounded decision
and explanation for every scene.

Actual Render Review (`reviews/render/<page>.json`):
`contract=render-review-v1`; source/plan/spec/storyboard/HTML hashes,
`browser_manifest_sha256`, real distinct reviewer contexts, `approved`,
`issues`; a `scene_audits` record for EVERY scene and six explicit
`checks` (each with dimension/passed/reason):
`visual_fidelity`, `interaction_semantics`, `source_fidelity`,
`cognitive_load`, `layout_integrity`, `transfer_alignment`.

The Render Reviewer inspects the actual HTML plus 390/1280 screenshots
and browser test results. A linear list fails a branching decision
Storyboard; a slider whose output never changes fails its learning action;
unsupported experimental values fail source fidelity. The deterministic
checker verifies hashes, evidence and component behavior; the independent
reviewer judges whether the visual representation teaches the mechanism.

## Rollout and compatibility

Before mass generation, validate three actual source-grounded pilot pages:
decision tree, numeric variable lab, experimental comparison/failure trace.
Repair component-level failures once before expanding production.
Reuse verified unchanged page/hash/screenshot reports; changed files need
fresh review. Never claim a synthetic fixture proves real learning quality.

Existing V6.4 plans without `render_contract` keep their historical renderer.
All previously delivered HTML, V3.5 learner profiles, real answers, progress
and nested Study-D return points remain untouched. New V6.5 course plans
must explicitly opt in to `storyboard-v1` and pass these stricter gates.
