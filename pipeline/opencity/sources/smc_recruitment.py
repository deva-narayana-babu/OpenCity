"""SMC current recruitment: open job advertisements of Surat Municipal Corporation, as records plus daily counts.

Publisher: Surat Municipal Corporation (Recruitment cell; advertisements are issued as PRO press notices). The page
is "Current Recruitment", linked from the Recruitment Dashboard. Queries go to recruitment@suratmunicipal.org
(printed on the page).

Endpoint: one plain GET, no parameters, no login or captcha (robots.txt on www.suratmunicipal.gov.in returns
404, so nothing is disallowed):

    https://www.suratmunicipal.gov.in/Information/Recruitment

Response layout (server-rendered HTML, no tables). One panel per organisation (heading "Surat Municipal
Corporation"), a section label (<li class="... text-2x text-bold">Opening</li>), then one <li> per advertisement:

    <p class="gujartifont">જાહેરાત ક્રમાંક :પી.આર.ઓ.નં.૩૦૧, તા.૨૧/૧૦/૨૦૨૬ થી સુરત મહાનગરપાલિકાની ...</p>
    <span class="emag-link pad-r5">No of post(s):</span>18
    <span class="emag-link pad-r5">Application Start Date:</span>09/11/2026 11:00 AM
    <span class="emag-link pad-r5">Application End Date:</span>23/11/2026 11:00 PM
    <span class="emag-link pad-r5">Remaining Day(s):</span> 30 day(s)        ("Today" on the last day)
    <a href=".../Recruitment/">Apply Now</a>                  (only while applications are open)
    <a href=".../Contents/Jobs/Opening/1973333.pdf">View More</a>   (the advertisement PDF; not fetched)

The title is Gujarati only and starts with the advertisement number: "જાહેરાત ક્રમાંક :પી.આર.ઓ.નં.૩૦૧,
તા.૨૧/૧૦/૨૦૨૬" means "Advertisement no.: P.R.O. No. 301, dated 21/10/2026" (Gujarati digits).

-> 'recruitment_ad' records, one per advertisement. The page is the complete current list, so an advertisement
   that is taken off the page gets closed. Key: 'pro-<no>-<ad date>' (e.g. 'pro-301-2026-10-21'); if the PRO
   number cannot be read, 'pdf-<file name>' from the View More link. Attributes:
     pro_no             PRO advertisement number (int), from the title
     ad_date            date of the PRO notice (ISO), from the title
     title              the full Gujarati title as published
     posts              "No of post(s)" (int; None if blank)
     application_start  "Application Start Date" (ISO local datetime)
     application_end    "Application End Date" (ISO local datetime)
     organisation       panel heading ("Surat Municipal Corporation")
     section            section label ("Opening")
     notice_pdf         the "View More" advertisement PDF link
     apply_url          the "Apply Now" link, or None when the page shows none
   "Remaining Day(s)" is NOT stored: it changes every day and would create a new record version daily.

-> smc_city observations, an instant reading dated to the day of the fetch (Asia/Kolkata, from Raw.retrieved_at),
   because the page has no data date of its own:
     recruitment.open_ads  number of advertisements on the page (0 is a real value when the list is empty)
     recruitment.posts     sum of "No of post(s)" over those advertisements; not_reported if any is blank
   validate() checks that "Application End Date" minus "Remaining Day(s)" gives the fetch date (within a day),
   so a stale cached page is caught. The footer "Last Updated" is a CMS edit time and is not used.

Snapshot 2026-10-24: two advertisements. PRO No. 301 of 21/10/2026: waiting list for 9 cadres, 18 posts,
applications 09/11/2026 11:00 AM to 23/11/2026 11:00 PM. PRO No. 263 of 29/09/2026: honorary sports coaches
(contract) for the Navagam-Dindoli sports complex, South East Zone, 8 posts, closing 24/10/2026 11:00 PM.

Quirks and caveats:
- An advertisement can be listed before its application window opens (PRO 301 above), so "listed" is not the
  same as "accepting applications". Compare application_start/application_end with the date if that matters.
- "No of post(s)" can count waiting-list places, not only vacancies, as in PRO 301.
- The advertisement PDFs, the Recruitment Dashboard and its news, answer-key, result and selection-list pages
  (/Information/RecruitmentNews) are not fetched. State and national exams (GPSC, GSSSB, UPSC, SSC) are other
  sources.

Geography: SMC city (jobs in the corporation). Cadence: daily (the list changes when advertisements are added or
expire). Units: advertisements and posts. Licence: Surat Municipal Corporation web page; public information. No
explicit open licence.
"""
from __future__ import annotations

