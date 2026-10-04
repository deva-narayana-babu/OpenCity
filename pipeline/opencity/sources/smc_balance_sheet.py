"""SMC balance sheet and income & expenditure account (annual, accrual basis, audited from FY2012-13).

Index: https://www.suratmunicipal.gov.in/Departments/Accounts/BalanceSheet
  A <ul class="list-group"> with one <li> per year: "Financial Year 2025-26" + a "View Balance Sheet" link to
  /Content/Documents/Departments/Accounts/BalanceSheet_25_26.pdf. The 2026-09-28 snapshot lists 2005-06 to 2025-26.

PDFs (all have a text layer; read with pdftotext -layout):
  FY2005-06, FY2006-07   old two-sided "Liabilities | Assets" (T-format) statements with different heads, previous
                         year first. NOT parsed and not fetched (FIRST_FY): FY2007-08 restates 31 March 2007 in the
                         current format as its comparative column.
  FY2007-08 .. FY2025-26 one vertical statement per page, the same heads every year:
      BALANCE SHEET AS ON/AT 31 MARCH, YYYY           PARTICULARS | Schedule No. | <current FY> | <previous FY>
      INCOME AND EXPENDITURE ACCOUNT FOR THE YEAR ENDED 31 MARCH, YYYY   (same columns)
    From FY2020-21 the PDF repeats both statements in Gujarati (pages 3-4); those pages are skipped (same numbers,
    and the legacy Gujarati font extracts as garbage). FY2016-17 has the I&E page first.

What is stored (geo smc_city/smc, unit INR, both the current and the comparative column of every statement):
  finance.balance_sheet.*      as at 31 March (period_start = period_end = YYYY-03-31)
  finance.income_expenditure.* for the financial year (1 April - 31 March)

Units: statements say "Amount in (Rs.)" / "(In Rs.)" / "(`)" (the rupee sign in the old Rupee Foradian font) and
print paise, so values are rupees and stored unchanged. FY2013-14, FY2018-19 and FY2019-20 print no unit; there the
amounts (with paise) are read as rupees only because the balance-sheet total then falls in the plausible range
(Rs 1,000 crore - Rs 10 lakh crore; read as lakhs it would be absurd). A statement in lakhs or crores is multiplied
by 1e5 / 1e7. Anything else is rejected rather than guessed.

Overlap between years: the FY N statement repeats FY N-1 as its comparative column, sometimes regrouped (e.g. the
FY2018-19 statement moves Rs 14.98 crore from investments to cash for 31 March 2018). fetch() yields the PDFs oldest
first, so the later statement's comparative figure is applied last and wins; the earlier figure is kept in
observation_revision by the database layer.

Consistency: every column is checked (sub-totals = sum of items, both GRAND TOTALs equal, total = application of
funds, income - expenditure = surplus). A current-year column that fails rejects the document. A comparative column
that fails is dropped from that document with a warning (FY2016-17's comparative 31-03-2016 balance sheet prints
two different GRAND TOTALs, Rs 48,460 apart); the year's own statement still provides that date.
"""
from __future__ import annotations

import logging
import re
from urllib.parse import urljoin

from ..model import FetchError, Metric, Obs, Raw, Record, Result, Source, ValidationError
from ..parse import clean, fy_period, fy_start, num, parse_date, pdf_text
from ..surat import SMC

log = logging.getLogger('opencity.sources.smc_balance_sheet')

INDEX_URL = 'https://www.suratmunicipal.gov.in/Departments/Accounts/BalanceSheet'
FIRST_FY = 2007     # FY2007-08: first statement in the current (vertical, accrual) format

BS = 'finance.balance_sheet.'
IE = 'finance.income_expenditure.'

