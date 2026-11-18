"""Test-only V6.5 module data and reviewer receipts. Not an actual agent review."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parents[1]))
import lesson_contract as lesson
import storyboard_contract as sb
import study_runtime as host

REASON=("This isolated fixture record checks that the teaching component presents "
        "one source-grounded relationship and a changed-condition learning action "
        "without relying on copied source quotations or decorative labels.")


def first_props(kind):
    if kind=="causal-flow":
        return {"nodes":[
          {"id":"read","label":"Read the evidence","meaning":"Inspect the full source and identify its required condition."},
          {"id":"apply","label":"Apply the decision","meaning":"Use the observed condition to select an operation."},
          {"id":"check","label":"Verify the result","meaning":"Compare the output with the documented target requirement."}],
          "edges":[{"from":"read","to":"apply","label":"The observed condition determines the valid operation"},
                   {"from":"apply","to":"check","label":"The operation produces a measurable result"}]}
    if kind=="decision-explorer":
        return {"start":"root","nodes":[
          {"id":"root","prompt":"What should the agent inspect after a failed tool action?",
           "options":[
             {"label":"Check tool return","to":"tool","reason":"Tool execution may have failed independently of the proposed action."},
             {"label":"Train the model first","to":"train","reason":"Training should follow a verified diagnosis of a model-specific deficiency."}]},
          {"id":"tool","outcome":"Inspect the tool result before changing the model.",
           "reason":"This isolates the first actual failure from the later generated explanation."},
          {"id":"train","outcome":"Confirm the model error before retraining the parameters.",
           "reason":"A training intervention must address a reproducible model-side mistake."}]}
    if kind=="variable-lab":
        return {"formula":"pass-at-k",
          "question":"How does increasing the number of independent attempts change the chance of one success?",
          "interpretation":"Independent samples improve the chance of at least one successful attempt, with diminishing gains.",
          "controls":[
             {"id":"p","label":"Single attempt probability","min":0.05,"max":0.95,"step":0.05,"default":0.25},
             {"id":"k","label":"Independent sample count","min":1,"max":16,"step":1,"default":3}]}
    if kind=="math-stepper":
        return {"formula":"Return = reward + discount × future value",
          "steps":[
             {"expression":"2 + 0.5 × 4","reason":"Insert the observed reward and the estimated discounted future state value."},
             {"expression":"2 + 2 = 4","reason":"Multiply the future state value by the discount and add the immediate reward."}]}
    if kind=="experiment-comparator":
        return {"columns":["Condition","Observation","Evidence boundary"],
          "rows":[["Control","Baseline source-aligned behavior","Synthetic teaching example"],
                  ["Changed condition","Different outcome following altered input","Synthetic teaching example"]],
          "provenance":"Synthetic classroom data only; these entries are explanatory placeholders, not reported study results.",
          "interpretation":"Compare controlled input conditions with their observed differences before drawing a qualified conclusion."}
    if kind=="trace-debugger":
        return {"steps":[
          {"action":"Read the project requirement","evidence":"Requirement lists a necessary hidden verification step.","consequence":"Agent records intended output conditions.","first_error":False},
          {"action":"Claim completion too early","evidence":"No independent verification tool result appears in the trace.","consequence":"The output appears complete but skips required checks.","first_error":True},
          {"action":"Receive an external failure report","evidence":"Holdout checks identify the skipped verification step.","consequence":"The final result fails the target acceptance.","first_error":False}],
          "repair":"Run the required independent verification tool before declaring the task complete.",
          "holdout":"Test both incomplete and already-complete cases so the agent neither stops early nor loops forever."}
    if kind=="worked-example":
        return {"scenario":"A small source-grounded decision task changes one input while holding other variables fixed.",
          "input":"The old source condition, a revised condition and the original expected result.",
          "steps":["Identify the exact source field that changed and the rule associated with it.",
                   "Apply the same rule to the new condition, then compare the predicted and observed outcome."],
          "outcome":"The learner explains the changed result by tracing the modified input through a concrete rule."}
    raise ValueError(kind)


def storyboard(plan,page,points,spec,kind="decision-explorer",layout=None):
    facts=[f["id"] for p in points for f in p["required_facts"]]
    lp_ids=list(page["lp_ids"])
    layout=layout or ("evidence" if kind in ("experiment-comparator","trace-debugger")
                      else "exploration" if kind in ("variable-lab","math-stepper")
                      else "overview")
    checkpoint={"question":spec["checkpoint"]["question"],
      "changed_condition":spec["checkpoint"]["changed_condition"],
      "rubric":spec["checkpoint"]["rubric"],
      "options":[{"label":"Copy the memorized answer","correct":False,
                  "reason":"Reusing the old answer ignores the changed source condition."},
                 {"label":"Trace the changed condition and recompute","correct":True,
                  "reason":"This links the new input through the source-supported mechanism."},
                 {"label":"Choose by visual formatting only","correct":False,
                  "reason":"Presentation style alone cannot establish the causal outcome."}]}
    if kind=="causal-flow":lp_action="observe"
    elif kind in ("experiment-comparator",):lp_action="compare"
    elif kind in ("variable-lab","math-stepper"):lp_action="compute"
    elif kind in ("decision-explorer","trace-debugger"):lp_action="diagnose"
    else:lp_action="predict"
    return {"schema_version":sb.VERSION,"page_id":page["page_id"],
      "lesson_spec_sha256":sb.fingerprint(spec),
      "layout":layout,"learning_action":lp_action,
      "narrative":"First observe a concrete source-grounded relationship, then change one condition and justify the resulting behavior.",
      "scenes":[
        {"id":"scene-primary","module":kind,"lp_ids":lp_ids,"fact_ids":facts,
         "purpose":"Investigate the source-grounded mechanism through a meaningful interactive teaching operation.",
         "props":first_props(kind)},
        {"id":"scene-transfer","module":"transfer-checkpoint",
         "lp_ids":lp_ids,"fact_ids":facts,
         "purpose":"Predict the outcome after a condition changes, then explain the result using original source evidence.",
         "props":checkpoint}
      ]}


def write_storyboard(ws,plan,source,page,spec,points,kind="decision-explorer",layout=None):
    w=Path(ws)
    board=storyboard(plan,page,points,spec,kind,layout)
    file,reviewfile,_=sb.path_set(w,page["page_id"])
    host.atomic_json(file,board)
    review={"contract":sb.VERSION,"review_mode":"isolated_host_agent",
      "writer_context_id":"fixture-story-author","reviewer_context_id":"fixture-story-reviewer",
      "page_id":page["page_id"],"source_sha256":source["source_sha256"],
      "plan_sha256":sb.fingerprint(plan),"lesson_spec_sha256":sb.fingerprint(spec),
      "storyboard_sha256":sb.fingerprint(board),"approved":True,"issues":[],
      "scene_audits":[{"scene_id":x["id"],"passed":True,"reason":REASON}
                      for x in board["scenes"]]}
    host.atomic_json(reviewfile,review)
    return board,sb.fingerprint(board)


def write_render_review(ws,plan,source,page,spec,board,qa,htmlfile):
    w=Path(ws);_,_,path=sb.path_set(w,page["page_id"])
    review={"contract":"render-review-v1","review_mode":"isolated_host_agent",
      "writer_context_id":"fixture-html-author","reviewer_context_id":"fixture-render-reviewer",
      "page_id":page["page_id"],"source_sha256":source["source_sha256"],
      "plan_sha256":sb.fingerprint(plan),"lesson_spec_sha256":sb.fingerprint(spec),
      "storyboard_sha256":sb.fingerprint(board),"html_sha256":sb.file_hash(htmlfile),
      "browser_manifest_sha256":qa["manifest_sha256"],
      "screenshot_sha256":{
         view:qa["screenshots"][page["page_id"]][view]["sha256"]
         for view in ("desktop","mobile")},
      "approved":True,"issues":[],"checks":[
        {"dimension":dimension,"passed":True,"reason":REASON}
        for dimension in sorted(sb.RENDER_DIMENSIONS)],
      "scene_audits":[{"scene_id":x["id"],"rendered":True,"reason":REASON}
                      for x in board["scenes"]]}
    host.atomic_json(path,review)
    return review
