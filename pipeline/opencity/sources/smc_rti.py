"""SMC Right to Information statistics: Gujarat RTI annual returns and the Patrak-7 / Patrak-8 quarterly returns.

Surat Municipal Corporation, as one public authority under the RTI Act 2005, publishes three kinds of return.
Every figure describes SMC as a whole, so everything is filed under geo smc_city/smc.

1. ANNUAL RETURNS, one PDF per year, listed on https://www.suratmunicipal.gov.in/Downloads/Acts/RTI_ActAnnualReturn
   ("Gujarat State RTI Annual Return - Year 2025 to 2026", 20 links back to 2005-07). Each is a one-page copy of
   the state's "Annual Return Form" (rti-ar.gujarat.gov.in), in English, always with the same fields:
       Public Authority : Surat Municipal Corporation      Year: 2025-2026
       row "Requests":      Opening Balance as on April 1st | Received during the Period (including cases
                            transferred to other Public Authority) | No. of cases transferred |
                            Decisions where requests/appeals rejected | Decisions where requests/appeals
                            accepted (*including partially rejected cases)
       row "First Appeals": the same columns without "transferred"
       No. of Cases where disciplinary action taken against any Officer
       No. of APIOs / PIOs / AAs designated
       No. of times various provisions were invoked while rejecting requests:
                            Section 8(1)(a)..(j), Sections 9, 11, 24, Other
       Amount of Charges Collected (in Rs.): Registration Fee Amount | Additional Fee & Any other charges |
                            Penalties Amount: Levied | Collected | Total
   The files come in four physical layouts: Chrome/Firefox/Foxit printouts of the web form (2019-20 onward) and
   Word re-typings of it (2005-07 .. 2014-15). Five years (2015-16, 2016-17, 2017-18, 2018-19, 2021-22) are
   image-only scans with no text layer; they cannot be read without OCR, so they are not downloaded
   (SCANNED_RETURNS) and those years have no rti.annual.* data.
   The parser works on word coordinates (pdftotext -bbox): a number belongs to the field whose header word is
   nearest, so a blank field becomes 'not_reported' instead of shifting its neighbours. Because every field of
   this form is always filled in (0 when nothing happened), more than two blank fields is treated as a layout
   the parser does not understand and the document is rejected rather than stored half-empty.
   -> rti.annual.* observations, period = the return's year (1 April .. 31 March; 2005-07 spans two years).
   The index page itself -> one 'rti_annual_return' record per linked PDF (title, url, years).

2. PATRAK-7 ("પત્રક-7"), the quarterly return of RTI applications received/disposed of by the PIOs, and
3. PATRAK-8 ("પત્રક-8"), the same for first appeals received/disposed of by the appellate authorities:
   https://www.suratmunicipal.gov.in/Content/Documents/rtiact/other/patrak-7.pdf and .../patrak-8.pdf, linked
   from https://www.suratmunicipal.gov.in/Information/RTI/RTI_ReportsCirculars. Both are overwritten in place
   every quarter; the raw archive keeps every version and each version lands on its own quarter period.
   They are Excel printouts whose Gujarati text uses a legacy (non-Unicode) font, so pdftotext returns ASCII
   gibberish for the labels (e.g. "l+DF;GL X~VFTDF\\ VUFpGL 50TZ VZHLVM" = ત્રિમાસની શરૂઆતમાં અગાઉની પડતર અરજીઓ).
   The numbers are ordinary digits. Rows are identified by their serial-number cell (also legacy font:
   "!"=1 "Z"=2 "#"=3 "$"=4 "5"=5 "&"=6 "*"=7 "("=8 ")"=9 "_"=0, ")sVf"=9(અ)), and the full sequence of serial
   numbers must equal the documented row lists P7_ROWS / P8_ROWS below, which say what each row means.
   Value columns: BPL applicants | other applicants | total (dims.applicants = bpl | non_bpl | all), located
   from the header row and the rows that have all three values. The quarter is read from the printed range
   "તા. 01/01/26 થી તા. 31/03/26" (legacy: "TFP _!q_!qZ& YL TFP #!q_#qZ&"), must be an exact financial-year
   quarter, and is cross-checked with the printed financial year ("નાણાંકીય વર્ષ : 2025 - 26").
   -> rti.quarterly.* observations, period = the quarter (Patrak-7 rows 13d and 14 cover the part of the
   financial year they describe).
   Layout differences handled (both checked against the live files, 2026-10-05, Q4 FY2025-26): Patrak-7 values
   are right-aligned and BPL cells are often left blank (-> not_reported); Patrak-8 values are centred, every
   cell is filled (0 printed), row 7(a)'s label wraps so its values sit one line below its serial number, and
   the row-9 heading runs on across the value columns. Any other text that starts inside the value columns
   ("1,234/-", "12 (a)") raises instead of being dropped as a blank.

publisher_as_of is the PDF's creation date (for the browser printouts it equals the printed date).

Validation (validate()): counts are whole numbers <= 200,000 and rupee amounts <= 1 crore; no period starts
before the RTI Act (2005) or after the fetch date. Annual: at most two blank fields, and transferred + rejected
+ accepted <= opening balance + received for requests and for first appeals. Quarterly (total column): the
form's own identities (row 1 + 2 = 3; 4 + 6 + 7 + 8 = 9 for Patrak-7, 4 + 5 + 6 = 7 for Patrak-8; 3 - disposed =
pending at end; disposed within time <= disposed; sections sum to their printed total), and BPL + other = total
on every count row where all three are printed. These identities are what proves that the position-mapped
rows (labels unreadable) landed on the right metrics.

The annual return and the quarterly returns are separate metric families on purpose: they are compiled
separately and do not reconcile (FY2025-26 annual return: 5,875 requests pending on 1 April 2025 and Rs 2,62,471
fees+charges for the year; Patrak-7 Q4 FY2025-26: Rs 4,29,678 "income in the year to date"). Never sum or splice
rti.annual.* with rti.quarterly.*.
"""
from __future__ import annotations

import html as htmllib
import re
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import date, timedelta

from ..model import Metric, Obs, Raw, Record, Result, Source, ValidationError
from ..parse import clean, links, quarter_of_fy
from ..surat import SMC

INDEX_URL = 'https://www.suratmunicipal.gov.in/Downloads/Acts/RTI_ActAnnualReturn'
PATRAK7_URL = 'https://www.suratmunicipal.gov.in/Content/Documents/rtiact/other/patrak-7.pdf'
PATRAK8_URL = 'https://www.suratmunicipal.gov.in/Content/Documents/rtiact/other/patrak-8.pdf'

# Annual returns published only as image scans (re-checked 2026-10-05: each is one page holding one embedded
# image and no text layer; three are "EPSON Scan" output). They are not downloaded on refresh: nothing in them can
# be parsed without OCR. If SMC ever replaces one with a text PDF, remove it from this set.
SCANNED_RETURNS = frozenset({'2015-2016', '2016-2017', '2017-2018', '2018-2019', '2021-2022'})

# Section 8(1) clauses and the other sections, as printed on all three forms (dims.section)
SECTIONS = ('8(1)(a)', '8(1)(b)', '8(1)(c)', '8(1)(d)', '8(1)(e)', '8(1)(f)', '8(1)(g)', '8(1)(h)',
            '8(1)(i)', '8(1)(j)', '9', '11', '24', 'other')
COLUMNS = ('bpl', 'non_bpl', 'all')

