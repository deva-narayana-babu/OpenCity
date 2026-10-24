"""Census of India 2011, Surat district: Primary Census Abstract (PCA) and Houselisting PCA (household amenities).

Publisher: Office of the Registrar General & Census Commissioner, India (ORGI), Ministry of Home Affairs.

Where it comes from: a MIRROR of official Census of India data, the GitHub repository pigshell/india-census-2011
(https://github.com/pigshell/india-census-2011). In 2014 it scraped the Census website's PCA pages
(censusindia.gov.in/pca/pca.aspx) and Houselisting PCA pages (censusindia.gov.in/hlpca/default.aspx) into CSV.
The official site has the Surat District Census Handbook (NADA catalog 422 = Part XII-A, 423 = Part XII-B, with
"inset tables" and amenity XLSX files). But censusindia.gov.in sends an incomplete TLS certificate chain, so
certificate verification fails (checked 2026-10-24 with curl and with Python's default SSL context: "unable to get
local issuer certificate"). The pipeline does not turn verification off, so the official files cannot be
downloaded here, and the mirror is the fetch source. The mirror's README warns "No guarantee of correctness of
the processing tool chain ... Validate before use". So on every fetch validate() checks the Surat district figures
against the official DCHB Surat Part XII-A (Analytical Note pp. 63-80; a copy is in
reference/district-modules/india-census-dchb-surat-part-a-2011.pdf). All of those checks matched when this adapter
was written.

Documents: two plain GETs with no parameters. Neither file has a header row; columns are positional and follow the
mirror's column dictionaries (pca-colnames.csv and hlpca-colnames.csv).
  1. PCA for Gujarat (state code 24):
     https://raw.githubusercontent.com/pigshell/india-census-2011/master/pca/24.csv
     81 rows: the state and its 26 districts, each as Total, Rural and Urban. 91 columns:
       State code | District code ('000' on the state rows) | Level (STATE / DISTRICT) | Name |
       TRU (Total / Rural / Urban) | Area in sq km | No. of households |
       then 28 Persons / Male / Female triples, in this order:
         total population, population aged 0-6, Scheduled Castes, Scheduled Tribes, literates, illiterates,
         total workers,
         main workers: all, cultivators, agricultural labourers, household industry, other,
         marginal workers: the same five,
         marginal workers who worked 3-6 months: the same five,
         marginal workers who worked less than 3 months: the same five,
         non-workers.
  2. Houselisting PCA for Gujarat:
     https://raw.githubusercontent.com/pigshell/india-census-2011/master/houselisting/csv/Gujarat.csv
     710 rows: the state, its districts and their sub-districts (talukas), each as Total, Rural and Urban.
     145 columns: 10 identifiers, then the dictionary's columns c11-c145. The identifiers are: state code, state
     name, district code, district name, tehsil code, tehsil name, town/village code, ward no, area name
     (e.g. "Sub-Dist - Olpad"), and Total / Rural / Urban.
     Every value is a PERCENTAGE OF HOUSEHOLDS with one decimal. c11 and c119 are the 100 % base; they are not
     stored, but parse() checks that both equal 100, which catches shifted columns. The file has no absolute
     household counts (census.households from the PCA has them, at district level).
     The mirror's other file, hlpca-full.csv, has a header row that mislabels columns (the wall-material columns
     are named Material_Roof_*) and 11 junk columns at the end. That is why the state file and the dictionary
     are used instead.

What is stored. Each document is parsed on its own; parse() tells them apart by their column count (91 or 145).
- PCA: one row each for Surat district (geo surat_district/surat) and Gujarat (state/gujarat), for each residence.
  Every observation has dims.residence (total / rural / urban). The person counts also have dims.sex
  (persons / male / female).
    census.area_km2          area of the district or state in the residence class, in sq km (Census 2011)
    census.households        number of households
    census.population        total population
    census.population_0_6    population aged 0-6 years
    census.population_sc     Scheduled Caste population
    census.population_st     Scheduled Tribe population
    census.literates         literates: persons aged 7 and above who can read and write with understanding
                             in any language
    census.illiterates       illiterates; this includes every child aged 0-6 by definition
    census.workers           total workers (main + marginal)
    census.main_workers      worked for 6 months or more in the year before enumeration; dims.category is
                             all / cultivators / agricultural_labourers / household_industry / other
    census.marginal_workers  worked for less than 6 months; dims.category as above, and dims.months_worked
                             is under_6 (all marginal workers), 3_to_6 or under_3
    census.non_workers       persons who did no work at all in that year
- Houselisting PCA: one row per residence for Surat district, its 10 Census 2011 sub-districts (geo surat_taluka)
  and Gujarat. Each table is one metric, in % of households. dims.residence is as above, and dims.item is the
  answer category, in the dictionary's column order (HL_GROUPS below lists them):
    census.hh_condition_pct         condition of the census house: good / livable / dilapidated. Also the share
                                    of households in residence-only and residence-cum-other-use houses, with
                                    the same three conditions for each.
    census.hh_roof_pct, census.hh_wall_pct, census.hh_floor_pct
                                    predominant material of the roof, wall and floor
    census.hh_rooms_pct             number of dwelling rooms: none (no exclusive room), 1 ... 5, 6_plus
    census.hh_size_pct              household size: 1 ... 5, 6_8, 9_plus persons
    census.hh_ownership_pct         owned / rented / other
    census.hh_married_couples_pct   married couples in the household: 0 ... 4, 5_plus
    census.hh_water_source_pct      main source of drinking water (tap from treated or untreated source, wells,
                                    handpump, tubewell/borehole, spring, river/canal, tank/pond/lake, other)
    census.hh_water_location_pct    location of that source: within / near the premises, or away
    census.hh_lighting_pct          main source of lighting (electricity, kerosene, solar, other oil, any other,
                                    none)
    census.hh_latrine_pct           within_premises is the total of the eight latrine types that follow it
                                    (flush to piped sewer / septic tank / other, pit with or without slab, night
                                    soil to open drain, service latrine emptied by a human or an animal).
                                    none_within_premises = public_latrine + open.
    census.hh_bathing_pct           bathroom / enclosure without roof / none
    census.hh_drainage_pct          waste-water outlet: closed drainage / open drainage / none
    census.hh_cooking_fuel_pct      main cooking fuel (firewood, crop residue, cowdung cake,
                                    coal/lignite/charcoal, kerosene, LPG/PNG, electricity, biogas, other,
                                    no cooking)
    census.hh_kitchen_pct           cooking inside the house (with / without a kitchen), cooking outside (with /
                                    without a kitchen), or no cooking
    census.hh_banking_pct           households availing banking services
    census.hh_assets_pct            radio, TV, computer (with / without internet), landline only, mobile only,
                                    both, bicycle, two-wheeler, car/jeep/van. A household can have several, so
                                    these do not add up to 100. all_of_tv_computer_phone_vehicle = has a TV, a
                                    computer, a phone and a scooter or car; none = none of the listed assets.
    census.hh_structure_pct         type of structure: permanent / semi-permanent / temporary, with temporary
                                    split into serviceable and non-serviceable, and unclassifiable

Geography:
- surat_district/surat: Surat district within its 2011 boundaries. Tapi district had already been carved out
  (2007), so the 2011 district has 10 talukas.
- state/gujarat: Gujarat state, kept for comparison.
- surat_taluka/<code>: a Census 2011 sub-district (the level is shared with gsdma_rainfall). The codes are olpad,
  mangrol, umarpada, mandvi, kamrej, surat_city, chorasi, palsana, bardoli and mahuva; Census codes 03932-03941
  map to them in SUBDISTRICTS. The boundaries are those of 2011.
  "Surat City" (03937) is the Surat Municipal Corporation area of 2011; the DCHB lists the whole sub-district
  as "Surat (M Corp.) (Part)", 4,467,797 persons. That is before the 2020 city-limit extension, so it is NOT
  filed as smc_city.
  Taluka rows that later sources list, such as Ambika and Areth in GSDMA's 2026 rainfall reports, were not
  Census 2011 sub-districts.

Periods: PCA counts are at the Census reference date, 00:00 hours of 1 March 2011, an instant period
(2011-03-01). The houselisting figures come from the Houselisting and Housing Census. It was held in every state
in a 45-day window between April and September 2010, so its period is the national window 2010-04-01..2010-09-30.

Cadence: static. Census 2011 results do not change, and the next figures will come from Census 2027. The mirror
is re-checked every 90 days with a conditional GET.

Quirks and caveats:
- A residence row that does not exist is simply absent. It is not stored as not_reported. Surat City has no
  Rural row (it was all urban), and Umarpada and Mahuva have no Urban row (no towns in 2011). A blank
  houselisting cell would be stored as not_reported, as long as its table still adds up to 100 %. A blank PCA
  cell fails validation, because the counts have to add up. The 2011 files have no blanks.
- Houselisting values are rounded to 0.1 %, so the shares in an exclusive group add up to 100 +/- 0.6.
- Sub-district PCA counts (population and literacy by taluka), the number of villages and towns (713 villages,
  690 of them inhabited; 8 statutory and 14 census towns) and taluka areas are only in the DCHB on
  censusindia.gov.in. That site fails TLS verification (see above), so none of these are stored. The SMC
  ward-level 2011 population is already loaded by smc_council (election.ward_population).
- Ratios are not stored, because the source does not publish them. They follow from the stored counts:
  sex ratio = female / male x 1000 (787 for Surat, which is the figure in the DCHB text);
  child sex ratio = female 0-6 / male 0-6 x 1000 (835);
  literacy rate = literates / (population - population 0-6) x 100 (85.53 %);
  density = population / area (1,337 per sq km);
  urban share = urban / total population (79.7 %).
  validate() recomputes these and compares them with the DCHB.
- Under its 2011 boundaries the district is 79.7 % urban. Most of its population is in the 2011 SMC area.

Licence: the data is Census of India 2011, published by the Office of the Registrar General & Census
Commissioner, India; attribute "Census of India 2011, ORGI". The mirror states no licence for the data. Its code
is MIT-licensed (c) 2014 ganeshv.
"""
from __future__ import annotations

