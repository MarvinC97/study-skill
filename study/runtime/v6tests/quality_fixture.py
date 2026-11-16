"""Explicit test-only data for strict Study quality receipts. Never use as real review."""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).parents[1]))
import quality_contract as qc
import study_runtime as host
import v6_agent as agent

GENERIC_REASON="The reviewer checked the actual source span against the focused objective, observed an independently testable mechanism, and found no additional teachable decision embedded in this LP."
CONTENT_REASON="The authored explanation connects the source condition to a concrete causal result, provides a worked example, covers a meaningful limitation and supports the checkpoint without relying on appended source quotations."

def add_inventory(plan,source):
    plan["source_inventory"]=[]
    for i,point in enumerate(plan["points"],1):
        iid=f"ITEM{i:04d}"
        sid=point["source_span_ids"][0]
        segment=next(x for x in source["segments"] if x["id"]==sid)
        for fact in point.get("required_facts",[]):
            source_fact_span=next(x for x in source["segments"] if x["id"]==fact["span_id"])
            fact["source_quote"]=source_fact_span["text"][:90]
        point["kind"]="mechanism"
        point["inventory_ids"]=[iid]
        plan["source_inventory"].append({
          "id":iid,"kind":"mechanism","span_id":sid,
          "title":"Source-grounded process "+str(i),
          "objective":"Explain this source process and its decision boundary",
          "source_quote":segment["text"][:100]})
    plan["experiment_coverage"]=[]
    plan["reflection_coverage"]=[]
    return plan

def plan_review(plan,source):
    return {"review_mode":"isolated_host_agent","reviewer_context_id":"fixture-plan-reviewer",
      "writer_context_id":"fixture-author","approved":True,"issues":[],
      "source_sha256":source["source_sha256"],"plan_sha256":agent.digest(plan),
      "checked_span_ids":[s["id"] for s in source["segments"]],
      "checked_inventory_ids":[x["id"] for x in plan.get("source_inventory",[])],
      "atomicity_audits":[{"lp_id":p["lp_id"],"atomic":True,"needs_split":False,
          "reason":GENERIC_REASON} for p in plan["points"]],
      "span_audits":[{"span_id":s["id"],"complete":True,"missing_inventory_ids":[],
          "reason":GENERIC_REASON} for s in source["segments"]],
      "experiment_audits":[],"reflection_audits":[]}

def teaching(point):
    fact=point["required_facts"][0]["id"]
    return {"lp_id":point["lp_id"],
      "core_explanation":"A source-grounded system begins with stable input evidence. The learner identifies the relevant condition, follows each processing decision, and predicts what the result becomes after a controlled change. This explanation uses the actual source to show the causal relation between an initial observation and the later outcome.",
      "causal_steps":[
        "First preserve the original input and trace its source anchors so a reviewer can reproduce the facts that motivated this decision.",
        "Next apply the described operation, compare its predicted output with an observed result, and revisit the condition when they disagree."],
      "worked_example":{
        "scenario":"A learner updates one line in the original document and needs to decide which teaching statement should be reviewed again.",
        "input":"The old source text, its stored SHA256, the new text, and one stable source-span reference.",
        "reasoning_steps":[
          "Compare the two source revisions and identify which concrete source span contains the changed condition.",
          "Trace the change to the affected learning objective and independently verify the consequence before changing the lesson."],
        "outcome":"The affected learning point is rechecked against the new source, while unrelated points keep their previous provenance.",
        "why":"The original document and the generated explanation serve different roles; preserving the chain of reasoning makes a change review auditable and prevents unrelated edits from being treated as evidence."},
      "conditions":["The underlying source is readable, the relevant anchors are stable, and the described operation has an observable expected outcome."],
      "limitations":["A source hash detects a changed document but does not prove that its technical meaning changed; a separate semantic comparison is still required."],
      "fact_explanations":[{"fact_id":fact,
        "explanation":"This particular source fact explains why the operation belongs in the learning sequence. The authored reasoning connects its input and condition to the expected output and then checks what would happen when that condition changes. The raw source quotation alone cannot teach that causal chain."}]}

def draft(point,title="Focused lesson"):
    evidence=teaching(point)
    return {"title":title,
      "intro":"This lesson explains a specific source-grounded mechanism with a real example.",
      "sections":[
        {"heading":"Why this mechanism matters","text":"The original source establishes a specific goal and a set of conditions for evaluating the result of the operation."},
        {"heading":"Causal process","text":"The author traces the conditions through the mechanism and checks the predicted output against the observed result."},
        {"heading":"Boundary and counterexample","text":"A controlled change to one source condition distinguishes the mechanism from an unsupported or coincidental explanation."}],
      "mini_questions":[{"question":"Which condition changes the outcome?","answer":"The relevant source condition determines the next result."}],
      "checkpoint":{"question":"Which evidence supports the causal conclusion?",
        "options":["A visual theme alone","A source-anchored before-and-after comparison","The number of buttons on the page"],
        "correct_index":1,"feedback":"The source and mechanism must support the conclusion.",
        "rubric":"A valid response identifies a source-anchored condition, explains the mechanism it affects, and predicts the correct change in outcome."},
      "represented_fact_ids":[x["id"] for x in point["required_facts"]],
      "teaching_evidence":[evidence]}

def content_review(plan,source,drafts):
    details=[];lookup={p["lp_id"]:p for p in plan["points"]}
    for page in plan["pages"]:
        obj=drafts[page["page_id"]]
        points=[lookup[x] for x in page["lp_ids"]]
        fids=[f for p in points for f in p["required_facts"]]
        quote=obj["teaching_evidence"][0]["fact_explanations"][0]["explanation"]
        audits=[{"fact_id":f["id"],"source_span_id":f["span_id"],
                 "source_quote":f["source_quote"],
                 "draft_quote":quote,"grounded":True,"explained":True,
                 "reason":CONTENT_REASON} for f in fids]
        dim=[{"dimension":k,"passed":True,
              "draft_quote":next(text for text in qc.dimension_text(obj,k) if qc.substantial(text,35)),
              "reason":CONTENT_REASON} for k in qc.REVIEW_DIMENSIONS]
        details.append({"page_id":page["page_id"],"approved":True,"issues":[],
             "checked_fact_ids":[f["id"] for f in fids],
             "draft_sha256":agent.digest(obj),"fact_audits":audits,
             "quality_dimensions":dim})
    return {"review_mode":"isolated_host_agent","writer_context_id":"fixture-author",
         "reviewer_context_id":"fixture-content-reviewer",
         "source_sha256":source["source_sha256"],
         "plan_sha256":agent.digest(plan),"pages":details}

def browser_receipt(ws):
    w=Path(ws);manifest=host.read_json(w/"content-manifest.json")
    result={"passed":True,"browser_executed":True,"pages_tested":len(manifest["pages"]),
      "issues":[],"viewports_tested":[390,1280],"keyboard_tested":True,
      "js_disabled_tested":True,"interactive_tested":True,
      "manifest_sha256":host.sha((w/"content-manifest.json").read_bytes()),
      "rendered_files":{x["file"]:host.sha((w/"draft-pages"/x["file"]).read_bytes()) for x in manifest["pages"]}}
    host.atomic_json(w/"reports"/"browser.json",result)
    return result
