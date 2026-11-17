"""Explicit test-only data for strict Study quality receipts. Never use as real review."""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).parents[1]))
import quality_contract as qc
import lesson_contract as lc
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
             "draft_sha256":agent.digest(obj),
             "lesson_spec_sha256":lc.digest(make_spec(page,points,obj)),
             "fact_audits":audits,
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

# All helpers below are TEST FIXTURES; never represent them as real independent
# teacher or reviewer judgments in an actual learner course.

def make_spec(page,points,draft,kind="mechanism"):
    facts=[f["id"] for p in points for f in p["required_facts"]]
    visual={"kind":"process",
       "purpose":"The connected source evidence forms a causal chain: preserve a source, apply an action, then inspect a changed outcome.",
       "nodes":[
         {"id":"input","label":"Source input","meaning":"The original evidence and its relevant condition are identified."},
         {"id":"action","label":"Decision step","meaning":"A learner applies a grounded operation to that evidence."},
         {"id":"result","label":"Verified result","meaning":"The observable outcome is checked against the independent source."}],
       "edges":[
         {"from":"input","to":"action","label":"Use the actual source condition to choose the next operation"},
         {"from":"action","to":"result","label":"Apply the operation and compare its measured result"}]}
    if kind=="experiment":
        visual={"kind":"experiment",
          "purpose":"Contrast a controlled baseline and changed input using separately labelled, explicitly fictional test observations.",
          "columns":["Experimental condition","Observed result"],
          "rows":[["Baseline example (fictional)","Control response from the fixture"],
                  ["Changed condition (fictional)","Different fixture observation"]],
          "data_provenance":"These two rows are synthetic test fixtures, not measurements from the chapter source."}
    elif kind=="failure_case":
        visual={"kind":"timeline",
          "purpose":"Locate the first wrong decision in an execution trace and follow its observable downstream consequences.",
          "nodes":[
             {"id":"start","label":"Task accepted","meaning":"The agent receives the target instructions and its source constraints."},
             {"id":"wrong","label":"Premature completion","meaning":"The agent claims completion before required external checks."},
             {"id":"fix","label":"Correct verification","meaning":"Independent test results are checked before final completion."}],
          "edges":[{"from":"start","to":"wrong","label":"The agent skips the required evidence collection"},
                   {"from":"wrong","to":"fix","label":"A verified test call replaces the premature conclusion"}],
          "first_error_id":"wrong"}
    elif kind=="math":
        visual={"kind":"math","purpose":"Explain exactly how a variable changes the numerical result and how each symbol enters the calculation.",
          "formula":"return = immediate_reward + discount * future_value",
          "variables":{"return":"Total expected score","discount":"Weight for future rewards"}}
    cp={"question":"Which source-grounded condition changes the expected result after the input is modified, and why?",
        "changed_condition":"A new but otherwise comparable input changes the source property used by the operation.",
        "expected_reasoning":"Trace the changed source condition through the original decision steps before predicting the new result.",
        "rubric":"Name the changed property, trace its effect on the operation, and justify the result using the actual source.",
        "fact_ids":facts}
    return {"schema_version":"lesson-design-v1","page_id":page["page_id"],
      "lesson_kind":kind,"lp_ids":page["lp_ids"],
      "objective":"Explain this source-grounded decision mechanism and transfer it to a changed condition.",
      "central_question":"Which source property controls the observed outcome when the learner changes the input?",
      "insight":"An independently checked source condition must explain the result instead of a memorized template.",
      "misconception":"A plausible-looking answer or a matching HTML field proves that the learner understands the mechanism.",
      "source_fact_ids":facts,
      "teaching_moves":[
        {"kind":"intuition","focus":"Show one observable input and predict the immediate result in a tiny scenario.",
         "fact_ids":facts},
        {"kind":"mechanism","focus":"Trace the actual cause and effect from original evidence to the produced result.",
         "fact_ids":facts},
        {"kind":"worked_example","focus":"Work through a complete case with input, meaningful steps and a result check.",
         "fact_ids":facts},
        {"kind":"boundary","focus":"Change one source condition and explain when the prior answer ceases to apply.",
         "fact_ids":facts}],
      "visual":visual,"checkpoint":cp}


def prepare_design(ws,plan,source,page,draft,kind="mechanism"):
    """Generate complete test-only design and faux reviewer receipts."""
    spec=make_spec(page,[p for p in plan["points"] if p["lp_id"] in page["lp_ids"]],draft,kind)
    draft["checkpoint"]["question"]=spec["checkpoint"]["question"]
    w=Path(ws);(w/"drafts").mkdir(parents=True,exist_ok=True)
    host.atomic_json(w/"drafts"/(page["page_id"]+".json"),draft)
    spec_path,review_path=lc.design_paths(w,page["page_id"])
    host.atomic_json(spec_path,spec)
    review={"contract":lc.SCHEMA,"review_mode":"isolated_host_agent",
       "writer_context_id":"fixture-teacher","reviewer_context_id":"fixture-isolated-reviewer",
       "page_id":page["page_id"],"source_sha256":source["source_sha256"],
       "plan_sha256":lc.digest(plan),"lesson_spec_sha256":lc.digest(spec),
       "checked_fact_ids":spec["source_fact_ids"],"approved":True,"issues":[],
       "checks":[{"dimension":name,"passed":True,
          "reason":"The fixture reviewer checks the source-supported objective, explanatory model, worked example and changed-condition test for this dimension."}
          for name in sorted(lc.CHECKS)]}
    host.atomic_json(review_path,review)
    return spec,lc.digest(spec)
