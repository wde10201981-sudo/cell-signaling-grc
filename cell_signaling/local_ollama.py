"""Local-only Qwen adapter for the bounded synthetic assessment probe."""
import json
import socket
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener, ProxyHandler, HTTPRedirectHandler

from .assessment_contract import VERSION, DIMENSIONS, STATES, ContractError, digest

MODEL = 'qwen3:8b'
BASE_URL = 'http://127.0.0.1:11434'
ADAPTER_VERSION = 'ollama-probe-0.2'
OPTIONS = {'temperature': 0, 'num_ctx': 8192, 'num_predict': 3072}
MAX_RESPONSE_BYTES = 2_000_000
MAX_PROMPT_BYTES = 24_000


class LocalAIError(ContractError):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise LocalAIError('Redirect refused: this adapter only contacts local Ollama.')


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise LocalAIError('Duplicate JSON field rejected.')
            result[key] = value
        return result
    def bad_constant(value):
        raise LocalAIError('Non-finite JSON value rejected.')
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=bad_constant)


def local_request(path, payload=None):
    if path not in ('/api/tags', '/api/show', '/api/chat', '/api/version'):
        raise LocalAIError('Unsupported endpoint.')
    request = Request(BASE_URL + path, data=None if payload is None else
                      json.dumps(payload, allow_nan=False).encode(),
                      headers={'Content-Type': 'application/json'})
    opener = build_opener(ProxyHandler({}), NoRedirect())
    try:
        with opener.open(request, timeout=180 if path == '/api/chat' else 10) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
        if len(raw) > MAX_RESPONSE_BYTES:
            raise LocalAIError('Ollama response exceeded the byte limit.')
        return strict_json(raw)
    except HTTPError as exc:
        raise LocalAIError(f'Ollama HTTP {exc.code}; check model installation and Ollama logs.') from exc
    except (TimeoutError, socket.timeout) as exc:
        raise LocalAIError('Ollama request timed out; no result accepted.') from exc
    except URLError as exc:
        raise LocalAIError('Cannot reach local Ollama at 127.0.0.1:11434. Start ollama serve.') from exc
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise LocalAIError('Ollama returned invalid JSON.') from exc


def obj(properties):
    return {'type': 'object', 'properties': properties, 'required': list(properties),
            'additionalProperties': False}


def array(items):
    return {'type': 'array', 'items': items}


def enum(values):
    return {'type': 'string', 'enum': list(values)}


TEXT = {'type': 'string', 'minLength': 1}


def assessment_schema(packet):
    citation = {'oneOf': [
        obj({'source_id': enum(s['id'] for s in packet['sources']),
             'purpose': enum(['support']), 'field': enum(['text']), 'value': TEXT}),
        obj({'source_id': enum(s['id'] for s in packet['sources']),
             'purpose': enum(['support', 'scope_limitation']),
             'field': enum(['populations']), 'value': array(TEXT)})]}
    dimension = obj({'state': enum(STATES), 'explanation': TEXT, 'citations': array(citation)})
    row = obj({'population': enum(packet['populations']), **{d: dimension for d in DIMENSIONS}})
    return obj({'contract_version': enum([VERSION]), 'input_hash': enum([digest(packet)]),
                'rows': array(row), 'questions': array(TEXT), 'proposed_actions': array(TEXT)})


def challenge_schema(packet, proposal):
    return obj({'input_hash': enum([digest(packet)]), 'proposal_hash': enum([digest(proposal)]),
                'checks': array(obj({'population': enum(packet['populations']),
                    'dimension': enum(DIMENSIONS), 'verdict': enum(['agrees', 'disagrees', 'uncertain']),
                    'reason': TEXT}))})


