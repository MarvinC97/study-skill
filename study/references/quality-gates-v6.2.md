# Study V6.2+ · Strict G2–G6 Quality Contracts

This file defines the strict deep-study gates. In Study V6.3, mode-specific
page grouping, cognitive load and teaching obligations are defined in
`study-modes.md`; load that file before either /study or /study-d.

This file is mandatory before executing /study-d. The Codex/DSH host remains
the model, planner, tutor and reviewer dispatcher. All Python checks are
deterministic. Genuine semantic review must happen in an isolated host agent
context, using the actual source and candidate text. A correct JSON shape
is evidence of review inputs/recording, not proof of expert accuracy.

## 0. Source inventory before page planning

Read ALL source text in the bounded scope and preserve hashes/spans. Enumerate
atomic information points before choosing a page count. Each independent
mechanism, decision, algorithm, experiment, failure case or boundary warrants
its own deep learning objective and usually its own page. Avoid a fixed page
target such as 22, 37 or 50. Avoid merging an experiment with adjacent
background content simply because it shares a source section.

G2 deep plans require:
- plan.source_inventory: every atomic source-grounded information point,
  each with id, kind, title, objective, span_id, and exact source_quote.
- plan.points: LP records with required_facts (each has id, text, span_id,
  exact source_quote) and exactly one inventory_id per atomic LP.
  Group up to four closely related LPs on one page when the page contains
  a meaningful shared learning_objective and source-grounded grouping_rationale.
  Each LP keeps its distinct source facts and assessment identity.
- plan.experiment_coverage: EVERY experiment actually headed in the selected
  source, mapped to LP IDs. For each experiment record purpose, setup, controls,
  results, limitations. Each facet is either source_provided with exact
  source_quotes or not_in_source with an explicit reason; never invent a result.
- plan.reflection_coverage: each numbered source thought question explicitly
  mapped to LP IDs and an assessment_plan. Reflection prompts may reuse LPs;
  they do not force an extra content page unless teaching requires it.
- Reviewer uses review_contract=g2-batched-v3: independent review in bounded
  source-anchored batches of at most 12 LPs, a focused audit of high-risk LPs,
  and per-page coherence audits for grouped pages. Full inventory, experiment
  and reflection coverage is still checked. Verified unchanged batch/page
  hashes may be reused; changed scopes are reviewed again. The older per-LP
  atomicity_audits/spans-audits receipt remains supported for single-LP plans.

Minimal illustration (actual IDs/quotes come from the current source):

