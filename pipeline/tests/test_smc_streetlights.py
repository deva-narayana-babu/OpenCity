import unittest

from tests import FIXTURES, raw_from_file
from opencity.sources import smc_streetlights

PAGE = FIXTURES / 'smc_streetlights/non-working-streetlights-2026-10-24.html'


class TestSmcStreetlights(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = raw_from_file(PAGE, retrieved_at='2026-10-24T22:11:06+05:30')
        cls.res = smc_streetlights.parse(cls.raw)
        cls.by = {o.period_start: o for o in cls.res.observations}

    def test_counts(self):
        # rows 1-25 in the first table, 26-48 in the second; March 2017 to February 2021
        self.assertEqual(len(self.res.observations), 48)
        self.assertEqual((min(self.by), max(self.by)), ('2017-03-01', '2021-02-01'))
        smc_streetlights.validate(self.res, self.raw)

    def test_values_read_off_the_page(self):
        self.assertEqual(self.by['2021-02-01'].value, 0.38)      # row 1, February/2021
        self.assertEqual(self.by['2019-01-01'].value, 0.34)      # row 26 (second table), January/2019
        self.assertEqual(self.by['2017-06-01'].value, 1.15)      # row 45, June/2017, the highest
        self.assertEqual(self.by['2017-03-01'].value, 0.76)      # row 48, March/2017

    def test_geography_and_periods(self):
        o = self.by['2020-02-01']
        self.assertEqual((o.metric_id, o.geo_level, o.geo_code, o.period_end, o.value),
                         ('streetlight.nonworking_pct', 'smc_city', 'smc', '2020-02-29', 0.30))


if __name__ == '__main__':
    unittest.main()
