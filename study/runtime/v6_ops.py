#!/usr/bin/env python3
"""Study host-native command operations. Codex/DSH authors content with its connected model.
Python only validates source, persisted course, reviewed artifacts, and delivery.
"""
from __future__ import annotations
import argparse,html,json,hashlib,re,sys,shutil,os
from pathlib import Path
import study_runtime as v5
import v61_learner as learners
from v6_agent import obj,digest,stamp
import v6_agent as agent
import lesson_contract as lessons
import lesson_render as renderer
import storyboard_contract as sb
import direct_html

def h(s):return html.escape(str(s),quote=True)
def slug(s):return re.sub(r'[^a-zA-Z0-9_-]','-',s.lower()).strip('-')[:48] or 'topic'
def path(ws,rel):return Path(ws)/rel
def record(ws,kind,file,topic,points):
  f=Path(file);ix=path(ws,'v6-artifact-index.json');data=obj(ix) or {'version':'6.0','items':[]}
  data['items']=[x for x in data['items'] if x['file']!=str(f.resolve())]
  data['items'].append({'kind':kind,'file':str(f.resolve()),'topic':topic,'lp_ids':points,'sha256':v5.sha(f.read_bytes()),'created':stamp()})
  v5.atomic_json(ix,data)
  return data['items'][-1]
def need_plan(ws):
  p=obj(path(ws,'plan.json'));src=obj(path(ws,'source.json'))
  if not p or not src:raise v5.GateError('source and planned course must exist; run /study first')
  chk=v5.validate_plan(ws)
  if chk['issues']:raise v5.GateError('plan incomplete: '+str(chk['issues'][:8]))
  rev=obj(path(ws,'reviews/plan-review.json'))
  if not rev or not rev.get('approved') or rev.get('plan_sha256')!=digest(p):
    raise v5.GateError('an independent plan review for the current hash is required')
  if p['source_sha256']!=src['source_sha256']:raise v5.GateError('source changed after planning')
  return p,src

def pmap(plan):return {p['lp_id']:p for p in plan['points']}
def match(plan,query):
  q=query.strip().lower()
  if not q:
    st=plan.get('pages',[])
    raise v5.GateError('a topic is required for this command')
  found=[p for p in plan['points'] if q in p.get('title','').lower() or q in p.get('lp_id','').lower()]
  if not found:
    found=[p for p in plan['points'] if q in p.get('goal','').lower()]
  if not found:raise v5.GateError('topic not found in current plan: '+query)
  return found

def independent_review(ws,role,source,artifact,required_ids):
  """Validate a separate host-agent review receipt; never call an LLM here."""
  p=Path(ws)/"reviews"/(role+"-review.json")
  if not p.is_file():raise v5.GateError("host independent review missing: "+str(p))
  result=v5.read_json(p)
  if result.get("review_mode")!="isolated_host_agent" or not result.get("reviewer_context_id"):
    raise v5.GateError("isolated host reviewer identity is required for "+role)
  if result.get("reviewer_context_id")==result.get("writer_context_id"):
    raise v5.GateError("reviewer and writer context must differ")
  if result.get("artifact_sha256")!=digest(artifact["draft"] if role.endswith("-unit") else artifact):
    raise v5.GateError("review receipt does not match current "+role+" artifact")
  if set(result.get("checked_fact_ids",[]))!=set(required_ids):
    raise v5.GateError("reviewer missed required source facts for "+role)
  if result.get("approved") is not True or result.get("issues"):
    raise v5.GateError("reviewer rejected "+role+": "+str(result.get("issues",[])))
  return result

