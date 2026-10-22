# Visual Output

Read this for Study overview pages, every standard learning Unit, and Study-E pages. The default experience should resemble a visual explainer, not an essay.

## Preferred format

When the host can create or display HTML, ALWAYS create a self-contained HTML learning page. Use `../assets/overview-template.html` for the initial Study overview and `../assets/unit-template.html` for Units.

When HTML is unavailable, reproduce the same information hierarchy in compact Markdown using diagrams, arrows, boxes, and short blocks.

## Visual principles

- One main idea per screen/section.
- Prefer 1–3 short sentences over paragraphs.
- Choose diagrams when they make the relationship easier to inspect; use clear text for simple ideas. Read `visual-semantics.md` for arrow and relationship rules.
- Use large labels and obvious direction of flow.
- Reveal technical depth progressively.
- Keep the current location visible: `Scope/Chapter · Unit · Topic`.
- Use whitespace aggressively.
- Use examples as part of the visual flow.
- Keep technical terminology visible in both learner language and source language when useful.

## Unit page order

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
- No dense article-width text walls.
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