_BS_METRICS = [
    ('municipal_fund', 'Municipal fund', 'Own funds (a) "Municipal Funds" (schedule 1).'),
    ('reserves_surplus', 'Reserves and surplus', 'Own funds (b) "Reserves and surplus" (schedule 2).'),
    ('own_funds', 'Own funds (total)', 'Unlabelled subtotal of the "Own Funds" block (municipal fund + reserves and surplus).'),
    ('secured_loans', 'Secured loans', '"Secured loans" under Loan Funds.'),
    ('unsecured_loans', 'Unsecured loans', '"Unsecured Loans" under Loan Funds (printed from FY2023-24).'),
    ('loan_funds', 'Loan funds (total)', 'Unlabelled subtotal of the "Loan Funds" block (secured + unsecured loans). '
                                         'Some years (FY2015-16 to FY2017-18) print no Loan Funds block at all.'),
    ('total', 'Balance sheet total', '"GRAND TOTAL" of the balance sheet (sources of funds = application of funds; '
                                     'the parser checks that both sides print the same figure).'),
    ('gross_block', 'Fixed assets: gross block', '"Gross Block" of fixed assets.'),
    ('accumulated_depreciation', 'Fixed assets: accumulated depreciation', '"Less: Depreciation" under Fixed Assets.'),
    ('net_block', 'Fixed assets: net block', '"Net Block" = gross block - accumulated depreciation.'),
    ('cwip', 'Capital work in progress', '"Capital - Work In Progress (FA)".'),
    ('investments', 'Investments', '"Investments".'),
    ('inventories', 'Inventories', 'Current assets (a) "Inventories".'),
    ('sundry_debtors', 'Sundry debtors', 'Current assets (b) "Sundry Debtors": amounts receivable.'),
    ('cash_bank', 'Cash and bank balances', 'Current assets (c) "Cash and bank balances".'),
    ('loans_advances', 'Loans and advances', 'Current assets (d) "Loans and advances".'),
    ('current_assets', 'Current assets, loans and advances (total)',
     'Unlabelled subtotal of the "Current assets, loans and advances" block.'),
    ('current_liabilities', 'Current liabilities', 'Less: Current liabilities and Provisions, (a) "Current liabilities".'),
    ('provisions_for_taxes', 'Provisions for taxes', 'Less: Current liabilities and Provisions, (b) "Provisions For Taxes".'),
]
_IE_METRICS = [
    ('tax_revenue', 'Tax revenues', 'Income: "Tax Revenues" (e.g. property tax).'),
    ('non_tax_revenue', 'Non-tax revenues', 'Income: "Non Tax Revenues" (fees, user charges, etc.).'),
    ('grants_contributions', 'Government grants, contributions and subsidies',
     'Income: "Govt. Grants, Contri. & Subsidies" credited to income.'),
    ('octroi_compensation', 'Compensation in lieu of octroi', 'Income: "Compensation in lieu of Octroi" from the State.'),
    ('other_income', 'Other income', 'Income: "Other Income".'),
    ('total_income', 'Total income', 'Unlabelled subtotal of the Income block.'),
    ('employee_costs', 'Payments and benefits to employees', 'Expenditure: "Payments & Benefits to Employees".'),
    ('administration_expenses', 'Administration expenses', 'Expenditure: "Administration Expenses".'),
    ('repairs_maintenance', 'Repairs and maintenance', 'Expenditure: "Repairs and Maintenance".'),
    ('service_utility_charges', 'Service and utilities charges', 'Expenditure: "Service & Utilities Charges".'),
    ('finance_charges', 'Finance charges', 'Expenditure: "Finance Charges" (interest etc.).'),
    ('other_expenses', 'Other expenses', 'Expenditure: "Other Expenses".'),
    ('depreciation', 'Depreciation', 'Expenditure: "Depreciation" charged for the year.'),
    ('loss_on_disposal', 'Loss on sale/disposal of fixed assets', 'Expenditure: "Loss on Sale/Disposal of Fixed Asset".'),
    ('total_expenditure', 'Total expenditure', 'Unlabelled subtotal of the Expenditure block.'),
    ('surplus_before_tax', 'Net surplus (deficit) before taxation',
     '"Net Surplus for the year before taxation" = total income - total expenditure; negative = deficit.'),
    ('tax_provision', 'Provision for taxes', '"Less : Provision for taxes" deducted from the surplus.'),
    ('surplus_after_tax', 'Net surplus (deficit) after taxation', '"Net Surplus for the year after taxation"; negative = deficit.'),
    ('prior_period_income', 'Prior period income', 'Prior period adjustments (a) "Prior period incomes".'),
    ('prior_period_expenses', 'Prior period expenses', 'Prior period adjustments (b) "Prior period Expenses".'),
    ('excess_income_over_expenditure', 'Excess of income over expenditure',
     '"Excess of Income Over Expenditure" = surplus after tax + prior period income - prior period expenses; '
     'negative = excess of expenditure.'),
]

