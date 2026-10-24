import unittest

from tests import FIXTURES, raw_from_file
from opencity.model import ValidationError
from opencity.sources import ndma_sachet_surat as s

DIR = FIXTURES / 'ndma_sachet_surat'
RSS = DIR / 'rss_india-2026-10-24T0206-trimmed.xml'          # 4 of the 100 items fetched 2026-10-24 02:06 IST
MAHARASHTRA = DIR / 'cap-1792759763404029-maharashtra.xml'
KERALA = DIR / 'cap-1792774397538006-kerala.xml'
CWC = DIR / 'cap-1792730555445016-cwc-bihar.xml'
FETCHED = '2026-10-24T02:10:00+05:30'


def raw(path, body=None, meta=None):
    r = raw_from_file(path, retrieved_at=FETCHED, meta=meta)
    if body is not None:
        r.body = body
    return r


class TestRss(unittest.TestCase):
    def test_items_and_prefilter(self):
        items = s.rss_items(RSS.read_bytes())
        self.assertEqual(len(items), 4)
        cwc = [i for i in items if i['guid'] == '1792730555445016'][0]
        self.assertEqual(cwc['agency'], 'CWC')
        self.assertTrue(cwc['title'].startswith('River Gandak at Dumariaghat'))
        # the real feed had no Gujarat alert: nothing is opened
        self.assertEqual([i for i in items if s.might_cover_surat(i)], [])
        self.assertEqual(s.parse(raw(RSS)).observations, [])
        s.validate(s.parse(raw(RSS)), raw(RSS))

    def test_prefilter_rules(self):
        base = {'guid': '1', 'link': '', 'agency': 'IMD Chennai', 'title': 'Rain likely over Chennai'}
        self.assertFalse(s.might_cover_surat(base))
        self.assertTrue(s.might_cover_surat(dict(base, agency='IMD Ahmedabad')))
        self.assertTrue(s.might_cover_surat(dict(base, agency='Gujarat SDMA')))
        self.assertTrue(s.might_cover_surat(dict(base, agency='CWC', title='River Tapi at Surat in Surat district')))
        self.assertTrue(s.might_cover_surat(dict(base, title='સુરત જિલ્લામાં વરસાદ')))
        self.assertFalse(s.might_cover_surat(dict(base, agency='CWC', title='River Ghaggar at Suratgarh, Rajasthan')))


class TestCap(unittest.TestCase):
    def test_fields_read_off_the_maharashtra_alert(self):
        a = s.read_cap(MAHARASHTRA.read_bytes())
        self.assertEqual(a['alert_id'], '1792759763404029')
        self.assertEqual(a['identifier'], 'IN-1792759763404029_29')
        self.assertEqual((a['sender'], a['msg_type'], a['status']), ('Maharashtra-SDMA', 'Update', 'Actual'))
        self.assertEqual(a['references'], 'IMD-Mumbai,IN-1792759763404029_46,2026-10-23T18:18:56+05:30')
        self.assertEqual((a['event'], a['severity'], a['urgency'], a['certainty']),
                         ('Moderate Thunderstorms', 'Severe', 'Expected', 'Likely'))
        self.assertEqual((a['sent'], a['effective'], a['expires']),
                         ('2026-10-23T18:52', '2026-10-23T18:00', '2026-10-23T21:00'))
        self.assertEqual(a['area_desc'], 'Sindhudurg district of Maharashtra')
        self.assertEqual(a['lgd_district_codes'], ['495'])
        self.assertEqual((a['language'], a['language_local']), ('en-IN', 'MR'))
        self.assertTrue(a['headline'].endswith('over Sindhudurg in next 3 hours.'))
        self.assertNotIn('contact', a)

    def test_alerts_elsewhere_are_not_stored(self):
        for path in (MAHARASHTRA, KERALA, CWC):
            res = s.parse(raw(path))
            self.assertEqual((res.records, res.observations), ([], []), path.name)
        self.assertEqual(s.read_cap(KERALA.read_bytes())['lgd_district_codes'], ['561', '562', '558', '557'])
        cwc = s.read_cap(CWC.read_bytes())
        self.assertEqual((cwc['area_desc'], cwc['lgd_district_codes']), ('Gandak, Dumariaghat, Gopalganj, Bihar', []))

    # The fixtures hold no Surat alert (none was in the feed). The tests below edit a real alert in memory to
    # check the matching rules; the edited copies are never saved as fixtures.
    def test_surat_by_lgd_code(self):
        body = KERALA.read_bytes().replace(b'<cap:value>558</cap:value>', b'<cap:value>459</cap:value>')
        r = raw(KERALA, body, meta={'alert_id': '1792774397538006'})
        res = s.parse(r)
        s.validate(res, r)
        (rec,) = res.records
        self.assertEqual((rec.record_type, rec.record_key), ('cap_alert', '1792774397538006'))
        self.assertEqual(rec.attrs['sender'], 'Kerala-SDMA')
        self.assertEqual(rec.attrs['expires'], '2026-10-24T01:21')
        self.assertEqual(rec.attrs['cap_url'],
                         'https://sachet.ndma.gov.in/cap_public_website/FetchXMLFile?identifier=1792774397538006')
        (o,) = res.observations
        self.assertEqual((o.metric_id, o.geo_level, o.geo_code, o.period_start, o.period_end, o.value),
                         ('sachet.alerts', 'surat_district', 'surat', '2026-10-23', '2026-10-23', 1))
        self.assertEqual(o.dims, {'alert': '1792774397538006', 'severity': 'severe'})

    def test_surat_by_area_name(self):
        body = CWC.read_bytes().replace(b'Gandak, Dumariaghat, Gopalganj, Bihar', b'Tapi, Surat, Surat, Gujarat')
        self.assertEqual(len(s.parse(raw(CWC, body)).records), 1)
        body = CWC.read_bytes().replace(b'Gandak, Dumariaghat, Gopalganj, Bihar', b'Ghaggar, Suratgarh, Rajasthan')
        self.assertEqual(s.parse(raw(CWC, body)).records, [])

    def test_cancel_and_exercise(self):
        surat = KERALA.read_bytes().replace(b'<cap:value>558</cap:value>', b'<cap:value>459</cap:value>')
        res = s.parse(raw(KERALA, surat.replace(b'<cap:msgType>Update</cap:msgType>', b'<cap:msgType>Cancel</cap:msgType>')))
        self.assertEqual((len(res.records), res.observations), (1, []))
        res = s.parse(raw(KERALA, surat.replace(b'<cap:status>Actual</cap:status>', b'<cap:status>Exercise</cap:status>')))
        self.assertEqual(res.records, [])

    def test_validate_rejects_wrong_document(self):
        surat = KERALA.read_bytes().replace(b'<cap:value>558</cap:value>', b'<cap:value>459</cap:value>')
        r = raw(KERALA, surat, meta={'alert_id': '1792759763404029'})
        with self.assertRaises(ValidationError):
            s.validate(s.parse(r), r)


if __name__ == '__main__':
    unittest.main()
