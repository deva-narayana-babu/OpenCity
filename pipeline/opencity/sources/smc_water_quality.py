"""SMC Hydraulic department: water samples collected and tested at consumer taps, by zone (monthly).

Index page: https://www.suratmunicipal.gov.in/Departments/HydraulicWaterQuality
  - a table of the sampling regime (stage / type of test / frequency), kept as `wq_sampling_test` records
  - "Monthly Data of Collected and Tested Water Samples": one link per month (Oct 2008 onward) to
    .../Content/Documents/rtiact/Disclosure/Hydraulic/WaterQuality/<YYYY>/<MM>.pdf, kept as `document` records

Each monthly PDF (Gujarati) starts with a summary table, one row per zone plus a total row:
    ઝોન | લેવાયેલા નમુનાઓ (samples taken) | ફીટ નમુનાઓ (fit) | અનફીટ નમુનાઓ (unfit)
followed by "અનફીટ સેમ્પલની વિગત": the date and HOUSEHOLD ADDRESS of every unfit sample. Only the summary
table is parsed into observations. From the list below it, only the DATES are read (to confirm the month, see
below); addresses are never read into observations or records. (The framework still archives the raw PDF
under data/raw/, which is git-ignored.)

The samples are household-tap samples taken during supply (the 2008 PDFs say "Residential Tap"; from 2011 a
note says samples from water works and distribution-station tanks are not included).

Zone labels. Gujarati text from these PDFs comes out of pdftotext with broken conjuncts and, in some years,
whole letters substituted (West is "વે ટ", "લેસ્ર્" or "ળેસ્ર્"; Central "સે લ", "વેન્્ર" or "શેન્્઱"), so
_zone() matches on shape, and validate() requires the zone SET to be one of the layouts SMC has used:
7 zones to Aug 2019, 8 from Sep 2019 (East split into East-A/East-B), 9 from Jul 2023 (South split into
South-A/South-B). The undivided East zone has no code in surat.ZONES, so this module adds smc_zone:east.

Layout repair. In a few PDFs pdftotext puts one number of a row on a line of its own (Dec 2014, North);
summary_rows() re-attaches it only if its character column fills exactly the missing cell.

Month. Normally the month in the URL (/YYYY/MM.pdf). But some PDFs are linked under the wrong month on the
index page: 2019/09.pdf is November 2019 and 2019/11.pdf is September 2019, 2020/06 and 2020/07 are swapped,
and 2020/04.pdf is a second copy of May 2020 (April 2020 is not published). In every such case the printed
heading and all the unfit-sample dates agree with each other and not with the link, so the month is taken
from the sample dates (>= 5 dates, >= 90% in one month; otherwise the URL month), and the printed heading
year must match it. Month names in the heading are too garbled to read reliably, so only the year is checked.

Not parsed: Oct 2008 - Apr 2009 and Apr 2011 (legacy non-Unicode font; digits not decodable) and Oct 2015
(the file on the server is truncated). fetch() skips them (FIRST_MONTH, UNREADABLE) so they are not
re-downloaded on every refresh; the index records list them with parsed: false.

Publisher arithmetic is not always exact (Jan 2013 Central: 545 taken, 524 fit, 22 unfit), so validate()
only rejects documents whose rows or columns are off by more than a small tolerance (a misparse signal).
A '-' cell becomes not_reported, even where the other columns imply zero (Jun 2011 South unfit).
"""
from __future__ import annotations

import logging
import re
from collections import Counter

from ..model import Geo, Metric, Obs, Raw, Record, Result, Source, ValidationError
from ..parse import clean, html_tables, links, month_period, num, pdf_text
from ..surat import SMC, zone_code, zone_geo

