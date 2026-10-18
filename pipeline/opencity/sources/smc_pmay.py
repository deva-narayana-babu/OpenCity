"""SMC affordable housing (PMAY-Urban, AHP vertical): project list with flats, contractor, tender value and status.

Page: https://www.suratmunicipal.gov.in/Departments/PradhanMantriAwasYojana  (Department of Affordable Housing)
The "Projects" tab holds two tables, "Completed Projects" and "Work in Progress Projects" (both captioned
"LIG Housing"), with the same columns:

    Sr. No. (blank, numbered by CSS) | Project Name | Location | Name of Contractor | No. of Flats |
    Tender Amount Rs (in Lacs) | Status
    ... one row per project ...
    Total (colspan 4) | <flats> | <tender> |

Snapshot 2026-09-28: 46 completed projects (23,422 flats) and 11 in progress (6,454 flats).

-> one 'housing_project' record per row (the page is the complete list, so projects that disappear get closed),
   keyed by project name + TP scheme + final plot (e.g. 'suman-jyot-tp-9-fp-164'; the whole location text if
   those cannot be split out) because names repeat for different plots (SUMAN MALHAR S.P.2 / S.P.3, SUMAN VANDAN
   P1 / P2). A change of status keeps the key, so it shows up as a new version of the record.
-> smc_city observations per status: number of projects and flats, counted from the project rows.

Quirks of the page, kept as published:
- The "Total" row of the work-in-progress table repeats the completed table's total (23422 flats, 150686.87
  lakh), so the published Total rows are not stored; the aggregates are counted from the rows instead
  (for completed projects the row sum equals the published 23,422 flats, but the published tender Total of
  150,686.87 lakh is not the row sum of 157,601.84 lakh, so tender amounts are only kept per project).
- Two projects list two contractors and two tender amounts (Package-I / Package-II) in one cell. The amounts are
  kept as a list (tender_amounts_lakh) and summed in tender_amount_lakh; the contractor cell is kept as one string.
- SUMAN ADARSH (408 flats) shows a tender amount of 29.74 lakh, far below every other project; stored as published.
- Location strings are inconsistent ("T.P.No.9 (Palanpore-Bhesan), F.P.No. 164", "TP.No.62(...)", "T.P.No.48
  Bhestan, F.P.No.85"); tp_scheme / tp_area / final_plot are split out best-effort and the full text is kept.

Dating: the page has no data date of its own. Its footer "Last Updated: September 12, 2023 05:04 PM" is the CMS
edit date of this page (it differs from page to page across SMC's site and is years older than the snapshot), so
the counts are filed as an instant reading on that date with publisher_as_of set to it. A later edit of the page
moves the date and starts a new point in the series.
"""
from __future__ import annotations

from datetime import datetime

from ..model import Metric, Obs, Raw, Record, Result, Source, ValidationError
from ..parse import clean, html_tables, num
from ..surat import SMC

URL = 'https://www.suratmunicipal.gov.in/Departments/PradhanMantriAwasYojana'

SOURCE = Source(
    id='smc_pmay',
    name='SMC PMAY affordable housing projects',
    publisher='Surat Municipal Corporation, Department of Affordable Housing',
    url=URL,
    module='housing',
    cadence='static',
    interval_hours=24 * 7,          # the page was last edited in 2023; weekly is more than enough
    record_types=('housing_project',),
    geo_note='SMC city (projects are on SMC town-planning schemes; each record keeps its TP scheme and plot)',
    licence_note='Surat Municipal Corporation web page; public information',
    notes='Counts are dated to the page footer "Last Updated" date. The published Total rows are not used '
          '(the work-in-progress Total repeats the completed one).',
    metrics=(
        Metric('pmay.projects', 'PMAY housing projects', 'projects',
               'Number of SMC PMAY (affordable housing) projects listed on the page, by dims.status '
               '(completed / work_in_progress). Counted from the project rows.'),
        Metric('pmay.flats', 'Flats in PMAY housing projects', 'flats',
               'Sum of "No. of Flats" over the listed projects, by dims.status. not_reported if any project in '
               'that group has a blank flat count.'),
    ),
)

STATUSES = {'completed': 'completed', 'work in progress': 'work_in_progress'}

# header text -> attribute name; first match wins
COLUMNS = [
    ('project name', 'name'),
    ('location', 'location'),
    ('contractor', 'contractor'),
    ('flats', 'flats'),
    ('tender', 'tender'),
    ('status', 'status'),
]


def fetch(ctx):
    yield ctx.get(URL)


def _slug(s: str) -> str:
    out = ''.join(ch if ch.isalnum() else ' ' for ch in s.lower())
    return '-'.join(out.split())


def _strip_no(s: str) -> str:
    """' No.  48 (Bhestan)' -> '48 (Bhestan)'."""
    s = s.strip(' .,')
    if s.lower().startswith('no'):
        s = s[2:]
    return s.strip(' .,')


