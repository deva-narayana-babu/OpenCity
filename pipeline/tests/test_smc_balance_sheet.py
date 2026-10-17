import unittest

from tests import FIXTURES, REFERENCE, raw_from_file
from opencity.model import ValidationError
from opencity.sources import smc_balance_sheet as m

BS, IE = m.BS, m.IE
FY26 = REFERENCE / 'budget/smc-balance-sheet-2025-26.pdf'
INDEX = REFERENCE / 'budget/smc-balance-sheet-index-2026-09-28.html'
FIX = FIXTURES / 'smc_balance_sheet'


def _parse(path, fy):
    raw = raw_from_file(path, meta={'doc': 'statement', 'fy': fy})
    res = m.parse(raw)
    m.validate(res, raw)
    return res, {(o.metric_id, o.period_start, o.period_end): o for o in res.observations}


class TestIndex(unittest.TestCase):
    def test_entries_and_records(self):
        entries = m.index_entries(INDEX.read_bytes())
        self.assertEqual(len(entries), 21)
        self.assertEqual(entries[0], (2025, '2025-26', 'https://www.suratmunicipal.gov.in/Content/Documents/'
                                                       'Departments/Accounts/BalanceSheet_25_26.pdf'))
        self.assertEqual(entries[-1][:2], (2005, '2005-06'))
        res = m.parse(raw_from_file(INDEX))
        m.validate(res, None)
        self.assertEqual(res.observations, [])
        self.assertEqual(res.complete_record_types, ('balance_sheet_pdf',))
        r = {x.record_key: x for x in res.records}['fy-2016-17']
        self.assertEqual(r.attrs['as_at'], '2017-03-31')
        self.assertTrue(r.attrs['url'].endswith('/BalanceSheet_16_17.pdf'))
        # fetch() only downloads FY2007-08 onward (older two are a different, two-sided format)
        self.assertEqual(sum(1 for e in entries if e[0] >= m.FIRST_FY), 19)


class TestFY2025_26(unittest.TestCase):
    """reference/budget/smc-balance-sheet-2025-26.pdf, page 1 (balance sheet) and page 2 (I&E), "Amount in (Rs.)"."""

    @classmethod
    def setUpClass(cls):
        cls.res, cls.by = _parse(FY26, '2025-26')

    def v(self, metric, start, end=None):
        return self.by[(metric, start, end or start)]

    def test_counts(self):
        self.assertEqual(len(self.res.observations), 80)      # (19 BS + 21 I&E heads) x 2 columns
        self.assertEqual({(o.geo_level, o.geo_code) for o in self.res.observations}, {('smc_city', 'smc')})
        self.assertEqual({o.publisher_as_of for o in self.res.observations}, {'2026-07-14'})   # "Date : 14 JULY 2026"

    def test_balance_sheet_values(self):
        d, p = '2026-03-31', '2025-03-31'
        self.assertEqual(self.v(BS + 'municipal_fund', d).value, 36306211973.33)          # 36,30,62,11,973.33
        self.assertEqual(self.v(BS + 'reserves_surplus', d).value, 270955267325.05)       # 2,70,95,52,67,325.05
        self.assertEqual(self.v(BS + 'secured_loans', d).value, 2000000000.00)            # 2,00,00,00,000.00
        self.assertEqual(self.v(BS + 'unsecured_loans', p).value, 10152319000.00)         # 10,15,23,19,000.00
        self.assertEqual(self.v(BS + 'total', d).value, 319855548765.38)                  # GRAND TOTAL 3,19,85,55,48,765.38
        self.assertEqual(self.v(BS + 'total', p).value, 284178455492.40)
        self.assertEqual(self.v(BS + 'cwip', d).value, 115754408956.46)                   # 1,15,75,44,08,956.46
        self.assertEqual(self.v(BS + 'investments', d).value, 1308081200.00)              # 1,30,80,81,200.00
        self.assertEqual(self.v(BS + 'cash_bank', d).value, 28043763066.38)               # 28,04,37,63,066.38
        self.assertEqual(self.v(BS + 'current_assets', p).value, 47905902550.80)          # 47,90,59,02,550.80
        self.assertEqual(self.v(BS + 'current_liabilities', d).value, 26239055176.45)     # 26,23,90,55,176.45

    def test_dash_is_not_reported(self):
        o = self.v(BS + 'secured_loans', '2025-03-31')                                     # printed "-"
        self.assertEqual((o.value, o.status), (None, 'not_reported'))
        o = self.v(BS + 'provisions_for_taxes', '2026-03-31')
        self.assertEqual((o.value, o.status), (None, 'not_reported'))

    def test_income_expenditure_values(self):
        fy, fy0 = ('2025-04-01', '2026-03-31'), ('2024-04-01', '2025-03-31')
        self.assertEqual(self.by[(IE + 'tax_revenue', *fy)].value, 20805210307.45)         # 20,80,52,10,307.45
        self.assertEqual(self.by[(IE + 'total_income', *fy)].value, 48047961253.39)        # 48,04,79,61,253.39
        self.assertEqual(self.by[(IE + 'employee_costs', *fy0)].value, 21166147774.99)     # 21,16,61,47,774.99
        self.assertEqual(self.by[(IE + 'surplus_before_tax', *fy)].value, -994549508.88)   # -99,45,49,508.88
        self.assertEqual(self.by[(IE + 'loss_on_disposal', *fy0)].value, 102888984.74)     # 10,28,88,984.74
        self.assertEqual(self.by[(IE + 'excess_income_over_expenditure', *fy)].value, 692980756.47)
        self.assertEqual(self.by[(IE + 'loss_on_disposal', *fy)].status, 'not_reported')
        self.assertEqual(self.by[(IE + 'tax_provision', *fy)].status, 'not_reported')     # printed line, no amounts

    def test_inconsistent_current_column_is_rejected(self):
        res, _ = _parse(FY26, '2025-26')
        for o in res.observations:
            if o.metric_id == BS + 'cash_bank' and o.period_end == '2026-03-31':
                o.value += 1000
        with self.assertRaises(ValidationError):
            m.validate(res, None)

    def test_index_year_must_match(self):
        with self.assertRaises(ValueError):
            m.parse(raw_from_file(FY26, meta={'doc': 'statement', 'fy': '2024-25'}))


