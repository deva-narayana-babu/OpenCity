"""SMC elected wing: corporators (2026-31 term), office bearers, and the 2021 ward-wise seats/voters statement.

Three SMC pages, each parsed on its own (parse() recognises the page from its content):

1. Corp_list ("Ward wise list of Corporators"): 30 blocks
       <h3>Ward No. N - <ward name></h3> <ul> <li><form ...><button>MRS FIRST MIDDLE LAST</button></form></li> x4 </ul>
   -> 'corporator' records keyed ward-<n>-<name-slug> (survives re-ordering of the list), plus the 30
      smc_ward geographies. The page is the complete current list, so people who drop off it get closed.
      Only the ward and the published name are stored. The per-corporator detail pages (POST + anti-forgery
      token) are NOT fetched: they are not needed and carry personal details.

2. OfficeBearers: <h2>Designation</h2> <h3>Smt./Shri Name</h3> <p><b>Ward:</b> ..</p> <p><b>Email:</b> ..</p>
   -> 'office_bearer' records keyed by designation slug (e.g. 'mayor'), so a change of office holder shows up
      as a new version of the same role. The page also prints each office bearer's residential address and
      personal mobile number; those fields are never read (whitelist of 'Ward' and 'Email' only), and an
      email is kept only when it is on an official government domain.

3. ElectionCensusWardwiseAllotmentSeats ("Statement Showing Situation of Seats & Nos. of Voters"), 2021 election:
   one table, 30 ward rows + a totals row:
       Ward No. | Ward Name | Ward Population (2011 Census, 2020 limits) | seat 1 (women) | seat 2 (women)
       | seat 3 | seat 4 | Male / Female / Third Gender / Total Voters as on date 01-01-2021
   -> numeric observations per smc_ward (and smc_city from the published totals row).
   The 2021 statement uses the same 30 ward numbers and names (spelling variants only) as the 2026-31
   corporator list, so it is filed under smc_ward. validate() re-checks that name correspondence on every
   fetch and fails loudly if it ever breaks (e.g. the page is replaced after a re-delimitation).
"""
from __future__ import annotations

import difflib
import re
from datetime import datetime
from html.parser import HTMLParser

from ..model import FetchError, Geo, Metric, Obs, Raw, Record, Result, Source, ValidationError
from ..parse import clean, html_tables, num, parse_date
from ..surat import SMC

CORP_URL = 'https://www.suratmunicipal.gov.in/Corporation/Corp_list'
OB_URL = 'https://www.suratmunicipal.gov.in/Corporation/OfficeBearers'
SEATS_URL = 'https://www.suratmunicipal.gov.in/Departments/ElectionCensus/ElectionCensusWardwiseAllotmentSeats'

DOCS = (
    (CORP_URL, 'corporators'),
    (OB_URL, 'office_bearers'),
    (SEATS_URL, 'wardwise_seats_voters'),
)

# Canonical ward names, exactly as on Corp_list (snapshot 2026-09-28, 2026-31 term). Used as the smc_ward
# geography names by every document of this source so the names do not flip between pages that spell them
# differently. The live Corp_list spelling is kept on each corporator record (attrs.ward_name).
WARDS_2026 = {
    1: 'Jahangirpura-Variyav-Chhaprabhatha-Kosad',
    2: 'Amroli-Mota Varachha-Kathor',
    3: 'Varachha-Sarthana-Simada-Laskana',
    4: 'Kapodra',
    5: 'Fulpada-Ashwinikumar',
    6: 'Katargam',
    7: 'Katargam-Vedroad',
    8: 'Dabholi-Singanpor',
    9: 'Rander-Jahangirabad-Palanpur',
    10: 'Adajan-Pal-Ichchhapor',
    11: 'Adajan-Gorat',
    12: 'Nanavat-Saiyadpura-Kubernagar-Mahidharpura',
    13: 'Wadi Falia-Navapura-Begumpura-Salabatpura',
    14: 'Umarwada-Matawadi',
    15: 'Karanj-Magob',
    16: 'Puna(West)',
    17: 'Puna(East)',
    18: 'Limbayat-Parvat-Kumbhariya',
    19: 'Aanjana-Dumbhal',
    20: 'Khatodara-Majura-Sagrampura',
    21: 'Soni Falia-Nanpura-Athwa-Piplod',
    22: 'Bhatar-Vesu-Dumas',
    23: 'Bamroli-Udhna(North)',
    24: 'Udhna(South)',
    25: 'Limbayat-Udhna Yard',
    26: 'Godadara-Dindoli(North)',
    27: 'Dindoli(South)',
    28: 'Pandesara-Bhestan',
    29: 'Althan-Bamroli-Vadod',
    30: 'Kansad-Sachin-Unn-Aabhva',
}
N_WARDS = len(WARDS_2026)
SEATS_PER_WARD = 4

