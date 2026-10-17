"""Command line. Run from the pipeline/ folder:

    python3 -m opencity refresh             refresh every source that is due, then write data/export/
    python3 -m opencity refresh smc_swm     refresh the named sources now
    python3 -m opencity status              show how fresh each source is
"""
from __future__ import annotations

import logging
import sys

from . import db, export, runner
from .registry import discover


def _print_table(rows: list[dict]) -> None:
    if not rows:
        print('(no rows)')
        return
    cols = list(rows[0])
    width = {c: min(60, max(len(c), *(len(str('' if r[c] is None else r[c])) for r in rows))) for c in cols}
    print('  '.join(c.ljust(width[c]) for c in cols))
    for r in rows:
        print('  '.join(str('' if r[c] is None else r[c])[:60].ljust(width[c]) for c in cols))


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    command, names = (args[0], args[1:]) if args else ('', [])
    if command not in ('refresh', 'status') or (command == 'status' and names):
        print(__doc__)
        return 2
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s',
                        datefmt='%Y-%m-%dT%H:%M:%S')
    adapters = discover()
    unknown = [n for n in names if n not in adapters]
    if unknown:
        print(f'unknown source(s): {", ".join(unknown)}\nknown: {", ".join(adapters)}')
        return 2
    conn = db.connect()

    if command == 'refresh':
        chosen = [adapters[n] for n in names] if names else list(adapters.values())
        outcome = runner.refresh(conn, chosen, due_only=not names, command=' '.join(args))
        export.export(conn)
        _print_table([{'source': k, 'result': v} for k, v in outcome.items()])
        return 1 if any(v.startswith('error') for v in outcome.values()) else 0

    for ad in adapters.values():          # status: list every adapter, even ones that never ran
        db.register_source(conn, ad.source)
    conn.commit()
    _print_table([dict(r) for r in conn.execute(
        'SELECT source_id, cadence, last_success, last_status, n_observations AS obs, '
        'n_current_records AS records, latest_period, errors_last_run AS errors, '
        'substr(last_error, 1, 50) AS last_error FROM v_source_health ORDER BY source_id')])
    return 0
