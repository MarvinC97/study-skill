# Study V6.3 — Granularity and Teaching Contracts

These two commands share a complete source-grounded inventory of atomic Learning
Points (LPs), their stable IDs, prerequisites, and the canonical learner evidence.
They choose different **teaching page boundaries**. LP count is a limit, not a
target; never invent or discard LPs merely to hit a page count.

## A. Standard `/study`: a coherent cluster of LPs becomes one Unit page

**Goal:** efficiently build one complete mental model from several related LPs.
A standard Unit is taught and checked in one self-contained HTML page.

**Quantity:**
- Typical: **2–4 related LPs** per Unit page.
- Allowed: **1–6**. Use one when a mechanism is intrinsically dense; 5–6 only
  when the LPs are light and tightly connected, with a genuinely shared example.
- One complex `algorithm`, `experiment`, or `failure_case` normally gets its
  own Unit or combines with at most two light contextual LPs. Two distinct heavy
  objectives require separate Units. The LPs remain independent evidence IDs.
- A complete chapter is composed of as many learnable Units as necessary;
  never enforce a fixed ratio of LP count to pages.

**How to group — all four conditions must hold:**
1. **One assessable objective.** Learners can explain or apply one overall
   mechanism/decision after the page. It cannot be two unrelated questions.
2. **A real structural relationship.** Use exactly one primary
   `grouping_relation`: `causal_chain`, `shared_mechanism`,
   `prerequisite_bridge`, `comparison`, or `same_task_workflow`.
   The relationship must be supported by the source, not only adjacent headings.
3. **One worked case or diagram can connect all LPs.** Record the page's
   `shared_case` as a concrete situation, with `grouping_rationale` explaining
   each connection. The teacher will use ONE full shared causal spine and one
   complete example, then preserve the unique explanation of each LP's facts.
4. **Manageable cognitive load.** Sequence LP IDs from accessible prerequisite
   to application. Prefer one central diagram, ≤1 new main mechanism and
   one primary example. Split when an LP needs a separate formula proof,
   experimental setup, failure analysis, prerequisite detour or independent
   checkpoint. A reviewer explicitly records `cognitive_load_ok` and
   `shared_case_ok` for the grouped Unit.

**Plan page fields for 2+ LPs:**
```json
{
  "page_id": "U003",
  "title": "RL interaction as one loop",
  "lp_ids": ["LP-state", "LP-action", "LP-reward", "LP-trajectory"],
  "learning_objective": "Trace a full environment interaction and predict its next step",
  "grouping_relation": "causal_chain",
  "shared_case": "An agent in a small game observes a state, chooses an action, receives feedback, and records the resulting trajectory.",
  "grouping_rationale": "State, action, feedback and trajectory are successive parts of one observable RL loop that can be explained and checked with the same game."
}
```

**Plan review:** isolated host reviewer checks complete source/LP coverage plus
one `unit_group_audits` entry for each grouped Unit:
`page_id, checked_lp_ids, coherent:true, shared_case_ok:true,
cognitive_load_ok:true, reason`. Validate the exact plan/source hash. A
single-LP Unit needs no grouped-Unit audit. The user receives the overview
only on `/study` and starts Unit 1 using `/study-n`.

**Teach:** one structured `shared_teaching` with `lp_ids`,
`core_explanation`, `causal_steps`, `worked_example`, `conditions` and
`limitations`. Each LP gets its own `teaching_evidence` record with
`lp_id`, `lp_connection`, and original `fact_explanations`.
Use 1–2 local microquestions if helpful, plus one page-level Checkpoint
with a reasoning rubric (1–3 checks total). One reviewer receipt contains
`unit_coherence: {coherent:true, checked_lp_ids:[...],
shared_case_ok:true, cognitive_load_ok:true, reason:"..."}`. Real learner
answers, not clicks, establish LP mastery.

**Examples:**
- Group state → action → reward → trajectory: one causal loop.
- Group the four training stages in a high-level comparative Unit (the
  learning objective is choosing the stage from the *type of deficit*).
