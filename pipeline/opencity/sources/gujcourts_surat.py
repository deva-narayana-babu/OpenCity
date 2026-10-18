"""Surat district courts: cases instituted, disposed and the case clearance rate (Virtual Justice Clock).

Page: https://gujcourts.guj.nic.in/dc_justice_clock/dc_institute_disposal_ccr.php?authority=GJSR01&estcode=ALL
"Virtual Justice Clock for District Judiciary of Gujarat - Institution, Disposal & Case Clearance Rate".
A plain PHP page (robots.txt is absent, so nothing is disallowed; no login or captcha):

    <select id="estlist1"> <option value='ALL'>ALL ESTABLISHMENTS UNDER DISTRICT COURT-SURAT</option>
                           <option value='GJSR15'>SMALL CAUSE COURT-SURAT</option> ... 14 establishments </select>
    table: DURATION | INSTITUTION | DISPOSAL | CCR
           Today | 275 | 77 | 28%      Last Day | ...   Last Week | ...   Last Month | ...
           This Year | ...              Last Year | 434812 | 433874 | 100%
    <p id="date">27/09/2026</p>          (the clock's date; JavaScript later overwrites it with the browser time)

The same URL with estcode=GJSR15 (etc.) returns one establishment, with that option marked selected='selected'.
fetch() takes the establishment list from the ALL page's dropdown and requests each one, so 15 documents per run.

-> ALL page: surat_district/surat (every establishment is in Surat district: Surat city courts plus the taluka
   courts of Olpad, Mangrol, Mandvi, Bardoli, Mahuva, Palsana, Kathor and Umarpada).
-> each establishment: geo level court_establishment, code = the lower-cased eCourts establishment code
   ('gjsr15'), parent surat_district/surat.

Periods: the page does not define its windows ("Last Week" = previous calendar week or last 7 days?). The ALL
figures for "Last Year" were identical on 2026-09-27 and 2026-10-17 and "Last Month" jumped from 13,223 to
184,195 institutions between those dates, which suggests calendar periods, but that is not published. So every
value is filed as an instant reading on the clock date with the window in dims.window (today, last_day,
last_week, last_month, this_year, last_year), and publisher_as_of = the clock date. "Today" is a running count
that can still grow after the fetch; a later fetch on the same clock date updates it (kept as a revision).
The clock date does not roll over at IST midnight: a fetch at 00:58 IST on 2026-10-18 still showed 17/10/2026.

The district (ALL) figures are the sum of the 14 establishments: on clock date 2026-10-17 they matched exactly in
every window for both counts. The dashboard must not add the two levels together.

CCR is published as a whole percent (disposal / institution); "--" (e.g. 1 instituted, 0 disposed) is stored as
not_reported. Pendency is not on this page (the page's script loads it from a separate POST endpoint,
reloadframependency.php, for another view), so none is stored.
"""
from __future__ import annotations

from datetime import date, timedelta

from ..model import Geo, Metric, Obs, Raw, Result, Source, ValidationError
from ..parse import clean, html_tables, num, parse_date
from ..surat import SURAT_DISTRICT

URL = 'https://gujcourts.guj.nic.in/dc_justice_clock/dc_institute_disposal_ccr.php'
AUTHORITY = 'GJSR01'            # District Court, Surat: the authority all Surat establishments sit under

SOURCE = Source(
    id='gujcourts_surat',
    name='Surat district courts: institution, disposal and case clearance rate',
    publisher='District Judiciary of Gujarat (High Court of Gujarat), Virtual Justice Clock',
    url=f'{URL}?authority={AUTHORITY}&estcode=ALL',
    module='courts',
    cadence='daily',
    interval_hours=24,
    geo_note='Surat district (all establishments under District Court-Surat) and each court establishment',
    licence_note='Public court statistics published by the Gujarat district judiciary',
    notes='Windows (Today ... Last Year) are as labelled by the publisher, relative to the clock date; their exact '
          'boundaries are not published. 15 GET requests per run (the district total and 14 establishments).',
    metrics=(
        Metric('courts.cases_instituted', 'Cases instituted', 'cases',
               'Cases instituted (filed) in the window dims.window, as shown on the Virtual Justice Clock on the '
               'clock date (period). Windows: today, last_day, last_week, last_month, this_year, last_year.'),
        Metric('courts.cases_disposed', 'Cases disposed', 'cases',
               'Cases disposed of in the window dims.window, as shown on the Virtual Justice Clock on the clock date.'),
        Metric('courts.clearance_rate_pct', 'Case clearance rate', '%',
               'Case clearance rate (disposed / instituted, whole percent as published) in the window dims.window. '
               'not_reported where the page shows "--".'),
    ),
)

COLUMNS = {'institution': 'courts.cases_instituted', 'disposal': 'courts.cases_disposed',
           'ccr': 'courts.clearance_rate_pct'}