_A = 'Annual return (Gujarat State RTI Annual Return form), SMC as a whole. '
_P7 = 'Patrak-7 quarterly return (applications to PIOs), SMC as a whole. '
_P8 = 'Patrak-8 quarterly return (first appeals to appellate authorities), SMC as a whole. '
_COLS = (' Split by applicant category in dims.applicants: bpl (Below Poverty Line applicants), '
         'non_bpl (the "other" column) and all (the printed total column).')

METRICS = (
    # ---- annual return ----
    Metric('rti.annual.requests_opening_balance', 'RTI requests pending at start of year', 'requests',
           _A + 'Requests pending at the start of the year ("Opening Balance as on April 1st").'),
    Metric('rti.annual.requests_received', 'RTI requests received', 'requests',
           _A + 'Requests received during the year, including cases then transferred to another public authority '
                '("Received during the Period (including cases transferred to other Public Authority)").'),
    Metric('rti.annual.requests_transferred', 'RTI requests transferred to other authorities', 'requests',
           _A + 'Requests transferred to another public authority during the year ("No. of cases transferred").'),
    Metric('rti.annual.requests_rejected', 'RTI requests rejected', 'requests',
           _A + 'Decisions during the year where requests were rejected.'),
    Metric('rti.annual.requests_accepted', 'RTI requests accepted', 'requests',
           _A + 'Decisions during the year where requests were accepted, including partially rejected cases.'),
    Metric('rti.annual.first_appeals_opening_balance', 'RTI first appeals pending at start of year', 'appeals',
           _A + 'First appeals (to SMC\'s own appellate authorities) pending at the start of the year.'),
    Metric('rti.annual.first_appeals_received', 'RTI first appeals received', 'appeals',
           _A + 'First appeals received during the year.'),
    Metric('rti.annual.first_appeals_rejected', 'RTI first appeals rejected', 'appeals',
           _A + 'Decisions during the year where first appeals were rejected.'),
    Metric('rti.annual.first_appeals_accepted', 'RTI first appeals accepted', 'appeals',
           _A + 'Decisions during the year where first appeals were accepted, including partially rejected cases.'),
    Metric('rti.annual.disciplinary_actions', 'Disciplinary actions against officers under RTI', 'cases',
           _A + 'Cases during the year where disciplinary action was taken against any officer.'),
    Metric('rti.annual.apios_designated', 'Assistant PIOs designated', 'officers',
           _A + 'Number of Assistant Public Information Officers (APIOs) designated, as filed for the year.'),
    Metric('rti.annual.pios_designated', 'Public Information Officers designated', 'officers',
           _A + 'Number of Public Information Officers (PIOs) designated, as filed for the year.'),
    Metric('rti.annual.aas_designated', 'Appellate Authorities designated', 'officers',
           _A + 'Number of first Appellate Authorities (AAs) designated, as filed for the year.'),
    Metric('rti.annual.rejections_by_section', 'RTI exemptions invoked when rejecting requests', 'times',
           _A + 'Number of times each provision of the RTI Act was invoked while rejecting requests during the '
                'year (dims.section: 8(1)(a)..8(1)(j), 9, 11, 24, other). One rejection can invoke several, so '
                'the sum can exceed rti.annual.requests_rejected.'),
    Metric('rti.annual.registration_fees_rs', 'RTI registration (application) fees collected', 'Rs',
           _A + '"Registration Fee Amount" collected during the year, in rupees.'),
    Metric('rti.annual.additional_fees_rs', 'RTI additional fees and other charges collected', 'Rs',
           _A + '"Additional Fee & Any other charges" (copying charges etc.) collected during the year, in rupees.'),
    Metric('rti.annual.penalties_levied_rs', 'RTI penalties levied', 'Rs',
           _A + 'Penalties amount "Levied" during the year, in rupees.'),
    Metric('rti.annual.penalties_collected_rs', 'RTI penalties collected', 'Rs',
           _A + 'Penalties amount "Collected" during the year, in rupees.'),
    Metric('rti.annual.penalties_total_rs', 'RTI penalties total (as printed)', 'Rs',
           _A + 'The penalties "Total" field printed after Levied and Collected, in rupees, stored as printed '
                '(the form does not say how it is computed).'),
    # ---- Patrak-7 ----
    Metric('rti.quarterly.requests_pending_start', 'RTI applications pending at start of quarter', 'applications',
           _P7 + 'Row 1: applications pending from earlier, at the start of the quarter.' + _COLS),
    Metric('rti.quarterly.requests_received', 'RTI applications received in quarter', 'applications',
           _P7 + 'Row 2: applications received during the quarter.' + _COLS),
    Metric('rti.quarterly.requests_total', 'RTI applications on hand in quarter', 'applications',
           _P7 + 'Row 3: total applications (row 1 + row 2).' + _COLS),
    Metric('rti.quarterly.requests_transferred_wholly', 'RTI applications wholly transferred', 'applications',
           _P7 + 'Row 4: applications wholly transferred to another public authority during the quarter.' + _COLS),
    Metric('rti.quarterly.requests_transferred_partly', 'RTI applications partly transferred', 'applications',
           _P7 + 'Row 5: applications partly transferred to another public authority during the quarter '
                 '(not counted in row 9).' + _COLS),
    Metric('rti.quarterly.requests_info_supplied', 'RTI applications answered in full', 'applications',
           _P7 + 'Row 6: applications where the information was supplied in full.' + _COLS),
    Metric('rti.quarterly.requests_refused_fully', 'RTI applications refused in full', 'applications',
           _P7 + 'Row 7: applications where the information was refused in full.' + _COLS),
    Metric('rti.quarterly.requests_refused_partly', 'RTI applications refused in part', 'applications',
           _P7 + 'Row 8: applications where the information was partly refused.' + _COLS),
    Metric('rti.quarterly.requests_disposed', 'RTI applications disposed of in quarter', 'applications',
           _P7 + 'Row 9: total applications disposed of during the quarter (rows 4 + 6 + 7 + 8).' + _COLS),
    Metric('rti.quarterly.requests_disposed_within_time', 'RTI applications disposed of within time limit',
           'applications',
           _P7 + 'Row 9(a): of the applications disposed of (row 9), those disposed of within the statutory time '
                 'limit.' + _COLS),
    Metric('rti.quarterly.requests_pending_end', 'RTI applications pending at end of quarter', 'applications',
           _P7 + 'Row 10: applications pending at the end of the quarter (row 3 - row 9).' + _COLS),
    Metric('rti.quarterly.refusals_by_section', 'RTI exemptions invoked in refusals (quarter)', 'times',
           _P7 + 'Rows 11(a)-(n): number of the refusals in rows 7 and 8 made under each section of the Act '
                 '(dims.section: 8(1)(a)..8(1)(j), 9, 11, 24, other).' + _COLS),
    Metric('rti.quarterly.refusals_total', 'RTI refusals by section, total (quarter)', 'times',
           _P7 + 'Row 12: total of rows 11(a) to 11(n).' + _COLS),
    Metric('rti.quarterly.application_fees_rs', 'RTI application fees received in quarter', 'Rs',
           _P7 + 'Row 13(a): application fees received during the quarter (cash or other forms), excluding '
                 'applications received on transfer from other authorities, in rupees.' + _COLS),
    Metric('rti.quarterly.other_charges_rs', 'RTI charges other than application fee (quarter)', 'Rs',
           _P7 + 'Row 13(b): charges other than the application fee (copying charges etc.) received during the '
                 'quarter, in rupees.' + _COLS),
    Metric('rti.quarterly.income_rs', 'RTI fee and charges income in quarter', 'Rs',
           _P7 + 'Row 13(c): total income during the quarter (13a + 13b), in rupees.' + _COLS),
    Metric('rti.quarterly.income_earlier_in_fy_rs', 'RTI income earlier in the financial year', 'Rs',
           _P7 + 'Row 13(d): total income in the earlier part of the current financial year, in rupees. The '
                 'observation period is that part (1 April to the day before the quarter); not emitted for Q1. '
                 'Stored as printed: in Q4 FY2025-26 the non_bpl (193828) and all (363873) columns disagree.' + _COLS),
    Metric('rti.quarterly.income_fy_to_date_rs', 'RTI income in financial year to date', 'Rs',
           _P7 + 'Row 14: total income from 1 April to the end of the quarter (13c + 13d), in rupees; the '
                 'observation period is that span.' + _COLS),
    Metric('rti.quarterly.pios', 'Public Information Officers (Patrak-7 header)', 'officers',
           _P7 + 'Total number of Public Information Officers printed in the return header for the quarter.'),
    # ---- Patrak-8 ----
    Metric('rti.quarterly.first_appeals_pending_start', 'RTI first appeals pending at start of quarter', 'appeals',
           _P8 + 'Row 1: first appeals pending from earlier, at the start of the quarter.' + _COLS),
    Metric('rti.quarterly.first_appeals_received', 'RTI first appeals received in quarter', 'appeals',
           _P8 + 'Row 2: first appeals received during the quarter.' + _COLS),
    Metric('rti.quarterly.first_appeals_total', 'RTI first appeals on hand in quarter', 'appeals',
           _P8 + 'Row 3: total appeals (row 1 + row 2).' + _COLS),
    Metric('rti.quarterly.first_appeals_allowed', 'RTI first appeals allowed in full', 'appeals',
           _P8 + 'Row 4: appeals fully allowed (અપીલ સંપૂર્ણ મંજૂર).' + _COLS),
    Metric('rti.quarterly.first_appeals_partly_allowed', 'RTI first appeals partly allowed', 'appeals',
           _P8 + 'Row 5: appeals partly allowed and partly rejected.' + _COLS),
    Metric('rti.quarterly.first_appeals_rejected', 'RTI first appeals rejected in full', 'appeals',
           _P8 + 'Row 6: appeals fully rejected (અપીલ સંપૂર્ણ નામંજૂર).' + _COLS),
    Metric('rti.quarterly.first_appeals_disposed', 'RTI first appeals disposed of in quarter', 'appeals',
           _P8 + 'Row 7: total appeals disposed of during the quarter (rows 4 + 5 + 6).' + _COLS),
    Metric('rti.quarterly.first_appeals_disposed_within_time', 'RTI first appeals disposed of within time limit',
           'appeals',
           _P8 + 'Row 7(a): of the appeals disposed of (row 7), those disposed of within the time limit of '
                 'section 19(6).' + _COLS),
    Metric('rti.quarterly.first_appeals_pending_end', 'RTI first appeals pending at end of quarter', 'appeals',
           _P8 + 'Row 8: appeals pending at the end of the quarter (row 3 - row 7).' + _COLS),
    Metric('rti.quarterly.first_appeal_refusals_by_section', 'RTI exemptions upheld in first appeals (quarter)',
           'times',
           _P8 + 'Rows 9(a)-(n): number of the appeals in rows 5 and 6 where the information asked for was refused, '
                 'by section of the Act (dims.section: 8(1)(a)..8(1)(j), 9, 11, 24, other). The printed label of '
                 'row (h) repeats clause (g) (a typo on the form); it is stored by position as 8(1)(h).' + _COLS),
    Metric('rti.quarterly.first_appeal_refusals_total', 'RTI exemptions upheld in first appeals, total', 'times',
           _P8 + 'Row 10: total of rows 9(a) to 9(n).' + _COLS),
    Metric('rti.quarterly.appellate_authorities', 'Appellate authorities (Patrak-8 header)', 'officers',
           _P8 + 'Total number of appellate officers printed in the return header for the quarter.'),
)

