import unittest

from tests import FIXTURES, raw_from_file
from opencity.model import ValidationError
from opencity.sources import njdg_surat

DIR = FIXTURES / 'njdg_surat'
FETCHED = '2026-10-24T02:02:00+05:30'
META = {'as_of': '2026-10-23', 'pending_total': 140354}


def _by(res):
    return {(o.metric_id, tuple(sorted(o.dims.items())), o.period_start): o for o in res.observations}


class TestNjdgSuratPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = raw_from_file(DIR / 'district_2026-10-23.html', retrieved_at=FETCHED)
        cls.res = njdg_surat.parse(cls.raw)
        cls.by = _by(cls.res)

    def get(self, metric, day='2026-10-23', **dims):
        return self.by[('njdg.' + metric, tuple(sorted(dims.items())), day)].value

    def test_counts(self):
        self.assertEqual(len(self.res.observations), 45)        # 3 cards + 14 blocks, x civil/criminal/total
        njdg_surat.validate(self.res, self.raw)

    def test_values_read_off_the_page(self):
        # cards: Civil Cases 32,002 | Criminal Cases 1,08,352 | Total Cases 1,40,354
        self.assertEqual(self.get('pending_cases', civil_criminal='civil'), 32002)
        self.assertEqual(self.get('pending_cases', civil_criminal='criminal'), 108352)
        self.assertEqual(self.get('pending_cases', civil_criminal='total'), 140354)
        # Age wise: "Less than one year" 15,319 | 53,964 | 69,283 (49%); "Above 10 Years" 2,328 | 2,092 | 4,420 (3%)
        self.assertEqual(self.get('pending_by_age', civil_criminal='total', age_band='lt_1y'), 69283)
        self.assertEqual(self.get('pending_by_age', civil_criminal='civil', age_band='gt_10y'), 2328)
        self.assertEqual(self.get('pending_by_age', civil_criminal='criminal', age_band='3_5y'), 13349)
        # Instituted in last month 1,248 | 1,83,355 | 1,84,603; Uncontested disposals 1,404 | 1,92,253 | 1,93,657
        self.assertEqual(self.get('instituted_last_month', civil_criminal='criminal'), 183355)
        self.assertEqual(self.get('disposed_last_month', civil_criminal='total', disposal='all'), 196647)
        self.assertEqual(self.get('disposed_last_month', civil_criminal='civil', disposal='contested'), 161)
        self.assertEqual(self.get('disposed_last_month', civil_criminal='criminal', disposal='uncontested'), 192253)
        # alert cards: Undated 7 / 28 / 35, Excessive Dated 1 / 1 / 2, Filed by Senior Citizen 5,851 / 3,530 / 9,381
        self.assertEqual(self.get('undated_cases', civil_criminal='total'), 35)
        self.assertEqual(self.get('excessive_dated_cases', civil_criminal='total'), 2)
        self.assertEqual(self.get('pending_filed_by_senior_citizens', civil_criminal='civil'), 5851)
        self.assertEqual(self.get('pending_filed_by_women', civil_criminal='total'), 9344)
        self.assertEqual(self.get('cases_listed_today', civil_criminal='criminal'), 4593)

    def test_geography_and_date(self):
        o = self.res.observations[0]
        self.assertEqual((o.geo_level, o.geo_code, o.period_start, o.period_end, o.publisher_as_of),
                         ('surat_district', 'surat', '2026-10-23', '2026-10-23', '2026-10-23'))

    def test_other_district_is_rejected(self):
        body = self.raw.body.replace(b'value="14" selected>SURAT', b'value="14" >SURAT')
        self.assertNotEqual(body, self.raw.body)
        with self.assertRaises(ValueError):
            njdg_surat.parse(_raw(body))

    def test_blank_undated_is_not_reported(self):
        # blank the visible Undated civil count: '...#modal_state_data">7<span class="visually-hidden">Civil Count'
        old = b'modal_state_data">7<span class="visually-hidden">Civil Count'
        self.assertEqual(self.raw.body.count(old), 1)
        raw = _raw(self.raw.body.replace(old, b'modal_state_data"><span class="visually-hidden">Civil Count'))
        raw.retrieved_at = FETCHED
        res = njdg_surat.parse(raw)
        o = [o for o in res.observations if o.metric_id == 'njdg.undated_cases'][0]
        self.assertEqual((o.dims, o.value, o.status), ({'civil_criminal': 'civil'}, None, 'not_reported'))
        njdg_surat.validate(res, raw)

    def test_stale_date_fails_validation(self):
        with self.assertRaises(ValidationError):
            njdg_surat.validate(self.res, raw_from_file(DIR / 'district_2026-10-23.html',
                                                        retrieved_at='2026-12-01T10:00:00+05:30'))

    def test_normalize_blanks_volatile_bits(self):
        a = b'<script src="/njdg_v3//js/ecourts.js?v=1791523696"></script><p class="x contrastFiltertxt m-0">S3</p>'
        b = b'<script src="/njdg_v3//js/ecourts.js?v=1791523328"></script><p class="x contrastFiltertxt m-0">S2</p>'
        self.assertEqual(njdg_surat.normalize(a), njdg_surat.normalize(b))


