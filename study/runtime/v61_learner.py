#!/usr/bin/env python3
"""Study V6.1 learner compatibility layer.

V6.0 owns model/host execution and its workspace. This module restores the
V3.5 contract: a named cross-course profile and authoritative per-course
schema-3.0 learning evidence. Both files live OUTSIDE the installed Skill.
It preserves unfamiliar legacy fields and never converts page visits to mastery.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, os, re, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path

class LearnerError(Exception): pass

def now(): return datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
def digest(data): return hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def source_hash(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path):
    p=Path(path)
    if not p.is_file(): raise LearnerError(f'file missing: {p}')
    try:
        data=json.loads(p.read_text(encoding='utf-8'))
    except Exception as exc: raise LearnerError(f'invalid JSON {p}: {exc}') from exc
    if not isinstance(data,dict):raise LearnerError(f'expected JSON object: {p}')
    return data

def atomic(path, data, exclusive=False):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    if p.is_symlink() or p.parent.is_symlink():raise LearnerError('symlink path refused')
    content=json.dumps(data,ensure_ascii=False,indent=2,sort_keys=False)+'\n'
    if exclusive:
        try:
            with p.open('x',encoding='utf-8') as f:
                f.write(content);f.flush();os.fsync(f.fileno())
        except FileExistsError: return False
    else:
        fd,name=tempfile.mkstemp(prefix='.study-',suffix='.tmp',dir=p.parent)
        try:
            with os.fdopen(fd,'w',encoding='utf-8') as f:
                f.write(content);f.flush();os.fsync(f.fileno())
            os.replace(name,p)
        finally:
            if os.path.exists(name):os.unlink(name)
    if load(p)!=data:raise LearnerError('readback failed: '+str(p))
    return True

def safe_name(name):
    if not isinstance(name,str) or not 1<=len(name)<=80 or not re.fullmatch(r"[A-Za-z '.-]+",name) or not re.search('[A-Za-z]',name):
        raise LearnerError('Use an explicitly supplied English name (1–80 ASCII chars).')
    display=' '.join(name.split());slug=re.sub('[^a-z]+','-',display.lower()).strip('-')
    if slug in {'con','prn','aux','nul'} or re.fullmatch(r'(com|lpt)[1-9]',slug):slug='learner-'+slug
    return display,slug

def root_path(root=None):return Path(root).expanduser().resolve() if root else Path.home()/'Study'
def learner_paths(name,root=None):
    display,slug=safe_name(name);base=root_path(root)/'learners'/slug
    profile=base/'learner-profile.json'
    for p in (base.parent,base,profile):
        if p.is_symlink():raise LearnerError('symlink path refused: '+str(p))
    return display,slug,base,profile

def initialize_profile(name,root=None):
    display,slug,base,profile=learner_paths(name,root)
    if not profile.exists():
        data={'schema_version':'1.0','learner_name':display,'learner_slug':slug,'updated_at':now(),
              'goals':[],'courses':[],'background':{k:[] for k in ('domains','coding','mathematics','language')},
              'preferences':[],'teaching_observations':[]}
        atomic(profile,data,exclusive=True)
    data=load(profile)
    if data.get('learner_name') and data['learner_name'].casefold()!=display.casefold():raise LearnerError('profile name mismatch')
    if data.get('learner_slug') and data['learner_slug']!=slug:raise LearnerError('profile slug mismatch')
    if data.get('schema_version')!='1.0':raise LearnerError('unexpected profile schema (expected 1.0)')
    return {'path':str(profile),'slug':slug,'created':data.get('updated_at'),'profile':data}

def locate_profile(name,root=None):
    display,slug,base,profile=learner_paths(name,root)
    if not profile.is_file():return {'found':False,'path':str(profile),'slug':slug}
    data=load(profile)
    return {'found':True,'path':str(profile),'slug':slug,'profile':data}

def course_id_from_source(src,scope=''):
    canonical=json.dumps({'src':str(src),'scope':scope},ensure_ascii=False,sort_keys=True)
    return 'course-'+hashlib.sha256(canonical.encode()).hexdigest()[:12]

def initial_course(course_id,source='',scope=''):
    return {'schema_version':'3.0','course_id':course_id,'sources':[],
            'active_scope':{'id':'scope-001','source_ids':[],'boundaries':scope,'inventory_complete':False,'gaps':[]},
            'learning_points':[],'units':[],'artifacts':[],'evidence':[],
            'navigation':{'current_unit_index':0,'main_return':None,'deep_branch':None},
            'chapter_summaries':[],
            'intake':{'goal':None,'map_reviewed':False,'familiarity':None,'finalized':False},
            'updated_at':now()}

def bind_workspace(workspace,name,root=None,course_id=None,scope='',source='',temporary=False):
    """Bind V6 runtime workspace without altering established V3.5 course identity."""
    w=Path(workspace).expanduser().resolve();w.mkdir(parents=True,exist_ok=True)
    pointer=w/'v61-binding.json'
    if pointer.exists():
        old=load(pointer)
        if not temporary and name and old.get('name','').casefold()!=name.casefold():raise LearnerError('workspace already belongs to another learner')
        if old.get('temporary') and not temporary:raise LearnerError('explicit migration from temporary to named storage required')
        return old
    if temporary:
        identity={'schema_version':'6.1','temporary':True,'name':None,'profile_path':None,
                  'course_state_path':str(w/'study-state.json'),'course_id':course_id or course_id_from_source(source or w,scope),
                  'workspace':str(w),'created_at':now()}
    else:
        if not name:raise LearnerError('First use requires an English learner name, or explicit --temporary. Reuse an existing named profile; do not infer from OS.')
        p=initialize_profile(name,root); slug=p['slug'];base=Path(p['path']).parent
        chosen=course_id or course_id_from_source(source or w,scope)
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,100}',chosen):raise LearnerError('invalid course_id')
        state_path=base/'courses'/chosen/'study-state.json'
        identity={'schema_version':'6.1','temporary':False,'name':name,'profile_path':str(p['path']),
                  'course_state_path':str(state_path),'course_id':chosen,'workspace':str(w),'created_at':now()}
    state_path=Path(identity['course_state_path']); state_path.parent.mkdir(parents=True,exist_ok=True)
    if not state_path.exists():atomic(state_path,initial_course(identity['course_id'],source,scope),exclusive=True)
    data=load(state_path)
    if data.get('schema_version')!='3.0' or data.get('course_id')!=identity['course_id']:
        raise LearnerError('existing course state identity/schema mismatch; no overwrite')
    if not identity['temporary']:
        profile=load(identity['profile_path']);courses=profile.setdefault('courses',[])
        if not any(c.get('course_id')==identity['course_id'] for c in courses):
            courses.append({'course_id':identity['course_id'],'title':scope or 'Untitled Study course',
                            'state_ref':str(state_path)})
            profile['updated_at']=now();atomic(identity['profile_path'],profile)
    atomic(pointer,identity,exclusive=True)
    return identity

def binding(workspace):
    p=Path(workspace)/'v61-binding.json'
    if not p.exists():raise LearnerError('workspace not bound: run /study with --learner-name, or explicitly --temporary')
    b=load(p)
    if b.get('schema_version')!='6.1':raise LearnerError('unknown binding revision')
    return b

def course(workspace):return load(binding(workspace)['course_state_path'])
def save_course(workspace,data):
    b=binding(workspace);old=load(b['course_state_path'])
    if old.get('course_id')!=data.get('course_id') or data.get('schema_version')!='3.0':raise LearnerError('course identity mismatch')
    data['updated_at']=now();atomic(b['course_state_path'],data);return data

def update_intake(workspace,goal=None,familiarity=None,map_reviewed=False,declined=False):
    """V3.5 startup order: name -> goal -> preliminary knowledge map ->
    prerequisite/target familiarity -> final overview. Self-reports never certify mastery.
    """
    w=Path(workspace);b=binding(w);d=course(w)
    if b.get('temporary'):
        return {'temporary':True,'finalized':True,'persistence':'workspace only'}
    intake=d.setdefault('intake',{'goal':None,'map_reviewed':False,'familiarity':None,'finalized':False})
    if goal is not None:
        if not isinstance(goal,str) or not goal.strip():raise LearnerError('learning goal must be nonempty')
        intake['goal']=goal.strip()
    if map_reviewed:
        if not (w/'overview.html').exists():raise LearnerError('preliminary map must exist before marking reviewed')
        intake['map_reviewed']=True
    if familiarity is not None:
        if not intake.get('map_reviewed'):raise LearnerError('show preliminary map before collecting target/prerequisite familiarity')
        if not isinstance(familiarity,str) or not familiarity.strip():raise LearnerError('familiarity must be meaningful or explicitly declined')
        intake['familiarity']={'statement':familiarity.strip(),'basis':'learner_report','observed_at':now()}
    elif declined:
        if not intake.get('map_reviewed'):raise LearnerError('show preliminary map before declining familiarity')
        intake['familiarity']={'statement':'declined','basis':'learner_report','observed_at':now()}
    intake['finalized']=bool(intake.get('goal') and intake.get('map_reviewed') and intake.get('familiarity'))
    save_course(w,d)
    if intake['finalized']:
        profile=load(b['profile_path'])
        key={'statement':intake['goal'],'scope':d['course_id'],'basis':'learner_report','source_ref':str(w/'overview.html')}
        if not any(g.get('scope')==key['scope'] and g.get('statement')==key['statement'] for g in profile.setdefault('goals',[])):
            profile['goals'].append(key)
        # A learner's familiarity is a self-report, never a mastery estimate.
        bg=profile.setdefault('background',{}).setdefault('domains',[])
        item={'statement':intake['familiarity']['statement'],'scope':d['course_id'],
              'basis':'learner_report','source_ref':str(w/'overview.html'),'observed_at':now()}
        if item not in bg:bg.append(item)
        profile['updated_at']=now();atomic(b['profile_path'],profile)
    return {'finalized':intake['finalized'],'next':'study-n' if intake['finalized'] else 'complete goal, review map, and give familiarity'}

def require_ready(workspace):
    b=binding(workspace)
    if b.get('temporary'):return True
    d=course(workspace);intake=d.get('intake',{})
    if not intake.get('finalized'):
        raise LearnerError('first-use not finalized: confirm learning goal, review the overview, and provide or decline relevant familiarity before /study-n')
    return True

def sync_plan(workspace):
    """Map frozen V6 LPs/Units into V3.5 course state without destroying evidence."""
    w=Path(workspace);b=binding(w);plan_path=w/'plan.json';source_path=w/'source.json'
    if not plan_path.exists() or not source_path.exists():return {'synced':False,'reason':'plan/source missing'}
    plan=load(plan_path);src=load(source_path);d=course(w)
    revision=src.get('source_sha256','unknown');origin=src.get('origin') or src.get('source') or 'bounded-source'
    if not any(x.get('source_id')=='src-v6' and x.get('source_revision')==revision for x in d['sources']):
        d['sources'].append({'source_id':'src-v6','source_revision':revision,'origin':str(origin)})
    scope=d.setdefault('active_scope',{})
    scope.update({'source_ids':['src-v6'],'inventory_complete':True,'gaps':[]})
    scope.setdefault('boundaries','current requested source scope')
    old_lp={x['id']:x for x in d.get('learning_points',[]) if 'id' in x}
    for p in plan.get('points',[]):
        pid=p['lp_id'];entry=old_lp.get(pid)
        if entry is None:
            entry={'id':pid,'title':p.get('title',''),'objective':p.get('goal',''),
                   'source_anchors':[],'prerequisites':{'hard':[],'soft':[]},'misconceptions':[],
                   'learning_status':'unassessed','assessment':None,'evidence_ids':[],'revision_review_needed':False}
            d.setdefault('learning_points',[]).append(entry);old_lp[pid]=entry
        entry['title']=p.get('title',entry.get('title',''));entry['objective']=p.get('goal',entry.get('objective',''))
        anchor={'source_id':'src-v6','source_revision':revision,'anchor':','.join(p.get('source_span_ids',[]))}
        anchors=entry.setdefault('source_anchors',[])
        if anchor not in anchors:anchors.append(anchor)
        if entry.get('source_anchors') and any(a.get('source_revision') not in (revision,'unknown') for a in anchors):
            entry['revision_review_needed']=True
        entry.setdefault('prerequisites',{'hard':[],'soft':[]})['hard']=p.get('prerequisites',[])
    units={u['id']:u for u in d.get('units',[]) if 'id' in u}
    for page in plan.get('pages',[]):
        uid=page['page_id'];entry=units.get(uid)
        if entry is None:
            entry={'id':uid,'title':page.get('title',''),'lp_ids':page.get('lp_ids',[]),
                   'route_status':'not_started','artifact_ids':[],'source_coverage':[]}
            d.setdefault('units',[]).append(entry);units[uid]=entry
        entry.update(title=page.get('title',''),lp_ids=page.get('lp_ids',[]))
    # Existing course navigation is authoritative only when it has a saved valid cursor.
    nav=d.setdefault('navigation',{})
    host_path=w/'state.json'
    host=load(host_path) if host_path.exists() else {}
    runtime_cursor=int(host.get('current_unit',0));legacy_cursor=nav.get('current_unit_index')
    if isinstance(legacy_cursor,int) and legacy_cursor>runtime_cursor and legacy_cursor<=len(plan.get('pages',[])):
        host['current_unit']=legacy_cursor
        atomic(host_path,host);runtime_cursor=legacy_cursor
    nav['current_unit_index']=runtime_cursor
    d.setdefault('v61_runtime',{})['plan_sha256']=digest(plan)
    d['v61_runtime']['source_sha256']=revision
    save_course(w,d)
    return {'synced':True,'learning_points':len(plan.get('points',[])), 'units':len(plan.get('pages',[])), 'course_id':b['course_id'],'cursor':runtime_cursor}

def mark_unit_delivered(workspace,unit_index,artifact_path=None):
    w=Path(workspace);d=course(w);plan=load(w/'plan.json');pages=plan.get('pages',[])
    if not 1<=unit_index<=len(pages):raise LearnerError('invalid unit index')
    page=pages[unit_index-1];uid=page['page_id'];artifact_id=f'artifact-{uid}'
    for item in d.get('units',[]):
        if item['id']==uid:
            item['route_status']='delivered' if item.get('route_status')!='legacy_completed' else 'legacy_completed'; a=item.setdefault('artifact_ids',[])
            if artifact_id not in a:a.append(artifact_id)
    nav=d.setdefault('navigation',{});nav['current_unit_index']=max(nav.get('current_unit_index',0),unit_index)
    if artifact_path:
        artifact=Path(artifact_path);value={'id':artifact_id,'revision':1,'kind':'unit','lp_ids':page['lp_ids'],
          'unit_ids':[uid],'generation_status':'verified' if artifact.exists() else 'failed',
          'delivery_status':'delivered','reference':str(artifact.resolve()),
          'availability':'available' if artifact.exists() else 'missing',
          'source_refs':[],'provenance':'newly_generated','sha256':source_hash(artifact) if artifact.exists() else None}
        lst=d.setdefault('artifacts',[])
        lst[:]=[x for x in lst if x.get('id')!=artifact_id];lst.append(value)
    save_course(w,d)
    return {'unit':uid,'cursor':nav['current_unit_index'],'mastery_changed':False}

def mark_artifact(workspace,kind,artifact_path,topic='',lp_ids=None):
    w=Path(workspace);d=course(w);p=Path(artifact_path)
    if not p.is_file():raise LearnerError('artifact missing: '+str(p))
    artifact_id='artifact-'+hashlib.sha256(str(p.resolve()).encode()).hexdigest()[:12]
    item={'id':artifact_id,'revision':1,'kind':kind,'lp_ids':lp_ids or [],'unit_ids':[],
          'generation_status':'verified','delivery_status':'not_delivered',
          'reference':str(p.resolve()),'availability':'available','provenance':'newly_generated',
          'sha256':source_hash(p),'topic':topic}
    lst=d.setdefault('artifacts',[]);lst[:]=[x for x in lst if x.get('id')!=artifact_id];lst.append(item)
    save_course(w,d)
    return {'artifact_id':artifact_id,'mastery_changed':False}


def confirm_artifact_delivery(workspace,artifact_path):
    """Mark a generated explanation or quiz delivered only on a host receipt."""
    w=Path(workspace);candidate=Path(artifact_path).resolve()
    if not candidate.is_file():raise LearnerError('artifact missing before confirmation')
    d=course(w)
    entry=next((a for a in d.get('artifacts',[])
        if a.get('kind') in ('explanation','quiz') and a.get('reference')==str(candidate)),None)
    if entry is None:raise LearnerError('artifact has no registered delivery record')
    if entry.get('sha256')!=source_hash(candidate):
        raise LearnerError('artifact hash changed before confirmation')
    if entry.get('delivery_status')=='delivered':
        return {'confirmed':True,'duplicate':True,'artifact_id':entry['id']}
    entry['delivery_status']='delivered'
    save_course(w,d)
    return {'confirmed':True,'duplicate':False,'artifact_id':entry['id']}


def record_assessment(workspace,lp_id,actual_answer,rubric,outcome,question_id,answer_source,assistance='independent',reviewed=False,source_ref=None):
    """A learner's actual answer and reviewed rubric, never an inferred click/view."""
    if not actual_answer or not rubric or not outcome or not question_id or not answer_source:
        raise LearnerError('assessment requires actual answer, rubric, outcome, question ID and answer source')
    if assistance not in ('independent','hinted','after_reveal'):raise LearnerError('invalid assistance level')
    w=Path(workspace);d=course(w)
    lp=next((x for x in d.get('learning_points',[]) if x.get('id')==lp_id),None)
    if not lp:raise LearnerError('unknown LP '+lp_id)
    eid='e-'+hashlib.sha256((lp_id+'|'+question_id+'|'+answer_source+'|'+actual_answer).encode()).hexdigest()[:16]
    if any(x.get('id')==eid for x in d.get('evidence',[])):return {'evidence_id':eid,'duplicate':True}
    entry={'id':eid,'lp_ids':[lp_id],'artifact_id':None,'artifact_revision':None,'question_id':question_id,
      'question_revision':1,'actual_answer':actual_answer,'answer_source':answer_source,'rubric':rubric,
      'outcome':outcome,'assistance':assistance,'reviewed':bool(reviewed),'source_ref':source_ref,'recorded_at':now()}
    d.setdefault('evidence',[]).append(entry);lp.setdefault('evidence_ids',[]).append(eid)
    good=bool(reviewed and assistance=='independent' and outcome in ('understood','applied'))
    if good:
        old=lp.get('learning_status','unassessed')
        rank={'unassessed':0,'attempted':1,'understood':2,'applied':3}
        if rank.get(outcome,0)>rank.get(old,0):lp['learning_status']=outcome
    elif lp.get('learning_status')=='unassessed':lp['learning_status']='attempted'
    save_course(w,d)
    return {'evidence_id':eid,'lp_status':lp.get('learning_status'),'mastery_promoted':good}

