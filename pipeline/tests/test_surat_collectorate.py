import unittest

from tests import FIXTURES, raw_from_file
from opencity.model import ValidationError
from opencity.sources import surat_collectorate

FIXTURE = FIXTURES / 'surat_collectorate/surat-whos-who-2026-10-24.html'


class TestSuratCollectorate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = raw_from_file(FIXTURE, retrieved_at='2026-10-24T02:30:00+05:30')
        cls.res = surat_collectorate.parse(cls.raw)
        cls.by = {r.record_key: r.attrs for r in cls.res.records}

    def test_counts(self):
        surat_collectorate.validate(self.res, self.raw)
        divisions = [a['division'] for a in self.by.values()]
        self.assertEqual((divisions.count('Collectorate'), divisions.count('Prant Officers')), (5, 6))
        self.assertEqual(self.res.complete_record_types, ('district_official',))

    def test_values_read_off_the_page(self):
        # "Shri Tejas Parmar IAS | Collector & District Magistrate | collector-sur[at]gujarat[dot]gov[dot]in |
        #  Collector Office, Jilla Seva Sadan-II, "B" Block, 5th Floor, Athwalines, Surat-395001 | +91-261-2655151 | +91-261-2655757"
        self.assertEqual(self.by['collector-district-magistrate'], {
            'division': 'Collectorate', 'designation': 'Collector & District Magistrate', 'honorific': 'Shri',
            'name': 'Tejas Parmar', 'service': 'IAS', 'email': 'collector-sur@gujarat.gov.in',
            'office_address': 'Collector Office, Jilla Seva Sadan-II, "B" Block, 5th Floor, Athwalines, Surat-395001',
            'phones': ['+91-261-2655151'], 'fax': ['+91-261-2655757']})
        rac = self.by['residential-additional-collector']
        self.assertEqual((rac['name'], rac['email'], rac['phones'], rac['fax']),
                         ('Vijay Rabari', 'rdc-sur@gujarat.gov.in', ['91-261-2669200'], []))
        bardoli = self.by['deputy-collector-prant-officer-bardoli']
        self.assertEqual((bardoli['division'], bardoli['name'], bardoli['phones']),
                         ('Prant Officers', 'Roshni J Patel', ['91-2622-221124']))

    def test_only_government_email(self):
        # the Prant offices publish gmail.com addresses: not stored
        self.assertIsNone(self.by['deputy-collector-prant-officer-olpad']['email'])
        self.assertIsNone(self.by['dy-collector-land-reform']['email'])
        for a in self.by.values():
            self.assertTrue(a['email'] is None or a['email'].endswith('.gov.in'), a['email'])

    def test_normalize_blanks_the_nonce(self):
        a = b'<div class ="ww_html" data-nonce="cdb7e59354" data-profile="">'
        b = b'<div class ="ww_html" data-nonce="f2156dd331" data-profile="">'
        self.assertEqual(surat_collectorate.normalize(a), surat_collectorate.normalize(b))

    def test_validate_needs_the_collector(self):
        res = surat_collectorate.parse(self.raw)
        res.records = [r for r in res.records if r.record_key != 'collector-district-magistrate']
        with self.assertRaises(ValidationError):
            surat_collectorate.validate(res, self.raw)


if __name__ == '__main__':
    unittest.main()