import csv
import io

from ..model import Geo, Metric, Obs, Raw, Result, Source, ValidationError
from ..parse import num
from ..surat import GUJARAT, SURAT_DISTRICT, TALUKA_NOTE

MIRROR = 'https://raw.githubusercontent.com/pigshell/india-census-2011/master/'
PCA_URL = MIRROR + 'pca/24.csv'
HLPCA_URL = MIRROR + 'houselisting/csv/Gujarat.csv'

PCA_DAY = '2011-03-01'                          # Census reference date (00:00 hours, 1 March 2011)
HL_PERIOD = ('2010-04-01', '2010-09-30')        # national window of the 2010 houselisting operations
SURAT_CODE = '492'                              # Census 2011 district code of Surat
RESIDENCE = {'Total': 'total', 'Rural': 'rural', 'Urban': 'urban'}
SEXES = ('persons', 'male', 'female')

# Census 2011 sub-district code -> (surat_taluka geo code, name in the file, geo name).
# The geo codes and names match gsdma_rainfall's, so the two sources do not rename each other's geos.
SUBDISTRICTS = {
    '03932': ('olpad', 'Olpad', 'Olpad'),
    '03933': ('mangrol', 'Mangrol', 'Mangrol'),
    '03934': ('umarpada', 'Umarpada', 'Umarpada'),
    '03935': ('mandvi', 'Mandvi', 'Mandvi'),
    '03936': ('kamrej', 'Kamrej', 'Kamrej'),
    '03937': ('surat_city', 'Surat City', 'Surat City'),
    '03938': ('chorasi', 'Chorasi', 'Chorasi (Choryasi)'),
    '03939': ('palsana', 'Palsana', 'Palsana'),
    '03940': ('bardoli', 'Bardoli', 'Bardoli'),
    '03941': ('mahuva', 'Mahuva', 'Mahuva'),
}
CATEGORIES = ('cultivators', 'agricultural_labourers', 'household_industry', 'other')

