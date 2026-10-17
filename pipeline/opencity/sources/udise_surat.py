"""UDISE+ "Education highlights" for Surat district: schools, enrolment, teachers, PTR, infrastructure.

Endpoint (the one dashboard.udiseplus.gov.in's report page calls; no key, no Origin/Referer needed):
    POST https://api.udiseplus.gov.in/open-services/v1.1/kpi/edu-highlights
    body {"yearId": Y, "regionCode": "2422", "regionType": 12, "valueType": 1}
    2422 = Surat district, regionType 12 = district.
Response: {"status": true, "data": [ {yearId, regionName, regionCode, totSch, ...} ], "metaData": {...}}.
"data" is an empty list for a year that has no data (checked 2026-10-05: yearId 10 and 13 are empty,
11 and 12 have data).

Year ids: the dashboard bundle (report2026/static/js/main.*.js) maps
    {12: "2025-26", 11: "2024-25", 10: "2023-24", 9: "2022-23", 8: "2021-22"},
i.e. financial-year start = 2013 + yearId. Periods are the UDISE+ year as an Indian financial year
(1 April - 31 March); UDISE+ figures are an annual snapshot of that school year.

Field meanings come from the same bundle, which labels every field shown on the dashboard
("Total Number of Schools" = totSch, "PTR at Foundational level" = foundation, "Transition Rates
Foundational to Preparatory" = tft, ...). Two exceptions, kept with that caveat in their descriptions:
  - dpt/dmt/dst are returned but not labelled on the dashboard; by analogy with tft/tmt/tst and the
    UDISE+ report tables they are read as dropout rates at the preparatory/middle/secondary stage.
  - overallScore/overallGrade are labelled "Performance Grading Index"; the 2025-26 value for Surat
    (328.84) matches the PGI-D 2025-26 report (329 of 600, Prachesta-1), so they are PGI-D for that year.
Unlabelled fields (tenrPPri, tschPpri) are not stored. A null in a labelled field is stored as
not_reported.

Geography: UDISE+ district 2422 is the whole of Surat district (SMC area plus the rural talukas),
so everything is geo surat_district/surat, never smc_city.

The response carries request/response timestamps; normalize() blanks them so an unchanged answer
is archived once.
"""
from __future__ import annotations

import json
import re

from ..model import Metric, Obs, Raw, Result, Source, ValidationError
from ..parse import fy_period, num
from ..surat import SURAT_DISTRICT

URL = 'https://api.udiseplus.gov.in/open-services/v1.1/kpi/edu-highlights'
PAGE = 'https://dashboard.udiseplus.gov.in/'
REGION_CODE = '2422'        # Surat district
REGION_TYPE = 12            # district
YEAR_ID_BASE = 2013         # yearId 12 -> FY 2025-26
FIRST_YEAR_ID = 11          # 2024-25; yearId 10 (2023-24) returned no data for Surat on 2026-10-05
MAX_YEARS_PER_RUN = 4

M = 'udise.'

