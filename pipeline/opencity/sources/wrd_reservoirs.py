"""Gujarat WRD daily reservoir storage report (PDF): Surat and Tapi district dams, Sardar Sarovar.

Report: https://wrd-dam.gujarat.gov.in/downloads/home_pdf.php?dt=<base64 of YYYY-MM-DD>
Published by the Narmada, Water Resources, Water Supply and Kalpsar Department (N.W.R.W.S. & Kalpsar),
one 23-page TCPDF report per day, every page stamped "Date :- DD-MM-YYYY". Pages used:

  p1   ABSTRACT, and the "Sardar Sarovar(Narmada Dam)" block:
         FRL :138.68 | Design Gross Storage : 9460.00 | Percentage Storage : 98.77%
         Present Water Level (m) | Average In Flow (cusecs) | Gross Storage (MCM) | 7 release columns
  p2   "Districtwise Storage": design/present gross and live storage (MCM) and % per district,
         a SARDAR SAROVAR row, and the Grand Total (all 207 schemes incl. Sardar Sarovar)
  p3   "Gross Storage of major schemes": the Sardar Sarovar row gives its warning level and
         inflow / outflow (river) / outflow (canal) in cusecs
  p4+  "Statement showing the details of dams in Gujarat", one row per scheme (206, excl. Sardar Sarovar):
         Sr | Scheme Id | Location Id | District | Taluka | Name | Region | Type | OSL | FRL | PWL (m) |
         design gross/live/dead | present gross/live/dead (MCM) | % filling | RF | CRF | warning |
         inflow | outflow river | outflow canal (cusecs)

What is stored (period = the report date, an instant):
  - every scheme the detailed statement files under District "Surat" or "Tapi" (2026: Lakhigam and
    Ver-II in Surat district; Ukai and Doswada in Tapi district). Ukai is in Tapi district (Songadh
    taluka) and is stored with parent tapi_district, never as a Surat dam.
  - Sardar Sarovar (Narmada district, parent: state) from pages 1-3.
  - the Surat and Tapi district rows and the Gujarat Grand Total of the districtwise table.

Layout notes: TCPDF wraps numbers that do not fit their cell, so `pdftotext -layout` prints e.g.
Ukai's design gross storage as "7414.2" with a "9" on the next line, right-aligned under it. Each
continuation fragment is joined to the cell on the row line whose column span it shares
(_merge_continuations). The warning cell wraps the same way ("HIGH"/"ALERT", "WARNI"/"NG").
A row of a Surat/Tapi scheme that cannot be read exactly raises; it is never guessed.

Unpublished days: the server answers 200 with an empty body (and a "report_01-01-1970.pdf" file
name) for a date whose report is not out yet. fetch() does not pass those on, so the date is
fetched again on the next run. The day's report is created at about 09:00 IST (PDF CreationDate
08:38-09:03 on five reports checked), so today's date is only asked for from 10:00 IST.
"""
from __future__ import annotations

import base64
import re
from datetime import date, timedelta

from ..model import FetchError, Geo, Metric, Obs, Raw, Result, Source, ValidationError
from ..parse import num, parse_date, pdf_text
from ..surat import GUJARAT, SURAT_DISTRICT, TAPI_DISTRICT

BASE = 'https://wrd-dam.gujarat.gov.in/downloads/home_pdf.php'
LOOKBACK_DAYS = 3          # each run asks for the latest report date and the 3 before it; parsed dates are skipped
REPORT_READY_HOUR = 10     # IST; the PDFs are created at about 08:40-09:05 (PDF CreationDate), so not asked earlier