from datetime import date, timedelta

from ..model import Metric, Obs, Raw, Record, Result, Source, ValidationError
from ..parse import clean, html_text, links, num, parse_date, parse_dt
from ..surat import SMC

URL = 'https://www.suratmunicipal.gov.in/Information/Recruitment'

SOURCE = Source(
    id='smc_recruitment',
    name='SMC current recruitment advertisements',
    publisher='Surat Municipal Corporation (Recruitment cell)',
    url=URL,
    module='jobs',
    cadence='daily',
    interval_hours=24,
    record_types=('recruitment_ad',),
    geo_note='SMC city (posts in Surat Municipal Corporation)',
    licence_note='Surat Municipal Corporation web page; public information',
    notes=('Titles are Gujarati only. Counts are dated to the fetch day because the page has no data date. '
           '"Remaining Day(s)" is not stored. The advertisement PDFs and the results/answer-key pages are not '
           'fetched.'),
    metrics=(
        Metric('recruitment.open_ads', 'SMC recruitment advertisements listed', 'advertisements',
               'Number of advertisements on SMC\'s "Current Recruitment" page on the fetch day. Includes '
               'advertisements whose application window has not opened yet.'),
        Metric('recruitment.posts', 'Posts in listed SMC recruitment advertisements', 'posts',
               'Sum of "No of post(s)" over the advertisements listed on the fetch day (may include waiting-list '
               'places). not_reported if any listed advertisement gives no number.'),
    ),
)

GU_DIGITS = str.maketrans('૦૧૨૩૪૫૬૭૮૯', '0123456789')
AD = '<p class="gujartifont">'
LABEL = '<span class="emag-link pad-r5">'
FIELDS = {
    'no of post(s):': 'posts',
    'application start date:': 'application_start',
    'application end date:': 'application_end',
    'remaining day(s):': 'remaining',
}


def fetch(ctx):
    yield ctx.get(URL)


def _after(text: str, marker: str) -> str:
    """Text after the LAST `marker` up to the next tag, cleaned ('' if the marker is absent)."""
    i = text.rfind(marker)
    if i < 0:
        return ''
    rest = text[i + len(marker):]
    return clean(rest[:rest.find('<')] if '<' in rest else rest)


def _pro(title: str) -> tuple[int | None, str | None]:
    """'જાહેરાત ક્રમાંક :પી.આર.ઓ.નં.૩૦૧, તા.૨૧/૧૦/૨૦૨૬ થી ...' -> (301, '2026-10-21')."""
    t = title.translate(GU_DIGITS)
    no = day = None
    if 'નં.' in t:
        after = t.split('નં.', 1)[1].strip()
        digits = after[:len(after) - len(after.lstrip('0123456789'))]
        no = int(digits) if digits else None
    if 'તા.' in t:
        stamp = t.split('તા.', 1)[1].split()[0].strip(',')
        day = parse_date(stamp).isoformat()
    return no, day


