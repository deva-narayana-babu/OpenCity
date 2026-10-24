"""NCRB "Crime in India 2024": Surat as one of the 19 metropolitan cities (cases, crime rate, chargesheeting rate).

Publisher of the data: National Crime Records Bureau (NCRB), Ministry of Home Affairs, Government of India,
"Crime in India 2024" (calendar year 1 January - 31 December 2024; tables show 2022, 2023 and 2024).
Files actually fetched: a MIRROR. OpenCity Foundation re-published the metropolitan-city tables as one-sheet
.xlsx files in its CKAN catalogue, dataset "Crime in India - 2024" (data.opencity.in/dataset/crime-in-india-2024,
licence shown as "Other (Public Domain)", organisation "Government of India (GoI)", uploaded 2026-05-07).
NCRB's own site cannot be used by this bot: www.ncrb.gov.in redirects to www.ncrb.mha.gov.in, whose robots.txt
is "User-agent: * / Disallow: /" (checked 2026-10-24), and NCRB publishes the tables as PDF, not as plainly
machine-readable files. data.opencity.in's robots.txt disallows /api/ (so the CKAN API is NOT used) and asks
for "Crawl-Delay: 10"; the resource download URLs below are allowed. fetch() waits 10 s between files.

Requests: one GET per table (10 per run), each a CKAN resource download
    https://data.opencity.in/dataset/7d883875-921a-4820-b298-713c6219bd90/resource/<resource id>/download/<file>
with no parameters. The edition is immutable, so each file is downloaded once (skip_if_seen) and only re-parsed
from the archive after a parser change. A new edition (Crime in India 2025) needs new URLs in TABLES.

File layout (first worksheet; the title is in A1, or "TABLE 6B.1" in A1 and the title in A2):
    TABLE 1B.3 - Total IPC/BNS & SLL Crimes in Metropolitan Cities - 2022-2024
    SL | City | 2022 | 2023 | 2024 | Actual Population (in Lakhs) (2011) | Rate of Cognizable Crimes (IPC+SLL) (2024)
       | Chargesheeting Rate (2024)
    1  | Ahmedabad (Gujarat) | 53845 | ...       (19 city rows, then "TOTAL CITIES")
    19 | Surat (Gujarat)     | 55300 | 63142 | 63166 | 45.8 | 1377.7 | 97.7
Column sets differ by table: 1B.1 and 6B.1 split 2024 into "2024 IPC Cases" / "2024 BNS Cases" / "2024 Total
(IPC+BNS)" (or "2024 (IPC)" / "2024 (BNS)" / "2024 (Total)"); 4B.1, 6B.1, 7B.1 and 7D.1 have no population or
rate (NCRB: no city population figures for children, SCs/STs or senior citizens). parse() reads the header row
and fails on any column it does not know. Only the Surat row is stored; "-" cells become not_reported.

Tables and dims.crime_group:
    1B.1 ipc_bns                  IPC/BNS crimes (2024: IPC and BNS cases shown separately)
    1B.2 sll                      Special & Local Laws crimes
    1B.3 all_cognizable           total cognizable crimes, IPC/BNS + SLL
    3B.1 against_women            crime against women (IPC/BNS + SLL)
    4B.1 against_children         crime against children (IPC/BNS + SLL)
    6B.1 against_senior_citizens  crime against senior citizens (60 years and above)
    7B.1 against_sc               crime/atrocities against Scheduled Castes
    7D.1 against_st               crime/atrocities against Scheduled Tribes
    8B.1 economic_offences        economic offences
    9B.1 cyber                    cyber crimes
(The package's head-wise table 8B.2 and the PDF volumes are not fetched.)

Metrics (geo ncrb_metro_city/surat; periods are calendar years):
    ncrb.cases_registered        cases registered in the year, dims crime_group and law (all; for 2024 in tables
                                 1B.1 and 6B.1 also ipc / bns = registered under the IPC / under the Bharatiya
                                 Nyaya Sanhita, which replaced the IPC on 1 July 2024; ipc + bns = all)
    ncrb.crime_rate_per_lakh     cases per lakh population in 2024, dims crime_group
    ncrb.chargesheeting_rate_pct cases chargesheeted / cases disposed of by police x 100 (NCRB's definition), 2024
    ncrb.rate_population_lakh    the Census 2011 population (lakh) the table divides by, dims crime_group;
                                 filed on the census reference date 2011-03-01
Units: cases; cases per 100,000 people; percent; lakh persons (1 lakh = 100,000).

Geography: new geo level ncrb_metro_city (code 'surat', parent surat_district). NCRB prints these tables for the
19 metropolitan cities with a Census 2011 population above 20 lakh; the figures come from each State Crime
Records Bureau. The reporting area is the city as policed and reported (presumably the Surat
City Police Commissionerate); NCRB does not publish its boundary. It is NOT the SMC area (smc_city) and NOT the
whole district (Surat Rural police is reported separately and is not covered here). The rate base is the Census
2011 "actual population" of the city, 45.85 lakh for Surat (printed as 45.8).

Caveats (from NCRB's notes in the publication):
- Counting follows the Principal Offence Rule: an FIR with several offences counts once, under the most serious.
- Metro-city rates use the 2011 census population while state rates use 2024 projections, so city and state rates
  are not comparable. For a city that has grown since 2011, a rate on the 2011 population is higher than the
  crime per current resident.
- In 3B.1 the population column is the female population (Surat 19.7 lakh; 540.9 for all 19 cities against
  1140.4 total), and the rate is per lakh women, although both the PDF and the mirror label it "Actual Population".
- NCRB: "States/UTs/Cities may not be compared purely on the basis of crime figures"; higher registration can
  reflect better reporting.
- The mirror stores some numbers as binary floats ("73.90000000000001"); values are rounded to 6 decimals.
- Cross-check done 2026-10-24: the Surat rows of 1B.1, 1B.2, 1B.3, 3B.1 and 4B.1 match the NCRB Crime in India 2024
  Volume I PDF (the copy in the same dataset) exactly. Tables 6B.1-9B.1 (footer "Volume II") were not checked
  against the PDF.

Licence: NCRB "Crime in India" is a Government of India publication; the mirror labels it "Other (Public Domain)".
Attribute "NCRB, Crime in India 2024 (via data.opencity.in)".
"""
from __future__ import annotations

