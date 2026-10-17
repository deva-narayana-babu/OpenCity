"""Tests for the smc_rti adapter (SMC RTI annual returns, Patrak-7 and Patrak-8 quarterly returns).

Frozen documents used (all offline):
  reference/rti/smc-rti-annual-returns-index-2026-09-27.html   index page, 20 yearly links
  reference/rti/smc-rti-annual-return-2023-24.pdf / -2024-25 / -2025-26   Chrome printouts of the web form
  reference/rti/smc-rti-patrak-7-q4-2025-26.pdf                 Patrak-7, Q4 FY2025-26
  tests/fixtures/smc_rti/ (byte-exact copies of the live files fetched 2026-10-05):
    patrak-8-q4-2025-26.pdf    .../Content/Documents/rtiact/other/patrak-8.pdf
                               sha256 223c701f4e3552d896be7b11ef46142fb8c902a28f4cfdfd4d5dda299e9cb172
    annual-return-2005-07.pdf  .../Content/Documents/rtiact/Annual-Return/2005-2007.pdf (Word re-typing layout)
                               sha256 6f5fcc589cf855db5ad3a93d7c8b70d566b6ba08009ec34cdca34fb9af4aa3e2
    annual-return-2019-20.pdf  .../Content/Documents/rtiact/Annual-Return/2019-2020.pdf (Foxit printout layout)
                               sha256 153bc6b03d32bce7a1fdae0a713bfb6afbe6f48a860e0dc987f32ce50c4af0ff
Every exact value asserted below was read off the document with `pdftotext -layout`.
"""
import copy
import tempfile
import unittest
from pathlib import Path

from tests import FIXTURES, REFERENCE, raw_from_file
from opencity import db, runner
from opencity.model import Raw, ValidationError
from opencity.registry import Adapter
from opencity.sources import smc_rti

RTI = REFERENCE / 'rti'
FIX = FIXTURES / 'smc_rti'
FETCHED = '2026-10-05T00:38:00+05:30'


def _parse(path, meta=None):
    raw = raw_from_file(path, meta=meta, retrieved_at=FETCHED)
    res = smc_rti.parse(raw)
    return res, raw


def _by(res):
    """(metric, period_start, period_end, section, applicants) -> Obs"""
    return {(o.metric_id, o.period_start, o.period_end, o.dims.get('section'), o.dims.get('applicants')): o
            for o in res.observations}


def _blank_pdf() -> bytes:
    """A valid one-page PDF with no text layer, standing in for SMC's image-only scanned returns."""
    objs = [b'<< /Type /Catalog /Pages 2 0 R >>', b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
            b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] >>']
    out, offs = b'%PDF-1.4\n', []
    for i, o in enumerate(objs, 1):
        offs.append(len(out))
        out += f'{i} 0 obj\n'.encode() + o + b'\nendobj\n'
    xref = len(out)
    out += f'xref\n0 {len(objs) + 1}\n0000000000 65535 f \n'.encode()
    out += b''.join(f'{o:010d} 00000 n \n'.encode() for o in offs)
    out += f'trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode()
    return out


class RunnerChecks:
    """Mixin: run the framework's own checks (declared metrics, statuses, geos, duplicate keys) + validate()."""

    def assertPassesRunner(self, res, raw):
        with tempfile.TemporaryDirectory() as d:
            conn = db.connect(Path(d) / 't.db')
            try:
                runner.validate(Adapter(smc_rti.SOURCE, smc_rti), res, raw, conn)
            finally:
                conn.close()