URL = 'https://www.suratmunicipal.gov.in/Departments/HydraulicWaterQuality'
PDF_RE = re.compile(r'/Hydraulic/WaterQuality/(\d{4})/(\d{1,2})\.pdf$', re.I)
FIRST_MONTH = (2009, 5)    # Oct 2008 - Apr 2009 PDFs use a legacy Gujarati font (digits not decodable)
RECHECK_MONTHS = 3         # the newest months are re-requested (conditional GET) in case SMC replaces them
# linked PDFs that cannot be read (not fetched, so a permanent failure is not re-downloaded on every refresh)
UNREADABLE = {
    (2011, 4): 'legacy non-Unicode Gujarati font (digits not decodable)',
    (2015, 10): 'file on the server is truncated (313,683 bytes, no PDF trailer; checked 2026-10-05)',
}
log = logging.getLogger(__name__)

EAST_UNDIVIDED = Geo('smc_zone', 'east', 'East Zone (Varachha), before its split into East-A and East-B',
                     'smc_city', 'smc', note='Added by smc_water_quality: surat.ZONES has no undivided East zone')

ZONE_LAYOUTS = (
    frozenset({'north', 'east', 'west', 'central', 'south_west', 'south', 'south_east'}),
    frozenset({'north', 'east_a', 'east_b', 'west', 'central', 'south_west', 'south', 'south_east'}),
    frozenset({'north', 'east_a', 'east_b', 'west', 'central', 'south_west', 'south_a', 'south_b', 'south_east'}),
)

SOURCE = Source(
    id='smc_water_quality',
    name='SMC water samples collected and tested at consumer taps, by zone (monthly)',
    publisher='Surat Municipal Corporation, Hydraulic Department',
    url=URL,
    module='water',
    cadence='monthly',
    interval_hours=24 * 7,          # a month's PDF appears a few weeks after the month ends
    geo_note='SMC zones (7, 8 or 9 depending on the year) and the SMC total',
    licence_note='Surat Municipal Corporation web page and PDFs (RTI suo-motu disclosure); public information',
    notes='Monthly PDFs from May 2009; the unfit-sample address list in each PDF is not parsed or stored.',
    metrics=(
        Metric('wq.tap_samples_collected', 'Water samples collected at consumer taps', 'samples',
               'Water samples collected from household taps during supply in the month (SMC monthly PDF).'),
        Metric('wq.tap_samples_fit', 'Water samples found fit', 'samples',
               'Samples found fit for drinking (SMC tests against IS:10500).'),
        Metric('wq.tap_samples_unfit', 'Water samples found unfit', 'samples',
               'Samples found unfit for drinking.'),
    ),
    record_types=('document', 'wq_sampling_test'),
)

_COLS = ('wq.tap_samples_collected', 'wq.tap_samples_fit', 'wq.tap_samples_unfit')
# heading of the unfit-sample address list ("અનફીટ સેમ્પલની વિગત", garbled in many ways): parse stops here
_DETAILS = re.compile(r'અન.{0,30}ગત')
_GU_YEAR = re.compile(r'([૧૨][૦૯][૦-૯]{2})')
_GU_DIGITS = str.maketrans('૦૧૨૩૪૫૬૭૮૯', '0123456789')


