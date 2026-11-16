import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
import merge_into_repo as m

class RepoOverlayTest(unittest.TestCase):
    def test_preserves_v35_core_bytes_and_adds_v62_runtime(self):
        with tempfile.TemporaryDirectory() as t:
            repo=Path(t)/'repo'; repo.mkdir()
            files={'study/SKILL.md':'name: study\nold entry\n',
                'study/references/first-use.md':'V3.5 original first-use rules\n',
                'study/schemas/learner-profile.md':'V3.5 original schema\n',
                'study/scripts/study_home.py':'print("original")\n',
                'study/agents/openai.yaml':'original agent metadata\n',
                'study/assets/icon.svg':'<svg/>\n'}
            for rel,content in files.items():
                f=repo/rel; f.parent.mkdir(parents=True,exist_ok=True);f.write_text(content)
            (repo/'README.md').write_text('Old Study **V3.5**; project badge 版本-V3.5\n')
            before={rel:m.sha(repo/rel) for rel in files if rel!='study/SKILL.md'}
            _,protected,actions=m.plan(repo)
            self.assertIn('study/SKILL.md',[a['path'] for a in actions])
            self.assertNotIn('study/references/first-use.md',[a['path'] for a in actions])
            m.apply(repo,protected,actions)
            for rel,h in before.items():self.assertEqual(m.sha(repo/rel),h,rel)
            self.assertTrue((repo/'study/runtime/v6_agent.py').is_file())
            self.assertTrue((repo/'study/runtime/v61_learner.py').is_file())
            self.assertIn('V6.3', (repo/'study/SKILL.md').read_text())
            self.assertIn('V6.3', (repo/'README.md').read_text())

if __name__=='__main__':unittest.main()
