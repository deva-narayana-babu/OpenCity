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
    return changed
