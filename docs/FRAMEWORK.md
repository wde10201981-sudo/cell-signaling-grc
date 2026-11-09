# Cell Signaling GRC — framework foundation

**Draft 0.2 · November 4, 2026 · Architecture specification for review**

This document defines the proposed framework contract. It does not describe capabilities already implemented. The Python skeleton currently supports one in-memory cell, layered records, explicit links, synchronous signals, and direct-neighbor requirement-change discovery. It has no AI, inter-cell transport, durable storage, authenticated authority or automatic assessment lifecycle.

## 1. Purpose and unit of responsibility

A cell is a bounded unit of organizational responsibility that maintains context, evaluates evidence, reasons about change and acts within delegated authority. An organization adopts the framework by describing its responsibilities as cells and mapping existing information into their layers.

The cell-signaling analogy guides the architecture: cells receive information, interpret its relevance, coordinate internal responses and communicate with other cells. It does not establish correctness, biological equivalence or autonomous authority.

A cell is not necessarily a department, database, application, AI agent or legal entity. Its boundary follows an accountable responsibility and scope. One system may supply several cells, and a cell may reference several systems. Information may remain in existing systems if stable, authorized, version-specific references are available.

Every cell uses six common conceptual layers. Its profile specializes their contents and reasoning questions. The framework does not require identical physical schemas or one model per layer. AI reasons across the layers; the layers are not a six-step pipeline.

The intelligence is logically part of each cell. Model infrastructure may be shared, but context, authority and access remain scoped to the calling cell. There is no assumed all-knowing central AI with authority over every cell.

Homeostasis is a core framework requirement: a cell must monitor the conditions needed to fulfill its mandate, detect deviations, coordinate authorized responses and verify their effects. It is an ongoing feedback process, not a static compliant/noncompliant label. The definition and mechanics below are proposed engineering requirements for this framework, not claims about biological behavior.

## 2. Minimum valid cell

A cell must declare the following manifest. These are logical fields, not a committed serialization or database design.

| Declaration | Required meaning |
|---|---|
| Identity | Organization namespace, stable cell ID, name, manifest revision, framework contract version and profile ID/version. |
| Mandate | The questions and responsibilities the cell owns, plus explicit exclusions. |
| Scope | Identifiable populations, services, platforms or organizational boundaries; scope revision and effective period. Unknown scope portions remain explicit. |
| Accountability | Accountable owner and escalation authority, expressed as resolvable organizational identities or roles. |
| Layers | A declaration for each of the six layers, including its records, source mappings or referenced provider. |
| Authority | Permitted analytical activities and actions, required approvals, limits and the source/version of that delegation. |
| Capabilities | Supported incoming/outgoing signal types and versions, supported analysis questions, and explicit unsupported capabilities. |
| Data policy | Source access, permitted recipients, classification, retention and evidence-sharing restrictions. |
| Lifecycle | Active, suspended or retired status, with effective time and reason. |
| Homeostasis policy | Versioned objectives, measured conditions and acceptable bounds, observation/freshness rules, response and escalation authority, recovery evidence, and affected peer dependencies. Unknown or unconfigured conditions prevent claims of confirmed stability. |

Each layer declares one of: **managed here**, **referenced/delegated**, **not yet available**, or **not applicable with rationale**. Delegation identifies the responsible provider and retrieval contract; it does not remove the cell owner's accountability. Unavailable data remains unavailable rather than being invented to make the manifest complete. Identity, authority and provenance responsibilities cannot be declared not applicable.

A structurally valid cell is not automatically ready for every analysis. Readiness is evaluated for a specific question, scope and action. Missing evidence can permit a bounded information request while preventing a substantive assurance conclusion.

Cells with overlapping scope must declare which responsibility each owns. Conflicting claims of ownership or authority require resolution; the model does not silently choose a governing cell.

## 3. Six-layer information contract

| Layer | Common responsibility | Minimum information when relevant to the question |
|---|---|---|
| `identity_scope` | Establish whose circumstances and which populations are represented. | Entity identifiers and source namespaces, scope predicates or population references, exclusions, owners, business dependencies and effective periods. |
| `governance_obligations` | Represent what must be achieved and why. | Source requirement text and location, authority, version, applicability, effective dates, interpretation, exceptions and satisfaction criteria. Separate original text from an AI interpretation. |
| `risk_controls` | Describe exposure and how obligations are addressed. | Risk statements, control objectives/mechanisms, responsible owners, scope, dependencies, compensating controls, known issues, and requirement-mapping rationale. |
| `evidence_assurance` | Represent what observations support or challenge claims. | Source references, observation/collection times, tested population, method, result, limitations, freshness policy, and evidence status such as current, superseded or withdrawn. |
| `work_decisions` | Represent proposed responses, authorized judgments and follow-up. | Information requests, proposed actions, owners, due dates where established, assessment references, decision authority/rationale, approval state and closure evidence. |
| `history_provenance` | Preserve the basis and evolution of reasoning and action. | Versioned source references, received signals, processing outcomes, prior assessments, model/prompt/rule versions, reviewer decisions and causal links. |