SOURCE = Source(
    id='wrd_reservoirs',
    name='Gujarat WRD daily reservoir storage: Surat and Tapi district dams, Sardar Sarovar',
    publisher='Narmada, Water Resources, Water Supply and Kalpsar Department, Government of Gujarat',
    url='https://wrd-dam.gujarat.gov.in/',
    module='water',
    cadence='daily',
    interval_hours=12,      # one report per day, out in the morning; two checks a day catch it the same day
    geo_note='Dams filed under Surat and Tapi districts in the WRD statement (geo level dam, parent '
             'surat_district / tapi_district; Ukai is in Tapi district), Sardar Sarovar (dam, parent state), '
             'the Surat and Tapi district totals, and the Gujarat grand total.',
    licence_note='Government of Gujarat daily report; public information',
    notes='URL takes the report date base64-encoded (dt=). Each report date is immutable and fetched once '
          '(skip_if_seen). An empty response means the report is not out yet; it is retried on the next run.',
    metrics=(
        Metric('wrd.dam_level_m', 'Reservoir water level', 'm',
               'Present water level (PWL, metres) from the detailed dam statement; for Sardar Sarovar the '
               '"Present Water Level (in m)" of its page-1 block.'),
        Metric('wrd.dam_frl_m', 'Full reservoir level', 'm',
               'Full reservoir level (FRL, metres) as printed in that day\'s report.'),
        Metric('wrd.design_gross_storage_mcm', 'Design gross storage', 'MCM',
               'Design gross storage capacity in million cubic metres. For a district or the state: the '
               'districtwise table\'s total over its dams.'),
        Metric('wrd.design_live_storage_mcm', 'Design live storage', 'MCM',
               'Design live storage capacity (MCM). District/state values from the districtwise table.'),
        Metric('wrd.gross_storage_mcm', 'Present gross storage', 'MCM',
               'Present gross storage (MCM) on the report date. District/state values from the districtwise table.'),
        Metric('wrd.live_storage_mcm', 'Present live storage', 'MCM',
               'Present live storage (MCM) on the report date. District/state values from the districtwise table.'),
        Metric('wrd.gross_storage_pct', 'Storage, % of design gross', '%',
               'Present gross storage as a percentage of design gross storage, as printed ("Percentage '
               'Filling %" for a dam; the gross % column of the districtwise table).'),
        Metric('wrd.live_storage_pct', 'Live storage, % of design live', '%',
               'Present live storage as a percentage of design live storage, from the districtwise table '
               '(districts, the state total and Sardar Sarovar only; the dam statement does not print it).'),
        Metric('wrd.alert_level', 'Reservoir warning level', '',
               'value_text = the report\'s "Type of Warning": HIGH ALERT (above 90% full), ALERT (80-90%), '
               'WARNING (70-80%) or NIL (below 70%), per the report\'s own abstract.'),
        Metric('wrd.inflow_cusec', 'Inflow', 'cusecs',
               'Inflow into the reservoir in cusecs as printed in the report (Sardar Sarovar: the "Inflow in '
               'Cusecs" of the major-schemes table).'),
        Metric('wrd.outflow_river_cusec', 'Outflow to the river', 'cusecs',
               'Outflow released to the river, cusecs, as printed.'),
        Metric('wrd.outflow_canal_cusec', 'Outflow to canals', 'cusecs',
               'Outflow released to canals, cusecs, as printed.'),
        Metric('wrd.rain_24h_mm', 'Rainfall at the dam, last 24 hours', 'mm',
               'Column RF of the dam statement (the rainfall statement calls it "Rain During Last 24 Hour").'),
        Metric('wrd.rain_cumulative_mm', 'Cumulative rainfall at the dam', 'mm',
               'Column CRF of the dam statement ("Cumm Rainfall"). The report does not state the start date '
               'of the accumulation.'),
    ),
)

TARGET_DISTRICTS = {'Surat': SURAT_DISTRICT, 'Tapi': TAPI_DISTRICT}
DISTRICT_ROWS = {'Surat': ('surat_district', 'surat'), 'Tapi': ('tapi_district', 'tapi')}

# WRD scheme id -> stable geo code and display name. Ukai's name matches smc_rainfall.UKAI so the shared
# geo row keeps one name whichever adapter writes last. A new Surat/Tapi scheme gets a slug of its name.
KNOWN_DAMS = {
    '36': ('ukai', 'Ukai dam (Tapi river)'),
    '37': ('doswada', 'Doswada dam'),
    '38': ('ver_ii', 'Ver-II dam'),
    '39': ('lakhigam', 'Lakhigam dam'),
}
SARDAR_SAROVAR = Geo('dam', 'sardar_sarovar', 'Sardar Sarovar dam (Narmada river)', 'state', 'gujarat',
                     note='Listed by the WRD report under Narmada district: outside Surat and Tapi districts. '
                          'Stored as the state\'s largest reservoir for context.')

REGIONS = {'SG', 'CG', 'NG', 'Sau', 'Kutch'}
GATE_TYPES = {'G', 'UG', 'FG'}
WARNINGS = {'HIGHALERT': 'HIGH ALERT', 'ALERT': 'ALERT', 'WARNING': 'WARNING', 'NIL': 'NIL'}

