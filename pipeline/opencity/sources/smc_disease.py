"""SMC Health Department disease incidence statistics + VBDC month-wise activity statistics.

Two pages, one adapter (fetch() tags each document with raw.meta['page']):

1. 'disease' - https://www.suratmunicipal.gov.in/Departments/HealthDepartmentDiseaseReports
   Seven HTML tables, one per tab, each named by a (visually hidden) <caption>:
     Gastro Enteritis, Enteric Fever, Pulmonary TB, Pneumonia, Hepatitis, Cholera
         header: Month | Particulars | Jan .. Dec | TOT
         rows:   <year> | Ind | 12 monthly values | total     (Ind = incidence)
                 ''     | D   | 12 monthly values | total     (D = deaths; the year cell is usually blank)
     Malaria Statistics (a different layout, one row per month):
         Month | Year | Collection | Examined | Positive Cases - Nos. | Positive Cases - (%) |
         P. Vivex(+) Case - Nos. | ..(%) | P. Falci.(+) Cases - Nos. | ..(%) | Death
         plus one 'Total' row per year.
   Coverage on the snapshot: 1995-2022 (cholera from 2002), malaria Jan 2005 - Oct 2023.

2. 'vbdc' - https://www.suratmunicipal.gov.in/Departments/VectorBorneDiseasesControlStatistics
   One wide table, one row per month (Jan 2005 - Oct 2023) plus a 'Total' row per year:
     intra-domestic survey (houses checked, breeding spots checked, positive spots by mosquito type),
     peri-domestic survey (construction sites checked, breeding spots, positives by mosquito type),
     biological control, notices, administrative charges, source reduction, fogging rounds.

The yearly TOT columns / 'Total' rows are NOT stored (they are sums of the months, and on the VBDC
page some are Excel-rounded, e.g. '1.01E+08'); parse() uses them only as a cross-check against
column shifts. Percent columns of the malaria table are derived ratios and are not stored either.
Both pages were last updated by SMC in November 2023, so the series are stale; that is expected.
"""
from __future__ import annotations

import re
from datetime import datetime

from ..model import Metric, Obs, Raw, Result, Source, ValidationError
from ..parse import clean, html_tables, month_no, month_period, num
from ..surat import SMC

DISEASE_URL = 'https://www.suratmunicipal.gov.in/Departments/HealthDepartmentDiseaseReports'
VBDC_URL = 'https://www.suratmunicipal.gov.in/Departments/VectorBorneDiseasesControlStatistics'

