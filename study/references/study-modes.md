# Study 6.6 — Two modes, one learning record

All seven commands use one source-grounded LP map and the same V3.5 learner
profile, course state, answers, mastery evidence, saved main cursor, and deep
return point. The difference between Study and Study-D is **teaching scope
and explanatory depth**, not an arbitrary number of LPs.

## /study — connected, complete learning Units

- Read the whole bounded scope and map all important LPs, experiments,
  prerequisites, source anchors and exceptions.
- Group closely connected LPs into a Unit with one understandable goal or
  mental model. The exact number follows prerequisite burden, real concept
  density and the amount that can be explained in a continuous lesson.
- Explain the central idea and the relations among LPs with a complete
  example. A visual comparison, process diagram or other device is used
  when it helps; plain text is valid for simple concepts.
- `/study` produces the course overview first. `/study-n` then writes the
  NEXT Unit as complete HTML using current learner evidence. The user
  receives one Unit at a time.
- Preserve every LP identity even when grouped into the same Unit, and
  identify which key knowledge is postponed to a later Unit.

Example: Agent's LLM, context and tools can form one standard Unit with
one task walkthrough showing information flow and feedback. The Unit must
define each component before asking the reader to diagnose an Agent error.

## /study-d — focused, fully explained knowledge

- Narrow the learning target to one independent mechanism, formula,
  algorithm, experiment, failure mode or question that genuinely warrants
  detailed teaching. A page can include several prerequisites and tightly
  connected LPs if necessary to make the core problem understandable.
- For a multi-page selected scope, complete source coverage mapping and
  independent outline review come first. The learner approves the full
  outline before the first teaching page.
- Give full reasoning steps, intermediate states, numerical values where
  reported, a concrete worked case, boundary conditions and the meaning of
  key terminology. Complex experiments explain the actual setup,
  comparison, observed result and limits.
- Generate and verify only the current page, deliver it and adapt the next
  page from feedback. Do not needlessly pre-generate an entire 30-page module.
- Record `main_return` and the deep `next_page` cursor. Return to ordinary
  Study at the saved Unit without restarting profile or intake.

Example: loss masking deserves a deep page that shows the actual tokenized
question and answer, specifies which tokens contribute to loss and follows
one step from prediction through gradient update.

## Shared authoring path

`Original source → complete LP coverage and approved route → directly authored
complete HTML → one independent final page review → browser check → confirmed
delivery → assessed learning if actual answers are submitted`.

- The HTML author decides narrative, figure type, visual hierarchy, pacing
  and interaction together. Mandatory design/spec/storyboard/typed-component
  files are historical V6.4/6.5 compatibility only.
- Complete explanations appear before self-checks and remain visible.
  Necessary English technical terminology receives Chinese explanation
  at first meaningful occurrence.
- Reviewer reads the actual original source and the final visible HTML;
  tests whether a beginner can follow the causal logic, see all required
  conditions and understand figures without guessing intermediate steps.
- Browser checks actual user-facing content at desktop and mobile sizes.
  Software QA and semantic review remain independent evidence.
- The canonical LP course state records real answers; HTML clicks alone do
  not advance mastery.

## Other commands

`/study-e` provides a new focused explanation without resetting the Unit
or deep route; retain the old version. `/study-q` tests taught material
with a separately retained answer key and scores real submissions.
`/study-c` produces a complete, readable compilation rather than a
one-paragraph summary. `/study-m` distinguishes planned, delivered and
assessed LP progress. They share the current source and course state.

## The primary failure mode to prevent

If the first screen is a diagnostic choice that requires knowledge which
has not yet been explained, the page's teaching order has failed. If a
four-stage training lesson contains only four category cards without the
actual process, signal, example and implication, the explanation is
incomplete. If a component displays only a label or clickable decoration,
it adds cognitive load without increasing understanding. Repair the actual
HTML at the first missing step, and re-review its new content hash.