\`\`\`json
{
  "mode":"study-d",
  "source_inventory":[
    {"id":"I001","kind":"mechanism","title":"How X works",
     "objective":"Explain the causal steps and predict an output",
     "span_id":"S0001","source_quote":"<exact substantial excerpt>"}
  ],
  "points":[
    {"lp_id":"LP0001","title":"How X works","kind":"mechanism",
     "goal":"Explain X and its boundary","inventory_ids":["I001"],
     "source_span_ids":["S0001"],
     "required_facts":[{"id":"F0001-01","text":"<supported assertion>",
       "span_id":"S0001","source_quote":"<exact source excerpt>"}]}
  ],
  "pages":[{"page_id":"P001","lp_ids":["LP0001"],"title":"How X works"}],
  "experiment_coverage":[],
  "reflection_coverage":[]
}
\`\`\`

For the AI Agent Book Chapter 8 scope, the observed source has 19 numbered
experiment headings (8-1…8-19) and 13 numbered thought questions. Each needs
explicit coverage; the source-specific numbers are extracted from the actual
bounded source, never used as global constants for every Study source.

## 1. G2 independent plan review and approval

A reviewer with an isolated **real** host context reads the source inventory,
full selected source spans and proposed page plan. For each LP, ask whether
any mechanism, decision, condition, experiment or case inside it could be
explained, tested and applied independently. An overloaded LP must be split
even when its source spans total fewer than 1,800 characters.

Plan reviewer receipt adds the following to the existing
review_mode/writer_context_id/reviewer_context_id/source_sha256/plan_sha256/
checked_span_ids/approved/issues:

\`\`\`json
{
  "checked_inventory_ids":["I001"],
  "atomicity_audits":[
    {"lp_id":"LP0001","atomic":true,"needs_split":false,
     "reason":"<concrete assessment of this LP, its source boundaries and potential splits>"}
  ],
  "span_audits":[
    {"span_id":"S0001","complete":true,"missing_inventory_ids":[],
     "reason":"<source-based explanation of how every independent claim is mapped>"}
  ],
  "experiment_audits":[],
  "reflection_audits":[]
}
\`\`\`

If experiments/reflections exist, provide one respective audit record per
experiment/question with experiment_id/number, complete/mapped, and reason.
The Host validates inventory ID sets and source coverage. Use
  g2-batched-v3 receipts for bounded reviewer batches (up to 12 LPs each),
  per-grouped-page coherence checks and dedicated risk-LP checks. Persist
  their exact scope hashes; unchanged approved reviews may be reused, and
  modified scopes require fresh independent review. Only then may
the user inspect/approve the reviewed Study-D outline. A page count chosen
before inventory/approval has no authority.

## 2. G3 genuine tutor-authored lesson evidence

The host creates drafts/<page-id>.json. Existing title/intro/sections,
mini_questions/checkpoint, represented_fact_ids, visual and simulation are
retained for HTML rendering. In addition, EVERY LP needs a separate
teaching_evidence object describing:
- shared_teaching: an optional complete causal mechanism/conditions/worked example
  once per grouped page, with a declared list of its LP IDs. Each grouped LP
  retains a substantial lp_connection and its own fact_explanations.
- core_explanation: causal mechanism or the corresponding decision, expressed
  in sufficient detail to explain *why*.
- causal_steps: distinguishable reasoning/process steps, not two paraphrases.
- worked_example: scenario, input, reasoning_steps, outcome, why.
- conditions and limitations: actual applicability and at least one countercase.
- fact_explanations: an original explanatory passage for every required fact;
  cite its fact_id and discuss what the source fact implies.
- experiment: purpose, setup, controls, results and limitations for an
  experimental LP. Preserve numbers and conditions only where the source
  supports them.
- checkpoint.rubric: explicitly state which reasoning would constitute an
  acceptable answer, beyond the multiple-choice answer key.

A source passage pasted into an automatic "facts" box counts as source
quotation, NOT as original explanation. HTML renders teaching evidence in its
own marked container. G3 verifies that the authored explanation appears in
the real page, independently of verbatim source callouts.

Minimum text/step checks reject missing content and obvious short placeholders.
Length is only a screening criterion; padded, repeated, misleading, or generic
prose still fails G4.

## 3. G4 isolated source-grounded semantic reviewer

For each page the independent reviewer compares original source, LP objective,
draft explanations, worked example, boundaries and checkpoint. The receipt
must bind the exact draft_sha256 and cover:

- fact_audits: each required fact, source_span_id, exact source_quote,
  a substantial draft_quote **from the authored teaching evidence**, grounded,
  explained, and a specific reason.
- quality_dimensions: mechanism, causal_reasoning, worked_example,
  conditions_and_limits, assessment_fairness, source_fidelity; add
  experiment_methods for experimental LPs.
- Each dimension: dimension, passed:true, draft_quote, reason. Draft quotes
  must occur in authored teaching content, not the auto-appended fact box.
- Reject any incorrect number, unsourced causal claim, missing variable,
  unexamined limit, invalid checkpoint, misleading analogy, or shallow
  explanation. When rejected, revise only affected LP/page, invalidate stale
  downstream receipts and request a genuinely fresh review.

An \`approved:true\` label with only checked_fact_ids does not satisfy G4.
The checker binds the attestation to the exact draft/source; it cannot prove
that a host reviewer was independently instantiated. Record limitations
accurately if the host cannot provide isolation.

## 4. G5 interactive browser proof bound to actual bytes

Run Chromium/Playwright on the generated HTML and inspect both 390 px and
1280 px viewports, keyboard reveal, answer feedback, reset, simulations and
JavaScript-off reading. Browser receipt carries:
- browser_executed and passed
- viewports_tested:[390,1280]
- keyboard_tested, js_disabled_tested, interactive_tested
- manifest_sha256 and rendered_files filename:sha256

G5 caches each real passing Chromium check by its exact HTML SHA256. When
  one page changes, retest that page and reuse only verified, unchanged pages;
  navigation link integrity is rechecked for the full current manifest.
G5 fails when any required browser evidence is unavailable or the HTML
bytes differ from the tested files. A static HTML scan is STRUCTURAL_ONLY,
and must never be promoted to BROWSER_PASS.

## 5. G6 prepared and delivered are separate

After the G2-reviewed plan is explicitly approved, the host may generate,
independently review, browser-test and stage one new page at a time using
  v6_agent.py stage-next-page --review-file ... . Each accepted page enters
an append-only delivery queue; the learner sees one page per turn. G3–G5
remain PARTIAL_VERIFIED until the approved page list is complete.
For full-batch workflows, after G1–G5 acceptance, publish copies the verified artifacts and records
G6_DELIVERY=PREPARED (ok:false). The host presents one real HTML page in one
learner-visible response and then calls confirm-delivery for its exact file.
Intermediate pages show IN_PROGRESS. Only the final confirmed page sets
G6_DELIVERY=DELIVERY_CONFIRMED (ok:true). Generation, review, publication,
delivery and learner mastery remain separate dimensions.

## 6. Previous 22 pages, 37-page drafts and migration

Treat any existing unapproved 22-page deep module as historical draft data.
Preserve course/learner profile, source fingerprints, prior answers and
archived HTML. Do NOT rename old drafts as verified pages, infer mastery
from reading, or silently discard prior material. First create an atomic
inventory and reviewed new outline from the current source revision. Compare
old page titles/source spans against new inventory, reuse accurate fragments
as candidate material, write revised drafts under a distinct module/revision,
then apply the full G2–G6 gates to their new bytes.

**Compatibility:** this is a stronger, deliberate fail-closed deep-study
contract. Older V6.2 plans and lessons lacking source_inventory,
teaching_evidence, or detailed reviewer receipts require explicit upgrade and
revalidation; no automatic PASS migration is permitted.

## 7. Mandatory negative regression cases

- Deliberately merge two independently testable mechanisms into one LP:
  G2 FAIL. Grouping them as two LPs on one page with one coherent learning
  objective and independent coverage evidence is allowed.
- Omit a numbered experiment or thought question from the plan: G2 FAIL.
- Create three shallow paragraphs, correct fact IDs and clickable controls,
  but no substantive author explanation/rubric: G3 FAIL.
- Return reviewer approved:true without source-anchored batch/page/fact and
  pedagogical evidence: G2/G4 FAIL. Reusing changed scope hashes also fails.
- Modify a reviewed draft or browser-tested HTML while retaining its old
  receipt: G4/G5 FAIL.
- Publish without user-visible delivery: G6 PREPARED, not DELIVERED.
