"""Surat district courts: pending cases (civil/criminal, by age, stage and case type) from the National Judicial Data Grid.

Publisher: National Judicial Data Grid (NJDG), part of the eCourts project of the e-Committee, Supreme Court of
India; built and hosted by the National Informatics Centre (NIC). NJDG aggregates the case data that each court
establishment uploads from its Case Information System (CIS).

Two requests per run, both to njdg.ecourts.gov.in (robots.txt returns 404, so nothing is disallowed). Neither
needs a login, a captcha, a cookie or a token. NJDG's case LISTS (the pop-ups that open when a figure is clicked,
and the case search) are behind a captcha; this adapter never calls them and stores aggregate counts only.

1. District page (HTML, GET):
       https://njdg.ecourts.gov.in/njdg_v3/?p=home/index&state_code=24~17&dist_code=14
   state_code '24~17' = Gujarat and dist_code '14' = SURAT, as in the page's own state/district dropdowns (both
   are marked "selected" on the page, and parse() checks that). The page is server-rendered:
       cards      "Civil Cases 32,002" | "Criminal Cases 1,08,352" | "Total Cases 1,40,354" | "Pre-Litigation / Pre-Trial"
       "Age wise pending cases"   Civil | Criminal | Total, one block per band:
                                  "Less than one year" 15,319 | 53,964 | 69,283 (49%)   ... "Above 10 Years"
       "Instituted in last month"  1,248 | 1,83,355 | 1,84,603        (Civil | Criminal | Total)
       "Disposal in last month"    1,565 | 1,95,082 | 1,96,647, then "Contested" and "Uncontested" blocks
       "Cases Listed Today", "Undated", "Excessive Dated Cases", "Cases Filed By Woman",
       "Cases Filed By Senior Citizen"   (each Civil | Criminal | Total, captioned "N% of Total Pending Cases")
       footer     "Last Updated : 23-10-2026"
   The page is read as visible text (parse.html_text), one value per line, taking the FIRST block with each
   label: the page repeats several blocks inside hidden layout copies (one hidden "Undated" copy is blank).
   A commented-out "Alerts" table in the HTML carries much larger numbers (e.g. "Cases Pending Registration
   900637"); HTML comments are not part of the visible text, so it is never read.

2. Pending dashboard (JSON, POST), what the page's "Pending Dashboard" tab loads:
       POST https://njdg.ecourts.gov.in/njdg_v3/?p=home/newPendDashboard
       form: ci_cri=1 (1 = civil and criminal together, 2 = civil, 3 = criminal), stage_ready=3, active_tab=pending,
             state_code=24~17, dist_code=14, ajax_req=true, app_token= (empty; the page's own token field is empty)
   The answer (served as text/html, with leading blank lines) is one JSON object of "~"-separated strings, labels
   quoted with "#" for spaces, e.g.
       "purpose_name": "\\"Process#Issue\\"~\\"Witness#Exmn.\\"~...",   "purpose_count": "70020~45947~..."
   Fields used:  purpose_name/purpose_count  (pending by stage, i.e. the purpose of the next hearing),
                 purposename/stagewise_count (NJDG's four stage groups), mattertype/cases_count (by case type),
                 caseChartcount (HTML table: Original / Appeal / Application / Execution),
                 year/year_count (pending by year of institution), insyear/ins_count/disp_count (cases instituted
                 and disposed per calendar year since 2018).
   Not used: delayName/delay_count. Those counts (6,866,010 for one reason on 2026-10-23) are far larger than the
   district's 1.4 lakh pending cases, so they are not Surat figures.
   The JSON names neither the district nor a date, so fetch() passes the page's "Last Updated" date and its total
   pending count in meta (as_of, pending_total); validate() requires the JSON totals to match the page.

Metrics (geo surat_district/surat; every establishment under District Court Surat: the Surat city courts and the
taluka courts). dims.civil_criminal is civil / criminal / total, as published (total = civil + criminal):
  njdg.pending_cases                    pending cases
  njdg.pending_by_age                   pending cases by dims.age_band (lt_1y, 1_3y, 3_5y, 5_10y, gt_10y)
  njdg.instituted_last_month            cases instituted "in last month"
  njdg.disposed_last_month              cases disposed "in last month", dims.disposal all / contested / uncontested
  njdg.pending_filed_by_women           pending cases filed by women ("Cases Filed By Woman")
  njdg.pending_filed_by_senior_citizens pending cases filed by senior citizens
  njdg.cases_listed_today               pending cases on the day's cause lists ("Cases Listed Today")
  njdg.undated_cases                    pending cases with no next hearing date
  njdg.excessive_dated_cases            pending cases whose next date is more than 3 months away
  from the JSON (civil and criminal together, no civil_criminal split):
  njdg.pending_by_stage, njdg.pending_by_stage_group, njdg.pending_by_case_type, njdg.pending_by_case_category,
  njdg.pending_by_filing_year, njdg.instituted_by_year, njdg.disposed_by_year
Units: cases. Snapshot figures are instant readings on the "Last Updated" date (publisher_as_of = that date).
Yearly flows have the calendar year as their period; the current year is year-to-date and grows until December.

Cadence: daily. The page shows only a date, no time. The footer read 23-10-2026 at 2026-10-24 02:02 IST, so it
is not a static edit date. An earlier read by the project's research step showed the same date with different
figures (pending 1,39,976 then, 1,40,354 at 02:02), so the figures can change more than once under one date
(the research notes say the courts' data is read twice a day). A later fetch for the same date is kept as a
revision.

Quirks and caveats:
- Age bands are counted in calendar years of institution, not exact days: on 2026-10-23 "Less than one year"
  (69,283) equals the cases instituted in 2026 plus 2025 (39,539 + 29,744), "1 to 3 Years" equals 2024 + 2023,
  and so on. A case filed in January 2025 is "less than one year" old until the end of 2026.
- The page's age bands add up to 2 more than its own totals (criminal 1,08,354 vs 1,08,352; total 1,40,356 vs
  1,40,354; "Above 10 Years" is 4,420 on the page but 4,418 in the JSON). Stored as published.
- The four stage groups add up to less than the total (1,39,969 vs 1,40,354 on 2026-10-23); the 26 detailed
  stages add up exactly. Stage names are NJDG's short purpose names, e.g. "Witness Exmn.", "313 Cr.PC".
- "Last month" is not defined on the page; it may not match the Virtual Justice Clock's "Last Month" window
  (source gujcourts_surat). The two sources count the same courts, so never add them together.
- Criminal institutions are very high (1,83,355 in the last month against 1,08,352 criminal cases pending, i.e.
  132% of all pending cases); most are quickly disposed petty / traffic-challan matters (98% of last month's
  disposals are uncontested).
- "Cases Filed By Woman / Senior Citizen" sit next to the last-month rows in the page's "Other Alerts" table, but
  their cards say "N% of Total Pending Cases"; they are read as pending cases filed by women / senior citizens.
- "Cases Listed Today" is filed under the "Last Updated" date; the page does not say which day "today" is.
- A blank count in the visible "Undated" card (only its hidden "Civil Count" caption left) is stored as
  not_reported, never 0. Any other blank or non-numeric block fails the document.
- If two stages (or case types, stage groups, years) decode to the same short name, their counts are added
  so the key stays unique (none did on 2026-10-23).
- "Excessive Dated Cases" is defined as "More than 3 Months" only in the page's commented-out Alerts table.
- The "Pre-Litigation / Pre-Trial" card (1,327) is not stored: the page does not define it.
- normalize() blanks the per-request script cache-buster (ecourts.js?v=...) and the server name in the footer
  ("S2", "S3"), so an unchanged page is archived once.

Licence: no open-data licence is stated on the dashboard page. The figures are public aggregate statistics
published by the eCourts project (Government of India); attribute "National Judicial Data Grid (NJDG)".
"""
from __future__ import annotations

