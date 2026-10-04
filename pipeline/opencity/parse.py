"""Parsing helpers for adapters: HTML tables, PDF text, numbers and dates.

Standard library only (plus the `pdftotext` command from poppler-utils).
"""
from __future__ import annotations

import calendar
import html as htmllib
import re
import subprocess
import tempfile
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from html.parser import HTMLParser

# ---------- numbers ----------

_GU_DIGITS = str.maketrans('૦૧૨૩૪૫૬૭૮૯', '0123456789')
_DEV_DIGITS = str.maketrans('०१२३४५६७८९', '0123456789')
_MISSING = {'', '-', '--', '—', '–', 'na', 'n.a.', 'n/a', 'nil', 'null', 'none', '*', 'nr', 'not reported'}


def num(s) -> float | None:
    """Parse '1,23,456.70', '(12)', '૧૨૩', '45%', '₹ 1.2' -> float. Missing markers -> None.
    Raises ValueError for text that is not a number, so bad parses fail loudly."""
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return float(s)
    t = str(s).translate(_GU_DIGITS).translate(_DEV_DIGITS).strip()
    t = t.replace('\xa0', ' ').replace('₹', '').replace('Rs.', '').replace('Rs', '').strip()
    if t.lower() in _MISSING:
        return None
    neg = t.startswith('(') and t.endswith(')')
    t = t.strip('()').replace(',', '').replace(' ', '').rstrip('%')
    if t.startswith('+'):
        t = t[1:]
    v = float(t)
    return -v if neg else v


def num_or_none(s) -> float | None:
    """Like num() but returns None instead of raising."""
    try:
        return num(s)
    except (ValueError, TypeError):
        return None


# ---------- dates and periods ----------

MONTHS = {m.lower(): i for i, m in enumerate(calendar.month_name) if m}
MONTHS.update({m.lower(): i for i, m in enumerate(calendar.month_abbr) if m})
MONTHS.update({'sept': 9, 'june': 6, 'july': 7})


def month_no(name: str) -> int:
    return MONTHS[name.strip().lower().rstrip('.')]


def month_period(year: int, month: int) -> tuple[str, str]:
    last = calendar.monthrange(year, month)[1]
    return date(year, month, 1).isoformat(), date(year, month, last).isoformat()


def year_period(year: int) -> tuple[str, str]:
    return f'{year}-01-01', f'{year}-12-31'


def fy_period(start_year: int) -> tuple[str, str]:
    """Indian financial year April-March: fy_period(2025) -> 2025-04-01..2026-03-31."""
    return f'{start_year}-04-01', f'{start_year + 1}-03-31'


def fy_start(label: str) -> int:
    """'2025-26', '2025-2026', 'FY 2025-26', '2025/26' -> 2025."""
    m = re.search(r'(20\d\d|19\d\d)\s*[-/–]\s*(\d{2,4})', label)
    if not m:
        raise ValueError(f'not a financial-year label: {label!r}')
    return int(m.group(1))


def quarter_of_fy(start_year: int, q: int) -> tuple[str, str]:
    """Quarter q (1..4) of FY starting April start_year."""
    m0 = 4 + 3 * (q - 1)
    y = start_year + (1 if m0 > 12 else 0)
    m0 = (m0 - 1) % 12 + 1
    return month_period(y, m0)[0], month_period(y, m0 + 2)[1]


def parse_date(s: str, *fmts: str) -> date:
    s = s.strip()
    for f in fmts or ('%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y', '%Y-%m-%d', '%d %B %Y', '%d %b %Y', '%d-%b-%Y'):
        try:
            return datetime.strptime(s, f).date()
        except ValueError:
            continue
    raise ValueError(f'unparsed date {s!r}')


