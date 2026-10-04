# Writing a source adapter

One module per data source, named after its `SOURCE.id` (for example `smc_swm.py`). The registry finds it automatically, so you never edit another file to add one. [smc_swm.py](smc_swm.py) is the worked example.

```python
SOURCE = Source(id='smc_xyz', name=..., publisher=..., url=..., module=..., cadence=...,
                interval_hours=..., metrics=(Metric(...), ...), record_types=(...), geo_note=..., licence_note=...)

def fetch(ctx):            # network ONLY through ctx.get(...) / ctx.post(...); yield each Raw
    yield ctx.get(URL)

def parse(raw) -> Result:  # PURE: no network, no clock, same input -> same output
    ...

def validate(result, raw): # optional sanity checks; raise ValidationError to reject the whole document
    ...
```

Optional hooks:
- `interval_hours(now) -> float`: replaces `SOURCE.interval_hours`, e.g. checking rainfall every 2 h in the monsoon.
- `normalize(body: bytes) -> bytes`: blanks site-specific volatile bits before hashing. Visitor counters and ASP.NET tokens are already handled in `archive.normalize`.

## Rules

1. **Never fabricate.**
   - No interpolation, estimates or defaults.
   - A blank, "-" or "NA" cell becomes `Obs(..., value=None, status='not_reported')`, never 0.
   - If a page doesn't publish something, don't emit it.
2. **One geography per observation.** Use the geo level the source actually covers:

   | Geo level | Codes |
   |---|---|
   | `smc_city` | `smc` |
   | `smc_zone` | from `surat.zone_code()`, plus `surat.zone_geo()` |
   | `smc_ward` | the ward number as a string, e.g. `'12'` |
   | `surat_district` | `surat` |
   | `tapi_district` | `tapi` |
   | `apmc_market` | the market ID |
   | `dam` | a slug, e.g. `ukai` |
   | `reporting_centre` | a slug |
   | `state` | `gujarat` |

   Emit a `Geo` in `Result.geos` for every level/code that isn't one of the standard geos in `surat.py`. District-level data (NFHS, UDISE+) must never be labelled `smc_city`.
3. **Periods are ISO** (`YYYY-MM-DD`, or `YYYY-MM-DDTHH:MM` local time for readings).
   - A monthly value covers the first to the last day of the month (`parse.month_period`).
   - Financial years run 1 April to 31 March (`parse.fy_period`).
   - An instant reading has the same start and end.
   - A "24:00" timestamp means 00:00 the next day (`parse.parse_dt` handles it).
4. **Use `dims` for breakdowns,** e.g. `{'mode': 'truck'}` or `{'commodity': 'Onion', 'variety': 'Red'}`. Keep the dims keys stable; together with metric, geo and period they form the primary key, and duplicates are rejected.
5. **Declare every metric** in `SOURCE.metrics` and every record type in `SOURCE.record_types`. Metric ids are dotted and lowercase: `<area>.<thing>[.<qualifier>]`.
6. **Records are for non-numeric entities** (corporators, PIOs, documents).
   - `record_key` must stay stable across fetches (e.g. `ward-12-seat-A`).
   - If the page is the full list, set `Result.complete_record_types=('corporator',)` so that people who disappear from it get closed.
   - Store only what the authority publishes for the role: designation, official contact, ward. Never store residential addresses or personal phone numbers.
7. **Fail loudly.** `parse.num()` raises on non-numeric text. Let it raise, or catch it and raise `ValidationError` with a clear message, rather than guessing.
8. **`validate()` should check:** that the row count is plausible, that values fall in plausible ranges, and that the latest period isn't absurd. The runner already checks metric/record declarations, statuses, ISO periods, known geographies and duplicate keys.
9. **Be polite.**
   - Only fetch what you parse.
   - For immutable documents (a PDF for a past year), pass `skip_if_seen=True` so they're downloaded once.
   - Don't add request headers that pretend to be a browser, and never try to get around captchas, logins or blocks.
   - If a source needs an API key, read it from an environment variable, and make `fetch()` log and return nothing when the key is missing.
