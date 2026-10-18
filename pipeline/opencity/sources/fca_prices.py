"""DoCA Price Monitoring Division: daily retail and wholesale prices of essential commodities, Surat centre.

DISABLED (SOURCE.enabled=False): the report form is captcha-protected, and we do not automate captchas.

Checked on 2026-10-18 with our plain OpenCityBot User-Agent (two GETs, two form postbacks, no report requested;
re-checked by the verifier with one GET the same day: captcha still on the landing form):
  GET  https://fcainfoweb.nic.in/reports/report_menu_web.aspx
       ASP.NET form: Report Type (Retail | Wholesale), Language, radio "Price report" / "Average/Month End
       Report" / "Variation Report ...", and a captcha (<img src="../CaptchaImage.aspx">, a required
       "Enter captcha" box).
  "Price report" -> a select: "Daily Prices" | "Zonewise Average Price".
  "Daily Prices" -> one Date box (dd/MM/yyyy) and a "Get Data" button whose onclick md5-hashes the captcha
       in the browser before posting; the report opens in a new window.
So every report needs a solved captcha. The fcainfoweb home page shows only all-India averages, headed
"All India Average Retail Price(₹/Kg)" and "All India Average Wholesale Price(₹/Qtl.)": that is where the
units below come from. Surat is centre 17 of the West Zone list
(reference/food-prices/india-doca-price-reporting-centres-2026-09-27.html).

Manual workflow (see SOURCE.notes): a person fills the form, solves the captcha and saves the report page.
parse() reads the Surat row from that saved page.

What parse() expects. No real report page has been obtained, so this layout is an assumption:
  - a line with the report date ("Date : 17/10/2026", "as on 17/10/2026" or "17-Oct-2026");
  - the words "retail price" or "wholesale price" (exactly one of the two);
  - an HTML table with commodity names across one header row and centres down the rows, with one row
    labelled "Surat".
If the real layout differs, parse() or validate() raises an error instead of guessing.

Stored: fca.retail_price (Rs/kg) and fca.wholesale_price (Rs/quintal). They are separate metrics because
their units differ. Each is one observation per commodity (dims.commodity) for the report date, at geo
reporting_centre:surat. Only the 23 commodities in COMMODITIES are read. Other columns, such as the home
page's "additional commodities" (eggs, banana, ...), are skipped because their units are not stated.
"""
from __future__ import annotations

from ..model import Geo, Metric, Obs, Raw, Result, Source, ValidationError
from ..parse import html_tables, html_text, num, parse_date

URL = 'https://fcainfoweb.nic.in/reports/report_menu_web.aspx'
CENTRE_NAME = 'Surat'           # spelling in DoCA's centre list
CENTRE = Geo('reporting_centre', 'surat', 'Surat (DoCA price reporting centre)', 'surat_district', 'surat',
             note='DoCA Price Monitoring Division centre "Surat" (West Zone). DoCA does not publish which '
                  'markets or shops are surveyed.')

M = 'fca.'
SOURCE = Source(
    id='fca_prices',
    name='DoCA daily retail and wholesale prices of essential commodities (Surat centre)',
    publisher='Price Monitoring Division, Department of Consumer Affairs, Government of India',
    url=URL,
    module='food',
    cadence='daily',
    interval_hours=24,
    enabled=False,
    geo_note='DoCA price reporting centre "Surat" (Gujarat, West Zone); surveyed markets not published',
    licence_note='Government of India web report (fcainfoweb.nic.in); public information',
    notes='Disabled: every fcainfoweb price report needs a captcha (checked 2026-10-18), and we do not automate '
          'captchas. Manual workflow: open https://fcainfoweb.nic.in/reports/report_menu_web.aspx, pick Report '
          'Type Retail (or Wholesale) and Language English, choose "Price report", then "Daily Prices", enter the '
          'date (dd/mm/yyyy), type the captcha and click "Get Data". The report opens in a new window: save it as '
          '"Web page, HTML only", one file per date and report type. parse() reads the Surat row from it. Its '
          'layout is unverified until a real saved report is tested. Weekend and holiday figures are provisional '
          'until DoCA verifies them on the next working day (disclaimer on the report form).',
    metrics=(
        Metric(M + 'retail_price', 'Retail price of essential commodities (DoCA, Surat centre)', 'Rs/kg',
               'Daily retail price reported by the Surat centre to DoCA, by commodity (dims.commodity). DoCA '
               'gives retail prices in Rs/kg. Milk is marked "@" by DoCA, and its unit (probably per litre) '
               'was not confirmed on the pages checked.'),
        Metric(M + 'wholesale_price', 'Wholesale price of essential commodities (DoCA, Surat centre)',
               'Rs/quintal',
               'Daily wholesale price reported by the Surat centre to DoCA, by commodity (dims.commodity). '
               'DoCA gives wholesale prices in Rs/quintal (100 kg). Milk is marked "@" and its basis was not '
               'confirmed.'),
    ),
)

