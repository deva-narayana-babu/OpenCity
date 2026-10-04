import dataclasses
import logging
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

from tests import REFERENCE, raw_from_file
from opencity import config, db, runner
from opencity.fetcher import Response
from opencity.model import Raw, ValidationError
from opencity.registry import Adapter
from opencity.sources import wrd_reservoirs as wrd

DIR = REFERENCE / 'district-modules'
FIX = {
    '2026-09-23': DIR / 'gujarat-wrd-reservoir-storage-2026-09-23.pdf',
    '2026-09-24': DIR / 'gujarat-wrd-reservoir-storage-2026-09-24.pdf',
    '2026-09-26': DIR / 'gujarat-wrd-reservoir-storage-2026-09-26.pdf',
    '2026-09-27': DIR / 'gujarat-wrd-dam-storage-2026-09-27.pdf',
}
FETCHED = '2026-09-28T02:00:00+05:30'


def _raw(day, **kw):
    return raw_from_file(FIX[day], url=wrd.report_url(datetime.fromisoformat(day).date()),
                         meta={'date': day}, retrieved_at=kw.get('retrieved_at', FETCHED))


class TestWrdReservoirs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.res = {day: wrd.parse(_raw(day)) for day in FIX}
        cls.by = {day: {(o.metric_id, o.geo_code): o for o in r.observations} for day, r in cls.res.items()}

    def v(self, day, metric, code):
        return self.by[day][(metric, code)].value

    def test_counts_and_validation(self):
        for day, res in self.res.items():
            # 4 Surat/Tapi dams x 13 metrics, Sardar Sarovar 12, Surat and Tapi district rows 6 each, Gujarat 6
            self.assertEqual(len(res.observations), 82, day)
            self.assertEqual({o.period_start for o in res.observations}, {day})
            self.assertTrue(all(o.period_start == o.period_end for o in res.observations))
            wrd.validate(res, _raw(day))
            wrd.validate(res, None)

    def test_ukai_row_with_wrapped_cells(self):
        # 23-09-2026 statement row 7: "Tapi Songadh Ukai SG G 78.77 105.156 102.98 7414.2 6729.9 684.39 6177.7
        # 5493.3 684.39 83.32% 3 1683 ALERT 6117 5317 800", with "9 0 0 1" wrapped onto the next line
        d = '2026-09-23'
        self.assertEqual(self.v(d, 'wrd.dam_level_m', 'ukai'), 102.98)
        self.assertEqual(self.v(d, 'wrd.dam_frl_m', 'ukai'), 105.156)
        self.assertEqual(self.v(d, 'wrd.design_gross_storage_mcm', 'ukai'), 7414.29)
        self.assertEqual(self.v(d, 'wrd.design_live_storage_mcm', 'ukai'), 6729.90)
        self.assertEqual(self.v(d, 'wrd.gross_storage_mcm', 'ukai'), 6177.70)
        self.assertEqual(self.v(d, 'wrd.live_storage_mcm', 'ukai'), 5493.31)
        self.assertEqual(self.v(d, 'wrd.gross_storage_pct', 'ukai'), 83.32)
        self.assertEqual(self.v(d, 'wrd.inflow_cusec', 'ukai'), 6117)
        self.assertEqual(self.v(d, 'wrd.outflow_river_cusec', 'ukai'), 5317)
        self.assertEqual(self.v(d, 'wrd.outflow_canal_cusec', 'ukai'), 800)
        self.assertEqual(self.v(d, 'wrd.rain_24h_mm', 'ukai'), 3)
        self.assertEqual(self.v(d, 'wrd.rain_cumulative_mm', 'ukai'), 1683)
        self.assertEqual(self.by[d][('wrd.alert_level', 'ukai')].value_text, 'ALERT')
        # 27-09-2026: "102.971 ... 6172.8 5488.4" with "4" and "5" wrapped below (page 3 prints 6172.84)
        self.assertEqual(self.v('2026-09-27', 'wrd.dam_level_m', 'ukai'), 102.971)
        self.assertEqual(self.v('2026-09-27', 'wrd.gross_storage_mcm', 'ukai'), 6172.84)
        self.assertEqual(self.v('2026-09-27', 'wrd.live_storage_mcm', 'ukai'), 5488.45)
        self.assertEqual(self.v('2026-09-27', 'wrd.gross_storage_pct', 'ukai'), 83.26)
        # 24-09-2026: inflow 800, outflow river 0 (a printed 0 stays 0), canal 800
        self.assertEqual(self.v('2026-09-24', 'wrd.inflow_cusec', 'ukai'), 800)
        self.assertEqual(self.by['2026-09-24'][('wrd.outflow_river_cusec', 'ukai')].status, 'reported')
        self.assertEqual(self.v('2026-09-24', 'wrd.outflow_river_cusec', 'ukai'), 0)

    def test_surat_district_dams(self):
        d = '2026-09-23'
        # "Surat Mandvi Ver-II SG G 101 115.8 114.85 31.88 31.72 0.16 27.20 27.04 0.16 85.32% 0 1187 ALERT 0 0 0"
        self.assertEqual(self.v(d, 'wrd.dam_level_m', 'ver_ii'), 114.85)
        self.assertEqual(self.v(d, 'wrd.gross_storage_mcm', 'ver_ii'), 27.20)
        self.assertEqual(self.v(d, 'wrd.gross_storage_pct', 'ver_ii'), 85.32)
        self.assertEqual(self.v(d, 'wrd.rain_cumulative_mm', 'ver_ii'), 1187)
        # 24-09-2026: Ver-II at 114.9 m, 27.43 MCM, 86.04%, 4 mm in 24 h, inflow 94 cusecs
        self.assertEqual(self.v('2026-09-24', 'wrd.dam_level_m', 'ver_ii'), 114.9)
        self.assertEqual(self.v('2026-09-24', 'wrd.gross_storage_mcm', 'ver_ii'), 27.43)
        self.assertEqual(self.v('2026-09-24', 'wrd.rain_24h_mm', 'ver_ii'), 4)
        self.assertEqual(self.v('2026-09-24', 'wrd.inflow_cusec', 'ver_ii'), 94)
        # Lakhigam: warning wrapped as "HIGH" / "ALERT"; 27-09-2026 canal outflow 15
        self.assertEqual(self.by[d][('wrd.alert_level', 'lakhigam')].value_text, 'HIGH ALERT')
        self.assertEqual(self.v(d, 'wrd.design_gross_storage_mcm', 'lakhigam'), 4.26)
        self.assertEqual(self.v('2026-09-27', 'wrd.outflow_canal_cusec', 'lakhigam'), 15)
        # district rows of the districtwise table
        self.assertEqual(self.v(d, 'wrd.design_gross_storage_mcm', 'surat'), 36.14)
        self.assertEqual(self.v(d, 'wrd.live_storage_mcm', 'surat'), 31.10)
        self.assertEqual(self.v(d, 'wrd.gross_storage_pct', 'surat'), 87.05)
        self.assertEqual(self.v(d, 'wrd.live_storage_pct', 'surat'), 86.93)
        self.assertEqual(self.v(d, 'wrd.gross_storage_mcm', 'tapi'), 6181.13)
        self.assertEqual(self.v('2026-09-27', 'wrd.gross_storage_mcm', 'tapi'), 6176.27)
        self.assertEqual(self.by[d][('wrd.gross_storage_mcm', 'tapi')].geo_level, 'tapi_district')
        # Gujarat grand total (incl. Sardar Sarovar)
        self.assertEqual(self.v(d, 'wrd.design_gross_storage_mcm', 'gujarat'), 25257.55)
        self.assertEqual(self.v(d, 'wrd.gross_storage_mcm', 'gujarat'), 20654.95)
        self.assertEqual(self.v(d, 'wrd.gross_storage_pct', 'gujarat'), 81.78)

    def test_sardar_sarovar(self):
        d = '2026-09-23'
        self.assertEqual(self.v(d, 'wrd.dam_level_m', 'sardar_sarovar'), 138.32)
        self.assertEqual(self.v(d, 'wrd.dam_frl_m', 'sardar_sarovar'), 138.68)
        self.assertEqual(self.v(d, 'wrd.gross_storage_mcm', 'sardar_sarovar'), 9344.06)
        self.assertEqual(self.v(d, 'wrd.live_storage_mcm', 'sardar_sarovar'), 5644.06)
        self.assertEqual(self.v(d, 'wrd.design_live_storage_mcm', 'sardar_sarovar'), 5760)
        self.assertEqual(self.v(d, 'wrd.gross_storage_pct', 'sardar_sarovar'), 98.77)
        self.assertEqual(self.v(d, 'wrd.live_storage_pct', 'sardar_sarovar'), 97.99)
        self.assertEqual(self.by[d][('wrd.alert_level', 'sardar_sarovar')].value_text, 'HIGH ALERT')
        self.assertEqual(self.v(d, 'wrd.inflow_cusec', 'sardar_sarovar'), 41296)
        self.assertEqual(self.v(d, 'wrd.outflow_river_cusec', 'sardar_sarovar'), 619)
        self.assertEqual(self.v(d, 'wrd.outflow_canal_cusec', 'sardar_sarovar'), 11712.38)
        self.assertEqual(self.v('2026-09-24', 'wrd.outflow_river_cusec', 'sardar_sarovar'), 12022)
        self.assertEqual(self.v('2026-09-26', 'wrd.inflow_cusec', 'sardar_sarovar'), 9729)

    def test_geographies(self):
        geos = {g.geo_code: g for g in self.res['2026-09-23'].geos if g.geo_level == 'dam'}
        self.assertEqual(set(geos), {'ukai', 'doswada', 'lakhigam', 'ver_ii', 'sardar_sarovar'})
        # Ukai is physically in Tapi district (Songadh taluka), never a Surat dam
        self.assertEqual((geos['ukai'].parent_level, geos['ukai'].parent_code), ('tapi_district', 'tapi'))
        self.assertEqual(geos['ukai'].name, 'Ukai dam (Tapi river)')
        self.assertIsNone(geos['ukai'].note)        # keeps the note smc_rainfall writes for the shared geo
        self.assertEqual(geos['doswada'].parent_code, 'tapi')
        self.assertEqual((geos['lakhigam'].parent_level, geos['ver_ii'].parent_code), ('surat_district', 'surat'))
        self.assertIn('Mandvi taluka', geos['ver_ii'].note)
        self.assertEqual(geos['sardar_sarovar'].parent_level, 'state')

    def test_validation_rejects(self):
        res = self.res['2026-09-23']
        with self.assertRaisesRegex(ValidationError, 'asked for'):
            wrd.validate(res, dataclasses.replace(_raw('2026-09-23'), meta={'date': '2026-09-24'}))
        with self.assertRaisesRegex(ValidationError, 'after the fetch time'):
            wrd.validate(res, _raw('2026-09-23', retrieved_at='2026-09-22T23:00:00+05:30'))
        # a dropped wrapped digit (7414.2 instead of 7414.29) no longer adds up to the Tapi district row
        bad = dataclasses.replace(res, observations=[
            dataclasses.replace(o, value=7414.2) if (o.metric_id, o.geo_code) == ('wrd.design_gross_storage_mcm', 'ukai')
            else o for o in res.observations])
        with self.assertRaisesRegex(ValidationError, 'tapi district'):
            wrd.validate(bad, None)
        bad = dataclasses.replace(res, observations=[
            dataclasses.replace(o, value=50) if (o.metric_id, o.geo_code) == ('wrd.gross_storage_pct', 'ver_ii')
            else o for o in res.observations])
        with self.assertRaisesRegex(ValidationError, 'printed 50'):
            wrd.validate(bad, None)
        with self.assertRaisesRegex(ValidationError, 'not a PDF'):
            wrd.parse(dataclasses.replace(_raw('2026-09-23'), body=b''))

    def test_runner_accepts_the_result(self):
        with tempfile.TemporaryDirectory() as d:
            conn = db.connect(Path(d) / 't.db')
            try:
                ad = Adapter(wrd.SOURCE, wrd)
                db.register_source(conn, ad.source)
                fid = db.insert_fetch(conn, source_id=ad.id, url='u', request_key='k')
                raw = dataclasses.replace(_raw('2026-09-23'), fetch_id=fid)
                runner.validate(ad, self.res['2026-09-23'], raw, conn)
                self.assertEqual(db.apply_result(conn, ad.source, fid, self.res['2026-09-23'], ad.parser)[0], 82)
            finally:
                conn.close()


