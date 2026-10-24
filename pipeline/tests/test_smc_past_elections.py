import unittest

from tests import FIXTURES, raw_from_file
from opencity.model import ValidationError
from opencity.sources import smc_past_elections as src

PAGE = FIXTURES / 'smc_past_elections/past-elections-2026-10-24.html'


class TestSmcPastElections(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = raw_from_file(PAGE, retrieved_at='2026-10-24T12:00:00+05:30')
        cls.res = src.parse(cls.raw)
        cls.by = {(o.metric_id, o.period_start, o.dims.get('category')): o for o in cls.res.observations}
        cls.rec = {r.record_key: r.attrs for r in cls.res.records}

    def test_counts(self):
        self.assertEqual(len(self.res.records), 11)
        # 11 elections x (3 totals + 4 reserved) + 6 elections x 3 "(n Female)" notes
        self.assertEqual(len(self.res.observations), 11 * 7 + 6 * 3)
        src.validate(self.res, self.raw)

    def test_values_read_off_the_page(self):
        # row 11: 2020 | 21.02.2021 | 30 | 32,88,173 | 120 | 3 (2 Female) | 4 (2 Female) | 12 (12 Female) | 60
        d = '2021-02-21'
        self.assertEqual(self.by[('election.past_wards', d, None)].value, 30)
        self.assertEqual(self.by[('election.past_voters', d, None)].value, 3288173)
        self.assertEqual(self.by[('election.past_seats', d, None)].value, 120)
        self.assertEqual(self.by[('election.past_reserved_seats', d, 'sc')].value, 3)
        self.assertEqual(self.by[('election.past_reserved_seats_women', d, 'sc')].value, 2)
        self.assertEqual(self.by[('election.past_reserved_seats', d, 'obc')].value, 12)
        self.assertEqual(self.by[('election.past_reserved_seats_women', d, 'obc')].value, 12)
        self.assertEqual(self.by[('election.past_reserved_seats', d, 'women')].value, 60)
        # row 1: 1969 | 08.06.1969 | 14 | 1,63,276 | 51 | 2 | 4 | --- | ---
        d = '1969-06-08'
        self.assertEqual(self.by[('election.past_voters', d, None)].value, 163276)
        self.assertEqual(self.by[('election.past_reserved_seats', d, 'st')].value, 4)
        self.assertNotIn(('election.past_reserved_seats_women', d, 'st'), self.by)

    def test_dashes_are_not_reported(self):
        obc = self.by[('election.past_reserved_seats', '1969-06-08', 'obc')]
        self.assertEqual((obc.value, obc.status), (None, 'not_reported'))
        # 2008: SC '-', women '04'
        sc = self.by[('election.past_reserved_seats', '2008-02-17', 'sc')]
        self.assertEqual((sc.value, sc.status), (None, 'not_reported'))
        self.assertEqual(self.by[('election.past_reserved_seats', '2008-02-17', 'women')].value, 4)

    def test_records(self):
        self.assertEqual(self.rec['2020'], {'election_year': '2020', 'poll_date': '2021-02-21',
                                            'first_board_meeting': '2020-03-12'})   # as printed
        self.assertEqual(self.rec['2010']['first_board_meeting'], '2010-12-15')
        self.assertNotIn('first_board_meeting', self.rec['1995'])
        self.assertEqual(self.res.complete_record_types, ('municipal_election',))

    def test_geography_and_periods(self):
        o = self.by[('election.past_seats', '2015-11-22', None)]
        self.assertEqual((o.geo_level, o.geo_code, o.period_end, o.value), ('smc_city', 'smc', '2015-11-22', 116))

    def test_validate_rejects_too_few_women_seats(self):
        bad = src.parse(self.raw)
        for o in bad.observations:
            if o.metric_id == 'election.past_reserved_seats' and o.dims['category'] == 'women' \
                    and o.period_start == '2015-11-22':
                o.value = 10
        with self.assertRaises(ValidationError):
            src.validate(bad, self.raw)


if __name__ == '__main__':
    unittest.main()