# The 28 Persons/Male/Female triples of the PCA file, in column order (after the 7 identifier columns):
# (metric, extra dims). The mirror's own column names are in the comments.
PCA_TRIPLES = [
    ('census.population', {}),                                   # TOT_P TOT_M TOT_F
    ('census.population_0_6', {}),                               # P_06 M_06 F_06
    ('census.population_sc', {}),                                # P_SC ...
    ('census.population_st', {}),                                # P_ST ...
    ('census.literates', {}),                                    # P_LIT ...
    ('census.illiterates', {}),                                  # P_ILL ...
    ('census.workers', {}),                                      # TOT_WORK_P ...
    ('census.main_workers', {'category': 'all'}),                # MAINWORK_P ...
    *[('census.main_workers', {'category': c}) for c in CATEGORIES],   # MAIN_CL_P ... MAIN_OT_F
    # MARGWORK_P ... MARG_OT_F, then MARGWORK_3_6_P ... MARG_OT_3_6_F, then MARGWORK_0_3_P ... MARG_OT_0_3_F
    *[('census.marginal_workers', {'category': c, 'months_worked': m})
      for m in ('under_6', '3_to_6', 'under_3')
      for c in ('all',) + CATEGORIES],
    ('census.non_workers', {}),                                  # NON_WORK_P ...
]
PCA_COLUMNS = 7 + 3 * len(PCA_TRIPLES)          # 91