SOURCE = Source(
    id='smc_balance_sheet',
    name='SMC balance sheet and income & expenditure account (annual)',
    publisher='Surat Municipal Corporation, Accounts Department',
    url=INDEX_URL,
    module='finance',
    cadence='annual',
    interval_hours=24 * 7,          # a new year appears once a year (FY2025-26 was signed 14 July 2026); weekly check
    geo_note='SMC city (the corporation as a whole); the statements have no zone breakdown',
    licence_note='Surat Municipal Corporation publication (balance sheet PDFs); public information',
    notes=('Amounts are rupees as printed (with paise). Balance-sheet items are stocks as at 31 March '
           '(period_start = period_end); income & expenditure items are flows for the financial year. Each PDF gives '
           'the current and the previous year; PDFs are applied oldest first so a later statement\'s comparative '
           'figure wins and earlier differing figures stay in observation_revision. A "-" or blank amount on a printed '
           'line (accounting nil) is stored as not_reported per project rule, never as 0; heads a year does not print '
           'are not stored. Statements FY2007-08 to FY2011-12 are signed by SMC officials only; from FY2012-13 they '
           'carry the auditors\' (Natvarlal Vepari & Co.) signature, and publisher_as_of is the date printed under it '
           'when there is one. FY2005-06 and FY2006-07 (old two-sided format) are not parsed. The Gujarati duplicate '
           'pages and the schedules are not parsed. The index page is stored as balance_sheet_pdf records '
           '(one per financial year, with its PDF link).'),
    metrics=tuple(Metric(BS + k, label, 'INR', desc + ' As at 31 March.') for k, label, desc in _BS_METRICS)
    + tuple(Metric(IE + k, label, 'INR', desc + ' For the financial year April-March.') for k, label, desc in _IE_METRICS),
    record_types=('balance_sheet_pdf',),
)

# ---------- fetch ----------


def fetch(ctx):
    """Index page, then every listed PDF from FIRST_FY, oldest first. Past years are immutable (skip_if_seen); the
    newest one is re-requested with a conditional GET (the server sends ETag/Last-Modified) in case SMC replaces it.
    A non-blocking failure on one PDF does not stop the others; the first one is re-raised at the end."""
    idx = ctx.get(INDEX_URL, meta={'doc': 'index'})
    entries = [e for e in index_entries(idx.body) if e[0] >= FIRST_FY]
    yield idx
    if not entries:
        return
    newest = max(fy for fy, _, _ in entries)
    first_error = None
    for fy, label, url in sorted(entries):
        try:
            raw = ctx.get(url, meta={'doc': 'statement', 'fy': label}, skip_if_seen=(fy != newest))
        except FetchError as e:
            if e.blocked:
                raise
            ctx.log.error('fetch failed for FY %s (%s): %s', label, url, e)
            first_error = first_error or e
            continue
        if raw is not None:
            yield raw
    if first_error is not None:
        raise first_error


# ---------- index ----------

_LI = re.compile(r'(?is)<li\b[^>]*class="[^"]*list-group-item[^"]*"[^>]*>(.*?)</li>')
_FY_LABEL = re.compile(r'Financial\s+Year\s+((?:19|20)\d\d\s*-\s*\d{2,4})', re.I)
_PDF_HREF = re.compile(r'(?is)<a\b[^>]*href\s*=\s*["\']([^"\']+\.pdf)["\']')


def index_entries(body: bytes) -> list[tuple[int, str, str]]:
    """(FY start year, 'YYYY-YY' label, absolute PDF url) for each year listed on the index page."""
    html = body.decode('utf-8', errors='replace')
    out = []
    for m in _LI.finditer(html):
        block = m.group(1)
        fm = _FY_LABEL.search(re.sub(r'<[^>]+>', ' ', block))
        hm = _PDF_HREF.search(block)
        if not (fm and hm):
            continue
        y = fy_start(fm.group(1))
        out.append((y, f'{y}-{(y + 1) % 100:02d}', urljoin(INDEX_URL, clean(hm.group(1)))))
    return out