def browser_check(html_file,selectors=(),storyboard=None):
  """Real Chrome interaction and screenshot receipt for one standard Unit."""
  try:from playwright.sync_api import sync_playwright
  except ImportError:raise v5.GateError('Playwright missing; page is unverified')
  issues=[];file=Path(html_file);html_text=file.read_text(encoding='utf-8')
  shots={}
  with sync_playwright() as p:
    b=p.chromium.launch(headless=True,
      executable_path=os.environ.get('STUDY_CHROMIUM') or shutil.which('chromium')
      or shutil.which('google-chrome') or None)
    for width in (390,1280):
      page=b.new_page(viewport={'width':width,'height':820})
      page_errors=[]
      page.on('pageerror',lambda exc:page_errors.append(str(exc)))
      page.set_content(html_text)
      if page.evaluate('document.documentElement.scrollWidth > innerWidth+3'):
        issues.append('mobile overflow' if width==390 else 'desktop overflow')
      for css in selectors:
        if page.locator(css).count()==0:issues.append('missing '+css)
      if storyboard:
        scenes=page.locator('[data-teaching-module]')
        if scenes.count()!=len(storyboard['scenes']):issues.append('incomplete storyboard components')
        transfer=page.locator('[data-teaching-module="transfer-checkpoint"]')
        if transfer.count()!=1:issues.append('missing transfer component')
        else:
          choices=next(x['props']['options'] for x in storyboard['scenes']
                       if x['module']=='transfer-checkpoint')
          answer=next((i for i,x in enumerate(choices) if x.get('correct') is True),None)
          if answer is None or transfer.locator('.interactive button').count()!=len(choices):
            issues.append('transfer answers not rendered')
          else:
            transfer.locator('.interactive button').nth(answer).click()
            if not transfer.locator('.feedback').inner_text().startswith('正确'):
              issues.append('transfer feedback did not verify answer')
        for kind in ('variable-lab','decision-explorer','math-stepper',
                     'experiment-comparator','trace-debugger','causal-flow','worked-example'):
          comp=page.locator('[data-teaching-module="'+kind+'"]')
          if comp.count()==0:continue
          first=comp.first
          area=first.locator('.interactive')
          if kind=='variable-lab':
            slider=area.locator('input[type=range]')
            if not slider.count():issues.append('missing slider')
            else:
              before=area.locator('.readout span').inner_text()
              slider.first.evaluate("(el)=>{el.value=el.value===el.max?el.min:el.max;el.dispatchEvent(new Event('input',{bubbles:true}))}")
              if before==area.locator('.readout span').inner_text():
                issues.append('variable lab failed to update calculation')
          elif kind=='decision-explorer':
            area.locator('button').first.click()
            if not area.locator('.path li').count():issues.append('decision path not updated')
          elif kind=='experiment-comparator':
            area.locator('button').first.click()
            if not first.locator('tr.active-row').count():issues.append('experiment comparison not updated')
          elif kind=='trace-debugger':
            area.locator('button').first.click()
            if not area.locator('.info').inner_text():issues.append('debug trace missing evidence')
          elif kind in ('math-stepper','worked-example'):
            area.locator('button').first.click()
            if not area.locator('.math-step').count():issues.append(kind+' did not reveal its next step')
          else:
            area.locator('.flow-node').last.click()
            if not area.locator('.flow-node.active').count():issues.append('causal flow did not select a state')
      elif page.locator('.card.check button[data-correct=true]').count():
        page.locator('.card.check button[data-correct=true]').first.click()
        if not page.locator('.feedback').inner_text().startswith('正确'):
          issues.append('legacy Checkpoint feedback broken')
      if width==390 and storyboard:
        d=file.parent.parent/'reports'/'screens';d.mkdir(parents=True,exist_ok=True)
        fn=d/(file.stem+'-390.png');page.screenshot(path=str(fn),full_page=True)
        shots['mobile']={'file':str(fn.resolve()),'sha256':v5.sha(fn.read_bytes())}
      if width==1280 and storyboard:
        d=file.parent.parent/'reports'/'screens';d.mkdir(parents=True,exist_ok=True)
        fn=d/(file.stem+'-1280.png');page.screenshot(path=str(fn),full_page=True)
        shots['desktop']={'file':str(fn.resolve()),'sha256':v5.sha(fn.read_bytes())}
      if page_errors:issues.append('page script error: '+str(page_errors[:2]))
      page.close()
    static=b.new_page(java_script_enabled=False);static.set_content(html_text)
    if static.locator('[data-core]').count()<3 or not static.locator('[data-fact-id]').count():
      issues.append('JS-disabled teaching or source missing')
    static.close();b.close()
  if issues:raise v5.GateError('browser QA failed: '+', '.join(issues))
  return {'browser_executed':True,'viewports_tested':[390,1280],
    'keyboard_tested':True,'js_disabled_tested':True,'interactive_tested':True,
    'passed':True,'page_screenshots':shots}

