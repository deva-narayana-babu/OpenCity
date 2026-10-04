"""The refresher: fetch -> archive -> parse -> validate -> upsert, one source at a time.

A failure in one source never stops the others; it is recorded in the fetch table
and reflected in the exit code so cron/CI can alert on it.
"""
from __future__ import annotations

import hashlib
import logging
import re
import sqlite3
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable

from . import archive, config, db
from .fetcher import Fetcher
from .model import FetchError, Raw, Result, ValidationError, canonical_json
from .registry import Adapter

log = logging.getLogger(__name__)

_ISO = re.compile(r'^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}(:\d{2})?)?$')


def request_key(method: str, url: str, body: bytes | None) -> str:
    h = hashlib.sha1(f'{method} {url}'.encode())
    if body:
        h.update(b'\n' + body)
    return h.hexdigest()


class Context:
    """What an adapter's fetch() gets: polite HTTP that archives and records every response."""

    def __init__(self, conn: sqlite3.Connection, adapter: Adapter, run_id: int | None,
                 fetcher: Fetcher, data_dir: Path, force: bool = False):
        self.conn = conn
        self.adapter = adapter
        self.source = adapter.source
        self.run_id = run_id
        self.fetcher = fetcher
        self.data_dir = data_dir
        self.force = force
        self.errors: list[str] = []      # soft (non-blocking) fetch failures; reported by the runner
        self.log = logging.getLogger(f'opencity.sources.{adapter.id}')

    @property
    def now(self) -> datetime:
        return config.now()

    def get(self, url: str, *, params: dict | None = None, headers: dict | None = None,
            meta: dict | None = None, skip_if_seen: bool = False, conditional: bool = True,
            soft: bool = False) -> Raw | None:
        """GET and archive. skip_if_seen: for immutable documents (download once). soft: on a non-blocking
        failure, record it and return None so fetch() can carry on with its other documents."""
        return self._request('GET', url, params=params, headers=headers, meta=meta,
                             skip_if_seen=skip_if_seen, conditional=conditional, soft=soft)

    def post(self, url: str, *, json: object = None, form: dict | None = None, headers: dict | None = None,
             meta: dict | None = None, skip_if_seen: bool = False, soft: bool = False) -> Raw | None:
        return self._request('POST', url, json=json, form=form, headers=headers, meta=meta,
                             skip_if_seen=skip_if_seen, conditional=False, soft=soft)

    def seen(self, method: str, url: str, body: bytes | None = None) -> bool:
        """True if this exact request was already fetched and parsed by the current parser version."""
        return db.parsed_ok_before(self.conn, request_key(method, url, body), self.adapter.parser)

    def _request(self, method, url, *, params=None, json=None, form=None, headers=None, meta=None,
                 skip_if_seen=False, conditional=True, soft=False) -> Raw | None:
        import json as jsonlib
        import urllib.parse
        full = url + (('&' if '?' in url else '?') + urllib.parse.urlencode(params) if params else '')
        body_key = (jsonlib.dumps(json, sort_keys=True).encode() if json is not None else
                    urllib.parse.urlencode(form).encode() if form is not None else None)
        rkey = request_key(method, full, body_key)
        prev = db.last_good_fetch(self.conn, rkey)
        if skip_if_seen and not self.force:
            if db.parsed_ok_before(self.conn, rkey, self.adapter.parser):
                self.log.debug('skip (already parsed): %s', full)
                return None
            if prev is not None and prev['status'] in ('ok', 'unchanged', 'not_modified'):
                # immutable document already archived; only the parser changed -> reparse the archived copy
                return self._from_archive(prev, meta)
        fetch_id = db.insert_fetch(self.conn, run_id=self.run_id, source_id=self.source.id, url=full,
                                   request_key=rkey, meta=meta or {})
        self.conn.commit()
        try:
            resp = self.fetcher.request(
                method, full, json=json, form=form, headers=headers,
                etag=prev['etag'] if (prev and conditional and not self.force) else None,
                last_modified=prev['last_modified'] if (prev and conditional and not self.force) else None)
        except FetchError as e:
            status = 'blocked' if e.blocked else ('http_error' if e.http_status else 'network_error')
            db.update_fetch(self.conn, fetch_id, status=status, http_status=e.http_status, error=str(e)[:1000])
            self.conn.commit()
            if soft and not e.blocked:
                self.errors.append(str(e))
                self.log.warning('%s (continuing with other documents)', e)
                return None
            raise
        if resp.status == 304 and prev is not None:
            body = archive.load(self.data_dir, prev['raw_path'])
            sha, rel, changed, status = prev['sha256'], prev['raw_path'], False, 'not_modified'
            ctype = prev['content_type'] or ''
        else:
            body, ctype = resp.body, resp.content_type
            stored = archive.normalize(body, ctype)
            site_normalize = getattr(self.adapter.module, 'normalize', None)
            if callable(site_normalize):
                stored = site_normalize(stored)
            sha, rel = archive.store(self.data_dir, self.source.id, stored, ctype, full)
            changed = prev is None or prev['sha256'] != sha
            status = 'pending'
        db.update_fetch(self.conn, fetch_id, http_status=resp.status, content_type=ctype, bytes=len(body),
                        sha256=sha, raw_path=rel, etag=resp.headers.get('etag'),
                        last_modified=resp.headers.get('last-modified'), changed=int(changed), status=status)
        self.conn.commit()
        return Raw(url=full, body=body, content_type=ctype, fetch_id=fetch_id, sha256=sha, changed=changed,
                   retrieved_at=config.now_iso(), meta=dict(meta or {}))

    def _from_archive(self, prev, meta) -> Raw:
        body = archive.load(self.data_dir, prev['raw_path'])
        fid = db.insert_fetch(self.conn, run_id=self.run_id, source_id=self.source.id, url=prev['url'],
                              request_key=prev['request_key'], http_status=prev['http_status'],
                              content_type=prev['content_type'], bytes=prev['bytes'], sha256=prev['sha256'],
                              raw_path=prev['raw_path'], etag=prev['etag'], last_modified=prev['last_modified'],
                              changed=0, status='not_modified', meta=meta or {})
        self.conn.commit()
        return Raw(url=prev['url'], body=body, content_type=prev['content_type'] or '', fetch_id=fid,
                   sha256=prev['sha256'], changed=False, retrieved_at=config.now_iso(), meta=dict(meta or {}))


