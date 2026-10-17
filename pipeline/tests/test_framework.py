"""Framework tests: parsing helpers, archive normalisation, upserts with history, and the runner (offline)."""
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

from opencity import archive, db, runner
from opencity.fetcher import Response
from opencity.model import FetchError, Geo, Metric, Obs, Record, Result, Source, ValidationError
from opencity.parse import (fy_period, fy_start, html_tables, month_period, month_year, num, num_or_none,
                            parse_dt, quarter_of_fy)
from opencity.registry import Adapter, discover
from opencity.surat import zone_code


class TestParse(unittest.TestCase):
    def test_num(self):
        self.assertEqual(num('1,23,456.70'), 123456.7)
        self.assertEqual(num('૧૨૩'), 123)
        self.assertEqual(num('(12)'), -12)
        self.assertEqual(num('45%'), 45)
        self.assertEqual(num('₹ 1,000'), 1000)
        for missing in ('', '-', 'NA', 'n.a.', 'Nil', None):
            self.assertIsNone(num(missing))
        with self.assertRaises(ValueError):
            num('twelve')
        self.assertIsNone(num_or_none('twelve'))

    def test_periods(self):
        self.assertEqual(month_year('July-2026'), (2026, 7))
        self.assertEqual(month_year('Sept 2025'), (2025, 9))
        self.assertEqual(month_period(2024, 2), ('2024-02-01', '2024-02-29'))
        self.assertEqual(fy_start('FY 2025-26'), 2025)
        self.assertEqual(fy_period(2025), ('2025-04-01', '2026-03-31'))
        self.assertEqual(quarter_of_fy(2025, 4), ('2026-01-01', '2026-03-31'))
        self.assertEqual(quarter_of_fy(2025, 1), ('2025-04-01', '2025-06-30'))

    def test_parse_dt_24h(self):
        self.assertEqual(parse_dt('27/09/2026 24:00'), '2026-09-28T00:00')
        self.assertEqual(parse_dt('31/12/2026 24:00'), '2027-01-01T00:00')
        self.assertEqual(parse_dt('27/09/2026 22:00'), '2026-09-27T22:00')

    def test_html_tables_spans(self):
        html = """<h3>Rain</h3><table><tr><th rowspan=2>Zone</th><th colspan=2>mm</th></tr>
                  <tr><th>Day</th><th>Total</th></tr>
                  <tr><td>Central</td><td>1</td><td><a href="/x">2</a></td></tr></table>"""
        (t,) = html_tables(html)
        self.assertEqual(t.rows[0], ['Zone', 'mm', 'mm'])
        self.assertEqual(t.rows[1], ['Zone', 'Day', 'Total'])
        self.assertEqual(t.rows[2], ['Central', '1', '2'])
        self.assertEqual(t.links[2][2], ['/x'])
        self.assertIn('Rain', t.heading)

    def test_zone_codes(self):
        cases = {'West Zone (mm)': 'west', 'Rander': 'west', 'East Zone A(mm)': 'east_a', 'East Zone - B': 'east_b',
                 'South Zone (mm)': 'south', 'South Zone-A': 'south_a', 'South Zone-B (Kanakpur)': 'south_b',
                 'Athwa Zone': 'south_west', 'South West Zone (mm)': 'south_west', 'South East Zone': 'south_east',
                 'Head Quarter': 'hq', 'Central Zone (mm)': 'central', 'North Zone': 'north'}
        for label, code in cases.items():
            self.assertEqual(zone_code(label), code, label)
        with self.assertRaises(KeyError):
            zone_code('Moon Zone')


class TestArchive(unittest.TestCase):
    def test_normalize_blanks_volatile_parts(self):
        a = b'<html><div>Visitor Count <span>79300522</span></div><input name="__RequestVerificationToken" type="hidden" value="abc"></html>'
        b = b'<html><div>Visitor Count <span>79300524</span></div><input name="__RequestVerificationToken" type="hidden" value="xyz"></html>'
        self.assertEqual(archive.normalize(a, 'text/html'), archive.normalize(b, 'text/html'))
        self.assertNotIn(b'abc', archive.normalize(a, 'text/html'))
        pdf = b'%PDF-1.4 Visitor Count 123'
        self.assertEqual(archive.normalize(pdf, 'application/pdf'), pdf)

    def test_store_is_content_addressed(self):
        with tempfile.TemporaryDirectory() as d:
            s1, p1 = archive.store(Path(d), 'x', b'hello', 'text/plain', 'http://e/a.txt')
            s2, p2 = archive.store(Path(d), 'x', b'hello', 'text/plain', 'http://e/b.txt')
            self.assertEqual((s1, p1), (s2, p2))
            self.assertEqual(archive.load(Path(d), p1), b'hello')


