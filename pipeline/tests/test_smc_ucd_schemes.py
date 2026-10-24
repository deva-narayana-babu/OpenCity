import unittest

from tests import FIXTURES, raw_from_file
from opencity.sources import smc_ucd_schemes

FIXTURE = FIXTURES / 'smc_ucd_schemes/ucd-home-2026-10-24.html'


class TestSmcUcdSchemes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = raw_from_file(FIXTURE)
        cls.res = smc_ucd_schemes.parse(cls.raw)
        cls.rec = {r.record_key: r.attrs for r in cls.res.records}

    def test_schemes(self):
        self.assertEqual(list(self.rec), [
            'self-help-group-shg', 'employment-through-skills-training-placement-est-p',
            'self-employment-programme-individual', 'self-employment-programme-group', 'shg-bank-linkage',
            'shelter-for-urban-homeless-suh', 'support-to-urban-street-vendors-susv', 'pmsvanidhi', 'mmuy'])
        self.assertEqual(self.res.observations, [])
        self.assertEqual(self.res.complete_record_types, ('smc_ucd_scheme',))
        smc_ucd_schemes.validate(self.res, self.raw)

    def test_values_read_off_the_page(self):
        shg = self.rec['self-help-group-shg']
        self.assertEqual(shg['title'], '(અ) સ્વ-સહાય જૂથ (Self Help Group-SHG)')
        self.assertEqual(shg['name_en'], 'Self Help Group-SHG')
        self.assertTrue(shg['component'].endswith('(Social Mobilisation And Institution Development – SM&ID)'))
        # "હેતુ" (purpose): groups of 10 to 20 urban poor women; "સહાય": Rs 10,000 revolving fund after grading
        self.assertEqual(shg['purpose'], '૧૦ થી ૨૦ શહેરી ગરીબ મહિલાઓનું જૂથ બનાવી બચત કરવાનો અભિગમ વિકસાવવો.')
        self.assertIn('રૂ. ૧૦,૦૦૦/- રીવોલ્વીંગ ફંડ', shg['assistance'])
        # SEP (individual): project amount up to Rs 2,00,000
        self.assertEqual(self.rec['self-employment-programme-individual']['project_amount'],
                         'રૂ. ૨,૦૦,૦૦૦/- (બે લાખ)ની મર્યાદામાં')
        # EST&P "તાલીમ ફી" (training fee): the beneficiary pays no fee
        self.assertEqual(self.rec['employment-through-skills-training-placement-est-p']['training_fee'],
                         'લાભાર્થીને કોઈપણ પ્રકારની ફી ચુકવવાની રહેતી નથી.')
        # unlabelled schemes keep their points in order: PM SVANidhi has 4, MMUY 10
        self.assertEqual(len(self.rec['pmsvanidhi']['points']), 4)
        self.assertIn('રૂ. ૧૦,૦૦૦/-', self.rec['pmsvanidhi']['points'][2])
        self.assertEqual(len(self.rec['mmuy']['points']), 10)
        self.assertIsNone(self.rec['mmuy']['component'])


if __name__ == '__main__':
    unittest.main()
