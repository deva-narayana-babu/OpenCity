# OpenCity data: sources and metrics

This file is written by the refresher (`opencity/export.py`) from the database and from each adapter's own description. Do not edit it by hand. The same catalogue is in `catalog/*.csv`, the numbers are in `observations/<source>.csv` and the named entities are in `records/<type>.csv`.

43 sources, 309 metrics with data, 35143 observations.

| Source | Module | Publisher | Cadence | Metrics | Observations | Latest period | Status |
|---|---|---|---|---|---|---|---|
| [shc_soil_surat](#shc_soil_surat) | agriculture | Department of Agriculture & Farmers Welfare, Government of India (Soil Health Card portal) | weekly | 4 | 1450 | 2027-03-31 | ok |
| [ndma_sachet_surat](#ndma_sachet_surat) | alerts | National Disaster Management Authority, SACHET CAP platform (alerts issued by IMD, CWC, INCOIS and State Disaster Management Authorities) | hourly | 1 | 0 |  | ok |
| [smc_helplines](#smc_helplines) | citizen | Surat Municipal Corporation | static | 0 | 0 |  | ok |
| [smc_council](#smc_council) | council | Surat Municipal Corporation (Elected Wing; Election & Census Department) | weekly | 4 | 395 | 2021-01-01 | ok |
| [smc_past_elections](#smc_past_elections) | council | Surat Municipal Corporation, Election & Census Department | static | 5 | 95 | 2021-02-21 | ok |
| [gujcourts_surat](#gujcourts_surat) | courts | District Judiciary of Gujarat (High Court of Gujarat), Virtual Justice Clock | daily | 3 | 270 | 2026-10-18 | ok |
| [njdg_surat](#njdg_surat) | courts | National Judicial Data Grid (eCourts project, e-Committee of the Supreme Court of India; NIC) | daily | 16 | 158 | 2026-12-31 | ok |
| [gseb_results](#gseb_results) | education | Gujarat Secondary and Higher Secondary Education Board (GSEB), Gandhinagar | annual | 5 | 428 | 2026-12-31 | ok |
| [udise_surat](#udise_surat) | education | Department of School Education & Literacy, Ministry of Education, Government of India (UDISE+) | annual | 20 | 192 | 2026-03-31 | ok |
| [cpcb_aqi](#cpcb_aqi) | environment | Central Pollution Control Board, Government of India | daily | 8 | 33 | 2026-10-18T10:00 | ok |
| [smc_air_quality](#smc_air_quality) | environment | Surat Municipal Corporation, Air Quality Management Cell | daily | 6 | 6 | 2026-10-18T11:02 | ok |
| [smc_swm](#smc_swm) | environment | Surat Municipal Corporation, Solid Waste Management Department | monthly | 5 | 3462 | 2026-09-30 | ok |
| [cityfinance_surat](#cityfinance_surat) | finance | Ministry of Housing and Urban Affairs, Government of India (CityFinance) | annual | 7 | 200 | 2024-03-31 | ok |
| [smc_balance_sheet](#smc_balance_sheet) | finance | Surat Municipal Corporation, Accounts Department | annual | 40 | 767 | 2026-03-31 | ok |
| [smc_budget_summary](#smc_budget_summary) | finance | Surat Municipal Corporation, Accounts Department | weekly | 2 | 264 | 2027-03-31 | ok |
| [agmarknet_surat](#agmarknet_surat) | food | Directorate of Marketing & Inspection (Agmarknet), Ministry of Agriculture & Farmers Welfare, Government of India | daily | 5 | 0 |  | disabled |
| [fca_prices](#fca_prices) | food | Price Monitoring Division, Department of Consumer Affairs, Government of India | daily | 2 | 0 |  | disabled |
| [nfhs5_surat](#nfhs5_surat) | health | International Institute for Population Sciences / Ministry of Health and Family Welfare (NFHS-5) | static | 3 | 208 | 2021-12-31 | ok |
| [smc_disease](#smc_disease) | health | Surat Municipal Corporation, Health Department and Vector Borne Diseases Control (VBDC) Department | monthly | 14 | 9288 | 2023-10-31 | ok |
| [smc_health_centres](#smc_health_centres) | health | Surat Municipal Corporation, Health Department | static | 1 | 20 | 2024-06-24 | ok |
| [smc_pmjay_hospitals](#smc_pmjay_hospitals) | health | Surat Municipal Corporation, Health Department (PM-JAY / MA Yojana hospital list) | static | 2 | 23 | 2024-06-27 | ok |
| [smc_smimer](#smc_smimer) | health | Surat Municipal Corporation, SMIMER hospital | monthly | 13 | 4658 | 2026-12-31 | ok |
| [smc_pmay](#smc_pmay) | housing | Surat Municipal Corporation, Department of Affordable Housing | static | 2 | 4 | 2023-09-12 | ok |
| [smc_recruitment](#smc_recruitment) | jobs | Surat Municipal Corporation (Recruitment cell) | daily | 2 | 2 | 2026-10-24 | ok |
| [smc_officials](#smc_officials) | leadership | Surat Municipal Corporation (administrative wing) | weekly | 0 | 0 |  | ok |
| [surat_collectorate](#surat_collectorate) | leadership | District Administration Surat (Collectorate), surat.nic.in (NIC S3WaaS) | weekly | 0 | 0 |  | ok |
| [smc_zone_offices](#smc_zone_offices) | offices | Surat Municipal Corporation | static | 0 | 0 |  | ok |
| [surat_talukas](#surat_talukas) | offices | District Administration Surat (Collectorate), surat.nic.in (NIC S3WaaS) | static | 0 | 0 |  | ok |
| [ncrb_metro_surat](#ncrb_metro_surat) | police | National Crime Records Bureau, Ministry of Home Affairs (Crime in India 2024); tables mirrored as XLSX by OpenCity Foundation (data.opencity.in) | annual | 4 | 56 | 2024-12-31 | ok |
| [census2011_surat](#census2011_surat) | population | Office of the Registrar General & Census Commissioner, India (Census of India 2011); CSV mirror by the pigshell/india-census-2011 GitHub repository | static | 31 | 4905 | 2011-03-01 | ok |
| [smc_vital_stats](#smc_vital_stats) | population | Surat Municipal Corporation, Health Department (Birth and Death Registration) | annual | 15 | 1413 | 2022-10-31 | ok |
| [smc_streetlights](#smc_streetlights) | power | Surat Municipal Corporation, Street Light Department | monthly | 1 | 48 | 2021-02-28 | ok |
| [smc_rti](#smc_rti) | rti | Surat Municipal Corporation, RTI Cell | quarterly | 50 | 644 | 2026-06-30 | ok |
| [smc_ucd_schemes](#smc_ucd_schemes) | schemes | Surat Municipal Corporation, Urban Community Development Department | static | 0 | 0 |  | ok |
| [smc_tenders](#smc_tenders) | tenders | Surat Municipal Corporation (tenders invited by its zones and departments) | daily | 2 | 4 | 2026-10-24 | ok |
| [aai_surat_airport](#aai_surat_airport) | transport | Airports Authority of India (Traffic News, Annexure III) | monthly | 2 | 0 |  | disabled |
| [smc_ebus](#smc_ebus) | transport | Surat Municipal Corporation (BRTS / city bus operations) | monthly | 6 | 6 | 2026-04-30 | ok |
| [jjm_surat](#jjm_surat) | water | Jal Jeevan Mission, Department of Drinking Water and Sanitation, Ministry of Jal Shakti, GoI | daily | 5 | 12 | 2026-10-24 | ok |
| [smc_rainfall](#smc_rainfall) | water | Surat Municipal Corporation (Ukai and weir figures credited on the page to the Irrigation Department / Collector Office) | 2-hourly | 12 | 198 | 2026-10-18T11:00 | ok |
| [smc_water_quality](#smc_water_quality) | water | Surat Municipal Corporation, Hydraulic Department | monthly | 3 | 5283 | 2026-08-31 | ok |
| [wrd_reservoirs](#wrd_reservoirs) | water | Narmada, Water Resources, Water Supply and Kalpsar Department, Government of Gujarat | daily | 14 | 246 | 2026-10-17 | ok |
| [gsdma_rainfall](#gsdma_rainfall) | weather | Gujarat State Disaster Management Authority / State Emergency Operation Centre, Government of Gujarat | daily | 5 | 405 | 2026-10-21T06:00 | ok |
| [openmeteo_surat](#openmeteo_surat) | weather | Open-Meteo.com (weather model data from national weather services) | 3-hourly | 17 | 0 |  | disabled |

## shc_soil_surat

**Soil Health Card nutrient dashboard: Surat district talukas**

- **Publisher:** Department of Agriculture & Farmers Welfare, Government of India (Soil Health Card portal)
- **Page:** https://soilhealth.dac.gov.in/
- **Module:** agriculture; **cadence:** weekly (checked every 168 h)
- **Geography:** Surat district talukas as Soil Health Card blocks (surat_taluka; the city is one surat_city block) and the Surat district total (sum of the block rows)
- **Licence:** Government of India portal (soilhealth.dac.gov.in); no explicit open licence
- **Enabled:** yes; **last success:** 2026-10-24T22:44:33+05:30
- **Holds:** 1450 observations
- **Notes:** Counts of soil samples by test-result class, per block, scheme and cycle (financial year), from the public GraphQL API behind the portal's Nutrient Dashboard. District values are sums of the block rows, as the portal's district view shows them. The current cycle is in progress.

<details><summary>How it is collected and parsed</summary>

```text
Soil Health Card nutrient dashboard: soil samples by nutrient class for the talukas (blocks) of Surat district.

Publisher: Department of Agriculture & Farmers Welfare, Ministry of Agriculture & Farmers Welfare, Government of
India, through the Soil Health Card portal (https://soilhealth.dac.gov.in/, "Nutrient Dashboard" page).

Endpoint: the public dashboard reads a GraphQL API. One POST per test cycle, JSON body, no login, token or API key
(the portal's own client sends "authorization" only when a user is signed in; anonymous visitors send none, and
so do we). soilhealth.dac.gov.in/robots.txt disallows nothing; the API host has no robots.txt (it answers
"GET query missing." to any GET).

    POST https://soilhealth4.dac.gov.in/
    {"query": "query GetNutrientDashboardForPortal($state: ID, $district: ID, ... $cycle: String, ...) {
                 getNutrientDashboardForPortal(state: $state, district: $district, ... cycle: $cycle, ...) }",
     "variables": {"state": "63f922a6dbc0f7fe06751641",       # GUJARAT (state code 24)
                   "district": "63f92c6189d86ca9e2bc2283",    # SURAT (district code 459)
                   "cycle": "2025-26"}}

The cycles are financial years. The portal offers 2023-24 to 2026-27 (2026-10-24); fetch() asks for every cycle
from 2023-24 to the current financial year. No scheme filter is sent, so all schemes come back.

Response layout: {"data": {"getNutrientDashboardForPortal": [row, ...]}}, one row per block and scheme:

    {"scheme": "660f941a5c8405ca8375c7c6", "cycle": "2025-26",
     "state": {"name": "GUJARAT", "code": "24"}, "district": {"name": "SURAT", "code": "459"},
     "block": {"name": "BARDOLI", "code": "4232"},
     "results": {"n": {"High": 0, "Low": 3093, "Medium": 0}, "p": {...}, "k": {...}, "OC": {...},
                 "pH": {"Alkaline": 299, "Acidic": 0, "Neutral": 2794}, "EC": {"Saline": 644, "NonSaline": 2449},
                 "S": {"Sufficient": 2389, "Deficient": 704}, "Fe": {...}, "Zn": {...}, "Cu": {...}, "B": {...},
                 "Mn": {...}},
     "updatedAt": "2026-10-23T17:54:00.877Z", "lastProcessedAt": "2026-10-23T17:17:18.196Z"}

Each number is a count of soil samples tested in that block, cycle and scheme whose result fell in that class.
2025-26: 15 rows (10 blocks under Soil Health Card RKVY, 5 under NMNF). 2023-24 rows have no updatedAt.

Observations (unit: soil samples), period = the cycle's financial year (1 April - 31 March), dims.scheme = the
scheme slug (SCHEMES; decoded once with the portal's public getSchemes query, e.g. shc_rkvy = "Soil Health Card
RKVY", nmnf = "National Mission on Natural Farming (NMNF)", others = "Others"):
    soil.shc_npk_oc_samples         dims.parameter n (available nitrogen), p (phosphorus), k (potassium),
                                    oc (organic carbon); dims.class high / medium / low
    soil.shc_ph_samples             soil reaction; dims.class acidic / neutral / alkaline
    soil.shc_ec_samples             electrical conductivity; dims.class saline / non_saline
    soil.shc_micronutrient_samples  dims.parameter s (sulphur), fe (iron), zn (zinc), cu (copper), b (boron),
                                    mn (manganese); dims.class sufficient / deficient
The class thresholds are the Soil Health Card scheme's, applied by the portal; they are not in the response.
publisher_as_of is the row's updatedAt in IST (the latest of the block rows for a district total).

Geography:
- surat_taluka/<code>: the portal's "block". In Gujarat the SHC block is the revenue taluka. Codes and names are
  shared with surat_talukas (BLOCKS maps the portal's names: BARDOLI -> bardoli, CHORASI -> chorasi, ...,
  Suratcity -> surat_city). The portal still files the city as one "Suratcity" block (code 4242), not as the six
  city talukas of surat.nic.in, and has no rows for Ambika or Areth (2023-24 to 2026-27).
- surat_district/surat: the sum of the block rows of the same scheme, cycle, parameter and class. The portal does
  not send a district row; its district view adds the block rows up the same way in the browser. A class that
  is missing (absent key, null parameter or null count) in any block row of that scheme and cycle makes the
  district value not_reported rather than a partial sum. A null count in a block row is stored as not_reported.

Cadence: the portal re-processes the counts daily (updatedAt), and samples keep being entered for past cycles
(2024-25 rows were updated on 2026-10-23), so every cycle is re-fetched; checked weekly. The current cycle is
in progress (2026-27: 11 rows on 2026-10-24, a few hundred samples per block).

Quirks and caveats:
- The class counts of one row do not always add up to the same total for every parameter: one sample can lack
  one parameter (2025-26 Mangrol: 3,307 samples for N but 3,306 for S). validate() allows a small difference.
- Counts are samples tested, not farms, cards or area; a block's sample count depends on the year's targets.
- The response carries database ids (_id) and a "__v" field; they are not stored.
- An unknown block name or scheme id fails the document, so codes and slugs stay stable; add it to BLOCKS or
  SCHEMES.
- The API is undocumented; it is what the public dashboard uses, with the same query text.

Licence: Government of India portal (Department of Agriculture & Farmers Welfare); no explicit open licence was
found on the portal. Aggregate public statistics, reproduced with attribution.
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `soil.shc_ec_samples` | Soil samples by salinity (EC) class | samples | 100 (100) | 11 | 2023-04-01 to 2027-03-31 | Soil samples tested in the cycle by electrical-conductivity class, dims.class (saline, non_saline), and dims.scheme. |
| `soil.shc_micronutrient_samples` | Soil samples by micronutrient sufficiency | samples | 600 (600) | 11 | 2023-04-01 to 2027-03-31 | Soil samples tested in the cycle by dims.parameter (s = sulphur, fe = iron, zn = zinc, cu = copper, b = boron, mn = manganese), dims.class (sufficient, deficient) and dims.scheme. |
| `soil.shc_npk_oc_samples` | Soil samples by N, P, K and organic-carbon class | samples | 600 (600) | 11 | 2023-04-01 to 2027-03-31 | Soil samples tested under the Soil Health Card programme in the cycle (financial year), by dims.parameter (n = available nitrogen, p = phosphorus, k = potassium, oc = organic carbon), dims.class (high, medium, low) and dims.scheme. |
| `soil.shc_ph_samples` | Soil samples by pH class | samples | 150 (150) | 11 | 2023-04-01 to 2027-03-31 | Soil samples tested in the cycle by soil reaction class, dims.class (acidic, neutral, alkaline), and dims.scheme. |

## ndma_sachet_surat

**NDMA SACHET official alerts (CAP) covering Surat district**

- **Publisher:** National Disaster Management Authority, SACHET CAP platform (alerts issued by IMD, CWC, INCOIS and State Disaster Management Authorities)
- **Page:** https://sachet.ndma.gov.in/CapFeed
- **Module:** alerts; **cadence:** hourly (checked every 1 h)
- **Geography:** Surat district: alerts whose CAP area lists LGD district code 459 or names Surat.
- **Licence:** RSS feed states "public domain"; official Government of India warnings
- **Enabled:** yes; **last success:** 2026-10-24T22:00:32+05:30
- **Holds:** 0 observations
- **Notes:** Only RSS items from Gujarat/Ahmedabad agencies or with Surat/Gujarat in the title are opened (at most 20 per run). Records are alert history keyed by the SACHET guid (an update is a new version). Counts are per alert and day; "active now" is computed from the records' effective/expires.

<details><summary>How it is collected and parsed</summary>

```text
NDMA SACHET: official disaster alerts (CAP 1.2) that cover Surat district.

Publisher: National Disaster Management Authority (NDMA), Government of India, through SACHET, the national
Common Alerting Protocol (CAP) platform built by C-DOT. The alerts themselves are issued by IMD centres
(for Gujarat: IMD Ahmedabad), the Central Water Commission (CWC), INCOIS and State Disaster Management
Authorities (Gujarat SDMA); in the alert files checked, the state SDMA had re-issued the IMD alert with a
local-language block added.

Endpoints (both plain GETs, no key; robots.txt is absent, i.e. nothing is disallowed):
  RSS  https://sachet.ndma.gov.in/cap_public_website/rss/rss_india.xml
       RSS 2.0, <copyright>public domain</copyright>; the newest 100 items for all of India (about 17 hours
       of alerts on 23-24 Oct 2026, none for Gujarat). Each <item>:
         title     the alert headline (English or a regional language)
         category  CAP category ("Met")
         link      https://sachet.ndma.gov.in/cap_public_website/FetchXMLFile?identifier=<guid>
         author    "controlroom@ndma.gov.in (IMD Mumbai)": NDMA's address and, in brackets, the originating agency
         guid      a number such as 1792759763404029 (it appears to start with the creation time in ms)
         pubDate   RFC 822 time (GMT)
  CAP  https://sachet.ndma.gov.in/cap_public_website/FetchXMLFile?identifier=<guid>
       One CAP 1.2 <cap:alert>: identifier ("IN-1792759763404029_29"), sender ("Maharashtra-SDMA"), sent,
       status (Actual/Exercise/Test/...), msgType (Alert/Update/Cancel), scope, references
       ("IMD-Mumbai,IN-1792759763404029_46,2026-10-23T18:18:56+05:30"), and one <cap:info> per language with
       category, event, urgency, severity, certainty, effective, onset, expires, headline, description,
       instruction, a "Polygon URL" parameter and <cap:area> (areaDesc, geocode "LGD District Code" values).
       The guid identifies the alert THREAD: the URL returns the thread's latest message, so after an SDMA
       re-issue (msgType Update) the same URL serves the SDMA message, whose references name the IMD original
       (same number, other suffix). SACHET's "CAP XML Feed Integration Guide for Agencies" asks consumers to
       send If-None-Match with the last ETag (304 when unchanged); the fetcher does that.
SACHET is reported to block bursts of requests (not tested here): requests are spaced by the fetcher's
per-host delay, at most MAX_CAPS alert files are requested per run, and a 403/429 stops the run.

Which alerts are fetched and stored:
1. From the RSS, only items that might concern Surat: the agency in the author brackets names Gujarat or
   Ahmedabad (Gujarat SDMA, IMD Ahmedabad), or the title names Surat or Gujarat ("Surat" as a whole word, so
   not "Suratgarh"; also Gujarati સુરત / ગુજરાત). Alerts from other agencies whose RSS title does not name
   Surat or Gujarat are assumed not to cover Surat (a known limitation; CWC and INCOIS titles name the place).
2. A fetched alert is stored only if its CAP area covers Surat district: a geocode "LGD District Code" 459
   (Surat district's Local Government Directory code, as tagged ref:LGD:district on the OpenStreetMap
   boundary saved in reference/district-modules/osm-surat-ahmedabad-admin-boundaries-tags-2026-09-27.json),
   or an areaDesc that names Surat (whole word, or સુરત). The polygon file (FetchPolygonXMLFile) is not
   fetched: SACHET lists the districts it covers as geocodes, and fetching polygons would double the requests.
   Only status "Actual" is stored (Test/Exercise/Draft/System messages are ignored).

What is stored (geography surat_district):
- one 'cap_alert' record per alert thread, keyed by the guid, so a re-issue or update is a new version of
  the same record. Attributes: alert_id, identifier, sender, sent, status, msg_type, references, category,
  event, urgency, severity, certainty, effective, onset, expires (ISO, IST, minutes), headline, description,
  instruction (English info block, or the first one), headline_local + language_local (first non-English
  block), area_desc, lgd_district_codes, cap_url. CAP <contact> is never stored.
  The RSS keeps an alert for about a day, so records are history, not a complete current list: an alert is
  in effect while effective <= now < expires and its latest msg_type is not "Cancel".
- metric sachet.alerts: value 1 per alert thread on the day (IST) of its latest message, with dims.alert =
  the guid and dims.severity = CAP severity in lower case (extreme, severe, moderate, minor, unknown).
  Summing gives the number of alerts for Surat per day, by severity. A Cancel adds no count. If an update on
  the same day changes the severity, both severities stay stored for that day (observations are never
  deleted): count distinct dims.alert for an exact daily total. "Active now" comes from the records.
  (Counts across several alerts cannot be computed in parse(), which sees one document at a time.)

Cadence: alerts are continuous (IMD nowcasts are valid for about 3 hours); the RSS covers about a day, so an
hourly refresh misses nothing. Outside the monsoon there is usually nothing for Surat and nothing is stored.

Licence: the RSS feed states "public domain"; the alerts are official Government of India warnings.
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `sachet.alerts` | Official alerts for Surat district (SACHET) | alerts | 0 |  |  | Value 1 for each SACHET alert thread whose CAP area covers Surat district, on the IST day of its latest message; dims.alert = SACHET guid, dims.severity = CAP severity (extreme, severe, moderate, minor, unknown). Sum for alerts per day or per severity; Cancel messages add nothing. |

## smc_helplines

**SMC emergency and helpline numbers**

- **Publisher:** Surat Municipal Corporation
- **Page:** https://www.suratmunicipal.gov.in/Home/EmergencyContactNo
- **Module:** citizen; **cadence:** static (checked every 168 h)
- **Geography:** SMC city; zone control-room lines carry a zone_code where the (older) zone name maps to one
- **Licence:** Surat Municipal Corporation web page; public information
- **Enabled:** yes; **last success:** 2026-10-24T22:00:38+05:30
- **Holds:** 0 observations; records: smc_helpline (30)
- **Notes:** Numbers are kept as printed (ranges not expanded; 7-digit numbers are Surat 0261 landlines). The zone section uses old zone names: "East Zone" gets no zone_code. /Home/TollFreeNumbers duplicates the toll-free lines and is not fetched.

<details><summary>How it is collected and parsed</summary>

```text
SMC emergency and helpline numbers: zone control rooms, complaint helplines, fire, ambulance, hospitals.

Publisher: Surat Municipal Corporation (the "Emergency/Imp. Nos." page under "Contact Us" on the SMC site).

Endpoint: one plain GET, no parameters, no login or captcha (robots.txt on www.suratmunicipal.gov.in returns 404,
so nothing is disallowed):

    https://www.suratmunicipal.gov.in/Home/EmergencyContactNo

The sibling page /Home/TollFreeNumbers lists the same three toll-free numbers that appear here under "SMC Help
Line", so it is not fetched.

Response layout (server-rendered HTML, no tables), two sections of boxes:

    <h2>Zone-wise Emergency/Imp Nos.</h2>   ... <h2>Other Emergency/Imp Nos.</h2>
    <div class="contact-block">
      <h2>Fire</h2>
      <div class="mar-b10"> <div class="text-bold">Contact Number</div> <div>101, 2414139</div> </div>
      <div> <div class="text-bold">Control Room</div> <div>2414195-96, 2423751-56 (Ext - 324), 9724346022</div> </div>

-> one 'smc_helpline' record per labelled line of a box (snapshot 2026-10-24: 30 lines in 15 boxes), keyed by
   box and label, e.g. 'fire-control-room', 'smc-help-line-for-complaint-registration'. The page is the complete
   list, so a line that disappears gets closed. Attributes:
     section    'zone' (Zone-wise Emergency/Imp Nos.) or 'other' (Other Emergency/Imp Nos.)
     service    the box title as printed: 'SMC HQ', 'Central Zone', 'Fire', 'Ambulance / Shabvahini',
                'SMIMER Hospital', 'Complaint Registration via WhatsApp', 'Stray Dog Bite Complaint', ...
     line       the label as printed: 'Contact Number', 'Control Room', 'Central Control Room',
                'For Complaint Registration', 'WhatsApp Number', 'Tele-Medicine Helpline No.', ...
     numbers    the entries as printed, split at commas outside brackets (so '2423751 to 56 (Ext - 205, 421, 422,
                423)' stays one entry); ranges such as '9724346030-33' are not expanded; 7-digit numbers are
                Surat landlines (STD code 0261)
     toll_free  True when an entry is marked '(Toll Free)'
     hours      service hours printed in square brackets ('6:00 am to 10:00 pm'), else None
     zone_code  zone section only: the canonical code from surat.zone_code() when the title maps to one
   Mobile numbers are kept: on this page every one of them is printed as the number of a control room, hospital
   or helpline, not of a person.

Quirks: the zone section still uses the older seven-zone names, from before the East and South zones were each
split in two (Central, East, South West, West, North, South, South East). 'South Zone' maps to code 'south'
(Udhna, before its split into South-A and South-B). 'East Zone' has no
code: the corporation's zone list has only East-A and East-B now, and the page does not say which one is meant
(its numbers are those of the East Zone A office), so zone_code is None rather than a guess. 'SMC HQ' also has no
zone code. The footer "Last Updated" is the CMS edit time, not a data date; it is not used.

No observations are emitted: this is reference data, not a time series.
Geography: SMC city and its zones (records only). Cadence: static reference data, edited without schedule;
checked weekly.
Licence: Surat Municipal Corporation web page; public information. No explicit licence.
```

</details>

## smc_council

**SMC council: corporators, office bearers and ward-wise seats/voters**

- **Publisher:** Surat Municipal Corporation (Elected Wing; Election & Census Department)
- **Page:** https://www.suratmunicipal.gov.in/Corporation/Corp_list
- **Module:** council; **cadence:** weekly (checked every 168 h)
- **Geography:** SMC election wards (smc_ward, codes 1-30) and the SMC city area (totals row of the 2021 statement)
- **Licence:** Surat Municipal Corporation web pages; public information about elected representatives
- **Enabled:** yes; **last success:** 2026-10-18T12:09:20+05:30
- **Holds:** 395 observations; records: corporator (120), office_bearer (4)
- **Notes:** Corporators: names and wards only, from Corp_list (2026-31 term; matches Gujarat Gazette Ex. 357 of 28-04-2026). Party is not published on Corp_list and is not stored. Office bearers: designation, name, ward and official email only; residential addresses and mobile numbers printed on the page are deliberately not stored. Seats/voters: 2021 general election statement (roll as on 01-01-2021, population per Census 2011 on the 2020 ward limits); its ward numbers/names match the 2026 list one-to-one, but boundary identity between the 2021 and 2026 elections is not independently verified. The ward table counts 2 SC and 5 ST seats, while SMC's past-elections summary page says 3 SC and 4 ST for 2021; the ward table is stored as published.

<details><summary>How it is collected and parsed</summary>

```text
SMC elected wing: corporators (2026-31 term), office bearers, and the 2021 ward-wise seats/voters statement.

Three SMC pages, each parsed on its own (parse() recognises the page from its content):

1. Corp_list ("Ward wise list of Corporators"): 30 blocks
       <h3>Ward No. N - <ward name></h3> <ul> <li><form ...><button>MRS FIRST MIDDLE LAST</button></form></li> x4 </ul>
   -> 'corporator' records keyed ward-<n>-<name-slug> (survives re-ordering of the list), plus the 30
      smc_ward geographies. The page is the complete current list, so people who drop off it get closed.
      Only the ward and the published name are stored. The per-corporator detail pages (POST + anti-forgery
      token) are NOT fetched: they are not needed and carry personal details.

2. OfficeBearers: <h2>Designation</h2> <h3>Smt./Shri Name</h3> <p><b>Ward:</b> ..</p> <p><b>Email:</b> ..</p>
   -> 'office_bearer' records keyed by designation slug (e.g. 'mayor'), so a change of office holder shows up
      as a new version of the same role. The page also prints each office bearer's residential address and
      personal mobile number; those fields are never read (whitelist of 'Ward' and 'Email' only), and an
      email is kept only when it is on an official government domain.

3. ElectionCensusWardwiseAllotmentSeats ("Statement Showing Situation of Seats & Nos. of Voters"), 2021 election:
   one table, 30 ward rows + a totals row:
       Ward No. | Ward Name | Ward Population (2011 Census, 2020 limits) | seat 1 (women) | seat 2 (women)
       | seat 3 | seat 4 | Male / Female / Third Gender / Total Voters as on date 01-01-2021
   -> numeric observations per smc_ward (and smc_city from the published totals row).
   The 2021 statement uses the same 30 ward numbers and names (spelling variants only) as the 2026-31
   corporator list, so it is filed under smc_ward. validate() re-checks that name correspondence on every
   fetch and fails loudly if it ever breaks (e.g. the page is replaced after a re-delimitation).
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `election.seats` | Council seats by reservation category | seats | 240 (240) | 30 | 2021-01-01 to 2021-01-01 | Seats allotted in the ward for the general election that used the electoral roll of the period date, by dims.category (general, sc, st, obc) and dims.women_reserved (yes = seat reserved for women, no = open seat). Counted from the per-seat allotment columns; all four seats of every ward are listed, so a 0 is a published fact, not a gap. |
| `election.voters` | Registered voters | voters | 31 (31) | 31 | 2021-01-01 to 2021-01-01 | Total voters on the electoral roll as on the period date. smc_city is the published total row. |
| `election.voters_by_gender` | Registered voters by gender | voters | 93 (93) | 31 | 2021-01-01 to 2021-01-01 | Voters on the electoral roll as on the period date, by dims.gender (male, female, third_gender). |
| `election.ward_population` | Ward population (Census 2011, election-ward limits) | persons | 31 (31) | 31 | 2011-03-01 to 2011-03-01 | Population as per Census 2011 re-aggregated to the election-ward limits after the 2020 city-limit extension, as used for seat allotment. smc_city is the published total row. |

## smc_past_elections

**SMC past municipal elections (1969-2021)**

- **Publisher:** Surat Municipal Corporation, Election & Census Department
- **Page:** https://www.suratmunicipal.gov.in/Departments/ElectionCensus/ElectionCensusPastMunicipalElections
- **Module:** council; **cadence:** static (checked every 720 h)
- **Geography:** SMC city: the corporation area as it was at each election (limits grew in 2006 and 2020)
- **Licence:** Surat Municipal Corporation web page; public information
- **Enabled:** yes; **last success:** 2026-10-24T22:44:26+05:30
- **Holds:** 95 observations; records: municipal_election (11)
- **Notes:** Eleven elections, 1969 to the "2020" election polled on 21.02.2021; the April 2026 election is not listed yet. "---" cells are stored as not_reported. No turnout or party results are published. The 2020 SC/ST counts (3/4) differ from the ward-wise seat table (2/5); both are stored as published.

<details><summary>How it is collected and parsed</summary>

```text
SMC past municipal elections: poll date, wards, voters, seats and reserved seats for every election since 1969.

Publisher: Surat Municipal Corporation, Election & Census Department.

Endpoint: one plain GET, no parameters, no login or captcha (the SMC robots.txt URL serves a 404 page, so nothing
is disallowed):

    https://www.suratmunicipal.gov.in/Departments/ElectionCensus/ElectionCensusPastMunicipalElections

Response layout (ASP.NET HTML). Under the heading "Details of Elections held from 01.10.1966 (Municipality
converted to Municipal Corporation)" there is one table, a header row and one row per election (11 rows on
2026-10-24):

    Sr. No. | Election Year | Election Date | No. of Election Wards | Total Voters | Total no. of Seats |
    No. of Seats Reserved for SC | No. of Seats Reserved for ST | No. of Seats Reserved for OBC |
    No. of Seats Reserved for Female
    1.  | 1969 | 08.06.1969 | 14 | 1,63,276  | 51  | 2            | 4            | ---           | ---
    11. | 2020 | 21.02.2021 | 30 | 32,88,173 | 120 | 3 (2 Female) | 4 (2 Female) | 12 (12 Female) | 60

A "Note:" block follows the table. Its lines "After the 2010 elections, the first meeting of the General Board was
held on 15.12.2010." are read; the other two lines (the voting age was 21 until 1975 and 18 from 1978) are not.

Observations, all at smc_city/smc, each an instant period on the poll date ("Election Date"):
    election.past_wards                number of election wards ("No. of Election Wards")
    election.past_voters               voters on the roll for that election ("Total Voters")
    election.past_seats                council seats filled at that election ("Total no. of Seats")
    election.past_reserved_seats       seats reserved per dims.category: sc, st, obc (the number before the
                                       bracket) and women ("No. of Seats Reserved for Female", all women's seats
                                       including those inside the SC/ST/OBC quotas)
    election.past_reserved_seats_women for dims.category sc, st, obc: how many of that category's seats were also
                                       reserved for women, the "(n Female)" part of the cell. Emitted only where
                                       the page prints the bracket (from 1995); a plain "2" does not say
                                       anything about women, so nothing is emitted for it.
A "---" or "-" cell (OBC and women before 1995, SC in 2008) is stored as not_reported with no value. Women's and
OBC reservation in municipal bodies came with the 74th Constitutional Amendment (1992), so for the early elections
"---" most likely means "no such reservation", but the page does not say so and 0 is not stored.

Records: 'municipal_election', one per row, keyed by the "Election Year" label (e.g. '2020'); the page is the
complete list, so a row that disappears gets closed. Attributes:
    election_year        the label as printed ('2020'); SMC names an election after the year it was due
    poll_date            ISO date of the poll ('2021-02-21')
    first_board_meeting  ISO date of the first General Board meeting after it, only where the Note gives one
                         (2010, 2015 and 2020 elections), as printed

Units: wards, voters and seats are counts. Geography: the SMC area as it was at each election; the city limits
grew in 2006 and again in 2020, so the rows are not comparable in area. Cadence: one new row per election (every
five years); the page was last edited on 03-07-2023 (footer "Last Updated", not used as a data date), so the
April 2026 general election is NOT listed yet. Checked monthly.

Quirks, kept as published:
- The "2020" election was polled on 21.02.2021 (postponed during COVID-19); the year label and the date differ.
- 2008 (17.02.2008) has only 4 wards, 5,34,910 voters and 12 seats. It is not a full general election; it looks
  like the election for the area added to SMC in 2006 (34 + 4 = 38 wards in 2010), but the page does not say so.
- 2010 voters are printed as a round 24,20,000.
- For 2020 the page counts 3 SC and 4 ST seats, while SMC's ward-wise seat table (loaded by smc_council as
  election.seats) counts 2 SC and 5 ST. Both are stored as published.
- For 2020 the Note says the first General Board meeting was on 12.03.2020, before the 21.02.2021 poll; it is
  most likely 12.03.2021, but it is stored as printed.
- No turnout, votes polled or party results are published on this page, so none are stored.

Licence: Surat Municipal Corporation web page ("Copyright 2026@SMC, All rights reserved"); public information about
municipal elections, reproduced as facts with attribution.
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `election.past_reserved_seats` | Reserved seats (past SMC elections) | seats | 44 (35) | 1 | 1969-06-08 to 2021-02-21 | Seats reserved at the SMC election polled on the period date, by dims.category: sc, st, obc (the number before the bracket) or women (all seats reserved for women, including those within the SC/ST/OBC quotas). "---" or "-" on the page is stored as not_reported. |
| `election.past_reserved_seats_women` | Reserved seats also reserved for women (past SMC elections) | seats | 18 (18) | 1 | 1995-06-12 to 2021-02-21 | Of the seats reserved for dims.category (sc, st, obc), how many were also reserved for women: the "(n Female)" note in the cell. Only where the page prints that note (1995 onwards, except 2008). |
| `election.past_seats` | Council seats (past SMC elections) | seats | 11 (11) | 1 | 1969-06-08 to 2021-02-21 | Total council seats filled at the SMC election polled on the period date ("Total no. of Seats"). |
| `election.past_voters` | Voters (past SMC elections) | voters | 11 (11) | 1 | 1969-06-08 to 2021-02-21 | Total voters on the electoral roll for the SMC election polled on the period date ("Total Voters"). |
| `election.past_wards` | Election wards (past SMC elections) | wards | 11 (11) | 1 | 1969-06-08 to 2021-02-21 | Number of election wards at the SMC election polled on the period date ("No. of Election Wards"). |

## gujcourts_surat

**Surat district courts: institution, disposal and case clearance rate**

- **Publisher:** District Judiciary of Gujarat (High Court of Gujarat), Virtual Justice Clock
- **Page:** https://gujcourts.guj.nic.in/dc_justice_clock/dc_institute_disposal_ccr.php?authority=GJSR01&estcode=ALL
- **Module:** courts; **cadence:** daily (checked every 24 h)
- **Geography:** Surat district (all establishments under District Court-Surat) and each court establishment
- **Licence:** Public court statistics published by the Gujarat district judiciary
- **Enabled:** yes; **last success:** 2026-10-18T11:02:06+05:30
- **Holds:** 270 observations
- **Notes:** Windows (Today ... Last Year) are as labelled by the publisher, relative to the clock date; their exact boundaries are not published. 15 GET requests per run (the district total and 14 establishments).

<details><summary>How it is collected and parsed</summary>

```text
Surat district courts: cases instituted, disposed and the case clearance rate (Virtual Justice Clock).

Page: https://gujcourts.guj.nic.in/dc_justice_clock/dc_institute_disposal_ccr.php?authority=GJSR01&estcode=ALL
"Virtual Justice Clock for District Judiciary of Gujarat - Institution, Disposal & Case Clearance Rate".
A plain PHP page (robots.txt is absent, so nothing is disallowed; no login or captcha):

    <select id="estlist1"> <option value='ALL'>ALL ESTABLISHMENTS UNDER DISTRICT COURT-SURAT</option>
                           <option value='GJSR15'>SMALL CAUSE COURT-SURAT</option> ... 14 establishments </select>
    table: DURATION | INSTITUTION | DISPOSAL | CCR
           Today | 275 | 77 | 28%      Last Day | ...   Last Week | ...   Last Month | ...
           This Year | ...              Last Year | 434812 | 433874 | 100%
    <p id="date">27/09/2026</p>          (the clock's date; JavaScript later overwrites it with the browser time)

The same URL with estcode=GJSR15 (etc.) returns one establishment, with that option marked selected='selected'.
fetch() takes the establishment list from the ALL page's dropdown and requests each one, so 15 documents per run.

-> ALL page: surat_district/surat (every establishment is in Surat district: Surat city courts plus the taluka
   courts of Olpad, Mangrol, Mandvi, Bardoli, Mahuva, Palsana, Kathor and Umarpada).
-> each establishment: geo level court_establishment, code = the lower-cased eCourts establishment code
   ('gjsr15'), parent surat_district/surat.

Periods: the page does not define its windows ("Last Week" = previous calendar week or last 7 days?). The ALL
figures for "Last Year" were identical on 2026-09-27 and 2026-10-17 and "Last Month" jumped from 13,223 to
184,195 institutions between those dates, which suggests calendar periods, but that is not published. So every
value is filed as an instant reading on the clock date with the window in dims.window (today, last_day,
last_week, last_month, this_year, last_year), and publisher_as_of = the clock date. "Today" is a running count
that can still grow after the fetch; a later fetch on the same clock date updates it (kept as a revision).
The clock date does not roll over at IST midnight: a fetch at 00:58 IST on 2026-10-18 still showed 17/10/2026.

The district (ALL) figures are the sum of the 14 establishments: on clock date 2026-10-17 they matched exactly in
every window for both counts. The dashboard must not add the two levels together.

CCR is published as a whole percent (disposal / institution); "--" (e.g. 1 instituted, 0 disposed) is stored as
not_reported. Pendency is not on this page (the page's script loads it from a separate POST endpoint,
reloadframependency.php, for another view), so none is stored.
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `courts.cases_disposed` | Cases disposed | cases | 90 (90) | 15 | 2026-10-18 to 2026-10-18 | Cases disposed of in the window dims.window, as shown on the Virtual Justice Clock on the clock date. |
| `courts.cases_instituted` | Cases instituted | cases | 90 (90) | 15 | 2026-10-18 to 2026-10-18 | Cases instituted (filed) in the window dims.window, as shown on the Virtual Justice Clock on the clock date (period). Windows: today, last_day, last_week, last_month, this_year, last_year. |
| `courts.clearance_rate_pct` | Case clearance rate | % | 90 (69) | 15 | 2026-10-18 to 2026-10-18 | Case clearance rate (disposed / instituted, whole percent as published) in the window dims.window. not_reported where the page shows "--". |

## njdg_surat

**Surat district courts: pendency, age, stage and case type (NJDG)**

- **Publisher:** National Judicial Data Grid (eCourts project, e-Committee of the Supreme Court of India; NIC)
- **Page:** https://njdg.ecourts.gov.in/njdg_v3/?p=home/index&state_code=24~17&dist_code=14
- **Module:** courts; **cadence:** daily (checked every 24 h)
- **Geography:** Surat district: all court establishments under District Court Surat (city and taluka courts)
- **Licence:** No licence stated; public aggregate statistics of the Government of India eCourts project. Attribute "National Judicial Data Grid (NJDG)".
- **Enabled:** yes; **last success:** 2026-10-24T22:00:33+05:30
- **Holds:** 158 observations
- **Notes:** Two requests per run: the district page (GET) and the pending-dashboard JSON (POST). No login, captcha or token is needed for either; NJDG case lists (captcha) are never requested. Snapshot figures are dated to the page's "Last Updated" date. Age bands are counted in calendar years of institution. Do not add these figures to gujcourts_surat (same courts).

<details><summary>How it is collected and parsed</summary>

```text
Surat district courts: pending cases (civil/criminal, by age, stage and case type) from the National Judicial Data Grid.

Publisher: National Judicial Data Grid (NJDG), part of the eCourts project of the e-Committee, Supreme Court of
India; built and hosted by the National Informatics Centre (NIC). NJDG aggregates the case data that each court
establishment uploads from its Case Information System (CIS).

Two requests per run, both to njdg.ecourts.gov.in (robots.txt returns 404, so nothing is disallowed). Neither
needs a login, a captcha, a cookie or a token. NJDG's case LISTS (the pop-ups that open when a figure is clicked,
and the case search) are behind a captcha; this adapter never calls them and stores aggregate counts only.

1. District page (HTML, GET):
       https://njdg.ecourts.gov.in/njdg_v3/?p=home/index&state_code=24~17&dist_code=14
   state_code '24~17' = Gujarat and dist_code '14' = SURAT, as in the page's own state/district dropdowns (both
   are marked "selected" on the page, and parse() checks that). The page is server-rendered:
       cards      "Civil Cases 32,002" | "Criminal Cases 1,08,352" | "Total Cases 1,40,354" | "Pre-Litigation / Pre-Trial"
       "Age wise pending cases"   Civil | Criminal | Total, one block per band:
                                  "Less than one year" 15,319 | 53,964 | 69,283 (49%)   ... "Above 10 Years"
       "Instituted in last month"  1,248 | 1,83,355 | 1,84,603        (Civil | Criminal | Total)
       "Disposal in last month"    1,565 | 1,95,082 | 1,96,647, then "Contested" and "Uncontested" blocks
       "Cases Listed Today", "Undated", "Excessive Dated Cases", "Cases Filed By Woman",
       "Cases Filed By Senior Citizen"   (each Civil | Criminal | Total, captioned "N% of Total Pending Cases")
       footer     "Last Updated : 23-10-2026"
   The page is read as visible text (parse.html_text), one value per line, taking the FIRST block with each
   label: the page repeats several blocks inside hidden layout copies (one hidden "Undated" copy is blank).
   A commented-out "Alerts" table in the HTML carries much larger numbers (e.g. "Cases Pending Registration
   900637"); HTML comments are not part of the visible text, so it is never read.

2. Pending dashboard (JSON, POST), what the page's "Pending Dashboard" tab loads:
       POST https://njdg.ecourts.gov.in/njdg_v3/?p=home/newPendDashboard
       form: ci_cri=1 (1 = civil and criminal together, 2 = civil, 3 = criminal), stage_ready=3, active_tab=pending,
             state_code=24~17, dist_code=14, ajax_req=true, app_token= (empty; the page's own token field is empty)
   The answer (served as text/html, with leading blank lines) is one JSON object of "~"-separated strings, labels
   quoted with "#" for spaces, e.g.
       "purpose_name": "\"Process#Issue\"~\"Witness#Exmn.\"~...",   "purpose_count": "70020~45947~..."
   Fields used:  purpose_name/purpose_count  (pending by stage, i.e. the purpose of the next hearing),
                 purposename/stagewise_count (NJDG's four stage groups), mattertype/cases_count (by case type),
                 caseChartcount (HTML table: Original / Appeal / Application / Execution),
                 year/year_count (pending by year of institution), insyear/ins_count/disp_count (cases instituted
                 and disposed per calendar year since 2018).
   Not used: delayName/delay_count. Those counts (6,866,010 for one reason on 2026-10-23) are far larger than the
   district's 1.4 lakh pending cases, so they are not Surat figures.
   The JSON names neither the district nor a date, so fetch() passes the page's "Last Updated" date and its total
   pending count in meta (as_of, pending_total); validate() requires the JSON totals to match the page.

Metrics (geo surat_district/surat; every establishment under District Court Surat: the Surat city courts and the
taluka courts). dims.civil_criminal is civil / criminal / total, as published (total = civil + criminal):
  njdg.pending_cases                    pending cases
  njdg.pending_by_age                   pending cases by dims.age_band (lt_1y, 1_3y, 3_5y, 5_10y, gt_10y)
  njdg.instituted_last_month            cases instituted "in last month"
  njdg.disposed_last_month              cases disposed "in last month", dims.disposal all / contested / uncontested
  njdg.pending_filed_by_women           pending cases filed by women ("Cases Filed By Woman")
  njdg.pending_filed_by_senior_citizens pending cases filed by senior citizens
  njdg.cases_listed_today               pending cases on the day's cause lists ("Cases Listed Today")
  njdg.undated_cases                    pending cases with no next hearing date
  njdg.excessive_dated_cases            pending cases whose next date is more than 3 months away
  from the JSON (civil and criminal together, no civil_criminal split):
  njdg.pending_by_stage, njdg.pending_by_stage_group, njdg.pending_by_case_type, njdg.pending_by_case_category,
  njdg.pending_by_filing_year, njdg.instituted_by_year, njdg.disposed_by_year
Units: cases. Snapshot figures are instant readings on the "Last Updated" date (publisher_as_of = that date).
Yearly flows have the calendar year as their period; the current year is year-to-date and grows until December.

Cadence: daily. The page shows only a date, no time. The footer read 23-10-2026 at 2026-10-24 02:02 IST, so it
is not a static edit date. An earlier read by the project's research step showed the same date with different
figures (pending 1,39,976 then, 1,40,354 at 02:02), so the figures can change more than once under one date
(the research notes say the courts' data is read twice a day). A later fetch for the same date is kept as a
revision.

Quirks and caveats:
- Age bands are counted in calendar years of institution, not exact days: on 2026-10-23 "Less than one year"
  (69,283) equals the cases instituted in 2026 plus 2025 (39,539 + 29,744), "1 to 3 Years" equals 2024 + 2023,
  and so on. A case filed in January 2025 is "less than one year" old until the end of 2026.
- The page's age bands add up to 2 more than its own totals (criminal 1,08,354 vs 1,08,352; total 1,40,356 vs
  1,40,354; "Above 10 Years" is 4,420 on the page but 4,418 in the JSON). Stored as published.
- The four stage groups add up to less than the total (1,39,969 vs 1,40,354 on 2026-10-23); the 26 detailed
  stages add up exactly. Stage names are NJDG's short purpose names, e.g. "Witness Exmn.", "313 Cr.PC".
- "Last month" is not defined on the page; it may not match the Virtual Justice Clock's "Last Month" window
  (source gujcourts_surat). The two sources count the same courts, so never add them together.
- Criminal institutions are very high (1,83,355 in the last month against 1,08,352 criminal cases pending, i.e.
  132% of all pending cases); most are quickly disposed petty / traffic-challan matters (98% of last month's
  disposals are uncontested).
- "Cases Filed By Woman / Senior Citizen" sit next to the last-month rows in the page's "Other Alerts" table, but
  their cards say "N% of Total Pending Cases"; they are read as pending cases filed by women / senior citizens.
- "Cases Listed Today" is filed under the "Last Updated" date; the page does not say which day "today" is.
- A blank count in the visible "Undated" card (only its hidden "Civil Count" caption left) is stored as
  not_reported, never 0. Any other blank or non-numeric block fails the document.
- If two stages (or case types, stage groups, years) decode to the same short name, their counts are added
  so the key stays unique (none did on 2026-10-23).
- "Excessive Dated Cases" is defined as "More than 3 Months" only in the page's commented-out Alerts table.
- The "Pre-Litigation / Pre-Trial" card (1,327) is not stored: the page does not define it.
- normalize() blanks the per-request script cache-buster (ecourts.js?v=...) and the server name in the footer
  ("S2", "S3"), so an unchanged page is archived once.

Licence: no open-data licence is stated on the dashboard page. The figures are public aggregate statistics
published by the eCourts project (Government of India); attribute "National Judicial Data Grid (NJDG)".
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `njdg.cases_listed_today` | Pending cases listed today (NJDG) | cases | 3 (3) | 1 | 2026-10-23 to 2026-10-23 | Pending cases on the cause lists of the day ("Cases Listed Today"), filed under the "Last Updated" date, by dims.civil_criminal. |
| `njdg.disposed_by_year` | Cases disposed per year (NJDG) | cases | 9 (9) | 1 | 2018-01-01 to 2026-12-31 | Cases (civil and criminal) disposed of in the calendar year. The current year is year-to-date. |
| `njdg.disposed_last_month` | Cases disposed in the last month (NJDG) | cases | 9 (9) | 1 | 2026-10-23 to 2026-10-23 | Cases disposed of "in last month", by dims.civil_criminal and dims.disposal (all, contested, uncontested; contested + uncontested = all). |
| `njdg.excessive_dated_cases` | Pending cases with a next date over 3 months away (NJDG) | cases | 3 (3) | 1 | 2026-10-23 to 2026-10-23 | Pending cases whose next hearing date is more than 3 months away ("Excessive Dated Cases"), by dims.civil_criminal. |
| `njdg.instituted_by_year` | Cases instituted per year (NJDG) | cases | 9 (9) | 1 | 2018-01-01 to 2026-12-31 | Cases (civil and criminal) instituted in the calendar year. The current year is year-to-date (see publisher_as_of) and is revised as the year goes on. |
| `njdg.instituted_last_month` | Cases instituted in the last month (NJDG) | cases | 3 (3) | 1 | 2026-10-23 to 2026-10-23 | Cases instituted "in last month" as shown on the "Last Updated" date, by dims.civil_criminal. NJDG does not define the window. |
| `njdg.pending_by_age` | Pending cases by age (NJDG) | cases | 15 (15) | 1 | 2026-10-23 to 2026-10-23 | Pending cases by age band (dims.age_band: lt_1y, 1_3y, 3_5y, 5_10y, gt_10y) and dims.civil_criminal. NJDG counts age in calendar years of institution: lt_1y = instituted this year or last year. |
| `njdg.pending_by_case_category` | Pending cases by case category (NJDG) | cases | 4 (4) | 1 | 2026-10-23 to 2026-10-23 | Pending cases (civil and criminal) by category (dims.case_category: original, appeal, application, execution). The categories add up to the total pending. |
| `njdg.pending_by_case_type` | Pending cases by case type (NJDG) | cases | 22 (22) | 1 | 2026-10-23 to 2026-10-23 | Pending cases (civil and criminal) by CIS case type (dims.case_type, e.g. "MAGISTRIAL CASES", "CIV SUITS", "MACP"), names as published. |
| `njdg.pending_by_filing_year` | Pending cases by year of institution (NJDG) | cases | 39 (39) | 1 | 2026-10-23 to 2026-10-23 | Pending cases (civil and criminal) by the year the case was instituted (dims.filing_year). |
| `njdg.pending_by_stage` | Pending cases by stage (NJDG) | cases | 26 (26) | 1 | 2026-10-23 to 2026-10-23 | Pending cases (civil and criminal) by stage, i.e. the purpose of the next hearing (dims.stage, NJDG's short name such as "Process Issue" or "Witness Exmn."). The stages add up to the total pending. |
| `njdg.pending_by_stage_group` | Pending cases by stage group (NJDG) | cases | 4 (4) | 1 | 2026-10-23 to 2026-10-23 | Pending cases (civil and criminal) by NJDG's stage group (dims.stage_group: Appearance/Service Related, Compliance/Steps/stay, Evidence/Argument/Judgement, Pleadings/Issues/Charge). The groups add up to slightly less than the total pending. |
| `njdg.pending_cases` | Pending cases (NJDG) | cases | 3 (3) | 1 | 2026-10-23 to 2026-10-23 | Cases pending in the district courts on the "Last Updated" date, by dims.civil_criminal (civil, criminal, total). |
| `njdg.pending_filed_by_senior_citizens` | Pending cases filed by senior citizens (NJDG) | cases | 3 (3) | 1 | 2026-10-23 to 2026-10-23 | Pending cases filed by senior citizens ("Cases Filed By Senior Citizen", shown as a share of total pending cases), by dims.civil_criminal. |
| `njdg.pending_filed_by_women` | Pending cases filed by women (NJDG) | cases | 3 (3) | 1 | 2026-10-23 to 2026-10-23 | Pending cases filed by women ("Cases Filed By Woman", shown as a share of total pending cases), by dims.civil_criminal. |
| `njdg.undated_cases` | Undated pending cases (NJDG) | cases | 3 (3) | 1 | 2026-10-23 to 2026-10-23 | Pending cases with no next hearing date ("Undated"), by dims.civil_criminal. |

## gseb_results

**GSEB SSC and HSC board-exam results, Surat district and exam centres (annual)**

- **Publisher:** Gujarat Secondary and Higher Secondary Education Board (GSEB), Gandhinagar
- **Page:** https://www.gseb.org/
- **Module:** education; **cadence:** annual (checked every 168 h)
- **Geography:** Surat district (GSEB district tables) and GSEB exam centres in Surat district (geo level exam_centre)
- **Licence:** Government of Gujarat (GSEB) result booklets; public information
- **Enabled:** yes; **last success:** 2026-10-18T11:01:38+05:30
- **Holds:** 428 observations
- **Notes:** Regular candidates only. Period = calendar year of the Feb-March main exam. dims.exam is ssc, hsc_science or hsc_general. Centre totals differ slightly from district totals as published.

<details><summary>How it is collected and parsed</summary>

```text
GSEB board-exam results for Surat district: SSC (class 10) and HSC (class 12, science and general).

Documents: the result-statistics booklets GSEB publishes on results day, in a per-year S3 bucket:
    https://gsebweb<YEAR>.s3.ap-south-1.amazonaws.com/pdf/sscbooklet.pdf   SSC (class 10), Feb-March exam
    https://gsebweb<YEAR>.s3.ap-south-1.amazonaws.com/pdf/scibooklet.pdf   HSC science stream
    https://gsebweb<YEAR>.s3.ap-south-1.amazonaws.com/pdf/genbooklet.pdf   HSC general stream (with the
                                                                           vocational and Uchchatar Uttar
                                                                           Buniyadi streams, as GSEB combines them)
(all three, plus *purakbooklet.pdf for the June supplementary exams, were in the 2026 bucket on 2026-10-05).
A booklet never changes once published, so each is downloaded once (skip_if_seen). fetch() asks for the
current exam year from 1 May (results come out in early May; 2026: SSC 6 May, HSC 4 May) and treats a
404 as "not published yet". GSEB_YEARS="2025,2026" overrides the years for a one-off backfill.

What is read (regular candidates; the booklets' district tables are for regular candidates):
  SSC   p.10-11 district table   "SURAT  regd appeared A-1 A-2 B-1 B-2 C-1 C-2 D E1* E1 E2 EQC PER."
        p.12   district pass % for the exam year and the two before ("30. 68 SURAT 86.04% 86.20% 86.75%")
        p.15+  centre-wise table "6810 6810 SURAT RANDER  regd appeared passed  2026%  2025%  change"
  HSC   "DISTRICTWISE GRADEWISE" table "18-SURAT regd app A1 A2 B1 B2 C1 C2 D E1 N.I. %age"
        district E.Q.C. table "18 SURAT 13,786"
        centre-wise table "1806 RANDER (SURAT) regd appeared E.Q.C. N.I. percentage"
"Passed" is GSEB's E.Q.C. (eligible for qualifying certificate). Checked on the 2026 booklets: for SSC,
A1..D plus E1* (differently-abled candidates passing with the 20% concession) = EQC and EQC + E1 + E2 =
appeared; for HSC, A1..E1 = E.Q.C. and %age = E.Q.C./appeared. HSC N.I. (needs improvement) is not
stored: it equals registered minus E.Q.C., so it counts absentees too.

Geography:
  - district rows -> surat_district/surat (SSC district 68 and HSC district 18 are Surat; Tapi, split
    off in 2007, is its own district in both booklets).
  - centre rows -> new geo level `exam_centre` (code "gseb-ssc-6810", "gseb-hsc-1806"), parent
    surat_district. A GSEB centre (kendra) groups the schools examined there; it is not an
    administrative area, and whether it lies inside SMC limits is not determined here. HSC science and
    general booklets use the same centre numbers (1802 SURAT, 1807 NANPURA (SURAT), ...), so they share a
    geo; SSC centres are numbered separately. Centre totals do not add up exactly to the district row
    (2026 SSC: 82,399 vs 82,306 registered), presumably because the district table counts candidates by
    school district and the centre table by where they sat; both are stored as published.
  - Name markers such as "(^^)" or "($)" (the year a centre opened, per the SSC legend) are dropped
    from centre names.

Periods: the calendar year of the main (February-March) examination, e.g. 2026-01-01..2026-12-31.
The SSC booklet's pass % for the two previous years and each centre's previous-year pass % are stored
for those years too.
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `gseb.appeared` | Board-exam candidates appeared | candidates | 88 (88) | 76 | 2026-01-01 to 2026-12-31 | Regular candidates who appeared (dims.exam). |
| `gseb.candidates_by_grade` | Board-exam candidates by grade | candidates | 26 (26) | 1 | 2026-01-01 to 2026-12-31 | District candidates by grade as printed (dims.grade). SSC: A1..D and E1* (differently-abled, passed with the 20% concession) are passes, E1 and E2 are not. HSC: A1..E1 add up to E.Q.C. |
| `gseb.pass_pct` | Board-exam pass percentage | % | 138 (137) | 76 | 2024-01-01 to 2026-12-31 | GSEB result percentage: passed (E.Q.C.) / appeared x 100, as printed (dims.exam). |
| `gseb.passed` | Board-exam candidates passed | candidates | 88 (88) | 76 | 2026-01-01 to 2026-12-31 | Regular candidates eligible for the certificate (GSEB "E.Q.C."), i.e. passed (dims.exam). |
| `gseb.registered` | Board-exam candidates registered | candidates | 88 (88) | 76 | 2026-01-01 to 2026-12-31 | Regular candidates registered for the main examination (dims.exam). |

## udise_surat

**UDISE+ education highlights, Surat district (annual)**

- **Publisher:** Department of School Education & Literacy, Ministry of Education, Government of India (UDISE+)
- **Page:** https://dashboard.udiseplus.gov.in/
- **Module:** education; **cadence:** annual (checked every 720 h)
- **Geography:** Surat district (UDISE+ district 2422): SMC area plus the rural talukas; not SMC city limits
- **Licence:** Government of India (MoE UDISE+) open-services API; public data
- **Enabled:** yes; **last success:** 2026-10-18T11:11:10+05:30
- **Holds:** 192 observations
- **Notes:** yearId -> FY mapping and field labels taken from the UDISE+ dashboard bundle. dpt/dmt/dst (dropout) are unlabelled on the dashboard and interpreted by analogy; see module docstring.

<details><summary>How it is collected and parsed</summary>

```text
UDISE+ "Education highlights" for Surat district: schools, enrolment, teachers, PTR, infrastructure.

Endpoint (the one dashboard.udiseplus.gov.in's report page calls; no key, no Origin/Referer needed):
    POST https://api.udiseplus.gov.in/open-services/v1.1/kpi/edu-highlights
    body {"yearId": Y, "regionCode": "2422", "regionType": 12, "valueType": 1}
    2422 = Surat district, regionType 12 = district.
Response: {"status": true, "data": [ {yearId, regionName, regionCode, totSch, ...} ], "metaData": {...}}.
"data" is an empty list for a year that has no data (checked 2026-10-05: yearId 10 and 13 are empty,
11 and 12 have data).

Year ids: the dashboard bundle (report2026/static/js/main.*.js) maps
    {12: "2025-26", 11: "2024-25", 10: "2023-24", 9: "2022-23", 8: "2021-22"},
i.e. financial-year start = 2013 + yearId. Periods are the UDISE+ year as an Indian financial year
(1 April - 31 March); UDISE+ figures are an annual snapshot of that school year.

Field meanings come from the same bundle, which labels every field shown on the dashboard
("Total Number of Schools" = totSch, "PTR at Foundational level" = foundation, "Transition Rates
Foundational to Preparatory" = tft, ...). Two exceptions, kept with that caveat in their descriptions:
  - dpt/dmt/dst are returned but not labelled on the dashboard; by analogy with tft/tmt/tst and the
    UDISE+ report tables they are read as dropout rates at the preparatory/middle/secondary stage.
  - overallScore/overallGrade are labelled "Performance Grading Index"; the 2025-26 value for Surat
    (328.84) matches the PGI-D 2025-26 report (329 of 600, Prachesta-1), so they are PGI-D for that year.
Unlabelled fields (tenrPPri, tschPpri) are not stored. A null in a labelled field is stored as
not_reported.

Geography: UDISE+ district 2422 is the whole of Surat district (SMC area plus the rural talukas),
so everything is geo surat_district/surat, never smc_city.

The response carries request/response timestamps; normalize() blanks them so an unchanged answer
is archived once.
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `udise.dropout_rate_pct` | Dropout rate | % | 6 (6) | 1 | 2024-04-01 to 2026-03-31 | Dropout rate at the preparatory / middle / secondary stage (dims.stage). API fields dpt/dmt/dst are not labelled on the UDISE+ dashboard; read as dropout rates by analogy with the UDISE+ reports. |
| `udise.enrolment` | Enrolment, foundational to secondary | students | 2 (2) | 1 | 2024-04-01 to 2026-03-31 | Total enrolment from the foundational to the secondary stage (tenrF2Sec). |
| `udise.enrolment.by_category` | Enrolment by school category | students | 20 (20) | 1 | 2024-04-01 to 2026-03-31 | Enrolment in schools of each UDISE+ school category (dims.category). As returned these do not add up to udise.enrolment (2024-25: 1,161,656 vs 1,286,170). |
| `udise.enrolment.by_management` | Enrolment by school management | students | 16 (12) | 1 | 2024-04-01 to 2026-03-31 | Enrolment by school management (dims.management, same codes as udise.schools.by_management; "govt" is a subtotal). |
| `udise.enrolment.by_social_group` | Enrolment by social group | students | 8 (8) | 1 | 2024-04-01 to 2026-03-31 | SC, ST, OBC and minority students, foundational to secondary (dims.group). Overlapping groups, not a partition of the total. |
| `udise.enrolment.by_stage` | Enrolment by NEP stage | students | 8 (8) | 1 | 2024-04-01 to 2026-03-31 | Enrolment in the foundational / preparatory / middle / secondary stage (dims.stage); the four add up to udise.enrolment. |
| `udise.enrolment.cwsn` | Children with special needs enrolled | students | 2 (2) | 1 | 2024-04-01 to 2026-03-31 | Number of CWSN students, foundational to secondary. |
| `udise.ger_pct` | Gross enrolment ratio | % | 6 (0) | 1 | 2024-04-01 to 2026-03-31 | Gross enrolment ratio at the foundational / preparatory / middle stage (dims.stage). Returned as null for districts so far (stored as not_reported). |
| `udise.pgi_d.grade` | PGI-D grade |  | 2 (2) | 1 | 2024-04-01 to 2026-03-31 | PGI-D grade as text in value_text (e.g. PRACHESTA-1 = 51-60% of the maximum score). |
| `udise.pgi_d.score` | PGI-D overall score | points (of 600) | 2 (2) | 1 | 2024-04-01 to 2026-03-31 | Performance Grading Index for Districts overall score returned for this UDISE+ year (2025-26 matches the PGI-D 2025-26 report). |
| `udise.ptr` | Pupil-teacher ratio | pupils per teacher | 8 (8) | 1 | 2024-04-01 to 2026-03-31 | Pupil-teacher ratio at the foundational / preparatory / middle / secondary level (dims.stage). |
| `udise.schools` | Schools | schools | 2 (2) | 1 | 2024-04-01 to 2026-03-31 | Total number of schools (totSch). |
| `udise.schools.by_category` | Schools by school category | schools | 20 (20) | 1 | 2024-04-01 to 2026-03-31 | Schools by UDISE+ school category, i.e. the classes offered (dims.category, e.g. upper_primary_1_8 = classes 1-8). Categories add up to all schools. |
| `udise.schools.by_management` | Schools by management | schools | 16 (16) | 1 | 2024-04-01 to 2026-03-31 | Schools by management (dims.management). "govt" is the subtotal of kendriya_vidyalaya, navodaya_vidyalaya, other_central_govt and state_govt; govt + govt_aided + private_unaided + other = all schools. |
| `udise.schools.primary_with_preprimary` | Govt and aided primary schools with Balvatika | schools | 2 (2) | 1 | 2024-04-01 to 2026-03-31 | Number of government and government-aided primary schools having Balvatika / pre-primary sections. |
| `udise.schools.with_primary` | Government / aided schools having primary levels | schools | 4 (4) | 1 | 2024-04-01 to 2026-03-31 | Number of government (dims.management=govt) or government-aided schools having primary levels. |
| `udise.schools_with_facility_pct` | Schools with a facility | % of schools | 44 (44) | 1 | 2024-04-01 to 2026-03-31 | Percentage of schools having a facility (dims.facility); dims.condition is "available" or "functional" (e.g. electricity connection vs functional electricity connection). |
| `udise.teachers` | Teachers | teachers | 2 (2) | 1 | 2024-04-01 to 2026-03-31 | Total number of teachers (ttch). |
| `udise.teachers.by_management` | Teachers by school management | teachers | 16 (16) | 1 | 2024-04-01 to 2026-03-31 | Teachers by school management (dims.management; "govt" is a subtotal). |
| `udise.transition_rate_pct` | Transition rate | % | 6 (6) | 1 | 2024-04-01 to 2026-03-31 | Transition rate between NEP stages (dims.transition, e.g. middle_to_secondary). |

## cpcb_aqi

**CPCB daily AQI bulletin and CAAQMS station feed: Surat**

- **Publisher:** Central Pollution Control Board, Government of India
- **Page:** https://airquality.cpcb.gov.in/
- **Module:** environment; **cadence:** daily (checked every 12 h)
- **Geography:** Bulletin: the "Surat" city row, stored as smc_city (its stations are in the SMC area). Feed: CPCB stations listed under Gujarat / Surat, geo level aq_station (parent surat_district).
- **Licence:** Government of India (CPCB) public bulletin and feed; CPCB asks that data use acknowledges the agencies that generate it
- **Enabled:** yes; **last success:** 2026-10-18T11:01:35+05:30
- **Holds:** 33 observations
- **Notes:** Bulletin URL by date (YYYYMMDD), immutable, fetched once. The feed is a live snapshot (hourly at source); each run stores the latest readings of the Surat stations.

<details><summary>How it is collected and parsed</summary>

```text
CPCB daily AQI bulletin (Surat row) and the CPCB CAAQMS station feed (Surat stations).

1. Daily bulletin PDF: https://cpcb.gov.in/upload/Downloads/AQI_Bulletin_YYYYMMDD.pdf
   (the cpcb.nic.in address in older links now answers 301 to cpcb.gov.in). Title on every page:
   "Air Quality Index on Sep 24, 2026 @ 4 PM (Average of past 24 hours)", then one row per city:
       S.No | City | Air Quality | Index Value | Prominent Pollutant | No. of Stations Participated/Total
   A long city name wraps around the row line ("Aurangabad" / "18 ... 84 ... 3/3" / "(Maharashtra)");
   rows are read block by block with words grouped into columns, so wrapped rows are read whole.
   After the table: "* Cities absent in AQI Bulletin due to insufficient data: 1) ..., 2) ...".
   Stored for SURAT only, as smc_city observations dated the bulletin day (publisher_as_of = the
   4 PM bulletin time). The bulletin's "Surat" is the average of CPCB's Surat stations; both stations
   CPCB lists for Surat in 2026 (Science Center - SMC, Katargam) lie inside the SMC area by their feed
   coordinates. If the bulletin lists Surat among the absent cities, cpcb.city_aqi is stored as
   not_reported with that reason.

2. Station feed JSON: https://airquality.cpcb.gov.in/caaqms/rss_feed_with_coordinates
   country[] -> stateId, citiesInState[] -> cityId, stationsInCity[] -> stationName, siteId, latitude,
   longitude, lastUpdate ("27-09-2026 12:00:00"), airQualityIndexValue, predominantParameter,
   pollutants[] -> indexId, min, max, avg, Hourly_sub_index. Fetched plainly (no key, no cookies).
   Stored for the stations under Gujarat / Surat, geo level aq_station (code = CPCB siteId, parent
   surat_district because CPCB's "Surat" label alone does not prove a station is inside SMC limits;
   coordinates are in the geo note), period = the station's lastUpdate.
   The pollutant values are on the AQI scale, not concentrations: in the 2026-09-27 snapshot and the
   2026-10-05 live feed every station's airQualityIndexValue equals the highest pollutant "avg"
   (439/439 and 459/459 stations). validate() keeps checking that for the Surat stations.
   A station that is offline drops out of the feed (Science Center was missing on 2026-10-05); nothing
   is stored for it then.

fetch(): the last 3 bulletins (skip_if_seen: a bulletin is immutable) and one feed snapshot.
Today's bulletin is only asked for after 17:00 IST; it is posted shortly after 16:00.
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `cpcb.city_aqi` | Air Quality Index (CPCB daily bulletin) | index | 3 (3) | 1 | 2026-10-15 to 2026-10-17 | City AQI in the CPCB 4 PM bulletin: average over the city's stations of the past 24 hours. not_reported (value_text = reason) when the bulletin lists the city as absent for insufficient data. |
| `cpcb.city_aqi_category` | AQI category (CPCB daily bulletin) |  | 3 (3) | 1 | 2026-10-15 to 2026-10-17 | value_text = "Air Quality" column: Good, Satisfactory, Moderate, Poor, Very Poor or Severe. |
| `cpcb.city_prominent_pollutants` | Prominent pollutant(s) (CPCB daily bulletin) |  | 3 (3) | 1 | 2026-10-15 to 2026-10-17 | value_text = "Prominent Pollutant" column as printed, e.g. "PM10, PM2.5". |
| `cpcb.city_stations_participated` | Stations in the city AQI | stations | 3 (3) | 1 | 2026-10-15 to 2026-10-17 | Number of monitoring stations that contributed to the city AQI that day ("Participated"). |
| `cpcb.city_stations_total` | Stations in the city | stations | 3 (3) | 1 | 2026-10-15 to 2026-10-17 | Number of CPCB-listed monitoring stations for the city ("Total Stations"). |
| `cpcb.station_aqi` | Station AQI (CPCB CAAQMS feed) | index | 2 (2) | 2 | 2026-10-18 to 2026-10-18 | airQualityIndexValue of the station in the CPCB feed at lastUpdate. |
| `cpcb.station_prominent_pollutant` | Station prominent pollutant (CPCB CAAQMS feed) |  | 2 (2) | 2 | 2026-10-18 to 2026-10-18 | value_text = predominantParameter of the station in the CPCB feed. |
| `cpcb.station_subindex_avg` | Pollutant sub-index, average (CPCB CAAQMS feed) | index | 14 (12) | 2 | 2026-10-18 to 2026-10-18 | The pollutant's "avg" value in the CPCB feed (dims.pollutant = the feed's indexId: PM2.5, PM10, NO2, NH3, SO2, CO, OZONE). It is on the AQI scale (the station AQI is the highest of them), not a concentration. |

## smc_air_quality

**SMC air-quality stations, past results and latest sensor reading**

- **Publisher:** Surat Municipal Corporation, Air Quality Management Cell
- **Page:** https://www.suratmunicipal.gov.in/Departments/AirQualityResults
- **Module:** environment; **cadence:** daily (checked every 6 h)
- **Geography:** Readings: one SMC sensor station inside the SMC area (geo level aq_station). Station records also list GPCB manual stations in Surat district outside SMC (Chalthan and Baleshwar, Palsana taluka).
- **Licence:** Surat Municipal Corporation web pages and the JSON feed behind its results page; public information
- **Enabled:** yes; **last success:** 2026-10-18T11:02:12+05:30
- **Holds:** 6 observations; records: aq_station (9), aq_station_proposed (7), document (7)
- **Notes:** Readings come from the JSON the results page loads; CO, AQI and unit-less fields are not stored. Yearly result PDFs are listed as document records only.

<details><summary>How it is collected and parsed</summary>

```text
SMC Air Quality Management Cell: monitoring stations, past-result PDFs and the latest real-time reading.

Three documents per refresh:

1. https://www.suratmunicipal.gov.in/Departments/CAAQMS (HTML, no readings): station lists, kept as records
     - "Location of Manual Air monitoring station installed by GPCB": address + DMS coordinates -> aq_station
     - "Locations of Sensor based CAAQMS installed by SMC" (Varachha, Limbayat zone offices)   -> aq_station
     - "Locations of USEPA Approved CAAQMS (Proposed by SMC / by GPCB)": zone + location      -> aq_station_proposed
   Coordinates are converted from the published degrees-minutes-seconds to decimal degrees (both kept).

2. https://www.suratmunicipal.gov.in/Departments/AirQualityResults (HTML)
     - "Past Results": yearly PDF reports per station (Limbayat 2018-2021, Varachha 2018-2021) -> `document`
       records (title, url, station, year). The PDFs are NOT downloaded or parsed (vendor-format reports).
     - "Real Time Results / Science Center": the numbers in the served HTML are placeholders ("0 ug/m3",
       "Last updated: -"); the page's own script fills them from (3). Nothing is read from the placeholders.

3. POST https://www.suratmunicipal.gov.in/Home/GetAirQualityInfoSci (form DeviceCode="") -> JSON, the request
   the results page itself makes for its "Science Center" panel. It returns ONE latest reading for station
   code "0034": dtl_date (/Date(ms)/ = midnight IST of the reading day) + testing_time (HH:MM:SS, IST).
   Emitted as instant observations at geo aq_station:smc-sensor-0034. Only the fields whose unit the page
   states are kept: SO2, NOx, PM2.5, PM10 (ug/m3), temperature (degC) and relative humidity (%).
   Not emitted:
     - CO: the page labels it ug/m3 but the values (about 1.45) are what CO looks like in mg/m3; unit unclear.
     - AQI: returned as 0.00 while PM2.5 is 50, i.e. not computed by the feed.
     - wind speed/direction, rainfall, solar radiation, pressure: no unit published on the page.
   Each refresh captures whatever the latest reading is; there is no history endpoint with data (the
   "...Last10" request the page also makes returned an empty list on 2026-10-05). On 2026-10-05 the latest
   reading was from 2026-09-29 20:24, so the feed may lag or stall; stale readings are stored as what they
   are (their own timestamp), never re-dated.

New geo level used: aq_station (already listed in the sources README).
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `air.smc_sensor_nox_ugm3` | NOx (SMC real-time sensor) | ug/m3 | 1 (1) | 1 | 2026-10-18 to 2026-10-18 | Latest NOx reading. |
| `air.smc_sensor_pm10_ugm3` | PM10 (SMC real-time sensor) | ug/m3 | 1 (1) | 1 | 2026-10-18 to 2026-10-18 | Latest PM10 reading. |
| `air.smc_sensor_pm25_ugm3` | PM2.5 (SMC real-time sensor) | ug/m3 | 1 (1) | 1 | 2026-10-18 to 2026-10-18 | Latest PM2.5 reading of the SMC sensor station, as shown on the Air Quality Results page. |
| `air.smc_sensor_relative_humidity_pct` | Relative humidity (SMC sensor station) | % | 1 (1) | 1 | 2026-10-18 to 2026-10-18 | Relative humidity at the sensor station at the time of the reading. |
| `air.smc_sensor_so2_ugm3` | SO2 (SMC real-time sensor) | ug/m3 | 1 (1) | 1 | 2026-10-18 to 2026-10-18 | Latest SO2 reading. |
| `air.smc_sensor_temperature_c` | Ambient temperature (SMC sensor station) | degC | 1 (1) | 1 | 2026-10-18 to 2026-10-18 | Ambient temperature at the sensor station at the time of the reading. |

## smc_swm

**SMC solid waste collection statistics (monthly)**

- **Publisher:** Surat Municipal Corporation, Solid Waste Management Department
- **Page:** https://www.suratmunicipal.gov.in/Departments/SolidWasteManagementStatistics
- **Module:** environment; **cadence:** monthly (checked every 168 h)
- **Geography:** SMC city (whole corporation area)
- **Licence:** Surat Municipal Corporation web page; public information
- **Enabled:** yes; **last success:** 2026-10-18T11:04:11+05:30
- **Holds:** 3462 observations

<details><summary>How it is collected and parsed</summary>

```text
SMC Solid Waste Management statistics: monthly MSW collection by collection method.

Page: https://www.suratmunicipal.gov.in/Departments/SolidWasteManagementStatistics
Twelve HTML tables:
  0-7   current series (Apr 2019 onward), one table per collection method
  8-11  legacy series (Oct 2008 - Mar 2019), four methods
Each table: title row "N. <method>", header row, then rows of
  Sr. No. | Period ("July-2026") | <numeric columns...>

This module is the reference example for writing adapters: a pure parse() that
turns the archived page into tidy observations, and a fetch() that only uses ctx.
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `swm.avg_collection_mt_per_day` | Average municipal solid waste collected | tonnes/day | 1052 (1048) | 1 | 2008-10-01 to 2026-09-30 | Average MSW collected per day in the month, by collection method (dims.mode). |
| `swm.smart_dustbins_installed` | Smart underground dustbins installed | dustbins | 90 (90) | 1 | 2019-04-01 to 2026-09-30 | Smart underground dustbins installed (mode smart_underground_dustbins only). |
| `swm.total_routes` | Night scraping/brushing routes | routes | 216 (216) | 1 | 2008-10-01 to 2026-09-30 | Total routes covered by night scraping/brushing (mode night_scraping only). |
| `swm.total_trips` | Collection trips | trips | 1052 (1048) | 1 | 2008-10-01 to 2026-09-30 | Total trips reported for the month, by collection method (dims.mode). |
| `swm.vehicles_utilized` | Vehicles used for collection | vehicles | 1052 (1048) | 1 | 2008-10-01 to 2026-09-30 | Number of vehicles utilised in the month, by collection method (dims.mode). |

## cityfinance_surat

**CityFinance standardised audited accounts: Surat Municipal Corporation (annual)**

- **Publisher:** Ministry of Housing and Urban Affairs, Government of India (CityFinance)
- **Page:** https://www.cityfinance.in/municipal-data/city/surat
- **Module:** finance; **cadence:** annual (checked every 720 h)
- **Geography:** SMC city (Surat Municipal Corporation as an urban local body)
- **Licence:** Government of India (MoHUA) public portal; JSON from the API that the CityFinance city page uses
- **Enabled:** yes; **last success:** 2026-10-18T11:01:29+05:30
- **Holds:** 200 observations
- **Notes:** CityFinance maps SMC's audited annual accounts to standard account heads, so its figures can differ from SMC's own statements (smc_balance_sheet). Only audited years are requested.

<details><summary>How it is collected and parsed</summary>

```text
MoHUA CityFinance: standardised audited accounts of Surat Municipal Corporation (annual, by financial year).

Page: https://www.cityfinance.in/municipal-data/city/surat, an Angular app. Its JS bundle (the city page chunk and
its "dashboard service") loads public JSON from https://www.cityfinance.in/api/v1/. fetch() calls three of those
endpoints as plain GETs with the default User-Agent and no extra headers:

  1. common/get-latest-standardized-year?ulbId=<id>&auditStatus=Audited
       {"success":true,"ledgerYears":["2023-24", ..., "2015-16"]}: the audited years, newest first. Used only to
       build the next two requests; nothing is stored from it. (auditStatus=Unaudited returned [] on 2026-10-18.)
  2. dashboard/city/bs-is?btnKey=incomeStatement&selectedUlb=<id>&ulbIds=<id>&years=2015-16&years=...
       The "Income Statement" table. One row per account head, with a "code" (110 Tax Revenue ... 272
       Depreciation) and one key per year, e.g. "202324_<ulb id>": 7280435255. Amounts are in RUPEES (integers):
       the same tax revenue shows as 728.04 Cr in the overview. A year with no key is a blank cell, stored as
       not_reported.
  3. ledger/getCityDasboardIndicators?keyType=overview&ulbId=<id>&years[]=2015-16&years[]=...
       The "Overview" tab. Rows look like {"name": "Own Source Revenue (Cr)", "yearData": ["939.88", ...]},
       in CRORE with 2 decimals, so they are multiplied by 1e7 and stored in INR (precise to Rs 1 lakh). "N/A" is
       stored as not_reported.

Surat's ULB id 5eb5844f76a3b61f40ba0693 (code GJ003, slug 'surat') comes from CityFinance's ULB list
(reference/budget/india-mohua-cityfinance-ulb-list-2026-09-27.json, from /api/v1/ulb).

What is stored (geo smc_city/smc, period = financial year 1 April - 31 March, unit INR):
  cityfinance.income.by_head, cityfinance.expenditure.by_head   income statement heads (dims.head)
  cityfinance.income.total, cityfinance.expenditure.total       "Total Income (A)" and "Total Expenditure (B)"
  cityfinance.own_source_revenue, cityfinance.revenue_expenditure, cityfinance.capital_expenditure   overview

Not stored:
  - subtotal rows ("Non-Tax Revenue" etc.), surplus lines, prior-period items (280), transfers to reserves (290);
  - the overview ratios and debt (smc_balance_sheet has SMC's own loan figures);
  - the overview's "Total Expenditure (Cr)", because it counts an N/A capital expenditure as zero (2015-16:
    1805.37 = revenue expenditure only).

How the figures relate (checked for all 8 years in the 2026-10-18 responses):
  - The overview's "Total Revenue Receipts" equals the income statement's "Total Income (A)".
  - The overview's "Own Source Revenue" equals income statement codes 110 + 130-150 + 170-180.
  - The overview's "Total Revenue Expenditure" equals "Total Expenditure (B)" plus prior-period items (code 280).
  - Capital expenditure is N/A for 2015-16 and 2019-20, the years that have no audited year just before them.
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `cityfinance.capital_expenditure` | Capital expenditure (CityFinance) | INR | 8 (6) | 1 | 2015-04-01 to 2024-03-31 | "Total Capital Expenditure" from the CityFinance overview, which CityFinance derives from fixed assets and capital work in progress in the balance sheet. It is N/A (not_reported) for years with no audited year just before them. Published in crore to 2 decimals. |
| `cityfinance.expenditure.by_head` | Revenue expenditure by account head (CityFinance income statement) | INR | 80 (47) | 1 | 2015-04-01 to 2024-03-31 | Income statement amount for one expenditure head (dims.head), e.g. establishment (code 210) or depreciation (272). Capital spending is not in the income statement. |
| `cityfinance.expenditure.total` | Total expenditure in the income statement (CityFinance) | INR | 8 (8) | 1 | 2015-04-01 to 2024-03-31 | "Total Expenditure (B)" of the income statement: the sum of the expenditure heads. It excludes capital expenditure and prior-period items. |
| `cityfinance.income.by_head` | Income by account head (CityFinance income statement) | INR | 80 (59) | 1 | 2015-04-01 to 2024-03-31 | Income statement amount for one head (dims.head), e.g. tax_revenue (code 110) or fees_user_charges (140). Blank cells are not_reported; older years report fewer heads separately. |
| `cityfinance.income.total` | Total revenue (CityFinance) | INR | 8 (8) | 1 | 2015-04-01 to 2024-03-31 | "Total Income (A)" of the income statement: the sum of all income heads, including assigned revenues and revenue grants. CityFinance shows the same figure as "Total Revenue". |
| `cityfinance.own_source_revenue` | Own source revenue (CityFinance) | INR | 8 (8) | 1 | 2015-04-01 to 2024-03-31 | "Own Source Revenue" from the CityFinance overview: income statement codes 110, 130-150 and 170-180 (tax, rent, fees, sales and other income incl. interest), excluding assigned revenues and grants (checked for all 8 years). Published in crore to 2 decimals (Rs 1 lakh). |
| `cityfinance.revenue_expenditure` | Revenue expenditure (CityFinance) | INR | 8 (8) | 1 | 2015-04-01 to 2024-03-31 | "Total Revenue Expenditure" from the CityFinance overview. In every year checked it equals the income statement total expenditure plus prior-period items. Published in crore to 2 decimals. |

## smc_balance_sheet

**SMC balance sheet and income & expenditure account (annual)**

- **Publisher:** Surat Municipal Corporation, Accounts Department
- **Page:** https://www.suratmunicipal.gov.in/Departments/Accounts/BalanceSheet
- **Module:** finance; **cadence:** annual (checked every 168 h)
- **Geography:** SMC city (the corporation as a whole); the statements have no zone breakdown
- **Licence:** Surat Municipal Corporation publication (balance sheet PDFs); public information
- **Enabled:** yes; **last success:** 2026-10-18T11:02:52+05:30
- **Holds:** 767 observations; records: balance_sheet_pdf (21)
- **Notes:** Amounts are rupees as printed (with paise). Balance-sheet items are stocks as at 31 March (period_start = period_end); income & expenditure items are flows for the financial year. Each PDF gives the current and the previous year; PDFs are applied oldest first so a later statement's comparative figure wins and earlier differing figures stay in observation_revision. A "-" or blank amount on a printed line (accounting nil) is stored as not_reported per project rule, never as 0; heads a year does not print are not stored. Statements FY2007-08 to FY2011-12 are signed by SMC officials only; from FY2012-13 they carry the auditors' (Natvarlal Vepari & Co.) signature, and publisher_as_of is the date printed under it when there is one. FY2005-06 and FY2006-07 (old two-sided format) are not parsed. The Gujarati duplicate pages and the schedules are not parsed. The index page is stored as balance_sheet_pdf records (one per financial year, with its PDF link).

<details><summary>How it is collected and parsed</summary>

```text
SMC balance sheet and income & expenditure account (annual, accrual basis, audited from FY2012-13).

Index: https://www.suratmunicipal.gov.in/Departments/Accounts/BalanceSheet
  A <ul class="list-group"> with one <li> per year: "Financial Year 2025-26" + a "View Balance Sheet" link to
  /Content/Documents/Departments/Accounts/BalanceSheet_25_26.pdf. The 2026-09-28 snapshot lists 2005-06 to 2025-26.

PDFs (all have a text layer; read with pdftotext -layout):
  FY2005-06, FY2006-07   old two-sided "Liabilities | Assets" (T-format) statements with different heads, previous
                         year first. NOT parsed and not fetched (FIRST_FY): FY2007-08 restates 31 March 2007 in the
                         current format as its comparative column.
  FY2007-08 .. FY2025-26 one vertical statement per page, the same heads every year:
      BALANCE SHEET AS ON/AT 31 MARCH, YYYY           PARTICULARS | Schedule No. | <current FY> | <previous FY>
      INCOME AND EXPENDITURE ACCOUNT FOR THE YEAR ENDED 31 MARCH, YYYY   (same columns)
    From FY2020-21 the PDF repeats both statements in Gujarati (pages 3-4); those pages are skipped (same numbers,
    and the legacy Gujarati font extracts as garbage). FY2016-17 has the I&E page first.

What is stored (geo smc_city/smc, unit INR, both the current and the comparative column of every statement):
  finance.balance_sheet.*      as at 31 March (period_start = period_end = YYYY-03-31)
  finance.income_expenditure.* for the financial year (1 April - 31 March)

Units: statements say "Amount in (Rs.)" / "(In Rs.)" / "(`)" (the rupee sign in the old Rupee Foradian font) and
print paise, so values are rupees and stored unchanged. FY2013-14, FY2018-19 and FY2019-20 print no unit; there the
amounts (with paise) are read as rupees only because the balance-sheet total then falls in the plausible range
(Rs 1,000 crore - Rs 10 lakh crore; read as lakhs it would be absurd). A statement in lakhs or crores is multiplied
by 1e5 / 1e7. Anything else is rejected rather than guessed.

Overlap between years: the FY N statement repeats FY N-1 as its comparative column, sometimes regrouped (e.g. the
FY2018-19 statement moves Rs 14.98 crore from investments to cash for 31 March 2018). fetch() yields the PDFs oldest
first, so the later statement's comparative figure is applied last and wins; the earlier figure is kept in
observation_revision by the database layer.

Consistency: every column is checked (sub-totals = sum of items, both GRAND TOTALs equal, total = application of
funds, income - expenditure = surplus). A current-year column that fails rejects the document. A comparative column
that fails is dropped from that document with a warning (FY2016-17's comparative 31-03-2016 balance sheet prints
two different GRAND TOTALs, Rs 48,460 apart); the year's own statement still provides that date.
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `finance.balance_sheet.accumulated_depreciation` | Fixed assets: accumulated depreciation | INR | 20 (20) | 1 | 2007-03-31 to 2026-03-31 | "Less: Depreciation" under Fixed Assets. As at 31 March. |
| `finance.balance_sheet.cash_bank` | Cash and bank balances | INR | 20 (20) | 1 | 2007-03-31 to 2026-03-31 | Current assets (c) "Cash and bank balances". As at 31 March. |
| `finance.balance_sheet.current_assets` | Current assets, loans and advances (total) | INR | 20 (20) | 1 | 2007-03-31 to 2026-03-31 | Unlabelled subtotal of the "Current assets, loans and advances" block. As at 31 March. |
| `finance.balance_sheet.current_liabilities` | Current liabilities | INR | 20 (20) | 1 | 2007-03-31 to 2026-03-31 | Less: Current liabilities and Provisions, (a) "Current liabilities". As at 31 March. |
| `finance.balance_sheet.cwip` | Capital work in progress | INR | 20 (20) | 1 | 2007-03-31 to 2026-03-31 | "Capital - Work In Progress (FA)". As at 31 March. |
| `finance.balance_sheet.gross_block` | Fixed assets: gross block | INR | 20 (20) | 1 | 2007-03-31 to 2026-03-31 | "Gross Block" of fixed assets. As at 31 March. |
| `finance.balance_sheet.inventories` | Inventories | INR | 20 (20) | 1 | 2007-03-31 to 2026-03-31 | Current assets (a) "Inventories". As at 31 March. |
| `finance.balance_sheet.investments` | Investments | INR | 20 (20) | 1 | 2007-03-31 to 2026-03-31 | "Investments". As at 31 March. |
| `finance.balance_sheet.loan_funds` | Loan funds (total) | INR | 18 (18) | 1 | 2007-03-31 to 2026-03-31 | Unlabelled subtotal of the "Loan Funds" block (secured + unsecured loans). Some years (FY2015-16 to FY2017-18) print no Loan Funds block at all. As at 31 March. |
| `finance.balance_sheet.loans_advances` | Loans and advances | INR | 20 (20) | 1 | 2007-03-31 to 2026-03-31 | Current assets (d) "Loans and advances". As at 31 March. |
| `finance.balance_sheet.municipal_fund` | Municipal fund | INR | 20 (20) | 1 | 2007-03-31 to 2026-03-31 | Own funds (a) "Municipal Funds" (schedule 1). As at 31 March. |
| `finance.balance_sheet.net_block` | Fixed assets: net block | INR | 20 (20) | 1 | 2007-03-31 to 2026-03-31 | "Net Block" = gross block - accumulated depreciation. As at 31 March. |
| `finance.balance_sheet.own_funds` | Own funds (total) | INR | 20 (20) | 1 | 2007-03-31 to 2026-03-31 | Unlabelled subtotal of the "Own Funds" block (municipal fund + reserves and surplus). As at 31 March. |
| `finance.balance_sheet.provisions_for_taxes` | Provisions for taxes | INR | 20 (5) | 1 | 2007-03-31 to 2026-03-31 | Less: Current liabilities and Provisions, (b) "Provisions For Taxes". As at 31 March. |
| `finance.balance_sheet.reserves_surplus` | Reserves and surplus | INR | 20 (20) | 1 | 2007-03-31 to 2026-03-31 | Own funds (b) "Reserves and surplus" (schedule 2). As at 31 March. |
| `finance.balance_sheet.secured_loans` | Secured loans | INR | 18 (16) | 1 | 2007-03-31 to 2026-03-31 | "Secured loans" under Loan Funds. As at 31 March. |
| `finance.balance_sheet.sundry_debtors` | Sundry debtors | INR | 20 (20) | 1 | 2007-03-31 to 2026-03-31 | Current assets (b) "Sundry Debtors": amounts receivable. As at 31 March. |
| `finance.balance_sheet.total` | Balance sheet total | INR | 20 (20) | 1 | 2007-03-31 to 2026-03-31 | "GRAND TOTAL" of the balance sheet (sources of funds = application of funds; the parser checks that both sides print the same figure). As at 31 March. |
| `finance.balance_sheet.unsecured_loans` | Unsecured loans | INR | 4 (3) | 1 | 2023-03-31 to 2026-03-31 | "Unsecured Loans" under Loan Funds (printed from FY2023-24). As at 31 March. |
| `finance.income_expenditure.administration_expenses` | Administration expenses | INR | 20 (20) | 1 | 2006-04-01 to 2026-03-31 | Expenditure: "Administration Expenses". For the financial year April-March. |
| `finance.income_expenditure.depreciation` | Depreciation | INR | 20 (20) | 1 | 2006-04-01 to 2026-03-31 | Expenditure: "Depreciation" charged for the year. For the financial year April-March. |
| `finance.income_expenditure.employee_costs` | Payments and benefits to employees | INR | 20 (20) | 1 | 2006-04-01 to 2026-03-31 | Expenditure: "Payments & Benefits to Employees". For the financial year April-March. |
| `finance.income_expenditure.excess_income_over_expenditure` | Excess of income over expenditure | INR | 20 (20) | 1 | 2006-04-01 to 2026-03-31 | "Excess of Income Over Expenditure" = surplus after tax + prior period income - prior period expenses; negative = excess of expenditure. For the financial year April-March. |
| `finance.income_expenditure.finance_charges` | Finance charges | INR | 20 (20) | 1 | 2006-04-01 to 2026-03-31 | Expenditure: "Finance Charges" (interest etc.). For the financial year April-March. |
| `finance.income_expenditure.grants_contributions` | Government grants, contributions and subsidies | INR | 20 (20) | 1 | 2006-04-01 to 2026-03-31 | Income: "Govt. Grants, Contri. & Subsidies" credited to income. For the financial year April-March. |
| `finance.income_expenditure.loss_on_disposal` | Loss on sale/disposal of fixed assets | INR | 9 (7) | 1 | 2006-04-01 to 2026-03-31 | Expenditure: "Loss on Sale/Disposal of Fixed Asset". For the financial year April-March. |
| `finance.income_expenditure.non_tax_revenue` | Non-tax revenues | INR | 20 (20) | 1 | 2006-04-01 to 2026-03-31 | Income: "Non Tax Revenues" (fees, user charges, etc.). For the financial year April-March. |
| `finance.income_expenditure.octroi_compensation` | Compensation in lieu of octroi | INR | 20 (20) | 1 | 2006-04-01 to 2026-03-31 | Income: "Compensation in lieu of Octroi" from the State. For the financial year April-March. |
| `finance.income_expenditure.other_expenses` | Other expenses | INR | 18 (13) | 1 | 2006-04-01 to 2026-03-31 | Expenditure: "Other Expenses". For the financial year April-March. |
| `finance.income_expenditure.other_income` | Other income | INR | 20 (20) | 1 | 2006-04-01 to 2026-03-31 | Income: "Other Income". For the financial year April-March. |
| `finance.income_expenditure.prior_period_expenses` | Prior period expenses | INR | 20 (20) | 1 | 2006-04-01 to 2026-03-31 | Prior period adjustments (b) "Prior period Expenses". For the financial year April-March. |
| `finance.income_expenditure.prior_period_income` | Prior period income | INR | 20 (20) | 1 | 2006-04-01 to 2026-03-31 | Prior period adjustments (a) "Prior period incomes". For the financial year April-March. |
| `finance.income_expenditure.repairs_maintenance` | Repairs and maintenance | INR | 20 (20) | 1 | 2006-04-01 to 2026-03-31 | Expenditure: "Repairs and Maintenance". For the financial year April-March. |
| `finance.income_expenditure.service_utility_charges` | Service and utilities charges | INR | 20 (20) | 1 | 2006-04-01 to 2026-03-31 | Expenditure: "Service & Utilities Charges". For the financial year April-March. |
| `finance.income_expenditure.surplus_after_tax` | Net surplus (deficit) after taxation | INR | 20 (20) | 1 | 2006-04-01 to 2026-03-31 | "Net Surplus for the year after taxation"; negative = deficit. For the financial year April-March. |
| `finance.income_expenditure.surplus_before_tax` | Net surplus (deficit) before taxation | INR | 20 (20) | 1 | 2006-04-01 to 2026-03-31 | "Net Surplus for the year before taxation" = total income - total expenditure; negative = deficit. For the financial year April-March. |
| `finance.income_expenditure.tax_provision` | Provision for taxes | INR | 20 (6) | 1 | 2006-04-01 to 2026-03-31 | "Less : Provision for taxes" deducted from the surplus. For the financial year April-March. |
| `finance.income_expenditure.tax_revenue` | Tax revenues | INR | 20 (20) | 1 | 2006-04-01 to 2026-03-31 | Income: "Tax Revenues" (e.g. property tax). For the financial year April-March. |
| `finance.income_expenditure.total_expenditure` | Total expenditure | INR | 20 (20) | 1 | 2006-04-01 to 2026-03-31 | Unlabelled subtotal of the Expenditure block. For the financial year April-March. |
| `finance.income_expenditure.total_income` | Total income | INR | 20 (20) | 1 | 2006-04-01 to 2026-03-31 | Unlabelled subtotal of the Income block. For the financial year April-March. |

## smc_budget_summary

**SMC revenue and capital budget vs actuals by zone (weekly)**

- **Publisher:** Surat Municipal Corporation, Accounts Department
- **Page:** https://www.suratmunicipal.gov.in/Departments/Accounts/CapitalRevenueBudgetSummary
- **Module:** finance; **cadence:** weekly (checked every 156 h)
- **Geography:** SMC city ("All Zone") plus Head Quarter and the nine administrative zones
- **Licence:** Surat Municipal Corporation web page (data loaded from its public JSON endpoint); public information
- **Enabled:** yes; **last success:** 2026-10-18T11:03:15+05:30
- **Holds:** 264 observations
- **Notes:** Figures are published in Rs thousand and stored in rupees. "Actuals (Tent.)" are tentative (unaudited) and change between weekly updates; the database keeps earlier values in observation_revision. The current year's actuals are year-to-date and stored with period_end = the "Last on" update date, so the weekly series accumulates. Percent columns are not stored. "All Zone" is stored as smc_city exactly as published, but it is NOT the sum of all listed zones: on the 2026-10-03 data it equals Head Quarter + West, Central, North, East-A, South-A, Athwa and South East, and leaves out East Zone-B and South Zone-B (Kanakpur) in every cell; whether those two are missing from the total or double-booked is unknown. Budget-centre drill-down pages keep state in a server session and are not fetched.

<details><summary>How it is collected and parsed</summary>

```text
SMC Revenue-Capital Budget Summary: zone-wise budget vs actuals, updated weekly.

Page: https://www.suratmunicipal.gov.in/Departments/Accounts/CapitalRevenueBudgetSummary
  Heading "Revenue-Capital Budget Summary (Rs. in '000) for <zone>", a zone <select id="drpZone"> (0 = All Zone,
  1 = Head Quarter, 2..10 = the nine zones), "Weekly Update (Last on 27/09/2026)", and an EMPTY table #dtBudget whose
  <thead> names the columns, e.g.
    Description | Actuals 24-25 | Original 25-26 | Revised 25-26 | Actuals (Tent.) 25-26 | % of Rev. 25-26 |
    Original 26-27 | Actuals (Tent.) 26-27 | % of Ori.26-27
  The rows are loaded by DataTables (server-side mode) from the endpoint named in the inline script
  ("SearchBy": "/Departments/getBudgetSummary", "BudgetYear": "2026"). The page's own script bundle
  (/bundles/BudgetZoneName) maps the JSON fields to the columns in this order:
    Description, PreviousYearActual2, PreviousYearOriginal1, PreviousYearRevised1, PreviousYearActual1, item5,
    item6, CurrentYearActuals, item8
  and $.fn.dataTable.pipeline sends a plain GET with the standard DataTables parameters (draw, columns[i][...],
  start=0, length=10, search[...]) plus CustomData[BudgetYear] and CustomData[ZoneCode]. fetch() sends exactly those
  parameters, with no cookies and no extra headers (no X-Requested-With, Origin or Referer); the server answers
  with JSON {"data": [4 rows], "status": 200, ...}. Without the DataTables parameters it redirects to /Error.html.

Each zone's JSON has four rows: Revenue Income, Revenue Expense, Capital Income, Capital Expense.

Stored (unit INR = Rs '000 x 1000):
  finance.budget_summary.income / .expenditure, dims {account: revenue|capital, measure: ...}
    measure budget_original   "Original YY-YY"            period = that financial year
            budget_revised    "Revised YY-YY"             period = that financial year
            actual            "Actuals YY-YY"             period = that financial year
            actual_tentative  "Actuals (Tent.) YY-YY"     a past financial year (unaudited, may still be revised)
            actual_ytd        "Actuals (Tent.) YY-YY"     the current budget year: cumulative actuals from 1 April to
                                                          the page's "Last on" date (period_end = that date), so
                                                          each weekly update is its own observation
  geo: All Zone -> smc_city/smc; Head Quarter -> smc_zone/hq; zones via surat.zone_code().
  CAVEAT: on the 2026-10-03 data "All Zone" equals Head Quarter + the seven zones with selector values 2-8 (West,
  Central, North, East-A, South-A, Athwa, South East) in every cell; the East Zone-B and South Zone-B (Kanakpur)
  figures are NOT included in it. Whether they are missing from the corporation total or also booked under
  East-A/South-A cannot be told from the page. "All Zone" is stored as published; do not expect the zones to add up
  to it, and do not add East-B/South-B to it either.
  The "%" columns are ratios of the stored columns; they are not stored but are used to check the column mapping.

The drill-down to budget centres (param() -> SetCapitalRevenueBCNT_Param -> CapitalRevenueBCNT) keeps the selection in
the server session and is not fetched.
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `finance.budget_summary.expenditure` | Budget summary: expenditure (revenue/capital) | INR | 132 (132) | 11 | 2024-04-01 to 2027-03-31 | Revenue or capital expenditure of the zone (dims.account), as budgeted or as spent. dims.account: revenue \| capital. dims.measure: budget_original ("Original"), budget_revised ("Revised"), actual ("Actuals"), actual_tentative ("Actuals (Tent.)" of a past year) or actual_ytd ("Actuals (Tent.)" of the current budget year, cumulative from 1 April to period_end = the page's weekly "Last on" date). Published in Rs '000; stored in rupees. |
| `finance.budget_summary.income` | Budget summary: income (revenue/capital) | INR | 132 (132) | 11 | 2024-04-01 to 2027-03-31 | Revenue or capital income of the zone (dims.account), as budgeted or as received. dims.account: revenue \| capital. dims.measure: budget_original ("Original"), budget_revised ("Revised"), actual ("Actuals"), actual_tentative ("Actuals (Tent.)" of a past year) or actual_ytd ("Actuals (Tent.)" of the current budget year, cumulative from 1 April to period_end = the page's weekly "Last on" date). Published in Rs '000; stored in rupees. |

## agmarknet_surat

**Agmarknet daily commodity arrivals and prices, Surat district APMC markets**

- **Publisher:** Directorate of Marketing & Inspection (Agmarknet), Ministry of Agriculture & Farmers Welfare, Government of India
- **Page:** https://agmarknet.gov.in/
- **Module:** food; **cadence:** daily (checked every 12 h)
- **Geography:** APMC markets of Surat district (geo apmc_market, code = Agmarknet market id, parent surat_district). Tapi-district markets that Agmarknet files under Surat (Vyara, Songadh, Uchhal, Nizar, Valod, Kukarmunda and sub-yards) are excluded. Only Surat APMC (64, Sardar Market, Dumbhal) is inside SMC limits.
- **Licence:** Government of India data (Agmarknet, published on data.gov.in under the Government Open Data License - India); public information
- **Enabled:** no; **last success:** never
- **Last error:** HTTP 400 for https://api.agmarknet.gov.in/v1/prices-and-arrivals/market-report/daily
- **Holds:** 0 observations
- **Notes:** Reads the data.gov.in open-data copy of the Agmarknet daily prices (Gujarat, filtered to Surat district here). Needs DATA_GOV_IN_API_KEY (free from data.gov.in); disabled without it. The old Agmarknet endpoint (https://api.agmarknet.gov.in/v1/prices-and-arrivals/market-report/daily) has required a captcha since 18 Oct 2026 and is not used; parse() still reads its archived responses, which also carry arrivals and "NIL Transaction" entries.

<details><summary>How it is collected and parsed</summary>

```text
Agmarknet daily arrivals and prices for the APMC markets of Surat district.

Since 18 Oct 2026 the Agmarknet report endpoint below answers every request with HTTP 400
"Captcha key and captcha value are required", so it is no longer called. fetch() now reads the
official open-data copy of the same prices instead:
    GET https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070
        ?api-key=<DATA_GOV_IN_API_KEY>&format=json&limit=1000&offset=0&filters[state.keyword]=Gujarat
("Current daily price of various commodities from various markets (Mandi)"). It needs a free API
key from data.gov.in in the DATA_GOV_IN_API_KEY environment variable; without it the source is
disabled. The key is sent but never stored or logged (the framework redacts it from URLs).
That resource has prices (Rs/quintal) but no arrivals, and no "NIL Transaction" entries.
Its record layout below follows the data.gov.in documentation; it has not been checked against a
live response yet (the public sample key was rate-limited), so check the first real run.
    records[] {state, district, market, commodity, variety, grade, arrival_date "dd/mm/yyyy",
               min_price, max_price, modal_price}   (older responses spell keys like "Min_x0020_Price")

The old endpoint, kept here because parse() still reads its archived responses and the frozen
copies in reference/ (the one agmarknet.gov.in's own report page calls):
    POST https://api.agmarknet.gov.in/v1/prices-and-arrivals/market-report/daily
    body {"date": "YYYY-MM-DD", "marketIds": [...], "stateIds": [11], "includeExcel": false}
Checked on 2026-10-04: it answers our plain OpenCityBot User-Agent without Origin/Referer
headers, so nothing is spoofed. One request per date.

Response (JSON), one document per date:
    title   "Market-wise, Commodity-wise Daily Report on: 01-Sep-2026"
    states[].markets[]  {marketId, marketName, commodities[]}
    commodities[] is one of
      - {commodityId, commodityName, total_arrivals, data: [{marketCenter, arrivals, unitOfArrivals,
         variety, grade, minimumPrice, maximumPrice, modalPrice, unitOfPrice}]}
      - {commodityName: "NIL Transaction - No Arrivals" | "... - Weekend Holiday" | "... - Public Holiday"}
        (no data key): the market states that it had no transactions that day
      - empty list: the market has uploaded nothing for that day (yet)
In every frozen response (28 Aug - 26 Sep 2026) arrivals are "Metric Tonnes" and prices
"Rs./Quintal"; any other unit raises instead of being silently mixed in.

What is stored, per market (geo apmc_market, code = Agmarknet market id) and day:
  - per commodity line (dims commodity/variety/grade): arrivals in tonnes and min/max/modal price
    in Rs/quintal. A price or arrival published as 0 is not a measurement: stored as not_reported
    with value_text "published as 0".
  - agm.market_reported: one observation per market-day. Reported -> value = number of commodity
    price lines in that day's report. A "NIL Transaction - ..." entry -> not_reported, value None,
    value_text = Agmarknet's reason verbatim (never 0 arrivals). An empty commodity list or a market
    missing from the response -> nothing is stored (nothing was published; a later upload fills it).

Geography: Agmarknet's market master files 33 markets under district "Surat" (district_id 159),
including the markets of Tapi district (split from Surat in 2007): Vyara, Songadh, Uchhal, Nizar,
Valod, Kukarmunda and their sub-yards. Their master addresses say "Dist. Tapi" (or are sub-yards of
those committees), so they are excluded here; only the 21 Surat-district market ids are requested
and parsed. Only the Surat APMC main yard (id 64, Sardar Market, Dumbhal, Puna-Kumbharia Road) is
known to be inside SMC limits.
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `agm.arrivals_tonnes` | Commodity arrivals | tonnes | 0 |  |  | Quantity of the commodity (dims commodity/variety/grade) arriving at the market that day, Agmarknet column "Arrivals" in "Metric Tonnes". Published 0 -> not_reported. Only in responses from the old Agmarknet endpoint; the data.gov.in copy has no arrivals. |
| `agm.market_reported` | Market reported prices | price lines | 0 |  |  | One per market and day. reported: value = number of commodity/variety/grade price lines in that day's report. not_reported: the market filed a "NIL Transaction" entry; value_text gives Agmarknet's reason verbatim (e.g. "NIL Transaction - No Arrivals", "NIL Transaction - Weekend Holiday"; old endpoint only). Days with nothing uploaded have no observation. |
| `agm.price_max_rs_per_qtl` | Maximum price | Rs/quintal | 0 |  |  | Highest price of the day for the commodity line, Agmarknet "Maximum Price" (Rs./Quintal). Published 0 -> not_reported. |
| `agm.price_min_rs_per_qtl` | Minimum price | Rs/quintal | 0 |  |  | Lowest price of the day for the commodity line, Agmarknet "Minimum Price" (Rs./Quintal). Published 0 -> not_reported. |
| `agm.price_modal_rs_per_qtl` | Modal price | Rs/quintal | 0 |  |  | Price at which most of the commodity traded that day, Agmarknet "Modal Price" (Rs./Quintal). Published 0 -> not_reported. |

## fca_prices

**DoCA daily retail and wholesale prices of essential commodities (Surat centre)**

- **Publisher:** Price Monitoring Division, Department of Consumer Affairs, Government of India
- **Page:** https://fcainfoweb.nic.in/reports/report_menu_web.aspx
- **Module:** food; **cadence:** daily (checked every 24 h)
- **Geography:** DoCA price reporting centre "Surat" (Gujarat, West Zone); surveyed markets not published
- **Licence:** Government of India web report (fcainfoweb.nic.in); public information
- **Enabled:** no; **last success:** never
- **Holds:** 0 observations
- **Notes:** Disabled: every fcainfoweb price report needs a captcha (checked 2026-10-18), and we do not automate captchas. Manual workflow: open https://fcainfoweb.nic.in/reports/report_menu_web.aspx, pick Report Type Retail (or Wholesale) and Language English, choose "Price report", then "Daily Prices", enter the date (dd/mm/yyyy), type the captcha and click "Get Data". The report opens in a new window: save it as "Web page, HTML only", one file per date and report type. parse() reads the Surat row from it. Its layout is unverified until a real saved report is tested. Weekend and holiday figures are provisional until DoCA verifies them on the next working day (disclaimer on the report form).

<details><summary>How it is collected and parsed</summary>

```text
DoCA Price Monitoring Division: daily retail and wholesale prices of essential commodities, Surat centre.

DISABLED (SOURCE.enabled=False): the report form is captcha-protected, and we do not automate captchas.

Checked on 2026-10-18 with our plain OpenCityBot User-Agent (two GETs, two form postbacks, no report requested;
re-checked by the verifier with one GET the same day: captcha still on the landing form):
  GET  https://fcainfoweb.nic.in/reports/report_menu_web.aspx
       ASP.NET form: Report Type (Retail | Wholesale), Language, radio "Price report" / "Average/Month End
       Report" / "Variation Report ...", and a captcha (<img src="../CaptchaImage.aspx">, a required
       "Enter captcha" box).
  "Price report" -> a select: "Daily Prices" | "Zonewise Average Price".
  "Daily Prices" -> one Date box (dd/MM/yyyy) and a "Get Data" button whose onclick md5-hashes the captcha
       in the browser before posting; the report opens in a new window.
So every report needs a solved captcha. The fcainfoweb home page shows only all-India averages, headed
"All India Average Retail Price(₹/Kg)" and "All India Average Wholesale Price(₹/Qtl.)": that is where the
units below come from. Surat is centre 17 of the West Zone list
(reference/food-prices/india-doca-price-reporting-centres-2026-09-27.html).

Manual workflow (see SOURCE.notes): a person fills the form, solves the captcha and saves the report page.
parse() reads the Surat row from that saved page.

What parse() expects. No real report page has been obtained, so this layout is an assumption:
  - a line with the report date ("Date : 17/10/2026", "as on 17/10/2026" or "17-Oct-2026");
  - the words "retail price" or "wholesale price" (exactly one of the two);
  - an HTML table with commodity names across one header row and centres down the rows, with one row
    labelled "Surat".
If the real layout differs, parse() or validate() raises an error instead of guessing.

Stored: fca.retail_price (Rs/kg) and fca.wholesale_price (Rs/quintal). They are separate metrics because
their units differ. Each is one observation per commodity (dims.commodity) for the report date, at geo
reporting_centre:surat. Only the 23 commodities in COMMODITIES are read. Other columns, such as the home
page's "additional commodities" (eggs, banana, ...), are skipped because their units are not stated.
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `fca.retail_price` | Retail price of essential commodities (DoCA, Surat centre) | Rs/kg | 0 |  |  | Daily retail price reported by the Surat centre to DoCA, by commodity (dims.commodity). DoCA gives retail prices in Rs/kg. Milk is marked "@" by DoCA, and its unit (probably per litre) was not confirmed on the pages checked. |
| `fca.wholesale_price` | Wholesale price of essential commodities (DoCA, Surat centre) | Rs/quintal | 0 |  |  | Daily wholesale price reported by the Surat centre to DoCA, by commodity (dims.commodity). DoCA gives wholesale prices in Rs/quintal (100 kg). Milk is marked "@" and its basis was not confirmed. |

## nfhs5_surat

**NFHS-5 district fact sheet indicators, Surat district (2019-21, with NFHS-4)**

- **Publisher:** International Institute for Population Sciences / Ministry of Health and Family Welfare (NFHS-5)
- **Page:** https://github.com/pratapvardhan/NFHS-5
- **Module:** health; **cadence:** static (checked every 2160 h)
- **Geography:** Surat district (survey sample covers the whole district, urban and rural); not SMC city limits
- **Licence:** Data from IIPS/MoHFW NFHS-5 district fact sheets; CSV compilation by pratapvardhan/NFHS-5 (GitHub)
- **Enabled:** yes; **last success:** 2026-10-18T11:02:08+05:30
- **Holds:** 208 observations
- **Notes:** Periods are survey-round labels (NFHS-5 2019-21, NFHS-4 2015-16). Values based on 25-49 unweighted cases carry that note in value_text; suppressed values (<25 cases) are stored as withheld.

<details><summary>How it is collected and parsed</summary>

```text
NFHS-5 (2019-21) district fact-sheet indicators for Surat district, with the NFHS-4 (2015-16) comparison.

Source: a CSV compilation of the NFHS-5 district fact sheets,
    https://raw.githubusercontent.com/pratapvardhan/NFHS-5/master/NFHS-5-Districts.csv
Long format, one row per district x indicator:
    State, State-Code, District, Indicator ("81. Children age 6-59 months who are anaemic (<11.0 g/dl)22 (%)"),
    NFHS-5, NFHS-4, NFHS-5-note, NFHS-4-note
Notes are either "Based on 25-49 unweighted cases" (the fact sheet prints such values in parentheses)
or "Percentage not shown; based on fewer than 25 unweighted cases" (the fact sheet prints "*").
Surat has 104 indicator rows (State "Gujarat", District "Surat"). Tapi is a separate district.

What is stored (geo surat_district/surat; never smc_city, the survey sample covers the whole district):
  - one observation per indicator and survey round; dims = {factsheet_no, indicator}
    factsheet_no is the NFHS-5 fact-sheet row number ("81"); NFHS-4 values are the comparison column
    of the same NFHS-5 fact sheet, so they share the row number.
  - indicator is the label with the row number and footnote digits removed. The CSV drops the fact
    sheet's sub-headings, which leaves rows 86-88 / 89-91 and 92-94 / 95-97 with identical labels;
    the population from the fact sheet heading is put back in front (e.g. "Women age 15 years and
    above: ..."), and likewise for family-planning rows 20-29 and cancer screening rows 98-100.
  - period = the survey round label: NFHS-5 2019-01-01..2021-12-31, NFHS-4 2015-01-01..2016-12-31
    (rounds, not fieldwork dates).
  - "Based on 25-49 unweighted cases": reported, value_text carries the note (treat with caution).
    "Percentage not shown ...": status withheld, value None, value_text the note.
    Blank without a note (indicator not in NFHS-4): not_reported.
  - Units: most rows are percentages (nfhs.indicator_pct); two sex ratios (nfhs.sex_ratio) and the
    out-of-pocket delivery cost (nfhs.delivery_oop_rs) get their own metrics so units never mix.
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `nfhs.delivery_oop_rs` | Out-of-pocket cost per delivery in a public facility | Rs. | 2 (2) | 1 | 2015-01-01 to 2021-12-31 | Average out-of-pocket expenditure per delivery in a public health facility (NFHS fact sheet). |
| `nfhs.indicator_pct` | NFHS indicator (percentage) | % | 202 (160) | 1 | 2015-01-01 to 2021-12-31 | NFHS district fact-sheet indicator expressed as a percentage; dims.indicator is the fact-sheet label, dims.factsheet_no its NFHS-5 row number. Period = survey round. |
| `nfhs.sex_ratio` | NFHS sex ratio | females per 1,000 males | 4 (4) | 1 | 2015-01-01 to 2021-12-31 | Sex ratio of the total population, or at birth for children born in the last five years (dims.indicator). |

## smc_disease

**SMC disease incidence statistics and vector-control activity (monthly)**

- **Publisher:** Surat Municipal Corporation, Health Department and Vector Borne Diseases Control (VBDC) Department
- **Page:** https://www.suratmunicipal.gov.in/Departments/HealthDepartmentDiseaseReports
- **Module:** health; **cadence:** monthly (checked every 168 h)
- **Geography:** SMC city (whole corporation area); no zone or ward breakdown is published on these pages
- **Licence:** Surat Municipal Corporation web pages; public information
- **Enabled:** yes; **last success:** 2026-10-18T11:03:26+05:30
- **Holds:** 9288 observations
- **Notes:** Disease incidence ("Ind") is described on SMC's Disease Incidence home page as admitted new cases reported at eight Surat hospitals (Maskati, Surat General, Ashktashram, Lokhat, Mahavir General, Mission, New Civil, SMIMER), so it is a hospital-based count, not total community incidence. The last year of a table can end in zeros (e.g. Pulmonary TB Nov-Dec 2022 = 0 after ~700/month); they are stored as published (0, reported) because the page prints 0, but they may be unfilled months. Blank cells are stored as not_reported. Yearly totals and percentages are not stored.

<details><summary>How it is collected and parsed</summary>

```text
SMC Health Department disease incidence statistics + VBDC month-wise activity statistics.

Two pages, one adapter (fetch() tags each document with raw.meta['page']):

1. 'disease' - https://www.suratmunicipal.gov.in/Departments/HealthDepartmentDiseaseReports
   Seven HTML tables, one per tab, each named by a (visually hidden) <caption>:
     Gastro Enteritis, Enteric Fever, Pulmonary TB, Pneumonia, Hepatitis, Cholera
         header: Month | Particulars | Jan .. Dec | TOT
         rows:   <year> | Ind | 12 monthly values | total     (Ind = incidence)
                 ''     | D   | 12 monthly values | total     (D = deaths; the year cell is usually blank)
     Malaria Statistics (a different layout, one row per month):
         Month | Year | Collection | Examined | Positive Cases - Nos. | Positive Cases - (%) |
         P. Vivex(+) Case - Nos. | ..(%) | P. Falci.(+) Cases - Nos. | ..(%) | Death
         plus one 'Total' row per year.
   Coverage on the snapshot: 1995-2022 (cholera from 2002), malaria Jan 2005 - Oct 2023.

2. 'vbdc' - https://www.suratmunicipal.gov.in/Departments/VectorBorneDiseasesControlStatistics
   One wide table, one row per month (Jan 2005 - Oct 2023) plus a 'Total' row per year:
     intra-domestic survey (houses checked, breeding spots checked, positive spots by mosquito type),
     peri-domestic survey (construction sites checked, breeding spots, positives by mosquito type),
     biological control, notices, administrative charges, source reduction, fogging rounds.

The yearly TOT columns / 'Total' rows are NOT stored (they are sums of the months, and on the VBDC
page some are Excel-rounded, e.g. '1.01E+08'); parse() uses them only as a cross-check against
column shifts. Percent columns of the malaria table are derived ratios and are not stored either.
Both pages were last updated by SMC in November 2023, so the series are stale; that is expected.
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `health.disease.cases` | Disease cases (incidence) | cases | 2158 (2157) | 1 | 1995-01-01 to 2023-10-31 | Monthly cases by disease (dims.disease). For gastroenteritis, enteric fever, pulmonary TB, pneumonia, hepatitis and cholera this is the "Ind" (incidence) row: admitted new cases reported at eight Surat hospitals. For malaria it is "Positive Cases - Nos." from the blood-smear surveillance table. |
| `health.disease.deaths` | Disease deaths | deaths | 2158 (2158) | 1 | 1995-01-01 to 2023-10-31 | Monthly deaths by disease (dims.disease): the "D" row of each disease table, or the "Death" column of the malaria table. |
| `health.malaria.positive_by_species` | Malaria positive cases by parasite species | cases | 452 (452) | 1 | 2005-01-01 to 2023-10-31 | Positive cases by species (dims.species: p_vivax, p_falciparum); columns "P. Vivex(+) Case - Nos." and "P. Falci.(+) Cases - Nos.". On the snapshot they add up to the total positive cases. |
| `health.malaria.smears_collected` | Malaria blood smears collected | samples | 226 (226) | 1 | 2005-01-01 to 2023-10-31 | Malaria surveillance table, column "Collection": blood samples collected in the month. |
| `health.malaria.smears_examined` | Malaria blood smears examined | samples | 226 (226) | 1 | 2005-01-01 to 2023-10-31 | Malaria surveillance table, column "Examined": samples examined in the month. |
| `vbdc.admin_charges` | Administrative charges levied for breeding sites | INR | 226 (226) | 1 | 2005-01-01 to 2023-10-31 | Column "Adm. Charge": administrative charges collected from defaulters. The column does not state a unit; the VBDC home page describes them as charges collected, so read as rupees. |
| `vbdc.biological_control` | Biological control actions | count | 226 (226) | 1 | 2005-01-01 to 2023-10-31 | Column "Biological control" (e.g. larvivorous fish release); the page does not state the unit. |
| `vbdc.breeding_spots_checked` | Potential mosquito breeding spots checked | spots | 452 (452) | 1 | 2005-01-01 to 2023-10-31 | Column "Breedingspot" / "Breeding spot" of the intra- or peri-domestic survey (dims.survey). Read as spots checked: positives by mosquito type are reported separately and are a small fraction of it. |
| `vbdc.breeding_spots_positive` | Breeding spots found positive, by mosquito type | spots | 1808 (1808) | 1 | 2005-01-01 to 2023-10-31 | Positive breeding spots by survey (dims.survey: intra_domestic, peri_domestic) and mosquito type (dims.mosquito: anopheles, aedes, culex, mixed). The published "Total" column is their sum. |
| `vbdc.construction_sites_checked` | Construction sites checked (peri-domestic survey) | sites | 226 (226) | 1 | 2005-01-01 to 2023-10-31 | VBDC peri-domestic survey: "Checked Construction" in the month. |
| `vbdc.fogging_rounds` | Fogging machine rounds | rounds | 452 (452) | 1 | 2005-01-01 to 2023-10-31 | Column "Fogging Machine Utilised (Round)", by equipment (dims.equipment: vehicle_mounted for "Geep mounted", handheld for "Handy Sets"). |
| `vbdc.houses_checked` | Houses checked (intra-domestic survey) | houses | 226 (226) | 1 | 2005-01-01 to 2023-10-31 | VBDC intra-domestic survey: "No. of Houses checked" in the month (repeat visits count again). |
| `vbdc.notices_issued` | Notices issued for breeding sites | notices | 226 (226) | 1 | 2005-01-01 to 2023-10-31 | Column "Notice": notices issued to owners of premises with mosquito breeding. |
| `vbdc.source_reduction` | Source reduction actions | count | 226 (226) | 1 | 2005-01-01 to 2023-10-31 | Column "Source Reduction" (breeding sources removed/eliminated); the page does not state the unit. |

## smc_health_centres

**SMC urban health centres (UHC / UCHC) by zone**

- **Publisher:** Surat Municipal Corporation, Health Department
- **Page:** https://www.suratmunicipal.gov.in/Departments/PMJAYUHC
- **Module:** health; **cadence:** static (checked every 168 h)
- **Geography:** SMC zones (smc_zone, codes from surat.zone_code()) and the SMC city area (sum of the zones)
- **Licence:** Surat Municipal Corporation web page; public information (no explicit open-data licence)
- **Enabled:** yes; **last success:** 2026-10-24T22:41:55+05:30
- **Holds:** 20 observations; records: smc_health_centre (80)
- **Notes:** The PM-JAY "Enrollment Health Centers" page, which lists SMC's urban health centres zone by zone. Type (UHC / UCHC) and the maternity-home flag are read from the centre name. Counts are dated to the page footer "Last Updated" date (a CMS edit date). Phone numbers are kept as printed.

<details><summary>How it is collected and parsed</summary>

```text
SMC urban health centres (UHC / UCHC): directory by zone, and the number of centres by type and zone.

Publisher: Surat Municipal Corporation, Health Department. The page sits in the SMC site menu under
Departments > Health > PM-JAY > "Enrollment Health Centers": the SMC health centres where residents can get a
PM-JAY / MA (Ayushman Bharat) card made. In practice it is SMC's list of its own urban health centres.

Endpoint: one plain GET, no parameters, no login or captcha (robots.txt on www.suratmunicipal.gov.in returns 404,
so nothing is disallowed):

    https://www.suratmunicipal.gov.in/Departments/PMJAYUHC

Response layout (server-rendered HTML, no <table>). Inside <div class="contentblock">, one block per zone:

    <h2 class="text-3x text-bold"> West Zone (Rander) </h2>
    <ul class="list-group">
      <li class="list-group-item hidden-xs hidden-sm"> Name | Address | Phone Numbers </li>    (column header)
      <li class="list-group-item">
        <div class="col-sm-12 col-md-3"><div class="visible-xs ...">Name</div> RANDER UHC </div>
        <div class="col-sm-12 col-md-6"><div class="visible-xs ...">Address</div> NR. RANDER BUS STAND, RANDER VILLAGE </div>
        <div class="col-sm-12 col-md-3"><div class="visible-xs ...">Phone Numbers</div> 2770925 </div>
      </li> ...

parse() reads each item through its own "Name" / "Address" / "Phone Numbers" labels, so it does not depend on
the CSS classes.

Records -> one 'smc_health_centre' per item, keyed by the name slug ('rander-uhc'). The page is the complete list,
so a centre that disappears from it gets closed. Attributes:
    name            as printed ('RANDER UHC', 'ASARAWALA UHC MH', 'NANDCHOWK URBAN HEALTH CENTER')
    facility_type   'uhc' (Urban Health Centre: names ending in UHC or URBAN HEALTH CENTER) or 'uchc' (Urban
                    Community Health Centre: names ending in UCHC). Read from the name; SMC prints no type column.
                    An unknown suffix raises an error rather than being guessed.
    maternity_home  True when the name ends in "MH" (maternity home attached; 2 centres in the snapshot). The page
                    does not list maternity homes separately, so there is no maternity-home count.
    zone            the zone heading as printed ('South Zone-A (Udhana)')
    zone_code       canonical code from surat.zone_code() (joins to geo level smc_zone)
    address         the centre's address as printed (a public building, not a person's address)
    phones          list of numbers as printed, split only at commas ('2423751-56, 381' -> ['2423751-56', '381']);
                    '-' means none and gives an empty list. Seven-digit numbers are Surat 0261 landlines.

Observations -> metric health.smc_centres (centres listed), by dims.type (uhc / uchc), for each smc_zone and for
smc_city (sum over the zones). Both types are emitted for every zone on the page, so a 0 means "none listed".
Counted from the items; the page prints no totals.

Snapshot 2026-10-24: 80 centres in 9 zones (71 UHC, 9 UCHC); footer "Last Updated: June 24, 2024 01:15 PM".

Dating: the page has no data date. Its footer "Last Updated" stayed at June 24, 2024 across fetches hours apart,
so it is the CMS edit date of this page (not the render time). The counts are filed as an instant reading on that
date, with publisher_as_of set to it; a later edit moves the date and starts a new point.

Quirks, kept as published: only 13 centres have a phone number; NAVANAGAR UHC lists a mobile-format number, kept
because it is printed as the centre's own number; spellings vary (GOURAVAPATH / GAURAVPATH, ICHHAPORE / ICHHAPOR,
"OPOSITE"); the West Zone list includes ADAJAN UHC and ADAJAN PATIYA UHC as separate centres.

Geography: SMC zones (smc_zone) and the SMC city area. Cadence: static, changes only when the page is edited;
checked weekly. Licence: Surat Municipal Corporation web page; public information; no explicit open-data licence.
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `health.smc_centres` | SMC urban health centres | centres | 20 (20) | 10 | 2024-06-24 to 2024-06-24 | Number of SMC health centres listed on the PM-JAY "Enrollment Health Centers" page, by dims.type: uhc = Urban Health Centre (name ends in UHC or URBAN HEALTH CENTER), uchc = Urban Community Health Centre (name ends in UCHC). Per smc_zone as listed under the zone heading; smc_city is the sum over the zones. Counted from the listed items (the page prints no totals). Instant reading on the page's "Last Updated" date. |

## smc_pmjay_hospitals

**PM-JAY empanelled hospitals in Surat (SMC list)**

- **Publisher:** Surat Municipal Corporation, Health Department (PM-JAY / MA Yojana hospital list)
- **Page:** https://www.suratmunicipal.gov.in/Content/Documents/Departments/PMJAY/PMJAYHospitals.pdf
- **Module:** health; **cadence:** static (checked every 168 h)
- **Geography:** Surat district (the list's District column; includes hospitals outside the SMC area)
- **Licence:** Surat Municipal Corporation web document; public information (no explicit open-data licence)
- **Enabled:** yes; **last success:** 2026-10-24T22:41:56+05:30
- **Holds:** 23 observations; records: pmjay_hospital (81)
- **Notes:** Parsed from the word positions (pdftotext -raw -bbox) because cells wrap over several lines. The contact-person and mobile columns are personal data and are never read. Speciality counts group the free-text speciality cell by keyword stems (see the module documentation). Dated to the PDF creation date; the document prints no date.

<details><summary>How it is collected and parsed</summary>

```text
PM-JAY (Ayushman Bharat / PMJAY-MA) empanelled hospitals in Surat, from SMC's list: directory and counts.

Publisher: Surat Municipal Corporation, Health Department (PM-JAY section of the SMC site; the menu link is labelled
"Enrollment Hosptials" under Departments > Health > PM-JAY). The list itself comes from the PM-JAY / MA Yojana
(Mukhyamantri Amrutam) scheme run by the National Health Authority and Gujarat's State Health Agency.

Endpoint: one plain GET of a PDF, no parameters, no login or captcha (robots.txt on www.suratmunicipal.gov.in
returns 404, so nothing is disallowed):

    https://www.suratmunicipal.gov.in/Content/Documents/Departments/PMJAY/PMJAYHospitals.pdf

Response layout: a 12-page landscape text PDF exported from Excel ("SURAT MUNICIPAL CORPORATION / PMJAY-MA YOJNA
AYUSHMAN BHARAT / EMPANALLED HOSPITAL LIST"), one table with no column header row:

    Sr | Hospital name | PM-JAY hospital ID | State | District | Address | Contact person | Mobile | Specialities

Cells wrap over several lines and are centred vertically, so the lines of neighbouring rows interleave in a plain
text dump. parse() therefore runs `pdftotext -raw -bbox`, which lists every word with its position in the order
the PDF draws it. Excel draws the table row by row and cell by cell, so a row is "a serial number and every word
after it until the next serial number"; the word's x position gives its column (left edges in COLUMNS). Words in
larger type (the 16 and 24 pt title) are skipped. The Contact person and Mobile columns name individual staff and
their mobile numbers: they are never read or stored.

Records -> one 'pmjay_hospital' per row, keyed by the PM-JAY hospital ID in lower case ('hosp24t123955'), or by
'name-<slug>' for the one row printed without an ID (Baps Pramukh Swami Hospital). The PDF is the complete list,
so hospitals that drop off it get closed. Attributes:
    serial_no          the row number as printed (no row carries 33 or 42, so 1-83 holds 81 rows)
    name               hospital name as printed (two different hospitals are both "Lifeline Multispeciality Hospital")
    pmjay_id           hospital ID as printed: 'HOSP24<letter><digits>' or the older 'HS24<digits>' form, or None
    state, district    as printed (always "Gujarat" / "Surat"; validate() insists on it)
    address            the hospital's address as printed
    specialities       the speciality cell split at commas, as extracted. Excel wraps long words mid-word, which
                       leaves stray spaces ("Orthopae dics", "Polytraum a"); duplicates ("Dialysis,Dialysis") kept.
    speciality_groups  the SPECIALITY_GROUPS slugs found in the specialities (sorted), see below.

Observations, filed under surat_district (the District column says Surat for every row; several hospitals are
outside the SMC area, e.g. Bardoli, Kim, Kamrej, Kadodara, Vankal):
    pmjay.listed_hospitals          number of hospitals on the list (rows).
    pmjay.hospitals_by_speciality   number of listed hospitals whose speciality text falls in dims.speciality.
        The speciality text is free text with many spellings, so each item is lower-cased, spaces and hyphens are
        removed, and it is put in every group whose stem it contains (SPECIALITY_GROUPS; e.g. 'paediatriccancer'
        counts under oncology and paediatrics), or in the group its exact text names (EXACT_GROUPS: 'ent',
        'urology', 'generalmedicine', 'generalsurgery', which are substrings of other words). Items such as
        "Medical Management" and "High end Medicine" fit no group and are only kept on the record. Every group is
        emitted, so 0 means no listed hospital mentions it. This is a count of what SMC's list says, not of the
        packages each hospital is actually empanelled for.
Both are instant readings on the PDF's creation date (PDF metadata CreationDate, 2024-06-27 in the snapshot); the
document prints no date of its own. A replaced PDF gets a new date and starts a new point.

Snapshot 2026-10-24 (PDF created 2024-06-27): 81 hospitals (serials 1-83 without 33 and 42).

Caveats: this is SMC's citizen-facing list, dated mid-2024; it need not match the National Health Authority's
current hospital register for Surat. There is no ownership column, and the letter in the ID is not decoded. The raw archive keeps
the PDF as published (with the contact columns); the test fixture is the pdftotext word list of pages 1-2 with
those two columns removed.

Geography: Surat district. Cadence: static (replaced without schedule); checked weekly.
Licence: Surat Municipal Corporation web document; public information; no explicit open-data licence.
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `pmjay.hospitals_by_speciality` | Listed PM-JAY hospitals by speciality | hospitals | 22 (22) | 1 | 2024-06-27 to 2024-06-27 | Number of hospitals on the list whose speciality cell mentions dims.speciality. The free-text items are grouped by keyword stems (e.g. oncology = medical, surgical or radiation oncology or paediatric cancer; nephrology_dialysis = nephrology or dialysis; urology = urology or genitourinary surgery). A hospital counts once per group. Instant reading on the PDF creation date. |
| `pmjay.listed_hospitals` | Hospitals on SMC's PM-JAY empanelled list | hospitals | 1 (1) | 1 | 2024-06-27 to 2024-06-27 | Number of hospitals (rows) on SMC's PMJAY-MA Yojana Ayushman Bharat empanelled hospital list for Surat. Instant reading on the PDF creation date. SMC's list, not the full NHA register. |

## smc_smimer

**SMIMER hospital statistics: milk, blood and eye bank, ICU (monthly)**

- **Publisher:** Surat Municipal Corporation, SMIMER hospital
- **Page:** https://www.suratmunicipal.gov.in/smimer/Hospital/SHMiscellaneousStatistics
- **Module:** health; **cadence:** monthly (checked every 168 h)
- **Geography:** One SMC-run hospital (geo level facility, code smimer)
- **Licence:** Surat Municipal Corporation web page; public information
- **Enabled:** yes; **last success:** 2026-10-18T11:04:09+05:30
- **Holds:** 4658 observations
- **Notes:** Skipped as ambiguous or derived: blood-bank issued Grand Total (composition varies), Total Voluntary (derivable), eye-bank Retina Clinical (not eyes utilised), ICU Total/Occupancy/averages (derived), and ICU tables whose month rows contradict their heading (Jan-Dec 2015 and Jan-Dec 2016 tables list April..March).

<details><summary>How it is collected and parsed</summary>

```text
SMIMER hospital miscellaneous statistics: milk bank, blood bank, eye bank and ICU (monthly).

Page: https://www.suratmunicipal.gov.in/smimer/Hospital/SHMiscellaneousStatistics
SMIMER (Surat Municipal Institute of Medical Education and Research) is the SMC-run medical college
hospital, so every value is filed under geo level `facility`, code `smimer` (parent smc_city).

The page has four sections, each a stack of 12-month tables (calendar years from 2015, financial
years April-March for 2011-12 to 2014-15); the section and the period come from the heading text
just before each table ("Blood Bank Statistics from January 2026 to December 2026"):

  Milk Bank   rows: collection (ml), milk given to newborns (ml), donor mothers, newborns receiving milk
  Blood Bank  rows: units collected (camp / blood bank / replacement / grand total), units issued by
              component under a "Smimer Hospital" sub-heading, units issued to other hospitals,
              donation camps
  Eye Bank    rows: eyes collected, eyes utilised (keratoplasty / sent to other eye bank / paediatric)
  I.C.U.      one row per month, one column per ICU (MICU, ICCU, SICU, PICU, NCU, RICU, OBS. ICU),
              then Total / Bed / Occupancy % / per-month and per-day averages

What is deliberately NOT emitted (ambiguous or derived):
  - Blood bank "Units Issued > Grand Total": in some months it equals the component rows, in others the
    component rows plus "Other Hospital" (and Jul 2020 matches neither), so its meaning is unclear.
  - Blood bank "Total Voluntary" (always camp + blood bank on this page; derivable, would double count).
  - Eye bank "Retina Clinical": listed under "No. of Eyes Utilised" but its values (e.g. 35-54 a month in
    2017) exceed the eyes collected, so it is not a count of eyes utilised. Mostly '-' anyway.
  - ICU Total, Occupancy %, pt./Month, pt./Day (Avg/Month, Avg/Day): derived from the monthly rows and beds.
  - ICU tables whose month rows contradict their heading: the tables headed "January 2016 to December
    2016" and "January 2015 to December 2015" list April..March, so the year of each row is ambiguous.
    They are skipped (see SKIPPED_NOTE); the same check skips any future table with that problem.

Overlapping tables (calendar 2015 vs FY 2014-15 / 2015-16) repeat the same months with the same values;
each month is emitted once. If two tables ever disagree on a month, that value is dropped rather than
choosing one (analyse() returns the conflicts and the skipped tables for inspection).
Months with no value in any row (future months of the current year) are not emitted; a blank or '-'
cell in a month that has other values becomes status 'not_reported'.
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `smimer.blood_components_issued` | Blood bank: units issued, by component | units | 1035 (1030) | 1 | 2011-04-01 to 2026-09-30 | Units issued in the month by component (dims.component), as listed under the page's "Smimer Hospital" sub-heading. The page is not consistent about whether these rows also cover units issued to other hospitals (its Grand Total sometimes adds the Other Hospital row, sometimes not), so do not add smimer.blood_units_issued_other_hospitals to them blindly. |
| `smimer.blood_donation_camps` | Blood bank: blood donation camps held | camps | 186 (186) | 1 | 2011-04-01 to 2026-09-30 | Number of blood donation camps in the month. |
| `smimer.blood_units_collected` | Blood bank: units collected, by type of donation | units | 558 (554) | 1 | 2011-04-01 to 2026-09-30 | Blood units collected in the month; dims.donation = voluntary_camp, voluntary_blood_bank or replacement. These add up to smimer.blood_units_collected_total. |
| `smimer.blood_units_collected_total` | Blood bank: units collected (grand total) | units | 186 (186) | 1 | 2011-04-01 to 2026-09-30 | Grand total of blood units collected in the month, as published. |
| `smimer.blood_units_issued_other_hospitals` | Blood bank: units issued to other hospitals | units | 186 (186) | 1 | 2011-04-01 to 2026-09-30 | Row "Other Hospital" under "No. of Blood Units Issued". |
| `smimer.eyes_collected` | Eye bank: eyes collected | eyes | 186 (186) | 1 | 2011-04-01 to 2026-09-30 | Number of eyes collected by the eye bank in the month. |
| `smimer.eyes_utilised` | Eye bank: eyes utilised, by use | eyes | 558 (558) | 1 | 2011-04-01 to 2026-09-30 | Eyes utilised in the month, dims.use = keratoplasty, sent_to_other_eye_bank or paediatric (row labels as published under "No. of Eyes Utilised"). |
| `smimer.icu_beds` | ICU beds | beds | 80 (80) | 1 | 2011-04-01 to 2026-12-31 | Beds per intensive care unit (dims.unit) as stated in the table for that year. |
| `smimer.icu_patient_count` | ICU patients (monthly figure per ICU) | patients | 939 (939) | 1 | 2011-04-01 to 2026-09-30 | Monthly figure per intensive care unit (dims.unit). The page does not say whether these are admissions or patient-days; its own occupancy row (figure / days / beds) treats them as patient-days. |
| `smimer.milk_collected_ml` | Human milk bank: milk collected | ml | 186 (186) | 1 | 2011-04-01 to 2026-09-30 | Amount of milk collected by the SMIMER human milk bank in the month. |
| `smimer.milk_donor_mothers` | Human milk bank: donor mothers | mothers | 186 (186) | 1 | 2011-04-01 to 2026-09-30 | Number of donor mothers in the month. |
| `smimer.milk_given_ml` | Human milk bank: milk given to newborns | ml | 186 (186) | 1 | 2011-04-01 to 2026-09-30 | Amount of milk donated to newborns in the month. |
| `smimer.milk_recipient_newborns` | Human milk bank: newborns receiving milk | newborns | 186 (186) | 1 | 2011-04-01 to 2026-09-30 | Number of newborns who received milk in the month. |

## smc_pmay

**SMC PMAY affordable housing projects**

- **Publisher:** Surat Municipal Corporation, Department of Affordable Housing
- **Page:** https://www.suratmunicipal.gov.in/Departments/PradhanMantriAwasYojana
- **Module:** housing; **cadence:** static (checked every 168 h)
- **Geography:** SMC city (projects are on SMC town-planning schemes; each record keeps its TP scheme and plot)
- **Licence:** Surat Municipal Corporation web page; public information
- **Enabled:** yes; **last success:** 2026-10-18T11:03:30+05:30
- **Holds:** 4 observations; records: housing_project (57)
- **Notes:** Counts are dated to the page footer "Last Updated" date. The published Total rows are not used (the work-in-progress Total repeats the completed one).

<details><summary>How it is collected and parsed</summary>

```text
SMC affordable housing (PMAY-Urban, AHP vertical): project list with flats, contractor, tender value and status.

Page: https://www.suratmunicipal.gov.in/Departments/PradhanMantriAwasYojana  (Department of Affordable Housing)
The "Projects" tab holds two tables, "Completed Projects" and "Work in Progress Projects" (both captioned
"LIG Housing"), with the same columns:

    Sr. No. (blank, numbered by CSS) | Project Name | Location | Name of Contractor | No. of Flats |
    Tender Amount Rs (in Lacs) | Status
    ... one row per project ...
    Total (colspan 4) | <flats> | <tender> |

Snapshot 2026-09-28: 46 completed projects (23,422 flats) and 11 in progress (6,454 flats).

-> one 'housing_project' record per row (the page is the complete list, so projects that disappear get closed),
   keyed by project name + TP scheme + final plot (e.g. 'suman-jyot-tp-9-fp-164'; the whole location text if
   those cannot be split out) because names repeat for different plots (SUMAN MALHAR S.P.2 / S.P.3, SUMAN VANDAN
   P1 / P2). A change of status keeps the key, so it shows up as a new version of the record.
-> smc_city observations per status: number of projects and flats, counted from the project rows.

Quirks of the page, kept as published:
- The "Total" row of the work-in-progress table repeats the completed table's total (23422 flats, 150686.87
  lakh), so the published Total rows are not stored; the aggregates are counted from the rows instead
  (for completed projects the row sum equals the published 23,422 flats, but the published tender Total of
  150,686.87 lakh is not the row sum of 157,601.84 lakh, so tender amounts are only kept per project).
- Two projects list two contractors and two tender amounts (Package-I / Package-II) in one cell. The amounts are
  kept as a list (tender_amounts_lakh) and summed in tender_amount_lakh; the contractor cell is kept as one string.
- SUMAN ADARSH (408 flats) shows a tender amount of 29.74 lakh, far below every other project; stored as published.
- Location strings are inconsistent ("T.P.No.9 (Palanpore-Bhesan), F.P.No. 164", "TP.No.62(...)", "T.P.No.48
  Bhestan, F.P.No.85"); tp_scheme / tp_area / final_plot are split out best-effort and the full text is kept.

Dating: the page has no data date of its own. Its footer "Last Updated: September 12, 2023 05:04 PM" is the CMS
edit date of this page (it differs from page to page across SMC's site and is years older than the snapshot), so
the counts are filed as an instant reading on that date with publisher_as_of set to it. A later edit of the page
moves the date and starts a new point in the series.
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `pmay.flats` | Flats in PMAY housing projects | flats | 2 (2) | 1 | 2023-09-12 to 2023-09-12 | Sum of "No. of Flats" over the listed projects, by dims.status. not_reported if any project in that group has a blank flat count. |
| `pmay.projects` | PMAY housing projects | projects | 2 (2) | 1 | 2023-09-12 to 2023-09-12 | Number of SMC PMAY (affordable housing) projects listed on the page, by dims.status (completed / work_in_progress). Counted from the project rows. |

## smc_recruitment

**SMC current recruitment advertisements**

- **Publisher:** Surat Municipal Corporation (Recruitment cell)
- **Page:** https://www.suratmunicipal.gov.in/Information/Recruitment
- **Module:** jobs; **cadence:** daily (checked every 24 h)
- **Geography:** SMC city (posts in Surat Municipal Corporation)
- **Licence:** Surat Municipal Corporation web page; public information
- **Enabled:** yes; **last success:** 2026-10-24T22:44:24+05:30
- **Holds:** 2 observations; records: recruitment_ad (2)
- **Notes:** Titles are Gujarati only. Counts are dated to the fetch day because the page has no data date. "Remaining Day(s)" is not stored. The advertisement PDFs and the results/answer-key pages are not fetched.

<details><summary>How it is collected and parsed</summary>

```text
SMC current recruitment: open job advertisements of Surat Municipal Corporation, as records plus daily counts.

Publisher: Surat Municipal Corporation (Recruitment cell; advertisements are issued as PRO press notices). The page
is "Current Recruitment", linked from the Recruitment Dashboard. Queries go to recruitment@suratmunicipal.org
(printed on the page).

Endpoint: one plain GET, no parameters, no login or captcha (robots.txt on www.suratmunicipal.gov.in returns
404, so nothing is disallowed):

    https://www.suratmunicipal.gov.in/Information/Recruitment

Response layout (server-rendered HTML, no tables). One panel per organisation (heading "Surat Municipal
Corporation"), a section label (<li class="... text-2x text-bold">Opening</li>), then one <li> per advertisement:

    <p class="gujartifont">જાહેરાત ક્રમાંક :પી.આર.ઓ.નં.૩૦૧, તા.૨૧/૧૦/૨૦૨૬ થી સુરત મહાનગરપાલિકાની ...</p>
    <span class="emag-link pad-r5">No of post(s):</span>18
    <span class="emag-link pad-r5">Application Start Date:</span>09/11/2026 11:00 AM
    <span class="emag-link pad-r5">Application End Date:</span>23/11/2026 11:00 PM
    <span class="emag-link pad-r5">Remaining Day(s):</span> 30 day(s)        ("Today" on the last day)
    <a href=".../Recruitment/">Apply Now</a>                  (only while applications are open)
    <a href=".../Contents/Jobs/Opening/1973333.pdf">View More</a>   (the advertisement PDF; not fetched)

The title is Gujarati only and starts with the advertisement number: "જાહેરાત ક્રમાંક :પી.આર.ઓ.નં.૩૦૧,
તા.૨૧/૧૦/૨૦૨૬" means "Advertisement no.: P.R.O. No. 301, dated 21/10/2026" (Gujarati digits).

-> 'recruitment_ad' records, one per advertisement. The page is the complete current list, so an advertisement
   that is taken off the page gets closed. Key: 'pro-<no>-<ad date>' (e.g. 'pro-301-2026-10-21'); if the PRO
   number cannot be read, 'pdf-<file name>' from the View More link. Attributes:
     pro_no             PRO advertisement number (int), from the title
     ad_date            date of the PRO notice (ISO), from the title
     title              the full Gujarati title as published
     posts              "No of post(s)" (int; None if blank)
     application_start  "Application Start Date" (ISO local datetime)
     application_end    "Application End Date" (ISO local datetime)
     organisation       panel heading ("Surat Municipal Corporation")
     section            section label ("Opening")
     notice_pdf         the "View More" advertisement PDF link
     apply_url          the "Apply Now" link, or None when the page shows none
   "Remaining Day(s)" is NOT stored: it changes every day and would create a new record version daily.

-> smc_city observations, an instant reading dated to the day of the fetch (Asia/Kolkata, from Raw.retrieved_at),
   because the page has no data date of its own:
     recruitment.open_ads  number of advertisements on the page (0 is a real value when the list is empty)
     recruitment.posts     sum of "No of post(s)" over those advertisements; not_reported if any is blank
   validate() checks that "Application End Date" minus "Remaining Day(s)" gives the fetch date (within a day),
   so a stale cached page is caught. The footer "Last Updated" is a CMS edit time and is not used.

Snapshot 2026-10-24: two advertisements. PRO No. 301 of 21/10/2026: waiting list for 9 cadres, 18 posts,
applications 09/11/2026 11:00 AM to 23/11/2026 11:00 PM. PRO No. 263 of 29/09/2026: honorary sports coaches
(contract) for the Navagam-Dindoli sports complex, South East Zone, 8 posts, closing 24/10/2026 11:00 PM.

Quirks and caveats:
- An advertisement can be listed before its application window opens (PRO 301 above), so "listed" is not the
  same as "accepting applications". Compare application_start/application_end with the date if that matters.
- "No of post(s)" can count waiting-list places, not only vacancies, as in PRO 301.
- The advertisement PDFs, the Recruitment Dashboard and its news, answer-key, result and selection-list pages
  (/Information/RecruitmentNews) are not fetched. State and national exams (GPSC, GSSSB, UPSC, SSC) are other
  sources.

Geography: SMC city (jobs in the corporation). Cadence: daily (the list changes when advertisements are added or
expire). Units: advertisements and posts. Licence: Surat Municipal Corporation web page; public information. No
explicit open licence.
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `recruitment.open_ads` | SMC recruitment advertisements listed | advertisements | 1 (1) | 1 | 2026-10-24 to 2026-10-24 | Number of advertisements on SMC's "Current Recruitment" page on the fetch day. Includes advertisements whose application window has not opened yet. |
| `recruitment.posts` | Posts in listed SMC recruitment advertisements | posts | 1 (1) | 1 | 2026-10-24 to 2026-10-24 | Sum of "No of post(s)" over the advertisements listed on the fetch day (may include waiting-list places). not_reported if any listed advertisement gives no number. |

## smc_officials

**SMC officials: Municipal Commissioner, Deputy Municipal Commissioners and department officers**

- **Publisher:** Surat Municipal Corporation (administrative wing)
- **Page:** https://www.suratmunicipal.gov.in/Home/SMCOfficials
- **Module:** leadership; **cadence:** weekly (checked every 168 h)
- **Geography:** SMC city (officers of the corporation; Food Safety Officer cards name their zone)
- **Licence:** Surat Municipal Corporation web page; public information about public officials
- **Enabled:** yes; **last success:** 2026-10-24T22:00:38+05:30
- **Holds:** 0 observations; records: smc_official (92)
- **Notes:** Names, designations, wing, zone, office ("(O)") phone numbers and official e-mail only. The "(M)" mobile numbers and gmail/yahoo addresses printed on the page are not stored and are blanked in the raw archive; "(O)" entries in mobile format are dropped too. The e-mail domain comes from the page's own script ("[at]suratmunicipal[dot]gov[dot]in").

<details><summary>How it is collected and parsed</summary>

```text
SMC administrative wing: the Municipal Commissioner and the officers listed on SMC's "SMC Officials" page.

Publisher: Surat Municipal Corporation (administrative wing; the page sits under "Contact Us" on the SMC site).

Endpoint: one plain GET, no parameters, no login or captcha (robots.txt on www.suratmunicipal.gov.in returns 404,
so nothing is disallowed):

    https://www.suratmunicipal.gov.in/Home/SMCOfficials

Response layout (server-rendered HTML, no tables). After the head-quarter and zone contact boxes (those belong to
the smc_zone_offices and smc_helplines sources and are not read here) comes "Contact Details of SMC Officers":

    <h3>Municipal Commissioner</h3>
      <div class="contact-block"> <div class="name">Shri Rajkumar Beniwal, IAS</div>
        <div class="designation">Municipal Commissioner, Surat Municipal Corporation</div>
        <div class="officeTelephone">(O) +91-261-2422244</div> <div class="faxNumber">(F) +91-261-2422110</div>
    <div class="contact-heading">Administrative | Engineering | Health</div>
      <ul> <li class="contact-block"> one card per officer:
        <div class="name">Ms. Nidhi Siwach (IAS)</div>
        <div class="text-bold">South West Zone(Athwa)</div>         (only on some Health cards: the zone)
        <div class="designation">Deputy Mun. Commissioner (Deputation)</div>
        <div class="contact-mobile">(M) ..........</div>             (NOT stored, see below)
        <div class="officeTelephone">(O) 0261-2423750 (PABX - 222)</div>   (0..n)
        <div class="contact-email govdotin">dmc.ns</div>             (0..n; also as <span> inside a wrapper)

The "govdotin" e-mail cells hold only the local part; a script at the end of the page appends
"[at]suratmunicipal[dot]gov[dot]in". parse() reads that suffix from the script (it fails if the script is gone)
instead of assuming it.

-> one 'smc_official' record per card (snapshot 2026-10-24: 92 cards: the Commissioner, 42 Administrative,
   16 Engineering, 33 Health, including 7 Deputy Municipal Commissioners and 20 zone Food Safety Officers).
   The page is the complete list, so an officer who disappears from it gets closed. Record attributes:
     wing         'commissioner', 'administrative', 'engineering' or 'health' (the page's grouping)
     designation  as printed, e.g. 'Executive Engineer (Hydraulic)': the department is part of it
     name         as printed without the honorific and service suffix; honorific ('Shri', 'Sh.', 'Smt.', 'Ms.',
                  'Dr.' ...) and service ('IAS' when the page says so) are kept separately
     zone, zone_code  the zone line of a card (Food Safety Officers) and its canonical code from surat.zone_code()
     office_phones    the "(O)" numbers as printed (STD 0261 for Surat; "to 56" ranges and PABX extensions kept
                      as text), list; the Commissioner card also has fax
     emails       official addresses only (domains gov.in, nic.in, suratmunicipal.org), list
   Keys: the designation slug (e.g. 'chief-fire-officer'), so a change of officer shows up as a new version of the
   same role. Designations printed on more than one card (5 x 'Deputy Mun. Commissioner', 20 x 'Food Safety
   Officer', ...) get the officer's name slug appended ('deputy-mun-commissioner-swati-p-desai').

What is deliberately NOT stored (whitelist; validate() rejects anything else):
- "(M)" mobile numbers. The page prints a mobile for almost every officer; they are personal contacts of the
  officer and are kept out of the database and, via normalize(), out of the raw archive too.
- Office numbers in mobile format. One card lists three 10-digit mobile numbers as "(O)"; the page does not say
  whether these are desk phones or the officer's own mobile, so any "(O)" entry that is a mobile number is dropped
  (it stays in the archived page, where SMC labels it as an office number).
- E-mail addresses on non-government domains. The 20 Food Safety Officer cards print gmail/yahoo addresses named
  after the officer; they are not stored and are blanked in the archive.
No observations are emitted: a count of names on a web page is not a statistic worth a time series.

Quirks, kept as published: honorifics do not always match the officer ("Sh." on several women's names); some
office numbers sit in the CSS class meant for mobiles, so a number is classified by its "(O)"/"(M)"/"(F)"
prefix, not by the class; one card prints the mobile-style prefix "(M)" and an office number "(O)" in two
"contact-mobile" divs. The footer "Last Updated" is the CMS edit time of the page, not a data date; it is not used.

Geography: SMC city (the corporation's officers). Cadence: no schedule, changes with transfers and postings;
checked weekly.
Licence: Surat Municipal Corporation web page; public information about public officials. No explicit licence.
```

</details>

## surat_collectorate

**Surat district Who's Who: Collector, Collectorate and Prant officers**

- **Publisher:** District Administration Surat (Collectorate), surat.nic.in (NIC S3WaaS)
- **Page:** https://surat.nic.in/whos-who/
- **Module:** leadership; **cadence:** weekly (checked every 168 h)
- **Geography:** Surat district: the Collectorate and its Prant (sub-division) offices
- **Licence:** surat.nic.in, content owned by District Administration Surat; no explicit reuse licence
- **Enabled:** yes; **last success:** 2026-10-24T22:01:50+05:30
- **Holds:** 0 observations; records: district_official (11)
- **Notes:** Name, designation, division, office address, office phone/fax and government-domain e-mail only. The gmail.com addresses printed for the Prant offices and the Land Reform branch are not stored.

<details><summary>How it is collected and parsed</summary>

```text
Surat district administration Who's Who: the Collector, Collectorate officers and the Prant (sub-division) officers.

Publisher: District Administration Surat (Collectorate), on its NIC S3WaaS website surat.nic.in ("Content Owned by
District Administration", developed and hosted by the National Informatics Centre).

Endpoint: one plain GET, no parameters, no login or captcha (https://surat.nic.in/robots.txt returns an empty
204 response, so nothing is disallowed):

    https://surat.nic.in/whos-who/

The page's division filter ("All", "Prant Officers", "Collectorate") only hides tables in the browser; the default
"All" page already carries every table, so nothing else is requested.

Response layout (WordPress HTML), one table per division, each with a <caption>:

    <caption>Collectorate</caption>     (5 rows on 2026-10-24)
    <caption>Prant Officers</caption>   (6 rows on 2026-10-24)
    Name | Designation | Email | Address | Phone | Fax
    Shri Tejas Parmar IAS | Collector & District Magistrate | collector-sur[at]gujarat[dot]gov[dot]in |
        Collector Office, Jilla Seva Sadan-II, "B" Block, 5th Floor, Athwalines, Surat-395001 | +91-261-2655151 |
        +91-261-2655757

-> one 'district_official' record per row, keyed by the designation slug (e.g. 'collector-district-magistrate',
   'deputy-collector-prant-officer-bardoli'), so a change of officer shows up as a new version of the same post
   (a designation printed twice would get the officer's name slug appended). The page is the complete list, so a
   post that disappears gets closed. Attributes:
     division     the table caption as printed ('Collectorate' or 'Prant Officers')
     designation  as printed; for Prant Officers it names the sub-division (Surat South, City North/Adajan, Mandvi,
                  Bardoli, Kamrej, Olpad)
     name         as printed, without the honorific ('Shri', 'Shri.') and the service ('IAS'), which are kept
                  separately as honorific / service
     email        the address decoded from "[at]"/"[dot]", kept ONLY on a government domain (gujarat.gov.in,
                  gov.in, nic.in); None otherwise
     office_address  the office address as printed (Jilla Seva Sadan, Taluka Seva Sadan, ...): an office, never a
                  residence
     phones, fax  the office numbers as printed, split at commas (e.g. '+91-261-2655151', '91-2623-221177');
                  mobile-format numbers would be dropped (none on the 2026-10-24 page)

Not stored: the gmail.com addresses that the Dy. Collector (Land Reform) and the six Prant offices publish
(e.g. a "prantmandvi" account). They look like office accounts, but an automatic rule cannot tell an office gmail
from a personal one, so only government-domain addresses are kept; the page itself remains the reference.

Quirks, kept as published: honorifics do not always match the officer ("Shri" before women's names); phone
numbers are printed with and without the leading "+"; the City Prant (North) and Surat Prant (South) share the
number 2665800. The site footer "Last Updated: 06.08.2019" is a template date, not the date of this list; it is
not used. The data has not changed between our saved copy of 2026-09-28 and 2026-10-24 (the site theme did).
The page carries a WordPress nonce that changes on every request; normalize() blanks it so an unchanged list is
recognised as unchanged.

No observations are emitted: a count of posts on a web page is not a statistic worth a time series.
Geography: Surat district (Collectorate) and its Prant sub-divisions, as text in the designation. Cadence: no
schedule, changes with transfers; checked weekly.
Licence: Government of Gujarat district website (S3WaaS); content owned by District Administration Surat; no
explicit reuse licence found. Public information about public officials.
```

</details>

## smc_zone_offices

**SMC zone offices: addresses and official phone numbers**

- **Publisher:** Surat Municipal Corporation
- **Page:** https://www.suratmunicipal.gov.in/Home/ZoneOfficials
- **Module:** offices; **cadence:** static (checked every 168 h)
- **Geography:** SMC zones (smc_zone, codes from surat.zone_code()): one office per zone
- **Licence:** Surat Municipal Corporation web page; public information
- **Enabled:** yes; **last success:** 2026-10-24T22:01:49+05:30
- **Holds:** 0 observations; records: smc_zone_office (9)
- **Notes:** Numbers are kept as printed (ranges not expanded; 7-digit numbers are Surat 0261 landlines). Mobile numbers are stored only because SMC prints them as the zone office or control-room contact. Zone detail pages are not fetched.

<details><summary>How it is collected and parsed</summary>

```text
SMC zone offices: address, telephone, office/control-room mobile and fax numbers of the nine zone offices.

Publisher: Surat Municipal Corporation (the "Zone Officials" page under "Contact Us" on the SMC site).

Endpoint: one plain GET, no parameters, no login or captcha (robots.txt on www.suratmunicipal.gov.in returns 404,
so nothing is disallowed):

    https://www.suratmunicipal.gov.in/Home/ZoneOfficials

Response layout (server-rendered HTML, no tables), one box per zone inside <div class="zones-contact">:

    <div class="contact-heading">Central Zone</div>
    <div class="contact-block">
      <div class="mar-b10">Central Zone Vahivati Bhavan, Gordhandas Chokhawala Marg, Shri Tapipura, Surat-395003</div>
      <div><span class="text-bold">Contact No. </span> 2427726</div>
      <div><span class="text-bold">Mobile No. </span>9727740932</div>
      <div><span class="text-bold">Fax No. </span>2420548 | <span class="text-bold">Control Room No. </span>2420547</div>
      <div class="zone-contact-details"><a href="/Zones/Central/CentralZone">Contact Details</a></div>

-> one 'smc_zone_office' record per box, keyed by the canonical zone code from surat.zone_code() ('west', 'central',
   'north', 'east_a', 'east_b', 'south_a', 'south_b', 'south_west', 'south_east'), plus the smc_zone geographies.
   The page is the complete list, so a zone box that disappears gets closed. Attributes:
     zone          the box heading as printed ('East Zone A')
     zone_code     canonical code (joins to geo level smc_zone)
     address       office address as printed (the zone office building, not a person's address)
     phones        "Contact No." entries, list
     mobiles       "Mobile No." entries: mobile numbers SMC prints as the zone office's own contact, list
     fax           "Fax No." entries, list
     control_room  "Control Room No." entries, list
     control_room_mobiles  "Control Room Mob. No." / "Control RoomMobile No." entries, list
     detail_url    the zone's "Contact Details" page (not fetched)
   Every number list keeps the entries exactly as printed, split only at commas: ranges such as "2786181 to 83",
   "9724346011-13" or "2331903-04-05" are NOT expanded. Seven-digit numbers are Surat landlines (STD code 0261).
   An unknown label raises an error so that a new kind of number is noticed rather than lost.

Snapshot 2026-10-24 (page footer "Last Updated: September 08, 2026"): nine zones. The same boxes are repeated on
/Home/SMCOfficials; this source reads them from the dedicated page only. The footer date is the CMS edit time of
the page, not a data date; it is not used.

Quirks, kept as published: East Zone B lists only control-room mobiles, the first of which (6559909506) looks like a
typo of 6359909506; South Zone B lists two mobile-format numbers under "Contact No."; some numbers are shared with
SMC's emergency page (smc_helplines), where the zones appear under their older names. The per-zone
"Contact Details" pages (zonal chief and zone officers with their personal mobiles) are not fetched.

No observations are emitted: the number of zone offices is a fixed fact of SMC's organisation, not a statistic.
Geography: SMC zones (smc_zone). Cadence: static reference data, edited without schedule; checked weekly.
Licence: Surat Municipal Corporation web page; public information. No explicit licence.
```

</details>

## surat_talukas

**Surat district talukas and Mamlatdar offices**

- **Publisher:** District Administration Surat (Collectorate), surat.nic.in (NIC S3WaaS)
- **Page:** https://surat.nic.in/taluka/
- **Module:** offices; **cadence:** static (checked every 720 h)
- **Geography:** Surat district talukas (surat_taluka, parent surat_district): 17 on 2026-10-24, six of them in Surat City
- **Licence:** surat.nic.in, content owned by District Administration Surat; no explicit reuse licence
- **Enabled:** yes; **last success:** 2026-10-24T22:44:28+05:30
- **Holds:** 0 observations; records: taluka_office (17)
- **Notes:** Taluka list, Mamlatdar office address, office phone and government-domain e-mail only. The gmail.com addresses printed for the city talukas and Ambika are not stored. No boundaries are published.

<details><summary>How it is collected and parsed</summary>

```text
Surat district talukas: the official list of talukas and their Mamlatdar offices, from the Collectorate website.

Publisher: District Administration Surat (Collectorate), on its NIC S3WaaS website surat.nic.in ("Content Owned by
District Administration", developed and hosted by the National Informatics Centre).

Endpoint: one plain GET, no parameters, no login or captcha (https://surat.nic.in/robots.txt returns an empty 204
response, so nothing is disallowed):

    https://surat.nic.in/taluka/

Response layout (WordPress HTML): a few paragraphs on the role of the Mamlatdar (the head of a taluka's revenue
administration), then one table with a header row and one row per taluka (17 rows on 2026-10-24):

    SNo. | Taluka Name | Office Address | Phone | EMail
    1  | Majura (Surat City) | Mamlatdar Office of SuratCity Taluka, Athwalines, Opp: District Court, Surat |
         0261-2650335 | 01[dot]mammajura[at]gmail[dot]com
    8  | Olpad | Mamlatdar Office, Olpad | 02621-221245 | mam-olpad[at]gujarat[dot]gov[dot]in
    17 | Areth | Mamlatdar Office, Areth | 02623-261023 | mam-areth[at]gujarat[dot]gov[dot]in

The 17 talukas are six "(Surat City)" talukas (Majura, Udhna, Katargam, Puna, Adajan, Abrama) and the eleven
rural talukas Chorasi, Olpad, Mangrol, Umarpada, Mandvi, Bardoli, Mahuva, Kamrej, Palsana, Ambika and Areth.

Geography: every row becomes a geo of level surat_taluka (parent surat_district/surat). The level is shared with
gsdma_rainfall, census2011_surat and shc_soil_surat, and the codes and names of the talukas they also use are
the same (e.g. chorasi = 'Chorasi (Choryasi)'), so the sources do not rename each other's geos. Codes are the
lower-case taluka names (TALUKAS); an unknown name fails validation instead of inventing a code. The six city
talukas are new codes (majura, udhna, katargam, puna, adajan, abrama). Other sources still report one 'Surat City'
taluka (surat_city: Census 2011, GSDMA rainfall, Soil Health Card); this page does not say how the six city
talukas relate to it, so no parent link between them is stored. No boundaries are published.

Records: 'taluka_office', one per row, keyed by the taluka code (e.g. 'olpad'); the page is the complete list, so
a taluka that disappears gets closed. Attributes:
    taluka          the name as printed ('Majura (Surat City)')
    surat_city      True for the six talukas printed with "(Surat City)"
    office_address  the Mamlatdar office address as printed (an office, never a residence)
    phone           the office landline as printed ('02621-221245'); None if blank. A mobile-format number
                    would be dropped (there is none on the 2026-10-24 page).
    email           the address decoded from "[at]"/"[dot]", kept ONLY on a government domain (gujarat.gov.in,
                    gov.in, nic.in); None otherwise

No observations are emitted: the list of talukas is a geography, not a statistic.

Quirks, kept as published:
- The six city talukas and Ambika publish gmail.com addresses (e.g. "01[dot]mammajura[at]gmail[dot]com", two of
  them malformed, missing "[at"); they look like office accounts, but an automatic rule cannot tell an office
  gmail from a personal one, so they are not stored (email = None).
- Kamrej's row gives "Mamlatdar Office, Bardoli" and mam-bardoli@gujarat.gov.in (Bardoli's own address and email),
  and Umarpada's gives "Mamlatdar Office, Mangrol"; probably copy errors on the page, stored as published.
- Majura and Udhna share one office and phone; Katargam, Puna and Adajan share the Old Collector Office, Nanpura.
- Abrama and Ambika have no phone number.
- Ambika and Areth are not Census 2011 sub-districts (Census 2011 had 10 talukas), so census figures do not line
  up one-to-one with this list.
- The footer "Last Updated: 28.09.2026" is a site-wide date, not the date of this list; it is not used.

Cadence: no schedule; the list changes only when talukas are created or offices move. Checked monthly.
Licence: Government of Gujarat district website (S3WaaS); content owned by District Administration Surat; no
explicit reuse licence found. Public information about government offices.
```

</details>

## ncrb_metro_surat

**NCRB Crime in India: Surat metropolitan city**

- **Publisher:** National Crime Records Bureau, Ministry of Home Affairs (Crime in India 2024); tables mirrored as XLSX by OpenCity Foundation (data.opencity.in)
- **Page:** https://data.opencity.in/dataset/crime-in-india-2024
- **Module:** police; **cadence:** annual (checked every 720 h)
- **Geography:** Surat as an NCRB metropolitan city (city police reporting area, Census 2011 population 45.85 lakh); not SMC limits and not Surat Rural
- **Licence:** Government of India (NCRB) publication; mirror labelled "Other (Public Domain)". Attribute "NCRB, Crime in India 2024 (via data.opencity.in)".
- **Enabled:** yes; **last success:** 2026-10-24T22:00:22+05:30
- **Holds:** 56 observations
- **Notes:** Mirror of NCRB tables: ncrb.mha.gov.in disallows all robots and publishes PDFs. Surat rows of 1B.1, 1B.2, 1B.3, 3B.1 and 4B.1 were checked against the NCRB Volume I PDF. 10 downloads per edition, 10 s apart (robots.txt Crawl-Delay); the CKAN API (/api/) is disallowed and not used. Rates use Census 2011 population; 3B.1 rates are per lakh women.

<details><summary>How it is collected and parsed</summary>

```text
NCRB "Crime in India 2024": Surat as one of the 19 metropolitan cities (cases, crime rate, chargesheeting rate).

Publisher of the data: National Crime Records Bureau (NCRB), Ministry of Home Affairs, Government of India,
"Crime in India 2024" (calendar year 1 January - 31 December 2024; tables show 2022, 2023 and 2024).
Files actually fetched: a MIRROR. OpenCity Foundation re-published the metropolitan-city tables as one-sheet
.xlsx files in its CKAN catalogue, dataset "Crime in India - 2024" (data.opencity.in/dataset/crime-in-india-2024,
licence shown as "Other (Public Domain)", organisation "Government of India (GoI)", uploaded 2026-05-07).
NCRB's own site cannot be used by this bot: www.ncrb.gov.in redirects to www.ncrb.mha.gov.in, whose robots.txt
is "User-agent: * / Disallow: /" (checked 2026-10-24), and NCRB publishes the tables as PDF, not as plainly
machine-readable files. data.opencity.in's robots.txt disallows /api/ (so the CKAN API is NOT used) and asks
for "Crawl-Delay: 10"; the resource download URLs below are allowed. fetch() waits 10 s between files.

Requests: one GET per table (10 per run), each a CKAN resource download
    https://data.opencity.in/dataset/7d883875-921a-4820-b298-713c6219bd90/resource/<resource id>/download/<file>
with no parameters. The edition is immutable, so each file is downloaded once (skip_if_seen) and only re-parsed
from the archive after a parser change. A new edition (Crime in India 2025) needs new URLs in TABLES.

File layout (first worksheet; the title is in A1, or "TABLE 6B.1" in A1 and the title in A2):
    TABLE 1B.3 - Total IPC/BNS & SLL Crimes in Metropolitan Cities - 2022-2024
    SL | City | 2022 | 2023 | 2024 | Actual Population (in Lakhs) (2011) | Rate of Cognizable Crimes (IPC+SLL) (2024)
       | Chargesheeting Rate (2024)
    1  | Ahmedabad (Gujarat) | 53845 | ...       (19 city rows, then "TOTAL CITIES")
    19 | Surat (Gujarat)     | 55300 | 63142 | 63166 | 45.8 | 1377.7 | 97.7
Column sets differ by table: 1B.1 and 6B.1 split 2024 into "2024 IPC Cases" / "2024 BNS Cases" / "2024 Total
(IPC+BNS)" (or "2024 (IPC)" / "2024 (BNS)" / "2024 (Total)"); 4B.1, 6B.1, 7B.1 and 7D.1 have no population or
rate (NCRB: no city population figures for children, SCs/STs or senior citizens). parse() reads the header row
and fails on any column it does not know. Only the Surat row is stored; "-" cells become not_reported.

Tables and dims.crime_group:
    1B.1 ipc_bns                  IPC/BNS crimes (2024: IPC and BNS cases shown separately)
    1B.2 sll                      Special & Local Laws crimes
    1B.3 all_cognizable           total cognizable crimes, IPC/BNS + SLL
    3B.1 against_women            crime against women (IPC/BNS + SLL)
    4B.1 against_children         crime against children (IPC/BNS + SLL)
    6B.1 against_senior_citizens  crime against senior citizens (60 years and above)
    7B.1 against_sc               crime/atrocities against Scheduled Castes
    7D.1 against_st               crime/atrocities against Scheduled Tribes
    8B.1 economic_offences        economic offences
    9B.1 cyber                    cyber crimes
(The package's head-wise table 8B.2 and the PDF volumes are not fetched.)

Metrics (geo ncrb_metro_city/surat; periods are calendar years):
    ncrb.cases_registered        cases registered in the year, dims crime_group and law (all; for 2024 in tables
                                 1B.1 and 6B.1 also ipc / bns = registered under the IPC / under the Bharatiya
                                 Nyaya Sanhita, which replaced the IPC on 1 July 2024; ipc + bns = all)
    ncrb.crime_rate_per_lakh     cases per lakh population in 2024, dims crime_group
    ncrb.chargesheeting_rate_pct cases chargesheeted / cases disposed of by police x 100 (NCRB's definition), 2024
    ncrb.rate_population_lakh    the Census 2011 population (lakh) the table divides by, dims crime_group;
                                 filed on the census reference date 2011-03-01
Units: cases; cases per 100,000 people; percent; lakh persons (1 lakh = 100,000).

Geography: new geo level ncrb_metro_city (code 'surat', parent surat_district). NCRB prints these tables for the
19 metropolitan cities with a Census 2011 population above 20 lakh; the figures come from each State Crime
Records Bureau. The reporting area is the city as policed and reported (presumably the Surat
City Police Commissionerate); NCRB does not publish its boundary. It is NOT the SMC area (smc_city) and NOT the
whole district (Surat Rural police is reported separately and is not covered here). The rate base is the Census
2011 "actual population" of the city, 45.85 lakh for Surat (printed as 45.8).

Caveats (from NCRB's notes in the publication):
- Counting follows the Principal Offence Rule: an FIR with several offences counts once, under the most serious.
- Metro-city rates use the 2011 census population while state rates use 2024 projections, so city and state rates
  are not comparable. For a city that has grown since 2011, a rate on the 2011 population is higher than the
  crime per current resident.
- In 3B.1 the population column is the female population (Surat 19.7 lakh; 540.9 for all 19 cities against
  1140.4 total), and the rate is per lakh women, although both the PDF and the mirror label it "Actual Population".
- NCRB: "States/UTs/Cities may not be compared purely on the basis of crime figures"; higher registration can
  reflect better reporting.
- The mirror stores some numbers as binary floats ("73.90000000000001"); values are rounded to 6 decimals.
- Cross-check done 2026-10-24: the Surat rows of 1B.1, 1B.2, 1B.3, 3B.1 and 4B.1 match the NCRB Crime in India 2024
  Volume I PDF (the copy in the same dataset) exactly. Tables 6B.1-9B.1 (footer "Volume II") were not checked
  against the PDF.

Licence: NCRB "Crime in India" is a Government of India publication; the mirror labels it "Other (Public Domain)".
Attribute "NCRB, Crime in India 2024 (via data.opencity.in)".
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `ncrb.cases_registered` | Crimes registered (NCRB, metropolitan city) | cases | 34 (34) | 1 | 2022-01-01 to 2024-12-31 | Cases registered in the calendar year by dims.crime_group (all_cognizable, ipc_bns, sll, against_women, against_children, against_senior_citizens, against_sc, against_st, economic_offences, cyber) and dims.law (all; for 2024 in ipc_bns and against_senior_citizens also ipc and bns = registered under the IPC / under the BNS). Principal Offence Rule. |
| `ncrb.chargesheeting_rate_pct` | Chargesheeting rate (NCRB, metropolitan city) | % | 10 (10) | 1 | 2024-01-01 to 2024-12-31 | Cases chargesheeted / cases disposed of by police x 100 in the year, by dims.crime_group. not_reported where NCRB prints "-". |
| `ncrb.crime_rate_per_lakh` | Crime rate (NCRB, metropolitan city) | cases per lakh population | 6 (6) | 1 | 2024-01-01 to 2024-12-31 | Cases registered in the year per 1,00,000 population, using the Census 2011 population in ncrb.rate_population_lakh (female population for against_women). By dims.crime_group. |
| `ncrb.rate_population_lakh` | Population used for the crime rate (Census 2011) | lakh persons | 6 (6) | 1 | 2011-03-01 to 2011-03-01 | The Census 2011 population (in lakh) that the table divides by for the crime rate of dims.crime_group: the whole city population, or the female population for against_women. |

## census2011_surat

**Census 2011: Primary Census Abstract and household amenities, Surat district**

- **Publisher:** Office of the Registrar General & Census Commissioner, India (Census of India 2011); CSV mirror by the pigshell/india-census-2011 GitHub repository
- **Page:** https://github.com/pigshell/india-census-2011
- **Module:** population; **cadence:** static (checked every 2160 h)
- **Geography:** Surat district (2011 boundaries, Total/Rural/Urban), its 10 Census 2011 sub-districts (surat_taluka; houselisting tables only) and Gujarat state for comparison. "Surat City" sub-district is the 2011 SMC area, not today's smc_city.
- **Licence:** Census of India 2011 data (Office of the Registrar General & Census Commissioner, India), attribute ORGI. Mirror code MIT (c) 2014 ganeshv; the mirror states no licence for the data.
- **Enabled:** yes; **last success:** 2026-10-24T21:58:25+05:30
- **Holds:** 4905 observations
- **Notes:** Fetched from a GitHub mirror because censusindia.gov.in fails TLS certificate verification (incomplete chain). The mirror disclaims correctness, so validate() requires its Surat totals to match the official DCHB Surat 2011. Houselisting values are % of households (no counts). Sub-district population, village and town counts are not in the mirror and are not stored. Ratios (sex ratio 787, child sex ratio 835, literacy 85.53 %, density 1,337/sq km) are not stored; compute them from the counts.

<details><summary>How it is collected and parsed</summary>

```text
Census of India 2011, Surat district: Primary Census Abstract (PCA) and Houselisting PCA (household amenities).

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
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `census.area_km2` | Area (Census 2011) | sq km | 6 (6) | 2 | 2011-03-01 to 2011-03-01 | Area in square kilometres as given in the Census 2011 PCA, by dims.residence (total / rural / urban). Population density = census.population / census.area_km2. |
| `census.hh_assets_pct` | Households by assets owned (Census 2011) | % of households | 396 (396) | 12 | 2010-04-01 to 2010-09-30 | Share of households having each asset (dims.item). Not exclusive: a household can own several. none = none of the listed assets. |
| `census.hh_banking_pct` | Households availing banking services (Census 2011) | % of households | 33 (33) | 12 | 2010-04-01 to 2010-09-30 | Share of households availing banking services (dims.item availing_banking). |
| `census.hh_bathing_pct` | Households by bathing facility (Census 2011) | % of households | 99 (99) | 12 | 2010-04-01 to 2010-09-30 | Share of households with a bathroom, an enclosure without roof, or no bathing facility within the premises (dims.item). |
| `census.hh_condition_pct` | Households by condition of the census house (Census 2011) | % of households | 363 (363) | 12 | 2010-04-01 to 2010-09-30 | Share of households living in a census house in good / livable / dilapidated condition (dims.item). The residence_* and residence_cum_other_* items split the same households into houses used only as a residence and houses also used for other purposes. |
| `census.hh_cooking_fuel_pct` | Households by cooking fuel (Census 2011) | % of households | 330 (330) | 12 | 2010-04-01 to 2010-09-30 | Share of households by main type of fuel used for cooking (dims.item), e.g. lpg_png, firewood. |
| `census.hh_drainage_pct` | Households by waste-water outlet (Census 2011) | % of households | 99 (99) | 12 | 2010-04-01 to 2010-09-30 | Share of households whose waste-water outlet is connected to closed drainage, open drainage or no drainage (dims.item). |
| `census.hh_floor_pct` | Households by floor material (Census 2011) | % of households | 231 (231) | 12 | 2010-04-01 to 2010-09-30 | Share of households by predominant material of the floor (dims.item). |
| `census.hh_kitchen_pct` | Households by kitchen facility (Census 2011) | % of households | 231 (231) | 12 | 2010-04-01 to 2010-09-30 | Share of households cooking inside the house (with / without a kitchen), outside the house (with / without a kitchen) or not cooking (dims.item). |
| `census.hh_latrine_pct` | Households by latrine facility (Census 2011) | % of households | 396 (396) | 12 | 2010-04-01 to 2010-09-30 | Share of households with a latrine within the premises (within_premises, then by type of latrine) or without one (none_within_premises = public_latrine + open), by dims.item. |
| `census.hh_lighting_pct` | Households by main source of lighting (Census 2011) | % of households | 198 (198) | 12 | 2010-04-01 to 2010-09-30 | Share of households by main source of lighting (dims.item), e.g. electricity. |
| `census.hh_married_couples_pct` | Households by number of married couples (Census 2011) | % of households | 198 (198) | 12 | 2010-04-01 to 2010-09-30 | Share of households by number of married couples living in them (dims.item: 0-4, 5_plus). |
| `census.hh_ownership_pct` | Households by ownership of the house (Census 2011) | % of households | 99 (99) | 12 | 2010-04-01 to 2010-09-30 | Share of households living in an owned / rented / other house (dims.item). |
| `census.hh_roof_pct` | Households by roof material (Census 2011) | % of households | 297 (297) | 12 | 2010-04-01 to 2010-09-30 | Share of households by predominant material of the roof (dims.item). |
| `census.hh_rooms_pct` | Households by number of dwelling rooms (Census 2011) | % of households | 231 (231) | 12 | 2010-04-01 to 2010-09-30 | Share of households by number of dwelling rooms (dims.item: none = no exclusive room, 1-5, 6_plus). |
| `census.hh_size_pct` | Households by household size (Census 2011) | % of households | 231 (231) | 12 | 2010-04-01 to 2010-09-30 | Share of households by number of members (dims.item: 1-5, 6_8, 9_plus). |
| `census.hh_structure_pct` | Households by type of structure of the house (Census 2011) | % of households | 198 (198) | 12 | 2010-04-01 to 2010-09-30 | Share of households by type of structure of the census house: permanent, semi_permanent, temporary (= temporary_serviceable + temporary_non_serviceable) and unclassifiable (dims.item). |
| `census.hh_wall_pct` | Households by wall material (Census 2011) | % of households | 330 (330) | 12 | 2010-04-01 to 2010-09-30 | Share of households by predominant material of the walls (dims.item). |
| `census.hh_water_location_pct` | Households by location of drinking water (Census 2011) | % of households | 99 (99) | 12 | 2010-04-01 to 2010-09-30 | Share of households whose main drinking-water source is within the premises, near the premises or away (dims.item). |
| `census.hh_water_source_pct` | Households by main source of drinking water (Census 2011) | % of households | 330 (330) | 12 | 2010-04-01 to 2010-09-30 | Share of households by main source of drinking water (dims.item), e.g. tap_treated = tap water from a treated source. |
| `census.households` | Households (Census 2011) | households | 6 (6) | 2 | 2011-03-01 to 2011-03-01 | Number of households in the Census 2011 PCA, by dims.residence. |
| `census.illiterates` | Illiterates (Census 2011) | persons | 18 (18) | 2 | 2011-03-01 to 2011-03-01 | Persons who are not literate, including all children aged 0-6 (population = literates + illiterates), by dims.residence and dims.sex. |
| `census.literates` | Literates (Census 2011) | persons | 18 (18) | 2 | 2011-03-01 to 2011-03-01 | Persons aged 7 and above who can read and write with understanding in any language, by dims.residence and dims.sex. Literacy rate = literates / (population - population 0-6) x 100. |
| `census.main_workers` | Main workers (Census 2011) | persons | 90 (90) | 2 | 2011-03-01 to 2011-03-01 | Workers who worked for 6 months or more in the reference year, by dims.residence, dims.sex and dims.category (all / cultivators / agricultural_labourers / household_industry / other). |
| `census.marginal_workers` | Marginal workers (Census 2011) | persons | 270 (270) | 2 | 2011-03-01 to 2011-03-01 | Workers who worked for less than 6 months in the reference year, by dims.residence, dims.sex, dims.category (as for main workers) and dims.months_worked (under_6 = all marginal workers; 3_to_6; under_3). |
| `census.non_workers` | Non-workers (Census 2011) | persons | 18 (18) | 2 | 2011-03-01 to 2011-03-01 | Persons who did no work at all in the reference year, by dims.residence and dims.sex. |
| `census.population` | Population (Census 2011) | persons | 18 (18) | 2 | 2011-03-01 to 2011-03-01 | Total population enumerated in Census 2011 (reference date 1 March 2011), by dims.residence and dims.sex (persons / male / female). Sex ratio = female / male x 1000. |
| `census.population_0_6` | Population aged 0-6 (Census 2011) | persons | 18 (18) | 2 | 2011-03-01 to 2011-03-01 | Children aged 0-6 years, by dims.residence and dims.sex. Child sex ratio = female / male x 1000. |
| `census.population_sc` | Scheduled Caste population (Census 2011) | persons | 18 (18) | 2 | 2011-03-01 to 2011-03-01 | Population belonging to Scheduled Castes, by dims.residence and dims.sex. |
| `census.population_st` | Scheduled Tribe population (Census 2011) | persons | 18 (18) | 2 | 2011-03-01 to 2011-03-01 | Population belonging to Scheduled Tribes, by dims.residence and dims.sex. |
| `census.workers` | Workers, main and marginal (Census 2011) | persons | 18 (18) | 2 | 2011-03-01 to 2011-03-01 | Persons who did any economically productive work in the year before enumeration (main + marginal workers), by dims.residence and dims.sex. |

## smc_vital_stats

**SMC vital statistics: births, deaths and mortality rates; monthly births by sex**

- **Publisher:** Surat Municipal Corporation, Health Department (Birth and Death Registration)
- **Page:** https://www.suratmunicipal.gov.in/Departments/BirthDeathRegistration
- **Module:** population; **cadence:** annual (checked every 168 h)
- **Geography:** SMC city (the corporation area as published; the page prints 326.555 sq km even after the 2020 extension of the city limits)
- **Licence:** Surat Municipal Corporation web pages; public information (no open-data licence stated)
- **Enabled:** yes; **last success:** 2026-10-24T22:01:47+05:30
- **Holds:** 1413 observations
- **Notes:** Annual table 2001-2021 ("Vital Statistics at a Glance"; page last edited March 2025). Monthly births by sex from the Birth Details API, 1991 to October 2022 (Nov-Dec 2022 not reported). Maternal mortality is printed per 1,000 live births up to 2017 and per 100,000 from 2018: two metrics. Some printed rates differ from the printed counts (IMR 2001-2004, CDR 2021); stored as printed. Sex ratio at birth is not published: compute female / male x 1000 from vital.births_by_month.

<details><summary>How it is collected and parsed</summary>

```text
SMC vital statistics: annual births, deaths and mortality rates (2001-2021), and monthly births by sex.

Publisher: Surat Municipal Corporation (SMC), Health Department, Birth and Death Registration. Registering births
and deaths inside SMC limits is the corporation's statutory duty. It is done at the zone offices and civic centres.

Documents (all on https://www.suratmunicipal.gov.in, no login, no robots.txt; checked 2026-10-24):
  1. GET /Departments/BirthDeathRegistration ("Birth and Death Registration")
     The page explains the registration rules, then shows "Vital Statistics at a Glance": five HTML tables, each
     with a header row "Details/Year | <year> ..." and one row per item.
       2018-2021, 2013-2017, 2009-2012, 2005-2008, 2001-2004 (this last table is captioned "2005 - 2008" by
       mistake, so years are always read from the header row, never from the caption)
     Rows: Mid year estimated population (2009 onwards) | Area of the City (Sq. kms.) | Registered Births |
       Registered Deaths | Registered Infant Deaths | Registered Maternal Deaths | Registered Still Births |
       Crude Birth Rate | Crude Death Rate | Infant Mortality Rate | Maternal Mortality Rate | Still Birth Ratio |
       Population Density Per Sq.km. (2001-2017 only)
     Numbers are plain or Indian-grouped ("55,907").
  2. GET /Departments/BirthDetails ("Birth Details")
     A form with a year drop-down, <select id="BirthMonth" name="Year">. It held 137 years on 2026-10-24: every
     year from 2022 back to 1899, then 13 scattered older years down to 1776. Only the year list is read.
     parse() checks it and stores nothing.
  3. POST /Departments/GetBirthDetails, form body Year=<yyyy> (the page's own script makes the same request)
     returns JSON:
       {"data": [{"mnth": "January - 2022", "BirthMonth": 1, "MaleCount": "3111", "FeMaleCount": "2753",
                  "TotalCount": "5864", ...}, ... (12 months),
                 {"mnth": "Grand Total", "BirthMonth": 13, ...}],
        "status": 200, ...}
     Counts are strings. "-" means no data, as for November and December 2022.
     fetch() requests every listed year from FIRST_YEAR (1991) on. The newest RECENT (2) years are requested on
     every run, because late registrations can still be added. Older years are downloaded once
     (skip_if_seen) and re-parsed from the archive when the parser changes.

What is stored (geo smc_city/smc, the SMC area as published):
- From the annual tables, one value per item and calendar year (period YYYY-01-01..YYYY-12-31):
    vital.mid_year_population    mid-year (1 July) estimated population of the city (2009-2021)
    vital.city_area_km2          "Area of the City" in sq km as printed for that year
    vital.population_density     persons per sq km as printed (2001-2017)
    vital.registered_births      live births registered in the year
    vital.registered_deaths      deaths registered in the year
    vital.infant_deaths          registered deaths of infants (under 1 year)
    vital.maternal_deaths        registered maternal deaths
    vital.still_births           registered still births
    vital.crude_birth_rate       births per 1,000 mid-year population
    vital.crude_death_rate       deaths per 1,000 mid-year population
    vital.infant_mortality_rate  infant deaths per 1,000 live births
    vital.maternal_mortality_per_1000  maternal deaths per 1,000 live births (as printed for 2001-2017)
    vital.maternal_mortality_per_100k  maternal deaths per 100,000 live births (as printed for 2018-2021)
    vital.still_birth_ratio      still births per 1,000 live births
  The page uses the label "Maternal Mortality Rate" for both units (0.46 in 2017, 24.91 in 2018). The two units
  are stored as separate metrics, so a series never mixes them. A value below 5 can only be per 1,000 live
  births: 5 per 1,000 would be 500 per 100,000, far above anything recorded for Surat. validate() checks that
  each value agrees with maternal deaths / births in the unit chosen.
- From the births API, one value per calendar month (month_period) and sex:
    vital.births_by_month        births in SMC's birth register for that month, dims.sex male / female / total.
                                 "total" is the published TotalCount. In some older months it is a little
                                 more than male + female (1995: 7 births; 1980: 86), presumably entries with
                                 no sex recorded. The page does not say whether the month is the month of
                                 birth or of registration. The year list reaching back to 1776 points to month
                                 of birth, so late registrations are filed under their birth year.
  The "Grand Total" entry is not stored: it is the sum of the months, and for 2022 it covers January-October
  only. parse() checks that the male and female months add up to it. For older years the TotalCount of the
  Grand Total is male + female, not the sum of the monthly totals.
  The sex ratio at birth is not published and is not stored. Compute it as female / male x 1000 from the
  monthly counts (2021: 31,516 / 36,999 -> 852).

Cadence: the tables are updated irregularly, about once a year. The footer said "Last Updated: March 17, 2025"
and the latest year was 2021. The births API stops at October 2022: November and December 2022 are "-", and
2022 is the newest year in the list. Both look frozen, so the page is checked weekly. The footer date is not
used as a data date (it is the CMS edit stamp; see the adapter README).

Quirks, all stored as published:
- Area of the City: 112.28 sq km for 2001-2006 (before the 2006 extension of the city limits), 326.515 for 2007,
  2011 and 2012, and 326.555 for the other years. It stays 326.555 for 2020 and 2021, although the city limits
  were extended again in 2020, so the rates for those years use the old area figure.
- The mid-year population falls from 4,786,002 (2010) to 4,462,002 (2011). The 2011 figure is close to the
  Census 2011 count for the SMC (4,467,797); the other years are estimates.
- Some printed rates do not follow from the printed counts:
    IMR for 2003 and 2004 repeats 2002's 19.65 (the counts give 19.31 and 19.60);
    IMR 2001 is 20.97 (the counts give 21.18);
    the crude death rate for 2021 is 6.07 (36,690 / 6,936,534 gives 5.29);
    the 2011 density is 13,555 (4,462,002 / 326.515 gives 13,666).
  validate() therefore checks only plausible ranges for these rates, not the arithmetic.
- The monthly births API and the annual table count differently: for 2021 both give 68,515; for 2011 the API
  gives 68,383 and the table 68,559.
- The page also states the registration fees. Registration within 21 days is free. A late fee of Rs 2 applies up
  to 30 days, and Rs 5 (with an affidavit) up to a year. Extra certificate copies cost Rs 20. These are not
  stored.

Licence: Surat Municipal Corporation web pages; public information. No open-data licence is stated.
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `vital.births_by_month` | Births by month and sex (SMC birth register) | births | 1152 (1146) | 1 | 1991-01-01 to 2022-12-31 | Births in the SMC birth register for the month (most likely the month of birth), by dims.sex: male, female, total (the published total, which can slightly exceed male + female). Sex ratio at birth = female / male x 1000. |
| `vital.city_area_km2` | City area used for vital statistics (SMC) | sq km | 21 (21) | 1 | 2001-01-01 to 2021-12-31 | Area of the city as printed in the vital statistics table for that year. |
| `vital.crude_birth_rate` | Crude birth rate (SMC) | per 1,000 population | 21 (21) | 1 | 2001-01-01 to 2021-12-31 | Registered live births per 1,000 mid-year population, as printed. |
| `vital.crude_death_rate` | Crude death rate (SMC) | per 1,000 population | 21 (21) | 1 | 2001-01-01 to 2021-12-31 | Registered deaths per 1,000 mid-year population, as printed (2021 is printed as 6.07, which does not follow from the printed deaths and population). |
| `vital.infant_deaths` | Registered infant deaths (SMC) | deaths | 21 (21) | 1 | 2001-01-01 to 2021-12-31 | Registered deaths of infants under one year of age in the calendar year. |
| `vital.infant_mortality_rate` | Infant mortality rate (SMC) | per 1,000 live births | 21 (21) | 1 | 2001-01-01 to 2021-12-31 | Registered infant deaths per 1,000 registered live births, as printed. |
| `vital.maternal_deaths` | Registered maternal deaths (SMC) | deaths | 21 (21) | 1 | 2001-01-01 to 2021-12-31 | Registered maternal deaths in the calendar year. |
| `vital.maternal_mortality_per_1000` | Maternal mortality rate per 1,000 live births (SMC) | per 1,000 live births | 17 (17) | 1 | 2001-01-01 to 2017-12-31 | Maternal deaths per 1,000 registered live births, as printed for 2001-2017 under the label "Maternal Mortality Rate". Multiply by 100 to compare with the per-100,000 series. |
| `vital.maternal_mortality_per_100k` | Maternal mortality rate per 100,000 live births (SMC) | per 100,000 live births | 4 (4) | 1 | 2018-01-01 to 2021-12-31 | Maternal deaths per 100,000 registered live births, as printed from 2018 under the label "Maternal Mortality Rate". |
| `vital.mid_year_population` | Mid-year estimated population (SMC) | persons | 13 (13) | 1 | 2009-01-01 to 2021-12-31 | Mid-year (1 July) estimated population of the SMC area used by SMC for its vital rates, filed under the calendar year. Published for 2009 onwards. |
| `vital.population_density` | Population density (SMC vital statistics) | persons per sq km | 17 (17) | 1 | 2001-01-01 to 2017-12-31 | Population density as printed in the vital statistics table (2001-2017). |
| `vital.registered_births` | Registered births (SMC) | births | 21 (21) | 1 | 2001-01-01 to 2021-12-31 | Live births registered with SMC in the calendar year. |
| `vital.registered_deaths` | Registered deaths (SMC) | deaths | 21 (21) | 1 | 2001-01-01 to 2021-12-31 | Deaths registered with SMC in the calendar year. |
| `vital.still_birth_ratio` | Still birth ratio (SMC) | per 1,000 live births | 21 (21) | 1 | 2001-01-01 to 2021-12-31 | Registered still births per 1,000 registered live births, as printed. |
| `vital.still_births` | Registered still births (SMC) | still births | 21 (21) | 1 | 2001-01-01 to 2021-12-31 | Still births registered in the calendar year. |

## smc_streetlights

**SMC non-working streetlights (monthly average, %)**

- **Publisher:** Surat Municipal Corporation, Street Light Department
- **Page:** https://www.suratmunicipal.gov.in/Departments/NonWorkingStreetlights
- **Module:** power; **cadence:** monthly (checked every 168 h)
- **Geography:** SMC city (whole corporation area)
- **Licence:** Surat Municipal Corporation web page; public information
- **Enabled:** yes; **last success:** 2026-10-24T22:44:22+05:30
- **Holds:** 48 observations
- **Notes:** Historical only: the series runs from March 2017 to February 2021 and the page was last edited in July 2022. The averaging method and the total number of streetlights are not published. These are not electricity outage data (DGVCL and Torrent Power supply Surat).

<details><summary>How it is collected and parsed</summary>

```text
SMC Street Light Department: monthly average percentage of non-working streetlights (March 2017 - February 2021).

Publisher: Surat Municipal Corporation, Street Light Department (Engineering). The page sits under
Departments > Street Light > "Non-working Streetlights" on the SMC website.

Endpoint: one plain GET, no parameters, no login or captcha (robots.txt on www.suratmunicipal.gov.in returns
404, so nothing is disallowed):

    https://www.suratmunicipal.gov.in/Departments/NonWorkingStreetlights

Response layout (server-rendered HTML; browser title "Non-working Street Lights (In Percentage)"). The series is
split over two side-by-side tables, both with the hidden caption "Percentages of Non-working Streetlights":

    Sr. No. | Month           | Avg. Non-working Streetlights
    1       | February/2021   | 0.38%
    ...                                    (table 1: rows 1-25, February 2021 back to February 2019)
    26      | January/2019    | 0.34%
    ...                                    (table 2: rows 26-48, January 2019 back to March 2017)

-> streetlight.nonworking_pct: one observation per month, smc_city, period = that calendar month
   (parse.month_period). The value is the published "Avg. Non-working Streetlights" percentage (0.38 means 0.38 %).
   SMC does not say how the average is taken (for example a mean of daily CCMS readings) or what the
   denominator is (the total number of streetlights is not on this page), so the figure is stored exactly as
   published. A blank, "-" or "NA" cell would become status='not_reported' with no value.

Snapshot 2026-10-24: 48 months, from March 2017 (0.76 %) to February 2021 (0.38 %). The highest is 1.15 % in
June 2017. The footer "Last Updated: July 21, 2022 04:27 PM" is the CMS edit time of the page, not a data date,
so it is not used.

Quirks and caveats:
- The series STOPPED at February 2021. The page is historical only. It is still checked weekly, so that a
  restart is noticed. validate() does not fail just because the data are old.
- The month cell uses "Month/Year" ("February/2021"). The slash is turned into a space before parse.month_year().
- These figures describe SMC-maintained street lighting only. They are not power-supply outage data: DGVCL and
  Torrent Power supply electricity in Surat, and their outage notices are a separate source.
- The sibling pages "Streetlight Luminaires Details", "Important Details" and "Energy Conservation and CCMS" are
  not fetched.

Geography: SMC city (smc_city:smc). Cadence: monthly series, no longer updated. Units: percent of streetlights.
Licence: Surat Municipal Corporation web page; public information. No explicit open licence.
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `streetlight.nonworking_pct` | Non-working streetlights (monthly average) | % | 48 (48) | 1 | 2017-03-01 to 2021-02-28 | Average percentage of SMC streetlights not working during the month, as published by the SMC Street Light Department ("Avg. Non-working Streetlights"). The averaging method and the base (total streetlights) are not stated. |

## smc_rti

**SMC Right to Information returns (annual returns, quarterly Patrak-7 and Patrak-8)**

- **Publisher:** Surat Municipal Corporation, RTI Cell
- **Page:** https://www.suratmunicipal.gov.in/Downloads/Acts/RTI_Act
- **Module:** rti; **cadence:** quarterly (checked every 168 h)
- **Geography:** SMC city: the figures describe Surat Municipal Corporation as one public authority under the RTI Act.
- **Licence:** Surat Municipal Corporation website; public information published under RTI Act s.4.
- **Enabled:** yes; **last success:** 2026-10-18T11:04:07+05:30
- **Holds:** 644 observations; records: rti_annual_return (20)
- **Notes:** Annual returns (rti.annual.*) are copies of the Gujarat RTI Annual Return form; past years are downloaded once (skip_if_seen) and 5 image-only years (SCANNED_RETURNS) are skipped. Patrak-7/8 (rti.quarterly.*) use a legacy Gujarati font: rows are mapped by serial number against documented row lists. Annual and quarterly series are compiled separately and do not reconcile: never mix them.

<details><summary>How it is collected and parsed</summary>

```text
SMC Right to Information statistics: Gujarat RTI annual returns and the Patrak-7 / Patrak-8 quarterly returns.

Surat Municipal Corporation, as one public authority under the RTI Act 2005, publishes three kinds of return.
Every figure describes SMC as a whole, so everything is filed under geo smc_city/smc.

1. ANNUAL RETURNS, one PDF per year, listed on https://www.suratmunicipal.gov.in/Downloads/Acts/RTI_ActAnnualReturn
   ("Gujarat State RTI Annual Return - Year 2025 to 2026", 20 links back to 2005-07). Each is a one-page copy of
   the state's "Annual Return Form" (rti-ar.gujarat.gov.in), in English, always with the same fields:
       Public Authority : Surat Municipal Corporation      Year: 2025-2026
       row "Requests":      Opening Balance as on April 1st | Received during the Period (including cases
                            transferred to other Public Authority) | No. of cases transferred |
                            Decisions where requests/appeals rejected | Decisions where requests/appeals
                            accepted (*including partially rejected cases)
       row "First Appeals": the same columns without "transferred"
       No. of Cases where disciplinary action taken against any Officer
       No. of APIOs / PIOs / AAs designated
       No. of times various provisions were invoked while rejecting requests:
                            Section 8(1)(a)..(j), Sections 9, 11, 24, Other
       Amount of Charges Collected (in Rs.): Registration Fee Amount | Additional Fee & Any other charges |
                            Penalties Amount: Levied | Collected | Total
   The files come in four physical layouts: Chrome/Firefox/Foxit printouts of the web form (2019-20 onward) and
   Word re-typings of it (2005-07 .. 2014-15). Five years (2015-16, 2016-17, 2017-18, 2018-19, 2021-22) are
   image-only scans with no text layer; they cannot be read without OCR, so they are not downloaded
   (SCANNED_RETURNS) and those years have no rti.annual.* data.
   The parser works on word coordinates (pdftotext -bbox): a number belongs to the field whose header word is
   nearest, so a blank field becomes 'not_reported' instead of shifting its neighbours. Because every field of
   this form is always filled in (0 when nothing happened), more than two blank fields is treated as a layout
   the parser does not understand and the document is rejected rather than stored half-empty.
   -> rti.annual.* observations, period = the return's year (1 April .. 31 March; 2005-07 spans two years).
   The index page itself -> one 'rti_annual_return' record per linked PDF (title, url, years).

2. PATRAK-7 ("પત્રક-7"), the quarterly return of RTI applications received/disposed of by the PIOs, and
3. PATRAK-8 ("પત્રક-8"), the same for first appeals received/disposed of by the appellate authorities:
   https://www.suratmunicipal.gov.in/Content/Documents/rtiact/other/patrak-7.pdf and .../patrak-8.pdf, linked
   from https://www.suratmunicipal.gov.in/Information/RTI/RTI_ReportsCirculars. Both are overwritten in place
   every quarter; the raw archive keeps every version and each version lands on its own quarter period.
   They are Excel printouts whose Gujarati text uses a legacy (non-Unicode) font, so pdftotext returns ASCII
   gibberish for the labels (e.g. "l+DF;GL X~VFTDF\ VUFpGL 50TZ VZHLVM" = ત્રિમાસની શરૂઆતમાં અગાઉની પડતર અરજીઓ).
   The numbers are ordinary digits. Rows are identified by their serial-number cell (also legacy font:
   "!"=1 "Z"=2 "#"=3 "$"=4 "5"=5 "&"=6 "*"=7 "("=8 ")"=9 "_"=0, ")sVf"=9(અ)), and the full sequence of serial
   numbers must equal the documented row lists P7_ROWS / P8_ROWS below, which say what each row means.
   Value columns: BPL applicants | other applicants | total (dims.applicants = bpl | non_bpl | all), located
   from the header row and the rows that have all three values. The quarter is read from the printed range
   "તા. 01/01/26 થી તા. 31/03/26" (legacy: "TFP _!q_!qZ& YL TFP #!q_#qZ&"), must be an exact financial-year
   quarter, and is cross-checked with the printed financial year ("નાણાંકીય વર્ષ : 2025 - 26").
   -> rti.quarterly.* observations, period = the quarter (Patrak-7 rows 13d and 14 cover the part of the
   financial year they describe).
   Layout differences handled (both checked against the live files, 2026-10-05, Q4 FY2025-26): Patrak-7 values
   are right-aligned and BPL cells are often left blank (-> not_reported); Patrak-8 values are centred, every
   cell is filled (0 printed), row 7(a)'s label wraps so its values sit one line below its serial number, and
   the row-9 heading runs on across the value columns. Any other text that starts inside the value columns
   ("1,234/-", "12 (a)") raises instead of being dropped as a blank.

publisher_as_of is the PDF's creation date (for the browser printouts it equals the printed date).

Validation (validate()): counts are whole numbers <= 200,000 and rupee amounts <= 1 crore; no period starts
before the RTI Act (2005) or after the fetch date. Annual: at most two blank fields, and transferred + rejected
+ accepted <= opening balance + received for requests and for first appeals. Quarterly (total column): the
form's own identities (row 1 + 2 = 3; 4 + 6 + 7 + 8 = 9 for Patrak-7, 4 + 5 + 6 = 7 for Patrak-8; 3 - disposed =
pending at end; disposed within time <= disposed; sections sum to their printed total), and BPL + other = total
on every count row where all three are printed. These identities are what proves that the position-mapped
rows (labels unreadable) landed on the right metrics.

The annual return and the quarterly returns are separate metric families on purpose: they are compiled
separately and do not reconcile (FY2025-26 annual return: 5,875 requests pending on 1 April 2025 and Rs 2,62,471
fees+charges for the year; Patrak-7 Q4 FY2025-26: Rs 4,29,678 "income in the year to date"). Never sum or splice
rti.annual.* with rti.quarterly.*.
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `rti.annual.aas_designated` | Appellate Authorities designated | officers | 15 (15) | 1 | 2005-04-01 to 2026-03-31 | Annual return (Gujarat State RTI Annual Return form), SMC as a whole. Number of first Appellate Authorities (AAs) designated, as filed for the year. |
| `rti.annual.additional_fees_rs` | RTI additional fees and other charges collected | Rs | 15 (15) | 1 | 2005-04-01 to 2026-03-31 | Annual return (Gujarat State RTI Annual Return form), SMC as a whole. "Additional Fee & Any other charges" (copying charges etc.) collected during the year, in rupees. |
| `rti.annual.apios_designated` | Assistant PIOs designated | officers | 15 (15) | 1 | 2005-04-01 to 2026-03-31 | Annual return (Gujarat State RTI Annual Return form), SMC as a whole. Number of Assistant Public Information Officers (APIOs) designated, as filed for the year. |
| `rti.annual.disciplinary_actions` | Disciplinary actions against officers under RTI | cases | 15 (15) | 1 | 2005-04-01 to 2026-03-31 | Annual return (Gujarat State RTI Annual Return form), SMC as a whole. Cases during the year where disciplinary action was taken against any officer. |
| `rti.annual.first_appeals_accepted` | RTI first appeals accepted | appeals | 15 (15) | 1 | 2005-04-01 to 2026-03-31 | Annual return (Gujarat State RTI Annual Return form), SMC as a whole. Decisions during the year where first appeals were accepted, including partially rejected cases. |
| `rti.annual.first_appeals_opening_balance` | RTI first appeals pending at start of year | appeals | 15 (15) | 1 | 2005-04-01 to 2026-03-31 | Annual return (Gujarat State RTI Annual Return form), SMC as a whole. First appeals (to SMC's own appellate authorities) pending at the start of the year. |
| `rti.annual.first_appeals_received` | RTI first appeals received | appeals | 15 (15) | 1 | 2005-04-01 to 2026-03-31 | Annual return (Gujarat State RTI Annual Return form), SMC as a whole. First appeals received during the year. |
| `rti.annual.first_appeals_rejected` | RTI first appeals rejected | appeals | 15 (15) | 1 | 2005-04-01 to 2026-03-31 | Annual return (Gujarat State RTI Annual Return form), SMC as a whole. Decisions during the year where first appeals were rejected. |
| `rti.annual.penalties_collected_rs` | RTI penalties collected | Rs | 15 (15) | 1 | 2005-04-01 to 2026-03-31 | Annual return (Gujarat State RTI Annual Return form), SMC as a whole. Penalties amount "Collected" during the year, in rupees. |
| `rti.annual.penalties_levied_rs` | RTI penalties levied | Rs | 15 (15) | 1 | 2005-04-01 to 2026-03-31 | Annual return (Gujarat State RTI Annual Return form), SMC as a whole. Penalties amount "Levied" during the year, in rupees. |
| `rti.annual.penalties_total_rs` | RTI penalties total (as printed) | Rs | 15 (15) | 1 | 2005-04-01 to 2026-03-31 | Annual return (Gujarat State RTI Annual Return form), SMC as a whole. The penalties "Total" field printed after Levied and Collected, in rupees, stored as printed (the form does not say how it is computed). |
| `rti.annual.pios_designated` | Public Information Officers designated | officers | 15 (15) | 1 | 2005-04-01 to 2026-03-31 | Annual return (Gujarat State RTI Annual Return form), SMC as a whole. Number of Public Information Officers (PIOs) designated, as filed for the year. |
| `rti.annual.registration_fees_rs` | RTI registration (application) fees collected | Rs | 15 (15) | 1 | 2005-04-01 to 2026-03-31 | Annual return (Gujarat State RTI Annual Return form), SMC as a whole. "Registration Fee Amount" collected during the year, in rupees. |
| `rti.annual.rejections_by_section` | RTI exemptions invoked when rejecting requests | times | 210 (210) | 1 | 2005-04-01 to 2026-03-31 | Annual return (Gujarat State RTI Annual Return form), SMC as a whole. Number of times each provision of the RTI Act was invoked while rejecting requests during the year (dims.section: 8(1)(a)..8(1)(j), 9, 11, 24, other). One rejection can invoke several, so the sum can exceed rti.annual.requests_rejected. |
| `rti.annual.requests_accepted` | RTI requests accepted | requests | 15 (15) | 1 | 2005-04-01 to 2026-03-31 | Annual return (Gujarat State RTI Annual Return form), SMC as a whole. Decisions during the year where requests were accepted, including partially rejected cases. |
| `rti.annual.requests_opening_balance` | RTI requests pending at start of year | requests | 15 (15) | 1 | 2005-04-01 to 2026-03-31 | Annual return (Gujarat State RTI Annual Return form), SMC as a whole. Requests pending at the start of the year ("Opening Balance as on April 1st"). |
| `rti.annual.requests_received` | RTI requests received | requests | 15 (15) | 1 | 2005-04-01 to 2026-03-31 | Annual return (Gujarat State RTI Annual Return form), SMC as a whole. Requests received during the year, including cases then transferred to another public authority ("Received during the Period (including cases transferred to other Public Authority)"). |
| `rti.annual.requests_rejected` | RTI requests rejected | requests | 15 (15) | 1 | 2005-04-01 to 2026-03-31 | Annual return (Gujarat State RTI Annual Return form), SMC as a whole. Decisions during the year where requests were rejected. |
| `rti.annual.requests_transferred` | RTI requests transferred to other authorities | requests | 15 (15) | 1 | 2005-04-01 to 2026-03-31 | Annual return (Gujarat State RTI Annual Return form), SMC as a whole. Requests transferred to another public authority during the year ("No. of cases transferred"). |
| `rti.quarterly.appellate_authorities` | Appellate authorities (Patrak-8 header) | officers | 1 (1) | 1 | 2026-04-01 to 2026-06-30 | Patrak-8 quarterly return (first appeals to appellate authorities), SMC as a whole. Total number of appellate officers printed in the return header for the quarter. |
| `rti.quarterly.application_fees_rs` | RTI application fees received in quarter | Rs | 3 (2) | 1 | 2026-04-01 to 2026-06-30 | Patrak-7 quarterly return (applications to PIOs), SMC as a whole. Row 13(a): application fees received during the quarter (cash or other forms), excluding applications received on transfer from other authorities, in rupees. Split by applicant category in dims.applicants: bpl (Below Poverty Line applicants), non_bpl (the "other" column) and all (the printed total column). |
| `rti.quarterly.first_appeal_refusals_by_section` | RTI exemptions upheld in first appeals (quarter) | times | 42 (42) | 1 | 2026-04-01 to 2026-06-30 | Patrak-8 quarterly return (first appeals to appellate authorities), SMC as a whole. Rows 9(a)-(n): number of the appeals in rows 5 and 6 where the information asked for was refused, by section of the Act (dims.section: 8(1)(a)..8(1)(j), 9, 11, 24, other). The printed label of row (h) repeats clause (g) (a typo on the form); it is stored by position as 8(1)(h). Split by applicant category in dims.applicants: bpl (Below Poverty Line applicants), non_bpl (the "other" column) and all (the printed total column). |
| `rti.quarterly.first_appeal_refusals_total` | RTI exemptions upheld in first appeals, total | times | 3 (3) | 1 | 2026-04-01 to 2026-06-30 | Patrak-8 quarterly return (first appeals to appellate authorities), SMC as a whole. Row 10: total of rows 9(a) to 9(n). Split by applicant category in dims.applicants: bpl (Below Poverty Line applicants), non_bpl (the "other" column) and all (the printed total column). |
| `rti.quarterly.first_appeals_allowed` | RTI first appeals allowed in full | appeals | 3 (3) | 1 | 2026-04-01 to 2026-06-30 | Patrak-8 quarterly return (first appeals to appellate authorities), SMC as a whole. Row 4: appeals fully allowed (અપીલ સંપૂર્ણ મંજૂર). Split by applicant category in dims.applicants: bpl (Below Poverty Line applicants), non_bpl (the "other" column) and all (the printed total column). |
| `rti.quarterly.first_appeals_disposed` | RTI first appeals disposed of in quarter | appeals | 3 (3) | 1 | 2026-04-01 to 2026-06-30 | Patrak-8 quarterly return (first appeals to appellate authorities), SMC as a whole. Row 7: total appeals disposed of during the quarter (rows 4 + 5 + 6). Split by applicant category in dims.applicants: bpl (Below Poverty Line applicants), non_bpl (the "other" column) and all (the printed total column). |
| `rti.quarterly.first_appeals_disposed_within_time` | RTI first appeals disposed of within time limit | appeals | 3 (3) | 1 | 2026-04-01 to 2026-06-30 | Patrak-8 quarterly return (first appeals to appellate authorities), SMC as a whole. Row 7(a): of the appeals disposed of (row 7), those disposed of within the time limit of section 19(6). Split by applicant category in dims.applicants: bpl (Below Poverty Line applicants), non_bpl (the "other" column) and all (the printed total column). |
| `rti.quarterly.first_appeals_partly_allowed` | RTI first appeals partly allowed | appeals | 3 (3) | 1 | 2026-04-01 to 2026-06-30 | Patrak-8 quarterly return (first appeals to appellate authorities), SMC as a whole. Row 5: appeals partly allowed and partly rejected. Split by applicant category in dims.applicants: bpl (Below Poverty Line applicants), non_bpl (the "other" column) and all (the printed total column). |
| `rti.quarterly.first_appeals_pending_end` | RTI first appeals pending at end of quarter | appeals | 3 (3) | 1 | 2026-04-01 to 2026-06-30 | Patrak-8 quarterly return (first appeals to appellate authorities), SMC as a whole. Row 8: appeals pending at the end of the quarter (row 3 - row 7). Split by applicant category in dims.applicants: bpl (Below Poverty Line applicants), non_bpl (the "other" column) and all (the printed total column). |
| `rti.quarterly.first_appeals_pending_start` | RTI first appeals pending at start of quarter | appeals | 3 (3) | 1 | 2026-04-01 to 2026-06-30 | Patrak-8 quarterly return (first appeals to appellate authorities), SMC as a whole. Row 1: first appeals pending from earlier, at the start of the quarter. Split by applicant category in dims.applicants: bpl (Below Poverty Line applicants), non_bpl (the "other" column) and all (the printed total column). |
| `rti.quarterly.first_appeals_received` | RTI first appeals received in quarter | appeals | 3 (3) | 1 | 2026-04-01 to 2026-06-30 | Patrak-8 quarterly return (first appeals to appellate authorities), SMC as a whole. Row 2: first appeals received during the quarter. Split by applicant category in dims.applicants: bpl (Below Poverty Line applicants), non_bpl (the "other" column) and all (the printed total column). |
| `rti.quarterly.first_appeals_rejected` | RTI first appeals rejected in full | appeals | 3 (3) | 1 | 2026-04-01 to 2026-06-30 | Patrak-8 quarterly return (first appeals to appellate authorities), SMC as a whole. Row 6: appeals fully rejected (અપીલ સંપૂર્ણ નામંજૂર). Split by applicant category in dims.applicants: bpl (Below Poverty Line applicants), non_bpl (the "other" column) and all (the printed total column). |
| `rti.quarterly.first_appeals_total` | RTI first appeals on hand in quarter | appeals | 3 (3) | 1 | 2026-04-01 to 2026-06-30 | Patrak-8 quarterly return (first appeals to appellate authorities), SMC as a whole. Row 3: total appeals (row 1 + row 2). Split by applicant category in dims.applicants: bpl (Below Poverty Line applicants), non_bpl (the "other" column) and all (the printed total column). |
| `rti.quarterly.income_earlier_in_fy_rs` | RTI income earlier in the financial year | Rs | 0 |  |  | Patrak-7 quarterly return (applications to PIOs), SMC as a whole. Row 13(d): total income in the earlier part of the current financial year, in rupees. The observation period is that part (1 April to the day before the quarter); not emitted for Q1. Stored as printed: in Q4 FY2025-26 the non_bpl (193828) and all (363873) columns disagree. Split by applicant category in dims.applicants: bpl (Below Poverty Line applicants), non_bpl (the "other" column) and all (the printed total column). |
| `rti.quarterly.income_fy_to_date_rs` | RTI income in financial year to date | Rs | 3 (3) | 1 | 2026-04-01 to 2026-06-30 | Patrak-7 quarterly return (applications to PIOs), SMC as a whole. Row 14: total income from 1 April to the end of the quarter (13c + 13d), in rupees; the observation period is that span. Split by applicant category in dims.applicants: bpl (Below Poverty Line applicants), non_bpl (the "other" column) and all (the printed total column). |
| `rti.quarterly.income_rs` | RTI fee and charges income in quarter | Rs | 3 (3) | 1 | 2026-04-01 to 2026-06-30 | Patrak-7 quarterly return (applications to PIOs), SMC as a whole. Row 13(c): total income during the quarter (13a + 13b), in rupees. Split by applicant category in dims.applicants: bpl (Below Poverty Line applicants), non_bpl (the "other" column) and all (the printed total column). |
| `rti.quarterly.other_charges_rs` | RTI charges other than application fee (quarter) | Rs | 3 (2) | 1 | 2026-04-01 to 2026-06-30 | Patrak-7 quarterly return (applications to PIOs), SMC as a whole. Row 13(b): charges other than the application fee (copying charges etc.) received during the quarter, in rupees. Split by applicant category in dims.applicants: bpl (Below Poverty Line applicants), non_bpl (the "other" column) and all (the printed total column). |
| `rti.quarterly.pios` | Public Information Officers (Patrak-7 header) | officers | 1 (1) | 1 | 2026-04-01 to 2026-06-30 | Patrak-7 quarterly return (applications to PIOs), SMC as a whole. Total number of Public Information Officers printed in the return header for the quarter. |
| `rti.quarterly.refusals_by_section` | RTI exemptions invoked in refusals (quarter) | times | 42 (28) | 1 | 2026-04-01 to 2026-06-30 | Patrak-7 quarterly return (applications to PIOs), SMC as a whole. Rows 11(a)-(n): number of the refusals in rows 7 and 8 made under each section of the Act (dims.section: 8(1)(a)..8(1)(j), 9, 11, 24, other). Split by applicant category in dims.applicants: bpl (Below Poverty Line applicants), non_bpl (the "other" column) and all (the printed total column). |
| `rti.quarterly.refusals_total` | RTI refusals by section, total (quarter) | times | 3 (3) | 1 | 2026-04-01 to 2026-06-30 | Patrak-7 quarterly return (applications to PIOs), SMC as a whole. Row 12: total of rows 11(a) to 11(n). Split by applicant category in dims.applicants: bpl (Below Poverty Line applicants), non_bpl (the "other" column) and all (the printed total column). |
| `rti.quarterly.requests_disposed` | RTI applications disposed of in quarter | applications | 3 (3) | 1 | 2026-04-01 to 2026-06-30 | Patrak-7 quarterly return (applications to PIOs), SMC as a whole. Row 9: total applications disposed of during the quarter (rows 4 + 6 + 7 + 8). Split by applicant category in dims.applicants: bpl (Below Poverty Line applicants), non_bpl (the "other" column) and all (the printed total column). |
| `rti.quarterly.requests_disposed_within_time` | RTI applications disposed of within time limit | applications | 3 (3) | 1 | 2026-04-01 to 2026-06-30 | Patrak-7 quarterly return (applications to PIOs), SMC as a whole. Row 9(a): of the applications disposed of (row 9), those disposed of within the statutory time limit. Split by applicant category in dims.applicants: bpl (Below Poverty Line applicants), non_bpl (the "other" column) and all (the printed total column). |
| `rti.quarterly.requests_info_supplied` | RTI applications answered in full | applications | 3 (3) | 1 | 2026-04-01 to 2026-06-30 | Patrak-7 quarterly return (applications to PIOs), SMC as a whole. Row 6: applications where the information was supplied in full. Split by applicant category in dims.applicants: bpl (Below Poverty Line applicants), non_bpl (the "other" column) and all (the printed total column). |
| `rti.quarterly.requests_pending_end` | RTI applications pending at end of quarter | applications | 3 (3) | 1 | 2026-04-01 to 2026-06-30 | Patrak-7 quarterly return (applications to PIOs), SMC as a whole. Row 10: applications pending at the end of the quarter (row 3 - row 9). Split by applicant category in dims.applicants: bpl (Below Poverty Line applicants), non_bpl (the "other" column) and all (the printed total column). |
| `rti.quarterly.requests_pending_start` | RTI applications pending at start of quarter | applications | 3 (3) | 1 | 2026-04-01 to 2026-06-30 | Patrak-7 quarterly return (applications to PIOs), SMC as a whole. Row 1: applications pending from earlier, at the start of the quarter. Split by applicant category in dims.applicants: bpl (Below Poverty Line applicants), non_bpl (the "other" column) and all (the printed total column). |
| `rti.quarterly.requests_received` | RTI applications received in quarter | applications | 3 (3) | 1 | 2026-04-01 to 2026-06-30 | Patrak-7 quarterly return (applications to PIOs), SMC as a whole. Row 2: applications received during the quarter. Split by applicant category in dims.applicants: bpl (Below Poverty Line applicants), non_bpl (the "other" column) and all (the printed total column). |
| `rti.quarterly.requests_refused_fully` | RTI applications refused in full | applications | 3 (2) | 1 | 2026-04-01 to 2026-06-30 | Patrak-7 quarterly return (applications to PIOs), SMC as a whole. Row 7: applications where the information was refused in full. Split by applicant category in dims.applicants: bpl (Below Poverty Line applicants), non_bpl (the "other" column) and all (the printed total column). |
| `rti.quarterly.requests_refused_partly` | RTI applications refused in part | applications | 3 (2) | 1 | 2026-04-01 to 2026-06-30 | Patrak-7 quarterly return (applications to PIOs), SMC as a whole. Row 8: applications where the information was partly refused. Split by applicant category in dims.applicants: bpl (Below Poverty Line applicants), non_bpl (the "other" column) and all (the printed total column). |
| `rti.quarterly.requests_total` | RTI applications on hand in quarter | applications | 3 (3) | 1 | 2026-04-01 to 2026-06-30 | Patrak-7 quarterly return (applications to PIOs), SMC as a whole. Row 3: total applications (row 1 + row 2). Split by applicant category in dims.applicants: bpl (Below Poverty Line applicants), non_bpl (the "other" column) and all (the printed total column). |
| `rti.quarterly.requests_transferred_partly` | RTI applications partly transferred | applications | 3 (3) | 1 | 2026-04-01 to 2026-06-30 | Patrak-7 quarterly return (applications to PIOs), SMC as a whole. Row 5: applications partly transferred to another public authority during the quarter (not counted in row 9). Split by applicant category in dims.applicants: bpl (Below Poverty Line applicants), non_bpl (the "other" column) and all (the printed total column). |
| `rti.quarterly.requests_transferred_wholly` | RTI applications wholly transferred | applications | 3 (3) | 1 | 2026-04-01 to 2026-06-30 | Patrak-7 quarterly return (applications to PIOs), SMC as a whole. Row 4: applications wholly transferred to another public authority during the quarter. Split by applicant category in dims.applicants: bpl (Below Poverty Line applicants), non_bpl (the "other" column) and all (the printed total column). |

## smc_ucd_schemes

**SMC Urban Community Development schemes**

- **Publisher:** Surat Municipal Corporation, Urban Community Development Department
- **Page:** https://www.suratmunicipal.gov.in/Departments/UrbanCommunityDevelopmentHome
- **Module:** schemes; **cadence:** static (checked every 168 h)
- **Geography:** SMC city (schemes run by SMC's UCD department)
- **Licence:** Surat Municipal Corporation web page; public information (no explicit open-data licence)
- **Enabled:** yes; **last success:** 2026-10-24T22:42:00+05:30
- **Holds:** 0 observations; records: smc_ucd_scheme (9)
- **Notes:** Gujarati text kept as published (not translated): purpose, eligibility, age, assistance, project amount, subsidy and training fee where the page gives them, plus the unlabelled points. No beneficiary counts are published, so there are no observations.

<details><summary>How it is collected and parsed</summary>

```text
SMC Urban Community Development (UCD) department: the welfare schemes it implements, as text records.

Publisher: Surat Municipal Corporation, Urban Community Development (UCD) Department (Departments > Social Welfare >
Urban Community Development). The page is in Gujarati; it describes the schemes the department runs for the urban
poor: the DAY-NULM components (self-help groups, skills training, self-employment loans, shelters for the urban
homeless, street vendors), PM SVANidhi and the state's Mukhyamantri Mahila Utkarsh Yojana.

Endpoint: one plain GET, no parameters, no login or captcha (robots.txt on www.suratmunicipal.gov.in returns 404,
so nothing is disallowed):

    https://www.suratmunicipal.gov.in/Departments/UrbanCommunityDevelopmentHome

Response layout (server-rendered HTML) inside <div class="contentblock gujartifont">:

    <div class="section-margin"> <p>intro: UCD started in 1967 ...</p> <p>DAY-NULM intro ...</p> </div>
    <div class="section-margin">
      <h2>સામાજિક ગતિશીલતા અને સંસ્થાગત વિકાસ ઘટક (Social Mobilisation And Institution Development – SM&ID)</h2>
      <div class="text-2x text-bold">(અ) સ્વ-સહાય જૂથ (Self Help Group-SHG)</div>              optional sub-scheme
      <ul class="list-group">
        <li class="list-group-item"><div class="text-2x text-bold mar-b10">હેતુ</div> purpose text </li>   labelled
        <li class="list-group-item"> a plain point </li>                                                unlabelled
      </ul> ...
    </div> ...

Records -> one 'smc_ucd_scheme' per scheme: an <h2> section, or each sub-scheme heading inside it ("(અ)", "(બ)",
"(ક)"). The page is the complete list, so schemes that disappear get closed. Key: the English words of the heading
as a slug ('self-help-group-shg', 'pmsvanidhi', 'mmuy'). Attributes (all text exactly as published, in Gujarati;
nothing is translated or summarised):
    title           the heading as printed
    name_en         the English (Latin-script) words of the heading ('Self Help Group-SHG', 'MMUY')
    component       for a sub-scheme, the <h2> title it sits under; otherwise None
    purpose         item labelled હેતુ (purpose)
    eligibility     item labelled લાભાર્થીની પાત્રતા (beneficiary eligibility)
    age_limit       item labelled લાભાર્થીની ઉમર (beneficiary age)
    assistance      item labelled સહાય (assistance)
    project_amount  item labelled પ્રોજેક્ટ રકમ (project amount)
    subsidy         item labelled સબસીડી (subsidy)
    training_fee    item labelled તાલીમ ફી (training fee)
    points          the unlabelled items, in order (list)
Only labels present on the page are set. An unknown label raises an error so a new kind of field is noticed.

Snapshot 2026-10-24 (footer "Last Updated: December 24, 2021"): 9 schemes: Self Help Group (under SM&ID), EST&P,
SEP Individual / Group / SHG Bank Linkage (under SEP), SUH, SUSV, PMSVANidhi, MMUY.

Caveats: editorial text, last edited in 2021, so amounts and rules may be out of date (e.g. PM SVANidhi loan
tranches); there are no beneficiary counts, so no observations are emitted. The two intro paragraphs are not
stored. Geography: SMC city. Cadence: static, checked weekly.
Licence: Surat Municipal Corporation web page; public information; no explicit open-data licence.
```

</details>

## smc_tenders

**SMC active tenders**

- **Publisher:** Surat Municipal Corporation (tenders invited by its zones and departments)
- **Page:** https://www.suratmunicipal.gov.in/Information/Tender/Tenders
- **Module:** tenders; **cadence:** daily (checked every 24 h)
- **Geography:** SMC city; each tender notice names its issuing zone or department
- **Licence:** Surat Municipal Corporation web pages; public information
- **Enabled:** yes; **last success:** 2026-10-24T22:44:20+05:30
- **Holds:** 4 observations; records: tender (70), tender_notice (70)
- **Notes:** Each tender's detail page is fetched once, with the same form POST as the site's "View Tender Details" button (only the hidden ID). Counts are dated to the fetch day because the list has no data date. Bid documents, bidders and awards (smctender.nprocure.com) are not collected. Sums of estimated value are left to the dashboard (from the tender_notice records).

<details><summary>How it is collected and parsed</summary>

```text
SMC active tenders: the live list of tenders invited by SMC zones and departments, with each notice's details.

Publisher: Surat Municipal Corporation. Tenders are invited by its zones and departments. Bids are submitted on
the e-procurement portal https://smctender.nprocure.com/ (run for SMC by (n)Code Solutions), which this source
does NOT read: bid documents, bidders and awards are not collected.

Endpoints (robots.txt on www.suratmunicipal.gov.in returns 404, so nothing is disallowed; no login or captcha):

1. List: GET https://www.suratmunicipal.gov.in/Information/Tender/Tenders  (no parameters), "Active Tenders".
   One <li> per tender:
       <span class="tender-serial">1</span>
       <form action="/Information/Tender/TenderInformation" method="post">
         <input type="hidden" name="hdnCustomerId" value="47260" />
         <p class="tender-description">Supply, Installation ... South Zone-B (Kanakpur) Surat ... work -4</p>
       </form>
       Start Date: 12-10-2026 11:00 | End Date: 26-10-2026 18:00
       Availability: 2 Day(s) | Submit within: 2 Day(s)
   The "View Tender Details" button posts that form. There is no anti-forgery token, only the hidden ID.

2. Detail: POST https://www.suratmunicipal.gov.in/Information/Tender/TenderInformation  with the form body
   hdnCustomerId=<id from the list>, which is exactly what the site's own button sends. The response is a
   <div class="list-group"> of label/value pairs: Tender Title, Description, Tender Notice Number, Tender Notice
   Date ("Wednesday , 07 October , 2026"), Required Category of Agency, Issuing Authority, Issuing Office, Tender
   Inviting Authority, Available between (two dates), Remaining period for Availability, Submission Date,
   Remaining period for Submission, Filled tender to be submitted to, Mode of submission, Tender Fees (in
   Rupees), Estimated Amount (in Rupees), Earnest Money Deposit (in Rupees), Documents Required, Probable Date
   of opening, and on some notices Prebid Conference Venue / Prebid Conference Date ("11:00 AM - Friday,
   30 October, 2026.").
   A notice's details do not change once it is published, so each ID is fetched ONCE (skip_if_seen), only when
   it first appears on the list. The ID travels in Raw.meta['tender_id'], because runner.reparse() does not
   replay the request body. Load on SMC: the first run posts once per listed tender (70 on 2026-10-24), and
   later daily runs make one GET plus one POST per new tender, 2 s apart (fetcher host delay). A detail page
   that fails to parse is posted again on the next run.

Stored:
-> 'tender' records from the list, keyed by the hdnCustomerId (e.g. '47260'). The list is the complete set of
   active tenders, so a tender that leaves it gets closed (valid_to = when it was first missing). Attributes:
     tender_id   the hdnCustomerId
     title       the list title, as published
     start       "Start Date" (ISO local datetime): documents available from
     end         "End Date" (ISO local datetime): last date for submission
     attempt     retender attempt number when the title says so, else None. Titles write it as "(2nd Attempt)",
                 "(2ND ATTEMPT)", "(Second Attempt)", "(Third Attempt)" or "(II ATTEMPT)" (22 of 70 on 2026-10-24)
   The "Availability" and "Submit within" day counts are not stored, because they change every day.
-> 'tender_notice' records from the detail pages, keyed by the same ID. These are never closed by the list:
   join them to the open 'tender' records to get the live ones. Attributes:
     tender_id, title, description, notice_no ("DMC/SZ-B/11/2026-27"), notice_date (ISO),
     agency_category ("Experienced"), issuing_authority, issuing_office, inviting_authority (designation and
       office as printed, lines joined with ", "; SMC truncates some, e.g. "surat municipal corporati"),
     available_from, available_to, submission_date, opening_date ("Probable Date of opening") (ISO dates),
     prebid_at (ISO local datetime of the prebid conference, None when not held),
     prebid_venue (as printed; in practice an office email such as exen.workshop@suratmunicipal.org. An email
       is kept only on an official domain: one notice gives a gmail.com address and one a misspelt
       "suratmunmicipal.org", and those become None),
     submit_to (office where a filled tender goes), submission_mode ("Postal Speed Post, RPAD"),
     fee_rs, estimated_amount_rs, emd_rs (Rupees, None when blank),
     amount_notes (the text SMC prints after an amount, by field: {'estimated_amount_rs': '+ GST'} or
       'without GST'; {} when there is none. Without a note the GST basis is not stated),
     documents_required (list of lines as printed),
     zone_code (surat.zone_code() of the issuing, else the inviting, authority when it names a zone; None for
       head-office departments; "New East (Sarthana) Zone" maps to east_b, whose zone office is at Sarthana. A bare
       "South Zone" maps to no zone, because SMC's South Zone is now split into South-A and South-B),
     other_labels (names of any labels this parser does not know; their values are not stored)
   Blank cells are stored as None. The "Remaining period" rows are not stored.
-> smc_city observations from the list, an instant reading dated to the day of the fetch (Asia/Kolkata, from
   Raw.retrieved_at), because the list has no data date (its "Last Updated: September 11, 2023" footer is a CMS
   edit time):
     tenders.active           number of tenders on the Active Tenders list
     tenders.closing_within   number whose End Date falls within dims.within_days ('2', '7', '14') days of the
                              fetch day (dates only; a tender closing today counts in every window, one whose
                              End Date has already passed but is still listed counts in none)
   validate() checks that "End Date" minus "Submit within" gives the fetch day (within a day), so a stale
   cached page is caught.

Snapshot 2026-10-24: 70 active tenders, all closing between 26 October and 20 November 2026 (4 within 2 days,
54 within 7, 69 within 14). Tender 47260: a passenger lift for the Moje-Gambheni health centre, South Zone-B
(Kanakpur), notice DMC/SZ-B/11/2026-27 of 07-10-2026, estimated Rs 12,49,799.25, EMD Rs 12,500, fee Rs 1,062,
submission 26-10-2026, probable opening 04-11-2026. Of the 70 detail pages, 24 had a prebid conference, 4 an
amount note ("+ GST" / "without GST"), 6 a blank estimated amount, and 41 named no zone that zone_code() knows
(mostly head-office departments such as Hydraulic, Drainage, Workshop and Light & Energy Efficiency).

Not collected, and why:
- Sums of estimated value by zone or department: each detail page is a separate document and parse() sees one
  document at a time, so the sum is not an observation. The 'tender_notice' records carry estimated_amount_rs
  and zone_code, so the dashboard can sum the live ones.
- Award, winner and contract value: not published on these pages.
- "Active Quotations" (/Information/Quotations, a separate list with Gujarati titles) and the e-Tenders
  explainer page (/Information/Tender/eTenders, text only) are not read.

Quirks and caveats:
- If SMC extends a tender, the list shows the new End Date (a new version of the 'tender' record), but the
  detail page is not fetched again, so 'tender_notice' keeps the dates as first published.
- Titles mix English and zone names in several spellings; the zone is taken from the authority fields, not the
  title.
- Some titles end in work numbers ("(W-1)", "work -4"); they are kept in the title.

Geography: SMC city (smc_city:smc) for counts; each notice names its zone (zone_code) or department.
Cadence: daily (the list changes daily; detail pages are fetched once per new tender). Units: tenders, Rupees.
Licence: Surat Municipal Corporation web pages; public information. No explicit open licence.
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `tenders.active` | SMC active tenders | tenders | 1 (1) | 1 | 2026-10-24 to 2026-10-24 | Number of tenders on SMC's "Active Tenders" list on the fetch day. |
| `tenders.closing_within` | SMC tenders closing soon | tenders | 3 (3) | 1 | 2026-10-24 to 2026-10-24 | Number of active tenders whose End Date (last date for submission) is on the fetch day or no more than dims.within_days (2, 7 or 14) days after it, counting whole dates. |

## aai_surat_airport

**AAI monthly passenger traffic at Surat airport**

- **Publisher:** Airports Authority of India (Traffic News, Annexure III)
- **Page:** https://www.aai.aero/en/business-opportunities/aai-traffic-news
- **Module:** transport; **cadence:** monthly (checked every 168 h)
- **Geography:** Surat airport (STV), geo facility:surat_airport under Surat district
- **Licence:** AAI website statistics; licence not stated
- **Enabled:** no; **last success:** never
- **Holds:** 0 observations
- **Notes:** Disabled: AAI hides its traffic-news PDF links from anonymous visitors until a download form (name, email with OTP, country, organisation, purpose) is completed, and robots.txt answers 403 to our User-Agent (checked 2026-10-24). We do not fill in or skip that form automatically. Manual workflow: open the listing page, choose the month, complete the form for "Annexure-III" and keep the PDF; parse() reads the SURAT rows from it. Data are provisional and subject to revision by AAI.

<details><summary>How it is collected and parsed</summary>

```text
Airports Authority of India monthly traffic news: passengers at Surat airport (STV), from Annexure III.

DISABLED (SOURCE.enabled=False): AAI puts its traffic-news downloads behind a registration form, and we do not
fill it in automatically or get around it. Checked on 2026-10-24 with our plain OpenCityBot User-Agent:
- The listing page https://www.aai.aero/en/business-opportunities/aai-traffic-news shows each month's PDFs as
  "click to download" items. Each item opens a form that asks for Name of the Person, Email, an OTP sent to that
  email, Country, Organisation and Purpose/Use. The direct PDF links are in the page, but the site's own
  stylesheet hides them from anonymous visitors until the form is completed
  (".role-anonymous-user .view-aai-traffic-news .views-row .views-field-field-news-type { display:none }", shown
  again only under ".download-destination-added"). Fetching the hidden links directly would skip that
  registration step, so the fetcher does not do it.
- https://www.aai.aero/robots.txt answers 403 Forbidden to our User-Agent, so the crawl policy cannot be read.

Manual workflow (see SOURCE.notes): a person opens the listing page, picks the month, completes the download form
for "Annexure-III" and keeps the PDF. parse() reads Surat's three passenger rows from that saved PDF. The CLI only
fetches, so loading saved files into the database is a maintainer step. The test fixture is pages 1, 2 and 5 of
the August 2026 Annexure III, which a research step saved on 2026-10-23.

Publisher: Airports Authority of India (AAI), Ministry of Civil Aviation, Government of India. Monthly "Traffic
News". The files are irregularly named, e.g. .../sites/default/files/traffic-news/Aug2k26Annex3.pdf next to
Aug2k26Annex_4.pdf and Anex5, so a manual user should pick the file by its label, not guess the name.

Document layout (bilingual Hindi/English PDF made from Excel; pdftotext -layout keeps the columns):
    ANNEXURE-III A  International Passengers   PASSENGERS (IN NOS.)
    ANNEXURE-III B  Domestic Passengers        Passengers(In Number's)
    ANNEXURE-III C  Total Passengers(Domestic+International)
Each part has the same header and one row per airport, grouped by airport category (INTERNATIONAL AIRPORTS,
PPP INTERNATIONAL, JV INTERNATIONAL AIRPORTS, CUSTOM AIRPORTS, DOMESTIC AIRPORTS, ...):
    S.NO  Airport            For The Month              For The Period
                             August   August   %        April To August           %
                             2026     2025     Change   2026-2027    2025-2026    Change
    15 सूरत SURAT             7021     15442    -54.5%   17406        82321        -78.9%
Surat is listed under "INTERNATIONAL AIRPORTS" (AAI-operated) in all three parts.

-> Observations at geo facility:surat_airport, with dims.traffic = 'international' | 'domestic' | 'total' (the
   part of Annexure III the row came from):
     aai.passengers        passengers handled in the report month (period = that calendar month)
     aai.passengers_fytd   passengers from 1 April to the end of the report month (period = FY start to month end)
   The month and year come from the header ("April To August" / "2026 ... 2026-2027"). Only the current-year
   columns are stored. The same-month-last-year columns are left out: they are the previous year's figures
   reprinted (possibly revised), and storing them would compete with that year's own report. The "% Change"
   columns are derived by AAI and not stored. A "-" or blank cell becomes status='not_reported'.

August 2026 (fixture): international 7,021, domestic 105,829, total 112,850 passengers. April-August 2026:
17,406 + 639,691 = 657,097. Surat's international traffic fell 54.5 % from August 2025 (15,442).

Not parsed: Annexures I (traffic summary by airport category), II (aircraft movements) and IV-VI (freight and the
other tables). No copy of them was examined, and fetching them would need the same form.

Caveats: AAI notes that the report "is compiled on the basis of data provided by the respective airport and is
subject to revision". Passengers are counted as AAI publishes them; transit and crew counting rules are not
stated in the annexure.

Geography: Surat airport (STV), a new 'facility' geography under surat_district. It serves Surat city and
district. Cadence: monthly; the report appears about four weeks after the month ends. Units: passengers (number).
Licence: AAI website statistics; no licence is stated on the page.
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `aai.passengers` | Airport passengers (AAI traffic news) | passengers | 0 |  |  | Passengers handled at the airport in the report month, as published in AAI Traffic News Annexure III, by dims.traffic: international (III A), domestic (III B), total (III C). |
| `aai.passengers_fytd` | Airport passengers, financial year to date (AAI traffic news) | passengers | 0 |  |  | Passengers handled from 1 April to the end of the report month ("For The Period" column of Annexure III), by dims.traffic: international, domestic, total. |

## smc_ebus

**SMC electric bus operations (fleet and cumulative totals)**

- **Publisher:** Surat Municipal Corporation (BRTS / city bus operations)
- **Page:** https://www.suratmunicipal.gov.in/Departments/BRTSEleBusOperations
- **Module:** transport; **cadence:** monthly (checked every 168 h)
- **Geography:** SMC city (city bus and BRTS network)
- **Licence:** Surat Municipal Corporation web page; public information
- **Enabled:** yes; **last success:** 2026-10-18T11:03:28+05:30
- **Holds:** 6 observations
- **Notes:** Values are dated to the page's "Last updated on date". Running totals have no published start date.

<details><summary>How it is collected and parsed</summary>

```text
SMC electric-bus operations: fleet size and cumulative running, fuel and emission totals.

Page: https://www.suratmunicipal.gov.in/Departments/BRTSEleBusOperations
A small server-rendered block (snapshot 2026-09-27):

    <h3>Total No. of Electric Buses Operated: 450</h3>
    one table, one header row and one data row:
        Total saved fuel (In Litres) | Fuel saving per day (In Litres) |
        GHG emission reduction (CO2e per day in Kg.) | Total GHG emission reduction (CO2e in Kg.) | Total Run Km
        23622009.74 | 22491.96 | 60278.43 | 63306981.51 | 77464469.40
    <div>Last updated on date: 30/04/2026</div>

The page publishes no ridership, energy (kWh) or route figures, so none are stored.

"Last updated on date" is a data date, not the server's render time: the snapshot taken on 2026-09-27 and the
page fetched on 2026-10-18 both said 30/04/2026. Every value is filed as an instant reading on that date, with
publisher_as_of set to it. The "Total ..." figures are running totals since e-bus operations began; the page does
not say when that was, so no start date is invented. Geography: SMC city (the city bus / BRTS network).
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `ebus.buses_operated` | Electric buses operated | buses | 1 (1) | 1 | 2026-04-30 to 2026-04-30 | "Total No. of Electric Buses Operated" on the page, as of its last-updated date. |
| `ebus.fuel_saved_litres_per_day` | Fuel saved per day by electric buses | litres/day | 1 (1) | 1 | 2026-04-30 to 2026-04-30 | "Fuel saving per day (In Litres)" as published (SMC does not say how the daily figure is derived). |
| `ebus.fuel_saved_litres_total` | Fuel saved by electric buses (cumulative) | litres | 1 (1) | 1 | 2026-04-30 to 2026-04-30 | "Total saved fuel (In Litres)": running total since e-bus operations began, as estimated by SMC. |
| `ebus.ghg_reduction_kg_co2e_per_day` | GHG emissions avoided per day | kg CO2e/day | 1 (1) | 1 | 2026-04-30 to 2026-04-30 | "GHG emission reduction (CO2e per day in Kg.)" as published. |
| `ebus.ghg_reduction_kg_co2e_total` | GHG emissions avoided (cumulative) | kg CO2e | 1 (1) | 1 | 2026-04-30 to 2026-04-30 | "Total GHG emission reduction (CO2e in Kg.)": running total since e-bus operations began. |
| `ebus.run_km_total` | Electric bus kilometres run (cumulative) | km | 1 (1) | 1 | 2026-04-30 to 2026-04-30 | "Total Run Km": running total since e-bus operations began (start date not published). |

## jjm_surat

**Jal Jeevan Mission: rural tap water connections (Surat, Tapi)**

- **Publisher:** Jal Jeevan Mission, Department of Drinking Water and Sanitation, Ministry of Jal Shakti, GoI
- **Page:** https://ejalshakti.gov.in/jjmreport/JJMIndia.aspx
- **Module:** water; **cadence:** daily (checked every 168 h)
- **Geography:** Surat and Tapi districts, rural households only (JJM does not cover the SMC or other urban areas)
- **Licence:** No licence stated; Government of India public dashboard (Jal Jeevan Mission IMIS)
- **Enabled:** yes; **last success:** 2026-10-24T22:41:58+05:30
- **Holds:** 12 observations
- **Notes:** Two POSTs to the dashboard's BindDistrictMap page method (Gujarat districts, as on today and as on 15 Aug 2019). The response has no date; the today view is filed on the fetch date. The 2019 coverage percent is not stored because JJM divides by today's household total.

<details><summary>How it is collected and parsed</summary>

```text
Jal Jeevan Mission (Har Ghar Jal): rural households with a tap water connection in Surat and Tapi districts.

Publisher: Jal Jeevan Mission (JJM), Department of Drinking Water and Sanitation, Ministry of Jal Shakti,
Government of India. The figures are the JJM IMIS numbers behind the public dashboard
https://ejalshakti.gov.in/jjmreport/JJMIndia.aspx ("Tap water supply in households (HHs)").

Endpoint: the dashboard's own ASP.NET page method, called with a JSON POST, no login or captcha (robots.txt on
ejalshakti.gov.in returns 404, so nothing is disallowed):

    POST https://ejalshakti.gov.in/jjmreport/JJMIndia.aspx/BindDistrictMap
    body {"StCode11": "351", "Cat": "11", "SubCat": "11", "Param": "21"}      (Content-Type: application/json)

Each value is passed through the page's JavaScript encodeTxt() (JJM_Dashboard.js, encN = 1): escape(), shift
every character code up by one, escape() again, append "1". So "351" is state code 24 (Gujarat), "11" is 0 and
"21" is 1. Cat 0 = household tap connections; SubCat 0 = "As on <today>", SubCat 1 = "As on 15 Aug 2019" (the
day JJM began); Param 1 = district level. fetch() makes two POSTs, the 15 Aug 2019 view first, then today's.

Response: {"d": [ {"__type": "JJMIndia+map_data", "KeyValue": "492", "KeyId": "0132", "Name": "Surat",
    "Name_hi": ..., "Per": "100.00", "ColorId": "5", "Value": "383576", "Total": "383576", "Lat": ..., "Long": ...,
    "ISHGJReported": "1", "IsHGJCertified": "0"}, ... ]}   one row per Gujarat district (33 in the snapshot).
    KeyValue is JJM's district code: 492 = Surat, 493 = Tapi (both are read; the other districts are ignored).
    KeyId, Name_hi, Lat, Long and ColorId (the map's legend class) are not used.
    Value = rural households with a tap connection on the view's date, Total = rural households now,
    Per = 100 * Value / Total (two decimals).
The response carries no date: the dashboard labels the today view with the browser's date. fetch() therefore puts
the fetch date (Asia/Kolkata) in meta.as_of, and parse() files the today view on that date (publisher_as_of too).

Metrics (geography surat_district / tapi_district; JJM counts RURAL households only, so homes inside the SMC area
and other urban local bodies are not included):
    jjm.rural_households          Total, today view: rural households in the district per JJM IMIS.
    jjm.households_with_tap       Value: rural households with a functional household tap connection; today view
                                  on the fetch date, and the 15 Aug 2019 view on 2019-08-15 (the JJM baseline).
    jjm.tap_coverage_pct          Per, today view only. The 15 Aug 2019 view's Per divides the 2019 connections by
                                  today's household total, so it is not stored (the 2019 Total is today's total too).
    jjm.har_ghar_jal_reported     ISHGJReported, today view: 1 if the district is reported "Har Ghar Jal" (every
                                  rural household reported as having a tap connection), else 0.
    jjm.har_ghar_jal_certified    IsHGJCertified, today view: 1 if the district is certified "Har Ghar Jal" (the
                                  gram sabhas of its villages have certified it by resolution), else 0.
A blank or "-" value becomes not_reported. Units: households, percent, 0/1 flags.

Snapshot 2026-10-24: Surat 383,576 of 383,576 rural households with a tap (100.00%), reported but not certified;
Tapi 239,248 of 239,248 (100.00%). On 15 Aug 2019: Surat 291,815, Tapi 100,229.

Caveats: the figures are self-reported by the state into JJM IMIS and change daily (the dashboard is live);
coverage is saturated at 100%, so mostly the household total moves. Gujarat's state total is not fetched.
Cadence: daily at the publisher; checked weekly. Licence: none stated; Government of India public dashboard
(cite Jal Jeevan Mission, Ministry of Jal Shakti).
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `jjm.har_ghar_jal_certified` | Har Ghar Jal certified district | flag | 2 (2) | 2 | 2026-10-24 to 2026-10-24 | 1 if JJM shows the district as Har Ghar Jal "certified" (certified by gram sabha resolutions), 0 if not. As on the fetch date. |
| `jjm.har_ghar_jal_reported` | Har Ghar Jal reported district | flag | 2 (2) | 2 | 2026-10-24 to 2026-10-24 | 1 if JJM shows the district as Har Ghar Jal "reported" (all rural households reported as having a tap connection), 0 if not. As on the fetch date. |
| `jjm.households_with_tap` | Rural households with a tap connection (JJM) | households | 4 (4) | 2 | 2019-08-15 to 2026-10-24 | Rural households with a functional household tap connection per JJM IMIS ("Value"): as on the fetch date, and as on 15 Aug 2019 (JJM baseline) for the period 2019-08-15. |
| `jjm.rural_households` | Rural households (JJM) | households | 2 (2) | 2 | 2026-10-24 to 2026-10-24 | Rural households in the district per Jal Jeevan Mission IMIS ("Total"), as on the fetch date. |
| `jjm.tap_coverage_pct` | Rural tap water coverage (JJM) | percent | 2 (2) | 2 | 2026-10-24 to 2026-10-24 | Rural households with a tap connection as a percent of all rural households, as published by JJM ("Per"), as on the fetch date. |

## smc_rainfall

**SMC rainfall statistics: Ukai dam, weir-cum-causeway, zone-wise rainfall and creek levels**

- **Publisher:** Surat Municipal Corporation (Ukai and weir figures credited on the page to the Irrigation Department / Collector Office)
- **Page:** https://www.suratmunicipal.gov.in/Home/RainfallInfo
- **Module:** water; **cadence:** 2-hourly (checked every 24 h)
- **Geography:** Ukai dam (dam:ukai, in Tapi district); Tapi weir-cum-causeway in Surat (weir); SMC zones (smc_zone, 8 zones incl. a single South Zone); SMC city total (smc_city); creek (khadi) gauges in Surat city (creek).
- **Licence:** Surat Municipal Corporation web page; public information
- **Enabled:** yes; **last success:** 2026-10-18T11:03:32+05:30
- **Holds:** 198 observations
- **Notes:** The page only shows the latest ~10 readings of each table (about 20 h of 2-hourly readings, 10 h of hourly creek readings). Refreshing every 2 h in June-October captures every reading; the daily refresh outside the monsoon leaves gaps. Zone rainfall per slot vs running daily total is not stated on the page (see metric description).

<details><summary>How it is collected and parsed</summary>

```text
SMC "Rainfall Statistics" page: Ukai dam, Tapi weir-cum-causeway, zone-wise rain and creek levels.

Page: https://www.suratmunicipal.gov.in/Home/RainfallInfo
Server-rendered HTML with five Bootstrap tab panes, each holding one table of the
most recent readings (newest first, about 10 rows):

  #UkaiDam          Date/Time | Level (ft) | Est. Inflow (cusec) | Est. Outflow (cusec)      2-hourly
                    text: "Ukai Full Reservoir Level - 345 ft", "Last Updated on 28-09-2026 02:12:37 AM",
                    "*Source-Irrigation Dept/Collector Office"
                    "Last Updated on" is the server's render time, NOT a data timestamp: two
                    fetches 37 s apart on 2026-10-04 differed only in it (12:37:56 vs 12:38:33 AM,
                    each ~2 s after the request). It is therefore not stored as publisher_as_of,
                    and normalize() blanks it so unchanged data hashes the same.
  #Causeway         Date/Time | Level (mt) | Est. Outflow (cusec)                            2-hourly
  ("Weir-Cum-       text: "Causeway overflow at 6.0 mt.", "Causeway is OPEN"
   Causeway" tab)
  #RainFall         Date/Time | Central Zone (mm) | West Zone (mm) | ... | South East Zone (mm) 2-hourly
                    (eight zones, still with a single "South Zone")
  #TotalRainFall    Date/Time | Total Rainfall (mm)                                          2-hourly
  #KhadiWaterLevel  Date/Time | Kakara Khadi Udhana Zone (D.L.- 8.48 MT) | ...                hourly

Timestamps look like "27/09/2026 24:00" (= 28/09/2026 00:00). Every reading is an
instant, so period_start == period_end == the ISO local datetime.

What the figures mean, as far as the page tells us:
- Zone rainfall is NOT cumulative over the season: on 27/09/2026 every zone showed
  0.00 mm in every slot while the "Total Rain Fall" tab stayed at 1983.00 mm. The page
  does not say whether a zone figure is the rain of the preceding 2-hour slot or a
  running total for the day, so the metric description says exactly that.
- "Total Rainfall (mm)" is a running city total (1983.00 mm in every slot of the dry
  days 27/09 and 03-04/10/2026); the page does not state when the accumulation starts
  or whether it is one gauge or an average of zones.
- Thresholds printed next to the readings (Ukai FRL, the causeway overflow level and
  each creek's danger level "D.L.") are stored as their own metrics, dated to the day of
  the latest reading they were shown with.
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `flood.causeway_overflow_level_m` | Causeway overflow level (as published) | m | 1 (1) | 1 | 2026-10-18 to 2026-10-18 | The "Causeway overflow at N mt." figure under the weir table: the level at which water overtops the causeway. Dated to the day of the latest weir reading it was shown with. |
| `flood.causeway_status` | Causeway status (as published) |  | 1 (1) | 1 | 2026-10-18 to 2026-10-18 | Text after "Causeway is" under the weir table (e.g. OPEN), stored in value_text. Stored at the instant of the latest weir reading shown with it; the page gives no separate time. |
| `flood.creek_danger_level_m` | Creek (khadi) danger level (as published) | m | 5 (5) | 5 | 2026-10-18 to 2026-10-18 | Danger level "D.L." printed in the creek column header, e.g. "(D.L.- 8.48 MT)". Dated to the day of the latest creek reading it was shown with. |
| `flood.creek_level_m` | Creek (khadi) water level | m | 50 (50) | 5 | 2026-10-18 to 2026-10-18 | Water level at an SMC creek (khadi) gauge, Khadi Water Level tab (hourly readings), metres as published ("MT"). |
| `flood.dam_frl_ft` | Ukai full reservoir level (as published) | ft | 1 (1) | 1 | 2026-10-18 to 2026-10-18 | The "Ukai Full Reservoir Level - N ft" figure printed above the Ukai table. Dated to the day of the latest Ukai reading it was shown with. |
| `flood.dam_inflow_cusec` | Ukai estimated inflow | cusec | 10 (10) | 1 | 2026-10-17 to 2026-10-18 | Column "Est. Inflow (cusec)" of the Ukai Dam tab: estimated inflow into the reservoir at the reading time, cubic feet per second, as published. Observed pattern (27/09 and 03-04/10/2026): it equals the outflow in slots where the level is unchanged and reads 0.00 in every slot where the level fell, so it looks like a storage-balance estimate floored at zero; a 0 here is not a measured zero river flow. |
| `flood.dam_level_ft` | Ukai reservoir level | ft | 10 (10) | 1 | 2026-10-17 to 2026-10-18 | Water level of the Ukai reservoir in feet, column "Level (ft)" of the Ukai Dam tab (2-hourly readings). The page states the Full Reservoir Level is 345 ft. |
| `flood.dam_outflow_cusec` | Ukai estimated outflow | cusec | 10 (10) | 1 | 2026-10-17 to 2026-10-18 | Column "Est. Outflow (cusec)" of the Ukai Dam tab: estimated release from the dam at the reading time, cubic feet per second, as published. |
| `flood.weir_level_m` | Weir-cum-causeway water level | m | 10 (10) | 1 | 2026-10-17 to 2026-10-18 | Column "Level (mt)" of the Weir-Cum-Causeway tab: water level at the Tapi weir-cum-causeway in Surat, metres as published (the page does not state the datum). |
| `flood.weir_outflow_cusec` | Weir-cum-causeway estimated outflow | cusec | 10 (10) | 1 | 2026-10-17 to 2026-10-18 | Column "Est. Outflow (cusec)" of the Weir-Cum-Causeway tab, cubic feet per second. |
| `rain.smc_total_mm` | Total rainfall, Surat city (cumulative) | mm | 10 (10) | 1 | 2026-10-17 to 2026-10-18 | Column "Total Rainfall (mm)" of the Total Rain Fall tab: cumulative rainfall for Surat city up to the reading time. The page does not state the start of the accumulation period (the monsoon season) or whether it is one gauge or an average of zones. |
| `rain.smc_zone_mm` | Zone-wise rainfall | mm | 80 (80) | 8 | 2026-10-17 to 2026-10-18 | Rainfall in the SMC zone for the slot ending at the reading time, from the Zonewise Rain Fall tab (2-hourly timestamps). Not cumulative over the season (all zones read 0.00 on 27/09/2026 while the season total was 1983 mm). The page does not say whether each figure is the rain of the preceding 2-hour slot or a running total for the day. |

## smc_water_quality

**SMC water samples collected and tested at consumer taps, by zone (monthly)**

- **Publisher:** Surat Municipal Corporation, Hydraulic Department
- **Page:** https://www.suratmunicipal.gov.in/Departments/HydraulicWaterQuality
- **Module:** water; **cadence:** monthly (checked every 168 h)
- **Geography:** SMC zones (7, 8 or 9 depending on the year) and the SMC total
- **Licence:** Surat Municipal Corporation web page and PDFs (RTI suo-motu disclosure); public information
- **Enabled:** yes; **last success:** 2026-10-18T11:11:05+05:30
- **Holds:** 5283 observations; records: document (215), wq_sampling_test (12)
- **Notes:** Monthly PDFs from May 2009; the unfit-sample address list in each PDF is not parsed or stored.

<details><summary>How it is collected and parsed</summary>

```text
SMC Hydraulic department: water samples collected and tested at consumer taps, by zone (monthly).

Index page: https://www.suratmunicipal.gov.in/Departments/HydraulicWaterQuality
  - a table of the sampling regime (stage / type of test / frequency), kept as `wq_sampling_test` records
  - "Monthly Data of Collected and Tested Water Samples": one link per month (Oct 2008 onward) to
    .../Content/Documents/rtiact/Disclosure/Hydraulic/WaterQuality/<YYYY>/<MM>.pdf, kept as `document` records

Each monthly PDF (Gujarati) starts with a summary table, one row per zone plus a total row:
    ઝોન | લેવાયેલા નમુનાઓ (samples taken) | ફીટ નમુનાઓ (fit) | અનફીટ નમુનાઓ (unfit)
followed by "અનફીટ સેમ્પલની વિગત": the date and HOUSEHOLD ADDRESS of every unfit sample. Only the summary
table is parsed into observations. From the list below it, only the DATES are read (to confirm the month, see
below); addresses are never read into observations or records. (The framework still archives the raw PDF
under data/raw/, which is git-ignored.)

The samples are household-tap samples taken during supply (the 2008 PDFs say "Residential Tap"; from 2011 a
note says samples from water works and distribution-station tanks are not included).

Zone labels. Gujarati text from these PDFs comes out of pdftotext with broken conjuncts and, in some years,
whole letters substituted (West is "વે ટ", "લેસ્ર્" or "ળેસ્ર્"; Central "સે લ", "વેન્્ર" or "શેન્્઱"), so
_zone() matches on shape, and validate() requires the zone SET to be one of the layouts SMC has used:
7 zones to Aug 2019, 8 from Sep 2019 (East split into East-A/East-B), 9 from Jul 2023 (South split into
South-A/South-B). The undivided East zone has no code in surat.ZONES, so this module adds smc_zone:east.

Layout repair. In a few PDFs pdftotext puts one number of a row on a line of its own (Dec 2014, North);
summary_rows() re-attaches it only if its character column fills exactly the missing cell.

Month. Normally the month in the URL (/YYYY/MM.pdf). But some PDFs are linked under the wrong month on the
index page: 2019/09.pdf is November 2019 and 2019/11.pdf is September 2019, 2020/06 and 2020/07 are swapped,
and 2020/04.pdf is a second copy of May 2020 (April 2020 is not published). In every such case the printed
heading and all the unfit-sample dates agree with each other and not with the link, so the month is taken
from the sample dates (>= 5 dates, >= 90% in one month; otherwise the URL month), and the printed heading
year must match it. Month names in the heading are too garbled to read reliably, so only the year is checked.

Not parsed: Oct 2008 - Apr 2009 and Apr 2011 (legacy non-Unicode font; digits not decodable) and Oct 2015
(the file on the server is truncated). fetch() skips them (FIRST_MONTH, UNREADABLE) so they are not
re-downloaded on every refresh; the index records list them with parsed: false.

Publisher arithmetic is not always exact (Jan 2013 Central: 545 taken, 524 fit, 22 unfit), so validate()
only rejects documents whose rows or columns are off by more than a small tolerance (a misparse signal).
A '-' cell becomes not_reported, even where the other columns imply zero (Jun 2011 South unfit).
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `wq.tap_samples_collected` | Water samples collected at consumer taps | samples | 1761 (1761) | 12 | 2009-05-01 to 2026-08-31 | Water samples collected from household taps during supply in the month (SMC monthly PDF). |
| `wq.tap_samples_fit` | Water samples found fit | samples | 1761 (1761) | 12 | 2009-05-01 to 2026-08-31 | Samples found fit for drinking (SMC tests against IS:10500). |
| `wq.tap_samples_unfit` | Water samples found unfit | samples | 1761 (1745) | 12 | 2009-05-01 to 2026-08-31 | Samples found unfit for drinking. |

## wrd_reservoirs

**Gujarat WRD daily reservoir storage: Surat and Tapi district dams, Sardar Sarovar**

- **Publisher:** Narmada, Water Resources, Water Supply and Kalpsar Department, Government of Gujarat
- **Page:** https://wrd-dam.gujarat.gov.in/
- **Module:** water; **cadence:** daily (checked every 12 h)
- **Geography:** Dams filed under Surat and Tapi districts in the WRD statement (geo level dam, parent surat_district / tapi_district; Ukai is in Tapi district), Sardar Sarovar (dam, parent state), the Surat and Tapi district totals, and the Gujarat grand total.
- **Licence:** Government of Gujarat daily report; public information
- **Enabled:** yes; **last success:** 2026-10-18T11:11:14+05:30
- **Holds:** 246 observations
- **Notes:** URL takes the report date base64-encoded (dt=). Each report date is immutable and fetched once (skip_if_seen). An empty response means the report is not out yet; it is retried on the next run.

<details><summary>How it is collected and parsed</summary>

```text
Gujarat WRD daily reservoir storage report (PDF): Surat and Tapi district dams, Sardar Sarovar.

Report: https://wrd-dam.gujarat.gov.in/downloads/home_pdf.php?dt=<base64 of YYYY-MM-DD>
Published by the Narmada, Water Resources, Water Supply and Kalpsar Department (N.W.R.W.S. & Kalpsar),
one 23-page TCPDF report per day, every page stamped "Date :- DD-MM-YYYY". Pages used:

  p1   ABSTRACT, and the "Sardar Sarovar(Narmada Dam)" block:
         FRL :138.68 | Design Gross Storage : 9460.00 | Percentage Storage : 98.77%
         Present Water Level (m) | Average In Flow (cusecs) | Gross Storage (MCM) | 7 release columns
  p2   "Districtwise Storage": design/present gross and live storage (MCM) and % per district,
         a SARDAR SAROVAR row, and the Grand Total (all 207 schemes incl. Sardar Sarovar)
  p3   "Gross Storage of major schemes": the Sardar Sarovar row gives its warning level and
         inflow / outflow (river) / outflow (canal) in cusecs
  p4+  "Statement showing the details of dams in Gujarat", one row per scheme (206, excl. Sardar Sarovar):
         Sr | Scheme Id | Location Id | District | Taluka | Name | Region | Type | OSL | FRL | PWL (m) |
         design gross/live/dead | present gross/live/dead (MCM) | % filling | RF | CRF | warning |
         inflow | outflow river | outflow canal (cusecs)

What is stored (period = the report date, an instant):
  - every scheme the detailed statement files under District "Surat" or "Tapi" (2026: Lakhigam and
    Ver-II in Surat district; Ukai and Doswada in Tapi district). Ukai is in Tapi district (Songadh
    taluka) and is stored with parent tapi_district, never as a Surat dam.
  - Sardar Sarovar (Narmada district, parent: state) from pages 1-3.
  - the Surat and Tapi district rows and the Gujarat Grand Total of the districtwise table.

Layout notes: TCPDF wraps numbers that do not fit their cell, so `pdftotext -layout` prints e.g.
Ukai's design gross storage as "7414.2" with a "9" on the next line, right-aligned under it. Each
continuation fragment is joined to the cell on the row line whose column span it shares
(_merge_continuations). The warning cell wraps the same way ("HIGH"/"ALERT", "WARNI"/"NG").
A row of a Surat/Tapi scheme that cannot be read exactly raises; it is never guessed.

Unpublished days: the server answers 200 with an empty body (and a "report_01-01-1970.pdf" file
name) for a date whose report is not out yet. fetch() does not pass those on, so the date is
fetched again on the next run. The day's report is created at about 09:00 IST (PDF CreationDate
08:38-09:03 on five reports checked), so today's date is only asked for from 10:00 IST.
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `wrd.alert_level` | Reservoir warning level |  | 15 (15) | 5 | 2026-10-15 to 2026-10-17 | value_text = the report's "Type of Warning": HIGH ALERT (above 90% full), ALERT (80-90%), WARNING (70-80%) or NIL (below 70%), per the report's own abstract. |
| `wrd.dam_frl_m` | Full reservoir level | m | 15 (15) | 5 | 2026-10-15 to 2026-10-17 | Full reservoir level (FRL, metres) as printed in that day's report. |
| `wrd.dam_level_m` | Reservoir water level | m | 15 (15) | 5 | 2026-10-15 to 2026-10-17 | Present water level (PWL, metres) from the detailed dam statement; for Sardar Sarovar the "Present Water Level (in m)" of its page-1 block. |
| `wrd.design_gross_storage_mcm` | Design gross storage | MCM | 24 (24) | 8 | 2026-10-15 to 2026-10-17 | Design gross storage capacity in million cubic metres. For a district or the state: the districtwise table's total over its dams. |
| `wrd.design_live_storage_mcm` | Design live storage | MCM | 24 (24) | 8 | 2026-10-15 to 2026-10-17 | Design live storage capacity (MCM). District/state values from the districtwise table. |
| `wrd.gross_storage_mcm` | Present gross storage | MCM | 24 (24) | 8 | 2026-10-15 to 2026-10-17 | Present gross storage (MCM) on the report date. District/state values from the districtwise table. |
| `wrd.gross_storage_pct` | Storage, % of design gross | % | 24 (24) | 8 | 2026-10-15 to 2026-10-17 | Present gross storage as a percentage of design gross storage, as printed ("Percentage Filling %" for a dam; the gross % column of the districtwise table). |
| `wrd.inflow_cusec` | Inflow | cusecs | 15 (15) | 5 | 2026-10-15 to 2026-10-17 | Inflow into the reservoir in cusecs as printed in the report (Sardar Sarovar: the "Inflow in Cusecs" of the major-schemes table). |
| `wrd.live_storage_mcm` | Present live storage | MCM | 24 (24) | 8 | 2026-10-15 to 2026-10-17 | Present live storage (MCM) on the report date. District/state values from the districtwise table. |
| `wrd.live_storage_pct` | Live storage, % of design live | % | 12 (12) | 4 | 2026-10-15 to 2026-10-17 | Present live storage as a percentage of design live storage, from the districtwise table (districts, the state total and Sardar Sarovar only; the dam statement does not print it). |
| `wrd.outflow_canal_cusec` | Outflow to canals | cusecs | 15 (15) | 5 | 2026-10-15 to 2026-10-17 | Outflow released to canals, cusecs, as printed. |
| `wrd.outflow_river_cusec` | Outflow to the river | cusecs | 15 (15) | 5 | 2026-10-15 to 2026-10-17 | Outflow released to the river, cusecs, as printed. |
| `wrd.rain_24h_mm` | Rainfall at the dam, last 24 hours | mm | 12 (12) | 4 | 2026-10-15 to 2026-10-17 | Column RF of the dam statement (the rainfall statement calls it "Rain During Last 24 Hour"). |
| `wrd.rain_cumulative_mm` | Cumulative rainfall at the dam | mm | 12 (12) | 4 | 2026-10-15 to 2026-10-17 | Column CRF of the dam statement ("Cumm Rainfall"). The report does not state the start date of the accumulation. |

## gsdma_rainfall

**GSDMA daily rainfall report: Surat district talukas vs 1996-2025 average**

- **Publisher:** Gujarat State Disaster Management Authority / State Emergency Operation Centre, Government of Gujarat
- **Page:** https://gsdma.org/rainfalldata-2?Type=2
- **Module:** weather; **cadence:** daily (checked every 12 h)
- **Geography:** Surat district talukas (surat_taluka, a level added by this adapter; 12 rows in 2026), Surat district (the published district average row) and Gujarat (state average and monthly state rain).
- **Licence:** Government of Gujarat public document; no explicit licence stated
- **Enabled:** yes; **last success:** 2026-10-24T21:58:43+05:30
- **Holds:** 405 observations
- **Notes:** Monsoon season only (about 2 June to 21 October in 2026). Only the newest 10 reports are fetched per run. Early-season files of 2026 (2 Jun - 7 Aug) answered HTTP 401 and are not requested. The percentage is season-to-date total against the whole-season average, not against the normal to date.

<details><summary>How it is collected and parsed</summary>

```text
GSDMA daily taluka-wise rainfall report: Surat district talukas against their 1996-2025 average.

Publisher: Gujarat State Disaster Management Authority (GSDMA) / State Emergency Operation Centre, Revenue
Department, Government of Gujarat. The report is an Excel sheet exported to PDF ("8 - RAINFALL REPORT-ZONEWISE/
TALUKAWISE"), posted every morning of the monsoon season.

Where it is published:
  Page      https://gsdma.org/rainfalldata-2?Type=2  ("Rainfall Data": a year calendar; click a day for its PDF)
  List      POST https://gsdma.org/GetFileData.aspx/GetColumnChartData
            body (JSON) {"Type": "2", "Year": "2026"}   (the page sends the Type from its own URL; Type 1 is empty)
            -> {"d": [{"__type": "GSDMA.GetFileData+ChartDetails", "DiffProjectCount": 0,
                       "PDFName": "https://www.gsdma.org/uploads/Rainfall/24hrsrainfalldata21stoctober1021...pdf",
                       "Date": "10/21/2026"}, ...]}          Date is MM/DD/YYYY; 142 reports for 2026 (2 Jun - 21 Oct)
  Report    the PDFName URL: a text PDF, 5 pages, read with pdftotext -layout. The files of 12 Aug - 2 Oct 2026 are
            named "ilovepdfmerged*.pdf"; the one checked (30 Sep) has 16 pages, the same report pages first.

Report layout. Every page starts with
    Rainfall Report 21-10-2026 (Rainfall in mm)(Dt.20.10.2026 06:00 am to Dt.21.10.2026 06:00 am)
then two side-by-side tables, one row per taluka, grouped by region and district:
    Sr. No | District/ Taluka | Avrg Rain (1996-2025) | Rain till Yesterday | Rain During last 24 Hrs. |
    Total Rainfall | % Against Avg Rain
Each district block is "<n> <District>", its taluka rows "<sr> <Taluka> <5 numbers>", and a "Dist. Avg." row.
On page 4 the Surat block ("31 Surat") is in the left table and shares its lines with a summary box on the right
("Raining Taluka/s", "June- 2026 Rain 35.21", ...), so lines are cut into cells at runs of 2+ spaces and only the
first 6 cells of a Surat row are read. The right table of page 4 ends with the "State Average" row; the summary
box lists the state's rain per month ("June- 2026 Rain" ... "November-2026 Rain") and their "Total".

What is stored:
- Surat district talukas (geo level surat_taluka, a level added by this adapter, parent surat_district): the 12
  rows printed under Surat in 2026: Ambika, Areth, Bardoli, Chorasi, Kamrej, Mahuva, Mandvi, Mangrol, Olpad,
  Palsana, Surat City, Umarpada. "Surat City" is GSDMA's reporting unit for the city taluka(s), not the SMC
  boundary, so it is NOT filed as smc_city.
- Surat district (surat_district): the "Dist. Avg." row. In the 2026 reports it is the plain (unweighted) mean of
  the 12 taluka rows; validate() checks this, which also catches a skipped or mis-read row.
- Gujarat (state): the "State Average" row, and the state's rain per month from the summary box.
Metrics:
  gsdma.rain_24h_mm          rain in the report's 24 hours (06:00 to 06:00 IST); period = that window
  gsdma.rain_season_mm       "Total Rainfall": rain since the start of the season, up to 06:00 IST of the report
                             day; an instant reading at that time (the report does not print when the
                             accumulation starts; its month list starts in June)
  gsdma.rain_normal_mm       "Avrg Rain (1996-2025)": the average WHOLE-SEASON rainfall over those years;
                             period = the averaging years as printed (1996-01-01..2025-12-31)
  gsdma.rain_pct_of_normal   "% Against Avg Rain" = season total so far / whole-season average x 100. It is NOT
                             "% of normal to date": early in the season it is low by construction.
  gsdma.state_month_rain_mm  state average rain in a calendar month; for the report's own month the period is
                             the 1st of the month to the report day (month to date); later months are not stored
"Rain till Yesterday" is not stored: it is Total minus the 24-hour figure (parse() checks that identity).
Units: millimetres; % for the ratio. Cadence: daily from about 2 June to 21 October (2026).

Quirks:
- Ambika and Areth appear as separate Surat rows in the 2026 reports; their printed 1996-2025 averages are
  identical to Mahuva's (1653 mm) and Mandvi's (1521 mm). Similar pairs elsewhere: Ukai = Songadh (Tapi),
  Chikda = Dediapada (Narmada, also printed with the same serial number). Stored as printed.
- The list can point at the wrong file: in 2026 the entry for 19 Oct is "24hrsrainfalldata17thoctober...pdf",
  whose content is the 17 Oct report. The report date is always taken from the PDF itself, so such an entry
  just re-stores the 17 Oct values; the 19 Oct report is missing.
- The early-season files are named "24hrsrainfalldatadt<stamp>.<dd>.<mm>.<yyyy>.pdf" (2 Jun - 7 Aug 2026); the
  two tried (2 Jun, 7 Aug) answer HTTP 401 Unauthorized. They are outside LOOKBACK, and nothing tries to get
  around a 401: it is recorded as a failed fetch.
- Month totals of a past month can still change (September 2026 was 125.53 mm on 30 Sep and 125.81 mm on
  17 Oct); later reports overwrite and the change is kept as a revision.
- A report's "Rain till Yesterday" is not always the previous report's Total: late returns are added without a
  24-hour figure (Surat Dist. Avg.: Total 1757.92 mm on 20 Oct 2026, then 0.00 mm in 24 h but Total 1758.08 mm
  on 21 Oct). So season totals can rise on a day with 0 mm in the last 24 hours; both are stored as printed.

fetch(): the year's list (one POST), then the newest LOOKBACK reports, oldest first, each downloaded once
(skip_if_seen: a posted PDF does not change). Reports older than that are not fetched.

Licence: Government of Gujarat public document; no licence is stated on the page or the PDF.
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `gsdma.rain_24h_mm` | Rainfall in the last 24 hours (GSDMA) | mm | 126 (126) | 14 | 2026-10-11 to 2026-10-21 | "Rain During last 24 Hrs." of the GSDMA daily report: rain from 06:00 IST of the previous day to 06:00 IST of the report day (the period). |
| `gsdma.rain_normal_mm` | Average season rainfall (GSDMA, 1996-2025) | mm | 14 (14) | 14 | 1996-01-01 to 2025-12-31 | "Avrg Rain (1996-2025)": average whole-season rainfall over the years printed in the header; the period is those years. For the district and the state it is the published average row. |
| `gsdma.rain_pct_of_normal` | Season rainfall so far, % of the season average (GSDMA) | % | 126 (126) | 14 | 2026-10-12 to 2026-10-21 | "% Against Avg Rain" = season total so far / whole-season average x 100, as printed; an instant reading at 06:00 IST of the report day. Not a comparison with the normal to date. |
| `gsdma.rain_season_mm` | Season rainfall so far (GSDMA) | mm | 126 (126) | 14 | 2026-10-12 to 2026-10-21 | "Total Rainfall" of the GSDMA daily report: rain since the start of the monsoon season up to 06:00 IST of the report day (an instant reading at that time). |
| `gsdma.state_month_rain_mm` | Gujarat average rainfall in the month (GSDMA) | mm | 13 (13) | 1 | 2026-06-01 to 2026-10-21 | State average rainfall in a calendar month, from the summary box ("June- 2026 Rain"). For the report's own month the period ends on the report day (month to date). |

## openmeteo_surat

**Open-Meteo weather model: Surat current conditions and daily forecast**

- **Publisher:** Open-Meteo.com (weather model data from national weather services)
- **Page:** https://open-meteo.com/en/docs
- **Module:** weather; **cadence:** 3-hourly (checked every 3 h)
- **Geography:** SMC city, represented by the single model grid cell Open-Meteo picks for 21.170 N, 72.831 E (central Surat); the response gives the cell used (21.195 N, 72.787 E, elevation 17 m in Oct 2026).
- **Licence:** CC-BY 4.0 (credit Open-Meteo.com); free API for non-commercial use, under 10,000 calls a day
- **Enabled:** no; **last success:** never
- **Holds:** 0 observations
- **Notes:** Disabled: api.open-meteo.com/robots.txt disallows all paths for all user agents (checked 2026-10-24), although Open-Meteo's terms invite free non-commercial API use. Enable only after the maintainers decide that the API host's robots.txt does not apply to this client. Values are weather-model output, not station observations; the 2 past days are model values too.

<details><summary>How it is collected and parsed</summary>

```text
Open-Meteo weather model data for Surat city: current conditions and a 10-day daily forecast.

Publisher: Open-Meteo.com, an open-source weather API that serves numerical weather model output from
national weather services (ECMWF, NOAA GFS, DWD ICON and others; its "best match" blend picks the models
for the location). These are MODEL values, not readings from a weather station: label them as such.

DISABLED BY DEFAULT (SOURCE.enabled=False). https://api.open-meteo.com/robots.txt reads
    User-agent: *
    Disallow: /
(checked 2026-10-24; the website https://open-meteo.com/robots.txt allows everything). Open-Meteo's terms
offer the API free and without a key for non-commercial use, so the Disallow is probably aimed at search
crawlers, but this project's rule is to respect robots.txt, so the adapter does not fetch unless the
maintainers decide otherwise and set enabled=True. parse() works on a saved response (the test fixture is one
real response fetched once while checking the source).

Request (one GET, no key, no cookies):
    https://api.open-meteo.com/v1/forecast
      ?latitude=21.170&longitude=72.831                     a point in central Surat (LAT/LON below)
      &current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,
               wind_direction_10m,surface_pressure,precipitation
      &daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,
             precipitation_sum,wind_speed_10m_max,sunrise,sunset,uv_index_max
      &timezone=Asia/Kolkata&forecast_days=8&past_days=2
Default units are requested (degC, km/h, mm, hPa).

Response (JSON):
    latitude, longitude, elevation     the model grid cell actually used (21.195 N, 72.787 E, 17 m on
                                       2026-10-24, about 5 km from the requested point, still inside SMC)
    utc_offset_seconds (19800), timezone ("Asia/Kolkata")
    current_units {...}, current {time: "2026-10-24T02:00", interval: 900, temperature_2m: 25.9, ...}
    daily_units {...},   daily {time: [10 dates], weather_code: [...], temperature_2m_max: [...], ...}
All times are local (IST) because timezone=Asia/Kolkata is requested. validate() checks the units, so a change
of default units fails loudly instead of being stored under the wrong unit.

What is stored (geography smc_city: one model grid cell in Surat city; see geo_note):
- Current conditions, as an instant reading at current.time (Open-Meteo rounds it to 15 minutes; the
  values come from its 15-minutely model data). Precipitation is the amount over the preceding
  current.interval seconds (900 s), so its period is [time - interval, time].
- Daily values for 10 days: the 2 past days (past_days=2: model values, not observed weather), today, and
  7 days ahead. Each day covers 00:00-24:00 IST. Every refresh replaces the forecast for a day; earlier
  forecasts survive in observation_revision, so the forecast history is kept.
- weather_code is the WMO weather interpretation code (WMO 4677 subset used by Open-Meteo); value_text holds
  Open-Meteo's description (e.g. 0 "Clear sky", 3 "Overcast", 95 "Thunderstorm").
- sunrise/sunset are stored as value_text "HH:MM" (IST) with no numeric value.

Cadence: Open-Meteo refreshes its models about hourly; every 3 hours is enough for a dashboard tile.
Quirks: a missing value comes back as null and is stored as not_reported. precipitation_probability_max is
only available for the forecast models that provide it; Open-Meteo returns null where it does not.

Licence: https://open-meteo.com/en/terms (checked 2026-10-24): users of the free API accept the CC-BY 4.0
licence (credit Open-Meteo.com), use it for non-commercial purposes only, and stay under 10,000 calls a day,
5,000 an hour and 600 a minute. This adapter would make about 8 calls a day.
```

</details>

| Metric | Label | Unit | Observations (reported) | Places | Periods | Description |
|---|---|---|---|---|---|---|
| `openmeteo.apparent_temperature_c` | Feels-like temperature (model) | degC | 0 |  |  | Current apparent ("feels like") temperature from temperature, humidity and wind (current.apparent_temperature). |
| `openmeteo.daily_precip_probability_max_pct` | Chance of rain (model) | % | 0 |  |  | Highest hourly probability of precipitation during the day from the forecast ensembles (daily.precipitation_probability_max). |
| `openmeteo.daily_precip_sum_mm` | Precipitation of the day (model) | mm | 0 |  |  | Total rain + showers + snow of the day (daily.precipitation_sum). |
| `openmeteo.daily_temperature_max_c` | Maximum temperature of the day (model) | degC | 0 |  |  | Highest 2 m air temperature of the day, 00:00-24:00 IST (daily.temperature_2m_max). |
| `openmeteo.daily_temperature_min_c` | Minimum temperature of the day (model) | degC | 0 |  |  | Lowest 2 m air temperature of the day, 00:00-24:00 IST (daily.temperature_2m_min). |
| `openmeteo.daily_uv_index_max` | Maximum UV index of the day (model) | UV index | 0 |  |  | Highest UV index of the day under the forecast cloud cover (daily.uv_index_max). |
| `openmeteo.daily_weather_code` | Weather of the day (WMO code, model) | WMO code | 0 |  |  | Most severe WMO weather code of the day (daily.weather_code); value_text = description. Past days are model values, later days a forecast. |
| `openmeteo.daily_wind_speed_max_kmh` | Maximum wind speed of the day (model) | km/h | 0 |  |  | Highest hourly wind speed 10 m above ground during the day (daily.wind_speed_10m_max). |
| `openmeteo.precipitation_mm` | Precipitation in the last 15 minutes (model) | mm | 0 |  |  | Rain + showers + snow over the preceding current.interval seconds (900 s); the period is that interval (current.precipitation). |
| `openmeteo.relative_humidity_pct` | Relative humidity at 2 m (model) | % | 0 |  |  | Current relative humidity 2 m above ground (current.relative_humidity_2m). |
| `openmeteo.sunrise` | Sunrise |  | 0 |  |  | value_text = local sunrise time "HH:MM" (IST) at the grid cell (daily.sunrise). |
| `openmeteo.sunset` | Sunset |  | 0 |  |  | value_text = local sunset time "HH:MM" (IST) at the grid cell (daily.sunset). |
| `openmeteo.surface_pressure_hpa` | Surface air pressure (model) | hPa | 0 |  |  | Current air pressure at the surface of the grid cell, not reduced to sea level (current.surface_pressure). |
| `openmeteo.temperature_c` | Air temperature at 2 m (model) | degC | 0 |  |  | Current air temperature 2 m above ground from Open-Meteo's weather models (current.temperature_2m), instant at current.time. |
| `openmeteo.weather_code` | Current weather (WMO code, model) | WMO code | 0 |  |  | Current WMO weather interpretation code (current.weather_code); value_text = Open-Meteo's description of the code. |
| `openmeteo.wind_direction_deg` | Wind direction at 10 m (model) | degrees | 0 |  |  | Current direction the wind blows FROM, degrees clockwise from north (current.wind_direction_10m). |
| `openmeteo.wind_speed_kmh` | Wind speed at 10 m (model) | km/h | 0 |  |  | Current wind speed 10 m above ground (current.wind_speed_10m). |
