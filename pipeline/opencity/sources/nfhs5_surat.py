"""NFHS-5 (2019-21) district fact-sheet indicators for Surat district, with the NFHS-4 (2015-16) comparison.

Source: a CSV compilation of the NFHS-5 district fact sheets,
    https://raw.githubusercontent.com/pratapvardhan/NFHS-5/master/NFHS-5-Districts.csv
Long format, one row per district x indicator:
    State, State-Code, District, Indicator ("81. Children age 6-59 months who are anaemic (<11.0 g/dl)22 (%)"),
    NFHS-5, NFHS-4, NFHS-5-note, NFHS-4-note
Notes are either "Based on 25-49 unweighted cases" (the fact sheet prints such values in parentheses)
or "Percentage not shown; based on fewer than 25 unweighted cases" (the fact sheet prints "*").
Surat has 104 indicator rows (State "Gujarat", District "Surat"). Tapi is a separate district.

What is stored (geo surat_district/surat; never smc_city, the survey sample covers the whole district):
  - one observation per indicator and survey round; dims = {factsheet_no, indicator}
    factsheet_no is the NFHS-5 fact-sheet row number ("81"); NFHS-4 values are the comparison column
    of the same NFHS-5 fact sheet, so they share the row number.
  - indicator is the label with the row number and footnote digits removed. The CSV drops the fact
    sheet's sub-headings, which leaves rows 86-88 / 89-91 and 92-94 / 95-97 with identical labels;
    the population from the fact sheet heading is put back in front (e.g. "Women age 15 years and
    above: ..."), and likewise for family-planning rows 20-29 and cancer screening rows 98-100.
  - period = the survey round label: NFHS-5 2019-01-01..2021-12-31, NFHS-4 2015-01-01..2016-12-31
    (rounds, not fieldwork dates).
  - "Based on 25-49 unweighted cases": reported, value_text carries the note (treat with caution).
    "Percentage not shown ...": status withheld, value None, value_text the note.
    Blank without a note (indicator not in NFHS-4): not_reported.
  - Units: most rows are percentages (nfhs.indicator_pct); two sex ratios (nfhs.sex_ratio) and the
    out-of-pocket delivery cost (nfhs.delivery_oop_rs) get their own metrics so units never mix.
"""
from __future__ import annotations

import csv
import io
import re

from ..model import Metric, Obs, Raw, Result, Source, ValidationError
from ..parse import clean
from ..surat import SURAT_DISTRICT

URL = 'https://raw.githubusercontent.com/pratapvardhan/NFHS-5/master/NFHS-5-Districts.csv'
STATE, DISTRICT = 'Gujarat', 'Surat'
ROUNDS = {'NFHS-5': ('2019-01-01', '2021-12-31'), 'NFHS-4': ('2015-01-01', '2016-12-31')}
N_INDICATORS = 104

PCT, SEX_RATIO, OOP = 'nfhs.indicator_pct', 'nfhs.sex_ratio', 'nfhs.delivery_oop_rs'

SOURCE = Source(
    id='nfhs5_surat',
    name='NFHS-5 district fact sheet indicators, Surat district (2019-21, with NFHS-4)',
    publisher='International Institute for Population Sciences / Ministry of Health and Family Welfare (NFHS-5)',
    url='https://github.com/pratapvardhan/NFHS-5',
    module='health',
    cadence='static',
    interval_hours=24 * 90,     # a finished survey; the mirror only changes if a fix is pushed
    geo_note='Surat district (survey sample covers the whole district, urban and rural); not SMC city limits',
    licence_note='Data from IIPS/MoHFW NFHS-5 district fact sheets; CSV compilation by pratapvardhan/NFHS-5 (GitHub)',
    notes='Periods are survey-round labels (NFHS-5 2019-21, NFHS-4 2015-16). Values based on 25-49 unweighted '
          'cases carry that note in value_text; suppressed values (<25 cases) are stored as withheld.',
    metrics=(
        Metric(PCT, 'NFHS indicator (percentage)', '%',
               'NFHS district fact-sheet indicator expressed as a percentage; dims.indicator is the fact-sheet '
               'label, dims.factsheet_no its NFHS-5 row number. Period = survey round.'),
        Metric(SEX_RATIO, 'NFHS sex ratio', 'females per 1,000 males',
               'Sex ratio of the total population, or at birth for children born in the last five years '
               '(dims.indicator).'),
        Metric(OOP, 'Out-of-pocket cost per delivery in a public facility', 'Rs.',
               'Average out-of-pocket expenditure per delivery in a public health facility (NFHS fact sheet).'),
    ),
)

