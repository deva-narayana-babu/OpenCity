import unittest

from tests import REFERENCE, raw_from_file
from opencity.model import ValidationError
from opencity.sources import smc_smimer

PAGE = REFERENCE / 'health-environment/smc-smimer-hospital-statistics-2026-09-27.html'


class TestSmcSmimer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = raw_from_file(PAGE, url=smc_smimer.URL, retrieved_at='2026-09-27T12:00:00+05:30')
        cls.res, cls.skipped, cls.conflicts = smc_smimer.analyse(cls.raw.body)
        cls.by = {(o.metric_id, o.period_start, tuple(sorted(o.dims.items()))): o for o in cls.res.observations}

    def get(self, metric, start, **dims):
        return self.by[(metric, start, tuple(sorted(dims.items())))]

    def test_counts_and_validate(self):
        self.assertEqual(len(self.res.observations), 4631)
        self.assertEqual(sum(o.status == 'not_reported' for o in self.res.observations), 9)
        self.assertEqual(self.conflicts, [])
        smc_smimer.validate(self.res, self.raw)
        self.assertEqual(smc_smimer.parse(self.raw).observations, self.res.observations)

    def test_values_read_off_the_page(self):
        # Milk Bank 2026: Aug 2026 collection 3760 ml; Apr 2026 donor mothers 173
        self.assertEqual(self.get('smimer.milk_collected_ml', '2026-08-01').value, 3760)
        self.assertEqual(self.get('smimer.milk_donor_mothers', '2026-04-01').value, 173)
        # Milk Bank FY 2011-12: Apr 2011 newborns receiving milk 18
        self.assertEqual(self.get('smimer.milk_recipient_newborns', '2011-04-01').value, 18)
        # Blood Bank 2026: Jan in camp 1217, Aug grand total collected 700, Jan red cell concentrate 771
        self.assertEqual(self.get('smimer.blood_units_collected', '2026-01-01', donation='voluntary_camp').value, 1217)
        self.assertEqual(self.get('smimer.blood_units_collected_total', '2026-08-01').value, 700)
        self.assertEqual(self.get('smimer.blood_components_issued', '2026-01-01',
                                  component='red_cell_concentrate').value, 771)
        # Blood Bank 2017: Apr FFP 1530, May other hospital 1348
        self.assertEqual(self.get('smimer.blood_components_issued', '2017-04-01',
                                  component='fresh_frozen_plasma').value, 1530)
        self.assertEqual(self.get('smimer.blood_units_issued_other_hospitals', '2017-05-01').value, 1348)
        # Blood Bank FY 2011-12: Apr 2011 replacement 4, grand total collected 506
        self.assertEqual(self.get('smimer.blood_units_collected', '2011-04-01', donation='replacement').value, 4)
        self.assertEqual(self.get('smimer.blood_units_collected_total', '2011-04-01').value, 506)
        # Eye Bank: Apr 2026 eyes sent to other eye bank 4; Aug 2013 paediatric 5
        self.assertEqual(self.get('smimer.eyes_utilised', '2026-04-01', use='sent_to_other_eye_bank').value, 4)
        self.assertEqual(self.get('smimer.eyes_utilised', '2013-08-01', use='paediatric').value, 5)
        # ICU 2026: Aug NCU 1043, beds NCU 26; ICU FY 2011-12: Jan 2012 PICU 72, NCU beds 13
        self.assertEqual(self.get('smimer.icu_patient_count', '2026-08-01', unit='ncu').value, 1043)
        self.assertEqual(self.get('smimer.icu_beds', '2026-01-01', unit='ncu').value, 26)
        self.assertEqual(self.get('smimer.icu_patient_count', '2012-01-01', unit='picu').value, 72)
        self.assertEqual(self.get('smimer.icu_beds', '2011-04-01', unit='ncu').value, 13)

    def test_blank_and_dash_cells_are_not_reported(self):
        o = self.get('smimer.blood_units_collected', '2024-10-01', donation='replacement')   # blank cell
        self.assertEqual((o.status, o.value), ('not_reported', None))
        o = self.get('smimer.blood_components_issued', '2018-01-01', component='cryo_poor_plasma')   # '-'
        self.assertEqual((o.status, o.value), ('not_reported', None))

    def test_unpublished_months_and_skipped_rows_are_absent(self):
        # Sep-Dec 2026 columns are empty on the page: nothing emitted for them
        self.assertNotIn(('smimer.milk_collected_ml', '2026-09-01', ()), self.by)
        self.assertNotIn(('smimer.icu_patient_count', '2026-09-01', (('unit', 'micu'),)), self.by)
        ids = {o.metric_id for o in self.res.observations}
        self.assertFalse(any('retina' in str(o.dims) for o in self.res.observations))
        self.assertNotIn('smimer.blood_units_issued_total', ids)

    def test_ambiguous_icu_tables_skipped(self):
        # "January 2016 to December 2016" and "January 2015 ..." list April..March -> skipped, nothing emitted
        self.assertEqual(len(self.skipped), 2)
        self.assertTrue(all('do not match heading' in s for s in self.skipped))
        self.assertNotIn(('smimer.icu_patient_count', '2016-04-01', (('unit', 'micu'),)), self.by)
        self.assertNotIn(('smimer.icu_beds', '2016-01-01', (('unit', 'micu'),)), self.by)
        # the neighbouring well-labelled tables are still there
        self.assertEqual(self.get('smimer.icu_patient_count', '2017-01-01', unit='micu').value, 196)
        self.assertEqual(self.get('smimer.icu_patient_count', '2014-04-01', unit='micu').value, 225)

    def test_geography_and_periods(self):
        o = self.get('smimer.icu_beds', '2026-01-01', unit='micu')
        self.assertEqual((o.geo_level, o.geo_code, o.period_end), ('facility', 'smimer', '2026-12-31'))
        o = self.get('smimer.icu_beds', '2011-04-01', unit='micu')
        self.assertEqual(o.period_end, '2012-03-31')
        self.assertIn(('facility', 'smimer'), {(g.geo_level, g.geo_code) for g in self.res.geos})

    def test_validate_rejects_future_month(self):
        early = raw_from_file(PAGE, retrieved_at='2026-05-01T00:00:00+05:30')
        with self.assertRaises(ValidationError):
            smc_smimer.validate(self.res, early)


if __name__ == '__main__':
    unittest.main()