import json
from datetime import date, timedelta

from ..archive import blank_number_after
from ..model import Metric, Obs, Raw, Result, Source, ValidationError
from ..parse import html_tables, html_text, num, parse_date, year_period
from ..surat import SURAT_DISTRICT

BASE = 'https://njdg.ecourts.gov.in/njdg_v3/'
STATE_CODE = '24~17'        # Gujarat
DIST_CODE = '14'            # SURAT
PAGE_URL = f'{BASE}?p=home/index&state_code={STATE_CODE}&dist_code={DIST_CODE}'
DASHBOARD_URL = f'{BASE}?p=home/newPendDashboard'
DASHBOARD_FORM = {'ci_cri': '1', 'stage_ready': '3', 'active_tab': 'pending', 'state_code': STATE_CODE,
                  'dist_code': DIST_CODE, 'ajax_req': 'true', 'app_token': ''}

M = 'njdg.'
SIDES = ('civil', 'criminal', 'total')       # the Civil | Criminal | Total columns, in page order

SOURCE = Source(
    id='njdg_surat',
    name='Surat district courts: pendency, age, stage and case type (NJDG)',
    publisher='National Judicial Data Grid (eCourts project, e-Committee of the Supreme Court of India; NIC)',
    url=PAGE_URL,
    module='courts',
    cadence='daily',
    interval_hours=24,
    geo_note='Surat district: all court establishments under District Court Surat (city and taluka courts)',
    licence_note='No licence stated; public aggregate statistics of the Government of India eCourts project. '
                 'Attribute "National Judicial Data Grid (NJDG)".',
    notes='Two requests per run: the district page (GET) and the pending-dashboard JSON (POST). No login, captcha '
          'or token is needed for either; NJDG case lists (captcha) are never requested. Snapshot figures are dated '
          'to the page\'s "Last Updated" date. Age bands are counted in calendar years of institution. Do not add '
          'these figures to gujcourts_surat (same courts).',
    metrics=(
        Metric(M + 'pending_cases', 'Pending cases (NJDG)', 'cases',
               'Cases pending in the district courts on the "Last Updated" date, by dims.civil_criminal '
               '(civil, criminal, total).'),
        Metric(M + 'pending_by_age', 'Pending cases by age (NJDG)', 'cases',
               'Pending cases by age band (dims.age_band: lt_1y, 1_3y, 3_5y, 5_10y, gt_10y) and dims.civil_criminal. '
               'NJDG counts age in calendar years of institution: lt_1y = instituted this year or last year.'),
        Metric(M + 'instituted_last_month', 'Cases instituted in the last month (NJDG)', 'cases',
               'Cases instituted "in last month" as shown on the "Last Updated" date, by dims.civil_criminal. '
               'NJDG does not define the window.'),
        Metric(M + 'disposed_last_month', 'Cases disposed in the last month (NJDG)', 'cases',
               'Cases disposed of "in last month", by dims.civil_criminal and dims.disposal (all, contested, '
               'uncontested; contested + uncontested = all).'),
        Metric(M + 'pending_filed_by_women', 'Pending cases filed by women (NJDG)', 'cases',
               'Pending cases filed by women ("Cases Filed By Woman", shown as a share of total pending cases), '
               'by dims.civil_criminal.'),
        Metric(M + 'pending_filed_by_senior_citizens', 'Pending cases filed by senior citizens (NJDG)', 'cases',
               'Pending cases filed by senior citizens ("Cases Filed By Senior Citizen", shown as a share of total '
               'pending cases), by dims.civil_criminal.'),
        Metric(M + 'cases_listed_today', 'Pending cases listed today (NJDG)', 'cases',
               'Pending cases on the cause lists of the day ("Cases Listed Today"), filed under the "Last Updated" '
               'date, by dims.civil_criminal.'),
        Metric(M + 'undated_cases', 'Undated pending cases (NJDG)', 'cases',
               'Pending cases with no next hearing date ("Undated"), by dims.civil_criminal.'),
        Metric(M + 'excessive_dated_cases', 'Pending cases with a next date over 3 months away (NJDG)', 'cases',
               'Pending cases whose next hearing date is more than 3 months away ("Excessive Dated Cases"), by '
               'dims.civil_criminal.'),
        Metric(M + 'pending_by_stage', 'Pending cases by stage (NJDG)', 'cases',
               'Pending cases (civil and criminal) by stage, i.e. the purpose of the next hearing (dims.stage, NJDG\'s '
               'short name such as "Process Issue" or "Witness Exmn."). The stages add up to the total pending.'),
        Metric(M + 'pending_by_stage_group', 'Pending cases by stage group (NJDG)', 'cases',
               'Pending cases (civil and criminal) by NJDG\'s stage group (dims.stage_group: Appearance/Service '
               'Related, Compliance/Steps/stay, Evidence/Argument/Judgement, Pleadings/Issues/Charge). The groups '
               'add up to slightly less than the total pending.'),
        Metric(M + 'pending_by_case_type', 'Pending cases by case type (NJDG)', 'cases',
               'Pending cases (civil and criminal) by CIS case type (dims.case_type, e.g. "MAGISTRIAL CASES", '
               '"CIV SUITS", "MACP"), names as published.'),
        Metric(M + 'pending_by_case_category', 'Pending cases by case category (NJDG)', 'cases',
               'Pending cases (civil and criminal) by category (dims.case_category: original, appeal, application, '
               'execution). The categories add up to the total pending.'),
        Metric(M + 'pending_by_filing_year', 'Pending cases by year of institution (NJDG)', 'cases',
               'Pending cases (civil and criminal) by the year the case was instituted (dims.filing_year).'),
        Metric(M + 'instituted_by_year', 'Cases instituted per year (NJDG)', 'cases',
               'Cases (civil and criminal) instituted in the calendar year. The current year is year-to-date '
               '(see publisher_as_of) and is revised as the year goes on.'),
        Metric(M + 'disposed_by_year', 'Cases disposed per year (NJDG)', 'cases',
               'Cases (civil and criminal) disposed of in the calendar year. The current year is year-to-date.'),
    ),
)

