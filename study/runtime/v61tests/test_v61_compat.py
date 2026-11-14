"""Actual functional V3.5 compatibility tests, stdlib only.
All tests run in temporary roots and never alter a real user profile.
"""
import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
import v61_learner as u

class V61Compatibility(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'Study'
        self.ws=Path(self.tmp.name)/'work'/'chapter8'
        self.ws.mkdir(parents=True)
        self.profile=u.initialize_profile('Marvin',self.root)['path']
        self.bind=u.bind_workspace(self.ws,'Marvin',self.root,scope='chapter8',source='chapter8.md')
        self.course_file=Path(self.bind['course_state_path'])
        self.plan={'source_sha256':'123abc','mode':'study',
            'points':[{'lp_id':'lp-001','title':'Pre-training','goal':'explain stages', 'source_span_ids':['span-a'], 'prerequisites':[]},
                      {'lp_id':'lp-002','title':'Next Token Prediction','goal':'explain token loss','source_span_ids':['span-b'],'prerequisites':['lp-001']}],
            'pages':[{'page_id':'U01','title':'Four stages','lp_ids':['lp-001']},
                     {'page_id':'U02','title':'Next Token Prediction','lp_ids':['lp-002']} ]}
        u.atomic(self.ws/'plan.json',self.plan)
        u.atomic(self.ws/'source.json',{'source_sha256':'123abc','origin':'chapter8.md'})
        u.atomic(self.ws/'state.json',{'version':'6.0','current_unit':0,'gates':{}})
    def test_profile_location_idempotent_and_no_overwrite(self):
        p=Path(self.profile);d=u.load(p);d['custom_legacy_field']='do not touch';u.atomic(p,d)
        u.initialize_profile('Marvin',self.root)
        self.assertEqual(u.load(p)['custom_legacy_field'],'do not touch')
        self.assertEqual(u.locate_profile('Marvin',self.root)['slug'],'marvin')
        with self.assertRaises(u.LearnerError):u.initialize_profile('../bad',self.root)
    def test_preserve_old_evidence_and_unknown_fields(self):
        d=u.load(self.course_file);d['extra_legacy_data']={'keep':'all'}
        d['learning_points']=[{'id':'lp-001','title':'legacy','learning_status':'understood','evidence_ids':['e-old'],'assessment':{'demonstrated_criteria':['reasoning']}}]
        d['evidence']=[{'id':'e-old','lp_ids':['lp-001'],'actual_answer':'I explained why','outcome':'understood','rubric':'causality'}]
        u.atomic(self.course_file,d)
        x=u.sync_plan(self.ws);new=u.load(self.course_file)
        self.assertEqual(x['learning_points'],2)
        self.assertEqual(new['extra_legacy_data'],{'keep':'all'})
        self.assertEqual(new['learning_points'][0]['learning_status'],'understood')
        self.assertEqual(new['evidence'][0]['id'],'e-old')
        self.assertEqual(new['learning_points'][1]['learning_status'],'unassessed')
    def test_startup_order_and_goal_report_is_not_mastery(self):
        u.sync_plan(self.ws)
        with self.assertRaises(u.LearnerError):u.require_ready(self.ws)
        u.update_intake(self.ws,goal='Understand model training')
        with self.assertRaises(u.LearnerError):u.update_intake(self.ws,familiarity='New to RL')
        (self.ws/'overview.html').write_text('<h1>map</h1>',encoding='utf-8')
        u.update_intake(self.ws,map_reviewed=True)
        done=u.update_intake(self.ws,familiarity='Python familiar; RL first exposure')
        self.assertTrue(done['finalized']); self.assertTrue(u.require_ready(self.ws))
        lp=u.course(self.ws)['learning_points']
        self.assertTrue(all(x['learning_status']=='unassessed' for x in lp))
        profile=u.load(self.profile)
        self.assertEqual(profile['goals'][-1]['statement'],'Understand model training')
    def test_resume_unit_cursor_without_mastery(self):
        u.sync_plan(self.ws)
        page=self.ws/'01.html';page.write_text('<html>Content</html>',encoding='utf-8')
        marked=u.mark_unit_delivered(self.ws,1,page)
        self.assertFalse(marked['mastery_changed']);self.assertEqual(marked['cursor'],1)
        self.assertTrue(all(p['learning_status']=='unassessed' for p in u.course(self.ws)['learning_points']))
        u.atomic(self.ws/'state.json',{'version':'6.0','current_unit':0,'gates':{}})
        r=u.recover(self.ws)
        self.assertEqual(r['current_unit_index'],1)
        self.assertEqual(u.load(self.ws/'state.json')['current_unit'],1)
    def test_assessment_requires_independent_review_for_mastery(self):
        u.sync_plan(self.ws)
        first=u.record_assessment(self.ws,'lp-001','my explanation','source rubric','understood','Q1','chat-m1',assistance='hinted',reviewed=True)
        self.assertFalse(first['mastery_promoted']);self.assertEqual(first['lp_status'],'attempted')
        second=u.record_assessment(self.ws,'lp-001','new independent explanation','source rubric','understood','Q2','chat-m2',assistance='independent',reviewed=True)
        self.assertTrue(second['mastery_promoted']);self.assertEqual(second['lp_status'],'understood')
        summary=u.update_chapter_summary(self.ws,chapter_id='ch08')
        self.assertTrue(summary['profile_updated'])
        self.assertEqual(u.load(self.profile)['courses'][0]['chapter_summary']['lp_status_counts']['understood'],1)
        self.assertEqual(len(u.course(self.ws)['evidence']),2)
    def test_recover_detects_source_changes(self):
        u.sync_plan(self.ws)
        u.atomic(self.ws/'source.json',{'source_sha256':'changed'})
        state=u.recover(self.ws)
        self.assertTrue(state['requires_new_plan'])
    def test_deep_branch_keeps_main_cursor(self):
        u.sync_plan(self.ws)
        deep=self.ws/'deep'/'kv';deep.mkdir(parents=True)
        b=u.deep_branch(self.ws,deep,'KV Cache',return_unit=1,next_page=2)
        self.assertEqual(b['main_return'],1)
        self.assertEqual(u.course(self.ws)['navigation']['current_unit_index'],0)
    def test_second_learner_cannot_steal_workspace(self):
        with self.assertRaises(u.LearnerError):u.bind_workspace(self.ws,'Other',self.root)
    def test_explicit_temporary_without_user_profile(self):
        w=Path(self.tmp.name)/'temporary'
        b=u.bind_workspace(w,'',self.root,temporary=True)
        self.assertTrue(b['temporary']);self.assertTrue(u.require_ready(w))

if __name__=='__main__':unittest.main()
