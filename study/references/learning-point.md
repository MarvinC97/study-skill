# Lightweight Learning Point and artifact registry

LP is the smallest source-coverage and understanding unit; Unit is the learner-facing container. Use stable IDs (e.g., `CH02-LP07`) independent of later Unit splits. No database requirement; use host file/workspace or conversation context.

```yaml
lp_id: CH02-LP07
title: "Agent Loop observation"
source_id: ai-agent-book
source_anchor: chapter2.md#agent-loop
classification: source-core  # source-core | prerequisite | optional-extension
learning_goal: "Explain why tool results must re-enter context"
prerequisites_required: [CH01-LP02]
prerequisites_helpful: []
misconceptions: ["Tool executions are automatically remembered by the model"]
unit_id: CH02-U03
questions: [Q-CH02-LP07-01]
artifacts:
  - {type: unit, path: "chapter2/unit03.html", verified: false}
  - {type: deep, path: "chapter2/deep-agent-loop/index.html", verified: false}
evidence:
  delivered: []
  attempted: []
  understood: []
  applied: []
```

Distinguish `delivered` (page created), `attempted` (answer/action submitted), `understood` (correct causal explanation with evidence ID), and `applied` (correct transfer to new situation with evidence ID). Opening a page, revealing an answer, completing the Unit, or clicking through a simulation does not imply mastery. Preserve user response, rubric, evaluation, and whether the prompt was ambiguous. Fix ambiguous questions before treating failure as a gap.

Maintain an artifact index by topic, LP ID and verified file path. Reuse for `/study-c`; list inaccessible artifacts instead of inventing their contents. Keep STORM proposed questions attached to LP IDs and annotate uncertainty. When necessary prerequisites block the next Unit, insert a miniature prerequisite and return to the main Unit pointer.

## V5 additional IDs
Each atomic LP maps to source span IDs and a set of required facts with stable fact IDs. These are the contractual minimum for both JSON explanation and final HTML. Keep `delivered`, `attempted`, `understood`, `applied` separately; learner replies plus rubrics are required for mastery.