SOURCE = Source(
    id='udise_surat',
    name='UDISE+ education highlights, Surat district (annual)',
    publisher='Department of School Education & Literacy, Ministry of Education, Government of India (UDISE+)',
    url=PAGE,
    module='education',
    cadence='annual',
    interval_hours=24 * 30,     # one snapshot per school year; a monthly check catches the new year and revisions
    geo_note='Surat district (UDISE+ district 2422): SMC area plus the rural talukas; not SMC city limits',
    licence_note='Government of India (MoE UDISE+) open-services API; public data',
    notes='yearId -> FY mapping and field labels taken from the UDISE+ dashboard bundle. dpt/dmt/dst (dropout) '
          'are unlabelled on the dashboard and interpreted by analogy; see module docstring.',
    metrics=(
        Metric(M + 'schools', 'Schools', 'schools', 'Total number of schools (totSch).'),
        Metric(M + 'schools.by_management', 'Schools by management', 'schools',
               'Schools by management (dims.management). "govt" is the subtotal of kendriya_vidyalaya, '
               'navodaya_vidyalaya, other_central_govt and state_govt; govt + govt_aided + private_unaided + '
               'other = all schools.'),
        Metric(M + 'schools.by_category', 'Schools by school category', 'schools',
               'Schools by UDISE+ school category, i.e. the classes offered (dims.category, e.g. '
               'upper_primary_1_8 = classes 1-8). Categories add up to all schools.'),
        Metric(M + 'schools.with_primary', 'Government / aided schools having primary levels', 'schools',
               'Number of government (dims.management=govt) or government-aided schools having primary levels.'),
        Metric(M + 'schools.primary_with_preprimary', 'Govt and aided primary schools with Balvatika', 'schools',
               'Number of government and government-aided primary schools having Balvatika / pre-primary sections.'),
        Metric(M + 'enrolment', 'Enrolment, foundational to secondary', 'students',
               'Total enrolment from the foundational to the secondary stage (tenrF2Sec).'),
        Metric(M + 'enrolment.by_stage', 'Enrolment by NEP stage', 'students',
               'Enrolment in the foundational / preparatory / middle / secondary stage (dims.stage); '
               'the four add up to udise.enrolment.'),
        Metric(M + 'enrolment.by_social_group', 'Enrolment by social group', 'students',
               'SC, ST, OBC and minority students, foundational to secondary (dims.group). Overlapping groups, '
               'not a partition of the total.'),
        Metric(M + 'enrolment.cwsn', 'Children with special needs enrolled', 'students',
               'Number of CWSN students, foundational to secondary.'),
        Metric(M + 'enrolment.by_management', 'Enrolment by school management', 'students',
               'Enrolment by school management (dims.management, same codes as udise.schools.by_management; '
               '"govt" is a subtotal).'),
        Metric(M + 'enrolment.by_category', 'Enrolment by school category', 'students',
               'Enrolment in schools of each UDISE+ school category (dims.category). As returned these do not '
               'add up to udise.enrolment (2024-25: 1,161,656 vs 1,286,170).'),
        Metric(M + 'teachers', 'Teachers', 'teachers', 'Total number of teachers (ttch).'),
        Metric(M + 'teachers.by_management', 'Teachers by school management', 'teachers',
               'Teachers by school management (dims.management; "govt" is a subtotal).'),
        Metric(M + 'ptr', 'Pupil-teacher ratio', 'pupils per teacher',
               'Pupil-teacher ratio at the foundational / preparatory / middle / secondary level (dims.stage).'),
        Metric(M + 'ger_pct', 'Gross enrolment ratio', '%',
               'Gross enrolment ratio at the foundational / preparatory / middle stage (dims.stage). Returned as '
               'null for districts so far (stored as not_reported).'),
        Metric(M + 'transition_rate_pct', 'Transition rate', '%',
               'Transition rate between NEP stages (dims.transition, e.g. middle_to_secondary).'),
        Metric(M + 'dropout_rate_pct', 'Dropout rate', '%',
               'Dropout rate at the preparatory / middle / secondary stage (dims.stage). API fields dpt/dmt/dst '
               'are not labelled on the UDISE+ dashboard; read as dropout rates by analogy with the UDISE+ reports.'),
        Metric(M + 'schools_with_facility_pct', 'Schools with a facility', '% of schools',
               'Percentage of schools having a facility (dims.facility); dims.condition is "available" or '
               '"functional" (e.g. electricity connection vs functional electricity connection).'),
        Metric(M + 'pgi_d.score', 'PGI-D overall score', 'points (of 600)',
               'Performance Grading Index for Districts overall score returned for this UDISE+ year (2025-26 '
               'matches the PGI-D 2025-26 report).'),
        Metric(M + 'pgi_d.grade', 'PGI-D grade', '',
               'PGI-D grade as text in value_text (e.g. PRACHESTA-1 = 51-60% of the maximum score).'),
    ),
)

MANAGEMENT = [('Kv', 'kendriya_vidyalaya'), ('Nv', 'navodaya_vidyalaya'), ('OthCenGovt', 'other_central_govt'),
              ('Govt', 'govt'), ('GovtAided', 'govt_aided'), ('PvtUnaided', 'private_unaided'), ('Oth', 'other')]
