"""Offline identity/failure-boundary regressions. No live model requests."""
import contextlib
import copy
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from cell_signaling import run_local_assessment as cli
from cell_signaling.local_ollama import LocalOllama, LocalAIError, MODEL
from cell_signaling.assessment_demo import load_cases, fixture_challenge

class Transport:
    def __init__(self):
        self.case = next(c for c in load_cases() if c['name']=='limited_scope')
        self.chats=0; self.preflights=0; self.bad=None; self.postrun_bad=False
        self.model=MODEL; self.role='assistant'
    def __call__(self,path,payload=None):
        if self.bad and path==self.bad[0]: return copy.deepcopy(self.bad[1])
        if path=='/api/tags':
            self.preflights+=1
            if self.postrun_bad and self.preflights==2: return {'models':[None]}
            return {'models':[{'name':MODEL,'digest':'synthetic-digest'}]}
        if path=='/api/show': return {}
        if path=='/api/version': return {'version':'mock'}
        self.chats+=1
        packet=self.case['packet']; proposal=self.case['reference_proposal']
        answer=proposal if self.chats==1 else fixture_challenge(packet,proposal,'')
        return {'model':self.model,'done':True,'done_reason':'stop','prompt_eval_count':2000,'eval_count':500,
                'message':{'role':self.role,'content':json.dumps(answer)}}

class ProtocolIdentityTests(unittest.TestCase):
    def test_wrong_response_model_rejected_and_observed_model_retained(self):
        transport=Transport(); adapter=LocalOllama(transport);adapter.preflight();transport.model='different:8b'
        with self.assertRaisesRegex(LocalAIError,'Response model'): adapter.assess(transport.case['packet'],'',{})
        self.assertEqual(adapter.calls[-1]['telemetry']['model'],'different:8b')
        self.assertEqual(adapter.calls[-1]['status'],'failed')
    def test_wrong_response_role_rejected_and_observed_role_retained(self):
        transport=Transport(); adapter=LocalOllama(transport);adapter.preflight();transport.role='user'
        with self.assertRaisesRegex(LocalAIError,'response role'): adapter.assess(transport.case['packet'],'',{})
        self.assertEqual(adapter.calls[-1]['response_role'],'user')
        self.assertEqual(adapter.calls[-1]['status'],'failed')
    def test_malformed_preflight_is_typed_failure_not_attribute_error(self):
        for path,value in [('/api/tags',None),('/api/tags',{'models':None}),('/api/tags',{'models':[None]}),
                           ('/api/tags',{'models':[{'name':MODEL,'digest':123}]}),('/api/show',None),
                           ('/api/version',None),('/api/version',{'version':False})]:
            with self.subTest(path=path,value=value):
                transport=Transport();transport.bad=(path,value);adapter=LocalOllama(transport)
                with self.assertRaises(LocalAIError):adapter.preflight()
                self.assertFalse(adapter.ready);self.assertEqual(transport.chats,0)
    def test_postrun_preflight_failure_saves_failed_record_and_reports_path(self):
        transport=Transport();transport.postrun_bad=True;adapter=LocalOllama(transport)
        self._cli_check(adapter,True)
    def test_initial_preflight_failure_saves_diagnostic_and_reports_path(self):
        transport=Transport();transport.bad=('/api/show',None);adapter=LocalOllama(transport)
        self._cli_check(adapter,False)
    def _cli_check(self,adapter,postrun):
        output=io.StringIO();original_save=cli.save_run
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(cli,'LocalOllama',return_value=adapter),patch.object(cli,'save_run',side_effect=lambda record:original_save(record,Path(directory))),patch.object(sys,'argv',['probe','--run']),contextlib.redirect_stdout(output):
                result=cli.main()
            paths=list(Path(directory).glob('assessment-*.json'));self.assertEqual(len(paths),1)
            record=json.loads(paths[0].read_text())
        self.assertEqual(result,1);self.assertEqual(record['status'],'processing_failed');self.assertTrue(record['error'])
        self.assertIn('Saved:',output.getvalue())
        if postrun:
            self.assertEqual(record['result']['status'],'processing_failed');self.assertIsNone(record['result']['summary'])
            self.assertIsNotNone(record['result']['proposal'])
        else:self.assertIsNone(record['result'])
