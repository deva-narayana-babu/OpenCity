"""CPCB daily AQI bulletin (Surat row) and the CPCB CAAQMS station feed (Surat stations).

1. Daily bulletin PDF: https://cpcb.gov.in/upload/Downloads/AQI_Bulletin_YYYYMMDD.pdf
   (the cpcb.nic.in address in older links now answers 301 to cpcb.gov.in). Title on every page:
   "Air Quality Index on Sep 24, 2026 @ 4 PM (Average of past 24 hours)", then one row per city:
       S.No | City | Air Quality | Index Value | Prominent Pollutant | No. of Stations Participated/Total
   A long city name wraps around the row line ("Aurangabad" / "18 ... 84 ... 3/3" / "(Maharashtra)");
   rows are read block by block with words grouped into columns, so wrapped rows are read whole.
   After the table: "* Cities absent in AQI Bulletin due to insufficient data: 1) ..., 2) ...".
   Stored for SURAT only, as smc_city observations dated the bulletin day (publisher_as_of = the
   4 PM bulletin time). The bulletin's "Surat" is the average of CPCB's Surat stations; both stations
   CPCB lists for Surat in 2026 (Science Center - SMC, Katargam) lie inside the SMC area by their feed
   coordinates. If the bulletin lists Surat among the absent cities, cpcb.city_aqi is stored as
   not_reported with that reason.

2. Station feed JSON: https://airquality.cpcb.gov.in/caaqms/rss_feed_with_coordinates
   country[] -> stateId, citiesInState[] -> cityId, stationsInCity[] -> stationName, siteId, latitude,
   longitude, lastUpdate ("27-09-2026 12:00:00"), airQualityIndexValue, predominantParameter,
   pollutants[] -> indexId, min, max, avg, Hourly_sub_index. Fetched plainly (no key, no cookies).
   Stored for the stations under Gujarat / Surat, geo level aq_station (code = CPCB siteId, parent
   surat_district because CPCB's "Surat" label alone does not prove a station is inside SMC limits;
   coordinates are in the geo note), period = the station's lastUpdate.
   The pollutant values are on the AQI scale, not concentrations: in the 2026-09-27 snapshot and the
   2026-10-05 live feed every station's airQualityIndexValue equals the highest pollutant "avg"
   (439/439 and 459/459 stations). validate() keeps checking that for the Surat stations.
   A station that is offline drops out of the feed (Science Center was missing on 2026-10-05); nothing
   is stored for it then.

fetch(): the last 3 bulletins (skip_if_seen: a bulletin is immutable) and one feed snapshot.
Today's bulletin is only asked for after 17:00 IST; it is posted shortly after 16:00.
"""
from __future__ import annotations

import json
import re
from datetime import timedelta

from ..model import Geo, Metric, Obs, Raw, Result, Source, ValidationError
from ..parse import clean, month_no, num, parse_dt, pdf_text
from ..surat import SMC, SURAT_DISTRICT

BULLETIN = 'https://cpcb.gov.in/upload/Downloads/AQI_Bulletin_{ymd}.pdf'
FEED = 'https://airquality.cpcb.gov.in/caaqms/rss_feed_with_coordinates'
LOOKBACK_DAYS = 3
BULLETIN_READY_HOUR = 17      # IST; the 4 PM bulletin is posted a few minutes after 16:00
CITY = 'Surat'
STATE = 'Gujarat'

