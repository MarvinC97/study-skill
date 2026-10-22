# Study-D Multi-Page Deep Module

Read this only when the user invokes:

`/study-d <topic>`

`/study-d` is the multi-page complete-learning mode for one difficult topic inside the active study source. It is the dedicated multi-page deep-learning mode for one difficult topic inside the active Study source.

Its goal is **complete coverage without visual overload**.

It must preserve the current Study source, source anchors, learner state, and return point. Use the one per-course `study-state.json` contract in `../schemas/learning-point.md`. Map the information-point checklist and pages to stable LP IDs, retaining English source terminology/code with Chinese explanation. Artifact generation, page delivery and learner understanding are independent.

## 1. Resolve the topic against the active source

Use the active source and current study context first.

Identify the exact source sections, pages, files, or timestamps that support the requested topic.

If the topic depends on nearby source sections, include them only when they are necessary to understand the topic correctly.

Do not silently fill source gaps with generic knowledge. If outside explanation is needed, label it as tutor explanation or extension.

## 2. Build a complete information-point checklist before generating pages

Identify every meaningful information point required for working understanding of the topic, including when relevant:

- purpose / problem being solved
- core concept and terminology
- actors or components
- inputs and outputs
- process stages
- causal relationships
- rules and constraints
- states or transitions
- comparisons and alternatives
- exceptions and failure cases
- examples
- important numbers, thresholds, or conditions
- prerequisite concepts needed to follow the explanation
- connection to the current chapter and nearby concepts

This checklist is the coverage authority for the module.

Do not start page generation until the checklist is coherent.

## 3. Turn the checklist into a page plan

Create one HTML page for each major information point or tightly related cluster.

Prefer more short pages over fewer overloaded pages.

There is no fixed page count.

A typical structure may look like:

- `index.html` — whole mental model + reading order
- `01-why-it-exists.html`
- `02-core-model.html`
- `03-how-it-works.html`
- `04-rules-and-boundaries.html`
- `05-example.html`
- `06-failure-case.html`
- `07-connections.html`

Use filenames that match the actual topic.

Do not mechanically create pages that have no useful content.

## 4. Draft `index.html` first as the internal navigation model

`index.html` must contain:

- source / chapter / current Unit locator
- requested topic
- one simple whole-topic mental model
- a visual map of the major information points
- every generated page in reading order
- a short plain-language label for each page
- links to every page
- a clear return point to the main Study Unit

The index is the learner's map, not a compressed article. Drafting it first does not mean delivering it first before the module is ready. Finalize real page references and verify the complete module before any link delivery (§9).

## 5. Generate the content pages

Each page should focus on one main idea.

Use `assets/study-d-page-template.html` as the default interaction pattern when HTML is supported.

A Study-D page is not just a visual explanation. It is a **guided discovery page**:

`CORE VISUAL → MICRO-QUESTION → HIDDEN REVEAL → NEXT MICRO-QUESTION → OPTIONAL DEEPER DETAIL → CHECKPOINT → REMEMBER`

Use only the blocks that help that page.

Each page should have:

- one clear title
- one main diagram / visual model
- short labels instead of dense prose
- source terminology after the intuition
- source anchor when available
- previous / index / next navigation
- one or more hidden micro-questions placed next to the knowledge point they unlock
- one final checkpoint that tests the page-level mental model

For prerequisite pages, teach only the minimum required to understand the main topic.

### 5.1 Hidden micro-questions are mandatory

Every major knowledge point on a content page must have at least one small question when a useful question can be formed.

The answer must be hidden by default and revealed only after the learner clicks/taps. Use a simple accessible `<details>` block or a button/reveal interaction.

The learner should encounter the question at the exact point where curiosity or confusion naturally appears.

Good micro-questions ask about:

- **role** — Who is responsible for this?
- **reason** — Why is this step needed?
- **dependency** — What information must exist first?
- **difference** — Why are these two things separated?
- **failure** — What breaks if this is skipped?
- **boundary** — When does this rule stop applying?
- **prediction** — What do you expect to happen next?
- **connection** — How does this affect the next layer or step?

Examples:

