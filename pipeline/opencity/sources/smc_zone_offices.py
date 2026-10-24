"""SMC zone offices: address, telephone, office/control-room mobile and fax numbers of the nine zone offices.

Publisher: Surat Municipal Corporation (the "Zone Officials" page under "Contact Us" on the SMC site).

Endpoint: one plain GET, no parameters, no login or captcha (robots.txt on www.suratmunicipal.gov.in returns 404,
so nothing is disallowed):

    https://www.suratmunicipal.gov.in/Home/ZoneOfficials

Response layout (server-rendered HTML, no tables), one box per zone inside <div class="zones-contact">:

    <div class="contact-heading">Central Zone</div>
    <div class="contact-block">
      <div class="mar-b10">Central Zone Vahivati Bhavan, Gordhandas Chokhawala Marg, Shri Tapipura, Surat-395003</div>
      <div><span class="text-bold">Contact No. </span> 2427726</div>
      <div><span class="text-bold">Mobile No. </span>9727740932</div>
      <div><span class="text-bold">Fax No. </span>2420548 | <span class="text-bold">Control Room No. </span>2420547</div>
      <div class="zone-contact-details"><a href="/Zones/Central/CentralZone">Contact Details</a></div>

-> one 'smc_zone_office' record per box, keyed by the canonical zone code from surat.zone_code() ('west', 'central',
   'north', 'east_a', 'east_b', 'south_a', 'south_b', 'south_west', 'south_east'), plus the smc_zone geographies.
   The page is the complete list, so a zone box that disappears gets closed. Attributes:
     zone          the box heading as printed ('East Zone A')
     zone_code     canonical code (joins to geo level smc_zone)
     address       office address as printed (the zone office building, not a person's address)
     phones        "Contact No." entries, list
     mobiles       "Mobile No." entries: mobile numbers SMC prints as the zone office's own contact, list
     fax           "Fax No." entries, list
     control_room  "Control Room No." entries, list
     control_room_mobiles  "Control Room Mob. No." / "Control RoomMobile No." entries, list
     detail_url    the zone's "Contact Details" page (not fetched)
   Every number list keeps the entries exactly as printed, split only at commas: ranges such as "2786181 to 83",
   "9724346011-13" or "2331903-04-05" are NOT expanded. Seven-digit numbers are Surat landlines (STD code 0261).
   An unknown label raises an error so that a new kind of number is noticed rather than lost.

Snapshot 2026-10-24 (page footer "Last Updated: September 08, 2026"): nine zones. The same boxes are repeated on
/Home/SMCOfficials; this source reads them from the dedicated page only. The footer date is the CMS edit time of
the page, not a data date; it is not used.

Quirks, kept as published: East Zone B lists only control-room mobiles, the first of which (6559909506) looks like a
typo of 6359909506; South Zone B lists two mobile-format numbers under "Contact No."; some numbers are shared with
SMC's emergency page (smc_helplines), where the zones appear under their older names. The per-zone
"Contact Details" pages (zonal chief and zone officers with their personal mobiles) are not fetched.

No observations are emitted: the number of zone offices is a fixed fact of SMC's organisation, not a statistic.
Geography: SMC zones (smc_zone). Cadence: static reference data, edited without schedule; checked weekly.
Licence: Surat Municipal Corporation web page; public information. No explicit licence.
"""
from __future__ import annotations

from ..model import Raw, Record, Result, Source, ValidationError
from ..parse import clean, html_text, links
from ..surat import ZONES, zone_code, zone_geo
from .smc_officials import split_top

URL = 'https://www.suratmunicipal.gov.in/Home/ZoneOfficials'

