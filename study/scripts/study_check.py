#!/usr/bin/env python3
"""Read-only, stdlib-only structural study checks. Never assesses learning semantics.

Exit 0: no structural errors (inspect warnings); 1: invalid input; 2: input I/O.
References resolve relative to the containing file. No URLs are fetched, no
JavaScript/CSS is executed, and no browser, database or host service is assumed.
"""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

STATUSES = ('unassessed', 'attempted', 'understood', 'applied')
ASSISTANCE = ('independent', 'hinted', 'after_reveal', 'unknown')

class Report:
    def __init__(self, kind):
        self.data = {'kind': kind, 'errors': [], 'warnings': [], 'checked_scope': [],
                     'semantic_validation': 'NOT_CHECKED',
                     'not_checked': ['answer correctness, rubric sufficiency, source fidelity, learner understanding',
                                     'browser rendering, computed CSS, accessibility, delivery, persistence durability']}
    def issue(self, code, location, message, warning=False):
        self.data['warnings' if warning else 'errors'].append({'code': code, 'location': location, 'message': message})
    def finish(self, io=False):
        self.data['issues'] = self.data['errors'] + self.data['warnings']
        self.data['result'] = 'IO_ERROR' if io else 'INVALID' if self.data['errors'] else 'PASS_WITH_WARNINGS' if self.data['warnings'] else 'PASS'
        print(json.dumps(self.data, ensure_ascii=False, indent=2))
        return 2 if io else 1 if self.data['errors'] else 0

def nonempty(value):
    return isinstance(value, str) and bool(value.strip())

def read_json(path):
    # Reject duplicate JSON keys rather than silently accepting the last value.
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Invalid constant: ' + x)))

def reference(value, base, report, location, availability=None):
    if value is None:
        if availability == 'available':
            report.issue('availability_conflict', location, 'Available requires an actual reference.')
        return
    if isinstance(value, str):
        target = value
        kind = 'url' if urlsplit(value).scheme else 'local_path'
    elif isinstance(value, dict):
        kind = value.get('type')
        target = value.get('path', value.get('value', value.get('url', value.get('id'))))
    else:
        report.issue('reference_shape', location, 'Reference must be null, string or typed object.'); return
    if not nonempty(target):
        report.issue('reference_shape', location, 'Reference needs a nonempty target.'); return
    if kind in ('local_path', 'path', 'file', 'local'):
        path = base / target
        try:
            with path.open('rb') as stream:
                stream.read(1)
        except OSError as exc:
            report.issue('reference_unavailable', location, 'Local reference unavailable: ' + str(exc), True)
            if availability not in ('missing', 'inaccessible', 'unknown'):
                report.issue('availability_gap', location, 'Record missing/inaccessible/unknown availability; do not claim available.', True)
    else:
        report.issue('reference_not_checked', location, 'Non-local or unsupported reference type; availability NOT_CHECKED.', True)

