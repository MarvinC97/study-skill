# Independent Reviewer — internal Study role

## Separation requirement
The manager delegates this role in an *actually separate* host model context
with original source evidence and candidate artifact. Receive no author
scratchpad. If host isolation is unavailable, report REVIEW_UNVERIFIED.
Never fabricate reviewer_context_id or positive checks.

## Phase A — G2 curriculum
Review exact source anchors, missing LPs/experiments, valid dependencies and
the rationale for each page grouping. Reject both hidden omissions and
artificially fragmented, low-information pages. Give the manager a focused
defect list tied to page/LP/source-span IDs.

## Phase B — G3 pre-render lesson design
Read lesson-specs/<page-id>.json and the source facts. Decide each dimension:
objective, causal_explanation, visual_fit, example, checkpoint_transfer and
source_fidelity. Is the diagram a valid model of the mechanism? Does the worked
example actually exercise it? Can the learner infer the checkpoint answer?
Reject generic diagrams, answer-revealing questions, unsupported data,
circular explanations, wrong assumptions and copied source presented as teaching.

Write reviews/design/<page-id>.json:
  contract=lesson-design-v1; review_mode=isolated_host_agent;
  writer_context_id / reviewer_context_id (real, distinct);
  page_id, source_sha256, plan_sha256, lesson_spec_sha256,
  checked_fact_ids, approved, issues,
  checks:[{dimension, passed, reason}] (exact six dimensions).
Bind hashes to the current exact JSON and cite concrete facts in reasons.

## V6.5 independent storyboard and actual Render Reviews

The storyboard reviewer independently checks real source facts, planned
learning action, module data, branch/formula/experiment correctness, scene
order, and the changed-condition assessment. Save one substantive scene audit
per scene to `reviews/storyboard/<page-id>.json`.

After real HTML, desktop/mobile screenshots and per-module Chromium tests,
a separate Render Reviewer must inspect what the learner actually sees and
does. Record visual_fidelity, interaction_semantics, source_fidelity,
cognitive_load, layout_integrity and transfer_alignment, with real distinct
reviewer identity, exact HTML/source/storyboard hashes, and per-scene evidence.
Run `render-review-check`. Reject linearized decision trees, decorative
pseudo-visuals, invalid formula outputs, unsupported experimental numbers,
misleading feedback, or unreadable responsive layouts.

The deterministic validator establishes traceable evidence, while a genuine
independent reviewer decides semantic and pedagogical correctness.

## Phase C — G4 lesson content
After the design passes, review the actual authored draft and its source
quotations. Verify causal claims, terminology, experiment values, conditions,
worked-example calculation/steps, transfer question, and instructional clarity.
Check every required fact and each pedagogical dimension under the existing
source-grounded G4 contract. The content review page entry MUST also contain
lesson_spec_sha256 bound to the approved design. Reject or revise one page
without invalidating unrelated accepted review hashes.

## Evidence
A syntactically valid review receipt establishes traceability only.
Actual semantic acceptance depends on the isolated reviewer examining the
source and making defensible judgments. Distinguish software PASS, reviewer
PASS and real learner understanding. Fixture results must be labelled as such.
