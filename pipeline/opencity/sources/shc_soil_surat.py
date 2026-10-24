"""Soil Health Card nutrient dashboard: soil samples by nutrient class for the talukas (blocks) of Surat district.

Publisher: Department of Agriculture & Farmers Welfare, Ministry of Agriculture & Farmers Welfare, Government of
India, through the Soil Health Card portal (https://soilhealth.dac.gov.in/, "Nutrient Dashboard" page).

Endpoint: the public dashboard reads a GraphQL API. One POST per test cycle, JSON body, no login, token or API key
(the portal's own client sends "authorization" only when a user is signed in; anonymous visitors send none, and
so do we). soilhealth.dac.gov.in/robots.txt disallows nothing; the API host has no robots.txt (it answers
"GET query missing." to any GET).

    POST https://soilhealth4.dac.gov.in/
    {"query": "query GetNutrientDashboardForPortal($state: ID, $district: ID, ... $cycle: String, ...) {
                 getNutrientDashboardForPortal(state: $state, district: $district, ... cycle: $cycle, ...) }",
     "variables": {"state": "63f922a6dbc0f7fe06751641",       # GUJARAT (state code 24)
                   "district": "63f92c6189d86ca9e2bc2283",    # SURAT (district code 459)
                   "cycle": "2025-26"}}

The cycles are financial years. The portal offers 2023-24 to 2026-27 (2026-10-24); fetch() asks for every cycle
from 2023-24 to the current financial year. No scheme filter is sent, so all schemes come back.

Response layout: {"data": {"getNutrientDashboardForPortal": [row, ...]}}, one row per block and scheme:

    {"scheme": "660f941a5c8405ca8375c7c6", "cycle": "2025-26",
     "state": {"name": "GUJARAT", "code": "24"}, "district": {"name": "SURAT", "code": "459"},
     "block": {"name": "BARDOLI", "code": "4232"},
     "results": {"n": {"High": 0, "Low": 3093, "Medium": 0}, "p": {...}, "k": {...}, "OC": {...},
                 "pH": {"Alkaline": 299, "Acidic": 0, "Neutral": 2794}, "EC": {"Saline": 644, "NonSaline": 2449},
                 "S": {"Sufficient": 2389, "Deficient": 704}, "Fe": {...}, "Zn": {...}, "Cu": {...}, "B": {...},
                 "Mn": {...}},
     "updatedAt": "2026-10-23T17:54:00.877Z", "lastProcessedAt": "2026-10-23T17:17:18.196Z"}

Each number is a count of soil samples tested in that block, cycle and scheme whose result fell in that class.
2025-26: 15 rows (10 blocks under Soil Health Card RKVY, 5 under NMNF). 2023-24 rows have no updatedAt.

Observations (unit: soil samples), period = the cycle's financial year (1 April - 31 March), dims.scheme = the
scheme slug (SCHEMES; decoded once with the portal's public getSchemes query, e.g. shc_rkvy = "Soil Health Card
RKVY", nmnf = "National Mission on Natural Farming (NMNF)", others = "Others"):
    soil.shc_npk_oc_samples         dims.parameter n (available nitrogen), p (phosphorus), k (potassium),
                                    oc (organic carbon); dims.class high / medium / low
    soil.shc_ph_samples             soil reaction; dims.class acidic / neutral / alkaline
    soil.shc_ec_samples             electrical conductivity; dims.class saline / non_saline
    soil.shc_micronutrient_samples  dims.parameter s (sulphur), fe (iron), zn (zinc), cu (copper), b (boron),
                                    mn (manganese); dims.class sufficient / deficient
The class thresholds are the Soil Health Card scheme's, applied by the portal; they are not in the response.
publisher_as_of is the row's updatedAt in IST (the latest of the block rows for a district total).

Geography:
- surat_taluka/<code>: the portal's "block". In Gujarat the SHC block is the revenue taluka. Codes and names are
  shared with surat_talukas (BLOCKS maps the portal's names: BARDOLI -> bardoli, CHORASI -> chorasi, ...,
  Suratcity -> surat_city). The portal still files the city as one "Suratcity" block (code 4242), not as the six
  city talukas of surat.nic.in, and has no rows for Ambika or Areth (2023-24 to 2026-27).
- surat_district/surat: the sum of the block rows of the same scheme, cycle, parameter and class. The portal does
  not send a district row; its district view adds the block rows up the same way in the browser. A class that
  is missing (absent key, null parameter or null count) in any block row of that scheme and cycle makes the
  district value not_reported rather than a partial sum. A null count in a block row is stored as not_reported.

Cadence: the portal re-processes the counts daily (updatedAt), and samples keep being entered for past cycles
(2024-25 rows were updated on 2026-10-23), so every cycle is re-fetched; checked weekly. The current cycle is
in progress (2026-27: 11 rows on 2026-10-24, a few hundred samples per block).

Quirks and caveats:
- The class counts of one row do not always add up to the same total for every parameter: one sample can lack
  one parameter (2025-26 Mangrol: 3,307 samples for N but 3,306 for S). validate() allows a small difference.
- Counts are samples tested, not farms, cards or area; a block's sample count depends on the year's targets.
- The response carries database ids (_id) and a "__v" field; they are not stored.
- An unknown block name or scheme id fails the document, so codes and slugs stay stable; add it to BLOCKS or
  SCHEMES.
- The API is undocumented; it is what the public dashboard uses, with the same query text.

Licence: Government of India portal (Department of Agriculture & Farmers Welfare); no explicit open licence was
found on the portal. Aggregate public statistics, reproduced with attribution.
"""
from __future__ import annotations

