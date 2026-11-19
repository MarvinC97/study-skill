# Clear explanations with source English preserved

> **Study 6.6 explanation-depth check:** Define a term before using it to reach a conclusion. Trace concrete input, intermediate steps, resulting output and WHY the result follows. Include a complete worked example; when conditions change, explain what would change and why. A list of correct categories or a summary card cannot substitute for the missing mechanism. Put self-check after teaching and keep critical explanations visible. The final Reviewer must reconstruct the reasoning from the page itself.


Read when writing teaching text, diagram labels, questions, feedback, or consolidation.

## Teach the inference instead of abbreviating it

The intended reader may have no background in the subject. A technically
accurate sentence such as "loss is calculated only on response tokens"
provides a conclusion; teach the process when this mechanism is a page goal:
show an actual example with the given input, the target output, which
positions participate, what receives feedback, and how training alters
subsequent behavior. Define each term before it is used to make a decision.

For a key explanation, the reader should be able to follow:
- **Starting conditions:** what real input, state or evidence enters, and
  which assumptions are held fixed.
- **Intermediate mechanism:** what specific transformation, calculation,
  supervision signal or choice occurs, including a small example where useful.
- **Observed or expected result:** exactly what changes and why, with
  original-source outcomes distinguished from tutor-created illustrations.
- **Boundary:** what changes under a different condition and what cannot
  be inferred from the evidence.

Use this as a reasoning check, not a four-box page template. Good explanations
may interleave prose, one annotated figure and a worked calculation.
An overview can defer a full derivation to an explicitly mapped later Unit,
while teaching the shared mechanism and distinctions needed for its own goal.

Avoid unexplained jumps from "reward 1/0" directly to "the policy learns":
say what is compared, what the learning signal favors, and what that
conclusion depends on. When the source does not provide a derivation, a
tutor-authored illustration must be marked as such and stay within the
supported scope.

**Reader reconstruction test:** can someone with only the prerequisites
already introduced explain the page's central *why/how* using its visible
explanation? If the reader must supply a missing causal step, rewrite that
passage before polishing the layout. Expand a necessary explanation even when
it takes a paragraph; avoid adding filler merely to reach a word count.

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
