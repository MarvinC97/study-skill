"""Negative/regression acceptance: shallow teaching, merged LPs, false reviews and stale QA."""
import sys,unittest,tempfile,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
sys.path.insert(0,str(Path(__file__).parent))
import study_runtime as host
import quality_contract as qc
import v6_agent as agent
import quality_fixture as qf

class DeepGateRegression(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.w=Path(self.temp.name)/"course"
  self.w.mkdir()
  self.original=Path(__file__).parents[1]/"fixtures"/"training-mini.md"
  host.ingest(self.w,self.original)
  self.source=host.read_json(self.w/"source.json")
  self.points=[]
  for i,seg in enumerate(self.source["segments"],1):
   self.points.append({"lp_id":f"LP{i:03d}","title":"Mechanism "+str(i),
     "goal":"Explain one source-grounded mechanism with a concrete decision",
     "kind":"mechanism","source_span_ids":[seg["id"]],"prerequisites":[],
     "required_facts":[{"id":f"FACT{i:03d}","text":seg["text"],"span_id":seg["id"]}]})
  self.plan={"mode":"study-d","source_sha256":self.source["source_sha256"],
    "points":self.points,"pages":[{"page_id":f"P{i:03d}","title":p["title"],"lp_ids":[p["lp_id"]]}
       for i,p in enumerate(self.points,1)]}
  qf.add_inventory(self.plan,self.source)
  host.atomic_json(self.w/"plan.json",self.plan)

 def test_rejects_two_independent_mechanisms_in_one_lp(self):
  item=copy.deepcopy(self.plan["source_inventory"][0])
  item["id"]="EXTRA_ATOMIC"
  item["title"]="A second independently testable mechanism"
  self.plan["source_inventory"].append(item)
  self.points[0]["inventory_ids"].append("EXTRA_ATOMIC")
  host.atomic_json(self.w/"plan.json",self.plan)
  issues=host.validate_plan(self.w)["issues"]
  self.assertTrue(any("multiple independent inventory items" in x for x in issues),issues)

 def test_rejects_missing_inventory_for_source_section(self):
  self.plan["source_inventory"]=self.plan["source_inventory"][:-1]
  host.atomic_json(self.w/"plan.json",self.plan)
  issues=host.validate_plan(self.w)["issues"]
  self.assertTrue(any("inventory" in x.lower() for x in issues),issues)

 def test_rejects_unmapped_numbered_experiment_and_thought_question(self):
  # Source-specific markers must be represented in plan; a title-only mention is insufficient.
  with_experiment=("## Tests\n> **实验 8-1：模型比较**\n"+
    ("具体测试在固定条件下运行，记录结果和局限。"*6)+
    "\n## 思考题\n1. 试说明这一条件为什么改变机制及其适用范围。\n")
  # Keep a coherent small source so the deterministic inventory can be checked.
  self.assertEqual(qc.experiment_markers(with_experiment),{"8-1"})
  self.assertEqual(qc.reflection_numbers(with_experiment),{1})
  scoped=dict(self.source,text=with_experiment)
  issues=qc.validate_deep_inventory(scoped,self.plan)
  self.assertTrue(any("experiments omitted" in x for x in issues),issues)
  self.assertTrue(any("reflection question coverage" in x for x in issues),issues)

 def test_rejects_three_paragraph_shallow_lesson_even_with_correct_fact_ids(self):
  p=self.points[0]
  shallow={"title":"A lesson","intro":"Summarize the concept.",
    "sections":[{"heading":"Why","text":"The concept matters in this case."},
      {"heading":"How","text":"The system follows a standard workflow."},
      {"heading":"Example","text":"An example helps with this concept."}],
    "represented_fact_ids":[p["required_facts"][0]["id"]],
    "mini_questions":[{"question":"Why?","answer":"Because it is so."}],
    "checkpoint":{"question":"What is correct?","options":["A","B","C"],
         "correct_index":1,"feedback":"An explanation"}}
  issues=host.validate_content_data([p],shallow)
  self.assertTrue(any("teaching_evidence" in x for x in issues),issues)
  self.assertTrue(any("rubric" in x for x in issues),issues)

 def test_experiment_kind_and_missing_methods_cannot_bypass_review(self):
  self.plan["source_inventory"][0]["kind"]="experiment"
  self.plan["source_inventory"][0]["experiment_id"]="8-1"
  host.atomic_json(self.w/"plan.json",self.plan)
  issues=host.validate_plan(self.w)["issues"]
  self.assertTrue(any("LP kind disagrees" in x for x in issues),issues)
  experimental=copy.deepcopy(self.points[0]);experimental["kind"]="experiment"
  draft=qf.draft(experimental)
  issues=host.validate_content_data([experimental],draft)
  self.assertTrue(any("experimental method/result missing" in x for x in issues),issues)

 def test_good_structured_lesson_satisfies_static_g3(self):
  draft=qf.draft(self.points[0])
  self.assertEqual(host.validate_content_data([self.points[0]],draft),[])

 def test_rejects_approved_plan_without_atomicity_audit(self):
  reviewer=qf.plan_review(self.plan,self.source)
  reviewer.pop("atomicity_audits")
  p=self.w/"plan-review.json";host.atomic_json(p,reviewer)
  with self.assertRaises(host.GateError):
   agent.accept_plan_review(self.w,p)

 def test_rejects_approved_content_without_semantic_fact_audit(self):
  reviewer=qf.plan_review(self.plan,self.source)
  p=self.w/"plan-review.json";host.atomic_json(p,reviewer)
  agent.accept_plan_review(self.w,p)
  host.approve_outline(self.w);agent.freeze(self.w)
  drafts={}
  for page in self.plan["pages"]:
   point=next(p for p in self.points if p["lp_id"]==page["lp_ids"][0])
   d=qf.draft(point);drafts[page["page_id"]]=d
   host.atomic_json(self.w/"drafts"/(page["page_id"]+".json"),d)
  review=qf.content_review(self.plan,self.source,drafts)
  review["pages"][0].pop("fact_audits")
  reviewpath=self.w/"review-input.json";host.atomic_json(reviewpath,review)
  with self.assertRaises(host.GateError):
   agent.accept_content_review(self.w,reviewpath)

 def test_one_generic_review_quote_cannot_pass_all_dimensions(self):
  # A rubber-stamp review repeating one explanatory quote for every dimension fails.
  rp=self.w/"plan-review.json";host.atomic_json(rp,qf.plan_review(self.plan,self.source))
  agent.accept_plan_review(self.w,rp);host.approve_outline(self.w);agent.freeze(self.w)
  drafts={}
  for page in self.plan["pages"]:
   point=next(p for p in self.points if p["lp_id"]==page["lp_ids"][0])
   d=qf.draft(point);drafts[page["page_id"]]=d
   host.atomic_json(self.w/"drafts"/(page["page_id"]+".json"),d)
  receipt=qf.content_review(self.plan,self.source,drafts)
  rubber_stamp=receipt["pages"][0]["fact_audits"][0]["draft_quote"]
  for dimension in receipt["pages"][0]["quality_dimensions"]:
   dimension["draft_quote"]=rubber_stamp
  path=self.w/"rubber-stamped-review.json";host.atomic_json(path,receipt)
  with self.assertRaises(host.GateError):
   agent.accept_content_review(self.w,path)

 def test_unchanged_review_receipt_cannot_approve_changed_draft(self):
  p=self.w/"plan-review.json";host.atomic_json(p,qf.plan_review(self.plan,self.source))
  agent.accept_plan_review(self.w,p);host.approve_outline(self.w);agent.freeze(self.w)
  drafts={}
  for page in self.plan["pages"]:
   point=next(p for p in self.points if p["lp_id"]==page["lp_ids"][0])
   d=qf.draft(point);drafts[page["page_id"]]=d
   host.atomic_json(self.w/"drafts"/(page["page_id"]+".json"),d)
  review=qf.content_review(self.plan,self.source,drafts)
  rp=self.w/"content-review-input.json";host.atomic_json(rp,review)
  agent.accept_content_review(self.w,rp)
  first=self.w/"drafts"/(self.plan["pages"][0]["page_id"]+".json")
  bad=host.read_json(first);bad["teaching_evidence"][0]["worked_example"]["why"]+=" changed"
  host.atomic_json(first,bad)
  with self.assertRaises(host.GateError):
   agent.check_review_integrity(self.w)

 def test_g6_prepared_is_not_delivered_and_confirmation_is_exact(self):
  # Validated host fixtures: this is a delivery-state test, not an actual UI review.
  p=self.w/"plan-review.json";host.atomic_json(p,qf.plan_review(self.plan,self.source))
  agent.accept_plan_review(self.w,p);host.approve_outline(self.w);agent.freeze(self.w)
  drafts={}
  for page in self.plan["pages"]:
   point=next(p for p in self.points if p["lp_id"]==page["lp_ids"][0])
   drafts[page["page_id"]]=qf.draft(point,page["title"])
   host.atomic_json(self.w/"drafts"/(page["page_id"]+".json"),drafts[page["page_id"]])
  rp=self.w/"content-review-input.json"
  host.atomic_json(rp,qf.content_review(self.plan,self.source,drafts))
  agent.accept_content_review(self.w,rp)
  agent.render(self.w)
  host.record_gate(self.w,"G3_CONTENT",True,evidence=self.w/"draft-pages")
  host.record_gate(self.w,"G4_REVIEW",True,evidence=self.w/"reviews"/"content-review.json")
  qf.browser_receipt(self.w)
  host.record_gate(self.w,"G5_BROWSER",True,evidence=self.w/"reports"/"browser.json")
  agent.publish(self.w)
  st=host.state(self.w)
  self.assertFalse(st["gates"]["G6_DELIVERY"]["ok"])
  self.assertEqual(st["verification"]["G6_DELIVERY"],"PREPARED")
  first=host.next_delivery(self.w)
  self.assertEqual(host.state(self.w)["verification"]["G6_DELIVERY"],"PREPARED")
  count=len(host.read_json(self.w/"delivery-queue.json")["files"])
  for i in range(count):
   prepared=first if i==0 else host.next_delivery(self.w)
   host.confirm_delivery(self.w,prepared["file"])
   if i<count-1:
    self.assertEqual(host.state(self.w)["verification"]["G6_DELIVERY"],"IN_PROGRESS")
  self.assertTrue(host.state(self.w)["gates"]["G6_DELIVERY"]["ok"])
  self.assertEqual(host.state(self.w)["verification"]["G6_DELIVERY"],"DELIVERY_CONFIRMED")

if __name__=="__main__":unittest.main()