SOURCE = Source(
    id='smc_rti',
    name='SMC Right to Information returns (annual returns, quarterly Patrak-7 and Patrak-8)',
    publisher='Surat Municipal Corporation, RTI Cell',
    url='https://www.suratmunicipal.gov.in/Downloads/Acts/RTI_Act',
    module='rti',
    cadence='quarterly',
    interval_hours=24 * 7,      # Patrak-7/8 are replaced once a quarter with an unknown lag; weekly checks suffice
    metrics=METRICS,
    record_types=('rti_annual_return',),
    geo_note='SMC city: the figures describe Surat Municipal Corporation as one public authority under the RTI Act.',
    licence_note='Surat Municipal Corporation website; public information published under RTI Act s.4.',
    notes=('Annual returns (rti.annual.*) are copies of the Gujarat RTI Annual Return form; past years are '
           'downloaded once (skip_if_seen) and 5 image-only years (SCANNED_RETURNS) are skipped. Patrak-7/8 '
           '(rti.quarterly.*) use a legacy Gujarati font: rows are mapped by serial number against documented row '
           'lists. Annual and quarterly series are compiled separately and do not reconcile: never mix them.'),
)


# ---------------------------------------------------------------- fetch

@dataclass(frozen=True)
class ReturnLink:
    url: str
    title: str
    y1: int          # "Year 2025 to 2026" -> 2025, 2026
    y2: int

    @property
    def label(self) -> str:
        return f'{self.y1}-{self.y2}'


_RETURN_TITLE = re.compile(r'Annual\s+Return\s*-\s*Year\s*((?:19|20)\d\d)\s*to\s*((?:19|20)\d\d)', re.I)


def annual_return_links(body: bytes | str, base: str = INDEX_URL) -> list[ReturnLink]:
    out, seen = [], set()
    for url, text in links(body, base):
        m = _RETURN_TITLE.search(text)
        if not m or not url.lower().split('?')[0].endswith('.pdf') or url in seen:
            continue
        seen.add(url)
        out.append(ReturnLink(url, text, int(m.group(1)), int(m.group(2))))
    return out


def fetch(ctx):
    # soft=True: one missing file records an error and the other documents still load; a block (403/429)
    # still raises and stops the run.
    yield ctx.get(PATRAK7_URL, meta={'doc': 'patrak7'}, soft=True)
    yield ctx.get(PATRAK8_URL, meta={'doc': 'patrak8'}, soft=True)
    index = ctx.get(INDEX_URL, meta={'doc': 'index'}, soft=True)
    if index is None:
        return
    yield index
    docs = annual_return_links(index.body)
    newest = max((d.y1 for d in docs), default=None)
    for d in sorted(docs, key=lambda d: d.y1):        # oldest first (README convention)
        if d.label in SCANNED_RETURNS:
            continue
        # a past year's return is immutable: download it once. The newest one is re-checked
        # (conditional GET, so normally a 304) in case SMC re-uploads a corrected return.
        yield ctx.get(d.url, meta={'doc': 'annual_return', 'year': d.label},
                      skip_if_seen=d.y1 != newest, soft=True)


# ---------------------------------------------------------------- PDF words

@dataclass(frozen=True)
class W:
    x0: float
    y0: float
    x1: float
    y1: float
    text: str
    page: int

    @property
    def xc(self) -> float:
        return (self.x0 + self.x1) / 2

    @property
    def yc(self) -> float:
        return (self.y0 + self.y1) / 2