WARD_NOTE = ('SMC election ward, numbered as on the 2026-31 corporator list. The 2021 general election used the '
             'same 30 ward numbers and names (2020 delimitation, after the 2020 city-limit extension).')

CATEGORIES = ('general', 'sc', 'st', 'obc')
_CATEGORY = {'general': 'general', 'sc': 'sc', 'st': 'st', 'obc': 'obc'}

SOURCE = Source(
    id='smc_council',
    name='SMC council: corporators, office bearers and ward-wise seats/voters',
    publisher='Surat Municipal Corporation (Elected Wing; Election & Census Department)',
    url=CORP_URL,
    module='council',
    cadence='weekly',
    interval_hours=24 * 7,      # lists change only after elections, by-elections or office-bearer changes
    geo_note='SMC election wards (smc_ward, codes 1-30) and the SMC city area (totals row of the 2021 statement)',
    licence_note='Surat Municipal Corporation web pages; public information about elected representatives',
    notes=('Corporators: names and wards only, from Corp_list (2026-31 term; matches Gujarat Gazette Ex. 357 of '
           '28-04-2026). Party is not published on Corp_list and is not stored. Office bearers: designation, '
           'name, ward and official email only; residential addresses and mobile numbers printed on the page are '
           'deliberately not stored. Seats/voters: 2021 general election statement (roll as on 01-01-2021, '
           'population per Census 2011 on the 2020 ward limits); its ward numbers/names match the 2026 list '
           'one-to-one, but boundary identity between the 2021 and 2026 elections is not independently '
           'verified. The ward table counts 2 SC and 5 ST seats, while SMC\'s past-elections summary page says '
           '3 SC and 4 ST for 2021; the ward table is stored as published.'),
    metrics=(
        Metric('election.ward_population', 'Ward population (Census 2011, election-ward limits)', 'persons',
               'Population as per Census 2011 re-aggregated to the election-ward limits after the 2020 city-limit '
               'extension, as used for seat allotment. smc_city is the published total row.'),
        Metric('election.voters', 'Registered voters', 'voters',
               'Total voters on the electoral roll as on the period date. smc_city is the published total row.'),
        Metric('election.voters_by_gender', 'Registered voters by gender', 'voters',
               'Voters on the electoral roll as on the period date, by dims.gender (male, female, third_gender).'),
        Metric('election.seats', 'Council seats by reservation category', 'seats',
               'Seats allotted in the ward for the general election that used the electoral roll of the period '
               'date, by dims.category (general, sc, st, obc) and dims.women_reserved (yes = seat reserved for '
               'women, no = open seat). Counted from the per-seat allotment columns; all four seats of every ward '
               'are listed, so a 0 is a published fact, not a gap.'),
    ),
    record_types=('corporator', 'office_bearer'),
)

# Record attributes we are allowed to store; anything else (address, mobile, ...) is a bug.
ALLOWED_ATTRS = {
    'corporator': {'ward_no', 'ward_name', 'name', 'honorific'},
    'office_bearer': {'designation', 'name', 'honorific', 'ward_name', 'ward_no', 'email'},
}
OFFICIAL_EMAIL_DOMAINS = ('suratmunicipal.org', 'suratmunicipal.gov.in', 'gujarat.gov.in', 'gov.in', 'nic.in')

