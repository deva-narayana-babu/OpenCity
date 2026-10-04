"""Content-addressed archive of raw responses: DATA_DIR/raw/<source>/<sha[:2]>/<sha>.<ext>.gz

Each distinct body is stored once, so re-fetching an unchanged page costs no disk.
The archive is the audit trail: any number in the database can be traced to the
exact bytes it was parsed from, and `opencity reparse` rebuilds the database from it.
"""
from __future__ import annotations

import gzip
import hashlib
import os
import re
import tempfile
from pathlib import Path

from . import config

# Parts of HTML pages that change on every request without the data changing.
# They are blanked before hashing/archiving, so an unchanged page is recognised as
# unchanged and session tokens never land in the archive.
_VOLATILE = [
    # visitor counters (SMC site template: <div title="Website's Visitor Count">Visitor Count <span>79300522</span>)
    (re.compile(rb'(Visitor\s+Count\s*(?:<[^>]+>\s*)*)[\d,]+', re.I), rb'\1'),
    # ASP.NET state and anti-forgery tokens, in either attribute order
    (re.compile(rb'(<input[^>]*?name="(?:__RequestVerificationToken|__VIEWSTATE|__VIEWSTATEGENERATOR|'
                rb'__EVENTVALIDATION|__PREVIOUSPAGE)"[^>]*?value=")[^"]*(")', re.I), rb'\1\2'),
    (re.compile(rb'(<input[^>]*?value=")[^"]*("[^>]*?name="(?:__RequestVerificationToken|__VIEWSTATE|'
                rb'__VIEWSTATEGENERATOR|__EVENTVALIDATION|__PREVIOUSPAGE)")', re.I), rb'\1\2'),
    (re.compile(rb'(<meta[^>]*?name="csrf-token"[^>]*?content=")[^"]*(")', re.I), rb'\1\2'),
]


def normalize(body: bytes, content_type: str = '') -> bytes:
    """Blank volatile, non-data parts of HTML responses (counters, session/anti-forgery tokens)."""
    head = body[:2000].lower()
    if 'html' not in (content_type or '').lower() and b'<html' not in head and b'<!doctype' not in head:
        return body
    for pat, rep in _VOLATILE:
        body = pat.sub(rep, body)
    return body

_EXT = {
    'text/html': 'html', 'application/xhtml+xml': 'html', 'application/json': 'json', 'text/json': 'json',
    'application/pdf': 'pdf', 'text/csv': 'csv', 'application/xml': 'xml', 'text/xml': 'xml',
    'text/plain': 'txt',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
    'application/vnd.ms-excel': 'xls',
}


def sha256(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def guess_ext(content_type: str, url: str, body: bytes) -> str:
    if body[:4] == b'%PDF':
        return 'pdf'
    if body[:2] == b'PK':
        return 'xlsx' if url.lower().endswith('xlsx') or 'spreadsheet' in content_type else 'zip'
    ct = (content_type or '').split(';')[0].strip().lower()
    if ct in _EXT:
        return _EXT[ct]
    tail = url.split('?')[0].rsplit('.', 1)
    if len(tail) == 2 and 1 <= len(tail[1]) <= 5 and tail[1].isalnum():
        return tail[1].lower()
    head = body[:200].lstrip().lower()
    if head.startswith((b'{', b'[')):
        return 'json'
    if head.startswith((b'<!doctype html', b'<html')):
        return 'html'
    return 'bin'


def store(data_dir: Path, source_id: str, body: bytes, content_type: str, url: str) -> tuple[str, str]:
    """Store body if new. Returns (sha256, path relative to data_dir)."""
    digest = sha256(body)
    rel = Path(config.RAW_DIR_NAME) / source_id / digest[:2] / f'{digest}.{guess_ext(content_type, url, body)}.gz'
    path = data_dir / rel
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=path.parent, prefix='.tmp-')
        try:
            with os.fdopen(fd, 'wb') as fh, gzip.GzipFile(fileobj=fh, mode='wb', mtime=0) as gz:
                gz.write(body)
            os.replace(tmp, path)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
    return digest, str(rel)


def load(data_dir: Path, rel: str) -> bytes:
    with gzip.open(data_dir / rel, 'rb') as fh:
        return fh.read()
