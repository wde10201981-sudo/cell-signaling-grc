"""Offline integration tests; authored responses do not measure model accuracy."""
import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from cell_signaling.assessment_contract import digest, ContractError
from cell_signaling.raw_date_extraction import evaluate
from cell_signaling.check_raw_dates import run_probe, load_inputs
from cell_signaling.local_ollama import LocalOllama, MODEL


def response(p, state='completed', raw='01/02/2027'):
    return {'input_hash': digest(p), 'observations': [
        {'source_id': s['id'], 'completion': state, 'raw_completion_date': raw,
         'quote': s['text']} for s in p['sources']]}


class RawDateTests(unittest.TestCase):
    def setUp(self): self.cases = load_inputs()

    def test_ambiguous_date_retained_and_late(self):
        p = self.cases[3]['packet']; a = response(p)
        old = copy.deepcopy(a)
        result = evaluate(p, a)
        self.assertEqual(result['result'], 'adverse_evidence')
        self.assertEqual(result['date_details'][0]['date_status'], 'ambiguous')
        self.assertIsNone(result['date_details'][0]['exact_date'])
        self.assertEqual(a, old)

    def test_straddling_deadline_remains_unknown(self):
        p = copy.deepcopy(self.cases[3]['packet'])
        p['deadline'] = p['sources'][0]['deadline'] = '2027-01-15'
        self.assertEqual(evaluate(p, response(p))['result'], 'not_established')

    def test_normalized_date_and_unsupported_fields_rejected(self):
        p = self.cases[3]['packet']
        with self.assertRaises(ValueError): evaluate(p, response(p, raw='2027-01-02'))
        a = response(p); a['observations'][0]['completed_on'] = '2027-01-02'
        with self.assertRaises(ContractError): evaluate(p, a)
        with self.assertRaises(ContractError): evaluate(p, response(p, state='not_stated'))

    def test_five_authored_results(self):
        states = [('completed','2026-12-29'),('not_stated',None),('not_stated',None),
                  ('completed','01/02/2027'),('completed','2026-12-30')]
        wanted = ['supported_execution','not_established','not_established','adverse_evidence','supported_execution']
        for c,(state,raw),want in zip(self.cases,states,wanted):
            with self.subTest(case=c['id']):
                self.assertEqual(evaluate(c['packet'],response(c['packet'],state,raw))['result'],want)

    def test_missing_invalid_and_out_of_period(self):
        p = copy.deepcopy(self.cases[3]['packet'])
        for raw,want in [(None,'not_established'),('2027-02-30','not_established'),('2026-11-01','needs_review')]:
            p['sources'][0]['text'] = 'Review completed. Date: ' + str(raw)
            self.assertEqual(evaluate(p,response(p,raw=raw))['result'],want)

    def test_wrong_source_quote_scope_hash_and_duplicate_rejected(self):
        p = self.cases[3]['packet']
        for field,value in [('source_id','absent'),('quote','fabricated')]:
            a=response(p);a['observations'][0][field]=value
            with self.assertRaises(ContractError):evaluate(p,a)
        a=response(p);a['input_hash']='wrong'
        with self.assertRaises(ContractError):evaluate(p,a)
        a=response(p);a['observations']*=2
        with self.assertRaises(ContractError):evaluate(p,a)
        bad=copy.deepcopy(p);bad['sources'][0]['population']='other'
        with self.assertRaises(ContractError):evaluate(bad,response(bad))

    def test_conflicting_sources_remain_review(self):
        p = copy.deepcopy(self.cases[3]['packet'])
        p['sources'].append(dict(p['sources'][0], id='DOC-B', text='The review was not performed.'))
        a=response(p);a['observations'][1].update(completion='not_completed',raw_completion_date=None)
        self.assertEqual(evaluate(p,a)['result'],'needs_review')

    def test_runner_protocol_and_postflight_failure(self):
        for fail in (False,True):
            sent=[];tags=0
            def transport(path,payload=None):
                nonlocal tags
                if path=='/api/tags':
                    tags+=1
                    if fail and tags==2:raise ConnectionResetError('simulated postflight reset')
                    return {'models':[{'name':MODEL,'digest':'offline-mock'}]}
                if path=='/api/show':return {}
                if path=='/api/version':return {'version':'offline-mock'}
                sent.append(payload)
                data=json.loads(payload['messages'][1]['content'])
                self.assertEqual(set(data),{'assignment'})
                answer=response(data['assignment'],state='not_stated',raw=None)
                return {'model':MODEL,'done':True,'done_reason':'stop','prompt_eval_count':900,'eval_count':150,
                        'message':{'role':'assistant','content':json.dumps(answer)}}
            original=Path.read_text
            def read(path,*args,**kwargs):
                if path.name.endswith('_review.json'):raise AssertionError('Reference answers read during inference')
                return original(path,*args,**kwargs)
            with patch.object(Path,'read_text',read):
                record=run_probe(LocalOllama(transport),self.cases)
            self.assertEqual(len(sent),5)
            self.assertEqual(record['status'],'processing_failed' if fail else 'completed_needs_review')
            if fail:self.assertTrue(all(c['status']=='diagnostic_only' for c in record['cases']))
