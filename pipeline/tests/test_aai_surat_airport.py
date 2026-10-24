import logging
import types
import unittest

from tests import FIXTURES, raw_from_file
from opencity.sources import aai_surat_airport

# Pages 1, 2 and 5 of AAI Traffic News August 2026, Annexure III (parts A, B and C), document metadata removed
PDF = FIXTURES / 'aai_surat_airport/aug2026-annex3-pages-1-2-5.pdf'


class TestAaiSuratAirport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = raw_from_file(PDF, retrieved_at='2026-10-23T23:20:00+05:30')
        cls.res = aai_surat_airport.parse(cls.raw)
        cls.by = {(o.metric_id, o.dims['traffic']): o for o in cls.res.observations}

    def test_counts(self):
        self.assertEqual(len(self.res.observations), 6)
        aai_surat_airport.validate(self.res, self.raw)

    def test_values_read_off_the_pdf(self):
        # "15 सूरत SURAT  7021  15442  -54.5%  17406  82321  -78.9%" (III A) and the same row in III B and III C
        self.assertEqual(self.by[('aai.passengers', 'international')].value, 7021)
        self.assertEqual(self.by[('aai.passengers', 'domestic')].value, 105829)
        self.assertEqual(self.by[('aai.passengers', 'total')].value, 112850)
        self.assertEqual(self.by[('aai.passengers_fytd', 'international')].value, 17406)
        self.assertEqual(self.by[('aai.passengers_fytd', 'domestic')].value, 639691)
        self.assertEqual(self.by[('aai.passengers_fytd', 'total')].value, 657097)

    def test_geography_and_periods(self):
        o = self.by[('aai.passengers', 'total')]
        self.assertEqual((o.geo_level, o.geo_code, o.period_start, o.period_end),
                         ('facility', 'surat_airport', '2026-08-01', '2026-08-31'))
        f = self.by[('aai.passengers_fytd', 'total')]
        self.assertEqual((f.period_start, f.period_end), ('2026-04-01', '2026-08-31'))
        self.assertEqual([(g.geo_level, g.geo_code, g.parent_code) for g in self.res.geos],
                         [('facility', 'surat_airport', 'surat')])

    def test_disabled_and_fetches_nothing(self):
        self.assertFalse(aai_surat_airport.SOURCE.enabled)
        ctx = types.SimpleNamespace(log=logging.getLogger('test'))
        with self.assertLogs('test', level='WARNING'):
            self.assertEqual(list(aai_surat_airport.fetch(ctx)), [])


if __name__ == '__main__':
    unittest.main()