class TestIndex(unittest.TestCase, RunnerChecks):
    @classmethod
    def setUpClass(cls):
        cls.res, cls.raw = _parse(RTI / 'smc-rti-annual-returns-index-2026-09-27.html')
        cls.recs = {r.record_key: r.attrs for r in cls.res.records}

    def test_records(self):
        self.assertEqual(len(self.res.observations), 0)
        self.assertEqual(len(self.recs), 20)
        self.assertEqual(self.res.complete_record_types, ('rti_annual_return',))
        self.assertEqual(min(self.recs), '2005-2007')
        self.assertEqual(max(self.recs), '2025-2026')
        r = self.recs['2025-2026']
        self.assertEqual(r['url'], 'https://www.suratmunicipal.gov.in/Content/Documents/rtiact/Annual-Return/2025-2026.pdf')
        self.assertEqual(r['title'], 'Gujarat State RTI Annual Return - Year 2025 to 2026')
        self.assertEqual((r['period_start'], r['period_end']), ('2025-04-01', '2026-03-31'))
        self.assertEqual(self.recs['2005-2007']['period_start'], '2005-04-01')
        self.assertEqual(self.recs['2005-2007']['period_end'], '2007-03-31')

    def test_scans_flagged(self):
        scanned = sorted(k for k, a in self.recs.items() if a['image_only_scan'])
        self.assertEqual(scanned, sorted(smc_rti.SCANNED_RETURNS))
        self.assertEqual(len(scanned), 5)

    def test_validates(self):
        self.assertPassesRunner(self.res, self.raw)


