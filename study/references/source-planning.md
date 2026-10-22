# Startup sequencing note · V3.4

For a new learner/course, follow `first-use.md` before finalizing the route. Knowledge inventory first produces a preliminary map used to ask about relevant prerequisites and target familiarity. After that answer (or explicit skip), adjust and save the final overview. Do not generate formal Unit 1 merely because the source is available. Existing routes and legacy state are preserved.

# Source Planning

Read this only after the current source has been loaded/normalized, or when starting a topic-only course, book, chapter, or substantial section.

## Goal

Before teaching, inventory the complete bounded ACTIVE learning scope and divide it into learnable Units based on information density, concept dependency, and cognitive load. The first `/study` output is an overview only.

## 1. Read the full relevant scope first

Use the normalized actual source as the authority. If extraction is still needed, return to `source-adapters.md`.

First record the active scope boundaries (chapter, substantial section, or named topic), its source revision and extraction gaps. “Complete” means all of this active scope, not an unbounded entire book/repository. If only part of the scope is accessible, disclose the gap and mark inventory incomplete rather than claiming full coverage.

Identify all important learning points in the requested scope:
- concepts and definitions
- mechanisms and causal relationships
- rules, conditions, boundaries, and exceptions
- examples, experiments, code, formulas, diagrams
- terminology the learner must recognize
- prerequisites the source assumes
- dependencies between learning points
- distinctions that are easy to confuse

Preserve source anchors such as page, file, section, or timestamp when available. Do not invent unsupported points.

Before finalizing LP objectives, translate the learner’s stated purpose into an observable chapter goal and criterion scope under `learning-loop.md`. Relevant earlier course evidence may reduce repeated teaching, not silently erase current source coverage.

## 2. Build a complete learning-point inventory

Create an internal checklist of every important learning point before splitting Units. Persist it in the one per-course `study-state.json` using `../schemas/learning-point.md`, not a second checklist database.

Each LP must carry a stable ID, observable learning objective, source anchors and source revision, hard/soft prerequisite IDs, common misconceptions, a main representation specification (visual when useful, concise plain text when clearer), and a check type. Retain original English terminology/code with Chinese explanation. Allocate identity independently of source revision and Unit ordering.

Classify hard prerequisites (needed to proceed) versus soft prerequisites (useful context that may be postponed). A missing hard prerequisite receives a bounded mini-Unit; do not expand into an unrelated introductory course.

The checklist is the coverage authority for the standard Study route. A learning point may be simplified or postponed inside a Unit, but it must not disappear from the route.

## 3. Split by information density

Group the learning points into Units. Do not use source headings or a fixed Unit count as the main split rule.

A Unit is the largest chunk that can still be learned comfortably in one sitting.

Split when any of these rises too high:
- number of new concepts
- number of causal steps
- number of conditions/exceptions
- prerequisite burden
- code/math density
- number of concept comparisons
- amount of source evidence required

Group adjacent points when they form one inseparable mental model; grouping does not merge their LP identities. Units and LPs, and artifacts and LPs, are many-to-many. Reordering/regrouping Units preserves LP IDs. A genuine LP split/merge gets explicit old-to-new identity mappings and a reason; reassess transferred evidence instead of copying mastery automatically.

Typical result:
- low-density scope: 2–4 Units
- medium-density scope: 4–8 Units
- high-density scope: 8–15+ Units

Use as many Units as the source needs. Completeness and learnability determine the count.

## 4. Order by dependency

Teach prerequisites before dependent ideas when needed, even when the source order differs slightly.

Illustrative teaching order only:
`tokens → attention intuition → Q/K/V → KV Cache`

This is neither a universal hard-prerequisite chain nor a causal graph. Justify each actual dependency against the LP objective and source; intuition may precede mathematical detail without making that detail a hard prerequisite.

Insert only the prerequisite depth needed to continue, and keep the original source relationship visible.

## 5. Unit contract

Each Unit should have:
- one clear learning objective
- a small set of tightly related learning points
- a coherent mental model or mechanism
- explicit source coverage
- a clear bridge to the next Unit

Avoid Units that are merely arbitrary page ranges or equal-sized slices.

## 6. First `/study` output: Overview only

After planning, send a visual overview and STOP. Do not teach Unit 1 in the same response. When HTML is supported, use `../assets/overview-template.html` as the base.

The overview should show:

1. **What this scope teaches** — 3–7 concrete outcomes.
2. **Big picture** — one visual map of how the main ideas connect.
3. **Unit route** — Unit 1…N with short titles and 1-line learning goals.
4. **Density / difficulty cues** — mark dense Units only when useful.
5. **Coverage signal** — state whether the bounded active-scope inventory is complete; disclose inaccessible/unread portions and their route gaps instead of claiming completeness.
6. **Progress** — `0 / N Units delivered` for a new route, or preserved actual progress when resuming. Show assessed learning separately.
7. **Next action** — `/study-n` starts Unit 1.

Keep the overview easy to scan. It is a map, not a mini textbook.

## 7. Large books or repositories

For a whole book, first create a compact book-level map from the accessible structure, clearly marking uninspected content. Do not imply every chapter has already been fully read or inventoried. When the learner enters a chapter or substantial section, inventory that scope and split it into Units using the same rules.

Do not flatten the entire book into hundreds of Units at once unless the source is small enough to remain navigable.

## V3.1 plan only useful teaching choices

Use existing LP `main_visual`, `check_type`, source anchors and misconception fields to note a useful primary representation, likely confusion and possible contrast/check. These are hypotheses to revise from learner responses, not compulsory components or new metadata collections. Prefer one meaningful comparison or interaction over decorative controls. Do not require a diagnostic interview before every Unit.

## V3.2 learner-aware planning

Use `learner-adaptation.md` for startup and adaptation. Link each current objective to the prerequisites actually needed for that objective; record a short reason for a hard/soft distinction when it changes the route. Related knowledge is not automatically a prerequisite. Source-supported scope remains intact: adapt order, chunk size and support, not truth or required coverage. Keep postponed content visible.

Read the relevant learner background and current LP evidence before choosing an entry point. Self-reported familiarity can guide pace without becoming demonstrated mastery. A domain change warrants only a relevant check when needed. Do not recursively build a prerequisite curriculum: supply the smallest bridge needed, preserve the return point, and offer a separate route only if the gap genuinely changes the learning goal.

Choose an evidence-producing action appropriate to the objective: explain a mechanism, perform/trace a procedure, interpret/translate a representation, use a term in context, or justify a judgment. This is a heuristic, not a mandatory category taxonomy or requirement to add an exercise to every block.
