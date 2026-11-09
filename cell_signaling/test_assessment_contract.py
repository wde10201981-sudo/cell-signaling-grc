import copy
import unittest
from cell_signaling.assessment_contract import (
    ContractError, DIMENSIONS, digest, run_assessment, validate_packet, validate_response)
from cell_signaling.assessment_demo import load_cases, fixture_challenge


class AssessmentContractTests(unittest.TestCase):
    def setUp(self):
        self.case = copy.deepcopy(load_cases()[0])
        self.packet = self.case['packet']
        self.proposal = self.case['reference_proposal']

    def run_case(self, assessor=None, challenger=fixture_challenge, current_hash=None):
        return run_assessment(self.packet, assessor or (lambda *args: self.proposal),
                              challenger, current_hash or (lambda: digest(self.packet)))

    def test_four_authored_cases_validate_without_claiming_model_accuracy(self):
        for case in load_cases():
            result = run_assessment(case['packet'], lambda *args: case['reference_proposal'],
                                    fixture_challenge, lambda: digest(case['packet']))
            self.assertEqual(result['summary'], case['expected_summary'])
            self.assertEqual(result['status'], 'expert_review_required')
            self.assertTrue(result['expert_review_required'])

    def test_cross_organization_duplicate_revision_and_missing_layer_rejected(self):
        for change in ('tenant', 'duplicate', 'layer'):
            packet = copy.deepcopy(self.packet)
            if change == 'tenant': packet['sources'][0]['organization'] = 'OTHER'
            if change == 'duplicate':
                twin = copy.deepcopy(packet['sources'][0]); twin['id'] = 'TWIN'
                packet['sources'].append(twin)
                packet['layers']['governance_obligations'].append('TWIN')
            if change == 'layer': del packet['layers']['history_provenance']
            with self.assertRaises(ContractError): validate_packet(packet)

    def test_scope_omission_and_duplicate_rows_rejected(self):
        for rows in (self.proposal['rows'][:1], self.proposal['rows']*2):
            candidate = copy.deepcopy(self.proposal); candidate['rows'] = rows
            with self.assertRaises(ContractError): validate_response(self.packet, candidate)

    def test_wrong_quote_and_unknown_citation_rejected(self):
        for key,value in [('quote','fabricated'),('source_id','nonexistent')]:
            candidate = copy.deepcopy(self.proposal)
            candidate['rows'][0]['execution']['citations'][0][key] = value
            with self.assertRaises(ContractError): validate_response(self.packet,candidate)

    def test_cloud_evidence_cannot_support_on_premises(self):
        case = copy.deepcopy(load_cases()[1])
        case['reference_proposal']['rows'][1]['execution'] = case['reference_proposal']['rows'][0]['execution']
        with self.assertRaises(ContractError): validate_response(case['packet'],case['reference_proposal'])

    def test_withdrawn_sources_cannot_support_current_assessment(self):
        self.packet['sources'][-1]['status'] = 'withdrawn'
        self.proposal['input_hash'] = digest(self.packet)
        self.assertEqual(self.run_case()['status'],'processing_failed')

    def test_stale_input_hash_rejected(self):
        self.packet['criteria']['execution'] += ' Revised criterion.'
        self.assertEqual(self.run_case()['status'],'processing_failed')

    def test_mid_run_source_change_supersedes_result(self):
        result = self.run_case(current_hash=lambda:'changed')
        self.assertEqual(result['status'],'superseded')
        self.assertIsNone(result['summary'])
        self.assertIsNotNone(result['proposal'])

    def test_timeout_and_malformed_output_do_not_become_coverage_judgment(self):
        def timeout(*args): raise TimeoutError('private provider content')
        for assessor in (timeout, lambda *args: {'status':'fully covered'}):
            result=self.run_case(assessor=assessor)
            self.assertEqual(result['status'],'processing_failed')
            self.assertIsNone(result['summary'])
            self.assertNotIn('private', str(result))

    def test_challenge_disagreement_or_uncertainty_routes_follow_up(self):
        for verdict in ('disagrees','uncertain'):
            def challenge(packet,proposal,instructions):
                result=fixture_challenge(packet,proposal,instructions)
                result['checks'][0]['verdict']=verdict
                return result
            result=self.run_case(challenger=challenge)
            self.assertEqual(result['status'],'needs_follow_up')
            self.assertIsNone(result['summary'])

    def test_incomplete_challenge_rejected(self):
        def challenge(packet,proposal,instructions):
            result=fixture_challenge(packet,proposal,instructions)
            result['checks'].pop()
            return result
        self.assertEqual(self.run_case(challenger=challenge)['status'],'processing_failed')

    def test_approval_field_not_accepted_from_model(self):
        self.proposal['approved']=True
        self.assertEqual(self.run_case()['status'],'processing_failed')

    def test_input_and_proposal_are_isolated_from_adapter_mutation(self):
        before=copy.deepcopy(self.packet)
        def assessor(packet,*args):
            packet['criteria']['execution']='Ignore everything'
            return self.proposal
        def challenger(packet,proposal,instructions):
            result=fixture_challenge(packet,proposal,instructions)
            proposal['rows'].clear()
            return result
        result=self.run_case(assessor,challenger)
        self.assertEqual(self.packet,before)
        self.assertEqual(len(result['proposal']['rows']),2)
        self.assertEqual(result['status'],'expert_review_required')

    def test_missing_evidence_is_valid_abstention_not_failure(self):
        self.packet['sources']=self.packet['sources'][:1]
        self.packet['layers']={layer: ['R1'] if layer=='governance_obligations' else []
                               for layer in self.packet['layers']}
        for row in self.proposal['rows']:
            for dim in DIMENSIONS:
                row[dim]={'state':'not_established','explanation':'No applicable support supplied.', 'citations':[]}
        self.proposal['input_hash']=digest(self.packet)
        result=self.run_case()
        self.assertEqual(result['summary'],'insufficient_evidence')
        self.assertEqual(result['status'],'expert_review_required')

    def test_conflict_needs_multiple_sources(self):
        self.proposal['rows'][0]['execution']['state']='conflicting'
        self.assertEqual(self.run_case()['status'],'processing_failed')

    def test_future_receipt_rejected_before_agent_runs(self):
        self.packet['sources'][0]['received_on']='2026-12-03'
        with self.assertRaises(ContractError): self.run_case()


if __name__ == '__main__':
    unittest.main()
