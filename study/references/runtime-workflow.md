# Study V6 Host gate contract (load when local execution is available)

The user-facing orchestrator is `runtime/v6_agent.py` and `runtime/v6_ops.py`; `runtime/study_runtime.py` supplies source, plan, review, HTML, and browser primitives. See `v6-agent-runtime.md` for the decision loop.

## Stages / evidence

| Gate | Required outputs | Fail closed on |
|---|---|---|
| G1_SOURCE | `source.txt`, `source.json` (SHA256, complete extracted text, bounded anchored segments) | unreadable source, missing actual text |
| G2_PLAN | `plan.json` → static plan audit → independent `plan-review.json` → user approval on dense source → `frozen-plan.json` | unmapped source spans, LP covering >1800 source chars, LP spanning headings, >1 LP/deep page, unapproved plan |
| G3_CONTENT | `drafts/Pxxx.json`, `draft-pages/*.html`, `content-manifest.json`, `content-static.json` | missing fact ID, missing section/example, required fact removed from HTML |
| G4_REVIEW | `reviews/content-review.json` from separate reviewer context | factual/semantic/pedagogical rejection, missing checked fact IDs |
| G5_BROWSER | `reports/browser.json` | absent browser test, broken reveal/checkpoint, mobile overflow, broken static reading |
| G6_DELIVERY | `published/*.html`, `delivery-queue.json` | any prior gate failed or missing output |

## Mandatory roles

- Source Reader: exact source, stable hash, page/line anchors, no hallucinated inaccessible content.
- Knowledge Planner: atomic Learning Points; independent algorithm, experiment, limitation or failure case should have separate LP / deep page.
- Plan Reviewer: a **new** LLM request with independent system prompt and source/plan input, not the planner self-approval.
- Content Writer: generate detailed JSON content meeting each frozen page's required fact IDs, not compressed prose.
- Content Reviewer: a **new** LLM request with direct source excerpts + content and contract; check all facts semantically.
- HTML Builder: deterministic encoding from reviewed JSON; preserve all fact text in visible HTML and a separate locally placed mini-question.
- Browser QA: actual Playwright evaluation (DOM, click, keyboard, mobile, JS-off core); static link checks run separately.
- Manager: owns state, retries/rejections, approval and delivery; a model's self-report does not override a gate.

## Commands and state

`/study`: ingest + planning + two plan audits + `overview` visual HTML **only**; no Unit 1. Use `run --mode study`.
`/study-n`: advance frozen Unit cursor only after delivery. Show one Unit.
`/study-e`: re-explain local LP, preserve return point, link extra artifact.
`/study-d`: use `run --mode study-d`, then strict frozen atomic LP → page contracts and question ladder; index and each page delivered separately by `deliver-next` across user turns. Never send all links in one response.
`/study-q`: 5+ question complete exam; do not display answer key on initial output. Independent validity review of ambiguous items.
`/study-c`: one fully expanded static HTML; all fact text, hidden minianswers, checkpoint solutions, available exam keys, user feedback and unique explanations visible without JS.
`/study-m`: render current source-grounded LP graph and uncovered state.

`/study-d` and `/study-e` do not change main `/study-n` pointer. `delivered`, `attempted`, `understood`, `applied` are separate recorded facts; page views/expansions are not mastery evidence.

## Reader boundaries

`runtime/study_runtime.py` directly supports UTF-8 Markdown/TXT/SRT/VTT/HTML/DOCX, plus text PDFs with PyMuPDF optional; remote raw text via HTTPS. Host source adapters handle full GitHub repo walking, scanned PDFs, video/audio transcription, figure extraction and other formats; provide a readable anchored materialized file to runtime. For content with unparsed figures or missing transcripts, flag source incomplete. The runtime is designed for a Windows local host; no WSL or DeepTutor installation needed.

## Operations

For full local execution with a compatible model API, see `README.md` and `runtime/README.md`. For large chapters, independent outline approval is mandatory: run `plan`, `review-plan`, show plan to owner; after explicit approval run `approve-outline`, `continue-run`. Do not automatically retry the entire task after that approval checkpoint.

Use `deliver-next` only for one separate user-visible message each time. A local CLI call cannot itself create independent future chat sessions; the host must handle delivery between turns.

## Limitations

A deterministic coverage check confirms required source spans and fact IDs are represented, not that paraphrases are semantically correct. That is the separate reviewer's job. All synthetic/example test output must be labeled as such. Claims of complete end-to-end quality require a live provider test on the requested full chapter plus browser QA.
