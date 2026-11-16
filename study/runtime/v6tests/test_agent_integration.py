"""Host-written standard Unit integration: no standalone model client."""
from pathlib import Path
import os,sys,tempfile,unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parents[1]))
import study_runtime as host
import v6_agent as agent
import v6_ops
import v61_learner as learners
import quality_fixture as qf

class HostOpsIntegration(unittest.TestCase):
 def test_standard_unit_and_profile_use_host_artifacts(self):
  with tempfile.TemporaryDirectory() as td,patch.dict(os.environ,{},clear=True):
   root=Path(td);w=root/'course'
   agent.bind(w,'Marvin',root/'Study',course_id='book-chapter-8',
     scope='Chapter 8',source=str(root/'book.md'))
   source=root/'source.md';source.write_text('# Topic\nA fact about training and its condition.\n',encoding='utf-8')
   host.ingest(w,source);src=host.read_json(w/'source.json')
   points=[]
   for i,span in enumerate(src['segments'],1):
    points.append({'lp_id':f'LP{i:04d}','title':'Training',
     'goal':'Explain the actual mechanism','source_span_ids':[span['id']],
     'required_facts':[{'id':f'F{i:04d}','text':span['text'],'span_id':span['id']}],
     'prerequisites':[]})
   plan={'source_sha256':src['source_sha256'],'mode':'study','points':points,
         'pages':[{'page_id':'U001','title':'Training Unit',
          'lp_ids':[p['lp_id'] for p in points]}]}
   host.atomic_json(w/'plan.json',plan)
   self.assertEqual(agent.plan_check(w)['status'],'pass')
   review={'review_mode':'isolated_host_agent','reviewer_context_id':'R','writer_context_id':'W',
    'source_sha256':src['source_sha256'],'plan_sha256':agent.digest(plan),
    'checked_span_ids':[x['id'] for x in src['segments']],'approved':True,'issues':[]}
   revfile=w/'input-review.json';host.atomic_json(revfile,review)
   agent.accept_plan_review(w,revfile)
   self.assertTrue(Path(agent.overview(w)['overview_file']).exists())
   learners.update_intake(w,goal='Learn training')
   learners.update_intake(w,map_reviewed=True)
   learners.update_intake(w,familiarity='Beginner')
   draft=qf.draft(points[0],"Training Unit")
   host.atomic_json(w/'drafts'/'U001.json',draft)
   artifact={'points':points,'draft':draft}
   receipt={'review_mode':'isolated_host_agent','reviewer_context_id':'R2','writer_context_id':'W2',
       'artifact_sha256':agent.digest(draft),'checked_fact_ids':draft['represented_fact_ids'],
       'approved':True,'issues':[]}
   host.atomic_json(w/'reviews'/'U001-unit-review.json',receipt)
   with patch.object(v6_ops,'browser_check',return_value={'passed':True}):
    prepared=v6_ops.next_unit(w)
   self.assertTrue(prepared['awaiting_confirmation'])
   self.assertEqual(host.state(w)['current_unit'],0)
   out=v6_ops.confirm_unit_delivery(w,prepared['file'])
   self.assertEqual(out['unit'],1)
   self.assertEqual(host.state(w)['current_unit'],1)
if __name__=='__main__':unittest.main()
