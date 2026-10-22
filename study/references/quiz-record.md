# Quiz record contract (Study 3.5)

Use two separate JSON records: a learner-facing public exam and a private teacher key. Do not embed the private key in HTML, JavaScript, DOM attributes, comments, collapsed content, or any other learner-delivered artifact. Hiding an answer visually does not make it private. Preserve original files; the checker is read-only.

## Public exam

Required fields:

- `assessment_id`: nonempty string identifying this specific assessment, shared with its private key.
- `revision`: positive JSON integer (not a boolean), shared with its private key. Increment it whenever questions change; regenerate the key at the same revision.
- `goal`: nonempty string describing the assessment goal.
- `required_lp_ids`: nonempty, duplicate-free array of existing learning-point IDs defining the blueprint.
- `questions`: at least five question objects, with unique nonempty `id` values.

Each question requires `id`, `type`, `lp_ids`, `prompt`, and `response_instruction`. `lp_ids` is a nonempty, duplicate-free string array; every ID must belong to `required_lp_ids`, and every required LP must appear in at least one question. `prompt` and `response_instruction` are nonempty strings. Instructions tell the learner what to submit, without revealing expected answers.

Question types:

- `single_choice`: `options` is an object with three or four nonempty option IDs mapped to nonempty texts. Trimmed texts must be distinct. Exactly one `correct_option` exists only in the private key.
- `true_false`: ask for a boolean judgment; `response_instruction` may additionally request a short reason. The private expected judgment is a JSON boolean, never `0`, `1`, `"true"`, or `"false"`.
- `scenario`: `parts` is an array of two or three nonempty strings, each a concrete small task. Human review must verify concreteness and alignment. Private scoring uses criteria rather than a correct-option/judgment field.

Default exams mix all three types, without a fixed ratio. A nonempty `format_override` explanation records an explicit reason for another mixture or a single-type exercise. It does not waive the minimum five questions or LP coverage. Do not invent an override to silently bypass a requested mixed exam.

Public JSON must not contain private answer fields at any depth, including extension objects or arrays. The checker rejects `correct_option`, `expected_judgment`, `answer`, `answers`, `rationale`, `criteria`, `distractor_misconceptions`, `answer_key`, `correct_answer`, `solution`, and `solutions` (case-insensitive, trimmed field-name comparison). This structural field denylist is not a security sanitizer and cannot detect all answer leaks in text or unrecognized fields. Human review of the actual learner-facing artifact is mandatory.

## Private teacher key

Required top-level fields: `assessment_id`, `revision` (positive JSON integer, not a boolean), and `answers` (array). Assessment IDs and revisions must match the public exam. An old-revision key cannot validate a revised exam; question changes require an incremented exam revision and a matching regenerated key. There must be exactly one answer for every public question, no extras and no duplicate `question_id` values.

Every answer requires:

- `question_id`: exact public question ID.
- `criteria`: nonempty array of nonempty scoring-criterion strings.
- `rationale`: nonempty explanation of the reasoning.
- `source_refs`: nonempty array of nonempty source-reference strings. These are traceability pointers, not proof of fidelity or availability.

Additional type-specific fields:

- `single_choice`: `correct_option` names an existing option. `distractor_misconceptions` is an object mapping exactly every incorrect option ID to a nonempty misconception explanation. No `expected_judgment`.
- `true_false`: `expected_judgment` is a JSON boolean. No `correct_option` or `distractor_misconceptions`.
- `scenario`: use `criteria` as the scoring basis, alongside common `rationale` and `source_refs`; no `correct_option`, `expected_judgment`, or `distractor_misconceptions`.

A populated misconception map proves only that the descriptions exist. A teacher must judge whether distractors are plausible, mutually distinguishable, and tied to meaningful misconceptions.

## Read-only structural check

Run with the Python standard library only:

```sh
python study/scripts/study_quiz_check.py exam exam.json --key teacher-key.json --state study-state.json
```

`--state` is optional. When present, `state.learning_points` must be an array of objects with unique nonempty `id` values; all required and referenced LPs must exist there. The quiz checker does not validate the rest of the state schema; use the state checker separately. Without `--state`, the report explicitly lists state LP existence as unchecked.

The checker emits a JSON report containing `result`, `errors`, `warnings`, `issues`, `checked_scope`, `not_checked`, and `semantic_validation: "NOT_CHECKED"`. Every error includes `code`, `location`, and a readable `message`. Exit codes: `0` structurally valid, `1` invalid content or arguments, `2` input I/O error. Invalid JSON, duplicate JSON object keys, nonstandard numeric constants, wrong field types, and unsupported shapes are rejected without editing any file. `--help` prints CLI help, not a JSON report.

A PASS establishes only the listed structural checks. It does not prove correctness, source fidelity, distractor quality, adequate grading criteria, meaningful question variety, no textual leakage, learner understanding, or mastery. Blueprint LP coverage is not learning evidence. This command never grades responses, writes evidence, updates learner status, rewrites a course archive, or publishes the private key.
