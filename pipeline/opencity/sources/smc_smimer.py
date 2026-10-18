"""SMIMER hospital miscellaneous statistics: milk bank, blood bank, eye bank and ICU (monthly).

Page: https://www.suratmunicipal.gov.in/smimer/Hospital/SHMiscellaneousStatistics
SMIMER (Surat Municipal Institute of Medical Education and Research) is the SMC-run medical college
hospital, so every value is filed under geo level `facility`, code `smimer` (parent smc_city).

The page has four sections, each a stack of 12-month tables (calendar years from 2015, financial
years April-March for 2011-12 to 2014-15); the section and the period come from the heading text
just before each table ("Blood Bank Statistics from January 2026 to December 2026"):

  Milk Bank   rows: collection (ml), milk given to newborns (ml), donor mothers, newborns receiving milk
  Blood Bank  rows: units collected (camp / blood bank / replacement / grand total), units issued by
              component under a "Smimer Hospital" sub-heading, units issued to other hospitals,
              donation camps
  Eye Bank    rows: eyes collected, eyes utilised (keratoplasty / sent to other eye bank / paediatric)
  I.C.U.      one row per month, one column per ICU (MICU, ICCU, SICU, PICU, NCU, RICU, OBS. ICU),
              then Total / Bed / Occupancy % / per-month and per-day averages

What is deliberately NOT emitted (ambiguous or derived):
  - Blood bank "Units Issued > Grand Total": in some months it equals the component rows, in others the
    component rows plus "Other Hospital" (and Jul 2020 matches neither), so its meaning is unclear.
  - Blood bank "Total Voluntary" (always camp + blood bank on this page; derivable, would double count).
  - Eye bank "Retina Clinical": listed under "No. of Eyes Utilised" but its values (e.g. 35-54 a month in
    2017) exceed the eyes collected, so it is not a count of eyes utilised. Mostly '-' anyway.
  - ICU Total, Occupancy %, pt./Month, pt./Day (Avg/Month, Avg/Day): derived from the monthly rows and beds.
  - ICU tables whose month rows contradict their heading: the tables headed "January 2016 to December
    2016" and "January 2015 to December 2015" list April..March, so the year of each row is ambiguous.
    They are skipped (see SKIPPED_NOTE); the same check skips any future table with that problem.

Overlapping tables (calendar 2015 vs FY 2014-15 / 2015-16) repeat the same months with the same values;
each month is emitted once. If two tables ever disagree on a month, that value is dropped rather than
choosing one (analyse() returns the conflicts and the skipped tables for inspection).
Months with no value in any row (future months of the current year) are not emitted; a blank or '-'
cell in a month that has other values becomes status 'not_reported'.
"""
from __future__ import annotations

import re

from ..model import Geo, Metric, Obs, Raw, Result, Source, ValidationError
from ..parse import html_tables, month_no, month_period, month_year, num
from ..surat import SMC

URL = 'https://www.suratmunicipal.gov.in/smimer/Hospital/SHMiscellaneousStatistics'

GEO = Geo('facility', 'smimer',
          'SMIMER hospital (Surat Municipal Institute of Medical Education and Research)', 'smc_city', 'smc',
          note='Medical college hospital run by Surat Municipal Corporation')

SKIPPED_NOTE = (
    'Skipped as ambiguous or derived: blood-bank issued Grand Total (composition varies), Total Voluntary '
    '(derivable), eye-bank Retina Clinical (not eyes utilised), ICU Total/Occupancy/averages (derived), and ICU '
    'tables whose month rows contradict their heading (Jan-Dec 2015 and Jan-Dec 2016 tables list April..March).')

