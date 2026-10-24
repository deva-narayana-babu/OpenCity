"""Write git-friendly CSV exports of the database (stable sort, files rewritten only when they change).

data/export/
  catalog/sources.csv, metrics.csv, geo.csv
  observations/<source_id>.csv     one tidy file per source, with provenance columns
  records/<record_type>.csv        current records, attributes expanded to columns
"""
from __future__ import annotations

import csv
import io
import json
import sqlite3
from pathlib import Path

from . import config


def _write_if_changed(path: Path, rows: list[dict], fields: list[str]) -> bool:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator='\n', extrasaction='ignore')
    w.writeheader()
    w.writerows(rows)
    data = buf.getvalue().encode()
    if path.exists() and path.read_bytes() == data:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_bytes(data)
    tmp.replace(path)
    return True


def export(conn: sqlite3.Connection, out_dir: Path | None = None) -> list[str]:
    out = Path(out_dir or config.EXPORT_DIR)
    changed = []

    def emit(rel: str, sql: str, params=()):
        cur = conn.execute(sql, params)
        fields = [d[0] for d in cur.description]
        rows = [dict(r) for r in cur.fetchall()]
        if _write_if_changed(out / rel, rows, fields):
            changed.append(rel)

    emit('catalog/sources.csv',
         'SELECT source_id, name, publisher, url, module, cadence, interval_hours, parser_version, geo_note, '
         'licence_note, notes FROM source ORDER BY source_id')
    emit('catalog/metrics.csv',
         'SELECT metric_id, label, unit, module, source_id, description FROM metric ORDER BY metric_id')
    emit('catalog/geo.csv',
         'SELECT geo_level, geo_code, name, parent_level, parent_code, note FROM geo ORDER BY geo_level, geo_code')

    for (sid,) in conn.execute('SELECT DISTINCT source_id FROM observation ORDER BY 1').fetchall():
        emit(f'observations/{sid}.csv',
             """SELECT o.metric_id, o.geo_level, o.geo_code, o.period_start, o.period_end, o.dims, o.value,
                       o.value_text, o.status, o.publisher_as_of, f.url AS source_url,
                       f.fetched_at AS retrieved_at, f.sha256 AS raw_sha256, o.parser
                FROM observation o JOIN fetch f ON f.fetch_id = o.fetch_id
                WHERE o.source_id = ?
                ORDER BY o.metric_id, o.geo_level, o.geo_code, o.period_start, o.period_end, o.dims""", (sid,))

    for (rtype,) in conn.execute('SELECT DISTINCT record_type FROM record ORDER BY 1').fetchall():
        rows = conn.execute(
            """SELECT r.record_key, r.attrs, r.valid_from, r.source_id, f.url AS source_url
               FROM record r JOIN fetch f ON f.fetch_id = r.fetch_id
               WHERE r.record_type = ? AND r.valid_to IS NULL ORDER BY r.record_key""", (rtype,)).fetchall()
        keys: list[str] = []
        flat = []
        for r in rows:
            attrs = json.loads(r['attrs'])
            for k in attrs:
                if k not in keys:
                    keys.append(k)
            flat.append({'record_key': r['record_key'], **attrs, 'valid_from': r['valid_from'],
                         'source_id': r['source_id'], 'source_url': r['source_url']})
        fields = ['record_key', *keys, 'valid_from', 'source_id', 'source_url']
        if _write_if_changed(out / f'records/{rtype}.csv', flat, fields):
            changed.append(f'records/{rtype}.csv')

    doc = sources_doc(conn).encode()
    if not (out / 'README.md').exists() or (out / 'README.md').read_bytes() != doc:
        (out / 'README.md').write_bytes(doc)
        changed.append('README.md')
    return changed


def _cell(v) -> str:
    return '' if v is None else str(v).replace('|', '\\|').replace('\n', ' ')


