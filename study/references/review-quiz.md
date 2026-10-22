# Assessment and Mastery Exam

For `/study-q <topic>`, use the complete workflow below. For Unit, Study-E and Study-D Checkpoints or micro-questions, use the applicable preflight, fairness and evidence rules without turning every check into a full exam. Load only the relevant source, LPs and learner evidence. The Agent makes teaching judgments; code checks deterministic structure, not understanding. No assessment platform or per-question multi-agent pipeline is required.

## Plan the exam before writing questions

Generate the whole exam in one output, not one question at a time. Use one self-contained visual HTML exam page when supported.

- Minimum 5 substantive questions; normally 6–10, with more only for genuinely distinct mechanisms or boundaries.
- Default to a mix of multiple choice, true/false judgment and a bounded integrated scenario. A 10-question exam might use 6 choice + 3 judgment + 1 integrated question; adjust to actual coverage and learner load, not a fixed ratio. Do not default to all short answers, all choices or obvious A/B contrasts.
- Build coverage from source-supported LP objectives and what was actually taught, not a generic topic checklist. Relevant dimensions include purpose, mechanism, responsibilities, information/state flow, conditions/exceptions, nearby distinctions, failure diagnosis, prediction and application/transfer. Architecture/engineering implications and Agent scenarios are optional when supported.
- Consult the relevant learner record: demonstrated gaps, prior independent evidence, assistance and teaching corrections. Do not treat a predicted misconception or an old summary as a current fact. Use this context to choose capability, scenario and difficulty, not to pre-judge the answer.
- Record the compact assessment definition using [quiz-record.md](quiz-record.md). State which LP dimensions each question tests, why its format fits and what remains untested. Repeated classification or definition questions do not create breadth. A chapter coverage claim needs actual question-to-LP/dimension mapping, not a question count or total score.

## Question authoring — capability → rubric → options → review

This is an internal authoring check, not another learner questionnaire or report. Apply it to every assessment question.

1. **Target and scenario.** Identify the main LP, capability and observable judgment using the source and relevant learner evidence. Combine objectives only when already taught and the integrated task is bounded. Supply actor, phase, concrete task, available information, assumptions/constraints and expected answer shape as needed; clarify ambiguous “it/the system.”
2. **Answerability.** New scenarios should transfer taught principles, not require new knowledge that the question omits. All necessary data, rules, material and transferable concepts must be visible or reliably accessible. Do not assume a broken link, unseen page or missing figure was read. Explain essential unfamiliar terms with their English name and a short Chinese operational meaning; a name in a table is not proof of familiarity. Do not assume domain experience, tool setup or implementation knowledge.
3. **Reference answer before distractors.** Privately trial-answer from the source. Establish required reasoning, material conditions/boundaries and acceptable alternatives in a rubric. If answering needs invented requirements or guessed intent, repair the stem, not the hidden key. If source uncertainty or the tutor's explanation conflicts with the source, resolve or disclose it before judging; the tutor's explanation is not independent evidence.
4. **Options and possible misunderstandings.** For choice items, normally use 3–4 plausible options parallel in grammar, length and technical level. Each wrong option corresponds to a plausible partial understanding, omitted condition or confused mechanism; identify its reasoning internally. This is a diagnostic hypothesis, not proof that a learner selecting it holds that misconception. Avoid joke/filler options and superficial “obviously good vs obviously bad” contrasts. If plausible alternatives cannot be written, revise the target or format instead of padding.
5. **Adversarial review.** Hide the options: the stem must still make the intended problem and required information understandable. Ask of every wrong option, “Under what conditions would this be correct?” Check whether those conditions are excluded by the stem. A different valid workflow, a later step or a jointly useful action is not automatically wrong. Rewrite ambiguous single-best-answer items. Check length clues, gratuitous absolute words, negation traps, overlapping options, patterned answer positions and cross-question answer leakage. Do not distort logical/numerical option order merely to balance letters.
6. **Demand and final coverage.** Trial-answer the final wording, then recheck the rubric and mapped coverage. Prefer concrete interpretation/comparison and bounded application over vocabulary parroting. “Design/optimize/configure” needs an object, goal, constraints and expected detail. Ask a main judgment and its reason, not unrelated design tasks. Do not make every choice require an essay.

