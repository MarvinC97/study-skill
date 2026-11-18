"""Actual standard Study V6.5: no HTML delivery before screenshot Render Review."""
import sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"v6tests"))
import study_runtime as host
import v6_ops
import v6_agent as agent
import storyboard_contract as sb
import quality_fixture as qf
import storyboard_fixture as sf
from test_incremental_quality import build_workspace,shared_draft

REASON=("The four criteria describe one causal lesson which can be explained "
        "with a single worked example, reviewed source facts and a manageable load.")

class RealStandardUnitStoryboard(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.w,self.source,self.plan=build_workspace(Path(self.tmp.name))
  self.plan["mode"]="study";self.plan["render_contract"]="storyboard-v1"
  for pg in self.plan["pages"]:
   pg["grouping_relation"]="causal_chain"
   pg["shared_case"]="A learner changes one condition in a source-grounded mechanism and inspects its computed effect."
  host.atomic_json(self.w/"plan.json",self.plan)
  review={"review_mode":"isolated_host_agent","writer_context_id":"fixture-author",
          "reviewer_context_id":"fixture-reviewer","approved":True,"issues":[],
          "source_sha256":self.source["source_sha256"],
          "plan_sha256":agent.digest(self.plan),
          "checked_span_ids":[x["id"] for x in self.source["segments"]],
          "unit_group_audits":[{"page_id":pg["page_id"],
            "checked_lp_ids":pg["lp_ids"],"coherent":True,
            "shared_case_ok":True,"cognitive_load_ok":True,"reason":REASON}
            for pg in self.plan["pages"]]}
  host.atomic_json(self.w/"review-input.json",review)
  agent.accept_plan_review(self.w,self.w/"review-input.json")
  self.page=self.plan["pages"][0]
  self.points=[p for p in self.plan["points"] if p["lp_id"] in self.page["lp_ids"]]

 def test_two_phase_standard_unit_rendered_review(self):
  draft=shared_draft(self.points)
  spec,design_sha=qf.prepare_design(self.w,self.plan,self.source,self.page,draft)
  board,board_sha=sf.write_storyboard(self.w,self.plan,self.source,
                                     self.page,spec,self.points,"variable-lab")
  receipt={"review_mode":"isolated_host_agent",
      "writer_context_id":"fixture-writer","reviewer_context_id":"fixture-reader",
      "approved":True,"issues":[],"artifact_sha256":agent.digest(draft),
      "checked_fact_ids":[f["id"] for p in self.points for f in p["required_facts"]],
      "lesson_spec_sha256":design_sha,"storyboard_sha256":board_sha,
      "unit_coherence":{"coherent":True,"shared_case_ok":True,"cognitive_load_ok":True,
       "checked_lp_ids":self.page["lp_ids"],"reason":REASON}}
  host.atomic_json(self.w/"reviews"/(self.page["page_id"]+"-unit-review.json"),receipt)
  with self.assertRaises(host.GateError) as exc:
   v6_ops.next_unit(self.w)
  self.assertIn("RENDER_REVIEW_PENDING",str(exc.exception))
  self.assertFalse((self.w/"published"/(self.page["page_id"]+".html")).exists())
  html=self.w/"draft-pages"/(self.page["page_id"]+".html")
  qa=host.read_json(self.w/"reports"/("unit-browser-"+self.page["page_id"]+".json"))
  self.assertTrue(qa["passed"])
  self.assertTrue(qa["screenshots"][self.page["page_id"]]["mobile"])
  sf.write_render_review(self.w,self.plan,self.source,self.page,spec,board,qa,html)
  result=v6_ops.next_unit(self.w)
  self.assertTrue(result["awaiting_confirmation"])
  self.assertEqual(result["unit"],1)
  self.assertTrue((self.w/"published"/(self.page["page_id"]+".html")).exists())
  self.assertEqual(host.state(self.w)["current_unit"],0)
  self.assertTrue((self.w/"unit-delivery-pending.json").is_file())

if __name__=="__main__":unittest.main()
