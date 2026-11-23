"""Test evaluation plumbing, not model semantic performance."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from cell_signaling.assessment_contract import digest
from cell_signaling.check_extraction_variants import ROOT, load_inputs, verify_frozen, run_variants
from cell_signaling.local_ollama import LocalOllama, MODEL


class ExtractionVariantTests(unittest.TestCase):
    def test_frozen_baseline_matches(self):
        self.assertEqual(verify_frozen()['baseline_commit'], '51e48301f1a0c2f277a9fe9c21a8a9253d7fd485')

    def test_changed_baseline_rejected_and_windows_line_endings_supported(self):
        manifest = verify_frozen()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ['examples/extraction_variants_manifest.json', *manifest['files']]:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / name).read_text(encoding='utf-8').replace('\n','\r\n').encode())
            verify_frozen(root)
            name = next(iter(manifest['files']))
            with (root / name).open('a') as out:
                out.write('\n# changed\n')
            with self.assertRaises(ValueError):
                verify_frozen(root)

    def test_requests_use_new_inputs_without_reviewer_answers(self):
        sent = []
        def transport(path, payload=None):
            if path == '/api/tags':
                return {'models': [{'name': MODEL, 'digest': 'offline-mock'}]}
            if path == '/api/show': return {}
            if path == '/api/version': return {'version': 'offline-mock'}
            sent.append(payload)
            assignment = json.loads(payload['messages'][1]['content'])
            self.assertEqual(set(assignment), {'assignment'})
            p = assignment['assignment']
            response = {'input_hash': digest(p), 'observations': [
                {'source_id': s['id'], 'completion': 'not_stated', 'completed_on': None, 'quote': ''}
                for s in p['sources']]}
            return {'model': MODEL, 'done': True, 'done_reason': 'stop',
                    'prompt_eval_count': 900, 'eval_count': 100,
                    'message': {'role': 'assistant', 'content': json.dumps(response)}}
        original = Path.read_text
        def read(path, *args, **kwargs):
            if path.name.endswith('_review.json'):
                raise AssertionError('Answer file must not be read during inference')
            return original(path, *args, **kwargs)
        with patch.object(Path, 'read_text', read):
            record = run_variants(LocalOllama(transport))
        self.assertEqual(record['status'], 'completed_needs_review')
        self.assertEqual(len(sent), 5)
        for payload, case in zip(sent, load_inputs()):
            self.assertEqual(json.loads(payload['messages'][1]['content'])['assignment'], case['packet'])
            self.assertNotIn('variant-0', json.dumps(payload))
