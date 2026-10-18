"""MoHUA CityFinance: standardised audited accounts of Surat Municipal Corporation (annual, by financial year).

Page: https://www.cityfinance.in/municipal-data/city/surat, an Angular app. Its JS bundle (the city page chunk and
its "dashboard service") loads public JSON from https://www.cityfinance.in/api/v1/. fetch() calls three of those
endpoints as plain GETs with the default User-Agent and no extra headers:

  1. common/get-latest-standardized-year?ulbId=<id>&auditStatus=Audited
       {"success":true,"ledgerYears":["2023-24", ..., "2015-16"]}: the audited years, newest first. Used only to
       build the next two requests; nothing is stored from it. (auditStatus=Unaudited returned [] on 2026-10-18.)
  2. dashboard/city/bs-is?btnKey=incomeStatement&selectedUlb=<id>&ulbIds=<id>&years=2015-16&years=...
       The "Income Statement" table. One row per account head, with a "code" (110 Tax Revenue ... 272
       Depreciation) and one key per year, e.g. "202324_<ulb id>": 7280435255. Amounts are in RUPEES (integers):
       the same tax revenue shows as 728.04 Cr in the overview. A year with no key is a blank cell, stored as
       not_reported.
  3. ledger/getCityDasboardIndicators?keyType=overview&ulbId=<id>&years[]=2015-16&years[]=...
       The "Overview" tab. Rows look like {"name": "Own Source Revenue (Cr)", "yearData": ["939.88", ...]},
       in CRORE with 2 decimals, so they are multiplied by 1e7 and stored in INR (precise to Rs 1 lakh). "N/A" is
       stored as not_reported.

Surat's ULB id 5eb5844f76a3b61f40ba0693 (code GJ003, slug 'surat') comes from CityFinance's ULB list
(reference/budget/india-mohua-cityfinance-ulb-list-2026-09-27.json, from /api/v1/ulb).

What is stored (geo smc_city/smc, period = financial year 1 April - 31 March, unit INR):
  cityfinance.income.by_head, cityfinance.expenditure.by_head   income statement heads (dims.head)
  cityfinance.income.total, cityfinance.expenditure.total       "Total Income (A)" and "Total Expenditure (B)"
  cityfinance.own_source_revenue, cityfinance.revenue_expenditure, cityfinance.capital_expenditure   overview

Not stored:
  - subtotal rows ("Non-Tax Revenue" etc.), surplus lines, prior-period items (280), transfers to reserves (290);
  - the overview ratios and debt (smc_balance_sheet has SMC's own loan figures);
  - the overview's "Total Expenditure (Cr)", because it counts an N/A capital expenditure as zero (2015-16:
    1805.37 = revenue expenditure only).

How the figures relate (checked for all 8 years in the 2026-10-18 responses):
  - The overview's "Total Revenue Receipts" equals the income statement's "Total Income (A)".
  - The overview's "Own Source Revenue" equals income statement codes 110 + 130-150 + 170-180.
  - The overview's "Total Revenue Expenditure" equals "Total Expenditure (B)" plus prior-period items (code 280).
  - Capital expenditure is N/A for 2015-16 and 2019-20, the years that have no audited year just before them.
"""
from __future__ import annotations

import json
from urllib.parse import urlencode

from ..model import Metric, Obs, Raw, Result, Source, ValidationError
from ..parse import fy_period, fy_start, num
from ..surat import SMC

API = 'https://www.cityfinance.in/api/v1/'
PAGE = 'https://www.cityfinance.in/municipal-data/city/surat'
ULB_ID = '5eb5844f76a3b61f40ba0693'
CRORE = 10_000_000

# income statement account code -> dims.head
INCOME_HEADS = {
    '110': 'tax_revenue',
    '120': 'assigned_revenues_compensation',
    '130': 'rental_income',
    '140': 'fees_user_charges',
    '150': 'sale_hire_charges',
    '160': 'revenue_grants_contributions_subsidies',
    '170': 'income_from_investments',
    '171': 'interest_earned',
    '180': 'other_income',
    '100': 'others',
}
EXPENDITURE_HEADS = {
    '210': 'establishment',
    '220': 'administrative',
    '230': 'operation_maintenance',
    '240': 'interest_finance_charges',
    '250': 'programme',
    '260': 'revenue_grants_contributions_subsidies',
    '270': 'provisions_write_off',
    '271': 'miscellaneous',
    '272': 'depreciation',
    '200': 'others',
}
SKIPPED_CODES = {'280', '290'}      # prior-period items, transfer to reserve funds

# overview row name (lower case, spaces removed) -> metric; "(cr)" pins the unit
OVERVIEW = {
    'ownsourcerevenue(cr)': 'cityfinance.own_source_revenue',
    'totalrevenueexpenditure(cr)': 'cityfinance.revenue_expenditure',
    'totalcapitalexpenditure(cr)': 'cityfinance.capital_expenditure',
}

