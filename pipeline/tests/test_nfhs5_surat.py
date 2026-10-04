import tempfile
import unittest
from pathlib import Path

from tests import REFERENCE, raw_from_file
from opencity import db, runner
from opencity.fetcher import Response
from opencity.model import ValidationError
from opencity.registry import discover
from opencity.sources import nfhs5_surat as m

CSV = REFERENCE / 'health-environment/nfhs5-mirror-district-indicators-2019-21.csv'
N5, N4 = '2019-01-01', '2015-01-01'


def _parse(body: bytes):
    raw = raw_from_file(CSV)
    raw.body = body
    res = m.parse(raw)
    m.validate(res, raw)
    return res


class TestNfhs5Surat(unittest.TestCase):
    """reference/health-environment/nfhs5-mirror-district-indicators-2019-21.csv, rows State=Gujarat, District=Surat."""

    @classmethod
    def setUpClass(cls):
        cls.res = _parse(CSV.read_bytes())
        cls.by = {(o.dims['factsheet_no'], o.period_start): o for o in cls.res.observations}

    def o(self, no, start=N5):
        return self.by[(str(no), start)]

    def test_counts_and_geography(self):
        obs = self.res.observations
        self.assertEqual(len(obs), 208)                               # 104 indicators x (NFHS-5, NFHS-4)
        self.assertEqual(sum(o.status == 'reported' for o in obs), 166)
        self.assertEqual(sum(o.status == 'withheld' for o in obs), 16)
        self.assertEqual(sum(o.status == 'not_reported' for o in obs), 26)
        self.assertEqual({(o.geo_level, o.geo_code) for o in obs}, {('surat_district', 'surat')})
        self.assertEqual({(o.period_start, o.period_end) for o in obs},
                         {('2019-01-01', '2021-12-31'), ('2015-01-01', '2016-12-31')})

    def test_values_read_off_the_csv(self):
        # 81. Children age 6-59 months who are anaemic (<11.0 g/dl)22 (%): 83.6 / 42.3
        a = self.o(81)
        self.assertEqual((a.metric_id, a.value), ('nfhs.indicator_pct', 83.6))
        self.assertEqual(a.dims['indicator'], 'Children age 6-59 months who are anaemic (<11.0 g/dl) (%)')
        self.assertEqual(self.o(81, N4).value, 42.3)
        # 3. Sex ratio of the total population: 912 / 881
        self.assertEqual((self.o(3).metric_id, self.o(3).value, self.o(3, N4).value), ('nfhs.sex_ratio', 912, 881))
        # 39. Average out-of-pocket expenditure per delivery in a public health facility (Rs.): 2342 / 1248
        self.assertEqual((self.o(39).metric_id, self.o(39).value), ('nfhs.delivery_oop_rs', 2342))
        self.assertEqual(self.o(39, N4).value, 1248)
        # 73. stunted 36.1 / 30.0; 102. men using tobacco 32.5 (no NFHS-4 value)
        self.assertEqual((self.o(73).value, self.o(73, N4).value), (36.1, 30.0))
        self.assertEqual(self.o(102).value, 32.5)
        self.assertEqual((self.o(102, N4).value, self.o(102, N4).status), (None, 'not_reported'))

    def test_notes(self):
        # 49. fully vaccinated 92.8, "Based on 25-49 unweighted cases" -> reported with the caution note
        v = self.o(49)
        self.assertEqual((v.value, v.status, v.value_text), (92.8, 'reported', 'Based on 25-49 unweighted cases'))
        # 40. home births checked within 24 h: suppressed (<25 cases) in both rounds
        for start in (N5, N4):
            w = self.o(40, start)
            self.assertEqual((w.value, w.status), (None, 'withheld'))
            self.assertTrue(w.value_text.startswith('Percentage not shown'))

    def test_lost_subheadings_restored(self):
        self.assertEqual(self.o(86).dims['indicator'], 'Women age 15 years and above: Blood sugar level - high (141-160 mg/dl) (%)')
        self.assertEqual(self.o(89).dims['indicator'], 'Men age 15 years and above: Blood sugar level - high (141-160 mg/dl) (%)')
        self.assertEqual((self.o(86).value, self.o(89).value), (6.8, 9.3))
        self.assertEqual((self.o(94).value, self.o(97).value), (23.4, 22.6))    # elevated BP: women / men
        self.assertTrue(self.o(20).dims['indicator'].startswith('Current use of family planning methods'))
        self.assertEqual(len({o.dims['indicator'] for o in self.res.observations}), 104)

    def test_clean_label(self):
        self.assertEqual(m.clean_label('8. Population living in households with an improved drinking-water source1 (%)'),
                         (8, 'Population living in households with an improved drinking-water source (%)'))
        self.assertEqual(m.clean_label('70. Breastfeeding children age 6-23 months receiving an adequate diet16, 17  (%)'),
                         (70, 'Breastfeeding children age 6-23 months receiving an adequate diet (%)'))
        self.assertEqual(m.clean_label('78. Women whose Body Mass Index (BMI) is below normal (BMI <18.5 kg/m2)21 (%)')[1],
                         'Women whose Body Mass Index (BMI) is below normal (BMI <18.5 kg/m2) (%)')

    def test_missing_rows_rejected(self):
        lines = CSV.read_bytes().split(b'\n')
        dropped = b'\n'.join(ln for ln in lines if not ln.startswith(b'Gujarat,GJ,Surat,81.'))
        with self.assertRaises(ValidationError):
            _parse(dropped)

    def test_parenthesised_value_rejected(self):
        body = CSV.read_bytes().replace(b'Gujarat,GJ,Surat,2. Population below age 15 years (%),23.1,',
                                        b'Gujarat,GJ,Surat,2. Population below age 15 years (%),(23.1),')
        with self.assertRaises(ValidationError):
            _parse(body)


class FakeGitHub:
    def request(self, method, url, **kw):
        assert url == m.URL
        return Response(200, CSV.read_bytes(), url, {'content-type': 'text/plain; charset=utf-8'})


class TestThroughRunner(unittest.TestCase):
    def test_refresh_into_scratch_db(self):
        with tempfile.TemporaryDirectory() as d:
            conn = db.connect(Path(d) / 't.db')
            out = runner.refresh(conn, [discover()['nfhs5_surat']], data_dir=Path(d), fetcher=FakeGitHub())
            self.assertTrue(out['nfhs5_surat'].startswith('ok: 1 document(s), 208 observation(s)'), out)
            conn.close()


if __name__ == '__main__':
    unittest.main()
