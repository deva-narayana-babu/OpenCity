"""SMC administrative wing: the Municipal Commissioner and the officers listed on SMC's "SMC Officials" page.

Publisher: Surat Municipal Corporation (administrative wing; the page sits under "Contact Us" on the SMC site).

Endpoint: one plain GET, no parameters, no login or captcha (robots.txt on www.suratmunicipal.gov.in returns 404,
so nothing is disallowed):

    https://www.suratmunicipal.gov.in/Home/SMCOfficials

Response layout (server-rendered HTML, no tables). After the head-quarter and zone contact boxes (those belong to
the smc_zone_offices and smc_helplines sources and are not read here) comes "Contact Details of SMC Officers":

    <h3>Municipal Commissioner</h3>
      <div class="contact-block"> <div class="name">Shri Rajkumar Beniwal, IAS</div>
        <div class="designation">Municipal Commissioner, Surat Municipal Corporation</div>
        <div class="officeTelephone">(O) +91-261-2422244</div> <div class="faxNumber">(F) +91-261-2422110</div>
    <div class="contact-heading">Administrative | Engineering | Health</div>
      <ul> <li class="contact-block"> one card per officer:
        <div class="name">Ms. Nidhi Siwach (IAS)</div>
        <div class="text-bold">South West Zone(Athwa)</div>         (only on some Health cards: the zone)
        <div class="designation">Deputy Mun. Commissioner (Deputation)</div>
        <div class="contact-mobile">(M) ..........</div>             (NOT stored, see below)
        <div class="officeTelephone">(O) 0261-2423750 (PABX - 222)</div>   (0..n)
        <div class="contact-email govdotin">dmc.ns</div>             (0..n; also as <span> inside a wrapper)

The "govdotin" e-mail cells hold only the local part; a script at the end of the page appends
"[at]suratmunicipal[dot]gov[dot]in". parse() reads that suffix from the script (it fails if the script is gone)
instead of assuming it.

-> one 'smc_official' record per card (snapshot 2026-10-24: 92 cards: the Commissioner, 42 Administrative,
   16 Engineering, 33 Health, including 7 Deputy Municipal Commissioners and 20 zone Food Safety Officers).
   The page is the complete list, so an officer who disappears from it gets closed. Record attributes:
     wing         'commissioner', 'administrative', 'engineering' or 'health' (the page's grouping)
     designation  as printed, e.g. 'Executive Engineer (Hydraulic)': the department is part of it
     name         as printed without the honorific and service suffix; honorific ('Shri', 'Sh.', 'Smt.', 'Ms.',
                  'Dr.' ...) and service ('IAS' when the page says so) are kept separately
     zone, zone_code  the zone line of a card (Food Safety Officers) and its canonical code from surat.zone_code()
     office_phones    the "(O)" numbers as printed (STD 0261 for Surat; "to 56" ranges and PABX extensions kept
                      as text), list; the Commissioner card also has fax
     emails       official addresses only (domains gov.in, nic.in, suratmunicipal.org), list
   Keys: the designation slug (e.g. 'chief-fire-officer'), so a change of officer shows up as a new version of the
   same role. Designations printed on more than one card (5 x 'Deputy Mun. Commissioner', 20 x 'Food Safety
   Officer', ...) get the officer's name slug appended ('deputy-mun-commissioner-swati-p-desai').

What is deliberately NOT stored (whitelist; validate() rejects anything else):
- "(M)" mobile numbers. The page prints a mobile for almost every officer; they are personal contacts of the
  officer and are kept out of the database and, via normalize(), out of the raw archive too.
- Office numbers in mobile format. One card lists three 10-digit mobile numbers as "(O)"; the page does not say
  whether these are desk phones or the officer's own mobile, so any "(O)" entry that is a mobile number is dropped
  (it stays in the archived page, where SMC labels it as an office number).
- E-mail addresses on non-government domains. The 20 Food Safety Officer cards print gmail/yahoo addresses named
  after the officer; they are not stored and are blanked in the archive.
No observations are emitted: a count of names on a web page is not a statistic worth a time series.

Quirks, kept as published: honorifics do not always match the officer ("Sh." on several women's names); some
office numbers sit in the CSS class meant for mobiles, so a number is classified by its "(O)"/"(M)"/"(F)"
prefix, not by the class; one card prints the mobile-style prefix "(M)" and an office number "(O)" in two
"contact-mobile" divs. The footer "Last Updated" is the CMS edit time of the page, not a data date; it is not used.

Geography: SMC city (the corporation's officers). Cadence: no schedule, changes with transfers and postings;
checked weekly.
Licence: Surat Municipal Corporation web page; public information about public officials. No explicit licence.
"""
from __future__ import annotations

