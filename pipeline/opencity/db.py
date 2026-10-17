"""SQLite access: schema migration, run/fetch bookkeeping and idempotent upserts."""
from __future__ import annotations

import json
import math
import sqlite3
from pathlib import Path
from typing import Iterable, Optional

from . import config
from .model import Geo, Metric, Result, Source, canonical_json
from .surat import STANDARD_GEOS

SCHEMA_VERSION = '1'
SCHEMA_FILE = Path(__file__).with_name('schema.sql')
SUCCESS = ('ok', 'unchanged', 'not_modified', 'skipped')


def connect(path: Path | str | None = None) -> sqlite3.Connection:
    path = Path(path or config.DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=60)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    conn.execute('PRAGMA journal_mode = WAL')
    conn.execute('PRAGMA synchronous = NORMAL')
    migrate(conn)
    return conn


def migrate(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_FILE.read_text())
    conn.execute("INSERT INTO meta(key, value) VALUES ('schema_version', ?) "
                 "ON CONFLICT(key) DO UPDATE SET value = excluded.value", (SCHEMA_VERSION,))
    upsert_geos(conn, STANDARD_GEOS)
    conn.commit()


# ---------- catalogue ----------

def register_source(conn: sqlite3.Connection, s: Source) -> None:
    conn.execute(
        """INSERT INTO source(source_id, name, publisher, url, module, cadence, interval_hours,
                              parser_version, geo_note, licence_note, notes, enabled, updated_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
           ON CONFLICT(source_id) DO UPDATE SET
             name=excluded.name, publisher=excluded.publisher, url=excluded.url, module=excluded.module,
             cadence=excluded.cadence, interval_hours=excluded.interval_hours,
             parser_version=excluded.parser_version, geo_note=excluded.geo_note,
             licence_note=excluded.licence_note, notes=excluded.notes, enabled=excluded.enabled,
             updated_at=excluded.updated_at""",
        (s.id, s.name, s.publisher, s.url, s.module, s.cadence, s.interval_hours, s.parser_version,
         s.geo_note, s.licence_note, s.notes, int(s.enabled), config.now_iso()))
    for m in s.metrics:
        register_metric(conn, s, m)


def register_metric(conn: sqlite3.Connection, s: Source, m: Metric) -> None:
    conn.execute(
        """INSERT INTO metric(metric_id, label, unit, module, description, source_id) VALUES (?,?,?,?,?,?)
           ON CONFLICT(metric_id) DO UPDATE SET label=excluded.label, unit=excluded.unit,
             module=excluded.module, description=excluded.description, source_id=excluded.source_id""",
        (m.id, m.label, m.unit, s.module, m.description, s.id))


def upsert_geos(conn: sqlite3.Connection, geos: Iterable[Geo]) -> None:
    for g in geos:
        conn.execute(
            """INSERT INTO geo(geo_level, geo_code, name, parent_level, parent_code, note) VALUES (?,?,?,?,?,?)
               ON CONFLICT(geo_level, geo_code) DO UPDATE SET name=excluded.name,
                 parent_level=coalesce(excluded.parent_level, geo.parent_level),
                 parent_code=coalesce(excluded.parent_code, geo.parent_code),
                 note=coalesce(excluded.note, geo.note)""",
            (g.geo_level, g.geo_code, g.name, g.parent_level, g.parent_code, g.note))


def geo_exists(conn: sqlite3.Connection, level: str, code: str) -> bool:
    return conn.execute('SELECT 1 FROM geo WHERE geo_level=? AND geo_code=?', (level, code)).fetchone() is not None


# ---------- runs and fetches ----------

def begin_run(conn: sqlite3.Connection, command: str) -> int:
    cur = conn.execute('INSERT INTO run(started_at, command) VALUES (?, ?)', (config.now_iso(), command))
    conn.commit()
    return cur.lastrowid


def end_run(conn: sqlite3.Connection, run_id: int, status: str) -> None:
    conn.execute('UPDATE run SET finished_at=?, status=? WHERE run_id=?', (config.now_iso(), status, run_id))
    conn.commit()


def insert_fetch(conn: sqlite3.Connection, **f) -> int:
    f.setdefault('fetched_at', config.now_iso())
    f.setdefault('status', 'pending')
    if isinstance(f.get('meta'), dict):
        f['meta'] = canonical_json(f['meta'])
    cols = ', '.join(f)
    cur = conn.execute(f'INSERT INTO fetch({cols}) VALUES ({", ".join("?" * len(f))})', tuple(f.values()))
    return cur.lastrowid


def update_fetch(conn: sqlite3.Connection, fetch_id: int, **f) -> None:
    if not f:
        return
    sets = ', '.join(f'{k}=?' for k in f)
    conn.execute(f'UPDATE fetch SET {sets} WHERE fetch_id=?', (*f.values(), fetch_id))


def last_good_fetch(conn: sqlite3.Connection, request_key: str) -> Optional[sqlite3.Row]:
    """Latest fetch of this exact request that produced a stored body."""
    return conn.execute(
        """SELECT * FROM fetch WHERE request_key=? AND sha256 IS NOT NULL AND raw_path IS NOT NULL
           ORDER BY fetch_id DESC LIMIT 1""", (request_key,)).fetchone()


