# Study V6 Runtime

Main interfaces:
- `v6_agent.py`: LLM-deciding Manager with dynamic allowed actions, G1–G6 Host checks, isolated workers, targeted revisions, persistent receipts, explicit user outline approval and one-link delivery.
- `v6_ops.py`: `/study-n`, `/study-e`, `/study-q`, `/study-c`, `/study-m` user commands with review, state and output validation.
- `study_runtime.py`: retained V5 source/parser, planner, tutor, independent reviewer, content/fact renderer, browser and publication primitives. It is an internal Host layer, not the user-facing V6 orchestrator.
- `preview_renderer.py`: two source-anchored acceptance HTML pages for Chapter 8. This preview does not exercise live model API calls.

The authoritative Windows setup and CLI commands are in `../README.md`.

The full command path requires `STUDY_API_BASE`, `STUDY_API_KEY`, and `STUDY_MODEL` and available Chromium. Only explicit real API tests can certify model quality. Fixture/mock tests exercise Manager tool dispatch without calling a provider; the model-authored first two pages have real HTML browser validation but no live-manager review receipt.

Deep modules should use `--topic` and a nested `--workspace` with `--parent-workspace` to register their pages for future `/study-c` consolidation. Source scope is pinned by headings/line ranges and full-source fingerprint; an ambiguous topic must be narrowed before execution.