from html.parser import HTMLParser

from ..model import Raw, Record, Result, Source, ValidationError
from ..parse import clean
from ..surat import zone_code

URL = 'https://www.suratmunicipal.gov.in/Home/SMCOfficials'

SOURCE = Source(
    id='smc_officials',
    name='SMC officials: Municipal Commissioner, Deputy Municipal Commissioners and department officers',
    publisher='Surat Municipal Corporation (administrative wing)',
    url=URL,
    module='leadership',
    cadence='weekly',
    interval_hours=24 * 7,          # the list changes with transfers and postings; a weekly check is enough
    record_types=('smc_official',),
    geo_note='SMC city (officers of the corporation; Food Safety Officer cards name their zone)',
    licence_note='Surat Municipal Corporation web page; public information about public officials',
    notes=('Names, designations, wing, zone, office ("(O)") phone numbers and official e-mail only. The "(M)" mobile '
           'numbers and gmail/yahoo addresses printed on the page are not stored and are blanked in the raw '
           'archive; "(O)" entries in mobile format are dropped too. The e-mail domain comes from the page\'s own '
           'script ("[at]suratmunicipal[dot]gov[dot]in").'),
)

ALLOWED_ATTRS = {'wing', 'designation', 'name', 'honorific', 'service', 'zone', 'zone_code',
                 'office_phones', 'fax', 'emails'}
OFFICIAL_EMAIL_DOMAINS = ('gov.in', 'nic.in', 'suratmunicipal.org')
HONORIFICS = {'shri', 'sh', 'smt', 'shrimati', 'ms', 'mr', 'mrs', 'dr', 'kum', 'kumari'}
SERVICES = ('IAS', 'IPS', 'IFS', 'GAS')
WINGS = {'municipal commissioner': 'commissioner', 'administrative': 'administrative',
         'engineering': 'engineering', 'health': 'health'}
GOVDOTIN = '.govdotin").append("'      # $(".contact-email.govdotin").append("[at]suratmunicipal[dot]gov[dot]in");


def fetch(ctx):
    yield ctx.get(URL)


# ---------- helpers shared with the other directory adapters ----------

def slug(s: str) -> str:
    out = ''.join(ch if ch.isalnum() else ' ' for ch in s.lower())
    return '-'.join(out.split())


def split_top(s: str) -> list[str]:
    """Split on commas outside brackets: '2420547, 2423751 to 56 (Ext - 205, 421)' -> ['2420547', '2423751 to 56 (Ext - 205, 421)']."""
    parts, buf, depth = [], [], 0
    for ch in s:
        if ch in '([':
            depth += 1
        elif ch in ')]':
            depth = max(0, depth - 1)
        if ch == ',' and depth == 0:
            parts.append(''.join(buf))
            buf = []
        else:
            buf.append(ch)
    parts.append(''.join(buf))
    return [clean(p) for p in parts if clean(p)]


def has_mobile(s: str) -> bool:
    """True if s contains an Indian mobile number: '63599 06891', '+91-9876543210', '9724346011-13'."""
    digits = ''.join(ch if ch.isdigit() else ' ' for ch in s.replace(' ', ''))
    for tok in digits.split():
        if len(tok) == 12 and tok.startswith('91'):
            tok = tok[2:]
        elif len(tok) == 11 and tok.startswith('0'):
            tok = tok[1:]
        if len(tok) == 10 and tok[0] in '6789':
            return True
    return False


def official_email(s: str) -> str | None:
    """'collector-sur[at]gujarat[dot]gov[dot]in' -> 'collector-sur@gujarat.gov.in'; None unless on a government domain."""
    e = s.lower().replace('[at]', '@').replace('(at)', '@').replace('[dot]', '.').replace('(dot)', '.')
    e = ''.join(e.split())
    user, at, domain = e.partition('@')
    if not (user and at and '.' in domain) or '@' in domain:
        return None
    if any(domain == d or domain.endswith('.' + d) for d in OFFICIAL_EMAIL_DOMAINS):
        return e
    return None


