import unittest

from tests import FIXTURES, raw_from_file
from opencity.model import ValidationError
from opencity.sources import smc_tenders

DIR = FIXTURES / 'smc_tenders'
FETCHED = '2026-10-24T22:11:15+05:30'


def detail(tid, retrieved_at=FETCHED):
    return raw_from_file(DIR / f'tender-{tid}-2026-10-24.html', meta={'tender_id': tid}, retrieved_at=retrieved_at)


class TestSmcTendersList(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # live Active Tenders list of 2026-10-24 (70 tenders), trimmed to its first 12 entries
        cls.raw = raw_from_file(DIR / 'active-tenders-2026-10-24-first-12.html', retrieved_at=FETCHED)
        cls.res = smc_tenders.parse(cls.raw)
        cls.rec = {r.record_key: r.attrs for r in cls.res.records}
        cls.obs = {(o.metric_id, o.dims.get('within_days')): o for o in cls.res.observations}

    def test_counts(self):
        self.assertEqual(len(self.res.records), 12)
        self.assertEqual(self.res.complete_record_types, ('tender',))
        smc_tenders.validate(self.res, self.raw)

    def test_records_read_off_the_page(self):
        # 2. "Maintenance and Repairing Work of Surat Castle ... (2nd Attempt) (W-1)", 14-10-2026 11:00 to 26-10-2026 18:00
        a = self.rec['47263']
        self.assertTrue(a['title'].startswith('Maintenance and Repairing Work of Surat Castle'))
        self.assertEqual((a['start'], a['end'], a['attempt']), ('2026-10-14T11:00', '2026-10-26T18:00', 2))
        self.assertIsNone(self.rec['47260']['attempt'])
        self.assertEqual(self.rec['47291']['end'], '2026-10-28T18:00')

    def test_daily_counts(self):
        # 4 of the 12 close on 26-10-2026 (2 days after the fetch day), the other 8 on 28-10-2026
        o = self.obs[('tenders.active', None)]
        self.assertEqual((o.value, o.period_start, o.period_end, o.geo_level), (12, '2026-10-24', '2026-10-24', 'smc_city'))
        self.assertEqual(self.obs[('tenders.closing_within', '2')].value, 4)
        self.assertEqual(self.obs[('tenders.closing_within', '7')].value, 12)
        self.assertEqual(self.obs[('tenders.closing_within', '14')].value, 12)

    def test_stale_page_is_rejected(self):
        # "Submit within: 2 Day(s)" for an End Date of 26-10-2026 means the page was rendered on 24-10-2026
        raw = raw_from_file(DIR / 'active-tenders-2026-10-24-first-12.html', retrieved_at='2026-11-02T10:00:00+05:30')
        with self.assertRaises(ValidationError):
            smc_tenders.validate(smc_tenders.parse(raw), raw)


class TestSmcTenderNotices(unittest.TestCase):
    def notice(self, tid):
        res = smc_tenders.parse(detail(tid))
        smc_tenders.validate(res, detail(tid))
        self.assertEqual([(r.record_type, r.record_key) for r in res.records], [('tender_notice', tid)])
        self.assertEqual(res.observations, [])
        return res.records[0].attrs

    def test_passenger_lift_notice(self):
        a = self.notice('47260')
        self.assertEqual(a['notice_no'], 'DMC/SZ-B/11/2026-27')
        self.assertEqual((a['notice_date'], a['available_from'], a['available_to']), ('2026-10-07', '2026-10-12', '2026-10-26'))
        self.assertEqual((a['submission_date'], a['opening_date']), ('2026-10-26', '2026-11-04'))
        self.assertEqual((a['estimated_amount_rs'], a['emd_rs'], a['fee_rs']), (1249799.25, 12500, 1062))
        self.assertEqual(a['amount_notes'], {})
        self.assertEqual(a['zone_code'], 'south_b')
        self.assertEqual(a['issuing_authority'], 'Executive Engineer, south zone -B (Kanakpur), surat municipal corporati')
        self.assertEqual(a['agency_category'], 'Experienced')
        self.assertEqual(a['submission_mode'], 'Postal Speed Post')
        self.assertEqual(len(a['documents_required']), 9)
        self.assertEqual(a['documents_required'][0], '1. Registration Certificate')
        self.assertEqual(a['other_labels'], [])
        self.assertIsNone(a['prebid_at'])

    def test_amount_with_gst_note_and_zone_from_inviting_authority(self):
        a = self.notice('47295')
        self.assertEqual(a['estimated_amount_rs'], 5901693.32)          # printed "5901693.32  - + GST"
        self.assertEqual(a['amount_notes'], {'estimated_amount_rs': '+ GST'})
        self.assertEqual((a['emd_rs'], a['fee_rs']), (60000, 2832))
        self.assertEqual(a['issuing_authority'], 'Executive Engineer')
        self.assertEqual(a['zone_code'], 'central')                    # from "Add.City Engineer Central Zone"
        self.assertEqual(a['agency_category'], '"D"')

    def test_prebid_and_unofficial_email_dropped(self):
        a = self.notice('47299')
        self.assertEqual(a['notice_no'], 'DMC/NEZ/12/2026-27')
        self.assertEqual((a['estimated_amount_rs'], a['emd_rs'], a['fee_rs']), (376230924.85, 3800000, 21240))
        self.assertEqual(a['prebid_at'], '2026-10-22T11:00')
        self.assertIsNone(a['prebid_venue'])                          # printed with a misspelt SMC domain
        self.assertEqual(a['zone_code'], 'east_b')                    # "New East (Sarthana) Zone" is East Zone-B
        self.assertEqual(a['opening_date'], '2026-10-27')

    def test_detail_needs_the_tender_id(self):
        raw = raw_from_file(DIR / 'tender-47260-2026-10-24.html', retrieved_at=FETCHED)
        with self.assertRaises(ValueError):
            smc_tenders.parse(raw)

    def test_helpers(self):
        self.assertEqual(smc_tenders._amount('₹ 1416800 - without GST'), (1416800, 'without GST'))
        self.assertEqual(smc_tenders._amount(''), (None, None))
        # attempt phrasings seen on the live list of 2026-10-24
        self.assertEqual(smc_tenders._attempt('Road work (4th Attempt) (W-2)'), 4)
        self.assertEqual(smc_tenders._attempt('O&M for 05 years.(2nd Attempt) (W-1)'), 2)
        self.assertEqual(smc_tenders._attempt('Pumps, Surat Municipal Corporation. (Third Attempt) (W-3)'), 3)
        self.assertEqual(smc_tenders._attempt('XEROX MACHINE ... (SARTHANA) ZONE, SURAT. (II ATTEMPT) (WORK NO. -1)'), 2)
        self.assertIsNone(smc_tenders._attempt('Multilevel Parking At Khan Saheb no Dello In Central Zone.'))
        self.assertIsNone(smc_tenders._zone('Executive Engineer', 'Deputy Municipal Commissioner South Zone'))
        self.assertEqual(smc_tenders._zone('Executive Engineer South Zone-A (Udhana) SMC',
                                           'Deputy Municipal Commissioner South Zone'), 'south_a')
        self.assertEqual(smc_tenders._long_date('Wednesday , 07 October , 2026'), '2026-10-07')
        self.assertEqual(smc_tenders._official('exen.sza@suratmunicipal.org'), 'exen.sza@suratmunicipal.org')
        self.assertIsNone(smc_tenders._official('someone@gmail.com'))
        self.assertIsNone(smc_tenders._official('exen@fakesuratmunicipal.org'))     # suffix only, not the domain
        self.assertEqual(smc_tenders._official('ee@gujarat.gov.in'), 'ee@gujarat.gov.in')


if __name__ == '__main__':
    unittest.main()