def _parse_index(raw: Raw) -> Result:
    entries = index_entries(raw.body)
    if not entries:
        raise ValueError('no "Financial Year YYYY-YY" + PDF link entries found on the balance-sheet index page')
    years = [fy for fy, _, _ in entries]
    if len(set(years)) != len(years):
        raise ValueError(f'duplicate financial years on the index page: {sorted(years)}')
    res = Result(complete_record_types=('balance_sheet_pdf',))
    for fy, label, url in entries:
        res.records.append(Record('balance_sheet_pdf', f'fy-{label}', {
            'fy': label, 'as_at': f'{fy + 1}-03-31', 'url': url, 'title': f'Balance Sheet, Financial Year {label}'}))
    return res


# ---------- statements (PDF) ----------

_NUMBER = re.compile(r'^(?:-?[\d,]*\d\.\d{2}|\(-?[\d,]*\d\.\d{2}\))$')     # amounts always carry paise
_DASH = re.compile(r'^[-–]$')                                             # printed nil
_YEAR_HDR = re.compile(r'((?:19|20)\d\d)\s*-\s*((?:19|20)?\d\d)')

# Labels are matched in "compact" form: lower case, letters only ("TaxRevenues" and "Tax Revenues" both occur).
_SECTIONS = [   # header lines without amounts; an unlabelled amount line is the subtotal of the current block
    (r'^ownfunds', 'own_funds'),
    (r'^loanfunds', 'loan_funds'),
    (r'^fixedassets', 'fixed_assets'),
    (r'^currentassets', 'current_assets'),
    (r'currentliabilitiesandprovisions', 'current_liabilities'),
    (r'^income$', 'income'),
    (r'^expenditure$', 'expenditure'),
    (r'^priorperiodadjustments?$', 'prior_period'),
    (r'^appropriation', 'appropriation'),
    (r'^sourcesoffunds|^applicationoffunds', 'other'),
]
_SUBTOTAL = {'own_funds': BS + 'own_funds', 'loan_funds': BS + 'loan_funds', 'current_assets': BS + 'current_assets',
             'income': IE + 'total_income', 'expenditure': IE + 'total_expenditure',
             'prior_period': '_excess_subtotal'}   # equals "Excess of Income Over Expenditure"; cross-check only

_BS_ITEMS = [
    (r'^munici(pal|apl)funds?$', 'municipal_fund'),
    (r'^reserves?(and)?surplus$', 'reserves_surplus'),
    (r'^securedloans?$', 'secured_loans'),
    (r'^unsecuredloans?$', 'unsecured_loans'),
    (r'^grandtotal$', 'total'),
    (r'^grossblock$', 'gross_block'),
    (r'^lessdepreciation$|^accumulateddepreciation$', 'accumulated_depreciation'),
    (r'^netblock$', 'net_block'),
    (r'^capitalworkinprogress(fa)?$', 'cwip'),
    (r'^investments?$', 'investments'),
    (r'^inventories$', 'inventories'),
    (r'^sundrydebtors$', 'sundry_debtors'),
    (r'^cash(and)?bankbalances?$', 'cash_bank'),
    (r'^loans(and)?advances$', 'loans_advances'),
    (r'^currentliabilities$', 'current_liabilities'),
    (r'^provisionsfortaxes$', 'provisions_for_taxes'),
]
_IE_ITEMS = [
    (r'^taxrevenues?$', 'tax_revenue'),
    (r'^nontaxrevenues?$', 'non_tax_revenue'),
    (r'^govtgrantscontrisubsidies$', 'grants_contributions'),
    (r'^compensationinlieuofoctroi$', 'octroi_compensation'),
    (r'^otherincome$', 'other_income'),
    (r'^paymentsbenefitstoemployees$', 'employee_costs'),
    (r'^administrationexpenses$', 'administration_expenses'),
    (r'^repairsandmaintenance$', 'repairs_maintenance'),
    (r'^serviceutilitiescharges$', 'service_utility_charges'),
    (r'^financecharges$', 'finance_charges'),
    (r'^otherexpenses$', 'other_expenses'),
    (r'^depreciation$', 'depreciation'),
    (r'^losson(sale)?(disposal)?offixedassets?$', 'loss_on_disposal'),
    (r'^netsurplusfortheyearbeforetaxation$', 'surplus_before_tax'),
    (r'^lessprovisionfortaxes$', 'tax_provision'),
    (r'^netsurplusfortheyearaftertaxation$', 'surplus_after_tax'),
    (r'^priorperiodincomes?$', 'prior_period_income'),
    (r'^priorperiodexpenses?$', 'prior_period_expenses'),
    (r'^excessofincomeoverexpenditure$', 'excess_income_over_expenditure'),
    # appropriation of the surplus and the running I&E balance: not stored
    (r'^balancebroughtforward|^balancecarriedto|^transferto(capital|general)fund$', None),
]
_STOP = re.compile(r'^\s*(For\s+.*&\s*Co\b|Chartered Accountants|Notes forming part)', re.I)


