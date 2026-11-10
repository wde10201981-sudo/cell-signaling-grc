"""Offline request-boundary tests; authored answers do not measure AI accuracy."""
import copy
import json
import unittest
from cell_signaling.check_challenger import load_inputs, run_probe
from cell_signaling.assessment_contract import digest, DIMENSIONS, validate_packet, validate_response
from cell_signaling.local_ollama import LocalOllama, MODEL


class ChallengerProbeTests(unittest.TestCase):
    def test_all_packets_and_proposals_validate_structurally(self):
        for c in load_inputs():
            c['proposal']['input_hash'] = digest(c['packet'])
            validate_packet(c['packet'])
            validate_response(c['packet'], c['proposal'])

    def exercise(self, bad_postflight=False):
        counts = {'chat': 0, 'tags': 0}
        def transport(path, payload=None):
            if path == '/api/tags':
                counts['tags'] += 1
                if bad_postflight and counts['tags'] == 2:
                    return {'models': [None]}
                return {'models': [{'name': MODEL, 'digest': 'test-digest'}]}
            if path == '/api/show': return {}
            if path == '/api/version': return {'version': 'test'}
            counts['chat'] += 1
            data = json.loads(payload['messages'][1]['content'])
            self.assertEqual(set(data), {'assignment', 'proposal'})
            self.assertNotIn('expected', json.dumps(data))
            self.assertNotIn('probe-0', json.dumps(data))
            p, proposal = data['assignment'], data['proposal']
            answer = {'input_hash': digest(p), 'proposal_hash': digest(proposal),
                      'checks': [{'population': 'hosted', 'dimension': d, 'verdict': 'uncertain',
                                  'reason': 'Authored transport fixture; no semantic claim.'} for d in DIMENSIONS]}
            return {'model': MODEL, 'done': True, 'done_reason': 'stop',
                    'prompt_eval_count': 2000, 'eval_count': 200,
                    'message': {'role': 'assistant', 'content': json.dumps(answer)}}
        record = run_probe(LocalOllama(transport), load_inputs())
        self.assertEqual(counts['chat'], 3)
        return record

    def test_exactly_three_challenges_without_answer_key_or_case_ids(self):
        result = self.exercise()
        self.assertEqual(result['status'], 'completed_needs_review')
        self.assertEqual(result['reasoning_review'], 'pending')

    def test_postflight_failure_is_not_completed(self):
        result = self.exercise(True)
        self.assertEqual(result['status'], 'processing_failed')
        self.assertTrue(result['error'])
        self.assertEqual(len(result['cases']), 3)