def parsed_ok_before(conn: sqlite3.Connection, request_key: str, parser: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM fetch WHERE request_key=? AND parser=? AND status IN ('ok','unchanged','not_modified') LIMIT 1",
        (request_key, parser)).fetchone() is not None


def last_success_time(conn: sqlite3.Connection, source_id: str) -> Optional[str]:
    row = conn.execute(
        f"SELECT max(fetched_at) FROM fetch WHERE source_id=? AND status IN ({','.join('?' * len(SUCCESS))})",
        (source_id, *SUCCESS)).fetchone()
    return row[0] if row else None


# ---------- applying parsed results ----------

def _same(a_val, a_text, a_status, b_val, b_text, b_status) -> bool:
    if a_status != b_status or (a_text or None) != (b_text or None):
        return False
    if a_val is None or b_val is None:
        return a_val is None and b_val is None
    return math.isclose(a_val, b_val, rel_tol=1e-9, abs_tol=1e-9)


def apply_result(conn: sqlite3.Connection, source: Source, fetch_id: int, result: Result, parser: str) -> tuple[int, int]:
    """Upsert observations (keeping revisions) and records (keeping validity history).
    Returns (n_observations, n_records) touched."""
    now = config.now_iso()
    upsert_geos(conn, result.geos)

    for o in result.observations:
        dims = canonical_json(o.dims)
        key = (o.metric_id, o.geo_level, o.geo_code, o.period_start, o.period_end, dims)
        row = conn.execute(
            """SELECT value, value_text, status, fetch_id FROM observation
               WHERE metric_id=? AND geo_level=? AND geo_code=? AND period_start=? AND period_end=? AND dims=?""",
            key).fetchone()
        if row is None:
            conn.execute(
                """INSERT INTO observation(metric_id, geo_level, geo_code, period_start, period_end, dims, value,
                     value_text, status, publisher_as_of, source_id, fetch_id, parser, first_seen, last_seen)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (*key, o.value, o.value_text, o.status, o.publisher_as_of, source.id, fetch_id, parser, now, now))
        elif _same(row['value'], row['value_text'], row['status'], o.value, o.value_text, o.status):
            conn.execute(
                """UPDATE observation SET last_seen=?, publisher_as_of=?, parser=?
                   WHERE metric_id=? AND geo_level=? AND geo_code=? AND period_start=? AND period_end=? AND dims=?""",
                (now, o.publisher_as_of, parser, *key))
        else:
            conn.execute(
                """INSERT INTO observation_revision(metric_id, geo_level, geo_code, period_start, period_end, dims,
                     old_value, old_value_text, old_status, old_fetch_id, new_value, new_value_text, new_status,
                     new_fetch_id, revised_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (*key, row['value'], row['value_text'], row['status'], row['fetch_id'],
                 o.value, o.value_text, o.status, fetch_id, now))
            conn.execute(
                """UPDATE observation SET value=?, value_text=?, status=?, publisher_as_of=?, fetch_id=?, parser=?,
                     last_seen=? WHERE metric_id=? AND geo_level=? AND geo_code=? AND period_start=? AND period_end=?
                     AND dims=?""",
                (o.value, o.value_text, o.status, o.publisher_as_of, fetch_id, parser, now, *key))

    seen: dict[str, set] = {}
    for r in result.records:
        attrs = canonical_json(r.attrs)
        seen.setdefault(r.record_type, set()).add(r.record_key)
        cur = conn.execute(
            'SELECT attrs, valid_from FROM record WHERE record_type=? AND record_key=? AND valid_to IS NULL',
            (r.record_type, r.record_key)).fetchone()
        if cur is not None and cur['attrs'] == attrs:
            continue
        if cur is not None and cur['valid_from'] == now:
            # changed again within the same second: amend that version instead of adding a zero-length one
            conn.execute('UPDATE record SET attrs=?, fetch_id=? WHERE record_type=? AND record_key=? AND valid_from=?',
                         (attrs, fetch_id, r.record_type, r.record_key, now))
            continue
        if cur is not None:
            conn.execute('UPDATE record SET valid_to=? WHERE record_type=? AND record_key=? AND valid_from=?',
                         (now, r.record_type, r.record_key, cur['valid_from']))
        conn.execute(
            'INSERT INTO record(record_type, record_key, attrs, valid_from, source_id, fetch_id) VALUES (?,?,?,?,?,?)',
            (r.record_type, r.record_key, attrs, now, source.id, fetch_id))

    for rtype in result.complete_record_types:
        keys = seen.get(rtype, set())
        for row in conn.execute(
                'SELECT record_key, valid_from FROM record WHERE record_type=? AND source_id=? AND valid_to IS NULL',
                (rtype, source.id)).fetchall():
            if row['record_key'] not in keys:
                conn.execute('UPDATE record SET valid_to=? WHERE record_type=? AND record_key=? AND valid_from=?',
                             (now, rtype, row['record_key'], row['valid_from']))

    return len(result.observations), len(result.records)


def query(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    return conn.execute(sql, params).fetchall()


def dumps_meta(meta: dict) -> str:
    return json.dumps(meta, sort_keys=True, ensure_ascii=False)
