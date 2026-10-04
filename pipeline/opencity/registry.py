"""Discovers source adapters: every module in opencity/sources/ that defines SOURCE, fetch() and parse().

Adapter contract (see sources/README.md):
    SOURCE = Source(id=<module name>, ...)
    def fetch(ctx) -> Iterable[Raw]          # network only through ctx.get / ctx.post
    def parse(raw: Raw) -> Result            # pure: no network, no clock, deterministic
    def validate(result, raw) -> None        # optional; raise ValidationError
    def interval_hours(now) -> float         # optional; overrides SOURCE.interval_hours (e.g. monsoon)
"""
from __future__ import annotations

import importlib
import pkgutil
from dataclasses import dataclass
from types import ModuleType

from . import sources as _sources_pkg
from .model import Source


@dataclass
class Adapter:
    source: Source
    module: ModuleType

    @property
    def id(self) -> str:
        return self.source.id

    @property
    def parser(self) -> str:
        return f'{self.source.id}@{self.source.parser_version}'


def discover() -> dict[str, Adapter]:
    out: dict[str, Adapter] = {}
    for info in sorted(pkgutil.iter_modules(_sources_pkg.__path__), key=lambda i: i.name):
        if info.name.startswith('_'):
            continue
        mod = importlib.import_module(f'{_sources_pkg.__name__}.{info.name}')
        src = getattr(mod, 'SOURCE', None)
        if src is None:
            continue
        for fn in ('fetch', 'parse'):
            if not callable(getattr(mod, fn, None)):
                raise TypeError(f'adapter {info.name} is missing {fn}()')
        if src.id != info.name:
            raise ValueError(f'adapter module {info.name} declares SOURCE.id={src.id!r}; they must match')
        out[src.id] = Adapter(src, mod)
    return out
