"""Study V6.4 source-grounded, lesson-kind-aware HTML renderer.

Displays the approved *teaching sequence* rather than dumping a fixed JSON
field list. Uses only inline CSS/JS; all source- and author-derived text is
escaped. It does not execute source code or call a model.
"""
from __future__ import annotations
from html import escape
from pathlib import Path

def e(x):
    return escape(str(x),quote=True)

CSS = """
:root{--bg:#f3f6f4;--paper:#fff;--ink:#182c30;--muted:#54676e;
--line:#d5e1df;--accent:#165b74;--soft:#e8f2f5;--good:#176a4b;
--warn:#94522c;--gold:#f7eddd;--radius:16px}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);
color:var(--ink);font:16px/1.62 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:1060px;margin:auto;padding:24px 18px 72px}h1{font-size:clamp(32px,4.5vw,52px);
letter-spacing:-.035em;line-height:1.15;margin:12px 0}h2{font-size:clamp(21px,3vw,27px);
line-height:1.25;margin:0 0 12px}h3{font-size:18px;margin:18px 0 8px}
p{margin:10px 0}a{color:var(--accent)}.eyebrow{text-transform:uppercase;letter-spacing:.1em;
color:var(--accent);font-size:12px;font-weight:750}.sub{font-size:18px;color:var(--muted);
max-width:790px}.card{margin:18px 0;border:1px solid var(--line);border-radius:var(--radius);
background:var(--paper);padding:24px}.hero{padding:26px 0 6px}.question-box{
background:var(--soft);border-left:4px solid var(--accent);padding:15px 18px;border-radius:8px}
.mark{color:var(--accent);font-weight:800;font-size:12px;letter-spacing:.07em}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(235px,1fr));gap:12px}
.step,.timeline-item,.compare-item{border:1px solid var(--line);background:#f9fbfa;
padding:15px;border-radius:12px}.step-label{font-weight:760}.node-meaning{font-size:14px;
color:var(--muted);margin-top:5px}.link-label{font-size:13px;color:var(--accent);
font-weight:750;line-height:1.35;padding:7px 0}.process{display:grid;gap:5px}
.process .step{position:relative}.timeline-item.first-error{background:#fff0e8;
border-color:#dfbca9}.result-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.note{padding:14px 17px;border-radius:10px;background:var(--soft)}
.note.limit{background:#fff3e8}.case{background:#f5f8fa;border:1px solid var(--line);
border-radius:12px;padding:18px}.reason{padding-left:22px}.reason li{padding:5px 0}
table{border-collapse:collapse;width:100%;font-size:14px;min-width:480px}
th,td{border-bottom:1px solid var(--line);padding:12px;text-align:left;vertical-align:top}
th{background:#edf3f5}.overflow{overflow:auto}.formula{white-space:pre-wrap;
overflow-wrap:anywhere;background:#e9f1f5;border-radius:10px;padding:18px;
font-size:19px;font-family:ui-monospace,SFMono-Regular,Consolas,monospace}
dl{display:grid;grid-template-columns:minmax(90px,auto) 1fr;gap:8px}dt{font-weight:750}
dd{margin:0}.source-line{font-size:13px;color:var(--muted);border-top:1px solid var(--line);
padding:10px 0}.micro-details{border:1px solid var(--line);border-radius:12px;
padding:0 17px;margin-top:10px;background:#f7fbf9}.micro-details summary{cursor:pointer;
font-weight:700;padding:14px 0}.micro-details .answer{padding-bottom:15px;color:var(--good)}
.check{border-left:5px solid #c98a37}.choices{display:grid;gap:10px;margin:15px 0}
button{font:inherit;cursor:pointer;border:1px solid #b5cac7;border-radius:10px;
padding:11px 15px;background:#f8fbfa;color:var(--ink);text-align:left}
button:hover{background:#e9f4f3}.feedback{font-weight:750;min-height:24px}
button:focus-visible,a:focus-visible,summary:focus-visible{outline:3px solid #1b7a9b;outline-offset:3px}
.nav{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-top:25px}
.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0)}
@media(max-width:680px){main{padding:14px 12px 60px}.card{padding:17px}
.result-grid{grid-template-columns:1fr}body{font-size:16px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
"""
SCRIPT = """
document.querySelectorAll(".check .choices button").forEach(button=>{
 button.addEventListener("click",()=>{
  const panel=button.closest(".check"),f=panel.querySelector(".feedback");
  const ok=button.dataset.correct==="true";
  f.textContent=(ok?"正确。":"请重新检查：")+panel.dataset.explain;
  f.style.color=ok?"#176a4b":"#94522c";
 });
});
document.querySelectorAll(".reset").forEach(button=>{
 button.addEventListener("click",()=>{
  document.querySelectorAll(".feedback").forEach(f=>f.textContent="");
  document.querySelectorAll(".micro-details").forEach(d=>d.open=false);
 });
});
"""