SOURCE = Source(
    id='cityfinance_surat',
    name='CityFinance standardised audited accounts: Surat Municipal Corporation (annual)',
    publisher='Ministry of Housing and Urban Affairs, Government of India (CityFinance)',
    url=PAGE,
    module='finance',
    cadence='annual',
    interval_hours=24 * 30,         # a new audited year appears about once a year; checking monthly is enough
    geo_note='SMC city (Surat Municipal Corporation as an urban local body)',
    licence_note='Government of India (MoHUA) public portal; JSON from the API that the CityFinance city page uses',
    notes='CityFinance maps SMC\'s audited annual accounts to standard account heads, so its figures can differ '
          'from SMC\'s own statements (smc_balance_sheet). Only audited years are requested.',
    metrics=(
        Metric('cityfinance.income.by_head', 'Income by account head (CityFinance income statement)', 'INR',
               'Income statement amount for one head (dims.head), e.g. tax_revenue (code 110) or fees_user_charges '
               '(140). Blank cells are not_reported; older years report fewer heads separately.'),
        Metric('cityfinance.income.total', 'Total revenue (CityFinance)', 'INR',
               '"Total Income (A)" of the income statement: the sum of all income heads, including assigned '
               'revenues and revenue grants. CityFinance shows the same figure as "Total Revenue".'),
        Metric('cityfinance.expenditure.by_head', 'Revenue expenditure by account head (CityFinance income statement)',
               'INR', 'Income statement amount for one expenditure head (dims.head), e.g. establishment (code 210) or '
                      'depreciation (272). Capital spending is not in the income statement.'),
        Metric('cityfinance.expenditure.total', 'Total expenditure in the income statement (CityFinance)', 'INR',
               '"Total Expenditure (B)" of the income statement: the sum of the expenditure heads. It excludes '
               'capital expenditure and prior-period items.'),
        Metric('cityfinance.own_source_revenue', 'Own source revenue (CityFinance)', 'INR',
               '"Own Source Revenue" from the CityFinance overview: income statement codes 110, 130-150 and '
               '170-180 (tax, rent, fees, sales and other income incl. interest), excluding assigned revenues and '
               'grants (checked for all 8 years). Published in crore to 2 decimals (Rs 1 lakh).'),
        Metric('cityfinance.revenue_expenditure', 'Revenue expenditure (CityFinance)', 'INR',
               '"Total Revenue Expenditure" from the CityFinance overview. In every year checked it equals the '
               'income statement total expenditure plus prior-period items. Published in crore to 2 decimals.'),
        Metric('cityfinance.capital_expenditure', 'Capital expenditure (CityFinance)', 'INR',
               '"Total Capital Expenditure" from the CityFinance overview, which CityFinance derives from fixed '
               'assets and capital work in progress in the balance sheet. It is N/A (not_reported) for years with '
               'no audited year just before them. Published in crore to 2 decimals.'),
    ),
)


def audited_years(body: bytes) -> list[str]:
    """['2015-16', ..., '2023-24'] from the audited-years response, oldest first."""
    doc = json.loads(body)
    years = doc.get('ledgerYears') or []
    if not doc.get('success') or not years:
        raise ValueError('CityFinance lists no audited years for Surat')
    return sorted(years, key=fy_start)        # fy_start also rejects anything that is not a year label


def fetch(ctx):
    idx = ctx.get(API + 'common/get-latest-standardized-year', params={'ulbId': ULB_ID, 'auditStatus': 'Audited'})
    years = audited_years(idx.body)
    yield idx
    q = [('btnKey', 'incomeStatement'), ('selectedUlb', ULB_ID), ('ulbIds', ULB_ID)] + [('years', y) for y in years]
    yield ctx.get(API + 'dashboard/city/bs-is?' + urlencode(q))
    q = [('keyType', 'overview'), ('ulbId', ULB_ID)] + [('years[]', y) for y in years]
    yield ctx.get(API + 'ledger/getCityDasboardIndicators?' + urlencode(q))


def normalize(body: bytes) -> bytes:
    """Drop the ',"fromCache":true' flag that the API appends on a server-side cache hit, so the same data
    is not archived as a change."""
    return body.replace(b',"fromCache":true', b'').replace(b',"fromCache":false', b'')


def parse(raw: Raw) -> Result:
    doc = json.loads(raw.body)
    if 'ledgerYears' in doc:
        audited_years(raw.body)
        return Result(geos=[SMC])
    if 'ulbsData' in doc:
        return _income_statement(doc)
    if 'response' in doc:
        return _overview(doc)
    raise ValueError(f'unrecognised CityFinance response with keys {sorted(doc)[:10]}')


def _obs(metric: str, fy: int, v: float | None, dims: dict | None = None) -> Obs:
    start, end = fy_period(fy)
    return Obs(metric, 'smc_city', 'smc', start, end, value=v,
               status='reported' if v is not None else 'not_reported', dims=dims or {})


