"""SMC past municipal elections: poll date, wards, voters, seats and reserved seats for every election since 1969.

Publisher: Surat Municipal Corporation, Election & Census Department.

Endpoint: one plain GET, no parameters, no login or captcha (the SMC robots.txt URL serves a 404 page, so nothing
is disallowed):

    https://www.suratmunicipal.gov.in/Departments/ElectionCensus/ElectionCensusPastMunicipalElections

Response layout (ASP.NET HTML). Under the heading "Details of Elections held from 01.10.1966 (Municipality
converted to Municipal Corporation)" there is one table, a header row and one row per election (11 rows on
2026-10-24):

    Sr. No. | Election Year | Election Date | No. of Election Wards | Total Voters | Total no. of Seats |
    No. of Seats Reserved for SC | No. of Seats Reserved for ST | No. of Seats Reserved for OBC |
    No. of Seats Reserved for Female
    1.  | 1969 | 08.06.1969 | 14 | 1,63,276  | 51  | 2            | 4            | ---           | ---
    11. | 2020 | 21.02.2021 | 30 | 32,88,173 | 120 | 3 (2 Female) | 4 (2 Female) | 12 (12 Female) | 60

A "Note:" block follows the table. Its lines "After the 2010 elections, the first meeting of the General Board was
held on 15.12.2010." are read; the other two lines (the voting age was 21 until 1975 and 18 from 1978) are not.

Observations, all at smc_city/smc, each an instant period on the poll date ("Election Date"):
    election.past_wards                number of election wards ("No. of Election Wards")
    election.past_voters               voters on the roll for that election ("Total Voters")
    election.past_seats                council seats filled at that election ("Total no. of Seats")
    election.past_reserved_seats       seats reserved per dims.category: sc, st, obc (the number before the
                                       bracket) and women ("No. of Seats Reserved for Female", all women's seats
                                       including those inside the SC/ST/OBC quotas)
    election.past_reserved_seats_women for dims.category sc, st, obc: how many of that category's seats were also
                                       reserved for women, the "(n Female)" part of the cell. Emitted only where
                                       the page prints the bracket (from 1995); a plain "2" does not say
                                       anything about women, so nothing is emitted for it.
A "---" or "-" cell (OBC and women before 1995, SC in 2008) is stored as not_reported with no value. Women's and
OBC reservation in municipal bodies came with the 74th Constitutional Amendment (1992), so for the early elections
"---" most likely means "no such reservation", but the page does not say so and 0 is not stored.

Records: 'municipal_election', one per row, keyed by the "Election Year" label (e.g. '2020'); the page is the
complete list, so a row that disappears gets closed. Attributes:
    election_year        the label as printed ('2020'); SMC names an election after the year it was due
    poll_date            ISO date of the poll ('2021-02-21')
    first_board_meeting  ISO date of the first General Board meeting after it, only where the Note gives one
                         (2010, 2015 and 2020 elections), as printed

Units: wards, voters and seats are counts. Geography: the SMC area as it was at each election; the city limits
grew in 2006 and again in 2020, so the rows are not comparable in area. Cadence: one new row per election (every
five years); the page was last edited on 03-07-2023 (footer "Last Updated", not used as a data date), so the
April 2026 general election is NOT listed yet. Checked monthly.

Quirks, kept as published:
- The "2020" election was polled on 21.02.2021 (postponed during COVID-19); the year label and the date differ.
- 2008 (17.02.2008) has only 4 wards, 5,34,910 voters and 12 seats. It is not a full general election; it looks
  like the election for the area added to SMC in 2006 (34 + 4 = 38 wards in 2010), but the page does not say so.
- 2010 voters are printed as a round 24,20,000.
- For 2020 the page counts 3 SC and 4 ST seats, while SMC's ward-wise seat table (loaded by smc_council as
  election.seats) counts 2 SC and 5 ST. Both are stored as published.
- For 2020 the Note says the first General Board meeting was on 12.03.2020, before the 21.02.2021 poll; it is
  most likely 12.03.2021, but it is stored as printed.
- No turnout, votes polled or party results are published on this page, so none are stored.

Licence: Surat Municipal Corporation web page ("Copyright 2026@SMC, All rights reserved"); public information about
municipal elections, reproduced as facts with attribution.
"""
from __future__ import annotations

