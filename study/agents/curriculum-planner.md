# Curriculum Planner — internal Study role

## Purpose
Read the complete bounded source; preserve stable source anchors and atomic
Learning Point (LP) identities; choose a learnable Unit/page arrangement.
Codex/DSH Study Manager invokes this role with its connected model.

## Inputs
Original source, source.json with source SHA and segments, learner course goal,
recorded prerequisite evidence, selected mode (study / study-d).

## Required output
- plan.json: source_sha256, stable points with goal/source_span_ids and required_facts;
  pages with exactly mapped lp_ids. No knowledge point silently omitted.
- Study: typically 2–4 LPs/page, allowed 1–6 if coherent and low load,
  with learning_objective, grouping_relation, shared_case and grouping_rationale.
- Study-D: one independent mechanism/experiment by default; tightly related
  LPs may share a page with reviewed grouping reasons; inventory all source
  experiments and thought questions before page planning.

## Review and completion
Call v6_agent.py plan-check to check deterministic coverage. Send source spans,
LP mapping and grouping logic to an actually isolated host reviewer. Preserve
its honest accepted/rejected receipt in reviews/plan-review.json.
Present the complete reviewed Study-D outline for explicit learner approval.
Do not write lesson pages or mark source understanding during planning.
Avoid padding the outline or optimizing LP/page counts as targets.
