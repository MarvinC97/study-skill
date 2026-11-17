#!/usr/bin/env python3
"""Host-native Study V6.2: Codex/DSH performs reasoning; this script enforces local gates.

All model-authored plans, explanations and reviews arrive as files from the
connected host's existing agent/subagents. This CLI makes NO model API calls.
"""
from __future__ import annotations
import argparse
import shutil
import json
from datetime import datetime,timezone
from pathlib import Path
import study_runtime as host
import v61_learner as learners
import quality_contract as qc
import lesson_contract as lessons
import lesson_render as renderer

def load(p):
    return host.read_json(p)

def obj(path):
    p=Path(path)
    return host.read_json(p) if p.is_file() else None

def stamp():
    return datetime.now(timezone.utc).isoformat()

def digest(data):
    return host.sha(json.dumps(data,sort_keys=True,ensure_ascii=False))

def need(ws,name):
    p=Path(ws)/name
    if not p.is_file():raise host.GateError("required artifact missing: "+str(p))
    return load(p)

def root_bound(ws):
    p=Path(ws)/"v61-binding.json"
    return load(p) if p.is_file() else None

def bind(ws,name="",root=None,course_id=None,scope="",source="",temporary=False,parent=None,topic=""):
    ws=Path(ws).resolve();ws.mkdir(parents=True,exist_ok=True)
    if parent:
        parent=Path(parent).resolve()
        pb=learners.binding(parent)
        if not ws.is_relative_to(parent) or ws==parent:
            raise host.GateError("deep workspace must reside strictly below the parent course")
        p=ws/"v61-binding.json"
        if not p.exists():
            link=dict(pb,workspace=str(ws),parent_workspace=str(parent),deep_branch=True)
            learners.atomic(p,link,exclusive=True)
        return learners.deep_branch(parent,ws,topic,
            return_unit=learners.course(parent).get("navigation",{}).get("current_unit_index",0))
    if root_bound(ws):return learners.binding(ws)
    return learners.bind_workspace(ws,name,root,course_id=course_id,
        scope=scope,source=source,temporary=temporary)

def plan_check(ws):
    src=need(ws,"source.json");plan=need(ws,"plan.json")
    rep=host.validate_plan(ws)
    if rep["issues"]:raise host.GateError("G2 plan structure rejected: "+str(rep["issues"][:12]))
    if root_bound(ws) and not root_bound(ws).get("parent_workspace"):
        learners.sync_plan(ws)
    rep["plan_sha256"]=digest(plan)
    rep["source_sha256"]=src["source_sha256"]
    return rep

