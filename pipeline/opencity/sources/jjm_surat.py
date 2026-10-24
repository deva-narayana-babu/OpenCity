"""Jal Jeevan Mission (Har Ghar Jal): rural households with a tap water connection in Surat and Tapi districts.

Publisher: Jal Jeevan Mission (JJM), Department of Drinking Water and Sanitation, Ministry of Jal Shakti,
Government of India. The figures are the JJM IMIS numbers behind the public dashboard
https://ejalshakti.gov.in/jjmreport/JJMIndia.aspx ("Tap water supply in households (HHs)").

Endpoint: the dashboard's own ASP.NET page method, called with a JSON POST, no login or captcha (robots.txt on
ejalshakti.gov.in returns 404, so nothing is disallowed):

    POST https://ejalshakti.gov.in/jjmreport/JJMIndia.aspx/BindDistrictMap
    body {"StCode11": "351", "Cat": "11", "SubCat": "11", "Param": "21"}      (Content-Type: application/json)

Each value is passed through the page's JavaScript encodeTxt() (JJM_Dashboard.js, encN = 1): escape(), shift
every character code up by one, escape() again, append "1". So "351" is state code 24 (Gujarat), "11" is 0 and
"21" is 1. Cat 0 = household tap connections; SubCat 0 = "As on <today>", SubCat 1 = "As on 15 Aug 2019" (the
day JJM began); Param 1 = district level. fetch() makes two POSTs, the 15 Aug 2019 view first, then today's.

Response: {"d": [ {"__type": "JJMIndia+map_data", "KeyValue": "492", "KeyId": "0132", "Name": "Surat",
    "Name_hi": ..., "Per": "100.00", "ColorId": "5", "Value": "383576", "Total": "383576", "Lat": ..., "Long": ...,
    "ISHGJReported": "1", "IsHGJCertified": "0"}, ... ]}   one row per Gujarat district (33 in the snapshot).
    KeyValue is JJM's district code: 492 = Surat, 493 = Tapi (both are read; the other districts are ignored).
    KeyId, Name_hi, Lat, Long and ColorId (the map's legend class) are not used.
    Value = rural households with a tap connection on the view's date, Total = rural households now,
    Per = 100 * Value / Total (two decimals).
The response carries no date: the dashboard labels the today view with the browser's date. fetch() therefore puts
the fetch date (Asia/Kolkata) in meta.as_of, and parse() files the today view on that date (publisher_as_of too).

Metrics (geography surat_district / tapi_district; JJM counts RURAL households only, so homes inside the SMC area
and other urban local bodies are not included):
    jjm.rural_households          Total, today view: rural households in the district per JJM IMIS.
    jjm.households_with_tap       Value: rural households with a functional household tap connection; today view
                                  on the fetch date, and the 15 Aug 2019 view on 2019-08-15 (the JJM baseline).
    jjm.tap_coverage_pct          Per, today view only. The 15 Aug 2019 view's Per divides the 2019 connections by
                                  today's household total, so it is not stored (the 2019 Total is today's total too).
    jjm.har_ghar_jal_reported     ISHGJReported, today view: 1 if the district is reported "Har Ghar Jal" (every
                                  rural household reported as having a tap connection), else 0.
    jjm.har_ghar_jal_certified    IsHGJCertified, today view: 1 if the district is certified "Har Ghar Jal" (the
                                  gram sabhas of its villages have certified it by resolution), else 0.
A blank or "-" value becomes not_reported. Units: households, percent, 0/1 flags.

Snapshot 2026-10-24: Surat 383,576 of 383,576 rural households with a tap (100.00%), reported but not certified;
Tapi 239,248 of 239,248 (100.00%). On 15 Aug 2019: Surat 291,815, Tapi 100,229.

Caveats: the figures are self-reported by the state into JJM IMIS and change daily (the dashboard is live);
coverage is saturated at 100%, so mostly the household total moves. Gujarat's state total is not fetched.
Cadence: daily at the publisher; checked weekly. Licence: none stated; Government of India public dashboard
(cite Jal Jeevan Mission, Ministry of Jal Shakti).
"""
from __future__ import annotations

import json
import urllib.parse

from ..model import Metric, Obs, Raw, Result, Source, ValidationError
from ..parse import num
from ..surat import SURAT_DISTRICT, TAPI_DISTRICT

PAGE = 'https://ejalshakti.gov.in/jjmreport/JJMIndia.aspx'
URL = PAGE + '/BindDistrictMap'
GUJARAT = '24'
BASELINE = '2019-08-15'
VIEWS = ((BASELINE, '1'), ('today', '0'))       # (meta.view, SubCat)

# JJM district code (KeyValue) -> (geo level, geo code, name in the response)
DISTRICTS = {'492': ('surat_district', 'surat', 'Surat'), '493': ('tapi_district', 'tapi', 'Tapi')}