def check_state(data, base, report, previous=None):
    report.data['checked_scope'] += ['JSON structure, IDs, internal references', 'evidence prerequisites (not correctness)', 'local artifact availability', 'cursor ordering']
    if not isinstance(data, dict):
        report.issue('state_shape', '$', 'State must be an object.'); return
    if data.get('schema_version') != '3.0':
        report.issue('state_version', 'schema_version', 'Expected course schema_version 3.0.')
    if not nonempty(data.get('course_id')):
        report.issue('course_id', 'course_id', 'Nonempty course_id required.')
    maps = {}
    for key, idkey in [('sources','source_id'), ('learning_points','id'), ('units','id'), ('artifacts','id'), ('evidence','id')]:
        records = data.get(key)
        maps[key] = {}
        if not isinstance(records, list):
            report.issue('list_shape', key, 'Required array.'); continue
        for index, record in enumerate(records):
            where = f'{key}[{index}]'
            if not isinstance(record, dict) or not nonempty(record.get(idkey)):
                report.issue('record_id', where, 'Object with nonempty ' + idkey + ' required.'); continue
            ident = record[idkey]
            if ident in maps[key]:
                report.issue('duplicate_id', where, 'Duplicate ID: ' + ident)
            maps[key][ident] = record
    def refs(value, target, where):
        if not isinstance(value, list):
            report.issue('reference_list', where, 'Expected ID array.'); return []
        for ident in value:
            if not isinstance(ident, str) or ident not in maps[target]:
                report.issue('dangling_reference', where, 'Unknown ' + target + ' ID: ' + str(ident))
        return value
    def single(value, target, where):
        if value is not None:
            refs([value], target, where)
    scope = data.get('active_scope')
    if not isinstance(scope, dict) or not nonempty(scope.get('id')):
        report.issue('scope_shape', 'active_scope', 'Object with scope ID required.'); scope = {}
    refs(scope.get('source_ids', []), 'sources', 'active_scope.source_ids')
    for ident, lp in maps['learning_points'].items():
        status = lp.get('learning_status')
        if status not in STATUSES:
            report.issue('learning_status', ident, 'Unknown learning status.')
        evidence_ids = refs(lp.get('evidence_ids', []), 'evidence', ident + '.evidence_ids')
        for eid in evidence_ids:
            ev = maps['evidence'].get(eid, {}) if isinstance(eid, str) else {}
            if ev and (not isinstance(ev.get('lp_ids'), list) or ident not in ev['lp_ids']):
                report.issue('evidence_lp_mismatch', ident, 'Referenced evidence must include this LP.')
        prerequisites = lp.get('prerequisites', {})
        if not isinstance(prerequisites, dict):
            report.issue('prerequisite_shape', ident, 'Prerequisites must be an object.')
        else:
            for level in ('hard', 'soft'):
                refs(prerequisites.get(level, []), 'learning_points', ident + '.prerequisites.' + level)
        anchors = lp.get('source_anchors', [])
        if not isinstance(anchors, list):
            report.issue('anchor_shape', ident, 'Source anchors must be an array.')
        else:
            for anchor in anchors:
                if not isinstance(anchor, dict):
                    report.issue('anchor_shape', ident, 'Source anchor must be an object.')
                else:
                    single(anchor.get('source_id'), 'sources', ident + '.source_anchors')
        if status in ('understood', 'applied'):
            adequate = False
            for eid in evidence_ids:
                ev = maps['evidence'].get(eid, {}) if isinstance(eid, str) else {}
                evlps = ev.get('lp_ids', [])
                if (isinstance(evlps, list) and ident in evlps and nonempty(ev.get('actual_answer'))
                        and nonempty(ev.get('rubric')) and ev.get('assistance') == 'independent'
                        and ev.get('resulting_status') in (('applied',) if status == 'applied' else ('understood', 'applied'))):
                    adequate = True
            if not adequate:
                unverified_legacy = lp.get('support_status') == 'unverified'
                if unverified_legacy and isinstance(previous, dict):
                    old_records = previous.get('learning_points', [])
                    old_lp = next((x for x in old_records if isinstance(x, dict) and x.get('id') == ident), {}) if isinstance(old_records, list) else {}
                    unverified_legacy = old_lp.get('learning_status') == status
                report.issue('unverified_legacy_mastery' if unverified_legacy else 'unsupported_mastery', ident, 'Status requires matching referenced independent answer evidence, nonempty rubric and adequate resulting_status. Preserve historical labels/evidence; do not reset existing progress. Semantics NOT_CHECKED.', warning=unverified_legacy)
    for ident, ev in maps['evidence'].items():
        refs(ev.get('lp_ids', []), 'learning_points', ident + '.lp_ids')
        single(ev.get('artifact_id'), 'artifacts', ident + '.artifact_id')
        if ev.get('assistance') not in ASSISTANCE:
            report.issue('assistance', ident, 'Assistance must be independent/hinted/after_reveal/unknown.')
        if ev.get('resulting_status') in ('understood', 'applied') and ev.get('assistance') != 'independent':
            report.issue('assisted_mastery_claim', ident, 'Assisted or unknown-assistance evidence cannot claim understood/applied, even when the LP is not promoted. Preserve historical evidence separately; do not silently rewrite it.')
        if ev.get('resulting_status') not in STATUSES:
            report.issue('evidence_status', ident, 'Invalid resulting_status.')
        if not nonempty(ev.get('actual_answer')):
            report.issue('empty_answer', ident, 'Evidence needs a nonempty actual answer.')
        aid = ev.get('artifact_id')
        artifact = maps['artifacts'].get(aid) if isinstance(aid, str) else None
        if artifact and ev.get('artifact_revision') is not None and ev['artifact_revision'] != artifact.get('revision'):
            report.issue('historical_revision', ident, 'Evidence references another artifact revision; historical availability NOT_CHECKED.', True)
    for ident, unit in maps['units'].items():
        refs(unit.get('lp_ids', []), 'learning_points', ident + '.lp_ids')
        refs(unit.get('artifact_ids', []), 'artifacts', ident + '.artifact_ids')
    for ident, artifact in maps['artifacts'].items():
        refs(artifact.get('lp_ids', []), 'learning_points', ident + '.lp_ids')
        refs(artifact.get('unit_ids', []), 'units', ident + '.unit_ids')
        if artifact.get('reference') is None and artifact.get('generation_status') in ('generated', 'verified'):
            report.issue('artifact_reference_missing', ident, 'Generated artifact has no reference; availability NOT_CHECKED.', True)
        reference(artifact.get('reference'), base, report, ident + '.reference', artifact.get('availability'))
    qa = data.get('qa_records', [])
    if not isinstance(qa, list):
        report.issue('qa_shape', 'qa_records', 'Expected array.')
    else:
        for index, record in enumerate(qa):
            if not isinstance(record, dict):
                report.issue('qa_shape', f'qa_records[{index}]', 'Expected object.')
            else:
                if not nonempty(record.get('artifact_id')):
                    report.issue('qa_artifact', f'qa_records[{index}]', 'Artifact ID required.')
                else:
                    single(record['artifact_id'], 'artifacts', f'qa_records[{index}].artifact_id')
    def cursor(value, where):
        if not isinstance(value, dict):
            report.issue('cursor_shape', where, 'Cursor must be an object.'); return
        if value.get('scope_id') is not None and value.get('scope_id') != scope.get('id'):
            report.issue('cursor_scope', where, 'Cursor scope does not resolve.')
        single(value.get('unit_id'), 'units', where + '.unit_id')
        single(value.get('next_unit_id'), 'units', where + '.next_unit_id')
    if data.get('main_cursor') is not None:
        cursor(data['main_cursor'], 'main_cursor')
    branch = data.get('deep_branch')
    if branch is not None:
        if not isinstance(branch, dict):
            report.issue('branch_shape', 'deep_branch', 'Expected object or null.')
        else:
            ordered = refs(branch.get('ordered_artifact_ids', []), 'artifacts', 'deep_branch.ordered_artifact_ids')
            refs(branch.get('lp_ids', []), 'learning_points', 'deep_branch.lp_ids')
            if len(set(str(x) for x in ordered)) != len(ordered):
                report.issue('deep_duplicate', 'deep_branch', 'Ordered artifact IDs must be unique.')
            delivered = branch.get('delivery_cursor')
            nxt = branch.get('next_page')
            for field, val in [('delivery_cursor', delivered), ('next_page', nxt)]:
                if val is not None and val not in ordered:
                    report.issue('deep_cursor', 'deep_branch.' + field, 'Cursor must refer to an ordered artifact.')
            if delivered in ordered:
                index = ordered.index(delivered)
                for aid in ordered[:index + 1]:
                    art = maps['artifacts'].get(aid, {}) if isinstance(aid, str) else {}
                    if art.get('generation_status') not in ('generated', 'verified') or art.get('delivery_status') != 'delivered':
                        report.issue('unconfirmed_cursor', 'deep_branch', 'Delivery cursor exceeds confirmed generated and delivered artifacts.')
            else:
                index = -1
            expected = ordered[index + 1] if index + 1 < len(ordered) else None
            if nxt != expected:
                report.issue('deep_next', 'deep_branch.next_page', 'Next page must follow the last confirmed delivery in order.')
            if branch.get('main_return') is not None:
                cursor(branch['main_return'], 'deep_branch.main_return')
    intake = data.get('intake')
    if intake is not None:
        if not isinstance(intake, dict):
            report.issue('intake_shape', 'intake', 'Expected intake object.')
        else:
            stage = intake.get('stage')
            if stage not in ('awaiting_goal', 'awaiting_familiarity', 'ready'):
                report.issue('intake_stage', 'intake.stage', 'Unknown onboarding stage.')
            familiarity = intake.get('familiarity', [])
            if not isinstance(familiarity, list):
                report.issue('familiarity_shape', 'intake.familiarity', 'Expected scoped self-report array.')
            if stage in ('awaiting_goal', 'awaiting_familiarity'):
                main = data.get('main_cursor')
                if isinstance(main, dict) and main.get('unit_id') is not None:
                    report.issue('intake_not_ready', 'main_cursor.unit_id', 'Pending intake cannot be recorded as formal Unit teaching.')
                for uid, unit in maps['units'].items():
                    if unit.get('route_status') in ('delivered', 'passed_on'):
                        report.issue('intake_not_ready', uid, 'Pending intake cannot mark a formal Unit delivered.')
            if stage == 'ready' and not familiarity and intake.get('skipped_by_learner') is not True:
                report.issue('familiarity_missing', 'intake', 'Ready intake needs recorded relevant familiarity or an explicit learner skip; self-report is not mastery.')
            report.data['checked_scope'].append('optional intake stage and formal-lesson boundary (not truth of self-report)')
    if previous is not None:
        report.data['checked_scope'].append('historical ID/evidence preservation and status downgrade signals')
        if not isinstance(previous, dict) or previous.get('course_id') != data.get('course_id'):
            report.issue('previous_course', '--previous', 'Previous state must be an object for the same course.'); return
        for group in ('learning_points', 'evidence'):
            old = previous.get(group, [])
            if not isinstance(old, list):
                report.issue('previous_shape', '--previous.' + group, 'Expected array.'); continue
            for item in old:
                if not isinstance(item, dict) or not nonempty(item.get('id')):
                    report.issue('previous_shape', '--previous.' + group, 'Invalid historical record.'); continue
                now = maps[group].get(item['id'])
                if now is None:
                    report.issue('removed_history', group, 'Historical ID removed: ' + item['id'])
                elif group == 'evidence' and any(now.get(k) != v for k, v in item.items()):
                    report.issue('changed_history', item['id'], 'Historical evidence changed; retain the original and record corrections separately.')
                elif group == 'learning_points' and item.get('learning_status') in STATUSES and now.get('learning_status') in STATUSES:
                    if STATUSES.index(now['learning_status']) < STATUSES.index(item['learning_status']):
                        report.issue('status_downgrade', item['id'], 'Learning status downgraded; verify recorded reason/conflict and preserve prior evidence.', True)