def accept_plan_review(ws,review_file):
    plan_check(ws)
    src=need(ws,"source.json");plan=need(ws,"plan.json")
    rev=load(review_file)
    if rev.get("review_mode")!="isolated_host_agent" or not rev.get("reviewer_context_id"):
        raise host.GateError("independent review must come from an isolated host agent context")
    if rev.get("writer_context_id")==rev.get("reviewer_context_id"):
        raise host.GateError("reviewer reused the writer context")
    required={s["id"] for s in src["segments"]}
    if set(rev.get("checked_span_ids",[]))!=required:
        raise host.GateError("independent reviewer did not account for every source span")
    if rev.get("plan_sha256")!=digest(plan) or rev.get("source_sha256")!=src["source_sha256"]:
        raise host.GateError("review does not match frozen source/plan hashes")
    if rev.get("approved") is not True or rev.get("issues"):
        raise host.GateError("independent reviewer rejected plan: "+str(rev.get("issues",[])))
    scope=dict(src,text=(Path(ws)/"source.txt").read_text(encoding="utf-8"))
    cachepath=Path(ws)/"reviews"/"plan-review-cache.json"
    cache=obj(cachepath) or {"batches":{},"pages":{}}
    audit_issues=qc.validate_plan_review_audits(rev,scope,plan,cache)
    audit_issues+=qc.validate_study_group_review(rev,plan)
    if audit_issues:
        raise host.GateError("G2 independent plan and Unit-coherence review failed: "+str(audit_issues[:12]))
    # Cache only VERIFIED reviewer batches; no model calls or repeat review
    # for unchanged source/LP and grouped-page scopes.
    if rev.get("review_contract")=="g2-batched-v3":
        for item in rev.get("batch_audits",[]):
            cache["batches"][item["scope_sha256"]]=item
        for item in rev.get("page_audits",[]):
            cache["pages"][item["scope_sha256"]]=item
        host.atomic_json(cachepath,cache)
    stored={"approved":True,"issues":[],"reviewer_role":"isolated_host_agent",
      "reviewer_context_id":rev["reviewer_context_id"],"plan_sha256":digest(plan),
      "source_sha256":src["source_sha256"],"checked_span_ids":sorted(required),
      "quality_contract":rev.get("review_contract","deep-semantic-v2"),
      "unit_group_audits":rev.get("unit_group_audits",[]),
      "quality_audits_validated":True,
      "reused_batches":len(rev.get("reuse_batch_sha256",[])),
      "reviewed_batches":len(rev.get("batch_audits",[])),
      "reviewed_grouped_pages":len(rev.get("page_audits",[])),
      "atomicity_audits":rev.get("atomicity_audits",[]),
      "span_audits":rev.get("span_audits",[]),
      "checked_inventory_ids":rev.get("checked_inventory_ids",[]),
      "experiment_audits":rev.get("experiment_audits",[]),
      "reflection_audits":rev.get("reflection_audits",[])}
    host.atomic_json(Path(ws)/"reviews"/"plan-review.json",stored)
    return {"reviewed":True,"plan_sha256":stored["plan_sha256"],
            "spans_checked":len(required),"reused_batches":stored["reused_batches"],
            "reviewed_batches":stored["reviewed_batches"],
            "reviewed_grouped_pages":stored["reviewed_grouped_pages"]}

def design_check(ws,page_id):
    """Explicit stop/go checkpoint BEFORE authoring the full lesson draft."""
    w=Path(ws)
    plan=need(w,"frozen-plan.json") if (w/"frozen-plan.json").is_file() else need(w,"plan.json")
    source=need(w,"source.json")
    page=next((p for p in plan["pages"] if p["page_id"]==page_id),None)
    if page is None:raise host.GateError("unknown lesson page "+str(page_id))
    byid={p["lp_id"]:p for p in plan["points"]}
    try:
        spec,design_hash=lessons.verify_ready(w,plan,page,source,
                             [byid[i] for i in page["lp_ids"]])
    except (lessons.LessonContractError,ValueError,TypeError,KeyError) as exc:
        raise host.GateError("G3 design approval required before writing: "+str(exc))
    return {"page_id":page_id,"lesson_kind":spec["lesson_kind"],
            "design_reviewed":True,"lesson_spec_sha256":design_hash,
            "checkpoint_question":spec["checkpoint"]["question"]}


def design_ready(ws,plan,page,src,related,draft):
    """Hard gate: every NEW teaching page needs a real reviewed design."""
    try:
        spec,design_hash=lessons.verify_ready(ws,plan,page,src,related)
        problems=lessons.validate_draft_alignment(spec,draft)
        if problems:raise lessons.LessonContractError("; ".join(problems))
        return spec,design_hash
    except (lessons.LessonContractError,ValueError,KeyError,TypeError) as exc:
        raise host.GateError("G3 lesson design is not accepted: "+str(exc))


