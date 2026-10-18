import unittest

from tests import REFERENCE, raw_from_file
from opencity.model import ValidationError
from opencity.sources import smc_pmay

FIXTURE = REFERENCE / 'district-modules/smc-pmay-housing-projects-2026-09-28.html'


class TestSmcPmay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = raw_from_file(FIXTURE, retrieved_at='2026-09-28T02:07:00+05:30')
        cls.res = smc_pmay.parse(cls.raw)
        cls.rec = {r.record_key: r.attrs for r in cls.res.records}
        cls.obs = {(o.metric_id, o.dims['status']): o for o in cls.res.observations}

    def test_counts(self):
        self.assertEqual(len(self.res.records), 57)
        self.assertEqual(len(self.rec), 57)                 # keys are unique
        self.assertEqual(len(self.res.observations), 4)
        self.assertEqual(self.res.complete_record_types, ('housing_project',))
        smc_pmay.validate(self.res, self.raw)

    def test_project_rows_read_off_the_page(self):
        # Completed, first row: SUMAN JYOT | T.P.No.9 (Palanpore-Bhesan), F.P.No. 164 | Skyway Infra Project Pvt. Ltd. | 300 | 1967.19
        a = self.rec['suman-jyot-tp-9-fp-164']
        self.assertEqual((a['name'], a['status'], a['tp_scheme'], a['tp_area'], a['final_plot']),
                         ('SUMAN JYOT', 'completed', '9', 'Palanpore-Bhesan', '164'))
        self.assertEqual((a['contractor'], a['flats'], a['tender_amount_lakh']),
                         ('Skyway Infra Project Pvt. Ltd.', 300, 1967.19))
        self.assertEqual(a['housing_type'], 'LIG Housing')
        # Two packages in one cell: SUMAN SHAKTI, 552 flats, 1297.91 + 1995.28 lakh
        a = self.rec['suman-shakti-tp-48-fp-69-p1-p2']
        self.assertEqual((a['flats'], a['tender_amounts_lakh'], a['tender_amount_lakh']), (552, [1297.91, 1995.28], 3293.19))
        # Work in progress: SUMAN PRAKRUTI | T.P.No.48 (Bhestan), F.P.No.89 | D. H. Patel, Surat | 792 | 6502.78
        a = self.rec['suman-prakruti-tp-48-fp-89']
        self.assertEqual((a['status'], a['contractor'], a['flats'], a['tender_amount_lakh']),
                         ('work_in_progress', 'D. H. Patel, Surat', 792, 6502.78))
        # Odd location formats: "TP.No.62(...), FP.No.173 (R-5)" and "T.P. No.68 (Puna-Simada), F.P. R-11"
        self.assertEqual(self.rec['suman-nupur-tp-62-fp-173-r-5']['tp_area'], 'Dindoli-Bhestan-Bhedvad')
        self.assertEqual(self.rec['suman-prabha-tp-68-fp-r-11']['final_plot'], 'R-11')
        # Same name, two plots
        self.assertIn('suman-malhar-tp-28-fp-32-p-s-p-2', self.rec)
        self.assertIn('suman-malhar-tp-28-fp-32-p-s-p-3', self.rec)

    def test_aggregates(self):
        # 46 completed projects whose flats add up to the page's own Total (23422); 11 in progress, 6454 flats
        self.assertEqual(self.obs[('pmay.projects', 'completed')].value, 46)
        self.assertEqual(self.obs[('pmay.flats', 'completed')].value, 23422)
        self.assertEqual(self.obs[('pmay.projects', 'work_in_progress')].value, 11)
        self.assertEqual(self.obs[('pmay.flats', 'work_in_progress')].value, 6454)
        for o in self.res.observations:
            # footer "Last Updated: September 12, 2023 05:04 PM"
            self.assertEqual((o.geo_level, o.geo_code, o.period_start, o.period_end, o.publisher_as_of),
                             ('smc_city', 'smc', '2023-09-12', '2023-09-12', '2023-09-12'))

    def test_blank_flats_are_not_reported(self):
        raw = raw_from_file(FIXTURE, retrieved_at='2026-09-28T02:07:00+05:30')
        raw.body = raw.body.replace(b'<td class="text-right">792</td>', b'<td class="text-right">-</td>', 1)
        res = smc_pmay.parse(raw)
        o = next(o for o in res.observations if o.metric_id == 'pmay.flats' and o.dims['status'] == 'work_in_progress')
        self.assertEqual((o.value, o.status), (None, 'not_reported'))
        self.assertIsNone({r.record_key: r.attrs for r in res.records}['suman-prakruti-tp-48-fp-89']['flats'])

    def test_validate_rejects_bad_flat_count(self):
        raw = raw_from_file(FIXTURE, retrieved_at='2026-09-28T02:07:00+05:30')
        raw.body = raw.body.replace(b'<td class="text-right">792</td>', b'<td class="text-right">79200</td>', 1)
        with self.assertRaises(ValidationError):
            smc_pmay.validate(smc_pmay.parse(raw), raw)


if __name__ == '__main__':
    unittest.main()
