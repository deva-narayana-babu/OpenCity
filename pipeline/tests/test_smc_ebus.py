import unittest

from tests import REFERENCE, raw_from_file
from opencity.model import ValidationError
from opencity.sources import smc_ebus

FIXTURE = REFERENCE / 'governance/smc-brts-ebus-operations-2026-09-27.html'


class TestSmcEbus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = raw_from_file(FIXTURE, retrieved_at='2026-09-27T12:00:00+05:30')
        cls.res = smc_ebus.parse(cls.raw)
        cls.by = {o.metric_id: o for o in cls.res.observations}

    def test_counts(self):
        self.assertEqual(len(self.res.observations), 6)
        self.assertEqual(set(self.by), {m.id for m in smc_ebus.SOURCE.metrics})
        smc_ebus.validate(self.res, self.raw)

    def test_values_read_off_the_page(self):
        # "Total No. of Electric Buses Operated: 450"; totals row 23622009.74 | 22491.96 | 60278.43 | 63306981.51 | 77464469.40
        self.assertEqual(self.by['ebus.buses_operated'].value, 450)
        self.assertAlmostEqual(self.by['ebus.fuel_saved_litres_total'].value, 23622009.74)
        self.assertAlmostEqual(self.by['ebus.fuel_saved_litres_per_day'].value, 22491.96)
        self.assertAlmostEqual(self.by['ebus.ghg_reduction_kg_co2e_per_day'].value, 60278.43)
        self.assertAlmostEqual(self.by['ebus.ghg_reduction_kg_co2e_total'].value, 63306981.51)
        self.assertAlmostEqual(self.by['ebus.run_km_total'].value, 77464469.40)

    def test_dated_to_last_updated(self):
        # "Last updated on date: 30/04/2026"
        for o in self.res.observations:
            self.assertEqual((o.geo_level, o.geo_code), ('smc_city', 'smc'))
            self.assertEqual((o.period_start, o.period_end, o.publisher_as_of), ('2026-04-30',) * 3)
            self.assertEqual(o.status, 'reported')

    def test_validate_rejects_shuffled_columns(self):
        body = FIXTURE.read_bytes().replace(b'<th>Total saved fuel (In Litres)</th>', b'<th>Total Run Km X</th>', 1)
        body = body.replace(b'<th>Total Run Km</th>', b'<th>Total saved fuel (In Litres)</th>', 1)
        body = body.replace(b'<th>Total Run Km X</th>', b'<th>Total Run Km</th>', 1)
        raw = raw_from_file(FIXTURE, retrieved_at='2026-09-27T12:00:00+05:30')
        raw.body = body
        with self.assertRaises(ValidationError):
            smc_ebus.validate(smc_ebus.parse(raw), raw)

    def test_missing_date_fails_loudly(self):
        raw = raw_from_file(FIXTURE)
        raw.body = raw.body.replace(b'Last updated on date', b'Updated')
        with self.assertRaises(ValueError):
            smc_ebus.parse(raw)


if __name__ == '__main__':
    unittest.main()