def accept_content_review(ws,review_file):
    plan=need(ws,"frozen-plan.json");src=need(ws,"source.json")
    rev=load(review_file)
    if rev.get("review_mode")!="isolated_host_agent" or not rev.get("reviewer_context_id"):
        raise host.GateError("isolated host reviewer receipt required")
    if rev.get("writer_context_id")==rev.get("reviewer_context_id"):
        raise host.GateError("reviewer reused the writer context")
    if rev.get("source_sha256")!=src["source_sha256"] or rev.get("plan_sha256")!=digest(plan):
        raise host.GateError("review source/plan hash mismatch")
    expected={p["page_id"]:p for p in plan["pages"]}
    points={p["lp_id"]:p for p in plan["points"]}
    cachepath=Path(ws)/"reviews"/"content-review-cache.json"
    cache=obj(cachepath) or {"pages":{}}
    compact=rev.get("review_contract")=="g4-compact-v3"
    incoming=list(rev.get("pages",[]))
    if compact:
        reusable=rev.get("reuse_page_sha256",[])
        if not isinstance(reusable,list):raise host.GateError("invalid cached page list")
        for token in reusable:
            old=cache.get("pages",{}).get(token)
            if not isinstance(old,dict):
                raise host.GateError("G4 missing previously accepted page review: "+str(token))
            incoming.append(old)
    all_ids=set();page_receipts=[];got=set();new_cache=[]
    for entry in incoming:
        if not isinstance(entry,dict):raise host.GateError("malformed content review entry")
        pid=entry.get("page_id")
        if pid not in expected or pid in got:
            raise host.GateError("unknown or repeated reviewed page: "+str(pid))
        got.add(pid);page=expected[pid]
        draft=need(ws,"drafts/"+pid+".json")
        relevant=[points[x] for x in page["lp_ids"]]
        errors=host.validate_content_data(relevant,draft,mode=plan.get("mode","study-d"))
        if errors:raise host.GateError("invalid reviewed draft "+pid+": "+str(errors))
        spec,design_hash=design_ready(ws,plan,page,src,relevant,draft)
        if entry.get("lesson_spec_sha256")!=design_hash:
            raise host.GateError("G4 content review is not bound to the approved lesson design "+pid)
        required={f["id"] for p in relevant for f in p["required_facts"]}
        if set(entry.get("checked_fact_ids",[]))!=required:
            raise host.GateError("reviewer did not check every required fact for "+pid)
        dsha=digest(draft)
        if entry.get("draft_sha256")!=dsha:
            raise host.GateError("review is stale for "+pid)
        if entry.get("approved") is not True or entry.get("issues"):
            raise host.GateError("reviewer rejected content of "+pid)
        review_scope=qc.content_page_scope(src,plan,page,draft)
        if compact and (entry.get("review_contract")!="g4-compact-v3"
                        or entry.get("review_scope_sha256")!=review_scope):
            raise host.GateError("G4 page review scope mismatch "+pid)
        quality=qc.validate_content_review_audits(entry,relevant,draft,src)
        if quality:
            raise host.GateError("G4 shallow/ungrounded lesson rejected "+pid+": "+str(quality[:14]))
        receipt={"page_id":pid,"approved":True,"issues":[],
          "lesson_spec_sha256":design_hash,
          "checked_fact_ids":sorted(required),"draft_sha256":dsha,
          "quality_dimensions":entry["quality_dimensions"],
          "quality_contract":"compact-semantic-v3" if compact else "deep-semantic-v2",
          "quality_audits_validated":True}
        if compact:
            receipt.update({"review_contract":"g4-compact-v3",
                 "review_scope_sha256":review_scope,
                 "fact_checks":entry["fact_checks"],"risk_audits":entry.get("risk_audits",[])})
            new_cache.append(receipt)
        else:
            receipt["fact_audits"]=entry["fact_audits"]
        page_receipts.append(receipt)
        all_ids.update(required)
    if got!=set(expected):
        raise host.GateError("content review lacks pages: "+str(set(expected)-got))
    result={"approved":True,"pages":page_receipts,"source_sha256":src["source_sha256"],
      "plan_sha256":digest(plan),"reviewer_context_id":rev["reviewer_context_id"],
      "quality_contract":"compact-semantic-v3" if compact else "deep-semantic-v2",
      "quality_audits_validated":True,
      "reused_pages":len(rev.get("reuse_page_sha256",[])) if compact else 0}
    host.atomic_json(Path(ws)/"reviews"/"content-review.json",result)
    if compact:
        for item in new_cache:
            cache["pages"][item["review_scope_sha256"]]=item
        host.atomic_json(cachepath,cache)
    return {"reviewed":True,"pages":len(page_receipts),
            "checked_fact_ids":len(all_ids),"reused_pages":result["reused_pages"]}

