# Study 6.6: Direct HTML teaching contract

## Goal

Transform the complete selected source into HTML that a new learner can
understand without inventing the missing reasoning. The approved learning
point (LP) map controls source coverage; the final authored HTML is the only
official lesson text. Codex/DSH's connected model first completes a source-grounded teaching
manuscript; a separate visual implementation pass transforms that manuscript
into an inspectable HTML lesson. Python handles deterministic provenance,
UI/browser checks and delivery state.

New courses set `render_contract: "direct-html-v1"` and
`authoring_mode: "two-pass"` in `plan.json`. For already approved or
in-progress direct HTML plans, perform the same two authoring passes without
rewriting the approved plan hash; they retain their original runtime contract.
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

## Two inputs with separate authority: original source + approved teaching benchmark

**The selected original source is the authority for facts.** Read the
page's actual passages and relevant surrounding material, including any
equations, figures, experiment setup, limitations and exceptions. Preserve
the approved LP/Unit scope and indicate material intentionally taught on
a later page. An LP title or Fact ID alone is insufficient teaching input.

**A previously accepted high-quality HTML sample is an optional presentation
benchmark.** When a sample is actually accessible and approved by the learner,
read the HTML or view the rendered page before authoring. Observe how it
introduces terms, lays out a causal relationship, places diagrams next to
the steps they explain, walks through a concrete case, and checks understanding.
Reuse those teaching principles and visual standard; source facts, numerical
values, experimental results and scope still come exclusively from the current
original source. Never invent a benchmark, reuse another course's facts, or
force its layout onto a different topic. If no sample is available, use the
reader-comprehension criteria below without claiming sample equivalence.

The Teaching Author and Visual Builder must satisfy **two independent
obligations in the final HTML**:
1. SOURCE FIDELITY: each scoped important LP, source condition and claim
   is supported and retains the author's intended meaning and limits.
2. READER COMPREHENSION: a learner with stated prerequisites can follow
   the key reasoning on this page and use it in a comparable new situation.

A visually polished page that drifts from the source fails (1).
An accurate list of conclusions that omits the reasoning fails (2).

## Default B workflow: two production passes, one final review

**Pass 1 · Teaching Author (content, no HTML).** Read all relevant original
passages and their context with the approved LP/page scope. Write
`lesson-drafts/<page-id>.md` as a complete Chinese teaching manuscript:
definitions before use, meaningful examples, intermediate causal/mathematical
steps, exact source conditions and limits, and original-versus-illustrative
distinctions. For experiments preserve real setup, controls, numeric evidence
where reported, and interpretation boundaries. The manuscript is an
**actual complete lesson** written to teach; it is not a schema, card catalog,
bullet outline, page storyboard, or set of slide captions. Provide source
anchors for important claims. The initial manuscript does not contain HTML/CSS/JS.
Finish and save its bytes before starting the visual pass.

**Pass 2 · Visual Builder (page design and implementation).** Start from the
saved manuscript and, when available, an accessible learner-approved visual
benchmark. Use a distinct host-agent context when supported; the same host
model and plan suffice. Read the manuscript in full. Convert its significant
conceptual relationships into suitable HTML visualizations, and show actual
intermediate operations rather than decorative cards. Examples include
labelled token alignment, a calculation with adjustable probability,
an experiment with comparable conditions, a labelled branching choice,
or a genuinely useful diagram. Select each based on the *current* subject.
Keep every essential explanation and original-source boundary in the HTML
without hiding it behind a disclosure. The manuscript remains the content
reference, not a separate rendering schema. Save the complete standalone
page at `authored-pages/<page-id>.html`. Use responsive semantic HTML,
safe local CSS/JS and a static readable core. No mandatory interactions
or fixed word, section, scene, component or diagram counts.

**One independent final review** compares original source + approved route +
saved teaching manuscript + *reader-visible* final HTML. Check both
(1) source fidelity and (2) teaching completeness/visual explanation.
Check that the manuscript's substantial learning content reached the final
page with correct meaning. Reviewers should point to a specific missing
intermediate step, example, visual relationship or factual condition.
Make targeted changes, update the manuscript if meaning changes, and
re-review exact final bytes. Run actual Chromium QA after content approval.
Deliver only the verified HTML; do not attach the manuscript unless the
learner requests it.

**Manuscript provenance for new plans.** The existing final review receipt
also includes `lesson_sha256` (SHA-256 of the exact saved UTF-8 manuscript
bytes) when `authoring_mode: "two-pass"`. The runtime verifies its
existence and that the hash still matches when publishing. This is a
single integrity check inside the existing final review, **not** another
approval stage. For older direct-HTML plans, the manuscript is useful
but its hash is optional for backward-compatible recovery.

## Teaching goals by page kind

For a roadmap/overview, show the common mental model and meaningful
differences, linking detailed derivations to their approved later pages.
For an algorithm, training step or formula, show actual input → operation /
learning signal → intermediate effect → result and assumptions.
For experiments, retain source-reported conditions, comparisons, outcomes
and inference limits. For failure cases, identify the first wrong decision
and its downstream consequences. Terms appear before they are required.

A comparison chart can provide a map, but a page about how a mechanism
works must also reveal the transformation. The reader should be able to
reconstruct it from the visible page. Questions follow the explanations
needed to answer them; answers and optional supplementary material may
use native disclosures.

## One independent review of the actual learner-visible HTML

Review source + current approved LP plan + the saved manuscript when
present + the **actual complete page**.
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
dimensions. For `explanation_depth`, `teaching_sequence`, and
`visual_pedagogy`, each check also supplies `reader_evidence`: a short
exact excerpt from the *reader-visible main HTML* supporting the verdict.
A passage hidden in an optional disclosure or an invented quote fails the
deterministic check. A matching excerpt is traceability evidence, **not**
proof of actual teaching sufficiency; the isolated Reviewer must explain
why the cited material demonstrates the mechanism or visual relationship.
For new two-pass plans, include `lesson_sha256` and verify that the final
HTML retains the manuscript's material reasoning, examples and limits. These source/plan/HTML hashes bind the review to the exact
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