### Formats and workload

- **Choice:** discriminate between plausible mechanisms, conditions, next steps or explanations. A correct selection is evidence of that selection, not proof of all reasoning or the whole LP.
- **True/false judgment:** test one precise claim under stated conditions, not compound wording or absolute-word guessing. Where reasoning matters, request a short reason or correction, normally one sentence. Bare true/false has limited evidence value; do not equate it with explanation or independent transfer.
- **Integrated scenario:** use one new, sufficiently specified situation requiring 2–3 short linked judgments, such as identify the failure, choose a response, then predict a changed condition. Each judgment should add evidence through applying taught relationships. Do not relabel earlier component-classification questions as “综合题,” or bundle several open-ended system designs.

Other forms (procedural trace, diagram-to-words explanation, contextual terminology or an open judgment with defensible alternatives) remain available when the objective warrants them. Vary the reasoning rather than merely the surface format.

A concrete failure case: after separate SELECT/WHERE, permission and execution questions, repeating those same judgments with a different city is not meaningful synthesis. Prefer a supplied small table plus two conflicting result previews: ask which rows/columns violate the stated goal and predict one changed filter. New data must change the reasoning, not merely the names. This is an example, not a mandatory SQL template.

## Answers and rubric separation

The initial exam contains questions and work areas only: no model answers, solution-disclosing hints, grading feedback or answer-key section. Do not hide keys in HTML, comments, scripts or CSS. Retain the key/rubric separately until the learner attempts the exam or explicitly requests answers.

Keep answer keys/rubrics as versioned assessment definitions under [quiz-record.md](quiz-record.md), not a second mutable progress record. Current completion/grading status lives in course state. Older auxiliary awaiting/completed labels are snapshots, reconciled against current evidence without overwriting history. Grade meaning and justified assumptions, not exact wording. Preserve English terms/API/code; explain feedback in Chinese.

## Evaluate, repair and close the learning loop

When actual answers arrive:

1. Evaluate every submitted question against its actual revision, distinguishing correct reasoning, missing reasoning, plausible diagnostic hypotheses and demonstrated misconceptions. A choice alone need not reveal why it was chosen; if that distinction matters and remains ambiguous, use one discriminating follow-up rather than inventing a diagnosis.
2. Preserve the actual answer or faithful response record, question ID/revision, LP IDs, rubric criteria, assistance context, outcome and supported misconceptions in the single course `evidence` array. Use existing `learning_status`, rubric and assistance fields under `../schemas/learning-point.md`.
3. Update only evidenced LP dimensions to `attempted`, `understood` or `applied` as warranted. Unfamiliar syntax is not automatically conceptual failure. Untested dimensions remain unassessed; a total score cannot promote the entire chapter.
4. Repair the smallest demonstrated gap, then offer a fresh near-transfer case that tests repaired reasoning instead of copying. Preserve original and follow-up evidence; unanswered checks are not passed or failed. Recommend `/study-e` for a local gap or `/study-d` for an incomplete conceptual structure without forcing either. Retain the key and feedback for `/study-c`.
5. Follow [learning-loop.md](learning-loop.md): actual course evidence → chapter summary → derived personal learner summary → a specific next-teaching decision. The personal summary is not a second mastery source. Cite the supporting course evidence and its scope, preserve uncertainty, and let relevant findings change the next Unit's example, prerequisite explanation, contrast or check. Merely writing a profile note does not close the loop.

For ambiguous, underspecified, source-inconsistent or multiply defensible questions, accept valid interpretations and repair the prompt/rubric. Preserve the original answer and link revisions; never silently grade it against a changed question. Withdraw invalid penalties and unsupported learner-misconception labels, retain the correction history, and refresh dependent chapter/profile summaries with corrected evidence references. Record teaching defects separately as teaching corrections. Do not erase unrelated valid evidence or make a false learner diagnosis persist in a summary.

