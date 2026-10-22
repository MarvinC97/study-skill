#!/usr/bin/env python3
"""Read-only stdlib structural quiz validator; never assesses learning semantics.

Usage: study_quiz_check.py exam EXAM.json --key KEY.json [--state STATE.json]
Exit 0: structurally valid; 1: invalid content/arguments; 2: input I/O error.
No input is rewritten, source fetched, answer graded or learner status changed.
"""
import argparse
import json
from pathlib import Path
import sys

TYPES = ('single_choice', 'true_false', 'scenario')
PRIVATE_FIELDS = frozenset(('correct_option', 'expected_judgment', 'answer', 'answers',
                            'rationale', 'criteria', 'distractor_misconceptions',
                            'answer_key', 'correct_answer', 'solution', 'solutions'))


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


class Report:
    def __init__(self):
        self.data = {'kind': 'exam', 'errors': [], 'warnings': [],
                     'semantic_validation': 'NOT_CHECKED',
                     'checked_scope': ['public/private JSON structure, assessment and revision binding',
                                       'question IDs, answer alignment, typed answer fields',
                                       'LP blueprint coverage, question mixture and minimum length',
                                       'recursive public answer-field exclusion'],
                     'not_checked': ['answer correctness, distractor plausibility, rubric sufficiency',
                                     'source fidelity and source availability',
                                     'all textual answer leakage, question clarity and concrete task quality',
                                     'learner mastery; blueprint coverage is not evidence of understanding']}

    def error(self, code, location, message):
        self.data['errors'].append({'code': code, 'location': location, 'message': message})

    def finish(self, io=False):
        self.data['result'] = 'IO_ERROR' if io else 'INVALID' if self.data['errors'] else 'PASS'
        self.data['issues'] = self.data['errors'] + self.data['warnings']
        print(json.dumps(self.data, ensure_ascii=False, indent=2))
        return 2 if io else 1 if self.data['errors'] else 0


def strings(value, where, report, minimum=1, maximum=None, unique=False):
    if not isinstance(value, list):
        report.error('list_shape', where, 'Expected a nonempty string array.'); return []
    if len(value) < minimum or (maximum is not None and len(value) > maximum):
        report.error('list_length', where, f'Expected {minimum} to {maximum or "any"} entries.')
    valid = []
    for i, item in enumerate(value):
        if not nonempty(item):
            report.error('string_shape', f'{where}[{i}]', 'Nonempty string required.')
        else:
            valid.append(item)
    if unique and len(set(valid)) != len(valid):
        report.error('duplicate_reference', where, 'Duplicate entries are not allowed.')
    return valid


def text_field(data, field, where, report):
    if not nonempty(data.get(field)):
        report.error('string_shape', where + '.' + field, 'Nonempty string required.')


def public_fields(data, report):
    # Iterative traversal avoids recursion limits on nested extension objects.
    stack = [('exam', data)]
    while stack:
        where, value = stack.pop()
        if isinstance(value, dict):
            for key, item in value.items():
                location = where + '.' + key
                if key.strip().casefold() in PRIVATE_FIELDS:
                    report.error('public_answer_field', location, 'Private answer field must not appear in public exam.')
                stack.append((location, item))
        elif isinstance(value, list):
            stack.extend((f'{where}[{i}]', item) for i, item in enumerate(value))


