import unittest

from tests import FIXTURES, raw_from_file
from opencity.model import ValidationError
from opencity.sources import gsdma_rainfall as g

DIR = FIXTURES / 'gsdma_rainfall'
# page 4 (South Gujarat, with the Surat block and the state summary) of the 21-10-2026 report
REPORT = DIR / 'report-2026-10-21-page4.pdf'


class TestGsdmaRainfall(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = raw_from_file(REPORT, retrieved_at='2026-10-24T02:00:00+05:30')
        cls.res = g.parse(cls.raw)
        cls.by = {(o.metric_id, o.geo_level, o.geo_code, o.period_start): o for o in cls.res.observations}

    def get(self, metric, code, start='2026-10-21T06:00', level='surat_taluka'):
        return self.by[(metric, level, code, start)].value

    def test_counts(self):
        # 12 Surat talukas + Dist. Avg. + State Average, 4 metrics each; June..October state months
        talukas = {o.geo_code for o in self.res.observations if o.geo_level == 'surat_taluka'}
        self.assertEqual(len(talukas), 12)
        self.assertEqual(len(self.res.observations), 14 * 4 + 5)
        g.validate(self.res, self.raw)

    def test_values_read_off_the_report(self):
        # "11 Surat City   1463   1966   0   1966   134.38"
        self.assertEqual(self.get('gsdma.rain_normal_mm', 'surat_city', '1996-01-01'), 1463)
        self.assertEqual(self.get('gsdma.rain_season_mm', 'surat_city'), 1966)
        self.assertEqual(self.get('gsdma.rain_pct_of_normal', 'surat_city'), 134.38)
        self.assertEqual(self.get('gsdma.rain_24h_mm', 'surat_city', '2026-10-20T06:00'), 0)
        # "12 Umarpada   2010   2653   0   2653   131.99"; "1 Ambika   1653   2739   0   2739   165.70"
        self.assertEqual(self.get('gsdma.rain_season_mm', 'umarpada'), 2653)
        self.assertEqual(self.get('gsdma.rain_pct_of_normal', 'umarpada'), 131.99)
        self.assertEqual(self.get('gsdma.rain_normal_mm', 'ambika', '1996-01-01'), 1653)
        # "Dist. Avg.   1514.17   1758.08   0.00   1758.08   116.11"
        self.assertEqual(self.get('gsdma.rain_normal_mm', 'surat', '1996-01-01', 'surat_district'), 1514.17)
        self.assertEqual(self.get('gsdma.rain_season_mm', 'surat', level='surat_district'), 1758.08)
        self.assertEqual(self.get('gsdma.rain_pct_of_normal', 'surat', level='surat_district'), 116.11)
        # "State Average   908.88   810.68   0.00   810.68   89.19"
        self.assertEqual(self.get('gsdma.rain_normal_mm', 'gujarat', '1996-01-01', 'state'), 908.88)
        self.assertEqual(self.get('gsdma.rain_season_mm', 'gujarat', level='state'), 810.68)

    def test_periods(self):
        o = self.by[('gsdma.rain_24h_mm', 'surat_taluka', 'bardoli', '2026-10-20T06:00')]
        self.assertEqual(o.period_end, '2026-10-21T06:00')
        o = self.by[('gsdma.rain_normal_mm', 'surat_taluka', 'bardoli', '1996-01-01')]
        self.assertEqual((o.period_end, o.value), ('2025-12-31', 1511))
        o = self.by[('gsdma.rain_season_mm', 'surat_taluka', 'chorasi', '2026-10-21T06:00')]
        self.assertEqual((o.period_end, o.value), ('2026-10-21T06:00', 1104))

    def test_state_months(self):
        months = {o.period_start: (o.period_end, o.value) for o in self.res.observations
                  if o.metric_id == 'gsdma.state_month_rain_mm'}
        self.assertEqual(months['2026-07-01'], ('2026-07-31', 552.57))
        self.assertEqual(months['2026-09-01'], ('2026-09-30', 125.81))
        self.assertEqual(months['2026-10-01'], ('2026-10-21', 0.08))     # month to date
        self.assertNotIn('2026-11-01', months)                            # printed 0.00, not started yet

    def test_geos(self):
        geos = {(x.geo_level, x.geo_code): x for x in self.res.geos}
        city = geos[('surat_taluka', 'surat_city')]
        self.assertEqual((city.parent_level, city.parent_code), ('surat_district', 'surat'))
        self.assertIn(('state', 'gujarat'), geos)

    def test_shifted_column_is_rejected(self):
        bad = g.Result(observations=list(self.res.observations))
        o = self.by[('gsdma.rain_pct_of_normal', 'surat_taluka', 'olpad', '2026-10-21T06:00')]
        bad.observations[bad.observations.index(o)] = g.Obs(o.metric_id, o.geo_level, o.geo_code, o.period_start,
                                                            o.period_end, value=13.28)
        with self.assertRaises(ValidationError):
            g.validate(bad, self.raw)

    def test_list(self):
        raw = raw_from_file(DIR / 'list-2026-trimmed.json')
        self.assertEqual(g.parse(raw).observations, [])
        links = g.report_links(raw.body)
        self.assertEqual(len(links), 6)
        self.assertEqual(links[0][0], '2026-06-02')
        self.assertEqual(links[-1], ('2026-10-21', 'https://www.gsdma.org/uploads/Rainfall/'
                                                   '24hrsrainfalldata21stoctober10212026061622397.pdf'))

    def test_interval(self):
        from datetime import datetime
        self.assertEqual(g.interval_hours(datetime(2026, 7, 1)), 12)
        self.assertEqual(g.interval_hours(datetime(2027, 2, 1)), 24 * 7)


if __name__ == '__main__':
    unittest.main()
