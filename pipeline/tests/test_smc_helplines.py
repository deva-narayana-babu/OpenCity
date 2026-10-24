import unittest

from tests import FIXTURES, raw_from_file
from opencity.model import ValidationError
from opencity.sources import smc_helplines

FIXTURE = FIXTURES / 'smc_helplines/emergency-contact-no-2026-10-24.html'


class TestSmcHelplines(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = raw_from_file(FIXTURE, retrieved_at='2026-10-24T02:30:00+05:30')
        cls.res = smc_helplines.parse(cls.raw)
        cls.by = {r.record_key: r.attrs for r in cls.res.records}

    def test_counts(self):
        smc_helplines.validate(self.res, self.raw)
        self.assertEqual(len(self.res.records), 30)
        sections = [a['section'] for a in self.by.values()]
        self.assertEqual((sections.count('zone'), sections.count('other')), (16, 14))
        self.assertEqual(self.res.complete_record_types, ('smc_helpline',))

    def test_values_read_off_the_page(self):
        # "SMC Help Line / For Complaint Registration /
        #  1800-123-8000 (Toll Free), 0261-2451913, 0261-2423751-56 (Ext.-300) [6:00 am to 10:00 pm]"
        self.assertEqual(self.by['smc-help-line-for-complaint-registration'], {
            'section': 'other', 'service': 'SMC Help Line', 'line': 'For Complaint Registration',
            'numbers': ['1800-123-8000 (Toll Free)', '0261-2451913', '0261-2423751-56 (Ext.-300)'],
            'toll_free': True, 'hours': '6:00 am to 10:00 pm'})
        self.assertEqual(self.by['fire-control-room']['numbers'], ['2414195-96', '2423751-56 (Ext - 324)', '9724346022'])
        self.assertEqual(self.by['complaint-registration-via-whatsapp-whatsapp-number']['numbers'], ['6359930020'])
        # the comma list inside "(Ext - 205, 421, 422, 423)" stays with its number
        self.assertEqual(self.by['central-zone-contact-number']['numbers'],
                         ['2420547', '2427726', '2423751 to 56 (Ext - 205, 421, 422, 423)'])

    def test_old_zone_names(self):
        self.assertEqual(self.by['central-zone-control-room']['zone_code'], 'central')
        self.assertEqual(self.by['south-zone-control-room']['zone_code'], 'south')      # pre-split South Zone
        self.assertIsNone(self.by['east-zone-control-room']['zone_code'])              # East A or B: not guessed
        self.assertIsNone(self.by['smc-hq-central-control-room']['zone_code'])
        self.assertNotIn('zone_code', self.by['fire-contact-number'])

    def test_validate_wants_fire_101(self):
        res = smc_helplines.parse(self.raw)
        for r in res.records:
            if r.attrs['service'] == 'Fire':
                r.attrs['numbers'] = [n for n in r.attrs['numbers'] if n != '101']
        with self.assertRaises(ValidationError):
            smc_helplines.validate(res, self.raw)


if __name__ == '__main__':
    unittest.main()
