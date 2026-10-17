"""GSEB board-exam results for Surat district: SSC (class 10) and HSC (class 12, science and general).

Documents: the result-statistics booklets GSEB publishes on results day, in a per-year S3 bucket:
    https://gsebweb<YEAR>.s3.ap-south-1.amazonaws.com/pdf/sscbooklet.pdf   SSC (class 10), Feb-March exam
    https://gsebweb<YEAR>.s3.ap-south-1.amazonaws.com/pdf/scibooklet.pdf   HSC science stream
    https://gsebweb<YEAR>.s3.ap-south-1.amazonaws.com/pdf/genbooklet.pdf   HSC general stream (with the
                                                                           vocational and Uchchatar Uttar
                                                                           Buniyadi streams, as GSEB combines them)
(all three, plus *purakbooklet.pdf for the June supplementary exams, were in the 2026 bucket on 2026-10-05).
A booklet never changes once published, so each is downloaded once (skip_if_seen). fetch() asks for the
current exam year from 1 May (results come out in early May; 2026: SSC 6 May, HSC 4 May) and treats a
404 as "not published yet". GSEB_YEARS="2025,2026" overrides the years for a one-off backfill.

What is read (regular candidates; the booklets' district tables are for regular candidates):
  SSC   p.10-11 district table   "SURAT  regd appeared A-1 A-2 B-1 B-2 C-1 C-2 D E1* E1 E2 EQC PER."
        p.12   district pass % for the exam year and the two before ("30. 68 SURAT 86.04% 86.20% 86.75%")
        p.15+  centre-wise table "6810 6810 SURAT RANDER  regd appeared passed  2026%  2025%  change"
  HSC   "DISTRICTWISE GRADEWISE" table "18-SURAT regd app A1 A2 B1 B2 C1 C2 D E1 N.I. %age"
        district E.Q.C. table "18 SURAT 13,786"
        centre-wise table "1806 RANDER (SURAT) regd appeared E.Q.C. N.I. percentage"
"Passed" is GSEB's E.Q.C. (eligible for qualifying certificate). Checked on the 2026 booklets: for SSC,
A1..D plus E1* (differently-abled candidates passing with the 20% concession) = EQC and EQC + E1 + E2 =
appeared; for HSC, A1..E1 = E.Q.C. and %age = E.Q.C./appeared. HSC N.I. (needs improvement) is not
stored: it equals registered minus E.Q.C., so it counts absentees too.

Geography:
  - district rows -> surat_district/surat (SSC district 68 and HSC district 18 are Surat; Tapi, split
    off in 2007, is its own district in both booklets).
  - centre rows -> new geo level `exam_centre` (code "gseb-ssc-6810", "gseb-hsc-1806"), parent
    surat_district. A GSEB centre (kendra) groups the schools examined there; it is not an
    administrative area, and whether it lies inside SMC limits is not determined here. HSC science and
    general booklets use the same centre numbers (1802 SURAT, 1807 NANPURA (SURAT), ...), so they share a
    geo; SSC centres are numbered separately. Centre totals do not add up exactly to the district row
    (2026 SSC: 82,399 vs 82,306 registered), presumably because the district table counts candidates by
    school district and the centre table by where they sat; both are stored as published.
  - Name markers such as "(^^)" or "($)" (the year a centre opened, per the SSC legend) are dropped
    from centre names.

Periods: the calendar year of the main (February-March) examination, e.g. 2026-01-01..2026-12-31.
The SSC booklet's pass % for the two previous years and each centre's previous-year pass % are stored
for those years too.
"""
from __future__ import annotations

import os
import re
from collections import Counter

from ..model import FetchError, Geo, Metric, Obs, Raw, Result, Source, ValidationError
from ..parse import num, pdf_text, year_period
from ..surat import SURAT_DISTRICT

BUCKET = 'https://gsebweb{year}.s3.ap-south-1.amazonaws.com/pdf/{file}'
BOOKLETS = (('ssc', 'sscbooklet.pdf'), ('hsc_science', 'scibooklet.pdf'), ('hsc_general', 'genbooklet.pdf'))
RESULTS_MONTH = 5           # booklets appear in early May
FIRST_YEAR = 2015
PCT_TOLERANCE = 0.011    # printed with 2 decimals (rounded, or possibly truncated)

