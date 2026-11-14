# Study V5 Runtime — 2026-11-14

## Preserved from V4
All seven commands, STORM questioning, HTML visual source-anchored lessons, deep pages with local hidden questions, exam, complete single-file consolidation, learning point IDs, state concepts and progressive-disclosure reference files.

## Added
- `runtime/study_runtime.py` executable Python manager and `references/runtime-workflow.md`.
- G1–G6 source → atomic LP plan → plan review + freeze → written content → independent semantic review → actual browser QA → verified output.
- Conservative complete-source extraction with SHA256 and anchored source segments; explicit format boundaries.
- G2 reject rules to prevent giant pages; source-span coverage must be 100%, each deep page exactly one LP.
- Dense-source outline approval gate; page contract with required source facts and independent audit.
- Deterministic HTML generator to preserve source facts; hidden interactive mini-questions and checkpoint feedback.
- Native saved state, delivery queue, consolidated HTML, learner evidence records that distinguish attempted vs mastered.
- Offline test fixtures + 8 integration/contract tests, including rejection of overpacked pages and missing factual content.

## Scope limitations
External model API and valid source are required for live automatic source-to-course runs. Source reader does not provide multimodal extraction of scans/figures or video transcription alone. The V5 offline demo and tests pass; live full-book LLM performance remains unverified until deployment environment and API are connected. Dense-source approvals require user action.
