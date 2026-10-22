# Learning Point and Lightweight Study State · V3.0

Use one per-course `study-state.json` as the canonical state. This is a lightweight file contract, not a database, service, event platform, or second parallel tracking system. If files cannot persist, maintain the same compact record in available conversation context and disclose recovery uncertainty. Offer an exportable compact state record for later resumption when persistent files are unavailable; if file export is also unavailable, provide a copyable record on request. Context-only recovery is not durable storage. Do not claim persistence that the host does not provide.

## Identity and relationships

- A Learning Point (LP, 学习点) is a stable conceptual learning objective, not a page or Unit number. Allocate opaque course-local IDs such as `lp-001`; never derive identity from changing headings, source revisions, or Unit positions.
- Keep `source_id`, `source_revision`, and anchors separate from LP identity. A new source revision updates evidence/anchors, not every LP ID. Mark affected LPs for review when their meaning changes.
- Units are teaching groups with their own stable IDs and ordered `lp_ids`. LPs and Units are many-to-many: one LP can recur in several Units, and each Unit can teach several LPs. Artifacts also carry `lp_ids` and `unit_ids`; an LP can appear in many artifacts.
- Regrouping/reordering Units does not renumber LP IDs. Record LP splits/merges explicitly with old/new IDs and the reason; retire old IDs without deleting historical references. Do not blindly copy old mastery onto every split child or a broader merged objective.
- Learner-facing prose is Chinese by default; retain original English technical terms, APIs, identifiers, equations and code, with Chinese explanation. Never translate executable identifiers or quietly alter source semantics.

## Minimal record shape

The following is a field guide, not a populated state file. Add records only when their facts are known; use `null`/empty lists for unknowns rather than invented paths, answers or dates.

```yaml
schema_version: "3.0"
course_id: "stable-course-id"
sources:
  - source_id: "src-001"
    source_revision: "observed version, commit, content hash, or unknown"
    origin: "verified source reference"
active_scope:
  id: "scope-001"
  source_ids: ["src-001"]
  boundaries: "requested chapter/section/topic, explicitly bounded"
  inventory_complete: false
  gaps: []
learning_points:
  - id: "lp-001"
    title: "English term + Chinese label"
    objective: "an observable explanation, prediction, diagnosis, or application"
    source_anchors:
      - source_id: "src-001"
        source_revision: "unknown"
        anchor: "verified page/heading/timestamp/file and lines"
    prerequisites:
      hard: []
      soft: []
    misconceptions: []
    unresolved_misconceptions: []
    assessment: null
    main_visual: "main representation: suitable diagram + relationship, or plain text when clearer"
    check_type: "explanation | prediction | comparison | diagnosis | application | transfer"
    scope_status: "required | optional | postponed"
    postponement_reason: null
    learning_status: "unassessed"
    evidence_ids: []
    revision_review_needed: false
units:
  - id: "unit-001"
    title: "..."
    lp_ids: ["lp-001"]
    source_coverage: []
    route_status: "not_started | delivered | passed_on | legacy_completed"
    artifact_ids: []
artifacts:
  - id: "artifact-001"
    revision: 1
    kind: "overview | unit | explanation | deep_index | deep_page | quiz | answer_key | feedback | consolidation"
    lp_ids: ["lp-001"]
    unit_ids: ["unit-001"]
    generation_status: "planned | generated | verified | failed"
    delivery_status: "not_delivered | delivered | uncertain"
    reference: null
    availability: "available | missing | inaccessible | unknown"
    provenance: "original | legacy | rebuilt | newly_generated"
    source_refs: []
    derived_from: []
    missing_coverage: []
evidence:
  - id: "evidence-001"
    lp_ids: ["lp-001"]
    artifact_id: null
    artifact_revision: null
    question_id: null
    question_revision: null
    actual_answer: "verbatim answer or faithful response record; never invented"
    answer_source: "verified message/artifact ref or locally retained response"
    rubric: "criteria, acceptable alternatives, and source support"
    outcome: "criteria met, missing reasoning, or unresolved ambiguity"
    misconceptions: []
    assistance: "independent | hinted | after_reveal | unknown"
    resulting_status: "attempted"
qa_records:
  - artifact_id: "artifact-001"
    artifact_revision: 1
    case: "specific required behavior or display check"
    environment: "actual host/browser/viewport or static inspection"
    expected: "observable success condition"
    observed: "what was actually checked; no invented execution"
    result: "PASS | FAIL | BLOCKED | NOT_RUN | STATIC_ONLY"
    limitations: []
main_cursor:
  scope_id: "scope-001"
  unit_id: "unit-001"
  next_unit_id: null
deep_branch: null
identity_changes: []
legacy_progress: []
```

