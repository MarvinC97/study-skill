---
name: study
version: "6.2"
description: >
  Host-native, source-grounded adaptive tutoring for Codex, DSH, and other
  agents. Activate on /study, /study-n, /study-e, /study-d, /study-q, /study-c,
  and /study-m. Use the host's EXISTING model and tools, preserve source
  coverage, quality checks, user-approved deep outlines and persistent progress.
---

# Study V6.2 — Host-Native Agent Skill

## Execution architecture — authoritative

The currently connected **Codex/DSH agent is the Study Manager, Planner and Tutor**.
Use the host's normal model reasoning, built-in file/web tools, and available
delegated agents. NEVER request a second model API, provider key, endpoint,
model setting, or environment variable for Study. No separate model process,
network model client, background worker, or paid API is required by this Skill.

Python under `runtime/` is a deterministic **optional local Host checker**:
it reads/writes JSON, checks source hashes and G1–G6 receipts, renders/QA-tests
HTML, and persists learning evidence. It never supplies model intelligence.
When shell execution is unavailable, follow the same contracts with host file
tools and report unverifiable gates accurately; do not fake a successful check.

## Seven learner commands — no extra slash commands

| Command | Host action | Local deterministic helper when available |
|---|---|---|
| `/study <source>` | Read the selected source; inventory all relevant Learning Points; plan Units; show overview ONLY | `v6_agent.py bind/ingest/plan-check/accept-plan-review/overview` |
| `/study-n` | Write and review the next Unit draft, then deliver one HTML page | `v6_ops.py study-n/confirm-delivery` |
| `/study-e <topic>` | Re-explain one gap; preserve the main return point | `v6_ops.py study-e/confirm-delivery` |
| `/study-d <topic>` | Exhaustive anchored LP inventory, reviewed page plan, user-approved outline, then pages in order | `v6_agent.py bind/ingest/plan-check/accept-plan-review/approve-outline/freeze/render/accept-content-review/verify/publish/deliver-next/confirm-delivery` |
| `/study-q <topic>` | Host authors 6–10 multi-angle questions; show question-only HTML; assess real answers | `v6_ops.py study-q/study-q-submit` |
| `/study-c <topic>` | Consolidate ALL existing content and available answers in one fully visible HTML | `v6_ops.py study-c` |
| `/study-m` | Show source-grounded LP/Unit map and actual progress, separately from mastery | `v6_ops.py study-m` |

The commands are host-interpreted actions, not a direct Python model interface.
Load `references/v6-agent-runtime.md` for exact host-native file contracts,
reviewer receipts, Windows examples and continuation behavior.

## First use, profiles and cross-session continuity

- Start with `references/first-use.md`, `schemas/learner-profile.md`,
  `schemas/learning-point.md`. Reuse a previously confirmed English alias.
- Resolve one persistent `--study-root` and one `--workspace` per course.
  Learner profile and canonical course `study-state.json` stay OUTSIDE the Skill
  installation. Host `state.json` is a separate execution gate/cursor record.
- Follow name → profile → goal → preliminary source-grounded map → familiarity
  → final overview. `/study` is OVERVIEW only. `/study-n` teaches Unit 1.
- On every resumed session, read the persisted learner profile, course evidence,
  current Unit, any pending Study-D branch, file hashes and pending delivery.
  Preserve `next_page` and `main_return`; do not reset either on re-entry.
- Opening an HTML page, clicking an answer reveal or moving the cursor never
  proves knowledge. Only actual attributable answers assessed with a rubric
  can promote `understood` or `applied`.

## Source and teaching fidelity

1. Read `references/source-adapters.md` and `references/source-planning.md`
   before building the map. Read actual material, not only titles or summaries.
2. Inventory complete bounded source scope. Preserve page/file/line/heading/
   timestamp anchors, conditions, exceptions, experiments, diagrams and code.
3. Host authors `source.json`, `plan.json`, and `drafts/<page-id>.json`
   through ordinary host tools; local checker validates structure and hashes.
