"""Run with python -m cell_signaling.coverage_demo. Synthetic data only."""
from datetime import date
from .coverage import CoverageExchange, Reference, ReviewRequest, ReviewEvidence
from .models import GRCCell


def scenario():
    security = GRCCell('SEC', 'Security assurance', 'Cloud and on-premises admins')
    identity = GRCCell('ID', 'Identity operations', 'Cloud admins')
    exchange = CoverageExchange('DEMO', security, identity, frozenset({'cloud'}))
    requirement = Reference('DEMO', 'SEC', 'MONTHLY-REVIEW', 1)
    request = ReviewRequest(requirement, frozenset({'cloud', 'on-premises'}),
                            date(2026, 11, 1), date(2026, 11, 30), date(2026, 11, 30))
    evidence = ReviewEvidence(Reference('DEMO', 'ID', 'CAMPAIGN', 1), requirement,
                              frozenset({'cloud'}), request.period_start, request.period_end,
                              date(2026, 11, 28), date(2026, 12, 2),
                              'synthetic://campaign/1')
    return exchange, request, evidence


def main():
    exchange, request, evidence = scenario()
    exchange.receive_evidence('observed-1', evidence)
    first = exchange.assess(request, date(2026, 12, 2))
    print('SYNTHETIC TWO-CELL EXERCISE — source truth not verified')
    print('Late arrival, timely execution:', dict(first.population_states))
    exchange.peer_contact = 'unavailable'
    cached = exchange.assess(request, date(2026, 12, 3))
    print('Peer unavailable, retained historical support:', dict(cached.population_states))
    exchange.withdraw('withdrawn-1', evidence.reference, date(2026, 12, 4), 'Source corrected')
    print('Earlier assessment needs reassessment:', exchange.needs_reassessment(first.assessment_id))
    current = exchange.assess(request, date(2026, 12, 4))
    print('After withdrawal:', dict(current.population_states))
    print('Original snapshot preserved:', dict(first.population_states))


if __name__ == '__main__':
    main()
