"""Bounded, in-memory two-cell monthly-review exercise; no AI or transport auth."""
from dataclasses import dataclass
from datetime import date
from uuid import uuid4

from .models import GRCCell, GRCSignal


@dataclass(frozen=True)
class Reference:
    organization: str
    cell: str
    record: str
    revision: int

    def __post_init__(self):
        if not all(isinstance(x, str) and x.strip() for x in
                   (self.organization, self.cell, self.record)):
            raise ValueError('Reference identifiers must be nonempty')
        if type(self.revision) is not int or self.revision < 1:
            raise ValueError('Revision must be a positive integer')


@dataclass(frozen=True)
class ReviewRequest:
    reference: Reference
    populations: frozenset[str]
    period_start: date
    period_end: date
    due: date

    def __post_init__(self):
        validate_population(self.populations)
        if not self.period_start <= self.period_end <= self.due:
            raise ValueError('Invalid review period or deadline')


@dataclass(frozen=True)
class ReviewEvidence:
    reference: Reference
    requirement: Reference
    populations: frozenset[str]
    period_start: date
    period_end: date
    executed: date
    received: date
    source_location: str

    def __post_init__(self):
        validate_population(self.populations)
        if not self.period_start <= self.period_end or self.executed > self.received:
            raise ValueError('Invalid evidence dates')
        if not self.source_location.strip():
            raise ValueError('Evidence needs a source location')


def validate_population(value):
    if not isinstance(value, frozenset) or not value or not all(
            isinstance(x, str) and x.strip() for x in value):
        raise ValueError('Populations must be a nonempty frozenset of identifiers')


@dataclass(frozen=True)
class Assessment:
    assessment_id: str
    requirement: Reference
    evaluated_on: date
    population_states: tuple[tuple[str, str], ...]
    evidence: tuple[Reference, ...]
    limitations: tuple[str, ...]


class CoverageExchange:
    """Explicitly configured local peers, not authenticated production identities.

    Inputs assert scoped execution facts. This exercise checks their temporal and
    dependency semantics; it does not verify source truth or control effectiveness.
    """
    def __init__(self, organization, security: GRCCell, identity: GRCCell,
                 identity_populations: frozenset[str]):
        validate_population(identity_populations)
        if not organization.strip() or security.cell_id == identity.cell_id:
            raise ValueError('Need organization and two distinct cells')
        self.organization = organization
        self.security = security
        self.identity = identity
        self.identity_populations = identity_populations
        self._evidence = {}
        self._withdrawn = {}
        self._assessments = []
        self._invalidated = set()
        self._deliveries = {}
        self.peer_contact = 'available'

    @property
    def assessments(self):
        return tuple(self._assessments)

    def needs_reassessment(self, assessment_id):
        if not any(a.assessment_id == assessment_id for a in self._assessments):
            raise ValueError('Unknown assessment')
        return assessment_id in self._invalidated

    def _check_reference(self, reference, cell):
        if reference.organization != self.organization or reference.cell != cell:
            raise ValueError('Reference outside configured organization/cell')

    def _repeat(self, signal_id, content):
        if not isinstance(signal_id, str) or not signal_id.strip():
            raise ValueError('Signal ID required')
        if signal_id in self._deliveries:
            if self._deliveries[signal_id] != content:
                raise ValueError('Same signal ID with changed content')
            return True
        return False

    def receive_evidence(self, signal_id, evidence):
        self._check_reference(evidence.reference, self.identity.cell_id)
        self._check_reference(evidence.requirement, self.security.cell_id)
        if not evidence.populations <= self.identity_populations:
            raise ValueError('Evidence exceeds identity cell scope')
        content = ('evidence', evidence)
        if self._repeat(signal_id, content):
            return False
        previous = self._evidence.get(evidence.reference)
        if previous is not None and previous != evidence:
            raise ValueError('Evidence revision cannot be overwritten')
        self._evidence[evidence.reference] = evidence
        if previous is None:
            for assessment in self._assessments:
                if assessment.requirement == evidence.requirement:
                    self._invalidated.add(assessment.assessment_id)
        self._deliveries[signal_id] = content
        event = GRCSignal('evidence.observed', self.identity.cell_id,
                          {'reference': evidence.reference}, signal_id=signal_id)
        self.identity.signal_history.append(event)
        self.security.signal_history.append(event)
        return True

    def withdraw(self, signal_id, reference, withdrawn_on, reason):
        self._check_reference(reference, self.identity.cell_id)
        if reference not in self._evidence or not reason.strip():
            raise ValueError('Withdrawal needs known evidence and reason')
        if withdrawn_on < self._evidence[reference].received:
            raise ValueError('Withdrawal cannot precede receipt')
        content = ('withdrawal', reference, withdrawn_on, reason)
        if self._repeat(signal_id, content):
            return False
        if reference in self._withdrawn:
            raise ValueError('Evidence revision already withdrawn')
        self._withdrawn[reference] = (withdrawn_on, reason)
        self._deliveries[signal_id] = content
        for assessment in self._assessments:
            if reference in assessment.evidence:
                self._invalidated.add(assessment.assessment_id)
        event = GRCSignal('evidence.withdrawn', self.identity.cell_id,
                          {'reference': reference, 'date': withdrawn_on, 'reason': reason},
                          signal_id=signal_id)
        self.identity.signal_history.append(event)
        self.security.signal_history.append(event)
        return True

    def assess(self, request, evaluated_on):
        self._check_reference(request.reference, self.security.cell_id)
        if evaluated_on < request.period_start:
            raise ValueError('Cannot assess before the period starts')
        # Request/reply is a local simulation: receipt is not approval.
        request_signal = GRCSignal('analysis.requested', self.security.cell_id,
                                   {'request': request})
        if self.peer_contact == 'available':
            self.identity.signal_history.append(request_signal)
        states = []
        used = set()
        for population in sorted(request.populations):
            matches = [e for e in self._evidence.values()
                       if e.requirement == request.reference
                       and population in e.populations
                       and (e.period_start, e.period_end) ==
                           (request.period_start, request.period_end)
                       and e.executed >= request.period_start
                       and e.received <= evaluated_on
                       and not (e.reference in self._withdrawn and
                                self._withdrawn[e.reference][0] <= evaluated_on)]
            used.update(e.reference for e in matches)
            outcomes = {'timely' if e.executed <= request.due else 'late'
                        for e in matches}
            # Multiple incompatible execution accounts require review, not voting.
            state = ('needs_review' if len(outcomes) > 1 else
                     next(iter(outcomes)) if outcomes else 'not_established')
            states.append((population, state))
        limitations = ['Structured evidence assertions are not independently verified.',
                       'This is cycle execution support, not a compliance determination.']
        if self.peer_contact != 'available':
            limitations.append('Peer unavailable; latest remote revisions are unknown.')
        assessment = Assessment(str(uuid4()), request.reference, evaluated_on,
                                tuple(states), tuple(sorted(used, key=repr)), tuple(limitations))
        self._assessments.append(assessment)
        reply = GRCSignal('assessment.proposed', self.identity.cell_id,
                          {'evidence': assessment.evidence, 'scope': self.identity_populations},
                          parent_signal_id=request_signal.signal_id)
        # With no peer contact, assessment uses cached evidence, not a fabricated reply.
        if self.peer_contact == 'available':
            self.identity.signal_history.append(reply)
            self.security.signal_history.append(reply)
        return assessment