def check_exam(exam, key, report, state=None, has_state=False):
    if not isinstance(exam, dict):
        report.error('exam_shape', 'exam', 'Exam must be an object.'); return
    if not isinstance(key, dict):
        report.error('key_shape', 'key', 'Private key must be an object.'); return
    public_fields(exam, report)
    for field in ('assessment_id', 'goal'):
        text_field(exam, field, 'exam', report)
    text_field(key, 'assessment_id', 'key', report)
    if key.get('assessment_id') != exam.get('assessment_id'):
        report.error('assessment_binding', 'key.assessment_id', 'Key must bind to the exam assessment_id.')
    for label, record in (('exam', exam), ('key', key)):
        revision = record.get('revision')
        if type(revision) is not int or revision < 1:
            report.error('revision_shape', label + '.revision', 'Revision must be a positive JSON integer, not a boolean.')
    if key.get('revision') != exam.get('revision'):
        report.error('revision_binding', 'key.revision', 'Key revision must match the public exam revision.')
    required = set(strings(exam.get('required_lp_ids'), 'exam.required_lp_ids', report, unique=True))
    real_lps = set()
    if has_state:
        report.data['checked_scope'].append('LP membership in supplied state.learning_points')
        records = state.get('learning_points') if isinstance(state, dict) else None
        if not isinstance(records, list):
            report.error('state_shape', 'state.learning_points', 'Expected an array of LP objects.')
        else:
            for i, record in enumerate(records):
                if not isinstance(record, dict) or not nonempty(record.get('id')):
                    report.error('state_lp_id', f'state.learning_points[{i}]', 'Object with nonempty id required.')
                elif record['id'] in real_lps:
                    report.error('duplicate_id', f'state.learning_points[{i}].id', 'Duplicate LP ID.')
                else:
                    real_lps.add(record['id'])
        for lp in sorted(required - real_lps):
            report.error('unknown_state_lp', 'exam.required_lp_ids', 'LP not found in state: ' + lp)
    else:
        report.data['not_checked'].append('state LP existence')
    questions = exam.get('questions')
    if not isinstance(questions, list):
        report.error('questions_shape', 'exam.questions', 'Expected an array.'); questions = []
    if len(questions) < 5:
        report.error('question_count', 'exam.questions', 'At least five questions are required, including with format_override.')
    by_id, covered, kinds = {}, set(), set()
    for i, q in enumerate(questions):
        where = f'exam.questions[{i}]'
        if not isinstance(q, dict):
            report.error('question_shape', where, 'Question must be an object.'); continue
        for field in ('id', 'prompt', 'response_instruction'):
            text_field(q, field, where, report)
        qid = q.get('id')
        if nonempty(qid):
            if qid in by_id: report.error('duplicate_id', where + '.id', 'Duplicate question ID.')
            by_id[qid] = q
        lp_ids = strings(q.get('lp_ids'), where + '.lp_ids', report, unique=True)
        covered.update(lp_ids)
        for lp in lp_ids:
            if lp not in required: report.error('lp_outside_blueprint', where + '.lp_ids', 'LP not in required_lp_ids: ' + lp)
            if has_state and lp not in real_lps: report.error('unknown_state_lp', where + '.lp_ids', 'LP not found in state: ' + lp)
        kind = q.get('type')
        if not isinstance(kind, str) or kind not in TYPES:
            report.error('question_type', where + '.type', 'Expected single_choice, true_false or scenario.'); continue
        kinds.add(kind)
        if kind == 'single_choice':
            options = q.get('options')
            if not isinstance(options, dict):
                report.error('options_shape', where + '.options', 'Expected an option-ID to text object.')
            else:
                if len(options) not in (3, 4): report.error('options_count', where + '.options', 'Expected three or four options.')
                texts = []
                for option, value in options.items():
                    if not nonempty(option) or not nonempty(value):
                        report.error('option_shape', where + '.options', 'Nonempty option ID and text required.')
                    else: texts.append(value.strip())
                if len(texts) != len(set(texts)): report.error('duplicate_option_text', where + '.options', 'Option texts must be distinct after trimming.')
        elif kind == 'scenario':
            strings(q.get('parts'), where + '.parts', report, minimum=2, maximum=3)
    for lp in sorted(required - covered):
        report.error('uncovered_lp', 'exam.questions', 'No question covers required LP: ' + lp)
    override = exam.get('format_override')
    if 'format_override' in exam and not nonempty(override):
        report.error('format_override', 'exam.format_override', 'Override requires a nonempty explicit explanation.')
    if not nonempty(override) and kinds != set(TYPES):
        report.error('question_mixture', 'exam.questions', 'Default exam must include all three question types; explicit format_override is required otherwise.')
    answers = key.get('answers')
    if not isinstance(answers, list):
        report.error('answers_shape', 'key.answers', 'Expected an answer array.'); answers = []
    seen = set()
    for i, a in enumerate(answers):
        where = f'key.answers[{i}]'
        if not isinstance(a, dict):
            report.error('answer_shape', where, 'Answer must be an object.'); continue
        text_field(a, 'question_id', where, report)
        qid = a.get('question_id')
        strings(a.get('criteria'), where + '.criteria', report)
        strings(a.get('source_refs'), where + '.source_refs', report)
        text_field(a, 'rationale', where, report)
        if not nonempty(qid): continue
        if qid in seen: report.error('duplicate_answer', where + '.question_id', 'Duplicate answer question_id.')
        seen.add(qid)
        if qid not in by_id:
            report.error('extra_answer', where + '.question_id', 'No matching public question.'); continue
        q = by_id[qid]
        kind = q.get('type')
        if kind == 'single_choice':
            option = a.get('correct_option')
            options = q.get('options')
            options = options if isinstance(options, dict) else {}
            if not nonempty(option) or option not in options:
                report.error('correct_option', where + '.correct_option', 'Correct option must name an existing option.')
            misconceptions = a.get('distractor_misconceptions')
            wrong = set(options) - ({option} if isinstance(option, str) else set())
            if not isinstance(misconceptions, dict) or set(misconceptions) != wrong or not all(nonempty(v) for v in misconceptions.values()):
                report.error('distractor_coverage', where + '.distractor_misconceptions', 'Nonempty misconception text required for exactly every wrong option.')
        elif kind == 'true_false':
            if type(a.get('expected_judgment')) is not bool:
                report.error('expected_judgment', where + '.expected_judgment', 'Expected a JSON boolean, not a number or string.')
        forbidden = ('expected_judgment',) if kind == 'single_choice' else ('correct_option', 'distractor_misconceptions') if kind == 'true_false' else ('correct_option', 'expected_judgment', 'distractor_misconceptions')
        for field in forbidden:
            if field in a: report.error('answer_type_mismatch', where + '.' + field, 'Answer field does not match this question type.')
    for qid in sorted(set(by_id) - seen):
        report.error('missing_answer', 'key.answers', 'Missing private answer for question: ' + qid)


def read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result: raise ValueError('Duplicate JSON key: ' + key)
            result[key] = value
        return result
    def constant(value):
        raise ValueError('Invalid JSON constant: ' + value)
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=pairs, parse_constant=constant)


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)


def main(argv=None):
    report = Report()
    parser = Parser(description=__doc__)
    parser.add_argument('mode', choices=['exam'])
    parser.add_argument('exam')
    parser.add_argument('--key', required=True)
    parser.add_argument('--state')
    try:
        args = parser.parse_args(argv)
        exam, key = read_json(args.exam), read_json(args.key)
        state = read_json(args.state) if args.state is not None else None
        check_exam(exam, key, report, state, args.state is not None)
    except OSError as exc:
        report.error('input_io', 'input', str(exc)); return report.finish(io=True)
    except (ValueError, UnicodeError, RecursionError) as exc:
        report.error('invalid_input', 'input', str(exc)); return report.finish()
    return report.finish()


if __name__ == '__main__':
    sys.exit(main())
