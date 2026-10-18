"""fca_prices is disabled because fcainfoweb price reports need a captcha. No real report page has been obtained.

- The frozen fixture is the real "Daily Prices" report form (fetched 2026-10-18, tokens blanked by
  archive.normalize), and parse() must refuse it.
- The centre spelling is checked against the frozen DoCA centre list in reference/.
- The table logic is tested on a SYNTHETIC page built below. Its layout is a guess, and its numbers are
  placeholders, not DoCA data.
"""
import logging
import unittest

from tests import FIXTURES, REFERENCE, raw_from_file
from opencity.model import Raw, ValidationError
from opencity.parse import html_tables
from opencity.sources import fca_prices

FORM = FIXTURES / 'fca_prices/report-menu-daily-prices-captcha-2026-10-18.html'
CENTRES = REFERENCE / 'food-prices/india-doca-price-reporting-centres-2026-09-27.html'

# SYNTHETIC test input, NOT DoCA data: the layout is a guess, and the numbers are placeholders (10, 11, 12, ...).
COLUMNS = ['Rice', 'Wheat', 'Atta (Wheat)', 'Gram Dal', 'Tur/Arhar Dal', 'Urad Dal', 'Moong Dal', 'Masoor Dal',
           'Sugar', 'Milk @', 'Groundnut Oil (Packed)', 'Mustard Oil (Packed)', 'Vanaspati (Packed)',
           'Soya Oil (Packed)', 'Sunflower Oil (Packed)', 'Palm Oil (Packed)', 'Gur', 'Tea Loose',
           'Salt Pack (Iodised)', 'Potato', 'Onion', 'Tomato', 'Eggs']


def synthetic(title, surat_cells):
    head = ''.join(f'<th>{c}</th>' for c in ['Sr No.', 'Centre'] + COLUMNS)
    other = '<td>500</td>' * len(COLUMNS)
    surat = ''.join(f'<td>{c}</td>' for c in surat_cells)
    page = (f'<html><body><h3>{title}</h3><p>Date : 17/10/2026</p><table><tr>{head}</tr>'
            f'<tr><td>1</td><td>Ahmedabad</td>{other}</tr><tr><td>2</td><td>Surat</td>{surat}</tr>'
            f'</table></body></html>')
    return Raw(url='file://synthetic', body=page.encode(), content_type='text/html', fetch_id=0, sha256='',
               changed=True, retrieved_at='2026-10-18T10:00:00+05:30')


def placeholder_cells():
    cells = [str(10 + i) for i in range(len(COLUMNS))]
    cells[1], cells[3], cells[21] = '', '-', '0'      # Wheat blank, Gram Dal '-', Tomato published as 0
    return cells


class StubCtx:
    log = logging.getLogger('test')

    def get(self, *a, **k):
        raise AssertionError('fca_prices must not fetch')

    post = get


class TestFcaPrices(unittest.TestCase):
    def test_disabled_and_fetch_requests_nothing(self):
        self.assertFalse(fca_prices.SOURCE.enabled)
        self.assertIn('captcha', fca_prices.SOURCE.notes)
        with self.assertLogs('test', 'WARNING'):
            self.assertEqual(list(fca_prices.fetch(StubCtx())), [])

    def test_real_report_form_has_a_captcha_and_is_refused(self):
        raw = raw_from_file(FORM)
        self.assertIn(b'../CaptchaImage.aspx', raw.body)
        self.assertIn(b'value="Get Data"', raw.body)
        self.assertIn(b'<option selected="selected" value="Daily Prices">', raw.body)
        with self.assertRaisesRegex(ValueError, 'captcha'):
            fca_prices.parse(raw)

    def test_centre_spelling_matches_doca_list(self):
        rows = [r for t in html_tables(CENTRES.read_bytes()) for r in t.rows]
        self.assertIn(['17', 'Surat'], rows)            # West Zone list, centre 17
        self.assertEqual([r[1] for r in rows if 'surat' in r[1].lower()], [fca_prices.CENTRE_NAME])

    def test_synthetic_retail_report(self):
        raw = synthetic('Daily Retail Prices Of Essential Commodities', placeholder_cells())
        res = fca_prices.parse(raw)
        fca_prices.validate(res, raw)
        by = {o.dims['commodity']: o for o in res.observations}
        self.assertEqual(len(res.observations), 22)      # 23 columns; Eggs skipped (unit not stated)
        self.assertNotIn('Eggs', by)
        o = by['Rice']
        self.assertEqual((o.metric_id, o.geo_level, o.geo_code, o.period_start, o.period_end, o.value),
                         ('fca.retail_price', 'reporting_centre', 'surat', '2026-10-17', '2026-10-17', 10.0))
        self.assertEqual(by['Milk'].value, 19.0)          # header "Milk @"
        self.assertEqual(by['Salt Pack (Iodised)'].value, 28.0)
        for name in ('Wheat', 'Gram Dal'):
            self.assertEqual((by[name].status, by[name].value), ('not_reported', None))
        self.assertEqual((by['Tomato'].status, by['Tomato'].value, by['Tomato'].value_text),
                         ('not_reported', None, 'published as 0'))
        self.assertNotIn(500.0, [o.value for o in res.observations])   # the Ahmedabad row is not read
        self.assertEqual([(g.geo_level, g.geo_code) for g in res.geos], [('reporting_centre', 'surat')])

    def test_validate_catches_unit_or_type_mixups(self):
        # retail-scale numbers under a wholesale (Rs/quintal) heading
        raw = synthetic('Daily Wholesale Prices Of Essential Commodities', placeholder_cells())
        res = fca_prices.parse(raw)
        self.assertEqual(res.observations[0].metric_id, 'fca.wholesale_price')
        with self.assertRaises(ValidationError):
            fca_prices.validate(res, raw)
        # quintal-scale numbers under a retail (Rs/kg) heading
        raw = synthetic('Daily Retail Prices Of Essential Commodities', [str(4000 + i) for i in range(len(COLUMNS))])
        with self.assertRaises(ValidationError):
            fca_prices.validate(fca_prices.parse(raw), raw)

    def test_page_without_report_type_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'retail'):
            fca_prices.parse(synthetic('Essential Commodities', placeholder_cells()))


if __name__ == '__main__':
    unittest.main()