def check_profile(data, base, report):
    report.data['checked_scope'] += ['profile 1.0 field shapes', 'no explicit global mastery scores or course LP status copies']
    if not isinstance(data, dict):
        report.issue('profile_shape', '$', 'Profile must be an object.'); return
    if data.get('schema_version') != '1.0':
        report.issue('profile_version', 'schema_version', 'Unsupported profile version; leave original intact.')
    if 'updated_at' not in data or (data['updated_at'] is not None and not nonempty(data['updated_at'])):
        report.issue('timestamp_shape', 'updated_at', 'Expected timestamp string or null.')
    for key in ('goals', 'courses', 'preferences', 'teaching_observations'):
        if not isinstance(data.get(key, [] if key in ('goals', 'courses') else None), list):
            report.issue('list_shape', key, 'Expected array.')
    background = data.get('background')
    if not isinstance(background, dict):
        report.issue('background_shape', 'background', 'Required object.'); background = {}
    groups = []
    for key in ('domains', 'coding', 'mathematics', 'language'):
        entries = background.get(key)
        if not isinstance(entries, list):
            report.issue('list_shape', 'background.' + key, 'Required array.'); continue
        groups.append(('background.' + key, entries, ('statement', 'scope', 'basis', 'source_ref', 'observed_at')))
    groups += [(key, data.get(key, []), fields) for key, fields in [
        ('preferences', ('statement', 'scope', 'source_ref', 'updated_at')),
        ('teaching_observations', ('method', 'scope', 'response', 'interpretation', 'basis', 'evidence_ref', 'confidence', 'observed_at'))]]
    for key, entries, fields in groups:
        if not isinstance(entries, list):
            continue
        for index, entry in enumerate(entries):
            where = f'{key}[{index}]'
            if not isinstance(entry, dict):
                report.issue('entry_shape', where, 'Expected object.'); continue
            for field in fields:
                if field not in entry:
                    report.issue('entry_field', where + '.' + field, 'Required entry field missing.')
            for field in ('statement', 'scope', 'method', 'response', 'interpretation'):
                if field in entry and not nonempty(entry[field]):
                    report.issue('entry_field_shape', where + '.' + field, 'Expected nonempty text.')
            for field in ('updated_at', 'observed_at'):
                if field in entry and entry[field] is not None and not nonempty(entry[field]):
                    report.issue('entry_field_shape', where + '.' + field, 'Expected timestamp string or null.')
            if 'basis' in entry:
                choices = ('learner_report', 'observed') if key.startswith('background') else ('learner_report', 'answer_evidence')
                if entry['basis'] not in choices:
                    report.issue('basis', where, 'Invalid basis.')
            if 'confidence' in entry and entry['confidence'] not in ('tentative', 'supported'):
                report.issue('confidence', where, 'Invalid confidence.')
    def forbidden(value, where='$'):
        if isinstance(value, dict):
            for key, child in value.items():
                normalized = key.lower().replace('-', '_')
                if normalized in ('global_mastery_score', 'mastery_score', 'global_mastery', 'lp_scores', 'lp_statuses', 'learning_status'):
                    report.issue('duplicated_mastery', where + '.' + key, 'Profile must not contain mastery scores or LP status copies.')
                forbidden(child, where + '.' + key)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                forbidden(child, where + '[' + str(index) + ']')
    forbidden(data)

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = []; self.text = []; self.title = []; self.styles = []; self.stack = []; self.refs = []; self.ids = set()
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs); self.tags.append((tag, attrs)); self.stack.append(tag)
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        for attr in ('href', 'src'):
            if attrs.get(attr):
                self.refs.append(attrs[attr])
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs); self.handle_endtag(tag)
    def handle_endtag(self, tag):
        if tag in self.stack:
            self.stack = self.stack[:len(self.stack) - 1 - self.stack[::-1].index(tag)]
    def handle_data(self, data):
        if 'title' in self.stack:
            self.title.append(data)
        if 'style' in self.stack:
            self.styles.append(data)
        if not any(tag in self.stack for tag in ('script', 'style', 'head')):
            self.text.append(data)