# header spelling (lower case, letters only) -> commodity name as printed on the fcainfoweb home page
# (v4.2, 2026-10-18). "masurdal" is the spelling in the home page's own description text.
COMMODITIES = {
    'rice': 'Rice', 'brokenrice': 'Broken Rice', 'wheat': 'Wheat', 'attawheat': 'Atta (Wheat)',
    'gramdal': 'Gram Dal', 'turarhardal': 'Tur/Arhar Dal', 'uraddal': 'Urad Dal', 'moongdal': 'Moong Dal',
    'masoordal': 'Masoor Dal', 'masurdal': 'Masoor Dal',
    'groundnutoilpacked': 'Groundnut Oil (Packed)', 'mustardoilpacked': 'Mustard Oil (Packed)',
    'vanaspatipacked': 'Vanaspati (Packed)', 'soyaoilpacked': 'Soya Oil (Packed)',
    'sunfloweroilpacked': 'Sunflower Oil (Packed)', 'palmoilpacked': 'Palm Oil (Packed)',
    'potato': 'Potato', 'onion': 'Onion', 'tomato': 'Tomato',
    'sugar': 'Sugar', 'gur': 'Gur', 'milk': 'Milk', 'tealoose': 'Tea Loose', 'saltpackiodised': 'Salt Pack (Iodised)',
}

# plausible price range per report type, in the report's own unit
RANGES = {'retail': (1, 1500), 'wholesale': (100, 150000)}


def _key(header: str) -> str:
    """'Atta (Wheat)' -> 'attawheat', 'Milk @' -> 'milk'."""
    return ''.join(ch for ch in header.lower() if ch.isalpha())


def _report_day(text: str) -> str:
    """The first date on a line that mentions 'date' or 'as on', e.g. 'Date : 17/10/2026'."""
    for line in text.splitlines():
        if 'date' not in line.lower() and 'as on' not in line.lower():
            continue
        for word in line.replace(':', ' ').split():
            try:
                return parse_date(word, '%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y', '%d-%b-%Y').isoformat()
            except ValueError:
                continue
    raise ValueError('no report date (a "Date" or "as on" line with dd/mm/yyyy) on the page')


def _price_type(text: str) -> str:
    t = text.lower()
    kinds = [k for k in ('retail', 'wholesale') if k + ' price' in t]
    if len(kinds) != 1:
        raise ValueError(f'cannot tell a retail report from a wholesale one (found {kinds or "neither"})')
    return kinds[0]


def _surat_row(body) -> tuple[list[str], list[str]] | None:
    """(header, row) from the first table with commodities across a header row and a 'Surat' row below it."""
    for table in html_tables(body):
        for i, header in enumerate(table.rows):
            if sum(_key(c) in COMMODITIES for c in header) < 10:
                continue
            for row in table.rows[i + 1:]:
                if any(c.strip().lower() == CENTRE_NAME.lower() for c in row[:3]):
                    return header, row
            break
    return None


def fetch(ctx):
    # Not called while SOURCE.enabled is False: the report needs a captcha, which we never automate.
    ctx.log.warning('fca_prices: fcainfoweb reports need a captcha; save them by hand (see SOURCE.notes)')
    return []


def parse(raw: Raw) -> Result:
    found = _surat_row(raw.body)
    if found is None:
        if b'CaptchaImage' in raw.body:
            raise ValueError('this is the captcha-protected report form, not a saved report')
        raise ValueError(f'no price table with a {CENTRE_NAME!r} row (commodities across, centres down)')
    text = html_text(raw.text)
    day = _report_day(text)
    metric = M + _price_type(text) + '_price'

    res = Result(geos=[CENTRE])
    for h, cell in zip(*found):
        name = COMMODITIES.get(_key(h))
        if name is None:
            continue
        v = num(cell)       # None for a blank, '-' or NA cell
        # a blank cell or a published 0 is not a price: not_reported, no value
        res.observations.append(Obs(
            metric, 'reporting_centre', 'surat', day, day, value=v or None,
            status='reported' if v else 'not_reported', value_text='published as 0' if v == 0 else None,
            dims={'commodity': name}, publisher_as_of=day))
    return res


def validate(result: Result, raw: Raw) -> None:
    obs = result.observations
    names = {o.dims['commodity'] for o in obs}
    if len(names) < 15:
        raise ValidationError(f'only {len(names)} known commodity columns read; the report layout may differ')
    kind = 'retail' if obs[0].metric_id == M + 'retail_price' else 'wholesale'
    lo, hi = RANGES[kind]
    for o in obs:
        if o.value is not None and not lo <= o.value <= hi:
            raise ValidationError(f'{kind} price {o.value} for {o.dims["commodity"]} is outside {lo}-{hi}; '
                                  f'wrong unit or report type?')
    day = obs[0].period_start
    if day < '2009-01-01' or (raw is not None and raw.retrieved_at and day > raw.retrieved_at[:10]):
        raise ValidationError(f'report date {day} is implausible')