def parse_dt(s: str, *fmts: str) -> str:
    """'27/09/2026 24:00' -> '2026-09-28T00:00'. Returns ISO local datetime (minutes)."""
    s = s.strip()
    m = re.match(r'(.*\d)\s+24:00(?::00)?$', s)
    if m:   # "24:00" means midnight at the end of that day
        d = parse_date(m.group(1))
        return (datetime(d.year, d.month, d.day) + timedelta(days=1)).isoformat(timespec='minutes')
    for f in fmts or ('%d/%m/%Y %H:%M', '%d-%m-%Y %H:%M', '%Y-%m-%d %H:%M', '%d/%m/%Y %H:%M:%S', '%d-%m-%Y %H:%M:%S'):
        try:
            return datetime.strptime(s, f).isoformat(timespec='minutes')
        except ValueError:
            continue
    raise ValueError(f'unparsed datetime {s!r}')


def month_year(label: str) -> tuple[int, int]:
    """'July-2026', 'Jul 2026', 'July, 2026' -> (2026, 7)."""
    m = re.match(r'\s*([A-Za-z]+)\.?[\s,\-/]*(\d{4})\s*$', label)
    if not m:
        raise ValueError(f'not a month-year label: {label!r}')
    return int(m.group(2)), month_no(m.group(1))


# ---------- text ----------

def clean(s: str | None) -> str:
    if s is None:
        return ''
    return re.sub(r'\s+', ' ', htmllib.unescape(s).replace('\xa0', ' ')).strip()


def html_text(html: str) -> str:
    t = re.sub(r'(?is)<(script|style|noscript)[^>]*>.*?</\1>', ' ', html)
    t = re.sub(r'(?i)<br\s*/?>|</p>|</div>|</tr>|</li>|</h\d>', '\n', t)
    t = re.sub(r'(?s)<[^>]+>', ' ', t)
    return '\n'.join(clean(line) for line in htmllib.unescape(t).splitlines() if clean(line))


# ---------- HTML tables ----------

@dataclass
class Table:
    rows: list[list[str]]                 # cell text, colspan/rowspan expanded
    caption: str = ''                     # <caption> text, if any
    heading: str = ''                     # nearest heading/bold text before the table
    links: list[list[list[str]]] = field(default_factory=list)   # hrefs per cell
    attrs: dict = field(default_factory=dict)

    def find_row(self, *needles: str) -> int:
        """Index of the first row containing all needles (case-insensitive)."""
        for i, r in enumerate(self.rows):
            j = ' | '.join(r).lower()
            if all(n.lower() in j for n in needles):
                return i
        return -1


class _TableParser(HTMLParser):
    _HEAD = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'b', 'legend', 'label', 'span', 'p', 'div'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables: list[Table] = []
        self._stack: list[dict] = []      # open tables (nested tables supported)
        self._text_since_table: list[str] = []
        self._in_caption = False

    # table state: rows (list of list of (text, colspan, rowspan, links)), cur row, cur cell
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'table':
            heading = clean(' '.join(self._text_since_table[-8:]))[-200:]
            self._stack.append({'rows': [], 'row': None, 'cell': None, 'caption': [], 'heading': heading, 'attrs': a})
            self._text_since_table = []
        elif not self._stack:
            return
        elif tag == 'caption':
            self._in_caption = True
        elif tag == 'tr':
            self._stack[-1]['row'] = []
        elif tag in ('td', 'th'):
            t = self._stack[-1]
            if t['row'] is None:
                t['row'] = []
            t['cell'] = {'text': [], 'colspan': _int(a.get('colspan')), 'rowspan': _int(a.get('rowspan')), 'links': []}
        elif tag == 'a' and self._stack[-1]['cell'] is not None and a.get('href'):
            self._stack[-1]['cell']['links'].append(a['href'])
        elif tag == 'br' and self._stack[-1]['cell'] is not None:
            self._stack[-1]['cell']['text'].append(' ')

    def handle_endtag(self, tag):
        if not self._stack:
            return
        t = self._stack[-1]
        if tag == 'caption':
            self._in_caption = False
        elif tag in ('td', 'th') and t['cell'] is not None:
            if t['row'] is None:
                t['row'] = []
            t['row'].append(t['cell'])
            t['cell'] = None
        elif tag == 'tr' and t['row'] is not None:
            if t['cell'] is not None:
                t['row'].append(t['cell'])
                t['cell'] = None
            t['rows'].append(t['row'])
            t['row'] = None
        elif tag == 'table':
            if t['row']:
                t['rows'].append(t['row'])
            self._stack.pop()
            self.tables.append(_expand(t))

    def handle_data(self, data):
        if self._stack:
            t = self._stack[-1]
            if self._in_caption:
                t['caption'].append(data)
            elif t['cell'] is not None:
                t['cell']['text'].append(data)
        else:
            if data.strip():
                self._text_since_table.append(data)
                if len(self._text_since_table) > 40:
                    self._text_since_table = self._text_since_table[-20:]


