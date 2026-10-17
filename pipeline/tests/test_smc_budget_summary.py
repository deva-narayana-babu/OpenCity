import json
import unittest

from tests import FIXTURES, REFERENCE, raw_from_file
from opencity.model import ValidationError
from opencity.sources import smc_budget_summary as m

PAGE = REFERENCE / 'budget/smc-revenue-capital-budget-summary-2026-09-28.html'
FIX = FIXTURES / 'smc_budget_summary'      # JSON answers of /Departments/getBudgetSummary fetched 2026-10-04
META = json.loads((FIX / 'meta.json').read_text())
INC, EXP = m.INCOME, m.EXPENDITURE


def _zone(value: str, **override):
    label = dict(META['zones'])[value]
    meta = {'doc': 'zone', 'zone_value': value, 'zone_label': label, 'budget_year': META['budget_year'],
            'headers': META['headers'], 'unit': META['unit'], 'as_of': META['as_of'], **override}
    raw = raw_from_file(FIX / f'zone-{value}.json', meta=meta)
    res = m.parse(raw)
    m.validate(res, raw)
    return res, {(o.metric_id, o.dims['account'], o.dims['measure'], o.period_start): o for o in res.observations}


class TestPage(unittest.TestCase):
    def test_page_info(self):
        info = m.page_info(PAGE.read_bytes())
        self.assertEqual(info['endpoint'], '/Departments/getBudgetSummary')
        self.assertEqual(info['budget_year'], 2026)
        self.assertEqual(info['unit'], "Rs. in '000")
        self.assertEqual(info['as_of'], '2026-09-27')                     # "Weekly Update(Last on 27/09/2026)"
        self.assertEqual(len(info['zones']), 11)
        self.assertEqual(info['zones'][0], ('0', 'All Zone'))
        self.assertEqual(info['zones'][10], ('10', 'South Zone-B (Kanakpur)'))
        self.assertEqual(info['headers'], META['headers'])                # same columns as when the JSON was fetched
        res = m.parse(raw_from_file(PAGE))
        m.validate(res, None)
        self.assertEqual(res.observations, [])

    def test_request_matches_the_page_script(self):
        p = m.request_params(2026, '3')
        self.assertEqual(p['CustomData[BudgetYear]'], '2026')
        self.assertEqual(p['CustomData[ZoneCode]'], '3')
        self.assertEqual(p['columns[7][data]'], 'CurrentYearActuals')
        self.assertEqual((p['start'], p['length']), ('0', '10'))

    def test_columns(self):
        self.assertEqual(m._column('Actuals 24-25', 2026), ('actual', 2024))
        self.assertEqual(m._column('Actuals (Tent.) 25-26', 2026), ('actual_tentative', 2025))
        self.assertEqual(m._column('Actuals (Tent.) 26-27', 2026), ('actual_ytd', 2026))
        self.assertEqual(m._column(' Original 26-27', 2026), ('budget_original', 2026))
        self.assertIsNone(m._column('% of Ori.26-27', 2026))
        with self.assertRaises(ValueError):
            m._column('Supplementary 26-27', 2026)


class TestZones(unittest.TestCase):
    def test_all_zone(self):
        res, by = _zone('0')
        self.assertEqual(len(res.observations), 24)                       # 4 rows x 6 value columns
        o = by[(INC, 'revenue', 'actual', '2024-04-01')]                    # Revenue Income, Actuals 24-25: 44599661
        self.assertEqual((o.geo_level, o.geo_code, o.period_end, o.value), ('smc_city', 'smc', '2025-03-31', 44599661000.0))
        self.assertEqual(by[(EXP, 'capital', 'budget_original', '2026-04-01')].value, 52252659000.0)   # 52252659
        self.assertEqual(by[(INC, 'capital', 'budget_revised', '2025-04-01')].value, 34404114000.0)    # 34404114
        self.assertEqual(by[(EXP, 'revenue', 'actual_tentative', '2025-04-01')].value, 42450567000.0)  # 42450567
        ytd = by[(INC, 'revenue', 'actual_ytd', '2026-04-01')]              # Actuals (Tent.) 26-27: 20718001
        self.assertEqual((ytd.period_end, ytd.value, ytd.publisher_as_of), ('2026-10-03', 20718001000.0, '2026-10-03'))

    def test_zone_geography(self):
        res, by = _zone('1')
        self.assertEqual({(o.geo_level, o.geo_code) for o in res.observations}, {('smc_zone', 'hq')})
        self.assertEqual(by[(EXP, 'revenue', 'actual', '2024-04-01')].value, 31477881000.0)            # 31477881
        res, by = _zone('10')
        self.assertEqual({o.geo_code for o in res.observations}, {'south_b'})
        self.assertEqual(by[(INC, 'capital', 'budget_revised', '2025-04-01')].value, 492578000.0)      # 492578
        res, _ = _zone('7')
        self.assertEqual({o.geo_code for o in res.observations}, {'south_west'})                       # Athwa Zone

    def test_all_zone_is_hq_plus_zones_2_to_8(self):
        # documented caveat: East Zone-B (9) and South Zone-B (10) are not part of "All Zone"
        parsed = {v: _zone(v)[1] for v, _ in META['zones']}
        for key, o in parsed['0'].items():
            s8 = sum(parsed[str(v)][key].value for v in range(1, 9))
            self.assertAlmostEqual(o.value, s8, places=2, msg=str(key))
            self.assertNotAlmostEqual(o.value, s8 + parsed['9'][key].value + parsed['10'][key].value, places=2)

    def test_shifted_columns_are_caught(self):
        headers = list(META['headers'])
        headers[3], headers[2] = headers[2], headers[3]         # swap Original/Revised 25-26: % check must fail
        with self.assertRaises(ValidationError):
            _zone('0', headers=headers)

    def test_ytd_needs_a_date_inside_the_year(self):
        with self.assertRaises(ValueError):
            _zone('2', as_of='2026-03-15')
        res, by = _zone('2', as_of=None)                        # no date: year-to-date values are skipped
        self.assertEqual(len(res.observations), 20)

    def test_error_answer_fails(self):
        raw = raw_from_file(FIX / 'zone-0.json', meta={'doc': 'zone', 'zone_value': '0', 'zone_label': 'All Zone',
                                                       'budget_year': 2026, 'headers': META['headers'],
                                                       'unit': META['unit'], 'as_of': META['as_of']})
        raw.body = b'{"data":null,"status":401,"redirectUrl":"/Error.html"}'
        with self.assertRaises(ValueError):
            m.parse(raw)


if __name__ == '__main__':
    unittest.main()