- `点击：Compiler 到底需要看到什么？`
- `点击：为什么 Reviewer 不能只复用生成者的判断？`
- `点击：如果这一步没有写入 Context，下一轮模型还能使用它吗？`
- `点击：这两个概念看起来很像，真正不同在哪里？`

Avoid trivia and vocabulary quizzes such as “这个缩写是什么意思？” unless the term itself is the learning target.

A hidden answer should usually be 1–4 short sentences. It should resolve one obstacle, not open a new lecture.

### 5.2 Use a question ladder, not random questions

When a page contains several sub-points, order the hidden questions so each answer prepares the learner for the next idea.

Preferred pattern:

`看图 → 猜一个关系 → 点击揭示 → 加一个条件 → 再问一个问题 → 点击揭示 → 得到完整模型`

For a causal concept:

`发生了什么？ → 为什么？ → 如果缺一步会怎样？`

For a component concept:

`谁负责？ → 它需要什么？ → 它把什么交给下一层？`

For a rule:

`规则是什么？ → 为什么这样定？ → 边界/例外是什么？`

Do not dump all questions at the bottom of the page. Embed them beside the relevant concept.

### 5.3 Separate micro-questions from the final checkpoint

Micro-questions are **teaching scaffolds**. They help the learner discover the explanation while reading.

The final Checkpoint is **retrieval/application**. It asks the learner to use the completed mental model without immediately revealing the answer.

A strong page therefore has both:

- hidden micro-questions during the explanation
- one final checkpoint after the explanation

When the checkpoint is interactive multiple choice, provide immediate feedback after selection.

## 6. Preserve completeness by adding pages, not density

When an important information point does not fit cleanly on an existing page, create another page.

Do not solve page-count pressure by:

- shrinking text
- merging unrelated concepts
- removing exceptions
- dropping conditions
- hiding important rules in long paragraphs

The visual page stays simple; the module stays complete.

## 7. Coverage verification

Before finalizing, compare the generated module against the information-point checklist.

Verify all of the following:

- every important information point appears on at least one page
- every important source rule, condition, exception, and relationship is preserved
- prerequisites required for understanding are covered
- source anchors are correct where available
- repeated information is minimized
- each major knowledge point has an appropriate hidden micro-question/reveal when useful
- micro-questions form a coherent discovery ladder rather than trivia
- each page has a final checkpoint distinct from its reveal questions
- page order forms a coherent learning path
- `index.html` links to every page
- every content page links back to `index.html`
- the main Study return point is preserved

If any checklist item is missing or only partially represented, revise the page plan or add another page before finalizing.

Do not declare the module complete until coverage verification passes. Also run `presentation-qa.md` on the module: check diagram semantics, interactive rules, page links, readability and source safety. Record the exact checks and limitations. A runtime or visual check that could not execute remains BLOCKED/NOT_RUN, not PASS. When only static checks are possible, label the delivery as statically checked with runtime/visual verification pending; it must not be called fully verified. Known content/interaction failures must be fixed or the affected interaction removed in favor of an accurate static explanation before delivery.

## 8. Learning-state behavior

`/study-d` is a temporary deep-learning branch.

It must:

- preserve the current scope/chapter and Unit position
- record module generation/QA and page delivery separately; “module delivered” never means “topic understood”
- update LP learning evidence only from actual learner answers plus rubric, outcome and misconceptions; reveal clicks are teaching interactions, not comprehension evidence
- return the learner to the same main-path Unit afterward

It must not automatically advance `/study-n` progress. Record `deep_branch` with module ID, LP IDs, ordered artifact IDs (index first), `generation_complete`, `qa_passed`, `delivery_cursor`, `next_page`, and `main_return` (scope/Unit). Each artifact needs an ID/revision, verified real reference, availability and provenance. Save the original main return before entering the branch and preserve it throughout.

A pending-branch `/study-n` must be resolved deliberately under `state-commands.md`: continue the next deep page or explicitly pause/return, never silently skip to a new main Unit. After the final page, offer returning to the saved Unit; do not advance it automatically.

## 9. Output behavior

When file/HTML artifact creation is supported, generate the complete module first and finish coverage verification before surfacing page links.

