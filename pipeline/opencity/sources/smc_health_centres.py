"""SMC urban health centres (UHC / UCHC): directory by zone, and the number of centres by type and zone.

Publisher: Surat Municipal Corporation, Health Department. The page sits in the SMC site menu under
Departments > Health > PM-JAY > "Enrollment Health Centers": the SMC health centres where residents can get a
PM-JAY / MA (Ayushman Bharat) card made. In practice it is SMC's list of its own urban health centres.

Endpoint: one plain GET, no parameters, no login or captcha (robots.txt on www.suratmunicipal.gov.in returns 404,
so nothing is disallowed):

    https://www.suratmunicipal.gov.in/Departments/PMJAYUHC

Response layout (server-rendered HTML, no <table>). Inside <div class="contentblock">, one block per zone:

    <h2 class="text-3x text-bold"> West Zone (Rander) </h2>
    <ul class="list-group">
      <li class="list-group-item hidden-xs hidden-sm"> Name | Address | Phone Numbers </li>    (column header)
      <li class="list-group-item">
        <div class="col-sm-12 col-md-3"><div class="visible-xs ...">Name</div> RANDER UHC </div>
        <div class="col-sm-12 col-md-6"><div class="visible-xs ...">Address</div> NR. RANDER BUS STAND, RANDER VILLAGE </div>
        <div class="col-sm-12 col-md-3"><div class="visible-xs ...">Phone Numbers</div> 2770925 </div>
      </li> ...

parse() reads each item through its own "Name" / "Address" / "Phone Numbers" labels, so it does not depend on
the CSS classes.

Records -> one 'smc_health_centre' per item, keyed by the name slug ('rander-uhc'). The page is the complete list,
so a centre that disappears from it gets closed. Attributes:
    name            as printed ('RANDER UHC', 'ASARAWALA UHC MH', 'NANDCHOWK URBAN HEALTH CENTER')
    facility_type   'uhc' (Urban Health Centre: names ending in UHC or URBAN HEALTH CENTER) or 'uchc' (Urban
                    Community Health Centre: names ending in UCHC). Read from the name; SMC prints no type column.
                    An unknown suffix raises an error rather than being guessed.
    maternity_home  True when the name ends in "MH" (maternity home attached; 2 centres in the snapshot). The page
                    does not list maternity homes separately, so there is no maternity-home count.
    zone            the zone heading as printed ('South Zone-A (Udhana)')
    zone_code       canonical code from surat.zone_code() (joins to geo level smc_zone)
    address         the centre's address as printed (a public building, not a person's address)
    phones          list of numbers as printed, split only at commas ('2423751-56, 381' -> ['2423751-56', '381']);
                    '-' means none and gives an empty list. Seven-digit numbers are Surat 0261 landlines.

Observations -> metric health.smc_centres (centres listed), by dims.type (uhc / uchc), for each smc_zone and for
smc_city (sum over the zones). Both types are emitted for every zone on the page, so a 0 means "none listed".
Counted from the items; the page prints no totals.

Snapshot 2026-10-24: 80 centres in 9 zones (71 UHC, 9 UCHC); footer "Last Updated: June 24, 2024 01:15 PM".

Dating: the page has no data date. Its footer "Last Updated" stayed at June 24, 2024 across fetches hours apart,
so it is the CMS edit date of this page (not the render time). The counts are filed as an instant reading on that
date, with publisher_as_of set to it; a later edit moves the date and starts a new point.

Quirks, kept as published: only 13 centres have a phone number; NAVANAGAR UHC lists a mobile-format number, kept
because it is printed as the centre's own number; spellings vary (GOURAVAPATH / GAURAVPATH, ICHHAPORE / ICHHAPOR,
"OPOSITE"); the West Zone list includes ADAJAN UHC and ADAJAN PATIYA UHC as separate centres.

Geography: SMC zones (smc_zone) and the SMC city area. Cadence: static, changes only when the page is edited;
checked weekly. Licence: Surat Municipal Corporation web page; public information; no explicit open-data licence.
"""
from __future__ import annotations

from datetime import datetime

from ..model import Metric, Obs, Raw, Record, Result, Source, ValidationError
from ..parse import clean, html_text
from ..surat import SMC, ZONES, zone_code, zone_geo
from .smc_officials import split_top

URL = 'https://www.suratmunicipal.gov.in/Departments/PMJAYUHC'

TYPES = ('uhc', 'uchc')

SOURCE = Source(
    id='smc_health_centres',
    name='SMC urban health centres (UHC / UCHC) by zone',
    publisher='Surat Municipal Corporation, Health Department',
    url=URL,
    module='health',
    cadence='static',
    interval_hours=24 * 7,          # the page was last edited in 2024; a weekly check is plenty
    record_types=('smc_health_centre',),
    geo_note='SMC zones (smc_zone, codes from surat.zone_code()) and the SMC city area (sum of the zones)',
    licence_note='Surat Municipal Corporation web page; public information (no explicit open-data licence)',
    notes=('The PM-JAY "Enrollment Health Centers" page, which lists SMC\'s urban health centres zone by zone. '
           'Type (UHC / UCHC) and the maternity-home flag are read from the centre name. Counts are dated to the '
           'page footer "Last Updated" date (a CMS edit date). Phone numbers are kept as printed.'),
    metrics=(
        Metric('health.smc_centres', 'SMC urban health centres', 'centres',
               'Number of SMC health centres listed on the PM-JAY "Enrollment Health Centers" page, by dims.type: '
               'uhc = Urban Health Centre (name ends in UHC or URBAN HEALTH CENTER), uchc = Urban Community Health '
               'Centre (name ends in UCHC). Per smc_zone as listed under the zone heading; smc_city is the sum over '
               'the zones. Counted from the listed items (the page prints no totals). Instant reading on the page\'s '
               '"Last Updated" date.'),
    ),
)


