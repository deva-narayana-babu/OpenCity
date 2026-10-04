"""smc_air_quality against the frozen CAAQMS and results pages, plus one saved response of the JSON request the
results page makes (tests/fixtures/smc_air_quality/live-sci-2026-10-05.json, fetched 2026-10-05 01:05 IST)."""
import json
import unittest

from tests import FIXTURES, REFERENCE, raw_from_file
from opencity.model import ValidationError
from opencity.sources import smc_air_quality as aq

LIVE = FIXTURES / 'smc_air_quality/live-sci-2026-10-05.json'


class TestStationsPage(unittest.TestCase):
    def setUp(self):
        self.raw = raw_from_file(REFERENCE / 'health-environment/smc-caaqms-2026-09-28.html', url=aq.CAAQMS_URL)
        self.res = aq.parse(self.raw)
        self.rec = {(r.record_type, r.record_key): r.attrs for r in self.res.records}

    def test_counts(self):
        aq.validate(self.res, self.raw)
        self.assertEqual(self.res.observations, [])
        self.assertEqual(sum(t == 'aq_station' for t, _ in self.rec), 9)            # 7 GPCB manual + 2 SMC sensor
        self.assertEqual(sum(t == 'aq_station_proposed' for t, _ in self.rec), 7)   # 4 by SMC + 3 by GPCB
        self.assertEqual(set(self.res.complete_record_types), {'aq_station', 'aq_station_proposed'})

    def test_values_read_off_the_page(self):
        # GPCB station 1: SVNIT, 21°10'00.7"N 72°46'54.2"E
        a = self.rec[('aq_station', 'gpcb-manual/21.1669,72.7817')]
        self.assertEqual(a['coordinates_published'], '21°10\'00.7"N 72°46\'54.2"E')
        self.assertAlmostEqual(a['latitude'], 21 + 10 / 60 + 0.7 / 3600, places=6)
        self.assertAlmostEqual(a['longitude'], 72 + 46 / 60 + 54.2 / 3600, places=6)
        self.assertIn('SVNIT', a['location'])
        # SMC sensor: Varachha Zone Office, Latitude:21.20335 Longitude:72.846603
        v = self.rec[('aq_station', 'smc-sensor/varachha-zone-office')]
        self.assertEqual((v['latitude'], v['longitude'], v['operator']), (21.20335, 72.846603, 'SMC'))
        # proposed by GPCB: South West Zone, Kavi Veer Narmad Library
        p = self.rec[('aq_station_proposed', 'proposed-gpcb/kavi-veer-narmad-library-ghoddod-road')]
        self.assertEqual((p['proposed_by'], p['zone_as_published']), ('GPCB', 'South West Zone'))

    def test_dms(self):
        self.assertEqual(aq.dms_to_decimal('21°06\'04.4"N 72°58\'09.7"E'), (21.101222, 72.969361))
        with self.assertRaises(ValueError):
            aq.dms_to_decimal('somewhere in Surat')


class TestResultsPage(unittest.TestCase):
    def test_document_records_only(self):
        raw = raw_from_file(REFERENCE / 'health-environment/smc-air-quality-results-index-2026-09-27.html',
                            url=aq.RESULTS_URL)
        res = aq.parse(raw)
        aq.validate(res, raw)
        # the "0 ug/m3" placeholders of the real-time widget are not readings: nothing emitted from this page
        self.assertEqual(res.observations, [])
        docs = {r.record_key: r.attrs for r in res.records}
        self.assertEqual(sorted(docs), ['smc-aq-results/limbayat/2018', 'smc-aq-results/limbayat/2020',
                                        'smc-aq-results/limbayat/2021', 'smc-aq-results/varachha/2018',
                                        'smc-aq-results/varachha/2019', 'smc-aq-results/varachha/2020',
                                        'smc-aq-results/varachha/2021'])
        d = docs['smc-aq-results/varachha/2021']
        self.assertEqual(d['url'], 'https://www.suratmunicipal.gov.in/Content/Documents/Departments/AQMCell/'
                                   'Results/Varachha/2021.pdf')
        self.assertEqual((d['year'], d['station'], d['parsed']), (2021, 'Varachha', False))


class TestLiveReading(unittest.TestCase):
    def setUp(self):
        self.raw = raw_from_file(LIVE, url=aq.LIVE_URL, retrieved_at='2026-10-05T01:05:00+05:30')
        self.res = aq.parse(self.raw)
        self.by = {o.metric_id: o for o in self.res.observations}

    def test_values_read_off_the_json(self):
        aq.validate(self.res, self.raw)
        self.assertEqual(len(self.res.observations), 6)
        self.assertEqual(self.by['air.smc_sensor_pm25_ugm3'].value, 50.0)
        self.assertEqual(self.by['air.smc_sensor_pm10_ugm3'].value, 73.0)
        self.assertEqual(self.by['air.smc_sensor_so2_ugm3'].value, 13.8)
        self.assertEqual(self.by['air.smc_sensor_nox_ugm3'].value, 15.05)
        self.assertEqual(self.by['air.smc_sensor_temperature_c'].value, 28.34)
        self.assertEqual(self.by['air.smc_sensor_relative_humidity_pct'].value, 73.05)

    def test_time_and_station(self):
        # dtl_date /Date(1790620200000)/ = 2026-09-29 00:00 IST, testing_time 20:24:23
        o = self.by['air.smc_sensor_pm25_ugm3']
        self.assertEqual((o.period_start, o.period_end), ('2026-09-29T20:24', '2026-09-29T20:24'))
        self.assertEqual((o.geo_level, o.geo_code), ('aq_station', 'smc-sensor-0034'))
        self.assertIn(('aq_station', 'smc-sensor-0034'), {(g.geo_level, g.geo_code) for g in self.res.geos})

    def test_co_aqi_and_unitless_fields_not_emitted(self):
        self.assertEqual(set(self.by), set(aq.LIVE_FIELDS.values()))
        self.assertFalse(any('co' in m.split('_') or 'aqi' in m for m in self.by))

    def test_empty_feed_gives_no_readings(self):
        raw = raw_from_file(LIVE, url=aq.LIVE_URL)
        raw.body = json.dumps({'data': None, 'status': 200}).encode()
        res = aq.parse(raw)
        self.assertEqual(res.observations, [])
        aq.validate(res, raw)

    def test_null_value_is_not_reported(self):
        raw = raw_from_file(LIVE, url=aq.LIVE_URL, retrieved_at='2026-10-05T01:05:00+05:30')
        j = json.loads(raw.body)
        j['data']['PM10'] = None
        raw.body = json.dumps(j).encode()
        o = next(o for o in aq.parse(raw).observations if o.metric_id == 'air.smc_sensor_pm10_ugm3')
        self.assertEqual((o.status, o.value), ('not_reported', None))

    def test_validate_rejects_future_reading_and_bad_values(self):
        early = raw_from_file(LIVE, url=aq.LIVE_URL, retrieved_at='2026-09-28T12:00:00+05:30')
        with self.assertRaises(ValidationError):
            aq.validate(self.res, early)
        raw = raw_from_file(LIVE, url=aq.LIVE_URL, retrieved_at='2026-10-05T01:05:00+05:30')
        j = json.loads(raw.body)
        j['data']['Relative_Humidity'] = 173.05
        raw.body = json.dumps(j).encode()
        with self.assertRaises(ValidationError):
            aq.validate(aq.parse(raw), raw)


if __name__ == '__main__':
    unittest.main()