def check_artifact(path, raw, mode, report):
    report.data['checked_scope'] += ['static HTML structure and readable text', 'known unresolved placeholder patterns', 'local href/src existence and fragment IDs']
    page = Page(); page.feed(raw); page.close()
    tags = [tag for tag, attrs in page.tags]
    for required in ('html', 'head', 'title', 'body'):
        if required not in tags:
            report.issue('html_structure', required, 'Missing HTML element.')
    if not any(tag == 'html' and nonempty(attrs.get('lang')) for tag, attrs in page.tags):
        report.issue('html_language', 'html', 'Explicit nonempty lang required.')
    if not ''.join(page.title).strip() or not ''.join(page.text).strip():
        report.issue('empty_content', str(path), 'Nonempty title and readable body text required.')
    if re.search(r'\{\{[^{}]+\}\}|\[\[(?:TODO|INSERT|PLACEHOLDER)[^\]]*\]\]|\b(?:TODO|FIXME|INSERT_CONTENT_HERE)\b', raw, re.I):
        report.issue('placeholder', str(path), 'Unresolved placeholder marker found; inspect actual content.')
    if mode == 'consolidated':
        report.data['checked_scope'].append('consolidated disclosure/script/obvious CSS hiding checks (not computed style)')
        for tag, attrs in page.tags:
            if tag in ('details', 'script') or 'hidden' in attrs or (attrs.get('aria-hidden') or '').lower() == 'true' or any(key.startswith('on') for key in attrs):
                report.issue('consolidated_hidden', tag, 'Consolidated output must be static and directly visible, without details/script/hidden content.')
        css = '\n'.join(page.styles + [(attrs.get('style') or '') for tag, attrs in page.tags])
        # A dormant universal [hidden] rule is common boilerplate, not hidden content.
        # Actual hidden attributes are rejected above. Other CSS remains conservative.
        css = re.sub(r'(?<![\w.#])\[hidden\]\s*\{[^{}]*\}', '', css, flags=re.I)
        if re.search(r'(?:display\s*:\s*none|visibility\s*:\s*(?:hidden|collapse)|opacity\s*:\s*0(?:[;\s}]|$)|content-visibility\s*:\s*hidden)', css, re.I):
            report.issue('consolidated_css_hidden', 'style', 'Obvious CSS hiding found; inspect and remove hidden content.')
        if any(tag == 'link' and 'stylesheet' in (attrs.get('rel') or '').lower() for tag, attrs in page.tags):
            report.issue('external_css', 'link', 'External stylesheet visibility is NOT_CHECKED; consolidate and inspect CSS.', True)
    if any(tag == 'base' and attrs.get('href') for tag, attrs in page.tags):
        report.issue('base_url_not_checked', 'base', 'HTML base changes reference resolution; all href/src availability and fragments NOT_CHECKED.', True)
        # Do not falsely flag relative files missing under a different base.
        # Executable URL rejection remains independent of file resolution.
        for value in page.refs:
            if urlsplit(value).scheme.lower() in ('javascript', 'vbscript'):
                report.issue('unsafe_link', value, 'Executable URL not allowed.')
        return
    for value in page.refs:
        parts = urlsplit(value)
        if parts.scheme.lower() in ('javascript', 'vbscript'):
            report.issue('unsafe_link', value, 'Executable URL not allowed.'); continue
        if parts.scheme or parts.netloc:
            report.issue('external_link', value, 'Remote/data reference NOT_CHECKED; no network requests made.', True); continue
        target = path.parent / unquote(parts.path) if parts.path else path
        if not target.is_file():
            report.issue('broken_local_link', value, 'Local target missing or not a file.'); continue
        if parts.fragment:
            if target == path:
                ids = page.ids
            elif target.suffix.lower() in ('.html', '.htm'):
                try:
                    linked = Page(); linked.feed(target.read_text(encoding='utf-8')); ids = linked.ids
                except (OSError, UnicodeError):
                    report.issue('link_unavailable', value, 'Linked page inaccessible; fragment NOT_CHECKED.', True); continue
            else:
                report.issue('fragment_not_checked', value, 'Non-HTML fragment NOT_CHECKED.', True); continue
            if unquote(parts.fragment) not in ids:
                report.issue('broken_fragment', value, 'Fragment ID not found in local HTML.')