def _raw(body):
    raw = raw_from_file(DIR / 'district_2026-10-23.html')
    raw.body = body
    return raw


class TestNjdgSuratDashboard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = raw_from_file(DIR / 'pending_dashboard_2026-10-23.json', meta=META, retrieved_at=FETCHED)
        cls.res = njdg_surat.parse(cls.raw)
        cls.by = _by(cls.res)

    def get(self, metric, day='2026-10-23', **dims):
        return self.by[('njdg.' + metric, tuple(sorted(dims.items())), day)].value

    def test_counts(self):
        n = {}
        for o in self.res.observations:
            n[o.metric_id] = n.get(o.metric_id, 0) + 1
        self.assertEqual(n, {'njdg.pending_by_stage': 26, 'njdg.pending_by_stage_group': 4,
                             'njdg.pending_by_case_type': 22, 'njdg.pending_by_case_category': 4,
                             'njdg.pending_by_filing_year': 39, 'njdg.instituted_by_year': 9,
                             'njdg.disposed_by_year': 9})
        njdg_surat.validate(self.res, self.raw)

    def test_values_read_off_the_json(self):
        # purpose_name "Process#Issue" ~ purpose_count 70020; "313#Cr.PC" 1854; "Suppl.##Copy" 92
        self.assertEqual(self.get('pending_by_stage', stage='Process Issue'), 70020)
        self.assertEqual(self.get('pending_by_stage', stage='313 Cr.PC'), 1854)
        self.assertEqual(self.get('pending_by_stage', stage='Suppl. Copy'), 92)
        self.assertEqual(self.get('pending_by_stage_group', stage_group='Evidence/Argument/Judgement'), 60147)
        self.assertEqual(self.get('pending_by_case_type', case_type='MAGISTRIAL CASES'), 88211)
        self.assertEqual(self.get('pending_by_case_category', case_category='execution'), 1446)
        self.assertEqual(self.get('pending_by_filing_year', filing_year='1984'), 1)
        # insyear 2025: instituted 441467, disposed 442577 (calendar year)
        self.assertEqual(self.get('instituted_by_year', day='2025-01-01'), 441467)
        o = self.by[('njdg.disposed_by_year', (), '2025-01-01')]
        self.assertEqual((o.value, o.period_end, o.publisher_as_of), (442577, '2025-12-31', '2026-10-23'))

    def test_age_bands_are_calendar_years(self):
        # the page's "Less than one year" (69,283) = cases instituted in 2026 + 2025
        self.assertEqual(self.get('pending_by_filing_year', filing_year='2026')
                         + self.get('pending_by_filing_year', filing_year='2025'), 69283)

    def test_district_page_mismatch_fails(self):
        raw = raw_from_file(DIR / 'pending_dashboard_2026-10-23.json', retrieved_at=FETCHED,
                            meta={'as_of': '2026-10-23', 'pending_total': 250000})
        with self.assertRaises(ValidationError):
            njdg_surat.validate(njdg_surat.parse(raw), raw)

    def test_needs_date_from_page(self):
        with self.assertRaises(ValueError):
            njdg_surat.parse(raw_from_file(DIR / 'pending_dashboard_2026-10-23.json'))


if __name__ == '__main__':
    unittest.main()
