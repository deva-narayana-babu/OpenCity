"""SMC Street Light Department: monthly average percentage of non-working streetlights (March 2017 - February 2021).

Publisher: Surat Municipal Corporation, Street Light Department (Engineering). The page sits under
Departments > Street Light > "Non-working Streetlights" on the SMC website.

Endpoint: one plain GET, no parameters, no login or captcha (robots.txt on www.suratmunicipal.gov.in returns
404, so nothing is disallowed):

    https://www.suratmunicipal.gov.in/Departments/NonWorkingStreetlights

Response layout (server-rendered HTML; browser title "Non-working Street Lights (In Percentage)"). The series is
split over two side-by-side tables, both with the hidden caption "Percentages of Non-working Streetlights":

    Sr. No. | Month           | Avg. Non-working Streetlights
    1       | February/2021   | 0.38%
    ...                                    (table 1: rows 1-25, February 2021 back to February 2019)
    26      | January/2019    | 0.34%
    ...                                    (table 2: rows 26-48, January 2019 back to March 2017)

-> streetlight.nonworking_pct: one observation per month, smc_city, period = that calendar month
   (parse.month_period). The value is the published "Avg. Non-working Streetlights" percentage (0.38 means 0.38 %).
   SMC does not say how the average is taken (for example a mean of daily CCMS readings) or what the
   denominator is (the total number of streetlights is not on this page), so the figure is stored exactly as
   published. A blank, "-" or "NA" cell would become status='not_reported' with no value.

Snapshot 2026-10-24: 48 months, from March 2017 (0.76 %) to February 2021 (0.38 %). The highest is 1.15 % in
June 2017. The footer "Last Updated: July 21, 2022 04:27 PM" is the CMS edit time of the page, not a data date,
so it is not used.

Quirks and caveats:
- The series STOPPED at February 2021. The page is historical only. It is still checked weekly, so that a
  restart is noticed. validate() does not fail just because the data are old.
- The month cell uses "Month/Year" ("February/2021"). The slash is turned into a space before parse.month_year().
- These figures describe SMC-maintained street lighting only. They are not power-supply outage data: DGVCL and
  Torrent Power supply electricity in Surat, and their outage notices are a separate source.
- The sibling pages "Streetlight Luminaires Details", "Important Details" and "Energy Conservation and CCMS" are
  not fetched.

Geography: SMC city (smc_city:smc). Cadence: monthly series, no longer updated. Units: percent of streetlights.
Licence: Surat Municipal Corporation web page; public information. No explicit open licence.
"""
from __future__ import annotations

from ..model import Metric, Obs, Raw, Result, Source, ValidationError
from ..parse import html_tables, month_period, month_year, num
from ..surat import SMC

URL = 'https://www.suratmunicipal.gov.in/Departments/NonWorkingStreetlights'
METRIC = 'streetlight.nonworking_pct'

SOURCE = Source(
    id='smc_streetlights',
    name='SMC non-working streetlights (monthly average, %)',
    publisher='Surat Municipal Corporation, Street Light Department',
    url=URL,
    module='power',
    cadence='monthly',
    interval_hours=24 * 7,          # series stopped in Feb 2021; a weekly check notices a restart
    geo_note='SMC city (whole corporation area)',
    licence_note='Surat Municipal Corporation web page; public information',
    notes=('Historical only: the series runs from March 2017 to February 2021 and the page was last edited in '
           'July 2022. The averaging method and the total number of streetlights are not published. These are '
           'not electricity outage data (DGVCL and Torrent Power supply Surat).'),
    metrics=(
        Metric(METRIC, 'Non-working streetlights (monthly average)', '%',
               'Average percentage of SMC streetlights not working during the month, as published by the SMC '
               'Street Light Department ("Avg. Non-working Streetlights"). The averaging method and the base '
               '(total streetlights) are not stated.'),
    ),
)


def fetch(ctx):
    yield ctx.get(URL)


def parse(raw: Raw) -> Result:
    res = Result(geos=[SMC])
    for table in html_tables(raw.body):
        if table.find_row('month', 'non-working') != 0:
            continue
        for row in table.rows[1:]:
            if len(row) < 3 or not row[1].strip():
                continue
            y, m = month_year(row[1].replace('/', ' '))
            start, end = month_period(y, m)
            v = num(row[2])
            res.observations.append(Obs(METRIC, 'smc_city', 'smc', start, end, value=v,
                                        status='reported' if v is not None else 'not_reported'))
    return res


def validate(result: Result, raw: Raw) -> None:
    obs = result.observations
    if len(obs) < 40:
        raise ValidationError(f'only {len(obs)} months parsed (48 on the page in 2026); layout may have changed')
    for o in obs:
        if o.value is not None and not 0 <= o.value <= 20:
            raise ValidationError(f'implausible non-working share {o.value}% for {o.period_start}')
    first = min(o.period_start for o in obs)
    latest = max(o.period_start for o in obs)
    if first < '2010-01-01':
        raise ValidationError(f'month {first} is implausibly early; month/year misread?')
    if raw is not None and raw.retrieved_at and latest > raw.retrieved_at[:10]:
        raise ValidationError(f'month {latest} is after the fetch date {raw.retrieved_at}')
