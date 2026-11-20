"""Offline tests of extraction contracts and rules, not model accuracy."""
import copy
import json
import unittest
from cell_signaling.assessment_contract import ContractError, digest
from cell_signaling.evidence_extraction import evaluate, validate_input
from cell_signaling.check_extraction import load_inputs, run_probe
from cell_signaling.local_ollama import LocalOllama, MODEL


def authored(packet, states):
    return {'input_hash': digest(packet), 'observations': [
        {'source_id': s['id'], 'completion': state, 'completed_on': when,
         'quote': '' if state == 'not_stated' else s['text']}
        for s,(state,when) in zip(packet['sources'], states)]}


class ExtractionTests(unittest.TestCase):
    def setUp(self): self.cases = load_inputs()

    def test_five_rule_outcomes(self):
        states = [[('completed','2026-11-27')],[('not_stated',None)],
                  [('not_completed',None)],[('completed','2026-12-03')],
                  [('completed','2026-11-27'),('not_completed',None)]]
        results = ['supported_execution','not_established','adverse_evidence','adverse_evidence','needs_review']
        for c,ss,want in zip(self.cases,states,results):
            with self.subTest(case=c['id']):
                self.assertEqual(evaluate(c['packet'],authored(c['packet'],ss))['result'], want)

    def test_unknown_completion_date_abstains(self):
        p=self.cases[0]['packet']
        self.assertEqual(evaluate(p,authored(p,[('completed',None)]))['result'],'not_established')

    def test_missing_quote_and_invented_date_rejected(self):
        p=self.cases[0]['packet'];a=authored(p,[('completed','2026-11-27')])
        for field,value in [('quote','invented quote'),('completed_on','2026-11-28')]:
            b=copy.deepcopy(a);b['observations'][0][field]=value
            with self.assertRaises(ContractError):evaluate(p,b)

    def test_source_scope_rejected(self):
        p=copy.deepcopy(self.cases[0]['packet']);p['sources'][0]['population']='other'
        with self.assertRaises(ContractError):validate_input(p)

    def test_omitted_duplicate_and_unknown_sources_rejected(self):
        p=self.cases[0]['packet'];a=authored(p,[('completed','2026-11-27')])
        for observations in [[],a['observations']*2,[dict(a['observations'][0],source_id='unknown')]]:
            with self.assertRaises(ContractError):evaluate(p,dict(a,observations=observations))

    def test_snapshot_and_not_stated_date_rejected(self):
        p=self.cases[1]['packet'];a=authored(p,[('not_stated',None)])
        with self.assertRaises(ContractError):evaluate(p,dict(a,input_hash='wrong'))
        a['observations'][0]['completed_on']='2026-11-27'
        with self.assertRaises(ContractError):evaluate(p,a)

    def exercise(self,fail=False):
        calls=[];tags=0
        def transport(path,payload=None):
            nonlocal tags
            if path=='/api/tags':
                tags+=1
                if tags==2 and fail:return {'models':[None]}
                return {'models':[{'name':MODEL,'digest':'mock'}]}
            if path=='/api/show':return {}
            if path=='/api/version':return {'version':'mock'}
            calls.append(payload)
            data=json.loads(payload['messages'][1]['content'])
            self.assertEqual(set(data),{'assignment'})
            self.assertNotIn('expectations',json.dumps(payload))
            self.assertNotIn('extract-0',json.dumps(payload))
            p=data['assignment'];answer=authored(p,[('not_stated',None)]*len(p['sources']))
            return {'model':MODEL,'done':True,'done_reason':'stop','prompt_eval_count':1000,'eval_count':100,
                    'message':{'role':'assistant','content':json.dumps(answer)}}
        result=run_probe(LocalOllama(transport),self.cases)
        self.assertEqual(len(calls),5)
        return result

    def test_bounded_requests_exclude_answers(self):
        self.assertEqual(self.exercise()['status'],'completed_needs_review')

    def test_postflight_failure_marks_all_diagnostic(self):
        result=self.exercise(True)
        self.assertEqual(result['status'],'processing_failed')
        self.assertTrue(all(c['status']=='diagnostic_only' for c in result['cases']))