def stage_next_page(ws,review_file):
    """Review, browser-test and prepare ONE page from an approved frozen plan.
    Previously delivered pages and receipts remain unchanged.
    """
    w=Path(ws);plan=need(w,"frozen-plan.json");src=need(w,"source.json")
    if plan.get("mode")!="study-d":
        raise host.GateError("stage-next-page applies to an approved Study-D plan")
    original=need(w,"plan.json")
    if digest(original)!=digest(plan):
        raise host.GateError("frozen Study-D plan has changed")
    approved=need(w,"reviews/plan-review.json")
    owner=need(w,"owner-outline-approval.json")
    if approved.get("plan_sha256")!=digest(plan) or approved.get("approved") is not True:
        raise host.GateError("G2 independent outline review missing")
    if owner.get("approved") is not True or owner.get("plan_sha256")!=digest(plan):
        raise host.GateError("Study-D owner approval missing")
    ledgerpath=w/"reports"/"page-receipts.json"
    ledger=obj(ledgerpath) or {"plan_sha256":digest(plan),
       "source_sha256":src["source_sha256"],"pages":[]}
    if ledger.get("plan_sha256")!=digest(plan) or ledger.get("source_sha256")!=src["source_sha256"]:
        raise host.GateError("incremental stage source/plan changed; reconcile existing pages first")
    if len(ledger["pages"])>=len(plan["pages"]):
        return {"finished_authoring":True,"pages":len(ledger["pages"])}
    next_page=plan["pages"][len(ledger["pages"])]
    pid=next_page["page_id"]
    queuepath=w/"delivery-queue.json"
    queue=obj(queuepath)
    if queue and queue.get("cursor",0)<len(queue.get("files",[])):
        raise host.GateError("finish presenting the previous prepared page before authoring the next")
    draft=need(w,"drafts/"+pid+".json")
    lookup={p["lp_id"]:p for p in plan["points"]}
    related=[lookup[lp] for lp in next_page["lp_ids"]]
    spec,design_hash=design_ready(w,plan,next_page,src,related,draft)
    errors=host.validate_content_data(related,draft,mode="study-d")
    if errors:raise host.GateError("G3 draft rejected "+pid+": "+str(errors[:12]))
    rev=load(review_file)
    if rev.get("review_mode")!="isolated_host_agent" or not rev.get("reviewer_context_id"):
        raise host.GateError("G4 independent host-agent reviewer required")
    if rev.get("writer_context_id")==rev.get("reviewer_context_id"):
        raise host.GateError("G4 reviewer cannot equal writer context")
    if rev.get("source_sha256")!=src["source_sha256"] or rev.get("plan_sha256")!=digest(plan):
        raise host.GateError("G4 page review source or outline is stale")
    entries=rev.get("pages",[])
    if len(entries)!=1 or entries[0].get("page_id")!=pid:
        raise host.GateError("G4 require exactly the next page review "+pid)
    entry=entries[0]
    required={f["id"] for p in related for f in p["required_facts"]}
    if (set(entry.get("checked_fact_ids",[]))!=required or
        entry.get("draft_sha256")!=digest(draft) or
        entry.get("lesson_spec_sha256")!=design_hash or
        entry.get("approved") is not True or entry.get("issues")):
        raise host.GateError("G4 fact coverage, approval or draft hash mismatch")
    if entry.get("review_contract")=="g4-compact-v3" and (
       entry.get("review_scope_sha256")!=qc.content_page_scope(src,plan,next_page,draft)):
        raise host.GateError("G4 scoped page audit stale")
    issues=qc.validate_content_review_audits(entry,related,draft,src)
    if issues:raise host.GateError("G4 semantic review failed: "+str(issues[:12]))
    # Generated navigation links only to the index until neighbors are ready.
    dest=w/"draft-pages"/(pid+".html")
    html=renderer.render(next_page,related,draft,src,spec,"index.html","index.html")
    host.write_text(dest,html)
    staged=ledger["pages"]+[{"page_id":pid,"file":pid+".html",
        "lp_ids":next_page["lp_ids"],"draft_sha256":digest(draft),
        "rendered_sha256":host.sha(html),
        "lesson_spec_sha256":design_hash,
        "review_scope_sha256":qc.content_page_scope(src,plan,next_page,draft),
        "reviewer_context_id":rev["reviewer_context_id"],
        "review_contract":entry.get("review_contract","deep-semantic-v2")}]
    index_lines=['<h1>Study-D · 已审定课程路线</h1>']
    for item in plan["pages"]:
        label=host.esc(item["page_id"]+" · "+item["title"])
        if any(v["page_id"]==item["page_id"] for v in staged):
            index_lines.append('<p><a href="'+host.esc(item["page_id"])+'.html">'+label+'</a></p>')
        else:index_lines.append('<p>'+label+' · 待生成</p>')
    index_markup='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+host.CSS+'</style><main>'+''.join(index_lines)+'</main></html>'
    host.write_text(w/"draft-pages"/"index.html",index_markup)
    manifest={"source_sha256":src["source_sha256"],"pages":staged,"index":"index.html"}
    host.atomic_json(w/"content-manifest.json",manifest)
    structural=host.content_static_check(w)
    if structural["issues"]:
        raise host.GateError("G3 page structure rejected: "+str(structural["issues"][:12]))
    browser=host.browser_qa(w)
    if browser.get("passed") is not True or browser.get("browser_executed") is not True:
        raise host.GateError("G5 real browser QA failed: "+str(browser.get("issues",[])))
    out=w/"published";out.mkdir(exist_ok=True)
    shutil.copy2(dest,out/(pid+".html"))
    shutil.copy2(w/"draft-pages"/"index.html",out/"index.html")
    host.atomic_json(ledgerpath,{"plan_sha256":digest(plan),
       "source_sha256":src["source_sha256"],"pages":staged})
    if queue is None:queue={"cursor":0,"files":["index.html"],"one_link_per_turn":True}
    queue["files"].append(pid+".html")
    host.atomic_json(queuepath,queue)
    all_staged=len(staged)==len(plan["pages"])
    if all_staged:
        # All pages have independently checked receipts and real browser QA.
        for gate,evidence in (("G3_CONTENT",w/"reports"/"content-static.json"),
                              ("G4_REVIEW",ledgerpath),
                              ("G5_BROWSER",w/"reports"/"browser.json")):
            host.record_gate(w,gate,True,evidence=evidence)
    else:
        state=host.state(w)
        for gate in ("G3_CONTENT","G4_REVIEW","G5_BROWSER"):
            state.setdefault("gates",{})[gate]={"ok":False,
               "status":"PARTIAL_VERIFIED","issues":[],"evidence":str(ledgerpath)}
            state.setdefault("verification",{})[gate]="PARTIAL_VERIFIED"
        host.save(w,state)
    state=host.state(w)
    state.setdefault("gates",{})["G6_DELIVERY"]={"ok":False,
       "status":"PREPARED","issues":[],"evidence":str(queuepath)}
    state.setdefault("verification",{})["G6_DELIVERY"]="PREPARED"
    host.save(w,state)
    return {"page_id":pid,"file":str((out/(pid+".html")).resolve()),
        "reviewed":True,"browser_pass":True,"pages_staged":len(staged),
        "total_pages":len(plan["pages"]),"awaiting_delivery_confirmation":True,
        "new_browser_tests":browser.get("pages_executed_now"),
        "reused_browser_tests":browser.get("pages_cached")}


