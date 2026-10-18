"""SMC Air Quality Management Cell: monitoring stations, past-result PDFs and the latest real-time reading.

Three documents per refresh:

1. https://www.suratmunicipal.gov.in/Departments/CAAQMS (HTML, no readings): station lists, kept as records
     - "Location of Manual Air monitoring station installed by GPCB": address + DMS coordinates -> aq_station
     - "Locations of Sensor based CAAQMS installed by SMC" (Varachha, Limbayat zone offices)   -> aq_station
     - "Locations of USEPA Approved CAAQMS (Proposed by SMC / by GPCB)": zone + location      -> aq_station_proposed
   Coordinates are converted from the published degrees-minutes-seconds to decimal degrees (both kept).

2. https://www.suratmunicipal.gov.in/Departments/AirQualityResults (HTML)
     - "Past Results": yearly PDF reports per station (Limbayat 2018-2021, Varachha 2018-2021) -> `document`
       records (title, url, station, year). The PDFs are NOT downloaded or parsed (vendor-format reports).
     - "Real Time Results / Science Center": the numbers in the served HTML are placeholders ("0 ug/m3",
       "Last updated: -"); the page's own script fills them from (3). Nothing is read from the placeholders.

3. POST https://www.suratmunicipal.gov.in/Home/GetAirQualityInfoSci (form DeviceCode="") -> JSON, the request
   the results page itself makes for its "Science Center" panel. It returns ONE latest reading for station
   code "0034": dtl_date (/Date(ms)/ = midnight IST of the reading day) + testing_time (HH:MM:SS, IST).
   Emitted as instant observations at geo aq_station:smc-sensor-0034. Only the fields whose unit the page
   states are kept: SO2, NOx, PM2.5, PM10 (ug/m3), temperature (degC) and relative humidity (%).
   Not emitted:
     - CO: the page labels it ug/m3 but the values (about 1.45) are what CO looks like in mg/m3; unit unclear.
     - AQI: returned as 0.00 while PM2.5 is 50, i.e. not computed by the feed.
     - wind speed/direction, rainfall, solar radiation, pressure: no unit published on the page.
   Each refresh captures whatever the latest reading is; there is no history endpoint with data (the
   "...Last10" request the page also makes returned an empty list on 2026-10-05). On 2026-10-05 the latest
   reading was from 2026-09-29 20:24, so the feed may lag or stall; stale readings are stored as what they
   are (their own timestamp), never re-dated.

New geo level used: aq_station (already listed in the sources README).
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone

from ..model import Geo, Metric, Obs, Raw, Record, Result, Source, ValidationError
from ..parse import clean, html_tables, links, num
from ..surat import SMC

CAAQMS_URL = 'https://www.suratmunicipal.gov.in/Departments/CAAQMS'
RESULTS_URL = 'https://www.suratmunicipal.gov.in/Departments/AirQualityResults'
LIVE_URL = 'https://www.suratmunicipal.gov.in/Home/GetAirQualityInfoSci'
# yearly result PDF link, e.g. matches '.../AQMCell/Results/Varachha/2021.pdf' -> ('Varachha', '2021')
RESULT_PDF_RE = re.compile(r'/AQMCell/Results/([^/]+)/(\d{4})\.pdf$', re.I)
IST = timezone(timedelta(hours=5, minutes=30))

SOURCE = Source(
    id='smc_air_quality',
    name='SMC air-quality stations, past results and latest sensor reading',
    publisher='Surat Municipal Corporation, Air Quality Management Cell',
    url=RESULTS_URL,
    module='environment',
    cadence='daily',
    interval_hours=6,               # snapshot of the latest real-time reading 4 times a day
    geo_note='Readings: one SMC sensor station inside the SMC area (geo level aq_station). Station records also '
             'list GPCB manual stations in Surat district outside SMC (Chalthan and Baleshwar, Palsana taluka).',
    licence_note='Surat Municipal Corporation web pages and the JSON feed behind its results page; public information',
    notes='Readings come from the JSON the results page loads; CO, AQI and unit-less fields are not stored. '
          'Yearly result PDFs are listed as document records only.',
    metrics=(
        Metric('air.smc_sensor_pm25_ugm3', 'PM2.5 (SMC real-time sensor)', 'ug/m3',
               'Latest PM2.5 reading of the SMC sensor station, as shown on the Air Quality Results page.'),
        Metric('air.smc_sensor_pm10_ugm3', 'PM10 (SMC real-time sensor)', 'ug/m3', 'Latest PM10 reading.'),
        Metric('air.smc_sensor_so2_ugm3', 'SO2 (SMC real-time sensor)', 'ug/m3', 'Latest SO2 reading.'),
        Metric('air.smc_sensor_nox_ugm3', 'NOx (SMC real-time sensor)', 'ug/m3', 'Latest NOx reading.'),
        Metric('air.smc_sensor_temperature_c', 'Ambient temperature (SMC sensor station)', 'degC',
               'Ambient temperature at the sensor station at the time of the reading.'),
        Metric('air.smc_sensor_relative_humidity_pct', 'Relative humidity (SMC sensor station)', '%',
               'Relative humidity at the sensor station at the time of the reading.'),
    ),
    record_types=('aq_station', 'aq_station_proposed', 'document'),
)

# JSON field -> metric (only fields whose unit the page states)
LIVE_FIELDS = {
    'PM2_5': 'air.smc_sensor_pm25_ugm3',
    'PM10': 'air.smc_sensor_pm10_ugm3',
    'So2': 'air.smc_sensor_so2_ugm3',
    'NOx': 'air.smc_sensor_nox_ugm3',
    'Ambient_Temperature': 'air.smc_sensor_temperature_c',
    'Relative_Humidity': 'air.smc_sensor_relative_humidity_pct',
}
RANGES = {
    'air.smc_sensor_pm25_ugm3': (0, 1500), 'air.smc_sensor_pm10_ugm3': (0, 3000),
    'air.smc_sensor_so2_ugm3': (0, 2000), 'air.smc_sensor_nox_ugm3': (0, 2000),
    'air.smc_sensor_temperature_c': (-5, 55), 'air.smc_sensor_relative_humidity_pct': (0, 100),
}


def fetch(ctx):
    yield ctx.get(CAAQMS_URL, meta={'doc': 'stations'}, soft=True)
    yield ctx.get(RESULTS_URL, meta={'doc': 'results'}, soft=True)
    yield ctx.post(LIVE_URL, form={'DeviceCode': ''}, meta={'doc': 'live'}, soft=True)


# ---------- helpers ----------

def _slug(s: str) -> str:
    # runs of anything but a-z/0-9 become '-', e.g. 'Rang Upvan, Nanpura' -> 'rang-upvan-nanpura'
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


# degrees-minutes-seconds pair, e.g. matches '21°10\'00.7"N 72°46\'54.2"E'
_DMS = re.compile(r'(\d+)\s*°\s*(\d+)\s*[\'′]\s*([\d.]+)\s*["″]?\s*([NS])\s*,?\s*'
                  r'(\d+)\s*°\s*(\d+)\s*[\'′]\s*([\d.]+)\s*["″]?\s*([EW])')


def dms_to_decimal(text: str) -> tuple[float, float]:
    m = _DMS.search(text)
    if not m:
        raise ValueError(f'unparsed coordinates {text!r}')
    lat = int(m.group(1)) + int(m.group(2)) / 60 + float(m.group(3)) / 3600
    lon = int(m.group(5)) + int(m.group(6)) / 60 + float(m.group(7)) / 3600
    return (round(-lat if m.group(4) == 'S' else lat, 6), round(-lon if m.group(8) == 'W' else lon, 6))


def _latlon_plain(text: str) -> tuple[float, float]:
    # e.g. matches 'Latitude:21.20335 Longitude:72.846603'
    m = re.search(r'Latitude\s*:\s*([\d.]+)\s*Longitude\s*:\s*([\d.]+)', text, re.I)
    if not m:
        raise ValueError(f'unparsed coordinates {text!r}')
    return float(m.group(1)), float(m.group(2))


def _ms_date(s) -> datetime:
    # .NET JSON date, e.g. matches '/Date(1790620200000)/'
    m = re.search(r'/Date\((-?\d+)\)/', str(s))
    if not m:
        raise ValueError(f'unparsed .NET date {s!r}')
    return datetime.fromtimestamp(int(m.group(1)) / 1000, IST)


def live_station_geo(stncode: str) -> Geo:
    return Geo('aq_station', f'smc-sensor-{stncode}',
               f'SMC real-time air-quality sensor {stncode} (shown as "Science Center" on SMC\'s results page)',
               'smc_city', 'smc')


# ---------- parsers ----------

def parse_stations(raw: Raw) -> Result:
    res = Result(complete_record_types=('aq_station', 'aq_station_proposed'))
    for t in html_tables(raw.body):
        head = t.heading.lower()
        hdr = [c.lower() for c in t.rows[0]] if t.rows else []
        if 'manual air monitoring station' in head and 'gpcb' in head:
            for r in t.rows[1:]:
                lat, lon = dms_to_decimal(r[2])
                res.records.append(Record('aq_station', f'gpcb-manual/{lat:.4f},{lon:.4f}', {
                    'operator': 'GPCB', 'type': 'manual', 'location': clean(r[1]),
                    'coordinates_published': clean(r[2]), 'latitude': lat, 'longitude': lon}))
        elif 'sensor based caaqms installed by surat municipal corporation' in head:
            for r in t.rows[1:]:
                lat, lon = _latlon_plain(r[1])
                res.records.append(Record('aq_station', f'smc-sensor/{_slug(r[0])}', {
                    'operator': 'SMC', 'type': 'sensor-based CAAQMS', 'location': clean(r[0]),
                    'coordinates_published': clean(r[1]), 'latitude': lat, 'longitude': lon,
                    'data_frequency_published': clean(r[2])}))
        elif 'usepa approved caaqms' in head and hdr[:3] == ['sr. no', 'zone office', 'location']:
            by = 'GPCB' if 'proposed by gpcb' in head else 'SMC' if 'proposed by surat municipal' in head else None
            if by is None:
                raise ValueError(f'proposed-station table with unknown proposer: {t.heading[-80:]!r}')
            for r in t.rows[1:]:
                res.records.append(Record('aq_station_proposed', f'proposed-{by.lower()}/{_slug(r[2])}', {
                    'proposed_by': by, 'type': 'USEPA approved CAAQMS (proposed)',
                    'zone_as_published': clean(r[1]), 'location': clean(r[2])}))
    return res


def parse_results(raw: Raw) -> Result:
    res = Result(complete_record_types=('document',))
    seen = set()
    for url, _text in links(raw.body, RESULTS_URL):
        m = RESULT_PDF_RE.search(url)
        if not m or url in seen:
            continue
        seen.add(url)
        station, year = m.group(1), int(m.group(2))
        res.records.append(Record('document', f'smc-aq-results/{_slug(station)}/{year}', {
            'kind': 'air_quality_results_pdf', 'station': station, 'year': year, 'url': url,
            'title': f'Air quality results, {station}, {year}',
            'page_note': 'Results of Air quality in Surat city - Source Gujarat Pollution Control Board (GPCB)',
            'parsed': False}))
    return res


def parse_live(raw: Raw) -> Result:
    j = json.loads(raw.body.decode('utf-8-sig'))
    d = j.get('data') if isinstance(j, dict) else None
    if j.get('status') != 200 or not isinstance(d, dict) or not d:
        return Result()                     # no reading published right now
    stn = str(d.get('stncode') or '').strip()
    # a short station code, e.g. '0034'
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,20}', stn):
        raise ValueError(f'unexpected station code {stn!r}')
    day = _ms_date(d['dtl_date'])
    # HH:MM with optional seconds, e.g. matches '20:24:23' -> ('20', '24')
    hh, mm = re.fullmatch(r'\s*(\d{1,2}):(\d{2})(?::\d{2})?\s*', str(d['testing_time'])).groups()
    at = datetime(day.year, day.month, day.day, int(hh), int(mm)).isoformat(timespec='minutes')
    geo = live_station_geo(stn)
    res = Result(geos=[SMC, geo])
    for field, metric in LIVE_FIELDS.items():
        if field not in d:
            continue
        v = num(d[field])
        res.observations.append(Obs(metric, geo.geo_level, geo.geo_code, at, at, value=v,
                                    status='reported' if v is not None else 'not_reported'))
    return res


def parse(raw: Raw) -> Result:
    url = raw.url
    if url.startswith(LIVE_URL) or raw.body.lstrip()[:1] == b'{':
        return parse_live(raw)
    if 'CAAQMS' in url or b'Manual Air monitoring station' in raw.body:
        return parse_stations(raw)
    return parse_results(raw)


# ---------- validation ----------

def validate(result: Result, raw: Raw) -> None:
    kinds = {r.record_type for r in result.records}
    if 'aq_station' in kinds or 'aq_station_proposed' in kinds or 'aq_station' in result.complete_record_types:
        st = [r for r in result.records if r.record_type == 'aq_station']
        if sum(r.attrs['operator'] == 'GPCB' for r in st) < 3 or not any(r.attrs['operator'] == 'SMC' for r in st):
            raise ValidationError(f'only {len(st)} stations parsed from the CAAQMS page; layout may have changed')
        for r in st:      # roughly Surat district
            if not (20.6 <= r.attrs['latitude'] <= 21.7 and 72.4 <= r.attrs['longitude'] <= 73.8):
                raise ValidationError(f'station {r.record_key} outside Surat: {r.attrs["coordinates_published"]}')
        return
    if 'document' in result.complete_record_types:
        if not result.records:
            raise ValidationError('no past-result PDF links found on the results page')
        return
    for o in result.observations:
        lo, hi = RANGES[o.metric_id]
        if o.value is not None and not lo <= o.value <= hi:
            raise ValidationError(f'implausible {o.metric_id} = {o.value} at {o.period_start}')
    if result.observations and raw is not None:
        fetched = datetime.fromisoformat(raw.retrieved_at)
        fetched = fetched.astimezone(IST).replace(tzinfo=None) if fetched.tzinfo else fetched
        reading = datetime.fromisoformat(result.observations[0].period_start)
        if reading > fetched + timedelta(hours=1):
            raise ValidationError(f'reading time {reading} is after the fetch time {fetched}')
