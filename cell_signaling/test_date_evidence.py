import unittest
from cell_signaling.date_evidence import interpret_date, interpret_quoted_date


class DateEvidenceTests(unittest.TestCase):
    def test_exact_date_and_deadline_equality(self):
        r = interpret_date('2026-12-31', '2026-12-31')
        self.assertEqual((r['date_status'], r['exact_date'], r['deadline_relation']),
                         ('exact', '2026-12-31', 'on_or_before_deadline'))

    def test_ambiguous_but_both_late_preserves_original(self):
        r = interpret_date('01/02/2027', '2026-12-31')
        self.assertEqual(r['raw_date'], '01/02/2027')
        self.assertEqual(r['date_status'], 'ambiguous')
        self.assertIsNone(r['exact_date'])
        self.assertEqual(r['candidate_dates'], ['2027-01-02', '2027-02-01'])
        self.assertEqual(r['deadline_relation'], 'after_deadline')

    def test_ambiguity_straddles_deadline(self):
        r = interpret_date('01/02/2027', '2027-01-15')
        self.assertEqual(r['deadline_relation'], 'not_established')

    def test_ambiguous_but_both_before_deadline(self):
        self.assertEqual(interpret_date('01/02/2027','2027-03-01')['deadline_relation'], 'on_or_before_deadline')

    def test_calendar_disambiguation_and_leap_year(self):
        self.assertEqual(interpret_date('13/02/2027','2027-03-01')['exact_date'], '2027-02-13')
        self.assertEqual(interpret_date('29/02/2028','2028-03-01')['exact_date'], '2028-02-29')
        self.assertEqual(interpret_date('29/02/2027','2027-03-01')['date_status'], 'invalid')

    def test_missing_invalid_and_unsupported_abstain(self):
        for raw, state in [(None,'missing'),('','missing'),('2027-02-30','invalid'),('next Friday','unsupported_format')]:
            with self.subTest(raw=raw):
                r = interpret_date(raw,'2027-03-01')
                self.assertEqual(r['date_status'],state)
                self.assertEqual(r['deadline_relation'],'not_established')

    def test_convention_requires_provenance(self):
        with self.assertRaises(ValueError):
            interpret_date('01/02/2027','2027-01-15',convention='DMY')
        r=interpret_date('01/02/2027','2027-01-15',convention='DMY',convention_reference='source-format-record')
        self.assertEqual(r['exact_date'],'2027-02-01')

    def test_original_quote_enforced(self):
        source='Review completed on 01/02/2027.'
        r=interpret_quoted_date(source,source,'01/02/2027','2026-12-31')
        self.assertEqual(r['date_status'],'ambiguous')
        for raw in ['2027-01-02','1/02/2027']:
            with self.assertRaises(ValueError):
                interpret_quoted_date(source,source,raw,'2026-12-31')
        with self.assertRaises(ValueError):
            interpret_quoted_date(source,'Invented quote','01/02/2027','2026-12-31')