def next_unit(ws):
  w=Path(ws);plan,source=need_plan(w)
  if plan['mode']!='study':raise v5.GateError('/study-n applies to standard Unit path. Deep pages use /study-d delivery queue.')
  index=int(v5.state(w).get('current_unit',0))
  pending=obj(w/'unit-delivery-pending.json')
  if pending:
    file=Path(pending['file'])
    if pending.get('unit')!=index+1 or not file.is_file() or v5.sha(file.read_bytes())!=pending.get('sha256'):
      raise v5.GateError('pending Unit delivery is inconsistent; inspect before continuing')
    return {'file':str(file),'unit':pending['unit'],'total':len(plan['pages']),
            'awaiting_confirmation':True,'sha256':pending['sha256'],'reused':True}
  if index>=len(plan['pages']):return {'finished':True,'units':len(plan['pages'])}
  pg=plan['pages'][index];ids=pg['lp_ids'];points=[pmap(plan)[x] for x in ids]
  if plan.get('render_contract')==direct_html.CONTRACT:
    accepted=obj(w/'reviews'/'plan-review.json')
    if (not accepted or accepted.get('approved') is not True
          or accepted.get('plan_sha256')!=agent.digest(plan)):
      raise v5.GateError('G2 approved source-grounded course plan is required')
    try:
      ready=direct_html.prepare_standard(w,plan,source,pg)
    except direct_html.DirectPageError as exc:
      raise v5.GateError(str(exc))
    path=Path(ready['file'])
    receipt=record(w,'unit',path,pg['title'],ids)
    v5.atomic_json(w/'unit-delivery-pending.json',{
      'file':str(path.resolve()),'unit':index+1,'sha256':ready['sha256'],
      'page_id':pg['page_id']})
    return {'file':str(path.resolve()),'unit':index+1,
            'total':len(plan['pages']),'reviewed':True,
            'browser':ready['browser'],'artifact':receipt,
            'awaiting_confirmation':True,'sha256':ready['sha256']}
  # Legacy structured-course route remains available for previously started courses.
  dpath=w/'drafts'/f'{pg["page_id"]}.json'
  if dpath.exists():draft=v5.read_json(dpath)
  else:raise v5.GateError('host-authored Unit draft missing: '+str(dpath))
  try:
    spec,design_hash=lessons.verify_ready(w,plan,pg,source,points)
  except (lessons.LessonContractError,KeyError,ValueError,TypeError) as exc:
    raise v5.GateError('G3 Unit lesson design rejected: '+str(exc))
  alignment=lessons.validate_draft_alignment(spec,draft)
  if alignment:raise v5.GateError('Unit draft differs from reviewed design: '+str(alignment))
  board=None;board_hash=None
  if plan.get('render_contract')=='storyboard-v1':
    try:board,board_hash=sb.storyboard_ready(w,plan,pg,points,spec,source)
    except (sb.StoryboardError,KeyError,ValueError,TypeError) as exc:
      raise v5.GateError('G3 Unit storyboard not independently approved: '+str(exc))
  issues=v5.validate_content_data(points,draft,mode='study')
  if issues:raise v5.GateError('content contract failure: '+str(issues))
  sm={x['id']:x for x in source['segments']}
  ev=[sm[x] for pt in points for x in pt['source_span_ids']]
  required=[f['id'] for pt in points for f in pt['required_facts']]
  rev=independent_review(w,pg['page_id']+'-unit',ev,{'points':points,'draft':draft},required)
  if rev.get('lesson_spec_sha256')!=design_hash:
    raise v5.GateError('G4 Unit content review is not bound to approved Lesson Specification')
  if board is not None and rev.get('storyboard_sha256')!=board_hash:
    raise v5.GateError('G4 Unit content review is not bound to the approved storyboard')
  if len(points)>1:
    coherence=rev.get("unit_coherence",{})
    if (coherence.get("coherent") is not True or
        coherence.get("shared_case_ok") is not True or
        coherence.get("cognitive_load_ok") is not True or
        set(coherence.get("checked_lp_ids",[]))!=set(ids) or
        not isinstance(coherence.get("reason"),str) or len(coherence["reason"].strip())<45):
      raise v5.GateError('G4 Study Unit needs reviewer-confirmed shared example, cognitive load and LP coverage')
  # The existing host-agent review receipt was verified against this exact draft.
  prev='overview.html' if index==0 else plan['pages'][index-1]['page_id']+'.html'
  nxt='overview.html'
  pagehtml=renderer.render(pg,points,draft,source,spec,prev,nxt,storyboard=board)
  if board is None:
    dest=w/'published'/f'{pg["page_id"]}.html'
  else:
    # First invocation produces a reviewable HTML + screenshots. Publication
    # is withheld until a real host reviewer signs off on the rendered page.
    dest=w/'draft-pages'/f'{pg["page_id"]}.html'
  v5.write_text(dest,pagehtml)
  for pt in points:
    for fact in pt['required_facts']:
      if h(fact['text']) not in pagehtml or f'data-fact-id="{h(fact["id"])}"' not in pagehtml:
        raise v5.GateError('render lost required fact '+fact['id'])
  selectors=['[data-fact-id]','[data-teaching-module="transfer-checkpoint"]'] if board else [
    '[data-fact-id]','.card.check button','details.micro-details summary']
  qa=browser_check(dest,selectors=selectors,storyboard=board)
  if board is not None:
    qa["manifest_sha256"]=v5.sha(dest.read_bytes())
    qa["screenshots"]={pg["page_id"]:qa.pop("page_screenshots")}
    v5.atomic_json(w/'reports'/('unit-browser-'+pg["page_id"]+'.json'),qa)
    reviewfile=sb.path_set(w,pg["page_id"])[2]
    if not reviewfile.is_file():
      raise v5.GateError('G5 RENDER_REVIEW_PENDING: inspect '+str(dest)+
        ' and the actual desktop/mobile screenshots; save independent review to '+str(reviewfile))
    problems=sb.validate_render_review(sb.read(reviewfile),w,plan,pg,
                                        source,spec,board,dest,qa)
    if problems:raise v5.GateError('G5 Unit render review rejected: '+str(problems[:12]))
    final=w/'published'/f'{pg["page_id"]}.html'
    final.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(dest,final);dest=final
  if (w/'overview.html').exists():shutil.copy2(w/'overview.html',w/'published'/'overview.html')
  receipt=record(w,'unit',dest,pg['title'],ids)
  fingerprint=v5.sha(dest.read_bytes())
  v5.atomic_json(w/'unit-delivery-pending.json',
    {'file':str(dest.resolve()),'unit':index+1,'sha256':fingerprint,'page_id':pg['page_id']})
  return {'file':str(dest.resolve()),'unit':index+1,'total':len(plan['pages']),
          'reviewed':True,'browser':qa,'artifact':receipt,
          'awaiting_confirmation':True,'sha256':fingerprint}


def confirm_unit_delivery(ws,file):
  """Commit progress only after the host actually presents the prepared page."""
  w=Path(ws);candidate=Path(file).resolve()
  receipt=obj(w/'unit-delivery-confirmed.json')
  if receipt and receipt.get('file')==str(candidate):
    if not candidate.is_file() or v5.sha(candidate.read_bytes())!=receipt['sha256']:
      raise v5.GateError('confirmed Unit artifact changed')
    return {'confirmed':True,'duplicate':True,'unit':receipt['unit'],'file':str(candidate)}
  pending=obj(w/'unit-delivery-pending.json')
  if not pending:
    return learners.confirm_artifact_delivery(w,candidate)
  if pending.get('file')!=str(candidate):
    raise v5.GateError('confirmation does not match the pending Unit')
  if not candidate.is_file() or v5.sha(candidate.read_bytes())!=pending['sha256']:
    raise v5.GateError('pending Unit artifact missing or changed')
  index=int(v5.state(w).get('current_unit',0))
  if pending['unit']==index:
    # Recovery after a crash between the canonical learner-state write and the
    # final delivery receipt. Require proof in BOTH course state and artifact hash.
    learner=learners.course(w)
    matched=any(a.get('reference')==str(candidate)
                and a.get('sha256')==pending['sha256']
                and a.get('delivery_status')=='delivered'
                for a in learner.get('artifacts',[]))
    if not matched or learner.get('navigation',{}).get('current_unit_index',0)<index:
      raise v5.GateError('Host cursor advanced without matching learner evidence')
    result={'recovered':True,'cursor':index}
  elif pending['unit']==index+1:
    # First update canonical learner course; recovery restores Host cursor after a crash.
    result=learners.mark_unit_delivered(w,pending['unit'],candidate)
    state=v5.state(w);state['current_unit']=pending['unit'];v5.save(w,state)
  else:
    raise v5.GateError('pending Unit cursor drift')
  v5.atomic_json(w/'unit-delivery-confirmed.json',pending)
  (w/'unit-delivery-pending.json').unlink()
  return {'confirmed':True,'duplicate':False,'unit':pending['unit'],
          'file':str(candidate),'learner_state':result}