def update_chapter_summary(workspace,chapter_id='current',source_ref=None):
    """Derived course summary then matching profile snapshot, preserving evidence authority."""
    w=Path(workspace);b=binding(w);d=course(w)
    statuses={'unassessed':0,'attempted':0,'understood':0,'applied':0}
    for p in d.get('learning_points',[]):
        s=p.get('learning_status','unassessed');statuses[s]=statuses.get(s,0)+1
    snapshot={'chapter_id':chapter_id,'course_id':d['course_id'],'lp_status_counts':statuses,
      'evidence_ids':[x['id'] for x in d.get('evidence',[])],
      'unresolved_lp_ids':[p['id'] for p in d.get('learning_points',[]) if p.get('learning_status') not in ('understood','applied')],
      'source_ref':source_ref,'updated_at':now()}
    arr=d.setdefault('chapter_summaries',[])
    arr[:]=[x for x in arr if x.get('chapter_id')!=chapter_id];arr.append(snapshot)
    save_course(w,d)
    if not b['temporary']:
        p=load(b['profile_path']);entries=p.setdefault('courses',[])
        row=next((x for x in entries if x.get('course_id')==d['course_id']),None)
        if row is None:raise LearnerError('bound course missing from profile')
        row['chapter_summary']=copy.deepcopy(snapshot);p['updated_at']=now();atomic(b['profile_path'],p)
        if load(b['profile_path'])['courses'][entries.index(row)]['chapter_summary']!=snapshot:
            raise LearnerError('profile summary readback mismatch')
    return {'chapter_id':chapter_id,'summary':snapshot,'profile_updated':not b['temporary']}