def _ads(text: str) -> list[dict]:
    """Every advertisement on the page as a dict (including the volatile 'remaining' text)."""
    start = text.find('<section class="inner-page-contents">')
    end = text.find('<footer', start)
    if start < 0 or 'Current Recruitment' not in text[start:start + 2000]:
        raise ValueError('"Current Recruitment" page heading not found; page layout may have changed')
    pieces = text[start:end if end > 0 else len(text)].split(AD)
    org = _after(pieces[0], '<div class="panel-heading">')
    section = _after(pieces[0], 'text-2x text-bold">')
    ads = []
    for piece in pieces[1:]:
        ad = {'title': clean(html_text(piece[:piece.find('</p>')])), 'organisation': org or None,
              'section': section or None}
        for chunk in piece.split(LABEL)[1:]:
            label, _, rest = chunk.partition('</span>')
            key = FIELDS.get(clean(label).lower())
            if key is None:
                raise ValueError(f'unknown recruitment field {clean(label)!r}')
            ad[key] = clean(rest[:rest.find('<')] if '<' in rest else rest)
        found = {t: u for u, t in links(piece, URL)}
        ad['notice_pdf'] = found.get('View More')
        ad['apply_url'] = found.get('Apply Now')
        ads.append(ad)
        # a panel heading or section label at the end of this piece belongs to the next advertisement
        org = _after(piece, '<div class="panel-heading">') or org
        section = _after(piece, 'text-2x text-bold">') or section
    return ads


def parse(raw: Raw) -> Result:
    day = raw.retrieved_at[:10]
    res = Result(geos=[SMC], complete_record_types=('recruitment_ad',))
    total, missing = 0, False
    for ad in _ads(raw.text):
        no, ad_date = _pro(ad['title'])
        posts = num(ad.get('posts'))
        attrs = {
            'pro_no': no,
            'ad_date': ad_date,
            'title': ad['title'],
            'posts': None if posts is None else int(posts),
            'application_start': parse_dt(ad['application_start'], '%d/%m/%Y %I:%M %p'),
            'application_end': parse_dt(ad['application_end'], '%d/%m/%Y %I:%M %p'),
            'organisation': ad['organisation'],
            'section': ad['section'],
            'notice_pdf': ad['notice_pdf'],
            'apply_url': ad['apply_url'],
        }
        if no is not None and ad_date:
            key = f'pro-{no}-{ad_date}'
        elif ad['notice_pdf']:
            key = 'pdf-' + ad['notice_pdf'].rsplit('/', 1)[-1].rsplit('.', 1)[0]
        else:
            raise ValueError(f'advertisement without PRO number or PDF link: {ad["title"][:80]!r}')
        res.records.append(Record('recruitment_ad', key, attrs))
        if posts is None:
            missing = True
        else:
            total += int(posts)
    res.observations.append(Obs('recruitment.open_ads', 'smc_city', 'smc', day, day, value=float(len(res.records))))
    res.observations.append(Obs('recruitment.posts', 'smc_city', 'smc', day, day,
                                value=None if missing else float(total),
                                status='not_reported' if missing else 'reported'))
    return res


def _page_day(ad: dict) -> date:
    """The server's 'today': application end date minus 'Remaining Day(s)' ('30 day(s)' or 'Today')."""
    end = parse_date(ad['application_end'].split()[0])
    remaining = ad.get('remaining', '')
    return end if remaining.lower() == 'today' else end - timedelta(days=int(remaining.split()[0]))


def validate(result: Result, raw: Raw) -> None:
    ads = [r.attrs for r in result.records]
    if len(ads) > 60:
        raise ValidationError(f'{len(ads)} open advertisements is implausible for SMC; layout may have changed')
    for a in ads:
        if a['posts'] is not None and not 1 <= a['posts'] <= 5000:
            raise ValidationError(f'PRO {a["pro_no"]}: implausible number of posts {a["posts"]}')
        if a['application_end'] < a['application_start']:
            raise ValidationError(f'PRO {a["pro_no"]}: application ends before it starts')
        if a['ad_date'] and not '2015-01-01' <= a['ad_date'] <= a['application_end'][:10]:
            raise ValidationError(f'PRO {a["pro_no"]}: notice date {a["ad_date"]} is implausible')
    if raw is None or not raw.retrieved_at:
        return
    fetched = date.fromisoformat(raw.retrieved_at[:10])
    for ad in _ads(raw.text):
        remaining = ad.get('remaining', '').lower()
        if (remaining[:1].isdigit() or remaining == 'today') and abs((_page_day(ad) - fetched).days) > 1:
            raise ValidationError(f'page counts days from {_page_day(ad)}, not the fetch date {fetched}; '
                                  'stale cached page?')