def fetch(ctx):
    yield ctx.get(URL)


def _slug(s: str) -> str:
    out = ''.join(ch if ch.isalnum() else ' ' for ch in s.lower())
    return '-'.join(out.split())


def _last_updated(text: str) -> str:
    """Footer '<span id="spnLastUpdated">June 24, 2024 01:15 PM</span>' -> '2024-06-24'."""
    i = text.find('id="spnLastUpdated"')
    if i < 0:
        raise ValueError('no "Last Updated" footer on the health centres page')
    start = text.find('>', i) + 1
    stamp = clean(text[start:text.find('<', start)])
    return datetime.strptime(stamp, '%B %d, %Y %I:%M %p').date().isoformat()


def _kind(name: str) -> tuple[str, bool]:
    """'ASARAWALA UHC MH' -> ('uhc', True); 'PAL UCHC' -> ('uchc', False)."""
    words = name.upper().split()
    maternity = words[-1] == 'MH'
    if maternity:
        words = words[:-1]
    if words[-1] == 'UCHC':
        return 'uchc', maternity
    if words[-1] == 'UHC' or ' '.join(words[-3:]) in ('URBAN HEALTH CENTER', 'URBAN HEALTH CENTRE'):
        return 'uhc', maternity
    raise ValueError(f'cannot tell the facility type of {name!r}')


def _fields(item: str) -> tuple[str, str, str]:
    """One <li> item -> (name, address, phone text), read between the item's own labels."""
    lines = html_text(item).split('\n')
    try:
        i, j, k = lines.index('Name'), lines.index('Address'), lines.index('Phone Numbers')
    except ValueError:
        raise ValueError(f'health centre item without Name/Address/Phone labels: {lines!r}') from None
    return ' '.join(lines[i + 1:j]), ' '.join(lines[j + 1:k]), ' '.join(lines[k + 1:])


def parse(raw: Raw) -> Result:
    text = raw.text
    day = _last_updated(text)
    start = text.find('<div class="contentblock">')
    if start < 0:
        raise ValueError('content block not found; page layout may have changed')
    end = text.find('<footer', start)
    region = text[start:end if end > 0 else len(text)]

    res = Result(geos=[SMC], complete_record_types=('smc_health_centre',))
    counts: dict[str, dict[str, int]] = {}
    for chunk in region.split('<h2')[1:]:
        heading = clean(html_text(chunk[chunk.find('>') + 1:chunk.find('</h2>')]))
        code = zone_code(heading)
        if code in counts:
            raise ValueError(f'zone {heading!r} appears twice on the page')
        counts[code] = {t: 0 for t in TYPES}
        res.geos.append(zone_geo(code))
        for item in chunk.split('<li class="list-group-item">')[1:]:
            name, address, phone = _fields(item[:item.find('</li>')])
            kind, maternity = _kind(name)
            counts[code][kind] += 1
            res.records.append(Record('smc_health_centre', _slug(name), {
                'name': name,
                'facility_type': kind,
                'maternity_home': maternity,
                'zone': heading,
                'zone_code': code,
                'address': address,
                'phones': [p for p in split_top(phone) if p != '-'],
            }))

    for code, by_type in counts.items():
        for kind, n in by_type.items():
            res.observations.append(Obs('health.smc_centres', 'smc_zone', code, day, day, value=float(n),
                                        dims={'type': kind}, publisher_as_of=day))
    for kind in TYPES:
        n = sum(by_type[kind] for by_type in counts.values())
        res.observations.append(Obs('health.smc_centres', 'smc_city', 'smc', day, day, value=float(n),
                                    dims={'type': kind}, publisher_as_of=day))
    return res


def validate(result: Result, raw: Raw) -> None:
    recs = result.records
    if not 50 <= len(recs) <= 200:
        raise ValidationError(f'{len(recs)} health centres parsed; expected about 80 (page layout may have changed)')
    zones = {r.attrs['zone_code'] for r in recs}
    if not 8 <= len(zones) <= len(ZONES) or zones & {'hq', 'south'}:
        raise ValidationError(f'unexpected zones {sorted(zones)}')
    for r in recs:
        a = r.attrs
        if len(a['name']) < 5 or len(a['address']) < 5:
            raise ValidationError(f'{r.record_key}: implausible name or address {a["name"]!r} / {a["address"]!r}')
        for p in a['phones']:
            if sum(ch.isdigit() for ch in p) < 3 or any(ch.isalpha() for ch in p):
                raise ValidationError(f'{r.record_key}: implausible phone number {p!r}')
    city = sum(o.value for o in result.observations if o.geo_level == 'smc_city')
    if city != len(recs):
        raise ValidationError(f'city total {city} does not match the {len(recs)} listed centres')
    day = result.observations[0].period_start
    if day < '2018-09-23' or (raw is not None and raw.retrieved_at and day > raw.retrieved_at[:10]):
        raise ValidationError(f'page date {day} is before PM-JAY began or after the fetch')
