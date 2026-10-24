"""SMC active tenders: the live list of tenders invited by SMC zones and departments, with each notice's details.

Publisher: Surat Municipal Corporation. Tenders are invited by its zones and departments. Bids are submitted on
the e-procurement portal https://smctender.nprocure.com/ (run for SMC by (n)Code Solutions), which this source
does NOT read: bid documents, bidders and awards are not collected.

Endpoints (robots.txt on www.suratmunicipal.gov.in returns 404, so nothing is disallowed; no login or captcha):

1. List: GET https://www.suratmunicipal.gov.in/Information/Tender/Tenders  (no parameters), "Active Tenders".
   One <li> per tender:
       <span class="tender-serial">1</span>
       <form action="/Information/Tender/TenderInformation" method="post">
         <input type="hidden" name="hdnCustomerId" value="47260" />
         <p class="tender-description">Supply, Installation ... South Zone-B (Kanakpur) Surat ... work -4</p>
       </form>
       Start Date: 12-10-2026 11:00 | End Date: 26-10-2026 18:00
       Availability: 2 Day(s) | Submit within: 2 Day(s)
   The "View Tender Details" button posts that form. There is no anti-forgery token, only the hidden ID.

2. Detail: POST https://www.suratmunicipal.gov.in/Information/Tender/TenderInformation  with the form body
   hdnCustomerId=<id from the list>, which is exactly what the site's own button sends. The response is a
   <div class="list-group"> of label/value pairs: Tender Title, Description, Tender Notice Number, Tender Notice
   Date ("Wednesday , 07 October , 2026"), Required Category of Agency, Issuing Authority, Issuing Office, Tender
   Inviting Authority, Available between (two dates), Remaining period for Availability, Submission Date,
   Remaining period for Submission, Filled tender to be submitted to, Mode of submission, Tender Fees (in
   Rupees), Estimated Amount (in Rupees), Earnest Money Deposit (in Rupees), Documents Required, Probable Date
   of opening, and on some notices Prebid Conference Venue / Prebid Conference Date ("11:00 AM - Friday,
   30 October, 2026.").
   A notice's details do not change once it is published, so each ID is fetched ONCE (skip_if_seen), only when
   it first appears on the list. The ID travels in Raw.meta['tender_id'], because runner.reparse() does not
   replay the request body. Load on SMC: the first run posts once per listed tender (70 on 2026-10-24), and
   later daily runs make one GET plus one POST per new tender, 2 s apart (fetcher host delay). A detail page
   that fails to parse is posted again on the next run.

Stored:
-> 'tender' records from the list, keyed by the hdnCustomerId (e.g. '47260'). The list is the complete set of
   active tenders, so a tender that leaves it gets closed (valid_to = when it was first missing). Attributes:
     tender_id   the hdnCustomerId
     title       the list title, as published
     start       "Start Date" (ISO local datetime): documents available from
     end         "End Date" (ISO local datetime): last date for submission
     attempt     retender attempt number when the title says so, else None. Titles write it as "(2nd Attempt)",
                 "(2ND ATTEMPT)", "(Second Attempt)", "(Third Attempt)" or "(II ATTEMPT)" (22 of 70 on 2026-10-24)
   The "Availability" and "Submit within" day counts are not stored, because they change every day.
-> 'tender_notice' records from the detail pages, keyed by the same ID. These are never closed by the list:
   join them to the open 'tender' records to get the live ones. Attributes:
     tender_id, title, description, notice_no ("DMC/SZ-B/11/2026-27"), notice_date (ISO),
     agency_category ("Experienced"), issuing_authority, issuing_office, inviting_authority (designation and
       office as printed, lines joined with ", "; SMC truncates some, e.g. "surat municipal corporati"),
     available_from, available_to, submission_date, opening_date ("Probable Date of opening") (ISO dates),
     prebid_at (ISO local datetime of the prebid conference, None when not held),
     prebid_venue (as printed; in practice an office email such as exen.workshop@suratmunicipal.org. An email
       is kept only on an official domain: one notice gives a gmail.com address and one a misspelt
       "suratmunmicipal.org", and those become None),
     submit_to (office where a filled tender goes), submission_mode ("Postal Speed Post, RPAD"),
     fee_rs, estimated_amount_rs, emd_rs (Rupees, None when blank),
     amount_notes (the text SMC prints after an amount, by field: {'estimated_amount_rs': '+ GST'} or
       'without GST'; {} when there is none. Without a note the GST basis is not stated),
     documents_required (list of lines as printed),
     zone_code (surat.zone_code() of the issuing, else the inviting, authority when it names a zone; None for
       head-office departments; "New East (Sarthana) Zone" maps to east_b, whose zone office is at Sarthana. A bare
       "South Zone" maps to no zone, because SMC's South Zone is now split into South-A and South-B),
     other_labels (names of any labels this parser does not know; their values are not stored)
   Blank cells are stored as None. The "Remaining period" rows are not stored.
-> smc_city observations from the list, an instant reading dated to the day of the fetch (Asia/Kolkata, from
   Raw.retrieved_at), because the list has no data date (its "Last Updated: September 11, 2023" footer is a CMS
   edit time):
     tenders.active           number of tenders on the Active Tenders list
     tenders.closing_within   number whose End Date falls within dims.within_days ('2', '7', '14') days of the
                              fetch day (dates only; a tender closing today counts in every window, one whose
                              End Date has already passed but is still listed counts in none)
   validate() checks that "End Date" minus "Submit within" gives the fetch day (within a day), so a stale
   cached page is caught.

Snapshot 2026-10-24: 70 active tenders, all closing between 26 October and 20 November 2026 (4 within 2 days,
54 within 7, 69 within 14). Tender 47260: a passenger lift for the Moje-Gambheni health centre, South Zone-B
(Kanakpur), notice DMC/SZ-B/11/2026-27 of 07-10-2026, estimated Rs 12,49,799.25, EMD Rs 12,500, fee Rs 1,062,
submission 26-10-2026, probable opening 04-11-2026. Of the 70 detail pages, 24 had a prebid conference, 4 an
amount note ("+ GST" / "without GST"), 6 a blank estimated amount, and 41 named no zone that zone_code() knows
(mostly head-office departments such as Hydraulic, Drainage, Workshop and Light & Energy Efficiency).

Not collected, and why:
- Sums of estimated value by zone or department: each detail page is a separate document and parse() sees one
  document at a time, so the sum is not an observation. The 'tender_notice' records carry estimated_amount_rs
  and zone_code, so the dashboard can sum the live ones.
- Award, winner and contract value: not published on these pages.
- "Active Quotations" (/Information/Quotations, a separate list with Gujarati titles) and the e-Tenders
  explainer page (/Information/Tender/eTenders, text only) are not read.

Quirks and caveats:
- If SMC extends a tender, the list shows the new End Date (a new version of the 'tender' record), but the
  detail page is not fetched again, so 'tender_notice' keeps the dates as first published.
- Titles mix English and zone names in several spellings; the zone is taken from the authority fields, not the
  title.
- Some titles end in work numbers ("(W-1)", "work -4"); they are kept in the title.

Geography: SMC city (smc_city:smc) for counts; each notice names its zone (zone_code) or department.
Cadence: daily (the list changes daily; detail pages are fetched once per new tender). Units: tenders, Rupees.
Licence: Surat Municipal Corporation web pages; public information. No explicit open licence.
"""
from __future__ import annotations

