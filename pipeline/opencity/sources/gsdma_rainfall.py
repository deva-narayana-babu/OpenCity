"""GSDMA daily taluka-wise rainfall report: Surat district talukas against their 1996-2025 average.

Publisher: Gujarat State Disaster Management Authority (GSDMA) / State Emergency Operation Centre, Revenue
Department, Government of Gujarat. The report is an Excel sheet exported to PDF ("8 - RAINFALL REPORT-ZONEWISE/
TALUKAWISE"), posted every morning of the monsoon season.

Where it is published:
  Page      https://gsdma.org/rainfalldata-2?Type=2  ("Rainfall Data": a year calendar; click a day for its PDF)
  List      POST https://gsdma.org/GetFileData.aspx/GetColumnChartData
            body (JSON) {"Type": "2", "Year": "2026"}   (the page sends the Type from its own URL; Type 1 is empty)
            -> {"d": [{"__type": "GSDMA.GetFileData+ChartDetails", "DiffProjectCount": 0,
                       "PDFName": "https://www.gsdma.org/uploads/Rainfall/24hrsrainfalldata21stoctober1021...pdf",
                       "Date": "10/21/2026"}, ...]}          Date is MM/DD/YYYY; 142 reports for 2026 (2 Jun - 21 Oct)
  Report    the PDFName URL: a text PDF, 5 pages, read with pdftotext -layout. The files of 12 Aug - 2 Oct 2026 are
            named "ilovepdfmerged*.pdf"; the one checked (30 Sep) has 16 pages, the same report pages first.

Report layout. Every page starts with
    Rainfall Report 21-10-2026 (Rainfall in mm)(Dt.20.10.2026 06:00 am to Dt.21.10.2026 06:00 am)
then two side-by-side tables, one row per taluka, grouped by region and district:
    Sr. No | District/ Taluka | Avrg Rain (1996-2025) | Rain till Yesterday | Rain During last 24 Hrs. |
    Total Rainfall | % Against Avg Rain
Each district block is "<n> <District>", its taluka rows "<sr> <Taluka> <5 numbers>", and a "Dist. Avg." row.
On page 4 the Surat block ("31 Surat") is in the left table and shares its lines with a summary box on the right
("Raining Taluka/s", "June- 2026 Rain 35.21", ...), so lines are cut into cells at runs of 2+ spaces and only the
first 6 cells of a Surat row are read. The right table of page 4 ends with the "State Average" row; the summary
box lists the state's rain per month ("June- 2026 Rain" ... "November-2026 Rain") and their "Total".

What is stored:
- Surat district talukas (geo level surat_taluka, a level added by this adapter, parent surat_district): the 12
  rows printed under Surat in 2026: Ambika, Areth, Bardoli, Chorasi, Kamrej, Mahuva, Mandvi, Mangrol, Olpad,
  Palsana, Surat City, Umarpada. "Surat City" is GSDMA's reporting unit for the city taluka(s), not the SMC
  boundary, so it is NOT filed as smc_city.
- Surat district (surat_district): the "Dist. Avg." row. In the 2026 reports it is the plain (unweighted) mean of
  the 12 taluka rows; validate() checks this, which also catches a skipped or mis-read row.
- Gujarat (state): the "State Average" row, and the state's rain per month from the summary box.
Metrics:
  gsdma.rain_24h_mm          rain in the report's 24 hours (06:00 to 06:00 IST); period = that window
  gsdma.rain_season_mm       "Total Rainfall": rain since the start of the season, up to 06:00 IST of the report
                             day; an instant reading at that time (the report does not print when the
                             accumulation starts; its month list starts in June)
  gsdma.rain_normal_mm       "Avrg Rain (1996-2025)": the average WHOLE-SEASON rainfall over those years;
                             period = the averaging years as printed (1996-01-01..2025-12-31)
  gsdma.rain_pct_of_normal   "% Against Avg Rain" = season total so far / whole-season average x 100. It is NOT
                             "% of normal to date": early in the season it is low by construction.
  gsdma.state_month_rain_mm  state average rain in a calendar month; for the report's own month the period is
                             the 1st of the month to the report day (month to date); later months are not stored
"Rain till Yesterday" is not stored: it is Total minus the 24-hour figure (parse() checks that identity).
Units: millimetres; % for the ratio. Cadence: daily from about 2 June to 21 October (2026).

Quirks:
- Ambika and Areth appear as separate Surat rows in the 2026 reports; their printed 1996-2025 averages are
  identical to Mahuva's (1653 mm) and Mandvi's (1521 mm). Similar pairs elsewhere: Ukai = Songadh (Tapi),
  Chikda = Dediapada (Narmada, also printed with the same serial number). Stored as printed.
- The list can point at the wrong file: in 2026 the entry for 19 Oct is "24hrsrainfalldata17thoctober...pdf",
  whose content is the 17 Oct report. The report date is always taken from the PDF itself, so such an entry
  just re-stores the 17 Oct values; the 19 Oct report is missing.
- The early-season files are named "24hrsrainfalldatadt<stamp>.<dd>.<mm>.<yyyy>.pdf" (2 Jun - 7 Aug 2026); the
  two tried (2 Jun, 7 Aug) answer HTTP 401 Unauthorized. They are outside LOOKBACK, and nothing tries to get
  around a 401: it is recorded as a failed fetch.
- Month totals of a past month can still change (September 2026 was 125.53 mm on 30 Sep and 125.81 mm on
  17 Oct); later reports overwrite and the change is kept as a revision.
- A report's "Rain till Yesterday" is not always the previous report's Total: late returns are added without a
  24-hour figure (Surat Dist. Avg.: Total 1757.92 mm on 20 Oct 2026, then 0.00 mm in 24 h but Total 1758.08 mm
  on 21 Oct). So season totals can rise on a day with 0 mm in the last 24 hours; both are stored as printed.

fetch(): the year's list (one POST), then the newest LOOKBACK reports, oldest first, each downloaded once
(skip_if_seen: a posted PDF does not change). Reports older than that are not fetched.

Licence: Government of Gujarat public document; no licence is stated on the page or the PDF.
"""
from __future__ import annotations

