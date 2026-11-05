# Contrasting cell profiles and contract exercises

**Draft 0.2 · Design examples, not executable implementations or completed tests**

These profiles exercise [the common framework](FRAMEWORK.md) without requiring identical operational records. All names, populations and events below are synthetic. A real organization must define its own responsibilities, evidence rules and delegations.

## 1. Common foundation, different responsibilities

Both cells belong to the example organization `ORG-DEMO`. They retain the six common layers and the same signal envelope. Each declares a distinct mandate, source mappings, capabilities and authority. Profile names and IDs below are proposed examples, not an exhaustive catalog of permissible cells.

| Property | Security assurance cell — `CELL-SEC` | Identity operations cell — `CELL-ID` |
|---|---|---|
| Profile | `security-coverage`, draft 0.1 | `identity-operations`, draft 0.1 |
| Mandate | Evaluate evidence-supported coverage of applicable security requirements across its declared scope. | Represent identity populations, access-review execution and operational exceptions within its declared scope. |
| Scope in this example | Production systems, including cloud and on-premises; workforce and service-account populations. | Workforce administrator accounts in the cloud population only. |
| Core question | Does the evidence support the claimed coverage, and what needs review? | Was the specified access review performed for this population, and what remains unresolved? |
| Accountability | Security assurance owner. | Identity operations owner. |
| Explicit exclusions | Does not own identity-system configuration or accept business risk by default. | Does not attest to all organizational requirements, on-premises systems or service-account coverage. |
| Example sources | Requirements register, control catalog, assessments, issues and approved exceptions. | Identity inventory, role assignments, review campaigns and remediation records. |
| AI role | Interpret requirements, challenge mappings, reconcile evidence and propose scoped assurance conclusions. | Interpret operational records, identify evidence gaps and propose review/remediation follow-up. |

The security cell's broader scope does not make it the administrative parent of the identity cell. Dependency, organizational hierarchy and authority are separate relationships. The identity cell's narrower scope does not make its evidence less useful; it limits the conclusions that evidence can support.

## 2. Layer contents

| Common layer | Security assurance specialization | Identity operations specialization |
|---|---|---|
| Identity and scope | Requirement applicability, business/system populations, owners and source-entity mappings. | Account populations, identity types, ownership, platform boundaries and exclusions. |
| Governance and obligations | Authoritative requirements, scope, versions, effective dates and agreed assessment rubrics. | Applicable access-review obligations, execution procedures and operational decision limits. |
| Risk and controls | Requirement/control mappings, risk scenarios, compensating coverage, issues and dependencies. | Access-review mechanisms, role-assignment controls, privileged permissions and operational exceptions. |
| Evidence and assurance | Cited observations and scoped peer assessments, with source lineage and limits. | Versioned campaign results, sampled/reviewed populations, reviewer records and unresolved exceptions. |
| Work and decisions | Assessment drafts, clarification requests, reviewer conclusions and approved dispositions. | Campaign work, proposed remediation and decisions by authorized identity owners. |
| History and provenance | Prior requirement/control assessments, changed dependencies and authorizations. | Prior population snapshots, review changes, execution records and correction/withdrawal signals. |

The shared layer purposes remain stable. Their domain fields and analytical questions differ. A business-service or third-party cell may later add a different profile through the same extension rules; those profiles need not be designed now.

## 3. Worked exchange: a review-frequency change

### Starting facts

- `CELL-SEC` holds requirement `REQ-ACCESS` revision 1 and a prior scoped assessment.
- Revision 2 changes the required review frequency from quarterly to monthly, with an explicit future effective date.
- `CELL-ID` owns control `CTRL-REVIEW` and evidence `EVD-CAMPAIGN`, each with explicit versions.
- The relationship between the requirement and control covers the cloud workforce administrator population only.
- The requirement also includes service accounts and on-premises administrators. No provider has yet established coverage for those populations in this example.

The effective date matters: a quarterly record from before the monthly requirement took effect is not automatically a violation of the new requirement. The question may be readiness for the future obligation rather than current failure.

### Intended processing

