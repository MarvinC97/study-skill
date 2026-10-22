# Unit Teaching

Read for standard Units entered through `/study-n` and local repairs through `/study-e <topic>`.

## Teaching target and planning

Build a correct mental model, then enough technical detail for working understanding. Do not expose depth-selection modes or impose a fixed amount of detail: adapt scaffolding, prerequisites, pacing and formal detail to the objective and actual evidence under `learner-adaptation.md`.

Use the Unit's stable learning-point (LP) IDs, source-supported objectives and current return position. Preserve important mechanisms, boundaries, source English terms and code. Explain in Chinese, with concrete intuition before formal definitions; follow `writing-clarity.md`.

Choose one main teaching form per coherent cluster using `visual-semantics.md`. Use `interaction-design.md` when an adjustable condition or step sequence reveals the mechanism, not merely to decorate a page.

## Standard Unit sequence

1. **WHY**: the problem this concept solves, in one concrete situation.
2. **INTUITION**: the simplest correct mental model, using a diagram, before/after, pipeline or tiny analogy when useful.
3. **REAL TERM**: the precise source terminology and definition, introducing unfamiliar terms without forced Chinese replacements.
4. **HOW IT WORKS**: a causal mechanism, such as `input → transformation → state/change → output`, or an explicit step sequence.
5. **EXAMPLE**: one realistic worked case; add cases only when they improve understanding.
6. **CONNECTION**: the previous Unit, current chapter map and next dependent idea.
7. **CONFUSION CHECK**: distinguish nearby concepts exactly where confusion matters.
8. **REMEMBER**: 2–4 durable mental models.
9. **CHECKPOINT**: 1–3 short reasoning questions about why, changed conditions, responsibility or information flow. Apply `review-quiz.md` preflight before showing them.

Link each Checkpoint to its LPs and retain expected reasoning, acceptable alternatives and common misconceptions separately from the initial question. Assess only actual received answers under `../schemas/learning-point.md`; predictions, clicks, displayed explanations and invitations to observe are not automatic evidence.

## Just-in-time prerequisites

Use `main Unit → prerequisite mini-Unit → minimum sufficient understanding → return to main Unit`. Do not front-load an entire prerequisite curriculum, infer inability from `unassessed`, or replace the existing objective with a remedial course.

## `/study-e <topic>` — smallest useful repair

Use a local re-explanation when one concept is unclear. Diagnose from the answer and current lesson, change the representation or example, and repair only the missing piece rather than repeating the previous wording.

A compact flow is `当前位置 → 新的直觉/表示 → 准确含义 → 最小例子 → 重新连接当前 Unit`. Keep only steps needed for this repair. Progressive examples are optional: add a realistic application, Agent case or engineering case only when the source/topic and learner's gap justify it. Never require an Agent or engineering ladder for every subject.

Preserve the main Unit return point and existing evidence. If the topic genuinely needs a complete multi-page treatment, offer the existing `/study-d <topic>` path with `deep-module.md`; do not silently expand `/study-e` into a module.

## Diagnose → repair → fresh check

Use actual answers before asking another question. If the gap is clear, address it directly. If “不知道” or an ambiguous response does not locate it, ask one discriminating question, not a new intake or confidence questionnaire.

Distinguish provisional explanations of a response:

- **Term/language**: connect the real English term to a concrete actor/action or bilingual gloss.
- **Code/notation**: unpack syntax, API or symbols; do not mistake unreadable code for failure of the underlying concept.
- **Mechanism/relationship**: show the missing input, transformation, output or causal link.
- **Confused concepts/conditions**: align the distinguishing criteria in a shared example, including overlooked boundaries.
- **Prerequisite**: give the minimum necessary explanation and return.
- **Application/execution slip**: distinguish a missing procedure from a local mistake; work only the needed step or case.
- **Question defect**: repair unclear actors, phase, assumptions or task before judging the learner.

These are hypotheses about a response, not labels for a person. Ask one targeted follow-up only if needed to distinguish them. Let the learner continue without a quiz gate and retain unresolved uncertainty.

After a repair, invite a causal explanation in the learner's own words or offer a small changed case. Accept chat answers or explicitly transferred page responses; do not imply uncaptured HTML input was received. A displayed reference explanation or assisted repetition is practice, not new independent mastery. Follow `review-quiz.md` for promotion and assistance rules.

## Controlled contrasts and transfer

When helpful, hold actors, data, task and evaluation criteria fixed, change one named condition, and explain the changed result. For example, keep a RAG question and answering policy fixed while changing whether the supplied passage contains the requested opening time. Label this as a controlled teaching example, not proof of real-world performance.

If several factors change, name them and do not attribute the result to one factor alone. Preserve limits; avoid universal superiority claims and forced good/bad binaries.

When a later Unit genuinely uses an earlier LP, optionally include one fresh scenario within the existing Checkpoint budget. Reuse its stable LP ID, record assistance, and preserve old/new evidence. Renamed nouns alone are not transfer. Respect skipped checks; do not add a compulsory repeat exam or an unsolicited review schedule.

## Code and mathematics

Teach code as `purpose → system flow → pseudocode → real code → important lines → engineering implications`, selecting the steps needed for the source and objective. Explain unfamiliar syntax/API separately from algorithmic reasoning.

Teach math as `question answered → variable meaning → intuitive relationship → formula → small numeric example → why it matters`. Separate notation or algebraic slips from conceptual misunderstanding.

## Adaptation and verification

Use relevant profile/course evidence to make an actual local adjustment, not merely mention the profile. Choose a complete worked example, partially supported task or independent application according to readiness; reduce help when evidence supports it. Do not permanently confine a learner to an initial level or preferred medium.

Retain observed explanation effects with their objective, method, actual next response and evidence reference when useful. Do not infer causality or effectiveness from engagement, or repeat an ineffective analogy because a profile lists that preference. Working context is sufficient; no per-turn log is required.

Register the actual artifact/version and accessible reference; mark delivery separately. Verify three distinct dimensions: software behavior, source-grounded content/coverage, and teaching clarity/fairness. Apply `presentation-qa.md` and the active runtime-check instructions using `../scripts/study_check.py` when file capabilities are available. A script or template pass cannot validate the lesson's content or pedagogy. Pause and repair only the affected action on failure; continue unrelated valid teaching without claiming unchecked work passed.