_WORD = re.compile(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>')


def pdf_words(body: bytes) -> list[W]:
    """Every word of a PDF with its bounding box (pdftotext -bbox), pages numbered from 1.
    opencity.parse.pdf_text has no coordinate mode, so this adapter makes its own pdftotext call."""
    with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp:
        tmp.write(body)
        tmp.flush()
        try:
            r = subprocess.run(['pdftotext', '-bbox', '-enc', 'UTF-8', tmp.name, '-'], capture_output=True, timeout=300)
        except FileNotFoundError:
            raise RuntimeError('pdftotext not found: install poppler-utils') from None
    if r.returncode != 0:
        raise RuntimeError(f'pdftotext -bbox failed: {r.stderr.decode(errors="replace")[:300]}')
    out = []
    for page_no, page in enumerate(r.stdout.decode('utf-8', errors='replace').split('<page ')[1:], start=1):
        for m in _WORD.finditer(page):
            out.append(W(float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)),
                         htmllib.unescape(m.group(5)), page_no))
    return out


# a printed number: digits with optional Indian/Western comma grouping and an optional decimal part
# ("1,23,456", "181780", "1234.50"). Decimals are accepted so that a fee printed with paise is read, not
# silently skipped; validate() still requires counts to be whole numbers.
_NUM = re.compile(r'(?:\d{1,3}(?:,\d{2,3})+|\d+)(?:\.\d+)?')


def _is_int(w: W) -> bool:
    """True if the word is a printed number (the name is historical: decimals count too)."""
    return bool(_NUM.fullmatch(w.text))


def _value(w: W | None) -> float | None:
    return float(w.text.replace(',', '')) if w is not None else None


def _line(words: list[W], ref: W, tol: float = 3.5) -> list[W]:
    """Words on the same text line as ref, left to right."""
    return sorted((w for w in words if w.page == ref.page and abs(w.yc - ref.yc) <= tol), key=lambda w: w.x0)


def _find(words: list[W], text: str, *, after: W | None = None) -> W:
    """First word equal to text (in reading order), optionally only below `after`."""
    for w in sorted(words, key=lambda w: (w.page, w.y0, w.x0)):
        if w.text == text and (after is None or (w.page, w.yc) > (after.page, after.yc + 2)):
            return w
    raise ValueError(f'word {text!r} not found: layout changed?')


def _next_number_line(words: list[W], y: float, limit: float = 45) -> list[W]:
    """The numbers on the first line below height y (within `limit` points)."""
    below = [w for w in words if _is_int(w) and y + 4 < w.yc < y + limit]
    if not below:
        return []
    top = min(w.yc for w in below)
    return [w for w in below if w.yc - top <= 3.5]


def _assign(nums: list[W], anchors: dict[str, float], what: str) -> dict[str, W]:
    """Each number goes to the anchor (field) whose x is nearest; two numbers in one field is an error."""
    out: dict[str, W] = {}
    for w in nums:
        k = min(anchors, key=lambda a: abs(anchors[a] - w.xc))
        if k in out:
            raise ValueError(f'{what}: two numbers ({out[k].text}, {w.text}) fall in the "{k}" field')
        out[k] = w
    return out


def _pdf_creation_date(body: bytes) -> str | None:
    m = re.search(rb'/CreationDate\s*\(D:(\d{4})(\d{2})(\d{2})', body)
    if not m:
        return None
    try:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3))).isoformat()
    except ValueError:
        return None


# ---------------------------------------------------------------- document type

def _doc(raw: Raw) -> str:
    doc = (raw.meta or {}).get('doc')
    if doc:
        return doc
    # parse-file / tests without meta: recognise the document by its content
    if not raw.body[:1024].lstrip().startswith(b'%PDF'):
        return 'index'
    text = ' '.join(w.text for w in pdf_words(raw.body)[:300])
    if 'Annual Return Form' in text or not text.strip():
        return 'annual_return'
    if re.search(r'5\+S\s+v\*', text) or re.search(r'પત્રક\s*-\s*7', text):
        return 'patrak7'
    if re.search(r'5\+S\s+v\(', text) or re.search(r'પત્રક\s*-\s*8', text):
        return 'patrak8'
    raise ValueError('cannot tell which RTI document this is (set raw.meta["doc"])')


def parse(raw: Raw) -> Result:
    doc = _doc(raw)
    res = Result(geos=[SMC])
    if doc == 'index':
        _parse_index(raw, res)
    elif doc == 'annual_return':
        _parse_annual(raw, res)
    elif doc in PATRAKS:
        _parse_patrak(raw, res, PATRAKS[doc])
    else:
        raise ValueError(f'unknown document tag {doc!r}')
    return res


# ---------------------------------------------------------------- index page

def _parse_index(raw: Raw, res: Result) -> None:
    docs = annual_return_links(raw.body, raw.url if raw.url.startswith('http') else INDEX_URL)
    if not docs:
        raise ValueError('no "Gujarat State RTI Annual Return - Year .. to .." PDF links found')
    for d in docs:
        res.records.append(Record('rti_annual_return', d.label, {
            'title': clean(d.title), 'url': d.url, 'year_label': d.label,
            'period_start': f'{d.y1}-04-01', 'period_end': f'{d.y2}-03-31',
            # adapter annotation, not from the page: the PDF is an image-only scan (see SCANNED_RETURNS)
            'image_only_scan': d.label in SCANNED_RETURNS}))
    res.complete_record_types = ('rti_annual_return',)


# ---------------------------------------------------------------- annual return

ANNUAL_FIELDS = (
    ['requests_' + f for f in ('opening_balance', 'received', 'transferred', 'rejected', 'accepted')]
    + ['first_appeals_' + f for f in ('opening_balance', 'received', 'rejected', 'accepted')]
    + ['disciplinary_actions', 'apios_designated', 'pios_designated', 'aas_designated']
    + [f'section:{s}' for s in SECTIONS]
    + ['registration_fees_rs', 'additional_fees_rs', 'penalties_levied_rs', 'penalties_collected_rs',
       'penalties_total_rs'])