Create one folder containing all module pages and make `index.html` the navigation entry point. The HTML files may remain together in one folder or bundle so their internal links work.

### 9.1 Link delivery protocol — mandatory

Do **not** present multiple module pages in one assistant message/session. A native single-page attachment is equivalent to a page link on attachment-based hosts.

Surface the generated pages as separate delivery messages/sessions in reading order. A delivery session is one learner-visible response containing one page link, not a claim that the host can autonomously create a new chat session:

1. Session 1 → `index.html` only.
2. Session 2 → first content page only.
3. Session 3 → second content page only.
4. Continue one page per session until every generated content page has been surfaced.

Each delivery session must contain:

- one short page label, such as `Page 2 · How it works`
- exactly one accessible page: a clickable HTML artifact link or supported native single-page attachment

Do not include links to any other module page in that session's chat message. Navigation between pages belongs inside the HTML itself.

Do not replace individual page delivery with:

- one message containing a list of all links
- one download-only ZIP link
- one index link followed by all child links in the same message
- a Markdown table of page links

The learner should experience each page as a separate learning step/session, while `index.html` remains the overall map.

### 9.2 Generation and delivery are separate phases

Generation phase:

`information checklist → page plan → generate all HTML → coverage verification`

Delivery phase:

`index session → page 01 session → page 02 session → ... → final page session`

Never start link delivery before coverage verification has passed. Also verify the actual page links resolve in the delivery surface: sibling relative links require a supported folder/bundle or valid Library references. Do not invent public URLs for local files. If rendering/link publication is unavailable, report that limitation and use the permitted visual fallback; a download-only ZIP does not replace the page protocol.

### 9.3 Host-limited continuation and recovery

If the host cannot autonomously create the next session, send only the current page (initially the index), invite the learner to say “继续”, persist `next_page` and `main_return`, and STOP. Wait for the learner's continuation before delivering the next page. Do not auto-loop messages, schedule artificial continuation, collapse multiple page links, or claim all pages were delivered because they were generated.

On an explicit continuation within the branch, read the saved cursor, verify the next artifact's availability/revision, and deliver exactly that page. Advance `delivery_cursor`/`next_page` only after host-accepted delivery of the verified accessible page/reference; reconcile uncertain sends before retrying. If an artifact disappeared, restore/regenerate and QA the affected material before delivery, preserving provenance and the main return point. No navigation step marks LP understanding.

The full module remains generated, coverage-checked and presentation-reviewed before this paced delivery begins. Declare any unexecuted presentation checks as specified in §7; do not mislabel them as passes. Host limits change delivery timing, not the original content-completeness requirement.

If the host cannot create HTML files, preserve the same one-learning-step-per-session behavior using separate visual responses rather than collapsing the module into one long response.

## V3.1 teaching quality within the existing page contract

Use `unit-teaching.md` for narrow confusion diagnosis and controlled contrasts; retain hidden micro-questions and the existing one-page delivery protocol. When a page uses an interactive model, its learner reflection prompt must remain in the active view, separate from the reference explanation. Add verified local source anchors where useful. Do not add pages merely to force every teaching technique into every module.

Before surfacing hidden micro-questions and final Checkpoints, apply `review-quiz.md` question preflight. Progressive disclosure is not permission to hide essential premises or ask about unexplained tools.

## Adaptive delivery and observable outcomes

Complete module generation still precedes paced delivery. Before surfacing the next page, check only whether newly observed learner gaps materially affect that page. Add a bounded bridge or revise affected future pages when needed, preserving unchanged pages, LP IDs, the main return point and prior evidence. Recheck changed pages and their affected coverage/links; do not regenerate the whole module merely because a preference changed.

One delivered page may be a supported native attachment, rendered page or verified HTML link. If no HTML delivery mechanism exists, use the existing one-step visual fallback and disclose that format; a ZIP alone still does not replace paced teaching. Host tool acceptance plus a valid accessible artifact/reference is the delivery event. Do not infer opening, reading or mastery. A failed/uncertain send does not advance the cursor; reconcile what the host actually reported rather than waiting for unavailable read receipts.
