import unittest

from tests import REFERENCE, raw_from_file
from opencity.sources import smc_swm


class TestSmcSwm(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.res = smc_swm.parse(raw_from_file(REFERENCE / 'health-environment/smc-swm-statistics-2026-09-28.html'))
        cls.by = {(o.metric_id, o.period_start, o.dims.get('mode')): o for o in cls.res.observations}

    def test_counts(self):
        self.assertEqual(len(self.res.observations), 3410)
        smc_swm.validate(self.res, None)

    def test_values_read_off_the_page(self):
        # Table 1 (door to door), July-2026: 678 vehicles, 1555 trips, 2440.770 t/day
        self.assertEqual(self.by[('swm.vehicles_utilized', '2026-07-01', 'door_to_door')].value, 678)
        self.assertEqual(self.by[('swm.total_trips', '2026-07-01', 'door_to_door')].value, 1555)
        self.assertAlmostEqual(self.by[('swm.avg_collection_mt_per_day', '2026-07-01', 'door_to_door')].value, 2440.77)
        # Legacy table 1 (door to door), October-2008: 615.124 t/day
        self.assertAlmostEqual(self.by[('swm.avg_collection_mt_per_day', '2008-10-01', 'door_to_door')].value, 615.124)
        # Smart dustbins (table 5), April-2019: 73 installed
        self.assertEqual(self.by[('swm.smart_dustbins_installed', '2019-04-01', 'smart_underground_dustbins')].value, 73)

    def test_geography_and_periods(self):
        o = self.by[('swm.total_trips', '2026-07-01', 'door_to_door')]
        self.assertEqual((o.geo_level, o.geo_code, o.period_end), ('smc_city', 'smc', '2026-07-31'))


if __name__ == '__main__':
    unittest.main()