def _parse_annual(raw: Raw, res: Result) -> None:
    words = [w for w in pdf_words(raw.body) if w.page == 1]
    if not words:
        raise ValueError('PDF has no text layer (an image-only scan): it cannot be read without OCR')
    text = ' '.join(w.text for w in sorted(words, key=lambda w: (w.y0, w.x0)))
    if 'Annual Return Form' not in text:
        raise ValueError('not a Gujarat RTI "Annual Return Form"')
    if not re.search(r'Public Authority\s*:\s*Surat Municipal Corporation', text):
        raise ValueError('annual return is not for Surat Municipal Corporation')
    m = re.search(r'Year:\s*((?:19|20)\d\d)\s*-\s*((?:19|20)\d\d)', text)
    if not m:
        raise ValueError('"Year: YYYY-YYYY" not found')
    y1, y2 = int(m.group(1)), int(m.group(2))
    if not 1 <= y2 - y1 <= 2:
        raise ValueError(f'odd return year {m.group(0)!r}')
    start, end = f'{y1}-04-01', f'{y2}-03-31'
    got: dict[str, W] = {}

    # requests / first appeals table. Header words wrap differently in every layout; "Opening", "Received" and
    # the two "Decisions" always share the first header line. "No. of cases transferred" sits between
    # "Received" and the first "Decisions" but wraps unpredictably, so its anchor is their midpoint.
    opening = _find(words, 'Opening')
    hdr = _line(words, opening)
    received = [w for w in hdr if w.text == 'Received']
    decisions = [w for w in hdr if w.text == 'Decisions']
    if len(received) != 1 or len(decisions) != 2:
        raise ValueError(f'requests table header changed: {[w.text for w in hdr]}')
    anchors = {'opening_balance': opening.xc, 'received': received[0].xc,
               'transferred': (received[0].xc + decisions[0].xc) / 2,
               'rejected': decisions[0].xc, 'accepted': decisions[1].xc}
    req = _find(words, 'Requests', after=opening)
    first = _find(words, 'First', after=req)
    appeals = _find(words, 'Appeals', after=opening)
    if not (abs(appeals.yc - first.yc) < 3.5 or 0 < appeals.y0 - first.y1 < 10):
        raise ValueError('"First Appeals" row label not found')
    for row, top, bottom, right in (('requests', req.y0, req.y1, req.x1),
                                    ('first_appeals', first.y0, max(first.y1, appeals.y1), max(first.x1, appeals.x1))):
        nums = [w for w in words if _is_int(w) and top - 3 <= w.yc <= bottom + 3 and w.x0 > right]
        vals = _assign(nums, anchors, row)
        if row == 'first_appeals' and 'transferred' in vals:
            raise ValueError('a "transferred" value on the First Appeals row: form changed')
        got.update({f'{row}_{k}': w for k, w in vals.items()})

    # disciplinary action: one number right of the 2-3 line label
    disc = _find(words, 'disciplinary')
    officer = _find(words, 'Officer', after=disc)
    band = [w for w in words if disc.y0 - 3 <= w.yc <= officer.y1 + 3]
    label_right = max(w.x1 for w in band if not _is_int(w))
    nums = [w for w in band if _is_int(w) and w.x0 > label_right]
    if len(nums) > 1:
        raise ValueError(f'disciplinary action: {len(nums)} numbers')
    if nums:
        got['disciplinary_actions'] = nums[0]

    # officers designated: values on the first number line below the three labels
    lab = {k: _find(words, t, after=officer) for k, t in (('apios', 'APIOs'), ('pios', 'PIOs'), ('aas', 'AAs'))}
    vals = _assign(_next_number_line(words, max(w.yc for w in lab.values())),
                   {k: w.xc for k, w in lab.items()}, 'officers designated')
    got.update({f'{k}_designated': w for k, w in vals.items()})

    # provisions invoked while rejecting: a header line a..j 9 11 24 Other, values on the next line
    other = _find(words, 'Other', after=officer)
    hdr = _line(words, other)
    if [w.text for w in hdr] != ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', '9', '11', '24', 'Other']:
        raise ValueError(f'sections header changed: {[w.text for w in hdr]}')
    vals = _assign(_next_number_line(words, other.yc), {s: w.xc for s, w in zip(SECTIONS, hdr)}, 'sections')
    got.update({f'section:{k}': w for k, w in vals.items()})

    # charges: two fee fields under their labels, then "Levied <n> Collected <n> Total <n>" where each
    # value follows its label (same line in the web printouts, slightly above in the Word re-typings)
    reg = _find(words, 'Registration', after=other)
    add = _find(words, 'Additional', after=other)
    levied = _find(words, 'Levied', after=reg)
    pen = [w for w in _line(words, levied) if w.text in ('Levied', 'Collected', 'Total')]
    if [w.text for w in pen] != ['Levied', 'Collected', 'Total']:
        raise ValueError(f'penalties labels changed: {[w.text for w in pen]}')
    for w in (w for w in words if _is_int(w) and reg.yc + 4 < w.yc <= levied.y1 + 3):
        if w.x0 >= levied.x0 - 2:
            lbl = [p for p in pen if p.x1 <= w.x0 + 2][-1]
            k = {'Levied': 'penalties_levied_rs', 'Collected': 'penalties_collected_rs',
                 'Total': 'penalties_total_rs'}[lbl.text]
        else:
            k = min((('registration_fees_rs', reg.xc), ('additional_fees_rs', add.xc)), key=lambda a: abs(a[1] - w.xc))[0]
        if k in got:
            raise ValueError(f'charges: two numbers for {k}')
        got[k] = w

    as_of = _pdf_creation_date(raw.body)
    for f in ANNUAL_FIELDS:
        w = got.get(f)
        metric, dims = f, {}
        if f.startswith('section:'):
            metric, dims = 'rejections_by_section', {'section': f.split(':', 1)[1]}
        v = _value(w)
        res.observations.append(Obs(f'rti.annual.{metric}', 'smc_city', 'smc', start, end, value=v,
                                    status='reported' if v is not None else 'not_reported',
                                    dims=dims, publisher_as_of=as_of))


# ---------------------------------------------------------------- Patrak-7 / Patrak-8

# Each form's rows, top to bottom, keyed by serial number: (key, metric or None for a heading row, dims, span).
# span: None = the quarter; 'fy_before' = 1 April .. day before the quarter; 'fy_to_date' = 1 April .. quarter end.
# Labels are our reading of the Gujarati form (pdftotext returns the legacy-font encoding quoted after it).
P7_ROWS: list[tuple[str, str | None, dict, str | None]] = [
    # 1  ત્રિમાસની શરૂઆતમાં અગાઉની પડતર અરજીઓ          "l+DF;GL X~VFTDF\ VUFpGL 50TZ VZHLVM"
    ('1', 'rti.quarterly.requests_pending_start', {}, None),
    # 2  ત્રિમાસિક અહેવાલ દરમ્યાન મળેલ અરજીઓ             "l+DFl;S VC[JF, NZdIFG D/[, VZHLVM"
    ('2', 'rti.quarterly.requests_received', {}, None),
    # 3  કુલ અરજીઓ                                       "S], VZHLVM"
    ('3', 'rti.quarterly.requests_total', {}, None),
    # 4  અન્ય જાહેર સત્તામંડળને સંપૂર્ણતઃ તબદીલ કરેલ અરજીઓ    "VgI HFC[Z ;tTFD\0/G[ ;\5}6"To TANL, SZ[, VZHLVM"
    ('4', 'rti.quarterly.requests_transferred_wholly', {}, None),
    # 5  અન્ય જાહેર સત્તામંડળને અંશતઃ તબદીલ કરેલ અરજીઓ       "VgI HFC[Z ;tTFD\0/G[ V\XTo TANL, SZ[, VZHLVM"
    ('5', 'rti.quarterly.requests_transferred_partly', {}, None),
    # 6  માહિતી સંપૂર્ણતઃ આપેલ હોય તેવી અરજીઓ             "DFlCTL ;\5]6"To VF5[, CMI T[JL VZHLVM"
    ('6', 'rti.quarterly.requests_info_supplied', {}, None),
    # 7  માહિતી સંપૂર્ણતઃ નકારેલ હોય તેવી અરજીઓ            "DFlCTL ;\5]6"To GSFZ[, CMI T[JL VZHLVM"
    ('7', 'rti.quarterly.requests_refused_fully', {}, None),
    # 8  માહિતી અંશતઃ નકારેલ હોય તેવી અરજીઓ               "DFlCTL V\XTo GSFZ[, CMI T[JL VZHLVM"
    ('8', 'rti.quarterly.requests_refused_partly', {}, None),
    # 9  (કોલમ-4+6+7+8 નો સરવાળો) કુલ નિકાલ               "sSM,Dv$+ &+ *+ ( GM ;ZJF/Mf S], lGSF,"
    ('9', 'rti.quarterly.requests_disposed', {}, None),
    # 9(અ) કુલ નિકાલ પૈકી સમયમર્યાદામાં નિકાલ કરેલ અરજીઓની સંખ્યા   "S], lGSF, 5{SL ;DIDIF"NFDF\ lGSF, SZ[, VZHLVMGL ;\bIF"
    ('9(a)', 'rti.quarterly.requests_disposed_within_time', {}, None),
    # 10 ત્રિમાસને અંતે પડતર અરજીઓ [કોલમ (3-9)]            "l+DF;G[ V\T[ 50TZ VZHLVM [ SM,Do s#v)f ]"
    ('10', 'rti.quarterly.requests_pending_end', {}, None),
    # 11 કોલમ-7 અને 8 માં દર્શાવેલ અરજીઓમાં માંગેલ માહિતી કાયદાની જે કલમ અન્વયે નકારેલ છે તેની સંખ્યા  (heading)
    ('11', None, {}, None),
    # 11(a)..(j) કાયદાની કલમ-8(1)(ક..ઠ) મુજબ, (k) કલમ-9, (l) કલમ-11, (m) કલમ-24, (n) અન્ય
    *[(f'11{c}', 'rti.quarterly.refusals_by_section', {'section': s}, None) for c, s in zip('abcdefghijklmn', SECTIONS)],
    # 12 કુલ :- 11(a) થી 11(n)                            "S], ov !!(a) YL !! sn)"
    ('12', 'rti.quarterly.refusals_total', {}, None),
    # 13 મળેલ ફી અને નકલ ચાર્જીસ (રોકડ કે અન્ય સ્વરૂપ સહિતની રકમ) ની વિગત  (heading)
    ('13', None, {}, None),
    # 13a ચાલુ ત્રિમાસમાં અરજી ફી પેટે મળેલ રકમ (તબદીલ થઈને આવેલ અરજીઓ સિવાયની)
    ('13a', 'rti.quarterly.application_fees_rs', {}, None),
    # 13b ચાલુ ત્રિમાસમાં અરજી ફી સિવાયની ચાર્જીસ વગેરેની રકમ
    ('13b', 'rti.quarterly.other_charges_rs', {}, None),
    # 13c અહેવાલના ત્રિમાસ દરમ્યાન થયેલ કુલ આવક (કોલમ 13a + 13b)
    ('13c', 'rti.quarterly.income_rs', {}, None),
    # 13d ચાલુ નાણાંકીય વર્ષના અગાઉના સમયગાળા દરમ્યાન થયેલ કુલ આવક
    ('13d', 'rti.quarterly.income_earlier_in_fy_rs', {}, 'fy_before'),
    # 14 કુલ આવકનો સરવાળો (કોલમ : 13c + 13d)
    ('14', 'rti.quarterly.income_fy_to_date_rs', {}, 'fy_to_date'),
]

