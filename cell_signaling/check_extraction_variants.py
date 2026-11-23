"""Run five new wording/scope/date variants with the unchanged extraction probe."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
from .check_extraction import run_probe
from .assessment_contract import digest
from .evidence_extraction import VERSION, INSTRUCTIONS, validate_input, schema, evaluate
from .local_ollama import LocalOllama
from .run_local_assessment import save_run

ROOT = Path(__file__).resolve().parent.parent


def load_inputs():
    return json.loads((ROOT / 'examples/extraction_variants_inputs.json').read_text(encoding='utf-8'))


def verify_frozen(root=ROOT):
    manifest = json.loads((root / 'examples/extraction_variants_manifest.json').read_text(encoding='utf-8'))
    for name, expected in manifest['files'].items():
        # Normalize Windows checkout line endings before hashing the text files.
        content = (root / name).read_text(encoding='utf-8').encode('utf-8')
        if hashlib.sha256(content).hexdigest() != expected:
            raise ValueError('Frozen comparison file changed: ' + name)
    return manifest


def run_variants(adapter):
    manifest = verify_frozen()
    record = run_probe(adapter, load_inputs())
    record['evaluation_set'] = 'extraction-variants-0.1'
    record['frozen_baseline'] = manifest
    return record



def run_single_variant(adapter, case_id):
    manifest = verify_frozen()
    case = next((c for c in load_inputs() if c['id'] == case_id), None)
    if case is None:
        raise ValueError('Unknown variant ID')
    packet = copy.deepcopy(case['packet'])
    entry = {'id': case_id, 'input_snapshot': packet, 'status': 'processing_failed'}
    record = {'synthetic': True, 'experiment': VERSION,
              'evaluation_set': 'extraction-variants-0.1', 'selected_case': case_id,
              'frozen_baseline': manifest, 'status': 'processing_failed',
              'cases': [entry], 'calls': adapter.calls, 'error': None,
              'reasoning_review': 'pending'}
    try:
        validate_input(packet)
        adapter.preflight()
        record['metadata'] = copy.deepcopy(adapter.metadata)
        print('Extracting one selected case with the frozen instructions...', flush=True)
        answer = adapter._chat('extractor', INSTRUCTIONS + '\ninput_hash=' + digest(packet),
                               {'assignment': packet}, schema(packet))
        entry['extracted'] = answer
        entry['assessment'] = evaluate(packet, answer)
        adapter.preflight()
        if record['metadata']['model_digest'] != adapter.metadata['model_digest']:
            raise ValueError('Model changed during probe.')
        entry['status'] = 'pending_expert_review'
        record['status'] = 'completed_needs_review'
    except (ValueError, TypeError, KeyError, ConnectionError, TimeoutError) as exc:
        record['error'] = str(exc)
        entry['status'] = 'diagnostic_only'
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--case', choices=[c['id'] for c in load_inputs()])
    args = parser.parse_args()
    try:
        verify_frozen()
    except (ValueError, OSError) as exc:
        print('Comparison blocked before model calls:', exc)
        return 1
    if not args.run:
        print('Frozen files verified. Add --run to execute selected cases; no model calls made.')
        return 0
    record = run_single_variant(LocalOllama(), args.case) if args.case else run_variants(LocalOllama())
    path = save_run(record)
    print('Status:', record['status'])
    for case in record['cases']:
        print(case['id'], case['status'], case.get('assessment', {}).get('result'))
    if record['error']:
        print('Error:', record['error'])
    print('Saved:', path)
    print('Review extracted meanings, dates and quotes against sources. No readiness score.')
    return int(record['status'] == 'processing_failed')


if __name__ == '__main__':
    raise SystemExit(main())