from datetime import date

from ..model import Metric, Obs, Raw, Record, Result, Source, ValidationError
from ..parse import html_tables, html_text, num, parse_date
from ..surat import SMC

URL = 'https://www.suratmunicipal.gov.in/Departments/ElectionCensus/ElectionCensusPastMunicipalElections'

SOURCE = Source(
    id='smc_past_elections',
    name='SMC past municipal elections (1969-2021)',
    publisher='Surat Municipal Corporation, Election & Census Department',
    url=URL,
    module='council',
    cadence='static',
    interval_hours=24 * 30,         # one new row per election; a monthly check is enough
    geo_note='SMC city: the corporation area as it was at each election (limits grew in 2006 and 2020)',
    licence_note='Surat Municipal Corporation web page; public information',
    notes=('Eleven elections, 1969 to the "2020" election polled on 21.02.2021; the April 2026 election is not '
           'listed yet. "---" cells are stored as not_reported. No turnout or party results are published. The '
           '2020 SC/ST counts (3/4) differ from the ward-wise seat table (2/5); both are stored as published.'),
    metrics=(
        Metric('election.past_wards', 'Election wards (past SMC elections)', 'wards',
               'Number of election wards at the SMC election polled on the period date ("No. of Election Wards").'),
        Metric('election.past_voters', 'Voters (past SMC elections)', 'voters',
               'Total voters on the electoral roll for the SMC election polled on the period date ("Total Voters").'),
        Metric('election.past_seats', 'Council seats (past SMC elections)', 'seats',
               'Total council seats filled at the SMC election polled on the period date ("Total no. of Seats").'),
        Metric('election.past_reserved_seats', 'Reserved seats (past SMC elections)', 'seats',
               'Seats reserved at the SMC election polled on the period date, by dims.category: sc, st, obc (the '
               'number before the bracket) or women (all seats reserved for women, including those within the '
               'SC/ST/OBC quotas). "---" or "-" on the page is stored as not_reported.'),
        Metric('election.past_reserved_seats_women', 'Reserved seats also reserved for women (past SMC elections)',
               'seats',
               'Of the seats reserved for dims.category (sc, st, obc), how many were also reserved for women: the '
               '"(n Female)" note in the cell. Only where the page prints that note (1995 onwards, except 2008).'),
    ),
    record_types=('municipal_election',),
)

# header text (lower case) -> column name; a header takes the first needle it contains
COLUMNS = [
    ('election year', 'year'),
    ('election date', 'date'),
    ('wards', 'wards'),
    ('voters', 'voters'),
    ('total no. of seats', 'seats'),
    ('female', 'women'),
    ('for sc', 'sc'),
    ('for st', 'st'),
    ('for obc', 'obc'),
]
BOARD_NOTE = 'first meeting of the General Board was held on'


def fetch(ctx):
    yield ctx.get(URL)


def _count(cell: str) -> float | None:
    """'1,63,276' -> 163276.0; '---' or '-' -> None."""
    if not cell.strip(' -'):
        return None
    return num(cell)


def _reserved(cell: str) -> tuple[float | None, float | None]:
    """'4 (1 Female)' -> (4.0, 1.0); '2' -> (2.0, None); '---' -> (None, None)."""
    main, bracket, rest = cell.partition('(')
    women = None
    if bracket:
        words = rest.replace(')', ' ').split()
        if len(words) != 2 or words[1].lower() not in ('female', 'women'):
            raise ValueError(f'unexpected reserved-seat cell {cell!r}')
        women = num(words[0])
    return _count(main), women


def _board_meetings(text: str) -> dict[str, str]:
    """Note lines 'After the 2010 elections, the first meeting of the General Board was held on 15.12.2010.'
    -> {'2010': '2010-12-15'}."""
    out = {}
    for line in text.splitlines():
        if line.startswith('After the ') and BOARD_NOTE in line:
            year = line[len('After the '):].split()[0]
            day = line.split(BOARD_NOTE)[1].strip(' .')
            out[year] = parse_date(day).isoformat()
    return out