P8_ROWS: list[tuple[str, str | None, dict, str | None]] = [
    # 1  ત્રિમાસની શરૂઆતમાં અગાઉની પડતર અપીલો          "l+DF;GL X~VFTDF\ VUFpGL 50TZ V5L,M"
    ('1', 'rti.quarterly.first_appeals_pending_start', {}, None),
    # 2  ત્રિમાસિક અહેવાલ દરમ્યાન મળેલ અપીલો             "l+DFl;S VC[JF, NZdIFG D/[, V5L,M"
    ('2', 'rti.quarterly.first_appeals_received', {}, None),
    # 3  કુલ અપીલો                                       "S], V5L,M"
    ('3', 'rti.quarterly.first_appeals_total', {}, None),
    # 4  અપીલ સંપૂર્ણ મંજૂર કરવામાં આવેલ હોય તેની સંખ્યા      "V5L, ;\5]6" D\H]Z SZJFDF\ VFJ[, CMI T[GL ;\bIF"
    ('4', 'rti.quarterly.first_appeals_allowed', {}, None),
    # 5  અપીલ અંશતઃ મંજૂર અને અંશતઃ નામંજૂર કરવામાં આવેલ હોય તેવી સંખ્યા
    ('5', 'rti.quarterly.first_appeals_partly_allowed', {}, None),
    # 6  અપીલ સંપૂર્ણ નામંજૂર કરવામાં આવેલ હોય તેની સંખ્યા     "V5L, ;\5]6" GFD\H]Z SZJFDF\ VFJ[, CMI T[GL ;\bIF"
    ('6', 'rti.quarterly.first_appeals_rejected', {}, None),
    # 7  કુલ નિકાલ                                        "S], lGSF,"
    ('7', 'rti.quarterly.first_appeals_disposed', {}, None),
    # 7(અ) કુલ નિકાલ પૈકી સમયમર્યાદામાં (કલમ-19(6)) નિકાલ કરેલ અપીલોની સંખ્યા  (values print on the line below)
    ('7(a)', 'rti.quarterly.first_appeals_disposed_within_time', {}, None),
    # 8  ત્રિમાસને અંતે પડતર અપીલો [કોલમ: (3-7)]            "l+DF;G[ V\T[ 50TZ V5L,M[ [ SM,Do s#v*f]"
    ('8', 'rti.quarterly.first_appeals_pending_end', {}, None),
    # 9  કોલમ-5 અને 6 માં દર્શાવેલ અરજીઓમાં માંગેલ માહિતી કાયદાની જે કલમ અન્વયે નકારેલ છે તેની સંખ્યા  (heading)
    ('9', None, {}, None),
    # 9(a)..(n) as in Patrak-7 row 11 (row h's label repeats "(જ)", a typo; positions are kept)
    *[(f'9{c}', 'rti.quarterly.first_appeal_refusals_by_section', {'section': s}, None)
      for c, s in zip('abcdefghijklmn', SECTIONS)],
    # 10 કુલ :- 9(a) થી 9(n)                              "S], ov )(a) YL ) sn)"
    ('10', 'rti.quarterly.first_appeal_refusals_total', {}, None),
]

# printed "nothing here" markers in a value cell: stored as not_reported, like an empty cell
_BLANK_MARKS = {'-', '--', '—', '–', 'na', 'n.a.', 'n/a', 'nil'}

# legacy-font digits seen in the header counts (a Unicode or ASCII number would match too)
_LD = r'[_!Z#$5&*()0-9૦-૯]'


@dataclass(frozen=True)
class Patrak:
    name: str
    rows: list
    count_metric: str
    count_patterns: tuple[str, ...]     # regexes for the officer count in the header text

    @property
    def keys(self) -> list[str]:
        return [r[0] for r in self.rows]


PATRAKS = {
    'patrak7': Patrak('Patrak-7', P7_ROWS, 'rti.quarterly.pios', (
        # "જાહેર માહિતી અધિકારીઓની કુલ સંખ્યા :- 353"  (legacy "HFC[Z DFlCTL VlWSFZLVMGL S], ;\bIF ov#5#")
        rf'HFC\[Z\s+DFlCTL\s+VlWSFZLVMGL\s+S\],\s+;\\bIF\s*ov\s*({_LD}+)',
        r'જાહેર\s+માહિતી\s+અધિકારીઓની\s+કુલ\s+સંખ્યા\s*:?-?\s*([0-9૦-૯]+)')),
    'patrak8': Patrak('Patrak-8', P8_ROWS, 'rti.quarterly.appellate_authorities', (
        # "અપીલ અધિકારીઓની કુલ સંખ્યા :- 73"  (legacy "V5L, VlWSFZLVMGL S], ;\bIF ov *#")
        rf'V5L,\s+VlWSFZLVMGL\s+S\],\s+;\\bIF\s*ov\s*({_LD}+)',
        r'અપીલ\s+અધિકારીઓની\s+કુલ\s+સંખ્યા\s*:?-?\s*([0-9૦-૯]+)')),
}

_LEGACY_DIGITS = str.maketrans('_!Z#$&*()', '012346789')     # '5' is drawn as itself
_GU_DIGITS = str.maketrans('૦૧૨૩૪૫૬૭૮૯', '0123456789')