# Houselisting PCA tables: (metric, number of its first column in hlpca-colnames.csv, items in column order).
# The columns run on without gaps from c12 to c145, except c119 (the 100 % kitchen base), which is skipped.
HL_GROUPS = [
    ('census.hh_condition_pct', 12, (
        'good', 'livable', 'dilapidated',
        'residence', 'residence_good', 'residence_livable', 'residence_dilapidated',
        'residence_cum_other', 'residence_cum_other_good', 'residence_cum_other_livable',
        'residence_cum_other_dilapidated')),
    ('census.hh_roof_pct', 23, (
        'grass_thatch_bamboo_wood_mud', 'plastic_polythene', 'handmade_tiles', 'machine_made_tiles', 'burnt_brick',
        'stone_slate', 'gi_metal_asbestos_sheets', 'concrete', 'other')),
    ('census.hh_wall_pct', 32, (
        'grass_thatch_bamboo', 'plastic_polythene', 'mud_unburnt_brick', 'wood', 'stone_without_mortar',
        'stone_with_mortar', 'gi_metal_asbestos_sheets', 'burnt_brick', 'concrete', 'other')),
    ('census.hh_floor_pct', 42, (
        'mud', 'wood_bamboo', 'burnt_brick', 'stone', 'cement', 'mosaic_floor_tiles', 'other')),
    ('census.hh_rooms_pct', 49, ('none', '1', '2', '3', '4', '5', '6_plus')),
    ('census.hh_size_pct', 56, ('1', '2', '3', '4', '5', '6_8', '9_plus')),
    ('census.hh_ownership_pct', 63, ('owned', 'rented', 'other')),
    ('census.hh_married_couples_pct', 66, ('0', '1', '2', '3', '4', '5_plus')),
    ('census.hh_water_source_pct', 72, (
        'tap_treated', 'tap_untreated', 'covered_well', 'uncovered_well', 'handpump', 'tubewell_borehole',
        'spring', 'river_canal', 'tank_pond_lake', 'other')),
    ('census.hh_water_location_pct', 82, ('within_premises', 'near_premises', 'away')),
    ('census.hh_lighting_pct', 85, ('electricity', 'kerosene', 'solar', 'other_oil', 'any_other', 'none')),
    ('census.hh_latrine_pct', 91, (
        'within_premises', 'flush_piped_sewer', 'flush_septic_tank', 'flush_other_system', 'pit_with_slab',
        'pit_without_slab', 'night_soil_open_drain', 'service_removed_by_human', 'service_by_animal',
        'none_within_premises', 'public_latrine', 'open')),
    ('census.hh_bathing_pct', 103, ('bathroom', 'enclosure_without_roof', 'none')),
    ('census.hh_drainage_pct', 106, ('closed', 'open', 'none')),
    ('census.hh_cooking_fuel_pct', 109, (
        'firewood', 'crop_residue', 'cowdung_cake', 'coal_lignite_charcoal', 'kerosene', 'lpg_png', 'electricity',
        'biogas', 'other', 'no_cooking')),
    ('census.hh_kitchen_pct', 120, (
        'cooking_inside', 'cooking_inside_with_kitchen', 'cooking_inside_without_kitchen', 'cooking_outside',
        'cooking_outside_with_kitchen', 'cooking_outside_without_kitchen', 'no_cooking')),
    ('census.hh_banking_pct', 127, ('availing_banking',)),
    ('census.hh_assets_pct', 128, (
        'radio', 'television', 'computer_with_internet', 'computer_without_internet', 'landline_only',
        'mobile_only', 'landline_and_mobile', 'bicycle', 'two_wheeler', 'car_jeep_van',
        'all_of_tv_computer_phone_vehicle', 'none')),
    ('census.hh_structure_pct', 140, (
        'permanent', 'semi_permanent', 'temporary', 'temporary_serviceable', 'temporary_non_serviceable',
        'unclassifiable')),
]
HL_COLUMNS = 145

# Items that are mutually exclusive and cover all households, so they add up to 100 %. In every other table
# all items are exclusive, except banking (a single item) and assets (a household can have several).
HL_PARTS = {
    'census.hh_condition_pct': ('good', 'livable', 'dilapidated'),
    'census.hh_latrine_pct': ('within_premises', 'none_within_premises'),
    'census.hh_kitchen_pct': ('cooking_inside', 'cooking_outside', 'no_cooking'),
    'census.hh_structure_pct': ('permanent', 'semi_permanent', 'temporary', 'unclassifiable'),
}
HL_NOT_EXCLUSIVE = ('census.hh_banking_pct', 'census.hh_assets_pct')

