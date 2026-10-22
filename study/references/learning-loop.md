# Knowledge Points and Learner Evidence Drive Study

Read for course planning, a stage/chapter assessment, a meaningful learner change, or resumption. This is the teaching loop, not a new service or mandatory interview at each turn.

## Start and plan

Read the established learner profile and current course checkpoint first; then load relevant LPs, source anchors and evidence. Preserve `first-use.md` for a new learner. Do not assume installing a Skill transfers host memory.

Use the learner's purpose to state a concrete chapter goal: e.g. “explain how SQL selects information without writing code” differs from “independently implement a query.” For each required LP, identify the observable criteria needed for that goal. Keep source coverage complete; adapt depth or mark optional/postponed material transparently, never silently remove important mechanisms. If the user changes the goal, revise criteria without erasing earlier evidence.

Inventory the accessible bounded book/video/chapter into stable LPs with sources, prerequisites and objectives. Group related LPs into Units; units are delivery groups, not mastery identities. Plan the route first, then generate the current standard Unit using the latest learner evidence. Do not prewrite every future standard Unit and ignore subsequent learning. `/study-d` remains the exception: generate the complete scoped multi-page module before pagewise delivery; adapt affected not-yet-delivered pages when a real gap appears, retaining versions.

## Teach, observe, continue

For each Unit choose its content from the current LP objectives + relevant profile + demonstrated course evidence. Change entry point, example, prerequisite explanation or support only when justified. Unknown is not inability. Explicit “I do not know SQL” needs a bounded repair and a return point, not a new programming course.

After the learner responds, separate navigation, actual understanding and teaching problems. Save useful observations in course evidence; no complete exam or profile rewrite is required after each Unit. `/study-n` continues the route with updated context, without automatically promoting mastery. When new evidence shows improvement, reduce unnecessary scaffolding; do not freeze the learner at their first recorded level. Preferences never override the current request.

LPs can be partly understood. In `assessment` or a compact evidence outcome record, state `demonstrated_criteria`, `pending_criteria`, and `next_check`. These may be plain-language lists, not numeric dimensions. Promote the overall LP only when its current goal's material criteria are supported. Knowing a term is not evidence of explaining its mechanism or applying its boundary. Preserve uncertainty and assisted/independent distinctions.

## Assess a stage, then update the learner record

At a natural stage/chapter boundary offer the mixed exam or honor `/study-q`; do not force testing to navigate. The exam blueprint uses the stage's required LPs, goal, actual taught material and relevant learner evidence. Target uncertainty while still covering the core scope. Change writing burden, not the required conceptual standard. Untested points stay unassessed. See `review-quiz.md`.

After actual submitted answers:
1. Grade against the frozen question revision and source-supported rubric. Diagnose narrowly; a wrong selection is a possible misconception, not proof of its cause. Withdraw invalid penalties if the question is defective.
2. Save actual answers/evidence and affected LP assessments in course state; verify readback. Do not promote from total score alone.
3. Write/update one current chapter summary in course `chapter_summaries`, retaining earlier assessment evidence. Show the learner what was demonstrated, what remains uncertain, and the next useful action.
4. Refresh the matching course entry's `chapter_summary` in the named learner profile as a **derived snapshot** of that summary. Detailed answers and authoritative LP states remain in course state. Verify the snapshot matches before reporting both saved.
5. At the next Unit/session, consult the latest authoritative course evidence. A stale/missing profile snapshot must not override it. Repair the snapshot when storage is available; a failed second save is a disclosed partial save, not grounds to discard the successful first save or stop teaching.

This snapshot is required after meaningful stage/chapter grading when persistence is available, not optional vague biography. If storage is declined/unavailable, give a compact exportable record and disclose that it was not durably saved. Do not invent answers or mark an unsubmitted exam completed.

## Lightweight summary contract

Optional additions keep legacy course schema `3.0` and profile schema `1.0` readable. Existing courses need no mass migration. Create summaries only after an actual assessment.

Course `chapter_summaries` is a list of objects with:
- `scope_id`, `goal`: nonempty strings; scope is the assessed chapter/stage, not a global ability label.
- `revision`: positive integer, increment for a meaningful changed assessment summary.
- `required_lp_ids`, `assessed_lp_ids`, `evidence_ids`: actual IDs in this course.
- `coverage`: `partial` or `complete`, meaning assessed coverage, **not mastery**. Complete requires every required LP assessed; reasoning adequacy still needs semantic review.
- `demonstrated`, `pending`, `next_actions`: concise string lists naming criteria/capabilities and uncertainty, not a duplicated scorecard. Pending may include assessed-but-unresolved and unassessed criteria.

The corresponding profile `courses[]` entry keeps `course_id` and its existing `state_ref`; `chapter_summary` is an exact derived copy of the current summary for that scope. Other chapters remain available via course state. Do not copy all raw answers or maintain independent mutable mastery in the profile. Invalidate/rebuild the snapshot after a grading correction; preserve original evidence and link the correction.

Run `study_check.py loop COURSE.json --profile PROFILE.json` after synchronizing, as well as existing state/profile checks. It checks references and snapshot agreement, not whether the pedagogical conclusions are true.

## Reuse knowledge across books and videos

Only when useful for the current LP, consult relevant course pointers in the learner profile. Compare meaning, goal, prerequisites and boundaries, not just matching English labels.
- Full overlap: reuse valid earlier evidence as scoped background, with its course/evidence reference; confirm only when necessary.
- Partial overlap: reuse the known part and teach/check the new boundary.
- Same name, different meaning: keep separate.

Keep local LP IDs; do not create a global ontology/database or copy old mastered labels into a new course. A related prior explanation can justify less repetition, but a broader goal needs new evidence. If prior evidence is unavailable, report the uncertainty rather than pretending to have read it.

## Reconfirmation and provenance

Do not automatically downgrade understanding with time. If the current task relies on an older, differently scoped or self-reported claim, or the learner says they forgot, offer a brief relevant check and permit skipping. Distinguish “demonstrated previously” from “reconfirmed now”; same-day repetition is not long-term retention evidence.

Keep source conclusions, tutor-added explanations and fictional scenario assumptions distinct through Unit → exam → key → grading → summary. Material required by a new scenario must be taught or supplied. A teacher's ambiguous question must not become a permanent learner defect.

## End-to-end acceptance

Verify generated behavior, not rule headings: a response exposes a specific gap → course evidence is saved → a subsequent actual Unit makes the relevant adjustment → a fresh bounded task supplies new evidence → chapter summary and profile snapshot agree → a new session resumes without repeating intake. No relevant new evidence means no forced teaching change. Synthetic test learners must never enter the real learner's folder.