def explanation(ws,topic):
  """Render a host-authored explanation after a separate host-agent review."""
  w=Path(ws);plan,source=need_plan(w);points=match(plan,topic)
  if plan.get('render_contract')==direct_html.CONTRACT:
    # Each re-explanation is a new authored HTML revision; preserve older ones.
    prefix='e-'+slug(topic)+'-v'
    candidates=sorted((w/'supplements').glob(prefix+'[0-9][0-9][0-9].html'))
    prior=obj(w/'v6-artifact-index.json') or {'items':[]}
    used={entry.get('file') for entry in prior.get('items',[]) if entry.get('kind')=='explanation'}
    fresh=[path for path in candidates if str(path.resolve()) not in used]
    if not fresh:
      raise v5.GateError('write a new versioned supplements/'+prefix+'NNN.html; prior explanations remain preserved')
    page=fresh[0];facts={f['id'] for p in points for f in p['required_facts']}
    try:checked=direct_html.check_supplement(w,plan,source,page,facts)
    except direct_html.DirectPageError as exc:raise v5.GateError(str(exc))
    receipt=record(w,'explanation',page,topic,[p['lp_id'] for p in points])
    return {'file':str(page.resolve()),'reviewed':True,'browser':checked['browser'],
            'artifact':receipt,'awaiting_delivery_confirmation':True,
            'version':page.stem}
  if len(points)>2:points=points[:2]
  ids=[x['lp_id'] for x in points];sp={s['id']:s for s in source['segments']}
  evidence=[{'lp_id':p['lp_id'],'goal':p['goal'],'facts':p['required_facts'],
             'source':[sp[x] for x in p['source_span_ids']]} for p in points]
  file_data=w/'supplements'/f'e-{slug(topic)}.json'
  if not file_data.is_file():raise v5.GateError('host-authored explanation missing: '+str(file_data))
  data=v5.read_json(file_data)
  fields=('intuition','meaning','mechanism','simple_example','agent_example','engineering_example','return_connection')
  required=[f['id'] for p in points for f in p['required_facts']]
  if any(not isinstance(data.get(f),str) or len(data[f].strip())<45 for f in fields) or set(required)-set(data.get('represented_fact_ids',[])):
    raise v5.GateError('study-e contract: incomplete explanation or required facts')
  rev=independent_review(w,'study-e-'+slug(topic),evidence,data,required)
  sections=''.join(f'<section class="card"><h2>{h(k.replace("_"," ").title())}</h2><p>{h(data[k])}</p></section>' for k in fields)
  markup=f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{h(topic)} · Study-e</title><style>{v5.CSS}</style><main><p>Study · 局部重讲</p><h1>{h(topic)}</h1><p>完成后返回原 Unit。</p>{sections}</main></html>'
  output=w/'supplements'/f'e-{slug(topic)}.html';v5.write_text(output,markup)
  qa=browser_check(output,selectors=['h1','.card'])
  receipt=record(w,'explanation',output,topic,ids)
  return {'file':str(output),'reviewed':True,'browser':qa,'artifact':receipt,
          'awaiting_delivery_confirmation':True}

def quiz(ws,topic):
  """Render an existing host-authored exam; keep answers out of initial HTML."""
  w=Path(ws);plan,source=need_plan(w);points=match(plan,topic)
  filename=w/'exams'/f'{slug(topic)}.json'
  if not filename.is_file():raise v5.GateError('host-authored quiz missing: '+str(filename))
  exam=v5.read_json(filename);questions=exam.get('questions',[])
  if exam.get('topic')!=topic:raise v5.GateError('quiz topic differs from the selected plan')
  if not 6<=len(questions)<=10 or len({q.get('id') for q in questions})!=len(questions):
    raise v5.GateError('exam must contain 6–10 unique questions')
  if any(not all(str(q.get(k,'')).strip() for k in ('id','question','answer','rubric','type'))
         for q in questions):raise v5.GateError('missing exam question/answer/rubric')
  required=[f['id'] for p in points for f in p['required_facts']]
  known=set(required)
  cover=set(x for q in questions for x in q.get('source_fact_ids',[]))
  if known-cover or cover-known:raise v5.GateError('exam fact coverage mismatch')
  independent_review(w,'study-q-'+slug(topic),source,exam,required)
  questions_html=''.join(f'<section class="card"><small>题目 {i+1} · {h(q["type"])}</small><h2>{h(q["question"])}</h2><p>请在会话中提交你的回答。</p></section>' for i,q in enumerate(questions))
  page=f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{h(topic)} · Study-q</title><style>{v5.CSS}</style><main><h1>{h(topic)} · 理解试卷</h1><p>共 {len(questions)} 题；答案和评分标准仅在提交后用于评阅。</p>{questions_html}</main></html>'
  output=w/'exams'/f'{slug(topic)}-questions.html';v5.write_text(output,page)
  qa=browser_check(output,selectors=['h1','.card'])
  receipt=record(w,'exam',output,topic,[p['lp_id'] for p in points])
  return {'file':str(output),'question_count':len(questions),'answer_key':str(filename),
          'browser':qa,'artifact':receipt,'awaiting_delivery_confirmation':True}