# page label -> (metric, extra dims); each label is followed by Civil | Criminal | Total
BLOCKS = [
    ('Less than one year', M + 'pending_by_age', {'age_band': 'lt_1y'}),
    ('1 to 3 Years', M + 'pending_by_age', {'age_band': '1_3y'}),
    ('3 to 5 Years', M + 'pending_by_age', {'age_band': '3_5y'}),
    ('5 to 10 Years', M + 'pending_by_age', {'age_band': '5_10y'}),
    ('Above 10 Years', M + 'pending_by_age', {'age_band': 'gt_10y'}),
    ('Instituted in last month', M + 'instituted_last_month', {}),
    ('Disposal in last month', M + 'disposed_last_month', {'disposal': 'all'}),
    ('Contested', M + 'disposed_last_month', {'disposal': 'contested'}),
    ('Uncontested', M + 'disposed_last_month', {'disposal': 'uncontested'}),
    ('Cases Filed By Woman', M + 'pending_filed_by_women', {}),
    ('Cases Filed By Senior Citizen', M + 'pending_filed_by_senior_citizens', {}),
    ('Cases Listed Today', M + 'cases_listed_today', {}),
    ('Undated', M + 'undated_cases', {}),
    ('Excessive Dated Cases', M + 'excessive_dated_cases', {}),
]
CARDS = ('Civil Cases', 'Criminal Cases', 'Total Cases')     # one number each, in SIDES order

