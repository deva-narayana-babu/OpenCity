import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from tests import REFERENCE, raw_from_file
from opencity import db, runner
from opencity.fetcher import Response
from opencity.model import Raw, ValidationError
from opencity.registry import discover
from opencity.sources import udise_surat as m

FY24 = REFERENCE / 'education/india-udise-district-profile-surat-2024-25.json'
FY25 = REFERENCE / 'education/india-udise-district-profile-surat-2025-26.json'
# what the API answered for yearId 13 on 2026-10-05 (no data yet)
EMPTY = (b'{"status":true,"data":[],"errorDetails":"","metaData":{"apiCode":"6055","apiVersion":"1.1",'
         b'"requestTimestamp":"05-10-2026 00:38:23.438","responseTimestamp":"05-10-2026 00:38:23.439",'
         b'"transactionId":"","pageNo":0,"totalPages":1,"recordsPerPage":0,"totalRecords":0}}')


def _raw(body: bytes, meta=None) -> Raw:
    return Raw(url=m.URL, body=body, content_type='application/json', fetch_id=0, sha256='', changed=True,
               retrieved_at='2026-10-05T00:00:00+05:30', meta=dict(meta or {}))


def _parse(path, year_id):
    raw = raw_from_file(path, url=m.URL, meta={'year_id': year_id}, retrieved_at='2026-10-05T00:00:00+05:30')
    res = m.parse(raw)
    m.validate(res, raw)
    return res, {(o.metric_id, tuple(sorted(o.dims.items()))): o for o in res.observations}


def v(by, metric, **dims):
    return by[('udise.' + metric, tuple(sorted(dims.items())))]


class TestUdise2024_25(unittest.TestCase):
    """reference/education/india-udise-district-profile-surat-2024-25.json (yearId 11)."""

    @classmethod
    def setUpClass(cls):
        cls.res, cls.by = _parse(FY24, 11)

    def test_counts_geo_period(self):
        self.assertEqual(len(self.res.observations), 96)
        self.assertEqual(sum(o.status == 'not_reported' for o in self.res.observations), 5)
        self.assertEqual({(o.geo_level, o.geo_code) for o in self.res.observations}, {('surat_district', 'surat')})
        self.assertEqual({(o.period_start, o.period_end) for o in self.res.observations},
                         {('2024-04-01', '2025-03-31')})

    def test_values_read_off_the_response(self):
        self.assertEqual(v(self.by, 'schools').value, 3294)                 # totSch
        self.assertEqual(v(self.by, 'enrolment').value, 1286170)            # tenrF2Sec
        self.assertEqual(v(self.by, 'teachers').value, 38812)               # ttch
        self.assertEqual(v(self.by, 'schools.by_management', management='state_govt').value, 1349)   # tschStatGovt
        self.assertEqual(v(self.by, 'schools.by_category', category='upper_primary_1_8').value, 1563)  # tsch1to8
        self.assertEqual(v(self.by, 'enrolment.by_stage', stage='preparatory').value, 338214)        # tenrP
        self.assertEqual(v(self.by, 'enrolment.by_social_group', group='st').value, 146275)         # tenrF2SecSt
        self.assertEqual(v(self.by, 'enrolment.cwsn').value, 3718)                                  # tenrFSecCwsn
        self.assertEqual(v(self.by, 'teachers.by_management', management='private_unaided').value, 26798)
        self.assertEqual(v(self.by, 'ptr', stage='foundational').value, 14)                         # foundation
        self.assertEqual(v(self.by, 'ptr', stage='secondary').value, 31)
        self.assertEqual(v(self.by, 'transition_rate_pct', transition='middle_to_secondary').value, 88.5)  # tst
        self.assertEqual(v(self.by, 'dropout_rate_pct', stage='secondary').value, 10.0)            # dst
        self.assertEqual(v(self.by, 'schools_with_facility_pct', facility='girls_toilet', condition='available').value,
                         99.62)                                                                     # toiletGPer
        self.assertEqual(v(self.by, 'schools_with_facility_pct', facility='smart_classroom',
                           condition='functional').value, 68.7)                                     # smartPerFun
        self.assertEqual(v(self.by, 'pgi_d.score').value, 325.58)
        g = v(self.by, 'pgi_d.grade')
        self.assertEqual((g.value, g.value_text, g.status), (None, 'PRACHESTA-1', 'reported'))

    def test_nulls_are_not_reported(self):
        for o in (v(self.by, 'ger_pct', stage='foundational'),                      # fger: null
                  v(self.by, 'enrolment.by_management', management='other')):        # tenrF2SecOth: null
            self.assertEqual((o.value, o.status), (None, 'not_reported'))

    def test_every_labelled_field_and_nothing_else(self):
        # every mapped field is present in this response; tenrPPri / tschPpri (unlabelled) are not stored
        self.assertEqual(len(self.res.observations), len(m.FIELDS) + len(m.FACILITIES) + 1)   # + PGI-D grade
        mapped = {f for f, *_ in m.FIELDS} | {f for f, *_ in m.FACILITIES} | {'overallGrade'}
        returned = set(json.loads(FY24.read_bytes())['data'][0])
        self.assertEqual(returned - mapped, {'yearId', 'regionName', 'regionType', 'regionCode', 'tenrPPri', 'tschPpri'})


