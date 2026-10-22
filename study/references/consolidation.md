# Study-C Consolidation

Read this only for `/study-c <topic>`.

## Goal

Create one final archival learning page for a topic/section by merging all already-generated Study material into a single complete, non-redundant, fully-visible HTML.

This is consolidation, not a new teaching pass. Read `../schemas/learning-point.md`: artifact coverage and core learning coverage are independent. A complete archive does not prove understanding; demonstrated LP knowledge does not make missing artifacts available. Keep English terminology/code intact and explain it in Chinese.

## Inputs to collect

Inventory every available artifact that belongs to the requested topic/section:

- standard `/study-n` Unit pages
- `/study-e <topic>` re-explanations and alternate examples
- every `/study-d <topic>` page plus its `index.html`
- `/study-q <topic>` exam questions
- model answer key
- learner answers when available
- grading/correction feedback when available
- prerequisite mini-Units that are necessary to understand the topic
- source anchors or source-supported notes already used by the courseware

Use generated artifacts and current study state as the primary consolidation inputs. Use the original source only to verify coverage or restore information that was clearly part of the studied scope but is missing from an available artifact.

Do not add unrelated outside knowledge.

## Workflow

### 1. Define the consolidation scope

Resolve exactly which topic/section the user named and which generated artifacts belong to it.

Do not merge unrelated chapters or neighboring topics merely because they are nearby.

### 2. Build an artifact inventory

Inventory the state index AND actually accessible local/Library/conversation artifacts, including legacy artifacts absent from the index. Reconcile both directions: indexed does not imply available, and unindexed does not imply nonexistent. Do not scan unrelated private material. Verify actual content/reference availability and artifact revision before use.

Record artifact ID/revision, kind, LP/Unit relations, real local/Library reference, availability, provenance and relevant source anchors in the single course state. Keep `original`, `legacy`, `rebuilt`, and `newly_generated` provenance distinct. A filename remembered in chat is not the artifact's contents.

For each artifact identify:

- concepts covered
- mechanisms covered
- examples covered
- conditions / boundaries / exceptions
- confusion checks
- hidden reveal answers
- quiz questions
- answer key
- learner/grading feedback

### 3. Build a coverage matrix

Create an internal checklist of every distinct information point represented across all relevant artifacts.

Each information point must end in exactly one of these states:

- included in final HTML
- merged into an equivalent stronger explanation
- intentionally omitted because it is a literal duplicate
- unavailable/uncertain, with an explicit missing-coverage note (never counted as included)

Never omit a distinct condition, exception, failure mode, example that adds a different mental model, or source-supported engineering detail merely to make the final page shorter.

### 3.1 Missing material and bounded reconstruction

If an artifact is missing, recover it from an authorized available reference first. If that fails, reconstruct only content clearly established as part of the known studied scope, from its available source anchors or reliable surviving material. Label the section/artifact `rebuilt`, identify what supports it, and retain the missing-original note. Do not claim exact recovery, import unstudied chapters, or invent historical examples, learner answers, scores or grading.

If quiz questions survive but the answer key does not, generate a source-grounded key for those exact questions and label it `newly_generated` rather than historical. Repair ambiguous questions transparently, retaining the original and explaining the correction; do not invent a grade. If no quiz was ever generated, mark the exam `not_generated`; do not create a new exam as a side effect of consolidation. If a quiz is known to have existed but is missing, mark it `missing`, not `not_generated`, and disclose the coverage gap. If prior quiz existence is uncertain, mark it `unknown` and state that uncertainty; do not mistake an empty index for proof of no quiz. Only reconstruct exact questions when reliable surviving evidence supports them.

### 4. Deduplicate by meaning

Merge semantic duplicates, not just identical wording.

When several artifacts explain the same point:

- keep the clearest explanation as the canonical explanation
- preserve a second example only when it teaches a materially different angle
- merge complementary details into the same block
- remove repeated headings, repeated definitions, repeated remember cards, and repeated navigation text

