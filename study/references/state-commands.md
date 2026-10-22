# State and Short Commands · V3.0

Read this for `/study-n`, `/study-m`, or state recovery. Use the single lightweight per-course `study-state.json` contract in `../schemas/learning-point.md`; do not introduce a database or parallel state files.

## Minimal study state

Track active source and revision, bounded active scope/chapter, stable LP/Unit IDs, Unit route/order, inserted prerequisite mini-Units, optional/postponed depth, actual learner evidence, weak/confused concepts, artifact revisions/references/availability, delivery progress and pending Study-D branch with its main-path return point. There is no teaching-depth mode state.

Keep three things separate:

1. Artifact generation and QA: has material actually been created and checked?
2. Delivery/navigation: what was surfaced, and where should the next step resume?
3. Learning evidence: what did the learner actually demonstrate?

The LP evidence states are `unassessed`, `attempted`, `understood`, `applied`. Require actual answers plus a source-supported rubric and misconception record; explanation delivery alone never establishes understanding. Keep original English terms/code and explain them in Chinese.

## `/study-n`

First inspect `deep_branch` before changing the main cursor.

- If a Study-D branch is pending/delivering, do not accidentally advance the main Unit. Briefly identify its next page and ask whether to continue the branch or return to the saved main Unit, unless the learner already clearly chose one. A bare `/study-n` is not permission to silently skip pending deep pages.
- If the learner chooses the branch, deliver only `next_page` under `deep-module.md` §9 and update the delivery cursor. If they choose the main path, mark the branch paused and restore `main_return`; keep its next page for later resumption.
- After an explicit return/pause, normal `/study-n` advances along the main route. Mention a paused branch in the map, not as a repeated blocker on every advance.
- With no active deep branch, enter the next unfinished route Unit. If the overview was just created, start Unit 1. If the learner explicitly continues after the current Unit, record route movement and start the next Unit, without changing LP understanding merely for continuing.

Do not regenerate the full overview. Begin with compact `Unit X / N` and one short bridge. Unit position uses current route order, while stored IDs remain stable. An evidenced hard-prerequisite gap gets the minimal repair first; unassessed alone is not evidence of a gap and must not become an automatic exam gate; do not silently drop the dependent LP.

## `/study-m`

Show the current chapter map by default. If the chapter is complete or the learner clearly asks for the whole book, show the cross-chapter map. Mark current position, pending/paused branches, intentionally postponed depth and source gaps.

Display route/artifact progress separately from assessed LP understanding. “5 / 5 Units delivered” is not “chapter mastered.” Use conservative language such as “3 LPs demonstrated; 2 not yet assessed.”

## Natural-language state actions

Handle going back, switching chapters, restarting a path, revealing original source locations, and asking current position without extra slash commands. Preserve progress unless explicitly reset. Switching scope preserves the old scope's state and branch return points. A restart of teaching does not delete historical answers.

## State recovery and migration

1. Read available state and verify the referenced artifacts, including accessible legacy artifacts not yet indexed.
2. Recover the last clearly established source/scope/Unit from conversation when state is missing.
3. Preserve explicitly completed Units as route history and preserve actual weak/confused evidence.
4. Migrate original concept labels conservatively using `learning-point.md`; never turn old “completed” into new “understood” without the answer/rubric evidence.
5. Preserve source and artifact revision identities; mark missing references unavailable rather than guessing content.
6. Recover a pending Study-D `next_page` and `main_return` if supported; otherwise ask one focused question only if navigation is blocked.
7. When persistent files are unavailable, offer an exportable compact course-state record and explicitly distinguish it from temporary conversation context.
8. Resume from the last unambiguous checkpoint. Do not invent progress or ask for information already available.

## Chapter completion

Use `learning-loop.md` for the learner’s goal-specific criteria and assessed chapter summary → profile snapshot update. Completion is relative to those criteria; merely knowing a definition cannot satisfy an independently-applied goal. Snapshot updates follow actual assessment, never route completion alone.


Report route completion and learning completion separately. LPs with `support_status: "unverified"` are historical claims, not current verified understanding. Learning completion requires each required LP to have demonstrated working understanding (`understood` or `applied` with suitable evidence), or an explicit source-supported optional/postponed non-blocking disposition. Required hard prerequisites cannot be waived as non-blocking depth. If `revision_review_needed` is true because source semantics changed, retain earlier understanding as historical evidence but do not count it as current-scope understanding until the affected objective/evidence has been reviewed or rechecked. Count postponed/optional points separately, never as mastered.

At completion show the integrated chapter map, what actual evidence says the learner can explain/apply, remaining Study-D/optional depth, and a bridge to the next chapter. If only delivery is complete, say that and offer a focused check without inventing mastery or blocking voluntary navigation.

## V3.1 bounded context and correction records

Keep the course index compact: current position, LP summaries, artifact references, unresolved issues and evidence links. Read detailed old lessons/answers only for the current LP or consolidation scope. When existing evidence becomes large, retain it in referenced available course artifacts rather than loading every transcript into each turn; do not invent another database or duplicate index.

Use existing evidence/rubric/assistance and unresolved-misconception fields for diagnostic corrections and cross-Unit checks. A local textarea is not an answer receipt. Preserve skipped/unanswered checks without treating them as passed or forcing the learner to stop.

## V3.2 learner profile and continuity

The restriction against parallel state files means no duplicate course mastery/index. A separate cross-course `learner-profile.json` is allowed for background, explicit preferences, scoped teaching observations, pointers to course state and verified derived chapter summaries; see `../schemas/learner-profile.md`. It is not another scorecard.

At session start read the available profile and current course checkpoint; then load relevant evidence on demand. Resolve the existing course path first, never create a fresh state over an accessible legacy course. New profile absence does not invalidate old LPs, answers, artifacts or cursors. Keep schema_version 3.0 records valid; the V3.2 additions are optional and the Skill version is independent of the state schema.

Update course evidence after receiving and evaluating an actual answer; update background/preferences when genuinely new information changes teaching. Validate JSON and reread changed values using available file tools before reporting a successful save. With no persistent storage, disclose the limitation and offer a compact export; do not repeatedly warn every turn. Natural-language requests can inspect/correct the profile or export/resume a course without new slash commands.

Simple handoff consists of the profile, selected course state and necessary referenced artifacts. Prefer relative paths within the user-selected study folder; verify availability on import, retain missing-item markers and resume from the last unambiguous point. Do not claim that installing a Skill transfers host memory. No identity service, synchronization, device conflict resolver or database is required.

## First-use recovery · V3.4

Read `first-use.md` when no named profile/course is established or current course intake is incomplete. A pending intake stage resumes only its missing step. `/study-n` before readiness continues that intake, not an invented Unit. Legacy courses without intake fields retain their route and evidence; absence does not mean they must start over. Keep an explicit alternative storage root fixed; do not move existing data automatically.
