"""Regression for a valid abstention rejected by the original citation contract."""
import copy
import unittest
from cell_signaling.assessment_contract import ContractError, DIMENSIONS, digest, validate_response, run_assessment
from cell_signaling.assessment_demo import load_cases, fixture_challenge
from cell_signaling.local_ollama import assessment_schema


class CitationScopeTests(unittest.TestCase):
    def setUp(self):
        case=copy.deepcopy(load_cases()[1])
        self.packet=case['packet']
        self.response=case['reference_proposal']
        self.aws,self.onprem=self.response['rows']

    def reject(self):
        with self.assertRaises(ContractError):
            validate_response(self.packet,self.response)

    def test_scope_exclusion_explains_abstention_and_reaches_challenge(self):
        # Reproduces the recorded model's valid distinction using the new field citation.
        self.onprem['control_fit']['explanation'] = (
            'Control C1 is only defined for the AWS population, and there is no evidence '
            'that it applies to on-premises systems in the supplied packet.')
        called=[]
        def challenger(packet, proposal, instructions):
            called.append(True)
            return fixture_challenge(packet,proposal,instructions)
        result=run_assessment(self.packet,lambda *args:self.response,challenger,lambda:digest(self.packet))
        self.assertEqual(called,[True])
        self.assertEqual(result['summary'],'partial_support')
        self.assertEqual(result['status'],'expert_review_required')

    def test_scope_limitation_never_establishes_positive_or_adverse_judgment(self):
        for state in ('supported','contradicted','conflicting'):
            with self.subTest(state=state):
                self.onprem['execution']['state']=state
                self.reject()

    def test_cross_population_support_still_rejected_even_for_abstention(self):
        self.onprem['execution']['citations'][0]['purpose']='support'
        self.reject()

    def test_limitation_cannot_cite_generic_description_instead_of_scope(self):
        citation=self.onprem['control_fit']['citations'][0]
        citation['field']='text';citation['value']=self.packet['sources'][1]['text']
        self.reject()

    def test_population_field_requires_complete_exact_array(self):
        for value in ('aws',['on-premises'],[],['aws','on-premises'],['aws','aws']):
            with self.subTest(value=value):
                self.onprem['control_fit']['citations'][0]['value']=value
                self.reject()

    def test_source_that_includes_population_is_not_scope_exclusion(self):
        citation=self.onprem['execution']['citations'][0]
        citation['source_id']='R1';citation['value']=['aws','on-premises']
        self.reject()

    def test_limitation_cannot_use_withdrawn_source(self):
        self.packet['sources'][1]['status']='withdrawn'
        self.response['input_hash']=digest(self.packet)
        # Remove other C1 references so the rejection concerns the limitation itself.
        self.aws['control_fit']={'state':'not_established','explanation':'Control withdrawn.', 'citations':[]}
        self.reject()

    def test_population_metadata_alone_cannot_establish_execution(self):
        self.aws['execution']['citations']=[{'source_id':'E2','purpose':'support',
                                           'field':'populations','value':['aws']}]
        self.reject()

    def test_two_fields_of_one_source_do_not_establish_conflict(self):
        finding=self.aws['execution'];finding['state']='conflicting'
        finding['citations'].append({'source_id':'E2','purpose':'support',
                                    'field':'populations','value':['aws']})
        self.reject()

    def test_unknown_purpose_and_field_fail_closed(self):
        for key,value in [('purpose','ignore_scope'),('field','assumed_scope')]:
            with self.subTest(key=key):
                original=copy.deepcopy(self.onprem['control_fit']['citations'][0])
                self.onprem['control_fit']['citations'][0][key]=value
                self.reject()
                self.onprem['control_fit']['citations'][0]=original

    def test_old_contract_and_ambiguous_old_citation_not_silently_upgraded(self):
        self.response['contract_version']='coverage-assessment-0.1'
        self.reject()
        self.response['contract_version']=self.packet['contract_version']
        self.onprem['control_fit']['citations']=[{'source_id':'C1','quote':self.packet['sources'][1]['text']}]
        self.reject()

    def test_explicit_schema_covers_both_citation_purposes(self):
        schema=assessment_schema(self.packet)
        variants=schema['properties']['rows']['items']['properties']['execution']['properties']['citations']['items']['oneOf']
        text_citation,field_citation=variants
        self.assertEqual(text_citation['properties']['purpose']['enum'],['support'])
        self.assertEqual(field_citation['properties']['field']['enum'],['populations'])
        self.assertIn('scope_limitation',field_citation['properties']['purpose']['enum'])
        self.assertEqual(field_citation['properties']['value']['type'],'array')


if __name__ == '__main__':
    unittest.main()
