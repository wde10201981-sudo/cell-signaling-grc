# Local AI probe and assessment memory

Backend only. This is one synthetic limited-scope assessment using local `qwen3:8b`,
followed by a separate challenge request to the same model. It is not a benchmark
of generalization, model superiority or customer readiness. No GUI or operational
writeback. The old repository and DeepSeek are not used by this command.

## Start on Windows

Quit an Ollama tray instance before starting a server with these settings. In a
PowerShell terminal run the following and leave it open:

```powershell
$env:OLLAMA_NO_CLOUD = '1'
$env:OLLAMA_HOST = '127.0.0.1:11434'
$env:OLLAMA_NUM_PARALLEL = '1'
$env:OLLAMA_MAX_LOADED_MODELS = '1'
$env:OLLAMA_CONTEXT_LENGTH = '8192'
ollama serve
```

`start-local-ai.ps1` contains the same settings if local execution policy permits.
If the port is already in use, another server is already listening. Reuse a server
known to have cloud disabled, or quit that instance and start this one. Do not run
multiple servers. Setting variables in a second terminal does not reconfigure an
already-running server. Check the server's cloud-disabled log line.

In a separate PyCharm terminal, from this repository:

```powershell
git pull --ff-only
python -m cell_signaling.run_local_assessment --run
```

The request loads Qwen automatically; no interactive `ollama run` chat is needed.
If the installed model is missing, the command will say so. Only in that case use
`ollama pull qwen3:8b`. Model downloads need internet; analysis uses numeric loopback.
The adapter does not start/stop servers or download models automatically.
`ollama ps` in another terminal shows loaded models and GPU/CPU placement.

## What the probe does

The command selects only the assignment packet from the limited-scope synthetic
case. It never sends the authored reference response or expected summary to the model.
Schema enums constrain the allowed vocabulary, not the correct outcome. The template's
prefilled judgment is also excluded. Original evidence goes to both roles.

The adapter uses `/api/chat`, nonstreaming JSON Schema output, temperature 0,
`think: false`, an 8192-token context and a 3072-token output limit. Schema is also
supplied as prompt text. The model is fixed to local qwen3:8b; no environment variable
can silently switch it to DeepSeek or a cloud model. Proxy use and HTTP redirects
are disabled, and remote-model metadata is rejected. Cloud-disabled server startup
remains a deployment configuration; the adapter cannot independently attest it.

Preflight records the installed digest, model details and server version. Postflight
checks the tag still names the same digest. This is not cryptographic attestation of
inference. Requests have socket timeouts (180 seconds chat, 10 seconds metadata), a
24,000-byte prompt cap and a 2 MB response cap. Requests run sequentially without
retries. Truncated, malformed, tool-request or thinking-only responses are rejected.
Token counts and completion reasons are retained. Reported input tokens must leave
room for the requested output budget. The byte cap is not exact tokenization and
cannot independently prove that a server never truncated a prompt. This command is
restricted to the small fixture; bulk/customer inputs need deliberate chunking and
validated token accounting before use.

## Persistent memory: the first increment

Each attempted run saves a unique JSON file under `local-output/`, including failures:

- Exact assignment/source snapshot and input hash.
- Model/adapter/contract versions, settings and model digest observations.
- Role prompts, response schemas, final answer text and token/timing diagnostics.
- Proposed assessment, challenge, processing status and pending review state.

Hidden thinking text is not retained; its character count is recorded for diagnostics.
These files survive stopping Ollama. They are ignored by Git and never uploaded by this
command. They are local plaintext, editable records, not a production audit boundary.
Do not put raw customer data into this synthetic probe. An operating-system or disk
failure can still prevent saving; the CLI will surface a write error rather than claim
that a record was saved.

This is **run history**, not trained model memory. Prior answers are not automatically
injected into new requests, and a saved proposal never becomes verified evidence.
The model does not learn new weights from this history. Future retrieval must filter
by organization, cell, scope, period, source revisions, withdrawal status and human
review state. Authoritative policy, accepted decisions and AI hypotheses must remain
separate. No vector database or automatic retrieval is implemented in this increment.
The history_provenance layer is the logical home for these records; the current CLI
archive is not yet a durable cell-record store.

## Read the result

`expert_review_required` means structural checks and the challenge completed; it does
not mean the assessment is true. `needs_follow_up` means challenge disagreement or
uncertainty. `processing_failed` means a valid assessment was not accepted. A retained
proposal from a failed run is diagnostic only. `superseded` means the snapshot/model
changed. The probe does not change approvals, customer systems or existing cell state.

Read each population's three judgments and explanations in the saved JSON. For this
case, check whether the model preserves the cloud/on-premises boundary and whether its
citations actually justify its claims. Same-model agreement may reproduce shared errors.
Review reasoning before proceeding beyond this case; do not silently tune away failures.

Offline tests use mock transports and authored responses; they establish adapter
behavior only. The developer environment cannot exercise the user's Windows GPU.

References: [Ollama chat API](https://docs.ollama.com/api/chat),
[structured outputs](https://docs.ollama.com/capabilities/structured-outputs),
[local configuration](https://docs.ollama.com/faq),
[model inventory](https://docs.ollama.com/api/tags).


### Scope-citation correction

Adapter `ollama-probe-0.2` uses assessment contract 0.2. It requests explicit
support versus scope-limitation citations and can cite structured population fields.
This fixes a false rejection of an on-premises abstention explained by AWS-only control
scope. It does not permit AWS evidence to establish on-premises coverage. Earlier run
files remain unchanged; rerun the same command after pulling the correction. The server
and model do not need restarting because the new schema/instructions travel per request.