# Surat district figures printed in the official DCHB Surat Part XII-A (Analytical Note pp. 63-80).
# validate() requires the mirror to match them exactly.
DCHB_SURAT = {
    ('census.population', 'total', 'persons'): 6081322,
    ('census.population', 'total', 'male'): 3402224,
    ('census.population', 'total', 'female'): 2679098,
    ('census.population', 'rural', 'persons'): 1232109,
    ('census.population', 'urban', 'persons'): 4849213,
    ('census.population_0_6', 'total', 'persons'): 736286,
    ('census.population_sc', 'total', 'persons'): 158115,
    ('census.population_st', 'total', 'persons'): 856952,
    ('census.literates', 'total', 'persons'): 4571410,
    ('census.illiterates', 'total', 'persons'): 1509912,
    ('census.workers', 'total', 'persons'): 2553542,
    ('census.non_workers', 'total', 'persons'): 3527780,
}

_HH = '% of households'
SOURCE = Source(
    id='census2011_surat',
    name='Census 2011: Primary Census Abstract and household amenities, Surat district',
    publisher='Office of the Registrar General & Census Commissioner, India (Census of India 2011); '
              'CSV mirror by the pigshell/india-census-2011 GitHub repository',
    url='https://github.com/pigshell/india-census-2011',
    module='population',
    cadence='static',
    interval_hours=24 * 90,     # Census 2011 does not change; the mirror is only re-checked for fixes
    geo_note='Surat district (2011 boundaries, Total/Rural/Urban), its 10 Census 2011 sub-districts '
             '(surat_taluka; houselisting tables only) and Gujarat state for comparison. "Surat City" '
             'sub-district is the 2011 SMC area, not today\'s smc_city.',
    licence_note='Census of India 2011 data (Office of the Registrar General & Census Commissioner, India), '
                 'attribute ORGI. Mirror code MIT (c) 2014 ganeshv; the mirror states no licence for the data.',
    notes='Fetched from a GitHub mirror because censusindia.gov.in fails TLS certificate verification (incomplete '
          'chain). The mirror disclaims correctness, so validate() requires its Surat totals to match the official '
          'DCHB Surat 2011. Houselisting values are % of households (no counts). Sub-district population, village '
          'and town counts are not in the mirror and are not stored. Ratios (sex ratio 787, child sex ratio 835, '
          'literacy 85.53 %, density 1,337/sq km) are not stored; compute them from the counts.',
    metrics=(
        Metric('census.area_km2', 'Area (Census 2011)', 'sq km',
               'Area in square kilometres as given in the Census 2011 PCA, by dims.residence (total / rural / '
               'urban). Population density = census.population / census.area_km2.'),
        Metric('census.households', 'Households (Census 2011)', 'households',
               'Number of households in the Census 2011 PCA, by dims.residence.'),
        Metric('census.population', 'Population (Census 2011)', 'persons',
               'Total population enumerated in Census 2011 (reference date 1 March 2011), by dims.residence '
               'and dims.sex (persons / male / female). Sex ratio = female / male x 1000.'),
        Metric('census.population_0_6', 'Population aged 0-6 (Census 2011)', 'persons',
               'Children aged 0-6 years, by dims.residence and dims.sex. Child sex ratio = female / male x 1000.'),
        Metric('census.population_sc', 'Scheduled Caste population (Census 2011)', 'persons',
               'Population belonging to Scheduled Castes, by dims.residence and dims.sex.'),
        Metric('census.population_st', 'Scheduled Tribe population (Census 2011)', 'persons',
               'Population belonging to Scheduled Tribes, by dims.residence and dims.sex.'),
        Metric('census.literates', 'Literates (Census 2011)', 'persons',
               'Persons aged 7 and above who can read and write with understanding in any language, by '
               'dims.residence and dims.sex. Literacy rate = literates / (population - population 0-6) x 100.'),
        Metric('census.illiterates', 'Illiterates (Census 2011)', 'persons',
               'Persons who are not literate, including all children aged 0-6 (population = literates + '
               'illiterates), by dims.residence and dims.sex.'),
        Metric('census.workers', 'Workers, main and marginal (Census 2011)', 'persons',
               'Persons who did any economically productive work in the year before enumeration (main + '
               'marginal workers), by dims.residence and dims.sex.'),
        Metric('census.main_workers', 'Main workers (Census 2011)', 'persons',
               'Workers who worked for 6 months or more in the reference year, by dims.residence, dims.sex and '
               'dims.category (all / cultivators / agricultural_labourers / household_industry / other).'),
        Metric('census.marginal_workers', 'Marginal workers (Census 2011)', 'persons',
               'Workers who worked for less than 6 months in the reference year, by dims.residence, dims.sex, '
               'dims.category (as for main workers) and dims.months_worked (under_6 = all marginal workers; '
               '3_to_6; under_3).'),
        Metric('census.non_workers', 'Non-workers (Census 2011)', 'persons',
               'Persons who did no work at all in the reference year, by dims.residence and dims.sex.'),
        Metric('census.hh_condition_pct', 'Households by condition of the census house (Census 2011)', _HH,
               'Share of households living in a census house in good / livable / dilapidated condition '
               '(dims.item). The residence_* and residence_cum_other_* items split the same households into '
               'houses used only as a residence and houses also used for other purposes.'),
        Metric('census.hh_roof_pct', 'Households by roof material (Census 2011)', _HH,
               'Share of households by predominant material of the roof (dims.item).'),
        Metric('census.hh_wall_pct', 'Households by wall material (Census 2011)', _HH,
               'Share of households by predominant material of the walls (dims.item).'),
        Metric('census.hh_floor_pct', 'Households by floor material (Census 2011)', _HH,
               'Share of households by predominant material of the floor (dims.item).'),
        Metric('census.hh_rooms_pct', 'Households by number of dwelling rooms (Census 2011)', _HH,
               'Share of households by number of dwelling rooms (dims.item: none = no exclusive room, 1-5, '
               '6_plus).'),
        Metric('census.hh_size_pct', 'Households by household size (Census 2011)', _HH,
               'Share of households by number of members (dims.item: 1-5, 6_8, 9_plus).'),
        Metric('census.hh_ownership_pct', 'Households by ownership of the house (Census 2011)', _HH,
               'Share of households living in an owned / rented / other house (dims.item).'),
        Metric('census.hh_married_couples_pct', 'Households by number of married couples (Census 2011)', _HH,
               'Share of households by number of married couples living in them (dims.item: 0-4, 5_plus).'),
        Metric('census.hh_water_source_pct', 'Households by main source of drinking water (Census 2011)', _HH,
               'Share of households by main source of drinking water (dims.item), e.g. tap_treated = tap water '
               'from a treated source.'),
        Metric('census.hh_water_location_pct', 'Households by location of drinking water (Census 2011)', _HH,
               'Share of households whose main drinking-water source is within the premises, near the premises '
               'or away (dims.item).'),
        Metric('census.hh_lighting_pct', 'Households by main source of lighting (Census 2011)', _HH,
               'Share of households by main source of lighting (dims.item), e.g. electricity.'),
        Metric('census.hh_latrine_pct', 'Households by latrine facility (Census 2011)', _HH,
               'Share of households with a latrine within the premises (within_premises, then by type of '
               'latrine) or without one (none_within_premises = public_latrine + open), by dims.item.'),
        Metric('census.hh_bathing_pct', 'Households by bathing facility (Census 2011)', _HH,
               'Share of households with a bathroom, an enclosure without roof, or no bathing facility within '
               'the premises (dims.item).'),
        Metric('census.hh_drainage_pct', 'Households by waste-water outlet (Census 2011)', _HH,
               'Share of households whose waste-water outlet is connected to closed drainage, open drainage or '
               'no drainage (dims.item).'),
        Metric('census.hh_cooking_fuel_pct', 'Households by cooking fuel (Census 2011)', _HH,
               'Share of households by main type of fuel used for cooking (dims.item), e.g. lpg_png, firewood.'),
        Metric('census.hh_kitchen_pct', 'Households by kitchen facility (Census 2011)', _HH,
               'Share of households cooking inside the house (with / without a kitchen), outside the house (with '
               '/ without a kitchen) or not cooking (dims.item).'),
        Metric('census.hh_banking_pct', 'Households availing banking services (Census 2011)', _HH,
               'Share of households availing banking services (dims.item availing_banking).'),
        Metric('census.hh_assets_pct', 'Households by assets owned (Census 2011)', _HH,
               'Share of households having each asset (dims.item). Not exclusive: a household can own several. '
               'none = none of the listed assets.'),
        Metric('census.hh_structure_pct', 'Households by type of structure of the house (Census 2011)', _HH,
               'Share of households by type of structure of the census house: permanent, semi_permanent, '
               'temporary (= temporary_serviceable + temporary_non_serviceable) and unclassifiable (dims.item).'),
    ),
)