10. **Tests.** Add `pipeline/tests/test_<id>.py` (stdlib `unittest`). It should parse the frozen snapshot in `reference/` (or a small fixture in `pipeline/tests/fixtures/<id>/`) and assert counts and a few exact values read off the document.

## Conventions learned while building the first adapters

- **Metric ids belong to one source.** `metric_id` is global and the observation key doesn't include the source. If two sources report the same concept (e.g. Ukai level from SMC's flood page and from the WRD bulletin), give each its own id (`flood.dam_level_ft`, `wrd.dam_level_m`) and reconcile them in the dashboard. Never reuse another adapter's metric id. `test_framework` enforces this.
- **Geo levels in use:**
  - `smc_city`, `smc_zone`, `smc_ward`
  - `surat_district`, `tapi_district`, `state`
  - `dam`, `weir`, `creek`
  - `apmc_market`, `reporting_centre`, `aq_station`
  - `facility` (e.g. SMIMER hospital)
  - `court_establishment`

  Add a new level only when none of these fits, and document it in your module docstring.
- **Ward names:** use `smc_council.WARDS_2026` for `smc_ward` geos so names don't flip between adapters, because `geo.name` is overwritten by whichever adapter writes last.
- **Agmarknet:** its market lists file Tapi-district markets under "Surat". Reuse `agmarknet_surat.TAPI_MARKETS` for the exclusion list.
- **SMC "Last Updated" is not a data date.** On some SMC pages it is just the server render time. Only use it as `publisher_as_of` after checking that it changes with the data.
- **`parse()` sees two versions of the body.**
  - On a live fetch, `raw.body` is the original response.
  - On `reparse`, it is the archived copy, with visitor counters and ASP.NET tokens blanked.
  - Parse only the data, so both give the same result. `fetch()` may read tokens from the live body, e.g. `__VIEWSTATE` for a postback.
- **`reparse` does not replay the request body.** For a POST, put everything `parse()` needs (date, ids) in `meta` or read it from the response.
- **Multi-document sources:**
  - Use `ctx.get(url, soft=True)` so that one missing page records an error and the other documents still load; the run is still reported as failed.
  - When several documents publish the same key (each balance sheet repeats the previous year), the one processed last wins. Yield documents oldest first, so the latest publication is authoritative.
- **Immutable documents:** with `skip_if_seen=True`, a document already parsed by the current parser version is skipped. After you bump `parser_version`, it is reparsed from the archive without being downloaded again.
- **Tests:** `raw_from_file(path, retrieved_at=...)` lets `validate()` checks like "report date not after the fetch time" pass against frozen files.

## Handy helpers (`opencity.parse`)

| Helper | What it does |
|---|---|
| `html_tables(body)` | Returns `Table` objects with `.rows`. Colspan and rowspan are expanded. `.heading` is the nearby text before the table, and `.links` gives the hrefs per cell. |
| `links(body, base)` | All `<a href>` links. |
| `html_text(body)` | The visible text. |
| `pdf_text(body, layout=True)` | Text via pdftotext. |
| `num(s)` | Number parsing; handles Indian digit grouping, Gujarati digits, `-`/NA and `(neg)`. `num_or_none(s)` is the non-raising version. |
| `month_year('July-2026')`, `month_period(y, m)` | Month labels and periods. |
| `fy_start('2025-26')`, `fy_period(y)`, `quarter_of_fy(y, q)` | Financial years and quarters. |
| `parse_date(s)`, `parse_dt(s)` | Dates and datetimes. |

## Trying it

```bash
cd pipeline
python3 -m opencity parse-file smc_xyz ../reference/<path>       # parse a saved file and print the observations
OPENCITY_DATA_DIR=/tmp/oc OPENCITY_DB=/tmp/oc/t.db python3 -m opencity refresh -s smc_xyz   # live run into a scratch DB
python3 -m unittest tests.test_smc_xyz -v
```