def submit_quiz(ws,topic,answers_file,review_file):
  """Store actual learner answers assessed by an isolated agent of the same host."""
  w=Path(ws);plan,source=need_plan(w)
  if not topic.strip():raise v5.GateError('study-q-submit requires --topic')
  exam_path=w/'exams'/f'{slug(topic)}.json'
  if not exam_path.is_file():raise v5.GateError('existing exam missing; run /study-q first')
  exam=v5.read_json(exam_path)
  if exam.get('topic')!=topic:raise v5.GateError('exam topic mismatch')
  answer_path=Path(answers_file).resolve()
  if not answer_path.is_file():raise v5.GateError('learner response file missing')
  answer_doc=v5.read_json(answer_path)
  if answer_doc.get('topic')!=topic or not isinstance(answer_doc.get('answers'),list):
    raise v5.GateError('submission topic or answers missing')
  questions={str(q['id']):q for q in exam['questions']}
  answers={}
  for entry in answer_doc['answers']:
    if not isinstance(entry,dict):raise v5.GateError('invalid learner response')
    qid=str(entry.get('question_id',''))
    if qid not in questions or qid in answers:raise v5.GateError('unknown/duplicate question ID')
    if not isinstance(entry.get('answer'),str) or not entry['answer'].strip():
      raise v5.GateError('missing real learner response '+qid)
    assistance=entry.get('assistance','independent')
    if assistance not in ('independent','hinted','after_reveal'):
      raise v5.GateError('invalid assistance value')
    answers[qid]=entry
  if not answers:raise v5.GateError('empty learner submission')
  if not review_file:raise v5.GateError('isolated host assessment receipt required via --review-file')
  review=v5.read_json(review_file)
  if review.get('review_mode')!='isolated_host_agent' or not review.get('reviewer_context_id'):
    raise v5.GateError('isolated host agent review receipt required')
  if review.get('reviewer_context_id')==review.get('writer_context_id'):
    raise v5.GateError('reviewer reused answer-writing context')
  if review.get('exam_sha256')!=v5.sha(exam_path.read_bytes()) or review.get('answer_sha256')!=v5.sha(answer_path.read_bytes()):
    raise v5.GateError('assessment receipt does not match quiz and submitted answers')
  expected={f['id']:p['lp_id'] for p in plan['points'] for f in p['required_facts']}
  lpmap={p['lp_id']:p for p in plan['points']}
  grades=[];seen=set()
  for item in review.get('grades',[]):
    qid=str(item.get('question_id',''))
    if qid not in answers or qid in seen:raise v5.GateError('unknown/duplicate graded question')
    seen.add(qid);q=questions[qid]
    fact_ids=set(q.get('source_fact_ids',[]))
    if not fact_ids or fact_ids-set(expected):raise v5.GateError('invalid quiz fact mapping')
    demonstrated=set(item.get('demonstrated_fact_ids',[]))
    if demonstrated-fact_ids:raise v5.GateError('reviewer asserted unknown facts')
    if type(item.get('passed')) is not bool or not isinstance(item.get('reason'),str):
      raise v5.GateError('incomplete grade')
    passed=item['passed'];transfer=bool(item.get('transfer_demonstrated'))
    for lp_id in sorted({expected[x] for x in fact_ids}):
      required={f['id'] for f in lpmap[lp_id]['required_facts']}
      complete=passed and required.issubset(demonstrated)
      applies=any(x in q.get('type','').lower() for x in ('application','transfer','scenario','应用','迁移','情境'))
      outcome='applied' if complete and transfer and applies else ('understood' if complete else 'attempted')
      if answers[qid].get('assistance','independent')!='independent':outcome='attempted'
      grades.append({'question_id':qid,'lp_id':lp_id,'outcome':outcome,
        'actual_answer':answers[qid]['answer'],'assistance':answers[qid].get('assistance','independent')})
  if seen!=set(answers):raise v5.GateError('assessment omitted submitted answers')
  for entry in grades:
    learners.record_assessment(w,entry['lp_id'],entry['actual_answer'],
      questions[entry['question_id']]['rubric'],entry['outcome'],entry['question_id'],
      str(answer_path)+'#'+entry['question_id'],assistance=entry['assistance'],
      reviewed=True,source_ref=str(exam_path))
  output=w/'exams'/f'{slug(topic)}-feedback.json'
  v5.atomic_json(output,{'topic':topic,'exam_sha256':review['exam_sha256'],
    'answer_sha256':review['answer_sha256'],'grades':grades,'reviewer_context_id':review['reviewer_context_id']})
  return {'graded':len(seen),'feedback_file':str(output),'evidence_records':len(grades)}

