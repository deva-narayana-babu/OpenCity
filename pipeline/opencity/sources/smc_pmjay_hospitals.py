"""PM-JAY (Ayushman Bharat / PMJAY-MA) empanelled hospitals in Surat, from SMC's list: directory and counts.

Publisher: Surat Municipal Corporation, Health Department (PM-JAY section of the SMC site; the menu link is labelled
"Enrollment Hosptials" under Departments > Health > PM-JAY). The list itself comes from the PM-JAY / MA Yojana
(Mukhyamantri Amrutam) scheme run by the National Health Authority and Gujarat's State Health Agency.

Endpoint: one plain GET of a PDF, no parameters, no login or captcha (robots.txt on www.suratmunicipal.gov.in
returns 404, so nothing is disallowed):

    https://www.suratmunicipal.gov.in/Content/Documents/Departments/PMJAY/PMJAYHospitals.pdf

Response layout: a 12-page landscape text PDF exported from Excel ("SURAT MUNICIPAL CORPORATION / PMJAY-MA YOJNA
AYUSHMAN BHARAT / EMPANALLED HOSPITAL LIST"), one table with no column header row:

    Sr | Hospital name | PM-JAY hospital ID | State | District | Address | Contact person | Mobile | Specialities

Cells wrap over several lines and are centred vertically, so the lines of neighbouring rows interleave in a plain
text dump. parse() therefore runs `pdftotext -raw -bbox`, which lists every word with its position in the order
the PDF draws it. Excel draws the table row by row and cell by cell, so a row is "a serial number and every word
after it until the next serial number"; the word's x position gives its column (left edges in COLUMNS). Words in
larger type (the 16 and 24 pt title) are skipped. The Contact person and Mobile columns name individual staff and
their mobile numbers: they are never read or stored.

Records -> one 'pmjay_hospital' per row, keyed by the PM-JAY hospital ID in lower case ('hosp24t123955'), or by
'name-<slug>' for the one row printed without an ID (Baps Pramukh Swami Hospital). The PDF is the complete list,
so hospitals that drop off it get closed. Attributes:
    serial_no          the row number as printed (no row carries 33 or 42, so 1-83 holds 81 rows)
    name               hospital name as printed (two different hospitals are both "Lifeline Multispeciality Hospital")
    pmjay_id           hospital ID as printed: 'HOSP24<letter><digits>' or the older 'HS24<digits>' form, or None
    state, district    as printed (always "Gujarat" / "Surat"; validate() insists on it)
    address            the hospital's address as printed
    specialities       the speciality cell split at commas, as extracted. Excel wraps long words mid-word, which
                       leaves stray spaces ("Orthopae dics", "Polytraum a"); duplicates ("Dialysis,Dialysis") kept.
    speciality_groups  the SPECIALITY_GROUPS slugs found in the specialities (sorted), see below.

Observations, filed under surat_district (the District column says Surat for every row; several hospitals are
outside the SMC area, e.g. Bardoli, Kim, Kamrej, Kadodara, Vankal):
    pmjay.listed_hospitals          number of hospitals on the list (rows).
    pmjay.hospitals_by_speciality   number of listed hospitals whose speciality text falls in dims.speciality.
        The speciality text is free text with many spellings, so each item is lower-cased, spaces and hyphens are
        removed, and it is put in every group whose stem it contains (SPECIALITY_GROUPS; e.g. 'paediatriccancer'
        counts under oncology and paediatrics), or in the group its exact text names (EXACT_GROUPS: 'ent',
        'urology', 'generalmedicine', 'generalsurgery', which are substrings of other words). Items such as
        "Medical Management" and "High end Medicine" fit no group and are only kept on the record. Every group is
        emitted, so 0 means no listed hospital mentions it. This is a count of what SMC's list says, not of the
        packages each hospital is actually empanelled for.
Both are instant readings on the PDF's creation date (PDF metadata CreationDate, 2024-06-27 in the snapshot); the
document prints no date of its own. A replaced PDF gets a new date and starts a new point.

Snapshot 2026-10-24 (PDF created 2024-06-27): 81 hospitals (serials 1-83 without 33 and 42).

Caveats: this is SMC's citizen-facing list, dated mid-2024; it need not match the National Health Authority's
current hospital register for Surat. There is no ownership column, and the letter in the ID is not decoded. The raw archive keeps
the PDF as published (with the contact columns); the test fixture is the pdftotext word list of pages 1-2 with
those two columns removed.

Geography: Surat district. Cadence: static (replaced without schedule); checked weekly.
Licence: Surat Municipal Corporation web document; public information; no explicit open-data licence.
"""
from __future__ import annotations