SOURCE = Source(
    id='cpcb_aqi',
    name='CPCB daily AQI bulletin and CAAQMS station feed: Surat',
    publisher='Central Pollution Control Board, Government of India',
    url='https://airquality.cpcb.gov.in/',
    module='environment',
    cadence='daily',
    interval_hours=12,        # bulletin once a day; a second run catches the evening bulletin and a fresh feed
    geo_note='Bulletin: the "Surat" city row, stored as smc_city (its stations are in the SMC area). '
             'Feed: CPCB stations listed under Gujarat / Surat, geo level aq_station (parent surat_district).',
    licence_note='Government of India (CPCB) public bulletin and feed; CPCB asks that data use acknowledges the '
                 'agencies that generate it',
    notes='Bulletin URL by date (YYYYMMDD), immutable, fetched once. The feed is a live snapshot (hourly at '
          'source); each run stores the latest readings of the Surat stations.',
    metrics=(
        Metric('cpcb.city_aqi', 'Air Quality Index (CPCB daily bulletin)', 'index',
               'City AQI in the CPCB 4 PM bulletin: average over the city\'s stations of the past 24 hours. '
               'not_reported (value_text = reason) when the bulletin lists the city as absent for '
               'insufficient data.'),
        Metric('cpcb.city_aqi_category', 'AQI category (CPCB daily bulletin)', '',
               'value_text = "Air Quality" column: Good, Satisfactory, Moderate, Poor, Very Poor or Severe.'),
        Metric('cpcb.city_prominent_pollutants', 'Prominent pollutant(s) (CPCB daily bulletin)', '',
               'value_text = "Prominent Pollutant" column as printed, e.g. "PM10, PM2.5".'),
        Metric('cpcb.city_stations_participated', 'Stations in the city AQI', 'stations',
               'Number of monitoring stations that contributed to the city AQI that day ("Participated").'),
        Metric('cpcb.city_stations_total', 'Stations in the city', 'stations',
               'Number of CPCB-listed monitoring stations for the city ("Total Stations").'),
        Metric('cpcb.station_aqi', 'Station AQI (CPCB CAAQMS feed)', 'index',
               'airQualityIndexValue of the station in the CPCB feed at lastUpdate.'),
        Metric('cpcb.station_prominent_pollutant', 'Station prominent pollutant (CPCB CAAQMS feed)', '',
               'value_text = predominantParameter of the station in the CPCB feed.'),
        Metric('cpcb.station_subindex_avg', 'Pollutant sub-index, average (CPCB CAAQMS feed)', 'index',
               'The pollutant\'s "avg" value in the CPCB feed (dims.pollutant = the feed\'s indexId: PM2.5, PM10, '
               'NO2, NH3, SO2, CO, OZONE). It is on the AQI scale (the station AQI is the highest of them), '
               'not a concentration.'),
    ),
)

CATEGORIES = {'Good': (0, 50), 'Satisfactory': (51, 100), 'Moderate': (101, 200), 'Poor': (201, 300),
              'Very Poor': (301, 400), 'Severe': (401, 500)}
_ROW = re.compile(r'^(\d+) (.+?) (Good|Satisfactory|Moderate|Very Poor|Poor|Severe) (\d+)(?: (.*?))? (\d+)/(\d+)$')
_TITLE = re.compile(r'Air Quality Index on\s+([A-Za-z]+)\.?\s+(\d{1,2}),\s*(\d{4})\s*@\s*(\d{1,2})(?::(\d{2}))?\s*([AP]M)',
                    re.I)
MIN_CITY_ROWS = 100           # ~240 cities in 2026
MIN_FEED_STATIONS = 100       # ~480 stations in 2026


def bulletin_url(d) -> str:
    return BULLETIN.format(ymd=d.strftime('%Y%m%d'))


def fetch(ctx):
    now = ctx.now
    last = now.date() if now.hour >= BULLETIN_READY_HOUR else now.date() - timedelta(days=1)
    for back in range(LOOKBACK_DAYS - 1, -1, -1):        # oldest first
        d = last - timedelta(days=back)
        raw = ctx.get(bulletin_url(d), meta={'date': d.isoformat()}, skip_if_seen=True, soft=True)
        if raw is not None:
            yield raw
    raw = ctx.get(FEED, soft=True)
    if raw is not None:
        yield raw


def parse(raw: Raw) -> Result:
    head = raw.body[:1024].lstrip()
    if head.startswith(b'%PDF'):
        return _parse_bulletin(raw.body)
    if head.startswith(b'{'):
        return _parse_feed(raw.body)
    raise ValidationError('neither a bulletin PDF nor the station feed JSON (error page?)')


# ---------- bulletin ----------

def _bulletin_time(text: str) -> tuple[str, str]:
    stamps = set()
    for mon, day, year, hh, mm, ampm in _TITLE.findall(text):
        h = int(hh) % 12 + (12 if ampm.upper() == 'PM' else 0)
        stamps.add((f'{int(year):04d}-{month_no(mon):02d}-{int(day):02d}', f'{h:02d}:{int(mm or 0):02d}'))
    if len(stamps) != 1:
        raise ValidationError(f'expected one "Air Quality Index on <date> @ <time>" title, found {sorted(stamps)}')
    day, hm = stamps.pop()
    return day, f'{day}T{hm}'


