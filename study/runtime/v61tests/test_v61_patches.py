"""Regression tests for V6.1 Study-D resume, delivery handshakes and quiz evidence."""
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).parents[1]))
import study_runtime as v5
import v61_learner as learners
import v6_ops
import v6_agent


class V61PatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.ws=self.root/'course'
        self.ws.mkdir()
        self.profile_root=self.root/'Study'
        self.binding=learners.bind_workspace(self.ws,'Marvin',self.profile_root,
                                             course_id='chapter8',scope='Chapter 8')
        self.plan={'mode':'study','source_sha256':'abc',
            'points':[{'lp_id':'LP1','title':'Training','goal':'reason about training',
                       'required_facts':[{'id':'F1','text':'A necessary fact.','span_id':'S1'}],
                       'source_span_ids':['S1'],'prerequisites':[]}],
            'pages':[{'page_id':'U001','title':'Unit','lp_ids':['LP1']}]}
        v5.atomic_json(self.ws/'plan.json',self.plan)
        v5.atomic_json(self.ws/'source.json',{'source_sha256':'abc','segments':[{'id':'S1','text':'A necessary fact.'}]})
        v5.atomic_json(self.ws/'state.json',{'current_unit':0,'gates':{}})
        learners.sync_plan(self.ws)

    def test_deep_resume_is_idempotent_and_guarded(self):
        deep=self.ws/'deep'/'topic'
        deep.mkdir(parents=True)
        initial=learners.deep_branch(self.ws,deep,'Topic',return_unit=1,next_page=3)
        self.assertEqual(initial['next_page'],3)
        self.assertEqual(initial['main_return'],1)
        again=learners.deep_branch(self.ws,deep,'Topic',return_unit=99)
        self.assertEqual(again,initial)
        with self.assertRaises(learners.LearnerError):
            learners.deep_branch(self.ws,self.ws/'deep'/'other','Other')
        with self.assertRaises(learners.LearnerError):
            learners.deep_branch(self.ws,self.ws,'Not a branch')

    def test_deep_page_pending_duplicate_and_confirm(self):
        deep=self.ws/'deep'/'topic'
        published=deep/'published'
        published.mkdir(parents=True)
        (published/'index.html').write_text('<h1>Index</h1>',encoding='utf-8')
        (published/'page1.html').write_text('<h1>Page 1</h1>',encoding='utf-8')
        v5.atomic_json(deep/'delivery-queue.json',{'cursor':0,
                        'files':['index.html','page1.html'],'one_link_per_turn':True})
        one=v5.next_delivery(deep);two=v5.next_delivery(deep)
        self.assertEqual(one['file'],two['file'])
        self.assertEqual(v5.read_json(deep/'delivery-queue.json')['cursor'],0)
        with self.assertRaises(v5.GateError):
            v5.confirm_delivery(deep,published/'page1.html')
        confirmed=v5.confirm_delivery(deep,one['file'])
        self.assertEqual(confirmed['index'],1)
        duplicate=v5.confirm_delivery(deep,one['file'])
        self.assertTrue(duplicate['duplicate'])
        self.assertEqual(v5.next_delivery(deep)['index'],2)
        with self.assertRaises(v5.GateError):
            v5.confirm_delivery(deep,self.root/'wrong.html')
        (published/'page1.html').write_text('<h1>Changed</h1>',encoding='utf-8')
        with self.assertRaises(v5.GateError):v5.next_delivery(deep)

    def test_unit_progress_only_advances_after_confirmation(self):
        draft={'title':'Unit','intro':'intro','sections':[],'mini_questions':[]}
        v5.atomic_json(self.ws/'drafts'/'U001.json',draft)
        page='<html><p data-fact-id="F1">A necessary fact.</p></html>'
        with patch.object(v6_ops,'need_plan',return_value=(self.plan,v5.read_json(self.ws/'source.json'))), \
             patch.object(v5,'validate_content_data',return_value=[]), \
             patch.object(v6_ops.lessons,'verify_ready',return_value=({'checkpoint':{'question':'test'}},'fixture-design-sha')), \
             patch.object(v6_ops.lessons,'validate_draft_alignment',return_value=[]), \
             patch.object(v6_ops,'independent_review',return_value={'approved':True,'lesson_spec_sha256':'fixture-design-sha'}), \
             patch.object(v6_ops.renderer,'render',return_value=page), \
             patch.object(v6_ops,'browser_check',return_value={'passed':True}):
            prepared=v6_ops.next_unit(self.ws)
            self.assertTrue(prepared['awaiting_confirmation'])
            self.assertEqual(v5.state(self.ws)['current_unit'],0)
            self.assertEqual(learners.course(self.ws)['navigation']['current_unit_index'],0)
            self.assertTrue(v6_ops.next_unit(self.ws)['reused'])
            with self.assertRaises(v5.GateError):
                v6_ops.confirm_unit_delivery(self.ws,self.root/'other.html')
            done=v6_ops.confirm_unit_delivery(self.ws,prepared['file'])
            self.assertEqual(done['unit'],1)
            self.assertEqual(v5.state(self.ws)['current_unit'],1)
            self.assertEqual(learners.course(self.ws)['navigation']['current_unit_index'],1)
            self.assertTrue(v6_ops.confirm_unit_delivery(self.ws,prepared['file'])['duplicate'])
            self.assertTrue(v6_ops.next_unit(self.ws)['finished'])

    def test_interrupted_unit_confirmation_reconciles_from_canonical_evidence(self):
        out=self.ws/'published'/'U001.html'
        out.parent.mkdir(parents=True)
        out.write_text('<html>Unit</html>',encoding='utf-8')
        pending={'file':str(out.resolve()),'unit':1,'sha256':v5.sha(out.read_bytes()),'page_id':'U001'}
        v5.atomic_json(self.ws/'unit-delivery-pending.json',pending)
        learners.mark_unit_delivered(self.ws,1,out)
        # Simulate interruption after learner state advanced, before Host and final receipt.
        result=learners.recover(self.ws)
        self.assertEqual(result['current_unit_index'],1)
        confirmed=v6_ops.confirm_unit_delivery(self.ws,out)
        self.assertEqual(confirmed['learner_state']['recovered'],True)
        self.assertTrue((self.ws/'unit-delivery-confirmed.json').is_file())
        self.assertFalse((self.ws/'unit-delivery-pending.json').exists())
        self.assertTrue(v6_ops.confirm_unit_delivery(self.ws,out)['duplicate'])

    def _grade_file(self,exam_path,answers_path,passed=True,assistance='independent',transfer=False):
        data={'review_mode':'isolated_host_agent','reviewer_context_id':'reviewer-1',
              'writer_context_id':'writer-1','exam_sha256':v5.sha(exam_path.read_bytes()),
              'answer_sha256':v5.sha(answers_path.read_bytes()),
              'grades':[{'question_id':'Q1','passed':passed,'reason':'Source-backed grade',
                         'demonstrated_fact_ids':['F1'] if passed else [],
                         'transfer_demonstrated':transfer}]}
        p=self.root/'grade.json';v5.atomic_json(p,data);return p

    def test_quiz_submission_records_actual_reviewed_evidence_once(self):
        exam={'topic':'Training','questions':[{'id':'Q1','question':'Why?','answer':'Because it works',
            'rubric':'Explain the source-supported mechanism',
            'type':'reasoning','source_fact_ids':['F1']}]}
        (self.ws/'exams').mkdir()
        exam_file=self.ws/'exams'/'training.json'
        v5.atomic_json(exam_file,exam)
        answers=self.root/'actual-answers.json'
        v5.atomic_json(answers,{'topic':'Training','answers':[{'question_id':'Q1',
            'answer':'The mechanism follows A necessary fact.','assistance':'independent'}]})
        grade=self._grade_file(exam_file,answers)
        with patch.object(v6_ops,'need_plan',return_value=(self.plan,v5.read_json(self.ws/'source.json'))):
            first=v6_ops.submit_quiz(self.ws,'Training',answers,grade)
            self.assertEqual(first['graded'],1)
            evidence=learners.course(self.ws)['evidence']
            self.assertEqual(len(evidence),1)
            self.assertEqual(evidence[0]['actual_answer'],
                             'The mechanism follows A necessary fact.')
            self.assertEqual(learners.course(self.ws)['learning_points'][0]['learning_status'],'understood')
            v6_ops.submit_quiz(self.ws,'Training',answers,grade)
            self.assertEqual(len(learners.course(self.ws)['evidence']),1)

    def test_quiz_hinted_answers_remain_attempted(self):
        exam={'topic':'Training','questions':[{'id':'Q1','question':'Why?','answer':'x',
            'rubric':'Explain it','type':'transfer','source_fact_ids':['F1']}]}
        (self.ws/'exams').mkdir()
        exam_file=self.ws/'exams'/'training.json'
        v5.atomic_json(exam_file,exam)
        answers=self.root/'hinted.json'
        v5.atomic_json(answers,{'topic':'Training','answers':[{'question_id':'Q1',
            'answer':'copy from hint','assistance':'hinted'}]})
        grade=self._grade_file(exam_file,answers,transfer=True)
        with patch.object(v6_ops,'need_plan',return_value=(self.plan,v5.read_json(self.ws/'source.json'))):
            v6_ops.submit_quiz(self.ws,'Training',answers,grade)
        self.assertEqual(learners.course(self.ws)['learning_points'][0]['learning_status'],'attempted')

    def test_rejects_self_grader_and_missing_review(self):
        exam={'topic':'Training','questions':[{'id':'Q1','question':'Why?','answer':'x',
            'rubric':'Explain it','type':'reasoning','source_fact_ids':['F1']}]}
        (self.ws/'exams').mkdir()
        exam_file=self.ws/'exams'/'training.json'
        v5.atomic_json(exam_file,exam)
        answers=self.root/'answers.json'
        v5.atomic_json(answers,{'topic':'Training','answers':[{'question_id':'Q1','answer':'I reasoned.'}]})
        grade=self._grade_file(exam_file,answers)
        with patch.object(v6_ops,'need_plan',return_value=(self.plan,v5.read_json(self.ws/'source.json'))):
            with self.assertRaises(v5.GateError):
                v6_ops.submit_quiz(self.ws,'Training',answers,None)
            data=v5.read_json(grade);data['review_mode']='self_review';v5.atomic_json(grade,data)
            with self.assertRaises(v5.GateError):
                v6_ops.submit_quiz(self.ws,'Training',answers,grade)


if __name__=='__main__':unittest.main()