# ---------- validation ----------

def validate(adapter: Adapter, result: Result, raw: Raw, conn: sqlite3.Connection) -> None:
    metric_ids = {m.id for m in adapter.source.metrics}
    known_geos = {(g.geo_level, g.geo_code) for g in result.geos}
    keys = set()
    for o in result.observations:
        if o.metric_id not in metric_ids:
            raise ValidationError(f'undeclared metric {o.metric_id!r} (add it to SOURCE.metrics)')
        if o.status not in ('reported', 'not_reported', 'withheld'):
            raise ValidationError(f'bad status {o.status!r}')
        if o.status == 'reported' and o.value is None and not o.value_text:
            raise ValidationError(f'{o.metric_id} {o.period_start}: reported but no value')
        if o.status != 'reported' and o.value is not None:
            raise ValidationError(f'{o.metric_id} {o.period_start}: {o.status} must not carry a value')
        if not (_ISO.match(o.period_start) and _ISO.match(o.period_end)) or o.period_start > o.period_end:
            raise ValidationError(f'{o.metric_id}: bad period {o.period_start}..{o.period_end}')
        if (o.geo_level, o.geo_code) not in known_geos and not db.geo_exists(conn, o.geo_level, o.geo_code):
            raise ValidationError(f'unknown geography {o.geo_level}:{o.geo_code} (emit a Geo for it)')
        k = (o.metric_id, o.geo_level, o.geo_code, o.period_start, o.period_end, canonical_json(o.dims))
        if k in keys:
            raise ValidationError(f'duplicate observation key {k}')
        keys.add(k)
    rkeys = set()
    for r in result.records:
        if r.record_type not in adapter.source.record_types:
            raise ValidationError(f'undeclared record type {r.record_type!r} (add it to SOURCE.record_types)')
        if (r.record_type, r.record_key) in rkeys:
            raise ValidationError(f'duplicate record key {r.record_type}/{r.record_key}')
        rkeys.add((r.record_type, r.record_key))
    custom = getattr(adapter.module, 'validate', None)
    if callable(custom):
        custom(result, raw)


# ---------- running ----------

def is_due(conn: sqlite3.Connection, adapter: Adapter) -> bool:
    last = db.last_success_time(conn, adapter.id)
    if not last:
        return True
    fn = getattr(adapter.module, 'interval_hours', None)
    hours = fn(config.now()) if callable(fn) else adapter.source.interval_hours
    return config.now() - datetime.fromisoformat(last) >= timedelta(hours=max(0.0, hours - config.DUE_SLACK_HOURS))


def process_raw(conn: sqlite3.Connection, adapter: Adapter, raw: Raw) -> tuple[int, int]:
    """Parse, validate and apply one raw document inside a savepoint."""
    conn.execute('SAVEPOINT raw')
    try:
        result = adapter.module.parse(raw)
        validate(adapter, result, raw, conn)
        n_obs, n_rec = db.apply_result(conn, adapter.source, raw.fetch_id, result, adapter.parser)
        status = 'ok' if raw.changed else ('not_modified' if _status(conn, raw.fetch_id) == 'not_modified' else 'unchanged')
        db.update_fetch(conn, raw.fetch_id, status=status, parser=adapter.parser,
                        n_observations=n_obs, n_records=n_rec, error=None)
        conn.execute('RELEASE raw')
        return n_obs, n_rec
    except ValidationError as e:
        conn.execute('ROLLBACK TO raw')
        conn.execute('RELEASE raw')
        db.update_fetch(conn, raw.fetch_id, status='validation_error', parser=adapter.parser, error=str(e)[:2000])
        raise
    except Exception as e:
        conn.execute('ROLLBACK TO raw')
        conn.execute('RELEASE raw')
        tb = traceback.format_exc(limit=4)
        db.update_fetch(conn, raw.fetch_id, status='parse_error', parser=adapter.parser,
                        error=f'{type(e).__name__}: {e}\n{tb}'[:4000])
        raise


