"""smc_water_quality against the frozen index page and page-1 crops of six monthly PDFs.

The fixtures in tests/fixtures/smc_water_quality/summary-YYYY-MM.pdf are the first page of SMC's monthly PDF
(.../Hydraulic/WaterQuality/YYYY/MM.pdf, downloaded 2026-10-05) cropped with `pdftocairo -pdf -W .. -H ..` to
just the zone summary table, so they carry none of the household addresses listed further down. The numeric
rows extract identically to the original PDFs (checked with pdftotext when the crops were made).
"""
import copy
import unittest

from tests import FIXTURES, REFERENCE, raw_from_file
from opencity.model import ValidationError
from opencity.sources import smc_water_quality as wq

PDF_URL = 'https://www.suratmunicipal.gov.in/Content/Documents/rtiact/Disclosure/Hydraulic/WaterQuality/{}/{}.pdf'


def month(ym, url_ym=None):
    y, m = (url_ym or ym).split('-')
    raw = raw_from_file(FIXTURES / f'smc_water_quality/summary-{ym}.pdf', url=PDF_URL.format(y, m),
                        retrieved_at='2026-10-05T00:00:00+05:30')
    return raw, wq.parse(raw)


def values(res):
    out = {}
    for o in res.observations:
        out.setdefault(o.geo_code, {})[o.metric_id.rsplit('_', 1)[1]] = o.value
    return out


class TestIndexPage(unittest.TestCase):
    def setUp(self):
        self.raw = raw_from_file(REFERENCE / 'health-environment/smc-water-quality-monitoring-2026-09-27.html',
                                 url=wq.URL)
        self.res = wq.parse(self.raw)

    def test_records(self):
        wq.validate(self.res, self.raw)
        docs = [r for r in self.res.records if r.record_type == 'document']
        tests = {r.record_key: r.attrs for r in self.res.records if r.record_type == 'wq_sampling_test'}
        self.assertEqual(len(docs), 215)            # Oct 2008 .. Aug 2026
        self.assertEqual(len(tests), 12)
        self.assertEqual(self.res.observations, [])
        self.assertEqual(set(self.res.complete_record_types), {'document', 'wq_sampling_test'})
        lab = tests['consumer-end-during-supply-chemical-test-lab-testing']
        self.assertEqual(lab['frequency'], 'Daily average 220 samples collected from all zones')
        d = {r.record_key: r.attrs for r in docs}
        self.assertEqual(d['smc-water-quality-monthly/2026-08']['url'], PDF_URL.format('2026', '08'))
        self.assertFalse(d['smc-water-quality-monthly/2008-10']['parsed'])
        self.assertFalse(d['smc-water-quality-monthly/2009-04']['parsed'])     # legacy font
        self.assertTrue(d['smc-water-quality-monthly/2009-05']['parsed'])