import io
import time
import zipfile
import xml.etree.ElementTree as ET

from ..model import Geo, Metric, Obs, Raw, Result, Source, ValidationError
from ..parse import clean, num, year_period

DATASET = 'https://data.opencity.in/dataset/crime-in-india-2024'
RESOURCES = 'https://data.opencity.in/dataset/7d883875-921a-4820-b298-713c6219bd90/resource/'
CRAWL_DELAY = 10            # seconds; data.opencity.in robots.txt asks for "Crawl-Delay: 10"
CENSUS_DAY = '2011-03-01'   # Census 2011 reference date

# NCRB table -> (dims.crime_group, CKAN resource path in the Crime in India 2024 dataset)
TABLES = {
    '1B.1': ('ipc_bns', 'c120a034-bf9c-4a7f-8259-16dc1425bf72/download/table_1b.1.xlsx'),
    '1B.2': ('sll', 'ee3c9a7e-e039-4eca-b7ce-c2c3f99a0d83/download/table_1b.2.xlsx'),
    '1B.3': ('all_cognizable', 'd5b81375-7f97-4a66-bbcc-e7aadb89140e/download/table_1b.3.xlsx'),
    '3B.1': ('against_women', '608413b5-5ff8-4b2b-ba8a-4c620c8837ba/download/table_3b.1.xlsx'),
    '4B.1': ('against_children', 'da728e96-58b8-48d0-84a0-e93b5c120f16/download/table_4b.1.xlsx'),
    '6B.1': ('against_senior_citizens', '4da7b8d7-e4a3-497f-b88e-2562774d591b/download/vol2-6b.1.xlsx'),
    '7B.1': ('against_sc', '65de0c72-1eaf-407a-ab1c-985fc79bf99c/download/vol2-7b.1.xlsx'),
    '7D.1': ('against_st', '9e00feb1-db7b-43d8-a081-79ba0a453069/download/vol2-7d.1.xlsx'),
    '8B.1': ('economic_offences', '27493242-4d73-4173-b248-38398e82f423/download/vol2-8b.1.xlsx'),
    '9B.1': ('cyber', 'c3e62daf-6c30-43b4-b937-be635ff175df/download/vol2-9b.1.xlsx'),
}

GEO = Geo('ncrb_metro_city', 'surat', 'Surat (NCRB metropolitan city)', 'surat_district', 'surat',
          note='City area reported to NCRB for its metropolitan-city tables (presumably the Surat City Police '
               'Commissionerate); not SMC limits, not the whole district. Rate base: Census 2011, 45.85 lakh.')

M = 'ncrb.'

