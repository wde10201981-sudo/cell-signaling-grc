# Two-cell coverage exercise

Synthetic, in-memory demonstration; six layers unchanged. Run
`python -m cell_signaling.coverage_demo`. No Ollama server is required.

`CoverageExchange` connects two existing GRCCell instances locally. Identity
supplies typed execution evidence; security assesses the specified requirement
revision, population and cycle. Requests/replies illustrate messaging only:
configured identities are trusted inputs, not authenticated senders. The original
SignalBus is unchanged; the exercise has its own idempotent delivery ledger.

## Semantics

- Exact namespaced requirement/evidence revisions and population identifiers.
- Calendar dates, inclusive deadlines; execution time is separate from receipt.
- States: timely, late, not_established, needs_review (conflicting timely/late accounts).
  These describe cycle-execution support, not full compliance or source truth.
- Evidence must match requirement revision and cycle; provider scope is enforced.
- Missing evidence does not prove nonexecution; cloud evidence cannot cover on-premises.
- Same ID/content delivery is idempotent; changed content is rejected. Evidence
  revisions cannot be overwritten. Withdrawals retain reason/date and invalidate
  dependent assessments without editing frozen historical snapshots. Replay cannot
  resurrect withdrawn evidence. New evidence conservatively flags prior assessments
  of that requirement. Reassessment is explicit, not an automatic scheduler.
- Peer outage retains historical support with a visibility limitation, without a
  fabricated reply. Withdrawal takes effect on its recorded date. Earlier as-of
  queries describe history, not current validity. Check needs_reassessment separately.

## Research refinements

Periodic, event-based and continuous obligations need profile-specific timing rules.
Continuous telemetry is not required for every monthly review. Separate contact,
evidence support and action authority. Recovery needs applicable evidence; closed
work or disappearing findings is insufficient. Source lineage prevents counting
repeated claims as independent proof. Future operational integrations must define
an execution/authorization boundary: pre-dispatch checks alone are not atomic safety.

## Verification and limits

Run `python -m unittest discover -s cell_signaling -p 'test_*.py' -v`.
Tests cover timing, missing support, scope, cycles/revisions, duplicate delivery,
conflicting accounts, new evidence, withdrawal/replay and retained outage history.
The demo has timely November cloud work received December 2, followed by outage
and withdrawal December 4. On-premises support remains unestablished.

No natural-language evidence verification, AI benchmark, control-effectiveness
validation, manifest negotiation, durable audit storage, automated expiry/controller,
operational writes, approvals or UI. Structured execution assertions are assumed.
The skeleton's signal payload dictionaries remain mutable, not a security boundary.
This exercise is not a production inter-cell implementation.
