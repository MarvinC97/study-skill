"""Study V6.5 storyboard, teaching-component and post-render evidence contracts.

The connected host Agent supplies design and genuine independent judgments.
This module only validates identities, facts, hashes, component data and
auditable review receipts. Do not equate valid receipts with learner mastery.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

VERSION="lesson-storyboard-v1"
LAYOUTS=frozenset(("overview","exploration","evidence"))
ACTIONS=frozenset(("observe","compare","predict","compute","diagnose"))
MODULES=frozenset(("causal-flow","decision-explorer","variable-lab",
                   "math-stepper","experiment-comparator","trace-debugger",
                   "worked-example","transfer-checkpoint"))
FORMULAS={
    "pass-at-k":frozenset(("p","k")),
    "q-learning":frozenset(("q","alpha","reward","gamma","next_q")),
    "ppo-clip":frozenset(("ratio","advantage","epsilon"))
}
RENDER_DIMENSIONS=frozenset(("visual_fidelity","interaction_semantics",
    "source_fidelity","cognitive_load","layout_integrity","transfer_alignment"))


class StoryboardError(ValueError):
    pass


def fingerprint(data):
    return hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False).encode("utf-8")).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def path_set(workspace,page_id):
    w=Path(workspace)
    return (w/"storyboards"/(page_id+".json"),
            w/"reviews"/"storyboard"/(page_id+".json"),
            w/"reviews"/"render"/(page_id+".json"))


def text_ok(v,n=12):
    return isinstance(v,str) and len(" ".join(v.split()))>=n


def _validate_props(kind,p):
    e=[]
    if not isinstance(p,dict):
        return ["component props must be a JSON object"]
    if kind=="causal-flow":
        nodes=p.get("nodes",[]);edges=p.get("edges",[])
        if not isinstance(nodes,list) or not 2<=len(nodes)<=9:
            e.append("causal flow needs 2–9 source-grounded nodes");nodes=[]
        ids=[x.get("id") for x in nodes if isinstance(x,dict)]
        if len(ids)!=len(nodes) or len(set(ids))!=len(ids):
            e.append("causal flow node IDs invalid")
        for n in nodes:
            if not isinstance(n,dict) or not text_ok(n.get("label"),2) or not text_ok(n.get("meaning"),12):
                e.append("causal node must explain its meaning")
        if not isinstance(edges,list) or len(edges)<len(nodes)-1:
            e.append("causal flow requires meaning-labelled relationships")
        else:
            for edge in edges:
                if not isinstance(edge,dict) or edge.get("from") not in ids or edge.get("to") not in ids or not text_ok(edge.get("label"),4):
                    e.append("causal edge has unknown node or unclear relationship")
    elif kind=="decision-explorer":
        nodes=p.get("nodes",[]);start=p.get("start")
        if not isinstance(nodes,list) or not 3<=len(nodes)<=16:
            e.append("decision tree requires 3–16 nodes");nodes=[]
        valid={x.get("id"):x for x in nodes if isinstance(x,dict)}
        if len(valid)!=len(nodes) or start not in valid:
            e.append("decision start/IDs invalid")
        terminal=0
        for n in nodes:
            if not isinstance(n,dict):continue
            if n.get("options"):
                if not text_ok(n.get("prompt"),12) or not 2<=len(n["options"])<=4:
                    e.append("decision must pose a specific choice")
                for op in n["options"]:
                    if not isinstance(op,dict) or op.get("to") not in valid or not text_ok(op.get("label"),2) or not text_ok(op.get("reason"),14):
                        e.append("decision edge lacks target or rationale")
            else:
                terminal+=1
                if not text_ok(n.get("outcome"),12) or not text_ok(n.get("reason"),15):
                    e.append("decision branch has no grounded final outcome")
        if terminal<2:e.append("decision tree requires at least two distinct outcomes")
        if start in valid:
            reached={start};front=[start]
            while front:
                current=front.pop()
                for op in valid[current].get("options",[]):
                    dest=op.get("to")
                    if dest in valid and dest not in reached:
                        reached.add(dest);front.append(dest)
            if reached!=set(valid):e.append("decision nodes include unreachable branches")
    elif kind=="variable-lab":
        formula=p.get("formula");controls=p.get("controls",[])
        if formula not in FORMULAS:
            e.append("variable lab formula must be a verified named computation")
        if not isinstance(controls,list):controls=[]
        names={c.get("id") for c in controls if isinstance(c,dict)}
        if formula in FORMULAS and names!=FORMULAS[formula]:
            e.append("variable lab controls do not match named formula")
        for c in controls:
            if not isinstance(c,dict):e.append("malformed variable control");continue
            v=[c.get(k) for k in ("min","max","step","default")]
            if not all(type(x) in (int,float) for x in v):
                e.append("variable slider uses numeric bounds");continue
            mn,mx,step,default=v
            if mn>=mx or not mn<=default<=mx or step<=0 or step>mx-mn:
                e.append("variable bounds or step invalid")
            if not text_ok(c.get("label"),2):e.append("variable must explain its meaning")
            if c.get("id") in ("p","alpha","gamma","epsilon") and (mn<0 or mx>1):
                e.append("probability/rate bound must be between 0 and 1")
            if c.get("id")=="k" and (mn<1 or int(step)!=step or int(default)!=default):
                e.append("k must be a positive integer")
        if not text_ok(p.get("question"),15) or not text_ok(p.get("interpretation"),20):
            e.append("variable lab needs predicted effect and feedback interpretation")
    elif kind=="math-stepper":
        steps=p.get("steps",[])
        if not text_ok(p.get("formula"),5) or not isinstance(steps,list) or not 2<=len(steps)<=10:
            e.append("math stepper requires formula and 2–10 derivation steps");steps=[]
        for st in steps:
            if not isinstance(st,dict) or not text_ok(st.get("expression"),4) or not text_ok(st.get("reason"),15):
                e.append("math step has no calculation or rationale")
    elif kind=="experiment-comparator":
        cols=p.get("columns",[]);rows=p.get("rows",[])
        if not isinstance(cols,list) or not 2<=len(cols)<=6 or not isinstance(rows,list) or not 2<=len(rows)<=20:
            e.append("experiment comparison needs columns and at least two conditions")
        else:
            if any(not isinstance(row,list) or len(row)!=len(cols) for row in rows):
                e.append("experimental observations do not align with columns")
        if not text_ok(p.get("provenance"),20) or not text_ok(p.get("interpretation"),25):
            e.append("experiment needs provenance and qualified interpretation")
    elif kind=="trace-debugger":
        steps=p.get("steps",[])
        if not isinstance(steps,list) or not 3<=len(steps)<=16:
            e.append("debug trace needs at least three steps");steps=[]
        wrong=[i for i,x in enumerate(steps) if isinstance(x,dict) and x.get("first_error") is True]
        if len(wrong)!=1:
            e.append("debug trace must identify exactly one first error")
        for st in steps:
            if not isinstance(st,dict) or not text_ok(st.get("action"),8) or not text_ok(st.get("evidence"),12) or not text_ok(st.get("consequence"),12):
                e.append("debug trace step needs action/evidence/consequence")
        if not text_ok(p.get("repair"),20) or not text_ok(p.get("holdout"),15):
            e.append("debug trace needs a focused fix and independent holdout")
    elif kind=="worked-example":
        steps=p.get("steps",[])
        if not text_ok(p.get("scenario"),20) or not text_ok(p.get("input"),12) or not text_ok(p.get("outcome"),18):
            e.append("worked example needs meaningful scenario/input/outcome")
        if not isinstance(steps,list) or len(steps)<2 or any(not text_ok(st,14) for st in steps):
            e.append("worked example needs at least two substantive reasoning steps")
    elif kind=="transfer-checkpoint":
        opts=p.get("options",[])
        if not text_ok(p.get("question"),18) or not text_ok(p.get("changed_condition"),14) or not text_ok(p.get("rubric"),24):
            e.append("transfer checkpoint must probe a changed condition")
        if not isinstance(opts,list) or not 3<=len(opts)<=4:
            e.append("transfer checkpoint needs three or four answer options")
        else:
            if sum(x.get("correct") is True for x in opts if isinstance(x,dict))!=1:
                e.append("transfer checkpoint requires exactly one correct answer")
            for op in opts:
                if not isinstance(op,dict) or not text_ok(op.get("label"),2) or not text_ok(op.get("reason"),14):
                    e.append("transfer option needs label and explanatory feedback")
    return e


def validate_storyboard(storyboard,page,points,spec,source):
    issues=[]
    if not isinstance(storyboard,dict):return ["storyboard must be a JSON object"]
    if storyboard.get("schema_version")!=VERSION:issues.append("storyboard schema version mismatch")
    if storyboard.get("page_id")!=page.get("page_id"):issues.append("storyboard page_id mismatch")
    if storyboard.get("lesson_spec_sha256")!=fingerprint(spec):
        issues.append("storyboard no longer matches approved Lesson Specification")
    if storyboard.get("layout") not in LAYOUTS:issues.append("unknown page layout")
    if storyboard.get("learning_action") not in ACTIONS:issues.append("missing learner cognitive action")
    if not text_ok(storyboard.get("narrative"),25):issues.append("storyboard needs coherent teaching narrative")
    scenes=storyboard.get("scenes",[])
    if not isinstance(scenes,list) or not 2<=len(scenes)<=7:
        issues.append("storyboard must compose 2–7 purposeful scenes");scenes=[]
    ids=[sc.get("id") for sc in scenes if isinstance(sc,dict)]
    if len(ids)!=len(scenes) or len(set(ids))!=len(ids) or any(not x for x in ids):
        issues.append("storyboard scene identifiers invalid")
    all_lp={p["lp_id"] for p in points}
    facts={f["id"] for p in points for f in p["required_facts"]}
    covered=set();checkpoints=[]
    for sc in scenes:
        if not isinstance(sc,dict):issues.append("malformed scene");continue
        name=sc.get("module")
        if name not in MODULES:issues.append("unknown teaching component "+str(name));continue
        if not text_ok(sc.get("purpose"),20):issues.append("scene needs its own teaching purpose")
        if (not isinstance(sc.get("lp_ids"),list) or not set(sc["lp_ids"]).issubset(all_lp)
             or not sc["lp_ids"]):issues.append("scene LP reference invalid")
        if (not isinstance(sc.get("fact_ids"),list) or not set(sc["fact_ids"]).issubset(facts)
             or not sc["fact_ids"]):issues.append("scene source-fact reference invalid")
        else:covered.update(sc["fact_ids"])
        issues.extend(sc["id"]+": "+err for err in _validate_props(name,sc.get("props")))
        if name=="transfer-checkpoint":
            checkpoints.append(sc["id"])
            if sc.get("props",{}).get("question")!=spec.get("checkpoint",{}).get("question"):
                issues.append("transfer question must equal approved design Checkpoint")
    if len(checkpoints)!=1:issues.append("exactly one transfer Checkpoint scene required")
    if checkpoints and scenes and scenes[-1].get("module")!="transfer-checkpoint":
        issues.append("final scene must check transfer after teaching")
    if covered!=facts:issues.append("storyboard omits or invents source-fact coverage")
    if storyboard.get("layout")=="evidence" and not any(sc.get("module") in
           ("experiment-comparator","trace-debugger") for sc in scenes):
        issues.append("evidence layout needs an experiment or failure-evidence scene")
    if spec.get("lesson_kind")=="experiment" and not any(sc.get("module")=="experiment-comparator" for sc in scenes):
        issues.append("experimental lesson requires an experiment comparator")
    if spec.get("lesson_kind")=="failure_case" and not any(sc.get("module")=="trace-debugger" for sc in scenes):
        issues.append("failure-case lesson requires a trace debugger")
    return sorted(set(issues))


def validate_storyboard_review(review,storyboard,page,points,spec,source,plan_hash):
    issues=[]
    if not isinstance(review,dict):return ["missing independent storyboard review"]
    if review.get("review_mode")!="isolated_host_agent" or not review.get("reviewer_context_id"):
        issues.append("storyboard reviewer must be an isolated host agent")
    if not review.get("writer_context_id") or review.get("writer_context_id")==review.get("reviewer_context_id"):
        issues.append("storyboard author and reviewer contexts must differ")
    for key,expected in (("contract",VERSION),("page_id",page["page_id"]),
                         ("source_sha256",source["source_sha256"]),
                         ("plan_sha256",plan_hash),
                         ("lesson_spec_sha256",fingerprint(spec)),
                         ("storyboard_sha256",fingerprint(storyboard))):
        if review.get(key)!=expected:issues.append("storyboard review "+key+" mismatch")
    if review.get("approved") is not True or review.get("issues"):
        issues.append("storyboard reviewer rejected")
    scene_ids={x["id"] for x in storyboard["scenes"]}
    audits=review.get("scene_audits",[])
    if not isinstance(audits,list) or len(audits)!=len(scene_ids) or {
      x.get("scene_id") for x in audits if isinstance(x,dict)}!=scene_ids:
        issues.append("storyboard reviewer omitted module scene audits")
    else:
        for a in audits:
            if a.get("passed") is not True or not text_ok(a.get("reason"),40):
                issues.append("storyboard scene learning action not justified "+str(a.get("scene_id")))
    return sorted(set(issues))


def storyboard_ready(ws,plan,page,points,spec,source):
    paths=path_set(ws,page["page_id"])
    if not paths[0].is_file():raise StoryboardError("missing storyboard: "+str(paths[0]))
    storyboard=read(paths[0])
    errors=validate_storyboard(storyboard,page,points,spec,source)
    if errors:raise StoryboardError("; ".join(errors[:12]))
    if not paths[1].is_file():raise StoryboardError("missing isolated storyboard review")
    rev=read(paths[1])
    errs=validate_storyboard_review(rev,storyboard,page,points,spec,source,fingerprint(plan))
    if errs:raise StoryboardError("; ".join(errs[:12]))
    return storyboard,fingerprint(storyboard)


def validate_render_review(review,ws,plan,page,source,spec,storyboard,htmlpath,qa):
    errs=[]
    if not isinstance(review,dict):return ["render review missing"]
    if review.get("review_mode")!="isolated_host_agent":
        errs.append("actual rendered page requires isolated reviewer")
    if not review.get("writer_context_id") or not review.get("reviewer_context_id") or review["writer_context_id"]==review["reviewer_context_id"]:
        errs.append("render reviewer identity invalid")
    for key,value in (("contract","render-review-v1"),("page_id",page["page_id"]),
          ("plan_sha256",fingerprint(plan)),("source_sha256",source["source_sha256"]),
          ("lesson_spec_sha256",fingerprint(spec)),
          ("storyboard_sha256",fingerprint(storyboard)),
          ("html_sha256",file_hash(htmlpath)),
          ("browser_manifest_sha256",qa.get("manifest_sha256"))):
        if review.get(key)!=value:errs.append("render reviewer stale "+key)
    if qa.get("passed") is not True or qa.get("browser_executed") is not True:
        errs.append("real browser QA is required before rendered-page review")
    screenshots=qa.get("screenshots",{})
    shot=screenshots.get(page["page_id"],{})
    if not shot:errs.append("missing actual browser screenshot evidence")
    else:
        for kind in ("desktop","mobile"):
            entry=shot.get(kind,{})
            path=Path(entry.get("file",""))
            if not path.is_file() or file_hash(path)!=entry.get("sha256"):
                errs.append("missing/modified "+kind+" browser screenshot")
            if review.get("screenshot_sha256",{}).get(kind)!=entry.get("sha256"):
                errs.append("render reviewer did not attest the actual "+kind+" screenshot hash")
    if review.get("approved") is not True or review.get("issues"):
        errs.append("render review rejected")
    checks=review.get("checks",[])
    if not isinstance(checks,list) or len(checks)!=len(RENDER_DIMENSIONS) or {
        x.get("dimension") for x in checks if isinstance(x,dict)}!=RENDER_DIMENSIONS:
        errs.append("render reviewer omitted visual/interaction dimensions")
    else:
        for x in checks:
            if x.get("passed") is not True or not text_ok(x.get("reason"),45):
                errs.append("render review dimension unsupported "+str(x.get("dimension")))
    if {x.get("scene_id") for x in review.get("scene_audits",[]) if isinstance(x,dict)}!={
        sc["id"] for sc in storyboard["scenes"]}:
        errs.append("render reviewer omitted storyboard scenes")
    else:
        for x in review.get("scene_audits",[]):
            if x.get("rendered") is not True or not text_ok(x.get("reason"),25):
                errs.append("render scene not verified "+str(x.get("scene_id")))
    return sorted(set(errs))