def parse(raw: Raw) -> Result:
    table = next((t for t in html_tables(raw.body) if t.find_row('election year', 'election date') == 0), None)
    if table is None:
        raise ValueError('past-elections table not found; page layout may have changed')
    col = {}
    for j, h in enumerate(table.rows[0]):
        for needle, name in COLUMNS:
            if needle in h.lower() and name not in col:
                col[name] = j
                break
    if len(col) != len(COLUMNS):
        raise ValueError(f'unexpected header {table.rows[0]!r}')

    meetings = _board_meetings(html_text(raw.text))
    res = Result(geos=[SMC], complete_record_types=('municipal_election',))

    def emit(metric, day, value, dims=None):
        res.observations.append(Obs(metric, 'smc_city', 'smc', day, day, value=value,
                                    status='reported' if value is not None else 'not_reported', dims=dims or {}))

    for row in table.rows[1:]:
        year = row[col['year']].strip()
        if not year:
            continue
        day = parse_date(row[col['date']]).isoformat()
        emit('election.past_wards', day, _count(row[col['wards']]))
        emit('election.past_voters', day, _count(row[col['voters']]))
        emit('election.past_seats', day, _count(row[col['seats']]))
        emit('election.past_reserved_seats', day, _count(row[col['women']]), {'category': 'women'})
        for category in ('sc', 'st', 'obc'):
            seats, women = _reserved(row[col[category]])
            emit('election.past_reserved_seats', day, seats, {'category': category})
            if women is not None:
                emit('election.past_reserved_seats_women', day, women, {'category': category})
        attrs = {'election_year': year, 'poll_date': day}
        if year in meetings:
            attrs['first_board_meeting'] = meetings.pop(year)
        res.records.append(Record('municipal_election', year, attrs))
    if meetings:
        raise ValueError(f'board-meeting note for elections not in the table: {sorted(meetings)}')
    return res


def validate(result: Result, raw: Raw) -> None:
    recs = result.records
    if len(recs) < 11:
        raise ValidationError(f'only {len(recs)} elections parsed (11 listed in 2026); page layout may have changed')
    latest = raw.retrieved_at[:10] if raw is not None and raw.retrieved_at else '2100-01-01'
    for r in recs:
        poll = r.attrs['poll_date']
        if not '1966-10-01' <= poll <= latest:
            raise ValidationError(f'election {r.record_key}: poll date {poll} before SMC existed or after the fetch')
        if int(poll[:4]) - int(r.attrs['election_year']) not in (0, 1):
            raise ValidationError(f'election {r.record_key} polled on {poll}: year label and date disagree')
        meeting = r.attrs.get('first_board_meeting')
        if meeting and abs((date.fromisoformat(meeting) - date.fromisoformat(poll)).days) > 400:
            raise ValidationError(f'election {r.record_key}: first board meeting {meeting} is far from the poll')

    val = {(o.metric_id, o.period_start, o.dims.get('category')): o.value for o in result.observations}
    for day in sorted({o.period_start for o in result.observations}):
        wards = val[('election.past_wards', day, None)]
        voters = val[('election.past_voters', day, None)]
        seats = val[('election.past_seats', day, None)]
        if wards is None or seats is None or voters is None:
            raise ValidationError(f'{day}: wards, voters or seats missing')
        if not 1 <= wards <= 100 or not wards <= seats <= 5 * wards:
            raise ValidationError(f'{day}: implausible {wards} wards for {seats} seats')
        if not 50_000 <= voters <= 10_000_000:
            raise ValidationError(f'{day}: implausible {voters} voters')
        reserved = {c: val[('election.past_reserved_seats', day, c)] for c in ('sc', 'st', 'obc', 'women')}
        if sum(v or 0 for c, v in reserved.items() if c != 'women') > seats or (reserved['women'] or 0) > seats:
            raise ValidationError(f'{day}: more reserved seats {reserved} than seats {seats}')
        for c in ('sc', 'st', 'obc'):
            women = val.get(('election.past_reserved_seats_women', day, c))
            if women is not None and women > (reserved[c] or 0):
                raise ValidationError(f'{day}: {women} {c} women seats out of {reserved[c]} {c} seats')
        # the 74th Amendment (1992) reserves at least one third of the seats for women
        if day >= '1993-06-01' and reserved['women'] is not None and reserved['women'] * 3 < seats:
            raise ValidationError(f'{day}: only {reserved["women"]} of {seats} seats reserved for women')