def _legacy_int(s: str) -> int:
    t = s.translate(_LEGACY_DIGITS).translate(_GU_DIGITS)
    if not t.isdigit():
        raise ValueError(f'not a legacy-font number: {s!r}')
    return int(t)


def _sr(text: str) -> str | None:
    """A serial-number cell -> '1', '10', '9(a)' (the "(અ)" sub-row) or a row letter 'a'..'n'; else None."""
    t = text.strip()
    for suffix in ('sVf', '(અ)', '(a)'):
        if t.endswith(suffix) and len(t) > len(suffix):
            n = t[:-len(suffix)].translate(_LEGACY_DIGITS).translate(_GU_DIGITS)
            return f'{n}(a)' if n.isdigit() else None
    if t == 'I':                # the forms print row (i) as a capital I
        return 'i'
    if re.fullmatch(r'[a-n]', t):
        return t
    t = t.translate(_LEGACY_DIGITS).translate(_GU_DIGITS)
    return t if re.fullmatch(r'\d{1,2}', t) else None


def _label_runs(words: list[W], x_start: float, gap: float = 6) -> set[int]:
    """ids of words that continue, on the same line and with word-spacing gaps (< `gap` pt), a run of text
    that starts left of x_start. Values sit 15+ pt away from their labels, so they never join a run."""
    out: set[int] = set()
    lines: list[list[W]] = []
    for w in sorted(words, key=lambda w: w.yc):
        if lines and abs(lines[-1][0].yc - w.yc) <= 2.5:
            lines[-1].append(w)
        else:
            lines.append([w])
    for line in lines:
        prev = None
        for w in sorted(line, key=lambda w: w.x0):
            if w.x0 < x_start or (prev is not None and id(prev) in out and w.x0 - prev.x1 < gap):
                out.add(id(w))
            prev = w if prev is None or w.x1 > prev.x1 else prev
    return out


def _patrak_header(words: list[W], name: str) -> tuple[W, list[W]]:
    """The table header row: the serial-number header ("ક્રમ") and the three value-column headers."""
    for w in words:
        if w.text in ('S|D', 'ક્રમ'):
            cols = _line(words, w)[-3:]
            names = [c.text for c in cols]
            if names in (['AL5LV[,', 'VgI', 'S],'], ['બીપીએલ', 'અન્ય', 'કુલ']):
                return w, cols
            raise ValueError(f'{name} column headers changed: {names}')
    raise ValueError(f'{name} table header ("ક્રમ") not found')


def _patrak_period(top: str, name: str) -> tuple[int, int, str, str]:
    """(FY start year, quarter, start, end) from the printed date range, checked against the printed FY."""
    dates = re.findall(rf'({_LD}{{1,2}})[q/.\-]({_LD}{{1,2}})[q/.\-]({_LD}{{2,4}})', top)
    if len(dates) < 2:
        raise ValueError(f'{name} date range ("તા. dd/mm/yy થી તા. dd/mm/yy") not found')
    ds = []
    for d, m, y in dates[:2]:
        yy = _legacy_int(y)
        ds.append(date(yy + 2000 if yy < 100 else yy, _legacy_int(m), _legacy_int(d)))
    d0, d1 = ds
    fy = d0.year if d0.month >= 4 else d0.year - 1
    q = (d0.month - 4) % 12 // 3 + 1
    qs, qe = quarter_of_fy(fy, q)
    if (d0.isoformat(), d1.isoformat()) != (qs, qe):
        raise ValueError(f'{name} period {d0}..{d1} is not a financial-year quarter')
    fm = (re.search(rf'JQF"\s*o\s*({_LD}{{4}})\s*v\s*({_LD}{{2}})', top)
          or re.search(r'વર્ષ\s*:?\s*([0-9૦-૯]{4})\s*-\s*([0-9૦-૯]{2})', top))
    if not fm:
        raise ValueError(f'{name} financial year ("નાણાંકીય વર્ષ : YYYY - YY") not found')
    if _legacy_int(fm.group(1)) != fy:
        raise ValueError(f'{name} financial year {fm.group(0)!r} does not contain the period {qs}..{qe}')
    return fy, q, qs, qe