# JSON field pairs (labels, counts) -> (metric, dims key)
SERIES = [
    ('purpose_name', 'purpose_count', M + 'pending_by_stage', 'stage'),
    ('purposename', 'stagewise_count', M + 'pending_by_stage_group', 'stage_group'),
    ('mattertype', 'cases_count', M + 'pending_by_case_type', 'case_type'),
    ('year', 'year_count', M + 'pending_by_filing_year', 'filing_year'),
]


def fetch(ctx):
    page = ctx.get(PAGE_URL)
    yield page
    lines = _lines(page.text)
    meta = {'as_of': _as_of(lines), 'pending_total': _values(lines, 'Total Cases', 1)[0]}
    yield ctx.post(DASHBOARD_URL, form=DASHBOARD_FORM, meta=meta)


def normalize(body: bytes) -> bytes:
    """Blank what changes on every request: 'ecourts.js?v=1791523696' and the server name 'S3' in the footer."""
    body = blank_number_after(body, b'ecourts.js?v=')
    return blank_number_after(body, b'contrastFiltertxt m-0">S')


def _lines(text: str) -> list[str]:
    return html_text(text).split('\n')


def _as_of(lines: list[str]) -> str:
    """'Last Updated : 23-10-2026' -> '2026-10-23'."""
    for line in lines:
        if line.startswith('Last Updated'):
            return parse_date(line.split(':', 1)[1]).isoformat()
    raise ValueError('no "Last Updated" date on the NJDG page')