def _income_statement(doc: dict) -> Result:
    if ULB_ID not in doc.get('ulbsData', {}):
        raise ValueError('income statement is not for Surat Municipal Corporation')
    rows = doc['data']
    # one key per year in each row, e.g. "202324_5eb5844f76a3b61f40ba0693" for 2023-24
    keys = sorted({k for r in rows for k in r if k.endswith('_' + ULB_ID)})
    if not keys:
        raise ValueError('income statement has no year columns')
    years = {k: fy_start(k[:4] + '-' + k[4:6]) for k in keys}

    res = Result(geos=[SMC])
    for r in rows:
        code = str(r.get('code'))
        item = (r.get('lineItem') or '').lower()
        dims = {}
        if item.startswith('total income'):
            metric = 'cityfinance.income.total'
        elif item.startswith('total expenditure'):
            metric = 'cityfinance.expenditure.total'
        elif r.get('code') is None or r.get('calculation') or code in SKIPPED_CODES:
            continue                # section headers, subtotals, surplus lines, prior-period items, reserves
        elif code in INCOME_HEADS:
            metric, dims = 'cityfinance.income.by_head', {'head': INCOME_HEADS[code]}
        elif code in EXPENDITURE_HEADS:
            metric, dims = 'cityfinance.expenditure.by_head', {'head': EXPENDITURE_HEADS[code]}
        else:
            raise ValueError(f'unknown income statement head {code} {r.get("lineItem")!r}')
        for k in keys:
            res.observations.append(_obs(metric, years[k], num(r.get(k)), dims))
    return res


def _overview(doc: dict) -> Result:
    rows = doc['response']['data']
    if rows[0].get('name') != 'Indicators':
        raise ValueError(f'overview header row is {rows[0].get("name")!r}, expected "Indicators"')
    years = [fy_start(y) for y in rows[0]['yearData']]

    found: dict[str, list] = {}     # rows and their child rows; the revenue tab repeats some rows as both
    for r in rows + [c for row in rows for c in row.get('children') or []]:
        metric = OVERVIEW.get(r.get('name', '').lower().replace(' ', ''))
        if metric is None:
            continue
        values = [num(v) for v in r['yearData']]
        if len(values) != len(years):
            raise ValueError(f'{r["name"]}: {len(values)} values for {len(years)} years')
        if metric in found and found[metric] != values:
            raise ValueError(f'{r["name"]} appears twice with different values')
        found[metric] = values

    res = Result(geos=[SMC])
    for metric, values in found.items():
        for fy, v in zip(years, values):
            res.observations.append(_obs(metric, fy, None if v is None else float(round(v * CRORE))))
    return res


def validate(result: Result, raw: Raw) -> None:
    obs = result.observations
    if not obs:
        return                      # the audited-years list; parse() already checked it
    by: dict[str, dict[str, list[Obs]]] = {}
    for o in obs:
        by.setdefault(o.metric_id, {}).setdefault(o.period_start, []).append(o)

    years = {o.period_start for o in obs}
    if len(years) < 5:
        raise ValidationError(f'only {len(years)} audited years (the 2026-10-18 response has 8)')
    latest_end = max(o.period_end for o in obs)
    if raw is not None and latest_end >= raw.retrieved_at[:10]:
        raise ValidationError(f'financial year ending {latest_end} cannot be audited by {raw.retrieved_at[:10]}')

    def check_range(metric, low_cr, high_cr):
        for o in obs:
            if o.metric_id == metric and o.value is not None and not low_cr * CRORE <= o.value <= high_cr * CRORE:
                raise ValidationError(f'implausible {metric} Rs {o.value / CRORE:.2f} crore for {o.period_start}')

    if 'cityfinance.income.total' in by:
        # the totals are the sums of the heads: this catches heads that were missed or misread
        for total, heads in (('cityfinance.income.total', 'cityfinance.income.by_head'),
                             ('cityfinance.expenditure.total', 'cityfinance.expenditure.by_head')):
            for start in sorted(years):
                t = by.get(total, {}).get(start, [None])[0]
                if t is None or t.value is None:
                    raise ValidationError(f'{total} missing for {start}')
                s = sum(o.value or 0 for o in by.get(heads, {}).get(start, []))
                if abs(s - t.value) > 10:
                    raise ValidationError(f'{heads} for {start} sum to {s:.0f}, but the total is {t.value:.0f}')
        # SMC's total income was Rs 1,706 crore in 2015-16 and Rs 4,407 crore in 2023-24
        check_range('cityfinance.income.total', 500, 50_000)
        check_range('cityfinance.expenditure.total', 500, 50_000)
    else:
        missing = set(OVERVIEW.values()) - set(by)
        if missing:
            raise ValidationError(f'overview rows not found: {sorted(missing)} (renamed, or no longer in crore?)')
        check_range('cityfinance.own_source_revenue', 100, 50_000)
        check_range('cityfinance.revenue_expenditure', 500, 50_000)
        check_range('cityfinance.capital_expenditure', 0, 50_000)
        if all(o.value is None for o in obs if o.metric_id == 'cityfinance.own_source_revenue'):
            raise ValidationError('no own source revenue reported for any year')
