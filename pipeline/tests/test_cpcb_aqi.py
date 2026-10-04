import dataclasses
import json
import logging
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from tests import REFERENCE, raw_from_file
from opencity import config, db, runner
from opencity.model import Raw, ValidationError
from opencity.parse import pdf_text
from opencity.registry import Adapter
from opencity.sources import cpcb_aqi as cpcb

DIR = REFERENCE / 'health-environment'
BULLETINS = {day: DIR / f'india-cpcb-aqi-bulletin-{day}.pdf' for day in ('2026-09-24', '2026-09-25', '2026-09-26')}
FEED = DIR / 'india-cpcb-caaqms-station-feed-2026-09-27.json'
FETCHED = '2026-09-27T13:01:00+05:30'


def _bulletin(day, **kw):
    return raw_from_file(BULLETINS[day], meta={'date': day}, retrieved_at=kw.get('retrieved_at', FETCHED))


def _index(res):
    return {(o.metric_id, o.geo_code, o.dims.get('pollutant')): o for o in res.observations}


class TestCpcbBulletin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.res = {day: cpcb.parse(_bulletin(day)) for day in BULLETINS}
        cls.by = {day: _index(r) for day, r in cls.res.items()}
        cls.text = pdf_text(BULLETINS['2026-09-24'].read_bytes())

    def test_surat_rows(self):
        # "223  Surat  Satisfactory  84  PM10, PM2.5  2/2"   (Sep 24, 2026 @ 4 PM)
        by = self.by['2026-09-24']
        o = by[('cpcb.city_aqi', 'smc', None)]
        self.assertEqual((o.geo_level, o.period_start, o.period_end, o.value), ('smc_city', '2026-09-24', '2026-09-24', 84))
        self.assertEqual(o.publisher_as_of, '2026-09-24T16:00')
        self.assertEqual(by[('cpcb.city_aqi_category', 'smc', None)].value_text, 'Satisfactory')
        self.assertEqual(by[('cpcb.city_prominent_pollutants', 'smc', None)].value_text, 'PM10, PM2.5')
        self.assertEqual(by[('cpcb.city_stations_participated', 'smc', None)].value, 2)
        self.assertEqual(by[('cpcb.city_stations_total', 'smc', None)].value, 2)
        # "222  Surat  Satisfactory  77  PM10  2/2" and "221  Surat  Satisfactory  61  PM10, CO  2/2"
        self.assertEqual(self.by['2026-09-25'][('cpcb.city_aqi', 'smc', None)].value, 77)
        self.assertEqual(self.by['2026-09-25'][('cpcb.city_prominent_pollutants', 'smc', None)].value_text, 'PM10')
        self.assertEqual(self.by['2026-09-26'][('cpcb.city_aqi', 'smc', None)].value, 61)
        self.assertEqual(self.by['2026-09-26'][('cpcb.city_prominent_pollutants', 'smc', None)].value_text, 'PM10, CO')
        for day, res in self.res.items():
            self.assertEqual(len(res.observations), 5, day)
            cpcb.validate(res, _bulletin(day))
            cpcb.validate(res, None)

    def test_whole_table_is_read(self):
        cut = self.text.index('Cities absent')
        rows = cpcb._city_rows(self.text[:cut])
        self.assertEqual(len(rows), 245)                 # S.No 1..245
        # wrapped row: "Aurangabad" / "18 ... 84 ... 3/3" / "(Maharashtra)"
        self.assertEqual(rows['Aurangabad (Maharashtra)'], ('Satisfactory', '84', 'PM2.5, PM10', '3', '3'))
        # last row of a page, printed right before the next page's title
        self.assertEqual(rows['Badlapur'], ('Good', '46', 'CO', '1', '1'))
        self.assertEqual(rows['Ahmedabad'], ('Moderate', '115', 'PM10, PM2.5', '7', '9'))
        absent = cpcb._absent_cities(self.text)
        self.assertEqual(len(absent), 77)
        self.assertIn('Ankleshwar', absent)
        self.assertNotIn('Surat', absent)

    def test_surat_absent_is_not_reported(self):
        lines = [ln for ln in self.text.split('\n') if ' Surat ' not in ln]
        text = '\n'.join(lines).replace('77)\nVirudhunagar', '77)\nVirudhunagar, 78) Surat')
        res = cpcb.bulletin_result(text)
        self.assertEqual(len(res.observations), 1)
        o = res.observations[0]
        self.assertEqual((o.metric_id, o.status, o.value), ('cpcb.city_aqi', 'not_reported', None))
        self.assertIn('insufficient data', o.value_text)
        cpcb.validate(res, None)
        with self.assertRaisesRegex(ValidationError, 'neither in the bulletin table'):
            cpcb.bulletin_result('\n'.join(lines))

    def test_validation_rejects(self):
        res = self.res['2026-09-24']
        with self.assertRaisesRegex(ValidationError, 'asked for'):
            cpcb.validate(res, dataclasses.replace(_bulletin('2026-09-24'), meta={'date': '2026-09-23'}))
        with self.assertRaisesRegex(ValidationError, 'after the fetch time'):
            cpcb.validate(res, _bulletin('2026-09-24', retrieved_at='2026-09-23T20:00:00+05:30'))
        bad = dataclasses.replace(res, observations=[dataclasses.replace(o, value=120) if o.metric_id == 'cpcb.city_aqi'
                                                     else o for o in res.observations])
        with self.assertRaisesRegex(ValidationError, 'Satisfactory'):
            cpcb.validate(bad, None)
        with self.assertRaisesRegex(ValidationError, 'neither a bulletin PDF'):
            cpcb.parse(dataclasses.replace(_bulletin('2026-09-24'), body=b'<html>404</html>'))