def check_review_integrity(ws):
    plan=need(ws,"frozen-plan.json");review=need(ws,"reviews/content-review.json")
    src=need(ws,"source.json");lookup={p["lp_id"]:p for p in plan["points"]}
    bypage={p["page_id"]:p for p in plan["pages"]}
    if review.get("plan_sha256")!=digest(plan):raise host.GateError("content review stale: plan changed")
    if review.get("quality_audits_validated") is not True:
        raise host.GateError("G4 semantic review receipt missing")
    for entry in review.get("pages",[]):
        pid=entry["page_id"];page=bypage.get(pid)
        if page is None:raise host.GateError("unknown reviewed page "+pid)
        draft=need(ws,"drafts/"+pid+".json")
        spec,design_hash=design_ready(ws,plan,page,src,
            [lookup[i] for i in page["lp_ids"]],draft)
        if entry.get("lesson_spec_sha256")!=design_hash:
            raise host.GateError("G4 lesson design changed after review "+pid)
        if digest(draft)!=entry.get("draft_sha256"):
            raise host.GateError("content review stale: draft changed "+pid)
        if entry.get("quality_audits_validated") is not True:
            raise host.GateError("G4 per-page quality review missing for "+pid)

def render(ws):
    plan=need(ws,"frozen-plan.json");src=need(ws,"source.json")
    lookup={p["lp_id"]:p for p in plan["points"]}
    for page in plan["pages"]:
        draft=need(ws,"drafts/"+page["page_id"]+".json")
        design_ready(ws,plan,page,src,[lookup[i] for i in page["lp_ids"]],draft)
    return host.build_pages(ws)

