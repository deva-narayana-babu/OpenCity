import copy
import json
import re
import unittest

from tests import REFERENCE, raw_from_file
from opencity.model import Raw, ValidationError
from opencity.sources import smc_council

CORP = REFERENCE / 'governance/smc-corporators-ward-list-2026-09-28.html'
OB = REFERENCE / 'district-modules/smc-office-bearers-2026-09-27.html'
SEATS = REFERENCE / 'governance/smc-wardwise-seats-voters-2021.html'


def _raw(body: bytes, meta=None) -> Raw:
    return Raw(url='file://fixture', body=body, content_type='', fetch_id=0, sha256='', changed=True,
               retrieved_at='2026-01-01T00:00:00+05:30', meta=dict(meta or {}))


class TestCorporators(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.res = smc_council.parse(raw_from_file(CORP))
        cls.by = {r.record_key: r for r in cls.res.records}

    def test_counts_and_validation(self):
        self.assertEqual(len(self.res.records), 120)
        self.assertEqual({r.record_type for r in self.res.records}, {'corporator'})
        self.assertEqual(len({r.attrs['ward_no'] for r in self.res.records}), 30)
        self.assertEqual(self.res.complete_record_types, ('corporator',))
        self.assertEqual(self.res.observations, [])
        smc_council.validate(self.res, None)

    def test_values_read_off_the_page(self):
        # Ward No. 1 - Jahangirpura-Variyav-Chhaprabhatha-Kosad: first listed "MRS NAYNABEN SURESHBHAI DOBARIYA"
        self.assertEqual(self.by['ward-1-naynaben-sureshbhai-dobariya'].attrs, {
            'ward_no': '1', 'ward_name': 'Jahangirpura-Variyav-Chhaprabhatha-Kosad',
            'name': 'NAYNABEN SURESHBHAI DOBARIYA', 'honorific': 'MRS'})
        # Ward 5: "DR. VISHNUBHAI AMATHABHAI DESAI (VIKRAM)"
        r = self.by['ward-5-vishnubhai-amathabhai-desai-vikram']
        self.assertEqual((r.attrs['honorific'], r.attrs['name']), ('DR.', 'VISHNUBHAI AMATHABHAI DESAI (VIKRAM)'))
        # Ward 16: "ADVOCATE VIKRAMBHAI  DEGAMA" (double space collapsed)
        r = self.by['ward-16-vikrambhai-degama']
        self.assertEqual((r.attrs['honorific'], r.attrs['name'], r.attrs['ward_name']),
                         ('ADVOCATE', 'VIKRAMBHAI DEGAMA', 'Puna(West)'))
        # Ward 14 includes the Mayor, "MRS MAYABEN DHARMENDRABHAI MAVANI"
        self.assertIn('ward-14-mayaben-dharmendrabhai-mavani', self.by)
        # Ward 30, last listed: "MR CHIRAGKUMAR HARISHCHANDRA SOLANKI"
        self.assertEqual(self.by['ward-30-chiragkumar-harishchandra-solanki'].attrs['ward_name'],
                         'Kansad-Sachin-Unn-Aabhva')
        for ward in range(1, 31):
            self.assertEqual(sum(1 for r in self.res.records if r.attrs['ward_no'] == str(ward)), 4)

    def test_geos(self):
        wards = {g.geo_code: g for g in self.res.geos if g.geo_level == 'smc_ward'}
        self.assertEqual(sorted(wards, key=int), [str(n) for n in range(1, 31)])
        self.assertEqual((wards['14'].name, wards['14'].parent_level, wards['14'].parent_code),
                         ('Umarwada-Matawadi', 'smc_city', 'smc'))
        # canonical geo names equal the names printed on this snapshot
        for r in self.res.records:
            self.assertEqual(wards[r.attrs['ward_no']].name, r.attrs['ward_name'])

    def test_keys_survive_reordering(self):
        body = CORP.read_text(encoding='utf-8')
        # reverse the order of the <li> entries inside every ward block
        def rev(m):
            items = re.findall(r'(?s)<li>.*?</li>', m.group(2))
            return m.group(1) + ''.join(reversed(items)) + m.group(3)
        shuffled = re.sub(r'(?s)(<ul class="list-unstyled type1">)(.*?)(</ul>)', rev, body)
        self.assertNotEqual(shuffled, body)
        res2 = smc_council.parse(_raw(shuffled.encode()))
        self.assertEqual({r.record_key: r.attrs for r in res2.records}, {k: r.attrs for k, r in self.by.items()})

    def test_missing_ward_rejected(self):
        res = copy.deepcopy(self.res)
        res.records = [r for r in res.records if r.attrs['ward_no'] != '30']
        with self.assertRaises(ValidationError):
            smc_council.validate(res, None)

    def test_renamed_ward_rejected(self):
        res = copy.deepcopy(self.res)
        for r in res.records:
            if r.attrs['ward_no'] == '7':
                r.attrs['ward_name'] = 'Katargam'     # name of ward 6: numbering no longer matches
        with self.assertRaises(ValidationError):
            smc_council.validate(res, None)

    def test_normalize_blanks_row_tokens(self):
        body = CORP.read_bytes()
        n1 = smc_council.normalize(body)
        self.assertNotIn(b'CHqVYr_PZl0PsOMxIDhXWg', n1)
        self.assertEqual(n1.count(b'name="data" value=""'), 120)
        other = body.replace(b'CHqVYr_PZl0PsOMxIDhXWg', b'XXXXXXXXXXXXXXXXXXXXXX')
        self.assertEqual(smc_council.normalize(other), n1)
        # names still parse from the normalised (archived) body
        self.assertEqual(len(smc_council.parse(_raw(n1)).records), 120)


class TestOfficeBearers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.res = smc_council.parse(raw_from_file(OB))
        cls.by = {r.record_key: r for r in cls.res.records}

    def test_counts_and_validation(self):
        self.assertEqual(sorted(self.by), ['deputy-mayor', 'leader-ruling-party', 'mayor',
                                           'standing-committee-chairman'])
        self.assertEqual(self.res.complete_record_types, ('office_bearer',))
        smc_council.validate(self.res, None)

    def test_values_read_off_the_page(self):
        self.assertEqual(self.by['mayor'].attrs, {
            'designation': 'Mayor', 'name': 'Mayaben Dharmendrabhai Mavani', 'honorific': 'Smt.',
            'ward_name': 'Umarwada-Matawadi', 'ward_no': '14', 'email': 'mayor@suratmunicipal.org'})
        self.assertEqual(self.by['deputy-mayor'].attrs, {
            'designation': 'Deputy Mayor', 'name': 'Sudhakar Lotanbhai Chaudhari', 'honorific': 'Shri',
            'ward_name': 'Dindoli(South)', 'ward_no': '27'})
        self.assertEqual(self.by['standing-committee-chairman'].attrs['ward_no'], '9')
        self.assertEqual(self.by['leader-ruling-party'].attrs['name'], 'Alpa Jiteshbhai Mehta')

    def test_no_residential_address_or_mobile_stored(self):
        dumped = json.dumps([r.attrs for r in self.res.records])
        for leaked in ('Bhavani Nagar', 'Govardhan Nagar', 'Ambaji Chakla', 'Shrenikpark', '395006',
                       '9724345101', '9879043175', '9825534488', '9726276656'):
            self.assertNotIn(leaked, dumped)
        self.assertIsNone(re.search(r'\d{10}', dumped))

    def test_office_bearers_are_listed_corporators(self):
        corp = smc_council.parse(raw_from_file(CORP))
        names = {(r.attrs['ward_no'], r.attrs['name'].upper()) for r in corp.records}
        for r in self.res.records:
            self.assertIn((r.attrs['ward_no'], r.attrs['name'].upper()), names)

    def test_privacy_guard_in_validate(self):
        res = copy.deepcopy(self.res)
        res.records[1].attrs['name'] = 'Someone 9876543210'
        with self.assertRaises(ValidationError):
            smc_council.validate(res, None)
        res = copy.deepcopy(self.res)
        res.records[0].attrs['address'] = 'anything'
        with self.assertRaises(ValidationError):
            smc_council.validate(res, None)

    def test_non_official_email_dropped(self):
        self.assertIsNone(smc_council._official_email('someone[at]gmail[dot]com'))
        self.assertEqual(smc_council._official_email('mayor[at]suratmunicipal[dot]org'), 'mayor@suratmunicipal.org')


class TestWardwiseSeatsVoters2021(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.res = smc_council.parse(raw_from_file(SEATS))
        cls.by = {(o.metric_id, o.geo_level, o.geo_code, o.dims.get('gender'), o.dims.get('category'),
                   o.dims.get('women_reserved')): o for o in cls.res.observations}

    def v(self, metric, code, gender=None, category=None, women=None, level='smc_ward'):
        return self.by[(metric, level, code, gender, category, women)].value

    def test_counts_and_validation(self):
        # per ward: population, voters, 3 gender splits, 8 seat cells = 13; plus 5 published city totals
        self.assertEqual(len(self.res.observations), 30 * 13 + 5)
        self.assertEqual(self.res.records, [])
        self.assertTrue(all(o.status == 'reported' for o in self.res.observations))
        smc_council.validate(self.res, None)

    def test_values_read_off_the_page(self):
        # Ward 1 row: 138480 | O.B.C. | GENERAL | GENERAL | GENERAL | 69434 | 57096 | 7 | 126537
        self.assertEqual(self.v('election.ward_population', '1'), 138480)
        self.assertEqual(self.v('election.voters', '1'), 126537)
        self.assertEqual(self.v('election.voters_by_gender', '1', 'male'), 69434)
        self.assertEqual(self.v('election.voters_by_gender', '1', 'female'), 57096)
        self.assertEqual(self.v('election.voters_by_gender', '1', 'third_gender'), 7)
        self.assertEqual(self.v('election.seats', '1', category='obc', women='yes'), 1)
        self.assertEqual(self.v('election.seats', '1', category='general', women='yes'), 1)
        self.assertEqual(self.v('election.seats', '1', category='general', women='no'), 2)
        self.assertEqual(self.v('election.seats', '1', category='obc', women='no'), 0)
        # Ward 2 row: 139365 | S.C. | GENERAL | S.T. | GENERAL | 93049 | 80461 | 7 | 173517
        self.assertEqual(self.v('election.seats', '2', category='sc', women='yes'), 1)
        self.assertEqual(self.v('election.seats', '2', category='st', women='no'), 1)
        self.assertEqual(self.v('election.voters', '2'), 173517)
        # Ward 6 (Katargam): third gender voters printed as 0 -> a reported zero
        self.assertEqual(self.v('election.voters_by_gender', '6', 'third_gender'), 0)
        # Totals row: 4645384 | 1817203 | 1470855 | 115 | 3288173
        self.assertEqual(self.v('election.ward_population', 'smc', level='smc_city'), 4645384)
        self.assertEqual(self.v('election.voters', 'smc', level='smc_city'), 3288173)
        self.assertEqual(self.v('election.voters_by_gender', 'smc', 'third_gender', level='smc_city'), 115)
        # seats across the city: 120, 60 women-reserved, 2 SC, 5 ST, 12 OBC (as published in this table)
        seats = [o for o in self.res.observations if o.metric_id == 'election.seats']
        self.assertEqual(sum(o.value for o in seats), 120)
        self.assertEqual(sum(o.value for o in seats if o.dims['women_reserved'] == 'yes'), 60)
        by_cat = {c: sum(o.value for o in seats if o.dims['category'] == c) for c in smc_council.CATEGORIES}
        self.assertEqual(by_cat, {'general': 101, 'sc': 2, 'st': 5, 'obc': 12})

    def test_periods_and_geography(self):
        o = self.by[('election.voters', 'smc_ward', '1', None, None, None)]
        self.assertEqual((o.period_start, o.period_end, o.publisher_as_of),
                         ('2021-01-01', '2021-01-01', '2021-12-15T12:37'))
        o = self.by[('election.ward_population', 'smc_ward', '1', None, None, None)]
        self.assertEqual((o.period_start, o.period_end), ('2011-03-01', '2011-03-01'))
        self.assertEqual({(g.geo_level, g.geo_code) for g in self.res.geos} - {('smc_city', 'smc')},
                         {('smc_ward', str(n)) for n in range(1, 31)})

    def test_2021_ward_names_match_2026_numbering(self):
        # every 2021 ward name is a spelling of the same-numbered 2026 ward (basis for using smc_ward)
        from opencity.parse import html_tables
        t = html_tables(SEATS.read_bytes())[0]
        rows = [r for r in t.rows[1:] if r[0].strip()]
        self.assertEqual(len(rows), 30)
        for r in rows:
            self.assertTrue(smc_council.ward_name_matches(int(r[0].rstrip('.')), r[1]), r[:2])

    def test_mismatched_ward_name_fails_loudly(self):
        body = SEATS.read_bytes().replace(b'Katargam-Ved', b'Pandesara-Bhestan')
        with self.assertRaises(ValidationError):
            smc_council.parse(_raw(body))

    def test_gender_sum_mismatch_rejected(self):
        res = copy.deepcopy(self.res)
        for o in res.observations:
            if o.metric_id == 'election.voters' and o.geo_code == '3':
                o.value += 1
        with self.assertRaises(ValidationError):
            smc_council.validate(res, None)

    def test_blank_cell_is_not_reported(self):
        body = SEATS.read_text(encoding='utf-8')
        # blank ward 4's male voter cell (54510): it must become not_reported, never 0
        self.assertEqual(body.count('>54510<'), 1)
        res = smc_council.parse(_raw(body.replace('>54510<', '><').encode()))
        o = next(o for o in res.observations if o.metric_id == 'election.voters_by_gender'
                 and o.geo_code == '4' and o.dims['gender'] == 'male')
        self.assertEqual((o.value, o.status), (None, 'not_reported'))


class TestDispatch(unittest.TestCase):
    def test_unrecognised_page(self):
        with self.assertRaises(ValueError):
            smc_council.parse(_raw(b'<html><body><p>Service unavailable</p></body></html>'))

    def test_wrong_page_for_url(self):
        with self.assertRaises(ValueError):
            smc_council.parse(_raw(OB.read_bytes(), meta={'doc': 'corporators'}))


class TestOfficeBearersOctober2026Layout(unittest.TestCase):
    """SMC moved roles from <h2>/<h3> to <div class="panel-heading">/<div class="h3"> in October 2026.
    The fixture is the archived copy, with addresses and mobile numbers already blanked."""

    @classmethod
    def setUpClass(cls):
        from tests import FIXTURES
        cls.raw = raw_from_file(FIXTURES / 'smc_council/office-bearers-2026-10-18.html', meta={'doc': 'office_bearers'})
        cls.res = smc_council.parse(cls.raw)

    def test_same_four_roles_as_old_layout(self):
        self.assertEqual([r.record_key for r in self.res.records],
                         ['mayor', 'deputy-mayor', 'standing-committee-chairman', 'leader-ruling-party'])
        smc_council.validate(self.res, self.raw)

    def test_values(self):
        mayor = self.res.records[0].attrs
        self.assertEqual(mayor, {'designation': 'Mayor', 'name': 'Mayaben Dharmendrabhai Mavani', 'honorific': 'Smt.',
                                 'ward_name': 'Umarwada-Matawadi', 'ward_no': '14',
                                 'email': 'mayor@suratmunicipal.org'})
        self.assertEqual(self.res.records[3].attrs['name'], 'Alpa Jiteshbhai Mehta')

    def test_detected_without_meta(self):
        res = smc_council.parse(_raw(self.raw.body))
        self.assertEqual(len(res.records), 4)


if __name__ == '__main__':
    unittest.main()
