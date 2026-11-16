"""Prevent accidental reintroduction of a second model API into Study."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
RUNTIME=ROOT/'runtime'

class NoStandaloneProviderTests(unittest.TestCase):
    def test_current_runtime_has_no_model_api_configuration(self):
        forbidden=['STUDY'+'_API_BASE','STUDY'+'_API_KEY','STUDY'+'_MODEL','STUDY'+'_REVIEW_MODEL']
        files=[ROOT/'SKILL.md',ROOT/'references'/'v6-agent-runtime.md',
               RUNTIME/'README.md',RUNTIME/'study_runtime.py',
               RUNTIME/'v6_agent.py',RUNTIME/'v6_ops.py']
        for file in files:
            content=file.read_text(encoding='utf-8')
            for term in forbidden:
                self.assertNotIn(term,content,str(file))
    def test_no_llm_client_function_or_network_model_adapter(self):
        for filename in ('study_runtime.py','v6_agent.py','v6_ops.py'):
            text=(RUNTIME/filename).read_text(encoding='utf-8')
            self.assertNotIn('def llm(',text,filename)
            self.assertNotIn('v5.llm(',text,filename)
            self.assertNotIn('chat/completions',text,filename)
    def test_skill_declares_current_host_as_model(self):
        skill=(ROOT/'SKILL.md').read_text(encoding='utf-8')
        self.assertIn('Codex/DSH agent',skill)
        self.assertIn('version: "6.2"',skill)
        self.assertIn('independently approved',skill)
if __name__=='__main__':unittest.main()
