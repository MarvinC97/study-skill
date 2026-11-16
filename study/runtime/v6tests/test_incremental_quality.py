"""Study-D efficient G2/G3/G4 acceptance, all with host-native model fixtures."""
import copy,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
sys.path.insert(0,str(Path(__file__).parent))
import study_runtime as host
import quality_contract as qc
import v6_agent as agent
import quality_fixture as qf

RATIONALE=("The neighboring source facts establish one shared mechanism and can be "
    "examined through a single worked example without dropping either independent LP.")
REASON=("The independent reviewer checked the exact scoped facts and verified "
    "a coherent teaching objective with an explicit condition, consequence and boundary.")
CONNECT=("This learning point supplies one necessary condition within the shared "
    "mechanism, and the explanation below shows how that condition changes the result.")

def build_workspace(root):
    w=root/"work"
    source=root/"text.md"
    source.write_text(
      "\n".join("## Part %d\nThe learner needs a source-grounded condition %d and its resulting mechanism to predict the outcome under a controlled change.\n"%(i,i) for i in range(1,5)),encoding="utf-8")
    host.ingest(w,source)
    src=host.read_json(w/"source.json")
    points=[]
    for i,seg in enumerate(src["segments"],1):
        points.append({"lp_id":f"LP{i:03d}","kind":"mechanism",
          "title":"Mechanism %d"%i,"goal":"Explain each grounded mechanism and its behavior",
          "source_span_ids":[seg["id"]],"required_facts":[{
            "id":f"F{i:03d}","text":seg["text"],"span_id":seg["id"]}],"prerequisites":[]})
    plan={"mode":"study-d","source_sha256":src["source_sha256"],
      "points":points,"pages":[
        {"page_id":"P001","title":"Connected mechanism A",
         "learning_objective":"Explain how the two connected steps cause the first outcome",
         "grouping_rationale":RATIONALE,"lp_ids":[p["lp_id"] for p in points[:2]]},
        {"page_id":"P002","title":"Connected mechanism B",
         "learning_objective":"Explain how the two connected steps cause the second outcome",
         "grouping_rationale":RATIONALE,"lp_ids":[p["lp_id"] for p in points[2:4]]}]}
    qf.add_inventory(plan,src)
    host.atomic_json(w/"plan.json",plan)
    return w,src,plan

def new_batched_review(src,plan,batches=None,page_ids=None,reused_batches=None,reused_pages=None):
    batches=batches if batches is not None else [[p["lp_id"] for p in plan["points"][:2]],
                                                   [p["lp_id"] for p in plan["points"][2:4]]]
    page_ids=page_ids if page_ids is not None else [p["page_id"] for p in plan["pages"]]
    pages={p["page_id"]:p for p in plan["pages"]}
    return {"review_contract":"g2-batched-v3",
      "review_mode":"isolated_host_agent","writer_context_id":"author-one",
      "reviewer_context_id":"reviewer-two",
      "approved":True,"issues":[],
      "plan_sha256":agent.digest(plan),"source_sha256":src["source_sha256"],
      "checked_span_ids":[x["id"] for x in src["segments"]],
      "checked_inventory_ids":[i["id"] for i in plan["source_inventory"]],
      "experiment_ids_checked":[],"reflection_numbers_checked":[],
      "batch_audits":[{"batch_id":"batch-"+str(i),"lp_ids":ids,
         "scope_sha256":qc.review_batch_scope(src,plan,ids),
         "approved":True,"issues":[],"reason":REASON,"risk_audits":[]}
         for i,ids in enumerate(batches,1)],
      "reuse_batch_sha256":reused_batches or [],
      "risk_audits":[],
      "page_audits":[{"page_id":pid,"scope_sha256":qc.review_page_scope(src,plan,pages[pid]),
         "coherent":True,"needs_split":False,"reason":REASON} for pid in page_ids],
      "reuse_page_sha256":reused_pages or []}

def shared_draft(points):
    d=qf.draft(points[0],title="Together: shared mechanism")
    shared=qf.teaching(points[0])
    shared["lp_ids"]=[p["lp_id"] for p in points]
    d["shared_teaching"]=shared
    d["teaching_evidence"]=[
      {"lp_id":p["lp_id"],"lp_connection":CONNECT,
       "fact_explanations":qf.teaching(p)["fact_explanations"]}
      for p in points]
    d["represented_fact_ids"]=[f["id"] for p in points for f in p["required_facts"]]
    d["mini_questions"]=[{"question":"Which source condition changes the output?",
                          "answer":"The relevant source condition changes the predicted outcome."}
                         for p in points]
    return d

def page_review(src,plan,page,draft):
    points={p["lp_id"]:p for p in plan["points"]}
    fact_checks=[]
    for p in (points[i] for i in page["lp_ids"]):
        for f in p["required_facts"]:
            item=next(x for r in draft["teaching_evidence"] if r["lp_id"]==p["lp_id"]
                      for x in r["fact_explanations"] if x["fact_id"]==f["id"])
            fact_checks.append({"fact_id":f["id"],"source_span_id":f["span_id"],
              "source_quote":f["source_quote"],"draft_quote":item["explanation"],
              "grounded":True,"explained":True})
    dimensions=[{"dimension":kind,"passed":True,"reason":REASON,
      "draft_quote":next(x for x in qc.dimension_text(draft,kind) if qc.substantial(x,35))}
      for kind in qc.REVIEW_DIMENSIONS]
    return {"review_contract":"g4-compact-v3",
      "review_scope_sha256":qc.content_page_scope(src,plan,page,draft),
      "page_id":page["page_id"],"approved":True,"issues":[],
      "checked_fact_ids":[f["id"] for p in plan["points"] if p["lp_id"] in page["lp_ids"]
                          for f in p["required_facts"]],
      "draft_sha256":agent.digest(draft),
      "fact_checks":fact_checks,"quality_dimensions":dimensions,"risk_audits":[]}

class EfficientStudyTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.w,self.source,self.plan=build_workspace(Path(self.temp.name))

    def approve_plan(self,review=None):
        review=review or new_batched_review(self.source,self.plan)
        p=self.w/"review-input.json";host.atomic_json(p,review)
        return agent.accept_plan_review(self.w,p)

    def test_four_atomic_LPs_fit_two_coherent_pages(self):
        result=agent.plan_check(self.w)
        self.assertEqual(result["status"],"pass",result)
        self.assertEqual(result["LPs"],4)
        self.assertEqual(result["pages"],2)
        review=self.approve_plan()
        self.assertEqual(review["reviewed_batches"],2)
        self.assertEqual(review["reviewed_grouped_pages"],2)

    def test_rejects_overloaded_page_and_ungrounded_grouping(self):
        self.plan["pages"]=[{"page_id":"P001","title":"Overloaded",
         "lp_ids":[p["lp_id"] for p in self.plan["points"]]}]
        self.plan["pages"][0]["grouping_rationale"]="just group"
        host.atomic_json(self.w/"plan.json",self.plan)
        problems=host.validate_plan(self.w)["issues"]
        self.assertTrue(any("grouping rationale" in p for p in problems),problems)

    def test_scoped_plan_batches_and_one_changed_page_reused(self):
        old=self.approve_plan()
        first=self.plan["pages"][0];second=self.plan["pages"][1]
        batch_hashes=[qc.review_batch_scope(self.source,self.plan,ids) for ids in
                     [[p["lp_id"] for p in self.plan["points"][:2]],
                      [p["lp_id"] for p in self.plan["points"][2:4]]]]
        unchanged_scope=qc.review_page_scope(self.source,self.plan,first)
        self.plan["pages"][1]["grouping_rationale"]+=(" The revised page narrows the example to one stable source case.")
        host.atomic_json(self.w/"plan.json",self.plan)
        review=new_batched_review(self.source,self.plan,batches=[],page_ids=["P002"],
            reused_batches=batch_hashes,reused_pages=[unchanged_scope])
        out=self.approve_plan(review)
        self.assertEqual(out["reviewed_batches"],0)
        self.assertEqual(out["reused_batches"],2)
        self.assertEqual(out["reviewed_grouped_pages"],1)

    def test_shared_teaching_has_one_spine_and_every_fact(self):
        draft=shared_draft(self.plan["points"][:2])
        problems=host.validate_content_data(self.plan["points"][:2],draft)
        self.assertEqual(problems,[])
        markup=host.html_page(self.plan["pages"][0],self.plan["points"][:2],
                              draft,self.source,"index.html","index.html")
        self.assertEqual(markup.count('data-shared-teaching="true"'),1)
        for p in self.plan["points"][:2]:
            self.assertIn('data-teaching-lp="'+p["lp_id"]+'"',markup)
            self.assertIn('data-authored-fact-id="'+p["required_facts"][0]["id"]+'"',markup)

    def test_compact_content_review_and_reuse(self):
        self.approve_plan()
        host.approve_outline(self.w);agent.freeze(self.w)
        drafts={}
        for pg in self.plan["pages"]:
            points=[p for p in self.plan["points"] if p["lp_id"] in pg["lp_ids"]]
            drafts[pg["page_id"]]=shared_draft(points)
            host.atomic_json(self.w/"drafts"/(pg["page_id"]+".json"),drafts[pg["page_id"]])
        page_checks=[page_review(self.source,self.plan,pg,drafts[pg["page_id"]])
                     for pg in self.plan["pages"]]
        request={"review_contract":"g4-compact-v3","review_mode":"isolated_host_agent",
         "writer_context_id":"author","reviewer_context_id":"reviewer",
         "source_sha256":self.source["source_sha256"],
         "plan_sha256":agent.digest(self.plan),"pages":page_checks}
        f=self.w/"content-input.json";host.atomic_json(f,request)
        result=agent.accept_content_review(self.w,f)
        self.assertEqual(result["reused_pages"],0)
        request["pages"]=[]
        request["reuse_page_sha256"]=[p["review_scope_sha256"] for p in page_checks]
        host.atomic_json(f,request)
        reused=agent.accept_content_review(self.w,f)
        self.assertEqual(reused["reused_pages"],2)
        changed=drafts["P002"]
        changed["shared_teaching"]["core_explanation"]+=" This sentence changes the reviewed draft."
        host.atomic_json(self.w/"drafts"/"P002.json",changed)
        request["pages"]=[page_review(self.source,self.plan,self.plan["pages"][1],changed)]
        request["reuse_page_sha256"]=[page_checks[0]["review_scope_sha256"]]
        host.atomic_json(f,request)
        modified=agent.accept_content_review(self.w,f)
        self.assertEqual(modified["reused_pages"],1)

if __name__=="__main__":unittest.main()