def _join_block(lines: list[str]) -> str:
    """Read a wrapped row: group words into columns by overlapping spans, then read columns left to right."""
    words = sorted(((m.start(), m.end(), i, m.group()) for i, ln in enumerate(lines)
                    for m in re.finditer(r'\S+', ln)), key=lambda w: (w[0], w[2]))
    cols: list[list] = []
    for s, e, i, t in words:
        if cols and s < cols[-1][1]:
            cols[-1][1] = max(cols[-1][1], e)
            cols[-1][2].append((i, s, t))
        else:
            cols.append([s, e, [(i, s, t)]])
    return ' '.join(t for _, _, ws in cols for _, _, t in sorted(ws))


def _city_rows(table_text: str) -> dict[str, tuple]:
    rows: dict[str, tuple] = {}
    blocks, cur = [], []
    for ln in table_text.replace('\f', '\n\n').split('\n'):     # a page break also ends a row block
        if ln.strip():
            cur.append(ln)
        elif cur:
            blocks.append(cur)
            cur = []
    if cur:
        blocks.append(cur)
    for block in blocks:
        singles = [_ROW.match(clean(ln)) for ln in block]
        if all(singles):
            matches = singles
        else:
            joined = _ROW.match(clean(_join_block(block)))
            matches = [joined] if joined else [m for m in singles if m]
        for m in matches:
            sno, city, cat, aqi, poll, part, total = m.groups()
            if city in rows:
                raise ValidationError(f'city {city!r} appears twice in the bulletin')
            rows[city] = (cat, aqi, (poll or '').strip(), part, total)
    return rows


def _absent_cities(text: str) -> set[str]:
    m = re.search(r'Cities absent in AQI Bulletin[^:]*:(.*?)(?:Notes:|$)', text, re.S | re.I)
    if not m:
        return set()
    body = ' '.join(m.group(1).split())
    return {clean(n).strip(' ,') for n in re.split(r'\d+\)', body) if clean(n).strip(' ,')}


def _parse_bulletin(body: bytes) -> Result:
    return bulletin_result(pdf_text(body))


def bulletin_result(text: str) -> Result:
    """The Surat observations from the bulletin's text (pdftotext -layout)."""
    day, as_of = _bulletin_time(text)
    cut = re.search(r'Cities absent in AQI Bulletin', text, re.I)
    rows = _city_rows(text[:cut.start()] if cut else text)
    if len(rows) < MIN_CITY_ROWS:
        raise ValidationError(f'only {len(rows)} city rows read from the bulletin; layout may have changed')
    res = Result(geos=[SMC])
    o = lambda metric, **kw: Obs(metric, 'smc_city', 'smc', day, day, publisher_as_of=as_of, **kw)
    if CITY in rows:
        cat, aqi, poll, part, total = rows[CITY]
        res.observations += [
            o('cpcb.city_aqi', value=num(aqi)),
            o('cpcb.city_aqi_category', value_text=cat),
            o('cpcb.city_prominent_pollutants', value_text=poll) if _has_text(poll)
            else o('cpcb.city_prominent_pollutants', status='not_reported'),
            o('cpcb.city_stations_participated', value=num(part)),
            o('cpcb.city_stations_total', value=num(total)),
        ]
    elif CITY in _absent_cities(text):
        res.observations.append(o('cpcb.city_aqi', status='not_reported',
                                  value_text='absent from the bulletin: insufficient data'))
    else:
        raise ValidationError(f'{CITY} is neither in the bulletin table nor in its list of absent cities')
    return res


def _has_text(s: str) -> bool:
    """True when a text cell carries something other than a blank / '-' / NA marker."""
    return bool(s) and s.strip().lower() not in {'-', '--', 'na', 'n.a.', 'n/a', 'nil'}


# ---------- station feed ----------