# the 16 cells after Region and Type in the detailed statement
TAIL = ('osl', 'frl', 'pwl', 'design_gross', 'design_live', 'design_dead', 'gross', 'live', 'dead',
        'pct', 'rf', 'crf', 'warning', 'inflow', 'outflow_river', 'outflow_canal')
DAM_METRICS = [
    ('pwl', 'wrd.dam_level_m'), ('frl', 'wrd.dam_frl_m'),
    ('design_gross', 'wrd.design_gross_storage_mcm'), ('design_live', 'wrd.design_live_storage_mcm'),
    ('gross', 'wrd.gross_storage_mcm'), ('live', 'wrd.live_storage_mcm'), ('pct', 'wrd.gross_storage_pct'),
    ('inflow', 'wrd.inflow_cusec'), ('outflow_river', 'wrd.outflow_river_cusec'),
    ('outflow_canal', 'wrd.outflow_canal_cusec'), ('rf', 'wrd.rain_24h_mm'), ('crf', 'wrd.rain_cumulative_mm'),
]
DISTRICT_COLS = ('wrd.design_gross_storage_mcm', 'wrd.design_live_storage_mcm', 'wrd.gross_storage_mcm',
                 'wrd.live_storage_mcm', 'wrd.gross_storage_pct', 'wrd.live_storage_pct')
MIN_DETAIL_ROWS = 150      # 206 schemes in 2026; far fewer means the layout changed

# one whitespace-free word, e.g. '7414.2' or 'Songadh'
_WORD = re.compile(r'\S+')
# a whole numeric cell, e.g. '7414.2', '-29.93' or '83.32%'
_NUMERIC = re.compile(r'^-?[\d.]+%?$')
# Sr | Scheme Id | Location Id | District, e.g. ' 7        36     7            Tapi'
_ROW_START = re.compile(r'^\s*\d+\s+\d+\s+\d+\s+[A-Za-z]')
# one captured number, e.g. '9460.00' or '-29.93'
_NUM = r'(-?[\d.]+)'


def report_url(d: date) -> str:
    return f'{BASE}?dt={base64.b64encode(d.isoformat().encode()).decode()}'


def fetch(ctx):
    now = ctx.now
    last = now.date() if now.hour >= REPORT_READY_HOUR else now.date() - timedelta(days=1)
    available = 0
    for back in range(LOOKBACK_DAYS, -1, -1):          # oldest first
        d = last - timedelta(days=back)
        url = report_url(d)
        if ctx.seen('GET', url):
            available += 1
            continue
        raw = ctx.get(url, meta={'date': d.isoformat()}, skip_if_seen=True, soft=True)
        if raw is None:
            continue
        if not raw.body.strip():
            ctx.log.info('no WRD report for %s yet (empty response)', d)
            continue
        available += 1
        yield raw
    if not available:
        raise FetchError(f'no WRD report obtained for any of the {LOOKBACK_DAYS + 1} dates up to {last}')


# ---------- parsing ----------

def _report_date(text: str) -> str:
    # the page stamp, e.g. 'Date :- 17-10-2026'
    dates = set(re.findall(r'Date\s*:-\s*(\d{1,2}-\d{1,2}-\d{4})', text))
    if len(dates) != 1:
        raise ValidationError(f'expected one "Date :-" stamp on every page, found {sorted(dates) or "none"}')
    return parse_date(dates.pop(), '%d-%m-%Y').isoformat()


def _tokens(line: str) -> list[list]:
    return [[m.start(), m.end(), m.group()] for m in _WORD.finditer(line)]


def _merge_continuations(toks: list[list], cont_lines: list[str]) -> None:
    """Append each wrapped fragment to the row cell whose column span it shares (in place)."""
    for line in cont_lines:
        for s, e, t in _tokens(line):
            best = max(toks, key=lambda k: (min(e, k[1]) - max(s, k[0]), -abs(k[1] - e)))
            if min(e, best[1]) - max(s, best[0]) <= 0 and abs(best[1] - e) > 2:
                raise ValueError(f'cannot place wrapped fragment {t!r} at column {s}')
            glue = '' if _NUMERIC.match(best[2]) and _NUMERIC.match(t) else ' '
            best[2] = best[2] + glue + t


def _detail_rows(pages: list[str]):
    """Yield (main_line, continuation_lines) for each scheme row of the detailed statement."""
    for page in pages:
        if 'OSL' not in page or 'Locati' not in page:
            continue
        lines = page.split('\n')
        i = 0
        while i < len(lines):
            if _ROW_START.match(lines[i]):
                j = i + 1
                while j < len(lines) and lines[j].strip() and not _ROW_START.match(lines[j]):
                    j += 1
                yield lines[i], lines[i + 1:j]
                i = j
            else:
                i += 1