def _values(lines: list[str], label: str, n: int = 3) -> list[int | None]:
    """The n numbers on the lines after the first line equal to label, e.g.
    ['Undated', '0% of Total Pending Cases', '7 Civil Count', '28 Criminal Count', '35 Total Count'] -> [7, 28, 35].
    A share caption ('2% of ...') before the numbers is skipped; '69,283 (49%)' -> 69283.
    A blank Undated cell leaves only its hidden caption ('Civil Count' with no number) -> None (not_reported)."""
    if label not in lines:
        raise ValueError(f'{label!r} not found on the NJDG page')
    out = []
    for line in lines[lines.index(label) + 1:]:
        first = line.split()[0].replace(',', '')
        if line in ('Civil Count', 'Criminal Count', 'Total Count'):
            out.append(None)
            if len(out) == n:
                return out
        elif first.isdigit():
            out.append(int(first))
            if len(out) == n:
                return out
        elif out or '%' not in line:
            raise ValueError(f'unexpected line {line!r} after {label!r} on the NJDG page')
    raise ValueError(f'fewer than {n} numbers after {label!r} on the NJDG page')


def _obs(metric: str, day: str, value, dims: dict) -> Obs:
    return Obs(metric, 'surat_district', 'surat', day, day, value=value,
               status='reported' if value is not None else 'not_reported', dims=dims, publisher_as_of=day)


def _parse_page(raw: Raw) -> Result:
    text = raw.text
    if 'selected>Gujarat</option>' not in text or 'selected>SURAT</option>' not in text:
        raise ValueError('this is not the NJDG page for Gujarat / SURAT (district not selected in the dropdowns)')
    lines = _lines(text)
    day = _as_of(lines)
    res = Result(geos=[SURAT_DISTRICT])
    for side, label in zip(SIDES, CARDS):
        res.observations.append(_obs(M + 'pending_cases', day, _values(lines, label, 1)[0], {'civil_criminal': side}))
    for label, metric, dims in BLOCKS:
        for side, v in zip(SIDES, _values(lines, label)):
            res.observations.append(_obs(metric, day, v, {'civil_criminal': side, **dims}))
    return res


def _series(d: dict, names: str, counts: str) -> list[tuple[str, float | None]]:
    """'"Process#Issue"~"Witness#Exmn."' + '70020~45947' -> [('Process Issue', 70020.0), ('Witness Exmn.', 45947.0)],
    decoded the way NJDG's own home.js does it ('~' separates items, '#' stands for a space)."""
    labels = json.loads('[' + d[names].replace('~', ',') + ']')
    values = d[counts].split('~')
    if len(labels) != len(values):
        raise ValueError(f'{names} has {len(labels)} labels but {counts} has {len(values)} values')
    return [(' '.join(str(lab).replace('#', ' ').split()), num(v)) for lab, v in zip(labels, values)]


def _parse_dashboard(raw: Raw) -> Result:
    day = raw.meta.get('as_of')
    if not day:
        raise ValueError('pending-dashboard JSON needs meta.as_of (the district page\'s "Last Updated" date)')
    d = json.loads(raw.body)
    res = Result(geos=[SURAT_DISTRICT])
    for names, counts, metric, key in SERIES:
        totals: dict[str, float | None] = {}
        for label, v in _series(d, names, counts):
            if label in totals:     # the same short name twice: add them up so the key stays unique
                v = None if v is None or totals[label] is None else totals[label] + v
            totals[label] = v
        for label, v in totals.items():
            res.observations.append(_obs(metric, day, v, {key: label}))

    (table,) = html_tables(d['caseChartcount'])
    for row in table.rows[1:]:
        if row[0].lower().startswith('total'):
            continue
        res.observations.append(_obs(M + 'pending_by_case_category', day, num(row[1]),
                                     {'case_category': row[0].lower()}))

    for year, ins, disp in zip(d['insyear'].split('~'), d['ins_count'].split('~'), d['disp_count'].split('~')):
        start, end = year_period(int(year))
        for metric, v in ((M + 'instituted_by_year', num(ins)), (M + 'disposed_by_year', num(disp))):
            res.observations.append(Obs(metric, 'surat_district', 'surat', start, end, value=v,
                                        status='reported' if v is not None else 'not_reported', publisher_as_of=day))
    return res


def parse(raw: Raw) -> Result:
    if raw.body.lstrip()[:1] == b'{':
        return _parse_dashboard(raw)
    return _parse_page(raw)


def _check_date(day: str, raw: Raw) -> None:
    if raw is None or not raw.retrieved_at:
        return
    fetched = date.fromisoformat(raw.retrieved_at[:10])
    if not fetched - timedelta(days=7) <= date.fromisoformat(day) <= fetched + timedelta(days=1):
        raise ValidationError(f'NJDG date {day} is far from the fetch date {fetched}')


