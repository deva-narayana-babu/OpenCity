import unittest

from tests import FIXTURES, raw_from_file
from opencity.model import ValidationError
from opencity.sources import openmeteo_surat as om

FIXTURE = FIXTURES / 'openmeteo_surat/forecast-2026-10-24T0200.json'


class TestOpenMeteoSurat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = raw_from_file(FIXTURE, retrieved_at='2026-10-24T02:06:00+05:30')
        cls.res = om.parse(cls.raw)
        cls.by = {(o.metric_id, o.period_start): o for o in cls.res.observations}

    def test_counts(self):
        # 8 current values + 9 daily fields x 10 days
        self.assertEqual(len(self.res.observations), 8 + 9 * 10)
        om.validate(self.res, self.raw)

    def test_current_values_read_off_the_response(self):
        # "current": {"time": "2026-10-24T02:00", "temperature_2m": 25.9, "relative_humidity_2m": 65,
        #             "apparent_temperature": 28.0, "weather_code": 0, "surface_pressure": 1007.6, ...}
        t = '2026-10-24T02:00'
        self.assertEqual(self.by[('openmeteo.temperature_c', t)].value, 25.9)
        self.assertEqual(self.by[('openmeteo.relative_humidity_pct', t)].value, 65)
        self.assertEqual(self.by[('openmeteo.apparent_temperature_c', t)].value, 28.0)
        self.assertEqual(self.by[('openmeteo.surface_pressure_hpa', t)].value, 1007.6)
        self.assertEqual(self.by[('openmeteo.wind_direction_deg', t)].value, 59)
        code = self.by[('openmeteo.weather_code', t)]
        self.assertEqual((code.value, code.value_text), (0, 'Clear sky'))
        # precipitation is a 15-minute sum (interval 900 s) ending at current.time
        rain = self.by[('openmeteo.precipitation_mm', '2026-10-24T01:45')]
        self.assertEqual((rain.period_end, rain.value), (t, 0.0))
        self.assertEqual((rain.geo_level, rain.geo_code), ('smc_city', 'smc'))

    def test_daily_values_read_off_the_response(self):
        # 2026-10-25 (3rd index of daily.time): max 36.4, min 23.1, UV 6.35, sunrise 06:38, sunset 18:07
        d = '2026-10-25'
        self.assertEqual(self.by[('openmeteo.daily_temperature_max_c', d)].value, 36.4)
        self.assertEqual(self.by[('openmeteo.daily_temperature_min_c', d)].value, 23.1)
        self.assertEqual(self.by[('openmeteo.daily_uv_index_max', d)].value, 6.35)
        self.assertEqual(self.by[('openmeteo.sunrise', d)].value_text, '06:38')
        self.assertIsNone(self.by[('openmeteo.sunrise', d)].value)
        self.assertEqual(self.by[('openmeteo.sunset', d)].value_text, '18:07')
        # a past day (past_days=2): 2026-10-22, code 51 drizzle, rain chance 69 %, 0.2 mm
        self.assertEqual(self.by[('openmeteo.daily_weather_code', '2026-10-22')].value_text, 'Light drizzle')
        self.assertEqual(self.by[('openmeteo.daily_precip_probability_max_pct', '2026-10-22')].value, 69)
        self.assertEqual(self.by[('openmeteo.daily_precip_sum_mm', '2026-10-22')].value, 0.2)
        # last forecast day 2026-10-31: 4.2 mm
        self.assertEqual(self.by[('openmeteo.daily_precip_sum_mm', '2026-10-31')].value, 4.2)

    def test_null_is_not_reported(self):
        body = FIXTURE.read_bytes().replace(b'"temperature_2m":25.9', b'"temperature_2m":null')
        raw = raw_from_file(FIXTURE, retrieved_at='2026-10-24T02:06:00+05:30')
        raw.body = body
        o = {o.metric_id: o for o in om.parse(raw).observations if o.period_start == '2026-10-24T02:00'}
        self.assertEqual((o['openmeteo.temperature_c'].status, o['openmeteo.temperature_c'].value), ('not_reported', None))

    def test_unit_change_fails_loudly(self):
        raw = raw_from_file(FIXTURE, retrieved_at='2026-10-24T02:06:00+05:30')
        raw.body = raw.body.replace(b'"wind_speed_10m":"km/h"', b'"wind_speed_10m":"mp/h"')
        with self.assertRaises(ValidationError):
            om.parse(raw)

    def test_disabled_because_of_robots_txt(self):
        self.assertFalse(om.SOURCE.enabled)
        self.assertIn('robots.txt', om.SOURCE.notes)


if __name__ == '__main__':
    unittest.main()