def _int(v) -> int:
    try:
        return max(1, int(str(v).strip()))
    except (TypeError, ValueError):
        return 1


def _expand(t: dict) -> Table:
    grid: list[list[str]] = []
    links: list[list[list[str]]] = []
    pending: dict[tuple[int, int], tuple[str, list]] = {}
    for r, row in enumerate(t['rows']):
        out, outl, c = [], [], 0
        cells = iter(row)
        cell = next(cells, None)
        while cell is not None or (r, c) in pending:
            if (r, c) in pending:
                txt, lk = pending.pop((r, c))
                out.append(txt)
                outl.append(lk)
                c += 1
                continue
            txt = clean(''.join(cell['text']))
            for dr in range(cell['rowspan']):
                for dc in range(cell['colspan']):
                    if dr == 0 and dc == 0:
                        continue
                    if dr == 0:
                        continue
                    pending[(r + dr, c + dc)] = (txt, cell['links'])
            for dc in range(cell['colspan']):
                out.append(txt)
                outl.append(cell['links'])
            c += cell['colspan']
            cell = next(cells, None)
        grid.append(out)
        links.append(outl)
    return Table(rows=grid, caption=clean(''.join(t['caption'])), heading=t['heading'], links=links, attrs=t['attrs'])


def html_tables(html: str | bytes) -> list[Table]:
    if isinstance(html, bytes):
        html = html.decode('utf-8', errors='replace')
    p = _TableParser()
    p.feed(html)
    p.close()
    return p.tables


def links(html: str | bytes, base: str = '') -> list[tuple[str, str]]:
    """All <a href> as (absolute_url, link_text)."""
    from urllib.parse import urljoin
    if isinstance(html, bytes):
        html = html.decode('utf-8', errors='replace')
    out = []
    for m in re.finditer(r'(?is)<a\b[^>]*?href\s*=\s*["\']([^"\']+)["\'][^>]*>(.*?)</a>', html):
        out.append((urljoin(base, htmllib.unescape(m.group(1).strip())), clean(re.sub(r'<[^>]+>', ' ', m.group(2)))))
    return out


# ---------- PDF ----------

def pdf_text(body: bytes, *, layout: bool = True, first: int | None = None, last: int | None = None) -> str:
    """Text of a PDF via poppler's pdftotext. Raises RuntimeError if pdftotext is missing or fails."""
    with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp:
        tmp.write(body)
        tmp.flush()
        cmd = ['pdftotext', '-enc', 'UTF-8']
        if layout:
            cmd.append('-layout')
        if first:
            cmd += ['-f', str(first)]
        if last:
            cmd += ['-l', str(last)]
        cmd += [tmp.name, '-']
        try:
            r = subprocess.run(cmd, capture_output=True, timeout=300)
        except FileNotFoundError:
            raise RuntimeError('pdftotext not found: install poppler-utils') from None
        if r.returncode != 0:
            raise RuntimeError(f'pdftotext failed: {r.stderr.decode(errors="replace")[:300]}')
        return r.stdout.decode('utf-8', errors='replace')
