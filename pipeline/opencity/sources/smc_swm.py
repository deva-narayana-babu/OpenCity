"""SMC Solid Waste Management statistics: monthly MSW collection by collection method.

Page: https://www.suratmunicipal.gov.in/Departments/SolidWasteManagementStatistics
Twelve HTML tables:
  0-7   current series (Apr 2019 onward), one table per collection method
  8-11  legacy series (Oct 2008 - Mar 2019), four methods
Each table: title row "N. <method>", header row, then rows of
  Sr. No. | Period ("July-2026") | <numeric columns...>

This module is the reference example for writing adapters: a pure parse() that
turns the archived page into tidy observations, and a fetch() that only uses ctx.
"""
from __future__ import annotations

import re

from ..model import Metric, Obs, Raw, Result, Source, ValidationError
from ..parse import html_tables, month_period, month_year, num
from ..surat import SMC

URL = 'https://www.suratmunicipal.gov.in/Departments/SolidWasteManagementStatistics'

SOURCE = Source(
    id='smc_swm',
    name='SMC solid waste collection statistics (monthly)',
    publisher='Surat Municipal Corporation, Solid Waste Management Department',
    url=URL,
    module='environment',
    cadence='monthly',
    interval_hours=24 * 7,          # page updates monthly with a lag; checking weekly is enough
    geo_note='SMC city (whole corporation area)',
    licence_note='Surat Municipal Corporation web page; public information',
    metrics=(
        Metric('swm.avg_collection_mt_per_day', 'Average municipal solid waste collected', 'tonnes/day',
               'Average MSW collected per day in the month, by collection method (dims.mode).'),
        Metric('swm.vehicles_utilized', 'Vehicles used for collection', 'vehicles',
               'Number of vehicles utilised in the month, by collection method (dims.mode).'),
        Metric('swm.total_trips', 'Collection trips', 'trips',
               'Total trips reported for the month, by collection method (dims.mode).'),
        Metric('swm.smart_dustbins_installed', 'Smart underground dustbins installed', 'dustbins',
               'Smart underground dustbins installed (mode smart_underground_dustbins only).'),
        Metric('swm.total_routes', 'Night scraping/brushing routes', 'routes',
               'Total routes covered by night scraping/brushing (mode night_scraping only).'),
    ),
)

# table title -> collection-method slug (dims.mode). Legacy and current tables share
# slugs where they describe the same method, so each method is one continuous series.
MODES = [
    (r'door to door', 'door_to_door'),
    (r'cradel|cradle|dumper placer', 'dumper_placer_containers'),
    (r'container lifting', 'container_lifting'),
    (r'tractor', 'tractor_hydraulic_trailer'),
    (r'truck', 'truck'),
    (r'smart under ?ground', 'smart_underground_dustbins'),
    (r'night scrap', 'night_scraping'),
    (r'secondary transport', 'secondary_transport'),
    (r'battery operated', 'battery_vehicles'),
]

COLUMNS = [
    (r'average msw collection', 'swm.avg_collection_mt_per_day'),
    (r'no\. of vehicles', 'swm.vehicles_utilized'),
    (r'total trips', 'swm.total_trips'),
    (r'smart dustbins installed', 'swm.smart_dustbins_installed'),
    (r'total route', 'swm.total_routes'),
]


def _mode(title: str) -> str:
    t = title.lower()
    for pat, slug in MODES:
        if re.search(pat, t):
            return slug
    raise ValueError(f'unknown collection method in table title {title!r}')


def fetch(ctx):
    yield ctx.get(URL)


def parse(raw: Raw) -> Result:
    res = Result(geos=[SMC])
    for table in html_tables(raw.body):
        if len(table.rows) < 3 or not re.match(r'\s*\d+\s*\.', table.rows[0][0]):
            continue
        hdr = table.find_row('sr. no', 'period')
        if hdr < 0:
            continue
        mode = _mode(table.rows[0][0])
        cols = {}
        for j, h in enumerate(table.rows[hdr]):
            for pat, metric in COLUMNS:
                if re.search(pat, h.lower()):
                    cols[j] = metric
        for row in table.rows[hdr + 1:]:
            if len(row) < 2 or not row[1].strip():
                continue
            y, m = month_year(row[1])
            start, end = month_period(y, m)
            for j, metric in cols.items():
                if j >= len(row):
                    continue
                v = num(row[j])
                res.observations.append(Obs(
                    metric, 'smc_city', 'smc', start, end, value=v,
                    status='reported' if v is not None else 'not_reported', dims={'mode': mode}))
    return res


def validate(result: Result, raw: Raw) -> None:
    n = sum(1 for o in result.observations if o.metric_id == 'swm.avg_collection_mt_per_day')
    if n < 50:
        raise ValidationError(f'only {n} monthly collection values parsed; page layout may have changed')
    for o in result.observations:
        if o.metric_id == 'swm.avg_collection_mt_per_day' and o.value is not None and not 0 <= o.value < 20000:
            raise ValidationError(f'implausible MSW collection {o.value} t/day ({o.period_start}, {o.dims})')