M = 'gseb.'
REG, APP, PASS, PCT, GRADE = M + 'registered', M + 'appeared', M + 'passed', M + 'pass_pct', M + 'candidates_by_grade'

SOURCE = Source(
    id='gseb_results',
    name='GSEB SSC and HSC board-exam results, Surat district and exam centres (annual)',
    publisher='Gujarat Secondary and Higher Secondary Education Board (GSEB), Gandhinagar',
    url='https://www.gseb.org/',
    module='education',
    cadence='annual',
    interval_hours=24 * 7,      # overridden by interval_hours(now): daily in May-June
    geo_note='Surat district (GSEB district tables) and GSEB exam centres in Surat district (geo level exam_centre)',
    licence_note='Government of Gujarat (GSEB) result booklets; public information',
    notes='Regular candidates only. Period = calendar year of the Feb-March main exam. dims.exam is ssc, '
          'hsc_science or hsc_general. Centre totals differ slightly from district totals as published.',
    metrics=(
        Metric(REG, 'Board-exam candidates registered', 'candidates',
               'Regular candidates registered for the main examination (dims.exam).'),
        Metric(APP, 'Board-exam candidates appeared', 'candidates',
               'Regular candidates who appeared (dims.exam).'),
        Metric(PASS, 'Board-exam candidates passed', 'candidates',
               'Regular candidates eligible for the certificate (GSEB "E.Q.C."), i.e. passed (dims.exam).'),
        Metric(PCT, 'Board-exam pass percentage', '%',
               'GSEB result percentage: passed (E.Q.C.) / appeared x 100, as printed (dims.exam).'),
        Metric(GRADE, 'Board-exam candidates by grade', 'candidates',
               'District candidates by grade as printed (dims.grade). SSC: A1..D and E1* (differently-abled, '
               'passed with the 20% concession) are passes, E1 and E2 are not. HSC: A1..E1 add up to E.Q.C.'),
    ),
)


# ---------- fetching ----------

def exam_years(now) -> list[int]:
    env = os.environ.get('GSEB_YEARS', '').strip()
    if env:
        return sorted({int(y) for y in re.split(r'[,\s]+', env) if y})
    return [now.year if now.month >= RESULTS_MONTH else now.year - 1]


def interval_hours(now) -> float:
    return 24 if RESULTS_MONTH <= now.month <= RESULTS_MONTH + 1 else 24 * 7


def fetch(ctx):
    first_error = None
    for year in exam_years(ctx.now):
        for exam, file in BOOKLETS:
            url = BUCKET.format(year=year, file=file)
            try:
                raw = ctx.get(url, meta={'exam': exam, 'year': year}, skip_if_seen=True)
            except FetchError as e:
                if e.http_status == 404:
                    ctx.log.info('%s %s booklet not published (404): %s', year, exam, url)
                    continue
                if e.blocked:
                    raise
                ctx.log.error('fetch failed for %s %s: %s', year, exam, e)
                first_error = first_error or e
                continue
            if raw is not None:
                yield raw
    if first_error is not None:
        raise first_error


# ---------- parsing ----------

_MARKER = re.compile(r'\s*\((?:[#$@&^*%]\s*)+\)\s*$')
_INT = r'\d[\d,]*'
_DASH = '[–—-]'


def _int(s: str) -> int:
    return int(num(s))


def centre_geo(exam: str, code: str, name: str) -> Geo:
    kind = 'ssc' if exam == 'ssc' else 'hsc'
    return Geo('exam_centre', f'gseb-{kind}-{code}', f'{name} (GSEB {kind.upper()} centre {code})',
               'surat_district', 'surat',
               note='GSEB examination centre (kendra) in Surat district as listed in the GSEB result booklet; '
                    'groups the schools examined there, not an administrative area.')


