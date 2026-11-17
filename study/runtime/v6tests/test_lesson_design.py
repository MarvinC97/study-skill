"""V6.4 negative/positive design-first quality contracts; no model API."""
import copy,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
sys.path.insert(0,str(Path(__file__).parent))
import lesson_contract as lc
import lesson_render as lr
import study_runtime as host
import v6_agent as agent
import quality_fixture as qf
from test_incremental_quality import build_workspace,shared_draft,new_batched_review

class DesignFirstTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.w,self.source,self.plan=build_workspace(Path(self.temp.name))
  review=self.w/"plan-review-input.json"
  host.atomic_json(review,new_batched_review(self.source,self.plan))
  agent.accept_plan_review(self.w,review)
  host.approve_outline(self.w)
  agent.freeze(self.w)
  self.page=self.plan["pages"][0]
  self.points=[p for p in self.plan["points"] if p["lp_id"] in self.page["lp_ids"]]
  self.draft=shared_draft(self.points)

 def ready(self,kind="mechanism"):
  return qf.prepare_design(self.w,self.plan,self.source,self.page,self.draft,kind)

 def test_no_spec_blocks_a_new_lesson_even_when_draft_fields_are_filled(self):
  host.atomic_json(self.w/"drafts"/(self.page["page_id"]+".json"),self.draft)
  with self.assertRaises(host.GateError):
   agent.design_check(self.w,self.page["page_id"])

 def test_valid_design_and_review_are_accepted(self):
  spec,digest=self.ready()
  self.assertEqual(lc.validate_spec(spec,self.page,self.points,self.source),[])
  self.assertEqual(lc.validate_draft_alignment(spec,self.draft),[])
  result=agent.design_check(self.w,self.page["page_id"])
  self.assertEqual(result["lesson_spec_sha256"],digest)
  self.assertTrue(result["design_reviewed"])

 def test_one_spec_revision_invalidates_prior_design_review(self):
  spec,_=self.ready()
  spec["misconception"]+=" Changed after the independent review."
  specfile,_=lc.design_paths(self.w,self.page["page_id"])
  host.atomic_json(specfile,spec)
  with self.assertRaises(host.GateError):
   agent.design_check(self.w,self.page["page_id"])

 def test_rejects_hollow_experiment_and_decorative_visual(self):
  spec,_=self.ready(kind="experiment")
  spec["visual"]={"kind":"text","purpose":"Generic arrows and heading decorations stand in for a measured experiment."}
  errors=lc.validate_spec(spec,self.page,self.points,self.source)
  self.assertTrue(any("causal representation" in x for x in errors),errors)

 def test_rejects_wrong_fact_mapping_and_fake_changed_condition(self):
  spec,_=self.ready()
  spec["source_fact_ids"]=[]
  spec["checkpoint"]["changed_condition"]="No real change"
  errors=lc.validate_spec(spec,self.page,self.points,self.source)
  self.assertTrue(any("all and only page facts" in x for x in errors),errors)
  self.assertTrue(any("changed_condition" in x for x in errors),errors)

 def test_draft_checkpoint_must_match_approved_transfer_question(self):
  spec,_=self.ready()
  self.draft["checkpoint"]["question"]="What does LP mean?"
  errors=lc.validate_draft_alignment(spec,self.draft)
  self.assertTrue(errors)

 def test_three_distinct_lesson_kinds_render_source_safe_meaningful_visuals(self):
  for kind,visual in [("mechanism","process"),("experiment","experiment"),
                      ("failure_case","timeline")]:
   draft=copy.deepcopy(self.draft)
   spec=qf.make_spec(self.page,self.points,draft,kind=kind)
   draft["checkpoint"]["question"]=spec["checkpoint"]["question"]
   html=lr.render(self.page,self.points,draft,self.source,spec)
   self.assertIn('data-lesson-contract="lesson-design-v1"',html)
   self.assertIn('data-visual-kind="'+visual+'"',html)
   self.assertIn('data-fact-id=',html)
   self.assertIn("独立",html)
   if kind=="experiment":self.assertIn("synthetic test fixtures",html)
   if kind=="failure_case":self.assertIn("first-error",html)

 def test_source_html_is_escaped_not_run(self):
  spec,_=self.ready()
  spec["visual"]["nodes"][0]["meaning"]='<script>alert("bad")</script>'
  html=lr.render(self.page,self.points,self.draft,self.source,spec)
  self.assertIn('&lt;script&gt;alert',html)
  self.assertNotIn('<script>alert("bad")</script>',html)

if __name__=="__main__":unittest.main()