import json
import re

from ..model import Geo, Metric, Obs, Raw, Result, Source, ValidationError
from ..parse import month_period, month_year, num, parse_date, parse_dt, pdf_text
from ..surat import TALUKA_NOTE
from ..surat import GUJARAT, SURAT_DISTRICT

PAGE = 'https://gsdma.org/rainfalldata-2?Type=2'
LIST_URL = 'https://gsdma.org/GetFileData.aspx/GetColumnChartData'
LOOKBACK = 10                  # newest reports fetched per run (each one only once)

# published taluka name (lower case) -> geo code; an unknown name fails validation so codes stay stable
TALUKAS = {
    'ambika': 'ambika', 'areth': 'areth', 'bardoli': 'bardoli', 'chorasi': 'chorasi', 'choryasi': 'chorasi',
    'kamrej': 'kamrej', 'mahuva': 'mahuva', 'mandvi': 'mandvi', 'mangrol': 'mangrol', 'olpad': 'olpad',
    'palsana': 'palsana', 'surat city': 'surat_city', 'umarpada': 'umarpada',
}
NAMES = {'ambika': 'Ambika', 'areth': 'Areth', 'bardoli': 'Bardoli', 'chorasi': 'Chorasi (Choryasi)',
         'kamrej': 'Kamrej', 'mahuva': 'Mahuva', 'mandvi': 'Mandvi', 'mangrol': 'Mangrol', 'olpad': 'Olpad',
         'palsana': 'Palsana', 'surat_city': 'Surat City', 'umarpada': 'Umarpada'}