The framework must distinguish **not supplied**, **not accessible**, **not applicable**, **not established**, and **evidence of failure**. Those are not interchangeable states. A profile defines domain-specific fields and completeness rules without weakening these distinctions.

## 4. Records, identity and relationships

A reference must identify the organization, cell or source namespace, record ID and exact revision/snapshot. A mutable URL by itself is not sufficient to reproduce an assessment. Record IDs from two customer organizations must never be merged because their strings match.

Entity matching has an explicit state: proposed, confirmed or disputed, with supporting evidence and the responsible decision. A model's name similarity is not confirmation. An unresolved match limits any inference that relies on it.

A relationship needs source/target references, a defined directional type, applicable scope, effective period, source or rationale, and review state. For example, `implements` must identify which obligation or clause and which population the control addresses. A declared mapping remains a claim to examine.

Relationship traversal finds candidate impacts. It does not prove coverage, causation or operational access. A profile defines which relationship types can propagate a particular change, in which direction, and with what stopping rules. Discovery may be bidirectional; inference must preserve the meaning and direction of each relationship.

The framework must support bounded multi-hop impact discovery with visited-record tracking. If a traversal limit is reached, the result is explicitly incomplete. A long path does not strengthen evidence. Conflicting records remain visible and are evaluated against their scopes and effective times; a newer observation is not automatically evidence that an older historical claim was false.

## 5. Cell-to-cell signal contract

The exchange unit is an envelope plus a versioned, signal-specific payload. Cells may have different internal profiles while sharing this contract.

| Envelope group | Required content |
|---|---|
| Identification | Contract/schema version, unique signal ID and a precisely defined signal type. |
| Sender and destination | Organization namespace, sending cell, intended recipient cell or authorized routing scope. |
| Semantics | Whether this is an observation/change, analysis request, assessment proposal, authorized decision or processing response. |
| Time and state | Emitted time, relevant observed/effective times, and referenced record/scope revisions. |
| Subject | Namespaced entity/record references and explicit applicable scope or an explicit statement that scope is unresolved. |
| Causality | Correlation ID for the workflow; parent signal ID where this signal responds to another. |
| Support and limits | Evidence references or an explicit reason none exist, uncertainties, exclusions and relevant contradictory-source references. |
| Handling | Information classification, access constraints, deadline/expiry if applicable, and routing/lifecycle metadata needed by the transport. |
| Payload | Data defined by the named signal schema; an empty or arbitrary dictionary does not establish semantic validity. |

A decision signal additionally references the decision record, authorizer, delegated authority, approved action/scope and exact assessment version. Claims of identity or authority inside a payload are not authentication. Receivers must check the authenticated sender and the organization's authority/access policy independently. Mechanisms for identity, transport and storage are deployment decisions still to be selected.

Suggested initial signal families: `requirement.changed`, `evidence.observed`, `evidence.withdrawn`, `analysis.requested`, `assessment.proposed`, `decision.authorized`, and `processing.responded`. Exact schemas remain to be specified and tested. The skeleton's `requirement.impact_assessed` is candidate discovery, not a completed coverage assessment.

### Receiver obligations

1. Validate schema/version, authenticated origin, recipient, organization boundary and access policy before interpreting the content.
2. Record receipt and a processing outcome separately. Receipt, successful processing and approval are distinct facts.
3. Deduplicate by sender namespace and signal ID. A retry with the same ID and same content must not repeat consequential work; the same ID with different content is an integrity error.
4. Resolve record/entity/scope references. Inaccessible evidence produces an explicit limitation or information request, not a fabricated finding.
5. Check ordering using record revisions and effective times. Late events must not silently overwrite newer state. Corrections and withdrawals supersede prior references while preserving historical context.
6. Process only supported capabilities. Unsupported schemas, conflicting identities and unauthorized actions are rejected or held with a reason; they are not interpreted opportunistically by AI.
7. Bound propagation, retries and processing duration. Dead-letter/escalation handling is required when a message cannot be processed. A cell must not endlessly echo another cell's assessment as fresh independent evidence.

Cells may disagree. Each keeps its scoped assessment and evidence; disagreement initiates clarification or escalation. Majority agreement among cells or models does not establish truth. Reusing a peer's derivative conclusion must retain its original evidence lineage rather than double-counting it as independent corroboration.

