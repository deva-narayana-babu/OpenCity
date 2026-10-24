import unittest

from tests import FIXTURES, raw_from_file
from opencity.sources import smc_vital_stats as vital

DIR = FIXTURES / 'smc_vital_stats'


class TestAnnualTables(unittest.TestCase):
    """birth-death-registration.html: the content block of /Departments/BirthDeathRegistration (2026-10-24)."""

    @classmethod
    def setUpClass(cls):
        cls.res = vital.parse(raw_from_file(DIR / 'birth-death-registration.html', meta={'doc': 'annual'}))
        cls.by = {(o.metric_id, o.period_start[:4]): o for o in cls.res.observations}

    def test_counts(self):
        # rows x years: 2018-21: 12 x 4, 2013-17: 13 x 5 (with density), 2009-12: 13 x 4,
        # 2005-08 and 2001-04: 12 x 4 each (density but no mid-year population)
        self.assertEqual(len(self.res.observations), 48 + 65 + 52 + 48 + 48)
        years = sorted(y for m, y in self.by if m == 'vital.registered_births')
        self.assertEqual((len(years), years[0], years[-1]), (21, '2001', '2021'))
        vital.validate(self.res, raw_from_file(DIR / 'birth-death-registration.html',
                                               retrieved_at='2026-10-24T02:35:00+05:30'))

    def test_values_read_off_the_page(self):
        v = {k: o.value for k, o in self.by.items()}
        self.assertEqual(v[('vital.mid_year_population', '2021')], 6936534)
        self.assertEqual(v[('vital.registered_births', '2021')], 68515)
        self.assertEqual(v[('vital.registered_deaths', '2021')], 36690)
        self.assertEqual(v[('vital.infant_deaths', '2021')], 1492)
        self.assertEqual(v[('vital.crude_death_rate', '2021')], 6.07)       # printed; counts give 5.29
        self.assertEqual(v[('vital.infant_mortality_rate', '2021')], 21.78)
        self.assertEqual(v[('vital.city_area_km2', '2011')], 326.515)
        self.assertEqual(v[('vital.population_density', '2017')], 18038)
        self.assertEqual(v[('vital.registered_births', '2005')], 55907)     # printed as "55,907"
        self.assertEqual(v[('vital.city_area_km2', '2001')], 112.28)        # table captioned "2005 - 2008"
        self.assertEqual(v[('vital.still_birth_ratio', '2001')], 8.96)

    def test_maternal_mortality_units_are_split(self):
        self.assertEqual(self.by[('vital.maternal_mortality_per_1000', '2017')].value, 0.46)
        self.assertEqual(self.by[('vital.maternal_mortality_per_100k', '2018')].value, 24.91)
        self.assertNotIn(('vital.maternal_mortality_per_100k', '2017'), self.by)
        self.assertNotIn(('vital.maternal_mortality_per_1000', '2018'), self.by)

    def test_rows_not_printed_are_not_invented(self):
        self.assertNotIn(('vital.mid_year_population', '2008'), self.by)
        self.assertNotIn(('vital.population_density', '2018'), self.by)

    def test_geography_and_period(self):
        o = self.by[('vital.registered_births', '2021')]
        self.assertEqual((o.geo_level, o.geo_code, o.period_start, o.period_end), ('smc_city', 'smc', '2021-01-01',
                                                                                   '2021-12-31'))


class TestMonthlyBirths(unittest.TestCase):
    """births-2022.json / births-1995.json: POST /Departments/GetBirthDetails Year=2022 / 1995 (2026-10-24)."""

    def _parse(self, year):
        res = vital.parse(raw_from_file(DIR / f'births-{year}.json', meta={'doc': 'births', 'year': year}))
        vital.validate(res, None)
        return res, {(o.period_start, o.dims['sex']): o for o in res.observations}

    def test_2022(self):
        res, by = self._parse(2022)
        self.assertEqual(len(res.observations), 36)
        # January - 2022: 3111 male, 2753 female, 5864 total
        self.assertEqual([by[('2022-01-01', s)].value for s in ('male', 'female', 'total')], [3111, 2753, 5864])
        self.assertEqual(by[('2022-10-01', 'total')].value, 7164)
        self.assertEqual(by[('2022-01-01', 'male')].period_end, '2022-01-31')
        # November and December 2022 are "-": not reported, no value
        nov = by[('2022-11-01', 'female')]
        self.assertEqual((nov.status, nov.value), ('not_reported', None))

    def test_1995_total_can_exceed_male_plus_female(self):
        _, by = self._parse(1995)
        # March - 1995: 1703 male, 1374 female, 3078 total (one more than male + female), kept as printed
        self.assertEqual([by[('1995-03-01', s)].value for s in ('male', 'female', 'total')], [1703, 1374, 3078])

    def test_wrong_year_is_rejected(self):
        with self.assertRaises(ValueError):
            vital.parse(raw_from_file(DIR / 'births-2022.json', meta={'doc': 'births', 'year': 2021}))


class TestYearList(unittest.TestCase):
    def test_years(self):
        body = (DIR / 'birth-details.html').read_text()
        years = vital.year_list(body)
        self.assertEqual((years[0], years[-1], len(years)), (1776, 2022, 137))
        res = vital.parse(raw_from_file(DIR / 'birth-details.html', meta={'doc': 'year_list'}))
        self.assertEqual(res.observations, [])
        vital.validate(res, None)


if __name__ == '__main__':
    unittest.main()
