# Clear explanations with source English preserved

Read when writing teaching text, diagram labels, questions, feedback, or consolidation.

## Language contract

For this learner, explain in Chinese while retaining English from the source. Preserve technical terms (Agent, Context, Harness, Tool Calling, KV Cache), abbreviations, identifiers, API names, filenames, commands, and code spelling/case. Do not translate executable syntax. Explain a term's meaning and role in Chinese at first useful occurrence; do not require a Chinese replacement for every English word. Reuse the same term in text, diagrams, questions, and feedback.

Keep necessary short original English passages alongside Chinese explanation and a source anchor. Distinguish original quotation, paraphrase, tutor explanation, and fictional example. Respect quotation limits; do not reproduce a whole source merely to preserve its English. English source material does not imply that the whole lesson should be in English. Follow an explicit later learner language request.

## Clarity rules

- One principal idea per sentence; name the actor and action.
- Explain concrete operations before an abstract definition, then restore the precise definition.
- Separate condition, action, and consequence without losing their relationship.
- Preserve negation, scope, uncertainty, exceptions, necessary vs sufficient conditions, and important numbers/units.
- Keep consistent terminology. Define unavoidable synonyms rather than silently swapping names.
- Use analogies to build intuition, then state where the analogy stops being accurate.
- Do not impose rigid sentence lengths or strip nuance to make sentences shorter.

These are clear-writing principles inspired by controlled technical language, not a claim of ASD-STE100 compliance, an English controlled-vocabulary translation, or an “80% compliant” score.

## Example

Source term: Retrieval-Augmented Generation (RAG).

用户提出问题。检索步骤从知识库寻找相关片段。系统把问题和片段一起交给模型。模型结合这些输入生成回答。资料遗漏或使用错误都可能使回答出错。

This is an introductory model, not a guarantee that an arbitrary RAG system refuses unsupported answers. A teaching example may specify such a policy, but label it as that example's policy.

## Quick check

Can the learner identify who does what, what enters and leaves each step, and when the explanation does not apply? Verify terminology and technical claims against the actual source, not readability alone.

## V3.1 inspectable source support

Place a short source anchor near a key technical claim when inspection would help: verified URL + heading, PDF page, repository path + commit/lines, or transcript timestamp. Preserve necessary short English wording beside its Chinese explanation. Distinguish “原文”, “中文解释”, and “教学类比/虚构例子” where the distinction matters; do not decorate every sentence with repeated citations.

Use only verified destinations. A source anchor may be a precise textual location if the host has no clickable deep-link support. Do not invent line numbers or treat remembered filenames as read contents. One source list at the end may supplement but must not obscure the support for a contentious claim. No need to copy the entire English source into the page.
