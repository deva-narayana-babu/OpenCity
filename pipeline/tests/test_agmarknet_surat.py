import copy
import json
import unittest
from datetime import datetime

from tests import REFERENCE, raw_from_file
from opencity.model import Raw, ValidationError
from opencity.sources import agmarknet_surat as agm

DAILY = REFERENCE / 'food-prices/india-agmarknet-daily-2026-08-28-to-2026-09-26'
FETCHED = '2026-09-27T12:52:00+05:30'      # the frozen responses were fetched on 27 Sep 2026


def load(day: str) -> Raw:
    raw = raw_from_file(DAILY / f'Surat_{day}.json', meta={'date': day})
    raw.retrieved_at = FETCHED
    return raw


def raw_doc(doc: dict, day: str | None = None) -> Raw:
    return Raw(url='file://synthetic', body=json.dumps(doc).encode(), content_type='application/json',
               fetch_id=0, sha256='', changed=True, retrieved_at=FETCHED, meta={'date': day} if day else {})


class TestAgmarknetSurat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.days = sorted(p.stem.split('_', 1)[1] for p in DAILY.glob('Surat_*.json'))
        cls.results = {}
        cls.by = {}
        for d in cls.days:
            raw = load(d)
            res = agm.parse(raw)
            agm.validate(res, raw)
            cls.results[d] = res
            for o in res.observations:
                k = (o.metric_id, o.geo_code, o.period_start, tuple(sorted(o.dims.items())))
                assert k not in cls.by, k
                cls.by[k] = o

    def test_counts(self):
        self.assertEqual(len(self.days), 30)
        self.assertEqual(sum(len(r.observations) for r in self.results.values()), 4234)
        # Surat_2026-09-01.json, Surat-district markets: price lines Surat APMC 39, Bardoli(Kadod) 4,
        # Mahuva(Anaval) 1, Mandvi 1 = 45; NIL entries from Bardoli, Bardoli(Madhi), Mahuva, Mandvi(Amba Paradi);
        # Kosamba and its two sub-yards and S.Mandvi are listed with empty commodity lists
        obs = self.results['2026-09-01'].observations
        self.assertEqual(sum(1 for o in obs if o.metric_id == agm.M_ARRIVALS), 45)
        status = sorted((o.geo_code, o.status) for o in obs if o.metric_id == agm.M_MARKET)
        self.assertEqual(status, [('1546', 'not_reported'), ('1686', 'reported'), ('2580', 'not_reported'),
                                  ('2622', 'reported'), ('2623', 'reported'), ('2816', 'not_reported'),
                                  ('64', 'reported'), ('785', 'not_reported')])
        self.assertEqual(len(obs), 45 * 4 + 8)

    def test_surat_apmc_reported_23_of_30_days(self):
        # per the README of the frozen set: Surat APMC had price rows on 23 of 30 days
        rep = sorted(d for d in self.days if (agm.M_MARKET, '64', d, ()) in self.by)
        self.assertEqual(len(rep), 23)
        missing = sorted(set(self.days) - set(rep))
        self.assertEqual(missing, ['2026-08-28', '2026-08-30', '2026-09-04', '2026-09-06',
                                   '2026-09-13', '2026-09-20', '2026-09-25'])
        for d in rep:
            self.assertEqual(self.by[(agm.M_MARKET, '64', d, ())].status, 'reported')

    def test_values_read_off_the_documents(self):
        b = self.by
        # Surat_2026-09-15.json, Surat APMC (64): Potato Other/FAQ 640 t, Rs 600 / 1750 / 1175 per quintal
        k = ('64', '2026-09-15', (('commodity', 'Potato'), ('grade', 'FAQ'), ('variety', 'Other')))
        self.assertEqual(b[(agm.M_ARRIVALS, *k)].value, 640)
        self.assertEqual(b[(agm.M_MIN, *k)].value, 600)
        self.assertEqual(b[(agm.M_MAX, *k)].value, 1750)
        self.assertEqual(b[(agm.M_MODAL, *k)].value, 1175)
        # Onion Other/FAQ 185 t, modal 3900; Ginger(Green) "Green Ginger"/FAQ modal 10500
        k = ('64', '2026-09-15', (('commodity', 'Onion'), ('grade', 'FAQ'), ('variety', 'Other')))
        self.assertEqual(b[(agm.M_ARRIVALS, *k)].value, 185)
        self.assertEqual(b[(agm.M_MODAL, *k)].value, 3900)
        k = ('64', '2026-09-15', (('commodity', 'Ginger(Green)'), ('grade', 'FAQ'), ('variety', 'Green Ginger')))
        self.assertEqual(b[(agm.M_MODAL, *k)].value, 10500)
        # the published name carries a trailing newline: "Spiny Gourd / Kartali(Kantola)\n"
        k = ('64', '2026-09-15', (('commodity', 'Spiny Gourd / Kartali(Kantola)'), ('grade', 'FAQ'),
                                  ('variety', 'Other')))
        self.assertEqual(b[(agm.M_ARRIVALS, *k)].value, 14)
        self.assertEqual(b[(agm.M_MODAL, *k)].value, 8000)
        self.assertEqual(b[(agm.M_MARKET, '64', '2026-09-15', ())].value, 39)
        # Surat_2026-09-01.json, Bardoli(Kadod) (2623): Bhindi(Ladies Finger) Other/Local 0.6 t, 2300/4200/2800
        k = ('2623', '2026-09-01', (('commodity', 'Bhindi(Ladies Finger)'), ('grade', 'Local'), ('variety', 'Other')))
        self.assertAlmostEqual(b[(agm.M_ARRIVALS, *k)].value, 0.6)    # published as 0.6000000000000001
        self.assertEqual(b[(agm.M_MIN, *k)].value, 2300)
        self.assertEqual(b[(agm.M_MAX, *k)].value, 4200)
        self.assertEqual(b[(agm.M_MODAL, *k)].value, 2800)
        self.assertEqual(b[(agm.M_MARKET, '2623', '2026-09-01', ())].value, 4)
        # Mandvi APMC (1686): Paddy(Common) Other/Non-FAQ 1.18 t, 1950/2000/1975
        k = ('1686', '2026-09-01', (('commodity', 'Paddy(Common)'), ('grade', 'Non-FAQ'), ('variety', 'Other')))
        self.assertAlmostEqual(b[(agm.M_ARRIVALS, *k)].value, 1.18)
        self.assertEqual(b[(agm.M_MODAL, *k)].value, 1975)

    def test_nil_transactions_are_not_reported_never_zero(self):
        o = self.by[(agm.M_MARKET, '785', '2026-09-01', ())]          # Bardoli APMC
        self.assertEqual((o.status, o.value, o.value_text), ('not_reported', None, 'NIL Transaction - No Arrivals'))
        o = self.by[(agm.M_MARKET, '1547', '2026-08-30', ())]         # Kosamba APMC
        self.assertEqual((o.status, o.value, o.value_text), ('not_reported', None, 'NIL Transaction - Public Holiday'))
        o = self.by[(agm.M_MARKET, '2580', '2026-08-30', ())]         # Mandvi(Amba Paradi)
        self.assertEqual(o.value_text, 'NIL Transaction - Weekend Holiday')
        # a NIL market emits nothing but the status row
        self.assertFalse([x for x in self.results['2026-09-01'].observations
                          if x.geo_code == '785' and x.metric_id != agm.M_MARKET])
        # empty commodity list (Surat APMC on 2026-08-30) -> nothing stored at all
        self.assertFalse([x for x in self.results['2026-08-30'].observations if x.geo_code == '64'])
        for r in self.results.values():
            for x in r.observations:
                if x.value is not None:
                    self.assertGreater(x.value, 0)

    def test_tapi_district_markets_excluded(self):
        codes = {o.geo_code for r in self.results.values() for o in r.observations}
        self.assertFalse(codes & {str(m) for m in agm.TAPI_MARKETS})
        # Songadh APMC (1559, Tapi district) did report on 2026-09-25 and is still left out
        self.assertNotIn('1559', {o.geo_code for o in self.results['2026-09-25'].observations})
        self.assertEqual(codes, {'64', '785', '1546', '1547', '1686', '2580', '2622', '2623', '2793', '2794', '2816'})

    def test_geography_periods_and_units(self):
        res = self.results['2026-09-15']
        geos = {g.geo_code: g for g in res.geos}
        self.assertEqual(len(geos), 21)
        g = geos['64']
        self.assertEqual((g.geo_level, g.name, g.parent_level, g.parent_code),
                         ('apmc_market', 'Surat APMC', 'surat_district', 'surat'))
        self.assertIn('Inside SMC limits', g.note)
        self.assertNotIn('Inside SMC limits', geos['785'].note)
        for o in res.observations:
            self.assertEqual((o.geo_level, o.period_start, o.period_end), ('apmc_market', '2026-09-15', '2026-09-15'))
        units = {m.id: m.unit for m in agm.SOURCE.metrics}
        self.assertEqual(units[agm.M_ARRIVALS], 'tonnes')
        self.assertEqual(units[agm.M_MODAL], 'Rs/quintal')

    # ---------- synthetic edge cases built from a real response ----------

    def _doc(self, day='2026-09-15'):
        return json.loads((DAILY / f'Surat_{day}.json').read_bytes())

    def _surat_lines(self, doc):
        m = next(m for s in doc['states'] for m in s['markets'] if m['marketId'] == 64)
        return [r for c in m['commodities'] for r in c['data']]

    def test_published_zero_is_not_reported(self):
        doc = self._doc()
        self._surat_lines(doc)[0]['arrivals'] = 0.0
        self._surat_lines(doc)[0]['modalPrice'] = None
        res = agm.parse(raw_doc(doc, '2026-09-15'))
        o = next(o for o in res.observations if o.metric_id == agm.M_ARRIVALS and o.dims['commodity'] == 'Banana - Green')
        self.assertEqual((o.status, o.value, o.value_text), ('not_reported', None, 'published as 0'))
        o = next(o for o in res.observations if o.metric_id == agm.M_MODAL and o.dims['commodity'] == 'Banana - Green')
        self.assertEqual((o.status, o.value), ('not_reported', None))

    def test_unknown_unit_fails_loudly(self):
        doc = self._doc()
        self._surat_lines(doc)[0]['unitOfPrice'] = 'Rs./Kg'
        with self.assertRaises(ValueError):
            agm.parse(raw_doc(doc))

    def test_wrong_date_and_failed_response_rejected(self):
        with self.assertRaises(ValidationError):
            agm.parse(raw_doc(self._doc(), '2026-09-16'))
        with self.assertRaises(ValidationError):
            agm.parse(raw_doc({'success': False, 'message': 'error'}))

    def test_validate_catches_swapped_columns_and_future_dates(self):
        doc = self._doc()
        for r in self._surat_lines(doc):
            r['minimumPrice'], r['maximumPrice'] = r['maximumPrice'], r['minimumPrice']
        raw = raw_doc(doc)
        with self.assertRaises(ValidationError):
            agm.validate(agm.parse(raw), raw)
        raw = raw_doc(self._doc())
        raw.retrieved_at = '2026-09-10T10:00:00+05:30'
        with self.assertRaises(ValidationError):
            agm.validate(agm.parse(raw), raw)

    def test_unexpected_market_rejected(self):
        doc = self._doc()
        extra = copy.deepcopy(doc['states'][0]['markets'][0])
        extra['marketId'] = 66                       # Ahmedabad APMC
        doc['states'][0]['markets'].append(extra)
        with self.assertRaises(ValidationError):
            agm.parse(raw_doc(doc))

    def test_old_endpoint_is_no_longer_called_without_a_key(self):
        calls = []

        class Ctx:
            log = __import__('logging').getLogger('test')

            def get(self, *a, **k):
                calls.append(a)

            def post(self, *a, **k):
                calls.append(a)

        old = agm.API_KEY
        try:
            agm.API_KEY = ''
            self.assertEqual(list(agm.fetch(Ctx())), [])
        finally:
            agm.API_KEY = old
        self.assertEqual(calls, [])


