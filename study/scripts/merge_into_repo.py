#!/usr/bin/env python3
"""Safely overlay V6.4 host-native Study Skill onto an EXISTING V3.5 Study Git repository.
Default is dry-run. Every historical V3.5 path except the entrypoint is kept
byte-for-byte; V6.4 runtime and new references are additive. No git push.
"""
from __future__ import annotations
import argparse,hashlib,json,shutil,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PROTECTED=[
 'study/agents/openai.yaml','study/assets/icon.svg',
 'study/references/first-use.md','study/references/learner-adaptation.md',
 'study/references/learning-loop.md','study/references/runtime-checks.md',
 'study/references/state-commands.md','study/references/review-quiz.md',
 'study/references/unit-teaching.md','study/references/source-planning.md',
 'study/references/source-adapters.md','study/references/consolidation.md',
 'study/references/visual-output.md','study/references/visual-semantics.md',
 'study/references/writing-clarity.md','study/references/interaction-design.md',
 'study/references/presentation-qa.md',
 'study/schemas/learner-profile.md','study/schemas/learning-point.md',
 'study/schemas/source-model.md',
 'study/scripts/study_home.py','study/scripts/study_check.py',
 'study/scripts/study_quiz_check.py'
]

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def plan(repo):
    repo=Path(repo).expanduser().resolve()
    if not (repo/'study/SKILL.md').exists() or not (repo/'study/references/first-use.md').exists():
        raise ValueError('target must be an existing Study V3.5 repository checkout (study/SKILL.md and first-use.md required)')
    original={rel:sha(repo/rel) for rel in PROTECTED if (repo/rel).exists()}
    actions=[]
    for src in ROOT.rglob('*'):
        if not src.is_file() or '__pycache__' in src.parts or src.suffix=='.pyc':continue
        rel='study/'+str(src.relative_to(ROOT)).replace('\\','/')
        if rel in PROTECTED:continue
        if rel in ('study/README.md','study/V5_VALIDATION_REPORT.md','study/V6_VALIDATION_REPORT.md','study/VALIDATION_REPORT.md'):continue
        dst=repo/rel
        if dst.exists() and rel!='study/SKILL.md' and not rel.startswith('study/runtime/'):
            # Keep all original docs/assets. New V6.4-specific refs are different names.
            continue
        if dst.is_file() and sha(src)==sha(dst):continue
        actions.append({'operation':'replace' if dst.exists() else 'add','path':rel})
    return repo,original,actions

def apply(repo,original,actions):
    for a in actions:
        rel=a['path'];src=ROOT/rel.removeprefix('study/');dst=repo/rel
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,dst)
    # Update public version notices by focused edits, while keeping explanatory V3.5 documentation.
    for rel in ('README.md','README.en.md'):
        path=repo/rel
        if not path.exists():continue
        text=path.read_text(encoding='utf-8')
        if 'V6.4 Host-Native Study' not in text:
            addition=('> **V6.4 Host-Native Study**：直接使用当前 Codex/DSH 模型，保留 V3.5 学习者档案、学习证据及进度恢复。\n\n'
                      if rel=='README.md' else '> **V6.4 Host-Native Study:** Uses the current Codex/DSH session model with learner profiles, evidence and recovery.\n\n')
            text=addition+text
            text=text.replace('版本-V3.5','版本-V6.4').replace('Version-V3.5','Version-V6.4')
            text=text.replace('好好学习（Study V3.5）','好好学习（Study V6.4）').replace('本项目当前为 **V3.5**','本项目当前为 **V6.4**')
            path.write_text(text,encoding='utf-8')
    for rel,prior in original.items():
        if sha(repo/rel)!=prior:raise RuntimeError('protected V3.5 file mutated: '+rel)
    return True

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',required=True);ap.add_argument('--apply',action='store_true')
    a=ap.parse_args()
    try:
        repo,protected,actions=plan(a.repo)
        if a.apply:apply(repo,protected,actions)
        print(json.dumps({'ok':True,'applied':a.apply,'repo':str(repo),'protected_v35_files':len(protected),
          'changes':actions,'new_version':'6.2','note':'Review git diff and run tests; no commit/push performed. Existing V3.5 files are preserved.'},ensure_ascii=False,indent=2))
    except Exception as exc:
        print(json.dumps({'ok':False,'error':str(exc)},ensure_ascii=False),file=sys.stderr);sys.exit(2)
if __name__=='__main__':main()