_HONORIFIC = re.compile(r'^(MRS|MR|MS|DR|SMT|SHRIMATI|SHRI|KUMARI|KUM|ADVOCATE|ADV)\.?(?=\s)\s*', re.I)
_MOBILE = re.compile(r'(?<!\d)(?:\+?91[\s-]?)?[6-9]\d{9}(?!\d)')


# ---------- fetch ----------

def fetch(ctx):
    """Fetch the three pages. A non-blocking failure on one page does not stop the others; the first failure
    is re-raised at the end so the run is still reported as failed. A block (403/429) stops immediately."""
    first_error = None
    for url, doc in DOCS:
        try:
            raw = ctx.get(url, meta={'doc': doc})
        except FetchError as e:
            if e.blocked:
                raise
            ctx.log.error('fetch failed for %s: %s', url, e)
            first_error = first_error or e
            continue
        yield raw
    if first_error is not None:
        raise first_error


def normalize(body: bytes) -> bytes:
    """Applied before a response is hashed and archived.

    - Corp_list carries an opaque per-row token (<input type="hidden" name="data" value="...">) used to POST
      to the detail page. It is not data; blank it so an unchanged list hashes as unchanged.
    - OfficeBearers prints each office bearer's residential address and personal mobile number. We never
      store them in the database, and we also keep them out of the raw archive.
    """
    body = re.sub(rb'(<input[^>]*?name="data"[^>]*?value=")[^"]*(")', rb'\1\2', body)
    body = re.sub(rb'(<input[^>]*?value=")[^"]*("[^>]*?name="data")', rb'\1\2', body)
    body = re.sub(rb'(<span[^>]*>\s*(?:Residential\s+Address|Mobile)\s*:\s*</span>)[^<]*', rb'\1 [removed]', body,
                  flags=re.I)
    return body


# ---------- parse ----------

def _doc_kind(raw: Raw) -> str:
    t = raw.text
    if re.search(r'Ward\s+wise\s+list\s+of\s+Corporators', t, re.I) and re.search(r'<h3[^>]*>\s*Ward\s+No', t, re.I):
        return 'corporators'
    if re.search(r'Statement\s+Showing\s+Situation\s+of\s+Seats', t, re.I):
        return 'wardwise_seats_voters'
    if '<h2>Mayor</h2>' in t or 'class="panel-heading">Mayor</div>' in t:   # old and Oct-2026 layouts
        return 'office_bearers'
    raise ValueError(f'unrecognised SMC council document ({raw.url}, meta={raw.meta}); page layout may have changed')


def parse(raw: Raw) -> Result:
    kind = _doc_kind(raw)
    expected = raw.meta.get('doc')
    if expected and expected != kind:
        raise ValueError(f'{raw.url}: expected the {expected} page but got the {kind} page')
    return {'corporators': _parse_corporators,
            'office_bearers': _parse_office_bearers,
            'wardwise_seats_voters': _parse_wardwise}[kind](raw)


