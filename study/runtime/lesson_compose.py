"""Study V6.5 storyboard-driven, source-safe HTML component composer.

Eight reusable teaching interactions, three layout shells. This Python
module uses no model and executes no arbitrary source-supplied code.
HTML/CSS/JS are self-contained and work from local file:// locations.
"""
from __future__ import annotations
import html
import json
import math


def h(value):
    return html.escape(str(value),quote=True)


def payload(value):
    # html.escape protects attribute boundaries and prevents source tags.
    return h(json.dumps(value,ensure_ascii=False).replace("<","\\u003c"))


CSS="""
:root{--bg:#f2f6f7;--card:#ffffff;--ink:#193239;--muted:#4b666c;
--line:#cddfe1;--accent:#1c6880;--accent2:#237e83;--pale:#eaf3f6;
--warn:#b45437;--good:#137451;--gold:#f6edda}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);
color:var(--ink);font:16px/1.65 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:1150px;margin:auto;padding:27px 20px 76px}
h1{font-size:clamp(30px,4.4vw,50px);line-height:1.16;letter-spacing:-.035em;margin:8px 0}
h2{font-size:clamp(19px,2.4vw,25px);line-height:1.26;margin:5px 0 12px}
h3{font-size:17px;margin:12px 0 6px}
p{margin:8px 0}a{color:var(--accent)}strong{font-weight:740}
.hero{padding:18px 0 26px}.eyebrow{color:var(--accent);font-size:12px;
font-weight:800;letter-spacing:.1em}.sub{font-size:18px;max-width:760px;color:var(--muted)}
.hero-question{padding:16px 20px;background:#e3eff3;border-left:4px solid var(--accent);
border-radius:8px;max-width:860px;margin-top:14px}.board{display:grid;gap:16px}
.board.layout-overview{grid-template-columns:repeat(2,minmax(0,1fr))}
.board.layout-exploration{grid-template-columns:minmax(0,1fr)}
.board.layout-evidence{grid-template-columns:repeat(2,minmax(0,1fr))}
.board.layout-evidence>:first-child{grid-column:1 / -1}
.scene,.card{min-width:0;border:1px solid var(--line);background:var(--card);
border-radius:16px;padding:23px;box-shadow:0 4px 18px #18435108}
.scene-head{display:flex;align-items:start;gap:12px}.scene-num{display:inline-flex;
width:30px;height:30px;align-items:center;justify-content:center;border-radius:9px;
background:var(--pale);color:var(--accent);font-size:12px;font-weight:800;flex:none}
.scene-purpose{color:var(--muted);font-size:14px}.scene-title{font-weight:780}
.scene-body{margin-top:18px}.pill{background:#e7f0f3;border:1px solid var(--line);
padding:9px 12px;border-radius:10px}.flow-steps{display:grid;gap:10px}
.flow-node{display:block;background:#f6faf9;border:1px solid var(--line);
padding:15px;border-radius:11px;width:100%;text-align:left;cursor:pointer}
.flow-node.active{border-color:var(--accent);background:#e6f2f5}
.flow-relation{padding:0 10px;color:var(--accent);font-size:13px;font-weight:740}
.info{padding:14px;background:#e9f4f6;border-radius:10px;color:var(--ink);margin-top:11px}
.detail-note{font-size:14px;color:var(--muted)}.hint{font-size:13px;color:var(--muted)}
button,input,select{font:inherit}button{border:1px solid #b7cdd0;border-radius:10px;
padding:10px 13px;cursor:pointer;background:#f8fbfb;color:var(--ink);text-align:left}
button:hover{background:#e6f1f3}button:focus-visible,input:focus-visible,
summary:focus-visible,a:focus-visible{outline:3px solid #1b6d89;outline-offset:3px}
button:disabled{opacity:.55;cursor:default}.actions{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}
.choice{width:100%;margin:6px 0}.choice.selected{background:#dbf0ea;border-color:#75b89c}
.path{margin:15px 0;display:grid;gap:8px}.range-grid{display:grid;
grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:16px;margin:17px 0}
.range-item{background:#f4f8fa;border:1px solid var(--line);padding:14px;border-radius:11px}
input[type=range]{display:block;width:100%;accent-color:var(--accent)}
.readout{font:750 clamp(24px,4vw,38px)/1.15 ui-monospace,Consolas,monospace;
color:var(--accent);margin:16px 0}.readout small{display:block;font:400 14px/1.5 system-ui;color:var(--muted)}
.formula{font:17px/1.5 ui-monospace,Consolas,monospace;white-space:pre-wrap;
overflow-wrap:anywhere;background:#edf4f7;border-radius:10px;padding:12px}
table{width:100%;min-width:410px;border-collapse:collapse;font-size:14px}
th,td{padding:11px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{background:#eaf2f5}.table-wrap{overflow:auto}
tr.active-row{background:#e8f2f5;outline:2px solid var(--accent);outline-offset:-2px}
.trace-item{border-left:3px solid #aac8d3;padding:13px;margin:9px 0;background:#f7faf9;
border-radius:0 9px 9px 0;cursor:pointer}.trace-item.first-error{border-color:var(--warn);
background:#fff0e7}.trace-item.active{outline:1px solid var(--accent)}
.math-step{margin:8px 0;padding:12px;background:#f7fafb;border-radius:10px}
.checkpoint{background:#fffaf1;border-color:#dfc99e}.options{display:grid;gap:8px;margin:15px 0}
.feedback{min-height:25px;font-weight:750;color:var(--good)}.feedback.warning{color:var(--warn)}
details{border:1px solid var(--line);border-radius:10px;margin:10px 0;padding:0 14px}
details summary{cursor:pointer;padding:12px 0;font-weight:670}
details p,details ol{margin-bottom:15px}ol li{padding:4px 0}
.source{font-size:13px;color:var(--muted)}.source p{padding:8px 0;border-bottom:1px solid var(--line)}
footer{margin-top:24px}.nav{display:flex;gap:15px;justify-content:space-between;flex-wrap:wrap}
.lesson-footnote{font-size:13px;color:var(--muted)}
@media(max-width:780px){main{padding:14px 12px 60px}.board.layout-overview,
.board.layout-evidence{grid-template-columns:1fr}.board.layout-evidence>:first-child{
grid-column:auto}.scene,.card{padding:16px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
"""
# Static scripts are authored by the Skill, never by the book/learner.
JS="""
(function(){
'use strict';
function data(el){try{return JSON.parse(el.getAttribute('data-payload')||'{}')}catch(_){return {}}}
function str(x){return String(x===undefined?'':x)}
function append(el,tag,txt,cls){const n=document.createElement(tag);n.textContent=str(txt);if(cls)n.className=cls;el.appendChild(n);return n}
function button(el,label,run){let b=append(el,'button',label);b.type='button';b.addEventListener('click',run);return b}
function numeric(formula,v){
 let o=0,interpret='';
 if(formula==='pass-at-k'){o=1-Math.pow(1-v.p,v.k);interpret='至少一次成功概率 = 1 − (1 − p)^k'}
 if(formula==='q-learning'){o=v.q+v.alpha*(v.reward+v.gamma*v.next_q-v.q);interpret='Q_new = Q + α × (r + γ × maxQ_next − Q)'}
 if(formula==='ppo-clip'){let clipped=Math.max(1-v.epsilon,Math.min(1+v.epsilon,v.ratio));
 o=Math.min(v.ratio*v.advantage,clipped*v.advantage);
 interpret='L_clip = min(r × A, clip(r, 1−ε, 1+ε) × A)'}
 return {value:Number(o),label:interpret}
}
function setupDecision(el,p){
 const zone=el.querySelector('.interactive'),history=[];let current=p.start;
 const nodes=Object.fromEntries((p.nodes||[]).map(n=>[n.id,n]));
 function show(){zone.replaceChildren();const n=nodes[current];if(!n)return;
   append(zone,'p',n.prompt||n.outcome,'scene-title');
   if(n.options&&n.options.length){n.options.forEach(op=>{
     button(zone,op.label,()=>{history.push({prompt:n.prompt,choice:op.label,why:op.reason});
       current=op.to;show()})})}
   else {append(zone,'div',n.reason||'', 'info')}
   if(history.length){let ol=append(zone,'ol','', 'path');
     history.forEach(x=>append(ol,'li',x.choice+' — '+x.why))}
   button(zone,'重新选择路径',()=>{current=p.start;history.length=0;show()})
 }show()
}
function setupVariable(el,p){
 const zone=el.querySelector('.interactive'),vals={};
 const panel=append(zone,'div','','range-grid');
 const valueBox=append(zone,'div','','readout');
 const change=()=>{const o=numeric(p.formula,vals);valueBox.replaceChildren();
   append(valueBox,'span',Number(o.value).toFixed(p.formula==='q-learning'?3:4));
   append(valueBox,'small',o.label);};
 (p.controls||[]).forEach(c=>{vals[c.id]=Number(c.default);
   const wrap=append(panel,'div','','range-item');
   append(wrap,'label',c.label+'  ');
   const display=append(wrap,'strong',String(c.default));
   const input=document.createElement('input');input.type='range';
   input.min=String(c.min);input.max=String(c.max);input.step=String(c.step);
   input.value=String(c.default);
   input.setAttribute('aria-label',c.label);
   input.addEventListener('input',()=>{vals[c.id]=Number(input.value);
     display.textContent=input.value;change()});wrap.appendChild(input)});
 change();
}
function setupFlow(el,p){
 const zone=el.querySelector('.interactive'),nodes=p.nodes||[];
 zone.replaceChildren();
 nodes.forEach((n,i)=>{const btn=button(zone,String(i+1)+'. '+n.label,()=>{
   zone.querySelectorAll('.flow-node').forEach(b=>b.classList.remove('active'));
   btn.classList.add('active');detail.textContent=n.meaning});
  btn.classList.add('flow-node');if(i<nodes.length-1){
   let edge=(p.edges||[]).find(x=>x.from===n.id&&x.to===nodes[i+1].id);
   if(edge)append(zone,'div','↓ '+edge.label,'flow-relation')}});
 const detail=append(zone,'p',nodes[0]?.meaning||'','info');
}
function setupStepper(el,p){
 const zone=el.querySelector('.interactive'),steps=p.steps||[];let visible=0;
 const results=append(zone,'div','','path'),controls=append(zone,'div','','actions');
 function show(){results.replaceChildren();steps.slice(0,visible).forEach((s,i)=>{
    let row=append(results,'div','','math-step');append(row,'strong',String(i+1)+'. '+s.expression);
    append(row,'p',s.reason)});
   controls.replaceChildren();
   button(controls,visible===steps.length?'已完成':'展示下一步',()=>{
      visible=Math.min(steps.length,visible+1);show()}).disabled=(visible===steps.length);
   button(controls,'重新推导',()=>{visible=0;show()})}show()
}
function setupExperiment(el,p){
 const zone=el.querySelector('.interactive'),rows=p.rows||[];
 const wrap=append(zone,'div','','actions');
 const label=append(zone,'div',p.interpretation||'','info');
 (rows||[]).forEach((row,i)=>{button(wrap,'突出第 '+(i+1)+' 组',()=>{
    el.querySelectorAll('tbody tr').forEach((tr,j)=>tr.classList.toggle('active-row',i===j));
    label.textContent='当前观察：'+row.join(' · ')+'。'+(p.interpretation||'')})})
}
function setupTrace(el,p){
 const zone=el.querySelector('.interactive'),steps=p.steps||[];
 steps.forEach((s,i)=>{const b=button(zone,'步骤 '+(i+1)+'：'+s.action,()=>{
    zone.querySelectorAll('.trace-item').forEach(t=>t.classList.remove('active'));
    b.classList.add('active');feedback.textContent=
      (s.first_error?'首个错误：':'证据：')+s.evidence+'；结果：'+s.consequence});
    b.className='trace-item'+(s.first_error?' first-error':'')});
 const feedback=append(zone,'p','选择一个步骤检查证据与影响','info')
}
function setupWorked(el,p){
 const zone=el.querySelector('.interactive');const steps=p.steps||[];let i=0;
 const result=append(zone,'div','','path');function show(){
  result.replaceChildren();steps.slice(0,i).forEach((s,j)=>append(result,'p',(j+1)+'. '+s,'math-step'));
  btn.disabled=i>=steps.length}
 const btn=button(zone,'继续推导下一步',()=>{i=Math.min(i+1,steps.length);show()});
 button(zone,'从头思考',()=>{i=0;show()});show()
}
function setupTransfer(el,p){
 const zone=el.querySelector('.interactive'),output=append(zone,'div','','feedback');
 (p.options||[]).forEach(op=>{const b=button(zone,op.label,()=>{
   output.classList.toggle('warning',!op.correct);
   output.textContent=(op.correct?'正确。':'再想一想：')+op.reason;
 });b.className='choice'});
}
document.querySelectorAll('[data-teaching-module]').forEach(el=>{
 const p=data(el),kind=el.getAttribute('data-teaching-module');
 if(kind==='causal-flow')setupFlow(el,p);
 if(kind==='decision-explorer')setupDecision(el,p);
 if(kind==='variable-lab')setupVariable(el,p);
 if(kind==='math-stepper')setupStepper(el,p);
 if(kind==='experiment-comparator')setupExperiment(el,p);
 if(kind==='trace-debugger')setupTrace(el,p);
 if(kind==='worked-example')setupWorked(el,p);
 if(kind==='transfer-checkpoint')setupTransfer(el,p);
});
document.querySelectorAll('button.reset').forEach(b=>b.addEventListener('click',()=>{
 document.querySelectorAll('details').forEach(d=>d.open=false);
 document.querySelectorAll('.feedback').forEach(f=>{f.textContent='';f.classList.remove('warning')});
}));
})();
"""

