# First AI assessment contract

Draft 0.2. Backend only. This implements a model-independent input/output boundary
and a bounded coordinator. The contract itself has no model dependency, UI, operational writeback,
automated approval, or claim of AI accuracy. Existing demonstrations remain unchanged.

## Where intelligence belongs

Each cell owns its scoped assessment process. The six layers organize information;
they are neither six agents nor six sequential reasoning steps. A deterministic
coordinator passes an explicit assignment to an assessment role, then the original
sources and proposal to a challenge role. The roles may eventually use a shared
model service, with independent requests and scoped access. Shared models can share
errors. Neither role can grant itself permissions or override the human owner.

This first profile asks whether controls and evidence support one monthly privileged
access review requirement, population by population, for a completed period. It does
not establish continuing effectiveness or organization-wide compliance.

## Assignment: data, not customer-specific code

`examples/assessment_cases.json` contains four draft synthetic assignments and authored
reference responses. Expected responses live outside the packet sent to an agent.
They are not an expert-approved or held-out benchmark. New customers must supply
records and configuration; their facts must not be encoded as decision branches.

The packet includes contract/rubric versions, organization, commissioning cell,
question, requirement reference, explicit criteria, populations, evaluation period,
evaluation date, limitations, six-layer source indexes and source snapshots.
Every source has organization/cell/record/revision, population, observation/receipt
 dates, status, location and text. A local source ID aliases that exact reference.
Empty layer indexes are explicit; no invented content fills them. Candidate controls
can include unmapped controls. The caller must assemble relevant counterevidence and
access limitations, not just favorable records. No automatic retrieval is implemented.

| Layer | Assignment content / destination |
|---|---|
| identity_scope | Population and entity evidence; packet states the evaluated populations |
| governance_obligations | Exact requirement text and version; criteria are caller-supplied, versioned interpretations |
| risk_controls | Control descriptions, scope, proposed mappings and known issues |
| evidence_assurance | Implementation and execution evidence, including counterevidence |
| work_decisions | Earlier decision context; new questions/actions remain proposals |
| history_provenance | Earlier relevant records; coordinator returns input snapshot, hashes, proposal and challenge |

This profile's observed_on means source observation date, not policy effective date.
Receipt cannot be later than evaluation. Detailed execution/effective dates remain
in source text and must be interpreted. This is not a general freshness/time engine.
Scoped source snapshots must retain enough context; ingestion must not strip a source
into a falsely favorable excerpt. Namespace checks are not authentication.

## Required answer

One row per population; each row separates **control fit**, **implementation** and
**execution**. Every dimension includes a state, explanation and typed source citations.
States are supported, not_established, contradicted and conflicting. Missing evidence
is not proof of failure. Conflicting assertions require reconciliation, not voting.
Positive/adverse judgments need a relevant source type; conflicts need multiple
references. Validation checks reference existence, excerpt/field matching, citation purpose and declared scope.
It cannot establish that the excerpt entails the conclusion or that source facts are true.

Questions and actions are proposals only. No agent-supplied approval, overall grade,
extra output fields or executable instructions are accepted. Summary labels are computed
conservatively from the dimension states: supported_coverage, partial_support,
insufficient_evidence, adverse_evidence or needs_review. These are reporting labels,
not compliance certification. In the missing-evidence fixture, control fit is supported
but execution/implementation are unknown, so the summary is partial_support; the
individual dimension results must always be shown alongside the summary.

## Coordinator and failure behavior

`run_assessment(packet, assessor, challenger, current_hash)` performs at most two
adapter calls: one assessment and one challenge. The challenge must address every
population/dimension against original sources and explicit criteria. Instructions
include explicit response structure and source-as-data boundaries. This is not a
proven prompt-injection defense; there are no tools granted by this coordinator.

The caller supplies a trusted current-snapshot hash function. A changed hash marks
results superseded. A disagreement/uncertainty routes needs_follow_up, with no accepted
summary. Malformed answers and timeout/connection errors produce processing_failed,
never a fabricated coverage grade. Invalid intake raises ContractError before any agent
runs. Valid completed insufficient-evidence findings remain substantive assessments.

Even agreement leaves expert_review_required. The coordinator never modifies the
existing cell records, approvals, prior coverage exercise or customer systems. Returned
snapshots/history are in memory, not durable or tamper-resistant audit records. A hash
is not authentication or an atomic commit check. A future persistence boundary must
atomically compare input revision and save current results, then invalidate dependent
assessments on changes. This callback check alone cannot prevent a later race.

## Execution and next gate

```powershell
python -m cell_signaling.assessment_demo
python -m unittest discover -s cell_signaling -v
```

No Ollama is required. The demo uses authored responses and an explicitly simulated
challenge; it verifies contract behavior only. Tests include malformed outputs, missing
populations, forbidden approval fields, source scope, withdrawn evidence, stale snapshots,
review disagreement, missing evidence and timeout handling.

Before a real model trial: review these criteria and reference judgments; add a model
adapter with bounded input/output size, timeouts, model/digest/settings metadata and
JSON decoding; preserve prompt/version and response telemetry. The adapter must supply
its own timeout because ordinary synchronous Python callbacks cannot be interrupted
by this coordinator. Then freeze the contract and evaluate unseen wording and cases,
including misleading mappings, malicious source instructions and disputed identities.
Do not tune on expected responses and call that a generalization test. Do not authorize
autonomous operational actions from these results. Human review by exception remains a
future operating target requiring measured error rates and appropriate sampling.


## Local adapter implementation

The separate [local AI probe](LOCAL-AI.md) now implements the bounded Ollama adapter
and local run archive described above. Its tests use mocked responses; real model
reasoning still requires a local run and expert review. The four authored fixtures
remain drafts, not an approved or held-out benchmark. Automatic memory retrieval and
operational authority remain unimplemented.


## Citation purposes (contract 0.2)

The first local run exposed a contract defect: an AWS-only control was cited to
explain why on-premises coverage was not established. The old validator treated
that reference as an attempt to prove on-premises coverage and rejected it.

Citations now explicitly contain `source_id`, `purpose`, `field` and `value`:

```json
{"source_id":"C1","purpose":"scope_limitation","field":"populations","value":["aws"]}
```

This is permitted only in a `not_established` finding for a population absent from
that exact source population array. The complete array must match; a prose description
that merely says "stated population" is insufficient to establish an AWS boundary.
It establishes the limitation of that source, not the absence of every other control
or evidence item. Explanations must keep absence claims scoped to the supplied packet.

For ordinary factual support, use `purpose: support`, `field: text`, and an exact
excerpt in `value`. The source must include the row population. Supporting population
metadata may also be cited, but cannot replace required text support for control fit,
implementation or execution. Conflict requires text from at least two distinct sources;
two fields of one source do not count as independent conflicting sources.

Limitation references cannot satisfy positive/adverse/conflict evidence requirements,
cannot refer to inactive sources, and cannot claim that a source excludes a population
which it includes. All source, organization, snapshot and approval boundaries remain.
The challenge must still evaluate whether each explanation follows from its sources;
structural validation does not establish semantic correctness.

This is a versioned response change to `coverage-assessment-0.2`; prior saved output
is neither silently converted nor approved. The local schema, instructions and authored
fixtures were updated together. A diagnostic replay with manually revised citation
representation is a regression exercise, not a new live model result. New scope tests
cover both valid abstention explanations and attempts to bypass the original boundary.