from datetime import date, timedelta

from ..model import Metric, Obs, Raw, Record, Result, Source, ValidationError
from ..parse import clean, html_text, num, parse_date, parse_dt
from ..surat import SMC, zone_code

LIST_URL = 'https://www.suratmunicipal.gov.in/Information/Tender/Tenders'
DETAIL_URL = 'https://www.suratmunicipal.gov.in/Information/Tender/TenderInformation'
WINDOWS = (2, 7, 14)

SOURCE = Source(
    id='smc_tenders',
    name='SMC active tenders',
    publisher='Surat Municipal Corporation (tenders invited by its zones and departments)',
    url=LIST_URL,
    module='tenders',
    cadence='daily',
    interval_hours=24,
    record_types=('tender', 'tender_notice'),
    geo_note='SMC city; each tender notice names its issuing zone or department',
    licence_note='Surat Municipal Corporation web pages; public information',
    notes=('Each tender\'s detail page is fetched once, with the same form POST as the site\'s "View Tender '
           'Details" button (only the hidden ID). Counts are dated to the fetch day because the list has no data '
           'date. Bid documents, bidders and awards (smctender.nprocure.com) are not collected. Sums of estimated '
           'value are left to the dashboard (from the tender_notice records).'),
    metrics=(
        Metric('tenders.active', 'SMC active tenders', 'tenders',
               'Number of tenders on SMC\'s "Active Tenders" list on the fetch day.'),
        Metric('tenders.closing_within', 'SMC tenders closing soon', 'tenders',
               'Number of active tenders whose End Date (last date for submission) is on the fetch day or no more '
               'than dims.within_days (2, 7 or 14) days after it, counting whole dates.'),
    ),
)