def detect_exam(text: str) -> str:
    if re.search(r'A-1\s+A-2\s+B-1.*\bEQC\b', text):
        return 'ssc'
    if 'DISTRICTWISE GRADEWISE' in text:
        if 'GUJCET' in text:
            return 'hsc_science'
        if 'H.S.C.E.' in text:
            return 'hsc_general'
    raise ValidationError('not a recognised GSEB SSC/HSC result booklet')


def text_year(text: str, exam: str) -> int | None:
    if exam == 'ssc':
        m = re.search(r'(?m)^\D*\b(20\d\d)\s{2,}(20\d\d)\s{2,}(20\d\d)\s*$', text)
        return int(m.group(1)) if m else None
    years = Counter(re.findall(r'-\s?(20\d\d)\b', text))
    return int(years.most_common(1)[0][0]) if years else None


def _year(raw: Raw, text: str, exam: str) -> int:
    found = text_year(text, exam)
    year = raw.meta.get('year')
    if year is None:
        m = re.search(r'gsebweb(20\d\d)', raw.url or '')
        year = int(m.group(1)) if m else found
    if year is None:
        raise ValidationError('exam year unknown: pass meta year or a gsebweb<YEAR> URL')
    year = int(year)
    if found is not None and found != year:
        raise ValidationError(f'booklet text says {found}, expected {year}')
    return year


def parse(raw: Raw) -> Result:
    text = pdf_text(raw.body)
    exam = detect_exam(text)
    if raw.meta.get('exam') and raw.meta['exam'] != exam:
        raise ValidationError(f'expected the {raw.meta["exam"]} booklet, the text looks like {exam}')
    year = _year(raw, text, exam)
    res = Result(geos=[SURAT_DISTRICT])
    (_ssc if exam == 'ssc' else _hsc)(text, exam, year, res)
    return res


def _district(res, exam, year, regd, app, passed, pct, grades):
    start, end = year_period(year)
    d = {'exam': exam}
    for metric, v in ((REG, regd), (APP, app), (PASS, passed), (PCT, pct)):
        res.observations.append(Obs(metric, 'surat_district', 'surat', start, end, value=float(v), dims=d))
    for g, v in grades.items():
        res.observations.append(Obs(GRADE, 'surat_district', 'surat', start, end, value=float(v),
                                    dims={'exam': exam, 'grade': g}))


def _centre(res, exam, year, code, name, regd, app, passed, pct):
    name = _MARKER.sub('', name).strip()
    if not re.search(r'[A-Za-z]', name):
        raise ValidationError(f'centre {code} has no name')
    geo = centre_geo(exam, code, name)
    res.geos.append(geo)
    start, end = year_period(year)
    for metric, v in ((REG, regd), (APP, app), (PASS, passed), (PCT, pct)):
        res.observations.append(Obs(metric, 'exam_centre', geo.geo_code, start, end, value=float(v),
                                    dims={'exam': exam}))
    return geo


