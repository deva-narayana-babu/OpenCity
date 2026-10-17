"""Shared Surat geography: standard places and one canonical code per SMC zone.

Different SMC pages name zones differently ("West Zone", "Rander", "Zone - A"),
so every adapter must go through zone_code() to keep zone codes consistent.
"""
from __future__ import annotations

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

def zone_code(name: str) -> str:
    """Map any SMC zone label to its canonical code. Raises KeyError for unknown labels.
    'East Zone - A (mm)' -> words ['east', 'a'] -> 'east_a'."""
    text = name.lower()
    for ch in '-()_,':
        text = text.replace(ch, ' ')
    words = [w for w in text.split() if w not in ('zone', 'mm')]
    joined = ''.join(words)                                  # 'south west' -> 'southwest'
    south = any(w in words for w in ('south', 'udhna', 'udhana'))
    east = any(w in words for w in ('east', 'varachha'))

    if 'head' in words or joined in ('hq', 'headquarter'):
        return 'hq'
    if 'southwest' in joined or 'athwa' in words:
        return 'south_west'
    if 'southeast' in joined or 'limbayat' in words:
        return 'south_east'
    if 'kanakpur' in words or (south and 'b' in words):
        return 'south_b'
    if south and 'a' in words:
        return 'south_a'
    if south:
        return 'south'
    if east and 'b' in words:
        return 'east_b'
    if east and 'a' in words:
        return 'east_a'
    if 'west' in words or 'rander' in words:
        return 'west'
    if 'north' in words or 'katargam' in words:
        return 'north'
    if 'central' in words:
        return 'central'
    raise KeyError(f'unknown SMC zone label: {name!r}')


def zone_geo(code: str) -> Geo:
    return Geo('smc_zone', code, ZONES[code], 'smc_city', 'smc')