class TestMonthlyPdfs(unittest.TestCase):
    def test_2026_08_nine_zones(self):
        raw, res = month('2026-08')
        wq.validate(res, raw)
        v = values(res)
        self.assertEqual(len(res.observations), 30)
        self.assertEqual(v['north'], {'collected': 1937, 'fit': 1838, 'unfit': 99})
        self.assertEqual(v['south_b'], {'collected': 678, 'fit': 630, 'unfit': 48})
        self.assertEqual(v['smc'], {'collected': 11935, 'fit': 11553, 'unfit': 382})
        o = next(o for o in res.observations if o.geo_code == 'smc')
        self.assertEqual((o.geo_level, o.period_start, o.period_end), ('smc_city', '2026-08-01', '2026-08-31'))
        self.assertEqual(res.records, [])           # nothing from the address list, ever

    def test_2021_06_eight_zones(self):
        raw, res = month('2021-06')
        wq.validate(res, raw)
        v = values(res)
        self.assertEqual(len(v), 9)                 # 8 zones + total (total label has a stray control char)
        self.assertEqual(v['east_a']['collected'], 897)
        self.assertEqual(v['south'], {'collected': 1139, 'fit': 1089, 'unfit': 50})
        self.assertEqual(v['smc']['unfit'], 425)

    def test_2018_06_odd_glyphs(self):
        # West printed as "લેસ્ર્", Central as "વેન્્ર", South West as "વાઉથ લેસ્ર્"
        raw, res = month('2018-06')
        wq.validate(res, raw)
        v = values(res)
        self.assertEqual(v['west']['collected'], 1276)
        self.assertEqual(v['central']['collected'], 1435)
        self.assertEqual(v['south_west']['unfit'], 45)
        self.assertIn(('smc_zone', 'east'), {(g.geo_level, g.geo_code) for g in res.geos})

    def test_2013_01_publisher_arithmetic_kept_as_published(self):
        raw, res = month('2013-01')
        wq.validate(res, raw)                       # 545 != 524 + 22 is tolerated, not "fixed"
        self.assertEqual(values(res)['central'], {'collected': 545, 'fit': 524, 'unfit': 22})
        self.assertEqual(values(res)['smc']['fit'], 5881)

    def test_2011_06_dash_is_not_reported(self):
        raw, res = month('2011-06')
        wq.validate(res, raw)
        o = next(o for o in res.observations if o.geo_code == 'south' and o.metric_id == 'wq.tap_samples_unfit')
        self.assertEqual((o.status, o.value), ('not_reported', None))

    def test_2010_06(self):
        raw, res = month('2010-06')
        wq.validate(res, raw)
        self.assertEqual(values(res)['south_west'], {'collected': 1392, 'fit': 1337, 'unfit': 55})
        self.assertEqual(values(res)['smc']['collected'], 6078)

    def test_year_in_pdf_must_match_url(self):
        with self.assertRaises(ValidationError):
            month('2026-08', url_ym='2025-08')

    def test_validate_catches_misaligned_columns(self):
        raw, res = month('2026-08')
        bad = copy.deepcopy(res)
        for o in bad.observations:
            if o.geo_code == 'north' and o.metric_id == 'wq.tap_samples_fit':
                o.value = 99            # as if the unfit column had been read into the fit column
        with self.assertRaises(ValidationError):
            wq.validate(bad, raw)

    def test_zone_labels(self):
        cases = {'નોથ': 'north', 'નોથટ': 'north', 'ઈ ટ-એ': 'east_a', 'ઈ ટ-બી': 'east_b', 'ઈસ્ર્': 'east',
                 'વે ટ': 'west', 'લેસ્ર્': 'west', 'સે લ': 'central', 'સેન્્િ': 'central', 'વેન્્ર': 'central',
                 'સે ટ્ લ': 'central', 'સાઉથ વે ટ': 'south_west', 'સાઉથવે ટ': 'south_west',
                 'વાઉથ લેસ્ર્': 'south_west', 'સાઉથ': 'south', 'વાઉથ': 'south', 'સાઉથ-એ': 'south_a',
                 'સાઉથ-બી': 'south_b', 'સાઉથ ઈ ટ': 'south_east', 'ુલ': 'total', '\x11ુ લ': 'total',
                 'કુ િ': 'total', 'કુ ર': 'total', 'કુ ઱': 'total', 'કુ લ': 'total', 'કલ': 'total',
                 # Feb 2013 substitutes વ->ળ and સ->શ
                 'ળેસ્ર્': 'west', 'શેન્્઱': 'central', 'શાઉથ ળેસ્ર્': 'south_west', 'શાઉથ': 'south',
                 'શાઉથ ઈસ્ર્': 'south_east', 'લેસ્ટ': 'west', 'વેન્ટ્ર્ર': 'central',
                 'સે,-લ': 'central', 'ઈસ્ર્-ફી': 'east_b'}                          # Dec 2020, Sep 2019
        for label, code in cases.items():
            self.assertEqual(wq._zone(label), code, label)
        for bad in ('ઉધના', 'વેસ્ટઝોન', 'સાઉથ ઉધના'):
            with self.assertRaises(ValueError):
                wq._zone(bad)