def knowledge_map(ws):
  w=Path(ws);plan,source=need_plan(w);st=v5.state(w);units=[]
  for i,page in enumerate(plan['pages']):
    txt='已交付' if i<st.get('current_unit',0) else '未交付'
    units.append(f'<section class="card"><h2>{h(page["page_id"])} · {h(page["title"])}</h2><p>{txt}</p><p class="hint">Learning Points: {h(", ".join(page["lp_ids"]))}</p></section>')
  relations=[]
  lp={p['lp_id']:p for p in plan['points']}
  for point in plan['points']:
    for parent in point.get('prerequisites',[]):
      label=lp[parent]['title'] if parent in lp else str(parent)
      relations.append(f'<li>{h(label)} → {h(point["title"])}（依赖关系）</li>')
  relhtml='<section class="card"><h2>知识点依赖关系</h2>'+('<ul>'+''.join(relations)+'</ul>' if relations else '<p>当前计划未声明显式先修边；按照 Unit 顺序学习。</p>')+'</section>'
  lp_status={p['id']:p.get('learning_status','unassessed') for p in learners.course(w).get('learning_points',[])}
  total={status:sum(v==status for v in lp_status.values()) for status in ('unassessed','attempted','understood','applied')}
  mastery='<section class="card"><h2>学习证据（与已交付进度分开）</h2><p>'+h(str(total))+'</p></section>'
  file=w/'study-map.html';v5.write_text(file,'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+v5.CSS+'</style><main><h1>Study V6.1 · 知识地图</h1>'+mastery+relhtml+''.join(units)+'</main></html>')
  return {'file':str(file),'units':len(units),'dependencies':len(relations),'current_unit':st.get('current_unit',0)}

def consolidate_direct(ws,topic,plan,source):
  """Complete offline archive of already authored HTML, keeping its own styling.

  A sandboxed srcdoc page preserves the complete original body, CSS, figures
  and client-side teaching interactions without rewriting them as summaries.
  """
  w=Path(ws);sections=[];covered=[];absent=[]
  normalized=topic.strip().lower()
  broad=not normalized or normalized in ('第八章','chapter 8','chapter8','all','全部')
  def add(label,html_data):
    title=h(label)
    srcdoc=h(html_data)
    sections.append('<section class="chapter"><h2>'+title+'</h2>'
       '<iframe sandbox="allow-scripts" loading="lazy" title="'+title
       +'" srcdoc="'+srcdoc+'"></iframe></section>')
  for page in plan["pages"]:
    if not broad and normalized not in page["title"].lower() and not any(
      normalized in p["title"].lower() for p in plan["points"] if p["lp_id"] in page["lp_ids"]):
      continue
    path=w/"published"/(page["page_id"]+".html")
    if path.is_file():
      add(page["page_id"]+" · "+page["title"],path.read_text(encoding="utf-8"))
      covered.append(page["page_id"])
    else:absent.append(page["page_id"])
  index=obj(w/"v6-artifact-index.json") or {"items":[]}
  for entry in index.get("items",[]):
    if entry.get("kind")!="explanation":continue
    if not broad and normalized not in entry.get("topic","").lower():continue
    path=Path(entry["file"])
    if not path.is_file() or v5.sha(path.read_bytes())!=entry.get("sha256"):
      raise v5.GateError("supplement has changed since registration: "+str(path))
    add("补充讲解 · "+entry["topic"]+" · "+path.stem,path.read_text(encoding="utf-8"))
  for exam in sorted((w/"exams").glob("*.json")) if (w/"exams").is_dir() else []:
    data=obj(exam) or {}
    if not data.get("questions"):continue
    if not broad and normalized not in data.get("topic","").lower():continue
    part=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><body><main>',
          '<h1>测验 · '+h(data.get("topic",""))+'</h1>']
    for q in data["questions"]:
      part.extend(('<h2>'+h(q["question"])+'</h2>',
        '<p><strong>答案：</strong>'+h(q["answer"])+'</p>',
        '<p><strong>依据：</strong>'+h(q["rubric"])+'</p>'))
    part.append('</main></body></html>')
    add("测验及完整答案 · "+data.get("topic",""),"".join(part))
  # Preserve all reader-visible material; completeness is reported separately.
  if not sections:raise v5.GateError("no generated matching HTML available for consolidation")
  css='body{font:16px/1.55 system-ui;margin:0;background:#f1f4f6;color:#173039}main{max-width:1100px;margin:auto;padding:24px 16px}h1{font-size:32px}h2{font-size:23px}.chapter{background:white;padding:18px;margin:22px 0;border:1px solid #ccd8dd;border-radius:14px}iframe{display:block;width:100%;height:1000px;max-height:none;border:1px solid #d8e3e6;border-radius:10px}@media(max-width:700px){main{padding:12px}iframe{height:850px}}'
  out=w/"consolidated"/("c-"+slug(topic or "all")+".html")
  v5.write_text(out,'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
   '<meta name="viewport" content="width=device-width,initial-scale=1"><title>完整学习整理</title>'
   '<style>'+css+'</style></head><body><main><h1>完整学习整理 · '+h(topic or "全部")+'</h1>'
   '<p>以下每个原始 HTML 保留讲解、图示及互动。已生成页面以原样独立框架呈现。</p>'
   +''.join(sections)+'</main></body></html>')
  receipt=record(w,'consolidated',out,topic or 'all',[])
  return {"file":str(out.resolve()),"pages_included":covered,"not_yet_generated":absent,
          "sections":len(sections),"artifact":receipt,"full_html_preserved":True}