SOURCE = Source(
    id='smc_smimer',
    name='SMIMER hospital statistics: milk, blood and eye bank, ICU (monthly)',
    publisher='Surat Municipal Corporation, SMIMER hospital',
    url=URL,
    module='health',
    cadence='monthly',
    interval_hours=24 * 7,          # the page gains one month at a time, with a lag
    geo_note='One SMC-run hospital (geo level facility, code smimer)',
    licence_note='Surat Municipal Corporation web page; public information',
    notes=SKIPPED_NOTE,
    metrics=(
        Metric('smimer.milk_collected_ml', 'Human milk bank: milk collected', 'ml',
               'Amount of milk collected by the SMIMER human milk bank in the month.'),
        Metric('smimer.milk_given_ml', 'Human milk bank: milk given to newborns', 'ml',
               'Amount of milk donated to newborns in the month.'),
        Metric('smimer.milk_donor_mothers', 'Human milk bank: donor mothers', 'mothers',
               'Number of donor mothers in the month.'),
        Metric('smimer.milk_recipient_newborns', 'Human milk bank: newborns receiving milk', 'newborns',
               'Number of newborns who received milk in the month.'),
        Metric('smimer.blood_units_collected', 'Blood bank: units collected, by type of donation', 'units',
               'Blood units collected in the month; dims.donation = voluntary_camp, voluntary_blood_bank or '
               'replacement. These add up to smimer.blood_units_collected_total.'),
        Metric('smimer.blood_units_collected_total', 'Blood bank: units collected (grand total)', 'units',
               'Grand total of blood units collected in the month, as published.'),
        Metric('smimer.blood_components_issued', 'Blood bank: units issued, by component', 'units',
               'Units issued in the month by component (dims.component), as listed under the page\'s '
               '"Smimer Hospital" sub-heading. The page is not consistent about whether these rows also '
               'cover units issued to other hospitals (its Grand Total sometimes adds the Other Hospital '
               'row, sometimes not), so do not add smimer.blood_units_issued_other_hospitals to them blindly.'),
        Metric('smimer.blood_units_issued_other_hospitals', 'Blood bank: units issued to other hospitals', 'units',
               'Row "Other Hospital" under "No. of Blood Units Issued".'),
        Metric('smimer.blood_donation_camps', 'Blood bank: blood donation camps held', 'camps',
               'Number of blood donation camps in the month.'),
        Metric('smimer.eyes_collected', 'Eye bank: eyes collected', 'eyes',
               'Number of eyes collected by the eye bank in the month.'),
        Metric('smimer.eyes_utilised', 'Eye bank: eyes utilised, by use', 'eyes',
               'Eyes utilised in the month, dims.use = keratoplasty, sent_to_other_eye_bank or paediatric '
               '(row labels as published under "No. of Eyes Utilised").'),
        Metric('smimer.icu_patient_count', 'ICU patients (monthly figure per ICU)', 'patients',
               'Monthly figure per intensive care unit (dims.unit). The page does not say whether these are '
               'admissions or patient-days; its own occupancy row (figure / days / beds) treats them as '
               'patient-days.'),
        Metric('smimer.icu_beds', 'ICU beds', 'beds',
               'Beds per intensive care unit (dims.unit) as stated in the table for that year.'),
    ),
)

# table heading, e.g. matches 'Blood Bank Statistics from January 2026 to December 2026' (at the end of the text)
_HEADING = re.compile(r'(Milk Bank|Blood Bank|Eye Bank|I\.C\.U\.) Statistics from ([A-Za-z]+) (\d{4}) '
                      r'to ([A-Za-z]+) (\d{4})\s*$')
# section label in the heading -> section key
_SECTION = {'Milk Bank': 'milk', 'Blood Bank': 'blood', 'Eye Bank': 'eye', 'I.C.U.': 'icu'}

# (row group, row label) -> (metric, dims) ; None = known row deliberately not emitted
# Patterns are searched in the lower-cased cells, e.g. r'^grand total$' matches the label 'Grand Total' and
# r'in camp' matches 'In Camp (Voluntary)'; a None label pattern matches any label in that group.
_ROWS = {
    'milk': [
        (r'amount of milk collection', None, ('smimer.milk_collected_ml', {})),
        (r'milk donated to new ?born', None, ('smimer.milk_given_ml', {})),
        (r'no\. of donor mothers', None, ('smimer.milk_donor_mothers', {})),
        (r'new ?born receiving milk', None, ('smimer.milk_recipient_newborns', {})),
    ],
    'blood': [
        (r'units collected', r'in camp', ('smimer.blood_units_collected', {'donation': 'voluntary_camp'})),
        (r'units collected', r'in blood bank', ('smimer.blood_units_collected', {'donation': 'voluntary_blood_bank'})),
        (r'units collected', r'^total voluntary$', None),
        (r'units collected', r'^replacement$', ('smimer.blood_units_collected', {'donation': 'replacement'})),
        (r'units collected', r'^grand total$', ('smimer.blood_units_collected_total', {})),
        (r'units issued', r'^smimer hospital$', None),            # sub-heading row
        (r'units issued', r'^whole blood$', ('smimer.blood_components_issued', {'component': 'whole_blood'})),
        (r'units issued', r'^red cell concentrate$',
         ('smimer.blood_components_issued', {'component': 'red_cell_concentrate'})),
        (r'units issued', r'^fresh frozen plasma$',
         ('smimer.blood_components_issued', {'component': 'fresh_frozen_plasma'})),
        (r'units issued', r'^platelet concentrate$',
         ('smimer.blood_components_issued', {'component': 'platelet_concentrate'})),
        (r'units issued', r'^cryoprecipitate$', ('smimer.blood_components_issued', {'component': 'cryoprecipitate'})),
        (r'units issued', r'^cpp$', ('smimer.blood_components_issued', {'component': 'cryo_poor_plasma'})),
        (r'units issued', r'^other hospital$', ('smimer.blood_units_issued_other_hospitals', {})),
        (r'units issued', r'^grand total$', None),                 # composition varies, see module docstring
        (r'blood donation camps', None, ('smimer.blood_donation_camps', {})),
    ],
    'eye': [
        (r'eyes collected', None, ('smimer.eyes_collected', {})),
        (r'eyes utilised', r'^keratoplasty$', ('smimer.eyes_utilised', {'use': 'keratoplasty'})),
        (r'eyes utilised', r'other eye bank', ('smimer.eyes_utilised', {'use': 'sent_to_other_eye_bank'})),
        (r'eyes utilised', r'^paediatric$', ('smimer.eyes_utilised', {'use': 'paediatric'})),
        (r'eyes utilised', r'^retina clinical$', None),            # not a count of eyes, see docstring
    ],
}