WINDOWS = ('today', 'last_day', 'last_week', 'last_month', 'this_year', 'last_year')


def _options(text: str) -> list[tuple[str, str, bool]]:
    """<option value='GJSR15' selected='selected'>SMALL CAUSE COURT-SURAT</option> -> ('GJSR15', 'SMALL ...', True)."""
    out = []
    for chunk in text.split('<option')[1:]:
        attrs, _, rest = chunk.partition('>')
        value = attrs.split('value=', 1)[1].split()[0].strip('\'"') if 'value=' in attrs else ''
        out.append((value, clean(rest.split('</option>', 1)[0]), 'selected' in attrs))
    return out


def _clock_date(text: str) -> str:
    """'<p id="date">27/09/2026</p>' -> '2026-09-27'."""
    i = text.find('id="date">')
    if i < 0:
        raise ValueError('no clock date (<p id="date">) on the justice clock page')
    i += len('id="date">')
    return parse_date(text[i:text.find('<', i)]).isoformat()


def fetch(ctx):
    first = ctx.get(URL, params={'authority': AUTHORITY, 'estcode': 'ALL'})
    yield first
    for code, _, _ in _options(first.text):
        if code != 'ALL':
            yield ctx.get(URL, params={'authority': AUTHORITY, 'estcode': code}, soft=True)


def parse(raw: Raw) -> Result:
    text = raw.text
    day = _clock_date(text)
    options = _options(text)
    if not options or any(code != 'ALL' and not code.startswith('GJSR') for code, _, _ in options):
        raise ValueError(f'establishment list is not Surat district\'s: {[c for c, _, _ in options]}')
    selected = [(code, name) for code, name, sel in options if sel]
    res = Result(geos=[SURAT_DISTRICT])
    if selected:
        code, name = selected[0]
        level, geo = 'court_establishment', code.lower()
        res.geos.append(Geo(level, geo, name, 'surat_district', 'surat', note=f'eCourts establishment code {code}'))
    elif 'SURAT' in options[0][1].upper():
        level, geo = 'surat_district', 'surat'
    else:
        raise ValueError(f'cannot tell which establishment this page is for (first option {options[0]!r})')

    tables = [t for t in html_tables(raw.body) if t.find_row('duration', 'institution') == 0]
    if len(tables) != 1:
        raise ValueError(f'expected one DURATION/INSTITUTION table, found {len(tables)}')
    header = [h.lower() for h in tables[0].rows[0]]
    if header[0] != 'duration' or any(h not in COLUMNS for h in header[1:]):
        raise ValueError(f'unexpected justice clock header {tables[0].rows[0]!r}')
    for row in tables[0].rows[1:]:
        window = '_'.join(row[0].lower().split())
        if window not in WINDOWS:
            raise ValueError(f'unknown duration {row[0]!r}')
        for h, cell in zip(header[1:], row[1:]):
            v = num(cell)
            res.observations.append(Obs(COLUMNS[h], level, geo, day, day, value=v,
                                        status='reported' if v is not None else 'not_reported',
                                        dims={'window': window}, publisher_as_of=day))
    return res


def validate(result: Result, raw: Raw) -> None:
    obs = {(o.metric_id, o.dims['window']): o.value for o in result.observations}
    if len(obs) != len(WINDOWS) * len(COLUMNS):
        raise ValidationError(f'{len(obs)} values parsed, expected {len(WINDOWS) * len(COLUMNS)}')
    for w in WINDOWS:
        inst, disp, ccr = (obs[(m, w)] for m in COLUMNS.values())
        if inst is None or disp is None:
            raise ValidationError(f'{w}: instituted/disposed count missing')
        if not (0 <= inst <= 5_000_000 and 0 <= disp <= 5_000_000):
            raise ValidationError(f'{w}: implausible counts instituted={inst} disposed={disp}')
        # the published CCR must match disposal / institution, or the columns have moved
        if ccr is not None and inst > 0 and abs(ccr - 100 * disp / inst) > 1:
            raise ValidationError(f'{w}: CCR {ccr}% does not match {disp} disposed / {inst} instituted')
    for m in ('courts.cases_instituted', 'courts.cases_disposed'):
        if obs[(m, 'this_year')] < obs[(m, 'today')]:
            raise ValidationError(f'{m}: this year ({obs[(m, "this_year")]}) is less than today ({obs[(m, "today")]})')
    if raw is not None and raw.retrieved_at:
        day = date.fromisoformat(result.observations[0].period_start)
        fetched = date.fromisoformat(raw.retrieved_at[:10])
        if not fetched - timedelta(days=7) <= day <= fetched + timedelta(days=1):
            raise ValidationError(f'clock date {day} is far from the fetch date {fetched}')