def split_name(full: str) -> tuple[str | None, str, str | None]:
    """'Ms. Nidhi Siwach (IAS)' -> ('Ms.', 'Nidhi Siwach', 'IAS'); 'Shri Tejas Parmar IAS' -> ('Shri', 'Tejas Parmar', 'IAS')."""
    name = clean(full).strip(' ,')
    honorific = None
    first, _, rest = name.partition(' ')
    if first.lower().rstrip('.') in HONORIFICS and rest:
        honorific, name = first, rest.strip()
    service = None
    for svc in SERVICES:
        for tail in (f'({svc})', f', {svc}', f' {svc}'):
            if name.endswith(tail):
                service, name = svc, name[:-len(tail)].strip(' ,')
    return honorific, name, service


# ---------- normalize ----------

def normalize(body: bytes) -> bytes:
    """Keep personal contacts out of the raw archive (parse() never reads them, so parsing is unaffected):
    '<div class="contact-mobile">(M) 9724345001</div>' -> '(M)</div>', and a non-government address in
    '<div class="contact-email">name[at]gmail[dot]com</div>' -> '<div class="contact-email"></div>'."""
    out, pos = [], 0
    i = body.find(b'(M)')
    while i != -1:
        before = i - 1
        while before > 0 and body[before:before + 1].isspace():
            before -= 1
        end = body.find(b'<', i)
        if body[before:before + 1] == b'>' and end != -1:        # "(M)" starts the element's text
            out.append(body[pos:i + 3])
            pos = end
        i = body.find(b'(M)', i + 3)
    out.append(body[pos:])
    body = b''.join(out)

    out, pos = [], 0
    i = body.find(b'class="contact-email"')
    while i != -1:
        start = body.find(b'>', i) + 1
        end = body.find(b'<', start)
        if start and end != -1 and not official_email(body[start:end].decode('utf-8', 'replace')):
            out.append(body[pos:start])
            pos = end
        i = body.find(b'class="contact-email"', i + 1)
    out.append(body[pos:])
    return b''.join(out)


# ---------- parse ----------

class _Cards(HTMLParser):
    """Collects officer cards as [(heading, [(field, text, classes)])] from the "Contact Details of SMC Officers" part."""
    FIELDS = ('name', 'designation', 'text-bold', 'officeTelephone', 'faxNumber', 'contact-mobile', 'contact-email')

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.heading = ''
        self.cards: list[tuple[str, list]] = []
        self._field = None          # (field, tag, classes) being captured
        self._depth = 0
        self._buf: list[str] = []

    def handle_starttag(self, tag, attrs):
        if self._field:
            if tag == self._field[1]:
                self._depth += 1
            self._buf.append(' ')
            return
        classes = (dict(attrs).get('class') or '').split()
        if 'contact-block' in classes:
            self.cards.append((self.heading, []))
        elif tag == 'h3' or 'contact-heading' in classes:
            self._field, self._buf = ('heading', tag, classes), []
        elif self.cards:
            for f in self.FIELDS:
                if f in classes:
                    self._field, self._buf = (f, tag, classes), []
                    break

    def handle_endtag(self, tag):
        if not self._field or tag != self._field[1]:
            return
        if self._depth:
            self._depth -= 1
            return
        text = clean(''.join(self._buf))
        if self._field[0] == 'heading':
            self.heading = text
        else:
            self.cards[-1][1].append((self._field[0], text, self._field[2]))
        self._field = None

    def handle_data(self, data):
        if self._field:
            self._buf.append(data)


def _email_suffix(text: str) -> str | None:
    i = text.find(GOVDOTIN)
    if i < 0:
        return None
    start = i + len(GOVDOTIN)
    return text[start:text.find('"', start)]