class TestUdise2025_26(unittest.TestCase):
    """reference/education/india-udise-district-profile-surat-2025-26.json (yearId 12)."""

    @classmethod
    def setUpClass(cls):
        cls.res, cls.by = _parse(FY25, 12)

    def test_values(self):
        self.assertEqual({o.period_start for o in self.res.observations}, {'2025-04-01'})
        self.assertEqual(v(self.by, 'schools').value, 3325)
        self.assertEqual(v(self.by, 'enrolment').value, 1306119)
        self.assertEqual(v(self.by, 'enrolment.by_stage', stage='foundational').value, 348647)
        self.assertEqual(v(self.by, 'teachers').value, 40103)
        self.assertEqual(v(self.by, 'schools_with_facility_pct', facility='internet', condition='available').value,
                         99.31)
        # dpt is published as 0.0: a reported zero, not a blank
        o = v(self.by, 'dropout_rate_pct', stage='preparatory')
        self.assertEqual((o.value, o.status), (0.0, 'reported'))
        # 328.84 matches "Surat 329" in the PGI-D 2025-26 report (reference/education/india-moe-pgi-d-report-2025-26.pdf)
        self.assertEqual(v(self.by, 'pgi_d.score').value, 328.84)


class TestEdgeCases(unittest.TestCase):
    def test_empty_year_gives_no_observations(self):
        raw = _raw(EMPTY, {'year_id': 13})
        res = m.parse(raw)
        m.validate(res, raw)
        self.assertEqual(res.observations, [])

    def test_wrong_region_or_year_rejected(self):
        doc = json.loads(FY24.read_bytes())
        doc['data'][0]['regionCode'] = '2401'
        with self.assertRaises(ValidationError):
            m.parse(_raw(json.dumps(doc).encode()))
        with self.assertRaises(ValidationError):
            m.parse(_raw(FY24.read_bytes(), {'year_id': 12}))
        with self.assertRaises(ValidationError):
            m.parse(_raw(b'{"status":false,"data":[],"errorDetails":"bad request"}'))

    def test_inconsistent_breakdown_rejected(self):
        doc = json.loads(FY24.read_bytes())
        doc['data'][0]['tenrS'] += 1000          # stages no longer add up to the total
        raw = _raw(json.dumps(doc).encode())
        with self.assertRaises(ValidationError):
            m.validate(m.parse(raw), raw)

    def test_normalize_blanks_timestamps(self):
        other = EMPTY.replace(b'00:38:23.438', b'11:11:11.111').replace(b'00:38:23.439', b'11:11:11.112')
        self.assertNotEqual(EMPTY, other)
        self.assertEqual(m.normalize(EMPTY), m.normalize(other))

    def test_year_ids(self):
        self.assertEqual(m.year_ids(datetime(2026, 10, 5)), [11, 12, 13])
        self.assertEqual(m.year_ids(datetime(2027, 3, 31)), [11, 12, 13])
        self.assertEqual(m.year_ids(datetime(2030, 4, 1)), [14, 15, 16, 17])


class FakeUdise:
    """Answers the edu-highlights POST from the frozen responses; any other year has no data."""

    def __init__(self):
        self.bodies = []

    def request(self, method, url, json=None, **kw):
        assert (method, url) == ('POST', m.URL), (method, url)
        self.bodies.append(json)
        body = {11: FY24.read_bytes(), 12: FY25.read_bytes()}.get(json['yearId'], EMPTY)
        return Response(200, body, url, {'content-type': 'application/json'})


class TestThroughRunner(unittest.TestCase):
    def test_refresh_into_scratch_db(self):
        with tempfile.TemporaryDirectory() as d:
            conn = db.connect(Path(d) / 't.db')
            f = FakeUdise()
            out = runner.refresh(conn, [discover()['udise_surat']], data_dir=Path(d), fetcher=f)
            self.assertTrue(out['udise_surat'].startswith('ok'), out)
            self.assertIn({'yearId': 11, 'regionCode': '2422', 'regionType': 12, 'valueType': 1}, f.bodies)
            n = conn.execute("SELECT count(*) FROM observation WHERE source_id='udise_surat'").fetchone()[0]
            self.assertEqual(n, 192)
            self.assertEqual(conn.execute("SELECT count(*) FROM observation WHERE geo_level != 'surat_district'"
                                          ).fetchone()[0], 0)
            conn.close()


if __name__ == '__main__':
    unittest.main()