SOURCE = Source(
    id='smc_disease',
    name='SMC disease incidence statistics and vector-control activity (monthly)',
    publisher='Surat Municipal Corporation, Health Department and Vector Borne Diseases Control (VBDC) Department',
    url=DISEASE_URL,
    module='health',
    cadence='monthly',
    interval_hours=24 * 7,          # both pages were last updated Nov 2023; a weekly check is plenty
    geo_note='SMC city (whole corporation area); no zone or ward breakdown is published on these pages',
    licence_note='Surat Municipal Corporation web pages; public information',
    notes=('Disease incidence ("Ind") is described on SMC\'s Disease Incidence home page as admitted new cases '
           'reported at eight Surat hospitals (Maskati, Surat General, Ashktashram, Lokhat, Mahavir General, '
           'Mission, New Civil, SMIMER), so it is a hospital-based count, not total community incidence. '
           'The last year of a table can end in zeros (e.g. Pulmonary TB Nov-Dec 2022 = 0 after ~700/month); '
           'they are stored as published (0, reported) because the page prints 0, but they may be unfilled months. '
           'Blank cells are stored as not_reported. Yearly totals and percentages are not stored.'),
    metrics=(
        Metric('health.disease.cases', 'Disease cases (incidence)', 'cases',
               'Monthly cases by disease (dims.disease). For gastroenteritis, enteric fever, pulmonary TB, '
               'pneumonia, hepatitis and cholera this is the "Ind" (incidence) row: admitted new cases reported '
               'at eight Surat hospitals. For malaria it is "Positive Cases - Nos." from the blood-smear '
               'surveillance table.'),
        Metric('health.disease.deaths', 'Disease deaths', 'deaths',
               'Monthly deaths by disease (dims.disease): the "D" row of each disease table, or the "Death" '
               'column of the malaria table.'),
        Metric('health.malaria.smears_collected', 'Malaria blood smears collected', 'samples',
               'Malaria surveillance table, column "Collection": blood samples collected in the month.'),
        Metric('health.malaria.smears_examined', 'Malaria blood smears examined', 'samples',
               'Malaria surveillance table, column "Examined": samples examined in the month.'),
        Metric('health.malaria.positive_by_species', 'Malaria positive cases by parasite species', 'cases',
               'Positive cases by species (dims.species: p_vivax, p_falciparum); columns "P. Vivex(+) Case - Nos." '
               'and "P. Falci.(+) Cases - Nos.". On the snapshot they add up to the total positive cases.'),
        Metric('vbdc.houses_checked', 'Houses checked (intra-domestic survey)', 'houses',
               'VBDC intra-domestic survey: "No. of Houses checked" in the month (repeat visits count again).'),
        Metric('vbdc.construction_sites_checked', 'Construction sites checked (peri-domestic survey)', 'sites',
               'VBDC peri-domestic survey: "Checked Construction" in the month.'),
        Metric('vbdc.breeding_spots_checked', 'Potential mosquito breeding spots checked', 'spots',
               'Column "Breedingspot" / "Breeding spot" of the intra- or peri-domestic survey (dims.survey). '
               'Read as spots checked: positives by mosquito type are reported separately and are a small '
               'fraction of it.'),
        Metric('vbdc.breeding_spots_positive', 'Breeding spots found positive, by mosquito type', 'spots',
               'Positive breeding spots by survey (dims.survey: intra_domestic, peri_domestic) and mosquito type '
               '(dims.mosquito: anopheles, aedes, culex, mixed). The published "Total" column is their sum.'),
        Metric('vbdc.biological_control', 'Biological control actions', 'count',
               'Column "Biological control" (e.g. larvivorous fish release); the page does not state the unit.'),
        Metric('vbdc.notices_issued', 'Notices issued for breeding sites', 'notices',
               'Column "Notice": notices issued to owners of premises with mosquito breeding.'),
        Metric('vbdc.admin_charges', 'Administrative charges levied for breeding sites', 'INR',
               'Column "Adm. Charge": administrative charges collected from defaulters. The column does not '
               'state a unit; the VBDC home page describes them as charges collected, so read as rupees.'),
        Metric('vbdc.source_reduction', 'Source reduction actions', 'count',
               'Column "Source Reduction" (breeding sources removed/eliminated); the page does not state the unit.'),
        Metric('vbdc.fogging_rounds', 'Fogging machine rounds', 'rounds',
               'Column "Fogging Machine Utilised (Round)", by equipment (dims.equipment: vehicle_mounted for '
               '"Geep mounted", handheld for "Handy Sets").'),
    ),
)

# caption text -> disease slug (dims.disease). Unknown captions fail loudly.
DISEASES = [
    (r'gastro', 'gastroenteritis'),
    (r'enteric|typhoid', 'enteric_fever'),
    (r'\btb\b|tubercul', 'pulmonary_tb'),
    (r'pneumonia', 'pneumonia'),
    (r'hepatitis|jaundice', 'hepatitis'),
    (r'cholera', 'cholera'),
    (r'malaria', 'malaria'),
]
EXPECTED_DISEASES = {slug for _, slug in DISEASES}

# malaria table header -> (metric, dims). Percent columns are matched first and skipped.
MALARIA_COLUMNS = [
    (r'%', None),
    (r'^collection', ('health.malaria.smears_collected', {})),
    (r'^examined', ('health.malaria.smears_examined', {})),
    (r'^positive cases', ('health.disease.cases', {'disease': 'malaria'})),
    (r'viv[ae]x', ('health.malaria.positive_by_species', {'species': 'p_vivax'})),
    (r'falci', ('health.malaria.positive_by_species', {'species': 'p_falciparum'})),
    (r'^deaths?$', ('health.disease.deaths', {'disease': 'malaria'})),
]

