"""SMC vital statistics: annual births, deaths and mortality rates (2001-2021), and monthly births by sex.

Publisher: Surat Municipal Corporation (SMC), Health Department, Birth and Death Registration. Registering births
and deaths inside SMC limits is the corporation's statutory duty. It is done at the zone offices and civic centres.

Documents (all on https://www.suratmunicipal.gov.in, no login, no robots.txt; checked 2026-10-24):
  1. GET /Departments/BirthDeathRegistration ("Birth and Death Registration")
     The page explains the registration rules, then shows "Vital Statistics at a Glance": five HTML tables, each
     with a header row "Details/Year | <year> ..." and one row per item.
       2018-2021, 2013-2017, 2009-2012, 2005-2008, 2001-2004 (this last table is captioned "2005 - 2008" by
       mistake, so years are always read from the header row, never from the caption)
     Rows: Mid year estimated population (2009 onwards) | Area of the City (Sq. kms.) | Registered Births |
       Registered Deaths | Registered Infant Deaths | Registered Maternal Deaths | Registered Still Births |
       Crude Birth Rate | Crude Death Rate | Infant Mortality Rate | Maternal Mortality Rate | Still Birth Ratio |
       Population Density Per Sq.km. (2001-2017 only)
     Numbers are plain or Indian-grouped ("55,907").
  2. GET /Departments/BirthDetails ("Birth Details")
     A form with a year drop-down, <select id="BirthMonth" name="Year">. It held 137 years on 2026-10-24: every
     year from 2022 back to 1899, then 13 scattered older years down to 1776. Only the year list is read.
     parse() checks it and stores nothing.
  3. POST /Departments/GetBirthDetails, form body Year=<yyyy> (the page's own script makes the same request)
     returns JSON:
       {"data": [{"mnth": "January - 2022", "BirthMonth": 1, "MaleCount": "3111", "FeMaleCount": "2753",
                  "TotalCount": "5864", ...}, ... (12 months),
                 {"mnth": "Grand Total", "BirthMonth": 13, ...}],
        "status": 200, ...}
     Counts are strings. "-" means no data, as for November and December 2022.
     fetch() requests every listed year from FIRST_YEAR (1991) on. The newest RECENT (2) years are requested on
     every run, because late registrations can still be added. Older years are downloaded once
     (skip_if_seen) and re-parsed from the archive when the parser changes.

What is stored (geo smc_city/smc, the SMC area as published):
- From the annual tables, one value per item and calendar year (period YYYY-01-01..YYYY-12-31):
    vital.mid_year_population    mid-year (1 July) estimated population of the city (2009-2021)
    vital.city_area_km2          "Area of the City" in sq km as printed for that year
    vital.population_density     persons per sq km as printed (2001-2017)
    vital.registered_births      live births registered in the year
    vital.registered_deaths      deaths registered in the year
    vital.infant_deaths          registered deaths of infants (under 1 year)
    vital.maternal_deaths        registered maternal deaths
    vital.still_births           registered still births
    vital.crude_birth_rate       births per 1,000 mid-year population
    vital.crude_death_rate       deaths per 1,000 mid-year population
    vital.infant_mortality_rate  infant deaths per 1,000 live births
    vital.maternal_mortality_per_1000  maternal deaths per 1,000 live births (as printed for 2001-2017)
    vital.maternal_mortality_per_100k  maternal deaths per 100,000 live births (as printed for 2018-2021)
    vital.still_birth_ratio      still births per 1,000 live births
  The page uses the label "Maternal Mortality Rate" for both units (0.46 in 2017, 24.91 in 2018). The two units
  are stored as separate metrics, so a series never mixes them. A value below 5 can only be per 1,000 live
  births: 5 per 1,000 would be 500 per 100,000, far above anything recorded for Surat. validate() checks that
  each value agrees with maternal deaths / births in the unit chosen.
- From the births API, one value per calendar month (month_period) and sex:
    vital.births_by_month        births in SMC's birth register for that month, dims.sex male / female / total.
                                 "total" is the published TotalCount. In some older months it is a little
                                 more than male + female (1995: 7 births; 1980: 86), presumably entries with
                                 no sex recorded. The page does not say whether the month is the month of
                                 birth or of registration. The year list reaching back to 1776 points to month
                                 of birth, so late registrations are filed under their birth year.
  The "Grand Total" entry is not stored: it is the sum of the months, and for 2022 it covers January-October
  only. parse() checks that the male and female months add up to it. For older years the TotalCount of the
  Grand Total is male + female, not the sum of the monthly totals.
  The sex ratio at birth is not published and is not stored. Compute it as female / male x 1000 from the
  monthly counts (2021: 31,516 / 36,999 -> 852).

Cadence: the tables are updated irregularly, about once a year. The footer said "Last Updated: March 17, 2025"
and the latest year was 2021. The births API stops at October 2022: November and December 2022 are "-", and
2022 is the newest year in the list. Both look frozen, so the page is checked weekly. The footer date is not
used as a data date (it is the CMS edit stamp; see the adapter README).

Quirks, all stored as published:
- Area of the City: 112.28 sq km for 2001-2006 (before the 2006 extension of the city limits), 326.515 for 2007,
  2011 and 2012, and 326.555 for the other years. It stays 326.555 for 2020 and 2021, although the city limits
  were extended again in 2020, so the rates for those years use the old area figure.
- The mid-year population falls from 4,786,002 (2010) to 4,462,002 (2011). The 2011 figure is close to the
  Census 2011 count for the SMC (4,467,797); the other years are estimates.
- Some printed rates do not follow from the printed counts:
    IMR for 2003 and 2004 repeats 2002's 19.65 (the counts give 19.31 and 19.60);
    IMR 2001 is 20.97 (the counts give 21.18);
    the crude death rate for 2021 is 6.07 (36,690 / 6,936,534 gives 5.29);
    the 2011 density is 13,555 (4,462,002 / 326.515 gives 13,666).
  validate() therefore checks only plausible ranges for these rates, not the arithmetic.
- The monthly births API and the annual table count differently: for 2021 both give 68,515; for 2011 the API
  gives 68,383 and the table 68,559.
- The page also states the registration fees. Registration within 21 days is free. A late fee of Rs 2 applies up
  to 30 days, and Rs 5 (with an affidavit) up to a year. Extra certificate copies cost Rs 20. These are not
  stored.

Licence: Surat Municipal Corporation web pages; public information. No open-data licence is stated.
"""
from __future__ import annotations