# fact-sheet sub-headings the CSV loses: row range -> population prefix and the label each range starts with
SECTIONS = [
    (20, 27, 'Current use of family planning methods (currently married women age 15-49 years)', 'Any method'),
    (28, 29, 'Unmet need for family planning (currently married women age 15-49 years)', 'Total unmet need'),
    (86, 88, 'Women age 15 years and above', 'Blood sugar level - high'),
    (89, 91, 'Men age 15 years and above', 'Blood sugar level - high'),
    (92, 94, 'Women age 15 years and above', 'Mildly elevated blood pressure'),
    (95, 97, 'Men age 15 years and above', 'Mildly elevated blood pressure'),
    (98, 100, 'Women age 30-49 years', 'Ever undergone a screening test for cervical cancer'),
]

_FOOTNOTE = re.compile(r'(?<=[A-Za-z)])\d{1,2}(?:\s*,\s*\d{1,2})*\s*(?=\((?:%|Rs\.)\)\s*$)')
_NUMBER = re.compile(r'-?\d+(?:\.\d+)?')
WITHHELD = 'percentage not shown'


def clean_label(text: str) -> tuple[int, str]:
    """'81. Children ... (<11.0 g/dl)22 (%)' -> (81, 'Children ... (<11.0 g/dl) (%)')."""
    m = re.match(r'\s*(\d{1,3})\.\s*(.+)$', text, re.S)
    if not m:
        raise ValidationError(f'indicator without a fact-sheet number: {text!r}')
    label = _FOOTNOTE.sub(' ', clean(m.group(2)))
    return int(m.group(1)), re.sub(r'\s+', ' ', label).strip()


def _metric(label: str) -> str:
    if label.endswith('(%)'):
        return PCT
    if label.endswith('(females per 1,000 males)'):
        return SEX_RATIO
    if label.endswith('(Rs.)'):
        return OOP
    raise ValidationError(f'unknown unit in NFHS indicator {label!r}')


def fetch(ctx):
    yield ctx.get(URL)


def parse(raw: Raw) -> Result:
    res = Result(geos=[SURAT_DISTRICT])
    reader = csv.DictReader(io.StringIO(raw.body.decode('utf-8-sig')))
    need = {'State', 'District', 'Indicator', *ROUNDS, *(r + '-note' for r in ROUNDS)}
    if not need <= set(reader.fieldnames or ()):
        raise ValidationError(f'CSV columns changed: {reader.fieldnames}')
    rows = [r for r in reader if r['State'].strip() == STATE and r['District'].strip() == DISTRICT]
    for r in rows:
        no, label = clean_label(r['Indicator'])
        for lo, hi, prefix, first in SECTIONS:
            if lo <= no <= hi:
                if no == lo and not label.startswith(first):
                    raise ValidationError(f'row {no} is {label!r}, expected it to start with {first!r}: '
                                          'fact-sheet numbering changed')
                label = f'{prefix}: {label}'
        metric = _metric(label)
        dims = {'factsheet_no': str(no), 'indicator': label}
        for rnd, (start, end) in ROUNDS.items():
            v, note = r[rnd].strip(), clean(r[rnd + '-note'])
            if v and not _NUMBER.fullmatch(v):
                raise ValidationError(f'row {no} {rnd}: unexpected value {v!r}')
            if v:
                res.observations.append(Obs(metric, 'surat_district', 'surat', start, end, value=float(v),
                                            value_text=note or None, dims=dims))
            elif note.lower().startswith(WITHHELD):
                res.observations.append(Obs(metric, 'surat_district', 'surat', start, end, value=None,
                                            value_text=note, status='withheld', dims=dims))
            else:
                res.observations.append(Obs(metric, 'surat_district', 'surat', start, end, value=None,
                                            value_text=note or None, status='not_reported', dims=dims))
    return res


def validate(result: Result, raw: Raw) -> None:
    nos = {int(o.dims['factsheet_no']) for o in result.observations}
    if nos != set(range(1, N_INDICATORS + 1)):
        raise ValidationError(f'expected fact-sheet rows 1-{N_INDICATORS} for {DISTRICT}, got {len(nos)} '
                              f'(missing {sorted(set(range(1, N_INDICATORS + 1)) - nos)[:10]})')
    labels = {o.dims['indicator'] for o in result.observations}
    if len(labels) != N_INDICATORS:
        raise ValidationError(f'{N_INDICATORS} rows but {len(labels)} distinct labels: duplicate indicator labels')
    reported5 = sum(1 for o in result.observations if o.status == 'reported' and o.period_start.startswith('2019'))
    if reported5 < 90:
        raise ValidationError(f'only {reported5} NFHS-5 values reported for {DISTRICT}; layout changed?')
    for o in result.observations:
        v = o.value
        if v is None:
            continue
        ok = {PCT: 0 <= v <= 100, SEX_RATIO: 600 <= v <= 1200, OOP: 0 <= v <= 100_000}[o.metric_id]
        if not ok:
            raise ValidationError(f'implausible {o.metric_id} {v} for row {o.dims["factsheet_no"]} ({o.period_start})')
