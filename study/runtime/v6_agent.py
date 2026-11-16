#!/usr/bin/env python3
"""Host-native Study V6.2: Codex/DSH performs reasoning; this script enforces local gates.

All model-authored plans, explanations and reviews arrive as files from the
connected host's existing agent/subagents. This CLI makes NO model API calls.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import study_runtime as host
import v61_learner as learners

def load(p):
    return host.read_json(p)

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
    stored={"approved":True,"issues":[],"reviewer_role":"isolated_host_agent",
      "reviewer_context_id":rev["reviewer_context_id"],"plan_sha256":digest(plan),
      "source_sha256":src["source_sha256"],"checked_span_ids":sorted(required)}
    host.atomic_json(Path(ws)/"reviews"/"plan-review.json",stored)
    return {"reviewed":True,"plan_sha256":stored["plan_sha256"],"spans_checked":len(required)}

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
    all_ids=set();page_receipts=[];got=set()
    for entry in rev.get("pages",[]):
        pid=entry.get("page_id")
        if pid not in expected or pid in got:raise host.GateError("unknown or repeated reviewed page: "+str(pid))
        got.add(pid)
        page=expected[pid];draftfile=Path(ws)/"drafts"/(pid+".json")
        draft=need(ws,"drafts/"+pid+".json")
        relevant=[points[x] for x in page["lp_ids"]]
        errors=host.validate_content_data(relevant,draft)
        if errors:raise host.GateError("invalid reviewed draft "+pid+": "+str(errors))
        required={f["id"] for p in relevant for f in p["required_facts"]}
        if set(entry.get("checked_fact_ids",[]))!=required:
            raise host.GateError("reviewer did not check every required fact for "+pid)
        dsha=digest(draft)
        if entry.get("draft_sha256")!=dsha:
            raise host.GateError("review is stale for "+pid)
        if entry.get("approved") is not True or entry.get("issues"):
            raise host.GateError("reviewer rejected content of "+pid)
        page_receipts.append({"page_id":pid,"approved":True,"issues":[],
          "checked_fact_ids":sorted(required),"draft_sha256":dsha})
        all_ids.update(required)
    if got!=set(expected):raise host.GateError("content review lacks pages: "+str(set(expected)-got))
    result={"approved":True,"pages":page_receipts,"source_sha256":src["source_sha256"],
      "plan_sha256":digest(plan),"reviewer_context_id":rev["reviewer_context_id"]}
    host.atomic_json(Path(ws)/"reviews"/"content-review.json",result)
    return {"reviewed":True,"pages":len(page_receipts),"checked_fact_ids":len(all_ids)}

def check_review_integrity(ws):
    plan=need(ws,"frozen-plan.json");review=need(ws,"reviews/content-review.json")
    if review.get("plan_sha256")!=digest(plan):raise host.GateError("content review stale: plan changed")
    for entry in review.get("pages",[]):
        draft=need(ws,"drafts/"+entry["page_id"]+".json")
        if digest(draft)!=entry.get("draft_sha256"):
            raise host.GateError("content review stale: draft changed "+entry["page_id"])

def render(ws):
    plan=need(ws,"frozen-plan.json")
    for page in plan["pages"]:need(ws,"drafts/"+page["page_id"]+".json")
    return host.build_pages(ws)

def verify(ws):
    plan=need(ws,"frozen-plan.json")
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
      "overview","approve-outline","freeze","draft-check","render","check-content",
      "accept-content-review","verify","publish","deliver-next","confirm-delivery","status"))
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
        elif a.command=="freeze":result=host.freeze(w)
        elif a.command=="draft-check":
            plan=need(w,"frozen-plan.json")
            if not a.page_id:raise host.GateError("draft-check requires --page-id")
            pg=next((x for x in plan["pages"] if x["page_id"]==a.page_id),None)
            if not pg:raise host.GateError("unknown page")
            points={x["lp_id"]:x for x in plan["points"]}
            issues=host.validate_content_data([points[x] for x in pg["lp_ids"]],
                                              need(w,"drafts/"+a.page_id+".json"))
            if issues:raise host.GateError(str(issues))
            result={"page_id":a.page_id,"valid":True}
        elif a.command=="render":result=render(w)
        elif a.command=="check-content":result=host.content_static_check(w)
        elif a.command=="accept-content-review":
            if not a.review_file:raise host.GateError("accept-content-review requires --review-file")
            result=accept_content_review(w,a.review_file)
        elif a.command=="verify":result=verify(w)
        elif a.command=="publish":result=publish(w)
        elif a.command=="deliver-next":result=host.next_delivery(w)
        elif a.command=="confirm-delivery":
            if not a.file:raise host.GateError("confirm-delivery requires --file")
            result=confirm_delivery(w,a.file)
        else:result=status(w)
        print(json.dumps({"ok":True,"result":result},ensure_ascii=False,indent=2))
    except (host.GateError,learners.LearnerError,ValueError,OSError,KeyError,TypeError) as e:
        print(json.dumps({"ok":False,"error":str(e)},ensure_ascii=False),file=__import__("sys").stderr)
        raise SystemExit(2)

if __name__=="__main__":main()