`reference` is either null or a real verified local path / Library ID / supported artifact link with its reference type. An ID is not itself a URL; never fabricate links. Track references and delivery status by the pair `(artifact ID, revision)`, retain older revisions when relevant to answers, and check actual availability before reuse/delivery. A new artifact revision does not inherit confirmed delivery from the previous revision. Store detailed learner work in the same state or a genuinely available artifact referenced by it; do not create a second independent state index.

For a pending deep branch, `deep_branch` records `module_id`, `lp_ids`, `ordered_artifact_ids` (index first), `generation_complete`, `qa_passed`, `delivery_cursor` (last confirmed delivered artifact), `next_page` (next undelivered artifact), `main_return` (scope/Unit), and `status` (`pending | delivering | paused | delivered`). Update delivery cursor only on confirmed delivery, not generation or a planned send. Unknown send outcome stays uncertain and must be reconciled before retrying. `delivered` describes artifacts, not comprehension.

`qa_passed` is true only for the explicitly scoped required checks, with their environment and limitations recorded; never use it to imply an unrun browser check passed. Record `coverage_passed` and `presentation_status` (`PASS | FAIL | BLOCKED | NOT_RUN | STATIC_ONLY`) on a deep branch as well, so a single boolean cannot hide unfinished presentation checks.

QA records stay compact and inside this same state, tied to the exact artifact revision. Distinguish executed checks from static inspection, blocked checks and tests not run; a rendered desktop view does not prove mobile or JavaScript-disabled behavior. Artifact revisions require relevant rechecks.

`misconceptions` lists anticipated traps; `unresolved_misconceptions` lists current observed issues with evidence IDs. Optional `assessment` summarizes current question/check, status, criteria and pending fresh check, not a second evidence store. Resolve an observed misconception only with appropriate follow-up answer evidence; preserve its original evidence history.

## Learning evidence is independent of artifact progress

- `unassessed`: no usable answer evidence yet, even if all pages were generated/delivered/read.
- `attempted`: an actual response exists, but understanding criteria are incomplete, ambiguous, or not yet evaluated.
- `understood`: source-supported rubric criteria are met through fresh independent explanation/reasoning for the LP, including material boundaries. State the demonstrated scope.
- `applied`: a fresh independent application/transfer response meets the relevant rubric, not merely a copied worked example.

Record actual answer, rubric, misconception and evidence source before updating learning status. “Continue,” `/study-n`, reveal clicks, opening pages, self-reported reading, a delivered archive and an isolated multiple-choice selection do not establish whole-topic mastery. A selected option can be narrow attempt evidence if captured, not proof of untested mechanisms/transfer. Reassess rather than silently downgrade when later evidence conflicts; preserve prior evidence and record the conflict.

`unassessed` means insufficient assessment evidence, not demonstrated inability. Do not infer a prerequisite gap or block voluntary continuation solely from that status. Use an observed misunderstanding, an explicit learner difficulty, or a necessary missing source concept to justify a prerequisite repair. An actually missing hard prerequisite limits demonstrated understanding of the dependent objective; provide a bounded mini-explanation and offer a check. The learner may skip the check or choose to continue. Preserve the unresolved evidence gap and do not claim dependent mastery; do not turn a check into a compulsory navigation gate. Soft prerequisites enrich understanding but can be explicitly postponed without blocking. Neither postponement nor optionality counts as demonstrated learning.