If the learner says a question is unclear, explain its intended target, clarify or withdraw it, and provide missing prerequisites before reassessment. A different valid tool/workflow is not an error.

## Assistance and mastery boundaries

Hints, worked solutions and answer reveal make the affected response assisted practice. They may show a narrow attempted dimension but must not produce new independent mastery promotion. Promotion requires a fresh, independently answered task meeting the relevant source-supported criteria, with material changes where transfer is claimed. Renamed nouns or copyable revealed reasoning are not fresh transfer.

Do not downgrade previously established independent mastery merely because the learner later requests a hint or practices after reveal. Preserve earlier evidence; actual contradictory reasoning warrants scoped reassessment, not silent erasure. Time passing alone does not revoke mastery.

A choice, numeric score, page view, “understood,” request to continue or revealed answer cannot establish whole-topic mastery. Assess only received responses; do not claim HTML answers were captured when the host provides no data. Skipped checks leave evidence gaps without blocking navigation.

Working mastery requires the evidence appropriate to the stated learning goal and LP criteria: explanation, mechanism, distinctions or application/transfer where required. Do not demand independent implementation or every cognitive dimension for a concept-reading goal. Judge criteria and boundaries, not a score alone. Same-day repetition is not independent long-term retention evidence. Preserve observation time/context when known, without invented probabilities or mandatory review schedules. Small cross-Unit checks follow `unit-teaching.md`.

## Clarity regressions

- “不放进 Context 怎么检查？” is underspecified. Name the Agent's Read access, relevant lines given to the model, refund-check task and inputs/results to inspect. Supply actual data/rules before grading a numeric result.
- After only introducing acceptance baseline, execution boundaries, feedback signals and rollback, reject “假设 Agent 修改代码，四个组件分别可以如何设置？” It lacks task/constraints and demands four designs at once.
- Bounded replacement: “Agent 要修复网页按钮。开始修改前，系统保存了一个可以恢复的旧版本。如果修改后网页打不开，这个旧版本有什么用？它属于四个组件中的哪一个？” Accept restoration/rollback reasoning without requiring Git configuration. The backup does not itself diagnose or repair the bug; this answer does not prove all four components.
- Before a UI/Linter question, explain that a Linter checks configured code rules, not an undefined aesthetic goal. Ask which completion criterion is missing instead of making the learner guess tool capabilities. Tool PASS alone proves neither UI quality nor full task completion.

## Verification and design sources

Separate software behavior, content/source correctness and teaching fairness. Apply the active runtime instructions using `../scripts/study_check.py`; use `../scripts/study_quiz_check.py` for the assessment record according to [quiz-record.md](quiz-record.md). These checks validate deterministic structure and references, not distractor plausibility, source truth, fair difficulty, valid diagnosis or learner mastery. Inspect actual generated questions, rubrics and evidence using `presentation-qa.md`. Repair a failed question or affected delivery/evaluation action without freezing unrelated work or claiming unchecked results passed.

Design influences, adapted narrowly rather than imported as workflows:

- [Hinge Question Designer](https://github.com/GarethManning/education-agent-skills/blob/main/skills/questioning-discussion/hinge-question-designer/SKILL.md): objective-focused checks, misconception-aware alternatives and acting on evidence. Study treats option-based diagnoses as hypotheses, not certainty.
- Question Engine [generator](https://github.com/jimmyleepruitt/question-engine/blob/main/skills/generator.md) and [distractor validator](https://github.com/jimmyleepruitt/question-engine/blob/main/skills/distractor-validator.md): source-grounded stems, option-hiding test and checking when an alternative could be valid. No clinical pipeline, medical assumptions or per-item multi-agent machinery is imported.
- [Quiz Generator](https://github.com/SkillMedev/skills/blob/main/skills/quiz-generator/SKILL.md): plan the capability mix, reject filler alternatives and check coverage. Its fixed format restrictions do not override Study's bounded mixed-format assessment or answer separation.
