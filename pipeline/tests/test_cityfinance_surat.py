import copy
import json
import unittest

from tests import FIXTURES, raw_from_file
from opencity.model import ValidationError
from opencity.sources import cityfinance_surat as cf

DIR = FIXTURES / 'cityfinance_surat'
AT = '2026-10-18T01:00:00+05:30'
YEARS = ['2015-16', '2016-17', '2017-18', '2019-20', '2020-21', '2021-22', '2022-23', '2023-24']


class TestCityFinanceSurat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.is_raw = raw_from_file(DIR / 'income-statement.json', retrieved_at=AT)
        cls.ov_raw = raw_from_file(DIR / 'overview.json', retrieved_at=AT)
        cls.is_res = cf.parse(cls.is_raw)
        cls.ov_res = cf.parse(cls.ov_raw)
        cls.by = {(o.metric_id, o.period_start[:4], o.dims.get('head')): o
                  for o in cls.is_res.observations + cls.ov_res.observations}

    def v(self, metric, year, head=None):
        return self.by[(metric, year, head)].value

    def test_audited_years(self):
        raw = raw_from_file(DIR / 'audited-years.json', retrieved_at=AT)
        self.assertEqual(cf.audited_years(raw.body), YEARS)
        res = cf.parse(raw)
        self.assertEqual(res.observations, [])
        cf.validate(res, raw)

    def test_counts(self):
        # 8 years x (10 income heads + 10 expenditure heads + 2 totals); 8 years x 3 overview rows
        self.assertEqual(len(self.is_res.observations), 8 * 22)
        self.assertEqual(len(self.ov_res.observations), 8 * 3)
        self.assertEqual(sorted({o.period_start for o in self.is_res.observations}),
                         [y[:4] + '-04-01' for y in YEARS])
        cf.validate(self.is_res, self.is_raw)
        cf.validate(self.ov_res, self.ov_raw)

    def test_income_statement_values_in_rupees(self):
        # read off income-statement.json, key "202324_5eb5844f76a3b61f40ba0693"
        self.assertEqual(self.v('cityfinance.income.by_head', '2023', 'tax_revenue'), 7280435255)
        self.assertEqual(self.v('cityfinance.income.by_head', '2023', 'fees_user_charges'), 25237551280)
        self.assertEqual(self.v('cityfinance.income.total', '2023'), 44068234541)
        self.assertEqual(self.v('cityfinance.expenditure.by_head', '2023', 'establishment'), 19791630640)
        self.assertEqual(self.v('cityfinance.expenditure.by_head', '2023', 'depreciation'), 7554142235)
        self.assertEqual(self.v('cityfinance.expenditure.total', '2023'), 43493259963)
        # 2015-16 ("201516_...")
        self.assertEqual(self.v('cityfinance.income.by_head', '2015', 'assigned_revenues_compensation'), 6567600000)
        self.assertEqual(self.v('cityfinance.income.total', '2015'), 17060283135)

    def test_blank_cells_are_not_reported(self):
        for key in [('cityfinance.income.by_head', '2015', 'rental_income'),       # no "201516_" key
                    ('cityfinance.income.by_head', '2020', 'assigned_revenues_compensation'),
                    ('cityfinance.expenditure.by_head', '2023', 'provisions_write_off'),
                    ('cityfinance.capital_expenditure', '2015', None),               # "N/A"
                    ('cityfinance.capital_expenditure', '2019', None)]:
            o = self.by[key]
            self.assertEqual((o.status, o.value), ('not_reported', None), key)

    def test_overview_values_converted_from_crore(self):
        # "Own Source Revenue (Cr)": 939.88 (2015-16) ... 3403.80 (2023-24)
        self.assertEqual(self.v('cityfinance.own_source_revenue', '2023'), 34038000000)
        self.assertEqual(self.v('cityfinance.own_source_revenue', '2015'), 9398800000)
        # "Total Capital Expenditure (Cr)": 3199.16 (2023-24); "Total Revenue Expenditure (Cr)": 1805.37 (2015-16)
        self.assertEqual(self.v('cityfinance.capital_expenditure', '2023'), 31991600000)
        self.assertEqual(self.v('cityfinance.revenue_expenditure', '2015'), 18053700000)

    def test_normalize_drops_cache_flag(self):
        body = self.is_raw.body
        self.assertEqual(cf.normalize(body[:-1] + b',"fromCache":true}'), body)

    def test_geography_and_period(self):
        o = self.by[('cityfinance.income.total', '2023', None)]
        self.assertEqual((o.geo_level, o.geo_code, o.period_start, o.period_end),
                         ('smc_city', 'smc', '2023-04-01', '2024-03-31'))

    def test_unknown_head_fails_loudly(self):
        doc = json.loads(self.is_raw.body)
        doc['data'].insert(3, {'code': 190, 'isNumber': True, 'lineItem': 'New head', '202324_' + cf.ULB_ID: 5})
        raw = copy.copy(self.is_raw)
        raw.body = json.dumps(doc).encode()
        with self.assertRaises(ValueError):
            cf.parse(raw)

    def test_validate_rejects_amounts_in_lakhs(self):
        res = cf.parse(self.is_raw)
        for o in res.observations:
            if o.value is not None:
                o.value = o.value / 100000
        with self.assertRaises(ValidationError):
            cf.validate(res, self.is_raw)


if __name__ == '__main__':
    unittest.main()
