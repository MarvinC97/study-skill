import tempfile,unittest,sys,json
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parents[1]))
import study_runtime as v5
from v6_agent import Manager

class AgentHostTests(unittest.TestCase):
 def test_host_denies_unauthorized_action(self):
  with tempfile.TemporaryDirectory() as td:
   mgr=Manager(td,source='fake.md',policy='fixture')
   self.assertEqual(mgr.allow(),['read_source'])
   with self.assertRaises(v5.GateError):mgr.act({'action':'publish','args':{}})
 def test_manager_converts_overview_only_and_persists(self):
  with tempfile.TemporaryDirectory() as td:
   v5.demo(td)
   p=Path(td)/'overview.html'
   if p.exists():p.unlink()
   mgr=Manager(td,mode='study',policy='fixture',max_steps=5)
   out=mgr.run()
   self.assertEqual(out['status'],'overview_ready')
   self.assertTrue(p.exists());self.assertEqual(len(mgr.st['steps']),1)
   self.assertTrue((Path(td)/'v6-manager.json').exists())
 def test_targeted_repair_preserves_unaffected_draft(self):
  with tempfile.TemporaryDirectory() as td:
   v5.demo(td)
   w=Path(td)
   plan=v5.read_json(w/'plan.json'); self.assertGreaterEqual(len(plan['pages']),2)
   bad=plan['pages'][1]['page_id']; good=plan['pages'][0]['page_id']
   untouched=(w/'drafts'/f'{good}.json').read_bytes()
   review={'approved':False,'pages':[{'page_id':p['page_id'],'approved':p['page_id']!=bad,'issues':['missing required explanation'] if p['page_id']==bad else []} for p in plan['pages']],'fixture_only':True}
   v5.atomic_json(w/'reviews/content-review.json',review)
   mgr=Manager(td,mode='study-d',policy='fixture')
   self.assertIn('repair_page',mgr.allow())
   result=mgr.act({'action':'repair_page','args':{'page_id':bad}})
   self.assertEqual(result['targeted_repair'],bad)
   self.assertTrue((w/'drafts'/f'{good}.json').exists())
   self.assertEqual((w/'drafts'/f'{good}.json').read_bytes(),untouched)
   self.assertFalse((w/'drafts'/f'{bad}.json').exists())
   self.assertFalse((w/'reviews/content-review.json').exists())
 def test_live_manager_decides_from_snapshot(self):
  with tempfile.TemporaryDirectory() as td:
   mgr=Manager(td,source='fake.md',policy='live')
   with patch.object(v5,'llm',return_value={'action':'read_source','args':{},'reason':'source missing'}) as llm:
    decision=mgr.decide()
   self.assertEqual(decision['action'],'read_source')
   self.assertTrue(llm.called)
if __name__=='__main__':unittest.main()

class SourceScopeTests(unittest.TestCase):
 def test_exact_topic_section_scoped_and_hash_anchored(self):
  from v6_agent import ingest_topic_scope
  with tempfile.TemporaryDirectory() as td:
   src=Path(td)/'original.md'
   src.write_text('# Book\n\n## First\n'+'first text. '*30+'\n## Second\n'+'second scope content. '*30+'\n## Third\n'+'third. '*30,encoding='utf-8')
   w=Path(td)/'work'
   result=ingest_topic_scope(w,src,'Second')
   scope=v5.read_json(w/'source-scope.json')
   self.assertTrue(scope['scope_is_partial']);self.assertEqual(scope['heading'],'Second')
   self.assertEqual(result['source_sha256'],scope['selected_sha256'])
   self.assertTrue('second scope content' in (w/'source.txt').read_text(encoding='utf-8'))
   self.assertFalse('third. ' in (w/'source.txt').read_text(encoding='utf-8'))
