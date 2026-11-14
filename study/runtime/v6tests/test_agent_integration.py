"""Real manager/Host loop with TEST DOUBLE model outputs; does not measure LLM quality."""
from pathlib import Path
import sys,tempfile,unittest,json,os
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parents[1]))
from v6_agent import Manager
import study_runtime as v5

class AgentIntegration(unittest.TestCase):
 def test_complete_tool_loop_with_mocked_model(self):
  stats={'manager_decisions':0,'planner':0,'tutor':0,'plan_review':0,'content_review':0}
  def model(messages,role='writer'):
   sysmsg=messages[0]['content']
   obj=json.loads(messages[1]['content'])
   if 'autonomous study Manager Agent' in sysmsg:
    stats['manager_decisions']+=1
    return {'action':obj['allowed_actions'][0], 'args':{}, 'reason':'next action selected from current verified state'}
   if 'source-fidelity Knowledge Planner' in sysmsg:
    stats['planner']+=1
    return {'points':[{'title':'机制 '+sp['id'],'kind':'mechanism','goal':'理解当前来源机制与应用条件',
      'source_span_ids':[sp['id']],'required_facts':[{'id':'tmp1','text':sp['text'],'span_id':sp['id']}],
      'prerequisites':[]} for sp in obj['source_spans']]}
   if 'INDEPENDENT syllabus reviewer' in sysmsg:
    stats['plan_review']+=1;return {'approved':True,'issues':[]}
   if 'excellent beginner-friendly Chinese technical tutor' in sysmsg:
    stats['tutor']+=1
    ids=[f['id'] for record in obj['evidence'] for f in record['facts']]
    return {'title':obj['page']['title'],'intro':'这个示例用于检查智能体如何逐步完成来源读取、知识拆分和内容构建。',
      'sections':[{'heading':'来源与学习目标','text':'我们先核对原文片段，说明这些片段提供了什么信息，以及为什么需要保持来源证据。'},
       {'heading':'机制与信息流','text':'系统先登记来源哈希，再把每个重要的事实写成内容合同，然后按合同生成学习页面。'},
       {'heading':'实际例子与限制','text':'这里是测试替身提供的课件。可以验证脚本与质量门禁是否运行，但无法证明模型生成的课程具有教学质量。'}],
       'visual':{'kind':'flow','title':'来源到课件','relation':'证据依次传递','nodes':[{'label':'原文','meaning':'锚点和哈希'},{'label':'合同','meaning':'必需事实'},{'label':'HTML','meaning':'可见呈现'}]},
       'simulation':{'kind':'preset','title':'来源变更','states':[{'label':'未变','observation':'哈希一致','explanation':'允许使用规划'},{'label':'变更','observation':'哈希不一致','explanation':'重新核对规划'}]},
       'mini_questions':[{'question':'如何知道来源改变？','answer':'检查 SHA256。'}],
       'checkpoint':{'question':'什么能证明来源没有静默改变？','options':['页面颜色','SHA256 与源锚点','页面字数'],'correct_index':1,'feedback':'检查哈希和锚点。'},
       'represented_fact_ids':ids}
   if 'independent technical and pedagogical reviewer' in sysmsg:
    stats['content_review']+=1
    ids=[f['id'] for p in obj['points'] for f in p['required_facts']]
    return {'approved':True,'issues':[],'checked_fact_ids':ids}
   raise AssertionError('unexpected system prompt: '+sysmsg[:110])
  with tempfile.TemporaryDirectory() as td:
   source=Path(__file__).parents[1]/'fixtures'/'training-mini.md'
   with patch.object(v5,'llm',side_effect=model), patch.dict(os.environ,{'STUDY_CHROMIUM':'/usr/bin/chromium'}):
    m=Manager(Path(td)/'run',source=str(source),mode='study-d',policy='live',max_steps=40)
    result=m.run()
    self.assertEqual(result['status'],'published',result)
    work=Path(result['workspace'])
    self.assertTrue((work/'published/index.html').exists())
    self.assertTrue((work/'delivery-queue.json').exists())
    self.assertTrue((work/'reports/browser.json').exists())
    q=v5.next_delivery(work)
    self.assertTrue(q['one_link_this_turn']);self.assertEqual(q['index'],1)
    self.assertGreater(stats['manager_decisions'],5)
    self.assertGreaterEqual(stats['planner'],1);self.assertGreaterEqual(stats['plan_review'],1)
    self.assertGreaterEqual(stats['tutor'],1);self.assertGreaterEqual(stats['content_review'],1)
    self.assertGreaterEqual(len(m.st['steps']),9)
if __name__=='__main__':unittest.main()