class TestOlderLayouts(unittest.TestCase):
    def test_fy2007_08_western_grouping_and_rupee_glyph(self):
        # unit printed as "(`)" (rupee sign in the Rupee Foradian font); western digit grouping
        res, by = _parse(FIX / 'BalanceSheet_07_08.pdf', '2007-08')
        self.assertEqual(len(res.observations), 78)
        self.assertEqual(by[(BS + 'municipal_fund', '2008-03-31', '2008-03-31')].value, 20412068173.40)
        self.assertEqual(by[(BS + 'total', '2007-03-31', '2007-03-31')].value, 40773195047.88)
        self.assertEqual(by[(BS + 'provisions_for_taxes', '2008-03-31', '2008-03-31')].value, 4500000.00)
        self.assertEqual(by[(IE + 'tax_provision', '2007-04-01', '2008-03-31')].value, 4500000.00)
        self.assertEqual(by[(IE + 'octroi_compensation', '2006-04-01', '2007-03-31')].value, 0.0)   # printed 0.00
        self.assertIsNone(res.observations[0].publisher_as_of)        # signed by SMC officials, no date

    def test_fy2013_14_no_unit_and_squashed_labels(self):
        # no "(In Rs.)" on either page; labels such as "TaxRevenues", "Otherincome"
        res, by = _parse(FIX / 'BalanceSheet_13_14.pdf', '2013-14')
        self.assertEqual(by[(IE + 'tax_revenue', '2013-04-01', '2014-03-31')].value, 5998066882.16)   # 5,99,80,66,882.16
        self.assertEqual(by[(IE + 'other_income', '2012-04-01', '2013-03-31')].value, 785512168.32)   # 78,55,12,168.32
        self.assertEqual(by[(BS + 'total', '2014-03-31', '2014-03-31')].value, 93040683976.71)
        o = by[(IE + 'other_expenses', '2012-04-01', '2013-03-31')]       # only the current column is printed
        self.assertEqual((o.value, o.status), (None, 'not_reported'))
        self.assertEqual(by[(IE + 'other_expenses', '2013-04-01', '2014-03-31')].value, 33.13)
        self.assertEqual(res.observations[0].publisher_as_of, '2017-03-22')   # "Date : 22/03/2017"

    def test_fy2016_17_inconsistent_comparative_is_dropped(self):
        # the comparative 31-03-2016 balance sheet prints GRAND TOTALs 1,22,06,98,35,666.89 vs 1,22,06,97,87,206.89
        res, by = _parse(FIX / 'BalanceSheet_16_17.pdf', '2016-17')
        self.assertEqual({o.period_end for o in res.observations if o.period_start == o.period_end}, {'2017-03-31'})
        self.assertEqual(by[(BS + 'total', '2017-03-31', '2017-03-31')].value, 134710317079.52)
        self.assertNotIn(BS + 'loan_funds', {o.metric_id for o in res.observations})   # no Loan Funds block
        # the I&E (printed before the balance sheet in this PDF) keeps both years
        self.assertEqual(by[(IE + 'non_tax_revenue', '2016-04-01', '2017-03-31')].value, 4286196254.00)
        self.assertEqual(by[(IE + 'surplus_before_tax', '2015-04-01', '2016-03-31')].value, -509463869.01)

    def test_t_format_is_recognised(self):
        page = ('Surat Municipal Corporation\nBalance Sheet\nAs on 31st March 2006\n'
                'Liabilities                     2004-2005        2005-2006        Assets   2004-2005  2005-2006\n')
        self.assertEqual(m._statement_kind(page), 'tformat')
        self.assertIsNone(m._explicit_unit(page))

    def test_units(self):
        self.assertEqual(m._explicit_unit('x\n   Amount in (Rs.)\n'), 1.0)
        self.assertEqual(m._explicit_unit('x\n (In Rs.)\n'), 1.0)
        self.assertEqual(m._explicit_unit('x\n (Rs. in Lakhs)\n'), 1e5)
        self.assertEqual(m._explicit_unit('x\n (Rs. in crore)\n'), 1e7)


if __name__ == '__main__':
    unittest.main()