def _zone(label: str) -> str:
    """Zone code (or 'total') for a garbled Gujarati zone label from the summary table.

    Some years substitute whole letters (વ->લ/ળ, સ->વ/શ), so West and Central are matched by shape:
    West = <letter>ે + સ્ર્/સ્ટ/ટ (વેસ્ટ), Central = <letter>ેન... or સે(ટ્)લ (સેન્ટ્રલ).
    validate() then requires each zone exactly once and the rows to add up, which catches a wrong match."""
    s = re.sub(r'[^\u0A80-\u0AFF\-]+', '', label)     # keep Gujarati letters and '-' (drops stray \x11, quotes)
    if re.fullmatch(r'[A-Za-z \-]+', label.strip()):        # in case a month is ever published in English
        return 'total' if label.strip().lower() == 'total' else zone_code(label)
    if re.fullmatch(r'(ક?ુ|ક)[લિર઱]', s):                 # કુલ (total); May 2009 prints 'કલ'
        return 'total'
    west = r'.ે(સ્ર્|સ્ટ|સ્ર|ટ)'
    if 'ાઉથ' in s:                                         # સાઉથ / વાઉથ / શાઉથ (south ...)
        rest = s.split('ાઉથ', 1)[1].lstrip('-')
        if not rest:
            return 'south'
        if rest.startswith('ઈ'):
            return 'south_east'
        if re.fullmatch(west, rest):
            return 'south_west'
        if rest == 'એ':
            return 'south_a'
        if rest in ('બી', 'ફી'):                          # 2019-20 PDFs print બ as ફ
            return 'south_b'
    elif s.startswith('ઈ'):                                # ઈસ્ટ (east)
        tail = s.split('-', 1)[1] if '-' in s else ''
        if not tail:
            return 'east'
        if tail == 'એ':
            return 'east_a'
        if tail in ('બી', 'ફી'):
            return 'east_b'
    elif s.startswith('નો'):                               # નોર્થ (north)
        return 'north'
    elif re.fullmatch(west, s.replace('-', '')):           # વેસ્ટ: વેટ, વેસ્ર્, લેસ્ર્, લેસ્ટ, ળેસ્ર્
        return 'west'
    elif re.match(r'.ેન', s) or re.fullmatch(r'સે(ટ્?)?[લ઱]', s.replace('-', '')):
        return 'central'                                    # સેન્ટ્રલ: સેલ, સે,-લ, સેટ્લ, સેન્્િ, વેન્્ર, શેન્્઱
    raise ValueError(f'unrecognised zone label {label!r}')


def _month_of(raw: Raw) -> tuple[int, int]:
    m = PDF_RE.search(raw.url)
    if m:
        return int(m.group(1)), int(m.group(2))
    if raw.meta.get('year') and raw.meta.get('month'):
        return int(raw.meta['year']), int(raw.meta['month'])
    raise ValueError(f'cannot tell the month of {raw.url!r}: expected .../WaterQuality/YYYY/MM.pdf')


_TOKEN = re.compile(r'(?<!\S)([૦-૯0-9][૦-૯0-9,]*|-)(?!\S)')


def _split(line: str) -> tuple[str, list[tuple[float, str]]]:
    """(label text before the first number, [(character-column centre, number token), ...])."""
    toks = [((m.start() + m.end()) / 2, m.group(1)) for m in _TOKEN.finditer(line)]
    return clean(line[:_TOKEN.search(line).start()] if toks else line), toks


def _line_up(toks: list[tuple[float, str]], centres: list[float]) -> list[str] | None:
    """Put each number in the column whose centre is nearest; None unless every column gets exactly one."""
    out: list[str | None] = [None] * len(centres)
    for pos, tok in toks:
        j = min(range(len(centres)), key=lambda k: abs(centres[k] - pos))
        if out[j] is not None or abs(centres[j] - pos) > 12:
            return None
        out[j] = tok
    return out if None not in out else None


def summary_rows(text: str) -> tuple[list[tuple[str, str, list]], int | None]:
    """(label, zone code, [taken, fit, unfit]) rows of the summary table, and the year printed in its heading.

    Normally a row is one line: label + three numbers. In a few PDFs pdftotext puts one number of a row on a
    line of its own just above or below (Dec 2014: North's 'taken' value). Such an orphan line is attached to
    the adjacent short row only if, by character column, its numbers fill exactly the missing columns
    (column centres come from the complete rows); otherwise parsing fails. validate() then checks the sums."""
    lines = text.splitlines()
    head = next((i for i, l in enumerate(lines) if re.search(r'(^|\s)ઝોન(\s|$)', l)), None)
    if head is None:
        raise ValueError('summary table header (ઝોન) not found')
    years = [int(y.translate(_GU_DIGITS)) for l in lines[:head] for y in _GU_YEAR.findall(l)]
    entries = []                                    # [label, tokens] of non-blank lines in the table area
    for line in lines[head + 1:]:
        if _DETAILS.search(line):
            break
        if line.strip():
            entries.append(list(_split(line)))
    full = [t for lab, t in entries if lab and len(t) == 3]
    centres = [sum(t[k][0] for t in full) / len(full) for k in range(3)] if full else None
    used: set[int] = set()
    rows = []
    for i, (label, toks) in enumerate(entries):
        if not label or not toks:
            continue                                # orphan numbers (handled below) or header text
        if len(toks) == 3:
            cells = [t for _, t in toks]
        else:
            cells = None
            orphans = [k for k in (i - 1, i + 1) if 0 <= k < len(entries) and not entries[k][0]
                       and entries[k][1] and k not in used]
            fits = []
            for combo in ([k] for k in orphans):
                lined = _line_up(toks + [t for k in combo for t in entries[k][1]], centres) if centres else None
                if lined:
                    fits.append((combo, lined))
            if len(fits) == 1:
                used.update(fits[0][0])
                cells = fits[0][1]
            if cells is None:
                raise ValueError(f'row {label!r} has {len(toks)} numbers and no unambiguous orphan line to complete it')
        code = _zone(label)
        rows.append((label, code, [num(c) for c in cells]))
        if code == 'total':
            break
    return rows, (years[-1] if years else None)


