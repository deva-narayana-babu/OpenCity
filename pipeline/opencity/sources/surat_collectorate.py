"""Surat district administration Who's Who: the Collector, Collectorate officers and the Prant (sub-division) officers.

Publisher: District Administration Surat (Collectorate), on its NIC S3WaaS website surat.nic.in ("Content Owned by
District Administration", developed and hosted by the National Informatics Centre).

Endpoint: one plain GET, no parameters, no login or captcha (https://surat.nic.in/robots.txt returns an empty
204 response, so nothing is disallowed):

    https://surat.nic.in/whos-who/

The page's division filter ("All", "Prant Officers", "Collectorate") only hides tables in the browser; the default
"All" page already carries every table, so nothing else is requested.

Response layout (WordPress HTML), one table per division, each with a <caption>:

    <caption>Collectorate</caption>     (5 rows on 2026-10-24)
    <caption>Prant Officers</caption>   (6 rows on 2026-10-24)
    Name | Designation | Email | Address | Phone | Fax
    Shri Tejas Parmar IAS | Collector & District Magistrate | collector-sur[at]gujarat[dot]gov[dot]in |
        Collector Office, Jilla Seva Sadan-II, "B" Block, 5th Floor, Athwalines, Surat-395001 | +91-261-2655151 |
        +91-261-2655757

-> one 'district_official' record per row, keyed by the designation slug (e.g. 'collector-district-magistrate',
   'deputy-collector-prant-officer-bardoli'), so a change of officer shows up as a new version of the same post
   (a designation printed twice would get the officer's name slug appended). The page is the complete list, so a
   post that disappears gets closed. Attributes:
     division     the table caption as printed ('Collectorate' or 'Prant Officers')
     designation  as printed; for Prant Officers it names the sub-division (Surat South, City North/Adajan, Mandvi,
                  Bardoli, Kamrej, Olpad)
     name         as printed, without the honorific ('Shri', 'Shri.') and the service ('IAS'), which are kept
                  separately as honorific / service
     email        the address decoded from "[at]"/"[dot]", kept ONLY on a government domain (gujarat.gov.in,
                  gov.in, nic.in); None otherwise
     office_address  the office address as printed (Jilla Seva Sadan, Taluka Seva Sadan, ...): an office, never a
                  residence
     phones, fax  the office numbers as printed, split at commas (e.g. '+91-261-2655151', '91-2623-221177');
                  mobile-format numbers would be dropped (none on the 2026-10-24 page)

Not stored: the gmail.com addresses that the Dy. Collector (Land Reform) and the six Prant offices publish
(e.g. a "prantmandvi" account). They look like office accounts, but an automatic rule cannot tell an office gmail
from a personal one, so only government-domain addresses are kept; the page itself remains the reference.

Quirks, kept as published: honorifics do not always match the officer ("Shri" before women's names); phone
numbers are printed with and without the leading "+"; the City Prant (North) and Surat Prant (South) share the
number 2665800. The site footer "Last Updated: 06.08.2019" is a template date, not the date of this list; it is
not used. The data has not changed between our saved copy of 2026-09-28 and 2026-10-24 (the site theme did).
The page carries a WordPress nonce that changes on every request; normalize() blanks it so an unchanged list is
recognised as unchanged.

No observations are emitted: a count of posts on a web page is not a statistic worth a time series.
Geography: Surat district (Collectorate) and its Prant sub-divisions, as text in the designation. Cadence: no
schedule, changes with transfers; checked weekly.
Licence: Government of Gujarat district website (S3WaaS); content owned by District Administration Surat; no
explicit reuse licence found. Public information about public officials.
"""
from __future__ import annotations

from ..archive import blank_attribute
from ..model import Raw, Record, Result, Source, ValidationError
from ..parse import html_tables
from .smc_officials import has_mobile, official_email, slug, split_name, split_top

URL = 'https://surat.nic.in/whos-who/'

