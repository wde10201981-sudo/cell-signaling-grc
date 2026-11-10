"""Three bounded synthetic challenger requests. No assessor or automatic approval."""
import argparse
import copy
import json
from pathlib import Path
from .assessment_contract import (CHALLENGER_INSTRUCTIONS, digest, validate_packet,
                                  validate_response, validate_challenge)
from .local_ollama import LocalOllama
from .run_local_assessment import save_run


def load_inputs():
    return json.loads((Path(__file__).resolve().parent.parent / 'examples/challenge_probe_inputs.json').read_text())


def run_probe(adapter, cases):
    record = {'synthetic': True, 'status': 'processing_failed', 'cases': [],
              'error': None, 'reasoning_review': 'pending', 'production_readiness': 'not_established',
              'calls': adapter.calls}
    try:
        prepared = copy.deepcopy(cases)
        if len(prepared) != 3:
            raise ValueError('Exactly three probe cases required.')
        for case in prepared:
            case['proposal']['input_hash'] = digest(case['packet'])
            validate_packet(case['packet'])
            validate_response(case['packet'], case['proposal'])
        adapter.preflight()
        record['metadata'] = copy.deepcopy(adapter.metadata)
        for case in prepared:
            entry = {'id': case['id'], 'input_snapshot': case['packet'], 'proposal': case['proposal']}
            record['cases'].append(entry)
            instructions = (CHALLENGER_INSTRUCTIONS + '\ninput_hash=' + digest(case['packet']) +
                            '\nproposal_hash=' + digest(case['proposal']))
            answer = adapter.challenge(case['packet'], case['proposal'], instructions)
            entry['challenge'] = answer
            validate_challenge(case['proposal'], answer)
        adapter.preflight()
        if adapter.metadata['model_digest'] != record['metadata']['model_digest']:
            raise ValueError('Model digest changed; discard comparison and review diagnostics.')
        record['status'] = 'completed_needs_review'
    except (ValueError, TypeError, KeyError, ConnectionError, TimeoutError) as exc:
        record['error'] = str(exc)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    if not args.run:
        print('No requests made. Add --run for exactly three challenger requests, without retries.')
        return 0
    record = run_probe(LocalOllama(), load_inputs())
    path = save_run(record)
    print('Status:', record['status'])
    for case in record['cases']:
        for check in case.get('challenge', {}).get('checks', []):
            print(case['id'], check['dimension'], check['verdict'], '—', check['reason'])
    if record['error']:
        print('Error:', record['error'])
    print('Saved:', path)
    print('Expert review of labels AND reasons required. This is not a readiness score.')
    return 1 if record['status'] == 'processing_failed' else 0


if __name__ == '__main__':
    raise SystemExit(main())