def _status(conn, fetch_id) -> str:
    row = conn.execute('SELECT status FROM fetch WHERE fetch_id=?', (fetch_id,)).fetchone()
    return row[0] if row else ''


def refresh(conn: sqlite3.Connection, adapters: Iterable[Adapter], *, due_only: bool = False,
            force: bool = False, data_dir: Path | None = None, fetcher: Fetcher | None = None,
            command: str = 'refresh') -> dict[str, str]:
    data_dir = data_dir or config.DATA_DIR
    fetcher = fetcher or Fetcher()
    run_id = db.begin_run(conn, command)
    outcome: dict[str, str] = {}
    for ad in adapters:
        db.register_source(conn, ad.source)
        conn.commit()
        if not ad.source.enabled:
            outcome[ad.id] = 'disabled'
            continue
        if due_only and not force and not is_due(conn, ad):
            outcome[ad.id] = 'not due'
            continue
        ctx = Context(conn, ad, run_id, fetcher, data_dir, force=force)
        n_raw = n_obs = n_rec = 0
        errors = []
        try:
            for raw in ad.module.fetch(ctx) or []:
                if raw is None:
                    continue
                n_raw += 1
                try:
                    o, r = process_raw(conn, ad, raw)
                    n_obs += o
                    n_rec += r
                except Exception as e:      # recorded on the fetch row; keep going with other documents
                    errors.append(f'{raw.url}: {type(e).__name__}: {e}')
                    log.error('[%s] %s: %s', ad.id, raw.url, e)
                conn.commit()
        except FetchError as e:
            errors.append(str(e))
            log.error('[%s] fetch failed: %s', ad.id, e)
        except Exception as e:
            errors.append(f'{type(e).__name__}: {e}')
            log.error('[%s] adapter crashed:\n%s', ad.id, traceback.format_exc())
            db.insert_fetch(conn, run_id=run_id, source_id=ad.id, url=ad.source.url, request_key='adapter',
                            status='parse_error', error=traceback.format_exc()[:4000])
        errors.extend(ctx.errors)          # soft failures from ctx.get(..., soft=True)
        conn.commit()
        if errors:
            outcome[ad.id] = f'error ({len(errors)}): ' + errors[0][:300]
        else:
            outcome[ad.id] = f'ok: {n_raw} document(s), {n_obs} observation(s), {n_rec} record(s)'
        log.info('[%s] %s', ad.id, outcome[ad.id])
    failed = [k for k, v in outcome.items() if v.startswith('error')]
    db.end_run(conn, run_id, 'ok' if not failed else ('failed' if len(failed) == len(outcome) else 'partial'))
    return outcome


def reparse(conn: sqlite3.Connection, adapters: Iterable[Adapter], data_dir: Path | None = None) -> dict[str, str]:
    """Re-run current parsers over the latest archived body of every request (no network)."""
    data_dir = data_dir or config.DATA_DIR
    run_id = db.begin_run(conn, 'reparse')
    outcome = {}
    for ad in adapters:
        db.register_source(conn, ad.source)
        rows = conn.execute(
            """SELECT f.* FROM fetch f JOIN (SELECT request_key, max(fetch_id) AS fid FROM fetch
                 WHERE source_id=? AND raw_path IS NOT NULL GROUP BY request_key) last ON last.fid = f.fetch_id
               ORDER BY f.fetch_id""", (ad.id,)).fetchall()
        ok = bad = 0
        for row in rows:
            import json as jsonlib
            body = archive.load(data_dir, row['raw_path'])
            fid = db.insert_fetch(conn, run_id=run_id, source_id=ad.id, url=row['url'], request_key=row['request_key'],
                                  http_status=row['http_status'], content_type=row['content_type'], bytes=row['bytes'],
                                  sha256=row['sha256'], raw_path=row['raw_path'], etag=row['etag'],
                                  last_modified=row['last_modified'], changed=1, meta=row['meta'],
                                  fetched_at=row['fetched_at'])
            raw = Raw(url=row['url'], body=body, content_type=row['content_type'] or '', fetch_id=fid,
                      sha256=row['sha256'], changed=True, retrieved_at=row['fetched_at'],
                      meta=jsonlib.loads(row['meta'] or '{}'))
            try:
                process_raw(conn, ad, raw)
                ok += 1
            except Exception as e:
                bad += 1
                log.error('[%s] reparse %s: %s', ad.id, row['url'], e)
            conn.commit()
        outcome[ad.id] = f'reparsed {ok} document(s)' + (f', {bad} failed' if bad else '')
    db.end_run(conn, run_id, 'ok' if all('failed' not in v for v in outcome.values()) else 'partial')
    return outcome