TITLES={
    "causal-flow":"看清因果关系","decision-explorer":"选择并解释路径",
    "variable-lab":"改变变量，观察结果","math-stepper":"一步步推导",
    "experiment-comparator":"比较实验条件与结果",
    "trace-debugger":"定位首个错误","worked-example":"跟着实例推理",
    "transfer-checkpoint":"换个条件，再试一次"
}


def _fallback(kind,p):
    """Static evidence remains readable without JavaScript."""
    out=['<details class="fallback"><summary>全部条件与解释（离线可读）</summary>']
    if kind in ("causal-flow","decision-explorer"):
        for n in p["nodes"]:
            out.append('<p><strong>'+h(n.get("label") or n.get("prompt") or n.get("outcome"))+
                       '</strong>：'+h(n.get("meaning") or n.get("reason") or "")+'</p>')
            for op in n.get("options",[]):
                out.append('<p>'+h(op["label"])+' → '+h(op["reason"])+'</p>')
    elif kind=="variable-lab":
        out.append('<p>'+h(p["interpretation"])+'</p>')
        for c in p["controls"]:out.append('<p>'+h(c["label"])+' = '+h(c["default"])+'</p>')
    elif kind=="math-stepper":
        for i,st in enumerate(p["steps"]):out.append('<p>'+h(str(i+1)+'. '+st["expression"]+" — "+st["reason"])+'</p>')
    elif kind=="experiment-comparator":
        out.append('<p>'+h(p["interpretation"])+' · '+h(p["provenance"])+'</p>')
    elif kind=="trace-debugger":
        for i,st in enumerate(p["steps"]):
            out.append('<p>'+h(str(i+1)+'. '+st["action"]+'；'+st["evidence"]+'；'+st["consequence"])+'</p>')
        out.append('<p>修复：'+h(p["repair"])+'；留出评估：'+h(p["holdout"])+'</p>')
    elif kind=="worked-example":
        for st in p["steps"]:out.append('<p>'+h(st)+'</p>')
    else:
        out.append('<p>条件变化：'+h(p["changed_condition"])+'。评分依据：'+h(p["rubric"])+'</p>')
    out.append('</details>')
    return ''.join(out)