def _parse_feed(body: bytes) -> Result:
    try:
        d = json.loads(body)
        states = d['country']
        n_stations = sum(len(c.get('stationsInCity') or []) for s in states for c in s.get('citiesInState') or [])
    except (ValueError, KeyError, TypeError, AttributeError) as e:
        raise ValidationError(f'station feed is not the expected JSON ({type(e).__name__}: {e})') from None
    if n_stations < MIN_FEED_STATIONS:
        raise ValidationError(f'only {n_stations} stations in the feed; format may have changed')
    res = Result(geos=[SURAT_DISTRICT])
    stations = [st for s in states if clean(s.get('stateId')).lower() == STATE.lower()
                for c in s.get('citiesInState') or [] if clean(c.get('cityId')).lower() == CITY.lower()
                for st in c.get('stationsInCity') or []]
    for st in stations:
        code, name = clean(st['siteId']), clean(st['stationName'])
        res.geos.append(Geo('aq_station', code, name, 'surat_district', 'surat',
                            note=f'CPCB CAAQMS station listed under {STATE} / {CITY}; '
                                 f'lat {st.get("latitude")}, lon {st.get("longitude")}.'))
        when = parse_dt(st['lastUpdate'], '%d-%m-%Y %H:%M:%S')

        def o(metric, cell, dims=None, text=False):
            if text:
                ok = _has_text(clean(cell))
                return Obs(metric, 'aq_station', code, when, when, value_text=clean(cell) if ok else None,
                           status='reported' if ok else 'not_reported', dims=dims or {})
            v = num(cell)
            return Obs(metric, 'aq_station', code, when, when, value=v,
                       status='reported' if v is not None else 'not_reported', dims=dims or {})

        res.observations.append(o('cpcb.station_aqi', st.get('airQualityIndexValue')))
        res.observations.append(o('cpcb.station_prominent_pollutant', st.get('predominantParameter'), text=True))
        for p in st.get('pollutants') or []:
            res.observations.append(o('cpcb.station_subindex_avg', p.get('avg'), {'pollutant': clean(p['indexId'])}))
    return res


# ---------- validation ----------

def validate(result: Result, raw: Raw | None) -> None:
    fetched = (raw.retrieved_at or '')[:10] if raw is not None else ''
    asked = (raw.meta or {}).get('date') if raw is not None else None
    city = {o.metric_id: o for o in result.observations if o.geo_level == 'smc_city'}
    if city:
        day = city['cpcb.city_aqi'].period_start
        if fetched and day > fetched:
            raise ValidationError(f'bulletin dated {day} is after the fetch time {raw.retrieved_at}')
        if asked and asked != day:
            raise ValidationError(f'asked for the bulletin of {asked} but it is dated {day}')
        aqi = city['cpcb.city_aqi'].value
        if aqi is not None:
            cat = city['cpcb.city_aqi_category'].value_text
            lo, hi = CATEGORIES[cat]
            if not lo <= aqi <= hi:
                raise ValidationError(f'{CITY} AQI {aqi} does not fall in the "{cat}" band {lo}-{hi}')
            part = city['cpcb.city_stations_participated'].value
            total = city['cpcb.city_stations_total'].value
            if not 1 <= part <= total <= 50:
                raise ValidationError(f'implausible station counts {part}/{total}')

    by_station: dict[str, dict] = {}
    for o in result.observations:
        if o.geo_level != 'aq_station':
            continue
        if fetched and o.period_start[:10] > fetched:
            raise ValidationError(f'station {o.geo_code} reading at {o.period_start} is after the fetch time')
        if o.value is not None and not 0 <= o.value <= 500:
            raise ValidationError(f'{o.metric_id} {o.value} at {o.geo_code} outside the AQI scale 0-500')
        by_station.setdefault(o.geo_code, {})[(o.metric_id, o.dims.get('pollutant'))] = o.value
    for code, vals in by_station.items():
        aqi = vals.get(('cpcb.station_aqi', None))
        subs = [v for (m, _), v in vals.items() if m == 'cpcb.station_subindex_avg' and v is not None]
        if aqi is not None and subs and abs(aqi - max(subs)) > 1:
            raise ValidationError(f'station {code}: AQI {aqi} is not the highest pollutant sub-index {max(subs)}; '
                                  'the feed\'s "avg" values may no longer be sub-indices')
