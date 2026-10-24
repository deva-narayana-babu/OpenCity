"""Surat district talukas: the official list of talukas and their Mamlatdar offices, from the Collectorate website.

Publisher: District Administration Surat (Collectorate), on its NIC S3WaaS website surat.nic.in ("Content Owned by
District Administration", developed and hosted by the National Informatics Centre).

Endpoint: one plain GET, no parameters, no login or captcha (https://surat.nic.in/robots.txt returns an empty 204
response, so nothing is disallowed):

    https://surat.nic.in/taluka/

Response layout (WordPress HTML): a few paragraphs on the role of the Mamlatdar (the head of a taluka's revenue
administration), then one table with a header row and one row per taluka (17 rows on 2026-10-24):

    SNo. | Taluka Name | Office Address | Phone | EMail
    1  | Majura (Surat City) | Mamlatdar Office of SuratCity Taluka, Athwalines, Opp: District Court, Surat |
         0261-2650335 | 01[dot]mammajura[at]gmail[dot]com
    8  | Olpad | Mamlatdar Office, Olpad | 02621-221245 | mam-olpad[at]gujarat[dot]gov[dot]in
    17 | Areth | Mamlatdar Office, Areth | 02623-261023 | mam-areth[at]gujarat[dot]gov[dot]in

The 17 talukas are six "(Surat City)" talukas (Majura, Udhna, Katargam, Puna, Adajan, Abrama) and the eleven
rural talukas Chorasi, Olpad, Mangrol, Umarpada, Mandvi, Bardoli, Mahuva, Kamrej, Palsana, Ambika and Areth.

Geography: every row becomes a geo of level surat_taluka (parent surat_district/surat). The level is shared with
gsdma_rainfall, census2011_surat and shc_soil_surat, and the codes and names of the talukas they also use are
the same (e.g. chorasi = 'Chorasi (Choryasi)'), so the sources do not rename each other's geos. Codes are the
lower-case taluka names (TALUKAS); an unknown name fails validation instead of inventing a code. The six city
talukas are new codes (majura, udhna, katargam, puna, adajan, abrama). Other sources still report one 'Surat City'
taluka (surat_city: Census 2011, GSDMA rainfall, Soil Health Card); this page does not say how the six city
talukas relate to it, so no parent link between them is stored. No boundaries are published.

Records: 'taluka_office', one per row, keyed by the taluka code (e.g. 'olpad'); the page is the complete list, so
a taluka that disappears gets closed. Attributes:
    taluka          the name as printed ('Majura (Surat City)')
    surat_city      True for the six talukas printed with "(Surat City)"
    office_address  the Mamlatdar office address as printed (an office, never a residence)
    phone           the office landline as printed ('02621-221245'); None if blank. A mobile-format number
                    would be dropped (there is none on the 2026-10-24 page).
    email           the address decoded from "[at]"/"[dot]", kept ONLY on a government domain (gujarat.gov.in,
                    gov.in, nic.in); None otherwise

No observations are emitted: the list of talukas is a geography, not a statistic.

Quirks, kept as published:
- The six city talukas and Ambika publish gmail.com addresses (e.g. "01[dot]mammajura[at]gmail[dot]com", two of
  them malformed, missing "[at"); they look like office accounts, but an automatic rule cannot tell an office
  gmail from a personal one, so they are not stored (email = None).
- Kamrej's row gives "Mamlatdar Office, Bardoli" and mam-bardoli@gujarat.gov.in (Bardoli's own address and email),
  and Umarpada's gives "Mamlatdar Office, Mangrol"; probably copy errors on the page, stored as published.
- Majura and Udhna share one office and phone; Katargam, Puna and Adajan share the Old Collector Office, Nanpura.
- Abrama and Ambika have no phone number.
- Ambika and Areth are not Census 2011 sub-districts (Census 2011 had 10 talukas), so census figures do not line
  up one-to-one with this list.
- The footer "Last Updated: 28.09.2026" is a site-wide date, not the date of this list; it is not used.

Cadence: no schedule; the list changes only when talukas are created or offices move. Checked monthly.
Licence: Government of Gujarat district website (S3WaaS); content owned by District Administration Surat; no
explicit reuse licence found. Public information about government offices.
"""
from __future__ import annotations

from ..model import Geo, Raw, Record, Result, Source, ValidationError
from ..parse import html_tables
from ..surat import TALUKA_NOTE
from .smc_officials import has_mobile, official_email

URL = 'https://surat.nic.in/taluka/'

SOURCE = Source(
    id='surat_talukas',
    name='Surat district talukas and Mamlatdar offices',
    publisher='District Administration Surat (Collectorate), surat.nic.in (NIC S3WaaS)',
    url=URL,
    module='offices',
    cadence='static',
    interval_hours=24 * 30,         # talukas and offices change rarely; a monthly check is enough
    record_types=('taluka_office',),
    geo_note='Surat district talukas (surat_taluka, parent surat_district): 17 on 2026-10-24, six of them in '
             'Surat City',
    licence_note='surat.nic.in, content owned by District Administration Surat; no explicit reuse licence',
    notes=('Taluka list, Mamlatdar office address, office phone and government-domain e-mail only. The gmail.com '
           'addresses printed for the city talukas and Ambika are not stored. No boundaries are published.'),
)