def recover(workspace):
    w=Path(workspace);b=binding(w);d=course(w);nav=d.get('navigation',{})
    hostpath=w/'state.json';host=load(hostpath) if hostpath.exists() else {}
    rev=d.get('v61_runtime',{}).get('source_sha256')
    source=w/'source.json'
    if source.exists() and rev and rev!=load(source).get('source_sha256'):
        return {'status':'source_changed','requires_new_plan':True,'learner':b.get('name')}
    plan=w/'plan.json';count=len(load(plan).get('pages',[])) if plan.exists() else None
    cursor=nav.get('current_unit_index',0)
    if not isinstance(cursor,int) or cursor<0 or (count is not None and cursor>count):
        raise LearnerError('invalid saved unit cursor; manual inspection required')
    if cursor>host.get('current_unit',0):
        host['current_unit']=cursor;atomic(hostpath,host)
    return {'status':'resumed','learner':b.get('name'),'course_id':b['course_id'],
      'current_unit_index':max(cursor,host.get('current_unit',0)),
      'deep_branch':nav.get('deep_branch'),'learning_points':len(d.get('learning_points',[])),
      'evidence':len(d.get('evidence',[]))}

def deep_branch(workspace,module_workspace,topic,return_unit=None,next_page=0):
    """Resume a matching Study-D branch without resetting its delivery cursor."""
    w=Path(workspace).resolve();module=Path(module_workspace).resolve()
    if module == w or not module.is_relative_to(w):
        raise LearnerError('deep branch must be strictly inside the same course workspace')
    if not isinstance(next_page,int) or next_page<0:
        raise LearnerError('invalid deep page cursor')
    d=course(w);nav=d.setdefault('navigation',{})
    existing=nav.get('deep_branch')
    if existing:
        prior=Path(existing.get('workspace','')).resolve()
        if prior == module:
            if existing.get('topic')!=topic:
                raise LearnerError('deep workspace is already associated with another topic')
            # Preserve pending/delivering/paused/completed and the original return point.
            # Only explicit delivery confirmation may advance next_page.
            return existing
        if existing.get('status') in ('pending','delivering','paused'):
            raise LearnerError('another deep branch is active; pause or finish it first')
    item={'topic':topic,'workspace':str(module),'next_page':next_page,
          'main_return':return_unit if return_unit is not None else nav.get('current_unit_index',0),
          'status':'pending'}
    nav['deep_branch']=item
    save_course(w,d)
    return item

