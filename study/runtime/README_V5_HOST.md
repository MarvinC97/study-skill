# Study V5 Runtime (Windows, optional OpenAI-compatible API)

This package upgrades the V4 *prompt-only* Study skill into a fail-closed command-line manager. It adds real source/LP/page contracts, independent LLM review calls, deterministic HTML rendering, Playwright tests, freeze/resume gates, a one-file consolidation operation, and one-link-per-turn delivery queue. It does **not** copy DeepTutor software or require a separate web platform.

## Requirements

- Python 3.11+ (Windows PowerShell, no WSL)
- An OpenAI-compatible text model API for automatic `plan`, `build`, and independent `review` stages (e.g., an authorized DeepSeek API or local compatible endpoint)
- `pip install playwright` and `python -m playwright install chromium` for G5 (or installed Chrome/Chromium via `STUDY_CHROMIUM`)
- `pip install pymupdf` only for text PDFs. Scanned PDF figures / video sources must first be extracted with host tools.

The core runtime uses Python's standard library; the browser and PDF parsers are optional extras. **No API key is included.**

## Windows quickstart

Unzip into a working folder, e.g. `D:\\StudyV5\\study`. Then open PowerShell:

```powershell
cd D:\\StudyV5\\study
py -3.12 -m pip install playwright pymupdf
py -3.12 -m playwright install chromium
$env:STUDY_API_BASE = 'https://api.deepseek.com/v1'
$env:STUDY_API_KEY = '<your key>'
$env:STUDY_MODEL = '<available chat model ID>'
$env:STUDY_REVIEW_MODEL = '<review model ID, optional>'
py -3.12 .\runtime\study_runtime.py run --mode study --source .\chapter8.md --workspace .\work\chapter8
# This generates overview.html only; it never starts Unit 1.
```

For `/study-d` multi-page generation, use `run --mode study-d`. On a **dense source** (more than 12,000 characters or 12 LPs), this stops at G2 for outline review/approval. The plan and source remain intact:

```powershell
# Inspect work\chapter8\plan.json and reports\plan-static.json
py -3.12 .\runtime\study_runtime.py approve-outline --workspace .\work\chapter8
py -3.12 .\runtime\study_runtime.py continue-run --workspace .\work\chapter8
```

`continue-run` renders the frozen plan, runs independent content review, browser QA and publication. The Study host uses the delivery queue to show each page in a separate user turn.

`approve-outline` is an authorization action: invoke only when the learner explicitly approves the current outline. The command checks that the independent plan reviewer approved the exact current plan hash.

To deliver one HTML link per turn:

```powershell
py -3.12 .\runtime\study_runtime.py deliver-next --workspace .\work\chapter8
```

It returns one verified path and advances the saved delivery cursor. Call again only on the user's next request.

To inspect status and merge a topic:

```powershell
py -3.12 .\runtime\study_runtime.py status --workspace .\work\chapter8
py -3.12 .\runtime\study_runtime.py consolidate --workspace .\work\chapter8 --topic "KV Cache"
```

Only matching existing page contents will be merged. The file is fully expanded, with original source facts, mini-question answers, checkpoint solutions, and any verified exam keys found in `work/exams/`.

## Offline diagnostics (no model connection)

```powershell
py -3.12 .\runtime\study_runtime.py demo --workspace .\work\demo
py -3.12 -m unittest discover -s .\runtime\tests -v
```

The demo uses **a synthetic miniature source** and hand-authored JSON. Passing proves parser, gates, deterministic rendering and browser interaction on that fixture. It does not prove live model lesson quality or full chapter coverage.

## How the gates prevent the two recorded failures

1. **Seven-page overcompression**: a full source span map is mandatory; LPs spanning unrelated headings or >1,800 source characters are rejected; in deep mode, every independent LP gets a separate page. The actual count emerges from the material. It is never forced to 7 or 37.
2. **Text-to-HTML omissions**: every LP has `required_facts` with stable `fact_id` and source `span_id`. The writer must explain them in structured JSON; the renderer always renders each exact required fact as a visible source callout. Static verification checks literal preservation; an isolated reviewer checks explanation quality and factual consistency.

## Provider compatibility and limitations

- An OpenAI Chat Completions-compatible endpoint returning valid JSON text is required. Some models need prompt or generation parameter tuning; live compatibility has not been certified in this environment.
- Plan and content reviewers are isolated *calls* with different system instructions and no writer history. They are independent review passes, but may still share model biases, especially with the same provider.
- For large sources, per-batch model extraction prevents silently sending just the first part of a chapter. Source coverage is verified for all recorded spans. Important diagrams, scans and audio still need faithful pre-extraction.
- Browser QA runs Chromium on generated HTML, checking mobile overflow, keyboard reveal, answer feedback, and JS-off core. Navigation target existence is checked statically. This sandbox uses page-content injection for browser testing because direct filesystem/loopback navigation is blocked; ordinary hosts can run the same tests.
- `state.json` and artifacts are saved on disk. This is a local manager, not a background cloud task or full DeepTutor platform.

## Folders created per workspace

```text
work/chapter8/
  source.txt, source.json
  plan.json, frozen-plan.json, owner-outline-approval.json
  drafts/P001.json ...
  draft-pages/index.html, P001.html ...
  reviews/plan-review.json, content-review.json
  reports/plan-static.json, content-static.json, browser.json
  content-manifest.json, state.json
  published/index.html, P001.html ...
  delivery-queue.json
  consolidated/all.html
```

## Research inspirations

Design inspiration only, no DeepTutor code copied:
- HKUDS/DeepTutor Book: reviewed outline before building typed blocks; source fingerprints and health checking.
- Mastery Path: sourced LPs, shared context, distinct evidence of understanding.
- Reading and Dito: source-anchored local explanation and page-specific questions.
- Release 1.6.15/1.7.2: independently graded assessments, recoverable sessions, bounded context and source quote checks.

Upstream: https://github.com/HKUDS/DeepTutor
