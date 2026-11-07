import unittest
from dataclasses import replace
from datetime import date
from cell_signaling.coverage_demo import scenario


class CoverageTests(unittest.TestCase):
    def setUp(self):
        self.exchange, self.request, self.evidence = scenario()

    def assess(self, day=date(2026, 12, 2)):
        return self.exchange.assess(self.request, day)

    def test_late_arrival_is_not_late_execution_and_scope_is_preserved(self):
        self.exchange.receive_evidence('one', self.evidence)
        self.assertEqual(dict(self.assess().population_states),
                         {'cloud': 'timely', 'on-premises': 'not_established'})

    def test_late_execution_remains_late(self):
        self.exchange.receive_evidence('one', replace(self.evidence, executed=date(2026, 12, 1)))
        self.assertEqual(dict(self.assess().population_states)['cloud'], 'late')

    def test_missing_evidence_does_not_assert_failure(self):
        self.assertEqual(set(dict(self.assess().population_states).values()), {'not_established'})

    def test_evidence_not_received_yet_is_not_used(self):
        self.exchange.receive_evidence('one', self.evidence)
        self.assertEqual(self.assess(date(2026, 11, 30)).evidence, ())

    def test_wrong_period_and_revision_do_not_support_claim(self):
        for evidence in (replace(self.evidence, period_start=date(2026, 10, 1)),
                         replace(self.evidence, requirement=replace(self.request.reference, revision=2))):
            exchange, request, _ = scenario()
            exchange.receive_evidence('one', evidence)
            self.assertEqual(exchange.assess(request, date(2026, 12, 2)).evidence, ())

    def test_scope_and_tenant_violations_rejected_without_history(self):
        for evidence in (replace(self.evidence, populations=frozenset({'on-premises'})),
                         replace(self.evidence, reference=replace(self.evidence.reference, organization='OTHER'))):
            with self.assertRaises(ValueError):
                self.exchange.receive_evidence('bad', evidence)
        self.assertEqual(self.exchange.security.signal_history, [])

    def test_duplicate_delivery_idempotent_and_changed_content_rejected(self):
        self.assertTrue(self.exchange.receive_evidence('one', self.evidence))
        self.assertFalse(self.exchange.receive_evidence('one', self.evidence))
        with self.assertRaises(ValueError):
            self.exchange.receive_evidence('one', replace(self.evidence, executed=date(2026, 11, 29)))
        self.assertEqual(len(self.exchange.security.signal_history), 1)

    def test_revision_cannot_be_overwritten(self):
        self.exchange.receive_evidence('one', self.evidence)
        with self.assertRaises(ValueError):
            self.exchange.receive_evidence('two', replace(self.evidence, executed=date(2026, 11, 29)))

    def test_withdrawal_invalidates_dependents_preserves_history_and_no_resurrection(self):
        self.exchange.receive_evidence('one', self.evidence)
        original = self.assess()
        self.exchange.withdraw('withdraw', self.evidence.reference, date(2026, 12, 3), 'Correction')
        self.assertTrue(self.exchange.needs_reassessment(original.assessment_id))
        self.assertEqual(dict(original.population_states)['cloud'], 'timely')
        self.assertEqual(self.assess(date(2026, 12, 3)).evidence, ())
        self.exchange.receive_evidence('replay', self.evidence)
        self.assertEqual(self.assess(date(2026, 12, 4)).evidence, ())
        self.assertFalse(self.exchange.withdraw('withdraw', self.evidence.reference, date(2026, 12, 3), 'Correction'))

    def test_withdrawal_does_not_invalidate_unrelated_assessment(self):
        empty = self.exchange.assess(replace(self.request, reference=replace(
            self.request.reference, record='UNRELATED')), date(2026, 12, 2))
        self.exchange.receive_evidence('one', self.evidence)
        supported = self.assess()
        self.exchange.withdraw('withdraw', self.evidence.reference, date(2026, 12, 3), 'Correction')
        self.assertTrue(self.exchange.needs_reassessment(supported.assessment_id))
        self.assertFalse(self.exchange.needs_reassessment(empty.assessment_id))

    def test_outage_preserves_historical_support_without_fake_reply(self):
        self.exchange.receive_evidence('one', self.evidence)
        self.exchange.peer_contact = 'unavailable'
        before = len(self.exchange.security.signal_history)
        result = self.assess()
        self.assertEqual(dict(result.population_states)['cloud'], 'timely')
        self.assertIn('Peer unavailable', result.limitations[-1])
        self.assertEqual(len(self.exchange.security.signal_history), before)

    def test_conflicting_execution_accounts_require_review(self):
        self.exchange.receive_evidence('one', self.evidence)
        other = replace(self.evidence, reference=replace(self.evidence.reference, record='OTHER'),
                        executed=date(2026, 12, 1))
        self.exchange.receive_evidence('two', other)
        self.assertEqual(dict(self.assess().population_states)['cloud'], 'needs_review')

    def test_new_evidence_invalidates_prior_assessment(self):
        prior = self.assess()
        self.exchange.receive_evidence('one', self.evidence)
        self.assertTrue(self.exchange.needs_reassessment(prior.assessment_id))

    def test_invalid_dates_and_mutable_populations_rejected(self):
        with self.assertRaises(ValueError):
            replace(self.evidence, executed=date(2026, 12, 3))
        with self.assertRaises(ValueError):
            replace(self.request, populations={'cloud'})
        with self.assertRaises(ValueError):
            replace(self.request, due=date(2026, 10, 1))


if __name__ == '__main__':
    unittest.main()
