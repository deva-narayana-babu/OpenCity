"""Polite HTTP client (standard library only).

- identifies itself with config.USER_AGENT
- waits config.HOST_MIN_DELAY seconds between requests to the same host
- retries network errors and 5xx with backoff; never retries 4xx
- stops on 403/429 (FetchError(blocked=True)): we do not try to get around blocks
- supports conditional GET (ETag / Last-Modified) and gzip
"""
from __future__ import annotations

import gzip
import json as jsonlib
import logging
import socket
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
import zlib
from dataclasses import dataclass, field

from . import config
from .model import FetchError

log = logging.getLogger(__name__)


@dataclass
class Response:
    status: int
    body: bytes
    url: str
    headers: dict = field(default_factory=dict)

    @property
    def content_type(self) -> str:
        return self.headers.get('content-type', '')


class Fetcher:
    def __init__(self, user_agent: str | None = None, min_delay: float | None = None,
                 timeout: float | None = None, retries: int | None = None):
        self.user_agent = user_agent or config.USER_AGENT
        self.min_delay = config.HOST_MIN_DELAY if min_delay is None else min_delay
        self.timeout = timeout or config.TIMEOUT
        self.retries = config.RETRIES if retries is None else retries
        self._last: dict[str, float] = {}
        self._ssl = ssl.create_default_context()

    def _throttle(self, host: str) -> None:
        last = self._last.get(host)
        if last is not None:
            wait = self.min_delay - (time.monotonic() - last)
            if wait > 0:
                time.sleep(wait)
        self._last[host] = time.monotonic()

    def request(self, method: str, url: str, *, params: dict | None = None, data: bytes | None = None,
                json: object = None, form: dict | None = None, headers: dict | None = None,
                etag: str | None = None, last_modified: str | None = None) -> Response:
        if params:
            url = url + ('&' if '?' in url else '?') + urllib.parse.urlencode(params)
        hdrs = {'User-Agent': self.user_agent, 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*'}
        if json is not None:
            data = jsonlib.dumps(json).encode()
            hdrs['Content-Type'] = 'application/json'
        elif form is not None:
            data = urllib.parse.urlencode(form).encode()
            hdrs['Content-Type'] = 'application/x-www-form-urlencoded'
        if etag:
            hdrs['If-None-Match'] = etag
        if last_modified:
            hdrs['If-Modified-Since'] = last_modified
        hdrs.update(headers or {})
        host = urllib.parse.urlsplit(url).hostname or ''

        attempt = 0
        while True:
            attempt += 1
            self._throttle(host)
            req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
            try:
                with urllib.request.urlopen(req, timeout=self.timeout, context=self._ssl) as r:
                    body = r.read()
                    h = {k.lower(): v for k, v in r.headers.items()}
                    return Response(r.status, _decode(body, h), r.geturl(), h)
            except urllib.error.HTTPError as e:
                h = {k.lower(): v for k, v in (e.headers or {}).items()}
                if e.code == 304:
                    return Response(304, b'', url, h)
                if e.code in (403, 429):
                    raise FetchError(f'HTTP {e.code} from {host}: blocked or rate-limited; not retrying',
                                     http_status=e.code, blocked=True) from None
                if e.code >= 500 and attempt <= self.retries:
                    self._backoff(attempt, f'HTTP {e.code}', url)
                    continue
                raise FetchError(f'HTTP {e.code} for {url}', http_status=e.code) from None
            except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError, ssl.SSLError) as e:
                if attempt <= self.retries:
                    self._backoff(attempt, repr(e), url)
                    continue
                raise FetchError(f'network error for {url}: {e!r}') from None

    def _backoff(self, attempt: int, why: str, url: str) -> None:
        delay = min(60, 5 * 2 ** (attempt - 1))
        log.warning('retry %d for %s after %s (sleep %ds)', attempt, url, why, delay)
        time.sleep(delay)


def _decode(body: bytes, headers: dict) -> bytes:
    enc = headers.get('content-encoding', '').lower()
    try:
        if enc == 'gzip' or body[:2] == b'\x1f\x8b':
            return gzip.decompress(body)
        if enc == 'deflate':
            return zlib.decompress(body)
    except (OSError, zlib.error):
        pass
    return body
