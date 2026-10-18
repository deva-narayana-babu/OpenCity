import unittest

from tests import FIXTURES, REFERENCE, raw_from_file
from opencity.model import ValidationError
from opencity.sources import gujcourts_surat

DISTRICT = REFERENCE / 'governance/gujarat-courts-justice-clock-surat-district-2026-09-27.html'
SMALL_CAUSE = FIXTURES / 'gujcourts_surat/small-cause-court-gjsr15-2026-10-18.html'


def _by(res):
    return {(o.metric_id, o.dims['window']): o for o in res.observations}


class TestGujcourtsSurat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = raw_from_file(DISTRICT, retrieved_at='2026-09-27T13:11:00+05:30')
        cls.res = gujcourts_surat.parse(cls.raw)
        cls.by = _by(cls.res)
        cls.est_raw = raw_from_file(SMALL_CAUSE, retrieved_at='2026-10-18T00:54:00+05:30')
        cls.est = gujcourts_surat.parse(cls.est_raw)

    def test_counts(self):
        self.assertEqual(len(self.res.observations), 18)
        self.assertEqual(len(self.est.observations), 18)
        gujcourts_surat.validate(self.res, self.raw)
        gujcourts_surat.validate(self.est, self.est_raw)

    def test_district_values_read_off_the_page(self):
        # Today 275 | 77 | 28%;  Last Month 13223 | 5307 | 40%;  This Year 652503 | 656365 | 101%;  Last Year 434812 | 433874 | 100%
        self.assertEqual(self.by[('courts.cases_instituted', 'today')].value, 275)
        self.assertEqual(self.by[('courts.cases_disposed', 'today')].value, 77)
        self.assertEqual(self.by[('courts.clearance_rate_pct', 'today')].value, 28)
        self.assertEqual(self.by[('courts.cases_instituted', 'last_month')].value, 13223)
        self.assertEqual(self.by[('courts.cases_disposed', 'this_year')].value, 656365)
        self.assertEqual(self.by[('courts.clearance_rate_pct', 'this_year')].value, 101)
        self.assertEqual(self.by[('courts.cases_instituted', 'last_year')].value, 434812)
        o = self.by[('courts.cases_disposed', 'last_week')]   # Last Week 2042 | 1047 | 51%
        self.assertEqual((o.value, o.geo_level, o.geo_code), (1047, 'surat_district', 'surat'))
        # clock date <p id="date">27/09/2026</p>
        self.assertEqual((o.period_start, o.period_end, o.publisher_as_of), ('2026-09-27',) * 3)

    def test_establishment_page(self):
        # GJSR15 SMALL CAUSE COURT-SURAT (selected), clock 17/10/2026: Today 1 | 0 | --;  Last Year 1401 | 3028 | 216%
        by = _by(self.est)
        today_ccr = by[('courts.clearance_rate_pct', 'today')]
        self.assertEqual((today_ccr.value, today_ccr.status), (None, 'not_reported'))
        self.assertEqual(by[('courts.cases_instituted', 'today')].value, 1)
        self.assertEqual(by[('courts.cases_disposed', 'last_year')].value, 3028)
        self.assertEqual(by[('courts.clearance_rate_pct', 'last_year')].value, 216)
        o = by[('courts.cases_instituted', 'last_year')]
        self.assertEqual((o.geo_level, o.geo_code, o.period_start), ('court_establishment', 'gjsr15', '2026-10-17'))
        geo = next(g for g in self.est.geos if g.geo_level == 'court_establishment')
        self.assertEqual((geo.name, geo.parent_level, geo.parent_code),
                         ('SMALL CAUSE COURT-SURAT', 'surat_district', 'surat'))

    def test_establishment_list_for_fetch(self):
        codes = [c for c, _, _ in gujcourts_surat._options(self.raw.text) if c != 'ALL']
        self.assertEqual(len(codes), 14)
        self.assertEqual(codes[:3], ['GJSR15', 'GJSR10', 'GJSR12'])

    def test_validate_rejects_swapped_columns(self):
        raw = raw_from_file(DISTRICT, retrieved_at='2026-09-27T13:11:00+05:30')
        raw.body = raw.body.replace(b'>INSTITUTION<', b'>X<').replace(b'>DISPOSAL<', b'>INSTITUTION<').replace(b'>X<', b'>DISPOSAL<')
        with self.assertRaises(ValidationError):
            gujcourts_surat.validate(gujcourts_surat.parse(raw), raw)

    def test_validate_rejects_stale_clock(self):
        raw = raw_from_file(DISTRICT, retrieved_at='2026-12-01T10:00:00+05:30')
        with self.assertRaises(ValidationError):
            gujcourts_surat.validate(gujcourts_surat.parse(raw), raw)

    def test_other_district_is_refused(self):
        ahmedabad = REFERENCE / 'governance/gujarat-courts-justice-clock-ahmedabad-rural-2026-09-27.html'
        with self.assertRaises(ValueError):
            gujcourts_surat.parse(raw_from_file(ahmedabad))


if __name__ == '__main__':
    unittest.main()