def visual_markup(spec):
    v=spec["visual"]
    kind=v["kind"]
    out=[f'<section class="card visual" data-core="visual" data-visual-kind="{e(kind)}">',
         '<div class="mark">SEE THE RELATIONSHIP</div>',
         '<h2>把关系看清楚</h2>',f'<p>{e(v["purpose"])}</p>']
    if kind in ("process","decision","timeline","concept_map"):
        nodes={n["id"]:n for n in v["nodes"]}
        links=v.get("edges",[])
        wrapper="timeline" if kind=="timeline" else "process"
        out.append(f'<div class="{wrapper}" role="group" aria-label="{e(v["purpose"])}">')
        for index,node in enumerate(v["nodes"]):
            cls="timeline-item" if kind=="timeline" else "step"
            if kind=="timeline" and node["id"]==v.get("first_error_id"):
                cls+=" first-error"
            out.append(f'<div class="{cls}" data-step-id="{e(node["id"])}"><div class="step-label">{e(node["label"])}</div>'
                       f'<div class="node-meaning">{e(node["meaning"])}</div></div>')
            if index<len(v["nodes"])-1:
                dest=v["nodes"][index+1]["id"]
                labels=[edge["label"] for edge in links
                        if edge.get("from")==node["id"] and edge.get("to")==dest]
                if labels:out.append('<div class="link-label">↓ '+e(" · ".join(labels))+'</div>')
        # Preserve non-sequential edges in a readable relationship key.
        other=[x for x in links if not any(
            x.get("from")==v["nodes"][i]["id"] and
            x.get("to")==v["nodes"][i+1]["id"] for i in range(len(v["nodes"])-1))]
        if other:
            out.append('<p class="node-meaning">补充关系：'+"；".join(
                e(nodes[x["from"]]["label"])+" → "+e(nodes[x["to"]]["label"])+
                "："+e(x["label"]) for x in other)+'</p>')
        out.append('</div>')
    elif kind in ("comparison","experiment"):
        out.append('<div class="overflow"><table><thead><tr>')
        for col in v["columns"]:out.append('<th scope="col">'+e(col)+'</th>')
        out.append('</tr></thead><tbody>')
        for row in v["rows"]:
            out.append('<tr>'+"".join('<td>'+e(cell)+'</td>' for cell in row)+'</tr>')
        out.append('</tbody></table></div>')
        if v.get("data_provenance"):
            out.append('<p class="node-meaning">数据边界：'+e(v["data_provenance"])+'</p>')
    elif kind=="math":
        out.append('<div class="formula">'+e(v["formula"])+'</div><dl>')
        for symbol,meaning in v["variables"].items():
            out.append('<dt>'+e(symbol)+'</dt><dd>'+e(meaning)+'</dd>')
        out.append('</dl>')
    else:
        out.append('<p class="note">本页机制用清晰文字解释。'+e(v.get("purpose",""))+'</p>')
    out.append('</section>')
    return ''.join(out)


def _spine(spine):
    result=['<section class="card mechanism" data-core="mechanism">',
            '<div class="mark">HOW IT WORKS</div><h2>原理从哪里来</h2>',
            '<p>'+e(spine["core_explanation"])+'</p>','<ol class="reason">']
    for step in spine["causal_steps"]:
        result.append('<li>'+e(step)+'</li>')
    result.append('</ol></section>')
    example=spine["worked_example"]
    result.append('<section class="card" data-core="worked-example"><div class="mark">WORKED EXAMPLE</div>'
                  '<h2>跟着一个具体情境走一遍</h2><div class="case">')
    for k,title in (("scenario","场景"),("input","已知输入"),("outcome","得到的结果"),("why","为什么")):
        result.append('<p><strong>'+title+'：</strong>'+e(example[k])+'</p>')
    result.append('<ol class="reason">')
    for step in example["reasoning_steps"]:
        result.append('<li>'+e(step)+'</li>')
    result.append('</ol></div></section>')
    result.append('<section class="card" data-core="limits"><div class="mark">BOUNDARIES</div>'
                  '<h2>什么条件下成立？</h2><div class="result-grid"><div class="note">'
                  '<h3>适用条件</h3>')
    for item in spine["conditions"]:result.append('<p>'+e(item)+'</p>')
    result.append('</div><div class="note limit"><h3>容易误用的边界</h3>')
    for item in spine["limitations"]:result.append('<p>'+e(item)+'</p>')
    result.append('</div></div></section>')
    return ''.join(result)