import html
import subprocess
import tempfile

from ..model import Metric, Obs, Raw, Record, Result, Source, ValidationError
from ..parse import clean
from ..surat import SURAT_DISTRICT

URL = 'https://www.suratmunicipal.gov.in/Content/Documents/Departments/PMJAY/PMJAYHospitals.pdf'

# (left edge in pt, column): a word belongs to the last column whose left edge is <= the word's xMin.
COLUMNS = (
    (0, 'sr'), (70, 'name'), (215, 'pmjay_id'), (305, 'state'), (360, 'district'),
    (410, 'address'), (562, 'contact_person'), (665, 'mobile'), (738, 'specialities'))
PERSONAL = ('contact_person', 'mobile')     # never read
BODY_TEXT_MAX_HEIGHT = 13                   # body text is 11.1 pt high; the title lines are 16 and 24 pt

# stem -> group: an item (lower case, no spaces or hyphens) is in every group whose stem it contains
SPECIALITY_GROUPS = (
    ('cardiology', 'cardiology'),
    ('cardiothora', 'cardiothoracic_surgery'),      # Cardio Thoracic Surgery, CardioThoracic Vascular, THORASIC
    ('oncology', 'oncology'), ('cancer', 'oncology'),   # medical / surgical / radiation oncology, paediatric cancer
    ('nephrology', 'nephrology_dialysis'), ('dialysis', 'nephrology_dialysis'),
    ('genitourinary', 'urology'),
    ('neurology', 'neurology'),
    ('neurosurgery', 'neurosurgery'),
    ('orthop', 'orthopaedics'),                     # Orthopaedics, ORTHOPEDIC
    ('jointrepla', 'joint_replacement'),            # also the misspelt "Joint Replasment"
    ('trauma', 'polytrauma'), ('truma', 'polytrauma'),  # Polytrauma, Trauma, "POLY TRUMA"
    ('gyn', 'obstetrics_gynaecology'), ('obst', 'obstetrics_gynaecology'),  # incl. "Gyneac and Obstrec"
    ('paediatric', 'paediatrics'), ('pediatric', 'paediatrics'), ('pedicatric', 'paediatrics'),
    ('neonat', 'neonatal'),                         # Neonatology, Neo-natal care Packages, NEONATAL
    ('ophthalm', 'ophthalmology'),
    ('otorhinolaryngology', 'ent'),
    ('pulmonology', 'pulmonology'),
    ('criticalcare', 'critical_care'),
    ('emergency', 'emergency_medicine'),
    ('dental', 'dental'),
    ('burns', 'burns_plastic_surgery'), ('plastic', 'burns_plastic_surgery'),
)
# whole-item names whose text is part of other words ('ent' in 'treatment', 'urology' in 'neurology')
EXACT_GROUPS = {'ent': 'ent', 'urology': 'urology', 'generalmedicine': 'general_medicine',
                'generalsurgery': 'general_surgery'}
GROUPS = tuple(dict.fromkeys([g for _, g in SPECIALITY_GROUPS] + list(EXACT_GROUPS.values())))