def _table(cols,rows):
    s=['<div class="table-wrap"><table><thead><tr>']
    s.extend('<th scope="col">'+h(c)+'</th>' for c in cols)
    s.append('</tr></thead><tbody>')
    for row in rows:s.append('<tr>'+''.join('<td>'+h(cell)+'</td>' for cell in row)+'</tr>')
    s.append('</tbody></table></div>')
    return ''.join(s)


def _render_scene(sc,i):
    kind=sc["module"];p=sc["props"]
    out=[f'<section class="scene'+(' checkpoint' if kind=="transfer-checkpoint" else '')+
         f'" data-scene-id="{h(sc["id"])}" data-teaching-module="{h(kind)}" data-payload="{payload(p)}">',
         f'<div class="scene-head"><span class="scene-num">{i+1:02d}</span><div>',
         f'<h2>{h(TITLES[kind])}</h2><p class="scene-purpose">{h(sc["purpose"])}</p></div></div>',
         '<div class="scene-body">']
    if kind=="causal-flow":out.append('<p class="hint">点击每个节点，观察条件与因果说明。</p>')
    if kind=="decision-explorer":out.append('<p class="hint">根据当前条件选择路径；每次选择会显示依据。</p>')
    if kind=="variable-lab":out.append('<p>'+h(p["question"])+'</p><p class="hint">先预测，再拖动滑块。</p>')
    if kind=="math-stepper":out.append('<div class="formula">'+h(p["formula"])+'</div>')
    if kind=="experiment-comparator":
        out.append(_table(p["columns"],p["rows"]))
        out.append('<p class="detail-note">来源：'+h(p["provenance"])+'</p>')
    if kind=="trace-debugger":
        out.append('<p class="hint">从任务开始，找出首个错误及其传播路径。</p>')
        out.append('<p class="info">修复：'+h(p["repair"])+'。留出验证：'+h(p["holdout"])+'</p>')
    if kind=="worked-example":
        out.append('<p><strong>场景：</strong>'+h(p["scenario"])+'</p>')
        out.append('<p><strong>输入：</strong>'+h(p["input"])+'</p>')
        out.append('<p><strong>输出：</strong>'+h(p["outcome"])+'</p>')
    if kind=="transfer-checkpoint":
        out.append('<p class="scene-title">'+h(p["question"])+'</p>')
        out.append('<p>新条件：'+h(p["changed_condition"])+'</p>')
    out.append('<div class="interactive" role="group" aria-label="'+h(TITLES[kind])+'"></div>')
    out.append(_fallback(kind,p))
    out.append('</div></section>')
    return ''.join(out)