# VBDC header (group - column, as expanded by html_tables) -> (metric, dims); None = cross-check only
_MOSQ = {'ano': 'anopheles', 'aedes': 'aedes', 'culex': 'culex', 'mix': 'mixed'}
VBDC_COLUMNS = [
    (r'^intra.*houses checked', ('vbdc.houses_checked', {})),
    (r'^intra.*breeding ?spot', ('vbdc.breeding_spots_checked', {'survey': 'intra_domestic'})),
    *[(rf'^intra.* - {k}\.?$', ('vbdc.breeding_spots_positive', {'survey': 'intra_domestic', 'mosquito': v}))
      for k, v in _MOSQ.items()],
    (r'^intra.* - total$', 'intra_total'),
    (r'^peri.*checked construction', ('vbdc.construction_sites_checked', {})),
    (r'^peri.*breeding ?spot', ('vbdc.breeding_spots_checked', {'survey': 'peri_domestic'})),
    *[(rf'^peri.* - {k}\.?$', ('vbdc.breeding_spots_positive', {'survey': 'peri_domestic', 'mosquito': v}))
      for k, v in _MOSQ.items()],
    (r'^peri.* - total$', 'peri_total'),
    (r'^biological control', ('vbdc.biological_control', {})),
    (r'^notice', ('vbdc.notices_issued', {})),
    (r'^adm\.? ?charge', ('vbdc.admin_charges', {})),
    (r'^source reduction', ('vbdc.source_reduction', {})),
    (r'fogging.*(geep|jeep|vehicle)', ('vbdc.fogging_rounds', {'equipment': 'vehicle_mounted'})),
    (r'fogging.*hand', ('vbdc.fogging_rounds', {'equipment': 'handheld'})),
]


def fetch(ctx):
    yield ctx.get(DISEASE_URL, meta={'page': 'disease'})
    yield ctx.get(VBDC_URL, meta={'page': 'vbdc'})


# ---------- helpers ----------

def _page(raw: Raw) -> str:
    page = (raw.meta or {}).get('page')
    if page:
        return page
    # parse-file / tests without meta: recognise the page by its content
    t = raw.text
    if re.search(r'Intra Domestic survey', t, re.I):
        return 'vbdc'
    if re.search(r'Ind=Incidence|Gastro Enteritis Statistics', t, re.I):
        return 'disease'
    raise ValueError('cannot tell which SMC page this is (set raw.meta["page"] to "disease" or "vbdc")')


def _as_of(raw: Raw) -> str | None:
    """'Last Updated: November 09, 2023 03:38 PM' -> '2023-11-09'."""
    m = re.search(r'id="spnLastUpdated"[^>]*>([^<]+)<', raw.text)
    if not m:
        return None
    s = clean(m.group(1))
    for f in ('%B %d, %Y %I:%M %p', '%B %d, %Y'):
        try:
            return datetime.strptime(s, f).date().isoformat()
        except ValueError:
            continue
    return None


def _disease(caption: str) -> str:
    c = caption.lower()
    for pat, slug in DISEASES:
        if re.search(pat, c):
            return slug
    raise ValueError(f'unknown disease table caption {caption!r}')


def _obs(metric, start, end, v, dims, as_of) -> Obs:
    return Obs(metric, 'smc_city', 'smc', start, end, value=v,
               status='reported' if v is not None else 'not_reported', dims=dict(dims), publisher_as_of=as_of)


def _crosscheck(what: str, checks: list[tuple[str, float, float]]) -> None:
    """checks: (label, sum of parsed months, published total). Small publisher discrepancies exist on the
    pages (e.g. Gastro 2005: months add to 3405, TOT 3411); a column shift produces many gross ones."""
    gross = [c for c in checks if abs(c[1] - c[2]) > max(20.0, 0.1 * abs(c[2]))]
    if len(gross) > 2:
        sample = '; '.join(f'{lab}: months sum {s:g} vs total {t:g}' for lab, s, t in gross[:4])
        raise ValidationError(f'{what}: {len(gross)} rows whose months do not add up to the published total '
                              f'(layout may have changed): {sample}')


