# Study V6 changes

- Added an LLM-directed Manager step loop (`runtime/v6_agent.py`), persisted event log, allowed-tool gates, bounded repairs and explicit outline approval stop.
- Added `/study-n`, `/study-e`, `/study-q`, `/study-c`, `/study-m` executable operations (`runtime/v6_ops.py`), building on the V5 source/contract system.
- Retained V5 source span mappings, atomic LP checks, content facts, isolated reviewer calls, browser test and state persistence.
- Raised configurable model completion token budget; narrowed plan-review context to source-relevant pages to reduce truncation.
- Added a self-contained, source-anchored, two-page Chapter 8 review preview with scenario selection, numeric Loss slider, hidden questions, interactive checkpoint and reset.
- Added real browser preview tests and Manager Host boundary/targeted-repair tests. Unit tests exercise fake/model-stub decisions; real model-driven execution is pending provider credentials.

## Review sample scope

Preview 01 = four-phase Pre-training/Mid-training/SFT/RL model.
Preview 02 = Next Token Prediction, token distribution, Loss and parameters.
Source: bojieli/ai-agent-book book/chapter8.md blob SHA 38eb64bf45b9e844b6bdbcbedfc61b9dcc12244b. Full chapter is not reproduced in the preview; its content contract covers only those two pages.
