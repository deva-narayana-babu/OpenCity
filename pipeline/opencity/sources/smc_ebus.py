"""SMC electric-bus operations: fleet size and cumulative running, fuel and emission totals.

Page: https://www.suratmunicipal.gov.in/Departments/BRTSEleBusOperations
A small server-rendered block (snapshot 2026-09-27):

    <h3>Total No. of Electric Buses Operated: 450</h3>
    one table, one header row and one data row:
        Total saved fuel (In Litres) | Fuel saving per day (In Litres) |
        GHG emission reduction (CO2e per day in Kg.) | Total GHG emission reduction (CO2e in Kg.) | Total Run Km
        23622009.74 | 22491.96 | 60278.43 | 63306981.51 | 77464469.40
    <div>Last updated on date: 30/04/2026</div>

The page publishes no ridership, energy (kWh) or route figures, so none are stored.

"Last updated on date" is a data date, not the server's render time: the snapshot taken on 2026-09-27 and the
page fetched on 2026-10-18 both said 30/04/2026. Every value is filed as an instant reading on that date, with
publisher_as_of set to it. The "Total ..." figures are running totals since e-bus operations began; the page does
not say when that was, so no start date is invented. Geography: SMC city (the city bus / BRTS network).
"""
from __future__ import annotations

from ..model import Metric, Obs, Raw, Result, Source, ValidationError
from ..parse import html_tables, html_text, num, parse_date
from ..surat import SMC

URL = 'https://www.suratmunicipal.gov.in/Departments/BRTSEleBusOperations'

M = 'ebus.'
SOURCE = Source(
    id='smc_ebus',
    name='SMC electric bus operations (fleet and cumulative totals)',
    publisher='Surat Municipal Corporation (BRTS / city bus operations)',
    url=URL,
    module='transport',
    cadence='monthly',
    interval_hours=24 * 7,          # updated every few months; a weekly check is plenty
    geo_note='SMC city (city bus and BRTS network)',
    licence_note='Surat Municipal Corporation web page; public information',
    notes='Values are dated to the page\'s "Last updated on date". Running totals have no published start date.',
    metrics=(
        Metric(M + 'buses_operated', 'Electric buses operated', 'buses',
               '"Total No. of Electric Buses Operated" on the page, as of its last-updated date.'),
        Metric(M + 'run_km_total', 'Electric bus kilometres run (cumulative)', 'km',
               '"Total Run Km": running total since e-bus operations began (start date not published).'),
        Metric(M + 'fuel_saved_litres_total', 'Fuel saved by electric buses (cumulative)', 'litres',
               '"Total saved fuel (In Litres)": running total since e-bus operations began, as estimated by SMC.'),
        Metric(M + 'fuel_saved_litres_per_day', 'Fuel saved per day by electric buses', 'litres/day',
               '"Fuel saving per day (In Litres)" as published (SMC does not say how the daily figure is derived).'),
        Metric(M + 'ghg_reduction_kg_co2e_total', 'GHG emissions avoided (cumulative)', 'kg CO2e',
               '"Total GHG emission reduction (CO2e in Kg.)": running total since e-bus operations began.'),
        Metric(M + 'ghg_reduction_kg_co2e_per_day', 'GHG emissions avoided per day', 'kg CO2e/day',
               '"GHG emission reduction (CO2e per day in Kg.)" as published.'),
    ),
)

# table header -> metric. Every word of the key must appear in the lower-cased header.
COLUMNS = [
    (('total', 'saved fuel'), M + 'fuel_saved_litres_total'),
    (('fuel saving', 'per day'), M + 'fuel_saved_litres_per_day'),
    (('total ghg',), M + 'ghg_reduction_kg_co2e_total'),
    (('ghg', 'per day'), M + 'ghg_reduction_kg_co2e_per_day'),
    (('run km',), M + 'run_km_total'),
]


def _column_metric(header: str) -> str:
    h = header.lower()
    for words, metric in COLUMNS:
        if all(w in h for w in words):
            return metric
    raise ValueError(f'unknown column {header!r} on the e-bus page')


def _after_colon(text: str, prefix: str) -> str:
    """The text after ':' on the first line that starts with prefix ('' if there is none)."""
    for line in text.splitlines():
        if line.lower().startswith(prefix.lower()):
            return line.split(':', 1)[-1].strip()
    return ''


def fetch(ctx):
    yield ctx.get(URL)


def parse(raw: Raw) -> Result:
    text = html_text(raw.text)
    updated = _after_colon(text, 'Last updated on date')
    if not updated:
        raise ValueError('no "Last updated on date" on the e-bus page')
    day = parse_date(updated).isoformat()
    buses = _after_colon(text, 'Total No. of Electric Buses')
    if not buses:
        raise ValueError('no "Total No. of Electric Buses Operated" on the e-bus page')

    res = Result(geos=[SMC])

    def add(metric, cell):
        v = num(cell)
        res.observations.append(Obs(metric, 'smc_city', 'smc', day, day, value=v,
                                    status='reported' if v is not None else 'not_reported', publisher_as_of=day))

    add(M + 'buses_operated', buses)
    tables = [t for t in html_tables(raw.body) if t.find_row('run km') == 0]
    if len(tables) != 1 or len(tables[0].rows) != 2:
        raise ValueError(f'expected one totals table with a header and one data row, found {len(tables)} tables')
    header, values = tables[0].rows
    for h, cell in zip(header, values):
        add(_column_metric(h), cell)
    return res


def validate(result: Result, raw: Raw) -> None:
    v = {o.metric_id: o.value for o in result.observations}
    missing = [m.id for m in SOURCE.metrics if v.get(m.id) is None]
    if missing:
        raise ValidationError(f'e-bus page is missing values for {missing}')
    if not 10 <= v[M + 'buses_operated'] <= 5000:
        raise ValidationError(f'implausible e-bus fleet {v[M + "buses_operated"]}')
    km = v[M + 'run_km_total']
    if not 1e5 <= km <= 1e10:
        raise ValidationError(f'implausible cumulative e-bus km {km}')
    # diesel buses do roughly 2-5 km per litre, so the fuel "saved" must be well below the km run
    if not 0.1 <= v[M + 'fuel_saved_litres_total'] / km <= 1.0:
        raise ValidationError(f'fuel saved ({v[M + "fuel_saved_litres_total"]} l) does not fit {km} km run')
    # burning one litre of diesel emits about 2.7 kg CO2, so avoided CO2e per litre saved must be close to that
    for kind in ('total', 'per_day'):
        ratio = v[f'{M}ghg_reduction_kg_co2e_{kind}'] / v[f'{M}fuel_saved_litres_{kind}']
        if not 2.0 <= ratio <= 3.5:
            raise ValidationError(f'GHG avoided per litre saved ({kind}) is {ratio:.2f} kg; columns may be shuffled')
    day = result.observations[0].period_start
    if day < '2019-01-01' or (raw is not None and raw.retrieved_at and day > raw.retrieved_at[:10]):
        raise ValidationError(f'last-updated date {day} is implausible')