import json

from ..model import Metric, Obs, Raw, Result, Source, ValidationError
from ..parse import html_tables, month_period, month_year, num, year_period
from ..surat import SMC

BASE = 'https://www.suratmunicipal.gov.in/Departments/'
STATS_URL = BASE + 'BirthDeathRegistration'
YEARS_URL = BASE + 'BirthDetails'
BIRTHS_URL = BASE + 'GetBirthDetails'
FIRST_YEAR = 1991       # monthly births are requested from this year on
RECENT = 2              # the newest years are re-requested every run; older ones only once

MMR_1000, MMR_100K = 'vital.maternal_mortality_per_1000', 'vital.maternal_mortality_per_100k'

# row label (lower case, start of the cell) -> metric. "maternal mortality rate" is split by unit in parse().
ROWS = [
    ('mid year estimated population', 'vital.mid_year_population'),
    ('area of the city', 'vital.city_area_km2'),
    ('registered births', 'vital.registered_births'),
    ('registered deaths', 'vital.registered_deaths'),
    ('registered infant deaths', 'vital.infant_deaths'),
    ('registered maternal deaths', 'vital.maternal_deaths'),
    ('registered still births', 'vital.still_births'),
    ('crude birth rate', 'vital.crude_birth_rate'),
    ('crude death rate', 'vital.crude_death_rate'),
    ('infant mortality rate', 'vital.infant_mortality_rate'),
    ('maternal mortality rate', MMR_1000),
    ('still birth ratio', 'vital.still_birth_ratio'),
    ('population density', 'vital.population_density'),
]

