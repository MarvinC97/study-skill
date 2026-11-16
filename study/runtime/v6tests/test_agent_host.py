"""Host-native control and quality-gate tests; no model API or credentials."""
from pathlib import Path
import json,os,tempfile,unittest,sys
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parents[1]))
import study_runtime as v5
import v6_agent as agent
import v6_ops
import v61_learner as learners

class HostNativeTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup)
  self.w=Path(self.t.name)/'course';self.w.mkdir()
  self.src=Path(__file__).parents[1]/'fixtures'/'training-mini.md'
  v5.ingest(self.w,self.src)
  src=v5.read_json(self.w/'source.json')
  self.points=[{'lp_id':f'LP{i:04d}','title':f"Mechanism {i}",
      'goal':'Explain one source-grounded mechanism','source_span_ids':[s['id']],
      'required_facts':[{'id':f'F{i:04d}-01','text':s['text'],'span_id':s['id']}],
      'prerequisites':[]} for i,s in enumerate(src['segments'],1)]
  self.plan={'source_sha256':src['source_sha256'],'points':self.points,
      'pages':[{'page_id':f'P{i:03d}','lp_ids':[p['lp_id']],'title':p['title']}
               for i,p in enumerate(self.points,1)],'mode':'study-d'}
  v5.atomic_json(self.w/'plan.json',self.plan)
  self.reviewdir=self.w/'reviews';self.reviewdir.mkdir()
  self.reader=src

 def plan_review(self):
  return {'review_mode':'isolated_host_agent','reviewer_context_id':'reviewer-A',
          'writer_context_id':'writer-B','approved':True,'issues':[],
          'checked_span_ids':[s['id'] for s in self.reader['segments']],
          'plan_sha256':agent.digest(self.plan),'source_sha256':self.reader['source_sha256']}

 def prepare_plan(self):
  r=self.w/'review.json';v5.atomic_json(r,self.plan_review())
  return agent.accept_plan_review(self.w,r)

 def write_drafts(self):
  for pg in self.plan['pages']:
   pid=pg['page_id']
   p=next(x for x in self.points if x['lp_id']==pg['lp_ids'][0])
   draft={'title':pg['title'],'intro':'Learn to explain a verified source mechanism.',
     'sections':[
       {'heading':'Why','text':'This topic follows from the original source and its factual conditions.'},
       {'heading':'How','text':'Inputs and steps determine a result, with explicit checks for each factual requirement.'},
       {'heading':'Example','text':'The source example demonstrates the mechanism under its stated conditions.'}
     ],
     'mini_questions':[{'question':'Which fact grounds this?','answer':'The cited source span.'}],
     'checkpoint':{'question':'Which supports the lesson?','options':['color','source','spacing'],
                   'correct_index':1,'feedback':'Use the source evidence.'},
     'represented_fact_ids':[p['required_facts'][0]['id']]}
   v5.atomic_json(self.w/'drafts'/(pid+'.json'),draft)

 def content_review(self):
  pages=[]
  for p in self.plan['pages']:
   pid=p['page_id'];draft=v5.read_json(self.w/'drafts'/(pid+'.json'))
   facts=[f['id'] for point in self.points if point['lp_id'] in p['lp_ids'] for f in point['required_facts']]
   pages.append({'page_id':pid,'approved':True,'issues':[],
                 'checked_fact_ids':facts,'draft_sha256':agent.digest(draft)})
  return {'review_mode':'isolated_host_agent','writer_context_id':'writer-A',
          'reviewer_context_id':'reviewer-C','source_sha256':self.reader['source_sha256'],
          'plan_sha256':agent.digest(self.plan),'pages':pages}

 def test_host_native_full_pipeline_without_provider_env(self):
  with patch.dict(os.environ,{},clear=True):
   self.assertEqual(agent.plan_check(self.w)['status'],'pass')
   self.assertTrue(self.prepare_plan()['reviewed'])
   v5.freeze(self.w)
   self.write_drafts()
   v5.atomic_json(self.w/'content-review-input.json',self.content_review())
   agent.accept_content_review(self.w,self.w/'content-review-input.json')
   self.assertGreater(len(agent.render(self.w)),0)
   report=v5.content_static_check(self.w)
   self.assertEqual(report['status'],'pass')
   def fake_browser(ws):
    result={'passed':True,'browser_executed':True,'pages_tested':len(self.plan['pages']),'issues':[]}
    v5.atomic_json(Path(ws)/'reports'/'browser.json',result)
    return result
   with patch.object(v5,'browser_qa',side_effect=fake_browser):
    gates=agent.verify(self.w)
   self.assertTrue(gates['G5_BROWSER']['ok'])
   self.assertTrue((self.w/'draft-pages'/'index.html').exists())
   published=agent.publish(self.w)
   self.assertTrue(Path(published['published_dir']).is_dir())
   pending=v5.next_delivery(self.w)
   self.assertTrue(pending['awaiting_confirmation'])
   self.assertEqual(v5.read_json(self.w/'delivery-queue.json')['cursor'],0)
   receipt=agent.confirm_delivery(self.w,pending['file'])
   self.assertTrue(receipt['confirmed'])
   self.assertEqual(receipt['index'],1)

 def test_no_self_review_can_pass(self):
  bad=self.plan_review()
  bad['review_mode']='self_review'
  reviewfile=self.w/'bad-review.json';v5.atomic_json(reviewfile,bad)
  with self.assertRaises(v5.GateError):agent.accept_plan_review(self.w,reviewfile)
  bad=self.plan_review();bad['reviewer_context_id']=bad['writer_context_id']
  v5.atomic_json(reviewfile,bad)
  with self.assertRaises(v5.GateError):agent.accept_plan_review(self.w,reviewfile)

 def test_fact_coverage_and_hash_drift_block(self):
  self.prepare_plan();v5.freeze(self.w);self.write_drafts()
  review=self.content_review();review['pages'][0]['checked_fact_ids']=[]
  inp=self.w/'content-review.json';v5.atomic_json(inp,review)
  with self.assertRaises(v5.GateError):agent.accept_content_review(self.w,inp)
  review=self.content_review();v5.atomic_json(inp,review)
  agent.accept_content_review(self.w,inp)
  altered=self.w/'drafts'/(self.plan['pages'][0]['page_id']+'.json')
  data=v5.read_json(altered);data['intro']='changed after review';v5.atomic_json(altered,data)
  with self.assertRaises(v5.GateError):agent.check_review_integrity(self.w)

if __name__=="__main__":unittest.main()