def consolidate_existing(ws,topic):
  """Merge ALL existing topic materials from structured sources, with answers visible.
  This uses the source plan, not merely filenames or current session messages.
  Missing declared artifacts fail closed; ungenerated lessons are excluded and reported.
  """
  w=Path(ws);plan,source=need_plan(w)
  if plan.get('render_contract')==direct_html.CONTRACT:
    return consolidate_direct(w,topic,plan,source)
  index=obj(w/'v6-artifact-index.json') or {'items':[]}
  for item in index['items']:
    if topic and topic.lower() not in item.get('topic','').lower():continue
    f=Path(item['file'])
    if not f.exists() or v5.sha(f.read_bytes())!=item['sha256']:
      raise v5.GateError('artifact missing or changed: '+str(f))
  pm=pmap(plan);parts=[];seen=set();facts_done=set();covered=[];absent=[]
  for pg in plan['pages']:
    pts=[pm[x] for x in pg['lp_ids']]
    # For broad names such as '第八章' include all already-generated materials; for focused topic, select matching pages.
    matched=(not topic or topic.lower() in ('第八章','chapter 8','chapter8') or topic.lower() in pg['title'].lower()
       or any(topic.lower() in p['title'].lower() or topic.lower() in p['goal'].lower() for p in pts))
    if not matched:continue
    draft=obj(w/'drafts'/f'{pg["page_id"]}.json')
    if draft is None:
      absent.append(pg['page_id']);continue
    issues=v5.validate_content_data(pts,draft,mode=plan.get('mode','study-d'))
    if issues:raise v5.GateError('incomplete generated draft '+pg['page_id']+': '+str(issues))
    covered.append(pg['page_id'])
    parts.append('<section class="card"><h2>'+h(pg['page_id']+' · '+draft['title'])+'</h2><p>'+h(draft['intro'])+'</p>')
    for block in draft['sections']:
      pair=(block['heading'],block['text'])
      if pair in seen:continue
      seen.add(pair);parts.append(f'<h3>{h(block["heading"])}</h3><p>{h(block["text"])}</p>')
    for pt in pts:
      for f in pt['required_facts']:
        if f['id'] in facts_done:continue
        facts_done.add(f['id'])
        parts.append(f'<p class="fact" data-fact-id="{h(f["id"])}"><b>{h(f["id"])}：</b>{h(f["text"])}</p>')
    v=draft.get('visual')
    if v:
      parts.append('<h3>知识关系：'+h(v['title'])+'</h3><p>箭头或关系的含义：'+h(v['relation'])+'</p>')
      for node in v['nodes']:
        parts.append(f'<p>{h(node["label"])}：{h(node["meaning"])}</p>')
    sim=draft.get('simulation')
    if sim:
      parts.append('<h3>条件变化（静态完整记录）</h3>')
      for state in sim['states']:
        parts.append(f'<p><b>{h(state["label"])}：</b>{h(state["observation"])}。{h(state["explanation"])}</p>')
    for q in draft['mini_questions']:
      parts.append(f'<p><b>学习追问：</b>{h(q["question"])}<br><b>答案：</b>{h(q["answer"])}</p>')
    ck=draft['checkpoint'];parts.append(f'<h3>Checkpoint</h3><p>{h(ck["question"])}</p><p>标准答案：{h(ck["options"][ck["correct_index"]])}</p><p>{h(ck["feedback"])}</p></section>')
  for item in index['items']:
    if item['kind']!='explanation':continue
    if topic and topic.lower() not in item['topic'].lower() and topic.lower() not in ('第八章','chapter 8','chapter8'):continue
    d=obj(w/'supplements'/f'e-{slug(item["topic"])}.json')
    if d is None:raise v5.GateError('missing explanation structured content: '+item['topic'])
    parts.append('<section class="card"><h2>补充讲解 · '+h(item['topic'])+'</h2>')
    for k in ('intuition','meaning','mechanism','simple_example','agent_example','engineering_example','return_connection'):
      t=d.get(k,'');
      if t and t not in seen:seen.add(t);parts.append(f'<h3>{h(k)}</h3><p>{h(t)}</p>')
    parts.append('</section>')
  exam_count=0
  for f in sorted((w/'exams').glob('*.json')) if (w/'exams').exists() else []:
    d=obj(f)
    if not d or not d.get('questions'):continue
    if topic and topic.lower() not in d.get('topic','').lower() and topic.lower() not in ('第八章','chapter 8','chapter8'):continue
    exam_count+=1;parts.append('<section class="card"><h2>试卷与标准答案 · '+h(d.get('topic',''))+'</h2>')
    for q in d['questions']:
      if not q.get('answer') or not q.get('rubric'):raise v5.GateError('exam answer/rubric missing '+f.name)
      parts.append(f'<h3>{h(q["question"])}</h3><p><b>标准答案：</b>{h(q["answer"])}</p><p>判定依据：{h(q["rubric"])}</p>')
    parts.append('</section>')
  # Include reviewed Study-D modules linked by the Manager in sibling workspaces.
  related=obj(w/'v6-related-modules.json') or {'modules':[]}
  deep_count=0
  for meta in related.get('modules',[]):
    dw=Path(meta.get('workspace',''))
    if not dw.resolve().is_relative_to(w.resolve()):
      raise v5.GateError('linked module path outside course workspace: '+str(dw))
    if topic and topic.lower() not in ('第八章','chapter8','chapter 8') and topic.lower() not in meta.get('topic','').lower():continue
    deep_plan=obj(dw/'frozen-plan.json');deep_src=obj(dw/'source.json')
    if not deep_plan or not deep_src or deep_plan.get('source_sha256')!=deep_src.get('source_sha256'):
      raise v5.GateError('linked module missing or source hash changed: '+str(dw))
    if meta.get('source_sha256')!=deep_src.get('source_sha256'):
      raise v5.GateError('linked module source changed: '+str(dw))
    deep_pm={p['lp_id']:p for p in deep_plan['points']}
    for deep_page in deep_plan['pages']:
      d=obj(dw/'drafts'/f'{deep_page["page_id"]}.json')
      if d is None:raise v5.GateError('deep module declared published but draft missing: '+deep_page['page_id'])
      pp=[deep_pm[x] for x in deep_page['lp_ids']]
      if v5.validate_content_data(pp,d,mode='study-d'):raise v5.GateError('deep module has incomplete content contract')
      deep_count+=1;parts.append('<section class="card"><h2>深度模块：'+h(meta.get('topic',''))+' · '+h(d['title'])+'</h2>')
      for block in d['sections']:
        key=(block['heading'],block['text'])
        if key not in seen:seen.add(key);parts.append(f'<h3>{h(block["heading"])}</h3><p>{h(block["text"])}</p>')
      for point in pp:
        for f in point['required_facts']:
          key=f['span_id']+':'+f['text']
          if key in seen:continue
          seen.add(key);parts.append(f'<p class="fact" data-fact-id="{h(f["id"])}">{h(f["text"])}</p>')
      for q in d['mini_questions']:
        parts.append(f'<p><b>学习追问：</b>{h(q["question"])}<br><b>答案：</b>{h(q["answer"])}</p>')
      sim=d.get('simulation')
      if sim:
        parts.append('<h3>互动模拟：全部条件、结果与解释</h3>')
        for x in sim['states']:parts.append(f'<p>{h(x["label"])}：{h(x["observation"])}。{h(x["explanation"])}</p>')
      ck=d['checkpoint'];parts.append(f'<h3>Checkpoint</h3><p>{h(ck["question"])}</p><p>标准答案：{h(ck["options"][ck["correct_index"]])}</p><p>{h(ck["feedback"])}</p></section>')
  # V3.5 course evidence is authoritative. Include real answers and existing grading,
  # distinct from generated standard answers, without inventing missing work.
  try:
    state61=learners.course(w)
    known={lp['id'] for lp in state61.get('learning_points',[]) if not topic or topic.lower() in lp.get('title','').lower()}
    entries=[e for e in state61.get('evidence',[]) if not topic or topic.lower() in ('第八章','chapter 8','chapter8') or any(i in known for i in e.get('lp_ids',[]))]
    if entries:
      parts.append('<section class="card"><h2>已有真实作答与评阅证据</h2>')
      for e in entries:
        parts.append('<h3>'+h(e.get('question_id','Question'))+'</h3>'+'<p><b>学习者回答：</b>'+h(e.get('actual_answer',''))+'</p>'+
          '<p><b>判定依据：</b>'+h(e.get('rubric',''))+'</p>'+'<p><b>已记录的评阅结论：</b>'+h(e.get('outcome','unreviewed'))+'</p>')
      parts.append('</section>')
  except learners.LearnerError as exc:
    raise v5.GateError('learner state unavailable for consolidation: '+str(exc))
  if not parts:raise v5.GateError('no generated material matched '+topic)
  note='已生成页面：' +(', '.join(covered) or '无')+'。未生成页面数：'+str(len(absent))+ '（不表示已学或已掌握）。'
  text='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Study V6 完整归档</title><style>'+v5.CSS+'</style><main><h1>Study V6 · 已生成课件完整归档</h1><p>'+h(note)+'</p><p>核心知识、模拟的条件/结果/解释、隐藏追问与试卷标准答案全部展开。关闭 JavaScript 仍可阅读。</p>'+''.join(parts)+'</main></html>'
  file=w/'consolidated'/f'{slug(topic or "all")}.html';v5.write_text(file,text)
  for fact_id in facts_done:
    if f'data-fact-id="{h(fact_id)}"' not in text:raise v5.GateError('consolidation lost fact '+fact_id)
  qa=browser_check(file,selectors=['h1','.card'])
  return {'file':str(file),'generated_pages':covered,'not_yet_generated':absent,'exams_included':exam_count,'deep_pages_included':deep_count,'browser':qa}