def render(page,points,draft,source,spec,storyboard,previous="index.html",following="index.html"):
    lp_ids={p["lp_id"] for p in points}
    out=['<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width,initial-scale=1">',
         '<title>'+h(page["title"])+'</title><style>'+CSS+'</style></head>',
         '<body data-lesson-contract="lesson-storyboard-v1" data-page-id="'+h(page["page_id"])+
         '" data-layout="'+h(storyboard["layout"])+'"><main>',
         '<header class="hero"><div class="eyebrow">STUDY · '+h(spec["lesson_kind"])+' · '+
         h(page["page_id"])+'</div><h1>'+h(draft["title"])+'</h1>',
         '<p class="sub">'+h(spec["objective"])+'</p><p class="hero-question" data-core="goal"><strong>本页问题：</strong>'+
         h(spec["central_question"])+'</p><p>'+h(draft["intro"])+'</p><p>'+h(storyboard["narrative"])+'</p></header>',
         '<div class="board layout-'+h(storyboard["layout"])+'">']
    for i,sc in enumerate(storyboard["scenes"]):out.append(_render_scene(sc,i))
    out.append('</div><section class="card" data-core="mechanism"><h2>把机制说清楚</h2>')
    shared=draft.get("shared_teaching")
    if shared:
        out.append('<div data-shared-teaching="true"><p>'+h(shared["core_explanation"])+'</p><ol>')
        out.extend('<li>'+h(s)+'</li>' for s in shared["causal_steps"]);out.append('</ol></div>')
    for record in draft["teaching_evidence"]:
        out.append('<div data-teaching-lp="'+h(record["lp_id"])+'">')
        if shared:out.append('<p>'+h(record["lp_connection"])+'</p>')
        else:
            out.append('<p>'+h(record["core_explanation"])+'</p><ol>')
            out.extend('<li>'+h(s)+'</li>' for s in record["causal_steps"]);out.append('</ol>')
        for fact in record.get("fact_explanations",[]):
            out.append('<p data-authored-fact-id="'+h(fact["fact_id"])+'">'+h(fact["explanation"])+'</p>')
        if record.get("experiment"):
            out.append('<details><summary>实验条件、数据与局限（原文核对）</summary>')
            for key in ("purpose","setup","controls","results","limitations"):
                out.append('<p>'+h(key)+': '+h(record["experiment"][key])+'</p>')
            out.append('</details>')
        out.append('</div>')
    out.append('</section>')
    # Every authored sentence stays readable, with secondary material behind disclosure.
    out.append('<details class="card"><summary>展开完整的实例推导、适用条件和补充讲解</summary>')
    stems=[shared] if shared else draft["teaching_evidence"]
    for st in stems:
        ex=st["worked_example"]
        for k in ("scenario","input","outcome","why"):
            out.append('<p>'+h(k)+': '+h(ex[k])+'</p>')
        out.append('<ol>');out.extend('<li>'+h(x)+'</li>' for x in ex["reasoning_steps"]);out.append('</ol>')
        out.append('<h3>适用条件</h3>')
        out.extend('<p>'+h(x)+'</p>' for x in st["conditions"])
        out.append('<h3>限制</h3>')
        out.extend('<p>'+h(x)+'</p>' for x in st["limitations"])
    for section in draft.get("sections",[]):
        out.append('<h3>'+h(section["heading"])+'</h3><p>'+h(section["text"])+'</p>')
    out.append('</details>')
    out.append('<details class="card"><summary>先思考，再揭示解释</summary>')
    for q in draft.get("mini_questions",[]):
        out.append('<details class="micro-details question"><summary>'+h(q["question"])+
                   '</summary><p class="answer">'+h(q["answer"])+'</p></details>')
    out.append('</details>')
    out.append('<details class="card"><summary>来源事实和 LP 对照</summary><div class="source" data-core="facts">')
    for p in points:
        for f in p["required_facts"]:
            out.append('<p data-fact-id="'+h(f["id"])+'">'+h(f["id"])+'：'+h(f["text"])+
                       '（'+h(f["span_id"])+'）</p>')
    out.append('</div></details>')
    out.append('<footer><button class="reset" type="button">重置当前解释</button>')
    out.append('<p class="lesson-footnote">操作图解和点击选择用于练习。真实掌握度来自学习者提交的回答及独立评分。</p>')
    out.append('<nav class="nav"><a href="'+h(previous)+'">上一页</a><a href="'+h(following)+'">下一页</a></nav>')
    out.append('</footer></main><script>'+JS+'</script></body></html>')
    return ''.join(out)
