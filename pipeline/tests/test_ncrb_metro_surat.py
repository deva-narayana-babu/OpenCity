import io
import unittest
import zipfile

from tests import FIXTURES, raw_from_file
from opencity.model import ValidationError
from opencity.sources import ncrb_metro_surat

DIR = FIXTURES / 'ncrb_metro_surat'
FILES = {'1B.1': 'table_1b.1.xlsx', '1B.2': 'table_1b.2.xlsx', '1B.3': 'table_1b.3.xlsx',
         '3B.1': 'table_3b.1.xlsx', '4B.1': 'table_4b.1.xlsx', '6B.1': 'vol2-6b.1.xlsx'}


def _parse(table):
    raw = raw_from_file(DIR / FILES[table], meta={'table': table})
    return raw, ncrb_metro_surat.parse(raw)


def _values(res):
    return {(o.metric_id[len('ncrb.'):], o.period_start[:4], o.dims.get('law')): o.value for o in res.observations}


class TestNcrbMetroSurat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parsed = {t: _parse(t) for t in FILES}
        cls.v = {t: _values(res) for t, (_, res) in cls.parsed.items()}

    def test_counts_and_validation(self):
        n = {t: len(res.observations) for t, (_, res) in self.parsed.items()}
        self.assertEqual(n, {'1B.1': 8, '1B.2': 6, '1B.3': 6, '3B.1': 6, '4B.1': 4, '6B.1': 6})
        for raw, res in self.parsed.values():
            ncrb_metro_surat.validate(res, raw)

    def test_values_read_off_table_1b3(self):
        # 19 | Surat (Gujarat) | 55300 | 63142 | 63166 | 45.8 | 1377.7 | 97.7   (same in the NCRB Volume I PDF)
        v = self.v['1B.3']
        self.assertEqual([v[('cases_registered', y, 'all')] for y in ('2022', '2023', '2024')], [55300, 63142, 63166])
        self.assertEqual(v[('rate_population_lakh', '2011', None)], 45.8)
        self.assertEqual(v[('crime_rate_per_lakh', '2024', None)], 1377.7)
        self.assertEqual(v[('chargesheeting_rate_pct', '2024', None)], 97.7)

    def test_ipc_bns_split(self):
        # 1B.1: 2024 IPC Cases 5771 | 2024 BNS Cases 5462 | 2024 Total (IPC+BNS) 11233; rate 245, chargesheeting 87.7
        v = self.v['1B.1']
        self.assertEqual((v[('cases_registered', '2024', 'ipc')], v[('cases_registered', '2024', 'bns')],
                          v[('cases_registered', '2024', 'all')]), (5771, 5462, 11233))
        self.assertEqual(v[('chargesheeting_rate_pct', '2024', None)], 87.7)    # stored as 87.69999999999999

    def test_tables_add_up(self):
        # IPC/BNS (1B.1) + SLL (1B.2) = total cognizable (1B.3) in every year
        for y in ('2022', '2023', '2024'):
            self.assertEqual(self.v['1B.1'][('cases_registered', y, 'all')] + self.v['1B.2'][('cases_registered', y, 'all')],
                             self.v['1B.3'][('cases_registered', y, 'all')])

    def test_women_rate_uses_female_population(self):
        # 3B.1: 797 | 869 | 945 | 19.7 | 47.9 | 83
        v = self.v['3B.1']
        self.assertEqual((v[('cases_registered', '2024', 'all')], v[('rate_population_lakh', '2011', None)],
                          v[('crime_rate_per_lakh', '2024', None)]), (945, 19.7, 47.9))

    def test_tables_without_rate(self):
        # 4B.1 (children): 540 | 550 | 559 | 52.9, no population or rate column
        self.assertEqual(self.v['4B.1'], {('cases_registered', '2022', 'all'): 540, ('cases_registered', '2023', 'all'): 550,
                                          ('cases_registered', '2024', 'all'): 559,
                                          ('chargesheeting_rate_pct', '2024', None): 52.9})

    def test_volume2_layout(self):
        # 6B.1 (title in A2, header in row 3, floats): 33.0 | 14.0 | 11.0 (IPC) | 2.0 (BNS) | 13.0 | 61.5
        v = self.v['6B.1']
        self.assertEqual([v[('cases_registered', '2022', 'all')], v[('cases_registered', '2024', 'ipc')],
                          v[('cases_registered', '2024', 'bns')], v[('chargesheeting_rate_pct', '2024', None)]],
                         [33, 11, 2, 61.5])

    def test_geography_and_periods(self):
        res = self.parsed['1B.3'][1]
        self.assertEqual([(g.geo_level, g.geo_code, g.parent_level) for g in res.geos],
                         [('ncrb_metro_city', 'surat', 'surat_district')])
        o = res.observations[2]
        self.assertEqual((o.metric_id, o.geo_level, o.geo_code, o.period_start, o.period_end, o.dims),
                         ('ncrb.cases_registered', 'ncrb_metro_city', 'surat', '2024-01-01', '2024-12-31',
                          {'crime_group': 'all_cognizable', 'law': 'all'}))
        pop = [o for o in res.observations if o.metric_id == 'ncrb.rate_population_lakh'][0]
        self.assertEqual((pop.period_start, pop.period_end), ('2011-03-01', '2011-03-01'))

    def test_dash_is_not_reported(self):
        body = _rewrite(DIR / FILES['6B.1'], b'<c r="H22" s="6"><v>61.5</v></c>',
                        b'<c r="H22" s="6" t="inlineStr"><is><t>-</t></is></c>')
        raw = raw_from_file(DIR / FILES['6B.1'])
        raw.body = body
        res = ncrb_metro_surat.parse(raw)
        o = [o for o in res.observations if o.metric_id == 'ncrb.chargesheeting_rate_pct'][0]
        self.assertEqual((o.value, o.status), (None, 'not_reported'))
        ncrb_metro_surat.validate(res, raw)

    def test_wrong_table_is_rejected(self):
        with self.assertRaises(ValueError):
            ncrb_metro_surat.parse(raw_from_file(DIR / FILES['1B.3'], meta={'table': '1B.1'}))

    def test_rate_mismatch_fails_validation(self):
        raw, res = _parse('1B.3')
        for o in res.observations:
            if o.metric_id == 'ncrb.crime_rate_per_lakh':
                o.value = 2000.0
        with self.assertRaises(ValidationError):
            ncrb_metro_surat.validate(res, raw)


def _rewrite(path, old: bytes, new: bytes) -> bytes:
    """Copy of an .xlsx with one string replaced in its worksheet."""
    src = zipfile.ZipFile(path)
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w') as z:
        for name in src.namelist():
            data = src.read(name)
            if name == 'xl/worksheets/sheet1.xml':
                assert old in data
                data = data.replace(old, new)
            z.writestr(name, data)
    return out.getvalue()


if __name__ == '__main__':
    unittest.main()
