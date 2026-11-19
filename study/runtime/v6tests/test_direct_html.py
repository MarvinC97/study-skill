"""Study 6.6 direct HTML: source fidelity, independent review and true delivery.

All reviewer data below is an explicitly synthetic fixture. It tests
deterministic enforcement, never the educational ability of a real model.
"""
from pathlib import Path
import sys, tempfile, unittest

sys.path.insert(0,str(Path(__file__).parents[1]))
sys.path.insert(0,str(Path(__file__).parent))
import study_runtime as host
import v6_agent as agent
import v6_ops
import direct_html as direct
from test_incremental_quality import build_workspace, new_batched_review

REASON = ("The reviewed HTML clearly explains the source-specific concept before "
          "asking a new question and follows the concrete input, observable "
          "intermediate change, result, and reason. The illustration carries "
          "the same causal relation as the visible explanation.")


def sample_page(title):
    return f"""<!doctype html><html lang="zh-CN">
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><body><main>
<h1>{title}</h1>
<p>先看一个简单的例子：一个学习者收到输入资料，识别其中的具体条件，
随后使用明确的计算或操作规则处理，最后检查输出是否满足原文要求。</p>
<div class="diagram" role="img" aria-label="证据经过处理得到结果">
<strong>原文条件</strong> → <strong>可验证的操作</strong> → <strong>输出与检查</strong></div>
<h2>为什么会得到这样的结果？</h2>
<p>由于规则依赖原文中的具体输入，改变输入会影响中间计算和最终结果。
学习时需要跟踪哪项条件被改变、它如何传播，以及原来结论在哪种边界内成立。</p>
<p>这个例子展示的是可检验的过程；模型的最终结论仍要与完整原始资料核对。</p>
<h2>检查理解</h2>
<details><summary>如果改变输入条件，结果还一样吗？</summary>
<p>需要重新应用规则；结果是否改变取决于该规则是否受这项条件影响。</p>
</details></main></body></html>"""


def approved_review(plan, source, page_id, path, fact_ids, manuscript=None):
    receipt = {"contract":direct.CONTRACT,
            "page_id":page_id,
            "source_sha256":source["source_sha256"],
            "plan_sha256":direct.hash_json(plan),
            "html_sha256":direct.sha(path.read_bytes()),
            "review_mode":"isolated_host_agent",
            "writer_context_id":"fixture-writer",
            "reviewer_context_id":"fixture-separated-reviewer",
            "approved":True,"issues":[],
            "checked_fact_ids":sorted(fact_ids),
            "checks":[{"dimension":dimension,"passed":True,"reason":REASON,
                        "reader_evidence":
                        ("由于规则依赖原文中的具体输入，改变输入会影响中间计算和最终结果"
                         if dimension in {"explanation_depth","teaching_sequence","visual_pedagogy"}
                         else "")}
                      for dimension in sorted(direct.REVIEW_DIMENSIONS)]}
    if plan.get("authoring_mode")==direct.TWO_PASS:
        if manuscript is None: raise ValueError("two-pass fixture must identify manuscript")
        receipt["lesson_sha256"]=direct.sha(manuscript.read_bytes())
    return receipt


class DirectHtmlTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.w,self.source,self.plan = build_workspace(Path(self.tmp.name))
        self.plan["render_contract"] = direct.CONTRACT
        self.plan["authoring_mode"] = direct.TWO_PASS
        host.atomic_json(self.w/"plan.json",self.plan)
        reviewfile=self.w/"review-plan-input.json"
        host.atomic_json(reviewfile,new_batched_review(self.source,self.plan))
        agent.accept_plan_review(self.w,reviewfile)
        host.approve_outline(self.w)
        agent.freeze(self.w)
        self.page=self.plan["pages"][0]
        self.page_path,self.review_path,_=direct.locations(self.w,self.page["page_id"])
        self.page_path.parent.mkdir(parents=True,exist_ok=True)
        self.page_path.write_text(sample_page("训练机制入门"),encoding="utf-8")
        self.manuscript = direct.lesson_path(self.w,self.page["page_id"])
        self.manuscript.parent.mkdir(parents=True,exist_ok=True)
        self.manuscript.write_text(
            "# 训练机制入门\\n\\n先看一个具体输入与条件，再依次解释转换、结果以及边界。\\n"
            "完整的示例讲稿先于 HTML，视觉作者负责把中间推理变得易于观察。\\n",
            encoding="utf-8")
        lookup={p["lp_id"]:p for p in self.plan["points"]}
        self.facts={fact["id"] for pid in self.page["lp_ids"]
                    for fact in lookup[pid]["required_facts"]}

    def approve_page(self):
        direct.save(self.review_path,approved_review(
          self.plan,self.source,self.page["page_id"],self.page_path,self.facts,
          manuscript=self.manuscript))

    def test_missing_review_is_not_published(self):
        with self.assertRaises(direct.DirectPageError) as ctx:
            direct.prepare_standard(self.w,self.plan,self.source,self.page)
        self.assertIn("REVIEW_PENDING",str(ctx.exception))
        self.assertFalse((self.w/"published"/(self.page["page_id"]+".html")).exists())

    def test_review_rejected_for_missing_fact_or_stale_html(self):
        self.approve_page()
        review=direct.read(self.review_path)
        review["checked_fact_ids"] = []
        direct.save(self.review_path,review)
        with self.assertRaises(direct.DirectPageError):
            direct.validate_review(self.w,self.plan,self.source,self.page["page_id"])
        self.approve_page()
        self.page_path.write_text(sample_page("修改后的标题"),encoding="utf-8")
        with self.assertRaises(direct.DirectPageError) as ctx:
            direct.validate_review(self.w,self.plan,self.source,self.page["page_id"])
        self.assertIn("html_sha256",str(ctx.exception))

    def test_two_pass_manuscript_is_required_and_hash_bound(self):
        self.approve_page()
        self.manuscript.unlink()
        with self.assertRaises(direct.DirectPageError) as ctx:
            direct.validate_review(self.w,self.plan,self.source,self.page["page_id"])
        self.assertIn("manuscript missing",str(ctx.exception))
        self.manuscript.write_text("# Updated manuscript\\nExact new content",encoding="utf-8")
        with self.assertRaises(direct.DirectPageError) as ctx:
            direct.validate_review(self.w,self.plan,self.source,self.page["page_id"])
        self.assertIn("lesson_sha256",str(ctx.exception))
        self.approve_page()
        page,receipt=direct.validate_review(self.w,self.plan,self.source,self.page["page_id"])
        self.assertTrue(page.is_file())
        self.assertEqual(receipt["lesson_sha256"],direct.sha(self.manuscript.read_bytes()))

    def test_historical_direct_html_is_still_accepted(self):
        self.plan.pop("authoring_mode",None)
        self.manuscript.unlink()
        self.approve_page()
        page,receipt=direct.validate_review(
            self.w,self.plan,self.source,self.page["page_id"])
        self.assertTrue(page.is_file())
        self.assertNotIn("lesson_sha256",receipt)

    def test_generic_or_hidden_review_evidence_is_rejected(self):
        self.approve_page()
        review=direct.read(self.review_path)
        for check in review["checks"]:
            if check["dimension"]=="explanation_depth":
                check.pop("reader_evidence")
        direct.save(self.review_path,review)
        with self.assertRaises(direct.DirectPageError) as ctx:
            direct.validate_review(self.w,self.plan,self.source,self.page["page_id"])
        self.assertIn("reader-visible",str(ctx.exception))
        self.approve_page()
        review=direct.read(self.review_path)
        for check in review["checks"]:
            if check["dimension"]=="teaching_sequence":
                # This question is only inside a collapsed answer and cannot
                # substitute for a visible teaching step.
                check["reader_evidence"]="如果改变输入条件，结果还一样吗？"
        direct.save(self.review_path,review)
        with self.assertRaises(direct.DirectPageError) as ctx:
            direct.validate_review(self.w,self.plan,self.source,self.page["page_id"])
        self.assertIn("reader-visible",str(ctx.exception))

    def test_source_review_requires_specific_visible_passage(self):
        self.approve_page()
        page,receipt=direct.validate_review(
            self.w,self.plan,self.source,self.page["page_id"])
        self.assertTrue(page.is_file())
        dimensions={x["dimension"] for x in receipt["checks"]
                    if x.get("reader_evidence")}
        self.assertEqual(dimensions,
                         {"explanation_depth","teaching_sequence","visual_pedagogy"})

    def test_visible_explanation_before_optional_disclosure(self):
        self.page_path.write_text("""<!doctype html><html><meta name="viewport" content="width=device-width,initial-scale=1">
        <body><main><details><summary>读完再答</summary>
        <p>所有重要解释都被放进折叠区域，这样首次阅读者很难理解这个机制。</p>
        </details><h1>标题</h1><p>请猜一猜下面会发生什么事情。</p></main></body></html>""",encoding="utf-8")
        issues=direct.inspect_html(self.page_path)
        self.assertTrue(any("concealed" in x or "visible" in x for x in issues),issues)

    def test_direct_deep_staging_preserves_delivery_cursor(self):
        self.approve_page()
        first=agent.stage_next_page(self.w)
        self.assertEqual(first["page_id"],self.page["page_id"])
        self.assertTrue(first["reviewed"])
        self.assertTrue(first["browser_pass"])
        with self.assertRaises(host.GateError):
            agent.stage_next_page(self.w)
        idx=host.next_delivery(self.w)
        self.assertEqual(Path(idx["file"]).name,"index.html")
        host.confirm_delivery(self.w,idx["file"])
        content=host.next_delivery(self.w)
        self.assertEqual(Path(content["file"]).name,self.page["page_id"]+".html")
        host.confirm_delivery(self.w,content["file"])
        next_page=self.plan["pages"][1]
        p2,r2,_=direct.locations(self.w,next_page["page_id"])
        p2.parent.mkdir(parents=True,exist_ok=True)
        p2.write_text(sample_page("下一个知识点"),encoding="utf-8")
        manuscript2=direct.lesson_path(self.w,next_page["page_id"])
        manuscript2.parent.mkdir(parents=True,exist_ok=True)
        manuscript2.write_text("# 下一页讲稿\\n\\n来源、机制、例子与边界已解释。",encoding="utf-8")
        lookup={p["lp_id"]:p for p in self.plan["points"]}
        facts={f["id"] for pid in next_page["lp_ids"] for f in lookup[pid]["required_facts"]}
        direct.save(r2,approved_review(self.plan,self.source,next_page["page_id"],p2,facts,
                                       manuscript=manuscript2))
        second=agent.stage_next_page(self.w)
        self.assertEqual(second["page_id"],next_page["page_id"])
        self.assertEqual(second["pages_staged"],2)

    def test_standard_unit_delivery_only_advances_on_confirmation(self):
        # Use an independent ordinary Study workspace to validate the same HTML.
        self.plan["mode"]="study"
        self.plan["pages"]=[{"page_id":p["page_id"],"title":p["title"],
                             "lp_ids":p["lp_ids"],"learning_objective":p["learning_objective"],
                             "grouping_rationale":p["grouping_rationale"],
                             "grouping_relation":"causal_chain",
                             "shared_case":"The learner follows one concrete input through a source-backed action and checks its result."}
                             for p in self.plan["pages"]]
        host.atomic_json(self.w/"plan.json",self.plan)
        # Existing Study-D G2 receipt is replaced with a mode-specific plan approval.
        source_review=direct.read(self.w/"reviews"/"plan-review.json")
        source_review["plan_sha256"]=direct.hash_json(self.plan)
        host.atomic_json(self.w/"reviews"/"plan-review.json",source_review)
        self.approve_page()
        v6_ops.learners.require_ready = lambda _: None
        # The standard command requires an existing named learner binding.
        # Test through the deterministic Unit preparation boundary here.
        result=direct.prepare_standard(self.w,self.plan,self.source,self.page)
        self.assertTrue(Path(result["file"]).is_file())
        self.assertFalse((self.w/"unit-delivery-pending.json").exists())
        self.assertEqual(host.state(self.w).get("current_unit",0),0)


if __name__=="__main__":
    unittest.main()
