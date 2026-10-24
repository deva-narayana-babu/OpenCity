"""SMC Urban Community Development (UCD) department: the welfare schemes it implements, as text records.

Publisher: Surat Municipal Corporation, Urban Community Development (UCD) Department (Departments > Social Welfare >
Urban Community Development). The page is in Gujarati; it describes the schemes the department runs for the urban
poor: the DAY-NULM components (self-help groups, skills training, self-employment loans, shelters for the urban
homeless, street vendors), PM SVANidhi and the state's Mukhyamantri Mahila Utkarsh Yojana.

Endpoint: one plain GET, no parameters, no login or captcha (robots.txt on www.suratmunicipal.gov.in returns 404,
so nothing is disallowed):

    https://www.suratmunicipal.gov.in/Departments/UrbanCommunityDevelopmentHome

Response layout (server-rendered HTML) inside <div class="contentblock gujartifont">:

    <div class="section-margin"> <p>intro: UCD started in 1967 ...</p> <p>DAY-NULM intro ...</p> </div>
    <div class="section-margin">
      <h2>સામાજિક ગતિશીલતા અને સંસ્થાગત વિકાસ ઘટક (Social Mobilisation And Institution Development – SM&ID)</h2>
      <div class="text-2x text-bold">(અ) સ્વ-સહાય જૂથ (Self Help Group-SHG)</div>              optional sub-scheme
      <ul class="list-group">
        <li class="list-group-item"><div class="text-2x text-bold mar-b10">હેતુ</div> purpose text </li>   labelled
        <li class="list-group-item"> a plain point </li>                                                unlabelled
      </ul> ...
    </div> ...

Records -> one 'smc_ucd_scheme' per scheme: an <h2> section, or each sub-scheme heading inside it ("(અ)", "(બ)",
"(ક)"). The page is the complete list, so schemes that disappear get closed. Key: the English words of the heading
as a slug ('self-help-group-shg', 'pmsvanidhi', 'mmuy'). Attributes (all text exactly as published, in Gujarati;
nothing is translated or summarised):
    title           the heading as printed
    name_en         the English (Latin-script) words of the heading ('Self Help Group-SHG', 'MMUY')
    component       for a sub-scheme, the <h2> title it sits under; otherwise None
    purpose         item labelled હેતુ (purpose)
    eligibility     item labelled લાભાર્થીની પાત્રતા (beneficiary eligibility)
    age_limit       item labelled લાભાર્થીની ઉમર (beneficiary age)
    assistance      item labelled સહાય (assistance)
    project_amount  item labelled પ્રોજેક્ટ રકમ (project amount)
    subsidy         item labelled સબસીડી (subsidy)
    training_fee    item labelled તાલીમ ફી (training fee)
    points          the unlabelled items, in order (list)
Only labels present on the page are set. An unknown label raises an error so a new kind of field is noticed.

Snapshot 2026-10-24 (footer "Last Updated: December 24, 2021"): 9 schemes: Self Help Group (under SM&ID), EST&P,
SEP Individual / Group / SHG Bank Linkage (under SEP), SUH, SUSV, PMSVANidhi, MMUY.

Caveats: editorial text, last edited in 2021, so amounts and rules may be out of date (e.g. PM SVANidhi loan
tranches); there are no beneficiary counts, so no observations are emitted. The two intro paragraphs are not
stored. Geography: SMC city. Cadence: static, checked weekly.
Licence: Surat Municipal Corporation web page; public information; no explicit open-data licence.
"""
from __future__ import annotations

from ..model import Raw, Record, Result, Source, ValidationError
from ..parse import clean, html_text

URL = 'https://www.suratmunicipal.gov.in/Departments/UrbanCommunityDevelopmentHome'

SOURCE = Source(
    id='smc_ucd_schemes',
    name='SMC Urban Community Development schemes',
    publisher='Surat Municipal Corporation, Urban Community Development Department',
    url=URL,
    module='schemes',
    cadence='static',
    interval_hours=24 * 7,          # the page was last edited in 2021; weekly is plenty
    record_types=('smc_ucd_scheme',),
    geo_note='SMC city (schemes run by SMC\'s UCD department)',
    licence_note='Surat Municipal Corporation web page; public information (no explicit open-data licence)',
    notes=('Gujarati text kept as published (not translated): purpose, eligibility, age, assistance, project '
           'amount, subsidy and training fee where the page gives them, plus the unlabelled points. No beneficiary '
           'counts are published, so there are no observations.'),
)