# ---------- disease page ----------

def _parse_ind_d(table, disease: str, as_of, res: Result) -> None:
    hdr = table.find_row('particulars')
    if hdr < 0:
        raise ValueError(f'{disease}: no "Particulars" header row')
    months: dict[int, int] = {}
    tot_col = None
    for j, h in enumerate(table.rows[hdr]):
        h = h.strip()
        if j < 2 or not h:
            continue
        if re.match(r'(?i)tot', h):
            tot_col = j
        else:
            months[j] = month_no(h)         # KeyError on an unexpected header: fail loudly
    if sorted(months.values()) != list(range(1, 13)):
        raise ValueError(f'{disease}: month columns are {sorted(months.values())}, expected Jan..Dec')
    checks = []
    year = None
    for row in table.rows[hdr + 1:]:
        if not any(c.strip() for c in row):
            continue
        ycell, part = row[0].strip(), row[1].strip().lower()
        if part in ('ind', 'incidence'):
            if not re.fullmatch(r'(19|20)\d\d', ycell):
                raise ValueError(f'{disease}: incidence row without a year: {row[:3]}')
            year = int(ycell)
            metric = 'health.disease.cases'
        elif part in ('d', 'death', 'deaths'):
            if year is None or (ycell and ycell != str(year)):
                raise ValueError(f'{disease}: death row {row[:3]} does not follow its year\'s incidence row')
            metric = 'health.disease.deaths'
        else:
            raise ValueError(f'{disease}: unknown Particulars value {row[1]!r}')
        total = 0.0
        for j, m in months.items():
            v = num(row[j]) if j < len(row) else None
            total += v or 0
            start, end = month_period(year, m)
            res.observations.append(_obs(metric, start, end, v, {'disease': disease}, as_of))
        if tot_col is not None:
            # every row on the page has a TOT; a blank one (e.g. values shifted one cell right) counts as 0
            published = num(row[tot_col]) if tot_col < len(row) else None
            checks.append((f'{year} {row[1]}', total, published or 0.0))
    _crosscheck(f'{disease} table', checks)


def _parse_malaria(table, as_of, res: Result) -> None:
    hdr = table.find_row('month', 'year', 'examined')
    if hdr < 0:
        raise ValueError('malaria: header row (Month | Year | ... Examined ...) not found')
    cols: dict[int, tuple] = {}
    for j, h in enumerate(table.rows[hdr]):
        hl = h.strip().lower()
        if j < 2:
            if hl not in ('month', 'year'):
                raise ValueError(f'malaria: unexpected leading header {h!r}')
            continue
        for pat, target in MALARIA_COLUMNS:
            if re.search(pat, hl):
                if target is not None:
                    cols[j] = target
                break
        else:
            raise ValueError(f'malaria: unknown column {h!r}')
    found = {(m, d.get('species')) for m, d in cols.values()}
    if len(found) != 6:
        raise ValueError(f'malaria: expected 6 count columns, found {sorted(found, key=str)}')
    sums: dict[tuple, float] = {}
    totals: dict[tuple, float] = {}
    for row in table.rows[hdr + 1:]:
        if not any(c.strip() for c in row):
            continue
        label, ycell = row[0].strip(), row[1].strip()
        if not re.fullmatch(r'(19|20)\d\d', ycell):
            raise ValueError(f'malaria: bad year cell in row {row[:3]}')
        year = int(ycell)
        if label.lower().startswith('total'):
            for j in cols:
                v = num(row[j])
                if v is not None:
                    totals[(year, j)] = v
            continue
        month = month_no(label)
        start, end = month_period(year, month)
        for j, (metric, dims) in cols.items():
            v = num(row[j]) if j < len(row) else None
            sums[(year, j)] = sums.get((year, j), 0.0) + (v or 0)
            res.observations.append(_obs(metric, start, end, v, dims, as_of))
    _crosscheck('malaria table', [(f'{y} {table.rows[hdr][j]}', sums.get((y, j), 0.0), t)
                                  for (y, j), t in sorted(totals.items())])