def parse_index(raw: Raw) -> Result:
    res = Result(complete_record_types=('document', 'wq_sampling_test'))
    for t in html_tables(raw.body):
        if t.rows and [c.lower() for c in t.rows[0][:3]] == ['stage', 'type of test', 'frequency']:
            for r in t.rows[1:]:
                stage, test, freq = (clean(c) for c in r[:3])
                key = re.sub(r'[^a-z0-9]+', '-', f'{stage}--{test}'.lower()).strip('-')
                res.records.append(Record('wq_sampling_test', key,
                                          {'stage': stage, 'test': test, 'frequency': freq, 'standard': 'IS:10500'}))
    seen = set()
    for url, _text in links(raw.body, URL):
        m = PDF_RE.search(url)
        if not m or url in seen:
            continue
        seen.add(url)
        y, mo = int(m.group(1)), int(m.group(2))
        res.records.append(Record('document', f'smc-water-quality-monthly/{y}-{mo:02d}', {
            'kind': 'water_quality_monthly_pdf', 'year': y, 'month': mo, 'url': url,
            'title': f'SMC Hydraulic: water samples collected and tested, {y}-{mo:02d}',
            'parsed': (y, mo) >= FIRST_MONTH and (y, mo) not in UNREADABLE,
            **({'not_parsed_because': UNREADABLE[(y, mo)]} if (y, mo) in UNREADABLE else {})}))
    return res


_DATE = re.compile(r'(?<![0-9])([0-9]{1,2})\s*[/\-.]\s*([0-9]{1,2})\s*[/\-.]\s*([0-9]{4})(?![0-9])')


def sample_month(text: str) -> tuple[int, int] | None:
    """Month of the unfit-sample dates listed after the summary (dates only; the addresses are not read).
    None if fewer than 5 dates; ValidationError if they do not fall (>= 90%) in one month."""
    m = _DETAILS.search(text)
    tail = (text[m.start():] if m else text).translate(_GU_DIGITS)
    c = Counter((int(yy), int(mm)) for _dd, mm, yy in _DATE.findall(tail) if 1 <= int(mm) <= 12)
    n = sum(c.values())
    if n < 5:
        return None
    ym, k = c.most_common(1)[0]
    if k < 0.9 * n:
        raise ValidationError(f'unfit-sample dates span several months: {dict(c.most_common(3))}')
    return ym


