import unittest

from tests import FIXTURES, raw_from_file
from opencity.sources import smc_health_centres

FIXTURE = FIXTURES / 'smc_health_centres/pmjayuhc-2026-10-24.html'


class TestSmcHealthCentres(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = raw_from_file(FIXTURE, retrieved_at='2026-10-24T22:00:00+05:30')
        cls.res = smc_health_centres.parse(cls.raw)
        cls.rec = {r.record_key: r.attrs for r in cls.res.records}
        cls.obs = {(o.geo_level, o.geo_code, o.dims['type']): o for o in cls.res.observations}

    def test_counts(self):
        self.assertEqual(len(self.res.records), 80)
        self.assertEqual(len(self.res.observations), 9 * 2 + 2)
        self.assertEqual(self.res.complete_record_types, ('smc_health_centre',))
        smc_health_centres.validate(self.res, self.raw)

    def test_records_read_off_the_page(self):
        # West Zone (Rander): RANDER UHC, NR. RANDER BUS STAND, RANDER VILLAGE, phone 2770925
        self.assertEqual(self.rec['rander-uhc'], {
            'name': 'RANDER UHC', 'facility_type': 'uhc', 'maternity_home': False, 'zone': 'West Zone (Rander)',
            'zone_code': 'west', 'address': 'NR. RANDER BUS STAND, RANDER VILLAGE', 'phones': ['2770925']})
        # Central Zone: LAKHPATI UHC, phone "2423751-56, 381" (split at the comma, range not expanded)
        self.assertEqual(self.rec['lakhpati-uhc']['phones'], ['2423751-56', '381'])
        # "-" in the phone column means no number
        self.assertEqual(self.rec['adajan-uhc']['phones'], [])
        # type and maternity-home flag come from the name
        self.assertEqual(self.rec['pal-uchc']['facility_type'], 'uchc')
        self.assertTrue(self.rec['asarawala-uhc-mh']['maternity_home'])
        self.assertEqual(self.rec['golden-chowk-urban-health-center']['facility_type'], 'uhc')
        self.assertEqual(self.rec['bamroli-uchc']['zone_code'], 'south_a')     # "South Zone-A (Udhana)"
        self.assertEqual(self.rec['kanakpur-uhc']['zone_code'], 'south_b')     # "South Zone-B (Kanakpur)"

    def test_counts_by_zone_and_type(self):
        # South East Zone (Limbayat) lists 12 centres: 10 UHC + BHATHENA UCHC and DUMBHAL UCHC
        self.assertEqual(self.obs[('smc_zone', 'south_east', 'uhc')].value, 10)
        self.assertEqual(self.obs[('smc_zone', 'south_east', 'uchc')].value, 2)
        self.assertEqual(self.obs[('smc_zone', 'central', 'uchc')].value, 0)
        self.assertEqual(self.obs[('smc_city', 'smc', 'uhc')].value, 71)
        self.assertEqual(self.obs[('smc_city', 'smc', 'uchc')].value, 9)

    def test_dated_to_last_updated(self):
        o = self.obs[('smc_city', 'smc', 'uhc')]
        self.assertEqual((o.period_start, o.period_end, o.publisher_as_of), ('2024-06-24',) * 3)


if __name__ == '__main__':
    unittest.main()