SOURCE = Source(
    id='surat_collectorate',
    name="Surat district Who's Who: Collector, Collectorate and Prant officers",
    publisher='District Administration Surat (Collectorate), surat.nic.in (NIC S3WaaS)',
    url=URL,
    module='leadership',
    cadence='weekly',
    interval_hours=24 * 7,          # changes with transfers; a weekly check is enough
    record_types=('district_official',),
    geo_note='Surat district: the Collectorate and its Prant (sub-division) offices',
    licence_note='surat.nic.in, content owned by District Administration Surat; no explicit reuse licence',
    notes=('Name, designation, division, office address, office phone/fax and government-domain e-mail only. The '
           'gmail.com addresses printed for the Prant offices and the Land Reform branch are not stored.'),
)

ALLOWED_ATTRS = {'division', 'designation', 'name', 'honorific', 'service', 'email', 'office_address', 'phones', 'fax'}
COLUMNS = ('name', 'designation', 'email', 'address', 'phone', 'fax')


def fetch(ctx):
    yield ctx.get(URL)


def normalize(body: bytes) -> bytes:
    """'<div class ="ww_html" data-nonce="cdb7e59354" ...>' -> 'data-nonce=""' (changes on every request)."""
    return blank_attribute(body, b'<div', (b'data-nonce=',), b'data-nonce')


def _numbers(cell: str) -> list[str]:
    return [p for p in split_top(cell) if not has_mobile(p)]


def parse(raw: Raw) -> Result:
    res = Result(complete_record_types=('district_official',))
    rows = []
    for table in html_tables(raw.body):
        if table.find_row('name', 'designation', 'email') != 0:
            continue
        header = [h.lower() for h in table.rows[0]]
        col = {c: next((j for j, h in enumerate(header) if h.startswith(c)), None) for c in COLUMNS}
        if None in col.values():
            raise ValueError(f'unexpected Who\'s Who header {table.rows[0]!r}')
        for row in table.rows[1:]:
            if not row[col['name']].strip():
                continue
            honorific, name, service = split_name(row[col['name']])
            attrs = {'division': table.caption, 'designation': row[col['designation']], 'name': name,
                     'email': official_email(row[col['email']]), 'office_address': row[col['address']] or None,
                     'phones': _numbers(row[col['phone']]), 'fax': _numbers(row[col['fax']])}
            if honorific:
                attrs['honorific'] = honorific
            if service:
                attrs['service'] = service
            rows.append(attrs)
    designations = [slug(a['designation']) for a in rows]
    for a in rows:
        key = slug(a['designation'])
        if designations.count(key) > 1:
            key = f'{key}-{slug(a["name"])}'
        res.records.append(Record('district_official', key, a))
    return res


def validate(result: Result, raw: Raw) -> None:
    recs = result.records
    if not 5 <= len(recs) <= 60:
        raise ValidationError(f'{len(recs)} officials parsed; expected about 11 (page layout may have changed)')
    collectors = [r for r in recs if r.attrs['designation'].lower().startswith('collector')]
    if len(collectors) != 1:
        raise ValidationError(f'expected one Collector & District Magistrate, found {len(collectors)}')
    prants = sum(1 for r in recs if 'prant' in r.attrs['designation'].lower())
    if not 3 <= prants <= 12:
        raise ValidationError(f'{prants} Prant officers listed; Surat district has about 6 sub-divisions')
    for r in recs:
        a = r.attrs
        extra = set(a) - ALLOWED_ATTRS
        if extra:
            raise ValidationError(f'{r.record_key}: attributes {sorted(extra)} are not allowed')
        if not a['designation'] or any(ch.isdigit() for ch in a['name']) or not 3 <= len(a['name']) <= 80:
            raise ValidationError(f'{r.record_key}: implausible name {a["name"]!r} or empty designation')
        if a['email'] and not official_email(a['email']):
            raise ValidationError(f'{r.record_key}: non-government e-mail {a["email"]!r}')
        for n in a['phones'] + a['fax']:
            if has_mobile(n) or sum(ch.isdigit() for ch in n) < 6:
                raise ValidationError(f'{r.record_key}: implausible or mobile number {n!r}')