## 6. AI analysis contract

AI performs domain interpretation and proposes justified judgments. Deterministic framework functions validate structure, resolve references, apply explicit authority rules and preserve history. Passing those checks does not prove a model's reasoning is correct.

Every analysis is commissioned with a specific question, subject/scope, evaluation time, trigger and permitted output/actions. The analysis must record the input snapshot, source access limitations, relevant policy/profile versions and model/prompt configuration.

The reasoning cycle is:

- Establish the relevant change and applicability.
- Discover candidate impacts using typed relationships.
- Assemble relevant supporting, conflicting and missing evidence across layers.
- Evaluate a specified question under a versioned domain rubric.
- Produce a scoped assessment, uncertainties, information requests and proportionate proposed actions.
- Check factual support and authority before committing any derived state or forwarding a decision.

An assessment must contain its question, scope, source versions, claims and supporting source locations, counterevidence, unresolved issues, concise reasoning summary, proposed conclusion, proposed actions and review state. Preserve usable explanations and evidence lineage; hidden model reasoning is not required as an audit artifact. Numerical confidence is optional and cannot substitute for evidence or imply calibrated probability.

Domain profiles define the conclusion vocabulary. A security-coverage profile may use Fully covered, Partially covered, No coverage and Insufficient evidence. An identity-operations profile may answer whether a named review completed for a specified population. The framework must not force every question into one compliance grade.

Analytical outcomes and execution failures remain separate. A completed assessment of insufficient evidence is a substantive result. A timeout, malformed answer, failed retrieval or unsupported operation is a processing failure and must not become a fabricated coverage judgment.

If relevant inputs change during analysis, preserve the old result as a historical/superseded result and schedule an assessment of the new state. Do not present the old result as current. After a completed assessment, changes invalidate the dependent derived state based on explicit dependency records; uncertain dependency discovery broadens review rather than silently preserving confidence.

An organization's facts cannot be embedded as bespoke application code. Adopters supply records, mappings, scope definitions and policy/profile configurations. Shared code implements the framework's common rules.

### 6.1. Homeostasis: the feedback contract

Each cell must sustain acceptable conditions for its mandate as data, obligations and dependencies change. Acceptable does not mean unchanged, risk-free or universally compliant. It means the declared conditions are supported by current observations and fall within authorized bounds. Known gaps and accepted risks remain visible as distinct facts.

**Define the condition before selecting an action.** Each monitored condition declares:

- A stable condition ID, accountable owner, applicable scope and policy version.
- The objective, indicator or evidence-based predicate, units/denominator where relevant, and source of the authorized bounds.
- How it is observed, the acceptable evidence age and coverage, evaluation cadence, and relevant change/dependency triggers.
- Warning, breach and recovery rules; response priority and maximum tolerated delay.
- Permitted responses, approval requirements, escalation destination and safe fallback.
- Required evidence of recovery, any sustained observation period, and dependent cells whose objectives or operations may be affected.

Conditions may concern evidenced control execution, unresolved coverage gaps, overdue decisions, stale evidence or the cell's own ability to process signals. These are separate dimensions. A functioning message bus does not establish control effectiveness; a favorable aggregate score must not hide a critical breach or unknown population.

**Close the feedback loop:** observe → compare against authorized conditions → diagnose the deviation and uncertainties → select an authorized response → carry out or request that response → obtain fresh evidence → verify recovery. If a response fails, produces adverse effects or cannot be verified, reassess and escalate rather than declaring success.

The AI interprets evidence, proposes causes and compares response options. A causal explanation remains a hypothesis unless established. The framework enforces authority, evaluates deterministic bounds where applicable and records the result. Restoration is established through evidence, not by a model saying “fixed” or by a task being marked complete. Autonomous responses require an explicit, bounded delegation; homeostasis does not create new authority.

Time itself can disturb a cell. Evidence can expire, exceptions can lapse, deadlines can pass and a peer can become unavailable without any new source event. The design therefore requires scheduled reevaluation in addition to event-triggered analysis. Absence of incoming signals is not evidence of stability.

**Represent condition and observability separately.** For each condition, use a proposed state vocabulary of within bounds, warning, outside bounds, recovering and unknown, together with observation freshness/adequacy and the last evaluation time. Preserve a last-known breach when visibility is lost; append unknown current observability rather than replacing that breach with a reassuring status. Recovery requires the declared evidence and confirmation window. Missing or contradictory evidence cannot establish within-bounds status. Any cell-level summary must expose material breaches and unknowns rather than average them away.

