#!/usr/bin/env python3
"""Study V5: executable gates for source-grounded, audited visual learning.
Deterministic Host checks and rendering. The connected agent supplies model reasoning.
Windows-native; no WSL, LangChain or DeepTutor required.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import time
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import urllib.request
import urllib.error
import zipfile
import xml.etree.ElementTree as ET
import quality_contract as qc

ROOT = Path(__file__).resolve().parent
GATES = ("G1_SOURCE", "G2_PLAN", "G3_CONTENT", "G4_REVIEW", "G5_BROWSER", "G6_DELIVERY")

class GateError(Exception):
    pass

def sha(s):
    return hashlib.sha256((s if isinstance(s, bytes) else s.encode("utf-8"))).hexdigest()

def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def atomic_json(path, obj):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="._", suffix=".json", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f: json.dump(obj,f,ensure_ascii=False,indent=2)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def write_text(path, value):
    path=Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value,encoding="utf-8")

def state(ws):
    p=Path(ws)/"state.json"
    if p.exists(): return read_json(p)
    return {"version":"5.0", "phase":"NEW", "gates":{}, "current_unit":0,"artifacts":[],"learner_evidence":{},"return_point":None}

def save(ws, obj): atomic_json(Path(ws)/"state.json",obj)

def record_gate(ws, gate, ok, issues=None, evidence=None):
    st=state(ws); st["gates"][gate]={"ok":bool(ok),"issues":issues or [],"evidence":str(evidence or "")}
    if ok: st["phase"]=gate
    states={"G1_SOURCE":"SOURCE_VERIFIED","G2_PLAN":"PLAN_REVIEW_PASS",
      "G3_CONTENT":"CONTENT_STRUCTURAL_PASS","G4_REVIEW":"CONTENT_REVIEW_PASS",
      "G5_BROWSER":"BROWSER_PASS","G6_DELIVERY":"DELIVERY_CONFIRMED"}
    st.setdefault("verification",{})[gate]=(states.get(gate,"PASS") if ok else "BLOCKED")
    save(ws,st)
    if not ok: raise GateError(f"{gate} BLOCKED: {'; '.join(issues or ['unknown'])}")

def normalize_url(uri):
    if "github.com/" in uri and "/blob/" in uri:
        return uri.replace("github.com/", "raw.githubusercontent.com/").replace("/blob/","/")
    return uri

def source_text(source):
    source=str(source)
    raw=b""
    if re.match(r"^https?://",source):
        url=normalize_url(source)
        with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Study-V5/1.0"}),timeout=30) as f:
            raw=f.read(15*1024*1024+1)
        if len(raw)>15*1024*1024: raise GateError("source exceeds 15MB limit; import a local file or split scope")
        ext=Path(url.split("?")[0]).suffix.lower()
    else:
        p=Path(source)
        if not p.exists() or not p.is_file(): raise GateError("source file inaccessible")
        raw=p.read_bytes(); ext=p.suffix.lower()
    if ext in (".md",".markdown",".txt",".srt",".vtt",".py",".json",".yaml",".yml",""):
        return raw.decode("utf-8-sig"),ext
    if ext in (".html",".htm"):
        class Cleaner(HTMLParser):
            def __init__(self): super().__init__(); self.out=[]; self.skip=0
            def handle_starttag(self,tag,attrs):
                if tag in ("script","style"): self.skip+=1
                if tag in ("h1","h2","h3","h4","p","li"): self.out.append("\n")
            def handle_endtag(self,tag):
                if tag in ("script","style"): self.skip=max(0,self.skip-1)
                if tag in ("h1","h2","h3","h4","p","li"): self.out.append("\n")
            def handle_data(self,data):
                if not self.skip:self.out.append(data)
        h=Cleaner();h.feed(raw.decode("utf-8","replace"));return "".join(h.out),ext
    if ext==".docx":
        with zipfile.ZipFile(__import__('io').BytesIO(raw)) as z:
            root=ET.fromstring(z.read("word/document.xml"))
        ns={"w":"http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        parts=["".join(x.itertext()) for x in root.findall(".//w:p",ns)]
        return "\n".join(parts),ext
    if ext==".pdf":
        try: import fitz
        except ImportError: raise GateError("PDF parsing requires optional PyMuPDF (`pip install pymupdf`), or provide extracted text")
        doc=fitz.open(stream=raw,filetype="pdf")
        texts=[f"[PDF PAGE {i+1}]\n"+p.get_text() for i,p in enumerate(doc)]
        if not any(len(s.strip())>18 for s in texts): raise GateError("scanned PDF requires host image-based extraction")
        return "\n".join(texts),ext
    raise GateError(f"unsupported source format {ext}; use source-adapters.md in host to supply readable text")

def split_source(text):
    """Conservative bounded segments with intact source text, line anchors and hashes."""
    lines=text.splitlines(); segments=[]; header="(root)"; buf=[]; start=1; max_chars=1050
    def flush(end):
        nonlocal buf,start
        s="\n".join(buf).strip()
        if s:
            segments.append({"id":f"S{len(segments)+1:04}","heading":header,"line_start":start,"line_end":end,
                             "text":s,"sha256":sha(s)})
        buf=[]
    for n,line in enumerate(lines,1):
        if re.match(r"^#{1,6} +",line):
            flush(n-1);header=line.strip().lstrip('# ').strip();start=n
            # Header is part of source; preserve itself in segment when a new header starts.
            buf=[line];continue
        # Split overlong lines only on punctuation; never truncate.
        portions=re.split(r'(?<=[。！？.!?；;])(?=\S)',line) if len(line)>max_chars else [line]
        for part in portions:
            if buf and len("\n".join(buf))+len(part)>max_chars:
                flush(n-1 if n>start else n);start=n
            buf.append(part)
        if line.strip()=="" and len("\n".join(buf))>220:
            flush(n);start=n+1
    flush(len(lines))
    return segments

def ingest(ws, source):
    text,ext=source_text(source)
    if len(text.strip())<30: raise GateError("source too short / extraction failed")
    segments=split_source(text)
    if not segments: raise GateError("no source segments")
    w=Path(ws); w.mkdir(parents=True,exist_ok=True)
    write_text(w/"source.txt",text)
    obj={"source":str(source),"format":ext,"source_sha256":sha(text),"segments":segments,"line_count":len(text.splitlines()),"char_count":len(text)}
    atomic_json(w/"source.json",obj)
    st=state(w);st.update({"source_sha256":obj["source_sha256"],"phase":"G1_SOURCE","gates":{},"current_unit":0,"artifacts":[]});save(w,st)
    record_gate(w,"G1_SOURCE",True,evidence=w/"source.json")
    return obj

def group_chunks(spans, budget=6200):
    chunks=[]; cur=[]; size=0
    for sp in spans:
        d=len(sp["text"])+120
        if cur and size+d>budget:chunks.append(cur);cur=[];size=0
        cur.append(sp);size+=d
    if cur:chunks.append(cur)
    return chunks

def validate_plan(ws):
    source=read_json(Path(ws)/"source.json"); plan=read_json(Path(ws)/"plan.json")
    issues=[]
    if plan.get("source_sha256")!=source["source_sha256"]:issues.append("source revision drift")
    spans={x["id"] for x in source["segments"]}; pts=plan.get("points",[]); pages=plan.get("pages",[])
    lpids=[p.get("lp_id") for p in pts]; pids=[p.get("page_id") for p in pages]
    if len(set(lpids))!=len(lpids) or None in lpids:issues.append("LP IDs duplicate/missing")
    if len(set(pids))!=len(pids) or None in pids:issues.append("page IDs duplicate/missing")
    mapped=set(); factids=[]
    span_map={x["id"]:x for x in source["segments"]}
    for p in pts:
        ss=p.get("source_span_ids",[])
        if not ss:issues.append(f"{p.get('lp_id')}: no source anchors")
        mapped.update(ss)
        # Quantified minimum granularity. One LP cannot silently swallow an entire subsection.
        known=[span_map[x] for x in ss if x in span_map]
        if sum(len(x["text"]) for x in known)>1800:
            issues.append(f"{p.get('lp_id')}: >1800 source chars mapped to one atomic LP; split")
        if len({x["heading"] for x in known})>1:
            issues.append(f"{p.get('lp_id')}: crosses distinct source headings; split")
        if not p.get("goal") or not p.get("title"):issues.append(f"{p.get('lp_id')}: missing goal/title")
        facts=p.get("required_facts",[])
        if not facts:issues.append(f"{p.get('lp_id')}: missing required facts")
        for f in facts:
            factids.append(f.get("id"))
            if f.get("span_id") not in ss or not f.get("text"):
                issues.append(f"{p.get('lp_id')}: unanchored required fact")
    if len(set(factids))!=len(factids):issues.append("fact IDs duplicate")
    if spans-mapped:issues.append("unmapped source spans: "+", ".join(sorted(spans-mapped)[:30]))
    if mapped-spans:issues.append("unknown source spans: "+", ".join(sorted(mapped-spans)[:10]))
    mapped_pages=[]
    for p in pages:
        refs=p.get("lp_ids",[]);mapped_pages.extend(refs)
        if not refs:issues.append(f"{p.get('page_id')}: empty page")
        if plan.get("mode")=="study-d":
            # Learning Points are atomic coverage/evidence IDs; page grouping is a
            # separate teaching decision. Keep bounded cognitive load and require
            # an explicit reason and common learning objective for related LPs.
            if len(refs)>4:issues.append(f"{p.get('page_id')}: >4 LPs overload one deep page")
            if len(refs)>1:
                if not qc.substantial(p.get("grouping_rationale"),35):
                    issues.append(f"{p.get('page_id')}: grouped LPs require source-grounded grouping rationale")
                if not qc.substantial(p.get("learning_objective"),20):
                    issues.append(f"{p.get('page_id')}: grouped LPs require one shared learning objective")
        elif len(refs)>2:
            issues.append(f"{p.get('page_id')}: standard Unit holds more than two independent LPs")
    if set(lpids)-set(mapped_pages):issues.append("unassigned LPs: "+str(set(lpids)-set(mapped_pages)))
    if set(mapped_pages)-set(lpids):issues.append("page references unknown LP")
    if len(mapped_pages)!=len(set(mapped_pages)):issues.append("LP duplicated on multiple primary pages")
    if not pages:issues.append("no pages")
    scoped=dict(source,text=(Path(ws)/"source.txt").read_text(encoding="utf-8") if (Path(ws)/"source.txt").is_file() else "")
    issues.extend(qc.validate_deep_inventory(scoped,plan))
    report={"status":"pass" if not issues else "fail","issues":issues,"sources":len(spans),"LPs":len(pts),"pages":len(pages),"source_coverage":len(spans&mapped)/len(spans) if spans else 0}
    atomic_json(Path(ws)/"reports"/"plan-static.json",report)
    return report

def freeze(ws):
    report=validate_plan(ws)
    issues=list(report["issues"])
    rpath=Path(ws)/"reviews"/"plan-review.json"
    if not rpath.exists():issues.append("independent plan review missing")
    else:
        rev=read_json(rpath); p=read_json(Path(ws)/"plan.json")
        if not rev.get("approved"):issues.append("independent plan reviewer rejected")
        if rev.get("quality_audits_validated") is not True:
            issues.append("G2 atomicity/source semantic review receipt missing")
        if rev.get("plan_sha256")!=sha(json.dumps(p,sort_keys=True,ensure_ascii=False)):issues.append("plan changed after reviewer")
    plan=read_json(Path(ws)/"plan.json")
    src=read_json(Path(ws)/"source.json")
    if plan.get("mode")=="study-d" and (src["char_count"] > 12000 or len(plan["points"])>12):
        ap=Path(ws)/"owner-outline-approval.json"
        expected=sha(json.dumps(plan,sort_keys=True,ensure_ascii=False))
        if not ap.exists() or read_json(ap).get("plan_sha256")!=expected or read_json(ap).get("approved") is not True:
            issues.append("dense-source outline approval missing or stale; review plan then run approve-outline")
    if issues:record_gate(ws,"G2_PLAN",False,issues)
    atomic_json(Path(ws)/"frozen-plan.json",plan)
    record_gate(ws,"G2_PLAN",True,evidence=Path(ws)/"frozen-plan.json")

def validate_content_data(points,obj):
    issues=[]
    if not isinstance(obj,dict):return ["content must be JSON object"]
    required={f["id"] for p in points for f in p.get("required_facts",[])}
    represented=set(obj.get("represented_fact_ids",[]))
    if required-represented:issues.append("missing fact IDs: "+str(sorted(required-represented)))
    if not obj.get("intro"):issues.append("missing introduction")
    sections=obj.get("sections",[])
    if not isinstance(sections,list) or len(sections)<3:issues.append("insufficient teaching sections")
    elif any(not x.get("heading") or len(x.get("text","").strip())<25 for x in sections):issues.append("empty/shallow teaching section")
    if len(obj.get("mini_questions",[]))<len(points):issues.append("not enough hidden microquestions")
    for q in obj.get("mini_questions",[]):
        if not q.get("answer") or not q.get("question"):issues.append("empty microquestion")
    visual=obj.get("visual")
    if visual:
        if not isinstance(visual,dict) or visual.get("kind") not in ("flow","hierarchy","comparison") or len(visual.get("nodes",[]))<2:
            issues.append("invalid optional visual")
        elif not visual.get("relation") or any(not x.get("label") or not x.get("meaning") for x in visual["nodes"]):
            issues.append("visual nodes/edge semantics incomplete")
    sim=obj.get("simulation")
    if sim:
        if not isinstance(sim,dict) or sim.get("kind")!="preset" or len(sim.get("states",[]))<2:
            issues.append("invalid optional simulation")
        elif any(not all(x.get(k) for k in ("label","observation","explanation")) for x in sim["states"]):
            issues.append("simulation states missing teaching fields")
    c=obj.get("checkpoint",{})
    if len(c.get("options",[]))<3 or c.get("correct_index") not in (0,1,2) or not c.get("feedback"):issues.append("checkpoint interaction invalid")
    issues.extend(qc.validate_authored_teaching(points,obj))
    return issues

def esc(s):return html.escape(str(s),quote=True)

CSS='''
:root{--bg:#f5f8f7;--fg:#162b32;--card:#fff;--muted:#597076;--stroke:#d6e4e1;--accent:#326ba0;--success:#247653}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:17px/1.75 system-ui,-apple-system,"Segoe UI",sans-serif}main{max-width:950px;margin:auto;padding:28px 18px 68px}h1{font-size:clamp(30px,5vw,48px);line-height:1.25}h2{font-size:23px}p{white-space:pre-wrap}.card{border:1px solid var(--stroke);background:var(--card);padding:24px;border-radius:20px;margin:20px 0;box-shadow:0 8px 20px #16393c09}.lede{font-size:20px;color:var(--muted)}.hint{color:var(--muted);font-size:14px}.flow{display:flex;align-items:center;gap:9px;flex-wrap:wrap}.chip{border:1px solid var(--stroke);padding:8px 12px;border-radius:12px;background:#eef6fa}.arrow{color:var(--accent)}button{cursor:pointer;background:#fff;border:1px solid var(--stroke);border-radius:12px;padding:10px 14px;font:inherit;color:inherit}.answer{display:none;background:#edf8f2;padding:14px;margin-top:12px;border-radius:12px;border-left:3px solid var(--success)}.open .answer{display:block}.check button{display:block;margin:9px 0;width:100%;text-align:left}.feedback{font-weight:650}.sim-controls{display:flex;flex-wrap:wrap;gap:10px}.sim-result{background:#f0f5fa;padding:14px;border-radius:12px;margin:12px 0}.sim-static{margin-top:12px}.fact{border-left:3px solid var(--accent);padding:10px 14px;background:#f0f5fa;margin:10px 0}.nav{display:flex;justify-content:space-between;gap:15px;flex-wrap:wrap}a{color:var(--accent)}@media(max-width:600px){main{padding:12px}.card{padding:16px}}'''
JS='''document.querySelectorAll(".reveal").forEach(b=>b.addEventListener("click",()=>{const card=b.closest(".question");card.classList.toggle("open");b.setAttribute("aria-expanded",card.classList.contains("open")?"true":"false") }));document.querySelectorAll(".check button").forEach(b=>b.addEventListener("click",()=>{const box=b.closest(".check"),ok=b.dataset.correct==="true",f=box.querySelector(".feedback");f.textContent=(ok?"正确。":"再检查一下。")+box.dataset.explain;f.style.color=ok?"#247653":"#a44735";}));document.querySelectorAll(".sim-controls button").forEach(b=>b.addEventListener("click",()=>{const s=b.closest(".sim"),r=s.querySelector(".sim-result");r.textContent=b.dataset.observation+" — "+b.dataset.explanation;}));document.querySelectorAll(".reset").forEach(b=>b.addEventListener("click",()=>{document.querySelectorAll(".question").forEach(c=>c.classList.remove("open"));document.querySelectorAll("button.reveal").forEach(x=>x.setAttribute("aria-expanded","false"));document.querySelectorAll(".feedback").forEach(x=>x.textContent="");document.querySelectorAll(".sim").forEach(s=>s.querySelector(".sim-result").textContent=s.querySelector(".sim-controls button").dataset.observation+" — "+s.querySelector(".sim-controls button").dataset.explanation)}));'''

def html_page(page,points,draft,source,prev_href,next_href):
    rows=[]
    rows.append(f'<p class="hint">Study V5 · {esc(page["page_id"])} · 来源 SHA256 {esc(source["source_sha256"][:12])}</p>')
    rows.append(f'<h1>{esc(draft["title"])}</h1><p class="lede" data-core="intro">{esc(draft["intro"])}</p>')
    for i,x in enumerate(draft["sections"],1):
        rows.append(f'<section class="card" data-core="section-{i}"><h2>{esc(x["heading"])}</h2><p>{esc(x["text"])}</p></section>')
    # Source quotes remain visually separate from the actual tutorial explanation.
    shared=draft.get("shared_teaching")
    def render_spine(item):
        rows.append(f'<p data-core="mechanism">{esc(item["core_explanation"])}</p>')
        rows.append('<h3>因果步骤</h3><ol>')
        for step in item["causal_steps"]:rows.append(f'<li>{esc(step)}</li>')
        rows.append('</ol><h3>完整示例</h3>')
        example=item["worked_example"]
        for key,label in (("scenario","场景"),("input","输入"),("outcome","结果"),("why","为什么")):
            rows.append(f'<p><strong>{label}：</strong>{esc(example[key])}</p>')
        rows.append('<ol>')
        for step in example["reasoning_steps"]:rows.append(f'<li>{esc(step)}</li>')
        rows.append('</ol><h3>适用条件</h3>')
        for v in item["conditions"]:rows.append(f'<p>{esc(v)}</p>')
        rows.append('<h3>限制与反例</h3>')
        for v in item["limitations"]:rows.append(f'<p>{esc(v)}</p>')
    if shared:
        rows.append('<section class="card" data-shared-teaching="true"><h2>共同机制与推导</h2>')
        render_spine(shared)
        rows.append('</section>')
    for item in draft.get("teaching_evidence",[]):
        rows.append(f'<section class="card" data-teaching-lp="{esc(item["lp_id"])}"><h2>学习点的具体解释</h2>')
        if shared:
            rows.append(f'<p data-lp-connection="{esc(item["lp_id"])}">{esc(item["lp_connection"])}</p>')
        else:
            render_spine(item)
        for value in item.get("fact_explanations",[]):
            rows.append(f'<p data-authored-fact-id="{esc(value["fact_id"])}">{esc(value["explanation"])}</p>')
        if item.get("experiment"):
            rows.append('<h3>实验设计与结论的边界</h3>')
            for key in qc.EXPERIMENT_FACETS:
                rows.append(f'<p><strong>{esc(key)}：</strong>{esc(item["experiment"][key])}</p>')
        rows.append('</section>')
    rows.append('<section class="card"><h2>原文事实引用（原文摘录，独立于讲解）</h2>')
    for p in points:
        for fact in p["required_facts"]:
            rows.append(f'<div class="fact" data-fact-id="{esc(fact["id"])}"><strong>{esc(fact["id"])}</strong> · {esc(fact["text"])} <small>({esc(fact["span_id"])})</small></div>')
    rows.append('</section>')
    visual=draft.get("visual")
    if visual:
        rows.append(f'<section class="card" data-core="visual"><h2>{esc(visual["title"])}</h2><p class="hint">关系含义：{esc(visual["relation"])}</p><div class="flow">')
        for i,node in enumerate(visual["nodes"]):
            if i:rows.append(f'<span class="arrow" aria-label="{esc(visual["relation"])}">→</span>')
            rows.append(f'<div class="chip"><strong>{esc(node["label"])}</strong><br><small>{esc(node["meaning"])}</small></div>')
        rows.append('</div></section>')
    sim=draft.get("simulation")
    if sim:
        rows.append(f'<section class="card sim"><h2>{esc(sim["title"])}</h2><p class="hint">预设教学模拟。先预测条件变化的结果，再切换观察。</p><div class="sim-controls">')
        for state in sim["states"]:
            rows.append(f'<button type="button" data-observation="{esc(state["observation"])}" data-explanation="{esc(state["explanation"])}">{esc(state["label"])}</button>')
        first=sim["states"][0]
        rows.append(f'</div><p class="sim-result" aria-live="polite">{esc(first["observation"])} — {esc(first["explanation"])}</p>')
        rows.append('<div class="sim-static"><h3>全部条件、结果与解释（关闭脚本仍可见）</h3>')
        for state in sim["states"]:
            rows.append(f'<p><strong>{esc(state["label"])}</strong>：{esc(state["observation"])}。{esc(state["explanation"])}</p>')
        rows.append('</div></section>')
    rows.append('<section class="card"><h2>隐藏小问题：先判断，再揭示</h2>')
    for q in draft["mini_questions"]:
        rows.append(f'<div class="question"><p>{esc(q["question"])}</p><button class="reveal" type="button" aria-expanded="false">查看解释</button><div class="answer">{esc(q["answer"])}</div></div>')
    rows.append('</section>')
    c=draft["checkpoint"]
    rows.append(f'<section class="card check" data-explain="{esc(c["feedback"])}"><h2>Checkpoint</h2><p>{esc(c["question"])}</p>')
    for i,option in enumerate(c["options"]):
        rows.append(f'<button type="button" data-correct="{str(i==c["correct_index"]).lower()}">{esc(option)}</button>')
    rows.append('<div class="feedback" aria-live="polite"></div></section>')
    rows.append('<p><button class="reset" type="button">重置本页互动</button></p>')
    rows.append(f'<nav class="nav"><a href="{esc(prev_href)}">上一页</a><a href="{esc(next_href)}">下一页</a></nav>')
    return '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(page["title"])+f'</title><style>{CSS}</style></head><body><main>'+"".join(rows)+f'</main><script>{JS}</script></body></html>'

def build_pages(ws, only_missing=True):
    plan=read_json(Path(ws)/"frozen-plan.json"); source=read_json(Path(ws)/"source.json")
    pages=plan["pages"]; pts={p["lp_id"]:p for p in plan["points"]}; out=Path(ws)/"draft-pages";out.mkdir(parents=True,exist_ok=True)
    contents=[]
    for i,page in enumerate(pages):
        pn=page["page_id"]+".html"
        points=[pts[x] for x in page["lp_ids"]]
        draftpath=Path(ws)/"drafts"/(page["page_id"]+".json")
        draft=read_json(draftpath) if draftpath.exists() else None
        if draft is None:raise GateError(f"host-authored draft missing: {draftpath}")
        issues=validate_content_data(points,draft)
        if issues:raise GateError(page["page_id"]+" draft invalid: "+str(issues))
        prev="index.html" if i==0 else pages[i-1]["page_id"]+".html"
        nxt="index.html" if i==len(pages)-1 else pages[i+1]["page_id"]+".html"
        h=html_page(page,points,draft,source,prev,nxt)
        write_text(out/pn,h); contents.append({"page_id":page["page_id"],"file":pn,"lp_ids":page["lp_ids"],"draft_sha256":sha(json.dumps(draft,ensure_ascii=False,sort_keys=True)), "rendered_sha256":sha(h)})
    idx=['<h1>Study V5 · 深度学习目录</h1><p>按知识依赖逐页阅读。每页包含完整解释、隐藏小问题和独立 Checkpoint。</p>']
    for p in pages:idx.append(f'<div class="card"><a href="{esc(p["page_id"])}.html">{esc(p["page_id"])} · {esc(p["title"])}</a></div>')
    write_text(out/"index.html",'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+CSS+'</style><main>'+"".join(idx)+'</main></html>')
    atomic_json(Path(ws)/"content-manifest.json",{"source_sha256":source["source_sha256"],"pages":contents,"index":"index.html"})
    return contents

def content_static_check(ws):
    manifest=read_json(Path(ws)/"content-manifest.json");plan=read_json(Path(ws)/"frozen-plan.json")
    pmap={p["lp_id"]:p for p in plan["points"]};issues=[]
    pages_dir=Path(ws)/"draft-pages"
    for info in manifest["pages"]:
        page=pages_dir/info["file"]
        if not page.exists():issues.append("missing "+str(page));continue
        h=page.read_text(encoding="utf-8")
        draftpath=Path(ws)/"drafts"/(info["page_id"]+".json")
        if not draftpath.is_file():issues.append("missing reviewed draft for "+info["page_id"]);continue
        draft=read_json(draftpath)
        related=[pmap[lp] for lp in info["lp_ids"]]
        issues.extend(info["file"]+": "+reason for reason in validate_content_data(related,draft))
        if sha(json.dumps(draft,ensure_ascii=False,sort_keys=True))!=info.get("draft_sha256"):
            issues.append(info["file"]+" source draft changed since HTML rendering")
        if info.get("rendered_sha256") and sha(page.read_bytes())!=info["rendered_sha256"]:
            issues.append(info["file"]+" HTML bytes changed since rendering")
        for text in qc.authored_text(draft):
            if qc.substantial(text,35) and esc(text) not in h:
                issues.append(info["file"]+" authored explanatory text absent from HTML")
        for id in info["lp_ids"]:
            if f'data-teaching-lp="{esc(id)}"' not in h:
                issues.append(info["file"]+" missing tutor-authored mechanism for "+id)
            for fact in pmap[id]["required_facts"]:
                if f'data-authored-fact-id="{esc(fact["id"])}"' not in h:
                    issues.append(f"{info['file']} missing authored explanation for {fact['id']}")
                if f'data-fact-id="{esc(fact["id"])}"' not in h: issues.append(f"{info['file']} missing source quote {fact['id']}")
                if esc(fact["text"]) not in h:issues.append(f"{info['file']} lost source fact {fact['id']}")
        if 'class="check"' not in h and 'class="card check"' not in h:issues.append(info["file"]+" missing checkpoint")
        if 'class="reveal"' not in h:issues.append(info["file"]+" missing interactive questions")
        for link in re.findall(r'href="([^"]+)"',h):
            if link.endswith('.html') and not (pages_dir/link).exists():issues.append(info["file"]+" broken link "+link)
    report={"status":"pass" if not issues else "fail","issues":issues,"page_count":len(manifest["pages"])}
    report["manifest_sha256"]=sha((Path(ws)/"content-manifest.json").read_bytes())
    atomic_json(Path(ws)/"reports"/"content-static.json",report)
    return report

def browser_qa(ws):
    manifest=read_json(Path(ws)/"content-manifest.json")
    try:from playwright.sync_api import sync_playwright
    except ImportError:
        report={"passed":False,"browser_executed":False,"issues":["Playwright unavailable; browser test unverified"]}
        atomic_json(Path(ws)/"reports"/"browser.json",report);return report
    issues=[];runs=0
    class QuietHTTP(SimpleHTTPRequestHandler):
        def log_message(self, *args): pass
    server=ThreadingHTTPServer(("127.0.0.1",0),partial(QuietHTTP,directory=str((Path(ws)/"draft-pages").resolve())))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    urlbase=f"http://127.0.0.1:{server.server_port}/"
    try:
      with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get("STUDY_CHROMIUM") or shutil.which("chromium") or shutil.which("google-chrome") or None)
        for page_info in manifest["pages"]:
            page=browser.new_page(viewport={"width":390,"height":840})
            page.set_content((Path(ws)/"draft-pages"/page_info["file"]).read_text(encoding="utf-8"))
            if page.locator(".card.check button").count()<3:issues.append(page_info["file"]+" missing checkpoint options")
            else:
                page.locator(".card.check button[data-correct=true]").click()
                if not page.locator(".feedback").inner_text().startswith("正确"):issues.append(page_info["file"]+" checkpoint feedback broken")
            if page.locator(".sim-controls button").count()>1:
                page.locator(".sim-controls button").last.click()
                expected=page.locator(".sim-controls button").last.get_attribute("data-observation")
                if expected not in page.locator(".sim-result").inner_text():issues.append(page_info["file"]+" simulation condition switch broken")
            if not page.locator("button.reveal").count():issues.append(page_info["file"]+" missing reveal")
            else:
                page.locator("button.reveal").first.focus();page.keyboard.press("Enter")
                if not page.locator(".question .answer").first.is_visible():issues.append(page_info["file"]+" reveal keyboard broken")
            page.locator("button.reset").click()
            if page.locator(".question .answer").first.is_visible():issues.append(page_info["file"]+" reset failed")
            if page.evaluate("document.documentElement.scrollWidth > innerWidth+3"):issues.append(page_info["file"]+" horizontal overflow on mobile")
            page.set_viewport_size({"width":1280,"height":900})
            if page.evaluate("document.documentElement.scrollWidth > innerWidth+3"):
                issues.append(page_info["file"]+" horizontal overflow on desktop")
            page.close();runs+=1
            static=browser.new_page(java_script_enabled=False)
            static.set_content((Path(ws)/"draft-pages"/page_info["file"]).read_text(encoding="utf-8"))
            if static.locator("[data-core]").count()<3 or not static.locator("[data-fact-id]").count():issues.append(page_info["file"]+" JS-disabled core content incomplete")
            static.close()
        browser.close()
    finally:
      server.shutdown();server.server_close()
    report={"passed":not issues,"browser_executed":True,"pages_tested":runs,"issues":issues,
            "rendered_files":{x["file"]:sha((Path(ws)/"draft-pages"/x["file"]).read_bytes()) for x in manifest["pages"]},
            "manifest_sha256":sha((Path(ws)/"content-manifest.json").read_bytes()),
            "viewports_tested":[390,1280],"keyboard_tested":True,
            "js_disabled_tested":True,"interactive_tested":True}
    atomic_json(Path(ws)/"reports"/"browser.json",report)
    return report

def verify(ws):
    issues=[]; report=content_static_check(ws)
    issues.extend(report["issues"])
    if issues:record_gate(ws,"G3_CONTENT",False,issues)
    record_gate(ws,"G3_CONTENT",True,evidence=Path(ws)/"reports"/"content-static.json")
    revpath=Path(ws)/"reviews"/"content-review.json"
    if not revpath.exists():record_gate(ws,"G4_REVIEW",False,["independent content review missing"])
    rev=read_json(revpath)
    if not rev.get("approved") or any(x.get("issues") for x in rev.get("pages",[])):record_gate(ws,"G4_REVIEW",False,["independent content review rejected"]+[str(x) for x in rev.get("pages",[]) if not x.get("approved")][:5])
    plan=read_json(Path(ws)/"frozen-plan.json");source=read_json(Path(ws)/"source.json")
    lookup={p["lp_id"]:p for p in plan["points"]}
    page_map={p["page_id"]:p for p in plan["pages"]}
    if rev.get("quality_audits_validated") is not True or len(rev.get("pages",[]))!=len(page_map):
        record_gate(ws,"G4_REVIEW",False,["semantic reviewer receipt missing or incomplete"])
    for item in rev["pages"]:
        if item.get("quality_audits_validated") is not True or item.get("page_id") not in page_map:
            record_gate(ws,"G4_REVIEW",False,["per-page semantic audit absent"])
        draft=read_json(Path(ws)/"drafts"/(item["page_id"]+".json"))
        relevant=[lookup[lp] for lp in page_map[item["page_id"]]["lp_ids"]]
        semantic=qc.validate_content_review_audits(item,relevant,draft,source)
        if semantic:record_gate(ws,"G4_REVIEW",False,semantic)
    # Ensure the content under review has not changed after a reviewer attested.
    for item in rev.get("pages",[]):
        draft=read_json(Path(ws)/"drafts"/(item["page_id"]+".json"))
        if sha(json.dumps(draft,sort_keys=True,ensure_ascii=False))!=item.get("draft_sha256"):
            record_gate(ws,"G4_REVIEW",False,["stale content review for "+item["page_id"]])
    record_gate(ws,"G4_REVIEW",True,evidence=revpath)
    b=browser_qa(ws)
    if not b.get("passed") or b.get("browser_executed") is not True:
        record_gate(ws,"G5_BROWSER",False,b.get("issues") or ["real browser QA not executed"])
    manifest=read_json(Path(ws)/"content-manifest.json")
    if b.get("viewports_tested")!=[390,1280] or any(
       b.get(k) is not True for k in ("keyboard_tested","js_disabled_tested","interactive_tested")):
        record_gate(ws,"G5_BROWSER",False,["interactive/mobile/desktop/keyboard/JS-off checks incomplete"])
    if b.get("manifest_sha256")!=sha((Path(ws)/"content-manifest.json").read_bytes()) or any(
       b.get("rendered_files",{}).get(x["file"])!=sha((Path(ws)/"draft-pages"/x["file"]).read_bytes())
       for x in manifest["pages"]):
        record_gate(ws,"G5_BROWSER",False,["browser receipt does not bind exact generated HTML bytes"])
    record_gate(ws,"G5_BROWSER",True,evidence=Path(ws)/"reports"/"browser.json")

def publish(ws):
    """Publish verified bytes; G6 remains PREPARED until the learner sees the full queue."""
    st=state(ws)
    missing=[g for g in GATES[:-1] if not st["gates"].get(g,{}).get("ok")]
    if missing:record_gate(ws,"G6_DELIVERY",False,["missing gates: "+", ".join(missing)])
    # Recheck the current reviewed draft and page structure before publication.
    report=content_static_check(ws)
    if report["issues"]:record_gate(ws,"G3_CONTENT",False,report["issues"])
    source=read_json(Path(ws)/"source.json")
    plan=read_json(Path(ws)/"frozen-plan.json")
    review=read_json(Path(ws)/"reviews"/"content-review.json")
    if review.get("source_sha256")!=source["source_sha256"] or review.get("plan_sha256")!=sha(json.dumps(plan,sort_keys=True,ensure_ascii=False)):
        record_gate(ws,"G4_REVIEW",False,["stale review source/plan"])
    for page in review.get("pages",[]):
        draft=read_json(Path(ws)/"drafts"/(page["page_id"]+".json"))
        if sha(json.dumps(draft,sort_keys=True,ensure_ascii=False))!=page.get("draft_sha256"):
            record_gate(ws,"G4_REVIEW",False,["stale draft review "+page["page_id"]])
    manifest=read_json(Path(ws)/"content-manifest.json")
    b=read_json(Path(ws)/"reports"/"browser.json")
    if b.get("manifest_sha256")!=sha((Path(ws)/"content-manifest.json").read_bytes()) or any(
       b.get("rendered_files",{}).get(x["file"])!=sha((Path(ws)/"draft-pages"/x["file"]).read_bytes())
       for x in manifest["pages"]):
        record_gate(ws,"G5_BROWSER",False,["published files differ from inspected browser QA bytes"])
    dst=Path(ws)/"published";dst.mkdir(exist_ok=True)
    files=["index.html"]+[item["file"] for item in manifest["pages"]]
    for name in files:
        src=Path(ws)/"draft-pages"/name
        if not src.is_file():record_gate(ws,"G6_DELIVERY",False,["missing generated page "+name])
        shutil.copy2(src,dst/name)
    st=state(ws)
    st["artifacts"]=[{"file":str((dst/name).resolve()),"sha256":sha((dst/name).read_bytes()),"verified":True} for name in files]
    st.setdefault("gates",{})["G6_DELIVERY"]={"ok":False,"status":"PREPARED","issues":[],"evidence":str(dst)}
    st.setdefault("verification",{})["G6_DELIVERY"]="PREPARED"
    st["phase"]="G6_PREPARED"
    save(ws,st)
    atomic_json(Path(ws)/"delivery-queue.json",{"cursor":0,"files":files,"one_link_per_turn":True})
    return dst

def demo(ws):
    """Offline demonstration with fixture content, not model-quality evidence."""
    w=Path(ws);w.mkdir(parents=True,exist_ok=True)
    fixture=ROOT/"fixtures"/"training-mini.md"
    ingest(w,fixture)
    src=read_json(w/"source.json")
    pts=[]
    for i,s in enumerate(src["segments"],1):
        pts.append({"lp_id":f"LP{i:04}","title":f"学习点 {i}: {s['heading']}","kind":"mechanism","goal":"理解来源内容的机制与条件","source_span_ids":[s["id"]],"prerequisites":[],
                    "required_facts":[{"id":f"F{i:04}-01","text":s["text"],"span_id":s["id"],"source_quote":s["text"][:90]}],
                    "inventory_ids":[f"I{i:04}"]})
    pages=[{"page_id":f"P{i:03}","lp_ids":[p["lp_id"]],"title":p["title"]} for i,p in enumerate(pts,1)]
    inventory=[{"id":f"I{i:04}","kind":"mechanism","span_id":seg["id"],
                "title":f"Source mechanism {i}","objective":"Explain how this verified source segment works",
                "source_quote":seg["text"][:100]} for i,seg in enumerate(src["segments"],1)]
    plan={"source_sha256":src["source_sha256"],"points":pts,"pages":pages,"mode":"study-d",
          "source_inventory":inventory,"experiment_coverage":[],"reflection_coverage":[]}
    atomic_json(w/"plan.json",plan)
    report=validate_plan(w)
    if report["issues"]:raise GateError("offline fixture plan invalid: "+str(report["issues"]))
    atomic_json(w/"reviews"/"plan-review.json",{"approved":True,"issues":[],"plan_sha256":sha(json.dumps(plan,sort_keys=True,ensure_ascii=False)),
        "quality_audits_validated":True,"fixture_only":True})
    freeze(w)
    for p in pages:
        id=p["lp_ids"][0];point=next(x for x in pts if x["lp_id"]==id)
        payload={"title":p["title"],"intro":"这是离线机制演示，来源核心要点完整保留。", "sections":[
            {"heading":"为什么有这个机制","text":"展示系统怎样处理来源输入、形成输出，并保留验证证据。这里的内容是测试样例，不代表模型生成质量。"},
            {"heading":"输入、过程、输出","text":"输入来自源文件，系统分割后保留 SHA256 和段落标记，内容合同关联来源信息与课件页面。"},
            {"heading":"条件与边界","text":"本页面用于检查点击、键盘、移动布局和静态回退；实际课程需要外部模型生成解释并由独立 Reviewer 审核。"}],
            "mini_questions":[{"question":"如果源文件改变，原来的规划还能直接使用吗？","answer":"需要重新检查源文件哈希并更新规划合同。"}],
            "checkpoint":{"question":"哪些证据可以证明课程来源未被静默替换？","options":["页面颜色","来源 SHA256 与引用锚点","按钮数量"],"correct_index":1,"feedback":"SHA256 与来源锚点用于检测漂移和定位。"},
            "represented_fact_ids":[point["required_facts"][0]["id"]],
            "visual":{"kind":"flow","title":"从原文到可验证的课件","nodes":[
                {"label":"Source","meaning":"保留原文字节与哈希"},{"label":"Contract","meaning":"登记所有必要学习信息"},
                {"label":"HTML","meaning":"将必要信息完整呈现"}],"relation":"信息与证据的依次传递"},
            "simulation":{"title":"来源更新状态对照","kind":"preset","states":[
                {"label":"来源未更新","observation":"Hash 一致","explanation":"现有规划仍适用于当前版本"},
                {"label":"来源已更新","observation":"Hash 不一致","explanation":"需要重新验证来源和页面合同"}]}}
        # Explicitly marked fixture: rich structured teaching keeps structural tests meaningful.
        payload["checkpoint"]["rubric"]="正确选项需要解释来源哈希为何固定材料版本，并说明锚点如何定位相应机制，以及旧材料变化会产生什么风险。"
        payload["teaching_evidence"]=[{
          "lp_id":id,
          "core_explanation":("源材料记录了从输入到输出的具体信息流程。学习者必须先读取源片段、确认可引用的来源位置，再将机制转换成明确可检验的内容约束。"+
                              "本演示强调文件哈希记录的是哪个版本的材料，知识点与事实 ID 记录的是哪一条依据。"+
                              "当来源发生变化时，复用旧内容可能产生错误，因此要重新比较证据后才能确认原有解释是否仍然成立。"),
          "causal_steps":[
            "先读取整个目标范围并保存原始来源的内容哈希和稳定片段编号，因为没有原文证据，任何教学解释都可能混淆版本。",
            "随后把来源片段映射到单独学习点及每条事实，让页面生成和审核能追溯遗漏的具体条件以及产生的后果。"],
          "worked_example":{
            "scenario":"某位学习者在复习来源材料后发现章节文本发生修改，需要判断旧版课程是否仍能用于当前学习。",
            "input":"原始章节哈希、最新章节原文，以及课程保存的来源片段和学习点对应表。",
            "reasoning_steps":[
               "首先比较当前原文与保存版本的 SHA256 指纹，识别是否发生任何可观测的文本修订。",
               "接着根据稳定的片段锚点核查被改动的条件，并重新评估引用它的教学内容与考核标准。"],
            "outcome":"若关键条件已变化，应更新相应学习点、页面解释和审核结果，再继续按新版本讲授。",
            "why":"这样能区分真正被影响的内容与保持有效的知识点，减少无差别重复学习，也让审阅者能够追溯每个判断的原始依据。此过程还需要检查条件变化是否影响实际结果，不能仅凭来源指纹改变就判断原有教学结论已失效。"},
          "conditions":["该流程适用于能够读取原文并取得可靠片段锚点的资料；其他资料应明确记录缺失范围并进行相应降级处理。"],
          "limitations":["哈希变化只能证明文件内容发生变化，不能独立判断概念是否改变，还需审阅具体片段及其对结论的影响。"],
          "fact_explanations":[{"fact_id":point["required_facts"][0]["id"],
             "explanation":"对应的来源事实是本页教学推导的起点。它用于证明为什么需要保留可复核的原始材料、稳定编号以及从机制到页面的映射关系。仅展示原始摘录只能说明材料存在，完整理解还需要通过上述步骤和改变条件的例子来解释其作用。"}]
        }]
        atomic_json(w/"drafts"/(p["page_id"]+".json"),payload)
    build_pages(w)
    rep=content_static_check(w)
    if rep["issues"]:raise GateError(str(rep["issues"]))
    b=browser_qa(w)
    atomic_json(w/"reports"/"DEMO-NOT-PRODUCTION.json",{"note":"Only fixture structural/browser test. No real LLM author/reviewer tests run.","static":rep,"browser":b})
    return {"pages":len(pages),"browser":b,"workspace":str(w)}


def approve_outline(ws):
    """Only invoke after user explicitly approved the visible draft outline."""
    report=validate_plan(ws)
    if report["issues"]:raise GateError("G2 static plan invalid; cannot approve")
    p=read_json(Path(ws)/"plan.json")
    r=read_json(Path(ws)/"reviews"/"plan-review.json")
    expected=sha(json.dumps(p,sort_keys=True,ensure_ascii=False))
    if not r.get("approved") or r.get("plan_sha256")!=expected or r.get("quality_audits_validated") is not True:
        raise GateError("independent atomicity/source reviewer must approve same plan first")
    atomic_json(Path(ws)/"owner-outline-approval.json",{"approved":True,"plan_sha256":expected,"actor":"user-approved-via-host"})
    return {"approved":True,"plan_sha256":expected}

def next_delivery(ws):
    """Prepare one verified HTML for the host. The cursor advances on confirmation."""
    w=Path(ws);qpath=w/"delivery-queue.json"
    if not qpath.exists():raise GateError("published delivery queue unavailable")
    q=read_json(qpath);i=q.get("cursor",0)
    if i>=len(q["files"]):return {"finished":True,"remaining":0}
    name=q["files"][i];target=(w/"published"/name).resolve()
    if not target.is_file():raise GateError("missing verified delivery file: "+name)
    # The pending receipt is repeatable and cannot silently skip the page.
    fingerprint=sha(target.read_bytes())
    pending=q.get("pending")
    if pending and (pending.get("index")!=i+1 or pending.get("sha256")!=fingerprint
                    or pending.get("file")!=str(target)):
        raise GateError("pending delivery changed; inspect and reconcile before retry")
    q["pending"]={"index":i+1,"file":str(target),"sha256":fingerprint}
    atomic_json(qpath,q)
    return {"file":str(target),"index":i+1,"total":len(q["files"]),
            "remaining":len(q["files"])-i,"one_link_this_turn":True,
            "awaiting_confirmation":True,"sha256":fingerprint}


def confirm_delivery(ws,file):
    """Host-only receipt after the exact prepared page is accessible to the learner."""
    w=Path(ws);qpath=w/"delivery-queue.json"
    if not qpath.exists():raise GateError("published delivery queue unavailable")
    q=read_json(qpath);candidate=Path(file).resolve()
    if q.get("confirmed") and q["confirmed"].get("file")==str(candidate):
        receipt=q["confirmed"]
        if not candidate.is_file() or sha(candidate.read_bytes())!=receipt["sha256"]:
            raise GateError("previously confirmed page has changed")
        return {"confirmed":True,"duplicate":True,"index":receipt["index"],
                "file":str(candidate)}
    pending=q.get("pending")
    if not pending:raise GateError("prepare delivery before confirming")
    if pending["file"]!=str(candidate):
        raise GateError("confirmation does not match pending page")
    if not candidate.is_file() or sha(candidate.read_bytes())!=pending["sha256"]:
        raise GateError("pending page missing or modified")
    if pending["index"]!=q["cursor"]+1:
        raise GateError("delivery index drift; manual reconciliation required")
    q["cursor"]+=1
    q["confirmed"]=pending
    q.pop("pending",None)
    atomic_json(qpath,q)
    st=state(w)
    finished=q["cursor"]==len(q["files"])
    st.setdefault("verification",{})["G6_DELIVERY"]="DELIVERY_CONFIRMED" if finished else "IN_PROGRESS"
    st.setdefault("gates",{})["G6_DELIVERY"]={"ok":finished,"status":st["verification"]["G6_DELIVERY"],
        "issues":[],"evidence":str(qpath)}
    if finished:st["phase"]="G6_DELIVERY"
    save(w,st)
    return {"confirmed":True,"duplicate":False,"index":q["cursor"],
            "file":str(candidate),"remaining":len(q["files"])-q["cursor"]}

def consolidate(ws,topic=""):
    """One self-contained, completely expanded archive. No JS-dependent essential content."""
    plan=read_json(Path(ws)/"frozen-plan.json"); source=read_json(Path(ws)/"source.json")
    pt={p["lp_id"]:p for p in plan["points"]}; sections=[]; matched=0
    for page in plan["pages"]:
        if topic and topic.lower() not in page["title"].lower() and not any(topic.lower() in pt[x]["title"].lower() for x in page["lp_ids"]):
            continue
        draftfile=Path(ws)/"drafts"/(page["page_id"]+".json")
        if not draftfile.exists():raise GateError("missing draft for consolidation: "+page["page_id"])
        d=read_json(draftfile);ids=page["lp_ids"];points=[pt[x] for x in ids]
        issues=validate_content_data(points,d)
        if issues:raise GateError("cannot consolidate incomplete page: "+str(issues))
        matched+=1
        sections.append(f'<section class="card"><h2>{esc(page["page_id"]+" · "+d["title"])}</h2><p>{esc(d["intro"])}</p>')
        for block in d["sections"]:
            sections.append(f'<h3>{esc(block["heading"])}</h3><p>{esc(block["text"])}</p>')
        sections.append('<h3>完整来源要点（含条件与边界）</h3>')
        for point in points:
            for fact in point["required_facts"]:
                sections.append(f'<p class="fact" data-fact-id="{esc(fact["id"])}">{esc(fact["id"])} · {esc(fact["text"])} ({esc(fact["span_id"])})</p>')
        if d.get("visual"):
            v=d["visual"]
            sections.append(f'<h3>知识关系图：{esc(v["title"])}</h3><p>关系含义：{esc(v["relation"])}</p>')
            for node in v["nodes"]:
                sections.append(f'<p>{esc(node["label"])}：{esc(node["meaning"])}</p>')
        if d.get("simulation"):
            sections.append('<h3>互动模拟的全部条件与结果</h3>')
            for v in d["simulation"]["states"]:
                sections.append(f'<p><strong>{esc(v["label"])}</strong>：{esc(v["observation"])}。{esc(v["explanation"])}</p>')
        sections.append('<h3>小问题与答案</h3>')
        for item in d["mini_questions"]:
            sections.append(f'<p><b>问：</b>{esc(item["question"])}<br><b>答：</b>{esc(item["answer"])}</p>')
        c=d["checkpoint"];sections.append(f'<h3>Checkpoint + 标准答案</h3><p>{esc(c["question"])}</p><ol>')
        for i,opt in enumerate(c["options"]):sections.append(f'<li>{esc(opt)}'+(' <strong>（正确）</strong>' if i==c["correct_index"] else '')+'</li>')
        sections.append(f'</ol><p>{esc(c["feedback"])}</p></section>')
    if not matched:raise GateError("no pages matched consolidation topic")
    # Exam artifacts (if supplied) must be included with answer keys or explicitly declared absent.
    exam_dir=Path(ws)/"exams"
    if exam_dir.exists():
        for f in sorted(exam_dir.glob("*.json")):
            e=read_json(f)
            if topic and topic.lower() not in f.stem.lower() and topic.lower() not in str(e.get("topic","")).lower():continue
            questions=e.get("questions",[])
            for item in questions:
                if not item.get("answer") or not item.get("question"):
                    raise GateError("consolidation requires verified answer for every exam item: "+f.name)
                sections.append(f'<section class="card"><h3>试题：{esc(item["question"])}</h3><p>标准答案：{esc(item["answer"])}</p><p>判定依据：{esc(item.get("rubric","以源材料为准"))}</p></section>')
    h='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Study V5 完整课件</title><style>'+CSS+'</style></head><body><main><h1>Study V5 · 完整归档</h1><p class="hint">所有核心知识、问题与答案直接可见，关闭 JavaScript 也能阅读。来源 SHA256 '+esc(source["source_sha256"][:12])+'</p>'+''.join(sections)+'</main></body></html>'
    dest=Path(ws)/"consolidated"/("all" if not topic else re.sub(r"[^A-Za-z0-9_\-]","_",topic)[:50] or "topic")
    dest=dest.with_suffix('.html');write_text(dest,h)
    # Render integrity using the same explicit source fact IDs.
    for point in plan["points"]:
        if topic and topic.lower() not in point["title"].lower() and not any(point["lp_id"] in x["lp_ids"] and topic.lower() in x["title"].lower() for x in plan["pages"]):continue
        for fact in point["required_facts"]:
            if esc(fact["text"]) not in h:raise GateError("consolidation lost fact: "+fact["id"])
    return {"file":str(dest),"pages":matched,"js_required":False}

def record_evidence(ws,data_file):
    """Track actual learner evidence; page views never set mastery."""
    record=read_json(data_file)
    allowed={"delivered","attempted","understood","applied"}
    if record.get("kind") not in allowed or not record.get("lp_id") or not record.get("evidence_id"):
        raise GateError("evidence requires kind, lp_id and evidence_id")
    if record["kind"] in ("understood","applied") and (not record.get("learner_response") or not record.get("rubric") or not record.get("assessment")):
        raise GateError("mastery must include learner response, rubric, and assessment; clicks do not count")
    if record['kind'] in ('understood','applied') and (Path(ws)/'v61-binding.json').exists():
        if not all(record.get(k) for k in ('question_id','answer_source','learner_response','rubric','assessment')):
            raise GateError('V6.1 requires actual question, answer source and rubric before storing mastery')
    st=state(ws)
    lp=st.setdefault("learner_evidence",{}).setdefault(record["lp_id"],{"delivered":[],"attempted":[],"understood":[],"applied":[]})
    if not any(x.get("evidence_id")==record["evidence_id"] for x in lp[record["kind"]]):
        lp[record["kind"]].append(record)
    save(ws,st)
    # Mirror only real answers with an attributable question/rubric to the preserved
    # V3.5 course evidence format. Legacy clicks/delivered states never yield mastery.
    if record['kind'] in ('attempted','understood','applied') and (Path(ws)/'v61-binding.json').exists():
        from v61_learner import record_assessment
        if not all(record.get(k) for k in ('learner_response','rubric','assessment','question_id','answer_source')):
            if record['kind'] in ('understood','applied'):
                raise GateError('V6.1 requires question_id and answer_source for mastery evidence')
        else:
            record_assessment(ws,record['lp_id'],record['learner_response'],record['rubric'],
                              record['kind'] if record['kind'] in ('understood','applied') else record['assessment'],
                              record['question_id'],record['answer_source'],
                              record.get('assistance','independent'),bool(record.get('reviewed')),
                              record.get('source_ref'))
    return {"recorded":True,"lp_id":record["lp_id"],"kind":record["kind"]}

def make_overview(ws):
    plan=read_json(Path(ws)/"plan.json")
    audit=validate_plan(ws)
    if audit["issues"]:raise GateError("G2 overview blocked by invalid plan: "+str(audit["issues"][:10]))
    rows=['<h1>学习总览 · Unit 规划</h1><p>已对来源片段进行全量知识点映射；本轮只交大纲。下一步由 /study-n 进入 Unit 1。</p>',
          f'<div class="card"><strong>{len(plan["points"])} 个 Learning Points · {len(plan["pages"])} 个 Unit</strong><p>规划状态：待学习者查看</p></div>']
    for p in plan["pages"]:
        goals=[x["goal"] for x in plan["points"] if x["lp_id"] in p["lp_ids"]]
        rows.append(f'<section class="card"><h2>{esc(p["page_id"])} · {esc(p["title"])}</h2><p>{esc("；".join(goals))}</p><small>{esc(", ".join(p["lp_ids"]))}</small></section>')
    h='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Study V5 总览</title><style>'+CSS+'</style></head><body><main>'+"".join(rows)+'</main></body></html>'
    path=Path(ws)/"overview.html";write_text(path,h)
    return {"overview_file":str(path),"units":len(plan["pages"]),"learning_points":len(plan["points"]),"does_not_start_unit1":True}

def main():
    parser=argparse.ArgumentParser(description="Study Host deterministic checks (Codex/DSH supplies model reasoning)")
    parser.add_argument("command",choices=["ingest","inspect-plan","freeze","render","check-content","browser",
      "verify","publish","status","deliver-next","confirm-delivery","consolidate","record-evidence",
      "approve-outline","overview","demo"])
    parser.add_argument("--workspace",required=True)
    parser.add_argument("--source")
    parser.add_argument("--topic",default="")
    parser.add_argument("--file")
    parser.add_argument("--evidence-file")
    args=parser.parse_args();w=Path(args.workspace).resolve()
    try:
        actions={
          "ingest":lambda:ingest(w,args.source),
          "inspect-plan":lambda:validate_plan(w),
          "freeze":lambda:freeze(w),
          "render":lambda:build_pages(w),
          "check-content":lambda:content_static_check(w),
          "browser":lambda:browser_qa(w),
          "verify":lambda:verify(w),
          "publish":lambda:str(publish(w)),
          "status":lambda:state(w),
          "deliver-next":lambda:next_delivery(w),
          "confirm-delivery":lambda:confirm_delivery(w,args.file),
          "consolidate":lambda:consolidate(w,args.topic),
          "record-evidence":lambda:record_evidence(w,args.evidence_file),
          "approve-outline":lambda:approve_outline(w),
          "overview":lambda:make_overview(w),
          "demo":lambda:demo(w)
        }
        result=actions[args.command]()
        print(json.dumps({"ok":True,"result":result},ensure_ascii=False,indent=2))
    except (GateError,KeyError,ValueError,OSError,TypeError) as exc:
        print(json.dumps({"ok":False,"error":str(exc),"workspace":str(w)},ensure_ascii=False),file=sys.stderr)
        sys.exit(2)
if __name__=="__main__":main()
