"""Explicit live probe. Run python -m cell_signaling.run_local_assessment --run."""
import argparse
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import uuid4

from .assessment_contract import digest, run_assessment
from .assessment_demo import load_cases
from .local_ollama import LocalOllama

OUTPUT_DIR = Path(__file__).resolve().parent.parent / 'local-output'


def save_run(record, directory=OUTPUT_DIR):
    directory.mkdir(parents=True, exist_ok=True)
    name = 'assessment-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid4().hex[:12] + '.json'
    path = directory / name
    with path.open('x', encoding='utf-8') as output:
        json.dump(record, output, indent=2, allow_nan=False)
        output.write('\n')
    return path


def main():
    parser = argparse.ArgumentParser(description='One synthetic limited-scope probe, using local qwen3:8b.')
    parser.add_argument('--run', action='store_true', help='Allow two local model requests; no expected answers sent.')
    args = parser.parse_args()
    if not args.run:
        print('No model request made. Add --run to run the synthetic limited-scope case.')
        return 0
    packet = next(case['packet'] for case in load_cases() if case['name'] == 'limited_scope')
    adapter = LocalOllama()
    record = {'synthetic': True, 'case': 'limited_scope', 'started_at': datetime.now(timezone.utc).isoformat(),
              'input_snapshot': packet, 'input_hash': digest(packet), 'status': 'processing_failed',
              'result': None, 'error': None, 'metadata': adapter.metadata, 'calls': adapter.calls,
              'reasoning_review': 'pending', 'production_readiness': 'not_established'}
    try:
        print('Checking local Ollama and qwen3:8b...', flush=True)
        adapter.preflight()
        record['metadata'] = copy.deepcopy(adapter.metadata)
        result = run_assessment(packet, adapter.assess, adapter.challenge, lambda: digest(packet))
        record['result'] = result
        record['status'] = result['status']
        # Ensure both calls used the same locally installed tag revision.
        before = adapter.metadata['model_digest']
        adapter.preflight()
        record['post_run_model_digest'] = adapter.metadata['model_digest']
        if before != adapter.metadata['model_digest']:
            record['status'] = result['status'] = 'superseded'
            result['summary'] = None
            record['error'] = 'Model tag changed during the run; review is required.'
    except (ValueError, TypeError, KeyError, ConnectionError, TimeoutError) as exc:
        record['error'] = str(exc)
        record['status'] = 'processing_failed'
        if record['result'] is not None:
            record['result']['status'] = 'processing_failed'
            record['result']['summary'] = None
    finally:
        record['finished_at'] = datetime.now(timezone.utc).isoformat()
        path = save_run(record)
    print('Status:', record['status'])
    result = record['result']
    if result:
        print('Summary:', result['summary'])
        if result['proposal']:
            for row in result['proposal']['rows']:
                print(row['population'] + ':', ', '.join(
                    f"{dimension}={row[dimension]['state']}" for dimension in ('control_fit','implementation','execution')))
        if result['error']:
            print('Contract error:', result.get('error_detail', result['error']))
    if record['error']:
        print('Error:', record['error'])
    for call in record['calls']:
        if call.get('error'):
            print(call['role'] + ':', call['error'])
    print('Saved:', path)
    print('Same model in separate passes. Human reasoning review remains pending.')
    return 1 if record['status'] == 'processing_failed' else 0


if __name__ == '__main__':
    raise SystemExit(main())