def sources_doc(conn: sqlite3.Connection) -> str:
    """data/export/README.md: every source with its provenance, how it is collected, health and metric coverage.
    Built from the database and the adapters' own docstrings, so it never drifts from the code."""
    from .registry import discover
    adapters = discover()
    health = {r['source_id']: r for r in conn.execute('SELECT * FROM v_source_health')}
    sources = conn.execute('SELECT * FROM source ORDER BY module, source_id').fetchall()
    stats = {r['metric_id']: r for r in conn.execute(
        """SELECT metric_id, count(*) AS n, sum(status = 'reported') AS reported,
                  min(period_start) AS first, max(period_end) AS last, count(DISTINCT geo_code) AS places
           FROM observation GROUP BY metric_id""")}
    records = {}
    for r in conn.execute('SELECT source_id, record_type, count(*) AS n FROM record WHERE valid_to IS NULL '
                          'GROUP BY 1, 2 ORDER BY 1, 2'):
        records.setdefault(r['source_id'], []).append(f"{r['record_type']} ({r['n']})")

    out = ['# OpenCity data: sources and metrics', '',
           'This file is written by the refresher (`opencity/export.py`) from the database and from each adapter\'s '
           'own description. Do not edit it by hand. The same catalogue is in `catalog/*.csv`, the numbers are in '
           '`observations/<source>.csv` and the named entities are in `records/<type>.csv`.', '',
           f'{len(sources)} sources, {sum(1 for _ in stats)} metrics with data, '
           f'{sum(r["n"] for r in stats.values())} observations.', '',
           '| Source | Module | Publisher | Cadence | Metrics | Observations | Latest period | Status |',
           '|---|---|---|---|---|---|---|---|']
    for s in sources:
        h = health.get(s['source_id'])
        n_metrics = conn.execute('SELECT count(*) FROM metric WHERE source_id=?', (s['source_id'],)).fetchone()[0]
        status = 'disabled' if not s['enabled'] else ('error' if h and h['errors_last_run'] else
                                                      ('ok' if h and h['last_success'] else 'not run yet'))
        out.append(f"| [{s['source_id']}](#{s['source_id']}) | {s['module']} | {_cell(s['publisher'])} | "
                   f"{s['cadence']} | {n_metrics} | {h['n_observations'] if h else 0} | "
                   f"{_cell(h['latest_period'] if h else '')} | {status} |")

    for s in sources:
        sid, h = s['source_id'], health.get(s['source_id'])
        out += ['', f'## {sid}', '', f"**{_cell(s['name'])}**", '',
                f"- **Publisher:** {_cell(s['publisher'])}",
                f"- **Page:** {s['url']}",
                f"- **Module:** {s['module']}; **cadence:** {s['cadence']} (checked every {s['interval_hours']:g} h)",
                f"- **Geography:** {_cell(s['geo_note'])}",
                f"- **Licence:** {_cell(s['licence_note'])}",
                f"- **Enabled:** {'yes' if s['enabled'] else 'no'}; **last success:** "
                f"{(h['last_success'] if h else None) or 'never'}"]
        if h and h['last_error'] and h['errors_last_run']:
            out.append(f"- **Last error:** {_cell(h['last_error'][:300])}")
        if h:
            out.append(f"- **Holds:** {h['n_observations']} observations"
                       + (f"; records: {', '.join(records[sid])}" if sid in records else ''))
        if s['notes']:
            out.append(f"- **Notes:** {_cell(s['notes'])}")
        ad = adapters.get(sid)
        if ad and ad.module.__doc__:
            out += ['', '<details><summary>How it is collected and parsed</summary>', '', '```text',
                    ad.module.__doc__.strip(), '```', '', '</details>']
        metrics = conn.execute('SELECT * FROM metric WHERE source_id=? ORDER BY metric_id', (sid,)).fetchall()
        if metrics:
            out += ['', '| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |',
                    '|---|---|---|---|---|---|---|']
            for m in metrics:
                st = stats.get(m['metric_id'])
                cov = (f"{st['n']} ({st['reported']})", st['places'], f"{st['first'][:10]} to {st['last'][:10]}") \
                    if st else ('0', '', '')
                out.append(f"| `{m['metric_id']}` | {_cell(m['label'])} | {_cell(m['unit'])} | {cov[0]} | {cov[1]} | "
                           f"{cov[2]} | {_cell(m['description'])} |")
    return '\n'.join(out) + '\n'
