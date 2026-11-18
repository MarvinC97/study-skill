"""V6.5 storyboard gates and eight reusable learning operations."""
import copy,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
sys.path.insert(0,str(Path(__file__).parent))
import lesson_contract as lc
import storyboard_contract as sb
import lesson_render as renderer
import study_runtime as host
import v6_agent as agent
import quality_fixture as qf
import storyboard_fixture as sf
from test_incremental_quality import build_workspace,new_batched_review,shared_draft

CASES=(
    ("causal-flow","mechanism"),
    ("decision-explorer","mechanism"),
    ("variable-lab","mechanism"),
    ("math-stepper","math"),
    ("experiment-comparator","experiment"),
    ("trace-debugger","failure_case"),
    ("worked-example","mechanism")
)

class StoryboardContracts(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.w,self.source,self.plan=build_workspace(Path(self.tmp.name))
        self.plan["render_contract"]="storyboard-v1"
        host.atomic_json(self.w/"plan.json",self.plan)
        host.atomic_json(self.w/"plan-review-input.json",
                         new_batched_review(self.source,self.plan))
        agent.accept_plan_review(self.w,self.w/"plan-review-input.json")
        host.approve_outline(self.w);agent.freeze(self.w)
        self.page=self.plan["pages"][0]
        self.points=[p for p in self.plan["points"] if p["lp_id"] in self.page["lp_ids"]]
        self.draft=shared_draft(self.points)

    def create(self,module="decision-explorer",kind="mechanism"):
        spec,_=qf.prepare_design(self.w,self.plan,self.source,self.page,self.draft,kind=kind)
        board,_=sf.write_storyboard(self.w,self.plan,self.source,self.page,
                                   spec,self.points,module)
        return spec,board

    def test_storyboard_missing_or_stale_stops_authoring(self):
        spec,_=qf.prepare_design(self.w,self.plan,self.source,self.page,self.draft)
        with self.assertRaises(host.GateError):
            agent.storyboard_check(self.w,self.page["page_id"])
        board,_=sf.write_storyboard(self.w,self.plan,self.source,self.page,
                                  spec,self.points)
        result=agent.storyboard_check(self.w,self.page["page_id"])
        self.assertTrue(result["storyboard_reviewed"])
        path=sb.path_set(self.w,self.page["page_id"])[0]
        board["narrative"]+=" This additional case was added after approval."
        host.atomic_json(path,board)
        with self.assertRaises(host.GateError):
            agent.storyboard_check(self.w,self.page["page_id"])

    def test_seven_teaching_types_are_valid_and_html_escapes_source(self):
        for module,kind in CASES:
            spec,board=self.create(module,kind)
            errors=sb.validate_storyboard(board,self.page,self.points,spec,self.source)
            self.assertEqual(errors,[],(module,errors))
            html=renderer.render(self.page,self.points,self.draft,self.source,
                                 spec,storyboard=board)
            self.assertIn('data-lesson-contract="lesson-storyboard-v1"',html)
            self.assertIn('data-teaching-module="'+module+'"',html)
            self.assertIn('data-teaching-module="transfer-checkpoint"',html)
            self.assertIn('data-authored-fact-id=',html)
            self.assertIn('data-fact-id=',html)

    def test_unsafe_module_type_and_freeform_formula_are_rejected(self):
        spec,board=self.create("variable-lab")
        b=copy.deepcopy(board);b["scenes"][0]["props"]["formula"]="eval(user_input)"
        errors=sb.validate_storyboard(b,self.page,self.points,spec,self.source)
        self.assertTrue(any("verified named computation" in x for x in errors),errors)
        b=copy.deepcopy(board);b["scenes"][0]["module"]="execute-raw-javascript"
        self.assertTrue(any("unknown teaching component" in x
                            for x in sb.validate_storyboard(b,self.page,self.points,spec,self.source)))

    def test_decision_requires_true_branches_and_trace_needs_first_error(self):
        spec,board=self.create("decision-explorer")
        board["scenes"][0]["props"]["nodes"][0]["options"][0]["to"]="unknown"
        self.assertTrue(any("unknown node" in x or "unreachable" in x
                            for x in sb.validate_storyboard(board,self.page,self.points,spec,self.source)))
        spec,board=self.create("trace-debugger",kind="failure_case")
        for step in board["scenes"][0]["props"]["steps"]:step["first_error"]=False
        self.assertTrue(any("first error" in x for x in
                        sb.validate_storyboard(board,self.page,self.points,spec,self.source)))

    def test_missing_required_fact_and_transfer_question_are_blocked(self):
        spec,board=self.create("causal-flow")
        board["scenes"][0]["fact_ids"]=[]
        board["scenes"][1]["fact_ids"]=[]
        self.assertTrue(any("source-fact" in x or "source-fact coverage" in x for x in
                            sb.validate_storyboard(board,self.page,self.points,spec,self.source)))
        spec,board=self.create("causal-flow")
        board["scenes"][-1]["props"]["question"]="Give me the chapter title."
        self.assertTrue(any("Transfer" in x or "transfer" in x for x in
                            sb.validate_storyboard(board,self.page,self.points,spec,self.source)))

    def test_fully_reviewed_design_does_not_imply_approved_actual_render(self):
        spec,board=self.create()
        with self.assertRaises(host.GateError):
            agent.render_review_check(self.w,self.page["page_id"])

if __name__=="__main__":unittest.main()