def fetch(ctx):
    yield ctx.get(PCA_URL, meta={'doc': 'pca'})
    yield ctx.get(HLPCA_URL, meta={'doc': 'hlpca'})


def _rows(raw: Raw) -> list[list[str]]:
    return [r for r in csv.reader(io.StringIO(raw.body.decode('utf-8-sig'))) if r]


def parse(raw: Raw) -> Result:
    rows = _rows(raw)
    width = len(rows[0]) if rows else 0
    kind = {PCA_COLUMNS: 'pca', HL_COLUMNS: 'hlpca'}.get(width)
    if kind is None:
        raise ValueError(f'{raw.url}: {width} columns, expected {PCA_COLUMNS} (PCA) or {HL_COLUMNS} (houselisting)')
    if raw.meta.get('doc', kind) != kind:
        raise ValueError(f'{raw.url}: expected the {raw.meta["doc"]} file but got the {kind} file')
    if any(len(r) != width for r in rows):
        raise ValueError(f'{raw.url}: rows of different lengths')
    if kind == 'pca':
        return _parse_pca(rows)
    return _parse_hlpca(rows)


def _obs(metric, geo, start, end, cell, dims) -> Obs:
    v = num(cell)
    return Obs(metric, geo.geo_level, geo.geo_code, start, end, value=v,
               status='reported' if v is not None else 'not_reported', dims=dims)