def _ssc(text: str, exam: str, year: int, res: Result) -> None:
    lines = text.splitlines()
    # 1. district table: header row with the grade columns, then "SURAT" + 13 integers + PER.
    hdr = [i for i, ln in enumerate(lines)
           if re.search(r'A-1\s+A-2\s+B-1\s+B-2\s+C-1\s+C-2\s+D\s+E1\*\s+E1\s+E2\s+EQC\s+PER\.', ln)]
    if len(hdr) != 1:
        raise ValidationError(f'SSC district table header found {len(hdr)} times')
    rows = [re.match(r'^\s*SURAT\s+((?:\d+\s+){13})(\d+\.\d+)%\s*$', ln) for ln in lines[hdr[0]:hdr[0] + 120]]
    rows = [m for m in rows if m]
    if len(rows) != 1:
        raise ValidationError(f'SURAT row of the SSC district table found {len(rows)} times')
    v = [int(x) for x in rows[0].group(1).split()]
    grades = dict(zip(('A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'D', 'E1*', 'E1', 'E2'), v[2:12]))
    _district(res, exam, year, v[0], v[1], v[12], float(rows[0].group(2)), grades)

    # 2. district pass % for this year and the two before, under a "2026 2025 2024" header
    years, hist, hist_years, code = None, None, None, None
    for ln in lines:
        h = re.search(r'\b(20\d\d)\s{2,}(20\d\d)\s{2,}(20\d\d)\s*$', ln)
        if h:
            years = [int(y) for y in h.groups()]
        m = re.search(r'\b\d{1,2}\.\s+(\d{2})\s+SURAT\s+(\d+\.\d+)%\s+(\d+\.\d+)%\s+(\d+\.\d+)%', ln)
        if m:
            if hist is not None:
                raise ValidationError('SURAT appears twice in the SSC district pass % table')
            code, hist = m.group(1), [float(x) for x in m.groups()[1:]]
            hist_years = years
    if hist is None or not hist_years:
        raise ValidationError('SSC district pass % history (e.g. "30. 68 SURAT 86.04% ...") not found')
    if hist_years != [year, year - 1, year - 2]:
        raise ValidationError(f'SSC pass % history covers {hist_years}, expected {year}..{year - 2}')
    for y, pct in zip(hist_years[1:], hist[1:]):
        s, e = year_period(y)
        res.observations.append(Obs(PCT, 'surat_district', 'surat', s, e, value=pct, dims={'exam': exam}))
    if abs(hist[0] - float(rows[0].group(2))) > 0.001:
        raise ValidationError(f'SSC pass % {hist[0]} in the history table vs {rows[0].group(2)} in the district table')

    # 3. centres of district <code>: "6810 6810 SURAT RANDER 2747 2730 2408 88.21% 86.91% 1.30%"
    if not any(re.match(rf'^\s*{code}\s+SURAT\s*$', ln) for ln in lines):
        raise ValidationError(f'SSC centre section heading "{code} SURAT" not found')
    pat = re.compile(rf'^\s*({code}\d\d)\s+\1\s+(.+?)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+\.\d+)%\s+'
                     rf'(?:(\d+\.\d+)%|{_DASH})\s+(?:-?\d+\.\d+%|{_DASH})\s*$')
    prev_s, prev_e = year_period(year - 1)
    for ln in lines:
        m = pat.match(ln)
        if not m:
            continue
        geo = _centre(res, exam, year, m.group(1), m.group(2), int(m.group(3)), int(m.group(4)),
                      int(m.group(5)), float(m.group(6)))
        prev = float(m.group(7)) if m.group(7) else None
        res.observations.append(Obs(PCT, 'exam_centre', geo.geo_code, prev_s, prev_e, value=prev,
                                    status='reported' if prev is not None else 'not_reported', dims={'exam': exam}))


def _hsc(text: str, exam: str, year: int, res: Result) -> None:
    lines = text.splitlines()
    # 1. "DISTRICTWISE GRADEWISE" table: 18-SURAT regd app A1 A2 B1 B2 C1 C2 D E1 N.I. %age
    if not re.search(r'\bA1\s+A2\s+B1\s+B2\s+C1\s+C2\s+D\s+E1\b', text):
        raise ValidationError('HSC grade-wise table header (A1 A2 B1 B2 C1 C2 D E1) not found')
    rows = [re.match(r'^\s*(\d{1,2})-SURAT\s+((?:\d+\s+){11})(\d+\.\d+)\s*$', ln) for ln in lines]
    rows = [m for m in rows if m]
    if len(rows) != 1:
        raise ValidationError(f'SURAT row of the HSC district grade-wise table found {len(rows)} times')
    code = rows[0].group(1)
    v = [int(x) for x in rows[0].group(2).split()]
    grades = dict(zip(('A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'D', 'E1'), v[2:10]))

    # 2. district E.Q.C. count: "18 SURAT 13,786"
    eqc = [re.match(rf'^\s*{code}\s+SURAT\s+({_INT})\s*$', ln) for ln in lines]
    eqc = [m for m in eqc if m]
    if len(eqc) != 1:
        raise ValidationError(f'SURAT row of the HSC district E.Q.C. table found {len(eqc)} times')
    _district(res, exam, year, v[0], v[1], _int(eqc[0].group(1)), float(rows[0].group(3)), grades)

    # 3. centres: "1806 RANDER (SURAT) 1685 1683 1521 164 90.37"
    if not re.search(r'Cent No\s+Centre Name\s+Regd\.\s+Appeared\s+E\.Q\.C\.\s+N\.I\.\s+Percentage', text):
        raise ValidationError('HSC centre-wise table header not found')
    pat = re.compile(rf'^\s*({code}\d\d)\s+(.+?)\s+({_INT})\s+({_INT})\s+({_INT})\s+({_INT})\s+(\d+\.\d+)\s*$')
    for ln in lines:
        m = pat.match(ln)
        if m:
            _centre(res, exam, year, m.group(1), m.group(2), _int(m.group(3)), _int(m.group(4)),
                    _int(m.group(5)), float(m.group(7)))


# ---------- validation ----------

def validate(result: Result, raw: Raw) -> None:
    obs = result.observations
    exams = {o.dims['exam'] for o in obs}
    if len(exams) != 1:
        raise ValidationError(f'one booklet must hold one exam, got {sorted(exams)}')
    exam = exams.pop()
    year = max(int(o.period_start[:4]) for o in obs)
    if not FIRST_YEAR <= year <= (int(raw.retrieved_at[:4]) if raw is not None else 9999):
        raise ValidationError(f'implausible exam year {year}')
    cur = f'{year}-01-01'
    dist = {o.metric_id: o.value for o in obs
            if o.geo_level == 'surat_district' and o.period_start == cur and o.metric_id != GRADE}
    if set(dist) != {REG, APP, PASS, PCT}:
        raise ValidationError(f'district figures incomplete: {sorted(dist)}')
    regd, app, passed, pct = dist[REG], dist[APP], dist[PASS], dist[PCT]
    if not 1000 <= regd <= 300_000:
        raise ValidationError(f'implausible district registrations {regd}')
    if not passed <= app <= regd:
        raise ValidationError(f'district counts out of order: passed {passed}, appeared {app}, registered {regd}')
    if abs(passed / app * 100 - pct) > PCT_TOLERANCE:
        raise ValidationError(f'district pass % {pct} does not match {passed}/{app}')
    g = {o.dims['grade']: o.value for o in obs if o.metric_id == GRADE}
    if exam == 'ssc':
        if sum(g[k] for k in ('A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'D', 'E1*')) != passed:
            raise ValidationError('SSC grades A1..D + E1* do not add up to EQC')
        if passed + g['E1'] + g['E2'] != app:
            raise ValidationError('SSC EQC + E1 + E2 does not add up to appeared')
    elif sum(g.values()) != passed and sum(v for k, v in g.items() if k != 'E1') != passed:
        raise ValidationError(f'HSC grades add up to {sum(g.values())}, E.Q.C. is {passed}')
    centres: dict[str, dict] = {}
    for o in obs:
        if o.geo_level == 'exam_centre' and o.period_start == cur:
            centres.setdefault(o.geo_code, {})[o.metric_id] = o.value
    if len(centres) < 5:
        raise ValidationError(f'only {len(centres)} Surat exam centres parsed')
    for code, c in centres.items():
        if not c[PASS] <= c[APP] <= c[REG] or c[APP] == 0:
            raise ValidationError(f'centre {code}: counts out of order {c}')
        if abs(c[PASS] / c[APP] * 100 - c[PCT]) > PCT_TOLERANCE:
            raise ValidationError(f'centre {code}: pass % {c[PCT]} does not match {c[PASS]}/{c[APP]}')
    total_app = sum(c[APP] for c in centres.values())
    if abs(total_app - app) > 0.05 * app:
        raise ValidationError(f'centres add up to {total_app} appeared, district row says {app}')
    for o in obs:
        if o.metric_id != PCT or o.value is None:
            continue
        lo = 20 if o.geo_level == 'surat_district' else 0      # a single centre can legitimately score very low
        if not lo <= o.value <= 100:
            raise ValidationError(f'implausible pass % {o.value} at {o.geo_code} {o.period_start}')