SOURCE = Source(
    id='ncrb_metro_surat',
    name='NCRB Crime in India: Surat metropolitan city',
    publisher='National Crime Records Bureau, Ministry of Home Affairs (Crime in India 2024); '
              'tables mirrored as XLSX by OpenCity Foundation (data.opencity.in)',
    url=DATASET,
    module='police',
    cadence='annual',
    interval_hours=24 * 30,     # one edition a year; files already seen are not downloaded again
    geo_note='Surat as an NCRB metropolitan city (city police reporting area, Census 2011 population 45.85 lakh); '
             'not SMC limits and not Surat Rural',
    licence_note='Government of India (NCRB) publication; mirror labelled "Other (Public Domain)". Attribute '
                 '"NCRB, Crime in India 2024 (via data.opencity.in)".',
    notes='Mirror of NCRB tables: ncrb.mha.gov.in disallows all robots and publishes PDFs. Surat rows of 1B.1, 1B.2, '
          '1B.3, 3B.1 and 4B.1 were checked against the NCRB Volume I PDF. 10 downloads per edition, 10 s apart '
          '(robots.txt Crawl-Delay); the CKAN API (/api/) is disallowed and not used. Rates use Census 2011 '
          'population; 3B.1 rates are per lakh women.',
    metrics=(
        Metric(M + 'cases_registered', 'Crimes registered (NCRB, metropolitan city)', 'cases',
               'Cases registered in the calendar year by dims.crime_group (all_cognizable, ipc_bns, sll, '
               'against_women, against_children, against_senior_citizens, against_sc, against_st, '
               'economic_offences, cyber) and dims.law (all; for 2024 in ipc_bns and against_senior_citizens also '
               'ipc and bns = registered under the IPC / under the BNS). Principal Offence Rule.'),
        Metric(M + 'crime_rate_per_lakh', 'Crime rate (NCRB, metropolitan city)', 'cases per lakh population',
               'Cases registered in the year per 1,00,000 population, using the Census 2011 population in '
               'ncrb.rate_population_lakh (female population for against_women). By dims.crime_group.'),
        Metric(M + 'chargesheeting_rate_pct', 'Chargesheeting rate (NCRB, metropolitan city)', '%',
               'Cases chargesheeted / cases disposed of by police x 100 in the year, by dims.crime_group. '
               'not_reported where NCRB prints "-".'),
        Metric(M + 'rate_population_lakh', 'Population used for the crime rate (Census 2011)', 'lakh persons',
               'The Census 2011 population (in lakh) that the table divides by for the crime rate of '
               'dims.crime_group: the whole city population, or the female population for against_women.'),
    ),
)

NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'


def fetch(ctx):
    for table, (_, path) in TABLES.items():
        raw = ctx.get(RESOURCES + path, meta={'table': table}, skip_if_seen=True, soft=True)
        if raw is not None:
            yield raw
            time.sleep(CRAWL_DELAY)


def _col(ref: str) -> int:
    """Cell reference -> column index from 0: 'B21' -> 1."""
    n = 0
    for ch in ref.rstrip('0123456789'):
        n = n * 26 + ord(ch) - ord('A') + 1
    return n - 1


def _sheet_rows(body: bytes) -> list[list[str]]:
    """Cell text of the first worksheet of an .xlsx file, one list per non-empty row ('' for empty cells)."""
    z = zipfile.ZipFile(io.BytesIO(body))
    shared = []
    if 'xl/sharedStrings.xml' in z.namelist():
        for si in ET.fromstring(z.read('xl/sharedStrings.xml')).iter(NS + 'si'):
            shared.append(''.join(t.text or '' for t in si.iter(NS + 't')))
    rows = []
    for row in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).iter(NS + 'row'):
        cells = {}
        for c in row.iter(NS + 'c'):
            v = c.find(NS + 'v')
            if c.get('t') == 'inlineStr':
                text = ''.join(t.text or '' for t in c.iter(NS + 't'))
            elif v is None:
                text = ''
            elif c.get('t') == 's':
                text = shared[int(v.text)]
            else:
                text = v.text or ''
            cells[_col(c.get('r'))] = clean(text)
        if any(cells.values()):
            rows.append([cells.get(i, '') for i in range(max(cells) + 1)])
    return rows


def _year(header: str) -> int:
    """The last 4-digit year in a header: 'Chargesheeting Rate (2024)' -> 2024."""
    years = [w for w in header.replace('(', ' ').replace(')', ' ').split() if len(w) == 4 and w.isdigit()]
    if not years:
        raise ValueError(f'no year in column header {header!r}')
    return int(years[-1])


