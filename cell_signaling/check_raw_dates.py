"""Five bounded local extraction requests. Run with --run; no retries."""
import argparse
import copy
import json
from pathlib import Path
from .raw_date_extraction import VERSION, INSTRUCTIONS, validate_input, schema, evaluate
from .check_extraction_variants import verify_frozen
from .assessment_contract import digest
from .local_ollama import LocalOllama
from .run_local_assessment import save_run


def load_inputs():
    return json.loads((Path(__file__).resolve().parent.parent / 'examples/extraction_variants_inputs.json').read_text())


def run_probe(adapter, cases):
    record = {'synthetic': True, 'experiment': VERSION, 'status': 'processing_failed',
              'cases': [], 'calls': adapter.calls, 'error': None, 'reasoning_review': 'pending', 'evaluation_set': 'raw-date-regression-0.1'}
    try:
        record['comparison_baseline'] = verify_frozen()
        if len(cases) != 5:
            raise ValueError('Expected exactly five synthetic cases.')
        for c in cases:
            validate_input(c['packet'])
        adapter.preflight()
        record['metadata'] = copy.deepcopy(adapter.metadata)
        for i,c in enumerate(cases, 1):
            packet = copy.deepcopy(c['packet'])
            entry = {'id': c['id'], 'input_snapshot': packet, 'status': 'processing_failed'}
            record['cases'].append(entry)
            print(f'{i}/5 Extracting review completion evidence...', flush=True)
            answer = adapter._chat('extractor', INSTRUCTIONS + '\ninput_hash=' + digest(packet),
                                   {'assignment': packet}, schema(packet))
            entry['extracted'] = answer
            entry['assessment'] = evaluate(packet, answer)
            entry['status'] = 'pending_expert_review'
        adapter.preflight()
        if record['metadata']['model_digest'] != adapter.metadata['model_digest']:
            raise ValueError('Model changed during probe.')
        record['status'] = 'completed_needs_review'
    except (ValueError, TypeError, KeyError, ConnectionError, TimeoutError) as exc:
        record['error'] = str(exc)
        for entry in record['cases']:
            entry['status'] = 'diagnostic_only'
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    if not parser.parse_args().run:
        print('No model calls. Add --run for five raw-date regression requests.')
        return 0
    record = run_probe(LocalOllama(), load_inputs())
    path = save_run(record)
    print('Status:', record['status'])
    for c in record['cases']:
        print(c['id'], c['status'], c.get('assessment', {}).get('result'))
        for detail in c.get('assessment', {}).get('date_details', []):
            print('  Date:', detail['raw_date'], '|', detail['date_status'], '|', detail['deadline_relation'])
    if record['error']: print('Error:', record['error'])
    print('Saved:', path)
    print('Extraction meaning and source truth require review; no compliance approval.')
    return int(record['status'] == 'processing_failed')


if __name__ == '__main__':
    raise SystemExit(main())
