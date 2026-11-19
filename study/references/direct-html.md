# Study 6.6: Direct HTML teaching contract

## Goal

Transform the complete selected source into HTML that a new learner can
understand without inventing the missing reasoning. The approved learning
point (LP) map controls source coverage; the final authored HTML is the only
official lesson text. Codex/DSH's connected model writes the explanations,
visuals, examples and actual HTML together. Python handles deterministic
provenance, UI/browser checks and delivery state.

New courses set `render_contract: "direct-html-v1"` in `plan.json`.
Older V3.5–V6.5 plans retain their historical reading and resumption paths.
No Lesson Specification, Storyboard, component registry, min-length content
quota, forced diagram, or mandatory scene count is required in the default
course authoring path.

## Modes

**/study:** inventory all important source LPs once, then teach related LPs
as a coherent Unit with one overall mental model or worked case. Its pages
may have any number of LPs supported by a manageable teaching objective.
`/study` gives the overview; `/study-n` generates/delivers the next Unit.

**/study-d:** focus on one mechanism, formula, experiment, algorithm or
case, giving enough space for intermediate steps, derivation, evidence,
boundaries and changed-condition reasoning. A page may include closely
linked LPs. For a multi-page deep scope, the complete source-grounded
outline is independently reviewed and explicitly approved by the learner
before page generation. Deliver one page per turn, preserve the main
course return point and the deep cursor.

Both modes share V3.5 stable LP IDs, course state schema 3.0 and genuine
answer evidence. Navigation or clicking an answer never establishes mastery.

## Authoring sequence: one source → one complete lesson

1. Read the actual page source and necessary surrounding paragraphs, source
   diagrams, formulas and experimental settings. Consult the approved plan,
   relevant prerequisites and learner background.
2. State what this page teaches and explain the necessary concepts **before**
   requiring problem diagnosis. Explain an acronym at first appearance with
   English expansion and Chinese meaning when relevant.
3. Show the actual mechanism **input → intermediate change → result → why**.
   A concrete worked case must exercise the same mechanism. Explain at least
   one meaningful changed condition or limitation when needed.
4. For experiments, preserve source question, setup, controlled variables,
   observations, numerical values where actually reported and interpretation
   boundaries. Label any illustrative invented example distinctly.
5. Let the teaching determine HTML order and visuals. Use a diagram for a
   causal relation, table for grounded comparison, calculation for numerical
   reasoning, and interactive controls only when their changes teach a
   real fact. A clear paragraph is a valid choice.
6. Place core explanations and diagrams visibly in reading order. Keep
   answers, optional supplementary detail and provenance in disclosures.
   A reader must understand the page without opening hidden material.
7. Finish the explanation before placing a short self-check. The answer must
   be inferable from what has already been taught; accept brief correct
   answers in the conversation. Do not force a self-check where unnecessary.
8. Write the full self-contained HTML at
   `authored-pages/<page-id>.html`. Use semantic HTML and a responsive
   viewport; local CSS/JS are allowed. Never ship untrusted third-party
   scripts or execute arbitrary source HTML.

## One independent review of the actual learner-visible HTML

Review source + current approved LP plan + the **actual complete page**.
Reviewer must reconstruct the core reasoning using only what readers can
see, locating each important intermediate step and the source supporting it.

The five review dimensions are:
- `source_fidelity` — accurate facts, conditions, experimental numbers.
- `explanation_depth` — mechanism, intermediate changes, causal reasons and
  meaningful case are explained clearly enough for the intended learner.
- `teaching_sequence` — concepts precede use, core knowledge is not hidden
  behind optional material or presented after an assessment.
- `visual_pedagogy` — figures/interactions explain real relationships;
  labels and narrated values agree. Text-only is acceptable when clearer.
- `assessment_fairness` — a question (when present) follows the explanation,
  checks a valid changed condition, and has source-supported feedback.

Reject precise omissions, misleading visual implications, unsupported claims
and unjustified inferences by page location. HTML structure, length and
reviewer metadata cannot alone prove educational quality.

Review metadata is saved at `reviews/html/<page-id>.json`:
`contract=direct-html-v1`, `page_id`, `source_sha256`,
`plan_sha256`, `html_sha256`, `review_mode=isolated_host_agent`,
real distinct `writer_context_id`/`reviewer_context_id`, `approved`,
`issues`, an exact `checked_fact_ids` set and a `checks` array with
`dimension`, `passed` and a **page-specific reason** for each of the five
dimensions. These source/plan/HTML hashes bind the review to the exact
files, not to generic intentions. If independent review is unavailable,
mark REVIEW_UNVERIFIED and do not publish it as passed.

## Runtime, browser and deliver

- `v6_agent.py direct-page-check --workspace WS --page-id PAGE` validates
  the authored HTML, final review and actual Chromium page.
- Standard `/study-n` checks the next reviewed HTML, copies exact bytes to
  `published/`, and records a pending Unit delivery.
- Deep `/study-d` uses `v6_agent.py stage-next-page --workspace WS`.
  It validates one approved page, appends it to the queue and keeps prior
  delivered pages unchanged.
- Chromium checks responsive widths, core visibility, browser errors and
  native keyboard disclosures when present. Content needs no compulsory
  buttons or scripts.
- Advance the Unit or deep cursor only after the exact page has genuinely
  been made available to the learner and confirmed. Generated, delivered,
  and assessed are three separate states.

## The other five commands

`/study-e` gives a fresh explanation of the identified knowledge gap,
retaining previous variants and the original route position. `/study-q`
uses questions only at first, then grades real submitted answers using the
separately saved key. `/study-c` compiles the complete existing explanations,
figures, experiments and corrections into a readable offline HTML. `/study-m`
shows source-backed LPs, delivered progress and actually evidenced mastery,
separately. These outputs follow the same reader-first teaching philosophy.

## Rollout and GitHub public scope

Before bulk generation, compare a genuine introductory mechanism page and
a math/experiment or troubleshooting page against a known clear sample.
If either is difficult to understand, adjust the teaching explanation first.
Keep no artificial LP/word/page/scene targets.

GitHub public synchronization covers **generic Skill rules, execution code,
and synthetic tests** only. Do not include course source excerpts, generated
HTML, local course workspaces, user profiles, actual answers or local paths.