def verify(ws):
    plan=need(ws,"frozen-plan.json")
    check_review_integrity(ws)
    if digest(plan)!=need(ws,"reviews/plan-review.json").get("plan_sha256"):
        raise host.GateError("approved plan changed before verification")
    check_review_integrity(ws)
    host.verify(ws)
    return host.state(ws).get("gates",{})

def publish(ws):
    check_review_integrity(ws)
    out=host.publish(ws)
    binding=root_bound(ws)
    if binding and binding.get("parent_workspace"):
        parent=Path(binding["parent_workspace"])
        p=parent/"v6-related-modules.json"
        data=load(p) if p.is_file() else {"modules":[]}
        data["modules"]=[x for x in data["modules"] if x.get("workspace")!=str(Path(ws).resolve())]
        source=need(ws,"source.json")
        topic=learners.course(parent).get("navigation",{}).get("deep_branch",{}).get("topic","")
        data["modules"].append({"workspace":str(Path(ws).resolve()),
           "topic":topic,"source_sha256":source["source_sha256"]})
        host.atomic_json(p,data)
    return {"published_dir":str(out)}

def freeze(ws):
    plan=need(ws,"plan.json")
    if plan.get("mode")=="study-d":
        approval=need(ws,"owner-outline-approval.json")
        if approval.get("approved") is not True or approval.get("plan_sha256")!=digest(plan):
            raise host.GateError("Study-D outline requires learner's explicit approval of this exact reviewed plan")
    return host.freeze(ws)

def overview(ws):
    plan_check(ws)
    rev=need(ws,"reviews/plan-review.json")
    if not rev.get("approved") or rev.get("plan_sha256")!=digest(need(ws,"plan.json")):
        raise host.GateError("overview requires current independent plan review")
    result=host.make_overview(ws)
    if root_bound(ws) and not root_bound(ws).get("parent_workspace"):
        learners.sync_plan(ws)
    return result

def confirm_delivery(ws,file):
    result=host.confirm_delivery(ws,file)
    binding=root_bound(ws)
    if binding and binding.get("parent_workspace"):
        parent=Path(binding["parent_workspace"])
        d=learners.course(parent)
        branch=d.get("navigation",{}).get("deep_branch")
        if not branch or branch.get("workspace")!=str(Path(ws).resolve()):
            raise host.GateError("parent deep branch link changed")
        if branch.get("next_page",0)>result["index"]:
            raise host.GateError("parent branch cursor exceeds confirmed delivery")
        branch["next_page"]=result["index"]
        queue=need(ws,"delivery-queue.json")
        branch["status"]="completed" if result["index"]>=len(queue["files"]) else "delivering"
        learners.save_course(parent,d)
    return result

