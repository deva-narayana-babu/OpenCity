import unittest

from tests import FIXTURES, raw_from_file
from opencity.sources import census2011_surat, gsdma_rainfall
from opencity.sources import surat_talukas as src

PAGE = FIXTURES / 'surat_talukas/taluka-2026-10-24.html'


class TestSuratTalukas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = raw_from_file(PAGE, retrieved_at='2026-10-24T12:00:00+05:30')
        cls.res = src.parse(cls.raw)
        cls.rec = {r.record_key: r.attrs for r in cls.res.records}
        cls.geo = {g.geo_code: g for g in cls.res.geos}

    def test_counts(self):
        self.assertEqual(len(self.res.records), 17)
        self.assertEqual(len(self.geo), 17)
        self.assertEqual(sum(a['surat_city'] for a in self.rec.values()), 6)
        src.validate(self.res, self.raw)

    def test_values_read_off_the_page(self):
        # row 8: Olpad | Mamlatdar Office, Olpad | 02621-221245 | mam-olpad[at]gujarat[dot]gov[dot]in
        self.assertEqual(self.rec['olpad'], {'taluka': 'Olpad', 'surat_city': False,
                                             'office_address': 'Mamlatdar Office, Olpad', 'phone': '02621-221245',
                                             'email': 'mam-olpad@gujarat.gov.in'})
        # row 1: Majura (Surat City), gmail address not stored
        a = self.rec['majura']
        self.assertEqual((a['taluka'], a['surat_city'], a['phone'], a['email']),
                         ('Majura (Surat City)', True, '0261-2650335', None))
        # row 6: Abrama has no phone; row 7 Chorasi
        self.assertIsNone(self.rec['abrama']['phone'])
        self.assertEqual(self.rec['chorasi']['email'], 'mam-choryasi@gujarat.gov.in')
        # row 14: Kamrej prints Bardoli's office and e-mail (kept as published)
        self.assertEqual(self.rec['kamrej']['email'], 'mam-bardoli@gujarat.gov.in')

    def test_geos(self):
        g = self.geo['areth']
        self.assertEqual((g.geo_level, g.name, g.parent_level, g.parent_code),
                         ('surat_taluka', 'Areth', 'surat_district', 'surat'))
        self.assertEqual(self.geo['puna'].name, 'Puna (Surat City)')
        self.assertEqual(self.res.complete_record_types, ('taluka_office',))

    def test_no_gmail_or_mobile_stored(self):
        for a in self.rec.values():
            self.assertNotIn('gmail', str(a))

    def test_names_match_other_taluka_sources(self):
        for code, name in gsdma_rainfall.NAMES.items():
            self.assertEqual(src.NAMES[code], name)
        for code, _, name in census2011_surat.SUBDISTRICTS.values():
            self.assertEqual(src.NAMES[code], name)


if __name__ == '__main__':
    unittest.main()
