"""SMC "Rainfall Statistics" page: Ukai dam, Tapi weir-cum-causeway, zone-wise rain and creek levels.

Page: https://www.suratmunicipal.gov.in/Home/RainfallInfo
Server-rendered HTML with five Bootstrap tab panes, each holding one table of the
most recent readings (newest first, about 10 rows):

  #UkaiDam          Date/Time | Level (ft) | Est. Inflow (cusec) | Est. Outflow (cusec)      2-hourly
                    text: "Ukai Full Reservoir Level - 345 ft", "Last Updated on 28-09-2026 02:12:37 AM",
                    "*Source-Irrigation Dept/Collector Office"
                    "Last Updated on" is the server's render time, NOT a data timestamp: two
                    fetches 37 s apart on 2026-10-04 differed only in it (12:37:56 vs 12:38:33 AM,
                    each ~2 s after the request). It is therefore not stored as publisher_as_of,
                    and normalize() blanks it so unchanged data hashes the same.
  #Causeway         Date/Time | Level (mt) | Est. Outflow (cusec)                            2-hourly
  ("Weir-Cum-       text: "Causeway overflow at 6.0 mt.", "Causeway is OPEN"
   Causeway" tab)
  #RainFall         Date/Time | Central Zone (mm) | West Zone (mm) | ... | South East Zone (mm) 2-hourly
                    (eight zones, still with a single "South Zone")
  #TotalRainFall    Date/Time | Total Rainfall (mm)                                          2-hourly
  #KhadiWaterLevel  Date/Time | Kakara Khadi Udhana Zone (D.L.- 8.48 MT) | ...                hourly

Timestamps look like "27/09/2026 24:00" (= 28/09/2026 00:00). Every reading is an
instant, so period_start == period_end == the ISO local datetime.

What the figures mean, as far as the page tells us:
- Zone rainfall is NOT cumulative over the season: on 27/09/2026 every zone showed
  0.00 mm in every slot while the "Total Rain Fall" tab stayed at 1983.00 mm. The page
  does not say whether a zone figure is the rain of the preceding 2-hour slot or a
  running total for the day, so the metric description says exactly that.
- "Total Rainfall (mm)" is a running city total (1983.00 mm in every slot of the dry
  days 27/09 and 03-04/10/2026); the page does not state when the accumulation starts
  or whether it is one gauge or an average of zones.
- Thresholds printed next to the readings (Ukai FRL, the causeway overflow level and
  each creek's danger level "D.L.") are stored as their own metrics, dated to the day of
  the latest reading they were shown with.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta

from ..model import Geo, Metric, Obs, Raw, Result, Source, ValidationError
from ..parse import clean, html_tables, html_text, num, parse_dt
from ..surat import SMC, TAPI_DISTRICT, ZONES, zone_code, zone_geo

URL = 'https://www.suratmunicipal.gov.in/Home/RainfallInfo'

UKAI = Geo('dam', 'ukai', 'Ukai dam (Tapi river)', 'tapi_district', 'tapi',
           note='Ukai dam and reservoir on the Tapi river, physically in Tapi district (Songadh taluka). '
                'Readings come from the SMC Rainfall Statistics page, which credits the Irrigation '
                'Department / Collector Office.')
WEIR = Geo('weir', 'surat_weir_causeway', 'Weir-cum-causeway on the Tapi river, Surat', 'smc_city', 'smc',
           note='The "Weir-Cum-Causeway" tab of the SMC Rainfall Statistics page. The page does not name its '
                'location; it is taken to be the Tapi weir-cum-causeway between Rander and Singanpor in '
                'Surat city (identification from general knowledge, not stated on the page). '
                'SMC states the causeway overflows at 6.0 m.')

SOURCE = Source(
    id='smc_rainfall',
    name='SMC rainfall statistics: Ukai dam, weir-cum-causeway, zone-wise rainfall and creek levels',
    publisher='Surat Municipal Corporation (Ukai and weir figures credited on the page to the '
              'Irrigation Department / Collector Office)',
    url=URL,
    module='water',
    cadence='2-hourly',
    interval_hours=24,      # overridden by interval_hours(now): every 2 h from June to October
    geo_note='Ukai dam (dam:ukai, in Tapi district); Tapi weir-cum-causeway in Surat (weir); SMC zones '
             '(smc_zone, 8 zones incl. a single South Zone); SMC city total (smc_city); creek (khadi) '
             'gauges in Surat city (creek).',
    licence_note='Surat Municipal Corporation web page; public information',
    notes='The page only shows the latest ~10 readings of each table (about 20 h of 2-hourly readings, '
          '10 h of hourly creek readings). Refreshing every 2 h in June-October captures every reading; '
          'the daily refresh outside the monsoon leaves gaps. Zone rainfall per slot vs running daily '
          'total is not stated on the page (see metric description).',
    metrics=(
        Metric('flood.dam_level_ft', 'Ukai reservoir level', 'ft',
               'Water level of the Ukai reservoir in feet, column "Level (ft)" of the Ukai Dam tab '
               '(2-hourly readings). The page states the Full Reservoir Level is 345 ft.'),
        Metric('flood.dam_inflow_cusec', 'Ukai estimated inflow', 'cusec',
               'Column "Est. Inflow (cusec)" of the Ukai Dam tab: estimated inflow into the reservoir '
               'at the reading time, cubic feet per second, as published. Observed pattern (27/09 and '
               '03-04/10/2026): it equals the outflow in slots where the level is unchanged and reads 0.00 '
               'in every slot where the level fell, so it looks like a storage-balance estimate floored at '
               'zero; a 0 here is not a measured zero river flow.'),
        Metric('flood.dam_outflow_cusec', 'Ukai estimated outflow', 'cusec',
               'Column "Est. Outflow (cusec)" of the Ukai Dam tab: estimated release from the dam at the '
               'reading time, cubic feet per second, as published.'),
        Metric('flood.dam_frl_ft', 'Ukai full reservoir level (as published)', 'ft',
               'The "Ukai Full Reservoir Level - N ft" figure printed above the Ukai table. Dated to the day '
               'of the latest Ukai reading it was shown with.'),
        Metric('flood.weir_level_m', 'Weir-cum-causeway water level', 'm',
               'Column "Level (mt)" of the Weir-Cum-Causeway tab: water level at the Tapi weir-cum-causeway '
               'in Surat, metres as published (the page does not state the datum).'),
        Metric('flood.weir_outflow_cusec', 'Weir-cum-causeway estimated outflow', 'cusec',
               'Column "Est. Outflow (cusec)" of the Weir-Cum-Causeway tab, cubic feet per second.'),
        Metric('flood.causeway_overflow_level_m', 'Causeway overflow level (as published)', 'm',
               'The "Causeway overflow at N mt." figure under the weir table: the level at which water '
               'overtops the causeway. Dated to the day of the latest weir reading it was shown with.'),
        Metric('flood.causeway_status', 'Causeway status (as published)', '',
               'Text after "Causeway is" under the weir table (e.g. OPEN), stored in value_text. Stored at '
               'the instant of the latest weir reading shown with it; the page gives no separate time.'),
        Metric('rain.smc_zone_mm', 'Zone-wise rainfall', 'mm',
               'Rainfall in the SMC zone for the slot ending at the reading time, from the Zonewise Rain Fall '
               'tab (2-hourly timestamps). Not cumulative over the season (all zones read 0.00 on 27/09/2026 '
               'while the season total was 1983 mm). The page does not say whether each figure is the rain '
               'of the preceding 2-hour slot or a running total for the day.'),
        Metric('rain.smc_total_mm', 'Total rainfall, Surat city (cumulative)', 'mm',
               'Column "Total Rainfall (mm)" of the Total Rain Fall tab: cumulative rainfall for Surat city '
               'up to the reading time. The page does not state the start of the accumulation period '
               '(the monsoon season) or whether it is one gauge or an average of zones.'),
        Metric('flood.creek_level_m', 'Creek (khadi) water level', 'm',
               'Water level at an SMC creek (khadi) gauge, Khadi Water Level tab (hourly readings), metres '
               'as published ("MT").'),
        Metric('flood.creek_danger_level_m', 'Creek (khadi) danger level (as published)', 'm',
               'Danger level "D.L." printed in the creek column header, e.g. "(D.L.- 8.48 MT)". Dated to the '
               'day of the latest creek reading it was shown with.'),
    ),
)

_PANE = re.compile(r'<div\b[^>]*\brole\s*=\s*["\']tabpanel["\'][^>]*>', re.I)
_ID = re.compile(r'\bid\s*=\s*["\']([^"\']+)["\']', re.I)


def interval_hours(now: datetime) -> float:
    """Readings change every 2 h; that matters during the monsoon (June to October)."""
    return 2.0 if 6 <= now.month <= 10 else 24.0


def fetch(ctx):
    yield ctx.get(URL)


_LAST_UPDATED = re.compile(rb'(Last Updated on\s*(?:<[^>]*>\s*)*)\d{1,2}-\d{1,2}-\d{4}\s+\d{1,2}:\d{2}(?::\d{2})?\s*[AP]M', re.I)


def normalize(body: bytes) -> bytes:
    """Blank the "Last Updated on <server time>" stamp, which changes on every request."""
    return _LAST_UPDATED.sub(rb'\1', body)


# ---------- parsing ----------

def _panes(html: str) -> list[tuple[str, str]]:
    """(pane id, pane html) for each Bootstrap tab pane, in page order."""
    marks = []
    for m in _PANE.finditer(html):
        idm = _ID.search(m.group(0))
        marks.append((m.start(), idm.group(1) if idm else ''))
    if not marks:
        raise ValueError('no tab panes (role="tabpanel") found: page layout changed')
    out = []
    for i, (pos, pid) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(html)
        out.append((pid, html[pos:end]))
    return out


def _kind(header: list[str]) -> str | None:
    h = ' | '.join(header).lower()
    if not header or not header[0].lower().startswith('date'):
        return None
    if 'khadi' in h:
        return 'creek'
    if 'total rainfall' in h:
        return 'total'
    if re.search(r'level\s*\((ft|feet)\)', h):
        return 'dam'
    if re.search(r'level\s*\((mt|m|mtr|metre|meter)s?\)', h):
        return 'weir'
    if 'zone' in h and '(mm)' in h:
        return 'zone'
    return None


def _rows(table) -> list[tuple[str, list[str]]]:
    """(ISO datetime, value cells) for each data row, with duplicate timestamps resolved.
    Identical duplicates collapse to one; conflicting duplicates raise."""
    seen: dict[str, list[str]] = {}
    out = []
    for row in table.rows[1:]:
        if not row or not row[0].strip():
            continue
        if row[0].strip().lower().startswith('date'):
            continue
        when = parse_dt(clean(row[0]))
        cells = [clean(c) for c in row[1:]]
        if when in seen:
            if seen[when] != cells:
                raise ValueError(f'conflicting rows for {when}: {seen[when]} vs {cells}')
            continue
        seen[when] = cells
        out.append((when, cells))
    return out


def _obs(metric, level, code, when, cell, **kw) -> Obs:
    v = num(cell)
    return Obs(metric, level, code, when, when, value=v, status='reported' if v is not None else 'not_reported', **kw)


def _cell(cells: list[str], j: int) -> str:
    # j is a column index of the header; cells excludes the date column
    return cells[j - 1] if 0 < j <= len(cells) else ''


def _slug(s: str) -> str:
    return re.sub(r'[^a-z0-9]+', '_', s.lower()).strip('_')


def _creek_column(h: str) -> tuple[str, str, str, float | None]:
    """'Kakara Khadi Udhana Zone(D.L.- 8.48 MT)' -> (code, name, zone label, danger level)."""
    dl = None
    m = re.search(r'\(\s*D\.?\s*L\.?\s*[-:]?\s*([\d.]+)\s*(?:mt|m|mtr|metre|meter)s?\.?\s*\)', h, re.I)
    if m:
        dl = num(m.group(1))
        h = (h[:m.start()] + h[m.end():]).strip()
    m = re.match(r'\s*(.*?\bkhadi)\b\s*(.*?)\s*$', h, re.I)
    if not m:
        raise ValueError(f'unrecognised creek column header {h!r}')
    creek, zone_label = clean(m.group(1)), clean(m.group(2))
    place = re.sub(r'\bzone\b', '', zone_label, flags=re.I).strip()
    code = _slug(f'{creek} {place}')
    return code, creek, zone_label, dl


def parse(raw: Raw) -> Result:
    html = raw.body.decode('utf-8', errors='replace') if isinstance(raw.body, bytes) else raw.body
    res = Result(geos=[SMC, TAPI_DISTRICT, UKAI, WEIR])
    found: dict[str, str] = {}
    for pid, pane in _panes(html):
        text = html_text(pane)
        for table in html_tables(pane):
            if not table.rows:
                continue
            kind = _kind(table.rows[0])
            if kind is None:
                continue
            if kind in found:
                raise ValueError(f'two {kind} tables (panes {found[kind]!r} and {pid!r}): page layout changed')
            found[kind] = pid
            rows = _rows(table)
            if not rows:
                continue
            latest = max(w for w, _ in rows)
            header = table.rows[0]
            if kind == 'dam':
                cols = {}
                for j, h in enumerate(header):
                    hl = h.lower()
                    if re.search(r'level\s*\((ft|feet)\)', hl):
                        cols[j] = 'flood.dam_level_ft'
                    elif 'inflow' in hl:
                        cols[j] = 'flood.dam_inflow_cusec'
                    elif 'outflow' in hl:
                        cols[j] = 'flood.dam_outflow_cusec'
                for when, cells in rows:
                    for j, metric in cols.items():
                        res.observations.append(_obs(metric, 'dam', 'ukai', when, _cell(cells, j)))
                fm = re.search(r'Full Reservoir Level\s*[-:]?\s*([\d.]+)\s*(?:ft|feet)', text, re.I)
                if fm:
                    day = latest[:10]
                    res.observations.append(Obs('flood.dam_frl_ft', 'dam', 'ukai', day, day, value=num(fm.group(1))))
            elif kind == 'weir':
                cols = {}
                for j, h in enumerate(header):
                    hl = h.lower()
                    if 'level' in hl:
                        cols[j] = 'flood.weir_level_m'
                    elif 'outflow' in hl:
                        cols[j] = 'flood.weir_outflow_cusec'
                for when, cells in rows:
                    for j, metric in cols.items():
                        res.observations.append(_obs(metric, WEIR.geo_level, WEIR.geo_code, when, _cell(cells, j)))
                om = re.search(r'Causeway overflow at\s*([\d.]+)\s*(?:mt|m)\b', text, re.I)
                if om:
                    day = latest[:10]
                    res.observations.append(Obs('flood.causeway_overflow_level_m', WEIR.geo_level, WEIR.geo_code,
                                                day, day, value=num(om.group(1))))
                sm = re.search(r'Causeway is\s+([^\n*]+)', text, re.I)
                if sm and sm.group(1).strip():
                    res.observations.append(Obs('flood.causeway_status', WEIR.geo_level, WEIR.geo_code,
                                                latest, latest, value_text=sm.group(1).strip().upper()))
            elif kind == 'zone':
                cols = {}
                for j, h in enumerate(header):
                    if j == 0:
                        continue
                    code = zone_code(h)
                    if code in cols.values():
                        raise ValueError(f'two columns map to zone {code!r}: {header}')
                    cols[j] = code
                for code in cols.values():
                    res.geos.append(zone_geo(code))
                for when, cells in rows:
                    for j, code in cols.items():
                        res.observations.append(_obs('rain.smc_zone_mm', 'smc_zone', code, when, _cell(cells, j)))
            elif kind == 'total':
                j = next(j for j, h in enumerate(header) if 'total rainfall' in h.lower())
                for when, cells in rows:
                    res.observations.append(_obs('rain.smc_total_mm', 'smc_city', 'smc', when, _cell(cells, j)))
            elif kind == 'creek':
                cols = {}
                for j, h in enumerate(header):
                    if j == 0:
                        continue
                    code, creek, zone_label, dl = _creek_column(h)
                    if code in {c for c, _ in cols.values()}:
                        raise ValueError(f'two columns map to creek gauge {code!r}: {header}')
                    cols[j] = (code, dl)
                    res.geos.append(Geo('creek', code, f'{creek} ({zone_label} gauge)' if zone_label else creek,
                                        'smc_city', 'smc',
                                        note=f'SMC Khadi Water Level gauge on {creek}, listed under '
                                             f'"{zone_label or "no zone"}". Danger level is stored as '
                                             f'flood.creek_danger_level_m.'))
                for when, cells in rows:
                    for j, (code, _) in cols.items():
                        res.observations.append(_obs('flood.creek_level_m', 'creek', code, when, _cell(cells, j)))
                day = latest[:10]
                for code, dl in cols.values():
                    if dl is not None:
                        res.observations.append(Obs('flood.creek_danger_level_m', 'creek', code, day, day, value=dl))
    return res


# ---------- validation ----------

# metric -> (low, high) plausible range for reported values
RANGES = {
    'flood.dam_level_ft': (240, 360),            # Ukai FRL 345 ft; dead storage level is ~270 ft
    'flood.dam_inflow_cusec': (0, 2_000_000),    # 2006 flood peak inflow was ~1.1 million cusec
    'flood.dam_outflow_cusec': (0, 2_000_000),
    'flood.dam_frl_ft': (330, 360),
    'flood.weir_level_m': (-5, 30),
    'flood.weir_outflow_cusec': (0, 2_000_000),
    'flood.causeway_overflow_level_m': (1, 20),
    'rain.smc_zone_mm': (0, 600),
    'rain.smc_total_mm': (0, 6000),
    'flood.creek_level_m': (-5, 30),
    'flood.creek_danger_level_m': (1, 30),
}

# metric -> minimum number of observations a healthy page yields (it shows ~10 rows per table)
MIN_COUNTS = {
    'flood.dam_level_ft': 3,
    'flood.weir_level_m': 3,
    'rain.smc_zone_mm': 3 * 5,
    'rain.smc_total_mm': 3,
    'flood.creek_level_m': 3,
}


def validate(result: Result, raw: Raw | None) -> None:
    counts: dict[str, int] = {}
    for o in result.observations:
        counts[o.metric_id] = counts.get(o.metric_id, 0) + 1
        lo_hi = RANGES.get(o.metric_id)
        if lo_hi and o.value is not None and not lo_hi[0] <= o.value <= lo_hi[1]:
            raise ValidationError(f'implausible {o.metric_id} = {o.value} at {o.geo_code} {o.period_start}')
    for metric, n in MIN_COUNTS.items():
        if counts.get(metric, 0) < n:
            raise ValidationError(f'only {counts.get(metric, 0)} {metric} values parsed (expected >= {n}); '
                                  'page layout may have changed')
    zones = {o.geo_code for o in result.observations if o.metric_id == 'rain.smc_zone_mm'}
    if len(zones) < 5 or not zones <= set(ZONES):
        raise ValidationError(f'unexpected zone set in rainfall table: {sorted(zones)}')
    for o in result.observations:
        if o.metric_id == 'flood.causeway_status' and not 2 <= len(o.value_text or '') <= 40:
            raise ValidationError(f'implausible causeway status text {o.value_text!r}')

    instants = [o.period_start for o in result.observations if 'T' in o.period_start]
    if not instants:
        raise ValidationError('no timestamped readings parsed')
    latest, earliest = max(instants), min(instants)
    if earliest < '2015-01-01':
        raise ValidationError(f'reading dated {earliest}: implausibly old')
    retrieved = (raw.retrieved_at if raw is not None else '') or ''
    if retrieved:
        limit = (datetime.fromisoformat(retrieved[:19]) + timedelta(hours=6)).isoformat(timespec='minutes')
        if latest > limit:
            raise ValidationError(f'reading dated {latest} is in the future (retrieved {retrieved})')
    # Each table lists its ~10 most recent readings. Tables may lag each other (e.g. creek gauges
    # not updated after the monsoon), so the window is checked per table: rows spread over more
    # than a month point to misread dates (day/month swapped), not to a real reading window.
    by_metric: dict[str, list[str]] = {}
    for o in result.observations:
        if 'T' in o.period_start:
            by_metric.setdefault(o.metric_id, []).append(o.period_start)
    for metric, ts in by_metric.items():
        span = datetime.fromisoformat(max(ts)) - datetime.fromisoformat(min(ts))
        if span > timedelta(days=31):
            raise ValidationError(f'{metric} readings span {span} ({min(ts)} .. {max(ts)}); dates misread?')
