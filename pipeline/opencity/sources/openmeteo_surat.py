"""Open-Meteo weather model data for Surat city: current conditions and a 10-day daily forecast.

Publisher: Open-Meteo.com, an open-source weather API that serves numerical weather model output from
national weather services (ECMWF, NOAA GFS, DWD ICON and others; its "best match" blend picks the models
for the location). These are MODEL values, not readings from a weather station: label them as such.

DISABLED BY DEFAULT (SOURCE.enabled=False). https://api.open-meteo.com/robots.txt reads
    User-agent: *
    Disallow: /
(checked 2026-10-24; the website https://open-meteo.com/robots.txt allows everything). Open-Meteo's terms
offer the API free and without a key for non-commercial use, so the Disallow is probably aimed at search
crawlers, but this project's rule is to respect robots.txt, so the adapter does not fetch unless the
maintainers decide otherwise and set enabled=True. parse() works on a saved response (the test fixture is one
real response fetched once while checking the source).

Request (one GET, no key, no cookies):
    https://api.open-meteo.com/v1/forecast
      ?latitude=21.170&longitude=72.831                     a point in central Surat (LAT/LON below)
      &current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,
               wind_direction_10m,surface_pressure,precipitation
      &daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,
             precipitation_sum,wind_speed_10m_max,sunrise,sunset,uv_index_max
      &timezone=Asia/Kolkata&forecast_days=8&past_days=2
Default units are requested (degC, km/h, mm, hPa).

Response (JSON):
    latitude, longitude, elevation     the model grid cell actually used (21.195 N, 72.787 E, 17 m on
                                       2026-10-24, about 5 km from the requested point, still inside SMC)
    utc_offset_seconds (19800), timezone ("Asia/Kolkata")
    current_units {...}, current {time: "2026-10-24T02:00", interval: 900, temperature_2m: 25.9, ...}
    daily_units {...},   daily {time: [10 dates], weather_code: [...], temperature_2m_max: [...], ...}
All times are local (IST) because timezone=Asia/Kolkata is requested. validate() checks the units, so a change
of default units fails loudly instead of being stored under the wrong unit.

What is stored (geography smc_city: one model grid cell in Surat city; see geo_note):
- Current conditions, as an instant reading at current.time (Open-Meteo rounds it to 15 minutes; the
  values come from its 15-minutely model data). Precipitation is the amount over the preceding
  current.interval seconds (900 s), so its period is [time - interval, time].
- Daily values for 10 days: the 2 past days (past_days=2: model values, not observed weather), today, and
  7 days ahead. Each day covers 00:00-24:00 IST. Every refresh replaces the forecast for a day; earlier
  forecasts survive in observation_revision, so the forecast history is kept.
- weather_code is the WMO weather interpretation code (WMO 4677 subset used by Open-Meteo); value_text holds
  Open-Meteo's description (e.g. 0 "Clear sky", 3 "Overcast", 95 "Thunderstorm").
- sunrise/sunset are stored as value_text "HH:MM" (IST) with no numeric value.

Cadence: Open-Meteo refreshes its models about hourly; every 3 hours is enough for a dashboard tile.
Quirks: a missing value comes back as null and is stored as not_reported. precipitation_probability_max is
only available for the forecast models that provide it; Open-Meteo returns null where it does not.

Licence: https://open-meteo.com/en/terms (checked 2026-10-24): users of the free API accept the CC-BY 4.0
licence (credit Open-Meteo.com), use it for non-commercial purposes only, and stay under 10,000 calls a day,
5,000 an hour and 600 a minute. This adapter would make about 8 calls a day.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta

from ..model import Metric, Obs, Raw, Result, Source, ValidationError
from ..surat import SMC

LAT, LON = 21.170, 72.831          # central Surat (near Chowk Bazaar); Open-Meteo snaps it to a model grid cell
CURRENT = ('temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,'
           'wind_direction_10m,surface_pressure,precipitation')
DAILY = ('weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum,'
         'wind_speed_10m_max,sunrise,sunset,uv_index_max')
URL = (f'https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current={CURRENT}'
       f'&daily={DAILY}&timezone=Asia%2FKolkata&forecast_days=8&past_days=2')

SOURCE = Source(
    id='openmeteo_surat',
    name='Open-Meteo weather model: Surat current conditions and daily forecast',
    publisher='Open-Meteo.com (weather model data from national weather services)',
    url='https://open-meteo.com/en/docs',
    module='weather',
    cadence='3-hourly',
    interval_hours=3,
    enabled=False,
    geo_note='SMC city, represented by the single model grid cell Open-Meteo picks for 21.170 N, 72.831 E '
             '(central Surat); the response gives the cell used (21.195 N, 72.787 E, elevation 17 m in Oct 2026).',
    licence_note='CC-BY 4.0 (credit Open-Meteo.com); free API for non-commercial use, under 10,000 calls a day',
    notes='Disabled: api.open-meteo.com/robots.txt disallows all paths for all user agents (checked 2026-10-24), '
          'although Open-Meteo\'s terms invite free non-commercial API use. Enable only after the maintainers '
          'decide that the API host\'s robots.txt does not apply to this client. Values are weather-model output, '
          'not station observations; the 2 past days are model values too.',
    metrics=(
        Metric('openmeteo.temperature_c', 'Air temperature at 2 m (model)', 'degC',
               'Current air temperature 2 m above ground from Open-Meteo\'s weather models (current.temperature_2m), '
               'instant at current.time.'),
        Metric('openmeteo.apparent_temperature_c', 'Feels-like temperature (model)', 'degC',
               'Current apparent ("feels like") temperature from temperature, humidity and wind '
               '(current.apparent_temperature).'),
        Metric('openmeteo.relative_humidity_pct', 'Relative humidity at 2 m (model)', '%',
               'Current relative humidity 2 m above ground (current.relative_humidity_2m).'),
        Metric('openmeteo.weather_code', 'Current weather (WMO code, model)', 'WMO code',
               'Current WMO weather interpretation code (current.weather_code); value_text = Open-Meteo\'s '
               'description of the code.'),
        Metric('openmeteo.wind_speed_kmh', 'Wind speed at 10 m (model)', 'km/h',
               'Current wind speed 10 m above ground (current.wind_speed_10m).'),
        Metric('openmeteo.wind_direction_deg', 'Wind direction at 10 m (model)', 'degrees',
               'Current direction the wind blows FROM, degrees clockwise from north (current.wind_direction_10m).'),
        Metric('openmeteo.surface_pressure_hpa', 'Surface air pressure (model)', 'hPa',
               'Current air pressure at the surface of the grid cell, not reduced to sea level '
               '(current.surface_pressure).'),
        Metric('openmeteo.precipitation_mm', 'Precipitation in the last 15 minutes (model)', 'mm',
               'Rain + showers + snow over the preceding current.interval seconds (900 s); the period is that '
               'interval (current.precipitation).'),
        Metric('openmeteo.daily_weather_code', 'Weather of the day (WMO code, model)', 'WMO code',
               'Most severe WMO weather code of the day (daily.weather_code); value_text = description. '
               'Past days are model values, later days a forecast.'),
        Metric('openmeteo.daily_temperature_max_c', 'Maximum temperature of the day (model)', 'degC',
               'Highest 2 m air temperature of the day, 00:00-24:00 IST (daily.temperature_2m_max).'),
        Metric('openmeteo.daily_temperature_min_c', 'Minimum temperature of the day (model)', 'degC',
               'Lowest 2 m air temperature of the day, 00:00-24:00 IST (daily.temperature_2m_min).'),
        Metric('openmeteo.daily_precip_probability_max_pct', 'Chance of rain (model)', '%',
               'Highest hourly probability of precipitation during the day from the forecast ensembles '
               '(daily.precipitation_probability_max).'),
        Metric('openmeteo.daily_precip_sum_mm', 'Precipitation of the day (model)', 'mm',
               'Total rain + showers + snow of the day (daily.precipitation_sum).'),
        Metric('openmeteo.daily_wind_speed_max_kmh', 'Maximum wind speed of the day (model)', 'km/h',
               'Highest hourly wind speed 10 m above ground during the day (daily.wind_speed_10m_max).'),
        Metric('openmeteo.daily_uv_index_max', 'Maximum UV index of the day (model)', 'UV index',
               'Highest UV index of the day under the forecast cloud cover (daily.uv_index_max).'),
        Metric('openmeteo.sunrise', 'Sunrise', '',
               'value_text = local sunrise time "HH:MM" (IST) at the grid cell (daily.sunrise).'),
        Metric('openmeteo.sunset', 'Sunset', '',
               'value_text = local sunset time "HH:MM" (IST) at the grid cell (daily.sunset).'),
    ),
)

# Open-Meteo's descriptions of the WMO weather codes it uses (from its API documentation)
WMO = {
    0: 'Clear sky', 1: 'Mainly clear', 2: 'Partly cloudy', 3: 'Overcast', 45: 'Fog', 48: 'Depositing rime fog',
    51: 'Light drizzle', 53: 'Moderate drizzle', 55: 'Dense drizzle', 56: 'Light freezing drizzle',
    57: 'Dense freezing drizzle', 61: 'Slight rain', 63: 'Moderate rain', 65: 'Heavy rain',
    66: 'Light freezing rain', 67: 'Heavy freezing rain', 71: 'Slight snow fall', 73: 'Moderate snow fall',
    75: 'Heavy snow fall', 77: 'Snow grains', 80: 'Slight rain showers', 81: 'Moderate rain showers',
    82: 'Violent rain showers', 85: 'Slight snow showers', 86: 'Heavy snow showers', 95: 'Thunderstorm',
    96: 'Thunderstorm with slight hail', 99: 'Thunderstorm with heavy hail',
}

# response field -> (metric id, unit Open-Meteo must report for it)
CURRENT_FIELDS = {
    'temperature_2m': ('openmeteo.temperature_c', '°C'),
    'apparent_temperature': ('openmeteo.apparent_temperature_c', '°C'),
    'relative_humidity_2m': ('openmeteo.relative_humidity_pct', '%'),
    'weather_code': ('openmeteo.weather_code', 'wmo code'),
    'wind_speed_10m': ('openmeteo.wind_speed_kmh', 'km/h'),
    'wind_direction_10m': ('openmeteo.wind_direction_deg', '°'),
    'surface_pressure': ('openmeteo.surface_pressure_hpa', 'hPa'),
    'precipitation': ('openmeteo.precipitation_mm', 'mm'),
}
DAILY_FIELDS = {
    'weather_code': ('openmeteo.daily_weather_code', 'wmo code'),
    'temperature_2m_max': ('openmeteo.daily_temperature_max_c', '°C'),
    'temperature_2m_min': ('openmeteo.daily_temperature_min_c', '°C'),
    'precipitation_probability_max': ('openmeteo.daily_precip_probability_max_pct', '%'),
    'precipitation_sum': ('openmeteo.daily_precip_sum_mm', 'mm'),
    'wind_speed_10m_max': ('openmeteo.daily_wind_speed_max_kmh', 'km/h'),
    'uv_index_max': ('openmeteo.daily_uv_index_max', ''),
    'sunrise': ('openmeteo.sunrise', 'iso8601'),
    'sunset': ('openmeteo.sunset', 'iso8601'),
}
# plausible ranges for Surat (validate)
RANGES = {
    'openmeteo.temperature_c': (5, 50), 'openmeteo.apparent_temperature_c': (0, 60),
    'openmeteo.relative_humidity_pct': (0, 100), 'openmeteo.wind_speed_kmh': (0, 250),
    'openmeteo.wind_direction_deg': (0, 360), 'openmeteo.surface_pressure_hpa': (900, 1050),
    'openmeteo.precipitation_mm': (0, 200), 'openmeteo.daily_temperature_max_c': (10, 50),
    'openmeteo.daily_temperature_min_c': (5, 40), 'openmeteo.daily_precip_probability_max_pct': (0, 100),
    'openmeteo.daily_precip_sum_mm': (0, 1000), 'openmeteo.daily_wind_speed_max_kmh': (0, 250),
    'openmeteo.daily_uv_index_max': (0, 20),
}


def fetch(ctx):
    yield ctx.get(URL)


def _obs(metric: str, start: str, end: str, v) -> Obs:
    """One observation; a null in the response is not_reported. Weather codes get their description."""
    if v is None:
        return Obs(metric, 'smc_city', 'smc', start, end, status='not_reported')
    text = None
    if metric.endswith('weather_code'):
        text = WMO.get(int(v), f'WMO code {int(v)}')
    if metric in ('openmeteo.sunrise', 'openmeteo.sunset'):
        return Obs(metric, 'smc_city', 'smc', start, end, value_text=v[11:16])    # '2026-10-24T06:37' -> '06:37'
    return Obs(metric, 'smc_city', 'smc', start, end, value=float(v), value_text=text)


def parse(raw: Raw) -> Result:
    d = json.loads(raw.body)
    if d.get('error'):
        raise ValidationError(f'Open-Meteo error: {d.get("reason")}')
    res = Result(geos=[SMC])

    cur, units = d['current'], d['current_units']
    t = cur['time']                                     # '2026-10-24T02:00', local time
    for field, (metric, unit) in CURRENT_FIELDS.items():
        if units.get(field) != unit:
            raise ValidationError(f'current.{field} is in {units.get(field)!r}, expected {unit!r}')
        start = t
        if field == 'precipitation':                    # a sum over the preceding interval
            start = (datetime.fromisoformat(t) - timedelta(seconds=cur['interval'])).isoformat(timespec='minutes')
        res.observations.append(_obs(metric, start, t, cur.get(field)))

    daily, units = d['daily'], d['daily_units']
    for field, (metric, unit) in DAILY_FIELDS.items():
        if units.get(field) != unit:
            raise ValidationError(f'daily.{field} is in {units.get(field)!r}, expected {unit!r}')
        values = daily[field]
        if len(values) != len(daily['time']):
            raise ValidationError(f'daily.{field} has {len(values)} values for {len(daily["time"])} days')
        for day, v in zip(daily['time'], values):
            res.observations.append(_obs(metric, day, day, v))
    return res


def validate(result: Result, raw: Raw) -> None:
    d = json.loads(raw.body)
    if abs(d['latitude'] - LAT) > 0.2 or abs(d['longitude'] - LON) > 0.2:
        raise ValidationError(f'grid cell {d["latitude"]}, {d["longitude"]} is not near Surat')
    if d.get('utc_offset_seconds') != 19800:
        raise ValidationError(f'times are not in IST (utc_offset_seconds={d.get("utc_offset_seconds")})')
    days = sorted({o.period_start for o in result.observations if o.metric_id == 'openmeteo.daily_temperature_max_c'})
    if len(days) != 10:
        raise ValidationError(f'expected 10 daily values (2 past + 8 forecast days), got {len(days)}')
    current = d['current']['time']
    if not days[0] < current[:10] <= days[-1]:
        raise ValidationError(f'current time {current} is outside the daily range {days[0]}..{days[-1]}')
    if raw.retrieved_at and abs(datetime.fromisoformat(current) - datetime.fromisoformat(raw.retrieved_at[:16])) > timedelta(hours=3):
        raise ValidationError(f'current time {current} is far from the fetch time {raw.retrieved_at}')
    by_day = {}
    for o in result.observations:
        lo_hi = RANGES.get(o.metric_id)
        if lo_hi and o.value is not None and not lo_hi[0] <= o.value <= lo_hi[1]:
            raise ValidationError(f'implausible {o.metric_id} = {o.value} on {o.period_start}')
        by_day.setdefault(o.period_start, {})[o.metric_id] = o.value
    for day, v in by_day.items():
        hi, lo = v.get('openmeteo.daily_temperature_max_c'), v.get('openmeteo.daily_temperature_min_c')
        if hi is not None and lo is not None and lo > hi:
            raise ValidationError(f'{day}: minimum temperature {lo} above maximum {hi}')
