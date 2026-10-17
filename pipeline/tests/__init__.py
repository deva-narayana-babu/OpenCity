"""Test helpers. Run from pipeline/:  python3 -m unittest discover -s tests -t . -v"""
from pathlib import Path

from opencity.model import Raw

PIPELINE = Path(__file__).resolve().parents[1]
REFERENCE = PIPELINE.parent / 'reference'          # frozen source snapshots used as fixtures
FIXTURES = Path(__file__).resolve().parent / 'fixtures'


def raw_from_file(path, url='file://fixture', meta=None, retrieved_at='2026-01-01T00:00:00+05:30') -> Raw:
    body = Path(path).read_bytes()
    return Raw(url=url, body=body, content_type='', fetch_id=0, sha256='', changed=True,
               retrieved_at=retrieved_at, meta=dict(meta or {}))