def render(page, points, draft, source, spec, previous="index.html", following="index.html"):
    """Render an independently reviewed lesson. Never interpolate raw source HTML."""
    pid=e(page["page_id"])
    rows=['<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">',
          '<meta name="viewport" content="width=device-width,initial-scale=1">',
          '<title>'+e(page["title"])+'</title><style>'+CSS+'</style></head>',
          '<body data-lesson-contract="lesson-design-v1" data-page-id="'+pid+'"><main>',
          '<div class="eyebrow">STUDY · '+e(spec["lesson_kind"])+' · '+pid+'</div>',
          '<header class="hero"><h1>'+e(draft["title"])+'</h1>',
          '<p class="sub">'+e(spec["objective"])+'</p>',
          '<div class="question-box" data-core="goal"><strong>本页要回答：</strong>'+
          e(spec["central_question"])+'</div>',
          '<p>'+e(draft["intro"])+'</p></header>']
    rows.append(visual_markup(spec))
    shared=draft.get("shared_teaching")
    if shared:
        rows.append('<div data-shared-teaching="true">'+_spine(shared)+'</div>')
    for record in draft["teaching_evidence"]:
        if not shared:
            rows.append('<div data-teaching-lp="'+e(record["lp_id"])+'">'+_spine(record)+'</div>')
        else:
            rows.append('<section class="card" data-teaching-lp="'+e(record["lp_id"])+'"><h2>'+
                        e(next((p["title"] for p in points if p["lp_id"]==record["lp_id"]),
                           record["lp_id"]))+'</h2><p>'+e(record["lp_connection"])+'</p></section>')
        if record.get("fact_explanations"):
            rows.append('<section class="card"><div class="mark">SOURCE → UNDERSTANDING</div>'
                        '<h2>关键事实怎么支持机制</h2>')
            for explanation in record["fact_explanations"]:
                rows.append('<p data-authored-fact-id="'+e(explanation["fact_id"])+'">'+
                            e(explanation["explanation"])+'</p>')
            rows.append('</section>')
        if record.get("experiment"):
            ex=record["experiment"]
            rows.append('<section class="card"><h2>实验方法与结论</h2>')
            for key,label in (("purpose","实验目的"),("setup","设置"),
                              ("controls","对照"),("results","观察结果"),
                              ("limitations","可外推的边界")):
                rows.append('<p><strong>'+label+'：</strong>'+e(ex[key])+'</p>')
            rows.append('</section>')
    if draft.get("sections"):
        rows.append('<details class="card"><summary><strong>补充讲解与原文延伸</strong></summary>')
        for section in draft["sections"]:
            rows.append('<h3>'+e(section["heading"])+'</h3><p>'+e(section["text"])+'</p>')
        rows.append('</details>')
    rows.append('<section class="card"><div class="mark">PREDICT FIRST</div>'
                '<h2>先判断，再看解释</h2>')
    for item in draft.get("mini_questions",[]):
        rows.append('<div class="question"><details class="micro-details">'
                    '<summary>'+e(item["question"])+'</summary>'
                    '<div class="answer">'+e(item["answer"])+'</div>'
                    '</details></div>')
    rows.append('</section>')
    c=draft["checkpoint"]
    rows.append('<section class="card check" data-explain="'+e(c["feedback"])+'">'
                '<div class="mark">CHECKPOINT</div><h2>试着应用一下</h2>'
                '<p>'+e(c["question"])+'</p><div class="choices">')
    for i,option in enumerate(c["options"]):
        rows.append('<button type="button" data-correct="'+
                    str(i==c["correct_index"]).lower()+'">'+e(option)+'</button>')
    rows.append('</div><div class="feedback" aria-live="polite"></div>'
                '<details class="micro-details"><summary>查看评判依据</summary>'
                '<p>'+e(spec["checkpoint"]["rubric"])+'</p>'
                '<p>条件变化：'+e(spec["checkpoint"]["changed_condition"])+'</p>'
                '<p>正确推理应包含：'+e(spec["checkpoint"]["expected_reasoning"])+'</p>'
                '</details></section>')
    rows.append('<details class="card"><summary><strong>原文依据与 LP 定位</strong></summary>'
                '<p>以下材料用于核对来源。页面的解释和实例由教学者编写，需独立验证。</p>')
    for point in points:
        for fact in point["required_facts"]:
            rows.append('<p class="source-line" data-fact-id="'+e(fact["id"])+'">'+
                        '<strong>'+e(fact["id"])+'</strong> · '+e(fact["text"])+
                        ' ('+e(fact["span_id"])+')</p>')
    rows.append('</details>')
    rows.append('<p class="node-meaning">仅浏览页面、展开解释或点击答案均不改变学习掌握状态；'
                '实际理解需要提交可归因的回答。</p>')
    rows.append('<button class="reset" type="button">重置互动</button>')
    rows.append('<nav class="nav" aria-label="页面导航"><a href="'+e(previous)+
                '">上一页</a><a href="'+e(following)+'">下一页</a></nav>')
    rows.append('</main><script>'+SCRIPT+'</script></body></html>')
    return ''.join(rows)