def _compact(label: str) -> str:
    return re.sub(r'[^a-z]', '', re.sub(r'^\s*[({]?[a-d]\)\s*', '', label.lower()))


def _fields(line: str) -> list[tuple[int, int, str]]:
    """Split a layout line on runs of 2+ spaces: (start col, end col, text)."""
    return [(m.start(), m.end(), m.group(0)) for m in re.finditer(r'\S+(?: \S+)*', line)]


def _statement_kind(page: str) -> str | None:
    if re.search(r'^\s*(Liabilities\s+\d{4}-\d{4}.*\bAssets|Income\s+\d{4}-\d{4}.*\bExpenditure)\b', page, re.M | re.I):
        return 'tformat'
    head = re.sub(r'\s+', ' ', page[:1500]).upper()
    if re.search(r'BALANCE SHEET AS (ON|AT)', head):
        return 'bs'
    if re.search(r'INCOME (AND|&) EXPENDITURE ACCOUNT', head):
        return 'ie'
    return None


def _explicit_unit(page: str) -> float | None:
    """Unit printed in the statement heading, or None if there is none."""
    head = '\n'.join(page.splitlines()[:12]).lower()
    if re.search(r'lakh', head):
        return 1e5
    if re.search(r'crore', head):
        return 1e7
    if re.search(r'\(\s*in\s+rs\.?\s*\)|amount\s+in\s*\(?\s*rs\.?\s*\)?|\(\s*[`₹]\s*\)', head):
        return 1.0
    return None


def _parse_statement(page: str, kind: str):
    """Returns ((current FY start, previous FY start), {metric: [current, previous]}, {key: [[cur, prev], ...]})."""
    lines = page.splitlines()
    hdr_i = next((i for i, ln in enumerate(lines) if len(_YEAR_HDR.findall(ln)) >= 2), None)
    if hdr_i is None:
        raise ValueError(f'{kind}: no "YYYY-YY  YYYY-YY" column header found')
    years = [(m.start(), m.end(), int(m.group(1))) for m in _YEAR_HDR.finditer(lines[hdr_i])][:2]
    (s0, e0, y0), (s1, e1, y1) = years
    if y0 != y1 + 1:
        raise ValueError(f'{kind}: column years {y0} and {y1} are not consecutive with the current year first')
    centres = ((s0 + e0) / 2, (s1 + e1) / 2)
    dash_from = s0 - 12         # a lone "-" left of this is part of a label ("Capital - Work In Progress")

    items = _BS_ITEMS if kind == 'bs' else _IE_ITEMS
    prefix = BS if kind == 'bs' else IE
    values: dict[str, list] = {}
    extra: dict[str, list] = {}
    section = None
    for ln in lines[hdr_i + 1:]:
        if _STOP.match(ln):
            break
        fields = _fields(ln)
        amounts = [f for f in fields if _NUMBER.match(f[2]) or (_DASH.match(f[2]) and f[1] > dash_from)]
        label_text = ' '.join(f[2] for f in fields if f not in amounts and not re.fullmatch(r'\d{1,2}|\.', f[2]))
        label = _compact(label_text)
        if len(amounts) > 2:
            raise ValueError(f'{kind}: more than two amounts on line {ln.strip()!r}')
        pair: list = [None, None]
        if len(amounts) == 2:
            pair = [amounts[0][2], amounts[1][2]]
        elif len(amounts) == 1:
            s, e, t = amounts[0]
            c = (s + e) / 2
            pair[0 if abs(c - centres[0]) <= abs(c - centres[1]) else 1] = t
        pair = [None if (p is None or _DASH.match(p)) else num(p) for p in pair]

        if not label:
            if not amounts or pair == [None, None]:
                continue            # blank line, page number, or a "-  -" difference line under GRAND TOTAL
            target = _SUBTOTAL.get(section)
            if target is None:
                raise ValueError(f'{kind}: unlabelled amount line outside a known block: {ln.strip()!r}')
            if target.startswith('_'):
                extra.setdefault(target, []).append(pair)
            elif target in values:
                raise ValueError(f'{kind}: second subtotal in block {section!r}: {ln.strip()!r}')
            else:
                values[target] = pair
            continue

        if not amounts:
            sec = next((s for pat, s in _SECTIONS if re.search(pat, label)), None)
            if sec is not None:
                section = sec
                continue
        metric = next((m for pat, m in items if re.search(pat, label)), 'unknown')
        if metric == 'unknown':
            if not amounts:
                continue            # headings, "PARTICULARS", "Schedule No.", wrapped text
            raise ValueError(f'{kind}: unrecognised line item {label_text!r} ({ln.strip()!r})')
        if metric is None:
            continue
        key = prefix + metric
        if key == BS + 'total' and key in values:
            extra['_total_application'] = [pair]
            continue
        if key in values:
            raise ValueError(f'{kind}: line item {label_text!r} appears twice')
        values[key] = pair          # a printed line with blank amounts -> [None, None] -> not_reported
    return (y0, y1), values, extra