SOURCE = Source(
    id='smc_pmjay_hospitals',
    name='PM-JAY empanelled hospitals in Surat (SMC list)',
    publisher='Surat Municipal Corporation, Health Department (PM-JAY / MA Yojana hospital list)',
    url=URL,
    module='health',
    cadence='static',
    interval_hours=24 * 7,          # the PDF is replaced without schedule; weekly is plenty
    record_types=('pmjay_hospital',),
    geo_note='Surat district (the list\'s District column; includes hospitals outside the SMC area)',
    licence_note='Surat Municipal Corporation web document; public information (no explicit open-data licence)',
    notes=('Parsed from the word positions (pdftotext -raw -bbox) because cells wrap over several lines. The '
           'contact-person and mobile columns are personal data and are never read. Speciality counts group the '
           'free-text speciality cell by keyword stems (see the module documentation). Dated to the PDF creation '
           'date; the document prints no date.'),
    metrics=(
        Metric('pmjay.listed_hospitals', 'Hospitals on SMC\'s PM-JAY empanelled list', 'hospitals',
               'Number of hospitals (rows) on SMC\'s PMJAY-MA Yojana Ayushman Bharat empanelled hospital list for '
               'Surat. Instant reading on the PDF creation date. SMC\'s list, not the full NHA register.'),
        Metric('pmjay.hospitals_by_speciality', 'Listed PM-JAY hospitals by speciality', 'hospitals',
               'Number of hospitals on the list whose speciality cell mentions dims.speciality. The free-text '
               'items are grouped by keyword stems (e.g. oncology = medical, surgical or radiation oncology or '
               'paediatric cancer; nephrology_dialysis = nephrology or dialysis; urology = urology or '
               'genitourinary surgery). A hospital counts once per group. Instant reading on the PDF creation date.'),
    ),
)


def fetch(ctx):
    yield ctx.get(URL)


def bbox_text(pdf: bytes) -> str:
    """Word list of the PDF in drawing order: `pdftotext -raw -bbox` (XHTML, one <word> per line)."""
    with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp:
        tmp.write(pdf)
        tmp.flush()
        try:
            r = subprocess.run(['pdftotext', '-raw', '-bbox', tmp.name, '-'], capture_output=True, timeout=300)
        except FileNotFoundError:
            raise RuntimeError('pdftotext not found: install poppler-utils') from None
    if r.returncode != 0:
        raise RuntimeError(f'pdftotext failed: {r.stderr.decode(errors="replace")[:300]}')
    return r.stdout.decode('utf-8', errors='replace')


def _words(xml: str):
    """Yield (xMin, height, text) per word line, e.g.
    '<word xMin="44.2" yMin="174.3" xMax="49.8" yMax="185.4">1</word>' -> (44.2, 11.1, '1')."""
    for line in xml.splitlines():
        line = line.strip()
        if line.startswith('<word '):
            q = line.split('"')     # ['<word xMin=', '44.2', ' yMin=', '174.3', ' xMax=', '49.8', ' yMax=', '185.4', '>1</word>']
            yield float(q[1]), float(q[7]) - float(q[3]), html.unescape(q[8][1:-len('</word>')])


def _column(x: float) -> str:
    return [name for edge, name in COLUMNS if x >= edge][-1]


def _created(xml: str) -> str:
    """'<meta name="CreationDate" content="2024-06-27T14:00:22+05:30"/>' -> '2024-06-27'."""
    tag = '<meta name="CreationDate" content="'
    i = xml.find(tag)
    if i < 0:
        raise ValueError('the PDF has no CreationDate; cannot date the list')
    return xml[i + len(tag):i + len(tag) + 10]


def _slug(s: str) -> str:
    out = ''.join(ch if ch.isalnum() else ' ' for ch in s.lower())
    return '-'.join(out.split())


def speciality_groups(items: list[str]) -> list[str]:
    found = set()
    for item in items:
        key = item.lower().replace(' ', '').replace('-', '')
        found |= {group for stem, group in SPECIALITY_GROUPS if stem in key}
        if key in EXACT_GROUPS:
            found.add(EXACT_GROUPS[key])
    return sorted(found)