**Avoid repeated overcorrection.** Profiles must define deduplication, retry/action limits, a recheck interval and, where appropriate, different thresholds for entering and leaving an alert state. These rules prevent small measurement changes from repeatedly opening and closing the same issue. Critical conditions retain immediate escalation rules; quiet periods cannot suppress required urgent handling. Irreversible or high-impact changes need explicit authority and a containment/recovery plan where applicable.

**Coordinate local and shared stability.** Before proposing a material correction, assess its known dependencies and possible effects on peer cells. For example, removing a privileged account may improve an access-control indicator while disrupting a dependent business service. A local improvement does not establish organizational recovery. Obtain the required peer input and authorization, disclose unknown dependencies, and escalate conflicting objectives to the accountable authority. Time-bounded emergency authority must be established in advance; the AI cannot invent it when coordination is slow.

A cell must not restore a green status by hiding evidence, excluding an inconvenient population, closing a gap without support or relaxing a threshold. Authorized changes to objectives, scope or risk disposition are versioned decisions and trigger reassessment; they are not retroactive evidence of recovery. Adaptation to a legitimate new requirement is supported without confusing a changed target with an improved condition.

Suggested lifecycle signals are `condition.deviation_detected`, `response.proposed`, `response.executed`, `recovery.observed` and `recovery.verified`. Each uses the common envelope and references the condition/policy revision, scope, observations, response/authorization and causal chain as applicable. Execution and recovery are separate events. State reversals retain their history. These signals and the feedback controller are not implemented in the current skeleton.

## 7. Decision authority and action boundaries

| Activity | Proposed default boundary |
|---|---|
| Interpret records, identify candidate impacts and propose assessments | AI may perform within authorized data scope. |
| Flag derived assessments for review or generate information requests | Framework may perform when explicitly permitted by cell policy; retain source/decision history. External communication still follows recipient authorization. |
| Accept risk, approve exceptions or issue formal assurance | Requires the designated organizational authority; an AI proposal is not authorization. |
| Change access, configurations or other operational systems | Requires a separately authorized action contract, target/scope checks and execution verification. No such integration exists in the skeleton. |
| Close an issue | Requires defined closure evidence and the responsible authority; completion of a task alone is not proof the risk is resolved. |

A peer cell's authorization applies only within its delegation. It does not transfer decision rights to this cell. Risk acceptance changes the disposition of a gap, not whether coverage has been evidenced.

A valid authorized decision references an exact assessment, scope and input snapshot. Subsequent changes trigger reconsideration of continuing validity without erasing the fact that the earlier decision was made. Human reviewers must be able to challenge an assessment and record an alternative conclusion with rationale and evidence; they are not merely approving a model's wording.

## 8. Adoption and extension

An adopter defines cell mandates/owners, maps existing data, resolves identifiers, selects profiles, establishes authority and access boundaries, and tests its signal interactions. Profiles may add record types, relationship semantics, analytical rubrics and signal payload schemas. They may not remove the common requirements for scope, provenance, uncertainty, authority or safe failure.

Contract/profile versions must be explicit. Breaking semantic changes require a new compatible agreement or migration; unknown versions are not assumed compatible. Physical transport, persistence, model provider and user interface remain replaceable deployment choices.

## 9. What we will settle before adding intelligence

The defaults in this draft are proposals for review, not established banking standards or confirmed customer requirements.

Open decisions include: the first cell's exact mandate and decision rights; the adopter's authoritative entity/scope vocabulary; evidence sufficiency and freshness rules by domain; ownership conflicts; approved inter-cell authentication/data-sharing mechanisms; retention and replay requirements; homeostatic conditions, bounds, recovery rules and cross-cell conflicts; and domain evaluation cases reviewed by subject-matter experts.

The next bounded implementation should express one manifest and one versioned signal contract as executable validations, then demonstrate an exchange between the two profiles in [CELL-PROFILES.md](CELL-PROFILES.md). First check references, scope, authority, duplicate delivery and withdrawal behavior deterministically. Add a narrowly defined AI question only after its inputs, rubric and expert-reviewed expected outcomes are agreed. No app interface is needed for these framework checks.



## Bounded implementation references

The six-layer specification above remains broader than the implementation. The
[two-cell exercise](COVERAGE-EXERCISE.md) tests structured timing and dependency rules.
The [first assessment contract](ASSESSMENT-CONTRACT.md) adds a model-independent
assignment/response boundary and two-role coordinator with synthetic fixtures.
These deterministic exercises do not establish AI reasoning accuracy, production transport or autonomous decision rights. A separate [local AI probe](LOCAL-AI.md) connects the assessment contract to Ollama for a bounded synthetic trial.