def _auditor_date(page: str) -> str | None:
    """Date printed in the signature block ("Date : 14 JULY 2026", "Date :10/08/2017"), if any."""
    m = re.search(r'Date\s*:\s*(\d{1,2})[\s./-]*([A-Za-z]{3,}|\d{1,2})[\s,./-]*(\d{4})', page)
    if not m:
        return None
    d, mo, y = m.groups()
    try:
        if mo.isdigit():
            return parse_date(f'{d}/{mo}/{y}', '%d/%m/%Y').isoformat()
        return parse_date(f'{d} {mo[:3]} {y}', '%d %b %Y').isoformat()
    except ValueError:
        return None


def _g(v: dict, k: str) -> float:
    x = v.get(k)
    return x or 0.0


def _close(a: float, b: float) -> bool:
    return abs(a - b) <= max(1.0, 1e-9 * abs(a))      # rupee-level rounding


def column_problems(kind: str, v: dict) -> list[str]:
    """Arithmetic checks on one column (metric -> value; None = not reported, counted as nil)."""
    out = []

    def check(what, lhs, rhs):
        if not _close(lhs, rhs):
            out.append(f'{what}: {lhs:,.2f} != {rhs:,.2f}')
    if kind == 'bs':
        total = v.get(BS + 'total')
        if total is None:
            return ['no GRAND TOTAL']
        if '_total_application' in v:
            check('GRAND TOTAL (sources) = GRAND TOTAL (application)', total, _g(v, '_total_application'))
        if BS + 'own_funds' in v:
            check('own funds = municipal fund + reserves', _g(v, BS + 'own_funds'),
                  _g(v, BS + 'municipal_fund') + _g(v, BS + 'reserves_surplus'))
        if BS + 'loan_funds' in v:
            check('loan funds = secured + unsecured', _g(v, BS + 'loan_funds'),
                  _g(v, BS + 'secured_loans') + _g(v, BS + 'unsecured_loans'))
        if BS + 'own_funds' in v:
            check('total = own funds + loan funds', total, _g(v, BS + 'own_funds') + _g(v, BS + 'loan_funds'))
        if BS + 'net_block' in v:
            check('net block = gross block - depreciation', _g(v, BS + 'net_block'),
                  _g(v, BS + 'gross_block') - _g(v, BS + 'accumulated_depreciation'))
        if BS + 'current_assets' in v:
            check('current assets = sum of items', _g(v, BS + 'current_assets'),
                  sum(_g(v, BS + k) for k in ('inventories', 'sundry_debtors', 'cash_bank', 'loans_advances')))
            check('total = application of funds', total,
                  _g(v, BS + 'net_block') + _g(v, BS + 'cwip') + _g(v, BS + 'investments') + _g(v, BS + 'current_assets')
                  - _g(v, BS + 'current_liabilities') - _g(v, BS + 'provisions_for_taxes'))
    else:
        inc, exp = v.get(IE + 'total_income'), v.get(IE + 'total_expenditure')
        if inc is None or exp is None:
            return ['income or expenditure total missing']
        check('total income = sum of items', inc, sum(_g(v, IE + k) for k in (
            'tax_revenue', 'non_tax_revenue', 'grants_contributions', 'octroi_compensation', 'other_income')))
        check('total expenditure = sum of items', exp, sum(_g(v, IE + k) for k in (
            'employee_costs', 'administration_expenses', 'repairs_maintenance', 'service_utility_charges',
            'finance_charges', 'other_expenses', 'depreciation', 'loss_on_disposal')))
        if IE + 'surplus_before_tax' in v:
            check('surplus before tax = income - expenditure', _g(v, IE + 'surplus_before_tax'), inc - exp)
        if IE + 'surplus_after_tax' in v:
            check('surplus after tax = before tax - provision', _g(v, IE + 'surplus_after_tax'),
                  _g(v, IE + 'surplus_before_tax') - _g(v, IE + 'tax_provision'))
            if IE + 'excess_income_over_expenditure' in v:
                check('excess = surplus after tax + prior period income - expenses',
                      _g(v, IE + 'excess_income_over_expenditure'),
                      _g(v, IE + 'surplus_after_tax') + _g(v, IE + 'prior_period_income')
                      - _g(v, IE + 'prior_period_expenses'))
        if '_excess_subtotal' in v and IE + 'excess_income_over_expenditure' in v:
            check('prior-period subtotal = excess of income over expenditure', _g(v, '_excess_subtotal'),
                  _g(v, IE + 'excess_income_over_expenditure'))
    return out


