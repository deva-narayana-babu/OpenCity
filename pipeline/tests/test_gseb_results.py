"""GSEB result booklets, March 2026 main exams.

SSC and HSC science: the frozen booklets in reference/education/. HSC general: tests/fixtures/gseb_results/
genbooklet-2026-pages-22-28-29.pdf, pages 22 (centre-wise, Surat centres 1801-1827), 28 (district E.Q.C.) and 29
(district grade-wise) of https://gsebweb2026.s3.ap-south-1.amazonaws.com/pdf/genbooklet.pdf (30 pages, sha256
b6bb5668...cc21f, downloaded 2026-10-05), cut with Ghostscript (-sPageList=22,28,29); pdftotext output of those
pages is identical to the full booklet's.
"""
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from tests import FIXTURES, REFERENCE, raw_from_file
from opencity import db, runner
from opencity.fetcher import Response
from opencity.model import FetchError, ValidationError
from opencity.registry import discover
from opencity.sources import gseb_results as m

SSC = REFERENCE / 'education/gujarat-gseb-ssc-result-booklet-2026.pdf'
SCI = REFERENCE / 'education/gujarat-gseb-hsc-science-result-booklet-2026.pdf'
GEN = FIXTURES / 'gseb_results/genbooklet-2026-pages-22-28-29.pdf'
Y26, Y25, Y24 = '2026-01-01', '2025-01-01', '2024-01-01'


def _parse(path, exam=None, year=None, url='file://fixture'):
    meta = {k: v for k, v in (('exam', exam), ('year', year)) if v is not None}
    raw = raw_from_file(path, url=url, meta=meta, retrieved_at='2026-10-05T00:00:00+05:30')
    res = m.parse(raw)
    m.validate(res, raw)
    by = {(o.metric_id[5:], o.geo_code, o.period_start, o.dims.get('grade')): o for o in res.observations}
    return res, by