# Summary table of .../WaterQuality/2014/12.pdf as pdftotext -layout prints it: North's "taken" value (૧૦૧૬)
# lands on a line of its own below the label row.
DEC_2014 = """                                                ભાસ : ડીસેમ્ફય - ૨૦૧૪
                        ઝોન               રેલામેરા નમુનાઓ               પીર્ નમુનાઓ            અનપીર્ નમુનાઓ

                        નોથટ                                                ૧૦૦૨                          ૧૪
                                                 ૧૦૧૬
                        ઈસ્ર્                     ૭૬૯                       ૭૬૨                           ૭
                        લેસ્ર્                    ૮૮૭                       ૮૮૦                           ૭
                       સેન્્ર                     ૮૭૭                       ૮૬૪                           ૧૩
                     સાઉથ લેસ્ર્                  ૮૮૭                       ૮૮૪                           ૩
                       સાઉથ                      ૧૦૫૧                       ૧૦૪૯                          ૨
                     સાઉથ ઈસ્ર્                   ૭૯૮                       ૭૯૩                           ૫

                        કુ ર                     ૬૨૮૫                       ૬૨૩૪                          ૫૧
"""


class TestLayoutRepairAndMonth(unittest.TestCase):
    def test_orphan_number_reattached_by_column(self):
        rows, year = wq.summary_rows(DEC_2014)
        self.assertEqual(year, 2014)
        by = {code: vals for _, code, vals in rows}
        self.assertEqual(by['north'], [1016, 1002, 14])
        self.assertEqual(by['total'], [6285, 6234, 51])
        self.assertEqual(len(rows), 8)

    def test_orphan_that_does_not_fit_fails(self):
        broken = DEC_2014.replace('                                                 ૧૦૧૬\n',
                                  '                                                                    ૧૦૧૬\n')
        with self.assertRaises(ValueError):          # lands in the already-filled 'fit' column
            wq.summary_rows(broken)

    def _parse_with_dates(self, dates, url_ym='2026-08'):
        """Real 2026-08 summary text + a synthetic unfit-sample list of dates only (no addresses)."""
        body = (FIXTURES / 'smc_water_quality/summary-2026-08.pdf').read_bytes()
        text = wq.pdf_text(body) + '\n        અનફીટ સેમ્પલની વિગત\n' + '\n'.join(f'   {d}   x' for d in dates)
        y, m = url_ym.split('-')
        raw = raw_from_file(FIXTURES / 'smc_water_quality/summary-2026-08.pdf', url=PDF_URL.format(y, m),
                            retrieved_at='2026-10-05T00:00:00+05:30')
        real = wq.pdf_text
        wq.pdf_text = lambda *_a, **_k: text
        try:
            return wq.parse(raw)
        finally:
            wq.pdf_text = real

    def test_document_filed_under_its_sample_dates(self):
        # like 2019/09.pdf (dates and heading say November): the document's own month wins over the link
        with self.assertLogs('opencity.sources.smc_water_quality', 'WARNING'):
            res = self._parse_with_dates(['૦૩-૦૭-૨૦૨૬'] * 6 + ['૧૫/૦૭/૨૦૨૬'] * 4)
        self.assertEqual({o.period_start for o in res.observations}, {'2026-07-01'})
        res = self._parse_with_dates(['૦૩-૦૮-૨૦૨૬'] * 6)
        self.assertEqual({o.period_start for o in res.observations}, {'2026-08-01'})

    def test_few_dates_fall_back_to_url_and_mixed_dates_fail(self):
        res = self._parse_with_dates(['૦૩-૦૭-૨૦૨૬'] * 3)
        self.assertEqual({o.period_start for o in res.observations}, {'2026-08-01'})
        with self.assertRaises(ValidationError):
            self._parse_with_dates(['૦૩-૦૭-૨૦૨૬'] * 5 + ['૦૩-૦૮-૨૦૨૬'] * 5)
        with self.assertRaises(ValidationError):    # heading says 2026, dates say 2025
            self._parse_with_dates(['૦૩-૦૭-૨૦૨૫'] * 6)

    def test_unreadable_months_are_listed_not_fetched(self):
        raw = raw_from_file(REFERENCE / 'health-environment/smc-water-quality-monitoring-2026-09-27.html', url=wq.URL)
        d = {r.record_key: r.attrs for r in wq.parse(raw).records}
        self.assertFalse(d['smc-water-quality-monthly/2015-10']['parsed'])
        self.assertIn('truncated', d['smc-water-quality-monthly/2015-10']['not_parsed_because'])
        self.assertIn((2011, 4), wq.UNREADABLE)


if __name__ == '__main__':
    unittest.main()