def _parse_row(line: str, cont: list[str]) -> dict | None:
    """One detailed-statement row -> dict of raw cells, or None if the line is not a scheme row."""
    toks = _tokens(line)
    ri = next((k for k in range(3, len(toks) - 1)
               if toks[k][2] in REGIONS and toks[k + 1][2] in GATE_TYPES), None)
    if ri is None:
        return None
    # cells are 2+ spaces apart, e.g. 'Tapi      Songadh                 Ukai' -> Tapi | Songadh | Ukai
    parts = re.split(r'\s{2,}', line[toks[2][1]:toks[ri][0]].strip())
    row = {'sr': toks[0][2], 'scheme_id': toks[1][2], 'parts': parts, 'district': parts[0],
           'region': toks[ri][2], 'gate': toks[ri + 1][2]}
    _merge_continuations(toks, cont)      # wrapped names land on name cells, wrapped numbers on theirs
    tail = [t[2] for t in toks[ri + 2:]]
    if len(tail) != len(TAIL):
        raise ValueError(f'row {row["sr"]} ({" ".join(parts)}): expected {len(TAIL)} cells after '
                         f'Region/Type, found {len(tail)}: {tail}')
    row.update(zip(TAIL, tail))
    return row


def _warning(cell: str) -> str:
    # drop the space a wrapped cell gets, e.g. 'WARNI NG' -> 'WARNING', 'HIGH ALERT' -> 'HIGHALERT'
    key = re.sub(r'\s+', '', cell).upper()
    if key not in WARNINGS:
        raise ValueError(f'unknown warning level {cell!r}')
    return WARNINGS[key]


def _obs(metric: str, geo: tuple[str, str], day: str, cell) -> Obs:
    v = num(cell)
    return Obs(metric, geo[0], geo[1], day, day, value=v, status='reported' if v is not None else 'not_reported')


def _dam_geo(row: dict) -> Geo:
    district, taluka, name = row['parts']
    parent = TARGET_DISTRICTS[district]
    code, label = KNOWN_DAMS.get(row['scheme_id'], (None, None))
    if code is None:
        # slug of the name, e.g. 'Ver-II' -> 'ver_ii'
        code = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')
        label = f'{name} dam'
    note = None if code == 'ukai' else (
        f'WRD scheme id {row["scheme_id"]}; {taluka} taluka, {district} district; gate type {row["gate"]}.')
    return Geo('dam', code, label, parent.geo_level, parent.geo_code, note=note)


def _sardar_sarovar(pages: list[str], day: str, res: Result) -> None:
    geo = ('dam', 'sardar_sarovar')
    # page 1 block
    p1 = pages[0]
    # everything after the heading 'Sardar Sarovar(Narmada Dam)'
    m = re.search(r'Sardar Sarovar\s*\(Narmada Dam\)(.*)', p1, re.S | re.I)
    if not m:
        raise ValidationError('Sardar Sarovar block not found on page 1')
    block = m.group(1)
    # e.g. 'FRL :138.68' and 'Percentage Storage : 99.66%'
    frl = re.search(r'FRL\s*:\s*' + _NUM, block)
    pct = re.search(r'Percentage Storage\s*:\s*' + _NUM + '%', block)
    vals = next((ln.split() for ln in block.split('\n')
                 if len(ln.split()) == 10 and all(_NUMERIC.match(t) for t in ln.split())), None)
    if not (frl and pct and vals):
        raise ValidationError('Sardar Sarovar block on page 1: FRL, percentage or the value row not found')
    level, gross = vals[0], vals[2]      # Present Water Level (m), [Average In Flow], Gross Storage (MCM)
    # page 2 districtwise row
    p2 = next((p for p in pages if 'Districtwise Storage' in p), '')
    # e.g. '  SARDAR SAROVAR   9460.00   5760.00   9427.79   5727.79   99.66%   99.44%'
    d = re.search(r'^\s*SARDAR SAROVAR\s+' + r'\s+'.join([_NUM] * 4) + r'\s+' + _NUM + r'%\s+' + _NUM + '%',
                  p2, re.M)
    # page 3 major-schemes row: "... 98.77% HIGH ALERT   41296.00   619   11712.38"
    p3 = next((p for p in pages if 'Gross Storage of major schemes' in p), '')
    s = re.search(r'SARDAR\s+[^%\n]*?' + _NUM + r'%\s+(HIGH\s*ALERT|ALERT|WARNING|NIL)\s+'
                  + _NUM + r'\s+' + _NUM + r'\s+' + _NUM + r'\s*$', p3, re.M)
    if not (d and s):
        raise ValidationError('Sardar Sarovar row missing from the districtwise or major-schemes table')
    if num(d.group(3)) != num(gross) or num(d.group(5)) != num(pct.group(1)):
        raise ValidationError(f'Sardar Sarovar storage differs between page 1 ({gross} MCM, {pct.group(1)}%) '
                              f'and page 2 ({d.group(3)} MCM, {d.group(5)}%)')
    res.observations += [
        _obs('wrd.dam_level_m', geo, day, level),
        _obs('wrd.dam_frl_m', geo, day, frl.group(1)),
        *[_obs(metric, geo, day, d.group(k + 1)) for k, metric in enumerate(DISTRICT_COLS)],
        Obs('wrd.alert_level', *geo, day, day, value_text=_warning(s.group(2))),
        _obs('wrd.inflow_cusec', geo, day, s.group(3)),
        _obs('wrd.outflow_river_cusec', geo, day, s.group(4)),
        _obs('wrd.outflow_canal_cusec', geo, day, s.group(5)),
    ]
    res.geos.append(SARDAR_SAROVAR)


