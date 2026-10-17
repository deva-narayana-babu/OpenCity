"""SMC Revenue-Capital Budget Summary: zone-wise budget vs actuals, updated weekly.

Page: https://www.suratmunicipal.gov.in/Departments/Accounts/CapitalRevenueBudgetSummary
  Heading "Revenue-Capital Budget Summary (Rs. in '000) for <zone>", a zone <select id="drpZone"> (0 = All Zone,
  1 = Head Quarter, 2..10 = the nine zones), "Weekly Update (Last on 27/09/2026)", and an EMPTY table #dtBudget whose
  <thead> names the columns, e.g.
    Description | Actuals 24-25 | Original 25-26 | Revised 25-26 | Actuals (Tent.) 25-26 | % of Rev. 25-26 |
    Original 26-27 | Actuals (Tent.) 26-27 | % of Ori.26-27
  The rows are loaded by DataTables (server-side mode) from the endpoint named in the inline script
  ("SearchBy": "/Departments/getBudgetSummary", "BudgetYear": "2026"). The page's own script bundle
  (/bundles/BudgetZoneName) maps the JSON fields to the columns in this order:
    Description, PreviousYearActual2, PreviousYearOriginal1, PreviousYearRevised1, PreviousYearActual1, item5,
    item6, CurrentYearActuals, item8
  and $.fn.dataTable.pipeline sends a plain GET with the standard DataTables parameters (draw, columns[i][...],
  start=0, length=10, search[...]) plus CustomData[BudgetYear] and CustomData[ZoneCode]. fetch() sends exactly those
  parameters, with no cookies and no extra headers (no X-Requested-With, Origin or Referer); the server answers
  with JSON {"data": [4 rows], "status": 200, ...}. Without the DataTables parameters it redirects to /Error.html.

Each zone's JSON has four rows: Revenue Income, Revenue Expense, Capital Income, Capital Expense.

Stored (unit INR = Rs '000 x 1000):
  finance.budget_summary.income / .expenditure, dims {account: revenue|capital, measure: ...}
    measure budget_original   "Original YY-YY"            period = that financial year
            budget_revised    "Revised YY-YY"             period = that financial year
            actual            "Actuals YY-YY"             period = that financial year
            actual_tentative  "Actuals (Tent.) YY-YY"     a past financial year (unaudited, may still be revised)
            actual_ytd        "Actuals (Tent.) YY-YY"     the current budget year: cumulative actuals from 1 April to
                                                          the page's "Last on" date (period_end = that date), so
                                                          each weekly update is its own observation
  geo: All Zone -> smc_city/smc; Head Quarter -> smc_zone/hq; zones via surat.zone_code().
  CAVEAT: on the 2026-10-03 data "All Zone" equals Head Quarter + the seven zones with selector values 2-8 (West,
  Central, North, East-A, South-A, Athwa, South East) in every cell; the East Zone-B and South Zone-B (Kanakpur)
  figures are NOT included in it. Whether they are missing from the corporation total or also booked under
  East-A/South-A cannot be told from the page. "All Zone" is stored as published; do not expect the zones to add up
  to it, and do not add East-B/South-B to it either.
  The "%" columns are ratios of the stored columns; they are not stored but are used to check the column mapping.

The drill-down to budget centres (param() -> SetCapitalRevenueBCNT_Param -> CapitalRevenueBCNT) keeps the selection in
the server session and is not fetched.
"""
from __future__ import annotations

import json
import logging
import re
from urllib.parse import urljoin

from ..model import FetchError, Metric, Obs, Raw, Result, Source, ValidationError
from ..parse import clean, fy_period, html_tables, html_text, parse_date
from ..surat import SMC, zone_code, zone_geo

log = logging.getLogger('opencity.sources.smc_budget_summary')

PAGE_URL = 'https://www.suratmunicipal.gov.in/Departments/Accounts/CapitalRevenueBudgetSummary'
FIELDS = ('Description', 'PreviousYearActual2', 'PreviousYearOriginal1', 'PreviousYearRevised1',
          'PreviousYearActual1', 'item5', 'item6', 'CurrentYearActuals', 'item8')
INCOME = 'finance.budget_summary.income'
EXPENDITURE = 'finance.budget_summary.expenditure'

_DIMS_NOTE = ('dims.account: revenue | capital. dims.measure: budget_original ("Original"), budget_revised '
              '("Revised"), actual ("Actuals"), actual_tentative ("Actuals (Tent.)" of a past year) or actual_ytd '
              '("Actuals (Tent.)" of the current budget year, cumulative from 1 April to period_end = the page\'s '
              'weekly "Last on" date). Published in Rs \'000; stored in rupees.')