# plausible ranges per metric for Surat city (validate)
RANGES = {
    'vital.mid_year_population': (1_000_000, 20_000_000),
    'vital.city_area_km2': (100, 1000),
    'vital.population_density': (5_000, 40_000),
    'vital.registered_births': (20_000, 200_000),
    'vital.registered_deaths': (5_000, 100_000),
    'vital.infant_deaths': (100, 10_000),
    'vital.maternal_deaths': (0, 500),
    'vital.still_births': (0, 5_000),
    'vital.crude_birth_rate': (5, 40),
    'vital.crude_death_rate': (1, 20),
    'vital.infant_mortality_rate': (2, 100),
    MMR_1000: (0, 5),
    MMR_100K: (0, 500),
    'vital.still_birth_ratio': (0, 50),
    'vital.births_by_month': (0, 20_000),
}

SOURCE = Source(
    id='smc_vital_stats',
    name='SMC vital statistics: births, deaths and mortality rates; monthly births by sex',
    publisher='Surat Municipal Corporation, Health Department (Birth and Death Registration)',
    url=STATS_URL,
    module='population',
    cadence='annual',
    interval_hours=24 * 7,      # irregular annual updates; the monthly births API looks frozen since Oct 2022
    geo_note='SMC city (the corporation area as published; the page prints 326.555 sq km even after the 2020 '
             'extension of the city limits)',
    licence_note='Surat Municipal Corporation web pages; public information (no open-data licence stated)',
    notes='Annual table 2001-2021 ("Vital Statistics at a Glance"; page last edited March 2025). Monthly births '
          'by sex from the Birth Details API, 1991 to October 2022 (Nov-Dec 2022 not reported). Maternal '
          'mortality is printed per 1,000 live births up to 2017 and per 100,000 from 2018: two metrics. '
          'Some printed rates differ from the printed counts (IMR 2001-2004, CDR 2021); stored as printed. '
          'Sex ratio at birth is not published: compute female / male x 1000 from vital.births_by_month.',
    metrics=(
        Metric('vital.mid_year_population', 'Mid-year estimated population (SMC)', 'persons',
               'Mid-year (1 July) estimated population of the SMC area used by SMC for its vital rates, filed '
               'under the calendar year. Published for 2009 onwards.'),
        Metric('vital.city_area_km2', 'City area used for vital statistics (SMC)', 'sq km',
               'Area of the city as printed in the vital statistics table for that year.'),
        Metric('vital.population_density', 'Population density (SMC vital statistics)', 'persons per sq km',
               'Population density as printed in the vital statistics table (2001-2017).'),
        Metric('vital.registered_births', 'Registered births (SMC)', 'births',
               'Live births registered with SMC in the calendar year.'),
        Metric('vital.registered_deaths', 'Registered deaths (SMC)', 'deaths',
               'Deaths registered with SMC in the calendar year.'),
        Metric('vital.infant_deaths', 'Registered infant deaths (SMC)', 'deaths',
               'Registered deaths of infants under one year of age in the calendar year.'),
        Metric('vital.maternal_deaths', 'Registered maternal deaths (SMC)', 'deaths',
               'Registered maternal deaths in the calendar year.'),
        Metric('vital.still_births', 'Registered still births (SMC)', 'still births',
               'Still births registered in the calendar year.'),
        Metric('vital.crude_birth_rate', 'Crude birth rate (SMC)', 'per 1,000 population',
               'Registered live births per 1,000 mid-year population, as printed.'),
        Metric('vital.crude_death_rate', 'Crude death rate (SMC)', 'per 1,000 population',
               'Registered deaths per 1,000 mid-year population, as printed (2021 is printed as 6.07, which does '
               'not follow from the printed deaths and population).'),
        Metric('vital.infant_mortality_rate', 'Infant mortality rate (SMC)', 'per 1,000 live births',
               'Registered infant deaths per 1,000 registered live births, as printed.'),
        Metric(MMR_1000, 'Maternal mortality rate per 1,000 live births (SMC)', 'per 1,000 live births',
               'Maternal deaths per 1,000 registered live births, as printed for 2001-2017 under the label '
               '"Maternal Mortality Rate". Multiply by 100 to compare with the per-100,000 series.'),
        Metric(MMR_100K, 'Maternal mortality rate per 100,000 live births (SMC)', 'per 100,000 live births',
               'Maternal deaths per 100,000 registered live births, as printed from 2018 under the label '
               '"Maternal Mortality Rate".'),
        Metric('vital.still_birth_ratio', 'Still birth ratio (SMC)', 'per 1,000 live births',
               'Registered still births per 1,000 registered live births, as printed.'),
        Metric('vital.births_by_month', 'Births by month and sex (SMC birth register)', 'births',
               'Births in the SMC birth register for the month (most likely the month of birth), by dims.sex: '
               'male, female, total (the published total, which can slightly exceed male + female). '
               'Sex ratio at birth = female / male x 1000.'),
    ),
)


