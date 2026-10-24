import unittest

from tests import FIXTURES, raw_from_file
from opencity.model import Raw, ValidationError
from opencity.sources import smc_officials

FIXTURE = FIXTURES / 'smc_officials/smc-officials-2026-10-24.html'


class TestSmcOfficials(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = raw_from_file(FIXTURE, retrieved_at='2026-10-24T02:30:00+05:30')
        cls.res = smc_officials.parse(cls.raw)
        cls.by = {r.record_key: r.attrs for r in cls.res.records}

    def test_counts(self):
        smc_officials.validate(self.res, self.raw)
        self.assertEqual(len(self.res.records), 92)
        wings = [r.attrs['wing'] for r in self.res.records]
        self.assertEqual({w: wings.count(w) for w in set(wings)},
                         {'commissioner': 1, 'administrative': 42, 'engineering': 16, 'health': 33})
        self.assertEqual(self.res.complete_record_types, ('smc_official',))
        dmc = [a for a in self.by.values() if a['designation'].startswith('Deputy Mun. Commissioner')]
        self.assertEqual(len(dmc), 7)

    def test_values_read_off_the_page(self):
        # "Shri Rajkumar Beniwal, IAS / Municipal Commissioner, Surat Municipal Corporation / (O) +91-261-2422244 / (F) +91-261-2422110"
        mc = self.by['municipal-commissioner-surat-municipal-corporation']
        self.assertEqual(mc, {'wing': 'commissioner', 'honorific': 'Shri', 'name': 'Rajkumar Beniwal', 'service': 'IAS',
                              'designation': 'Municipal Commissioner, Surat Municipal Corporation',
                              'office_phones': ['+91-261-2422244'], 'fax': '+91-261-2422110', 'emails': []})
        # "Ms. Nidhi Siwach (IAS) / Deputy Mun. Commissioner (Deputation) / (O) 0261-2423750 (PABX - 222) / dmc.ns"
        d = self.by['deputy-mun-commissioner-deputation']
        self.assertEqual((d['name'], d['service'], d['office_phones'], d['emails']),
                         ('Nidhi Siwach', 'IAS', ['0261-2423750 (PABX - 222)'], ['dmc.ns@suratmunicipal.gov.in']))
        # repeated designation -> name appended to the key
        self.assertEqual(self.by['deputy-mun-commissioner-swati-p-desai']['office_phones'], ['0261-2432690 (PABX - 337)'])
        # comma inside the PABX brackets stays one entry; two "(O)" lines give two entries
        self.assertEqual(self.by['medical-superintendent-smimer-prof-ms-general-surgery']['office_phones'],
                         ['0261-2333756 (PABX - 1600, 2005)'])
        self.assertEqual(self.by['dean-smimer']['office_phones'], ['0261-2366367 (PABX - 1100)', '0261-2252858'])
        # an "(O)" number printed in the mobile CSS class is still an office number
        self.assertEqual(self.by['i-c-public-relations-officer-manager-indoor-stadium-gandhi-smruti-bhavan-rang-upvan-'
                                 'sports-sports-development']['office_phones'], ['0261-2664325 (PABX - 21)'])
        self.assertEqual(self.by['chief-fire-officer']['name'], 'Basantkumar Pareek')

    def test_zone_on_food_safety_cards(self):
        a = self.by['food-safety-officer-s-c-desai']
        self.assertEqual((a['zone'], a['zone_code']), ('South West Zone(Athwa)', 'south_west'))
        self.assertEqual(sum(1 for k in self.by if k.startswith('food-safety-officer-')), 20)

    def test_no_personal_contacts(self):
        # "(O) 63599 06891, 6359909271, 6359909272" are mobile-format numbers: dropped
        self.assertEqual(self.by['administrative-officer-affordable-housing-cell']['office_phones'], [])
        for a in self.by.values():
            for e in a['emails']:
                self.assertTrue(e.endswith('@suratmunicipal.gov.in'), e)
            self.assertLessEqual(set(a), smc_officials.ALLOWED_ATTRS)

    def test_mobiles_and_private_mail_are_dropped_and_blanked(self):
        # synthetic card in the page's layout, with a dummy mobile and a private address
        html = (b'<h2>Contact Details of SMC Officers</h2><div class="contact-heading">Health</div><ul>'
                b'<li class="contact-block"><div class="name">Sh. A B Test</div><div class="designation">Food Safety Officer</div>'
                b'<div class="contact-mobile">(M) 9876543210</div><div class="officeTelephone">(O) 0261-2423750, 98765 43210</div>'
                b'<div class="contact-email">a.b.test[at]gmail[dot]com</div></li></ul>'
                b'<script>$(".contact-email.govdotin").append("[at]suratmunicipal[dot]gov[dot]in");</script>')
        raw = Raw('u', html, 'text/html', 0, '', True, '2026-10-24T00:00:00+05:30')
        (r,) = smc_officials.parse(raw).records
        self.assertEqual((r.attrs['office_phones'], r.attrs['emails']), (['0261-2423750'], []))
        clean = smc_officials.normalize(html)
        self.assertNotIn(b'9876543210', clean)
        self.assertNotIn(b'gmail', clean)
        self.assertIn(b'98765 43210', clean)      # an "(O)" line is left alone in the archive (parse drops it)

    def test_validate_rejects_a_mobile(self):
        res = smc_officials.parse(self.raw)
        res.records[1].attrs['office_phones'] = ['9876543210']
        with self.assertRaises(ValidationError):
            smc_officials.validate(res, self.raw)


if __name__ == '__main__':
    unittest.main()