import json
from datetime import datetime

from ..config import TZ
from ..model import Geo, Metric, Obs, Raw, Result, Source, ValidationError
from ..parse import fy_period, fy_start
from ..surat import TALUKA_NOTE
from .surat_talukas import NAMES

PORTAL = 'https://soilhealth.dac.gov.in/'
API = 'https://soilhealth4.dac.gov.in/'
STATE_ID = '63f922a6dbc0f7fe06751641'       # GUJARAT
DISTRICT_ID = '63f92c6189d86ca9e2bc2283'    # SURAT (district code 459)
FIRST_CYCLE = 2023                          # the portal's cycle list starts at 2023-24

# the portal's own query text (Nutrient Dashboard page)
QUERY = """query GetNutrientDashboardForPortal($state: ID, $district: ID, $block: ID, $village: ID, $cycle: String, $count: Boolean,$scheme: String) {
  getNutrientDashboardForPortal(state: $state, district: $district, block: $block, village: $village, cycle: $cycle, count: $count,scheme: $scheme)
}"""

SOURCE = Source(
    id='shc_soil_surat',
    name='Soil Health Card nutrient dashboard: Surat district talukas',
    publisher='Department of Agriculture & Farmers Welfare, Government of India (Soil Health Card portal)',
    url=PORTAL,
    module='agriculture',
    cadence='weekly',
    interval_hours=24 * 7,          # counts are re-processed daily, but they move slowly
    geo_note='Surat district talukas as Soil Health Card blocks (surat_taluka; the city is one surat_city block) '
             'and the Surat district total (sum of the block rows)',
    licence_note='Government of India portal (soilhealth.dac.gov.in); no explicit open licence',
    notes=('Counts of soil samples by test-result class, per block, scheme and cycle (financial year), from the '
           'public GraphQL API behind the portal\'s Nutrient Dashboard. District values are sums of the block '
           'rows, as the portal\'s district view shows them. The current cycle is in progress.'),
    metrics=(
        Metric('soil.shc_npk_oc_samples', 'Soil samples by N, P, K and organic-carbon class', 'samples',
               'Soil samples tested under the Soil Health Card programme in the cycle (financial year), by '
               'dims.parameter (n = available nitrogen, p = phosphorus, k = potassium, oc = organic carbon), '
               'dims.class (high, medium, low) and dims.scheme.'),
        Metric('soil.shc_ph_samples', 'Soil samples by pH class', 'samples',
               'Soil samples tested in the cycle by soil reaction class, dims.class (acidic, neutral, alkaline), '
               'and dims.scheme.'),
        Metric('soil.shc_ec_samples', 'Soil samples by salinity (EC) class', 'samples',
               'Soil samples tested in the cycle by electrical-conductivity class, dims.class (saline, '
               'non_saline), and dims.scheme.'),
        Metric('soil.shc_micronutrient_samples', 'Soil samples by micronutrient sufficiency', 'samples',
               'Soil samples tested in the cycle by dims.parameter (s = sulphur, fe = iron, zn = zinc, cu = copper, '
               'b = boron, mn = manganese), dims.class (sufficient, deficient) and dims.scheme.'),
    ),
)

