"""Content-addressed archive of raw responses: DATA_DIR/raw/<source>/<sha[:2]>/<sha>.<ext>.gz

Each distinct body is stored once, so re-fetching an unchanged page costs no disk.
The archive is the audit trail: any number in the database can be traced to the
exact bytes it was parsed from, and runner.reparse() can rebuild the database from it.
"""
from __future__ import annotations

import gzip
import hashlib
import os
import tempfile
from pathlib import Path

from . import config

# Hidden form fields that carry per-session ASP.NET / anti-forgery tokens, not data.
TOKEN_FIELDS = ('__RequestVerificationToken', '__VIEWSTATE', '__VIEWSTATEGENERATOR', '__EVENTVALIDATION',
                '__PREVIOUSPAGE')


def blank_attribute(body: bytes, tag: bytes, must_contain: tuple[bytes, ...], attribute: bytes) -> bytes:
    """Empty one attribute in every tag that contains one of `must_contain`, e.g.
    blank_attribute(body, b'<input', (b'name="__VIEWSTATE"',), b'value')
      <input name="__VIEWSTATE" value="abc123"> -> <input name="__VIEWSTATE" value="">"""
    marker = b' ' + attribute + b'="'
    out, pos = [], 0
    while True:
        start = body.find(tag, pos)
        end = body.find(b'>', start) if start != -1 else -1
        if end == -1:
            break
        piece = body[start:end + 1]
        if any(m in piece for m in must_contain):
            i = piece.find(marker)
            j = piece.find(b'"', i + len(marker)) if i != -1 else -1
            if j != -1:
                piece = piece[:i + len(marker)] + piece[j:]
        out += [body[pos:start], piece]
        pos = end + 1
    out.append(body[pos:])
    return b''.join(out)


def blank_number_after(body: bytes, label: bytes) -> bytes:
    """Remove the number that follows `label`, skipping spaces and tags in between, e.g.
      'Visitor Count <span>79,300,522</span>' -> 'Visitor Count <span></span>'"""
    i = body.find(label)
    while i != -1:
        j = i + len(label)
        while j < len(body):
            if body[j:j + 1].isspace():
                j += 1
            elif body[j:j + 1] == b'<' and body.find(b'>', j) != -1:
                j = body.find(b'>', j) + 1
            else:
                break
        k = j
        while k < len(body) and body[k:k + 1] in b'0123456789,':
            k += 1
        body = body[:j] + body[k:]
        i = body.find(label, j)
    return body


def normalize(body: bytes, content_type: str = '') -> bytes:
    """Blank the parts of an HTML page that change on every request without the data changing
    (visitor counters, session/anti-forgery tokens). This runs before hashing and archiving, so an
    unchanged page is recognised as unchanged and session tokens never land in the archive."""
    head = body[:2000].lower()
    if 'html' not in (content_type or '').lower() and b'<html' not in head and b'<!doctype' not in head:
        return body
    body = blank_number_after(body, b'Visitor Count')
    fields = tuple(f'name="{f}"'.encode() for f in TOKEN_FIELDS)
    body = blank_attribute(body, b'<input', fields, b'value')
    body = blank_attribute(body, b'<meta', (b'name="csrf-token"',), b'content')
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