def _column(header: str) -> tuple[str, int, str | None] | None:
    """Header -> (metric, year, law), or None for SL/City. '2024 BNS Cases' -> ('ncrb.cases_registered', 2024, 'bns')."""
    h = header.lower()
    if h in ('sl', 'city'):
        return None
    if h[:4].isdigit():
        rest = h[4:]
        if not rest.strip() or 'total' in rest:        # '2023', '2024 Total (IPC+BNS)', '2024 (Total)'
            law = 'all'
        elif 'bns' in rest:                             # '2024 BNS Cases', '2024 (BNS)'
            law = 'bns'
        elif 'ipc' in rest:                             # '2024 IPC Cases', '2024 (IPC)'
            law = 'ipc'
        else:
            raise ValueError(f'unknown cases column {header!r}')
        return M + 'cases_registered', int(h[:4]), law
    if 'population' in h:
        return M + 'rate_population_lakh', _year(header), None
    if h.startswith('rate of'):
        return M + 'crime_rate_per_lakh', _year(header), None
    if h.startswith('chargesheeting rate'):
        return M + 'chargesheeting_rate_pct', _year(header), None
    raise ValueError(f'unknown column {header!r}')


def parse(raw: Raw) -> Result:
    rows = _sheet_rows(raw.body)
    title = ' '.join(c for row in rows[:2] for c in row if c)
    words = title.split()
    table = words[1].upper() if len(words) > 1 and words[0].upper() == 'TABLE' else ''
    if table not in TABLES or 'metropolitan cities' not in title.lower():
        raise ValueError(f'not a known NCRB metropolitan-city table: {title[:100]!r}')
    if raw.meta.get('table') and raw.meta['table'] != table:
        raise ValueError(f'expected table {raw.meta["table"]}, the file is table {table}')
    group = TABLES[table][0]

    head = next((i for i, row in enumerate(rows) if 'City' in row), None)
    if head is None:
        raise ValueError(f'table {table}: no header row with "City"')
    columns = [_column(h) for h in rows[head]]
    city = rows[head].index('City')
    surat = [row for row in rows[head + 1:] if len(row) > city and row[city].lower().startswith('surat')]
    if len(surat) != 1:
        raise ValueError(f'table {table}: expected one Surat row, found {len(surat)}')

    res = Result(geos=[GEO])
    for col, cell in zip(columns, surat[0]):
        if col is None:
            continue
        metric, year, law = col
        v = num(cell)
        v = None if v is None else round(v, 6)
        start, end = (CENSUS_DAY, CENSUS_DAY) if metric == M + 'rate_population_lakh' else year_period(year)
        dims = {'crime_group': group, 'law': law} if law else {'crime_group': group}
        res.observations.append(Obs(metric, 'ncrb_metro_city', 'surat', start, end, value=v,
                                    status='reported' if v is not None else 'not_reported', dims=dims))
    return res


def validate(result: Result, raw: Raw) -> None:
    v = {(o.metric_id, o.period_start[:4], o.dims.get('law')): o.value for o in result.observations}
    group = result.observations[0].dims['crime_group']
    years = sorted(y for m, y, law in v if m == M + 'cases_registered' and law == 'all')
    if len(years) != 3 or int(years[2]) - int(years[0]) != 2:
        raise ValidationError(f'{group}: expected cases for three consecutive years, got {years}')
    if raw is not None and raw.retrieved_at and int(years[-1]) >= int(raw.retrieved_at[:4]):
        raise ValidationError(f'{group}: latest year {years[-1]} is not a completed year')
    latest = years[-1]
    for (m, y, law), value in v.items():
        if value is None:
            continue
        if m == M + 'cases_registered' and not 0 <= value <= 500_000:
            raise ValidationError(f'{group} {y}: implausible case count {value}')
        if m == M + 'chargesheeting_rate_pct' and not 0 <= value <= 100:
            raise ValidationError(f'{group}: chargesheeting rate {value}% out of range')
        if m == M + 'rate_population_lakh' and not 5 <= value <= 100:
            raise ValidationError(f'{group}: implausible population base {value} lakh for Surat')
    split = [v.get((M + 'cases_registered', latest, law)) for law in ('ipc', 'bns', 'all')]
    if split[0] is not None and split[1] is not None and split[0] + split[1] != split[2]:
        raise ValidationError(f'{group} {latest}: IPC {split[0]} + BNS {split[1]} != total {split[2]}')
    rate, pop = v.get((M + 'crime_rate_per_lakh', latest, None)), v.get((M + 'rate_population_lakh', '2011', None))
    cases = v.get((M + 'cases_registered', latest, 'all'))
    if rate is not None and pop and cases is not None:
        # the printed population is rounded to 0.1 lakh, the rate to 0.1: allow 2% plus rounding
        if abs(cases / pop - rate) > 0.02 * rate + 0.1:
            raise ValidationError(f'{group}: rate {rate} does not match {cases} cases / {pop} lakh')