def status(ws):
    out={"host":host.state(ws)}
    if (Path(ws)/"source.json").exists():out["source_sha256"]=need(ws,"source.json")["source_sha256"]
    if (Path(ws)/"delivery-queue.json").exists():out["delivery"]=need(ws,"delivery-queue.json")
    if root_bound(ws):
        out["learner"]=learners.recover(Path(root_bound(ws).get("parent_workspace",ws)))
    return out

def main():
    p=argparse.ArgumentParser(description="Study host-native deterministic runtime (no model API)")
    p.add_argument("command",choices=("bind","ingest","plan-check","accept-plan-review",
      "overview","approve-outline","freeze","design-check","draft-check","render","check-content",
      "accept-content-review","stage-next-page","verify","publish","deliver-next","confirm-delivery","hash-json","status"))
    p.add_argument("--workspace",required=True)
    p.add_argument("--source")
    p.add_argument("--topic",default="")
    p.add_argument("--review-file")
    p.add_argument("--file")
    p.add_argument("--page-id")
    p.add_argument("--parent-workspace")
    p.add_argument("--learner-name",default="")
    p.add_argument("--study-root")
    p.add_argument("--course-id")
    p.add_argument("--temporary",action="store_true")
    a=p.parse_args();w=Path(a.workspace).resolve()
    try:
        if a.command=="bind":
            result=bind(w,a.learner_name,a.study_root,a.course_id,a.topic,a.source,
              a.temporary,a.parent_workspace,a.topic)
        elif a.command=="ingest":
            if not a.source:raise host.GateError("ingest requires --source")
            result=host.ingest(w,a.source)
        elif a.command=="plan-check":result=plan_check(w)
        elif a.command=="accept-plan-review":
            if not a.review_file:raise host.GateError("accept-plan-review requires --review-file")
            result=accept_plan_review(w,a.review_file)
        elif a.command=="overview":result=overview(w)
        elif a.command=="approve-outline":result=host.approve_outline(w)
        elif a.command=="freeze":result=freeze(w)
        elif a.command=="design-check":
            if not a.page_id:raise host.GateError("design-check requires --page-id")
            result=design_check(w,a.page_id)
        elif a.command=="draft-check":
            plan=need(w,"frozen-plan.json")
            if not a.page_id:raise host.GateError("draft-check requires --page-id")
            pg=next((x for x in plan["pages"] if x["page_id"]==a.page_id),None)
            if not pg:raise host.GateError("unknown page")
            points={x["lp_id"]:x for x in plan["points"]}
            issues=host.validate_content_data([points[x] for x in pg["lp_ids"]],
                                              need(w,"drafts/"+a.page_id+".json"),
                                              mode=plan.get("mode","study-d"))
            if issues:raise host.GateError(str(issues))
            result={"page_id":a.page_id,"valid":True,"draft_sha256":digest(need(w,"drafts/"+a.page_id+".json"))}
        elif a.command=="render":result=render(w)
        elif a.command=="check-content":result=host.content_static_check(w)
        elif a.command=="accept-content-review":
            if not a.review_file:raise host.GateError("accept-content-review requires --review-file")
            result=accept_content_review(w,a.review_file)
        elif a.command=="stage-next-page":
            if not a.review_file:raise host.GateError("stage-next-page requires --review-file")
            result=stage_next_page(w,a.review_file)
        elif a.command=="verify":result=verify(w)
        elif a.command=="publish":result=publish(w)
        elif a.command=="deliver-next":result=host.next_delivery(w)
        elif a.command=="hash-json":
            if not a.file:raise host.GateError("hash-json requires --file")
            result={"file":str(Path(a.file).resolve()),"sha256":digest(load(a.file))}
        elif a.command=="confirm-delivery":
            if not a.file:raise host.GateError("confirm-delivery requires --file")
            result=confirm_delivery(w,a.file)
        else:result=status(w)
        print(json.dumps({"ok":True,"result":result},ensure_ascii=False,indent=2))
    except (host.GateError,learners.LearnerError,ValueError,OSError,KeyError,TypeError) as e:
        print(json.dumps({"ok":False,"error":str(e)},ensure_ascii=False),file=__import__("sys").stderr)
        raise SystemExit(2)

if __name__=="__main__":main()