1. **Register the changed obligation.** Update the requirement through an authorized source change, preserve revision 1, and emit `requirement.changed` identifying both revisions, the effective time and affected scope. The signal alone does not substitute for updating the source record.
2. **Discover dependent assessments and controls.** `CELL-SEC` identifies candidate impacts using relationship types and scope. The prior assessment is retained and flagged for reconsideration against revision 2.
3. **Request a scoped operational analysis.** `CELL-SEC` sends `analysis.requested` to `CELL-ID`: what evidence establishes monthly execution/readiness for the population within your mandate? The request references the exact obligation, effective date and entity definitions. It does not order account changes or widen `CELL-ID`'s authority.
4. **Evaluate operational support.** `CELL-ID` evaluates its campaign records and returns `assessment.proposed`, with input versions, the reviewed population, relevant period, source evidence and limitations. Its reply may establish a completed review for cloud workforce administrators; it does not establish service-account or on-premises coverage.
5. **Reconcile the broader requirement.** `CELL-SEC` evaluates that reply and its original sources against the broader requirement. A defensible outcome identifies established coverage for the evidenced subset and explicitly unproven remaining scope. It requests information from the responsible owners rather than inventing absent controls or declaring them nonexistent.
6. **Route the proposed decision.** The security assurance owner reviews the scoped conclusion. A formal decision requires the authority and exact assessment references in the framework contract. An operational remediation action would require a separate identity-owner authorization.
7. **Respond to later changes.** If `EVD-CAMPAIGN` is corrected or withdrawn, `CELL-ID` publishes the affected evidence revision. `CELL-SEC` marks dependent current conclusions for reassessment while preserving earlier decisions as historical records.

A reply is not automatically an approved decision. A peer's assertion of full coverage within its own population does not establish full coverage of the requesting cell's larger population. The framework carries both scopes through every step.

### Homeostasis across the two profiles

Each profile declares its own conditions under the shared feedback contract. Numeric limits and review periods are deliberately left for the responsible organization to approve.

| Cell | Example condition | Disturbance | Proposed response | Evidence needed to establish recovery |
|---|---|---|---|---|
| Security assurance | Material coverage assertions remain supported by current evidence for their declared populations; unresolved gaps stay within explicitly authorized handling limits. | Supporting evidence expires, an obligation changes, or an uncovered population is discovered. | Reassess dependent conclusions, request evidence, assign authorized follow-up and escalate overdue material gaps. | Current evidence and a reviewed assessment for the affected scope; unresolved exclusions remain visible. A risk disposition alone does not establish coverage. |
| Identity operations | In-scope privileged-access reviews execute at the required cadence and unresolved exceptions are handled within authorized limits. | A review is missed, evidence is withdrawn, or a privileged assignment lacks the required approval. | Determine the affected population, request owner review and propose authorized corrective actions with service-impact checks. | Evidence of the actual review/correction, treatment of exceptions and confirmation that required recovery criteria are met. A completed ticket alone is insufficient. |

In the frequency-change example, the cells must evaluate readiness before the effective date, detect any unfulfilled obligation when it becomes applicable, and revisit execution after the operational response. Receiving a new procedure does not establish that monthly reviews actually occurred.

A correction in the identity cell may affect service continuity elsewhere. These two cells must identify that dependency and obtain the relevant service owner's/cell's input when required; the example does not assume that service continuity has been evaluated. If no responsible peer is available, record the unresolved impact and follow the defined escalation or emergency policy.

The security cell and identity cell can be in different states at the same time. The identity cell may have restored its own cloud workforce review condition while the security cell still has unproven service-account coverage. Local recovery must not automatically turn the broader requirement green.

## 4. Design acceptance cases

These are requirements for future executable tests and expert evaluation. They have not been run as model-quality tests. Contract-validation cases can be deterministic; interpretation of coverage needs an agreed rubric and expert-reviewed source packets.