## Conservative migration

Read existing progress first. Retain original completed Unit markers, learner replies, source anchors, weak/confused concepts and deep-module records in `legacy_progress`, with their source and uncertainty. Map old `strong/working/developing/weak/unseen` to new statuses only when underlying answer evidence supports that status. Otherwise preserve the old label as historical information and use `unassessed`; do not erase progress or imply the learner failed. An old completed Unit is route history, not automatic LP mastery. Record ID mappings for old concepts/Units where identifiable; ask only when ambiguity prevents safe continuation.

## Integrity checks before saving

All references resolve or carry an explicit availability gap. LP/Unit/artifact relations point to existing IDs; retired IDs retain explicit replacements. Required LPs cannot disappear during regrouping. A delivery cursor cannot exceed verified generated artifacts, and a learning status cannot outrun its evidence. Update this single record after meaningful planning, delivery, assessment, or navigation changes; preserve unknown fields and unrelated course progress.

## V3.2 optional extensions (backward-compatible)

Keep this course record as the sole authority for course understanding. The cross-course profile contract is in `learner-profile.md`; its course summaries are references, not duplicated mastery judgments. Preserve existing schema_version 3.0 records and unknown fields; do not require wholesale migration to start learning.

Optional additions, only when useful and supported:
- Course `learner_profile_ref`: actual path/reference to the available profile, or null.
- Evidence `observed_at` and `context`: known observation time and actual task context; unknown time remains null. Assistance and rubric remain authoritative.
- LP `assessment.diagnostic_map`: compact anticipated/observed tells, tentative issue, discriminating probe, targeted repair and prerequisite reference. Mark anticipated versus observed explicitly and link observed claims to evidence IDs.
- Course `teaching_observations`: LP IDs, explanation/artifact reference, observed helpful/unhelpful/unclear response, evidence IDs and a bounded next-teaching implication. This records teaching effects, not a second learner score or causal efficacy claim.

When an objective's meaning changes, review its prerequisites, examples, rubrics and remediation links as well as source anchors. Earlier evidence remains historical and should not automatically establish understanding of an expanded objective. Mere formatting changes do not invalidate unrelated learning evidence.

## Evidence promotion boundary

Only adequate `independent` evidence can newly promote an LP to `understood` or `applied`. `hinted`, `after_reveal` and `unknown` answers remain practice/attempt evidence unless a fresh independent check supplies the missing proof. A later assisted practice does not erase a previously valid independent judgment. Check whether the independent evidence actually covers the current objective; a field or label alone is not semantic proof. Preserve older status labels when evidence is unavailable, mark their current support unverified, and do not silently rewrite history or count them as newly verified mastery.

Delivery means the host accepted this exact page/reference and the supported delivery mechanism made it accessible, not that the learner opened or understood it. If the outcome is uncertain, retain uncertainty and reconcile before retrying; do not demand read receipts unavailable on the host. Native single-page attachments are equivalent to a verified single-page HTML link when that is the supported surface.

For a preserved historical status whose supporting evidence is currently unavailable, set optional `support_status: "unverified"` and explain the gap in existing legacy/evidence notes. This is not a newly verified promotion and does not count toward current verified mastery. A comparison with an earlier lower status must still reject an unsupported upgrade; an unverified marker is not a bypass. Remove that marker only after appropriate accessible evidence is evaluated.

## V3.5 optional learning-loop additions

See `../references/learning-loop.md` for goal-specific LP assessment criteria and `chapter_summaries`. These extend the existing course record, not a second mastery source. Existing states remain valid without them; create after actual assessment. Profile summaries are derived views of these records.
