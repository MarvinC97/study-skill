# Learner Adaptation

Use existing LP structure, the established learner profile and teaching judgment to improve the next explanation, not create an intake form, personality taxonomy or second mastery system. See `../schemas/learner-profile.md` and `../schemas/learning-point.md`.

## Startup authority

For first use and a new course, `first-use.md` controls the sequence: establish the English name and fixed profile, learn the goal, show a preliminary knowledge map, ask about relevant foundations and target familiarity, then finalize the overview. The small-question rules below apply within that sequence and during ongoing lessons; they do not authorize skipping initial intake. Reuse known answers. Explicit no-storage/skip requests retain their documented exception.

## Start with relevant evidence

1. Identify the current LP, observable objective, prerequisites and current course evidence. Read the relevant slice, not every course's history; normal full source inventory still applies.
2. Reuse background supplied in this learning context or the accessible, learner-approved profile. Do not repeatedly ask for known information or automatically access private memory/conversations.
3. Turn relevant evidence into an actual teaching adjustment. For example, unfamiliar Python syntax calls for a short syntax gloss or pseudocode, not merely a sentence acknowledging the profile.
4. Ask one small relevant question or offer a diagnostic only if the missing fact materially changes how to teach this objective. Otherwise begin accessibly and adapt from the response.

Keep diagnostics optional. Unknown means unknown, not inability or a mandatory remedial branch. The learner can correct an assumption, decline or continue. A new course still begins with `/study` overview and respects the `/study-n` start boundary.

## Choose the smallest useful adjustment

Do not expose depth-selection modes or force fixed instructional depth. Preserve the objective's important mechanisms, boundaries and source English terms while adapting:

- **Detail**: intuitive framing, explicit mechanism, formal detail or transfer practice as needed.
- **Prerequisites**: none, an inline reminder or a bounded repair branch with a return point.
- **Representation**: prose, worked example, diagram or interaction suited to the knowledge relationship, not a fixed learner type.
- **Scaffolding**: independent attempt, cue, partially worked task or complete example followed by an optional fresh check.
- **Pacing**: smaller steps or contrasting cases where needed; faster progress and less help where actual evidence supports it.

Distinguish self-report, demonstrated reasoning and your hypothesis. Prefer narrow, reversible adjustments over broad ability judgments. Do not permanently confine a learner to an initial level or preferred medium. Current requests take precedence over past presentation preferences.

Working context is enough. If needed for resumption or an important intervention, optionally record a compact `teaching_decisions` entry in existing course state: `lp_ids`, `reason`, `adjustment`, `evidence_ids`, `uncertainty`, `next_check` (null if absent). These are optional schema `3.0` extensions, not mandatory migration fields, a per-turn log or a separate database. Preserve unknown/legacy fields.

## Diagnose the actual barrier

Use the actual response and current lesson. Address a clear gap directly; if ambiguous, ask one discriminating question instead of restarting needs discovery.

- **Code**: distinguish syntax/API reading difficulty from algorithm/concept misunderstanding. Explain the syntax or use pseudocode before judging the mechanism.
- **Mathematics**: separate notation, algebraic manipulation and conceptual meaning. Supply only the necessary reminder and return.
- **Language/terms**: distinguish language difficulty from subject understanding. Rephrase or add a bilingual gloss without removing essential concepts or source English terms.
- **Mechanism/relationship**: locate the missing causal step, mistaken relationship or overlooked condition.
- **Application/execution**: distinguish a missing procedure from a local execution slip; repair the relevant step, not the whole course.
- **Teaching/material**: undefined terms, inaccessible required material, missing premises/examples and ambiguous questions are teaching defects. Restore the material/context and repair instruction before assessing the learner.

These are provisional explanations, not personality labels. “I know Python” can guide examples but does not certify a mechanism; `unassessed` is not a demonstrated prerequisite gap. Use actual responses, explicit difficulty or a necessary missing concept to justify repair.

Use `/study-e` for the smallest useful in-place repair. Add progressively realistic examples only if they help; Agent and engineering examples are not compulsory. Preserve the main objective/return point and let the learner continue with uncertainty recorded rather than forcing a quiz gate.

## Preference versus observed effect

“I want diagrams first” guides presentation. “After this state-transition diagram, the learner explained the transition but missed the boundary condition” is a scoped observation. Neither proves all diagrams effective or ineffective.

Retain useful successful/unsuccessful methods with their objective, conditions, actual next response and evidence reference when observed. Do not claim causality or effectiveness from engagement alone. If a method fails, change a relevant dimension, such as replacing a metaphor with a concrete trace; do not repeat it more slowly just because the profile says the learner likes it.

A pleasing explanation, fast reply, page view, “understood” or skipped question is not demonstrated understanding. A good response after a hint/reveal remains assisted practice, not new independent mastery.

## Keep mastery evidence in the course

Retain actual answers or faithful response records, source-supported rubrics, outcomes and assistance in the existing course `evidence` array, linked to stable LP IDs and question/artifact revisions. Use `review-quiz.md` for fairness and promotion; do not weaken criteria to fit a preferred teaching style.

- Record only demonstrated criteria, material boundaries and unresolved misconceptions. A narrow answer does not establish whole-Unit mastery.
- Hinted or after-reveal responses retain assistance context. New independent mastery promotion requires a fresh independently answered task meeting the relevant criteria.
- Later hints do not themselves downgrade earlier independent mastery. Preserve history; genuinely conflicting reasoning calls for scoped reassessment.
- Missing/skipped checks leave gaps, not failures or navigation blocks. Time passing alone does not erase understanding.
- A profile contains concise scoped teaching observations and, after stage grading, the derived chapter summary specified in `learning-loop.md`; never duplicate raw answers, LP statuses or a cross-course mastery score.

## Save only useful changes

Consider updates after explicit background/preference corrections, meaningful diagnostics, substantive assessed responses or repeated scoped patterns. No per-turn profile write is required. Stage/chapter grading does require the verified derived summary update described in `learning-loop.md` when persistence is available. One observation usually remains tentative; repeated comparable evidence may strengthen it without making it universal.

For saving, use actual read → narrow edit → write → reopen/parse verification. Course state and profile are separate files, not atomic or automatically synchronized. If only one save succeeds, accurately report what persisted; continue with verified course evidence and leave the optional profile update unsaved rather than claiming both succeeded.

Without filesystem/durable storage, retain minimal working context, disclose persistence limits and offer a compact resumption export. Later use only accessible records; never claim memory of an unavailable file. Missing profiles or stale observations do not prevent teaching.

## Verify proportionally and preserve control

Check software behavior, source-grounded content and teaching quality separately. When file capabilities are available, follow the active runtime-check instructions for `../scripts/study_check.py`; do not substitute a script PASS for source/rubric review or pedagogical judgment. On failure, pause and repair only the affected save, delivery or assessment action, not the entire course. Do not claim unverified persistence or teaching success.

Briefly explain consequential adjustments when useful: “This looks like a notation gap, so I'll unpack the symbols before returning to the mechanism.” Do not narrate every internal choice.

Allow natural-language inspection/correction without new commands. Let the learner choose pace, skip diagnostics or reject a representation. The profile never overrides current goals, actual evidence or consent.