def _validate_page(result: Result, raw: Raw) -> None:
    v = {(o.metric_id, o.dims.get('civil_criminal'), o.dims.get('age_band') or o.dims.get('disposal')): o.value
         for o in result.observations}
    pending = {s: v[(M + 'pending_cases', s, None)] for s in SIDES}
    if pending['civil'] + pending['criminal'] != pending['total']:
        raise ValidationError(f'pending civil + criminal != total: {pending}')
    if not 10_000 <= pending['total'] <= 2_000_000:
        raise ValidationError(f'implausible pending total {pending["total"]} for Surat district')
    for s in SIDES:
        by_age = sum(v[(M + 'pending_by_age', s, band)] for band in ('lt_1y', '1_3y', '3_5y', '5_10y', 'gt_10y'))
        if abs(by_age - pending[s]) > 0.001 * pending['total']:     # the page is off by 2 cases on 2026-10-23
            raise ValidationError(f'{s}: age bands add up to {by_age}, pending is {pending[s]}')
        disposed = [v[(M + 'disposed_last_month', s, k)] for k in ('all', 'contested', 'uncontested')]
        if disposed[1] + disposed[2] != disposed[0]:
            raise ValidationError(f'{s}: contested + uncontested != disposed last month ({disposed})')
        for m in ('pending_filed_by_women', 'pending_filed_by_senior_citizens', 'undated_cases',
                  'excessive_dated_cases', 'cases_listed_today'):
            if (v[(M + m, s, None)] or 0) > pending[s]:
                raise ValidationError(f'{s}: {m} ({v[(M + m, s, None)]}) exceeds pending ({pending[s]})')
    for m, k in (('instituted_last_month', None), ('disposed_last_month', 'all')):
        civ, cri, tot = (v[(M + m, s, k)] for s in SIDES)
        if civ + cri != tot or tot > 2_000_000:
            raise ValidationError(f'{m}: civil {civ} + criminal {cri} != total {tot}, or implausible')
    _check_date(result.observations[0].period_start, raw)


def _validate_dashboard(result: Result, raw: Raw) -> None:
    sums: dict[str, float] = {}
    rows: dict[str, int] = {}
    for o in result.observations:
        sums[o.metric_id] = sums.get(o.metric_id, 0) + (o.value or 0)
        rows[o.metric_id] = rows.get(o.metric_id, 0) + 1
        if o.value is not None and not 0 <= o.value <= 5_000_000:
            raise ValidationError(f'implausible {o.metric_id} {o.value} ({o.dims}, {o.period_start})')
    total = sums.get(M + 'pending_by_stage', 0)
    for m in ('pending_by_case_type', 'pending_by_case_category', 'pending_by_filing_year'):
        if sums.get(M + m) != total:
            raise ValidationError(f'{m} adds up to {sums.get(M + m)}, stages add up to {total}')
    if sums.get(M + 'pending_by_stage_group', 0) > total:
        raise ValidationError('stage groups add up to more than the total pending')
    if rows.get(M + 'pending_by_stage', 0) < 5 or rows.get(M + 'pending_by_case_type', 0) < 5:
        raise ValidationError(f'too few stages / case types parsed: {rows}')
    if rows.get(M + 'pending_by_case_category') != 4 or not rows.get(M + 'instituted_by_year'):
        raise ValidationError(f'case categories or yearly flows missing: {rows}')
    expected = raw.meta.get('pending_total') if raw is not None else None
    if expected and abs(total - expected) > 0.01 * expected:
        raise ValidationError(f'JSON total pending {total} does not match the district page ({expected}): '
                              f'wrong district or a different snapshot')
    day = raw.meta.get('as_of') if raw is not None else None
    years = [o.period_start[:4] for o in result.observations if o.metric_id == M + 'instituted_by_year']
    years += [o.dims['filing_year'] for o in result.observations if o.metric_id == M + 'pending_by_filing_year']
    if day and max(years) > day[:4]:
        raise ValidationError(f'year {max(years)} is after the NJDG date {day}')
    _check_date(result.observations[0].publisher_as_of, raw)


def validate(result: Result, raw: Raw) -> None:
    if any(o.metric_id == M + 'pending_cases' for o in result.observations):
        _validate_page(result, raw)
    else:
        _validate_dashboard(result, raw)
