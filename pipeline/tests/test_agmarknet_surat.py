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

    def test_fetch_requests_last_ten_days_for_surat_district_only(self):
        calls = []

        class Ctx:
            now = datetime(2026, 10, 4, 9, 0)

            def post(self, url, *, json=None, meta=None, skip_if_seen=False, headers=None, form=None):
                calls.append((url, json, meta, skip_if_seen, headers))

        list(agm.fetch(Ctx()))
        self.assertEqual(len(calls), 10)
        self.assertEqual([c[2]['date'] for c in calls][:2], ['2026-10-04', '2026-10-03'])
        self.assertEqual(calls[-1][2]['date'], '2026-09-25')
        for url, body, meta, skip, headers in calls:
            self.assertEqual(url, agm.URL)
            self.assertEqual(body['date'], meta['date'])
            self.assertEqual(body['stateIds'], [11])
            self.assertFalse(set(body['marketIds']) & set(agm.TAPI_MARKETS))
            self.assertEqual(len(body['marketIds']), 21)
            self.assertFalse(skip)
            self.assertIsNone(headers)              # no Origin/Referer or browser headers


if __name__ == '__main__':
    unittest.main()
