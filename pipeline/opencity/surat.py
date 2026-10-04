"""Shared Surat geography: standard places and one canonical code per SMC zone.

Different SMC pages name zones differently ("West Zone", "Rander", "Zone - A"),
so every adapter must go through zone_code() to keep zone codes consistent.
"""
from __future__ import annotations

import re

from .model import Geo

SMC = Geo('smc_city', 'smc', 'Surat Municipal Corporation area')
SURAT_DISTRICT = Geo('surat_district', 'surat', 'Surat district', 'state', 'gujarat')
TAPI_DISTRICT = Geo('tapi_district', 'tapi', 'Tapi district', 'state', 'gujarat',
                    note='Some sources (Agmarknet market lists, WRD dam tables) file Tapi places under Surat.')
GUJARAT = Geo('state', 'gujarat', 'Gujarat')

STANDARD_GEOS = [GUJARAT, SURAT_DISTRICT, TAPI_DISTRICT, SMC]

# canonical code -> display name (zones as listed on SMC's budget-summary page, 2026)
ZONES = {
    'hq': 'Head Quarter',
    'central': 'Central Zone',
    'west': 'West Zone (Rander)',
    'north': 'North Zone (Katargam)',
    'east_a': 'East Zone - A (Varachha-A)',
    'east_b': 'East Zone - B (Varachha-B)',
    'south': 'South Zone (Udhna), before its split into South-A and South-B',
    'south_a': 'South Zone - A (Udhna-A)',
    'south_b': 'South Zone - B (Kanakpur)',
    'south_west': 'South West Zone (Athwa)',
    'south_east': 'South East Zone (Limbayat)',
}

_ALIASES = [
    (r'head ?quarter|^hq$', 'hq'),
    (r'south ?-? ?west|athwa', 'south_west'),
    (r'south ?-? ?east|limbayat', 'south_east'),
    (r'south.*\bb\b|kanakpur|udh?a?na ?-? ?b', 'south_b'),
    (r'south.*\ba\b|udh?a?na ?-? ?a', 'south_a'),
    (r'^south( zone)?$|udh?a?na', 'south'),
    (r'east.*\bb\b|varachha ?-? ?b', 'east_b'),
    (r'east.*\ba\b|varachha ?-? ?a', 'east_a'),
    (r'west|rander', 'west'),
    (r'north|katargam', 'north'),
    (r'central', 'central'),
]


def zone_code(name: str) -> str:
    """Map any SMC zone label to its canonical code. Raises KeyError for unknown labels."""
    s = re.sub(r'\(mm\)|\bzone\b|\s+', ' ', name.lower()).strip()
    s = re.sub(r'\s+', ' ', s)
    for pat, code in _ALIASES:
        if re.search(pat, s):
            return code
    raise KeyError(f'unknown SMC zone label: {name!r}')


def zone_geo(code: str) -> Geo:
    return Geo('smc_zone', code, ZONES[code], 'smc_city', 'smc')
