"""Real browser test of incremental Studio-D staging, without a model API."""
import sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"v6tests"))
import study_runtime as host
import v6_agent as agent
import quality_fixture as qf
from test_incremental_quality import build_workspace,new_batched_review,shared_draft,page_review

class IncrementalBrowserAndDelivery(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.w,self.source,self.plan=build_workspace(Path(self.temp.name))
  self.assertEqual(agent.plan_check(self.w)["status"],"pass")
  review=self.w/"plan-review-input.json"
  host.atomic_json(review,new_batched_review(self.source,self.plan))
  agent.accept_plan_review(self.w,review)
  host.approve_outline(self.w)
  agent.freeze(self.w)

 def prepare(self,index):
  page=self.plan["pages"][index]
  points=[p for p in self.plan["points"] if p["lp_id"] in page["lp_ids"]]
  draft=shared_draft(points)
  qf.prepare_design(self.w,self.plan,self.source,page,draft)
  review={"review_mode":"isolated_host_agent","writer_context_id":"writer-1",
          "reviewer_context_id":"reviewer-2",
          "source_sha256":self.source["source_sha256"],
          "plan_sha256":agent.digest(self.plan),
          "pages":[page_review(self.source,self.plan,page,draft)]}
  filename=self.w/("page-review-%d.json"%(index+1))
  host.atomic_json(filename,review)
  return agent.stage_next_page(self.w,filename)

 def test_one_page_at_a_time_and_browser_cache(self):
  first=self.prepare(0)
  self.assertEqual(first["pages_staged"],1)
  self.assertEqual(first["new_browser_tests"],1)
  self.assertEqual(first["reused_browser_tests"],0)
  queue=host.read_json(self.w/"delivery-queue.json")
  self.assertEqual(queue["files"],["index.html","P001.html"])
  self.assertEqual(host.state(self.w)["verification"]["G6_DELIVERY"],"PREPARED")
  for expected in ("index.html","P001.html"):
   item=host.next_delivery(self.w)
   self.assertEqual(Path(item["file"]).name,expected)
   host.confirm_delivery(self.w,item["file"])
  state=host.state(self.w)
  self.assertFalse(state["gates"]["G6_DELIVERY"]["ok"])
  self.assertEqual(host.next_delivery(self.w)["awaiting_next_page_authoring"],True)
  second=self.prepare(1)
  self.assertEqual(second["pages_staged"],2)
  self.assertEqual(second["new_browser_tests"],1)
  self.assertEqual(second["reused_browser_tests"],1)
  item=host.next_delivery(self.w)
  self.assertEqual(Path(item["file"]).name,"P002.html")
  self.assertEqual(host.state(self.w)["gates"]["G6_DELIVERY"]["ok"],False)
  host.confirm_delivery(self.w,item["file"])
  self.assertTrue(host.state(self.w)["gates"]["G6_DELIVERY"]["ok"])
  self.assertTrue(host.next_delivery(self.w)["finished"])
  cached=host.browser_qa(self.w)
  self.assertTrue(cached["passed"],cached)
  self.assertEqual(cached["pages_executed_now"],0)
  self.assertEqual(cached["pages_cached"],2)

 def test_html_change_retests_only_changed_page(self):
  self.prepare(0)
  for _ in range(2):
   item=host.next_delivery(self.w);host.confirm_delivery(self.w,item["file"])
  self.prepare(1)
  rendered=self.w/"draft-pages"/"P001.html"
  rendered.write_text(rendered.read_text(encoding="utf-8").replace(
      "Study V5","Study V6.2"),encoding="utf-8")
  result=host.browser_qa(self.w)
  self.assertTrue(result["passed"],result)
  self.assertEqual(result["pages_executed_now"],1)
  self.assertEqual(result["pages_cached"],1)
  static=host.content_static_check(self.w)
  self.assertEqual(static["status"],"fail") # artifact changed after manifest freeze

if __name__=="__main__":unittest.main()
