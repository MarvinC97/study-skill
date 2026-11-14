import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/'study_runtime.py'
spec=importlib.util.spec_from_file_location('study_v5',SCRIPT)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class ContractTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.w=Path(self.t.name)
        self.src=m.ingest(self.w,Path(__file__).resolve().parents[1]/'fixtures'/'training-mini.md')
    def tearDown(self):self.t.cleanup()
    def plan(self):
        pts=[]
        for i,s in enumerate(self.src['segments'],1):
            pts.append({'lp_id':f'LP{i:04}','title':s['heading'],'goal':'解释原理','source_span_ids':[s['id']],
                        'required_facts':[{'id':f'F{i:04}-01','text':s['text'],'span_id':s['id']}]})
        pages=[{'page_id':f'P{i:03}','title':p['title'],'lp_ids':[p['lp_id']]} for i,p in enumerate(pts,1)]
        return {'source_sha256':self.src['source_sha256'],'mode':'study-d','points':pts,'pages':pages}
    def test_complete_atomic_plan_passes(self):
        m.atomic_json(self.w/'plan.json',self.plan());self.assertEqual(m.validate_plan(self.w)['status'],'pass')
    def test_seven_pages_overpacked_plan_rejected(self):
        p=self.plan();p['pages']=[{'page_id':'P001','title':'Too broad','lp_ids':[x['lp_id'] for x in p['points']]}]
        m.atomic_json(self.w/'plan.json',p);report=m.validate_plan(self.w)
        self.assertEqual(report['status'],'fail');self.assertTrue(any('more than 2' in x or 'deep page merges' in x for x in report['issues']))

    def test_lp_swallowing_large_span_group_is_rejected(self):
        p=self.plan()
        if len(p['points'])<2:self.skipTest('need multiple source spans')
        bad=p['points'][0]
        bad['source_span_ids']=[x['id'] for x in self.src['segments']]
        p['points']=[bad]
        p['pages']=[{'page_id':'P001','title':'everything','lp_ids':[bad['lp_id']]}]
        m.atomic_json(self.w/'plan.json',p)
        rep=m.validate_plan(self.w)
        self.assertEqual(rep['status'],'fail')
        self.assertTrue(any('headings' in x or '1800' in x for x in rep['issues']))

    def test_missing_source_span_rejected(self):
        p=self.plan();p['points']=p['points'][:-1];p['pages']=p['pages'][:-1];m.atomic_json(self.w/'plan.json',p)
        self.assertIn('unmapped source',str(m.validate_plan(self.w)['issues']))
    def test_missing_content_fact_rejected(self):
        p=self.plan()['points'][0]
        obj={'title':'x','intro':'intro','sections':[{'heading':'a','text':'Long useful explanatory text.'}]*3,
             'mini_questions':[{'question':'why','answer':'because'}],
             'checkpoint':{'question':'what','options':['a','b','c'],'correct_index':0,'feedback':'explain'},'represented_fact_ids':[]}
        self.assertTrue(any('missing fact IDs' in x for x in m.validate_content_data([p],obj)))
    def test_unsigned_planner_review_blocks_freeze(self):
        m.atomic_json(self.w/'plan.json',self.plan())
        with self.assertRaises(m.GateError):m.freeze(self.w)
    def test_publish_blocks_without_reviewer(self):
        with self.assertRaises(m.GateError):m.publish(self.w)
    def test_mastery_click_never_counts(self):
        record={'kind':'understood','lp_id':'LP0001','evidence_id':'click-1'}
        f=self.w/'e.json';m.atomic_json(f,record)
        with self.assertRaises(m.GateError):m.record_evidence(self.w,f)
        self.assertEqual(m.state(self.w)['learner_evidence'],{})

class DemoTests(unittest.TestCase):
    def test_demo_content_browser_and_single_file_consolidation(self):
        with tempfile.TemporaryDirectory() as directory:
            w=Path(directory);result=m.demo(w)
            self.assertTrue(result['browser']['passed'])
            c=m.consolidate(w)
            s=Path(c['file']).read_text(encoding='utf-8')
            self.assertIn('标准答案',s)
            self.assertNotIn('<script',s)
            self.assertIn('data-fact-id',s)
            self.assertGreaterEqual(result['pages'],2)
            # Mutate one rendered core fact: the contract must fail.
            manifest=m.read_json(w/'content-manifest.json')
            page_file=w/'draft-pages'/manifest['pages'][0]['file']
            original=page_file.read_text(encoding='utf-8')
            fact=m.read_json(w/'frozen-plan.json')['points'][0]['required_facts'][0]['text']
            self.assertIn(m.esc(fact),original)
            page_file.write_text(original.replace(m.esc(fact),'REMOVED FACT'),encoding='utf-8')
            self.assertEqual(m.content_static_check(w)['status'],'fail')
if __name__=='__main__':unittest.main()