def _parse_pca(rows) -> Result:
    res = Result(geos=[GUJARAT, SURAT_DISTRICT])
    for r in rows:
        district, level, name = r[1], r[2], r[3]
        if level == 'STATE' and district == '000':
            geo = GUJARAT
        elif level == 'DISTRICT' and district == SURAT_CODE:
            if name != 'Surat':
                raise ValueError(f'district {SURAT_CODE} is named {name!r}, expected Surat')
            geo = SURAT_DISTRICT
        else:
            continue
        residence = RESIDENCE[r[4]]
        res.observations.append(_obs('census.area_km2', geo, PCA_DAY, PCA_DAY, r[5], {'residence': residence}))
        res.observations.append(_obs('census.households', geo, PCA_DAY, PCA_DAY, r[6], {'residence': residence}))
        for i, (metric, dims) in enumerate(PCA_TRIPLES):
            for sex, cell in zip(SEXES, r[7 + 3 * i: 10 + 3 * i]):
                res.observations.append(_obs(metric, geo, PCA_DAY, PCA_DAY, cell,
                                             {'residence': residence, 'sex': sex, **dims}))
    return res


def _parse_hlpca(rows) -> Result:
    res = Result(geos=[GUJARAT, SURAT_DISTRICT])
    for r in rows:
        district, tehsil, tehsil_name = r[2], r[4], r[5]
        if district == '000':
            geo = GUJARAT
        elif district == SURAT_CODE and tehsil == '00000':
            geo = SURAT_DISTRICT
        elif district == SURAT_CODE:
            if tehsil not in SUBDISTRICTS:
                raise ValueError(f'unknown Surat sub-district {tehsil} {tehsil_name!r}: add it to SUBDISTRICTS')
            code, census_name, geo_name = SUBDISTRICTS[tehsil]
            if tehsil_name != census_name:
                raise ValueError(f'sub-district {tehsil} is named {tehsil_name!r}, expected {census_name!r}')
            geo = Geo('surat_taluka', code, geo_name, 'surat_district', 'surat', note=TALUKA_NOTE)
            if geo not in res.geos:
                res.geos.append(geo)
        else:
            continue
        # c11 (households, total) and c119 (kitchen, total) are the 100 % bases: anything else means shifted columns
        if num(r[10]) != 100 or num(r[118]) != 100:
            raise ValueError(f'{r[8]} {r[9]}: base columns c11/c119 are {r[10]}/{r[118]}, not 100')
        residence = RESIDENCE[r[9]]
        for metric, first, items in HL_GROUPS:
            for col, item in enumerate(items, start=first):
                res.observations.append(_obs(metric, geo, *HL_PERIOD, r[col - 1],
                                             {'residence': residence, 'item': item}))
    return res


# ---------- validation ----------

def validate(result: Result, raw: Raw) -> None:
    metrics = {o.metric_id for o in result.observations}
    if 'census.population' in metrics:
        _validate_pca(result)
    elif 'census.hh_condition_pct' in metrics:
        _validate_hlpca(result)
    else:
        raise ValidationError('no Census observations parsed; the mirror file may have changed')