def _parse_patrak(raw: Raw, res: Result, spec: Patrak) -> None:
    words = [w for w in pdf_words(raw.body) if w.page == 1]
    sr_head, cols = _patrak_header(words, spec.name)
    top = ' '.join(w.text for w in sorted(words, key=lambda w: (w.y0, w.x0)) if w.y1 < sr_head.y0)
    fy, q, qs, qe = _patrak_period(top, spec.name)
    as_of = _pdf_creation_date(raw.body)

    # serial-number cells: the column under the "ક્રમ" header, top to bottom
    srs: list[tuple[str, W]] = []
    parent = None
    for w in sorted((w for w in words if w.y0 > sr_head.y1 and sr_head.x0 - 10 <= w.xc <= sr_head.x1 + 10),
                    key=lambda w: w.y0):
        k = _sr(w.text)
        if k is None:
            continue
        if k.isalpha():
            if parent is None:
                raise ValueError(f'{spec.name}: lettered row {w.text!r} before any numbered row')
            k = parent + k
        elif '(' not in k:
            parent = k
        srs.append((k, w))
    found = [k for k, _ in srs]
    if found != spec.keys:
        raise ValueError(f'{spec.name} rows changed: found {found}, expected {spec.keys}')

    # value cells: numbers right of the labels; each belongs to the last serial cell at or above it
    # (a wrapped label can push its values one line down, as in Patrak-8 row 7(a))
    by_row: dict[str, list[W]] = {}
    bottom = srs[-1][1].y1 + 6
    # fail loudly: a word that starts inside the value columns must be a number or a blank marker. Anything
    # else ("1,234/-", "12 (a)") would otherwise be dropped and stored as not_reported. Long labels that run
    # on into the value columns (Patrak-8 row 9's heading) are skipped: they are chained to a word that starts
    # left of the columns.
    region = [w for w in words if sr_head.y1 < w.y0 < bottom]
    labels = _label_runs(region, cols[0].x0 - 5)
    odd = [w.text for w in region if w.x0 >= cols[0].x0 - 5 and id(w) not in labels
           and not _is_int(w) and w.text.strip().lower() not in _BLANK_MARKS]
    if odd:
        raise ValueError(f'{spec.name}: unreadable value cells {odd[:6]}')
    for w in words:
        if not (_is_int(w) and w.x1 > cols[0].x0 - 15 and sr_head.y1 < w.y0 < bottom):
            continue
        above = [(k, s) for k, s in srs if s.y0 <= w.yc + 2]
        if not above or w.yc - above[-1][1].yc > 16:
            raise ValueError(f'{spec.name}: number {w.text} at y={w.y0:.0f} is on no numbered row')
        by_row.setdefault(above[-1][0], []).append(w)
    metric_of = {k: m for k, m, _, _ in spec.rows}
    stray = [k for k in by_row if metric_of[k] is None]
    if stray:
        raise ValueError(f'{spec.name}: numbers on heading rows {stray}')

    # columns: right-aligned (Patrak-7) or centred (Patrak-8) under BPL / other / total. Anchor each column on
    # the median centre of the values in rows that fill all three, falling back to the header centres.
    anchors = [c.xc for c in cols]
    full = [sorted(ws, key=lambda w: w.x0) for ws in by_row.values() if len(ws) == 3]
    if full:
        anchors = [sorted(ws[i].xc for ws in full)[len(full) // 2] for i in range(3)]
        if any(abs(a - c.xc) > 35 for a, c in zip(anchors, cols)):
            raise ValueError(f'{spec.name}: value columns do not line up with the header')
    cells: dict[tuple[str, str], W] = {}
    for k, ws in by_row.items():
        for w in ws:
            col = COLUMNS[min(range(3), key=lambda i: abs(anchors[i] - w.xc))]
            if (k, col) in cells:
                raise ValueError(f'{spec.name} row {k}: two numbers ({cells[(k, col)].text}, {w.text}) in {col}')
            cells[(k, col)] = w

    fy_start = f'{fy}-04-01'
    for key, metric, dims, span in spec.rows:
        if metric is None:
            continue
        start, end = qs, qe
        if span == 'fy_before':
            if q == 1:
                # "earlier in the year" is empty in Q1: nothing to store, but a non-zero figure means the
                # quarter or the row mapping is wrong
                if any(_value(cells.get((key, c))) for c in COLUMNS):
                    raise ValueError(f'{spec.name}: Q1 return with income "earlier in the year" (row {key})')
                continue
            start, end = fy_start, (date.fromisoformat(qs) - timedelta(days=1)).isoformat()
        elif span == 'fy_to_date':
            start = fy_start
        for col in COLUMNS:
            v = _value(cells.get((key, col)))
            res.observations.append(Obs(metric, 'smc_city', 'smc', start, end, value=v,
                                        status='reported' if v is not None else 'not_reported',
                                        dims={**dims, 'applicants': col}, publisher_as_of=as_of))

    for pat in spec.count_patterns:
        pm = re.search(pat, top)
        if pm:
            res.observations.append(Obs(spec.count_metric, 'smc_city', 'smc', qs, qe,
                                        value=float(_legacy_int(pm.group(1))), publisher_as_of=as_of))
            break


# ---------------------------------------------------------------- validation

def validate(result: Result, raw: Raw) -> None:
    if result.records:          # index page
        years = sorted(int(r.record_key[:4]) for r in result.records)
        if len(years) < 15:
            raise ValidationError(f'only {len(years)} annual-return links on the index page')
        if len(set(years)) != len(years):
            raise ValidationError('duplicate years among the annual-return links')
        if years[0] < 2005 or years[-1] < 2024:
            raise ValidationError(f'implausible annual-return years {years[0]}..{years[-1]}')
        return
    obs = result.observations
    if not obs:
        raise ValidationError('no observations parsed')
    for o in obs:
        if o.value is None:
            continue
        rupees = o.metric_id.endswith('_rs')
        if o.value < 0 or (not rupees and o.value != int(o.value)):
            raise ValidationError(f'{o.metric_id} {o.dims}: {o.value} is not a non-negative whole number')
        # SMC gets ~10-20k applications a year (FY2023-24: 18,071) and collects a few lakh rupees in fees
        cap = 10_000_000 if rupees else 200_000
        if o.value > cap:
            raise ValidationError(f'{o.metric_id} {o.dims}: implausible value {o.value}')
    if min(o.period_start for o in obs) < '2005-04-01':
        raise ValidationError('period before the RTI Act came into force (2005)')
    # a return describes a period that has at least begun: a period starting after the fetch is a misread
    # year or quarter. (Tests pass raw=None or a frozen file's retrieved_at.)
    fetched = (getattr(raw, 'retrieved_at', '') or '')[:10]
    latest = max(o.period_start for o in obs)
    if fetched and latest > fetched:
        raise ValidationError(f'period starting {latest} is after the fetch date {fetched}')
    metrics = {o.metric_id for o in obs}
    if 'rti.annual.requests_received' in metrics:
        _validate_annual(obs)
    elif 'rti.quarterly.requests_total' in metrics:
        _validate_quarter(obs, 'requests', 'Patrak-7', [
            (('pending_start', 'received'), 'total'),
            (('transferred_wholly', 'info_supplied', 'refused_fully', 'refused_partly'), 'disposed')],
            'rti.quarterly.refusals_by_section', 'rti.quarterly.refusals_total')
    elif 'rti.quarterly.first_appeals_total' in metrics:
        _validate_quarter(obs, 'first_appeals', 'Patrak-8', [
            (('pending_start', 'received'), 'total'),
            (('allowed', 'partly_allowed', 'rejected'), 'disposed')],
            'rti.quarterly.first_appeal_refusals_by_section', 'rti.quarterly.first_appeal_refusals_total')
    else:
        raise ValidationError(f'unrecognised result: {sorted(metrics)[:5]}')


def _validate_annual(obs: list[Obs]) -> None:
    blank = [(o.metric_id, o.dims.get('section')) for o in obs if o.status != 'reported']
    if len(blank) > 2:
        # every field of this form is always filled in: many blanks mean the layout was not understood
        raise ValidationError(f'annual return: {len(blank)} fields not found, layout not understood: {blank[:6]}')
    v = {o.metric_id: o.value for o in obs if not o.dims}
    for core in ('requests_opening_balance', 'requests_received', 'first_appeals_received'):
        if v.get(f'rti.annual.{core}') is None:
            raise ValidationError(f'annual return without {core}')
    for row in ('requests', 'first_appeals'):
        have = sum(v.get(f'rti.annual.{row}_{k}') or 0 for k in ('opening_balance', 'received'))
        done = sum(v.get(f'rti.annual.{row}_{k}') or 0 for k in ('transferred', 'rejected', 'accepted'))
        if done > have:
            raise ValidationError(f'annual return {row}: {done} decided/transferred > {have} opening + received')


def _validate_quarter(obs: list[Obs], stem: str, name: str, sums, by_section: str, section_total: str) -> None:
    """The flow identities the form computes itself (total column), plus BPL + other = total on count rows."""
    prefix = f'rti.quarterly.{stem}_'
    q = {o.metric_id.removeprefix(prefix): o.value for o in obs
         if o.metric_id.startswith(prefix) and o.dims.get('applicants') == 'all'}
    need = ('pending_start', 'received', 'total', 'disposed', 'disposed_within_time', 'pending_end')
    missing = [k for k in need if q.get(k) is None]
    if missing:
        raise ValidationError(f'{name}: total column missing {missing}')
    for parts, total in sums:
        s = sum(q.get(p) or 0 for p in parts)
        if s != q[total]:
            raise ValidationError(f'{name}: {" + ".join(parts)} = {s} but {total} = {q[total]}')
    if q['total'] - q['disposed'] != q['pending_end']:
        raise ValidationError(f'{name}: total - disposed != pending_end ({q})')
    if q['disposed_within_time'] > q['disposed']:
        raise ValidationError(f'{name}: disposed within time > disposed')
    secs = sum(o.value or 0 for o in obs if o.metric_id == by_section and o.dims['applicants'] == 'all')
    tot = [o.value for o in obs if o.metric_id == section_total and o.dims['applicants'] == 'all']
    if tot and tot[0] is not None and tot[0] != secs:
        raise ValidationError(f'{name}: section total {tot[0]} != sum of sections {secs}')
    # BPL + other = total wherever all three are printed (count rows; the fee rows are not checked because the
    # published Q4 FY2025-26 Patrak-7 itself breaks this in row 13d/14)
    cells: dict[tuple, dict] = {}
    for o in obs:
        if 'applicants' in o.dims and not o.metric_id.endswith('_rs') and o.value is not None:
            k = (o.metric_id, o.period_start, tuple(sorted((a, b) for a, b in o.dims.items() if a != 'applicants')))
            cells.setdefault(k, {})[o.dims['applicants']] = o.value
    for k, c in cells.items():
        if len(c) == 3 and c['bpl'] + c['non_bpl'] != c['all']:
            raise ValidationError(f'{name}: bpl + non_bpl != all for {k}: {c}')