# published taluka name (lower case, without "(Surat City)") -> surat_taluka code
TALUKAS = {
    'majura': 'majura', 'udhna': 'udhna', 'katargam': 'katargam', 'puna': 'puna', 'adajan': 'adajan',
    'abrama': 'abrama', 'chorasi': 'chorasi', 'choryasi': 'chorasi', 'olpad': 'olpad', 'mangrol': 'mangrol',
    'umarpada': 'umarpada', 'mandvi': 'mandvi', 'bardoli': 'bardoli', 'mahuva': 'mahuva', 'kamrej': 'kamrej',
    'palsana': 'palsana', 'ambika': 'ambika', 'areth': 'areth',
}
# surat_taluka code -> geo name. Codes shared with gsdma_rainfall / census2011_surat use their names; surat_city is
# not on this page but is listed so shc_soil_surat can name it the same way.
NAMES = {
    'majura': 'Majura (Surat City)', 'udhna': 'Udhna (Surat City)', 'katargam': 'Katargam (Surat City)',
    'puna': 'Puna (Surat City)', 'adajan': 'Adajan (Surat City)', 'abrama': 'Abrama (Surat City)',
    'chorasi': 'Chorasi (Choryasi)', 'olpad': 'Olpad', 'mangrol': 'Mangrol', 'umarpada': 'Umarpada',
    'mandvi': 'Mandvi', 'bardoli': 'Bardoli', 'mahuva': 'Mahuva', 'kamrej': 'Kamrej', 'palsana': 'Palsana',
    'ambika': 'Ambika', 'areth': 'Areth', 'surat_city': 'Surat City',
}
COLUMNS = ('taluka', 'office address', 'phone', 'email')
ALLOWED_ATTRS = {'taluka', 'surat_city', 'office_address', 'phone', 'email'}


def fetch(ctx):
    yield ctx.get(URL)


def taluka_geo(code: str) -> Geo:
    return Geo('surat_taluka', code, NAMES[code], 'surat_district', 'surat', note=TALUKA_NOTE)


def parse(raw: Raw) -> Result:
    table = next((t for t in html_tables(raw.body) if t.find_row('taluka name', 'office address') == 0), None)
    if table is None:
        raise ValueError('taluka table not found; page layout may have changed')
    header = [h.lower() for h in table.rows[0]]
    col = {c: next((j for j, h in enumerate(header) if h.startswith(c)), None) for c in COLUMNS}
    if None in col.values():
        raise ValueError(f'unexpected taluka table header {table.rows[0]!r}')
    res = Result(complete_record_types=('taluka_office',))
    for row in table.rows[1:]:
        name = row[col['taluka']].strip()
        if not name:
            continue
        base = name.split('(')[0].strip().lower()
        if base not in TALUKAS:
            raise ValidationError(f'unknown Surat taluka {name!r}: add it to TALUKAS and NAMES')
        code = TALUKAS[base]
        phone = row[col['phone']].strip()
        res.geos.append(taluka_geo(code))
        res.records.append(Record('taluka_office', code, {
            'taluka': name,
            'surat_city': '(surat city)' in name.lower(),
            'office_address': row[col['office address']] or None,
            'phone': phone if phone and not has_mobile(phone) else None,
            'email': official_email(row[col['email']]),
        }))
    return res


def validate(result: Result, raw: Raw) -> None:
    recs = result.records
    if not 12 <= len(recs) <= 30:
        raise ValidationError(f'{len(recs)} talukas parsed; expected about 17 (page layout may have changed)')
    codes = {r.record_key for r in recs}
    missing = {'olpad', 'bardoli', 'mandvi', 'kamrej', 'chorasi'} - codes
    if missing:
        raise ValidationError(f'core Surat talukas {sorted(missing)} missing from the list')
    for r in recs:
        a = r.attrs
        extra = set(a) - ALLOWED_ATTRS
        if extra:
            raise ValidationError(f'{r.record_key}: attributes {sorted(extra)} are not allowed')
        if not a['office_address'] or len(a['office_address']) > 200 or has_mobile(a['office_address']):
            raise ValidationError(f'{r.record_key}: implausible office address {a["office_address"]!r}')
        if a['phone'] and (has_mobile(a['phone']) or sum(ch.isdigit() for ch in a['phone']) < 8):
            raise ValidationError(f'{r.record_key}: implausible or mobile phone {a["phone"]!r}')
        if a['email'] and not official_email(a['email']):
            raise ValidationError(f'{r.record_key}: non-government e-mail {a["email"]!r}')