class TestAnnualReturns(unittest.TestCase, RunnerChecks):
    @classmethod
    def setUpClass(cls):
        cls.docs = {
            '2023': _parse(RTI / 'smc-rti-annual-return-2023-24.pdf'),
            '2024': _parse(RTI / 'smc-rti-annual-return-2024-25.pdf'),
            '2025': _parse(RTI / 'smc-rti-annual-return-2025-26.pdf'),
            '2005': _parse(FIX / 'annual-return-2005-07.pdf'),
            '2019': _parse(FIX / 'annual-return-2019-20.pdf'),
        }

    def _v(self, year, metric, section=None):
        res = self.docs[year][0]
        (o,) = [o for o in res.observations if o.metric_id == f'rti.annual.{metric}' and o.dims.get('section') == section]
        return o.value

    def test_counts_and_validation(self):
        for y, (res, raw) in self.docs.items():
            with self.subTest(year=y):
                # 9 request/appeal fields + disciplinary + 3 officer counts + 14 sections + 5 charges
                self.assertEqual(len(res.observations), 32)
                self.assertTrue(all(o.status == 'reported' for o in res.observations))
                self.assertTrue(all((o.geo_level, o.geo_code) == ('smc_city', 'smc') for o in res.observations))
                self.assertPassesRunner(res, raw)

    def test_2025_26_values(self):
        # Requests: 5875 | 8653 | 2926 | 25 | 7633; First Appeals: 831 | 737 | - | 88 | 721
        exp = {'requests_opening_balance': 5875, 'requests_received': 8653, 'requests_transferred': 2926,
               'requests_rejected': 25, 'requests_accepted': 7633, 'first_appeals_opening_balance': 831,
               'first_appeals_received': 737, 'first_appeals_rejected': 88, 'first_appeals_accepted': 721,
               'disciplinary_actions': 0, 'apios_designated': 0, 'pios_designated': 353, 'aas_designated': 74,
               'registration_fees_rs': 94440, 'additional_fees_rs': 168031, 'penalties_levied_rs': 0,
               'penalties_collected_rs': 0, 'penalties_total_rs': 0}
        for m, v in exp.items():
            self.assertEqual(self._v('2025', m), v, m)
        self.assertEqual(self._v('2025', 'rejections_by_section', '8(1)(h)'), 1)
        self.assertEqual(self._v('2025', 'rejections_by_section', '8(1)(j)'), 14)
        self.assertEqual(self._v('2025', 'rejections_by_section', '11'), 13)
        o = self.docs['2025'][0].observations[0]
        self.assertEqual((o.period_start, o.period_end, o.publisher_as_of), ('2025-04-01', '2026-03-31', '2026-05-20'))

    def test_2023_24_and_2024_25_values(self):
        self.assertEqual(self._v('2023', 'requests_opening_balance'), 18364)
        self.assertEqual(self._v('2023', 'requests_received'), 18071)
        self.assertEqual(self._v('2023', 'requests_transferred'), 6032)
        self.assertEqual(self._v('2023', 'first_appeals_received'), 2214)
        self.assertEqual(self._v('2023', 'pios_designated'), 341)
        self.assertEqual(self._v('2023', 'rejections_by_section', '8(1)(j)'), 61)
        self.assertEqual(self._v('2023', 'rejections_by_section', '24'), 1)
        self.assertEqual(self._v('2023', 'rejections_by_section', 'other'), 13)
        self.assertEqual(self._v('2023', 'penalties_collected_rs'), 6000)
        self.assertEqual(self._v('2023', 'penalties_total_rs'), 6000)
        self.assertEqual(self._v('2024', 'requests_received'), 15213)
        self.assertEqual(self._v('2024', 'additional_fees_rs'), 377004)
        self.assertEqual(self._v('2024', 'rejections_by_section', '11'), 82)
        self.assertEqual(self._v('2024', 'rejections_by_section', '8(1)(b)'), 1)

    def test_2005_07_word_layout(self):
        # two-year return, values printed ABOVE the Levied/Collected/Total labels
        res = self.docs['2005'][0]
        self.assertEqual({(o.period_start, o.period_end) for o in res.observations}, {('2005-04-01', '2007-03-31')})
        exp = {'requests_opening_balance': 0, 'requests_received': 974, 'requests_transferred': 19,
               'requests_rejected': 8, 'requests_accepted': 775, 'first_appeals_opening_balance': 0,
               'first_appeals_received': 103, 'first_appeals_rejected': 10, 'first_appeals_accepted': 85,
               'apios_designated': 75, 'pios_designated': 18, 'aas_designated': 1,
               'registration_fees_rs': 17985, 'additional_fees_rs': 4725, 'penalties_levied_rs': 0}
        for m, v in exp.items():
            self.assertEqual(self._v('2005', m), v, m)
        self.assertEqual(self._v('2005', 'rejections_by_section', '8(1)(e)'), 5)
        self.assertEqual(self._v('2005', 'rejections_by_section', '8(1)(j)'), 3)
        self.assertEqual(res.observations[0].publisher_as_of, '2015-01-05')

    def test_2019_20_foxit_layout(self):
        exp = {'requests_opening_balance': 9617, 'requests_received': 23960, 'requests_transferred': 7731,
               'requests_rejected': 90, 'requests_accepted': 14575, 'first_appeals_opening_balance': 886,
               'first_appeals_received': 2496, 'first_appeals_rejected': 188, 'first_appeals_accepted': 2047,
               'pios_designated': 338, 'aas_designated': 72, 'registration_fees_rs': 198960,
               'additional_fees_rs': 263233, 'penalties_levied_rs': 0, 'penalties_collected_rs': 17500,
               'penalties_total_rs': 17500}
        for m, v in exp.items():
            self.assertEqual(self._v('2019', m), v, m)
        secs = {s: self._v('2019', 'rejections_by_section', s) for s in smc_rti.SECTIONS}
        self.assertEqual(secs, {'8(1)(a)': 0, '8(1)(b)': 0, '8(1)(c)': 0, '8(1)(d)': 0, '8(1)(e)': 0, '8(1)(f)': 0,
                                '8(1)(g)': 4, '8(1)(h)': 2, '8(1)(i)': 9, '8(1)(j)': 51, '9': 15, '11': 0, '24': 0,
                                'other': 9})

    def test_scanned_return_fails_loudly(self):
        raw = Raw(url='file://scan', body=_blank_pdf(), content_type='application/pdf', fetch_id=0, sha256='',
                  changed=True, retrieved_at=FETCHED, meta={'doc': 'annual_return'})
        with self.assertRaisesRegex(ValueError, 'no text layer'):
            smc_rti.parse(raw)

    def test_validate_rejects_half_empty_return(self):
        res, raw = copy.deepcopy(self.docs['2025'])
        for o in res.observations[:3]:
            o.value, o.status = None, 'not_reported'
        with self.assertRaisesRegex(ValidationError, 'layout not understood'):
            smc_rti.validate(res, raw)

    def test_validate_rejects_impossible_flow(self):
        res, raw = copy.deepcopy(self.docs['2025'])
        for o in res.observations:
            if o.metric_id == 'rti.annual.requests_accepted':
                o.value = 99999.0      # more decided than opening + received (5875 + 8653)
        with self.assertRaisesRegex(ValidationError, 'decided/transferred'):
            smc_rti.validate(res, raw)


