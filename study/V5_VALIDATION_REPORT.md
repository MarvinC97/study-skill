# Study V5 Runtime Validation (2026-11-14)

## What was actually executed

- V4 skill static check (`tests/validate_skill.py`): PASS (all 7 commands, 14 original references, assets).
- V5 Python runtime tests: 9/9 PASS (source coverage, oversized/merged LP rejection, no source omission, missing content-fact rejection, missing reviewer gate, no false mastery, browser demo, consolidation, tampered HTML rejection).
- Playwright in Chromium on offline miniature source: PASS for three pages. Tests actually click checkpoint options, reveal hidden answers via keyboard, switch preset-state conditions, click reset, check 390px viewport horizontal overflow, and inspect JS-disabled core readability.
- `consolidate` on miniature source: PASS; one self-contained expanded HTML with actual facts and answer key.
- ZIP archive syntax, references and file integrity: verified before delivery.

## Not yet executed / not to be confused with PASS

- Live DeepSeek/Codex-compatible model provider run of a full chapter, as no API credentials are configured in this sandbox.
- Independent LLM reviewer semantic accuracy on the entire chapter 8 source.
- Full real chapter 8 extraction via V5 local runtime and model-driven atomic LP count; seven-page regression is tested with a synthetic overpacked plan.
- Integration with the user's actual Codex UI/session host, including delivery across distinct chat turns.
- Full figures/scan/video/audio extraction. These still require host source adapters.

## Release status

**Runnable V5 candidate**, validated locally for structural gates and real offline HTML interaction; deployment acceptance requires live provider and Chapter 8 end-to-end smoke test. The package is suitable for a Windows Codex host but does not install or launch an unattended external service automatically.

## Source references for design inspiration

- https://github.com/HKUDS/DeepTutor — Book outline review, typed blocks, source health, Mastery Path and Reading.
- https://github.com/HKUDS/DeepTutor/releases — 1.6.15 grouped assessments, sourced answer assessment and recovery; 1.7.2 tutoring reliability.
- https://arxiv.org/abs/2604.26962 — DeepTutor tutoring/personalization research.