def _slug(s: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def _split_honorific(full: str) -> tuple[str | None, str]:
    full = clean(full)
    m = _HONORIFIC.match(full)
    if not m:
        return None, full
    return clean(m.group(0)), full[m.end():].strip()


def _ward_key(s: str) -> str:
    return re.sub(r'[^a-z]', '', s.lower())


def _ratio(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, _ward_key(a), _ward_key(b)).ratio()


def ward_name_matches(n: int, name: str) -> bool:
    """True if `name` is a spelling of the 2026 name of ward n (and fits it better than any other ward)."""
    if n not in WARDS_2026:
        return False
    own = _ratio(name, WARDS_2026[n])
    other = max(_ratio(name, w) for k, w in WARDS_2026.items() if k != n)
    return own >= 0.8 and own > other


def ward_no_for_name(name: str) -> int | None:
    """Ward number for a ward name as printed on another SMC page, or None if not unambiguous."""
    key = _ward_key(name)
    for n, w in WARDS_2026.items():
        if _ward_key(w) == key:
            return n
    scored = sorted(((_ratio(name, w), n) for n, w in WARDS_2026.items()), reverse=True)
    if scored[0][0] >= 0.9 and scored[0][0] - scored[1][0] >= 0.05:
        return scored[0][1]
    return None


def _ward_geos() -> list[Geo]:
    return [Geo('smc_ward', str(n), name, 'smc_city', 'smc', note=WARD_NOTE) for n, name in WARDS_2026.items()]


def _parse_corporators(raw: Raw) -> Result:
    res = Result(geos=[SMC] + _ward_geos(), complete_record_types=('corporator',))
    text = raw.text
    for m in re.finditer(r'(?is)<h3[^>]*>(.*?)</h3>(.*?)</ul>', text):
        head = clean(re.sub(r'<[^>]+>', ' ', m.group(1)))
        hm = re.match(r'Ward\s*No\.?\s*(\d+)\s*(?:[-–:]\s*(.*))?$', head, re.I)
        if not hm:
            continue
        ward_no = int(hm.group(1))
        ward_name = clean(hm.group(2) or '')
        for b in re.finditer(r'(?is)<button\b[^>]*>(.*?)</button>', m.group(2)):
            honorific, name = _split_honorific(re.sub(r'<[^>]+>', ' ', b.group(1)))
            if not name:
                continue
            attrs = {'ward_no': str(ward_no), 'ward_name': ward_name, 'name': name}
            if honorific:
                attrs['honorific'] = honorific
            res.records.append(Record('corporator', f'ward-{ward_no}-{_slug(name)}', attrs))
    return res


def _deobfuscate_email(s: str) -> str:
    s = re.sub(r'\s*[\[(]\s*at\s*[\])]\s*', '@', s, flags=re.I)
    s = re.sub(r'\s*[\[(]\s*dot\s*[\])]\s*', '.', s, flags=re.I)
    return s.strip().lower()


def _official_email(s: str) -> str | None:
    e = _deobfuscate_email(s)
    m = re.fullmatch(r'[a-z0-9._%+-]+@([a-z0-9.-]+\.[a-z]{2,})', e)
    if not m:
        return None
    domain = m.group(1)
    if any(domain == d or domain.endswith('.' + d) for d in OFFICIAL_EMAIL_DOMAINS):
        return e
    return None


class _OfficeBearerPage(HTMLParser):
    """Collects [(designation, [(name, [lines])])] from the office-bearers page. Handles both layouts SMC has used:
      until Sep 2026: <h2>Mayor</h2> <h3>Name</h3> <p>Ward: ...</p>
      from Oct 2026:  <div class="panel-heading">Mayor</div> <div class="h3 mar-b20">Name</div> <p>Ward: ...</p>"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.sections: list[tuple[str, list]] = []
        self._kind = None          # what is being captured: 'heading', 'name' or 'line'
        self._end_tag = None
        self._buf: list[str] = []

    def handle_starttag(self, tag, attrs):
        if self._kind:
            self._buf.append(' ')
            return
        classes = (dict(attrs).get('class') or '').split()
        if tag == 'h2' or (tag == 'div' and 'panel-heading' in classes):
            self._kind, self._end_tag, self._buf = 'heading', tag, []
        elif tag == 'h3' or (tag == 'div' and 'h3' in classes):
            self._kind, self._end_tag, self._buf = 'name', tag, []
        elif tag == 'p' and self.sections and self.sections[-1][1]:
            self._kind, self._end_tag, self._buf = 'line', tag, []

    def handle_endtag(self, tag):
        if not self._kind:
            return
        if tag != self._end_tag:
            self._buf.append(' ')
            return
        text = ''.join(self._buf)
        if self._kind == 'heading':
            self.sections.append((clean(text), []))
        elif self._kind == 'name' and self.sections:
            self.sections[-1][1].append((text, []))
        elif self._kind == 'line':
            self.sections[-1][1][-1][1].append(clean(text))
        self._kind = None

    def handle_data(self, data):
        if self._kind:
            self._buf.append(data)


def _parse_office_bearers(raw: Raw) -> Result:
    res = Result(complete_record_types=('office_bearer',))
    text = raw.text
    start = text.find('contentblock')
    body = text[start:] if start >= 0 else text
    end = body.lower().find('<footer')
    if end >= 0:
        body = body[:end]
    page = _OfficeBearerPage()
    page.feed(body)
    page.close()
    for designation, people in page.sections:
        holders = []
        for raw_name, lines in people:
            honorific, name = _split_honorific(raw_name)
            if not name:
                continue
            attrs = {'designation': designation, 'name': name}
            if honorific:
                attrs['honorific'] = honorific
            # whitelist: only 'Ward' and 'Email' are read; address/mobile lines are skipped on purpose
            for line in lines:
                label, sep, value = line.partition(':')
                if not sep:
                    continue
                label, value = label.strip().lower(), value.strip()
                if label == 'ward' and value:
                    attrs['ward_name'] = value
                    n = ward_no_for_name(value)
                    if n is not None:
                        attrs['ward_no'] = str(n)
                elif label in ('email', 'e-mail', 'email id') and value:
                    e = _official_email(value)
                    if e:
                        attrs['email'] = e
            holders.append(attrs)
        for attrs in holders:
            key = _slug(designation) if len(holders) == 1 else f'{_slug(designation)}-{_slug(attrs["name"])}'
            res.records.append(Record('office_bearer', key, attrs))
    return res


def _last_updated(text: str) -> str | None:
    m = re.search(r'id="spnLastUpdated"[^>]*>\s*([^<]+?)\s*<', text)
    if not m:
        return None
    try:
        return datetime.strptime(clean(m.group(1)), '%B %d, %Y %I:%M %p').isoformat(timespec='minutes')
    except ValueError:
        return None


def _category(cell: str) -> str:
    k = re.sub(r'[^a-z]', '', cell.lower())
    if k not in _CATEGORY:
        raise ValueError(f'unknown seat reservation category {cell!r}')
    return _CATEGORY[k]


def _parse_wardwise(raw: Raw) -> Result:
    res = Result(geos=[SMC] + _ward_geos())
    as_of = _last_updated(raw.text)
    table = None
    for t in html_tables(raw.body):
        if t.find_row('ward no', 'total voters') >= 0:
            table = t
            break
    if table is None:
        raise ValueError('ward-wise seats/voters table not found')
    hdr_i = table.find_row('ward no', 'total voters')
    hdr = [h.lower() for h in table.rows[hdr_i]]

    col = {}
    seat_cols = []          # (column index, women_reserved)
    roll_dates = set()
    for j, h in enumerate(hdr):
        if re.match(r'\s*ward no', h):
            col['ward'] = j
        elif re.match(r'\s*ward name', h):
            col['name'] = j
        elif 'population' in h:
            col['population'] = j
        elif re.search(r'\b(first|second|third|fou?rth)\s+seat', h):
            seat_cols.append((j, 'yes' if re.search(r'reserved\s+for\s+(female|women)', h) else 'no'))
        elif 'voters' in h:
            dm = re.search(r'as on (?:date\s*)?(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})', h)
            if dm:
                roll_dates.add(parse_date(dm.group(1)).isoformat())
            if re.match(r'\s*female', h):
                col['female'] = j
            elif re.match(r'\s*male', h):
                col['male'] = j
            elif 'third gender' in h or 'other' in h:
                col['third_gender'] = j
            elif re.match(r'\s*total', h):
                col['total'] = j
    missing = {'ward', 'name', 'population', 'male', 'female', 'third_gender', 'total'} - set(col)
    if missing or len(seat_cols) != SEATS_PER_WARD:
        raise ValueError(f'unexpected header {table.rows[hdr_i]!r} (missing {sorted(missing)}, '
                         f'{len(seat_cols)} seat columns)')
    if len(roll_dates) != 1:
        raise ValueError(f'expected one electoral-roll date in the voter headers, got {sorted(roll_dates)}')
    roll = roll_dates.pop()
    census = '2011-03-01'   # Census 2011 reference date (00:00 hrs, 1 March 2011)

    def emit(metric, level, code, start, cell, dims=None):
        v = num(cell)
        res.observations.append(Obs(metric, level, code, start, start, value=v,
                                    status='reported' if v is not None else 'not_reported',
                                    dims=dims or {}, publisher_as_of=as_of))

    def numbers(level, code, row):
        emit('election.ward_population', level, code, census, row[col['population']])
        emit('election.voters', level, code, roll, row[col['total']])
        for g in ('male', 'female', 'third_gender'):
            emit('election.voters_by_gender', level, code, roll, row[col[g]], {'gender': g})

    for row in table.rows[hdr_i + 1:]:
        if len(row) < len(hdr):
            continue
        ward_cell, name_cell = row[col['ward']].strip(), row[col['name']].strip()
        if not ward_cell and not name_cell or re.match(r'(?i)total', ward_cell or name_cell):
            if any(row[col[k]].strip() for k in ('population', 'total')):
                numbers('smc_city', 'smc', row)       # published totals row
            continue
        n = int(num(ward_cell))
        code = str(n)
        if n not in WARDS_2026:
            raise ValidationError(f'ward number {n} is not one of the {N_WARDS} SMC wards')
        if not ward_name_matches(n, name_cell):
            raise ValidationError(f'ward {n} is named {name_cell!r} here but {WARDS_2026[n]!r} on the 2026 '
                                  'corporator list: ward numbering may differ, do not file it under smc_ward')
        numbers('smc_ward', code, row)
        counts = {(c, w): 0 for c in CATEGORIES for w in ('yes', 'no')}
        for j, women in seat_cols:
            if not row[j].strip():
                raise ValueError(f'ward {n}: blank seat allotment cell in column {j}')
            counts[(_category(row[j]), women)] += 1
        for (c, w), k in counts.items():
            res.observations.append(Obs('election.seats', 'smc_ward', code, roll, roll, value=float(k),
                                        dims={'category': c, 'women_reserved': w}, publisher_as_of=as_of))
    return res


# ---------- validate ----------

def validate(result: Result, raw: Raw) -> None:
    for r in result.records:
        extra = set(r.attrs) - ALLOWED_ATTRS[r.record_type]
        if extra:
            raise ValidationError(f'{r.record_type} {r.record_key}: attributes {sorted(extra)} are not allowed')
        for k, v in r.attrs.items():
            if isinstance(v, str) and _MOBILE.search(v):
                raise ValidationError(f'{r.record_type} {r.record_key}: {k} looks like a phone number; not stored')
    if 'corporator' in result.complete_record_types:
        _validate_corporators(result)
    if 'office_bearer' in result.complete_record_types:
        _validate_office_bearers(result)
    if result.observations:
        _validate_wardwise(result)


def _validate_corporators(result: Result) -> None:
    recs = [r for r in result.records if r.record_type == 'corporator']
    keys = [r.record_key for r in recs]
    if len(keys) != len(set(keys)):
        dup = sorted({k for k in keys if keys.count(k) > 1})
        raise ValidationError(f'duplicate corporator keys {dup}')
    by_ward: dict[int, list] = {}
    for r in recs:
        by_ward.setdefault(int(r.attrs['ward_no']), []).append(r)
    if sorted(by_ward) != list(range(1, N_WARDS + 1)):
        raise ValidationError(f'expected wards 1..{N_WARDS}, parsed {sorted(by_ward)}; page layout may have changed')
    for n, rs in by_ward.items():
        if not 1 <= len(rs) <= SEATS_PER_WARD:
            raise ValidationError(f'ward {n}: {len(rs)} corporators listed (expected at most {SEATS_PER_WARD})')
        name = rs[0].attrs['ward_name']
        if not ward_name_matches(n, name):
            raise ValidationError(f'ward {n} is now named {name!r} (was {WARDS_2026[n]!r}): possible '
                                  're-delimitation; review WARDS_2026 and the 2021 smc_ward mapping')
        for r in rs:
            nm = r.attrs['name']
            if re.search(r'\d', nm) or len(nm.split()) < 2 or len(nm) > 80:
                raise ValidationError(f'implausible corporator name {nm!r} in ward {n}')
    if not N_WARDS * SEATS_PER_WARD - 10 <= len(recs) <= N_WARDS * SEATS_PER_WARD:
        raise ValidationError(f'{len(recs)} corporators parsed; expected about {N_WARDS * SEATS_PER_WARD}')


def _validate_office_bearers(result: Result) -> None:
    recs = [r for r in result.records if r.record_type == 'office_bearer']
    if not 1 <= len(recs) <= 15:
        raise ValidationError(f'{len(recs)} office bearers parsed; page layout may have changed')
    if not any(r.attrs['designation'].strip().lower() == 'mayor' for r in recs):
        raise ValidationError('no Mayor found on the office bearers page')
    for r in recs:
        nm = r.attrs['name']
        if re.search(r'\d', nm) or len(nm.split()) < 2 or len(nm) > 80:
            raise ValidationError(f'implausible office-bearer name {nm!r} ({r.attrs["designation"]})')
        if 'ward_no' in r.attrs and not 1 <= int(r.attrs['ward_no']) <= N_WARDS:
            raise ValidationError(f'office bearer {nm!r}: ward {r.attrs["ward_no"]} out of range')


def _validate_wardwise(result: Result) -> None:
    obs = result.observations
    val = {(o.metric_id, o.geo_level, o.geo_code, o.dims.get('gender'), o.dims.get('category'),
            o.dims.get('women_reserved')): o.value for o in obs}
    wards = sorted({int(o.geo_code) for o in obs if o.geo_level == 'smc_ward'})
    if wards != list(range(1, N_WARDS + 1)):
        raise ValidationError(f'expected wards 1..{N_WARDS} in the seats/voters table, got {wards}')
    roll = {o.period_start for o in obs if o.metric_id == 'election.voters'}
    for d in roll:
        if not '1990-01-01' <= d <= '2100-01-01':
            raise ValidationError(f'absurd electoral-roll date {d}')
    total_seats = women_seats = 0
    for n in wards:
        c = str(n)
        seats = [o.value for o in obs if o.metric_id == 'election.seats' and o.geo_code == c]
        if sum(seats) != SEATS_PER_WARD:
            raise ValidationError(f'ward {n}: {sum(seats)} seats counted, expected {SEATS_PER_WARD}')
        total_seats += sum(seats)
        women_seats += sum(o.value for o in obs if o.metric_id == 'election.seats' and o.geo_code == c
                           and o.dims['women_reserved'] == 'yes')
        tot = val.get(('election.voters', 'smc_ward', c, None, None, None))
        parts = [val.get(('election.voters_by_gender', 'smc_ward', c, g, None, None))
                 for g in ('male', 'female', 'third_gender')]
        if tot is not None and not 10_000 <= tot <= 600_000:
            raise ValidationError(f'ward {n}: implausible voter count {tot}')
        if tot is not None and None not in parts and sum(parts) != tot:
            raise ValidationError(f'ward {n}: male+female+third gender = {sum(parts)} but total voters = {tot}')
        pop = val.get(('election.ward_population', 'smc_ward', c, None, None, None))
        if pop is not None and not 20_000 <= pop <= 600_000:
            raise ValidationError(f'ward {n}: implausible ward population {pop}')
    if women_seats * 2 < total_seats:
        raise ValidationError(f'only {women_seats} of {total_seats} seats reserved for women (law requires 50%)')
    # published totals row must equal the sum of the wards
    for metric, gender in (('election.ward_population', None), ('election.voters', None),
                           ('election.voters_by_gender', 'male'), ('election.voters_by_gender', 'female'),
                           ('election.voters_by_gender', 'third_gender')):
        city = val.get((metric, 'smc_city', 'smc', gender, None, None))
        if city is None:
            continue
        s = sum(val.get((metric, 'smc_ward', str(n), gender, None, None)) or 0 for n in wards)
        if s != city:
            raise ValidationError(f'{metric} {gender or ""}: wards sum to {s} but the total row says {city}')