def _validate_pca(result: Result) -> None:
    v = {}      # (geo, residence, metric, category, months_worked, sex) -> value
    for o in result.observations:
        d = o.dims
        if o.value is None:
            raise ValidationError(f'{o.metric_id} {o.geo_code} {d}: blank in the 2011 PCA, which has no blanks')
        v[(o.geo_code, d['residence'], o.metric_id, d.get('category', ''), d.get('months_worked', ''),
           d.get('sex', ''))] = o.value
    places = {(k[0], k[1]) for k in v}
    if places != {(g, r) for g in ('surat', 'gujarat') for r in RESIDENCE.values()}:
        raise ValidationError(f'expected Total/Rural/Urban rows for Surat and Gujarat, got {sorted(places)}')

    for (geo, res, metric, cat, months, sex), value in v.items():
        if sex == 'persons':
            parts = v[(geo, res, metric, cat, months, 'male')] + v[(geo, res, metric, cat, months, 'female')]
            if value != parts:
                raise ValidationError(f'{geo} {res} {metric} {cat}: persons {value} is not male + female {parts}')
        if res == 'total' and metric in ('census.population', 'census.households', 'census.area_km2'):
            parts = v[(geo, 'rural', metric, cat, months, sex)] + v[(geo, 'urban', metric, cat, months, sex)]
            if abs(value - parts) > 0.02:
                raise ValidationError(f'{geo} {metric} {sex}: total {value} is not rural + urban {parts}')

    for geo, res in places:
        for sex in SEXES:
            def get(metric, cat='', months=''):
                return v[(geo, res, metric, cat, months, sex)]
            marg = 'census.marginal_workers'
            pop = get('census.population')
            sums = {
                'literates + illiterates': get('census.literates') + get('census.illiterates'),
                'workers + non-workers': get('census.workers') + get('census.non_workers'),
            }
            for what, total in sums.items():
                if total != pop:
                    raise ValidationError(f'{geo} {res} {sex}: population {pop} is not {what} ({total})')
            if get('census.workers') != get('census.main_workers', 'all') + get(marg, 'all', 'under_6'):
                raise ValidationError(f'{geo} {res} {sex}: workers is not main + marginal workers')
            if get('census.main_workers', 'all') != sum(get('census.main_workers', c) for c in CATEGORIES):
                raise ValidationError(f'{geo} {res} {sex}: main workers do not add up over the four categories')
            for c in ('all',) + CATEGORIES:
                if get(marg, c, 'under_6') != get(marg, c, '3_to_6') + get(marg, c, 'under_3'):
                    raise ValidationError(f'{geo} {res} {sex}: marginal {c} is not 3-6 + under-3 months')
            for m in ('under_6', '3_to_6', 'under_3'):
                if get(marg, 'all', m) != sum(get(marg, c, m) for c in CATEGORIES):
                    raise ValidationError(f'{geo} {res} {sex}: marginal workers ({m}) do not add up')

    def surat(metric, sex='persons', res='total'):
        return v[('surat', res, metric, '', '', sex)]

    for (metric, res, sex), official in DCHB_SURAT.items():
        if surat(metric, sex, res) != official:
            raise ValidationError(f'Surat {metric} {res} {sex} = {surat(metric, sex, res)}, '
                                  f'but the official DCHB prints {official}')

    # ratios quoted in the DCHB text: sex ratio 787, child sex ratio 835, literacy 85.53 %, 1,337 persons per sq km
    pop, kids = surat('census.population'), surat('census.population_0_6')
    derived = {
        'sex ratio': (round(surat('census.population', 'female') / surat('census.population', 'male') * 1000), 787),
        'child sex ratio': (round(surat('census.population_0_6', 'female') / surat('census.population_0_6', 'male')
                                  * 1000), 835),
        'literacy rate': (round(surat('census.literates') / (pop - kids) * 100, 2), 85.53),
        'density': (round(pop / surat('census.area_km2', '')), 1337),
    }
    for what, (got, official) in derived.items():
        if got != official:
            raise ValidationError(f'Surat {what} works out to {got}, the DCHB says {official}')


def _validate_hlpca(result: Result) -> None:
    exclusive = {metric: HL_PARTS.get(metric, items) for metric, _, items in HL_GROUPS
                 if metric not in HL_NOT_EXCLUSIVE}
    sums: dict[tuple, float] = {}
    places = set()
    for o in result.observations:
        if o.value is None:
            continue
        if not 0 <= o.value <= 100:
            raise ValidationError(f'{o.metric_id} {o.geo_code} {o.dims}: {o.value} % is not a percentage')
        place = (o.geo_level, o.geo_code, o.dims['residence'])
        places.add(place)
        if o.dims['item'] in exclusive.get(o.metric_id, ()):
            sums[place + (o.metric_id,)] = sums.get(place + (o.metric_id,), 0) + o.value
    for (level, code, residence, metric), total in sums.items():
        if abs(total - 100) > 1.0:
            raise ValidationError(f'{metric} {code} {residence}: shares add up to {total:.1f} %, not 100')
    talukas = {code for level, code, _ in places if level == 'surat_taluka'}
    if talukas != {code for code, _, _ in SUBDISTRICTS.values()}:
        raise ValidationError(f'Surat sub-districts parsed: {sorted(talukas)}; expected all 10')
    for residence in RESIDENCE.values():
        if ('surat_district', 'surat', residence) not in places or ('state', 'gujarat', residence) not in places:
            raise ValidationError(f'missing the {residence} row for Surat district or Gujarat')
    if len(places) < 30:
        raise ValidationError(f'only {len(places)} houselisting rows parsed for Surat and Gujarat')
