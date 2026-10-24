"""SMC emergency and helpline numbers: zone control rooms, complaint helplines, fire, ambulance, hospitals.

Publisher: Surat Municipal Corporation (the "Emergency/Imp. Nos." page under "Contact Us" on the SMC site).

Endpoint: one plain GET, no parameters, no login or captcha (robots.txt on www.suratmunicipal.gov.in returns 404,
so nothing is disallowed):

    https://www.suratmunicipal.gov.in/Home/EmergencyContactNo

The sibling page /Home/TollFreeNumbers lists the same three toll-free numbers that appear here under "SMC Help
Line", so it is not fetched.

Response layout (server-rendered HTML, no tables), two sections of boxes:

    <h2>Zone-wise Emergency/Imp Nos.</h2>   ... <h2>Other Emergency/Imp Nos.</h2>
    <div class="contact-block">
      <h2>Fire</h2>
      <div class="mar-b10"> <div class="text-bold">Contact Number</div> <div>101, 2414139</div> </div>
      <div> <div class="text-bold">Control Room</div> <div>2414195-96, 2423751-56 (Ext - 324), 9724346022</div> </div>

-> one 'smc_helpline' record per labelled line of a box (snapshot 2026-10-24: 30 lines in 15 boxes), keyed by
   box and label, e.g. 'fire-control-room', 'smc-help-line-for-complaint-registration'. The page is the complete
   list, so a line that disappears gets closed. Attributes:
     section    'zone' (Zone-wise Emergency/Imp Nos.) or 'other' (Other Emergency/Imp Nos.)
     service    the box title as printed: 'SMC HQ', 'Central Zone', 'Fire', 'Ambulance / Shabvahini',
                'SMIMER Hospital', 'Complaint Registration via WhatsApp', 'Stray Dog Bite Complaint', ...
     line       the label as printed: 'Contact Number', 'Control Room', 'Central Control Room',
                'For Complaint Registration', 'WhatsApp Number', 'Tele-Medicine Helpline No.', ...
     numbers    the entries as printed, split at commas outside brackets (so '2423751 to 56 (Ext - 205, 421, 422,
                423)' stays one entry); ranges such as '9724346030-33' are not expanded; 7-digit numbers are
                Surat landlines (STD code 0261)
     toll_free  True when an entry is marked '(Toll Free)'
     hours      service hours printed in square brackets ('6:00 am to 10:00 pm'), else None
     zone_code  zone section only: the canonical code from surat.zone_code() when the title maps to one
   Mobile numbers are kept: on this page every one of them is printed as the number of a control room, hospital
   or helpline, not of a person.

Quirks: the zone section still uses the older seven-zone names, from before the East and South zones were each
split in two (Central, East, South West, West, North, South, South East). 'South Zone' maps to code 'south'
(Udhna, before its split into South-A and South-B). 'East Zone' has no
code: the corporation's zone list has only East-A and East-B now, and the page does not say which one is meant
(its numbers are those of the East Zone A office), so zone_code is None rather than a guess. 'SMC HQ' also has no
zone code. The footer "Last Updated" is the CMS edit time, not a data date; it is not used.

No observations are emitted: this is reference data, not a time series.
Geography: SMC city and its zones (records only). Cadence: static reference data, edited without schedule;
checked weekly.
Licence: Surat Municipal Corporation web page; public information. No explicit licence.
"""
from __future__ import annotations

from ..model import Raw, Record, Result, Source, ValidationError
from ..parse import html_text
from ..surat import zone_code
from .smc_officials import slug, split_top

URL = 'https://www.suratmunicipal.gov.in/Home/EmergencyContactNo'

SOURCE = Source(
    id='smc_helplines',
    name='SMC emergency and helpline numbers',
    publisher='Surat Municipal Corporation',
    url=URL,
    module='citizen',
    cadence='static',
    interval_hours=24 * 7,          # reference data; a weekly check is plenty
    record_types=('smc_helpline',),
    geo_note='SMC city; zone control-room lines carry a zone_code where the (older) zone name maps to one',
    licence_note='Surat Municipal Corporation web page; public information',
    notes=('Numbers are kept as printed (ranges not expanded; 7-digit numbers are Surat 0261 landlines). The zone '
           'section uses old zone names: "East Zone" gets no zone_code. /Home/TollFreeNumbers duplicates the '
           'toll-free lines and is not fetched.'),
)

SECTIONS = (('zone', 'Zone-wise Emergency'), ('other', 'Other Emergency'))
BOX = '<div class="contact-block">'


def fetch(ctx):
    yield ctx.get(URL)


def _code(title: str) -> str | None:
    try:
        return zone_code(title)
    except KeyError:
        return None


def _line(section: str, title: str, label: str, value: str) -> Record:
    hours = None
    if '[' in value and ']' in value:
        i, j = value.find('['), value.find(']')
        hours, value = value[i + 1:j].strip(), value[:i] + value[j + 1:]
    numbers = split_top(value)
    attrs = {'section': section, 'service': title, 'line': label, 'numbers': numbers,
             'toll_free': any('toll free' in n.lower() for n in numbers), 'hours': hours}
    if section == 'zone':
        attrs['zone_code'] = _code(title)
    return Record('smc_helpline', slug(f'{title} {label}'), attrs)


def parse(raw: Raw) -> Result:
    text = raw.text
    starts = [text.find(marker) for _, marker in SECTIONS]
    if min(starts) < 0:
        raise ValueError('emergency number sections not found; page layout may have changed')
    end = text.find('<footer', starts[-1])
    bounds = starts + [end if end > 0 else len(text)]
    res = Result(complete_record_types=('smc_helpline',))
    for k, (section, _) in enumerate(SECTIONS):
        for box in text[bounds[k]:bounds[k + 1]].split(BOX)[1:]:
            lines = html_text(box).splitlines()       # title, then label / value pairs
            title, pairs = lines[0], lines[1:]
            if len(pairs) % 2:
                raise ValueError(f'{title}: a label without a number (or the reverse): {pairs!r}')
            for i in range(0, len(pairs), 2):
                res.records.append(_line(section, title, pairs[i], pairs[i + 1]))
    return res


def validate(result: Result, raw: Raw) -> None:
    recs = [r.attrs for r in result.records]
    if not 15 <= len(recs) <= 80:
        raise ValidationError(f'{len(recs)} helpline lines parsed; expected about 30 (page layout may have changed)')
    for a in recs:
        if not a['numbers']:
            raise ValidationError(f'{a["service"]} / {a["line"]}: no number')
        for n in a['numbers']:
            if sum(ch.isdigit() for ch in n) < 3:
                raise ValidationError(f'{a["service"]} / {a["line"]}: implausible number {n!r}')
    for service, emergency in (('fire', '101'), ('ambulance', '102')):
        if not any(a['service'].lower().startswith(service) and emergency in a['numbers'] for a in recs):
            raise ValidationError(f'no {service} line with the national number {emergency}')
    if not any(a['toll_free'] and any(n.startswith('1800') for n in a['numbers']) for a in recs):
        raise ValidationError('no toll-free (1800) complaint line found')
    zoned = sum(1 for a in recs if a.get('zone_code'))
    if zoned < 5:
        raise ValidationError(f'only {zoned} zone lines map to an SMC zone; zone names may have changed')
