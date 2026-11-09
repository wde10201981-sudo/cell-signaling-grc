"""Offline contract exercise using authored responses, not AI output."""
import json
from pathlib import Path
from .assessment_contract import DIMENSIONS, digest, run_assessment


def load_cases():
    return json.loads((Path(__file__).resolve().parent.parent /
                       'examples/assessment_cases.json').read_text())['cases']


def fixture_challenge(packet, proposal, instructions):
    return {'input_hash': digest(packet), 'proposal_hash': digest(proposal), 'checks': [
        {'population': row['population'], 'dimension': dim, 'verdict': 'agrees',
         'reason': 'Authored fixture acceptance only; no model or independent reasoning was exercised.'}
        for row in proposal['rows'] for dim in DIMENSIONS]}


def main():
    print('SYNTHETIC CONTRACT EXERCISE — authored responses, not AI evaluation')
    for case in load_cases():
        packet = case['packet']
        result = run_assessment(packet, lambda *args: case['reference_proposal'],
                                fixture_challenge, lambda: digest(packet))
        print(f"{case['name']}: {result['summary']} | {result['status']}")
        if result['summary'] != case['expected_summary']:
            raise RuntimeError('Fixture contract failed')


if __name__ == '__main__':
    main()