def parse_pdf(raw: Raw) -> Result:
    """Month: the PDF's own unfit-sample dates decide, because some PDFs are linked under the wrong month on
    the index page (2019/09.pdf is November 2019 and 2019/11.pdf is September; 2020/06 and 2020/07 are swapped;
    2020/04.pdf repeats May 2020) - in each case the printed heading agrees with the dates. Without at least
    5 dates the URL month is used. The heading year must match."""
    url_month = _month_of(raw)
    text = pdf_text(raw.body, layout=True)
    if not re.search(r'[૦-૯]', text):
        raise ValueError('no Gujarati digits in the PDF text (legacy non-Unicode font?)')
    rows, printed_year = summary_rows(text)
    y, mo = sample_month(text) or url_month
    if printed_year is None:
        raise ValueError('no year found in the PDF heading')
    if printed_year != y:
        raise ValidationError(f'PDF heading says {printed_year}, but the document month is {y}-{mo:02d}')
    if (y, mo) != url_month:
        log.warning('%s is linked as %d-%02d but its sample dates are %d-%02d; filed under the latter',
                    raw.url, *url_month, y, mo)
    start, end = month_period(y, mo)
    res = Result(geos=[SMC])
    zones_seen = set()
    for label, code, vals in rows:
        if code == 'total':
            level, gcode = 'smc_city', 'smc'
        else:
            level, gcode = 'smc_zone', code
            if code in zones_seen:
                raise ValueError(f'zone {code} appears twice ({label!r})')
            zones_seen.add(code)
            res.geos.append(EAST_UNDIVIDED if code == 'east' else zone_geo(code))
        for metric, v in zip(_COLS, vals):
            res.observations.append(Obs(metric, level, gcode, start, end, value=v,
                                        status='reported' if v is not None else 'not_reported'))
    return res


def parse(raw: Raw) -> Result:
    if raw.body[:5] == b'%PDF-' or PDF_RE.search(raw.url):
        return parse_pdf(raw)
    return parse_index(raw)


def fetch(ctx):
    idx = ctx.get(URL)
    yield idx
    reports = sorted({(int(m.group(1)), int(m.group(2)), url) for url, _ in links(idx.body, URL)
                      for m in [PDF_RE.search(url)] if m})
    today = ctx.now.date()
    for y, mo, url in reports:
        if (y, mo) < FIRST_MONTH or (y, mo) in UNREADABLE:
            continue
        age = (today.year - y) * 12 + (today.month - mo)
        raw = ctx.get(url, meta={'year': y, 'month': mo}, skip_if_seen=age > RECHECK_MONTHS, soft=True)
        if raw is not None:
            yield raw


def _close(a: float, b: float, rel: float = 0.02, floor: float = 5) -> bool:
    return abs(a - b) <= max(floor, rel * max(abs(a), abs(b)))


def validate(result: Result, raw: Raw) -> None:
    if not result.observations:      # index page
        docs = sum(r.record_type == 'document' for r in result.records)
        tests = sum(r.record_type == 'wq_sampling_test' for r in result.records)
        if docs < 100 or tests < 5:
            raise ValidationError(f'index page gave {docs} monthly PDF links and {tests} sampling rows; '
                                  'layout may have changed')
        return
    by = {(o.geo_code, o.metric_id): o.value for o in result.observations}
    zones = {o.geo_code for o in result.observations if o.geo_level == 'smc_zone'}
    if frozenset(zones) not in ZONE_LAYOUTS:
        raise ValidationError(f'unexpected set of zones {sorted(zones)}')
    if ('smc', 'wq.tap_samples_collected') not in by:
        raise ValidationError('no total row')
    for z in zones | {'smc'}:
        taken, fit, unfit = (by.get((z, m)) for m in _COLS)
        if taken is not None and not (0 < taken <= (60_000 if z == 'smc' else 10_000)):
            raise ValidationError(f'implausible samples taken {taken} in {z}')
        if None not in (taken, fit, unfit) and not _close(fit + unfit, taken, floor=2):
            raise ValidationError(f'{z}: fit {fit} + unfit {unfit} != taken {taken} (columns misread?)')
        if None not in (taken, unfit) and unfit > taken:
            raise ValidationError(f'{z}: unfit {unfit} > taken {taken}')
    for m in _COLS:
        total = by.get(('smc', m))
        parts = [by.get((z, m)) for z in zones]
        if total is not None and None not in parts and not _close(sum(parts), total):
            raise ValidationError(f'{m}: zones add up to {sum(parts)}, total row says {total}')
    start = result.observations[0].period_start
    if raw is not None and start > raw.retrieved_at[:10]:
        raise ValidationError(f'month {start} is after the fetch date {raw.retrieved_at[:10]}')

