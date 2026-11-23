"""Run five new wording/scope/date variants with the unchanged extraction probe."""
import argparse
import hashlib
import json
from pathlib import Path
from .check_extraction import run_probe
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    try:
        verify_frozen()
    except (ValueError, OSError) as exc:
        print('Comparison blocked before model calls:', exc)
        return 1
    if not args.run:
        print('Frozen files verified. Add --run for five new synthetic cases; no model calls made.')
        return 0
    record = run_variants(LocalOllama())
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
