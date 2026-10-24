"""Airports Authority of India monthly traffic news: passengers at Surat airport (STV), from Annexure III.

DISABLED (SOURCE.enabled=False): AAI puts its traffic-news downloads behind a registration form, and we do not
fill it in automatically or get around it. Checked on 2026-10-24 with our plain OpenCityBot User-Agent:
- The listing page https://www.aai.aero/en/business-opportunities/aai-traffic-news shows each month's PDFs as
  "click to download" items. Each item opens a form that asks for Name of the Person, Email, an OTP sent to that
  email, Country, Organisation and Purpose/Use. The direct PDF links are in the page, but the site's own
  stylesheet hides them from anonymous visitors until the form is completed
  (".role-anonymous-user .view-aai-traffic-news .views-row .views-field-field-news-type { display:none }", shown
  again only under ".download-destination-added"). Fetching the hidden links directly would skip that
  registration step, so the fetcher does not do it.
- https://www.aai.aero/robots.txt answers 403 Forbidden to our User-Agent, so the crawl policy cannot be read.

Manual workflow (see SOURCE.notes): a person opens the listing page, picks the month, completes the download form
for "Annexure-III" and keeps the PDF. parse() reads Surat's three passenger rows from that saved PDF. The CLI only
fetches, so loading saved files into the database is a maintainer step. The test fixture is pages 1, 2 and 5 of
the August 2026 Annexure III, which a research step saved on 2026-10-23.

Publisher: Airports Authority of India (AAI), Ministry of Civil Aviation, Government of India. Monthly "Traffic
News". The files are irregularly named, e.g. .../sites/default/files/traffic-news/Aug2k26Annex3.pdf next to
Aug2k26Annex_4.pdf and Anex5, so a manual user should pick the file by its label, not guess the name.

Document layout (bilingual Hindi/English PDF made from Excel; pdftotext -layout keeps the columns):
    ANNEXURE-III A  International Passengers   PASSENGERS (IN NOS.)
    ANNEXURE-III B  Domestic Passengers        Passengers(In Number's)
    ANNEXURE-III C  Total Passengers(Domestic+International)
Each part has the same header and one row per airport, grouped by airport category (INTERNATIONAL AIRPORTS,
PPP INTERNATIONAL, JV INTERNATIONAL AIRPORTS, CUSTOM AIRPORTS, DOMESTIC AIRPORTS, ...):
    S.NO  Airport            For The Month              For The Period
                             August   August   %        April To August           %
                             2026     2025     Change   2026-2027    2025-2026    Change
    15 सूरत SURAT             7021     15442    -54.5%   17406        82321        -78.9%
Surat is listed under "INTERNATIONAL AIRPORTS" (AAI-operated) in all three parts.

-> Observations at geo facility:surat_airport, with dims.traffic = 'international' | 'domestic' | 'total' (the
   part of Annexure III the row came from):
     aai.passengers        passengers handled in the report month (period = that calendar month)
     aai.passengers_fytd   passengers from 1 April to the end of the report month (period = FY start to month end)
   The month and year come from the header ("April To August" / "2026 ... 2026-2027"). Only the current-year
   columns are stored. The same-month-last-year columns are left out: they are the previous year's figures
   reprinted (possibly revised), and storing them would compete with that year's own report. The "% Change"
   columns are derived by AAI and not stored. A "-" or blank cell becomes status='not_reported'.

August 2026 (fixture): international 7,021, domestic 105,829, total 112,850 passengers. April-August 2026:
17,406 + 639,691 = 657,097. Surat's international traffic fell 54.5 % from August 2025 (15,442).

Not parsed: Annexures I (traffic summary by airport category), II (aircraft movements) and IV-VI (freight and the
other tables). No copy of them was examined, and fetching them would need the same form.

Caveats: AAI notes that the report "is compiled on the basis of data provided by the respective airport and is
subject to revision". Passengers are counted as AAI publishes them; transit and crew counting rules are not
stated in the annexure.

Geography: Surat airport (STV), a new 'facility' geography under surat_district. It serves Surat city and
district. Cadence: monthly; the report appears about four weeks after the month ends. Units: passengers (number).
Licence: AAI website statistics; no licence is stated on the page.
"""
from __future__ import annotations

from ..model import Geo, Metric, Obs, Raw, Result, Source, ValidationError
from ..parse import fy_period, month_no, month_period, num, pdf_text

URL = 'https://www.aai.aero/en/business-opportunities/aai-traffic-news'
AIRPORT = Geo('facility', 'surat_airport', 'Surat Airport (STV)', 'surat_district', 'surat',
              note='Surat International Airport, operated by the Airports Authority of India; IATA code STV. It '
                   'serves Surat city and district.')
ROW_NAME = 'SURAT'          # airport name as printed in the annexure rows