# Gujarati item label -> attribute
LABELS = {
    'હેતુ': 'purpose',
    'લાભાર્થીની પાત્રતા': 'eligibility',
    'લાભાર્થીની ઉમર': 'age_limit',
    'સહાય': 'assistance',
    'પ્રોજેક્ટ રકમ': 'project_amount',
    'સબસીડી': 'subsidy',
    'તાલીમ ફી': 'training_fee',
}
SUB_HEADINGS = ('<div class="text-2x text-bold">', '<div class="text-3x text-bold">')   # labels add " mar-b10"
ITEM = '<li class="list-group-item">'


def fetch(ctx):
    yield ctx.get(URL)


def _text(fragment: str) -> str:
    return clean(html_text(fragment).replace('\n', ' '))


def _name_en(title: str) -> str:
    """'(અ) સ્વ-સહાય જૂથ (Self Help Group-SHG)' -> 'Self Help Group-SHG'."""
    name = ' '.join(w for w in title.split() if w.isascii() and w != '-')
    if name.startswith('(') and name.endswith(')'):
        name = name[1:-1]
    return name


def _slug(s: str) -> str:
    out = ''.join(ch.lower() if ch.isascii() and ch.isalnum() else ' ' for ch in s)
    return '-'.join(out.split())


def _scheme(title: str, component: str | None, block: str) -> Record:
    attrs = {'title': title, 'name_en': _name_en(title), 'component': component, 'points': []}
    for item in block.split(ITEM)[1:]:
        item = item[:item.find('</li>')].strip()
        if item.startswith('<div'):
            end = item.find('</div>') + len('</div>')
            label = _text(item[:end])
            if label not in LABELS:
                raise ValueError(f'{title}: unknown item label {label!r}')
            attrs[LABELS[label]] = _text(item[end:])
        else:
            attrs['points'].append(_text(item))
    return Record('smc_ucd_scheme', _slug(attrs['name_en']), attrs)


def parse(raw: Raw) -> Result:
    text = raw.text
    start = text.find('<div class="contentblock')
    if start < 0:
        raise ValueError('content block not found; page layout may have changed')
    end = text.find('<footer', start)
    region = text[start:end if end > 0 else len(text)]
    res = Result(complete_record_types=('smc_ucd_scheme',))
    for section in region.split('<div class="section-margin">')[1:]:
        if '<h2' not in section:
            continue                                   # the intro paragraphs
        h2_start = section.find('>', section.find('<h2')) + 1
        h2_end = section.find('</h2>')
        h2 = _text(section[h2_start:h2_end])
        rest = section[h2_end:]
        for marker in SUB_HEADINGS:
            rest = rest.replace(marker, '\x00')
        parts = rest.split('\x00')
        if ITEM in parts[0] or len(parts) == 1:
            res.records.append(_scheme(h2, None, parts[0]))
        for part in parts[1:]:
            res.records.append(_scheme(_text(part[:part.find('</div>')]), h2, part))
    return res


def validate(result: Result, raw: Raw) -> None:
    recs = result.records
    if not 5 <= len(recs) <= 40:
        raise ValidationError(f'{len(recs)} schemes parsed; expected about 9 (page layout may have changed)')
    for r in recs:
        a = r.attrs
        if not r.record_key or not a['name_en']:
            raise ValidationError(f'scheme {a["title"]!r} has no English name to key it by')
        if not any('઀' <= ch <= '૿' for ch in a['title']):
            raise ValidationError(f'{r.record_key}: title {a["title"]!r} is not in Gujarati')
        fields = [a[f] for f in LABELS.values() if f in a] + a['points']
        if not fields or any(len(f) < 5 for f in fields):
            raise ValidationError(f'{r.record_key}: no text, or an empty item')
    if not any('eligibility' in r.attrs for r in recs):
        raise ValidationError('no scheme has an eligibility item; labels may have changed')