SOURCE = Source(
    id='gsdma_rainfall',
    name='GSDMA daily rainfall report: Surat district talukas vs 1996-2025 average',
    publisher='Gujarat State Disaster Management Authority / State Emergency Operation Centre, Government of Gujarat',
    url=PAGE,
    module='weather',
    cadence='daily',
    interval_hours=12,          # overridden by interval_hours(now): weekly outside June-November
    geo_note='Surat district talukas (surat_taluka, a level added by this adapter; 12 rows in 2026), Surat district '
             '(the published district average row) and Gujarat (state average and monthly state rain).',
    licence_note='Government of Gujarat public document; no explicit licence stated',
    notes='Monsoon season only (about 2 June to 21 October in 2026). Only the newest 10 reports are fetched per run. '
          'Early-season files of 2026 (2 Jun - 7 Aug) answered HTTP 401 and are not requested. The percentage is '
          'season-to-date total against the whole-season average, not against the normal to date.',
    metrics=(
        Metric('gsdma.rain_24h_mm', 'Rainfall in the last 24 hours (GSDMA)', 'mm',
               '"Rain During last 24 Hrs." of the GSDMA daily report: rain from 06:00 IST of the previous day to '
               '06:00 IST of the report day (the period).'),
        Metric('gsdma.rain_season_mm', 'Season rainfall so far (GSDMA)', 'mm',
               '"Total Rainfall" of the GSDMA daily report: rain since the start of the monsoon season up to 06:00 '
               'IST of the report day (an instant reading at that time).'),
        Metric('gsdma.rain_normal_mm', 'Average season rainfall (GSDMA, 1996-2025)', 'mm',
               '"Avrg Rain (1996-2025)": average whole-season rainfall over the years printed in the header; the '
               'period is those years. For the district and the state it is the published average row.'),
        Metric('gsdma.rain_pct_of_normal', 'Season rainfall so far, % of the season average (GSDMA)', '%',
               '"% Against Avg Rain" = season total so far / whole-season average x 100, as printed; an instant '
               'reading at 06:00 IST of the report day. Not a comparison with the normal to date.'),
        Metric('gsdma.state_month_rain_mm', 'Gujarat average rainfall in the month (GSDMA)', 'mm',
               'State average rainfall in a calendar month, from the summary box ("June- 2026 Rain"). For the '
               'report\'s own month the period ends on the report day (month to date).'),
    ),
)

COLUMNS = ('normal', 'till_yesterday', '24h', 'season', 'pct')


def interval_hours(now) -> float:
    return 12 if 6 <= now.month <= 11 else 24 * 7


def report_links(body: bytes) -> list[tuple[str, str]]:
    """[(ISO date, PDF url)] from the list response, oldest first."""
    out = set()
    for item in json.loads(body)['d']:
        out.add((parse_date(item['Date'], '%m/%d/%Y').isoformat(), item['PDFName'].strip()))
    return sorted(out)


def fetch(ctx):
    year = ctx.now.year
    listing = ctx.post(LIST_URL, json={'Type': '2', 'Year': str(year)}, meta={'doc': 'list', 'year': year})
    yield listing
    for day, url in report_links(listing.body)[-LOOKBACK:]:
        raw = ctx.get(url, meta={'doc': 'report', 'list_date': day}, skip_if_seen=True, soft=True)
        if raw is not None:
            yield raw


# ---------- parsing ----------

def _cells(line: str) -> list[str]:
    """Cut a pdftotext -layout line at runs of 2+ spaces: ' 4 Chorasi    1313   1104' -> ['4 Chorasi', '1313', '1104']."""
    return [c.strip() for c in line.split('  ') if c.strip()]


def _numbers(cells: list[str], what: str) -> dict:
    if len(cells) < 5:
        raise ValueError(f'{what}: expected 5 numbers, got {cells}')
    return dict(zip(COLUMNS, (num(c) for c in cells[:5])))