SOURCE = Source(
    id='aai_surat_airport',
    name='AAI monthly passenger traffic at Surat airport',
    publisher='Airports Authority of India (Traffic News, Annexure III)',
    url=URL,
    module='transport',
    cadence='monthly',
    interval_hours=24 * 7,
    enabled=False,
    geo_note='Surat airport (STV), geo facility:surat_airport under Surat district',
    licence_note='AAI website statistics; licence not stated',
    notes=('Disabled: AAI hides its traffic-news PDF links from anonymous visitors until a download form (name, '
           'email with OTP, country, organisation, purpose) is completed, and robots.txt answers 403 to our '
           'User-Agent (checked 2026-10-24). We do not fill in or skip that form automatically. Manual workflow: '
           'open the listing page, choose the month, complete the form for "Annexure-III" and keep the PDF; '
           'parse() reads the SURAT rows from it. Data are provisional and subject to revision by AAI.'),
    metrics=(
        Metric('aai.passengers', 'Airport passengers (AAI traffic news)', 'passengers',
               'Passengers handled at the airport in the report month, as published in AAI Traffic News '
               'Annexure III, by dims.traffic: international (III A), domestic (III B), total (III C).'),
        Metric('aai.passengers_fytd', 'Airport passengers, financial year to date (AAI traffic news)', 'passengers',
               'Passengers handled from 1 April to the end of the report month ("For The Period" column of '
               'Annexure III), by dims.traffic: international, domestic, total.'),
    ),
)

# English heading of each part of Annexure III -> dims.traffic (checked in this order)
PARTS = (('total passengers', 'total'), ('international passengers', 'international'),
         ('domestic passengers', 'domestic'))


def fetch(ctx):
    # Not called while SOURCE.enabled is False: the PDFs sit behind AAI's download form, which we never automate.
    ctx.log.warning('aai_surat_airport: AAI traffic-news PDFs need a download form; save them by hand '
                    '(see SOURCE.notes)')
    return []


def _month(part: str) -> tuple[int, int, int]:
    """Header lines '... April To August' and '2026  2025  2026-2027  2025-2026' -> (2026, 8, fy 2026)."""
    lines = part.splitlines()
    for i, line in enumerate(lines):
        if 'April To' in line:
            m = month_no(line.split()[-1])
            for later in lines[i + 1:i + 6]:
                words = later.split()
                if words and words[0].isdigit() and len(words[0]) == 4:
                    year = int(words[0])
                    fy = year if m >= 4 else year - 1
                    if f'{fy}-{fy + 1}' not in later:
                        raise ValueError(f'header year line {later.strip()!r} does not show FY {fy}-{fy + 1}')
                    return year, m, fy
    raise ValueError('no "April To <month>" header with a year line in this part of Annexure III')


def parse(raw: Raw) -> Result:
    text = pdf_text(raw.body)
    if 'ANNEXURE-III' not in text:
        raise ValueError('not an AAI Traffic News Annexure III (no "ANNEXURE-III" heading)')
    res = Result(geos=[AIRPORT])
    for part in text.split('ANNEXURE-III')[1:]:
        head = part[:600].lower()
        traffic = next((t for words, t in PARTS if words in head), None)
        if traffic is None:
            raise ValueError(f'unknown Annexure III part: {part[:120].strip()!r}')
        rows = [line.split() for line in part.splitlines() if ROW_NAME in line.split()]
        if len(rows) != 1:
            raise ValueError(f'{len(rows)} {ROW_NAME} rows in the {traffic} part (expected exactly 1)')
        values = rows[0][rows[0].index(ROW_NAME) + 1:]
        if len(values) != 6:
            raise ValueError(f'{traffic}: expected 6 columns after {ROW_NAME}, got {values!r}')
        year, m, fy = _month(part)
        start, end = month_period(year, m)
        for metric, cell, period_start in (('aai.passengers', values[0], start),
                                           ('aai.passengers_fytd', values[3], fy_period(fy)[0])):
            v = num(cell)
            res.observations.append(Obs(metric, AIRPORT.geo_level, AIRPORT.geo_code, period_start, end, value=v,
                                        status='reported' if v is not None else 'not_reported',
                                        dims={'traffic': traffic}))
    return res


def validate(result: Result, raw: Raw) -> None:
    by = {(o.metric_id, o.dims['traffic']): o for o in result.observations}
    if len(by) != 6:
        raise ValidationError(f'expected international, domestic and total passengers (6 values), got {sorted(by)}')
    if len({o.period_end for o in result.observations}) != 1:
        raise ValidationError('the three parts of Annexure III are for different months')
    for metric in ('aai.passengers', 'aai.passengers_fytd'):
        intl, dom, tot = (by[(metric, t)].value for t in ('international', 'domestic', 'total'))
        if None not in (intl, dom, tot) and intl + dom != tot:
            raise ValidationError(f'{metric}: international {intl} + domestic {dom} != total {tot}')
        cap = 2e6 if metric == 'aai.passengers' else 2.4e7      # STV handles about 0.1-0.2 million a month
        if tot is not None and not 0 <= tot <= cap:
            raise ValidationError(f'{metric}: implausible total {tot} passengers at Surat airport')
    for t in ('international', 'domestic', 'total'):
        month, fytd = by[('aai.passengers', t)].value, by[('aai.passengers_fytd', t)].value
        if None not in (month, fytd) and fytd < month:
            raise ValidationError(f'{t}: financial-year-to-date {fytd} is below the month figure {month}')
    end = result.observations[0].period_end
    if end < '2015-01-01' or (raw is not None and raw.retrieved_at and end[:7] >= raw.retrieved_at[:7]):
        raise ValidationError(f'report month ending {end} is implausible for a report read on {raw and raw.retrieved_at}')
