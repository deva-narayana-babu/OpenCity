import dataclasses
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from tests import REFERENCE, raw_from_file
from opencity import db, runner
from opencity.model import ValidationError
from opencity.registry import Adapter
from opencity.sources import smc_rainfall

FIXTURE = REFERENCE / 'district-modules/smc-rainfall-ukai-levels-2026-09-28.html'
ZONES8 = {'central', 'west', 'north', 'east_a', 'east_b', 'south', 'south_west', 'south_east'}


def _raw(body: bytes | None = None, retrieved_at: str = '2026-09-28T02:12:37+05:30'):
    raw = raw_from_file(FIXTURE, url=smc_rainfall.URL)
    return dataclasses.replace(raw, body=raw.body if body is None else body, retrieved_at=retrieved_at)


def _index(res):
    return {(o.metric_id, o.geo_code, o.period_start): o for o in res.observations}


class TestSmcRainfall(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.body = FIXTURE.read_bytes()
        cls.res = smc_rainfall.parse(_raw())
        cls.by = _index(cls.res)

    def count(self, metric):
        return sum(1 for o in self.res.observations if o.metric_id == metric)

    def test_counts(self):
        self.assertEqual(len(self.res.observations), 198)
        expected = {
            'flood.dam_level_ft': 10, 'flood.dam_inflow_cusec': 10, 'flood.dam_outflow_cusec': 10,
            'flood.dam_frl_ft': 1, 'flood.weir_level_m': 10, 'flood.weir_outflow_cusec': 10,
            'flood.causeway_overflow_level_m': 1, 'flood.causeway_status': 1, 'rain.smc_zone_mm': 80,
            'rain.smc_total_mm': 10, 'flood.creek_level_m': 50, 'flood.creek_danger_level_m': 5,
        }
        for metric, n in expected.items():
            self.assertEqual(self.count(metric), n, metric)
        smc_rainfall.validate(self.res, _raw())
        smc_rainfall.validate(self.res, None)

    def test_ukai_values_read_off_the_page(self):
        # "27/09/2026 24:00 | 337.82 | 6133.00 | 6133.00" -> midnight at the start of 28/09
        o = self.by[('flood.dam_level_ft', 'ukai', '2026-09-28T00:00')]
        self.assertEqual((o.geo_level, o.period_end, o.status), ('dam', '2026-09-28T00:00', 'reported'))
        self.assertAlmostEqual(o.value, 337.82)
        self.assertIsNone(o.publisher_as_of)    # "Last Updated on" is the server render time
        self.assertEqual(self.by[('flood.dam_inflow_cusec', 'ukai', '2026-09-28T00:00')].value, 6133)
        self.assertEqual(self.by[('flood.dam_outflow_cusec', 'ukai', '2026-09-28T00:00')].value, 6133)
        # "27/09/2026 20:00 | 337.82 | 0.00 | 6126.00": a published 0, kept as 0
        self.assertEqual(self.by[('flood.dam_inflow_cusec', 'ukai', '2026-09-27T20:00')].value, 0)
        self.assertEqual(self.by[('flood.dam_inflow_cusec', 'ukai', '2026-09-27T20:00')].status, 'reported')
        self.assertEqual(self.by[('flood.dam_outflow_cusec', 'ukai', '2026-09-27T20:00')].value, 6126)
        # "27/09/2026 18:00 | 337.83 | 6119.00 | 6119.00" and "27/09/2026 06:00 | 337.83 | 800.00 | 800.00"
        self.assertAlmostEqual(self.by[('flood.dam_level_ft', 'ukai', '2026-09-27T18:00')].value, 337.83)
        self.assertEqual(self.by[('flood.dam_inflow_cusec', 'ukai', '2026-09-27T18:00')].value, 6119)
        self.assertEqual(self.by[('flood.dam_outflow_cusec', 'ukai', '2026-09-27T06:00')].value, 800)
        # "Ukai Full Reservoir Level - 345 ft", dated to the day of the latest reading
        self.assertEqual(self.by[('flood.dam_frl_ft', 'ukai', '2026-09-28')].value, 345)

    def test_weir_values_read_off_the_page(self):
        # "27/09/2026 24:00 | 5.55 | 0.00" ... "27/09/2026 08:00 | 5.58 | 0.00"
        o = self.by[('flood.weir_level_m', 'surat_weir_causeway', '2026-09-28T00:00')]
        self.assertEqual(o.geo_level, 'weir')
        self.assertAlmostEqual(o.value, 5.55)
        self.assertAlmostEqual(self.by[('flood.weir_level_m', 'surat_weir_causeway', '2026-09-27T08:00')].value, 5.58)
        self.assertAlmostEqual(self.by[('flood.weir_level_m', 'surat_weir_causeway', '2026-09-27T16:00')].value, 5.57)
        self.assertEqual(self.by[('flood.weir_outflow_cusec', 'surat_weir_causeway', '2026-09-28T00:00')].value, 0)
        # "Causeway overflow at 6.0 mt." / "Causeway is OPEN"
        self.assertEqual(self.by[('flood.causeway_overflow_level_m', 'surat_weir_causeway', '2026-09-28')].value, 6.0)
        st = self.by[('flood.causeway_status', 'surat_weir_causeway', '2026-09-28T00:00')]
        self.assertEqual((st.value, st.value_text, st.status), (None, 'OPEN', 'reported'))

    def test_zone_rainfall(self):
        zone_obs = [o for o in self.res.observations if o.metric_id == 'rain.smc_zone_mm']
        self.assertEqual({o.geo_code for o in zone_obs}, ZONES8)       # single "South Zone" -> 'south'
        self.assertTrue(all(o.geo_level == 'smc_zone' for o in zone_obs))
        # every slot on 27/09/2026 reads 0.00 in every zone
        self.assertTrue(all(o.value == 0 and o.status == 'reported' for o in zone_obs))
        self.assertEqual(min(o.period_start for o in zone_obs), '2026-09-27T06:00')
        self.assertEqual(max(o.period_start for o in zone_obs), '2026-09-28T00:00')
        self.assertIn('south', {g.geo_code for g in self.res.geos if g.geo_level == 'smc_zone'})

    def test_total_rainfall(self):
        o = self.by[('rain.smc_total_mm', 'smc', '2026-09-28T00:00')]
        self.assertEqual((o.geo_level, o.value), ('smc_city', 1983))
        self.assertEqual(self.by[('rain.smc_total_mm', 'smc', '2026-09-27T06:00')].value, 1983)

    def test_creek_levels_and_danger_levels(self):
        # "28/09/2026 00:00 | 5.20 | 5.50 | 6.50 | 5.40 | 1.90" (hourly table)
        latest = {'kakara_khadi_udhana': 5.20, 'bhedwad_khadi_udhana': 5.50, 'mithi_khadi_limbayat': 6.50,
                  'bhatena_khadi_limbayat': 5.40, 'simada_khadi_varachha': 1.90}
        for code, v in latest.items():
            o = self.by[('flood.creek_level_m', code, '2026-09-28T00:00')]
            self.assertEqual(o.geo_level, 'creek')
            self.assertAlmostEqual(o.value, v, msg=code)
        self.assertAlmostEqual(self.by[('flood.creek_level_m', 'mithi_khadi_limbayat', '2026-09-27T15:00')].value, 6.50)
        # header "(D.L.- 8.48 MT)" etc.
        danger = {'kakara_khadi_udhana': 8.48, 'bhedwad_khadi_udhana': 7.2, 'mithi_khadi_limbayat': 9.35,
                  'bhatena_khadi_limbayat': 8.25, 'simada_khadi_varachha': 4.50}
        for code, v in danger.items():
            self.assertAlmostEqual(self.by[('flood.creek_danger_level_m', code, '2026-09-28')].value, v, msg=code)
        geos = {g.geo_code: g for g in self.res.geos if g.geo_level == 'creek'}
        self.assertEqual(set(geos), set(latest))
        self.assertEqual(geos['kakara_khadi_udhana'].name, 'Kakara Khadi (Udhana Zone gauge)')
        self.assertEqual((geos['simada_khadi_varachha'].parent_level, geos['simada_khadi_varachha'].parent_code),
                         ('smc_city', 'smc'))

    def test_geographies(self):
        geos = {(g.geo_level, g.geo_code): g for g in self.res.geos}
        ukai = geos[('dam', 'ukai')]
        self.assertEqual((ukai.parent_level, ukai.parent_code), ('tapi_district', 'tapi'))
        self.assertIn(('weir', 'surat_weir_causeway'), geos)
        used = {(o.geo_level, o.geo_code) for o in self.res.observations}
        self.assertTrue(used <= set(geos), used - set(geos))
        self.assertNotIn('surat_district', {lvl for lvl, _ in used})

    def test_blank_and_dash_cells_are_not_reported(self):
        body = self.body.replace(b'337.82<span class="equal"></span>', b'-<span class="equal"></span>', 1)
        body = body.replace(b'1983.00', b' ', 1)
        by = _index(smc_rainfall.parse(_raw(body)))
        o = by[('flood.dam_level_ft', 'ukai', '2026-09-28T00:00')]
        self.assertEqual((o.value, o.status), (None, 'not_reported'))
        o = by[('rain.smc_total_mm', 'smc', '2026-09-28T00:00')]
        self.assertEqual((o.value, o.status), (None, 'not_reported'))
        self.assertEqual(by[('rain.smc_total_mm', 'smc', '2026-09-27T22:00')].value, 1983)

    def test_non_numeric_cell_fails_loudly(self):
        body = self.body.replace(b'337.82<span class="equal"></span>', b'gauge down<span></span>', 1)
        with self.assertRaises(ValueError):
            smc_rainfall.parse(_raw(body))

    def test_layout_change_fails_loudly(self):
        with self.assertRaises(ValueError):
            smc_rainfall.parse(_raw(self.body.replace(b'role="tabpanel"', b'role="region"')))
        # creek table no longer recognised -> too few creek readings
        res = smc_rainfall.parse(_raw(self.body.replace(b'Khadi', b'Nala')))
        with self.assertRaises(ValidationError):
            smc_rainfall.validate(res, _raw())

    def test_validate_rejects_implausible_values(self):
        body = self.body.replace(b'337.82<span class="equal"></span>', b'3378.2<span class="equal"></span>', 1)
        with self.assertRaisesRegex(ValidationError, 'flood.dam_level_ft'):
            smc_rainfall.validate(smc_rainfall.parse(_raw(body)), _raw())
        body = self.body.replace(b'Bhedwad Khadi Udhana Zone<div>(D.L.- 7.2 MT)',
                                 b'Bhedwad Khadi Udhana Zone<div>(D.L.- 72 MT)')
        with self.assertRaisesRegex(ValidationError, 'danger'):
            smc_rainfall.validate(smc_rainfall.parse(_raw(body)), _raw())

    def test_validate_rejects_readings_after_retrieval(self):
        with self.assertRaisesRegex(ValidationError, 'future'):
            smc_rainfall.validate(self.res, _raw(retrieved_at='2026-09-20T10:00:00+05:30'))

    def test_validate_rejects_misread_dates(self):
        # one Ukai row dated two months earlier: the table window would span > 31 days
        body = self.body.replace(b'27/09/2026 &nbsp;&nbsp; 06:00', b'27/07/2026 &nbsp;&nbsp; 06:00', 1)
        with self.assertRaisesRegex(ValidationError, 'span'):
            smc_rainfall.validate(smc_rainfall.parse(_raw(body)), _raw())

    def test_normalize_blanks_render_time(self):
        a = self.body
        b = a.replace(b'28-09-2026 02:12:37 AM', b'04-10-2026 12:38:33 AM')
        self.assertNotEqual(a, b)
        self.assertEqual(smc_rainfall.normalize(a), smc_rainfall.normalize(b))
        # the archived (normalised) body parses to the same observations
        self.assertEqual(smc_rainfall.parse(_raw(smc_rainfall.normalize(a))).observations, self.res.observations)

    def test_interval_hours(self):
        self.assertEqual(smc_rainfall.interval_hours(datetime(2026, 6, 1)), 2)
        self.assertEqual(smc_rainfall.interval_hours(datetime(2026, 10, 31, 23)), 2)
        self.assertEqual(smc_rainfall.interval_hours(datetime(2026, 11, 1)), 24)
        self.assertEqual(smc_rainfall.interval_hours(datetime(2026, 5, 31)), 24)

    def test_runner_accepts_and_reapplies_without_revisions(self):
        with tempfile.TemporaryDirectory() as d:
            conn = db.connect(Path(d) / 't.db')
            try:
                ad = Adapter(smc_rainfall.SOURCE, smc_rainfall)
                db.register_source(conn, ad.source)
                fid = db.insert_fetch(conn, source_id=ad.id, url=smc_rainfall.URL, request_key='k')
                raw = dataclasses.replace(_raw(), fetch_id=fid)
                runner.validate(ad, self.res, raw, conn)
                self.assertEqual(db.apply_result(conn, ad.source, fid, self.res, ad.parser)[0], 198)
                db.apply_result(conn, ad.source, fid, smc_rainfall.parse(raw), ad.parser)
                self.assertEqual(conn.execute('SELECT count(*) FROM observation').fetchone()[0], 198)
                self.assertEqual(conn.execute('SELECT count(*) FROM observation_revision').fetchone()[0], 0)
                row = conn.execute("SELECT parent_level, parent_code FROM geo WHERE geo_level='dam' AND geo_code='ukai'"
                                   ).fetchone()
                self.assertEqual(tuple(row), ('tapi_district', 'tapi'))
            finally:
                conn.close()


if __name__ == '__main__':
    unittest.main()