SOURCE = Source(
    id='jjm_surat',
    name='Jal Jeevan Mission: rural tap water connections (Surat, Tapi)',
    publisher='Jal Jeevan Mission, Department of Drinking Water and Sanitation, Ministry of Jal Shakti, GoI',
    url=PAGE,
    module='water',
    cadence='daily',
    interval_hours=24 * 7,          # coverage is saturated at 100%; a weekly snapshot is enough
    geo_note='Surat and Tapi districts, rural households only (JJM does not cover the SMC or other urban areas)',
    licence_note='No licence stated; Government of India public dashboard (Jal Jeevan Mission IMIS)',
    notes=('Two POSTs to the dashboard\'s BindDistrictMap page method (Gujarat districts, as on today and as on '
           '15 Aug 2019). The response has no date; the today view is filed on the fetch date. The 2019 '
           'coverage percent is not stored because JJM divides by today\'s household total.'),
    metrics=(
        Metric('jjm.rural_households', 'Rural households (JJM)', 'households',
               'Rural households in the district per Jal Jeevan Mission IMIS ("Total"), as on the fetch date.'),
        Metric('jjm.households_with_tap', 'Rural households with a tap connection (JJM)', 'households',
               'Rural households with a functional household tap connection per JJM IMIS ("Value"): as on the '
               'fetch date, and as on 15 Aug 2019 (JJM baseline) for the period 2019-08-15.'),
        Metric('jjm.tap_coverage_pct', 'Rural tap water coverage (JJM)', 'percent',
               'Rural households with a tap connection as a percent of all rural households, as published by '
               'JJM ("Per"), as on the fetch date.'),
        Metric('jjm.har_ghar_jal_reported', 'Har Ghar Jal reported district', 'flag',
               '1 if JJM shows the district as Har Ghar Jal "reported" (all rural households reported as having '
               'a tap connection), 0 if not. As on the fetch date.'),
        Metric('jjm.har_ghar_jal_certified', 'Har Ghar Jal certified district', 'flag',
               '1 if JJM shows the district as Har Ghar Jal "certified" (certified by gram sabha resolutions), '
               '0 if not. As on the fetch date.'),
    ),
)


def encode_txt(s: str) -> str:
    """The dashboard's encodeTxt() with encN = 1: '24' -> '351', '0' -> '11', '1' -> '21'."""
    safe = '@*_+-./'        # what JavaScript's escape() leaves alone (besides letters and digits)
    shifted = ''.join(chr(ord(ch) + 1) for ch in urllib.parse.quote(s, safe=safe))
    return urllib.parse.quote(shifted, safe=safe) + '1'


def fetch(ctx):
    as_of = ctx.now.date().isoformat()
    for view, subcat in VIEWS:
        body = {'StCode11': encode_txt(GUJARAT), 'Cat': encode_txt('0'), 'SubCat': encode_txt(subcat),
                'Param': encode_txt('1')}
        yield ctx.post(URL, json=body, meta={'view': view, 'as_of': as_of})


def _obs(metric: str, level: str, code: str, day: str, cell) -> Obs:
    v = num(cell)
    return Obs(metric, level, code, day, day, value=v, status='reported' if v is not None else 'not_reported',
               publisher_as_of=day)


def parse(raw: Raw) -> Result:
    view = raw.meta.get('view')
    if view not in (BASELINE, 'today'):
        raise ValueError(f'meta.view must be {BASELINE!r} or "today", got {view!r}')
    day = BASELINE if view == BASELINE else raw.meta['as_of']
    res = Result(geos=[SURAT_DISTRICT, TAPI_DISTRICT])
    found = set()
    for row in json.loads(raw.text)['d']:
        if row.get('KeyValue') not in DISTRICTS:
            continue
        level, code, name = DISTRICTS[row['KeyValue']]
        if row.get('Name') != name:
            raise ValueError(f'JJM district {row["KeyValue"]} is {row.get("Name")!r}, expected {name!r}')
        found.add(code)
        res.observations.append(_obs('jjm.households_with_tap', level, code, day, row['Value']))
        if view == 'today':
            res.observations += [
                _obs('jjm.rural_households', level, code, day, row['Total']),
                _obs('jjm.tap_coverage_pct', level, code, day, row['Per']),
                _obs('jjm.har_ghar_jal_reported', level, code, day, row['ISHGJReported']),
                _obs('jjm.har_ghar_jal_certified', level, code, day, row['IsHGJCertified']),
            ]
    if len(found) != len(DISTRICTS):
        raise ValueError(f'Surat/Tapi rows missing from the JJM response (found {sorted(found)})')
    return res


def validate(result: Result, raw: Raw) -> None:
    by = {(o.metric_id, o.geo_code): o.value for o in result.observations}
    for code in ('surat', 'tapi'):
        tap = by.get(('jjm.households_with_tap', code))
        total = by.get(('jjm.rural_households', code))
        pct = by.get(('jjm.tap_coverage_pct', code))
        if tap is not None and not 10_000 <= tap <= 1_500_000:
            raise ValidationError(f'{code}: implausible {tap} households with a tap')
        if total is not None and not 50_000 <= total <= 1_500_000:
            raise ValidationError(f'{code}: implausible {total} rural households')
        if None not in (tap, total) and tap > total:
            raise ValidationError(f'{code}: {tap} households with a tap but only {total} households')
        if None not in (tap, total, pct) and abs(100 * tap / total - pct) > 0.01:
            raise ValidationError(f'{code}: published {pct}% does not match {tap}/{total}')
        flags = [by.get((f'jjm.har_ghar_jal_{f}', code)) for f in ('reported', 'certified')]
        if any(f not in (None, 0, 1) for f in flags) or flags == [0, 1]:
            raise ValidationError(f'{code}: implausible Har Ghar Jal flags {flags} (certified but not reported?)')
    day = result.observations[0].period_start
    if day < BASELINE or (raw is not None and raw.retrieved_at and day > raw.retrieved_at[:10]):
        raise ValidationError(f'date {day} is before JJM began or after the fetch')