def main(argv=None):
    p=argparse.ArgumentParser(description='Study V6.1 learner profile and course evidence commands')
    p.add_argument('command',choices=('locate','init','bind','intake','sync-plan','delivered','artifact','assess','summary','recover','status'))
    p.add_argument('--name',default='');p.add_argument('--root');p.add_argument('--workspace');p.add_argument('--course-id')
    p.add_argument('--scope',default='');p.add_argument('--source',default='');p.add_argument('--temporary',action='store_true')
    p.add_argument('--goal');p.add_argument('--familiarity');p.add_argument('--map-reviewed',action='store_true');p.add_argument('--decline-familiarity',action='store_true')
    p.add_argument('--unit',type=int,default=0);p.add_argument('--file');p.add_argument('--kind',default='unit');p.add_argument('--topic',default='')
    p.add_argument('--lp-id');p.add_argument('--answer');p.add_argument('--rubric');p.add_argument('--outcome');p.add_argument('--question-id');p.add_argument('--answer-source');p.add_argument('--assistance',default='independent');p.add_argument('--reviewed',action='store_true')
    args=p.parse_args(argv)
    try:
        cmd=args.command
        if cmd=='locate':result=locate_profile(args.name,args.root)
        elif cmd=='init':result=initialize_profile(args.name,args.root)
        elif cmd=='bind':result=bind_workspace(args.workspace,args.name,args.root,args.course_id,args.scope,args.source,args.temporary)
        elif cmd=='intake':result=update_intake(args.workspace,args.goal,args.familiarity,args.map_reviewed,args.decline_familiarity)
        elif cmd=='sync-plan':result=sync_plan(args.workspace)
        elif cmd=='delivered':result=mark_unit_delivered(args.workspace,args.unit,args.file)
        elif cmd=='artifact':result=mark_artifact(args.workspace,args.kind,args.file,args.topic)
        elif cmd=='assess':result=record_assessment(args.workspace,args.lp_id,args.answer,args.rubric,args.outcome,args.question_id,args.answer_source,args.assistance,args.reviewed)
        elif cmd=='summary':result=update_chapter_summary(args.workspace,args.scope or 'current')
        elif cmd=='recover':result=recover(args.workspace)
        else:
            b=binding(args.workspace);d=course(args.workspace)
            result={'binding':b,'course':{'course_id':d['course_id'],'learning_points':len(d.get('learning_points',[])),
              'units':len(d.get('units',[])),'evidence':len(d.get('evidence',[])), 'current_unit':d.get('navigation',{}).get('current_unit_index')}}
        print(json.dumps({'ok':True,'result':result},ensure_ascii=False,indent=2))
    except Exception as e:
        print(json.dumps({'ok':False,'error':str(e)},ensure_ascii=False),file=sys.stderr);sys.exit(2)
if __name__=='__main__':main()