def _parse_disease_page(raw: Raw, as_of, res: Result) -> None:
    seen = set()
    for table in html_tables(raw.body):
        if not table.caption or not re.search(r'statistics', table.caption, re.I):
            continue
        disease = _disease(table.caption)
        if disease in seen:
            raise ValueError(f'two tables for {disease}')
        seen.add(disease)
        if disease == 'malaria':
            _parse_malaria(table, as_of, res)
        else:
            _parse_ind_d(table, disease, as_of, res)
    missing = EXPECTED_DISEASES - seen
    if missing:
        raise ValidationError(f'disease tables missing from page: {sorted(missing)}')


# ---------- VBDC page ----------

def _parse_vbdc_page(raw: Raw, as_of, res: Result) -> None:
    tables = [t for t in html_tables(raw.body) if t.find_row('intra domestic') >= 0]
    if len(tables) != 1:
        raise ValueError(f'expected one VBDC activity table, found {len(tables)}')
    table = tables[0]
    hdr = table.find_row('month', 'year', 'intra domestic')
    cols: dict[int, object] = {}
    for j, h in enumerate(table.rows[hdr]):
        hl = clean(h).lower()
        if j < 2:
            if hl not in ('month', 'year'):
                raise ValueError(f'vbdc: unexpected leading header {h!r}')
            continue
        for pat, target in VBDC_COLUMNS:
            if re.search(pat, hl):
                cols[j] = target
                break
        else:
            raise ValueError(f'vbdc: unknown column {h!r}')
    if len(cols) != len(VBDC_COLUMNS) or len({str(t) for t in cols.values()}) != len(VBDC_COLUMNS):
        raise ValueError(f'vbdc: expected {len(VBDC_COLUMNS)} distinct columns, mapped {len(cols)}')
    group_total = {'intra_total': 'intra_domestic', 'peri_total': 'peri_domestic'}
    row_checks, sums, totals = [], {}, {}
    for row in table.rows[hdr + 1:]:
        if not any(c.strip() for c in row):
            continue
        label, ycell = row[0].strip(), row[1].strip()
        if not re.fullmatch(r'(19|20)\d\d', ycell):
            raise ValueError(f'vbdc: bad year cell in row {row[:3]}')
        year = int(ycell)
        if label.lower().startswith('total'):
            for j in cols:
                v = num(row[j])       # Excel-style '1.01E+08' parses; only used for the cross-check
                if v is not None:
                    totals[(year, j)] = v
            continue
        month = month_no(label)
        start, end = month_period(year, month)
        pos = {'intra_domestic': 0.0, 'peri_domestic': 0.0}
        published_total = {}
        for j, target in cols.items():
            v = num(row[j]) if j < len(row) else None
            sums[(year, j)] = sums.get((year, j), 0.0) + (v or 0)
            if isinstance(target, str):         # the per-row "Total" of positive spots: check only
                if v is not None:
                    published_total[group_total[target]] = v
                continue
            metric, dims = target
            if metric == 'vbdc.breeding_spots_positive':
                pos[dims['survey']] += v or 0
            res.observations.append(_obs(metric, start, end, v, dims, as_of))
        for survey, t in published_total.items():
            row_checks.append((f'{label} {year} {survey}', pos[survey], t))
    _crosscheck('vbdc positive spots by mosquito type vs "Total" column', row_checks)
    _crosscheck('vbdc yearly totals', [(f'{y} {table.rows[hdr][j]}', sums.get((y, j), 0.0), t)
                                       for (y, j), t in sorted(totals.items())])


# ---------- adapter entry points ----------

def parse(raw: Raw) -> Result:
    res = Result(geos=[SMC])
    as_of = _as_of(raw)
    page = _page(raw)
    if page == 'disease':
        _parse_disease_page(raw, as_of, res)
    elif page == 'vbdc':
        _parse_vbdc_page(raw, as_of, res)
    else:
        raise ValueError(f'unknown page tag {page!r}')
    return res