class FakeFetcher:
    def __init__(self, pages):
        self.pages = pages
        self.calls = []

    def request(self, method, url, **kw):
        self.calls.append(url)
        body = self.pages[url]
        if isinstance(body, Exception):
            raise body
        return Response(200, body, url, {'content-type': 'application/pdf'})


class TestWrdFetch(unittest.TestCase):
    """fetch(): last 4 report dates, empty (not yet published) answers are not stored as parsed."""

    def test_refresh_skips_parsed_dates_and_retries_unpublished(self):
        now = datetime(2026, 9, 27, 10, 0, tzinfo=config.TZ)
        url = {day: wrd.report_url(datetime.fromisoformat(day).date())
               for day in ('2026-09-24', '2026-09-25', '2026-09-26', '2026-09-27')}
        f = FakeFetcher({url['2026-09-24']: FIX['2026-09-24'].read_bytes(), url['2026-09-25']: b'',
                         url['2026-09-26']: FIX['2026-09-26'].read_bytes(),
                         url['2026-09-27']: FIX['2026-09-27'].read_bytes()})
        with tempfile.TemporaryDirectory() as d, mock.patch('opencity.config.now', return_value=now):
            conn = db.connect(Path(d) / 't.db')
            try:
                ad = Adapter(wrd.SOURCE, wrd)
                logging.disable(logging.INFO)
                out = runner.refresh(conn, [ad], data_dir=Path(d), fetcher=f)
                self.assertEqual(out['wrd_reservoirs'], 'ok: 3 document(s), 246 observation(s), 0 record(s)')
                self.assertEqual(f.calls, [url[k] for k in sorted(url)])
                days = [r[0] for r in conn.execute("SELECT DISTINCT period_start FROM observation ORDER BY 1")]
                self.assertEqual(days, ['2026-09-24', '2026-09-26', '2026-09-27'])
                # second run: parsed dates are skipped, the empty one is asked for again
                out = runner.refresh(conn, [ad], data_dir=Path(d), fetcher=f)
                self.assertEqual(f.calls[4:], [url['2026-09-25']])
                self.assertTrue(out['wrd_reservoirs'].startswith('ok: 0 document(s)'), out)
            finally:
                logging.disable(logging.NOTSET)
                conn.close()

    def test_nothing_published_is_an_error(self):
        now = datetime(2026, 9, 27, 10, 0, tzinfo=config.TZ)
        days = ('2026-09-24', '2026-09-25', '2026-09-26', '2026-09-27')
        f = FakeFetcher({wrd.report_url(datetime.fromisoformat(k).date()): b'' for k in days})
        with tempfile.TemporaryDirectory() as d, mock.patch('opencity.config.now', return_value=now):
            conn = db.connect(Path(d) / 't.db')
            try:
                logging.disable(logging.CRITICAL)
                out = runner.refresh(conn, [Adapter(wrd.SOURCE, wrd)], data_dir=Path(d), fetcher=f)
                self.assertTrue(out['wrd_reservoirs'].startswith('error'), out)
                self.assertIn('no WRD report obtained', out['wrd_reservoirs'])
            finally:
                logging.disable(logging.NOTSET)
                conn.close()

    def test_today_only_asked_for_after_10(self):
        class Ctx:
            log = logging.getLogger('test')

            def __init__(self, now):
                self.now, self.asked = now, []

            def seen(self, method, url):
                return False

            def get(self, url, **kw):
                self.asked.append(kw['meta']['date'])
                return Raw(url=url, body=b'%PDF', content_type='', fetch_id=0, sha256='', changed=True,
                           retrieved_at='', meta=kw['meta'])
        early, late = Ctx(datetime(2026, 9, 27, 8, 0, tzinfo=config.TZ)), Ctx(datetime(2026, 9, 27, 10, 0, tzinfo=config.TZ))
        list(wrd.fetch(early))
        list(wrd.fetch(late))
        self.assertEqual(early.asked, ['2026-09-23', '2026-09-24', '2026-09-25', '2026-09-26'])
        self.assertEqual(late.asked, ['2026-09-24', '2026-09-25', '2026-09-26', '2026-09-27'])

    def test_report_url(self):
        self.assertEqual(wrd.report_url(datetime(2026, 9, 27).date()),
                         'https://wrd-dam.gujarat.gov.in/downloads/home_pdf.php?dt=MjAyNi0wOS0yNw==')


if __name__ == '__main__':
    unittest.main()