- Separate Q-learning derivation from PPO/GRPO derivation; each needs its
  own mechanism and worked check.
- The fact that two items share a heading or appear nearby is insufficient.

## B. `/study-d`: focused deep discovery, retaining V3.5 visual teaching

**Goal:** thoroughly understand a *specific* mechanism, experiment, algorithm,
or failure case — its conditions, causal steps, concrete example, exceptions
and transfer boundary — with progressive diagrams and probing questions.

**Quantity:**
- Default: **one independently examinable core LP per page**.
- When the *relationship itself* is the objective, **2–3 closely connected LPs**
  can share a page; the existing deterministic ceiling remains **4**.
  Grouping requires a reviewed `learning_objective` and
  `grouping_rationale`. A page is split whenever two objectives each need
  an independent derivation, experiment or decision.
- A complex experiment is normally a standalone page. For each numbered
  experiment retain purpose, setup, comparison/control, numeric observations
  when present, result interpretation, and scope/limitations. Link its
  prerequisites in the previous page or in a small contextual block.
- Similar independent failure cases should be analyzed separately, then
  connected by one optional synthesis/comparison page only if that relationship
  needs teaching. Avoid one low-information page for every trivial fact.

**How to split:**
1. Build the full bounded source_inventory before deciding page count;
   preserve source quotes, every major causal statement and the experiment
   and reflection-question registers.
2. Identify the decision/mechanism each LP must teach. Group prerequisites
   only when they are small enough to support the SAME mechanism and worked case.
3. Check whether each LP has different input/output, mathematical derivation,
   counterexample, experimental setup, measurable outcome, or failure boundary.
   Different independent objectives usually imply different deep pages.
4. For each page, create a WHY → intuition visual → real terminology →
   step-by-step causal chain → worked case → conditions/limits →
   hidden predictive microquestions → distinct final Checkpoint sequence.
5. Keep deep microquestions linked to each important LP, reveal progressively
   using native details where practical, and use a transfer/checkpoint that
   tests changed conditions. Use diagrams or interactive simulations only
   where they disclose a genuine relationship.
6. Independently review source coverage, individual experiments and
   reasoning depth using the existing G2-batched / G4 quality contracts.
   Present the reviewed exact page outline for **explicit owner approval**
   before generating any deep content.
7. After approval, create and quality-check pages incrementally (G3–G5)
   or as a complete batch; deliver exactly one page per learner response.
   Advance the deep cursor only on confirmed real user-visible delivery.
   Preserve the original Study Unit return point.

**Chapter 8 example:** For ordinary Study, an RL overview may combine
state, action, reward and trajectory into one Unit. In deep Study, the
Agent–Environment loop, MDP full-state requirement, token/tool action
space, tabular Q-learning update, and Experiment 8-1 each warrant an
independent explanation/check; a small comparison page may connect them.

## C. Same foundation and compatibility

Both modes preserve the V3.5 first-use/profile, progress, recorded real
answers, evidence-based mastery, optional just-in-time prerequisites,
source/provenance, navigational return and seven commands. They use the
**existing Codex/DSH model**, without Study-specific API keys.

- G1 reads the actual source and verifies anchors.
- G2 checks complete coverage, group quality and genuine independent
  review. Normal Study uses lightweight Unit coherence; Study-D uses the
  full source_inventory, experiments and high-risk audit contracts.
- G3 requires explanatory content and independent source fact coverage.
  Standard Study reuses the shared mechanism/example; Study-D spends more
  space on each independent objective.
- G4 independently validates the actual teaching, with review scope/quality
  appropriate to the mode. Never equate a stamped PASS with semantic accuracy.
- G5 checks the actual HTML at mobile/desktop widths and interactions,
  reusing cached checks only for identical verified bytes.
- G6 separates generation from real page delivery; learner understanding
  is tracked separately from delivery.

When a learner requests `/study-d` for an LP already taught in normal Study,
reuse the same LP identity and previously recorded evidence, keep the current
main Unit cursor, and create a nested deep branch. An LP can be studied
again in more depth; prior completion is neither erased nor assumed from a
new page view.