# field suffixes differ between the school, enrolment and teacher blocks
SCHOOL_MGMT = {'tsch' + s: c for s, c in MANAGEMENT} | {'tschStatGovt': 'state_govt'}
ENROL_MGMT = {'tenrF2SecKv': 'kendriya_vidyalaya', 'tenrF2SecNv': 'navodaya_vidyalaya',
              'tenrF2SecOthCgov': 'other_central_govt', 'tenrF2SecStateGov': 'state_govt', 'tenrF2SecGov': 'govt',
              'tenrF2SecGovAided': 'govt_aided', 'tenrF2SecPvtUnaided': 'private_unaided', 'tenrF2SecOth': 'other'}
TEACHER_MGMT = {'ttch' + s: c for s, c in MANAGEMENT} | {'ttchState': 'state_govt'}

CATEGORIES = [('1to5', 'primary_1_5'), ('1to8', 'upper_primary_1_8'), ('6to8', 'upper_primary_6_8'),
              ('1to10', 'secondary_1_10'), ('6to10', 'secondary_6_10'), ('9to10', 'secondary_9_10'),
              ('1to12', 'higher_secondary_1_12'), ('6to12', 'higher_secondary_6_12'),
              ('9to12', 'higher_secondary_9_12'), ('11to12', 'higher_secondary_11_12')]

STAGES4 = ('foundational', 'preparatory', 'middle', 'secondary')

# (field, metric, dims)
FIELDS: list[tuple[str, str, dict]] = [
    ('totSch', 'schools', {}),
    *[(f, 'schools.by_management', {'management': c}) for f, c in SCHOOL_MGMT.items()],
    *[('tsch' + k, 'schools.by_category', {'category': c}) for k, c in CATEGORIES],
    ('tschGovtPri', 'schools.with_primary', {'management': 'govt'}),
    ('tschGovtAidedPri', 'schools.with_primary', {'management': 'govt_aided'}),
    ('tschGovtAidedPri2', 'schools.primary_with_preprimary', {}),
    ('tenrF2Sec', 'enrolment', {}),
    *[(f, 'enrolment.by_stage', {'stage': s}) for f, s in zip(('tenrF', 'tenrP', 'tenrM', 'tenrS'), STAGES4)],
    ('tenrF2SecSc', 'enrolment.by_social_group', {'group': 'sc'}),
    ('tenrF2SecSt', 'enrolment.by_social_group', {'group': 'st'}),
    ('tenrF2SecObc', 'enrolment.by_social_group', {'group': 'obc'}),
    ('tenrF2SecMinority', 'enrolment.by_social_group', {'group': 'minority'}),
    ('tenrFSecCwsn', 'enrolment.cwsn', {}),
    *[(f, 'enrolment.by_management', {'management': c}) for f, c in ENROL_MGMT.items()],
    *[('tenr' + k, 'enrolment.by_category', {'category': c}) for k, c in CATEGORIES],
    ('ttch', 'teachers', {}),
    *[(f, 'teachers.by_management', {'management': c}) for f, c in TEACHER_MGMT.items()],
    *[(f, 'ptr', {'stage': s}) for f, s in zip(('foundation', 'preparatory', 'middle', 'secondary'), STAGES4)],
    ('fger', 'ger_pct', {'stage': 'foundational'}),
    ('pger', 'ger_pct', {'stage': 'preparatory'}),
    ('mger', 'ger_pct', {'stage': 'middle'}),
    ('tft', 'transition_rate_pct', {'transition': 'foundational_to_preparatory'}),
    ('tmt', 'transition_rate_pct', {'transition': 'preparatory_to_middle'}),
    ('tst', 'transition_rate_pct', {'transition': 'middle_to_secondary'}),
    ('dpt', 'dropout_rate_pct', {'stage': 'preparatory'}),
    ('dmt', 'dropout_rate_pct', {'stage': 'middle'}),
    ('dst', 'dropout_rate_pct', {'stage': 'secondary'}),
    ('overallScore', 'pgi_d.score', {}),
]

