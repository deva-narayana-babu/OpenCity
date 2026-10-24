import copy
import unittest

from tests import FIXTURES, raw_from_file
from opencity.model import ValidationError
from opencity.sources import census2011_surat as census

DIR = FIXTURES / 'census2011_surat'


def _key(o):
    d = o.dims
    return (o.metric_id, o.geo_code, d['residence'], d.get('sex') or d.get('item'), d.get('category'),
            d.get('months_worked'))


class TestCensus2011Pca(unittest.TestCase):
    """pca-24.csv: the Gujarat state, Surat and Tapi rows of the mirror's pca/24.csv (fetched 2026-10-24)."""

    @classmethod
    def setUpClass(cls):
        cls.res = census.parse(raw_from_file(DIR / 'pca-24.csv', meta={'doc': 'pca'}))
        cls.by = {_key(o): o for o in cls.res.observations}

    def test_counts(self):
        # 6 rows (Surat and Gujarat x Total/Rural/Urban) x (area + households + 28 triples x 3 sexes); Tapi skipped
        self.assertEqual(len(self.res.observations), 6 * (2 + 28 * 3))
        self.assertNotIn('tapi', {o.geo_code for o in self.res.observations})
        census.validate(self.res, None)

    def test_values_read_off_the_file(self):
        # Surat Total row: 24,492,DISTRICT,Surat,Total,4549.00,1333200,6081322,3402224,2679098,736286,401315,334971,...
        self.assertEqual(self.by[('census.population', 'surat', 'total', 'persons', None, None)].value, 6081322)
        self.assertEqual(self.by[('census.population', 'surat', 'total', 'female', None, None)].value, 2679098)
        self.assertEqual(self.by[('census.population_0_6', 'surat', 'total', 'male', None, None)].value, 401315)
        self.assertEqual(self.by[('census.households', 'surat', 'total', None, None, None)].value, 1333200)
        self.assertEqual(self.by[('census.area_km2', 'surat', 'total', None, None, None)].value, 4549)
        self.assertAlmostEqual(self.by[('census.area_km2', 'surat', 'rural', None, None, None)].value, 4040.39)
        self.assertEqual(self.by[('census.population_st', 'surat', 'rural', 'persons', None, None)].value, 683413)
        self.assertEqual(self.by[('census.literates', 'surat', 'urban', 'persons', None, None)].value, 3730966)
        # main cultivators 101747, marginal agricultural labourers 51003, marginal other workers <3 months 10212
        self.assertEqual(self.by[('census.main_workers', 'surat', 'total', 'persons', 'cultivators', None)].value,
                         101747)
        self.assertEqual(self.by[('census.marginal_workers', 'surat', 'total', 'persons', 'agricultural_labourers',
                                  'under_6')].value, 51003)
        self.assertEqual(self.by[('census.marginal_workers', 'surat', 'total', 'persons', 'other', 'under_3')].value,
                         10212)
        self.assertEqual(self.by[('census.non_workers', 'surat', 'total', 'female', None, None)].value, 2268375)
        # Gujarat state Total: 60439692 persons
        self.assertEqual(self.by[('census.population', 'gujarat', 'total', 'persons', None, None)].value, 60439692)

    def test_geography_and_period(self):
        o = self.by[('census.population', 'surat', 'total', 'persons', None, None)]
        self.assertEqual((o.geo_level, o.period_start, o.period_end, o.status), ('surat_district', '2011-03-01',
                                                                                 '2011-03-01', 'reported'))

    def test_validate_catches_a_changed_value(self):
        bad = copy.deepcopy(self.res)
        for o in bad.observations:
            if (o.metric_id, o.geo_code) == ('census.literates', 'surat') and \
                    o.dims == {'residence': 'total', 'sex': 'male'}:
                o.value += 1
        with self.assertRaises(ValidationError):
            census.validate(bad, None)


