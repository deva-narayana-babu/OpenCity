"""Plain data types shared by the runner and the source adapters."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Callable, Optional

STATUSES = ('reported', 'not_reported', 'withheld')


def canonical_json(d: dict | None) -> str:
    """Stable JSON used for observation dims and record attributes (sorted keys, no spaces)."""
    if not d:
        return '{}'
    return json.dumps(d, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


@dataclass(frozen=True)
class Metric:
    id: str                 # dotted id, e.g. "swm.d2d.avg_collection_mt_per_day"
    label: str
    unit: str = ''
    description: str = ''


@dataclass(frozen=True)
class Source:
    id: str                 # snake_case, matches the module name in opencity/sources/
    name: str
    publisher: str
    url: str                # human-facing page for the dataset
    module: str             # dashboard module: finance, health, environment, water, council, rti, food, education, transport, housing
    cadence: str            # daily | weekly | monthly | quarterly | annual | static | 2-hourly
    interval_hours: float   # minimum hours between refreshes when running with --due
    metrics: tuple[Metric, ...] = ()
    record_types: tuple[str, ...] = ()
    geo_note: str = ''      # which geography the data covers (SMC city, Surat district, ...)
    licence_note: str = ''
    notes: str = ''
    parser_version: str = '1'
    enabled: bool = True


@dataclass
class Raw:
    """One fetched document, archived and recorded in the fetch table."""
    url: str
    body: bytes
    content_type: str
    fetch_id: int
    sha256: str
    changed: bool           # content differs from the previous fetch of the same request
    retrieved_at: str       # ISO timestamp (Asia/Kolkata)
    meta: dict = field(default_factory=dict)   # adapter-supplied context (e.g. fiscal year from a link label)

    @property
    def text(self) -> str:
        return self.body.decode('utf-8', errors='replace')


@dataclass
class Obs:
    metric_id: str
    geo_level: str
    geo_code: str
    period_start: str       # ISO date or datetime (local time, Asia/Kolkata)
    period_end: str
    value: Optional[float] = None
    value_text: Optional[str] = None
    status: str = 'reported'
    dims: dict = field(default_factory=dict)
    publisher_as_of: Optional[str] = None


@dataclass
class Record:
    """A non-numeric entity (a corporator, a PIO, a document) tracked with validity history."""
    record_type: str
    record_key: str
    attrs: dict


@dataclass
class Geo:
    geo_level: str
    geo_code: str
    name: str
    parent_level: Optional[str] = None
    parent_code: Optional[str] = None
    note: Optional[str] = None


@dataclass
class Result:
    observations: list[Obs] = field(default_factory=list)
    records: list[Record] = field(default_factory=list)
    geos: list[Geo] = field(default_factory=list)
    # record types for which this result is the COMPLETE current list: keys missing from it get closed
    complete_record_types: tuple[str, ...] = ()

    def extend(self, other: 'Result') -> 'Result':
        self.observations += other.observations
        self.records += other.records
        self.geos += other.geos
        self.complete_record_types = tuple(sorted(set(self.complete_record_types) | set(other.complete_record_types)))
        return self


class FetchError(Exception):
    def __init__(self, msg: str, *, http_status: int | None = None, blocked: bool = False):
        super().__init__(msg)
        self.http_status = http_status
        self.blocked = blocked


class ValidationError(Exception):
    pass


Validator = Callable[[Result, Raw], None]