def _tp_fp(location: str) -> tuple[str | None, str | None, str | None]:
    """'T.P.No.9 (Palanpore-Bhesan), F.P.No. 164' -> ('9', 'Palanpore-Bhesan', '164')."""
    s = location.replace('TP.', 'T.P.').replace('FP.', 'F.P.')
    tp_part, found, fp_part = s.partition('F.P.')
    if not found or 'T.P.' not in tp_part:
        return None, None, None
    tp_part = _strip_no(tp_part.split('T.P.', 1)[1])
    digits = len(tp_part) - len(tp_part.lstrip('0123456789'))
    tp = str(int(tp_part[:digits])) if digits else None
    area = tp_part[digits:].strip(' ,()') or None
    return tp, area, _strip_no(fp_part) or None


def _last_updated(text: str) -> str:
    """Footer '<span id="spnLastUpdated">September 12, 2023 05:04 PM</span>' -> '2023-09-12'."""
    i = text.find('id="spnLastUpdated"')
    if i < 0:
        raise ValueError('no "Last Updated" footer on the PMAY page')
    start = text.find('>', i) + 1
    stamp = clean(text[start:text.find('<', start)])
    return datetime.strptime(stamp, '%B %d, %Y %I:%M %p').date().isoformat()


def _int(cell: str) -> int | None:
    v = num(cell)
    if v is not None and v != int(v):
        raise ValueError(f'flat count {cell!r} is not a whole number')
    return None if v is None else int(v)


def parse(raw: Raw) -> Result:
    day = _last_updated(raw.text)
    res = Result(geos=[SMC], complete_record_types=('housing_project',))
    projects = {s: 0 for s in STATUSES.values()}
    flats: dict[str, int | None] = {s: 0 for s in STATUSES.values()}
    for table in html_tables(raw.body):
        if table.find_row('project name', 'flats') != 0:
            continue
        col = {}
        for j, h in enumerate(table.rows[0]):
            for needle, attr in COLUMNS:
                if needle in h.lower() and attr not in col:
                    col[attr] = j
                    break
        if len(col) != len(COLUMNS):
            raise ValueError(f'unexpected PMAY table header {table.rows[0]!r}')
        for row in table.rows[1:]:
            name = row[col['name']]
            if not name or name.lower() == 'total':
                continue
            status_text = row[col['status']].lower()
            if status_text not in STATUSES:
                raise ValueError(f'unknown project status {row[col["status"]]!r} for {name}')
            status = STATUSES[status_text]
            n_flats = _int(row[col['flats']])
            amounts = [num(x) for x in row[col['tender']].split()]
            location = row[col['location']]
            tp, area, fp = _tp_fp(location)
            key = _slug(f'{name} tp {tp} fp {fp}' if tp and fp else f'{name} {location}')
            res.records.append(Record('housing_project', key, {
                'name': name,
                'status': status,
                'location': location,
                'tp_scheme': tp,
                'tp_area': area,
                'final_plot': fp,
                'contractor': row[col['contractor']] or None,
                'flats': n_flats,
                'tender_amount_lakh': round(sum(amounts), 2) if amounts else None,
                'tender_amounts_lakh': amounts,
                'housing_type': table.caption or None,
            }))
            projects[status] += 1
            flats[status] = None if (n_flats is None or flats[status] is None) else flats[status] + n_flats

    for status in STATUSES.values():
        for metric, v in (('pmay.projects', projects[status]), ('pmay.flats', flats[status])):
            res.observations.append(Obs(metric, 'smc_city', 'smc', day, day,
                                        value=None if v is None else float(v),
                                        status='reported' if v is not None else 'not_reported',
                                        dims={'status': status}, publisher_as_of=day))
    return res


def validate(result: Result, raw: Raw) -> None:
    n = {s: 0 for s in STATUSES.values()}
    for r in result.records:
        a = r.attrs
        n[a['status']] += 1
        if a['flats'] is not None and not 20 <= a['flats'] <= 5000:
            raise ValidationError(f'{a["name"]}: implausible flat count {a["flats"]}')
        for amount in a['tender_amounts_lakh']:
            if amount is None or not 0 < amount < 50000:    # 50000 lakh = Rs 500 crore for one project
                raise ValidationError(f'{a["name"]}: implausible tender amount {amount} lakh')
    if sum(n.values()) < 30 or not n['completed']:
        raise ValidationError(f'only {n} PMAY projects parsed; page layout may have changed')
    total = sum(o.value or 0 for o in result.observations if o.metric_id == 'pmay.flats')
    if total > 300000:
        raise ValidationError(f'{total} PMAY flats is implausible for SMC')
    day = result.observations[0].period_start
    if day < '2015-06-25' or (raw is not None and raw.retrieved_at and day > raw.retrieved_at[:10]):
        raise ValidationError(f'page date {day} is before PMAY-U began or after the fetch')