def _heading(text: str) -> tuple[str, str, str]:
    """'Rainfall Report 21-10-2026 (Rainfall in mm)(Dt.20.10.2026 06:00 am to Dt.21.10.2026 06:00 am)'
    -> ('2026-10-21', '2026-10-20T06:00', '2026-10-21T06:00'). Every page must carry the same heading."""
    found = set()
    for line in text.splitlines():
        i, a, b = line.find('Rainfall Report '), line.find('(Dt.'), line.find(' to Dt.')
        if i < 0 or a < 0 or b < 0:
            continue
        day = parse_date(line[i:].split()[2], '%d-%m-%Y').isoformat()
        fmt = '%d.%m.%Y %I:%M %p'
        found.add((day, parse_dt(line[a + 4:b], fmt), parse_dt(line[b + 7:line.find(')', b)], fmt)))
    if len(found) != 1:
        raise ValueError(f'expected one "Rainfall Report <date> (Dt.. to Dt..)" heading, found {sorted(found)}')
    return found.pop()


def _surat_block(lines: list[str]) -> tuple[list[tuple[int, str, dict]], dict]:
    """Taluka rows [(sr, name, numbers)] and the Dist. Avg. numbers of the "<n> Surat" block (left table)."""
    rows, inside = [], False
    for line in lines:
        cells = _cells(line)
        if not cells:
            continue
        words = cells[0].split()
        if not inside:
            inside = len(words) == 2 and words[0].isdigit() and words[1] == 'Surat'
            continue
        if cells[0] == 'Dist. Avg.':
            return rows, _numbers(cells[1:], 'Surat Dist. Avg.')
        if len(line) - len(line.lstrip()) > 10:       # only the right-hand summary box on this line
            continue
        sr, _, name = cells[0].partition(' ')
        if not sr.isdigit() or not name:
            raise ValueError(f'unexpected line in the Surat block: {line.strip()!r}')
        rows.append((int(sr), name, _numbers(cells[1:], name)))
    raise ValueError('Surat district block ("<n> Surat" ... "Dist. Avg.") not found')


def _state_average(lines: list[str]) -> dict:
    for line in lines:
        cells = _cells(line)
        if 'State Average' in cells:
            i = cells.index('State Average')
            return _numbers(cells[i + 1:], 'State Average')
    raise ValueError('"State Average" row not found')


def _months(lines: list[str]) -> list[tuple[int, int, float]]:
    """Summary box cells 'June- 2026 Rain', '35.21' -> [(2026, 6, 35.21), ...]."""
    out = []
    for line in lines:
        cells = _cells(line)
        for i, c in enumerate(cells[:-1]):
            if c.endswith(' Rain') and c[:-5].strip()[-4:].isdigit():
                y, m = month_year(c[:-5])
                out.append((y, m, num(cells[i + 1])))
    return out


def parse(raw: Raw) -> Result:
    head = raw.body[:1024].lstrip()
    if head.startswith(b'{'):
        report_links(raw.body)              # the list: checked for shape, nothing to store
        return Result()
    if not head.startswith(b'%PDF'):
        raise ValueError('neither the report list nor a PDF (error page?)')

    text = pdf_text(raw.body)
    if 'Rain till' not in text or '% Against' not in text:
        raise ValueError('column headers "Rain till Yesterday" / "% Against Avg Rain" not found')
    day, w_start, w_end = _heading(text)
    # the averaging period in the column header, e.g. '(1996-2025)'
    m = re.search(r'\((\d{4})-(\d{4})\)', text)
    if not m:
        raise ValueError('averaging period "(YYYY-YYYY)" not found in the header')
    n_start, n_end = f'{m.group(1)}-01-01', f'{m.group(2)}-12-31'
    lines = text.splitlines()
    rows, dist = _surat_block(lines)
    if [sr for sr, _, _ in rows] != list(range(1, len(rows) + 1)):
        raise ValidationError(f'Surat serial numbers are not 1..n: {[sr for sr, _, _ in rows]}')
    for sr, name, v in rows + [(0, 'Dist. Avg.', dist)]:
        # Total = Rain till Yesterday + last 24 h; a shifted or missing cell breaks this
        if None not in (v['till_yesterday'], v['24h'], v['season']) and \
                abs(v['till_yesterday'] + v['24h'] - v['season']) > 0.02:
            raise ValidationError(f'{name}: till yesterday + 24 h != total ({v})')

    res = Result(geos=[GUJARAT, SURAT_DISTRICT])
    places = []
    for sr, name, v in rows:
        code = TALUKAS.get(name.lower())
        if code is None:
            raise ValidationError(f'unknown Surat taluka {name!r}: add it to TALUKAS')
        res.geos.append(Geo('surat_taluka', code, NAMES[code], 'surat_district', 'surat', note=TALUKA_NOTE))
        places.append(('surat_taluka', code, v))
    places.append(('surat_district', 'surat', dist))
    places.append(('state', 'gujarat', _state_average(lines)))

    for level, code, v in places:
        for metric, key, start, end in (('gsdma.rain_normal_mm', 'normal', n_start, n_end),
                                        ('gsdma.rain_24h_mm', '24h', w_start, w_end),
                                        ('gsdma.rain_season_mm', 'season', w_end, w_end),
                                        ('gsdma.rain_pct_of_normal', 'pct', w_end, w_end)):
            res.observations.append(Obs(metric, level, code, start, end, value=v[key],
                                        status='reported' if v[key] is not None else 'not_reported'))

    for y, mo, v in _months(lines):
        start, end = month_period(y, mo)
        if start > day:
            continue                        # a month that has not started yet (printed as 0.00)
        res.observations.append(Obs('gsdma.state_month_rain_mm', 'state', 'gujarat', start, min(end, day), value=v,
                                    status='reported' if v is not None else 'not_reported'))
    return res