class TestPatrak7(unittest.TestCase, RunnerChecks):
    Q = ('2026-01-01', '2026-03-31')

    @classmethod
    def setUpClass(cls):
        cls.res, cls.raw = _parse(RTI / 'smc-rti-patrak-7-q4-2025-26.pdf')
        cls.by = _by(cls.res)

    def v(self, metric, col='all', section=None, period=None):
        o = self.by[(f'rti.quarterly.{metric}', *(period or self.Q), section, col)]
        return o.value

    def test_counts_and_validation(self):
        # 31 data rows x 3 columns + the PIO count
        self.assertEqual(len(self.res.observations), 94)
        self.assertPassesRunner(self.res, self.raw)

    def test_flow_rows(self):
        self.assertEqual([self.v('requests_pending_start', c) for c in ('bpl', 'non_bpl', 'all')], [54, 3096, 3150])
        self.assertEqual(self.v('requests_received', 'non_bpl'), 1865)
        self.assertEqual(self.v('requests_received'), 1865)
        self.assertEqual(self.v('requests_total'), 5015)
        self.assertEqual(self.v('requests_transferred_wholly'), 596)
        self.assertEqual(self.v('requests_transferred_partly'), 14)
        self.assertEqual(self.v('requests_info_supplied'), 1214)
        self.assertEqual(self.v('requests_refused_fully'), 8)
        self.assertEqual(self.v('requests_refused_partly'), 0)
        self.assertEqual(self.v('requests_disposed'), 1818)
        self.assertEqual(self.v('requests_disposed_within_time'), 1106)
        self.assertEqual([self.v('requests_pending_end', c) for c in ('bpl', 'non_bpl', 'all')], [54, 3143, 3197])

    def test_blank_bpl_cells_are_not_reported(self):
        o = self.by[('rti.quarterly.requests_received', *self.Q, None, 'bpl')]
        self.assertIsNone(o.value)
        self.assertEqual(o.status, 'not_reported')
        # but a printed 0 is a 0
        self.assertEqual(self.v('refusals_total', 'bpl'), 0)
        self.assertEqual(self.by[('rti.quarterly.refusals_total', *self.Q, None, 'bpl')].status, 'reported')

    def test_sections(self):
        got = {s: self.v('refusals_by_section', section=s) for s in smc_rti.SECTIONS}
        self.assertEqual({s: v for s, v in got.items() if v}, {'8(1)(h)': 1, '8(1)(j)': 4, '11': 3})
        self.assertEqual(self.v('refusals_total'), 8)

    def test_fees_and_periods(self):
        self.assertEqual(self.v('application_fees_rs'), 21920)
        self.assertEqual(self.v('other_charges_rs'), 43885)
        self.assertEqual(self.v('income_rs'), 65805)
        # row 13d: April..December 2025, printed as-is although the two columns disagree
        before = ('2025-04-01', '2025-12-31')
        self.assertEqual(self.v('income_earlier_in_fy_rs', 'non_bpl', period=before), 193828)
        self.assertEqual(self.v('income_earlier_in_fy_rs', 'all', period=before), 363873)
        # row 14: April 2025..March 2026
        ytd = ('2025-04-01', '2026-03-31')
        self.assertEqual(self.v('income_fy_to_date_rs', 'non_bpl', period=ytd), 259633)
        self.assertEqual(self.v('income_fy_to_date_rs', 'all', period=ytd), 429678)

    def test_header(self):
        (o,) = [o for o in self.res.observations if o.metric_id == 'rti.quarterly.pios']
        self.assertEqual((o.value, o.period_start, o.period_end), (353, *self.Q))
        self.assertEqual(o.publisher_as_of, '2026-05-25')
        self.assertTrue(all((o.geo_level, o.geo_code) == ('smc_city', 'smc') for o in self.res.observations))

    def test_document_sniffed_without_meta(self):
        self.assertEqual(smc_rti._doc(self.raw), 'patrak7')

    def test_validate_rejects_broken_identity(self):
        res = copy.deepcopy(self.res)
        for o in res.observations:
            if o.metric_id == 'rti.quarterly.requests_pending_end' and o.dims['applicants'] == 'all':
                o.value = 3198.0
        with self.assertRaisesRegex(ValidationError, 'pending_end'):
            smc_rti.validate(res, self.raw)

    def test_validate_rejects_period_after_fetch(self):
        early = raw_from_file(RTI / 'smc-rti-patrak-7-q4-2025-26.pdf', retrieved_at='2025-12-15T10:00:00+05:30')
        with self.assertRaisesRegex(ValidationError, 'after the fetch date'):
            smc_rti.validate(self.res, early)


