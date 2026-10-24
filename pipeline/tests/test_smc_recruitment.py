import unittest

from tests import FIXTURES, raw_from_file
from opencity.model import ValidationError
from opencity.sources import smc_recruitment

PAGE = FIXTURES / 'smc_recruitment/current-recruitment-2026-10-24.html'
FETCHED = '2026-10-24T22:11:07+05:30'


class TestSmcRecruitment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = raw_from_file(PAGE, retrieved_at=FETCHED)
        cls.res = smc_recruitment.parse(cls.raw)
        cls.rec = {r.record_key: r.attrs for r in cls.res.records}
        cls.obs = {o.metric_id: o for o in cls.res.observations}

    def test_counts(self):
        self.assertEqual(sorted(self.rec), ['pro-263-2026-09-29', 'pro-301-2026-10-21'])
        self.assertEqual(self.res.complete_record_types, ('recruitment_ad',))
        smc_recruitment.validate(self.res, self.raw)

    def test_records_read_off_the_page(self):
        # PRO No. 301 of 21/10/2026: 9 cadres, 18 posts, applications 09/11/2026 11:00 AM - 23/11/2026 11:00 PM
        a = self.rec['pro-301-2026-10-21']
        self.assertEqual((a['pro_no'], a['ad_date'], a['posts']), (301, '2026-10-21', 18))
        self.assertEqual((a['application_start'], a['application_end']), ('2026-11-09T11:00', '2026-11-23T23:00'))
        self.assertTrue(a['title'].startswith('જાહેરાત ક્રમાંક :પી.આર.ઓ.નં.૩૦૧'))
        self.assertEqual(a['notice_pdf'], 'https://www.suratmunicipal.gov.in/Contents/Jobs/Opening/1973333.pdf')
        self.assertIsNone(a['apply_url'])                     # window not open yet: no "Apply Now" button
        self.assertEqual((a['organisation'], a['section']), ('Surat Municipal Corporation', 'Opening'))
        # PRO No. 263 of 29/09/2026: honorary sports coaches, 8 posts, closing 24/10/2026 11:00 PM ("Today")
        b = self.rec['pro-263-2026-09-29']
        self.assertEqual((b['posts'], b['application_end']), (8, '2026-10-24T23:00'))
        self.assertEqual(b['apply_url'], 'https://www.suratmunicipal.gov.in/recruitment/')
        self.assertNotIn('remaining', b)

    def test_daily_counts(self):
        ads, posts = self.obs['recruitment.open_ads'], self.obs['recruitment.posts']
        self.assertEqual((ads.value, ads.period_start, ads.period_end, ads.geo_code), (2, '2026-10-24', '2026-10-24', 'smc'))
        self.assertEqual((posts.value, posts.status), (26, 'reported'))

    def test_stale_page_is_rejected(self):
        # "Remaining Day(s): 30 day(s)" to 23/11/2026 dates the page to 24/10/2026, not the fetch day below
        raw = raw_from_file(PAGE, retrieved_at='2026-11-10T09:00:00+05:30')
        with self.assertRaises(ValidationError):
            smc_recruitment.validate(smc_recruitment.parse(raw), raw)

    def test_pro_number_from_gujarati_title(self):
        self.assertEqual(smc_recruitment._pro('જાહેરાત ક્રમાંક :પી.આર.ઓ.નં.૨૬૩, તા.૨૯/૦૯/૨૦૨૬ થી'), (263, '2026-09-29'))
        self.assertEqual(smc_recruitment._pro('no number here'), (None, None))


if __name__ == '__main__':
    unittest.main()