def parse(raw: Raw) -> Result:
    text = raw.text
    start = text.find('Contact Details of SMC Officers')
    if start < 0:
        raise ValueError('"Contact Details of SMC Officers" not found; page layout may have changed')
    end = text.find('<footer', start)
    cards = _Cards()
    cards.feed(text[start:end if end > 0 else len(text)])
    cards.close()
    suffix = _email_suffix(text)

    people = []
    for heading, fields in cards.cards:
        attrs = {'wing': WINGS.get(heading.lower(), slug(heading).replace('-', '_')),
                 'office_phones': [], 'emails': []}
        for field, value, classes in fields:
            if field == 'name' and value:
                honorific, attrs['name'], service = split_name(value)
                if honorific:
                    attrs['honorific'] = honorific
                if service:
                    attrs['service'] = service
            elif field == 'designation' and value:
                attrs['designation'] = value
            elif field == 'text-bold' and value:
                attrs['zone'] = value
                attrs['zone_code'] = zone_code(value)
            elif field == 'contact-email' and value:
                if 'govdotin' in classes:
                    if not suffix:
                        raise ValueError('e-mail domain script ".govdotin").append(...)" not found')
                    value += suffix
                email = official_email(value)
                if email:
                    attrs['emails'].append(email)
            elif value.startswith('(O)') or (field == 'officeTelephone' and not value.startswith('(')):
                # an office line may hold several numbers; mobile-format ones are dropped (see docstring)
                attrs['office_phones'] += [p for p in split_top(value.removeprefix('(O)')) if not has_mobile(p)]
            elif value.startswith('(F)') or field == 'faxNumber':
                attrs['fax'] = clean(value.removeprefix('(F)'))
            # "(M)" numbers, in whatever class, are never read
        if 'name' not in attrs:
            continue
        if 'designation' not in attrs:
            raise ValueError(f'officer card {attrs["name"]!r} has no designation')
        people.append(attrs)

    seen: dict[str, int] = {}
    for a in people:
        seen[slug(a['designation'])] = seen.get(slug(a['designation']), 0) + 1
    res = Result(complete_record_types=('smc_official',))
    for a in people:
        key = slug(a['designation'])
        if seen[key] > 1:
            key = f'{key}-{slug(a["name"])}'
        res.records.append(Record('smc_official', key, a))
    return res


# ---------- validate ----------

def validate(result: Result, raw: Raw) -> None:
    recs = result.records
    if not 40 <= len(recs) <= 250:
        raise ValidationError(f'{len(recs)} officer cards parsed; expected about 90 (page layout may have changed)')
    for r in recs:
        a = r.attrs
        extra = set(a) - ALLOWED_ATTRS
        if extra:
            raise ValidationError(f'{r.record_key}: attributes {sorted(extra)} are not allowed')
        for k, v in a.items():
            for s in (v if isinstance(v, list) else [v]):
                if isinstance(s, str) and has_mobile(s):
                    raise ValidationError(f'{r.record_key}: {k} contains a mobile number; not stored')
        for e in a['emails']:
            if not official_email(e):
                raise ValidationError(f'{r.record_key}: non-official e-mail {e!r}')
        nm = a['name']
        if any(ch.isdigit() for ch in nm) or not 3 <= len(nm) <= 80:
            raise ValidationError(f'implausible officer name {nm!r} ({a["designation"]})')
        for p in a['office_phones'] + ([a['fax']] if 'fax' in a else []):
            if sum(ch.isdigit() for ch in p) < 6:
                raise ValidationError(f'{r.record_key}: implausible phone {p!r}')
    wings: dict[str, int] = {}
    for r in recs:
        wings[r.attrs['wing']] = wings.get(r.attrs['wing'], 0) + 1
    if wings.get('commissioner') != 1:
        raise ValidationError(f'expected one Municipal Commissioner card, got {wings.get("commissioner", 0)}')
    commissioner = next(r.attrs for r in recs if r.attrs['wing'] == 'commissioner')
    if not commissioner['designation'].lower().startswith('municipal commissioner'):
        raise ValidationError(f'Commissioner card has designation {commissioner["designation"]!r}')
    for w in ('administrative', 'engineering', 'health'):
        if wings.get(w, 0) < 5:
            raise ValidationError(f'only {wings.get(w, 0)} officers in the {w} list; page layout may have changed')
    dmc = sum(1 for r in recs if r.attrs['designation'].lower().startswith(('deputy mun', 'deputy municipal')))
    if not 2 <= dmc <= 15:
        raise ValidationError(f'{dmc} Deputy Municipal Commissioners listed; expected 2..15')