def _parse_pdf(raw: Raw) -> Result:
    text = pdf_text(raw.body, layout=True)
    res = Result(geos=[SMC])
    fy_label = raw.meta.get('fy', '?')
    if len(re.findall(r'[A-Za-z]{3,}', text)) < 20:
        log.warning('%s (FY %s): no text layer (scanned PDF?); nothing recorded, no OCR', raw.url, fy_label)
        return res
    found: dict[str, tuple[str, tuple]] = {}
    for page in text.split('\f'):
        kind = _statement_kind(page)
        if kind == 'tformat':
            log.warning('%s (FY %s): old two-sided (Liabilities | Assets) statement; not parsed', raw.url, fy_label)
            return res
        if kind is None or kind in found:
            continue        # Gujarati duplicates, other pages
        found[kind] = (page, _parse_statement(page, kind))
    if 'bs' not in found:
        raise ValueError('no English "BALANCE SHEET AS ON/AT ..." page found in the PDF')

    bs_page, ((y0, _), bs_values, _) = found['bs']
    m = re.search(r'BALANCE SHEET AS (?:ON|AT)\s+(?:THE\s+)?31\S*\s+MARCH\W*(\d{4})', re.sub(r'\s+', ' ', bs_page.upper()))
    if not m or int(m.group(1)) != y0 + 1:
        raise ValueError(f'balance sheet date ({m and m.group(1)}) does not match its first column {y0}-{y0 + 1}')
    if raw.meta.get('fy') and fy_start(raw.meta['fy']) != y0:
        raise ValueError(f'index says FY {raw.meta["fy"]} but the balance sheet is for {y0}-{y0 + 1}')
    if 'ie' in found and found['ie'][1][0][0] != y0:
        raise ValueError(f'income & expenditure account is for {found["ie"][1][0][0]}, balance sheet for {y0}')

    units = {k: _explicit_unit(p) for k, (p, _) in found.items()}
    stated = {u for u in units.values() if u is not None}
    if len(stated) > 1:
        raise ValueError(f'statements in one PDF use different units: {units}')
    if stated:
        factor = stated.pop()
    else:
        total = bs_values.get(BS + 'total', [None])[0]
        if total is None or not 1e10 <= total <= 1e13:
            raise ValueError('no unit printed and the balance sheet total is not plausible as rupees')
        log.info('%s (FY %s): no unit printed; amounts read as rupees (balance sheet total Rs %.0f)',
                 raw.url, fy_label, total)
        factor = 1.0
    as_of = _auditor_date(found['bs'][0]) or (_auditor_date(found['ie'][0]) if 'ie' in found else None)

    for kind, (page, ((c, p), values, extra)) in found.items():
        for col, fy in ((0, c), (1, p)):
            v = {k: pair[col] for k, pair in values.items()}
            for k, pairs in extra.items():
                v[k] = pairs[-1][col]
            problems = column_problems(kind, v)
            if problems:
                what = ('balance sheet as at 31-03-%d' % (fy + 1)) if kind == 'bs' else f'I&E {fy}-{fy + 1}'
                if col == 0:
                    raise ValidationError(f'{what} (current year) is inconsistent: ' + '; '.join(problems))
                log.warning('%s (FY %s): comparative %s is inconsistent (%s); not stored from this document',
                            raw.url, fy_label, what, '; '.join(problems))
                continue
            start, end = (f'{fy + 1}-03-31',) * 2 if kind == 'bs' else fy_period(fy)
            for metric, x in values.items():
                x = None if x[col] is None else round(x[col] * factor, 2)
                res.observations.append(Obs(metric, 'smc_city', 'smc', start, end, value=x,
                                            status='reported' if x is not None else 'not_reported',
                                            publisher_as_of=as_of))
    return res


