import unittest

from tests import FIXTURES, raw_from_file
from opencity.model import ValidationError
from opencity.sources import smc_zone_offices

FIXTURE = FIXTURES / 'smc_zone_offices/zone-officials-2026-10-24.html'


class TestSmcZoneOffices(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = raw_from_file(FIXTURE, retrieved_at='2026-10-24T02:30:00+05:30')
        cls.res = smc_zone_offices.parse(cls.raw)
        cls.by = {r.record_key: r.attrs for r in cls.res.records}

    def test_counts(self):
        smc_zone_offices.validate(self.res, self.raw)
        self.assertEqual(sorted(self.by), ['central', 'east_a', 'east_b', 'north', 'south_a', 'south_b', 'south_east',
                                           'south_west', 'west'])
        self.assertEqual(self.res.complete_record_types, ('smc_zone_office',))
        self.assertEqual({(g.geo_level, g.parent_code) for g in self.res.geos}, {('smc_zone', 'smc')})

    def test_values_read_off_the_page(self):
        # Central Zone: "Contact No. 2427726 / Mobile No. 9727740932 / Fax No. 2420548 | Control Room No. 2420547"
        self.assertEqual(self.by['central'], {
            'zone': 'Central Zone', 'zone_code': 'central',
            'address': 'Central Zone Vahivati Bhavan, Gordhandas Chokhawala Marg, Shri Tapipura, Surat-395003',
            'phones': ['2427726'], 'mobiles': ['9727740932'], 'fax': ['2420548'], 'control_room': ['2420547'],
            'control_room_mobiles': [], 'detail_url': 'https://www.suratmunicipal.gov.in/Zones/Central/CentralZone'})
        # ranges are kept as printed
        self.assertEqual(self.by['west']['phones'], ['2786181 to 83'])
        self.assertEqual(self.by['south_east']['mobiles'], ['9724346049-50-51-52'])
        self.assertEqual(self.by['south_west']['phones'], ['2663049-50', '2667926', '2665511', '2668833'])
        # "Control RoomMobile No." (no space) and "Control Room Mob. No." are both control-room mobiles
        self.assertEqual(self.by['east_b']['control_room_mobiles'], ['6559909506', '6359909606'])
        self.assertEqual(self.by['east_a']['control_room_mobiles'], ['9724346031', '9727740946'])
        self.assertEqual(self.by['south_b']['address'], 'Beside Swami Narayan Mandir, Gujarat Housing Board, Kanakpur')

    def test_unknown_label_fails_loudly(self):
        html = ('<div class="zones-contact"><div class="contact-heading">West Zone</div><div class="contact-block">'
                '<div class="mar-b10">Tadwadi, Surat</div><div><span class="text-bold">Pager No. </span>123</div></div></div>')
        raw = raw_from_file(FIXTURE)
        raw.body = html.encode()
        with self.assertRaises(ValueError):
            smc_zone_offices.parse(raw)

    def test_validate_rejects_missing_zones(self):
        res = smc_zone_offices.parse(self.raw)
        res.records = res.records[:5]
        with self.assertRaises(ValidationError):
            smc_zone_offices.validate(res, self.raw)


if __name__ == '__main__':
    unittest.main()