| Case | Expected behavior |
|---|---|
| Different internal record schemas | The two profiles exchange a supported signal using common identity, scope and evidence references without adopting identical tables. |
| Narrower evidence scope | An identity assessment for cloud workforce accounts cannot establish full coverage of service accounts or on-premises administrators. |
| Missing scope mapping | The receiving cell requests clarification or abstains from that inference; it does not equate similar labels. |
| Ambiguous cross-system entity ID | Entity matching remains proposed/disputed until supported. Dependent conclusions retain the limitation. |
| Duplicate delivery, same content | No duplicated assessment job or consequential action; the earlier processing result can be acknowledged. |
| Same signal ID, changed content | Integrity error; no silent replacement. |
| Unsupported signal version | An explicit unsupported-version outcome; no AI improvisation around the contract. |
| Requirement change with future effective date | Distinguish present compliance/coverage from future readiness; do not retroactively apply a new frequency. |
| Evidence from different populations or periods | Do not label it contradictory until the scopes and times are shown to overlap in a relevant way. |
| Inaccessible source evidence | Record access limitations and request authorized evidence; do not manufacture a coverage result from an inaccessible citation. |
| Source withdrawal or correction | Identify dependent current conclusions, mark them for reassessment, and preserve historical records. |
| Late old signal | Retain its historical meaning without overwriting the newer record revision. |
| New evidence arrives during analysis | Bind the result to its old snapshot and prevent its presentation as current; schedule evaluation of the new snapshot. |
| Peer cell repeats our own conclusion | Retain shared lineage; do not count the echo as independent corroboration or start an unbounded signal loop. |
| AI proposes risk acceptance | Keep it a proposal pending authorized disposition. Acceptance does not turn an uncovered requirement into evidenced coverage. |
| Peer sends an unauthorized account-change instruction | Reject the action even if its message schema is valid or its sender is authenticated. |
| Source text contains instructions to the model | Treat them as data; they cannot change tools, scope, policy or approval authority. |
| Model timeout or malformed output | Processing failure, not a negative or positive assurance conclusion. Preserve diagnostic status and permit bounded follow-up. |
| Multi-hop exploration reaches its limit | Explicitly incomplete impact discovery; no claim that all affected records have been identified. |

### Additional homeostasis acceptance cases

| Case | Expected behavior |
|---|---|
| Evidence ages past its validity without a new event | Scheduled evaluation detects the loss of support and reevaluates dependent conditions. |
| A remediation ticket closes without outcome evidence | Work completion is recorded, but the condition is not declared recovered. |
| Small observations alternate around an alert threshold | Approved entry/exit rules prevent repeated contradictory actions; material breaches still escalate. |
| Observability is lost after a breach | Preserve the last-known breach and mark current visibility unknown; do not report recovery. |
| A local correction threatens a dependent service | Surface the tradeoff, seek required coordination/authorization, and do not assume organization-wide improvement. |
| An action fails or the same condition repeatedly relapses | Record outcomes, enforce action/retry limits and escalate; do not loop indefinitely. |
| A model proposes weakening a target to restore stability | Treat it as an unauthorized policy change unless separately approved; never record it as evidence of recovery. |
| Valid scoped recovery evidence arrives | Verify the policy's recovery criteria/window, update only the supported condition/scope and notify dependent cells. |
| A critical breach is masked by an otherwise favorable summary | The material breach remains visible and actionable; the summary cannot claim confirmed overall stability. |

## 5. First implementation boundary

The first framework exercise should instantiate these two manifests and validate one scoped request/reply exchange with synthetic, versioned references. Include rejection of an unauthorized decision and handling of a repeated message. Add one synthetic disturbance-and-recovery cycle with scheduled evidence expiry and a check that work completion alone cannot establish recovery. Do not connect bank systems or grant operational write authority for this exercise.

The first AI exercise should answer one agreed question from a fixed evidence packet, such as whether the peer's evidence supports the specified population and period. The correct result must be judged from the underlying sources, not encoded as an answer in the packet. Evaluate successful completion, factual support, scope preservation and appropriate abstention separately. A correct label with defective reasoning is not a passing assessment.

This sequence tests the common structure before expanding the number of agents, cells or integrations.