FACILITIES = [
    ('elecPer', 'electricity', 'available'), ('elecPerFun', 'electricity', 'functional'),
    ('waterPer', 'drinking_water', 'available'), ('waterPerFun', 'drinking_water', 'functional'),
    ('toiletPer', 'toilet', 'available'), ('toiletPerFun', 'toilet', 'functional'),
    ('toiletBPer', 'boys_toilet', 'available'), ('toiletBPerFun', 'boys_toilet', 'functional'),
    ('toiletGPer', 'girls_toilet', 'available'), ('toiletGPerFun', 'girls_toilet', 'functional'),
    ('handwashPer', 'handwash', 'available'),
    ('pgroundPer', 'playground', 'available'),
    ('compPer', 'computer', 'available'), ('compPerFun', 'computer', 'functional'),
    ('internetPer', 'internet', 'available'),
    ('toiletCwsnPer', 'cwsn_toilet', 'available'), ('toiletCwsnPerFun', 'cwsn_toilet', 'functional'),
    ('rampWithHandrailPer', 'ramp_with_handrail', 'available'),
    ('kitGardPer', 'kitchen_garden', 'available'),
    ('rainWatPer', 'rainwater_harvesting', 'available'),
    ('libBbnkRcorPer', 'library_book_bank_reading_corner', 'available'),
    ('smartPerFun', 'smart_classroom', 'functional'),
]


def year_ids(now) -> list[int]:
    """UDISE+ year ids worth asking for: the current school year and up to three before it."""
    fy = now.year if now.month >= 4 else now.year - 1
    cur = fy - YEAR_ID_BASE
    return list(range(max(FIRST_YEAR_ID, cur - MAX_YEARS_PER_RUN + 1), cur + 1))


def fetch(ctx):
    for y in year_ids(ctx.now):
        body = {'yearId': y, 'regionCode': REGION_CODE, 'regionType': REGION_TYPE, 'valueType': 1}
        raw = ctx.post(URL, json=body, meta={'year_id': y}, soft=True)
        if raw is not None:
            yield raw


def normalize(body: bytes) -> bytes:
    return re.sub(rb'"(requestTimestamp|responseTimestamp)"\s*:\s*"[^"]*"', rb'"\1":""', body)


def _load(raw: Raw) -> dict:
    try:
        doc = json.loads(raw.body)
    except ValueError as e:
        raise ValidationError(f'UDISE+ response is not JSON: {e}') from None
    if not isinstance(doc, dict) or 'data' not in doc:
        raise ValidationError('UDISE+ response has no "data" key; API format changed?')
    if doc.get('status') is not True:
        raise ValidationError(f'UDISE+ status {doc.get("status")!r}: {doc.get("errorDetails")!r}')
    if not isinstance(doc['data'], list) or len(doc['data']) > 1:
        raise ValidationError(f'expected 0 or 1 data rows for one district, got {doc["data"]!r:.200}')
    return doc


def _value(v):
    if isinstance(v, bool):
        raise ValidationError(f'unexpected boolean {v!r}')
    return num(v)


def parse(raw: Raw) -> Result:
    res = Result(geos=[SURAT_DISTRICT])
    doc = _load(raw)
    if not doc['data']:
        return res                       # no data published for that year (yet)
    d = doc['data'][0]
    if str(d.get('regionCode')) != REGION_CODE or str(d.get('regionName', '')).strip().upper() != 'SURAT':
        raise ValidationError(f'response is for region {d.get("regionCode")!r} {d.get("regionName")!r}, not Surat')
    year_id = int(d['yearId'])
    if 'year_id' in raw.meta and int(raw.meta['year_id']) != year_id:
        raise ValidationError(f'asked for yearId {raw.meta["year_id"]}, got {year_id}')
    start, end = fy_period(YEAR_ID_BASE + year_id)

    def add(metric, v, dims):
        res.observations.append(Obs(M + metric, 'surat_district', 'surat', start, end, value=v,
                                    status='reported' if v is not None else 'not_reported', dims=dims))

    for field, metric, dims in FIELDS:
        if field in d:
            add(metric, _value(d[field]), dims)
    for field, facility, condition in FACILITIES:
        if field in d:
            add('schools_with_facility_pct', _value(d[field]), {'facility': facility, 'condition': condition})
    if 'overallGrade' in d:
        g = (d['overallGrade'] or '').strip()
        res.observations.append(Obs(M + 'pgi_d.grade', 'surat_district', 'surat', start, end, value_text=g or None,
                                    status='reported' if g else 'not_reported'))
    return res


