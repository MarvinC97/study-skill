"""Real Chromium acceptance for eight teaching operations, screenshot review and staged G6."""
import sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"v6tests"))
import study_runtime as host
import lesson_render as renderer
import v6_agent as agent
import quality_fixture as qf
import storyboard_fixture as sf
import storyboard_contract as sb
from test_incremental_quality import build_workspace,new_batched_review,shared_draft,page_review

KINDS=("causal-flow","decision-explorer","variable-lab","math-stepper",
       "experiment-comparator","trace-debugger","worked-example")

class RealStoryboardBrowser(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.w,self.source,self.plan=build_workspace(Path(self.temp.name))
  self.plan["render_contract"]="storyboard-v1"
  host.atomic_json(self.w/"plan.json",self.plan)
  p=self.w/"plan-review.json"
  host.atomic_json(p,new_batched_review(self.source,self.plan))
  agent.accept_plan_review(self.w,p)
  host.approve_outline(self.w);agent.freeze(self.w)
  self.page=self.plan["pages"][0]
  self.points=[p for p in self.plan["points"] if p["lp_id"] in self.page["lp_ids"]]

 def prepare(self,kind):
  draft=shared_draft(self.points)
  lesson_kind="experiment" if kind=="experiment-comparator" else (
       "failure_case" if kind=="trace-debugger" else
       "math" if kind=="math-stepper" else "mechanism")
  spec,ds=qf.prepare_design(self.w,self.plan,self.source,self.page,draft,
                            kind=lesson_kind)
  board,bs=sf.write_storyboard(self.w,self.plan,self.source,self.page,
                              spec,self.points,kind)
  return draft,spec,board

 def test_seven_component_kinds_in_real_browser(self):
  for kind in KINDS:
   with self.subTest(component=kind):
    draft,spec,board=self.prepare(kind)
    html=renderer.render(self.page,self.points,draft,self.source,spec,storyboard=board)
    root=self.w/"draft-pages"
    host.write_text(root/(self.page["page_id"]+".html"),html)
    host.write_text(root/"index.html",'<html><meta charset="utf-8"><h1>Index</h1></html>')
    host.atomic_json(self.w/"content-manifest.json",{
      "source_sha256":self.source["source_sha256"],"index":"index.html",
      "pages":[{"page_id":self.page["page_id"],"lp_ids":self.page["lp_ids"],
        "file":self.page["page_id"]+".html",
        "draft_sha256":host.sha(__import__("json").dumps(draft,sort_keys=True,ensure_ascii=False)),
        "rendered_sha256":host.sha(html)}]})
    qa=host.browser_qa(self.w)
    self.assertTrue(qa["passed"],(kind,qa))
    self.assertEqual(qa["pages_executed_now"],1)
    self.assertTrue(qa["screenshots"][self.page["page_id"]]["mobile"])
    static=host.content_static_check(self.w)
    self.assertEqual(static["status"],"pass",(kind,static["issues"]))
    again=host.browser_qa(self.w)
    self.assertTrue(again["passed"],(kind,again))
    self.assertEqual(again["pages_executed_now"],0)

 def test_render_review_required_before_incremental_delivery(self):
  draft,spec,board=self.prepare("decision-explorer")
  entry=page_review(self.source,self.plan,self.page,draft)
  entry["storyboard_sha256"]=sb.fingerprint(board)
  review={"review_mode":"isolated_host_agent","writer_context_id":"fixture-content-author",
          "reviewer_context_id":"fixture-content-reviewer",
          "source_sha256":self.source["source_sha256"],
          "plan_sha256":agent.digest(self.plan),"pages":[entry]}
  rfile=self.w/"review-content.json";host.atomic_json(rfile,review)
  with self.assertRaises(host.GateError) as raised:
   agent.stage_next_page(self.w,rfile)
  self.assertIn("RENDER_REVIEW_PENDING",str(raised.exception))
  self.assertFalse((self.w/"published"/(self.page["page_id"]+".html")).exists())
  qa=host.read_json(self.w/"reports"/"browser.json")
  self.assertTrue(qa["passed"])
  html=self.w/"draft-pages"/(self.page["page_id"]+".html")
  sf.write_render_review(self.w,self.plan,self.source,self.page,spec,board,qa,html)
  delivered=agent.stage_next_page(self.w,rfile)
  self.assertTrue(delivered["browser_pass"])
  self.assertEqual(delivered["page_id"],self.page["page_id"])
  self.assertTrue((self.w/"published"/(self.page["page_id"]+".html")).exists())
  render_review=agent.render_review_check(self.w,self.page["page_id"])
  self.assertTrue(render_review["render_reviewed"])
  # Screenshot mutation invalidates the previously accepted reviewer evidence.
  mobile=Path(qa["screenshots"][self.page["page_id"]]["mobile"]["file"])
  original_mobile=mobile.read_bytes()
  mobile.write_bytes(original_mobile+b"tampered")
  with self.assertRaises(host.GateError):
   agent.render_review_check(self.w,self.page["page_id"])
  mobile.write_bytes(original_mobile)
  # A modified HTML invalidates the previously accepted render review.
  html.write_bytes(html.read_bytes()+b"<!-- altered after review -->")
  with self.assertRaises(host.GateError):
   agent.render_review_check(self.w,self.page["page_id"])

if __name__=="__main__":unittest.main()
