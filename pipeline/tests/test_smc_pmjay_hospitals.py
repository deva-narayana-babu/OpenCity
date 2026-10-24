import dataclasses
import unittest

from tests import FIXTURES
from opencity.model import ValidationError
from opencity.sources import smc_pmjay_hospitals

# pdftotext -raw -bbox word list of pages 1-2 of the real PDF (rows 1-18), contact columns removed
FIXTURE = FIXTURES / 'smc_pmjay_hospitals/pmjayhospitals-p1-2-words.html'


class TestSmcPmjayHospitals(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.res = smc_pmjay_hospitals.parse_bbox(FIXTURE.read_text(encoding='utf-8'))
        cls.rec = {r.record_key: r.attrs for r in cls.res.records}
        cls.obs = {o.dims.get('speciality'): o for o in cls.res.observations}

    def test_rows(self):
        self.assertEqual([r.attrs['serial_no'] for r in self.res.records], [str(i) for i in range(1, 19)])
        self.assertEqual(self.res.complete_record_types, ('pmjay_hospital',))

    def test_records_read_off_the_pdf(self):
        # row 1: Aamena Sarvajanik Hospital, HOSP24T123955, Gujarat, Surat, Unn
        self.assertEqual(self.rec['hosp24t123955'], {
            'serial_no': '1', 'name': 'Aamena Sarvajanik Hospital', 'pmjay_id': 'HOSP24T123955',
            'state': 'Gujarat', 'district': 'Surat',
            'address': 'Rahat Co.Op. Housing Society,Gabheni,Unn,Surat- 394230',
            'specialities': ['MEDICAL MANAGEMENT', 'GENERAL SURGERY', 'ORTHOPEDIC', 'PEDIATRIC MANAGEMENT', 'NEONATAL'],
            'speciality_groups': ['general_surgery', 'neonatal', 'orthopaedics', 'paediatrics']})
        # row 2: a three-line name and a three-line address, centred around the serial number
        self.assertEqual(self.rec['hosp24p129906']['name'],
                         'Amity Advanced Institute Of Higher Medical Science And Research Centre')
        # row 11 has no hospital ID; row 12 has an old-style HS ID
        self.assertIsNone(self.rec['name-baps-pramukh-swami-hospital']['pmjay_id'])
        self.assertEqual(self.rec['hs24022087']['name'], 'Bardoli Hospital')
        # row 8: Excel's mid-word wrap is kept as extracted, but still grouped
        self.assertIn('Orthopae dics', self.rec['hosp24p68107']['specialities'])
        self.assertIn('orthopaedics', self.rec['hosp24p68107']['speciality_groups'])

    def test_no_personal_columns(self):
        for a in self.rec.values():
            self.assertNotIn('contact_person', a)
            self.assertFalse(any(len(w) == 10 and w.isdigit() for v in a.values() for w in str(v).split()))

    def test_counts(self):
        o = self.obs[None]
        self.assertEqual((o.metric_id, o.geo_level, o.geo_code, o.value), ('pmjay.listed_hospitals', 'surat_district',
                                                                             'surat', 18))
        self.assertEqual((o.period_start, o.publisher_as_of), ('2024-06-27', '2024-06-27'))   # PDF CreationDate
        self.assertEqual(self.obs['orthopaedics'].value, 11)
        self.assertEqual(self.obs['cardiology'].value, 3)
        self.assertEqual(self.obs['ophthalmology'].value, 0)

    def test_speciality_groups(self):
        g = smc_pmjay_hospitals.speciality_groups
        self.assertEqual(g(['Neurology']), ['neurology'])                 # not urology
        self.assertEqual(g(['Treatment Procedure Dental Procedures']), ['dental'])   # not ENT
        self.assertEqual(g(['Paediatric Cancer']), ['oncology', 'paediatrics'])
        self.assertEqual(g(['Gyneac and Obstrec', 'POLY TRUMA', 'Cardio- thoracic & Vascular Surgery']),
                         ['cardiothoracic_surgery', 'obstetrics_gynaecology', 'polytrauma'])
        self.assertEqual(g(['Medical Management']), [])

    def test_validate(self):
        with self.assertRaisesRegex(ValidationError, '18 hospitals parsed'):     # a 2-page excerpt is too short
            smc_pmjay_hospitals.validate(self.res, None)
        many = dataclasses.replace(self.res, records=[
            dataclasses.replace(r, attrs={**r.attrs, 'address': f'{r.attrs["address"]} {i}'})
            for i in range(4) for r in self.res.records])
        smc_pmjay_hospitals.validate(many, None)
        moved = dataclasses.replace(many, records=[dataclasses.replace(
            many.records[0], attrs={**many.records[0].attrs, 'district': 'Surat Gujarat'})] + many.records[1:])
        with self.assertRaisesRegex(ValidationError, 'columns may have moved'):
            smc_pmjay_hospitals.validate(moved, None)


if __name__ == '__main__':
    unittest.main()