# ICU column header (lower-cased) -> unit slug, e.g. r'^n(i)?cu\b' matches 'ncu (nicu + inicu)' and 'nicu'
_ICU_UNITS = [
    (r'^micu$', 'micu'), (r'^iccu$', 'iccu'), (r'^sicu$', 'sicu'), (r'^picu$', 'picu'),
    (r'^n(i)?cu\b', 'ncu'), (r'^ricu$', 'ricu'), (r'^obs\.? ?icu$', 'obs_icu'),
]
_MONTH_NAMES = {'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september',
                'october', 'november', 'december'}
# derived ICU summary rows, e.g. matches 'Total', 'OCCU %', 'Occu. %', 'pt./Month', 'Avg/Day'
_ICU_DERIVED = re.compile(r'^(total|occu\.? ?%|pt\./month|pt\./day|avg/month|avg/day)$', re.I)


def fetch(ctx):
    yield ctx.get(URL)


def _row_spec(section: str, group: str, label: str):
    g, lab = group.strip().lower(), label.strip().lower()
    for gpat, lpat, spec in _ROWS[section]:
        if re.search(gpat, g) and (lpat is None or re.search(lpat, lab)):
            return spec
    raise ValueError(f'unknown {section} row {group!r} / {label!r}')


def _icu_unit(h: str) -> str:
    t = h.strip().lower()
    for pat, slug in _ICU_UNITS:
        if re.search(pat, t):
            return slug
    raise ValueError(f'unknown ICU column {h!r}')


def _months(start_m: int, start_y: int, n: int = 12) -> list[tuple[int, int]]:
    out, y, m = [], start_y, start_m
    for _ in range(n):
        out.append((y, m))
        m += 1
        if m > 12:
            y, m = y + 1, 1
    return out


def _parse_monthly_columns(table, section, months, add):
    """Milk/blood/eye tables: header row 'Month | Month | Jan 2026 | ...', then (group, label, values...)."""
    hdr = table.rows[0]
    cols = [month_year(c) for c in hdr[2:]]
    if cols != months:
        return f'columns {hdr[2]}..{hdr[-1]} do not match heading'
    # a month is published if any data row has a value in it
    data_rows = [r for r in table.rows[1:] if len(r) >= 2 + len(cols)]
    published = [any(r[2 + j].strip() not in ('',) for r in data_rows
                     if _row_spec(section, r[0], r[1]) is not None) for j in range(len(cols))]
    for r in data_rows:
        spec = _row_spec(section, r[0], r[1])
        if spec is None:
            continue
        metric, dims = spec
        for j, (y, m) in enumerate(cols):
            if published[j]:
                add(metric, month_period(y, m), num(r[2 + j]), dims)
    return None


def _parse_icu(table, months, period, add):
    # header row: first cell 'Month' and a 'MICU' column, e.g. ['Month', 'MICU', 'ICCU', ...]
    hi = next((i for i, r in enumerate(table.rows) if r and r[0].strip().lower() == 'month'
               and any(re.search(r'micu', c, re.I) for c in r)), -1)
    if hi < 0:
        raise ValueError('ICU table without a MICU header row')
    units = [_icu_unit(c) for c in table.rows[hi][1:]]
    body = table.rows[hi + 1:]
    month_rows = [r for r in body if r and r[0].strip().lower() in _MONTH_NAMES]
    seq = [month_no(r[0]) for r in month_rows]
    if seq != [m for _, m in months]:
        return f'month rows {month_rows[0][0] if month_rows else "?"}..{month_rows[-1][0] if month_rows else "?"} ' \
               f'do not match heading'
    for r, (y, m) in zip(month_rows, months):
        cells = r[1:1 + len(units)]
        if not any(c.strip() for c in cells):
            continue                        # month not published yet
        for unit, c in zip(units, cells):
            add('smimer.icu_patient_count', month_period(y, m), num(c), {'unit': unit})
    for r in body:
        label = r[0].strip() if r else ''
        if label.lower() in _MONTH_NAMES or _ICU_DERIVED.match(label):
            continue
        if label.lower() == 'bed':
            for unit, c in zip(units, r[1:1 + len(units)]):
                add('smimer.icu_beds', period, num(c), {'unit': unit})
            continue
        raise ValueError(f'unknown ICU row {label!r}')
    return None



