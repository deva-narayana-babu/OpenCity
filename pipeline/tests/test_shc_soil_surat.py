import json
import unittest

from tests import FIXTURES, raw_from_file
from opencity.model import ValidationError
from opencity.sources import shc_soil_surat as src

DIR = FIXTURES / 'shc_soil_surat'
WHEN = '2026-10-24T12:00:00+05:30'


def load(cycle):
    return raw_from_file(DIR / f'nutrient-dashboard-surat-{cycle}.json', url=src.API, meta={'cycle': cycle},
                         retrieved_at=WHEN)


def key(o):
    return (o.metric_id, o.geo_level, o.geo_code, o.dims.get('scheme'), o.dims.get('parameter'), o.dims['class'])


class TestShcSoilSurat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = load('2025-26')
        cls.res = src.parse(cls.raw)
        cls.by = {key(o): o for o in cls.res.observations}
        cls.old_raw = load('2023-24')
        cls.old = src.parse(cls.old_raw)
        cls.old_by = {key(o): o for o in cls.old.observations}

    def test_counts(self):
        per_row = 4 * 3 + 3 + 2 + 6 * 2      # N/P/K/OC x 3 classes, pH 3, EC 2, six micronutrients x 2
        # 2025-26: 15 block rows (10 under shc_rkvy, 5 under nmnf) plus one district total per scheme
        self.assertEqual(len(self.res.observations), 15 * per_row + 2 * per_row)
        # 2023-24: 9 block rows, all shc_rkvy
        self.assertEqual(len(self.old.observations), 9 * per_row + per_row)
        src.validate(self.res, self.raw)
        src.validate(self.old, self.old_raw)

    def test_values_read_off_the_response(self):
        t = 'soil.shc_npk_oc_samples', 'surat_taluka', 'bardoli', 'shc_rkvy'
        # BARDOLI, scheme 660f941a... (Soil Health Card RKVY), 2025-26: n {High 0, Low 3093, Medium 0}
        o = self.by[(*t, 'n', 'low')]
        self.assertEqual((o.value, o.period_start, o.period_end), (3093, '2025-04-01', '2026-03-31'))
        self.assertEqual(o.publisher_as_of, '2026-10-23T23:24')     # updatedAt 2026-10-23T17:54:00.877Z in IST
        self.assertEqual(self.by[(*t, 'p', 'high')].value, 2290)
        self.assertEqual(self.by[(*t, 'n', 'high')].value, 0)
        self.assertEqual(self.by[('soil.shc_ph_samples', 'surat_taluka', 'bardoli', 'shc_rkvy', None, 'alkaline')].value,
                         299)
        self.assertEqual(self.by[('soil.shc_micronutrient_samples', 'surat_taluka', 'bardoli', 'shc_rkvy', 'b',
                                  'deficient')].value, 2646)
        self.assertEqual(self.by[('soil.shc_ec_samples', 'surat_taluka', 'bardoli', 'shc_rkvy', None,
                                  'non_saline')].value, 2449)
        # Suratcity block (code 4242) -> surat_city: pH Neutral 119, Fe Deficient 118
        self.assertEqual(self.by[('soil.shc_ph_samples', 'surat_taluka', 'surat_city', 'shc_rkvy', None,
                                  'neutral')].value, 119)
        self.assertEqual(self.by[('soil.shc_micronutrient_samples', 'surat_taluka', 'surat_city', 'shc_rkvy', 'fe',
                                  'deficient')].value, 118)
        # NMNF scheme (6847f8ff...), KAMREJ: n Low 62
        self.assertEqual(self.by[('soil.shc_npk_oc_samples', 'surat_taluka', 'kamrej', 'nmnf', 'n', 'low')].value, 62)
        # 2023-24: OLPAD OC High 426; PALSANA Cu Sufficient 427 + Deficient 6 = 433 (434 for the others)
        self.assertEqual(self.old_by[('soil.shc_npk_oc_samples', 'surat_taluka', 'olpad', 'shc_rkvy', 'oc',
                                      'high')].value, 426)
        cu = self.old_by[('soil.shc_micronutrient_samples', 'surat_taluka', 'palsana', 'shc_rkvy', 'cu', 'sufficient')]
        self.assertEqual((cu.value, cu.period_start, cu.publisher_as_of), (427, '2023-04-01', None))

    def test_district_is_the_sum_of_the_blocks(self):
        d = 'surat_district', 'surat'
        self.assertEqual(self.by[('soil.shc_npk_oc_samples', *d, 'shc_rkvy', 'n', 'low')].value, 20661)
        self.assertEqual(self.by[('soil.shc_ph_samples', *d, 'shc_rkvy', None, 'neutral')].value, 24484)
        self.assertEqual(self.by[('soil.shc_micronutrient_samples', *d, 'shc_rkvy', 'zn', 'deficient')].value, 13773)
        self.assertEqual(self.by[('soil.shc_npk_oc_samples', *d, 'nmnf', 'n', 'low')].value, 162)

    def test_district_not_reported_when_a_block_lacks_a_class(self):
        doc = json.loads(self.raw.body)
        rows = doc['data']['getNutrientDashboardForPortal']
        bardoli = next(r for r in rows if r['block']['name'] == 'BARDOLI' and r['scheme'] == '660f941a5c8405ca8375c7c6')
        del bardoli['results']['n']['Low']          # one block row without "Low" for N
        bardoli['results']['B'] = None              # and without boron at all
        raw = load('2025-26')
        raw.body = json.dumps(doc).encode()
        by = {key(o): o for o in src.parse(raw).observations}
        d = 'surat_district', 'surat', 'shc_rkvy'
        for k in (('soil.shc_npk_oc_samples', *d, 'n', 'low'), ('soil.shc_micronutrient_samples', *d, 'b', 'deficient')):
            self.assertEqual((by[k].value, by[k].status), (None, 'not_reported'))
        self.assertEqual(by[('soil.shc_npk_oc_samples', *d, 'n', 'medium')].status, 'reported')

    def test_geos(self):
        geos = {g.geo_code: g for g in self.res.geos}
        self.assertEqual(sorted(geos), ['bardoli', 'chorasi', 'kamrej', 'mahuva', 'mandvi', 'mangrol', 'olpad',
                                        'palsana', 'surat_city', 'umarpada'])
        self.assertEqual((geos['chorasi'].name, geos['chorasi'].parent_code), ('Chorasi (Choryasi)', 'surat'))

    def test_every_published_scheme_is_known(self):
        schemes = json.loads((DIR / 'schemes-2026-10-24.json').read_bytes())['data']['getSchemes']
        self.assertEqual({s['id'] for s in schemes}, set(src.SCHEMES))
        self.assertEqual(len(set(src.SCHEMES.values())), len(src.SCHEMES))

    def test_validate_catches_a_misread_class(self):
        bad = src.parse(self.raw)
        for o in bad.observations:
            if key(o) == ('soil.shc_npk_oc_samples', 'surat_taluka', 'mandvi', 'shc_rkvy', 'k', 'high'):
                o.value += 500
        with self.assertRaises(ValidationError):
            src.validate(bad, self.raw)

    def test_empty_response(self):
        body = b'{"data":{"getNutrientDashboardForPortal":[]}}'
        raw = load('2023-24')
        raw.body = body
        with self.assertRaises(ValidationError):           # a finished cycle must have rows
            src.validate(src.parse(raw), raw)
        raw.meta = {'cycle': '2026-27'}                    # the current cycle may still be empty
        src.validate(src.parse(raw), raw)


if __name__ == '__main__':
    unittest.main()