class LocalOllama:
    def __init__(self, transport=local_request):
        self.transport = transport
        self.calls = []
        self.metadata = {'adapter_version': ADAPTER_VERSION, 'model': MODEL,
                         'options': dict(OPTIONS), 'think': False, 'model_digest': None}
        self.ready = False

    def preflight(self):
        self.ready = False
        models = self.transport('/api/tags')['models']
        match = next((m for m in models if m.get('name') == MODEL or m.get('model') == MODEL), None)
        if match is None or not match.get('digest'):
            raise LocalAIError('qwen3:8b is not installed locally. Run ollama pull qwen3:8b.')
        info = self.transport('/api/show', {'model': MODEL})
        if info.get('remote_host') or info.get('remote_model'):
            raise LocalAIError('Remote model refused; use the local qwen3:8b weights.')
        self.metadata['model_digest'] = match['digest']
        self.metadata['model_details'] = match.get('details', {})
        self.metadata['ollama_version'] = self.transport('/api/version').get('version')
        self.ready = True

    def _chat(self, role, instructions, data, schema):
        if not self.ready:
            raise LocalAIError('Run local model preflight first.')
        messages = [{'role': 'system', 'content': instructions +
                     '\nUse concise explanations and the shortest exact excerpts sufficient to support them.\n'
                     'Required response JSON schema:\n' + json.dumps(schema)},
                    {'role': 'user', 'content': json.dumps(data)}]
        if len(json.dumps(messages).encode()) > MAX_PROMPT_BYTES:
            raise LocalAIError('Input exceeds this small probe budget; split the assignment explicitly.')
        call = {'role': role, 'messages': messages, 'schema': schema, 'status': 'started'}
        self.calls.append(call)
        try:
            response = self.transport('/api/chat', {'model': MODEL, 'messages': messages,
                'stream': False, 'think': False, 'format': schema, 'options': dict(OPTIONS), 'keep_alive': '5m'})
            if not isinstance(response, dict):
                raise LocalAIError('Invalid Ollama response envelope.')
            call['telemetry'] = {key: response.get(key) for key in (
                'model', 'done', 'done_reason', 'prompt_eval_count', 'eval_count', 'total_duration', 'load_duration')}
            message = response.get('message', {})
            if not isinstance(message, dict):
                raise LocalAIError('Invalid message envelope.')
            content = message.get('content', '')
            call['response_text'] = content
            call['thinking_characters'] = len(message.get('thinking', '') or '')
            if response.get('done') is not True or response.get('done_reason') != 'stop':
                raise LocalAIError('Incomplete AI response; no result accepted. See saved token telemetry.')
            if message.get('tool_calls'):
                raise LocalAIError('Unexpected tool request rejected.')
            counts = (response.get('prompt_eval_count'), response.get('eval_count'))
            if not all(type(n) is int and n >= 0 for n in counts):
                raise LocalAIError('Missing token telemetry; cannot validate this probe budget.')
            if counts[0] > OPTIONS['num_ctx'] - OPTIONS['num_predict'] or sum(counts) >= OPTIONS['num_ctx']:
                raise LocalAIError('Context budget exceeded; no result accepted.')
            if not isinstance(content, str) or not content.strip():
                raise LocalAIError('No final answer; thinking-only output is not an assessment.')
            result = strict_json(content)
            if not isinstance(result, dict):
                raise LocalAIError('Model must return a JSON object.')
            call['status'] = 'decoded'
            return result
        except (ValueError, TypeError, KeyError, ConnectionError, TimeoutError) as exc:
            call['status'] = 'failed'
            call['error'] = str(exc)
            raise

    def assess(self, packet, instructions, template):
        print('1/2 Assessing the synthetic requirement locally...', flush=True)
        # Deliberately exclude reference answers and prefilled template judgments.
        return self._chat('assessor', instructions, {'assignment': packet}, assessment_schema(packet))

    def challenge(self, packet, proposal, instructions):
        print('2/2 Challenging the proposal against the original sources...', flush=True)
        return self._chat('challenger', instructions, {'assignment': packet, 'proposal': proposal},
                          challenge_schema(packet, proposal))
