import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from cell_signaling.assessment_contract import run_assessment, digest
from cell_signaling.assessment_demo import load_cases, fixture_challenge
from cell_signaling.local_ollama import (
    LocalOllama, LocalAIError, MODEL, OPTIONS, strict_json, NoRedirect, local_request)
from cell_signaling.run_local_assessment import save_run


class FakeTransport:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def __call__(self, path, payload=None):
        self.calls.append((path, copy.deepcopy(payload)))
        if path == '/api/tags':
            return {'models': [{'name':MODEL, 'digest':'synthetic-digest'}]}
        if path == '/api/show': return {'capabilities':['completion','thinking']}
        if path == '/api/version': return {'version':'test-only'}
        return copy.deepcopy(self.response)


def envelope(content):
    return {'model': MODEL, 'done': True, 'done_reason': 'stop',
            'prompt_eval_count': 1700, 'eval_count': 900,
            'message': {'role':'assistant', 'content':json.dumps(content)}}


class LocalOllamaTests(unittest.TestCase):
    def setUp(self):
        self.case = load_cases()[1]
        self.fake = FakeTransport(envelope(self.case['reference_proposal']))
        self.adapter = LocalOllama(self.fake)
        self.adapter.preflight()

    def chat(self):
        return self.adapter.assess(self.case['packet'], 'Instructions', {})

    def test_no_answer_leakage_and_local_request_settings(self):
        self.chat()
        path, body = self.fake.calls[-1]
        self.assertEqual(path,'/api/chat')
        self.assertEqual(body['model'],'qwen3:8b')
        self.assertFalse(body['think'])
        self.assertFalse(body['stream'])
        self.assertEqual(body['options'], OPTIONS)
        user_data=json.loads(body['messages'][1]['content'])
        self.assertEqual(set(user_data),{'assignment'})
        self.assertEqual(user_data['assignment'],self.case['packet'])
        self.assertNotIn('tools',body)
        self.assertEqual(self.adapter.metadata['model_digest'],'synthetic-digest')

    def test_truncated_and_thinking_only_outputs_rejected_with_diagnostics(self):
        for changes in ({'done':False}, {'done_reason':'length'},
                        {'message':{'content':'','thinking':'private thoughts'}}):
            self.fake.response=envelope({});self.fake.response.update(changes)
            with self.assertRaises(LocalAIError): self.chat()
            self.assertEqual(self.adapter.calls[-1]['status'],'failed')
            self.assertNotIn('private thoughts',json.dumps(self.adapter.calls[-1]))

    def test_tool_requests_and_context_overflow_rejected(self):
        for changes in ({'message':{'content':'{}','tool_calls':[{}]}},
                        {'prompt_eval_count':7000}, {'eval_count':None}):
            self.fake.response=envelope({});self.fake.response.update(changes)
            with self.assertRaises(LocalAIError): self.chat()

    def test_duplicate_keys_nonfinite_and_nonjson_rejected(self):
        for raw in ('{"a":1,"a":2}','{"a":NaN}','not json'):
            with self.assertRaises(ValueError): strict_json(raw)

    def test_nonobject_final_answer_rejected(self):
        self.fake.response=envelope([])
        with self.assertRaises(LocalAIError): self.chat()

    def test_remote_model_and_missing_model_rejected(self):
        for bad_path, bad_response in [('/api/show',{'remote_host':'https://remote'}),
                                       ('/api/tags',{'models':[]})]:
            def transport(path,payload=None):
                return bad_response if path==bad_path else self.fake(path,payload)
            with self.assertRaises(LocalAIError): LocalOllama(transport).preflight()

    def test_no_preflight_no_generation(self):
        adapter=LocalOllama(self.fake)
        with self.assertRaises(LocalAIError): adapter.assess(self.case['packet'],'',{})
        self.assertFalse(any(path=='/api/chat' for path,_ in self.fake.calls))

    def test_request_size_bounded_before_transport(self):
        with self.assertRaises(LocalAIError): self.adapter.assess(self.case['packet'],'x'*25000,{})
        self.assertFalse(any(path=='/api/chat' for path,_ in self.fake.calls))

    def test_no_redirect_or_unapproved_endpoint(self):
        with self.assertRaises(LocalAIError): NoRedirect().redirect_request(None,None,None,None,None,None)
        with self.assertRaises(LocalAIError): local_request('https://example.com')

    def test_proxy_disabled_and_numeric_loopback_used(self):
        with patch('cell_signaling.local_ollama.build_opener') as builder:
            response=builder.return_value.open.return_value.__enter__.return_value
            response.read.return_value=b'{"version":"test"}'
            local_request('/api/version')
            handlers=builder.call_args.args
            self.assertEqual(handlers[0].proxies,{})
            request=builder.return_value.open.call_args.args[0]
            self.assertEqual(request.full_url,'http://127.0.0.1:11434/api/version')

    def test_failure_becomes_processing_failure_not_coverage(self):
        self.fake.response=envelope({});self.fake.response['done_reason']='length'
        result=run_assessment(self.case['packet'],self.adapter.assess,self.adapter.challenge,
                              lambda:digest(self.case['packet']))
        self.assertEqual(result['status'],'processing_failed')
        self.assertIsNone(result['summary'])
        self.assertEqual(len(self.adapter.calls),1)

    def test_successful_mock_two_role_flow_is_not_model_evaluation(self):
        proposal=self.case['reference_proposal']
        challenge=fixture_challenge(self.case['packet'],proposal,'')
        original=self.fake
        def transport(path,payload=None):
            if path=='/api/chat' and len(self.adapter.calls)==2:
                return envelope(challenge)
            return original(path,payload)
        self.adapter.transport=transport
        result=run_assessment(self.case['packet'],self.adapter.assess,self.adapter.challenge,
                              lambda:digest(self.case['packet']))
        self.assertEqual(result['status'],'expert_review_required')
        self.assertEqual(len(self.adapter.calls),2)

    def test_run_memory_preserves_distinct_snapshots_without_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            first={'status':'expert_review_required','input_snapshot':self.case['packet']}
            a=save_run(first,Path(tmp));b=save_run({'status':'processing_failed'},Path(tmp))
            self.assertNotEqual(a,b)
            self.assertEqual(json.loads(a.read_text()),first)
            self.assertEqual(len(list(Path(tmp).glob('*.json'))),2)


if __name__ == '__main__':
    unittest.main()
