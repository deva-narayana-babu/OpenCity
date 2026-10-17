# OpenCity data pipeline (Surat)

This folder holds a SQLite database of Surat civic data and the refresher that keeps it current. It uses only the Python 3.9+ standard library plus `pdftotext` (from poppler-utils), so there is nothing to `pip install`.

```
scripts/refresh.sh            fetch whatever is due -> update data/opencity.db -> write data/export/*.csv
scripts/db.sh                 is every source fresh? what failed?
scripts/install-schedule.sh   run the refresher hourly with cron
```

## Quick start

```bash
sudo apt install poppler-utils          # pdftotext, needed for PDF sources
scripts/refresh.sh                      # first run loads every source (a few minutes; polite 2 s gap per host)
scripts/refresh.sh smc_swm              # refresh one source now
scripts/db.sh                           # one line per source: last success, rows, latest period, last error
scripts/install-schedule.sh             # hourly cron entry; each source decides if it is due
```

## How a refresh works

```
fetch (polite HTTP) -> archive raw bytes -> parse -> validate -> upsert -> export CSV
```

1. **Fetch.** Each source adapter in `opencity/sources/` fetches only through `ctx.get`/`ctx.post`.
   - The client identifies itself honestly (`OPENCITY_CONTACT`) and waits 2 s between requests to the same host.
   - It retries 5xx and network errors, and uses conditional GET.
   - It stops on 403/429: we don't work around blocks or captchas.
2. **Archive.** Every response is saved once, gzipped, under `data/raw/<source>/` and named by its sha256.
   - Visitor counters and ASP.NET session tokens are blanked first, so an unchanged page is recognised as unchanged and no tokens are stored.
   - `runner.reparse()` can rebuild the whole database from this archive without touching the network.
3. **Parse.** `parse()` is pure: the same bytes always give the same rows. Tests run it against the frozen snapshots in `../reference/`.
4. **Validate.**
   - The runner rejects a whole document rather than storing anything doubtful: undeclared metrics, unknown geographies, non-ISO periods, duplicate keys, or a "reported" value with no number.
   - Each source can add plausibility checks of its own.
5. **Upsert.**
   - Re-fetching the same number changes nothing but `last_seen`.
   - If a publisher revises a number, the old value goes to `observation_revision`.
   - Entities such as corporators keep validity history: `valid_from`/`valid_to`.
6. **Export.** `data/export/` holds CSVs with stable ordering, rewritten only when they change, so git diffs show real data changes.

A failure in one source never stops the others. The exit code is non-zero if anything failed; `scripts/db.sh` shows the last error per source and the `fetch` table has the full history.

## Database

`opencity/schema.sql` is the source of truth for the schema. The main tables:

| Table | What it holds |
|---|---|
| `source` | One row per adapter: publisher, URL, cadence, refresh interval, geographic coverage, licence note |
| `fetch` | Every request: URL, status, HTTP code, sha256, archived file, parser version, error |
| `metric` | The metric catalogue: id, label, unit, module |
| `geo` | Places: `smc_city`, `smc_zone`, `smc_ward`, `surat_district`, `tapi_district`, `dam`, `apmc_market`, ... |
| `observation` | Tidy numbers: metric x place x period x `dims` -> value or `not_reported` |
| `observation_revision` | Values that a publisher later changed |
| `record` | Non-numeric entities (corporators, projects, documents) with validity history |

Views:

| View | What it shows |
|---|---|
| `v_observation` | Observations joined with their metric, place, publisher, source URL, retrieval time and raw sha256 |
| `v_current_record` | The current version of every record |
| `v_source_health` | Freshness per source |

Conventions:

- **Periods** are ISO dates in Asia/Kolkata local time.
  - A month runs from its first to its last day.
  - A financial year runs from 1 April to 31 March.
  - A reading at an instant has the same start and end (`2026-09-28T00:00`).
- **Missing data** is `status='not_reported'` with a NULL value, never 0.
- **Geography matters.** District-level data (NFHS-5, UDISE+) is `surat_district`, not the city. Ukai dam is in Tapi district.

## Sources

Run `scripts/db.sh` for the list of sources and see `data/export/catalog/` for the full metric catalogue. Each adapter's module docstring explains the page, its quirks and what every metric means. To add a source, read [opencity/sources/README.md](opencity/sources/README.md).

## Tests

```bash
cd pipeline && python3 -m unittest discover -s tests -t . -v
```

The tests use no network. Framework tests cover parsing helpers, archive normalisation, revisions, history and runner behaviour. Each adapter's tests assert exact values read off a frozen source document.

## Configuration (environment variables)

| Variable | Default | Meaning |
|---|---|---|
| `OPENCITY_DATA_DIR` | `data/` | Database, raw archive, logs |
| `OPENCITY_DB` | `data/opencity.db` | Database file |
| `OPENCITY_EXPORT_DIR` | `data/export/` | CSV exports |
| `OPENCITY_CONTACT` | repo URL | Contact put in the User-Agent; set it to a team email |
| `OPENCITY_HOST_DELAY` | `2.0` | Seconds between requests to one host |
| `DATA_GOV_IN_API_KEY` | (unset) | Only for sources that use the data.gov.in API |

## What goes in git

`data/export/` (CSV) is meant to be committed. The database, the raw archive and the logs are git-ignored: they're large, binary or regenerable. A new teammate runs `scripts/refresh.sh` to build their own copy.