def check_loop(data, profile, report):
    report.data['checked_scope'].append('chapter summary IDs, answer references, assessed coverage and derived profile snapshot equality')
    if not isinstance(data, dict) or not isinstance(profile, dict):
        report.issue('loop_shape', '$', 'Course and profile must be objects.'); return
    if not nonempty(data.get('course_id')):
        report.issue('course_identity', 'course_id', 'Nonempty course ID required.'); return
    for key in ('learning_points', 'evidence'):
        if not isinstance(data.get(key, []), list):
            report.issue('course_collection', key, 'Expected list.'); return
    summaries = data.get('chapter_summaries', [])
    if not isinstance(summaries, list):
        report.issue('summary_shape', 'chapter_summaries', 'Expected list.'); return
    if not summaries:
        report.issue('summary_absent', 'chapter_summaries', 'No assessed chapter summary present; legacy or unassessed state, not proof of completed assessment.', True); return
    lps = {x.get('id') for x in data.get('learning_points', []) if isinstance(x, dict) and isinstance(x.get('id'), str)}
    ev = {x.get('id'): x for x in data.get('evidence', []) if isinstance(x, dict) and isinstance(x.get('id'), str)}
    by_scope = {}
    for i, s in enumerate(summaries):
        where = f'chapter_summaries[{i}]'
        if not isinstance(s, dict):
            report.issue('summary_shape', where, 'Expected object.'); continue
        for key in ('scope_id', 'goal'):
            if not nonempty(s.get(key)): report.issue('summary_field', where+'.'+key, 'Nonempty text required.')
        scope = s.get('scope_id')
        if isinstance(scope, str):
            if scope in by_scope: report.issue('duplicate_scope', where, 'One current summary per scope; retain prior evidence separately.')
            by_scope[scope] = s
        if type(s.get('revision')) is not int or s['revision'] < 1: report.issue('summary_revision', where, 'Positive integer revision required.')
        lists = {}
        for key in ('required_lp_ids','assessed_lp_ids','evidence_ids','demonstrated','pending','next_actions'):
            val = s.get(key)
            if not isinstance(val, list) or any(not nonempty(x) for x in val):
                report.issue('summary_list', where+'.'+key, 'Expected list of nonempty strings.'); lists[key]=[]
            else: lists[key]=val
        for key in ('required_lp_ids','assessed_lp_ids','evidence_ids'):
            if len(lists[key]) != len(set(lists[key])): report.issue('summary_duplicate_id', where+'.'+key, 'Duplicate IDs.')
        required, assessed = set(lists['required_lp_ids']),set(lists['assessed_lp_ids'])
        if not required or not required <= lps or not assessed <= required: report.issue('summary_lp_refs',where,'Required IDs must exist; assessed IDs must be within required scope.')
        if s.get('coverage') not in ('partial','complete'): report.issue('summary_coverage',where,'Expected partial or complete.')
        if s.get('coverage') == 'complete' and assessed != required: report.issue('coverage_overclaim',where,'Complete coverage requires all required LPs assessed; it does not mean mastery.')
        supported=set()
        for eid in lists['evidence_ids']:
            entry=ev.get(eid)
            if not entry: report.issue('summary_evidence_ref',where,'Evidence not found: '+eid); continue
            if not nonempty(entry.get('actual_answer')): report.issue('summary_answer_missing',where,'Actual answer required for assessment summary.')
            ids=entry.get('lp_ids',[])
            if isinstance(ids,list): supported.update(x for x in ids if isinstance(x,str))
        if not assessed <= supported: report.issue('summary_evidence_coverage',where,'Assessed LP lacks referenced answer evidence.')
    courses=profile.get('courses',[])
    matches=[x for x in courses if isinstance(x,dict) and x.get('course_id')==data.get('course_id')] if isinstance(courses,list) else []
    if len(matches)!=1:
        report.issue('profile_course_binding','courses','Exactly one corresponding course entry required.');return
    snapshot=matches[0].get('chapter_summary')
    if not isinstance(snapshot,dict) or not isinstance(snapshot.get('scope_id'),str):
        report.issue('profile_snapshot_missing','chapter_summary','Derived chapter snapshot missing.');return
    original=by_scope.get(snapshot['scope_id'])
    if original is None or snapshot != original: report.issue('profile_snapshot_stale','chapter_summary','Snapshot must equal the authoritative summary; do not independently edit conclusions.')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='kind', required=True)
    p = sub.add_parser('state'); p.add_argument('path', type=Path); p.add_argument('--previous', type=Path)
    p = sub.add_parser('profile'); p.add_argument('path', type=Path)
    p = sub.add_parser('loop'); p.add_argument('path', type=Path); p.add_argument('--profile', type=Path, required=True)
    p = sub.add_parser('artifact'); p.add_argument('path', type=Path); p.add_argument('--mode', choices=('unit', 'deep', 'consolidated'), default='unit'); p.add_argument('--state', type=Path)
    args = parser.parse_args(argv); report = Report(args.kind)
    try:
        if args.kind == 'loop':
            check_loop(read_json(args.path), read_json(args.profile), report)
        elif args.kind == 'artifact':
            check_artifact(args.path, args.path.read_text(encoding='utf-8'), args.mode, report)
            if args.state:
                check_state(read_json(args.state), args.state.parent, report)
        elif args.kind == 'state':
            check_state(read_json(args.path), args.path.parent, report, read_json(args.previous) if args.previous else None)
        else:
            check_profile(read_json(args.path), args.path.parent, report)
    except OSError as exc:
        report.issue('io_error', str(args.path), str(exc)); return report.finish(io=True)
    except (ValueError, UnicodeError) as exc:
        report.issue('parse_error', str(args.path), str(exc))
    return report.finish()

if __name__ == '__main__':
    sys.exit(main())