def parse(raw: Raw) -> Result:
    return parse_bbox(bbox_text(raw.body))


def parse_bbox(xml: str) -> Result:
    """Parse the `pdftotext -raw -bbox` word list (parse() makes it from the PDF; the test fixture is one)."""
    day = _created(xml)
    rows: list[dict] = []
    for x, height, text in _words(xml):
        if height > BODY_TEXT_MAX_HEIGHT:
            continue
        col = _column(x)
        if col == 'sr':
            if not text.isdigit():
                raise ValueError(f'unexpected text {text!r} in the serial-number column')
            rows.append({'sr': text})
        elif col not in PERSONAL:
            if not rows:
                raise ValueError(f'text {text!r} before the first serial number')
            rows[-1].setdefault(col, []).append(text)

    res = Result(geos=[SURAT_DISTRICT], complete_record_types=('pmjay_hospital',))
    per_group = {g: 0 for g in GROUPS}
    for row in rows:
        ids = row.get('pmjay_id', [])
        if len(ids) > 1:
            raise ValueError(f'row {row["sr"]}: several hospital IDs {ids}; rows ran together')
        name = ' '.join(row.get('name', []))
        items = [clean(i) for i in ' '.join(row.get('specialities', [])).split(',') if clean(i)]
        groups = speciality_groups(items)
        for g in groups:
            per_group[g] += 1
        pmjay_id = ids[0] if ids else None
        res.records.append(Record('pmjay_hospital', pmjay_id.lower() if pmjay_id else f'name-{_slug(name)}', {
            'serial_no': row['sr'],
            'name': name,
            'pmjay_id': pmjay_id,
            'state': ' '.join(row.get('state', [])),
            'district': ' '.join(row.get('district', [])),
            'address': ' '.join(row.get('address', [])),
            'specialities': items,
            'speciality_groups': groups,
        }))

    geo = ('surat_district', 'surat', day, day)
    res.observations.append(Obs('pmjay.listed_hospitals', *geo, value=float(len(rows)), publisher_as_of=day))
    for g, n in per_group.items():
        res.observations.append(Obs('pmjay.hospitals_by_speciality', *geo, value=float(n),
                                    dims={'speciality': g}, publisher_as_of=day))
    return res


def validate(result: Result, raw: Raw) -> None:
    recs = result.records
    if not 50 <= len(recs) <= 400:
        raise ValidationError(f'{len(recs)} hospitals parsed; expected about 80 (PDF layout may have changed)')
    names = set()
    for r in recs:
        a = r.attrs
        if (a['state'], a['district']) != ('Gujarat', 'Surat'):
            raise ValidationError(f'row {a["serial_no"]}: state/district {a["state"]!r}/{a["district"]!r}, '
                                  'expected Gujarat/Surat (columns may have moved)')
        if a['pmjay_id'] is not None and not a['pmjay_id'].startswith(('HOSP24', 'HS24')):
            raise ValidationError(f'row {a["serial_no"]}: {a["pmjay_id"]!r} is not a Gujarat PM-JAY hospital ID')
        if len(a['name']) < 4 or len(a['address']) < 4 or not a['specialities']:
            raise ValidationError(f'row {a["serial_no"]}: missing name, address or specialities')
        names.add((a['name'], a['address']))
    if len(names) != len(recs):
        raise ValidationError('the same hospital appears twice')
    with_group = sum(1 for r in recs if r.attrs['speciality_groups'])
    if with_group < 0.9 * len(recs):
        raise ValidationError(f'only {with_group} of {len(recs)} hospitals have a recognised speciality')
    day = result.observations[0].period_start
    if day < '2018-09-23' or (raw is not None and raw.retrieved_at and day > raw.retrieved_at[:10]):
        raise ValidationError(f'PDF date {day} is before PM-JAY began or after the fetch')