SOURCE = Source(
    id='smc_budget_summary',
    name='SMC revenue and capital budget vs actuals by zone (weekly)',
    publisher='Surat Municipal Corporation, Accounts Department',
    url=PAGE_URL,
    module='finance',
    cadence='weekly',
    interval_hours=24 * 7 - 12,     # the page says "Weekly Update"; 2026-09-27 was a Sunday
    geo_note='SMC city ("All Zone") plus Head Quarter and the nine administrative zones',
    licence_note='Surat Municipal Corporation web page (data loaded from its public JSON endpoint); public information',
    notes=('Figures are published in Rs thousand and stored in rupees. "Actuals (Tent.)" are tentative (unaudited) '
           'and change between weekly updates; the database keeps earlier values in observation_revision. The '
           'current year\'s actuals are year-to-date and stored with period_end = the "Last on" update date, so the '
           'weekly series accumulates. Percent columns are not stored. "All Zone" is stored as smc_city exactly as '
           'published, but it is NOT the sum of all listed zones: on the 2026-10-03 data it equals Head Quarter + '
           'West, Central, North, East-A, South-A, Athwa and South East, and leaves out East Zone-B and South Zone-B '
           '(Kanakpur) in every cell; whether those two are missing from the total or double-booked is unknown. '
           'Budget-centre drill-down pages keep state in a server session and are not fetched.'),
    metrics=(
        Metric(INCOME, 'Budget summary: income (revenue/capital)', 'INR',
               'Revenue or capital income of the zone (dims.account), as budgeted or as received. ' + _DIMS_NOTE),
        Metric(EXPENDITURE, 'Budget summary: expenditure (revenue/capital)', 'INR',
               'Revenue or capital expenditure of the zone (dims.account), as budgeted or as spent. ' + _DIMS_NOTE),
    ),
)

ROWS = {
    'revenue income': (INCOME, 'revenue'),
    'revenue expense': (EXPENDITURE, 'revenue'),
    'capital income': (INCOME, 'capital'),
    'capital expense': (EXPENDITURE, 'capital'),
}

# ---------- page ----------


def page_info(body: bytes) -> dict:
    """What fetch() and parse() need from the HTML page. Raises ValueError if the layout changed."""
    html = body.decode('utf-8', errors='replace')
    table = next((t for t in html_tables(html) if t.attrs.get('id') == 'dtBudget'), None)
    if table is None or not table.rows:
        raise ValueError('table #dtBudget with a header row not found')
    headers = [clean(h) for h in table.rows[0]]
    if len(headers) != len(FIELDS) or headers[0].lower() != 'description':
        raise ValueError(f'unexpected #dtBudget columns {headers}; the JSON field mapping may have changed')
    sel = re.search(r'(?is)<select[^>]*id="drpZone"[^>]*>(.*?)</select>', html)
    if not sel:
        raise ValueError('zone selector #drpZone not found')
    zones = [(v.strip(), clean(re.sub(r'<[^>]+>', ' ', t)))
             for v, t in re.findall(r'(?is)<option[^>]*value="([^"]*)"[^>]*>(.*?)</option>', sel.group(1))]
    endpoint = re.search(r'"SearchBy"\s*:\s*"([^"]+)"', html)
    budget_year = re.search(r'"BudgetYear"\s*:\s*"(\d{4})"', html)
    if not (endpoint and budget_year):
        raise ValueError('inline script no longer names the "SearchBy" endpoint and "BudgetYear"')
    text = html_text(html)
    unit = re.search(r"Budget Summary\s*\(([^)]*)\)", text)
    last = re.search(r'Last on\s*(\d{1,2}/\d{1,2}/\d{4})', text)
    return {
        'headers': headers,
        'zones': zones,
        'endpoint': endpoint.group(1),
        'budget_year': int(budget_year.group(1)),
        'unit': clean(unit.group(1)) if unit else None,
        'as_of': parse_date(last.group(1), '%d/%m/%Y').isoformat() if last else None,
    }