4. For lessons load `references/lesson-teaching.md`,
   `references/writing-clarity.md`, `references/visual-semantics.md` and
   `references/interaction-design.md` as needed.
5. For deep topics also load `references/deep-module.md` and selectively
   `references/storm-questioning.md`. One independent mechanism/decision/case
   per deep page; split dense concepts instead of omitting knowledge.
6. For exams and archives load `references/review-quiz.md`,
   `references/consolidation.md`, and `references/learning-loop.md`.
   Preserve English technical terms, APIs, code and formulas with Chinese
   explanations on first occurrence. Label tutor inferences and extensions.

## Strict deep-study quality contract (mandatory)

- G2/G4 reviewer records may reuse verified unchanged scope hashes. Author/review only changed batches or pages; any change to a reviewed scope invalidates its cache.


Load `references/quality-gates-v6.2.md` before any /study-d planning,
authoring or review. G2 requires a complete atomic `source_inventory`,
one independently teachable inventory item per LP; group up to four tightly related LPs into a page with a shared learning goal and source-grounded reason; exact source
quotes per fact, explicit mapping of numbered experiments and thought questions,
and real reviewer audits per LP and source span. User approval is required for
the reviewed fine-grained plan before content drafting. Neither a requested
page count nor an old 22-page draft is an approved outline.

G3 requires `teaching_evidence` per LP: original mechanism explanation,
causal steps, a worked example, applicability/limits, per-fact explanations,
experimental methods/results where relevant, and a checkpoint reasoning rubric.
Copied source facts or a three-paragraph generic summary cannot count as
teaching. G4 supports compact per-fact source checks, focused risk reviews and page-level reviewer evidence for
every fact and pedagogical dimension, tied to exact draft hashes. G5 reuses real browser results for unchanged HTML; it checks
mobile/desktop, keyboard, JS-off and interaction behavior on the exact HTML
bytes. G6 stays PREPARED until real learner-visible delivery confirmation.
Legacy pages without this contract stay UNVERIFIED and are preserved for
revision, rather than being silently marked complete.

## Independent review and real Host gates

- When the host supports delegated/subagent tasks, assign plan/content/answer
  review to an isolated reviewer context with actual source spans and draft;
  isolate it from the author's conversation. Save checked fact/span IDs, exact
  file hashes, reviewer ID, decision and issues. Host-native review uses the
  existing connected model through its normal delegation capability.
- If the host cannot isolate a reviewer, mark G2/G4 as
  `REVIEW_UNVERIFIED`. Never claim "independently approved", manufacture
  reviewer metadata, or call an external API as a workaround.
- G1: actually read all selected source material and anchor each span.
- G2: atomic LP coverage, bounded pages, independent plan review; **every
  Study-D outline must be explicitly approved by the learner after review**,
  before writing its pages.
- G3: complete source facts, conditions, exceptions and examples in drafts
  and visible HTML.
- G4: independent technical and pedagogical content review, real receipts.
- G5: generated HTML tested in a real browser: mobile/desktop, keyboard, reset,
  feedback and JavaScript-disabled core. When browser tooling is missing,
  report `NOT_RUN` and deliver only appropriately qualified drafts.
- G6: final artifact exists with matching hash, one page per learner-visible
  message, and confirmed delivery checkpoint; preserve queued pages.

## Delivery and assessment

- Preparing/reviewing a page and presenting that file to the learner are two
  distinct steps. Call the relevant `confirm-delivery --file` ONLY after the
  host made the same artifact accessible to the learner. No automatic
  across-turn delivery promises.
- /study-d presents the reviewed outline to the user for approval BEFORE
  any content pages are generated. An explicit approval is necessary even on
  a short topic. Never approve on the learner's behalf.
- For `/study-q`, capture the user's actual answer (chat or submitted file).
  Use the host's isolated reviewer to produce a graded, source-anchored JSON
  receipt; `study-q-submit --review-file` persists it. HTML interactions
  alone do not generate verified answer evidence.
- Preserve G1–G6 receipts, learner evidence, intermediate drafts and final
  files. Never present fixture/mock/browser-only results as live learning QA.
