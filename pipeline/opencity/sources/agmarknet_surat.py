"""Agmarknet daily arrivals and prices for the APMC markets of Surat district.

Since 18 Oct 2026 the Agmarknet report endpoint below answers every request with HTTP 400
"Captcha key and captcha value are required", so it is no longer called. fetch() now reads the
official open-data copy of the same prices instead:
    GET https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070
        ?api-key=<DATA_GOV_IN_API_KEY>&format=json&limit=1000&offset=0&filters[state.keyword]=Gujarat
("Current daily price of various commodities from various markets (Mandi)"). It needs a free API
key from data.gov.in in the DATA_GOV_IN_API_KEY environment variable; without it the source is
disabled. The key is sent but never stored or logged (the framework redacts it from URLs).
That resource has prices (Rs/quintal) but no arrivals, and no "NIL Transaction" entries.
Its record layout below follows the data.gov.in documentation; it has not been checked against a
live response yet (the public sample key was rate-limited), so check the first real run.
    records[] {state, district, market, commodity, variety, grade, arrival_date "dd/mm/yyyy",
               min_price, max_price, modal_price}   (older responses spell keys like "Min_x0020_Price")

The old endpoint, kept here because parse() still reads its archived responses and the frozen
copies in reference/ (the one agmarknet.gov.in's own report page calls):
    POST https://api.agmarknet.gov.in/v1/prices-and-arrivals/market-report/daily
    body {"date": "YYYY-MM-DD", "marketIds": [...], "stateIds": [11], "includeExcel": false}
Checked on 2026-10-04: it answers our plain OpenCityBot User-Agent without Origin/Referer
headers, so nothing is spoofed. One request per date.

Response (JSON), one document per date:
    title   "Market-wise, Commodity-wise Daily Report on: 01-Sep-2026"
    states[].markets[]  {marketId, marketName, commodities[]}
    commodities[] is one of
      - {commodityId, commodityName, total_arrivals, data: [{marketCenter, arrivals, unitOfArrivals,
         variety, grade, minimumPrice, maximumPrice, modalPrice, unitOfPrice}]}
      - {commodityName: "NIL Transaction - No Arrivals" | "... - Weekend Holiday" | "... - Public Holiday"}
        (no data key): the market states that it had no transactions that day
      - empty list: the market has uploaded nothing for that day (yet)
In every frozen response (28 Aug - 26 Sep 2026) arrivals are "Metric Tonnes" and prices
"Rs./Quintal"; any other unit raises instead of being silently mixed in.

What is stored, per market (geo apmc_market, code = Agmarknet market id) and day:
  - per commodity line (dims commodity/variety/grade): arrivals in tonnes and min/max/modal price
    in Rs/quintal. A price or arrival published as 0 is not a measurement: stored as not_reported
    with value_text "published as 0".
  - agm.market_reported: one observation per market-day. Reported -> value = number of commodity
    price lines in that day's report. A "NIL Transaction - ..." entry -> not_reported, value None,
    value_text = Agmarknet's reason verbatim (never 0 arrivals). An empty commodity list or a market
    missing from the response -> nothing is stored (nothing was published; a later upload fills it).

Geography: Agmarknet's market master files 33 markets under district "Surat" (district_id 159),
including the markets of Tapi district (split from Surat in 2007): Vyara, Songadh, Uchhal, Nizar,
Valod, Kukarmunda and their sub-yards. Their master addresses say "Dist. Tapi" (or are sub-yards of
those committees), so they are excluded here; only the 21 Surat-district market ids are requested
and parsed. Only the Surat APMC main yard (id 64, Sardar Market, Dumbhal, Puna-Kumbharia Road) is
known to be inside SMC limits.
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timedelta

from ..model import Geo, Metric, Obs, Raw, Result, Source, ValidationError
from ..parse import clean, num, parse_date

URL = 'https://api.agmarknet.gov.in/v1/prices-and-arrivals/market-report/daily'   # captcha since Oct 2026
PAGE = 'https://agmarknet.gov.in/'
OGD_URL = 'https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070'
OGD_PAGE_SIZE = 1000
API_KEY = os.environ.get('DATA_GOV_IN_API_KEY', '')
GUJARAT_STATE_ID = 11

_INSIDE = 'Inside SMC limits.'
_OUTSIDE = 'Taluka market outside SMC limits.'
_UNKNOWN = ('Marked inactive (status 0) in the Agmarknet market master, which gives no address; '
            'position relative to SMC limits not determined.')

# Surat-district markets in Agmarknet (market id -> name, geo note). Names and addresses from
# reference/food-prices/india-agmarknet-market-{district-state,master-with-category}-2026-09-27.json
SURAT_MARKETS: dict[int, tuple[str, str]] = {
    64: ('Surat APMC', 'Principal market yard, "Sardar Market", Dumbhal, Puna-Kumbharia Road, Surat 395010. '
                       + _INSIDE),
    448: ('S.Mandvi APMC', 'Listed with category "Other" at the same address as Mandvi APMC (1686): Ambaji '
                           'Road, Mandvi taluka. ' + _OUTSIDE),
    785: ('Bardoli APMC', 'Market yard, Bardoli. ' + _OUTSIDE),
    1546: ('Mahuva APMC', 'Principal market yard, Mahuva. ' + _OUTSIDE),
    1547: ('Kosamba APMC', 'Principal market yard, Tarsadi-Kosamba, Mangrol taluka. ' + _OUTSIDE),
    1686: ('Mandvi APMC', 'Principal market yard, Ambaji Road, Mandvi. ' + _OUTSIDE),
    2553: ('Surat(Old Sardar Market) APMC', 'Sub-yard of Surat APMC; marked inactive (status 0) in the Agmarknet '
                                            'market master and never present in the 2026 responses. Address '
                                            'only says "Market yard Surat": position relative to SMC limits '
                                            'not determined.'),
    2580: ('Mandvi(Amba Paradi) APMC', 'Sub-yard of Mandvi APMC. ' + _OUTSIDE),
    2622: ('Mahuva(Anaval) APMC', 'Sub-yard of Mahuva APMC at Anaval. ' + _OUTSIDE),
    2623: ('Bardoli(Kadod) APMC', 'Sub-yard of Bardoli APMC at Kadod. ' + _OUTSIDE),
    2793: ('Kosamba(Vankal) APMC', 'Sub-yard of Kosamba APMC at Vankal, Mangrol taluka. ' + _OUTSIDE),
    2794: ('Kosamba(Zangvav) APMC', 'Sub-yard of Kosamba APMC at Zankhvav. ' + _OUTSIDE),
    2816: ('Bardoli(Madhi) APMC', 'Madhi, Bardoli taluka. ' + _OUTSIDE),
    3847: ('Kim APMC', _UNKNOWN),
    3848: ('Olapad APMC', _UNKNOWN),
    3849: ('Umarpada APMC', _UNKNOWN),
    3850: ('Kamrej APMC', _UNKNOWN),
    3851: ('chorayashi APMC', _UNKNOWN),
    3852: ('Navagam APMC', _UNKNOWN),
    3853: ('Kadodara APMC', _UNKNOWN),
    3878: ('Mangarol APMC', _UNKNOWN),
}

# Filed under "Surat" by Agmarknet but physically in Tapi district: never requested, dropped if present.
TAPI_MARKETS: dict[int, str] = {
    449: 'Vyra APMC', 1548: 'Uchhal APMC', 1549: 'Valod APMC', 1550: 'Nizar APMC', 1559: 'Songadh APMC',
    2581: 'Vyara(Paati) APMC', 2624: 'Uchhal(Karod) APMC', 2625: 'Valod(Buhari) APMC',
    2626: 'KUKARMUNDA APMC', 2629: 'Songadh(Badarpada) APMC', 2795: 'Songadh(Umrada) APMC',
    2796: 'Nizar(Rumkitalav) APMC',
}

MARKET_GEOS = [Geo('apmc_market', str(mid), name, 'surat_district', 'surat',
                   note=f'Agmarknet market id {mid}. {note}')
               for mid, (name, note) in SURAT_MARKETS.items()]

M_ARRIVALS = 'agm.arrivals_tonnes'
M_MIN = 'agm.price_min_rs_per_qtl'
M_MAX = 'agm.price_max_rs_per_qtl'
M_MODAL = 'agm.price_modal_rs_per_qtl'
M_MARKET = 'agm.market_reported'

SOURCE = Source(
    id='agmarknet_surat',
    name='Agmarknet daily commodity arrivals and prices, Surat district APMC markets',
    publisher='Directorate of Marketing & Inspection (Agmarknet), Ministry of Agriculture & Farmers Welfare, '
              'Government of India',
    url=PAGE,
    module='food',
    cadence='daily',
    interval_hours=12,      # markets upload in the evening and sometimes days late; 10-day lookback each run
    geo_note='APMC markets of Surat district (geo apmc_market, code = Agmarknet market id, parent '
             'surat_district). Tapi-district markets that Agmarknet files under Surat (Vyara, Songadh, '
             'Uchhal, Nizar, Valod, Kukarmunda and sub-yards) are excluded. Only Surat APMC (64, Sardar '
             'Market, Dumbhal) is inside SMC limits.',
    licence_note='Government of India data (Agmarknet, published on data.gov.in under the Government Open Data '
                 'License - India); public information',
    notes='Reads the data.gov.in open-data copy of the Agmarknet daily prices (Gujarat, filtered to Surat '
          'district here). Needs DATA_GOV_IN_API_KEY (free from data.gov.in); disabled without it. The old '
          f'Agmarknet endpoint ({URL}) has required a captcha since 18 Oct 2026 and is not used; parse() still '
          'reads its archived responses, which also carry arrivals and "NIL Transaction" entries.',
    enabled=bool(API_KEY),
    metrics=(
        Metric(M_ARRIVALS, 'Commodity arrivals', 'tonnes',
               'Quantity of the commodity (dims commodity/variety/grade) arriving at the market that day, '
               'Agmarknet column "Arrivals" in "Metric Tonnes". Published 0 -> not_reported. Only in responses '
               'from the old Agmarknet endpoint; the data.gov.in copy has no arrivals.'),
        Metric(M_MIN, 'Minimum price', 'Rs/quintal',
               'Lowest price of the day for the commodity line, Agmarknet "Minimum Price" (Rs./Quintal). '
               'Published 0 -> not_reported.'),
        Metric(M_MAX, 'Maximum price', 'Rs/quintal',
               'Highest price of the day for the commodity line, Agmarknet "Maximum Price" (Rs./Quintal). '
               'Published 0 -> not_reported.'),
        Metric(M_MODAL, 'Modal price', 'Rs/quintal',
               'Price at which most of the commodity traded that day, Agmarknet "Modal Price" '
               '(Rs./Quintal). Published 0 -> not_reported.'),
        Metric(M_MARKET, 'Market reported prices', 'price lines',
               'One per market and day. reported: value = number of commodity/variety/grade price lines '
               'in that day\'s report. not_reported: the market filed a "NIL Transaction" entry; '
               'value_text gives Agmarknet\'s reason verbatim (e.g. "NIL Transaction - No Arrivals", '
               '"NIL Transaction - Weekend Holiday"; old endpoint only). Days with nothing uploaded have no '
               'observation.'),
    ),
)

_ARRIVAL_UNITS = {'metric tonnes': 1.0, 'metric tonne': 1.0, 'tonnes': 1.0, 'tonne': 1.0}
_PRICE_UNITS = {'rs./quintal', 'rs/quintal', 'rs. /quintal'}
_TITLE_DATE = re.compile(r'Report on:\s*(\d{1,2}-[A-Za-z]{3}-\d{4})')


def _market_key(name) -> str:
    """'Bardoli(Kadod) APMC' and 'Bardoli(Kadod)' -> 'bardoli(kadod)' (data.gov.in drops the ' APMC')."""
    return clean(name).lower().replace(' apmc', '').replace(' ', '')


_SURAT_BY_NAME = {_market_key(name): mid for mid, (name, _) in SURAT_MARKETS.items()}
_TAPI_NAMES = {_market_key(name) for name in TAPI_MARKETS.values()}


def fetch(ctx):
    if not API_KEY:
        ctx.log.warning('DATA_GOV_IN_API_KEY is not set; Agmarknet prices skipped')
        return
    offset = 0
    while True:
        raw = ctx.get(OGD_URL, params={'api-key': API_KEY, 'format': 'json', 'limit': OGD_PAGE_SIZE,
                                       'offset': offset, 'filters[state.keyword]': 'Gujarat'})
        yield raw
        doc = json.loads(raw.body)
        offset += OGD_PAGE_SIZE
        if not doc.get('records') or offset >= int(doc.get('total') or 0):
            break


def report_date(doc: dict) -> str:
    m = _TITLE_DATE.search(doc.get('title') or '')
    if not m:
        raise ValidationError(f'no report date in title {doc.get("title")!r}')
    return datetime.strptime(m.group(1), '%d-%b-%Y').date().isoformat()


def _cell(raw_value, factor: float = 1.0) -> dict:
    """Obs fields for one numeric cell. null/blank -> not_reported; a published 0 is not a real price or
    arrival either, so it is not_reported too (with value_text saying so)."""
    v = num(raw_value)
    if v is None:
        return {'value': None, 'status': 'not_reported'}
    if v == 0:
        return {'value': None, 'value_text': 'published as 0', 'status': 'not_reported'}
    return {'value': round(v * factor, 6), 'status': 'reported'}


def parse(raw: Raw) -> Result:
    try:
        doc = json.loads(raw.body)
    except ValueError as e:
        raise ValidationError(f'response is not JSON: {e}') from None
    if isinstance(doc, dict) and 'records' in doc:
        return _parse_ogd(doc)
    if not isinstance(doc, dict) or doc.get('success') is not True:
        raise ValidationError(f'Agmarknet did not return success: {str(doc)[:300]}')
    day = report_date(doc)
    want = (raw.meta or {}).get('date')
    if want and want != day:
        raise ValidationError(f'asked for {want} but the report is for {day}')

    res = Result(geos=list(MARKET_GEOS))
    for state in doc.get('states') or []:
        if state.get('stateId') != GUJARAT_STATE_ID:
            raise ValidationError(f'unexpected state {state.get("stateId")} {state.get("stateName")!r}')
        for market in state.get('markets') or []:
            mid = market.get('marketId')
            if mid in TAPI_MARKETS:
                continue
            if mid not in SURAT_MARKETS:
                raise ValidationError(f'unexpected market {mid} {market.get("marketName")!r} in response')
            code = str(mid)
            lines = 0
            nil_reasons = []
            for com in market.get('commodities') or []:
                name = clean(com.get('commodityName'))
                if 'data' not in com:
                    if not name.lower().startswith('nil transaction'):
                        raise ValidationError(f'market {mid}: commodity {name!r} without data rows')
                    nil_reasons.append(name)
                    continue
                for row in com['data']:
                    ua = clean(row.get('unitOfArrivals')).lower()
                    up = clean(row.get('unitOfPrice')).lower()
                    if ua not in _ARRIVAL_UNITS:
                        raise ValueError(f'market {mid} {name}: unknown arrival unit {row.get("unitOfArrivals")!r}')
                    if up not in _PRICE_UNITS:
                        raise ValueError(f'market {mid} {name}: unknown price unit {row.get("unitOfPrice")!r}')
                    dims = {'commodity': name, 'variety': clean(row.get('variety')), 'grade': clean(row.get('grade'))}
                    cells = [(M_ARRIVALS, row.get('arrivals'), _ARRIVAL_UNITS[ua]), (M_MIN, row.get('minimumPrice'), 1.0),
                             (M_MAX, row.get('maximumPrice'), 1.0), (M_MODAL, row.get('modalPrice'), 1.0)]
                    for metric, cell, factor in cells:
                        res.observations.append(Obs(metric, 'apmc_market', code, day, day, dims=dims,
                                                    **_cell(cell, factor)))
                    lines += 1
            if lines:
                res.observations.append(Obs(M_MARKET, 'apmc_market', code, day, day, value=lines))
            elif nil_reasons:
                res.observations.append(Obs(M_MARKET, 'apmc_market', code, day, day, value=None,
                                            value_text='; '.join(dict.fromkeys(nil_reasons)), status='not_reported'))
    return res


def _parse_ogd(doc: dict) -> Result:
    """data.gov.in records: one price line per market, commodity, variety, grade and arrival date."""
    res = Result(geos=list(MARKET_GEOS))
    lines: dict[tuple, int] = {}
    seen: dict[tuple, tuple] = {}
    for rec in doc['records']:
        r = {k.lower().replace('_x0020_', '_'): v for k, v in rec.items()}
        if clean(r.get('state')).lower() != 'gujarat' or clean(r.get('district')).lower() != 'surat':
            continue
        name = _market_key(r.get('market'))
        if name in _TAPI_NAMES:
            continue
        if name not in _SURAT_BY_NAME:
            raise ValidationError(f'unknown Surat-district market {r.get("market")!r}; add it to SURAT_MARKETS')
        code = str(_SURAT_BY_NAME[name])
        day = parse_date(clean(r.get('arrival_date'))).isoformat()
        dims = {'commodity': clean(r.get('commodity')), 'variety': clean(r.get('variety')), 'grade': clean(r.get('grade'))}
        prices = (r.get('min_price'), r.get('max_price'), r.get('modal_price'))
        key = (code, day, tuple(dims.values()))
        if key in seen:
            if seen[key] != prices:
                raise ValidationError(f'conflicting rows for {key}: {seen[key]} vs {prices}')
            continue                     # an exact repeat of a row already read
        seen[key] = prices
        for metric, cell in zip((M_MIN, M_MAX, M_MODAL), prices):
            res.observations.append(Obs(metric, 'apmc_market', code, day, day, dims=dims, **_cell(cell)))
        lines[(code, day)] = lines.get((code, day), 0) + 1
    for (code, day), n in sorted(lines.items()):
        res.observations.append(Obs(M_MARKET, 'apmc_market', code, day, day, value=n))
    return res


def validate(result: Result, raw: Raw | None) -> None:
    surat_codes = {str(m) for m in SURAT_MARKETS}
    days = {o.period_start for o in result.observations}
    for d in days:
        if d < '2010-01-01':
            raise ValidationError(f'implausible report date {d}')
        if raw is not None and raw.retrieved_at and d > raw.retrieved_at[:10]:
            raise ValidationError(f'report date {d} is after the fetch time {raw.retrieved_at}')

    lines: dict[str, int] = {}
    prices: dict[tuple, dict] = {}
    for o in result.observations:
        if o.geo_level != 'apmc_market' or o.geo_code not in surat_codes:
            raise ValidationError(f'observation outside the Surat-district markets: {o.geo_level}:{o.geo_code}')
        if o.metric_id == M_MARKET:
            continue
        if o.metric_id == M_MODAL:
            lines[(o.geo_code, o.period_start)] = lines.get((o.geo_code, o.period_start), 0) + 1
        if o.metric_id == M_ARRIVALS:
            if o.value is not None and not 0 < o.value < 20000:
                raise ValidationError(f'implausible arrivals {o.value} t ({o.geo_code} {o.dims})')
        elif o.value is not None:
            if not 0 < o.value < 1_000_000:
                raise ValidationError(f'implausible price {o.value} Rs/quintal ({o.geo_code} {o.dims})')
            prices.setdefault((o.geo_code, tuple(sorted(o.dims.items()))), {})[o.metric_id] = o.value

    for o in result.observations:
        n = lines.get((o.geo_code, o.period_start))
        if o.metric_id == M_MARKET and o.status == 'reported' and o.value != n:
            raise ValidationError(f'market {o.geo_code} {o.period_start}: {o.value} lines counted but {n} parsed')

    # publishers occasionally slip (modal outside min..max); many such lines means columns got mixed up
    full = [p for p in prices.values() if len(p) == 3]
    bad = [p for p in full if not p[M_MIN] <= p[M_MODAL] <= p[M_MAX]]
    if len(bad) > max(3, len(full) // 20):
        raise ValidationError(f'{len(bad)} of {len(full)} lines violate min <= modal <= max; columns may be misread')

    if raw is not None and raw.body:
        doc = json.loads(raw.body)
        listed = {m.get('marketId') for s in doc.get('states') or [] for m in s.get('markets') or []}
        if doc.get('states') and not listed & set(SURAT_MARKETS):
            raise ValidationError('response lists none of the requested Surat-district markets')