def parse(raw: Raw) -> Result:
    if raw.body[:5] == b'%PDF-':
        return _parse_pdf(raw)
    if raw.meta.get('doc') == 'statement':
        raise ValueError(f'{raw.url}: expected a PDF statement but got {raw.body[:60]!r}')
    return _parse_index(raw)


# ---------- validate ----------

def validate(result: Result, raw: Raw) -> None:
    if result.records:
        n = len(result.records)
        if n < 15:
            raise ValidationError(f'only {n} balance sheets listed on the index page (the 2026 snapshot lists 21)')
        return
    if not result.observations:
        return      # a statement we deliberately do not parse; logged by parse()
    by_period: dict[tuple[str, str], dict[str, float | None]] = {}
    for o in result.observations:
        by_period.setdefault((o.period_start, o.period_end), {})[o.metric_id] = o.value
    bs_dates = sorted(p[1] for p in by_period if p[0] == p[1])
    if not 1 <= len(bs_dates) <= 2:
        raise ValidationError(f'expected one or two balance sheet dates per document, got {bs_dates}')
    for (start, end), v in by_period.items():
        kind = 'bs' if start == end else 'ie'
        problems = column_problems(kind, v)
        if problems:
            raise ValidationError(f'{start}..{end}: ' + '; '.join(problems))
        if kind == 'bs':
            if not end.endswith('-03-31') or not '2000' <= end[:4] <= '2100':
                raise ValidationError(f'implausible balance sheet date {end}')
            total = v[BS + 'total']
            if not 1e10 <= total <= 1e13:      # Rs 1,000 crore .. Rs 10 lakh crore
                raise ValidationError(f'{end}: implausible balance sheet total Rs {total:,.0f}')
            for k in ('municipal_fund', 'reserves_surplus', 'gross_block', 'net_block', 'cwip', 'cash_bank'):
                x = v.get(BS + k)
                if x is not None and not 0 <= x <= total * 1.5:
                    raise ValidationError(f'{end}: implausible {k} Rs {x:,.0f} (total Rs {total:,.0f})')
        else:
            inc = v[IE + 'total_income']
            if not 1e9 <= inc <= 1e12:        # Rs 100 crore .. Rs 1 lakh crore a year
                raise ValidationError(f'{start}..{end}: implausible total income Rs {inc:,.0f}')
            for k in ('tax_revenue', 'employee_costs', 'depreciation'):
                x = v.get(IE + k)
                if x is not None and not 0 <= x <= inc * 1.5:
                    raise ValidationError(f'{start}..{end}: implausible {k} Rs {x:,.0f} (income Rs {inc:,.0f})')