class TestDataGovIn(unittest.TestCase):
    """The data.gov.in copy of the prices. SAMPLE follows the documented record layout; it is synthetic
    (no live response has been seen yet), so replace it with a real saved response when one is available."""

    SAMPLE = {
        'total': 5, 'count': 5,
        'records': [
            {'state': 'Gujarat', 'district': 'Surat', 'market': 'Surat', 'commodity': 'Onion', 'variety': 'Red',
             'grade': 'FAQ', 'arrival_date': '17/10/2026', 'min_price': '1200', 'max_price': '2000',
             'modal_price': '1600'},
            {'state': 'Gujarat', 'district': 'Surat', 'market': 'Bardoli(Kadod)', 'commodity': 'Bhindi(Ladies Finger)',
             'variety': 'Other', 'grade': 'Local', 'arrival_date': '17/10/2026', 'min_price': '2100',
             'max_price': '4200', 'modal_price': '0'},
            {'state': 'Gujarat', 'district': 'Surat', 'market': 'Vyra', 'commodity': 'Onion', 'variety': 'Red',
             'grade': 'FAQ', 'arrival_date': '17/10/2026', 'min_price': '1000', 'max_price': '1500',
             'modal_price': '1200'},
            {'state': 'Gujarat', 'district': 'Ahmedabad', 'market': 'Ahmedabad', 'commodity': 'Onion',
             'variety': 'Red', 'grade': 'FAQ', 'arrival_date': '17/10/2026', 'min_price': '1300',
             'max_price': '2100', 'modal_price': '1700'},
            {'State': 'Gujarat', 'District': 'Surat', 'Market': 'Surat', 'Commodity': 'Potato', 'Variety': 'Other',
             'Grade': 'FAQ', 'Arrival_Date': '16/10/2026', 'Min_x0020_Price': '900', 'Max_x0020_Price': '1300',
             'Modal_x0020_Price': '1100'},
        ],
    }

    def parse(self, doc=None):
        raw = raw_doc(doc or self.SAMPLE)
        raw.retrieved_at = '2026-10-18T10:00:00+05:30'
        res = agm.parse(raw)
        agm.validate(res, raw)
        return res

    def test_surat_rows_only_and_values(self):
        res = self.parse()
        by = {(o.metric_id, o.geo_code, o.period_start, o.dims.get('commodity')): o for o in res.observations}
        self.assertEqual(by[(agm.M_MODAL, '64', '2026-10-17', 'Onion')].value, 1600)
        self.assertEqual(by[(agm.M_MIN, '2623', '2026-10-17', 'Bhindi(Ladies Finger)')].value, 2100)
        self.assertEqual(by[(agm.M_MODAL, '2623', '2026-10-17', 'Bhindi(Ladies Finger)')].status, 'not_reported')
        self.assertEqual(by[(agm.M_MAX, '64', '2026-10-16', 'Potato')].value, 1300)       # "_x0020_" key spelling
        codes = {o.geo_code for o in res.observations}
        self.assertEqual(codes, {'64', '2623'})          # Tapi (Vyra) and Ahmedabad rows are dropped
        self.assertFalse(any(o.metric_id == agm.M_ARRIVALS for o in res.observations))

    def test_price_lines_counted_per_market_and_day(self):
        res = self.parse()
        counts = {(o.geo_code, o.period_start): o.value for o in res.observations if o.metric_id == agm.M_MARKET}
        self.assertEqual(counts, {('64', '2026-10-16'): 1, ('64', '2026-10-17'): 1, ('2623', '2026-10-17'): 1})

    def test_unknown_market_and_conflicting_repeats_rejected(self):
        doc = copy.deepcopy(self.SAMPLE)
        doc['records'][0]['market'] = 'Nowhere'
        with self.assertRaises(ValidationError):
            self.parse(doc)
        doc = copy.deepcopy(self.SAMPLE)
        doc['records'].append(dict(doc['records'][0], modal_price='1700'))
        with self.assertRaises(ValidationError):
            self.parse(doc)
        doc = copy.deepcopy(self.SAMPLE)
        doc['records'].append(dict(doc['records'][0]))          # an exact repeat is read once
        self.assertEqual(len(self.parse(doc).observations), len(self.parse().observations))

    def test_fetch_uses_the_official_api_with_plain_get(self):
        calls = []
        sample = self.SAMPLE

        class Ctx:
            log = __import__('logging').getLogger('test')

            def get(self, url, params=None, headers=None, **k):
                calls.append((url, params, headers))
                return raw_doc(sample)

            def post(self, *a, **k):
                raise AssertionError('the captcha-protected endpoint must not be called')

        old = agm.API_KEY
        try:
            agm.API_KEY = 'TESTKEY'
            docs = list(agm.fetch(Ctx()))
        finally:
            agm.API_KEY = old
        self.assertEqual(len(docs), 1)                   # total 5 fits in one page
        url, params, headers = calls[0]
        self.assertEqual(url, agm.OGD_URL)
        self.assertEqual(params['api-key'], 'TESTKEY')
        self.assertEqual(params['filters[state.keyword]'], 'Gujarat')
        self.assertEqual((params['format'], params['offset']), ('json', 0))
        self.assertIsNone(headers)                       # no browser or Origin/Referer headers

if __name__ == '__main__':
    unittest.main()