# detail label (lower case) -> attribute; None = shown on the page but deliberately not stored (changes daily)
LABELS = {
    'tender title': 'title',
    'description': 'description',
    'tender notice number': 'notice_no',
    'tender notice date': 'notice_date',
    'required category of agency': 'agency_category',
    'issuing authority': 'issuing_authority',
    'issuing office': 'issuing_office',
    'tender inviting authority': 'inviting_authority',
    'available between': 'available',
    'remaining period for availability': None,
    'submission date': 'submission_date',
    'remaining period for submission': None,
    'filled tender to be submitted to': 'submit_to',
    'mode of submission': 'submission_mode',
    'tender fees (in rupees)': 'fee_rs',
    'estimated amount (in rupees)': 'estimated_amount_rs',
    'earnest money deposit (in rupees)': 'emd_rs',
    'documents required': 'documents_required',
    'probable date of opening': 'opening_date',
    'prebid conference venue': 'prebid_venue',
    'prebid conference date': 'prebid_date',
}
AMOUNTS = ('fee_rs', 'estimated_amount_rs', 'emd_rs')
# retender attempts written in words or Roman numerals ("(Second Attempt)", "(II ATTEMPT)")
ATTEMPT_WORDS = {'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5, 'sixth': 6, 'seventh': 7,
                 'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5, 'vi': 6, 'vii': 7}
OFFICIAL_EMAIL_DOMAINS = ('suratmunicipal.org', 'suratmunicipal.gov.in', 'gujarat.gov.in', 'gov.in', 'nic.in')
ITEM = '<div class="list-group-item">'
SERIAL = '<span class="tender-serial">'


def _between(text: str, start: str, end: str = '<') -> str:
    """Cleaned text after the first `start` up to the next `end` ('' if `start` is absent)."""
    i = text.find(start)
    if i < 0:
        return ''
    rest = text[i + len(start):]
    return clean(rest[:rest.find(end)] if end in rest else rest)


def _list_items(text: str) -> list[dict]:
    """Active Tenders list -> [{'tender_id', 'title', 'start', 'end', 'submit_within'}] in page order."""
    items = []
    for li in text.split(SERIAL)[1:]:
        items.append({
            'tender_id': _between(li, 'name="hdnCustomerId" value="', '"'),
            'title': _between(li, '<p class="tender-description">', '</p>'),
            'start': _between(li, 'Start Date: </span>'),
            'end': _between(li, 'End Date: </span>'),
            'submit_within': _between(li, 'Submit within: </span>'),
        })
    return items


def fetch(ctx):
    listing = ctx.get(LIST_URL)
    yield listing
    for item in _list_items(listing.text):
        tid = item['tender_id']
        if tid.isdigit():           # a malformed ID is reported by parse(); never post it
            yield ctx.post(DETAIL_URL, form={'hdnCustomerId': tid}, meta={'tender_id': tid},
                           skip_if_seen=True, soft=True)


def _attempt(title: str) -> int | None:
    """'(2nd Attempt)', 'YEARS.(2ND ATTEMPT)', '(Third Attempt)', '(II ATTEMPT)' -> 2, 2, 3, 2; None when the
    title names no attempt."""
    low = title.lower()
    i = low.find('attempt')
    words = low[:i].replace('(', ' ').split() if i >= 0 else []
    if not words:
        return None
    word = words[-1]
    digits = word[:len(word) - len(word.lstrip('0123456789'))]
    return int(digits) if digits else ATTEMPT_WORDS.get(word)


def _long_date(s: str) -> str | None:
    """'Wednesday , 07 October , 2026' -> '2026-10-07' (the weekday is dropped); '' -> None."""
    parts = [p.strip() for p in s.split(',') if p.strip()]
    if not parts:
        return None
    return parse_date(' '.join(parts[1:]), '%d %B %Y').isoformat()


def _amount(s: str) -> tuple[float | None, str | None]:
    """'₹ 5901693.32 - + GST' -> (5901693.32, '+ GST'); '₹ 12500' -> (12500.0, None); '' -> (None, None)."""
    value, _, note = s.partition(' - ')
    return num(value), note.strip() or None


def _prebid_at(s: str) -> str | None:
    """'11:00 AM - Friday, 30 October, 2026.' -> '2026-10-30T11:00'; '' -> None."""
    if not s:
        return None
    time, _, day = s.partition(' - ')
    return parse_dt(f'{_long_date(day.rstrip("."))} {time}', '%Y-%m-%d %I:%M %p')


def _official(s: str | None) -> str | None:
    """Keep a venue that is an email address only if it is on an official domain (one entry is a gmail.com
    address and one has a misspelt SMC domain); other venue text is kept as printed."""
    if s and '@' in s:
        domain = s.rsplit('@', 1)[1].strip().lower()
        # whole domain or a subdomain of it: 'gov.in' accepts 'gujarat.gov.in' but not 'notgov.in'
        if not any(domain == d or domain.endswith('.' + d) for d in OFFICIAL_EMAIL_DOMAINS):
            return None
    return s


def _zone(*authorities: str | None) -> str | None:
    for text in authorities:
        if text and 'zone' in text.lower():
            try:
                code = zone_code(text)
            except KeyError:
                continue
            # "Deputy Municipal Commissioner South Zone" oversees both South-A and South-B; the legacy
            # pre-split code 'south' would mislabel the notice, so look at the next authority instead
            if code != 'south':
                return code
    return None


def _parse_list(raw: Raw) -> Result:
    day = raw.retrieved_at[:10]
    res = Result(geos=[SMC], complete_record_types=('tender',))
    ends = []
    for it in _list_items(raw.text):
        if not it['tender_id'].isdigit():
            raise ValueError(f'tender without a numeric hdnCustomerId: {it["title"][:80]!r}')
        start, end = parse_dt(it['start']), parse_dt(it['end'])
        res.records.append(Record('tender', it['tender_id'], {
            'tender_id': it['tender_id'], 'title': it['title'], 'start': start, 'end': end,
            'attempt': _attempt(it['title'])}))
        ends.append(date.fromisoformat(end[:10]))
    today = date.fromisoformat(day)
    res.observations.append(Obs('tenders.active', 'smc_city', 'smc', day, day, value=float(len(ends))))
    for n in WINDOWS:
        count = sum(1 for e in ends if 0 <= (e - today).days <= n)
        res.observations.append(Obs('tenders.closing_within', 'smc_city', 'smc', day, day, value=float(count),
                                    dims={'within_days': str(n)}))
    return res


def _parse_detail(raw: Raw) -> Result:
    tid = str(raw.meta.get('tender_id', ''))
    if not tid.isdigit():
        raise ValueError('tender detail page without meta["tender_id"]; cannot key the record')
    text = raw.text
    start = text.find('<div class="list-group">')
    if start < 0:
        raise ValueError('no tender detail fields found; page layout may have changed')
    end = text.find('<footer', start)
    fields, other = {}, []
    for item in text[start:end if end > 0 else len(text)].split(ITEM)[1:]:
        label_html, _, value_html = item.partition('</div>')
        label = clean(html_text(label_html)).lower()
        lines = [clean(x) for x in html_text(value_html).split('\n') if clean(x)]
        if label not in LABELS:
            other.append(clean(html_text(label_html)))
        elif LABELS[label]:
            fields[LABELS[label]] = lines
    one = {k: ' '.join(v) for k, v in fields.items()}
    available = one.get('available', '').split(' - ')
    if len(available) != 2:
        raise ValueError(f'tender {tid}: unexpected "Available between" value {one.get("available")!r}')
    attrs = {
        'tender_id': tid,
        'title': one.get('title') or None,
        'description': one.get('description') or None,
        'notice_no': one.get('notice_no') or None,
        'notice_date': _long_date(one.get('notice_date', '')),
        'agency_category': one.get('agency_category') or None,
        'issuing_authority': ', '.join(fields.get('issuing_authority', [])) or None,
        'issuing_office': one.get('issuing_office') or None,
        'inviting_authority': ', '.join(fields.get('inviting_authority', [])) or None,
        'available_from': _long_date(available[0]),
        'available_to': _long_date(available[1]),
        'submission_date': _long_date(one.get('submission_date', '')),
        'opening_date': _long_date(one.get('opening_date', '')),
        'prebid_at': _prebid_at(one.get('prebid_date', '')),
        'prebid_venue': _official(one.get('prebid_venue') or None),
        'submit_to': one.get('submit_to') or None,
        'submission_mode': one.get('submission_mode') or None,
        'documents_required': fields.get('documents_required', []),
        'other_labels': other,
    }
    notes = {}
    for k in AMOUNTS:
        attrs[k], note = _amount(one.get(k, ''))
        if note:
            notes[k] = note
    attrs['amount_notes'] = notes
    attrs['zone_code'] = _zone(attrs['issuing_authority'], attrs['inviting_authority'])
    return Result(records=[Record('tender_notice', tid, attrs)])


def parse(raw: Raw) -> Result:
    if 'Below is the tender complete information' in raw.text:
        return _parse_detail(raw)
    if SERIAL in raw.text and 'Active Tenders' in raw.text:
        return _parse_list(raw)
    raise ValueError(f'unrecognised SMC tender page ({raw.url}); page layout may have changed')


def _page_day(item: dict) -> date:
    """The server's 'today': End Date minus 'Submit within' ('2 Day(s)')."""
    return parse_date(item['end'].split()[0]) - timedelta(days=int(item['submit_within'].split()[0]))


def validate(result: Result, raw: Raw) -> None:
    tenders = [r.attrs for r in result.records if r.record_type == 'tender']
    notices = [r.attrs for r in result.records if r.record_type == 'tender_notice']
    if result.observations and not 5 <= len(tenders) <= 1000:
        raise ValidationError(f'{len(tenders)} active tenders parsed (70 in Oct 2026); layout may have changed')
    for t in tenders:
        if t['end'] < t['start'] or not '2015-01-01' <= t['start'][:10] <= '2040-12-31':
            raise ValidationError(f'tender {t["tender_id"]}: implausible dates {t["start"]} .. {t["end"]}')
    for a in notices:
        if not a['title'] or not a['submission_date']:
            raise ValidationError(f'tender {a["tender_id"]}: no title or submission date on the detail page')
        for k, top in (('estimated_amount_rs', 5e10), ('emd_rs', 1e9), ('fee_rs', 1e7)):
            if a[k] is not None and not 0 <= a[k] <= top:
                raise ValidationError(f'tender {a["tender_id"]}: implausible {k} {a[k]}')
        for k in ('notice_date', 'available_from', 'available_to', 'submission_date', 'opening_date', 'prebid_at'):
            if a[k] and not '2015-01-01' <= a[k] <= '2040-12-31':
                raise ValidationError(f'tender {a["tender_id"]}: implausible {k} {a[k]}')
    if not tenders or raw is None or not raw.retrieved_at:
        return
    fetched = date.fromisoformat(raw.retrieved_at[:10])
    for it in _list_items(raw.text):
        if it['submit_within'][:1].isdigit() and abs((_page_day(it) - fetched).days) > 1:
            raise ValidationError(f'list counts days from {_page_day(it)}, not the fetch date {fetched}; '
                                  'stale cached page?')
