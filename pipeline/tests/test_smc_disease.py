import unittest

from tests import REFERENCE, raw_from_file
from opencity.model import ValidationError, canonical_json
from opencity.sources import smc_disease

DISEASE_FILE = REFERENCE / 'health-environment/smc-disease-incidence-statistics-2026-09-28.html'
VBDC_FILE = REFERENCE / 'health-environment/smc-vbdc-activity-statistics-2026-09-27.html'


def _index(res):
    return {(o.metric_id, o.period_start, canonical_json(o.dims)): o for o in res.observations}


def _key(metric, start, **dims):
    return (metric, start, canonical_json(dims))


class TestDiseasePage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = raw_from_file(DISEASE_FILE, meta={'page': 'disease'})
        cls.res = smc_disease.parse(cls.raw)
        cls.by = _index(cls.res)

    def test_counts_and_validate(self):
        # 5 diseases x 28 years (1995-2022) x 12 months x {cases, deaths} = 3360
        # cholera 21 years (2002-2022) x 12 x 2 = 504
        # malaria Jan 2005 - Oct 2023 = 226 months x 6 metrics/dims = 1356
        self.assertEqual(len(self.res.observations), 3360 + 504 + 1356)
        self.assertEqual(len(self.by), len(self.res.observations))      # no duplicate keys
        smc_disease.validate(self.res, self.raw)

    def test_ind_and_d_rows(self):
        c, d = 'health.disease.cases', 'health.disease.deaths'
        # Gastro Enteritis 1995: Jan Ind 55, Aug Ind 291, Jan D 1
        self.assertEqual(self.by[_key(c, '1995-01-01', disease='gastroenteritis')].value, 55)
        self.assertEqual(self.by[_key(c, '1995-08-01', disease='gastroenteritis')].value, 291)
        self.assertEqual(self.by[_key(d, '1995-01-01', disease='gastroenteritis')].value, 1)
        # Pulmonary TB 2022: Mar Ind 1427; 1996: May D 18
        self.assertEqual(self.by[_key(c, '2022-03-01', disease='pulmonary_tb')].value, 1427)
        self.assertEqual(self.by[_key(d, '1996-05-01', disease='pulmonary_tb')].value, 18)
        # Enteric Fever 1995 Sept Ind 35; Hepatitis 1996 June Ind 95
        self.assertEqual(self.by[_key(c, '1995-09-01', disease='enteric_fever')].value, 35)
        self.assertEqual(self.by[_key(c, '1996-06-01', disease='hepatitis')].value, 95)
        # Cholera 2016: May Ind 47 (row TOT says 124 though months add to 126; stored as published per month)
        self.assertEqual(self.by[_key(c, '2016-05-01', disease='cholera')].value, 47)
        # Cholera table starts in 2002
        self.assertNotIn(_key(c, '2001-01-01', disease='cholera'), self.by)
        self.assertIn(_key(c, '2002-01-01', disease='cholera'), self.by)

    def test_blank_is_not_reported_and_zero_is_zero(self):
        # Pneumonia 2022 Dec cell is '&nbsp;'
        o = self.by[_key('health.disease.cases', '2022-12-01', disease='pneumonia')]
        self.assertEqual((o.status, o.value), ('not_reported', None))
        # Pulmonary TB 2022 Nov is printed as 0, so it stays a reported 0
        o = self.by[_key('health.disease.cases', '2022-11-01', disease='pulmonary_tb')]
        self.assertEqual((o.status, o.value), ('reported', 0))
        self.assertEqual(sum(1 for o in self.res.observations if o.status == 'not_reported'), 1)

    def test_malaria_table(self):
        # January 2005: Collection 32848, Examined 32848, Positive 315, P.vivax 150, P.falci 165, Death 0
        s = '2005-01-01'
        self.assertEqual(self.by[_key('health.malaria.smears_collected', s)].value, 32848)
        self.assertEqual(self.by[_key('health.malaria.smears_examined', s)].value, 32848)
        self.assertEqual(self.by[_key('health.disease.cases', s, disease='malaria')].value, 315)
        self.assertEqual(self.by[_key('health.malaria.positive_by_species', s, species='p_vivax')].value, 150)
        self.assertEqual(self.by[_key('health.malaria.positive_by_species', s, species='p_falciparum')].value, 165)
        self.assertEqual(self.by[_key('health.disease.deaths', s, disease='malaria')].value, 0)
        # October 2023 (last row): 110719 collected, 83 positive, 74 Pv, 9 Pf
        s = '2023-10-01'
        self.assertEqual(self.by[_key('health.malaria.smears_collected', s)].value, 110719)
        self.assertEqual(self.by[_key('health.disease.cases', s, disease='malaria')].value, 83)
        self.assertEqual(self.by[_key('health.malaria.positive_by_species', s, species='p_vivax')].value, 74)
        self.assertEqual(self.by[_key('health.malaria.positive_by_species', s, species='p_falciparum')].value, 9)
        # 2023 stops at October; yearly 'Total' rows are not stored as months
        self.assertNotIn(_key('health.disease.cases', '2023-11-01', disease='malaria'), self.by)
        self.assertFalse(any(o.period_end[5:] == '12-31' and o.period_start[5:] == '01-01'
                             for o in self.res.observations))

    def test_geography_period_and_as_of(self):
        o = self.by[_key('health.disease.cases', '1996-02-01', disease='gastroenteritis')]
        self.assertEqual((o.geo_level, o.geo_code, o.period_end), ('smc_city', 'smc', '1996-02-29'))
        self.assertEqual(o.publisher_as_of, '2023-11-09')          # "Last Updated: November 09, 2023 03:38 PM"
        self.assertEqual({o.dims['disease'] for o in self.res.observations if 'disease' in o.dims},
                         smc_disease.EXPECTED_DISEASES)

    def test_page_detected_without_meta(self):
        res = smc_disease.parse(raw_from_file(DISEASE_FILE))      # e.g. `opencity parse-file`
        self.assertEqual(len(res.observations), len(self.res.observations))


class TestVbdcPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = raw_from_file(VBDC_FILE, meta={'page': 'vbdc'})
        cls.res = smc_disease.parse(cls.raw)
        cls.by = _index(cls.res)

    def test_counts_and_validate(self):
        # Jan 2005 - Oct 2023 = 226 months x 18 series (Total rows/columns not stored)
        self.assertEqual(len(self.res.observations), 226 * 18)
        self.assertEqual(len(self.by), len(self.res.observations))
        self.assertTrue(all(o.status == 'reported' for o in self.res.observations))
        smc_disease.validate(self.res, self.raw)

    def test_values_read_off_the_page(self):
        b = self.by
        # January 2005 row
        s = '2005-01-01'
        self.assertEqual(b[_key('vbdc.houses_checked', s)].value, 486977)
        self.assertEqual(b[_key('vbdc.breeding_spots_checked', s, survey='intra_domestic')].value, 1106802)
        self.assertEqual(b[_key('vbdc.breeding_spots_positive', s, survey='intra_domestic', mosquito='anopheles')].value, 790)
        self.assertEqual(b[_key('vbdc.breeding_spots_positive', s, survey='intra_domestic', mosquito='aedes')].value, 1994)
        self.assertEqual(b[_key('vbdc.breeding_spots_positive', s, survey='intra_domestic', mosquito='culex')].value, 78)
        self.assertEqual(b[_key('vbdc.breeding_spots_positive', s, survey='intra_domestic', mosquito='mixed')].value, 192)
        self.assertEqual(b[_key('vbdc.construction_sites_checked', s)].value, 4203)
        self.assertEqual(b[_key('vbdc.breeding_spots_checked', s, survey='peri_domestic')].value, 93106)
        self.assertEqual(b[_key('vbdc.breeding_spots_positive', s, survey='peri_domestic', mosquito='culex')].value, 1774)
        self.assertEqual(b[_key('vbdc.biological_control', s)].value, 982)
        self.assertEqual(b[_key('vbdc.notices_issued', s)].value, 590)
        self.assertEqual(b[_key('vbdc.admin_charges', s)].value, 40250)
        self.assertEqual(b[_key('vbdc.source_reduction', s)].value, 2671)
        self.assertEqual(b[_key('vbdc.fogging_rounds', s, equipment='vehicle_mounted')].value, 198)
        self.assertEqual(b[_key('vbdc.fogging_rounds', s, equipment='handheld')].value, 2913)
        # October 2023 row (the last month on the page)
        s = '2023-10-01'
        self.assertEqual(b[_key('vbdc.houses_checked', s)].value, 1389099)
        self.assertEqual(b[_key('vbdc.breeding_spots_positive', s, survey='intra_domestic', mosquito='aedes')].value, 9726)
        self.assertEqual(b[_key('vbdc.breeding_spots_checked', s, survey='peri_domestic')].value, 353097)
        self.assertEqual(b[_key('vbdc.admin_charges', s)].value, 1095300)
        self.assertEqual(b[_key('vbdc.fogging_rounds', s, equipment='handheld')].value, 7848)
        self.assertEqual(max(o.period_start for o in self.res.observations), '2023-10-01')
        self.assertEqual(b[_key('vbdc.houses_checked', s)].publisher_as_of, '2023-11-09')

    def test_page_detected_without_meta(self):
        res = smc_disease.parse(raw_from_file(VBDC_FILE))
        self.assertEqual(len(res.observations), len(self.res.observations))


