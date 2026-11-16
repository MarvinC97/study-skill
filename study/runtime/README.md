# Study V6 Runtime

Main interfaces:
- `v6_agent.py`: LLM-deciding Manager with dynamic allowed actions, G1–G6 Host checks, isolated workers, targeted revisions, persistent receipts, explicit user outline approval and one-link delivery.
- `v6_ops.py`: `/study-n`, `/study-e`, `/study-q`, `/study-c`, `/study-m` user commands with review, state and output validation.
- `study_runtime.py`: retained V5 source/parser, planner, tutor, independent reviewer, content/fact renderer, browser and publication primitives. It is an internal Host layer, not the user-facing V6 orchestrator.
- `preview_renderer.py`: two source-anchored acceptance HTML pages for Chapter 8. This preview does not exercise live model API calls.

This file is the operational reference for the current V6.1 runtime. Install and activate the Skill as described in the repository root `README.md`.

The full command path requires `STUDY_API_BASE`, `STUDY_API_KEY`, and `STUDY_MODEL` and available Chromium. Only explicit real API tests can certify model quality. Fixture/mock tests exercise Manager tool dispatch without calling a provider; the model-authored first two pages have real HTML browser validation but no live-manager review receipt.

Deep modules should use `--topic` and a nested `--workspace` with `--parent-workspace` to register their pages for future `/study-c` consolidation. Source scope is pinned by headings/line ranges and full-source fingerprint; an ambiguous topic must be narrowed before execution.


## Windows setup and local data

- Python 3.11+; Playwright with Chromium for browser QA; optional PyMuPDF for native PDF text extraction.
- OpenAI Chat Completions-compatible API, configured through environment variables `STUDY_API_BASE`, `STUDY_API_KEY`, `STUDY_MODEL` (optional `STUDY_REVIEW_MODEL`). Keep credentials out of the repository.
- Use `--workspace` for each individual course's runtime intermediates and deliverables. Use `--study-root` for the stable external learner profile root. A deep module uses a child workspace and `--parent-workspace` to preserve the original course identity.

```powershell
py -3.12 -m pip install playwright
py -3.12 -m playwright install chromium
$env:STUDY_API_BASE = 'https://<your-compatible-provider>/v1'
$env:STUDY_API_KEY = '<your-secret-key>'
$env:STUDY_MODEL = '<provider-model-id>'
py -3.12 study/runtime/v6_agent.py run --mode study --learner-name Marvin --study-root 'E:\Study-Lab' --workspace 'E:\Study-Lab\courses\chapter8\workspace' --source 'E:\Study-Lab\sources\chapter8.md'
```

Once the first overview is available, follow `references/first-use.md` and finalize the learner intake before `study-n`. For dense `study-d` sources, user outline approval is required before proceeding. A successful command that returns an HTML file path prepares a deliverable; host presentation and explicit confirmation complete delivery.

## Current delivery, recovery and assessment contract

The schema-3.0 `study-state.json` remains authoritative for learner evidence and `learner-profile.json` for cross-course background.

### 1. Study-D branch recovery

`v61_learner.deep_branch(parent, module, topic)` is idempotent for the same
module and topic. Re-entry preserves `next_page`, `main_return`, and branch
status. Attempting to replace an active or paused branch is blocked; explicitly
resolve the branch first. The module workspace must be a child of the course workspace.

### 2. Confirmed delivery (two-phase)

Preparing a file and recording a successful host presentation are separate.

**Standard Unit:**

```powershell
python study/runtime/v6_ops.py study-n --workspace "E:\Study-Lab\courses\chapter8\workspace"
# Host presents the JSON result's exact "file" to the learner.
python study/runtime/v6_ops.py confirm-delivery --workspace "E:\Study-Lab\courses\chapter8\workspace" --file "<exact file from study-n>"
```

**Study-D index and content pages:**

```powershell
python study/runtime/v6_agent.py deliver-next --workspace "<deep workspace>"
# Host presents the exact "file", at most one per learner-facing response.
python study/runtime/v6_agent.py confirm-delivery --workspace "<deep workspace>" --file "<exact file from deliver-next>"
```

`deliver-next` and `study-n` are safe to repeat before confirmation and
return the same pending page. Confirmation verifies the exact file's SHA-256.
Only confirmation advances the durable delivery cursor and learner route.
On failure, inspect and retry the same pending file. Do not call
`confirm-delivery` before actually making the artifact accessible to the user.
After confirmation, the next page is available.

**Supplemental explanation and quiz artifacts:** `study-e` and `study-q`
register generated artifacts with `delivery_status=not_delivered`. Once
presented, call `v6_ops.py confirm-delivery --file ...` to record delivery.

**Host rule:** A command returning a local file path is a *prepared artifact*,
not an automatically verified user-visible delivery. The chat/GUI adapter
must present the file and then explicitly call the confirmation command.
Where no attachment or URL facility is available, retain pending delivery.

### 3. Quiz assessment recording

The exam is produced by `study-q`. Learner answers must be captured from
their actual message or a user-supplied answer document. Write a JSON file:

```json
{
  "topic": "Training",
  "answers": [
    {
      "question_id": "Q1",
      "answer": "My explanation, with conditions and reasons.",
      "assistance": "independent"
    }
  ]
}
```

Then use:

```powershell
python study/runtime/v6_ops.py study-q-submit --workspace "<course workspace>" --topic "Training" --answers-file "<user-answer-file.json>"
```

The independent reviewer receives source-anchored facts, the existing quiz's
question/rubric, and the learner's actual response. It returns a structured
judgment and demonstrated fact IDs. `v61_learner.record_assessment` writes
idempotent learner evidence to canonical `study-state.json`; feedback goes
to `exams/<topic>-feedback.json`. Hinted/after-reveal answers and isolated
option selections are at most attempted evidence. The reviewer must verify
all required facts of the target LP before promoting `understood` or
`applied`. Incomplete or malformed review output fails closed.

The generated standalone HTML does not directly send answers to a local
server. The host must capture the actual answer, submit its JSON file and
report the review. Keep real learner replies and external API credentials
out of public Git commits.

### Verification

The included `v61tests/test_v61_patches.py` uses offline model doubles for
state transitions and answer-evidence contracts. Run:

```powershell
python -m unittest discover -s study/runtime/v61tests -p "test_*.py" -v
python -m unittest discover -s study/runtime/v6tests -p "test_agent_host.py" -v
```

These tests check deterministic control flow. End-to-end provider quality and
Windows Chromium rendering require additional live acceptance tests.