# ---------- fetch ----------

def year_list(html: str) -> list[int]:
    """Years offered by <select id="BirthMonth" name="Year"><option value="2022">2022</option>...</select>."""
    start = html.find('id="BirthMonth"')
    if start < 0:
        raise ValueError('no year drop-down (id="BirthMonth") on the Birth Details page')
    block = html[start:html.find('</select>', start)]
    years = []
    for part in block.split('<option value="')[1:]:
        value = part.split('"', 1)[0]
        if value.isdigit():
            years.append(int(value))
    if not years:
        raise ValueError('the Birth Details year drop-down is empty')
    return sorted(years)


def fetch(ctx):
    yield ctx.get(STATS_URL, meta={'doc': 'annual'})
    page = ctx.get(YEARS_URL, meta={'doc': 'year_list'})
    yield page
    years = [y for y in year_list(page.text) if y >= FIRST_YEAR]
    for y in years:                                     # oldest first
        recent = y in years[-RECENT:]
        raw = ctx.post(BIRTHS_URL, form={'Year': str(y)}, meta={'doc': 'births', 'year': y},
                       skip_if_seen=not recent, soft=True)
        if raw is not None:
            yield raw


# ---------- parse ----------

def parse(raw: Raw) -> Result:
    text = raw.text
    if text.lstrip().startswith('{'):
        kind = 'births'
    elif 'Vital Statistics at a Glance' in text:
        kind = 'annual'
    elif 'id="BirthMonth"' in text:
        kind = 'year_list'
    else:
        raise ValueError(f'{raw.url}: not a vital-statistics page or births response (layout changed?)')
    if raw.meta.get('doc', kind) != kind:
        raise ValueError(f'{raw.url}: expected the {raw.meta["doc"]} document but got the {kind} document')
    if kind == 'year_list':
        year_list(text)                                 # shape check only; the years drive fetch()
        return Result()
    if kind == 'births':
        return _parse_births(raw)
    return _parse_annual(raw)


def _obs(metric, start, end, v, dims=None) -> Obs:
    return Obs(metric, 'smc_city', 'smc', start, end, value=v,
               status='reported' if v is not None else 'not_reported', dims=dims or {})


def _metric(label: str) -> str:
    low = label.lower()
    for start, metric in ROWS:
        if low.startswith(start):
            return metric
    raise ValueError(f'unknown row {label!r} in the vital statistics table')


def _parse_annual(raw: Raw) -> Result:
    res = Result(geos=[SMC])
    tables = [t for t in html_tables(raw.body) if t.rows and t.rows[0][0].lower().startswith('details/year')]
    if not tables:
        raise ValueError('no "Details/Year" tables on the Birth and Death Registration page')
    for t in tables:
        years = [int(y) for y in t.rows[0][1:]]
        for row in t.rows[1:]:
            metric = _metric(row[0])
            for year, cell in zip(years, row[1:]):
                v = num(cell)
                m = metric
                if metric == MMR_1000 and v is not None and v >= 5:
                    m = MMR_100K                        # printed per 100,000 live births (2018 onwards)
                res.observations.append(_obs(m, *year_period(year), v))
    return res