SHIFTED = """<table><caption>Gastro Enteritis Statistics</caption>
<tr><th>Month</th><th>Particulars</th><th>Jan</th><th>Feb</th><th>Mar</th><th>April</th><th>May</th><th>June</th>
<th>July</th><th>Aug</th><th>Sept</th><th>Oct</th><th>Nov</th><th>Dec</th><th>TOT</th></tr>
%s</table>"""
# each row's cells moved one column right (Jan cell lost), so the TOT lands in Dec and the sums break
_ROW = '<tr><td>%d</td><td>Ind</td><td>9</td><td>9</td><td>9</td><td>9</td><td>9</td><td>9</td><td>9</td>' \
       '<td>9</td><td>9</td><td>9</td><td>9</td><td>108</td><td></td></tr>'


class TestFailsLoudly(unittest.TestCase):
    def _raw(self, body):
        r = raw_from_file(DISEASE_FILE, meta={'page': 'disease'})
        r.body = body.encode()
        return r

    def test_column_shift_detected(self):
        body = SHIFTED % ''.join(_ROW % y for y in (2001, 2002, 2003))
        with self.assertRaisesRegex(ValidationError, 'do not add up'):
            smc_disease.parse(self._raw(body))

    def test_unknown_disease_caption(self):
        body = (SHIFTED % '').replace('Gastro Enteritis', 'Dengue')
        with self.assertRaisesRegex(ValueError, 'unknown disease'):
            smc_disease.parse(self._raw(body))

    def test_validate_rejects_implausible_value(self):
        res = smc_disease.parse(raw_from_file(DISEASE_FILE, meta={'page': 'disease'}))
        res.observations[0].value = 5_000_000
        with self.assertRaises(ValidationError):
            smc_disease.validate(res, None)

    def test_validate_rejects_species_not_adding_up(self):
        res = smc_disease.parse(raw_from_file(DISEASE_FILE, meta={'page': 'disease'}))
        n = 0
        for o in res.observations:
            if o.metric_id == 'health.malaria.positive_by_species' and o.dims['species'] == 'p_vivax' and n < 5:
                o.value += 1
                n += 1
        with self.assertRaisesRegex(ValidationError, 'inconsistent'):
            smc_disease.validate(res, None)


if __name__ == '__main__':
    unittest.main()
