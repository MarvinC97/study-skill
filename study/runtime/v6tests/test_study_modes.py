"""User-facing Study / Study-D granularity contract regression tests.

Full source inventory remains authoritative. Study groups related LPs into a
coherent Unit; Study-D retains focused explanations with source depth.
"""
import sys,unittest,copy,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
sys.path.insert(0,str(Path(__file__).parent))
import study_runtime as host
import v6_agent as agent
import quality_fixture as qf
from test_incremental_quality import build_workspace,shared_draft

GOAL="Trace all four stages of one interaction and explain how changing one condition changes the result"
RATIONALE=("All LPs are successive parts of a single source-grounded causal mechanism. "
           "They can be drawn as one loop and checked using the same changed-condition scenario.")
CASE=("A small simulated Agent observes its environment, selects an action, receives a reward, "
      "and traces the resulting trajectory to explain why the next state changes.")
AUDIT_REASON=("The four source-grounded LPs describe one mental model, fit into a single"
              " worked scenario and have manageable cognitive load with independently identifiable facts.")

class StandardAndDeepContracts(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  self.addCleanup(self.tmp.cleanup)
  self.w,self.source,self.plan=build_workspace(Path(self.tmp.name))
  self.plan["mode"]="study"
  self.plan["pages"]=[{"page_id":"U001","title":"One complete learning loop",
       "lp_ids":[x["lp_id"] for x in self.plan["points"]],
       "learning_objective":GOAL,
       "grouping_relation":"causal_chain",
       "shared_case":CASE,
       "grouping_rationale":RATIONALE}]
  host.atomic_json(self.w/"plan.json",self.plan)

 def test_related_four_LPs_make_one_standard_Unit(self):
  p=host.validate_plan(self.w)
  self.assertEqual(p["status"],"pass",p["issues"])
  self.assertEqual((p["LPs"],p["pages"]),(4,1))
  review={"review_mode":"isolated_host_agent",
          "reviewer_context_id":"independent-reviewer",
          "writer_context_id":"teacher",
          "source_sha256":self.source["source_sha256"],
          "plan_sha256":agent.digest(self.plan),
          "checked_span_ids":[x["id"] for x in self.source["segments"]],
          "approved":True,"issues":[],
          "unit_group_audits":[{"page_id":"U001",
              "checked_lp_ids":[x["lp_id"] for x in self.plan["points"]],
              "coherent":True,"shared_case_ok":True,"cognitive_load_ok":True,
              "reason":AUDIT_REASON}]}
  rp=self.w/"review.json";host.atomic_json(rp,review)
  agent.accept_plan_review(self.w,rp)
  draft=shared_draft(self.plan["points"])
  draft["mini_questions"]=draft["mini_questions"][:1]
  self.assertEqual(host.validate_content_data(self.plan["points"],draft,mode="study"),[])
  self.assertTrue(host.validate_content_data(self.plan["points"],draft,mode="study-d"))
  html=host.html_page(self.plan["pages"][0],self.plan["points"],draft,
                      self.source,"overview.html","overview.html")
  self.assertEqual(html.count('data-shared-teaching="true"'),1)
  for point in self.plan["points"]:
    self.assertIn('data-teaching-lp="'+point["lp_id"]+'"',html)

 def test_page_needs_concrete_relation_and_example(self):
  self.plan["pages"][0]["grouping_relation"]="adjacent_in_chapter"
  self.plan["pages"][0]["shared_case"]="example"
  host.atomic_json(self.w/"plan.json",self.plan)
  errors=host.validate_plan(self.w)["issues"]
  self.assertTrue(any("relationship" in e for e in errors),errors)
  self.assertTrue(any("worked scenario" in e for e in errors),errors)

 def test_different_algorithms_overload_one_standard_Unit(self):
  for p in self.plan["points"][:2]:p["kind"]="algorithm"
  host.atomic_json(self.w/"plan.json",self.plan)
  errors=host.validate_plan(self.w)["issues"]
  self.assertTrue(any("heavyweight" in e for e in errors),errors)

 def test_reviewer_must_check_shared_example_and_load(self):
  review={"unit_group_audits":[{"page_id":"U001",
            "checked_lp_ids":[x["lp_id"] for x in self.plan["points"]],
            "coherent":True,"shared_case_ok":False,
            "cognitive_load_ok":True,"reason":AUDIT_REASON}]}
  errors=__import__("quality_contract").validate_study_group_review(review,self.plan)
  self.assertTrue(any("cognitive-load review" in e for e in errors),errors)

 def test_deep_keeps_existing_one_focused_LP_default(self):
  self.plan["mode"]="study-d"
  self.plan["pages"]=[{"page_id":"P%03d"%i,"title":p["title"],
              "lp_ids":[p["lp_id"]]} for i,p in enumerate(self.plan["points"],1)]
  host.atomic_json(self.w/"plan.json",self.plan)
  result=host.validate_plan(self.w)
  self.assertEqual(result["status"],"pass",result["issues"])
  self.assertEqual(result["pages"],4)

if __name__=="__main__":unittest.main()