class TestPatrak8(unittest.TestCase, RunnerChecks):
    Q = ('2026-01-01', '2026-03-31')

    @classmethod
    def setUpClass(cls):
        cls.res, cls.raw = _parse(FIX / 'patrak-8-q4-2025-26.pdf')
        cls.by = _by(cls.res)

    def v(self, metric, col='all', section=None):
        return self.by[(f'rti.quarterly.{metric}', *self.Q, section, col)].value

    def test_counts_and_validation(self):
        # 24 data rows x 3 columns + the appellate-officer count; every cell is printed (no blanks)
        self.assertEqual(len(self.res.observations), 73)
        self.assertTrue(all(o.status == 'reported' for o in self.res.observations))
        self.assertPassesRunner(self.res, self.raw)

    def test_values(self):
        self.assertEqual([self.v('first_appeals_pending_start', c) for c in ('bpl', 'non_bpl', 'all')], [134, 702, 836])
        self.assertEqual([self.v('first_appeals_received', c) for c in ('bpl', 'non_bpl', 'all')], [0, 170, 170])
        self.assertEqual(self.v('first_appeals_total'), 1006)
        self.assertEqual(self.v('first_appeals_allowed'), 98)
        self.assertEqual(self.v('first_appeals_partly_allowed'), 4)
        self.assertEqual(self.v('first_appeals_rejected'), 57)
        self.assertEqual(self.v('first_appeals_disposed'), 159)
        # row 7(a): its label wraps, so the values print on the line below the serial number
        self.assertEqual([self.v('first_appeals_disposed_within_time', c) for c in ('bpl', 'non_bpl', 'all')],
                         [0, 100, 100])
        self.assertEqual([self.v('first_appeals_pending_end', c) for c in ('bpl', 'non_bpl', 'all')], [134, 713, 847])
        got = {s: self.v('first_appeal_refusals_by_section', section=s) for s in smc_rti.SECTIONS}
        self.assertEqual({s: v for s, v in got.items() if v}, {'other': 37})
        self.assertEqual(self.v('first_appeal_refusals_total'), 37)
        (o,) = [o for o in self.res.observations if o.metric_id == 'rti.quarterly.appellate_authorities']
        self.assertEqual(o.value, 73)
        self.assertEqual(o.publisher_as_of, '2026-05-25')

    def test_document_sniffed_without_meta(self):
        self.assertEqual(smc_rti._doc(self.raw), 'patrak8')