class TestSsc2026(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.res, cls.by = _parse(SSC, 'ssc', 2026)

    def v(self, metric, geo='surat', start=Y26, grade=None):
        return self.by[(metric, geo, start, grade)].value

    def test_counts(self):
        obs = self.res.observations
        self.assertEqual(len(obs), 256)       # district 4 + 10 grades + 2 earlier pass %; 48 centres x (4 + 2025 %)
        self.assertEqual(sum(o.geo_level == 'exam_centre' for o in obs), 240)
        self.assertEqual({o.dims['exam'] for o in obs}, {'ssc'})
        self.assertEqual(len(self.res.geos), 49)

    def test_district_row(self):
        # p.11: SURAT 82306 81652 6475 13534 14588 14790 13207 7147 513 0 6314 5084 70254 86.04%
        self.assertEqual([self.v(x) for x in ('registered', 'appeared', 'passed', 'pass_pct')],
                         [82306, 81652, 70254, 86.04])
        self.assertEqual([self.v('candidates_by_grade', grade=g) for g in ('A1', 'C2', 'E1*', 'E1', 'E2')],
                         [6475, 7147, 0, 6314, 5084])
        o = self.by[('pass_pct', 'surat', Y26, None)]
        self.assertEqual((o.geo_level, o.period_end), ('surat_district', '2026-12-31'))
        # p.12: 30. 68 SURAT 86.04% 86.20% 86.75%
        self.assertEqual((self.v('pass_pct', start=Y25), self.v('pass_pct', start=Y24)), (86.20, 86.75))

    def test_centres(self):
        # p.34: 6810 6810 SURAT RANDER 2747 2730 2408 88.21% 86.91% 1.30%
        g = 'gseb-ssc-6810'
        self.assertEqual([self.v(x, g) for x in ('registered', 'appeared', 'passed', 'pass_pct')], [2747, 2730, 2408, 88.21])
        self.assertEqual(self.v('pass_pct', g, Y25), 86.91)
        # 6838 DINDOLI 6451 6408 5541 86.47%
        self.assertEqual(self.v('passed', 'gseb-ssc-6838'), 5541)
        # 6850 WANKANER(^^): new centre, 2025 shown as "–"
        o = self.by[('pass_pct', 'gseb-ssc-6850', Y25, None)]
        self.assertEqual((o.value, o.status), (None, 'not_reported'))
        geos = {x.geo_code: x for x in self.res.geos}
        self.assertEqual(geos['gseb-ssc-6850'].name, 'WANKANER (GSEB SSC centre 6850)')
        self.assertEqual((geos['gseb-ssc-6810'].geo_level, geos['gseb-ssc-6810'].parent_level,
                          geos['gseb-ssc-6810'].parent_code), ('exam_centre', 'surat_district', 'surat'))
        # no Tapi (79xx) or other districts' centres
        self.assertTrue(all(c.startswith('gseb-ssc-68') for c in geos if c != 'surat'))


class TestHscScience2026(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.res, cls.by = _parse(SCI, 'hsc_science', 2026)

    def v(self, metric, geo='surat', grade=None):
        return self.by[(metric, geo, Y26, grade)].value

    def test_values(self):
        self.assertEqual(len(self.res.observations), 60)        # 4 + 8 grades + 12 centres x 4
        # p.18: 18-SURAT 15817 15798 459 2460 3061 2834 2714 1894 362 2 2031 87.26 ; p.17: 18 SURAT 13,786
        self.assertEqual([self.v(x) for x in ('registered', 'appeared', 'passed', 'pass_pct')],
                         [15817, 15798, 13786, 87.26])
        self.assertEqual((self.v('candidates_by_grade', grade='A1'), self.v('candidates_by_grade', grade='E1')), (459, 2))
        # p.15: 1806 RANDER (SURAT) 1685 1683 1521 164 90.37
        self.assertEqual([self.v(x, 'gseb-hsc-1806') for x in ('registered', 'appeared', 'passed', 'pass_pct')],
                         [1685, 1683, 1521, 90.37])
        self.assertEqual(self.v('pass_pct', 'gseb-hsc-1808'), 75.57)        # UDHANA (SURAT)
        self.assertNotIn(('pass_pct', 'gseb-hsc-2801', Y26, None), self.by)  # VYARA is in Tapi district


class TestHscGeneral2026(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.res, cls.by = _parse(GEN, 'hsc_general', 2026)

    def v(self, metric, geo='surat', grade=None):
        return self.by[(metric, geo, Y26, grade)].value

    def test_values(self):
        self.assertEqual(len(self.res.observations), 112)       # 4 + 8 grades + 25 centres x 4
        # p.29: 18-SURAT 47235 47091 2083 6910 8219 9181 9430 6872 1289 25 3226 93.46 ; p.28: 18 SURAT 44,009
        self.assertEqual([self.v(x) for x in ('registered', 'appeared', 'passed', 'pass_pct')],
                         [47235, 47091, 44009, 93.46])
        self.assertEqual(self.v('candidates_by_grade', grade='D'), 1289)
        # p.22: 1816 NANPURA BLIND (SURAT) 15 15 15 0 100.00 ; 1806 SURAT - RANDER 4024 4022 3829 195 95.20
        self.assertEqual(self.v('pass_pct', 'gseb-hsc-1816'), 100.0)
        self.assertEqual([self.v(x, 'gseb-hsc-1806') for x in ('registered', 'appeared', 'passed', 'pass_pct')],
                         [4024, 4022, 3829, 95.20])


class TestDetectionAndGuards(unittest.TestCase):
    def test_exam_and_year_detected_without_meta(self):
        res, by = _parse(SCI)
        self.assertEqual(by[('passed', 'surat', Y26, None)].dims, {'exam': 'hsc_science'})
        res, by = _parse(GEN, url='https://gsebweb2026.s3.ap-south-1.amazonaws.com/pdf/genbooklet.pdf')
        self.assertEqual(by[('passed', 'surat', Y26, None)].value, 44009)

    def test_wrong_year_or_exam_rejected(self):
        with self.assertRaises(ValidationError):
            _parse(SSC, 'ssc', 2025)            # the history table says 2026 2025 2024
        with self.assertRaises(ValidationError):
            _parse(SCI, 'hsc_general', 2026)
        with self.assertRaises(ValidationError):
            m.parse(raw_from_file(REFERENCE / 'education/gujarat-gseb-ssc-supplementary-result-2026.pdf'))


class FakeCtx:
    def __init__(self, now, present):
        self.now, self.present, self.urls = now, present, []
        self.log = SimpleNamespace(info=lambda *a: None, error=lambda *a: None)

    def get(self, url, meta=None, skip_if_seen=False):
        self.urls.append(url)
        assert skip_if_seen
        if url not in self.present:
            raise FetchError(f'HTTP 404 for {url}', http_status=404)
        return SimpleNamespace(url=url, meta=meta)


class TestFetch(unittest.TestCase):
    def test_current_exam_year_and_404s_skipped(self):
        with mock.patch.dict(os.environ, {'GSEB_YEARS': ''}):
            ssc = 'https://gsebweb2026.s3.ap-south-1.amazonaws.com/pdf/sscbooklet.pdf'
            ctx = FakeCtx(datetime(2026, 10, 5), {ssc})
            got = list(m.fetch(ctx))                               # 404s for sci/gen: no exception
            self.assertEqual([r.url for r in got], [ssc])
            self.assertEqual(got[0].meta, {'exam': 'ssc', 'year': 2026})
            self.assertEqual(len(ctx.urls), 3)
            ctx = FakeCtx(datetime(2027, 4, 30), set())
            list(m.fetch(ctx))
            self.assertTrue(all('gsebweb2026' in u for u in ctx.urls))   # 2027 results not out before May
        self.assertEqual(m.interval_hours(datetime(2027, 5, 2)), 24)
        self.assertEqual(m.interval_hours(datetime(2027, 9, 2)), 24 * 7)


class FakeS3:
    def request(self, method, url, **kw):
        files = {'sscbooklet.pdf': SSC, 'scibooklet.pdf': SCI, 'genbooklet.pdf': GEN}
        name = url.rsplit('/', 1)[1]
        assert url.startswith('https://gsebweb2026.s3.ap-south-1.amazonaws.com/pdf/') and name in files, url
        return Response(200, files[name].read_bytes(), url, {'content-type': 'application/pdf'})


class TestThroughRunner(unittest.TestCase):
    def test_refresh_then_skip_if_seen(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {'GSEB_YEARS': '2026'}):
            conn = db.connect(Path(d) / 't.db')
            ad = discover()['gseb_results']
            out = runner.refresh(conn, [ad], data_dir=Path(d), fetcher=FakeS3())
            self.assertEqual(out['gseb_results'], 'ok: 3 document(s), 428 observation(s), 0 record(s)')
            # HSC science (12 centres) and general (25) share centre numbers: 27 HSC geos, 2 of them science-only
            # (1803 KAMREJ, 1828 KARCHELIYA)
            self.assertEqual(conn.execute("SELECT count(*) FROM geo WHERE geo_level='exam_centre'").fetchone()[0], 48 + 27)
            out = runner.refresh(conn, [ad], data_dir=Path(d), fetcher=FakeS3())
            self.assertEqual(out['gseb_results'], 'ok: 0 document(s), 0 observation(s), 0 record(s)')
            conn.close()


if __name__ == '__main__':
    unittest.main()