def _parse_births(raw: Raw) -> Result:
    data = json.loads(raw.body)
    if data.get('status') != 200:
        raise ValueError(f'births API answered status {data.get("status")}: {data.get("statusText")}')
    rows = data['data']
    months = [r for r in rows if 1 <= r['BirthMonth'] <= 12]
    totals = [r for r in rows if r['BirthMonth'] == 13]
    if len(months) != 12 or len(totals) != 1:
        raise ValueError(f'expected 12 months and a Grand Total, got {[r["BirthMonth"] for r in rows]}')
    res = Result(geos=[SMC])
    columns = (('male', 'MaleCount'), ('female', 'FeMaleCount'), ('total', 'TotalCount'))
    sums = {'male': 0, 'female': 0}
    for r in months:
        year, month = month_year(r['mnth'])             # 'January - 2022'
        if month != r['BirthMonth'] or year != raw.meta.get('year', year):
            raise ValueError(f'month label {r["mnth"]!r} does not match month {r["BirthMonth"]} / '
                             f'year {raw.meta.get("year")}')
        for sex, key in columns:
            v = num(r[key])
            if sex in sums:
                sums[sex] += v or 0
            res.observations.append(_obs('vital.births_by_month', *month_period(year, month), v, {'sex': sex}))
    for sex, key in columns[:2]:
        if sums[sex] != num(totals[0][key]):
            raise ValueError(f'{sex} months add up to {sums[sex]}, the Grand Total says {totals[0][key]}')
    return res


# ---------- validation ----------

def validate(result: Result, raw: Raw) -> None:
    for o in result.observations:
        lo, hi = RANGES[o.metric_id]
        if o.value is not None and not lo <= o.value <= hi:
            raise ValidationError(f'{o.metric_id} {o.period_start} {o.dims}: {o.value} is outside {lo}-{hi}')
    today = raw.retrieved_at[:10] if raw is not None and raw.retrieved_at else '9999'
    late = [o for o in result.observations if o.value is not None and o.period_start > today]
    if late:
        raise ValidationError(f'{late[0].metric_id} has a value for {late[0].period_start}, after the fetch')
    metrics = {o.metric_id for o in result.observations}
    if 'vital.registered_births' in metrics:
        _validate_annual(result)
    elif metrics:
        _validate_births(result)


def _validate_annual(result: Result) -> None:
    v = {(o.metric_id, o.period_start[:4]): o.value for o in result.observations}
    years = sorted(y for m, y in v if m == 'vital.registered_births')
    if len(years) < 15 or years[-1] < '2021':
        raise ValidationError(f'registered births for only {len(years)} years ending {years[-1]}; '
                              'the page had 2001-2021')
    for y in years:
        births, deaths = v[('vital.registered_births', y)], v.get(('vital.maternal_deaths', y))
        for metric, per in ((MMR_1000, 1000), (MMR_100K, 100_000)):
            rate = v.get((metric, y))
            if rate is None or deaths is None:
                continue
            expected = deaths / births * per
            if abs(rate - expected) > max(0.01, 0.03 * expected):
                raise ValidationError(f'{y}: maternal mortality {rate} does not match {deaths} deaths / {births} '
                                      f'births per {per} ({expected:.2f}); unit detection failed')
        if v[('vital.infant_deaths', y)] >= births / 10:
            raise ValidationError(f'{y}: infant deaths {v[("vital.infant_deaths", y)]} vs {births} births')


def _validate_births(result: Result) -> None:
    by = {}
    for o in result.observations:
        by.setdefault(o.period_start, {})[o.dims['sex']] = o.value
    male = female = 0
    for start, n in by.items():
        if None not in (n['male'], n['female'], n['total']) and n['total'] < n['male'] + n['female']:
            raise ValidationError(f'{start}: total births {n["total"]} below male + female')
        male += n['male'] or 0
        female += n['female'] or 0
    if male >= 1000 and not 700 <= female / male * 1000 <= 1100:
        raise ValidationError(f'sex ratio at birth {female / male * 1000:.0f} is implausible; columns swapped?')