# plausible monthly maxima for the whole city (well above anything on the pages)
_MAX = {
    'health.disease.cases': 20000,
    'health.disease.deaths': 1000,
    'health.malaria.smears_collected': 1_000_000,
    'health.malaria.smears_examined': 1_000_000,
    'health.malaria.positive_by_species': 20000,
    'vbdc.houses_checked': 20_000_000,
    'vbdc.construction_sites_checked': 200_000,
    'vbdc.breeding_spots_checked': 50_000_000,
    'vbdc.breeding_spots_positive': 500_000,
    'vbdc.biological_control': 100_000,
    'vbdc.notices_issued': 200_000,
    'vbdc.admin_charges': 100_000_000,
    'vbdc.source_reduction': 1_000_000,
    'vbdc.fogging_rounds': 200_000,
}


def validate(result: Result, raw: Raw | None) -> None:
    obs = result.observations
    if not obs:
        raise ValidationError('no observations parsed')
    by = {}
    for o in obs:
        hi = _MAX[o.metric_id]
        if o.value is not None and not 0 <= o.value <= hi:
            raise ValidationError(f'implausible {o.metric_id} = {o.value} ({o.period_start}, {o.dims})')
        by[(o.metric_id, o.period_start, tuple(sorted(o.dims.items())))] = o.value

    def val(metric, start, **dims):
        return by.get((metric, start, tuple(sorted(dims.items()))))

    reported = [o.period_start for o in obs if o.status == 'reported']
    if not reported:
        raise ValidationError('every value is blank')
    latest = max(reported)
    if latest < '2020-01-01':
        raise ValidationError(f'latest reported month is {latest}; the page used to run to 2022-2023')
    if raw is not None and raw.retrieved_at and latest > raw.retrieved_at[:10]:
        raise ValidationError(f'latest reported month {latest} is after the retrieval date {raw.retrieved_at}')

    oddities = []
    if any(o.metric_id.startswith('health.') for o in obs):
        for d in sorted(EXPECTED_DISEASES):
            n = sum(1 for o in obs if o.metric_id == 'health.disease.cases' and o.dims.get('disease') == d
                    and o.status == 'reported')
            if n < 120:
                raise ValidationError(f'only {n} monthly case values for {d}; page layout may have changed')
        for o in obs:
            if o.metric_id != 'health.disease.cases' or o.value is None:
                continue
            d, s = o.dims['disease'], o.period_start
            deaths = val('health.disease.deaths', s, disease=d)
            if deaths is not None and deaths > o.value:
                oddities.append(f'{d} {s}: deaths {deaths:g} > cases {o.value:g}')
            if d == 'malaria':
                pv = val('health.malaria.positive_by_species', s, species='p_vivax')
                pf = val('health.malaria.positive_by_species', s, species='p_falciparum')
                ex = val('health.malaria.smears_examined', s)
                if pv is not None and pf is not None and pv + pf != o.value:
                    oddities.append(f'malaria {s}: Pv {pv:g} + Pf {pf:g} != positive {o.value:g}')
                if ex is not None and o.value > ex:
                    oddities.append(f'malaria {s}: positive {o.value:g} > examined {ex:g}')
    if any(o.metric_id.startswith('vbdc.') for o in obs):
        n = sum(1 for o in obs if o.metric_id == 'vbdc.houses_checked' and o.status == 'reported')
        if n < 120:
            raise ValidationError(f'only {n} monthly VBDC rows; page layout may have changed')
        pos: dict[tuple, float] = {}
        for o in obs:
            if o.metric_id == 'vbdc.breeding_spots_positive' and o.value is not None:
                k = (o.period_start, o.dims['survey'])
                pos[k] = pos.get(k, 0.0) + o.value
        for (s, survey), p in sorted(pos.items()):
            checked = val('vbdc.breeding_spots_checked', s, survey=survey)
            if checked is not None and p > checked:
                oddities.append(f'{survey} {s}: {p:g} positive spots > {checked:g} checked')
    if len(oddities) > 3:
        raise ValidationError(f'{len(oddities)} internally inconsistent months, e.g. ' + '; '.join(oddities[:4]))