class TestCensus2011Houselisting(unittest.TestCase):
    """hlpca-gujarat.csv: the Gujarat, Surat (district + sub-districts) and Tapi district rows of the mirror's
    houselisting/csv/Gujarat.csv (fetched 2026-10-24)."""

    @classmethod
    def setUpClass(cls):
        cls.res = census.parse(raw_from_file(DIR / 'hlpca-gujarat.csv', meta={'doc': 'hlpca'}))
        cls.by = {_key(o): o for o in cls.res.observations}

    def test_counts(self):
        # 33 rows (Gujarat 3, Surat district 3, sub-districts 27) x 133 items; Tapi skipped
        self.assertEqual(len(self.res.observations), 33 * 133)
        self.assertEqual(len({o.geo_code for o in self.res.observations if o.geo_level == 'surat_taluka'}), 10)
        census.validate(self.res, None)

    def test_values_read_off_the_file(self):
        # District - Surat, Total: good 77.3, electricity 96.4, latrine within premises 84.9, LPG/PNG 62.7,
        # tap water from a treated source 64, wall of burnt brick 82.5, banking 52.9, car/jeep/van 8.2
        def surat(metric, item, residence='total'):
            return self.by[(metric, 'surat', residence, item, None, None)].value
        self.assertEqual(surat('census.hh_condition_pct', 'good'), 77.3)
        self.assertEqual(surat('census.hh_lighting_pct', 'electricity'), 96.4)
        self.assertEqual(surat('census.hh_latrine_pct', 'within_premises'), 84.9)
        self.assertEqual(surat('census.hh_latrine_pct', 'open'), 11.5)
        self.assertEqual(surat('census.hh_cooking_fuel_pct', 'lpg_png'), 62.7)
        self.assertEqual(surat('census.hh_water_source_pct', 'tap_treated'), 64)
        self.assertEqual(surat('census.hh_wall_pct', 'burnt_brick'), 82.5)
        self.assertEqual(surat('census.hh_banking_pct', 'availing_banking'), 52.9)
        self.assertEqual(surat('census.hh_assets_pct', 'car_jeep_van'), 8.2)
        self.assertEqual(surat('census.hh_structure_pct', 'unclassifiable'), 0.1)
        self.assertEqual(surat('census.hh_latrine_pct', 'within_premises', 'rural'), 49.9)
        # Sub-Dist - Umarpada, Total: LPG/PNG 2.1; Sub-Dist - Surat City, Urban: latrine within premises 94.7
        self.assertEqual(self.by[('census.hh_cooking_fuel_pct', 'umarpada', 'total', 'lpg_png', None, None)].value, 2.1)
        self.assertEqual(self.by[('census.hh_latrine_pct', 'surat_city', 'urban', 'within_premises', None, None)].value,
                         94.7)
        # Gujarat state, Total: good 67.3
        self.assertEqual(self.by[('census.hh_condition_pct', 'gujarat', 'total', 'good', None, None)].value, 67.3)

    def test_missing_residence_rows_are_not_invented(self):
        self.assertNotIn(('census.hh_condition_pct', 'surat_city', 'rural', 'good', None, None), self.by)
        self.assertNotIn(('census.hh_condition_pct', 'umarpada', 'urban', 'good', None, None), self.by)

    def test_geography_and_period(self):
        o = self.by[('census.hh_condition_pct', 'chorasi', 'total', 'good', None, None)]
        self.assertEqual((o.geo_level, o.period_start, o.period_end), ('surat_taluka', '2010-04-01', '2010-09-30'))
        geo = next(g for g in self.res.geos if g.geo_code == 'chorasi')
        self.assertEqual((geo.name, geo.parent_level, geo.parent_code),
                         ('Chorasi (Choryasi)', 'surat_district', 'surat'))

    def test_shifted_columns_fail(self):
        lines = (DIR / 'hlpca-gujarat.csv').read_text().splitlines()
        cells = lines[0].split(',')
        shifted = ','.join(cells[:10] + cells[11:] + ['0'])     # drop c11: every column moves left by one
        raw = raw_from_file(DIR / 'hlpca-gujarat.csv')
        raw.body = (shifted + '\n').encode()
        with self.assertRaises(ValueError):
            census.parse(raw)


if __name__ == '__main__':
    unittest.main()
