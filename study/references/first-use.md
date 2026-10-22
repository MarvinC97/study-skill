# First Use and Returning Learners · Study V3.4

This is the normal startup contract, not a script for every teaching turn. Respect the order while reusing answers already explicitly supplied. Never ask a long questionnaire before the learner can see the knowledge map. Maintenance of the Skill itself does not create a learner profile.

## 1. Establish the English name

For a genuinely new learner, first ask: “你的英文姓名或常用英文名是什么？” English applies to the name only; instruction remains Chinese with source English terms. A preferred English alias/romanized name is enough; no legal identity or account verification is needed. If the learner already explicitly supplied a usable name in the current setup, use it without asking again. Do not infer a name from an OS account or unseen host memory.

Wait for the name before normal profile creation and course intake. If only a Chinese name was supplied, ask for their preferred English spelling; do not silently transliterate. If a source arrived with the initial request, retain it for step 3 rather than asking them to send it again.

## 2. Resolve and create/read the fixed profile

Default data root: `Path.home() / "Study"`, resolved through the actual host. Default learner file:
`<home>/Study/learners/<name-slug>/learner-profile.json`.
Course data: `<home>/Study/learners/<name-slug>/courses/<course-id>/study-state.json` and its artifacts. Example English name Marvin → `learners/marvin/learner-profile.json`. The original English spelling lives inside the JSON; a safe lowercase slug names its folder.

Use `../scripts/study_home.py` with `locate --name NAME` first, then `init --name NAME` only after the supplied name establishes the requested profile. Shell-quote the actual name; never interpolate raw input into code. The helper checks names, uses a safe path, creates only missing profiles and verifies readback; it will not replace existing profile contents. It has no database or network. Its atomic creation uses a filesystem hard link; if the filesystem does not support it, report that exact limitation and use a supported verified file-creation method only within the same authorized data location, preserving existing files. Do not change OS permissions or silently switch roots. Existing files must be read, not recreated as empty. A legacy profile without name fields is read with the existing checker first; after the learner explicitly selects it, add only the confirmed name/slug fields with a backup and readback, rather than repeatedly calling init or erasing it. Then run `study_check.py profile` on the actual path.

An explicit previously chosen data root takes precedence over the default; use `--root` for that actual root. Keep it fixed and visible for subsequent sessions. If the default is outside allowed writes, do not silently switch to a random temporary path: explain and ask for one accessible persistent Study root. If no persistent filesystem exists, disclose that fact and offer an exportable profile; preserve the name→goal→map→background order but do not claim fixed-location storage. The learner may explicitly request temporary learning without saving or naming; label that exception rather than block an urgent explanation.

No user/account service, multi-device synchronization or conflict-merge system is introduced. The name is only a human-readable file locator.

## 3. Ask what to learn

Ask for the material/topic and purpose when missing. Reuse supplied books, chapters, files, URLs and explicit goals. Do not yet assume they know the prerequisite vocabulary. Store goals as self-report, not evidence of mastery.

## 4. Build and show the preliminary knowledge structure

Read actual available source material under source-adapters/source-planning. Present the bounded topic map: what the source contains, the relevant hard/soft prerequisites and why they matter, and what understanding would look like. Mark unread source portions and provisional dependencies honestly. This map is a planning artifact, not formal Unit 1 teaching; do not silently drop required concepts to fit an assumed level.

## 5. Ask about relevant prerequisite AND target familiarity

Use the displayed map to ask short concrete questions, grouped only when easy to answer. Ask about both needed foundations and the topic itself. Describe unfamiliar ideas in ordinary language; do not ask a novice to rate a bare list of jargon. Offer natural answers such as first exposure / heard of it / can explain / have used it, and accept “不知道”. These are self-reports, never automatic mastery states.

Example for SQL: “你用过 Excel 这种行列表格吗？你知道数据库大致做什么吗？SQL 是第一次接触，还是看过/使用过？” This is an example, not a mandatory universal questionnaire. Known course evidence can answer a question already; explain any important remaining uncertainty briefly. Optional small diagnostics may clarify only material ambiguity. Do not require a formal exam or numerical self-rating.

Wait for their response or explicit choice to skip before finalizing the normal route. A skip means an accessible provisional starting point with unknown evidence, not that prerequisites passed. Record meaningful answers in profile/background and the current course intake.

## 6. Finalize route, save, then teach

Adjust entry point, prerequisite bridges and support based on step 5. Save the profile and course route, verify readback, then deliver the final overview only. `/study-n` enters the first Unit; an explicit request to begin after the finalized overview is equivalent. Do not restart the whole intake before each Unit.

Optional per-course `intake` extension under schema 3.0: `stage` (awaiting_goal / awaiting_familiarity / ready), `preliminary_map_ref`, `familiarity` (scoped self-report and actual source), and `skipped_by_learner`. Store only useful facts; no second mastery record. A checkpoint before readiness must not be presented as a formally started lesson. Persist the actual current stage when files exist so an interrupted intake resumes at the missing step.

## Returning use

Use the explicit name/current course locator or a verified profile already established in the session. Read the same file and course state; do not repeatedly ask the name, reset progress or re-run familiar foundations. In a fresh session with no established locator, check only the fixed Study learner directory: a single valid named profile can be used with a brief “继续 NAME 的记录”; if selection is genuinely ambiguous, ask which English name rather than inventing one. No broad private-directory search.

An existing course without V3.4 intake fields is legacy progress, not a new learner: preserve it, establish a missing name/location only as needed, and do not force re-onboarding. New topic: reuse profile, then goal→preliminary map→only relevant missing familiarity→final route. Never silently move legacy course data just to satisfy the new default path.