def analyse(body: bytes) -> tuple[Result, list[str], list[tuple]]:
    """Parse the page; also return the tables skipped (heading + reason) and any cross-table conflicts."""
    res = Result(geos=[SMC, GEO])
    values: dict[tuple, Obs] = {}
    conflicts: list[tuple] = []
    skipped: list[str] = []

    def add(metric, period, v, dims):
        o = Obs(metric, 'facility', 'smimer', period[0], period[1], value=v,
                status='reported' if v is not None else 'not_reported', dims=dict(dims))
        k = (metric, period[0], period[1], tuple(sorted(dims.items())))
        if k in values:
            if values[k] is not None and values[k].value != v:
                conflicts.append((k, values[k].value, v))
                values[k] = None            # tables disagree: emit neither
            return
        values[k] = o

    for table in html_tables(body):
        m = _HEADING.search(table.heading)
        if not m or len(table.rows) < 3:
            continue
        section = _SECTION[m.group(1)]
        sm, sy, em, ey = month_no(m.group(2)), int(m.group(3)), month_no(m.group(4)), int(m.group(5))
        months = _months(sm, sy)
        if months[-1] != (ey, em):
            skipped.append(f'{m.group(0)}: not a 12-month span')
            continue
        period = (month_period(sy, sm)[0], month_period(ey, em)[1])
        if section == 'icu':
            why = _parse_icu(table, months, period, add)
        else:
            why = _parse_monthly_columns(table, section, months, add)
        if why:
            skipped.append(f'{m.group(0)}: {why}')

    res.observations = [o for o in values.values() if o is not None]
    return res, skipped, conflicts


def parse(raw: Raw) -> Result:
    return analyse(raw.body)[0]


_RANGES = {
    'smimer.milk_collected_ml': 200_000, 'smimer.milk_given_ml': 200_000,
    'smimer.milk_donor_mothers': 2_000, 'smimer.milk_recipient_newborns': 2_000,
    'smimer.blood_units_collected': 10_000, 'smimer.blood_units_collected_total': 10_000,
    'smimer.blood_components_issued': 10_000, 'smimer.blood_units_issued_other_hospitals': 10_000,
    'smimer.blood_donation_camps': 200, 'smimer.eyes_collected': 500, 'smimer.eyes_utilised': 500,
    'smimer.icu_patient_count': 10_000, 'smimer.icu_beds': 500,
}


def validate(result: Result, raw: Raw) -> None:
    obs = result.observations
    by_metric: dict[str, int] = {}
    for o in obs:
        by_metric[o.metric_id] = by_metric.get(o.metric_id, 0) + 1
        if o.value is not None and not 0 <= o.value <= _RANGES[o.metric_id]:
            raise ValidationError(f'implausible {o.metric_id} = {o.value} ({o.period_start}, {o.dims})')
    for metric, minimum in (('smimer.milk_collected_ml', 100), ('smimer.blood_units_collected_total', 100),
                            ('smimer.eyes_collected', 100), ('smimer.icu_patient_count', 400)):
        if by_metric.get(metric, 0) < minimum:
            raise ValidationError(f'only {by_metric.get(metric, 0)} {metric} values parsed; layout may have changed')
    # alignment check: camp + blood bank + replacement should equal the published grand total
    parts: dict[str, float] = {}
    totals: dict[str, float] = {}
    for o in obs:
        if o.value is None:
            continue
        if o.metric_id == 'smimer.blood_units_collected':
            parts[o.period_start] = parts.get(o.period_start, 0) + o.value
        elif o.metric_id == 'smimer.blood_units_collected_total':
            totals[o.period_start] = o.value
    bad = [p for p, t in totals.items() if p in parts and parts[p] != t]
    if len(bad) > max(3, len(totals) // 10):
        raise ValidationError(f'blood collection rows do not add up in {len(bad)} months (e.g. {bad[:3]}); '
                              'columns may be misaligned')
    latest = max(o.period_start for o in obs)
    if raw is not None and latest > raw.retrieved_at[:10]:
        raise ValidationError(f'latest month {latest} is after the fetch date {raw.retrieved_at[:10]}')