def validate(result: Result, raw: Raw) -> None:
    if not result.observations:
        if raw is not None and raw.body[:1024].lstrip().startswith(b'%PDF'):
            raise ValidationError('report parsed to nothing')
        return                              # the list document
    by = {}
    for o in result.observations:
        by.setdefault((o.geo_level, o.geo_code), {})[o.metric_id] = o
    talukas = [k for k in by if k[0] == 'surat_taluka']
    if not 10 <= len(talukas) <= 15 or ('surat_taluka', 'surat_city') not in by:
        raise ValidationError(f'{len(talukas)} Surat taluka rows parsed (expected 10-15 incl. Surat City)')

    season = {}
    for place, ms in by.items():
        normal, rain24, total, pct = (ms[m].value for m in ('gsdma.rain_normal_mm', 'gsdma.rain_24h_mm',
                                                              'gsdma.rain_season_mm', 'gsdma.rain_pct_of_normal'))
        if None in (normal, rain24, total, pct):
            continue
        if not 300 <= normal <= 4000 or not 0 <= rain24 <= 1000 or not 0 <= total <= 6000:
            raise ValidationError(f'{place}: implausible normal {normal} / 24 h {rain24} / total {total} mm')
        if abs(total / normal * 100 - pct) > 0.06:
            raise ValidationError(f'{place}: {pct}% does not match {total} / {normal} mm (columns shifted?)')
        season[place] = (normal, total)
    # the district row is the plain mean of the taluka rows (2026 reports); a missed or mis-read row breaks it
    tal = [season[k] for k in talukas if k in season]
    if len(tal) == len(talukas) and ('surat_district', 'surat') in season:
        d_normal, d_total = season[('surat_district', 'surat')]
        if abs(sum(n for n, _ in tal) / len(tal) - d_normal) > 0.01 or abs(sum(t for _, t in tal) / len(tal) - d_total) > 0.01:
            raise ValidationError('Surat "Dist. Avg." is not the mean of the taluka rows: a row was missed or mis-read')
    end = next(o.period_end for o in result.observations if o.metric_id == 'gsdma.rain_season_mm')
    if raw is not None and raw.retrieved_at and end[:10] > raw.retrieved_at[:10]:
        raise ValidationError(f'report time {end} is after the fetch ({raw.retrieved_at})')
    months = [o for o in result.observations if o.metric_id == 'gsdma.state_month_rain_mm']
    if not months or any(o.value is not None and not 0 <= o.value <= 2000 for o in months):
        raise ValidationError(f'state monthly rain missing or implausible: {[(o.period_start, o.value) for o in months]}')