# response key -> (metric, dims.parameter or None)
PARAMETERS = {
    'n': ('soil.shc_npk_oc_samples', 'n'),
    'p': ('soil.shc_npk_oc_samples', 'p'),
    'k': ('soil.shc_npk_oc_samples', 'k'),
    'OC': ('soil.shc_npk_oc_samples', 'oc'),
    'pH': ('soil.shc_ph_samples', None),
    'EC': ('soil.shc_ec_samples', None),
    'S': ('soil.shc_micronutrient_samples', 's'),
    'Fe': ('soil.shc_micronutrient_samples', 'fe'),
    'Zn': ('soil.shc_micronutrient_samples', 'zn'),
    'Cu': ('soil.shc_micronutrient_samples', 'cu'),
    'B': ('soil.shc_micronutrient_samples', 'b'),
    'Mn': ('soil.shc_micronutrient_samples', 'mn'),
}
CLASSES = {'High': 'high', 'Medium': 'medium', 'Low': 'low', 'Acidic': 'acidic', 'Neutral': 'neutral',
           'Alkaline': 'alkaline', 'Saline': 'saline', 'NonSaline': 'non_saline', 'Sufficient': 'sufficient',
           'Deficient': 'deficient'}

# portal block name (lower case) -> surat_taluka code
BLOCKS = {
    'bardoli': 'bardoli', 'chorasi': 'chorasi', 'choryasi': 'chorasi', 'kamrej': 'kamrej', 'mahuva': 'mahuva',
    'mandvi': 'mandvi', 'mangrol': 'mangrol', 'olpad': 'olpad', 'palsana': 'palsana', 'umarpada': 'umarpada',
    'suratcity': 'surat_city', 'surat city': 'surat_city', 'ambika': 'ambika', 'areth': 'areth',
}

# scheme id -> dims.scheme, decoded with the portal's getSchemes query on 2026-10-24
SCHEMES = {
    '660f941a5c8405ca8375c7c6': 'shc_rkvy',                     # Soil Health Card RKVY
    '6847f8ffc5086e743fbc77e4': 'nmnf',                         # National Mission on Natural Farming (NMNF)
    '6a193cc9ec600a329f830c28': 'others',                       # Others
    '67fe3b57945e1f97b651fa64': 'school_shc',                   # School Soil Health Card
    '663c805326a0446a669500b4': 'nmeo_oilseed',                 # NMEO Oilseed
    '6641a76640b8d7c6a7b419ca': 'movcd_ner',                    # MOVCD NER
    '6641a7ea874be0780e00d5a1': 'pkvy',                         # PKVY
    '6645ad613a7971d0160ef31c': 'smam',                         # Sub mission on Agriculture Mechanization
    '66472f30b7ae80f037dfeeb7': 'aif',                          # Agri Infrastructure Fund (AIF)
    '665439d7ea3e054866323088': 'pdmc',                         # PDMC
    '6655e70a99422e03b9f9d77a': 'pmfby',                        # Pradhan Mantri Fasal Bima Yojna
    '66571f1db6a2581eb3d924ce': 'bamboo_mission',               # National Bamboo Mission
    '6658631edc56ca00f50e35bb': 'food_nutrition_security',      # Food and Nutrition Security
    '6660050ecc4518d1117479ac': 'rad',                          # Rainfed Area Development (RAD)
    '666c498e4af9299d955ba694': 'midh',                         # MIDH
    '6672707046bfb892131d7418': 'rkvy_agroforestry',            # RKVY Agroforestry
    '67c9a569a05a99fa19028c2f': 'karnataka_raitha_samriddhi',   # Karnataka Raitha Samriddhi Yojane
    '6a426c8ce98086b860bff7d3': 'pulses_mission',               # Pulses mission
}


def fetch(ctx):
    now = ctx.now
    current = now.year if now.month >= 4 else now.year - 1
    for year in range(FIRST_CYCLE, current + 1):
        cycle = f'{year}-{(year + 1) % 100:02d}'
        variables = {'state': STATE_ID, 'district': DISTRICT_ID, 'cycle': cycle}
        raw = ctx.post(API, json={'query': QUERY, 'variables': variables}, meta={'cycle': cycle}, soft=True)
        if raw is not None:
            yield raw


def _as_of(row: dict) -> str | None:
    """'2026-10-23T17:54:00.877Z' -> '2026-10-23T23:24' (IST)."""
    stamp = row.get('updatedAt')
    if not stamp:
        return None
    return datetime.fromisoformat(stamp).astimezone(TZ).strftime('%Y-%m-%dT%H:%M')