class TestHelpers(unittest.TestCase):
    def test_legacy_digits(self):
        self.assertEqual(smc_rti._legacy_int('#5#'), 353)
        self.assertEqual(smc_rti._legacy_int('Z_Z5'), 2025)
        self.assertEqual(smc_rti._legacy_int('*#'), 73)
        self.assertEqual([smc_rti._sr(t) for t in ('!', '!_', '!$', ')sVf', '*sVf', 'I', 'n', 'VZHLVM')],
                         ['1', '10', '14', '9(a)', '7(a)', 'i', 'n', None])

    def test_quarter_from_legacy_header(self):
        top = 'TFP _!q_$qZ& YL TFP #_q_&qZ& GF6F\\SLI JQF" o Z_Z& v Z*'     # 01/04/26 - 30/06/26, FY 2026-27
        self.assertEqual(smc_rti._patrak_period(top, 'P7'), (2026, 1, '2026-04-01', '2026-06-30'))
        top = 'તા. 01/10/26 થી તા. 31/12/26  નાણાંકીય વર્ષ : 2026 - 27'      # a Unicode re-typing
        self.assertEqual(smc_rti._patrak_period(top, 'P7'), (2026, 3, '2026-10-01', '2026-12-31'))

    def test_quarter_must_be_exact_and_match_fy(self):
        with self.assertRaisesRegex(ValueError, 'not a financial-year quarter'):
            smc_rti._patrak_period('TFP _!q_!qZ& YL TFP Z(q_ZqZ& JQF" o Z_Z5 v Z&', 'P7')    # Jan-Feb only
        with self.assertRaisesRegex(ValueError, 'does not contain'):
            smc_rti._patrak_period('TFP _!q_!qZ& YL TFP #!q_#qZ& JQF" o Z_Z& v Z*', 'P7')     # wrong FY

    def test_metric_ids_declared_once(self):
        ids = [m.id for m in smc_rti.SOURCE.metrics]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(i.startswith(('rti.annual.', 'rti.quarterly.')) for i in ids))
        used = {r[1] for r in smc_rti.P7_ROWS + smc_rti.P8_ROWS if r[1]}
        self.assertTrue(used <= set(ids))


class FakeCtx:
    def __init__(self, index_body: bytes):
        self.index_body = index_body
        self.calls = []

    def get(self, url, **kw):
        self.calls.append((url, kw))
        body = self.index_body if url == smc_rti.INDEX_URL else b'%PDF-'
        return Raw(url=url, body=body, content_type='', fetch_id=len(self.calls), sha256='', changed=True,
                   retrieved_at=FETCHED, meta=kw.get('meta') or {})


class TestFetch(unittest.TestCase):
    def test_fetch_plan(self):
        ctx = FakeCtx((RTI / 'smc-rti-annual-returns-index-2026-09-27.html').read_bytes())
        raws = list(smc_rti.fetch(ctx))
        urls = [u for u, _ in ctx.calls]
        self.assertEqual(urls[:3], [smc_rti.PATRAK7_URL, smc_rti.PATRAK8_URL, smc_rti.INDEX_URL])
        annual = ctx.calls[3:]
        self.assertEqual(len(annual), 20 - len(smc_rti.SCANNED_RETURNS))
        years = [kw['meta']['year'] for _, kw in annual]
        self.assertEqual(years, sorted(years))                       # oldest first
        self.assertFalse(set(years) & smc_rti.SCANNED_RETURNS)       # image-only scans are not downloaded
        self.assertTrue(all(kw['soft'] for _, kw in ctx.calls))      # one missing file doesn't stop the rest
        # past years are immutable (download once); only the newest return is re-checked
        self.assertEqual([y for (_, kw), y in zip(annual, years) if not kw['skip_if_seen']], ['2025-2026'])
        self.assertEqual(len(raws), len(ctx.calls))


if __name__ == '__main__':
    unittest.main()