The target is `complete + non-redundant`, not `short`.

### 5. Rebuild one coherent teaching flow

Recommended order:

1. topic title + scope
2. complete mental model / overview
3. core concepts in dependency order
4. mechanisms / information flow
5. rules, conditions, boundaries, exceptions
6. common confusions
7. simple examples
8. realistic Agent examples
9. engineering / failure examples
10. Study-D deeper details that add unique information
11. existing mastery exam, or explicit `not_generated`/missing note
12. complete answer key for available existing questions
13. learner answer + grading feedback when available
14. final knowledge map / durable takeaways
15. source anchors / coverage note when useful

Do not preserve the old artifact order when a different order produces a clearer single-page course.

## Full-visibility contract

The final HTML is an archival study sheet. Core information must be visible without interaction.

Hard requirements:

- one self-contained HTML file
- all core explanations expanded by default
- all quiz questions visible
- all model answers visible in the answer-key section
- learner answers and grading feedback visible when available
- no core content hidden behind `<details>`, accordion, tabs, hover, modal, click-to-reveal, or JavaScript-only UI
- no content clipped by fixed-height containers, `overflow:hidden`, carousel, or paginated panels
- page must remain readable when JavaScript is disabled
- responsive on desktop and mobile
- internal anchor navigation is allowed
- optional theme switching is allowed only when it does not control content visibility

If a Study-D source page used hidden micro-questions, convert each into a visible `Question → Answer → Why it matters` block in the consolidated page.

## Quiz section

Include the full existing exam and answers when available. This requirement does not authorize creating an exam that never existed. Apply the missing-material rules above and label a newly generated replacement key. Keep known learner responses verbatim or faithfully represented with provenance; no answer means “no recorded learner answer,” not a fabricated sample response.

For every question show:

- question
- tested knowledge dimension
- model answer
- key reasoning points

When learner work exists, additionally show:

- learner answer
- evaluation
- missing/corrective reasoning

Do not expose a fake learner answer when none exists.

## Coverage verification

Before delivery, verify:

- every relevant generated artifact was inventoried
- every available unique information point appears in the final HTML; unavailable points have explicit gaps, not a false completeness claim
- literal and semantic repetition has been removed
- existing available quiz questions have a complete answer key, or a specific unresolved gap; a nonexistent quiz is marked `not_generated`
- hidden Study-D answers have been made visible
- necessary prerequisite content is present
- no core content depends on interaction to become visible
- no section is visually clipped or overflow-hidden
- internal anchors work
- the HTML is self-contained

Report two separate checks: core learning-point coverage of the known studied scope, and artifact/history coverage of all expected materials. If coverage cannot be proven because a referenced artifact is unavailable, name the missing artifact and affected LPs/examples in the HTML coverage note and delivery summary. A rebuilt section may restore known conceptual coverage but does not restore historical artifact/answer provenance. Never label either dimension complete while its gaps remain.

Verify all content with JavaScript disabled: all explanations, questions, model answers and recorded feedback must remain visible. Inline styles/assets needed for core reading; no required network fetch, external font/script/image, or sibling page. Retain every unique example, condition and exception; semantic deduplication must not erase complementary reasoning.

## Output

Deliver exactly one HTML artifact for `/study-c <topic>`.

Suggested filename:

`study-c-<topic-slug>.html`

Do not split Study-C across multiple pages or multiple page links.

## V3.1 learning corrections and contrasts

Include unique diagnostic clarifications, corrected question interpretations, controlled-contrast conditions and cross-Unit transfer feedback already generated within the requested scope. Preserve actual response provenance; locally typed but unsubmitted HTML fields are not recoverable learner history unless genuinely available. Show both the learner reflection question and its reference explanation as visible text. Keep unavailable personal answers explicitly absent. Retain source anchors beside key claims where they aid inspection. Do not create new remediation lessons or transfer exams as a side effect of consolidation.