SOURCE = Source(
    id='smc_zone_offices',
    name='SMC zone offices: addresses and official phone numbers',
    publisher='Surat Municipal Corporation',
    url=URL,
    module='offices',
    cadence='static',
    interval_hours=24 * 7,          # static directory; a weekly check is plenty
    record_types=('smc_zone_office',),
    geo_note='SMC zones (smc_zone, codes from surat.zone_code()): one office per zone',
    licence_note='Surat Municipal Corporation web page; public information',
    notes=('Numbers are kept as printed (ranges not expanded; 7-digit numbers are Surat 0261 landlines). Mobile '
           'numbers are stored only because SMC prints them as the zone office or control-room contact. Zone '
           'detail pages are not fetched.'),
)

# label (lower case, spaces removed) -> attribute
LABELS = {
    'contactno.': 'phones',
    'mobileno.': 'mobiles',
    'faxno.': 'fax',
    'controlroomno.': 'control_room',
    'controlroommob.no.': 'control_room_mobiles',
    'controlroommobileno.': 'control_room_mobiles',
}
NUMBER_FIELDS = ('phones', 'mobiles', 'fax', 'control_room', 'control_room_mobiles')
HEADING = '<div class="contact-heading">'
LABEL = '<span class="text-bold">'


def fetch(ctx):
    yield ctx.get(URL)


def _office(heading: str, box: str) -> dict:
    """One zone box (the HTML after its heading) -> record attributes."""
    attrs = {'zone': heading, 'zone_code': zone_code(heading)}
    i = box.find('class="mar-b10"')
    if i < 0:
        raise ValueError(f'{heading}: no address line')
    start = box.find('>', i) + 1
    attrs['address'] = clean(html_text(box[start:box.find('</div>', start)]))
    for f in NUMBER_FIELDS:
        attrs[f] = []
    # '<span class="text-bold">Fax No. </span>2420548 | <span ...' -> label 'Fax No.', value '2420548'
    for piece in box.split(LABEL)[1:]:
        label, _, rest = piece.partition('</span>')
        key = ''.join(clean(label).lower().split())
        if key not in LABELS:
            raise ValueError(f'{heading}: unknown label {clean(label)!r}')
        value = clean(rest[:rest.find('<')] if '<' in rest else rest).strip(' |')
        attrs[LABELS[key]] += split_top(value)
    attrs['detail_url'] = next((u for u, t in links(box, URL) if t == 'Contact Details'), None)
    return attrs


def parse(raw: Raw) -> Result:
    text = raw.text
    start = text.find('<div class="zones-contact">')
    if start < 0:
        raise ValueError('zone contact boxes not found; page layout may have changed')
    end = text.find('<footer', start)
    region = text[start:end if end > 0 else len(text)]
    res = Result(complete_record_types=('smc_zone_office',))
    for chunk in region.split(HEADING)[1:]:
        heading = clean(html_text(chunk[:chunk.find('</div>')]))
        attrs = _office(heading, chunk[chunk.find('</div>') + 6:])
        res.records.append(Record('smc_zone_office', attrs['zone_code'], attrs))
        res.geos.append(zone_geo(attrs['zone_code']))
    return res


def validate(result: Result, raw: Raw) -> None:
    recs = result.records
    if not 8 <= len(recs) <= len(ZONES):
        raise ValidationError(f'{len(recs)} zone offices parsed; expected 9 (page layout may have changed)')
    if any(r.record_key in ('hq', 'south') for r in recs):
        raise ValidationError('a head-quarter or pre-split South Zone box is not a current zone office')
    for r in recs:
        a = r.attrs
        if len(a['address']) < 15 or ',' not in a['address']:
            raise ValidationError(f'{r.record_key}: implausible address {a["address"]!r}')
        numbers = [n for f in NUMBER_FIELDS for n in a[f]]
        if not numbers:
            raise ValidationError(f'{r.record_key}: no phone number at all')
        for n in numbers:
            letters = ''.join(ch for ch in n.lower() if ch.isalpha())
            if sum(ch.isdigit() for ch in n) < 7 or letters not in ('', 'to'):
                raise ValidationError(f'{r.record_key}: implausible number {n!r}')