SRC = Source(id='fake', name='Fake', publisher='Test', url='http://example.test/', module='test', cadence='daily',
             interval_hours=24, metrics=(Metric('t.value', 'Value'),), record_types=('person',))


class TestApplyResult(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.conn = db.connect(Path(self.tmp.name) / 't.db')
        db.register_source(self.conn, SRC)
        self.fid = db.insert_fetch(self.conn, source_id='fake', url='u', request_key='k')

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def _obs(self, v, status='reported'):
        return Obs('t.value', 'smc_city', 'smc', '2026-01-01', '2026-01-31', value=v, status=status)

    def test_revisions_kept(self):
        db.apply_result(self.conn, SRC, self.fid, Result(observations=[self._obs(10)]), 'fake@1')
        db.apply_result(self.conn, SRC, self.fid, Result(observations=[self._obs(10)]), 'fake@1')
        self.assertEqual(self.conn.execute('SELECT count(*) FROM observation_revision').fetchone()[0], 0)
        db.apply_result(self.conn, SRC, self.fid, Result(observations=[self._obs(12)]), 'fake@1')
        rev = self.conn.execute('SELECT old_value, new_value FROM observation_revision').fetchone()
        self.assertEqual(tuple(rev), (10, 12))
        db.apply_result(self.conn, SRC, self.fid, Result(observations=[self._obs(None, 'not_reported')]), 'fake@1')
        row = self.conn.execute('SELECT value, status FROM observation').fetchone()
        self.assertEqual(tuple(row), (None, 'not_reported'))

    def _two_runs(self, times):
        r1 = Record('person', 'ward-1-a', {'name': 'A'})
        r2 = Record('person', 'ward-1-b', {'name': 'B'})
        with mock.patch('opencity.config.now_iso', side_effect=times):
            db.apply_result(self.conn, SRC, self.fid, Result(records=[r1, r2], complete_record_types=('person',)), 'p')
            db.apply_result(self.conn, SRC, self.fid, Result(records=[Record('person', 'ward-1-a', {'name': 'A2'})],
                                                             complete_record_types=('person',)), 'p')
        return {r['record_key']: r['attrs'] for r in self.conn.execute('SELECT * FROM v_current_record')}

    def test_record_history_and_closing(self):
        cur = self._two_runs(['2026-01-01T10:00:00+05:30', '2026-01-02T10:00:00+05:30'])
        self.assertEqual(cur, {'ward-1-a': '{"name":"A2"}'})       # B dropped off the complete list -> closed
        rows = self.conn.execute('SELECT record_key, attrs, valid_from, valid_to FROM record ORDER BY 1, 3').fetchall()
        self.assertEqual([tuple(r) for r in rows], [
            ('ward-1-a', '{"name":"A"}', '2026-01-01T10:00:00+05:30', '2026-01-02T10:00:00+05:30'),
            ('ward-1-a', '{"name":"A2"}', '2026-01-02T10:00:00+05:30', None),
            ('ward-1-b', '{"name":"B"}', '2026-01-01T10:00:00+05:30', '2026-01-02T10:00:00+05:30')])

    def test_record_changed_twice_in_same_second_is_amended(self):
        cur = self._two_runs(['2026-01-01T10:00:00+05:30'] * 2)
        self.assertEqual(cur, {'ward-1-a': '{"name":"A2"}'})
        self.assertEqual(self.conn.execute("SELECT count(*) FROM record WHERE record_key='ward-1-a'").fetchone()[0], 1)


class FakeFetcher:
    def __init__(self, pages):
        self.pages = pages
        self.calls = 0

    def request(self, method, url, **kw):
        self.calls += 1
        body = self.pages[url]
        if isinstance(body, Exception):
            raise body
        return Response(200, body, url, {'content-type': 'text/html'})


def fake_adapter(source=SRC, parse=None):
    def fetch(ctx):
        yield ctx.get('http://example.test/page')

    def default_parse(raw):
        v = float(raw.text.strip('<p>/'))
        return Result(observations=[Obs('t.value', 'smc_city', 'smc', '2026-01-01', '2026-01-31', value=v)])
    mod = types.SimpleNamespace(SOURCE=source, fetch=fetch, parse=parse or default_parse)
    return Adapter(source, mod)


class TestRunner(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.conn = db.connect(self.dir / 't.db')

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def test_refresh_and_unchanged_and_due(self):
        f = FakeFetcher({'http://example.test/page': b'<p>5</p>'})
        out = runner.refresh(self.conn, [fake_adapter()], data_dir=self.dir, fetcher=f)
        self.assertTrue(out['fake'].startswith('ok'), out)
        out = runner.refresh(self.conn, [fake_adapter()], data_dir=self.dir, fetcher=f)
        statuses = [r[0] for r in self.conn.execute('SELECT status FROM fetch ORDER BY fetch_id')]
        self.assertEqual(statuses, ['ok', 'unchanged'])
        out = runner.refresh(self.conn, [fake_adapter()], due_only=True, data_dir=self.dir, fetcher=f)
        self.assertEqual(out['fake'], 'not due')
        self.assertEqual(f.calls, 2)

    def test_validation_error_is_recorded_and_nothing_written(self):
        def bad_parse(raw):
            return Result(observations=[Obs('t.undeclared', 'smc_city', 'smc', '2026-01-01', '2026-01-31', value=1)])
        f = FakeFetcher({'http://example.test/page': b'<p>5</p>'})
        out = runner.refresh(self.conn, [fake_adapter(parse=bad_parse)], data_dir=self.dir, fetcher=f)
        self.assertTrue(out['fake'].startswith('error'), out)
        row = self.conn.execute('SELECT status, error FROM fetch').fetchone()
        self.assertEqual(row['status'], 'validation_error')
        self.assertIn('undeclared metric', row['error'])
        self.assertEqual(self.conn.execute('SELECT count(*) FROM observation').fetchone()[0], 0)

    def test_unknown_geo_rejected(self):
        def geo_parse(raw):
            return Result(observations=[Obs('t.value', 'smc_ward', '99', '2026-01-01', '2026-01-31', value=1)])
        f = FakeFetcher({'http://example.test/page': b'x'})
        runner.refresh(self.conn, [fake_adapter(parse=geo_parse)], data_dir=self.dir, fetcher=f)
        self.assertIn('unknown geography', self.conn.execute('SELECT error FROM fetch').fetchone()[0])

        def geo_ok(raw):
            return Result(observations=[Obs('t.value', 'smc_ward', '99', '2026-01-01', '2026-01-31', value=1)],
                          geos=[Geo('smc_ward', '99', 'Ward 99', 'smc_city', 'smc')])
        out = runner.refresh(self.conn, [fake_adapter(parse=geo_ok)], data_dir=self.dir, fetcher=f, force=True)
        self.assertTrue(out['fake'].startswith('ok'), out)

    def test_fetch_error_does_not_stop_other_sources(self):
        other = Source(id='other', name='Other', publisher='T', url='http://o.test/', module='test', cadence='daily',
                       interval_hours=24, metrics=(Metric('t.value', 'Value'),))
        f = FakeFetcher({'http://example.test/page': FetchError('HTTP 503', http_status=503)})
        out = runner.refresh(self.conn, [fake_adapter(), fake_adapter(other)], data_dir=self.dir, fetcher=f)
        self.assertTrue(out['fake'].startswith('error'))
        self.assertTrue(out['other'].startswith('error'))   # same URL in this fake; both recorded, neither crashed
        self.assertEqual(self.conn.execute("SELECT count(*) FROM fetch WHERE status='http_error'").fetchone()[0], 2)

    def test_reparse_from_archive(self):
        f = FakeFetcher({'http://example.test/page': b'<p>7</p>'})
        runner.refresh(self.conn, [fake_adapter()], data_dir=self.dir, fetcher=f)
        self.conn.execute('DELETE FROM observation')
        self.conn.commit()
        out = runner.reparse(self.conn, [fake_adapter()], data_dir=self.dir)
        self.assertEqual(out['fake'], 'reparsed 1 document(s)')
        self.assertEqual(self.conn.execute('SELECT value FROM observation').fetchone()[0], 7)


class TestRunnerFeatures(unittest.TestCase):
    """soft fetches, archive reuse for immutable documents, and the health view."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.conn = db.connect(self.dir / 't.db')

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def _adapter(self, version='1', urls=('http://example.test/a',), soft=False, skip=False):
        src = Source(id='fake', name='Fake', publisher='T', url='http://example.test/', module='test',
                     cadence='daily', interval_hours=24, metrics=(Metric('t.value', 'Value'),), parser_version=version)

        def fetch(ctx):
            for u in urls:
                yield ctx.get(u, soft=soft, skip_if_seen=skip, meta={'u': u})

        def parse(raw):
            v = float(raw.text.strip('<p>/'))
            day = '2026-01-0' + raw.meta['u'][-1].replace('a', '1').replace('b', '2')
            return Result(observations=[Obs('t.value', 'smc_city', 'smc', day, day, value=v)])
        return Adapter(src, types.SimpleNamespace(SOURCE=src, fetch=fetch, parse=parse))

    def test_soft_failure_keeps_other_documents(self):
        f = FakeFetcher({'http://example.test/a': FetchError('HTTP 500', http_status=500),
                         'http://example.test/b': b'<p>3</p>'})
        out = runner.refresh(self.conn, [self._adapter(urls=('http://example.test/a', 'http://example.test/b'),
                                                       soft=True)], data_dir=self.dir, fetcher=f)
        self.assertTrue(out['fake'].startswith('error (1)'), out)
        self.assertEqual(self.conn.execute('SELECT value FROM observation').fetchone()[0], 3)

    def test_skip_if_seen_reuses_archive_when_parser_changes(self):
        f = FakeFetcher({'http://example.test/a': b'<p>4</p>'})
        runner.refresh(self.conn, [self._adapter('1', skip=True)], data_dir=self.dir, fetcher=f)
        runner.refresh(self.conn, [self._adapter('1', skip=True)], data_dir=self.dir, fetcher=f)
        self.assertEqual(f.calls, 1)                       # already parsed by v1: skipped
        out = runner.refresh(self.conn, [self._adapter('2', skip=True)], data_dir=self.dir, fetcher=f)
        self.assertEqual(f.calls, 1, 'parser bump must reparse the archived copy, not re-download')
        self.assertTrue(out['fake'].startswith('ok: 1 document'), out)
        self.assertEqual(self.conn.execute('SELECT parser FROM observation').fetchone()[0], 'fake@2')

    def test_health_view_forgets_errors_after_a_clean_run(self):
        bad = FakeFetcher({'http://example.test/a': FetchError('HTTP 500', http_status=500)})
        runner.refresh(self.conn, [self._adapter()], data_dir=self.dir, fetcher=bad)
        h = self.conn.execute('SELECT errors_last_run, last_error FROM v_source_health').fetchone()
        self.assertEqual(h['errors_last_run'], 1)
        good = FakeFetcher({'http://example.test/a': b'<p>1</p>'})
        runner.refresh(self.conn, [self._adapter()], data_dir=self.dir, fetcher=good)
        h = self.conn.execute('SELECT errors_last_run, last_error, last_status FROM v_source_health').fetchone()
        self.assertEqual((h['errors_last_run'], h['last_error'], h['last_status']), (0, None, 'ok'))


class TestRegistry(unittest.TestCase):
    def test_all_adapters_load_and_declare_metrics(self):
        adapters = discover()
        self.assertIn('smc_swm', adapters)
        seen = {}
        for ad in adapters.values():
            self.assertTrue(ad.source.metrics or ad.source.record_types, ad.id)
            for m in ad.source.metrics:
                self.assertNotIn(m.id, seen, f'metric {m.id} declared by both {seen.get(m.id)} and {ad.id}')
                seen[m.id] = ad.id


if __name__ == '__main__':
    unittest.main()
