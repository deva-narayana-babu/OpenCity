import unittest

from tests import FIXTURES, raw_from_file
from opencity.model import ValidationError
from opencity.sources import jjm_surat

DIR = FIXTURES / 'jjm_surat'
FETCHED = '2026-10-24T22:00:00+05:30'


def _parse(name, view):
    raw = raw_from_file(DIR / name, meta={'view': view, 'as_of': FETCHED[:10]}, retrieved_at=FETCHED)
    res = jjm_surat.parse(raw)
    return raw, res, {(o.metric_id, o.geo_code): o for o in res.observations}


class TestJjmSurat(unittest.TestCase):
    def test_encode_txt_matches_the_dashboard(self):
        # the values the dashboard sends for Gujarat (24), Cat 0, SubCat 0/1, Param 1
        self.assertEqual([jjm_surat.encode_txt(s) for s in ('24', '0', '1')], ['351', '11', '21'])

    def test_today_view(self):
        raw, res, by = _parse('binddistrictmap-gujarat-today-2026-10-24.json', 'today')
        self.assertEqual(len(res.observations), 2 * 5)
        jjm_surat.validate(res, raw)
        # Surat (KeyValue 492): Value 383576, Total 383576, Per 100.00, ISHGJReported 1, IsHGJCertified 0
        self.assertEqual(by[('jjm.households_with_tap', 'surat')].value, 383576)
        self.assertEqual(by[('jjm.rural_households', 'surat')].value, 383576)
        self.assertEqual(by[('jjm.tap_coverage_pct', 'surat')].value, 100.0)
        self.assertEqual(by[('jjm.har_ghar_jal_reported', 'surat')].value, 1)
        self.assertEqual(by[('jjm.har_ghar_jal_certified', 'surat')].value, 0)
        # Tapi (KeyValue 493): 239248 / 239248
        self.assertEqual(by[('jjm.rural_households', 'tapi')].value, 239248)
        o = by[('jjm.households_with_tap', 'surat')]
        self.assertEqual((o.geo_level, o.period_start, o.period_end, o.publisher_as_of),
                         ('surat_district', '2026-10-24', '2026-10-24', '2026-10-24'))
        self.assertEqual(by[('jjm.households_with_tap', 'tapi')].geo_level, 'tapi_district')

    def test_baseline_view(self):
        raw, res, by = _parse('binddistrictmap-gujarat-2019-08-15.json', '2019-08-15')
        jjm_surat.validate(res, raw)
        # As on 15 Aug 2019: Surat Value 291815 (Per 76.08 against today's total, not stored), Tapi 100229
        self.assertEqual({k: o.value for k, o in by.items()},
                         {('jjm.households_with_tap', 'surat'): 291815, ('jjm.households_with_tap', 'tapi'): 100229})
        self.assertEqual(by[('jjm.households_with_tap', 'surat')].period_start, '2019-08-15')

    def test_needs_the_view(self):
        with self.assertRaises(ValueError):
            jjm_surat.parse(raw_from_file(DIR / 'binddistrictmap-gujarat-2019-08-15.json'))

    def test_validate_rejects_inconsistent_percent(self):
        raw, res, by = _parse('binddistrictmap-gujarat-today-2026-10-24.json', 'today')
        by[('jjm.tap_coverage_pct', 'tapi')].value = 90.0
        with self.assertRaisesRegex(ValidationError, 'does not match'):
            jjm_surat.validate(res, raw)


if __name__ == '__main__':
    unittest.main()