def request_params(budget_year: int, zone: str) -> dict:
    """The query string the page's DataTables pipeline sends (minus jQuery's '_' cache-buster)."""
    p = {'draw': '1'}
    for i, f in enumerate(FIELDS):
        p.update({f'columns[{i}][data]': f, f'columns[{i}][name]': '', f'columns[{i}][searchable]': 'true',
                  f'columns[{i}][orderable]': 'false', f'columns[{i}][search][value]': '',
                  f'columns[{i}][search][regex]': 'false'})
    p.update({'start': '0', 'length': '10', 'search[value]': '', 'search[regex]': 'false',
              'CustomData[BudgetYear]': str(budget_year), 'CustomData[ZoneCode]': zone})
    return p


# ---------- fetch ----------

def fetch(ctx):
    page = ctx.get(PAGE_URL, meta={'doc': 'page'})
    info = page_info(page.body)
    yield page
    url = urljoin(PAGE_URL, info['endpoint'])
    first_error = None
    for zone, label in info['zones']:
        meta = {'doc': 'zone', 'zone_value': zone, 'zone_label': label, 'budget_year': info['budget_year'],
                'headers': info['headers'], 'unit': info['unit'], 'as_of': info['as_of']}
        try:
            raw = ctx.get(url, params=request_params(info['budget_year'], zone), meta=meta, conditional=False)
        except FetchError as e:
            if e.blocked:
                raise
            ctx.log.error('fetch failed for zone %s (%s): %s', label, zone, e)
            first_error = first_error or e
            continue
        yield raw
    if first_error is not None:
        raise first_error


# ---------- parse ----------

def _unit_factor(unit: str | None) -> float:
    u = (unit or '').lower().replace('’', "'")
    if re.search(r"rs\.?\s*in\s*'?000|thousand", u):
        return 1e3
    if 'lakh' in u:
        return 1e5
    if 'crore' in u:
        return 1e7
    raise ValueError(f'unknown unit in the page heading: {unit!r}')


def _column(label: str, budget_year: int) -> tuple[str, int] | None:
    """Header label -> (measure, FY start year); None for the % columns."""
    lab = clean(label)
    if lab.startswith('%'):
        return None
    m = re.match(r"(?i)^(actuals?\s*\(tent\.?\)|actuals?|original|revised)\s*(\d{2})\s*-\s*(\d{2})$", lab)
    if not m:
        raise ValueError(f'unrecognised column header {label!r}')
    y = 2000 + int(m.group(2))
    if (y + 1) % 100 != int(m.group(3)):
        raise ValueError(f'column header {label!r} is not a financial year')
    kind = m.group(1).lower()
    if 'tent' in kind:
        measure = 'actual_ytd' if y == budget_year else 'actual_tentative'
    else:
        measure = {'actual': 'actual', 'actuals': 'actual', 'original': 'budget_original', 'revised': 'budget_revised'}[kind]
    if y > budget_year or y < budget_year - 3:
        raise ValueError(f'column {label!r} is not near budget year {budget_year}')
    return measure, y


def _geo(meta: dict):
    label = meta.get('zone_label', '')
    if meta.get('zone_value') == '0' or re.fullmatch(r'(?i)all\s*zones?', label.strip()):
        return 'smc_city', 'smc', SMC
    code = zone_code(label)
    return 'smc_zone', code, zone_geo(code)


def _parse_zone(raw: Raw) -> Result:
    meta = raw.meta
    for k in ('zone_value', 'zone_label', 'budget_year', 'headers', 'unit'):
        if k not in meta:
            raise ValueError(f'raw.meta lacks {k!r}: the JSON can only be read with the page context fetch() records')
    doc = json.loads(raw.body.decode('utf-8-sig'))
    if doc.get('status') != 200 or not isinstance(doc.get('data'), list):
        raise ValueError(f'endpoint did not return data: status={doc.get("status")!r} redirect={doc.get("redirectUrl")!r}')
    level, code, geo = _geo(meta)
    factor = _unit_factor(meta['unit'])
    budget_year = int(meta['budget_year'])
    as_of = meta.get('as_of')
    cols = [(f, _column(h, budget_year)) for f, h in zip(FIELDS[1:], meta['headers'][1:])]

    res = Result(geos=[geo])
    seen_rows = set()
    for row in doc['data']:
        desc = clean(str(row.get('Description', ''))).lower()
        if desc not in ROWS:
            raise ValueError(f'unexpected row {row.get("Description")!r}')
        if desc in seen_rows:
            raise ValueError(f'row {desc!r} appears twice')
        seen_rows.add(desc)
        metric, account = ROWS[desc]
        by_measure: dict[tuple[str, int], float | None] = {}
        for field, col in cols:
            if field not in row:
                raise ValueError(f'JSON row lacks field {field!r}')
            if col is None:
                continue
            measure, fy = col
            v = row[field]
            if isinstance(v, str):
                v = v.strip().replace(',', '') or None
            v = None if v is None else float(v)
            by_measure[(measure, fy)] = v
            if measure == 'actual_ytd':
                if not as_of:
                    continue        # logged once below
                start, end = fy_period(fy)[0], as_of
                if not start <= end <= fy_period(fy)[1]:
                    raise ValueError(f'"Last on" date {as_of} is outside budget year {fy}-{fy + 1}')
            else:
                start, end = fy_period(fy)
            x = None if v is None else round(v * factor, 2)
            res.observations.append(Obs(metric, level, code, start, end, value=x,
                                        status='reported' if x is not None else 'not_reported',
                                        dims={'account': account, 'measure': measure}, publisher_as_of=as_of))
        _check_percentages(row, cols, meta['headers'], by_measure, desc)
    if seen_rows != set(ROWS):
        raise ValueError(f'{meta["zone_label"]}: expected rows {sorted(ROWS)}, got {sorted(seen_rows)}')
    if not as_of and any(c and c[0] == 'actual_ytd' for _, c in cols):
        log.warning('%s: no "Last on" date on the page; year-to-date actuals not stored', meta['zone_label'])
    return res