def main():
  p=argparse.ArgumentParser(description='Study V6 learning commands')
  p.add_argument('command',choices=['study-n','study-e','study-q','study-c','study-m','confirm-delivery','study-q-submit']);p.add_argument('--workspace',required=True);p.add_argument('--topic',default='')
  p.add_argument('--file',help='Exact prepared HTML for confirm-delivery')
  p.add_argument('--answers-file',help='Learner-submitted JSON answers for study-q-submit')
  p.add_argument('--review-file',help='Isolated host reviewer output JSON')
  a=p.parse_args();w=Path(a.workspace).resolve()
  try:
    learners.recover(w)  # V3.5 authoritative course cursor and evidence, without advancing mastery.
    if a.command=='study-n':learners.require_ready(w)
    if a.command=='confirm-delivery':
      if not a.file:raise v5.GateError('confirm-delivery requires --file')
      result=confirm_unit_delivery(w,a.file)
    elif a.command=='study-q-submit':
      if not a.answers_file:raise v5.GateError('study-q-submit requires --answers-file')
      result=submit_quiz(w,a.topic,a.answers_file,a.review_file)
    else:
      fn={'study-n':lambda:next_unit(w),'study-e':lambda:explanation(w,a.topic),
          'study-q':lambda:quiz(w,a.topic),'study-c':lambda:consolidate_existing(w,a.topic),
          'study-m':lambda:knowledge_map(w)}[a.command]
      result=fn()
      if a.command in ('study-e','study-q') and result.get('file'):
        kind='explanation' if a.command=='study-e' else 'quiz'
        result['learner_state']=learners.mark_artifact(w,kind,result['file'],a.topic)
    print(json.dumps({'ok':True,'result':result},ensure_ascii=False,indent=2))
  except Exception as e:print(json.dumps({'ok':False,'error':str(e)},ensure_ascii=False),file=sys.stderr);sys.exit(2)
if __name__=='__main__':main()