class TestCpcbFeed(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = raw_from_file(FEED, retrieved_at='2026-09-27T13:01:00+05:30')
        cls.res = cpcb.parse(cls.raw)
        cls.by = _index(cls.res)

    def test_surat_stations(self):
        self.assertEqual(len(self.res.observations), 18)     # 2 stations x (AQI, prominent, 7 pollutants)
        cpcb.validate(self.res, self.raw)
        # Science Center, Surat - SMC (site_5664): AQI 53, predominant CO; CO avg 53, NH3 and OZONE "NA"
        o = self.by[('cpcb.station_aqi', 'site_5664', None)]
        self.assertEqual((o.geo_level, o.period_start, o.period_end, o.value), ('aq_station', '2026-09-27T12:00',
                                                                                 '2026-09-27T12:00', 53))
        self.assertEqual(self.by[('cpcb.station_prominent_pollutant', 'site_5664', None)].value_text, 'CO')
        self.assertEqual(self.by[('cpcb.station_subindex_avg', 'site_5664', 'CO')].value, 53)
        self.assertEqual(self.by[('cpcb.station_subindex_avg', 'site_5664', 'PM2.5')].value, 18)
        for p in ('NH3', 'OZONE'):
            o = self.by[('cpcb.station_subindex_avg', 'site_5664', p)]
            self.assertEqual((o.status, o.value), ('not_reported', None))
        # Katargam, Surat - Nexteng Enviro (site_6066): AQI 60 from PM10 avg 60, OZONE 14
        self.assertEqual(self.by[('cpcb.station_aqi', 'site_6066', None)].value, 60)
        self.assertEqual(self.by[('cpcb.station_subindex_avg', 'site_6066', 'PM10')].value, 60)
        self.assertEqual(self.by[('cpcb.station_subindex_avg', 'site_6066', 'OZONE')].value, 14)

    def test_station_geos(self):
        geos = {g.geo_code: g for g in self.res.geos if g.geo_level == 'aq_station'}
        self.assertEqual(set(geos), {'site_5664', 'site_6066'})
        self.assertEqual(geos['site_5664'].name, 'Science Center, Surat - SMC')
        self.assertEqual((geos['site_6066'].parent_level, geos['site_6066'].parent_code), ('surat_district', 'surat'))
        self.assertIn('21.217779', geos['site_6066'].note)

    def test_validation_rejects(self):
        bad = dataclasses.replace(self.res, observations=[
            dataclasses.replace(o, value=90) if (o.metric_id, o.geo_code) == ('cpcb.station_aqi', 'site_6066')
            else o for o in self.res.observations])
        with self.assertRaisesRegex(ValidationError, 'highest pollutant sub-index'):
            cpcb.validate(bad, None)
        with self.assertRaisesRegex(ValidationError, 'after the fetch time'):
            cpcb.validate(self.res, dataclasses.replace(self.raw, retrieved_at='2026-09-26T23:00:00+05:30'))
        with self.assertRaisesRegex(ValidationError, 'stations in the feed'):
            cpcb.parse(dataclasses.replace(self.raw, body=json.dumps({'countryId': 'India', 'country': []}).encode()))

    def test_runner_accepts_both_documents(self):
        with tempfile.TemporaryDirectory() as d:
            conn = db.connect(Path(d) / 't.db')
            try:
                ad = Adapter(cpcb.SOURCE, cpcb)
                db.register_source(conn, ad.source)
                for raw, n in ((_bulletin('2026-09-24'), 5), (self.raw, 18)):
                    fid = db.insert_fetch(conn, source_id=ad.id, url='u', request_key='k')
                    raw = dataclasses.replace(raw, fetch_id=fid)
                    res = cpcb.parse(raw)
                    runner.validate(ad, res, raw, conn)
                    self.assertEqual(db.apply_result(conn, ad.source, fid, res, ad.parser)[0], n)
            finally:
                conn.close()


class FakeCtx:
    def __init__(self, now):
        self.now = now
        self.calls = []
        self.log = logging.getLogger('test')

    def get(self, url, **kw):
        self.calls.append((url, kw.get('skip_if_seen', False)))
        return Raw(url=url, body=b'x', content_type='', fetch_id=0, sha256='', changed=True,
                   retrieved_at='', meta=kw.get('meta') or {})


class TestCpcbFetch(unittest.TestCase):
    def test_bulletin_dates(self):
        ctx = FakeCtx(datetime(2026, 9, 27, 10, 0, tzinfo=config.TZ))     # before 17:00: today's is not out
        list(cpcb.fetch(ctx))
        self.assertEqual(ctx.calls, [
            ('https://cpcb.gov.in/upload/Downloads/AQI_Bulletin_20260924.pdf', True),
            ('https://cpcb.gov.in/upload/Downloads/AQI_Bulletin_20260925.pdf', True),
            ('https://cpcb.gov.in/upload/Downloads/AQI_Bulletin_20260926.pdf', True),
            (cpcb.FEED, False)])
        ctx = FakeCtx(datetime(2026, 9, 27, 18, 0, tzinfo=config.TZ))
        list(cpcb.fetch(ctx))
        self.assertEqual(ctx.calls[-2][0], 'https://cpcb.gov.in/upload/Downloads/AQI_Bulletin_20260927.pdf')


if __name__ == '__main__':
    unittest.main()
