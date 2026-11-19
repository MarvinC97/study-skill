# Visual Output

> **Study 6.6 B-mode visual authoring:** Read the completed teaching manuscript before implementing HTML. Convert its meaningful causal and quantitative relations into visuals using the same objects and labels; retain the complete explanation. A causal diagram should expose meaningful intermediate changes; an experiment should compare true source-reported conditions and results; an interactive calculator must recompute and explain the observed value. A simple concept can use a clear paragraph. Keep figures near their causal explanation, and show key teaching directly. Reviewer checks the finished visible page rather than confirming a component type.


Read this for Study overview pages, every standard learning Unit, and Study-E pages. Use visual explanations when they make a relationship clearer; a coherent explanation remains essential.

## Historical V6.4 visual representation contract (legacy only)

Read `lesson-design.md` before creating a new page. Select the representation
that exposes the concept's causal or quantitative relationship: process,
decision, experiment table, formula, timeline, comparison or a focused
concept map. A source-grounded diagram must label transitions and their
meaning. Simple concepts may use text when clearer. The current
`lesson_render.py` renders the reviewed specification; full source
citations are in a separate expandable audit layer. Verify mobile/desktop,
keyboard native disclosure, Checkpoint feedback and JS-disabled core in
actual Chromium. A diagram that merely repeats a list of terms fails the
teaching design review.

## V6.6 direct HTML: content-led visual authoring (takes precedence)

For plans with `render_contract: direct-html-v1`, the Teaching Author owns
the complete lesson manuscript; the Visual Builder owns its HTML visual
implementation and reading order. The builder reads the saved manuscript
before coding CSS, SVG or JS. The V6.4 renderer and older
card-template guidance elsewhere in this file apply **only to legacy plans**.
An accepted template or sample is an *optional visual quality reference*,
not a page-layout requirement. Inspect an accessible learner-approved sample
to learn its hierarchy, diagram semantics and pacing, then design for the
current source. Never copy its factual content into another course.

Choose a visual because it exposes something the reader otherwise must infer:
- **System composition:** clear roles, inputs/outputs and the payload between
  components.
- **Causal or training process:** meaningful intermediate change, signal
  and result; labels must match the adjoining explanation.
- **Numerical or token-level mechanism:** show concrete values, aligned
  input/output positions, calculations or before/after probability.
- **Controlled experiment:** pair actual conditions with actual observed
  outcomes and state the limits of comparison.
- **Decision/failure:** depict real alternative paths, first error and
  downstream consequences; a linear chain must not masquerade as a tree.

Begin with a clear question and an accessible entry point. Put explanatory
graphics directly beside the mechanism they illustrate. Build explanations
in readable sections with enough room for a complete reasoning chain.
Avoid forcing 1–3 sentence limits, a fixed number of figures, a fixed
WHY/INTUITION/MECHANISM card sequence, or mandatory interactions.
Questions generally follow the teaching needed to answer them. Core prose,
key diagram meanings and worked calculations remain visible by default.

A source-faithful **text-only** paragraph is appropriate when a visual
would add little. A rich layout with attractive cards but no inspectable
relationship needs revision. Keep exact technical terms in the figure and
body; distinguish learner-authored hypothetical data from original reports.

## Preferred format

When the host can create or display HTML, create a self-contained HTML page. For **legacy V3–V6.5** plans, `../assets/overview-template.html` and `../assets/unit-template.html` remain available as optional starting assets. For `direct-html-v1`, first complete the separate teaching manuscript,
then implement the page's explanation and visual layout.

When HTML is unavailable, reproduce the same information hierarchy in compact Markdown using diagrams, arrows, boxes, and short blocks.

## Visual principles

- One main idea per screen/section.
- Use readable paragraphs or short blocks as the mechanism needs; preserve every necessary inference step.
- Choose diagrams when they make the relationship easier to inspect; use clear text for simple ideas. Read `visual-semantics.md` for arrow and relationship rules.
- Use large labels and obvious direction of flow.
- Reveal technical depth progressively.
- Keep the current location visible: `Scope/Chapter · Unit · Topic`.
- Use whitespace aggressively.
- Use examples as part of the visual flow.
- Keep technical terminology visible in both learner language and source language when useful.

## Historical Unit page order (legacy reference; never mandatory for direct-html-v1)

1. Locator + progress
2. WHY
3. INTUITION visual
4. HOW IT WORKS visual
5. concrete example
6. CONNECTION map
7. optional “Easy to confuse” card
8. REMEMBER cards
9. CHECKPOINT

Do not force every Unit to use every card.

## HTML requirements

- Self-contained: inline CSS; no external libraries required.
- Responsive on desktop and mobile.
- Accessible contrast and readable font sizes.
- No decorative animation needed.
- Break genuinely dense passages with meaningful explanations and examples; retain the reasoning rather than deleting it.
- Use semantic HTML where practical.
- Prefer simple CSS diagrams over complex SVG when possible.
- Use `<details>` for optional engineering depth or source notes in normal Units. `/study-c` is the exception: all core content, questions and answers must be visible without disclosure controls.
- Read `writing-clarity.md` for preserved English and clear Chinese.
- Use `interaction-design.md` only when changing conditions reveals a mechanism. Do not confuse reveal buttons with a simulation.
- Apply `presentation-qa.md` to actual output.

## Cognitive-density target

A learner should understand the main visual on first glance and then drill down.

If a block becomes dense, split it into coherent sections or move genuinely optional detail into disclosure controls. Do not enforce English word counts on Chinese or delete essential conditions for brevity. For `/study-c`, split into visible sections instead of hiding content.

## Visual patterns

Use patterns such as:

### Pipeline

`User → Model → Tool → Result → Context → Model`

### Layer stack

`System instructions`
`Conversation`
`Tool results`
`Retrieved knowledge`
`↓`
`Current Context`

### Dependency

Label prerequisite edges explicitly (prerequisite → dependent), and justify them against the learning objective. Do not use an unlabeled sequence of related terms as if it established dependency.

### Before/after

`Before compression: noisy long context`
`After compression: compact task-relevant context`

## Avoid

- long chapter summaries
- walls of bullets
- many unrelated definitions on one screen
- decorative icons that add no meaning
- putting Layer C engineering details into the first explanation
- repeating the same idea as diagram + paragraph + bullet list