def parse(raw: Raw) -> Result:
    doc = json.loads(raw.body)
    if doc.get('errors'):
        raise ValueError(f'GraphQL errors: {doc["errors"]}')
    rows = (doc.get('data') or {}).get('getNutrientDashboardForPortal') or []
    res = Result()
    district: dict[tuple, tuple] = {}     # (metric, start, end, dims) -> ([block values], [block as_of])
    n_rows: dict[tuple, int] = {}         # (start, scheme) -> number of block rows
    for row in rows:
        if row['district']['code'] != '459' or row['state']['code'] != '24':
            raise ValueError(f'row for {row["district"]["name"]}, {row["state"]["name"]} is not Surat, Gujarat')
        block = row['block']['name'].strip().lower()
        if block not in BLOCKS:
            raise ValidationError(f'unknown Surat block {row["block"]["name"]!r}: add it to BLOCKS')
        if row['scheme'] not in SCHEMES:
            raise ValidationError(f'unknown scheme id {row["scheme"]!r}: decode it with getSchemes, add to SCHEMES')
        code, scheme = BLOCKS[block], SCHEMES[row['scheme']]
        start, end = fy_period(fy_start(row['cycle']))
        as_of = _as_of(row)
        n_rows[(start, scheme)] = n_rows.get((start, scheme), 0) + 1
        res.geos.append(Geo('surat_taluka', code, NAMES[code], 'surat_district', 'surat', note=TALUKA_NOTE))
        for key, classes in row['results'].items():
            if key not in PARAMETERS:
                raise ValueError(f'unknown soil parameter {key!r} in the response')
            if classes is None:
                continue
            metric, parameter = PARAMETERS[key]
            for cls, value in classes.items():
                dims = {'class': CLASSES[cls], 'scheme': scheme}
                if parameter:
                    dims['parameter'] = parameter
                v = None if value is None else float(value)
                res.observations.append(Obs(metric, 'surat_taluka', code, start, end, value=v,
                                            status='reported' if v is not None else 'not_reported',
                                            dims=dims, publisher_as_of=as_of))
                values, stamps = district.setdefault((metric, start, end, tuple(sorted(dims.items()))), ([], []))
                values.append(v)
                stamps.append(as_of or '')
    for (metric, start, end, dims), (values, stamps) in district.items():
        # a block row without this class (missing key, null parameter or null count) leaves the sum incomplete
        complete = len(values) == n_rows[(start, dict(dims)['scheme'])] and None not in values
        total = sum(values) if complete else None
        res.observations.append(Obs(metric, 'surat_district', 'surat', start, end, value=total,
                                    status='reported' if total is not None else 'not_reported', dims=dict(dims),
                                    publisher_as_of=max(stamps) or None))
    return res


def validate(result: Result, raw: Raw) -> None:
    cycle = (raw.meta.get('cycle') if raw is not None else None) or ''
    fetched = raw.retrieved_at[:10] if raw is not None and raw.retrieved_at else '2100-12-31'
    current = int(fetched[:4]) if fetched[5:7] >= '04' else int(fetched[:4]) - 1    # FY start year of the fetch
    taluka = [o for o in result.observations if o.geo_level == 'surat_taluka']
    if not taluka:
        if cycle and fy_start(cycle) < current:
            raise ValidationError(f'no rows for the finished cycle {cycle}; API or layout may have changed')
        return
    blocks = {o.geo_code for o in taluka if o.dims['scheme'] == 'shc_rkvy'}
    if cycle and fy_start(cycle) < current and len(blocks) < 5:
        raise ValidationError(f'only {len(blocks)} Surat blocks under Soil Health Card RKVY in {cycle}')
    for o in result.observations:
        if not '2015-04-01' <= o.period_start <= f'{current}-04-01':
            raise ValidationError(f'cycle starting {o.period_start} is before SHC began or after the fetch')
        if o.value is not None and not 0 <= o.value <= 200_000:
            raise ValidationError(f'implausible sample count {o.value} ({o.geo_code}, {o.dims})')
    # within one block row, every parameter's classes add up to (nearly) the same number of samples
    totals: dict[tuple, dict] = {}
    for o in taluka:
        row = (o.geo_code, o.period_start, o.dims['scheme'])
        param = (o.metric_id, o.dims.get('parameter'))
        totals.setdefault(row, {}).setdefault(param, 0)
        totals[row][param] += o.value or 0
    for row, per_param in totals.items():
        hi, lo = max(per_param.values()), min(per_param.values())
        if hi - lo > max(5, hi * 0.01):
            raise ValidationError(f'{row}: parameter totals range from {lo} to {hi}; a class was mis-read')
