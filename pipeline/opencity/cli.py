"""Command line: python3 -m opencity <command> (run from pipeline/, or use scripts/*.sh)."""
from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from pathlib import Path

from . import config, db, export as export_mod, runner
from .model import Raw
from .registry import discover


def _adapters(ids: list[str] | None):
    all_ = discover()
    if not ids:
        return list(all_.values())
    missing = [i for i in ids if i not in all_]
    if missing:
        sys.exit(f'unknown source(s): {", ".join(missing)}. Known: {", ".join(all_)}')
    return [all_[i] for i in ids]


def _table(rows, cols=None, out=sys.stdout):
    rows = [dict(r) for r in rows]
    if not rows:
        print('(no rows)', file=out)
        return
    cols = cols or list(rows[0])
    widths = {c: min(60, max(len(c), *(len(str(r.get(c, '') if r.get(c) is not None else '')) for r in rows))) for c in cols}
    print('  '.join(c.ljust(widths[c]) for c in cols), file=out)
    print('  '.join('-' * widths[c] for c in cols), file=out)
    for r in rows:
        print('  '.join(str('' if r.get(c) is None else r.get(c))[:60].ljust(widths[c]) for c in cols), file=out)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog='opencity', description='OpenCity Surat data pipeline')
    p.add_argument('--db', type=Path, default=config.DB_PATH, help=f'database file (default {config.DB_PATH})')
    p.add_argument('--data-dir', type=Path, default=config.DATA_DIR, help='where raw/ snapshots are archived')
    p.add_argument('-v', '--verbose', action='store_true')
    sub = p.add_subparsers(dest='cmd', required=True)

    sub.add_parser('init', help='create or migrate the database')
    sub.add_parser('sources', help='list source adapters')

    r = sub.add_parser('refresh', help='fetch sources and update the database')
    r.add_argument('--source', '-s', action='append', help='only this source (repeatable)')
    r.add_argument('--due', action='store_true', help='only sources whose refresh interval has elapsed')
    r.add_argument('--force', action='store_true', help='ignore intervals, conditional GET and already-seen documents')

    rp = sub.add_parser('reparse', help='re-run parsers over archived raw snapshots (no network)')
    rp.add_argument('--source', '-s', action='append')

    pf = sub.add_parser('parse-file', help='run one adapter\'s parser on a local file and print the result')
    pf.add_argument('source')
    pf.add_argument('path', type=Path)
    pf.add_argument('--url', default='file://local')
    pf.add_argument('--meta', action='append', default=[], help='key=value passed as raw.meta')
    pf.add_argument('--meta-json', help='JSON object merged into raw.meta (for list/dict values)')
    pf.add_argument('--json', action='store_true', help='print JSON instead of CSV')

    sub.add_parser('status', help='freshness and health of every source')

    e = sub.add_parser('export', help='write CSV exports')
    e.add_argument('--out', type=Path, default=config.EXPORT_DIR)

    q = sub.add_parser('query', help='run a read-only SQL query')
    q.add_argument('sql')
    q.add_argument('--csv', action='store_true')

    a = p.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if a.verbose else logging.INFO,
                        format='%(asctime)s %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%dT%H:%M:%S')

    if a.cmd == 'sources':
        _table([{'source_id': x.id, 'module': x.source.module, 'cadence': x.source.cadence,
                 'interval_h': x.source.interval_hours, 'metrics': len(x.source.metrics),
                 'name': x.source.name} for x in _adapters(None)])
        return 0

    if a.cmd == 'parse-file':
        ad = _adapters([a.source])[0]
        meta = dict(kv.split('=', 1) for kv in a.meta)
        if a.meta_json:
            meta.update(json.loads(a.meta_json))
        raw = Raw(url=a.url, body=a.path.read_bytes(), content_type='', fetch_id=0, sha256='',
                  changed=True, retrieved_at=config.now_iso(), meta=meta)
        res = ad.module.parse(raw)
        if a.json:
            print(json.dumps({'observations': [o.__dict__ for o in res.observations],
                              'records': [r.__dict__ for r in res.records],
                              'geos': [g.__dict__ for g in res.geos]}, ensure_ascii=False, indent=1))
        else:
            w = csv.writer(sys.stdout)
            w.writerow(['metric_id', 'geo_level', 'geo_code', 'period_start', 'period_end', 'dims', 'value',
                        'value_text', 'status', 'publisher_as_of'])
            for o in res.observations:
                w.writerow([o.metric_id, o.geo_level, o.geo_code, o.period_start, o.period_end,
                            json.dumps(o.dims, ensure_ascii=False) if o.dims else '', o.value, o.value_text,
                            o.status, o.publisher_as_of])
            for r in res.records:
                print(f'# record {r.record_type} {r.record_key} {json.dumps(r.attrs, ensure_ascii=False)}')
        print(f'# {len(res.observations)} observations, {len(res.records)} records, {len(res.geos)} geos',
              file=sys.stderr)
        return 0

    conn = db.connect(a.db)
    if a.cmd == 'init':
        for ad in _adapters(None):
            db.register_source(conn, ad.source)
        conn.commit()
        print(f'database ready: {a.db}')
        return 0

    if a.cmd == 'refresh':
        out = runner.refresh(conn, _adapters(a.source), due_only=a.due, force=a.force, data_dir=a.data_dir,
                             command=' '.join(sys.argv[1:]) or 'refresh')
        _table([{'source': k, 'result': v} for k, v in out.items()])
        return 1 if any(v.startswith('error') for v in out.values()) else 0

    if a.cmd == 'reparse':
        out = runner.reparse(conn, _adapters(a.source), data_dir=a.data_dir)
        _table([{'source': k, 'result': v} for k, v in out.items()])
        return 1 if any('failed' in v for v in out.values()) else 0

    if a.cmd == 'status':
        _table(db.query(conn, 'SELECT source_id, cadence, last_success, last_status, n_observations AS obs, '
                              'n_current_records AS records, latest_period, errors_last_run AS errors, '
                              'substr(last_error, 1, 50) AS last_error '
                              'FROM v_source_health ORDER BY source_id'))
        return 0

    if a.cmd == 'export':
        changed = export_mod.export(conn, a.out)
        print(f'{len(changed)} file(s) changed under {a.out}')
        for c in changed:
            print('  ' + c)
        return 0

    if a.cmd == 'query':
        ro = db.connect(a.db)
        ro.execute('PRAGMA query_only = ON')
        rows = ro.execute(a.sql).fetchall()
        if a.csv:
            w = csv.writer(sys.stdout)
            if rows:
                w.writerow(rows[0].keys())
            w.writerows([tuple(r) for r in rows])
        else:
            _table(rows)
        return 0
    return 2
