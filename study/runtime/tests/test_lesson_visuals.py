"""Actual Chromium acceptance for three Study V6.4 learning layouts."""
import sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"v6tests"))
import study_runtime as host
import lesson_render as renderer
import quality_fixture as qf
from test_incremental_quality import build_workspace,shared_draft

class ThreeKindBrowserPilot(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.w,self.source,self.plan=build_workspace(Path(self.tmp.name))
  host.atomic_json(self.w/"frozen-plan.json",self.plan)
  self.page=self.plan["pages"][0]
  self.points=[p for p in self.plan["points"] if p["lp_id"] in self.page["lp_ids"]]

 def test_real_chromium_three_teaching_shapes_and_unchanged_cache(self):
  for kind,visual in (("mechanism","process"),("experiment","experiment"),
                      ("failure_case","timeline")):
   draft=shared_draft(self.points)
   spec,_=qf.prepare_design(self.w,self.plan,self.source,self.page,draft,kind=kind)
   html=renderer.render(self.page,self.points,draft,self.source,spec)
   path=self.w/"draft-pages"/(self.page["page_id"]+".html")
   host.write_text(path,html)
   host.atomic_json(self.w/"content-manifest.json",{
     "source_sha256":self.source["source_sha256"],"index":"index.html",
     "pages":[{"page_id":self.page["page_id"],"lp_ids":self.page["lp_ids"],
        "file":path.name,"draft_sha256":host.sha(__import__("json").dumps(draft,ensure_ascii=False,sort_keys=True)),
        "rendered_sha256":host.sha(html)}]})
   # For this one-page fixture, all genuine visual/interaction tests run on new bytes.
   report=host.browser_qa(self.w)
   self.assertTrue(report["passed"],(kind,report))
   self.assertEqual(report["pages_executed_now"],1)
   self.assertEqual(report["pages_cached"],0)
   self.assertEqual(report["viewports_tested"],[390,1280])
   static=host.content_static_check(self.w)
   self.assertEqual(static["status"],"pass",(kind,static["issues"]))
   # Source and HTML bytes are unchanged, so Chrome is not rerun.
   reuse=host.browser_qa(self.w)
   self.assertEqual(reuse["pages_executed_now"],0)
   self.assertEqual(reuse["pages_cached"],1)

if __name__=="__main__":unittest.main()