def _sum_check(by, label, total_key, part_keys, slack=0):
    total = by.get(total_key)
    if total is None:
        return
    parts = [by.get(k) for k in part_keys]
    s = sum(p or 0 for p in parts)
    if abs(s - total) > slack:
        raise ValidationError(f'{label}: parts add up to {s}, total is {total}')


def validate(result: Result, raw: Raw) -> None:
    if not result.observations:
        if raw is not None and _load(raw)['data']:
            raise ValidationError('UDISE+ returned a data row but nothing was parsed')
        return
    starts = {o.period_start for o in result.observations}
    if len(starts) != 1:
        raise ValidationError(f'one response must cover one year, got {sorted(starts)}')
    fy = int(next(iter(starts))[:4])
    if raw is not None and not 2015 <= fy <= int(raw.retrieved_at[:4]):
        raise ValidationError(f'implausible UDISE+ year {fy}-{fy + 1 - 2000:02d}')
    by = {(o.metric_id[len(M):],) + tuple(sorted(o.dims.values())): o.value for o in result.observations}
    for key in (('schools',), ('enrolment',), ('teachers',)):
        if by.get(key) is None:
            raise ValidationError(f'core figure {key[0]} missing from the UDISE+ response')
    if not 1000 <= by[('schools',)] <= 10000:
        raise ValidationError(f'implausible number of schools {by[("schools",)]}')
    if not 200_000 <= by[('enrolment',)] <= 3_000_000:
        raise ValidationError(f'implausible enrolment {by[("enrolment",)]}')
    if not 10_000 <= by[('teachers',)] <= 150_000:
        raise ValidationError(f'implausible number of teachers {by[("teachers",)]}')
    # internal consistency: the publisher's own breakdowns must add up
    mg = ('govt', 'govt_aided', 'private_unaided', 'other')
    _sum_check(by, 'schools by management', ('schools',), [('schools.by_management', c) for c in mg])
    _sum_check(by, 'schools by category', ('schools',), [('schools.by_category', c) for _, c in CATEGORIES])
    _sum_check(by, 'enrolment by stage', ('enrolment',), [('enrolment.by_stage', s) for s in STAGES4])
    _sum_check(by, 'enrolment by management', ('enrolment',), [('enrolment.by_management', c) for c in mg])
    _sum_check(by, 'teachers by management', ('teachers',), [('teachers.by_management', c) for c in mg])
    gov = ('kendriya_vidyalaya', 'navodaya_vidyalaya', 'other_central_govt', 'state_govt')
    _sum_check(by, 'government schools', ('schools.by_management', 'govt'),
               [('schools.by_management', c) for c in gov])
    for o in result.observations:
        m, v = o.metric_id[len(M):], o.value
        if v is None:
            continue
        if v < 0:
            raise ValidationError(f'negative value {v} for {m} {o.dims}')
        if m.endswith('_pct') and v > 100:
            raise ValidationError(f'percentage over 100: {m} {o.dims} = {v}')
        if m == 'ptr' and not 1 <= v <= 100:
            raise ValidationError(f'implausible pupil-teacher ratio {v} {o.dims}')
        if m == 'pgi_d.score' and not 0 < v <= 600:
            raise ValidationError(f'PGI-D score {v} outside 0-600')
        if m.startswith(('schools.', 'enrolment.', 'teachers.')) and v > by.get((m.split('.')[0],), v):
            raise ValidationError(f'{m} {o.dims} = {v} exceeds the total')