def _districtwise(pages: list[str], day: str, res: Result) -> None:
    p2 = next((p for p in pages if 'Districtwise Storage' in p), None)
    if p2 is None:
        raise ValidationError('"Districtwise Storage" page not found')
    # four MCM values and two percentages, e.g. '36.14   35.78   31.73   31.37   87.80%   87.67%'
    six = r'\s+'.join([_NUM] * 4) + r'\s+' + _NUM + r'%\s+' + _NUM + '%'
    for district, geo in DISTRICT_ROWS.items():
        # e.g. '   13      Surat   36.14   35.78   31.73   31.37   87.80%   87.67%'
        m = re.search(r'^\s*\d+\s+' + district + r'\s+' + six + r'\s*$', p2, re.M)
        if not m:
            raise ValidationError(f'{district} row missing from the districtwise table')
        res.observations += [_obs(metric, geo, day, m.group(k + 1)) for k, metric in enumerate(DISTRICT_COLS)]
    # e.g. 'Grand Total :   25257.55   20353.03   20136.36   15269.85   79.72%   75.02%'
    m = re.search(r'Grand Total\s*:\s*' + six, p2)
    if not m:
        raise ValidationError('Grand Total row missing from the districtwise table')
    res.observations += [_obs(metric, ('state', 'gujarat'), day, m.group(k + 1))
                         for k, metric in enumerate(DISTRICT_COLS)]


def parse(raw: Raw) -> Result:
    if not raw.body[:1024].lstrip().startswith(b'%PDF'):
        raise ValidationError('not a PDF (an empty body means the report for that date is not out yet)')
    text = pdf_text(raw.body)
    pages = text.split('\f')
    day = _report_date(text)
    res = Result(geos=[GUJARAT, SURAT_DISTRICT, TAPI_DISTRICT])

    n_rows = 0
    for line, cont in _detail_rows(pages):
        # a Surat/Tapi statement row, e.g. ' 8        39     8           Surat        Mandvi ...'
        target = re.match(r'^\s*\d+\s+\d+\s+\d+\s+(Surat|Tapi)\s', line)
        try:
            row = _parse_row(line, cont)
        except ValueError:
            if target:
                raise
            n_rows += 1        # a scheme row this adapter does not store; its layout quirks don't matter
            continue
        if row is None:
            if target:
                raise ValueError(f'Surat/Tapi row without Region/Type codes: {line.strip()!r}')
            continue
        n_rows += 1
        if row['district'] not in TARGET_DISTRICTS:
            continue
        if len(row['parts']) != 3:
            raise ValueError(f'cannot split District | Taluka | Name in {line.strip()!r}')
        geo = _dam_geo(row)
        res.geos.append(geo)
        g = (geo.geo_level, geo.geo_code)
        res.observations += [_obs(metric, g, day, row[cell]) for cell, metric in DAM_METRICS]
        res.observations.append(Obs('wrd.alert_level', *g, day, day, value_text=_warning(row['warning'])))
    if n_rows < MIN_DETAIL_ROWS:
        raise ValidationError(f'only {n_rows} scheme rows found in the dam statement; layout may have changed')

    _districtwise(pages, day, res)
    _sardar_sarovar(pages, day, res)
    return res