def _check_percentages(row, cols, headers, by_measure, desc):
    """'% of Rev. 25-26' = actual / revised and '% of Ori.26-27' = actual / original, rounded to 2 decimals.
    A mismatch means the JSON fields no longer line up with the column headers."""
    for (field, col), h in zip(cols, headers[1:]):
        if col is not None or row.get(field) is None:
            continue
        m = re.search(r'(?i)of\s*(rev|ori)\w*\.?\s*(\d{2})\s*-\s*(\d{2})', h)
        if not m:
            raise ValueError(f'unrecognised percent column {h!r}')
        fy = 2000 + int(m.group(2))
        den = by_measure.get(('budget_revised' if m.group(1).lower() == 'rev' else 'budget_original', fy))
        num_ = next((v for (ms, y), v in by_measure.items() if y == fy and ms.startswith('actual')), None)
        if not den or num_ is None:
            continue
        pct = float(row[field])
        if abs(pct - 100 * num_ / den) > 0.02:
            raise ValidationError(f'{desc}: column {h!r} = {pct} but actual/budget = {100 * num_ / den:.2f}%; '
                                  'JSON fields and headers no longer match')


def parse(raw: Raw) -> Result:
    if raw.meta.get('doc') == 'zone' or raw.body.lstrip()[:1] in (b'{', b'['):
        return _parse_zone(raw)
    info = page_info(raw.body)
    _unit_factor(info['unit'])
    if not info['as_of']:
        raise ValueError('page has no "Weekly Update (Last on dd/mm/yyyy)" date')
    for f, h in zip(FIELDS[1:], info['headers'][1:]):
        _column(h, info['budget_year'])
    if not any(v == '0' for v, _ in info['zones']):
        raise ValueError('zone selector has no "All Zone" (value 0) option')
    for v, label in info['zones']:
        if v != '0':
            zone_code(label)        # unknown zone labels fail here, before any JSON is parsed
    return Result()


# ---------- validate ----------

def validate(result: Result, raw: Raw) -> None:
    if not result.observations:
        return      # the HTML page: its structure is checked by parse()
    rows = {(o.metric_id, o.dims['account']) for o in result.observations}
    if len(rows) != 4:
        raise ValidationError(f'expected 4 rows (revenue/capital x income/expense), got {sorted(rows)}')
    city = result.observations[0].geo_level == 'smc_city'
    for o in result.observations:
        if o.value is None:
            continue
        if abs(o.value) > 2e12:          # Rs 2 lakh crore: far above any SMC budget head
            raise ValidationError(f'implausible {o.metric_id} {o.dims} {o.period_start}: Rs {o.value:,.0f}')
        if city and o.dims['account'] == 'revenue' and o.dims['measure'] in ('budget_original', 'budget_revised') \
                and not 1e10 <= o.value <= 5e11:  # SMC revenue budget: Rs 1,000 - 50,000 crore
            raise ValidationError(f'implausible city revenue budget {o.metric_id} {o.period_start}: Rs {o.value:,.0f}')
    fys = {o.period_start[:4] for o in result.observations}
    if len(fys) > 3:
        raise ValidationError(f'observations span {len(fys)} financial years; the page has columns for 3')
