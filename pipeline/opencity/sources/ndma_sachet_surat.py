"""NDMA SACHET: official disaster alerts (CAP 1.2) that cover Surat district.

Publisher: National Disaster Management Authority (NDMA), Government of India, through SACHET, the national
Common Alerting Protocol (CAP) platform built by C-DOT. The alerts themselves are issued by IMD centres
(for Gujarat: IMD Ahmedabad), the Central Water Commission (CWC), INCOIS and State Disaster Management
Authorities (Gujarat SDMA); in the alert files checked, the state SDMA had re-issued the IMD alert with a
local-language block added.

Endpoints (both plain GETs, no key; robots.txt is absent, i.e. nothing is disallowed):
  RSS  https://sachet.ndma.gov.in/cap_public_website/rss/rss_india.xml
       RSS 2.0, <copyright>public domain</copyright>; the newest 100 items for all of India (about 17 hours
       of alerts on 23-24 Oct 2026, none for Gujarat). Each <item>:
         title     the alert headline (English or a regional language)
         category  CAP category ("Met")
         link      https://sachet.ndma.gov.in/cap_public_website/FetchXMLFile?identifier=<guid>
         author    "controlroom@ndma.gov.in (IMD Mumbai)": NDMA's address and, in brackets, the originating agency
         guid      a number such as 1792759763404029 (it appears to start with the creation time in ms)
         pubDate   RFC 822 time (GMT)
  CAP  https://sachet.ndma.gov.in/cap_public_website/FetchXMLFile?identifier=<guid>
       One CAP 1.2 <cap:alert>: identifier ("IN-1792759763404029_29"), sender ("Maharashtra-SDMA"), sent,
       status (Actual/Exercise/Test/...), msgType (Alert/Update/Cancel), scope, references
       ("IMD-Mumbai,IN-1792759763404029_46,2026-10-23T18:18:56+05:30"), and one <cap:info> per language with
       category, event, urgency, severity, certainty, effective, onset, expires, headline, description,
       instruction, a "Polygon URL" parameter and <cap:area> (areaDesc, geocode "LGD District Code" values).
       The guid identifies the alert THREAD: the URL returns the thread's latest message, so after an SDMA
       re-issue (msgType Update) the same URL serves the SDMA message, whose references name the IMD original
       (same number, other suffix). SACHET's "CAP XML Feed Integration Guide for Agencies" asks consumers to
       send If-None-Match with the last ETag (304 when unchanged); the fetcher does that.
SACHET is reported to block bursts of requests (not tested here): requests are spaced by the fetcher's
per-host delay, at most MAX_CAPS alert files are requested per run, and a 403/429 stops the run.

Which alerts are fetched and stored:
1. From the RSS, only items that might concern Surat: the agency in the author brackets names Gujarat or
   Ahmedabad (Gujarat SDMA, IMD Ahmedabad), or the title names Surat or Gujarat ("Surat" as a whole word, so
   not "Suratgarh"; also Gujarati સુરત / ગુજરાત). Alerts from other agencies whose RSS title does not name
   Surat or Gujarat are assumed not to cover Surat (a known limitation; CWC and INCOIS titles name the place).
2. A fetched alert is stored only if its CAP area covers Surat district: a geocode "LGD District Code" 459
   (Surat district's Local Government Directory code, as tagged ref:LGD:district on the OpenStreetMap
   boundary saved in reference/district-modules/osm-surat-ahmedabad-admin-boundaries-tags-2026-09-27.json),
   or an areaDesc that names Surat (whole word, or સુરત). The polygon file (FetchPolygonXMLFile) is not
   fetched: SACHET lists the districts it covers as geocodes, and fetching polygons would double the requests.
   Only status "Actual" is stored (Test/Exercise/Draft/System messages are ignored).

What is stored (geography surat_district):
- one 'cap_alert' record per alert thread, keyed by the guid, so a re-issue or update is a new version of
  the same record. Attributes: alert_id, identifier, sender, sent, status, msg_type, references, category,
  event, urgency, severity, certainty, effective, onset, expires (ISO, IST, minutes), headline, description,
  instruction (English info block, or the first one), headline_local + language_local (first non-English
  block), area_desc, lgd_district_codes, cap_url. CAP <contact> is never stored.
  The RSS keeps an alert for about a day, so records are history, not a complete current list: an alert is
  in effect while effective <= now < expires and its latest msg_type is not "Cancel".
- metric sachet.alerts: value 1 per alert thread on the day (IST) of its latest message, with dims.alert =
  the guid and dims.severity = CAP severity in lower case (extreme, severe, moderate, minor, unknown).
  Summing gives the number of alerts for Surat per day, by severity. A Cancel adds no count. If an update on
  the same day changes the severity, both severities stay stored for that day (observations are never
  deleted): count distinct dims.alert for an exact daily total. "Active now" comes from the records.
  (Counts across several alerts cannot be computed in parse(), which sees one document at a time.)

Cadence: alerts are continuous (IMD nowcasts are valid for about 3 hours); the RSS covers about a day, so an
hourly refresh misses nothing. Outside the monsoon there is usually nothing for Surat and nothing is stored.

Licence: the RSS feed states "public domain"; the alerts are official Government of India warnings.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import datetime

from ..config import TZ
from ..model import Metric, Obs, Raw, Record, Result, Source, ValidationError
from ..surat import SURAT_DISTRICT

RSS = 'https://sachet.ndma.gov.in/cap_public_website/rss/rss_india.xml'
CAP = 'https://sachet.ndma.gov.in/cap_public_website/FetchXMLFile?identifier={guid}'
NS = {'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}
SURAT_LGD = '459'               # LGD district code of Surat (OSM ref:LGD:district, see the docstring)
MAX_CAPS = 20                   # alert files requested per run at most (SACHET's firewall blocks bursts)

SENDER_WORDS = ('gujarat', 'ahmedabad')                 # RSS author brackets: Gujarat SDMA, IMD Ahmedabad
TITLE_WORDS = ('surat', 'gujarat')
TITLE_GUJARATI = ('સુરત', 'ગુજરાત')
SEVERITIES = ('extreme', 'severe', 'moderate', 'minor', 'unknown')
URGENCIES = ('Immediate', 'Expected', 'Future', 'Past', 'Unknown')
CERTAINTIES = ('Observed', 'Likely', 'Possible', 'Unlikely', 'Unknown')

SOURCE = Source(
    id='ndma_sachet_surat',
    name='NDMA SACHET official alerts (CAP) covering Surat district',
    publisher='National Disaster Management Authority, SACHET CAP platform (alerts issued by IMD, CWC, INCOIS and '
              'State Disaster Management Authorities)',
    url='https://sachet.ndma.gov.in/CapFeed',
    module='alerts',
    cadence='hourly',
    interval_hours=1,
    record_types=('cap_alert',),
    geo_note='Surat district: alerts whose CAP area lists LGD district code 459 or names Surat.',
    licence_note='RSS feed states "public domain"; official Government of India warnings',
    notes='Only RSS items from Gujarat/Ahmedabad agencies or with Surat/Gujarat in the title are opened (at most '
          f'{MAX_CAPS} per run). Records are alert history keyed by the SACHET guid (an update is a new version). '
          'Counts are per alert and day; "active now" is computed from the records\' effective/expires.',
    metrics=(
        Metric('sachet.alerts', 'Official alerts for Surat district (SACHET)', 'alerts',
               'Value 1 for each SACHET alert thread whose CAP area covers Surat district, on the IST day of its '
               'latest message; dims.alert = SACHET guid, dims.severity = CAP severity (extreme, severe, moderate, '
               'minor, unknown). Sum for alerts per day or per severity; Cancel messages add nothing.'),
    ),
)


# ---------- RSS ----------

def _words(text: str) -> list[str]:
    """'Suratgarh, Surat-city' -> ['suratgarh', 'surat', 'city']."""
    return ''.join(ch if ch.isalnum() else ' ' for ch in text.lower()).split()


def rss_items(body: bytes) -> list[dict]:
    root = ET.fromstring(body)
    if root.tag != 'rss':
        raise ValueError(f'not an RSS feed (root <{root.tag}>)')
    out = []
    for item in root.findall('./channel/item'):
        author = item.findtext('author') or ''
        out.append({'guid': (item.findtext('guid') or '').strip(), 'title': item.findtext('title') or '',
                    'agency': author.partition('(')[2].rstrip(') '), 'link': item.findtext('link') or ''})
    return out


def might_cover_surat(item: dict) -> bool:
    words = _words(item['title'])
    return (any(w in item['agency'].lower() for w in SENDER_WORDS) or any(w in words for w in TITLE_WORDS)
            or any(w in item['title'] for w in TITLE_GUJARATI))


def fetch(ctx):
    rss = ctx.get(RSS)
    yield rss
    guids = [i['guid'] for i in rss_items(rss.body) if i['guid'].isdigit() and might_cover_surat(i)]
    for guid in reversed(guids[:MAX_CAPS]):            # the feed is newest first; process oldest first
        raw = ctx.get(CAP.format(guid=guid), meta={'alert_id': guid}, soft=True)
        if raw is not None:
            yield raw


# ---------- CAP ----------

def _ist(stamp: str | None) -> str | None:
    """'2026-10-23T18:52:46+05:30' -> '2026-10-23T18:52' (IST)."""
    if not stamp:
        return None
    return datetime.fromisoformat(stamp.strip()).astimezone(TZ).strftime('%Y-%m-%dT%H:%M')


def _text(el, path: str) -> str | None:
    v = el.findtext(path, namespaces=NS)
    return v.strip() if v and v.strip() else None


def read_cap(body: bytes) -> dict:
    """The fields of one CAP alert we keep (no <contact>), with times in IST."""
    root = ET.fromstring(body)
    if root.tag != '{urn:oasis:names:tc:emergency:cap:1.2}alert':
        raise ValueError(f'not a CAP 1.2 alert (root <{root.tag}>)')
    infos = root.findall('cap:info', NS)
    if not infos:
        raise ValueError('CAP alert without <info>')
    main = next((i for i in infos if (_text(i, 'cap:language') or '').lower().startswith('en')), infos[0])
    local = next((i for i in infos if i is not main), None)
    identifier = _text(root, 'cap:identifier') or ''
    a = {
        'alert_id': identifier.partition('-')[2].partition('_')[0],      # 'IN-1792759763404029_29' -> guid
        'identifier': identifier,
        'sender': _text(root, 'cap:sender'),
        'sent': _ist(_text(root, 'cap:sent')),
        'status': _text(root, 'cap:status'),
        'msg_type': _text(root, 'cap:msgType'),
        'references': _text(root, 'cap:references'),
        'language': _text(main, 'cap:language'),
    }
    for field in ('category', 'event', 'urgency', 'severity', 'certainty', 'headline', 'description', 'instruction'):
        a[field] = _text(main, f'cap:{field}')
    for field in ('effective', 'onset', 'expires'):
        a[field] = _ist(_text(main, f'cap:{field}'))
    if local is not None:
        a['language_local'] = _text(local, 'cap:language')
        a['headline_local'] = _text(local, 'cap:headline')
    areas = [x for i in infos for x in i.findall('cap:area', NS)]
    a['area_desc'] = '; '.join(dict.fromkeys(_text(x, 'cap:areaDesc') or '' for x in areas)) or None
    codes = []
    for x in areas:
        for g in x.findall('cap:geocode', NS):
            if (_text(g, 'cap:valueName') or '').lower() == 'lgd district code' and _text(g, 'cap:value'):
                codes.append(_text(g, 'cap:value'))
    a['lgd_district_codes'] = list(dict.fromkeys(codes))
    return a


def covers_surat(a: dict) -> bool:
    area = a['area_desc'] or ''
    return SURAT_LGD in a['lgd_district_codes'] or 'surat' in _words(area) or 'સુરત' in area


def parse(raw: Raw) -> Result:
    head = raw.body[:2048].lstrip()
    if b'<rss' in head:
        rss_items(raw.body)                 # the index: checked for shape, nothing to store
        return Result()
    a = read_cap(raw.body)
    if a['status'] != 'Actual' or not covers_surat(a):
        return Result()
    a['cap_url'] = CAP.format(guid=a['alert_id'])
    res = Result(geos=[SURAT_DISTRICT], records=[Record('cap_alert', a['alert_id'], a)])
    if a['msg_type'] != 'Cancel':
        day = a['sent'][:10]
        res.observations.append(Obs('sachet.alerts', 'surat_district', 'surat', day, day, value=1,
                                    dims={'alert': a['alert_id'], 'severity': (a['severity'] or 'unknown').lower()}))
    return res


def validate(result: Result, raw: Raw) -> None:
    if raw is not None and b'<rss' in raw.body[:2048] and not rss_items(raw.body):
        raise ValidationError('the SACHET RSS feed has no items')
    for r in result.records:
        a = r.attrs
        if not a['alert_id'].isdigit():
            raise ValidationError(f'unexpected CAP identifier {a["identifier"]!r}')
        if raw is not None and raw.meta.get('alert_id') not in (None, a['alert_id']):
            raise ValidationError(f'asked for alert {raw.meta["alert_id"]} but got {a["identifier"]}')
        if (a['severity'] or 'unknown').lower() not in SEVERITIES or a['urgency'] not in URGENCIES + (None,) \
                or a['certainty'] not in CERTAINTIES + (None,):
            raise ValidationError(f'{a["identifier"]}: not a CAP severity/urgency/certainty: '
                                  f'{a["severity"]}/{a["urgency"]}/{a["certainty"]}')
        if not a['sent'] or a['sent'] < '2015-01-01':
            raise ValidationError(f'{a["identifier"]}: implausible sent time {a["sent"]}')
        if raw is not None and raw.retrieved_at and a['sent'][:10] > raw.retrieved_at[:10]:
            raise ValidationError(f'{a["identifier"]}: sent {a["sent"]} after the fetch ({raw.retrieved_at})')
        if a['effective'] and a['expires'] and a['expires'] < a['effective']:
            raise ValidationError(f'{a["identifier"]}: expires {a["expires"]} before effective {a["effective"]}')
        if not covers_surat(a):
            raise ValidationError(f'{a["identifier"]}: stored but its area does not cover Surat')