# ---------- validation ----------

RANGES = {
    'wrd.dam_level_m': (0, 300),             # Ukai ~80-106 m, Sardar Sarovar ~110-139 m
    'wrd.dam_frl_m': (0, 300),
    'wrd.gross_storage_pct': (0, 110),
    'wrd.live_storage_pct': (0, 110),
    'wrd.inflow_cusec': (0, 2_000_000),     # Ukai's 2006 flood peak was ~1.1 million cusecs
    'wrd.outflow_river_cusec': (0, 2_000_000),
    'wrd.outflow_canal_cusec': (0, 100_000),
    'wrd.rain_24h_mm': (0, 1000),
    'wrd.rain_cumulative_mm': (0, 6000),
}


def validate(result: Result, raw: Raw | None) -> None:
    by = {(o.metric_id, o.geo_level, o.geo_code): o for o in result.observations}
    days = {o.period_start for o in result.observations}
    if len(days) != 1:
        raise ValidationError(f'expected one report date, got {sorted(days)}')
    day = days.pop()
    if raw is not None:
        if raw.retrieved_at and day > raw.retrieved_at[:10]:
            raise ValidationError(f'report date {day} is after the fetch time {raw.retrieved_at}')
        asked = (raw.meta or {}).get('date')
        if asked and asked != day:
            raise ValidationError(f'asked for the report of {asked} but the PDF is dated {day}')
    if ('wrd.gross_storage_mcm', 'dam', 'ukai') not in by:
        raise ValidationError('Ukai (Tapi district) not found in the dam statement')

    for o in result.observations:
        if o.value is None:
            continue
        # storages (MCM): Sardar Sarovar 9460 is the largest dam, the Gujarat grand total ~25,300
        lo, hi = RANGES.get(o.metric_id, (0, 30000))
        if not lo <= o.value <= hi:
            raise ValidationError(f'implausible {o.metric_id} = {o.value} for {o.geo_code} on {day}')

    dams = [g for g in result.geos if g.geo_level == 'dam']
    for g in dams:
        v = {m: o.value for (m, lvl, c), o in by.items() if lvl == 'dam' and c == g.geo_code}
        level, frl = v.get('wrd.dam_level_m'), v.get('wrd.dam_frl_m')
        if None not in (level, frl) and level > frl + 3:
            raise ValidationError(f'{g.geo_code}: water level {level} m is far above the FRL {frl} m')
        gross, design = v.get('wrd.gross_storage_mcm'), v.get('wrd.design_gross_storage_mcm')
        pct = v.get('wrd.gross_storage_pct')
        if None not in (gross, design, pct) and design > 0 and abs(100 * gross / design - pct) > 0.5:
            raise ValidationError(f'{g.geo_code}: {gross}/{design} MCM is not the printed {pct}%')
        if None not in (gross, design) and gross > design * 1.05:
            raise ValidationError(f'{g.geo_code}: present storage {gross} exceeds design {design} MCM')
        live, dlive = v.get('wrd.live_storage_mcm'), v.get('wrd.design_live_storage_mcm')
        if None not in (live, gross) and live > gross + 0.01:
            raise ValidationError(f'{g.geo_code}: live storage {live} exceeds gross {gross} MCM')
        if None not in (dlive, design) and dlive > design + 0.01:
            raise ValidationError(f'{g.geo_code}: design live {dlive} exceeds design gross {design} MCM')

    # the dams stored for a district must add up to that district's row of the districtwise table,
    # so a Surat/Tapi scheme that was skipped or misread cannot go unnoticed
    for level, code in DISTRICT_ROWS.values():
        members = [g.geo_code for g in dams if g.parent_code == code]
        for metric in ('wrd.design_gross_storage_mcm', 'wrd.gross_storage_mcm'):
            total = by[(metric, level, code)].value
            parts = [by[(metric, 'dam', c)].value for c in members]
            if total is None or any(p is None for p in parts):
                continue
            # each printed value is rounded to 0.01, so honest totals differ by a few hundredths at most
            if abs(sum(parts) - total) > 0.03 + 0.01 * len(parts):
                raise ValidationError(f'{code} district {metric}: dams add up to {sum(parts):.2f}, '
                                      f'the districtwise table says {total}')
