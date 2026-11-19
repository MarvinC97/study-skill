#!/usr/bin/env python3
"""Static audit for the bundled Study skill. Does not validate generated lessons."""
from pathlib import Path
import re
import sys
import yaml
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
main=(ROOT/'SKILL.md').read_text(encoding='utf-8')
assert main.startswith('---\n'), 'YAML frontmatter missing'
front=yaml.safe_load(main.split('---',2)[1])
assert front['name']=='study' and front.get('description'), 'Invalid skill metadata'
assert len(main.splitlines())<150, 'Main skill lost progressive disclosure'
commands=['/study','/study-n','/study-e','/study-d','/study-q','/study-c','/study-m']
for command in commands:
    assert re.search(re.escape(command)+r'(?=\s|\b|<|\[|`)', main),f'Command absent: {command}'
for bad in ['/study easy','/study normal','/study deep','/study next','/study explain','/study example','/study review','/study quiz','/study status','/study source']:
    assert bad not in main, f'Unexpected old command: {bad}'
paths=set(re.findall(r'`((?:references|assets|schemas)/[^`\s]+)`', main))
for rel in sorted(paths):
    assert (ROOT/rel).is_file(),f'Broken reference: {rel}'
expected=['source-adapters.md','source-planning.md','storm-questioning.md','learning-point.md','lesson-teaching.md','state-commands.md','review-quiz.md','deep-module.md','consolidation.md','writing-clarity.md','visual-semantics.md','interaction-design.md','visual-output.md','presentation-qa.md']
for name in expected: assert (ROOT/'references'/name).is_file(),f'Missing reference {name}'
for html in (ROOT/'assets').glob('*.html'):
    soup=BeautifulSoup(html.read_text(encoding='utf-8'),'html.parser')
    assert soup.html and soup.title and soup.main, f'Invalid template structure: {html}'
    assert soup.html.get('lang')=='zh-CN',f'Missing Chinese lang: {html}'
assert 'source-core' in (ROOT/'references'/'storm-questioning.md').read_text()
assert '/study-c' in (ROOT/'references'/'consolidation.md').read_text()
assert 'overview' in (ROOT/'references'/'source-planning.md').read_text().lower()
assert 'direct-html-v1' in main
assert 'authoring_mode: "two-pass"' in main, 'New courses must use the two-pass authoring contract'
assert 'lesson-drafts/<page-id>.md' in main, 'Skill must identify the teaching manuscript artifact'
assert 'reviews/html/<page-id>.json' in main
assert 'complete HTML' in main or 'complete, readable' in main
assert (ROOT/'references'/'direct-html.md').is_file()
assert 'Codex/DSH agent' in main, 'Skill must use host model'
assert 'STUDY'+'_API_KEY' not in main, 'Study should not request an independent provider credential'
print('PASS: host-native model, 7 commands, progressive disclosure, references, HTML templates')
print('STATIC ONLY: this does not certify Agent runtime behavior, source correctness or HTML browser interaction')
