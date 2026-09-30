# Other district modules (census, dams, rainfall, power, housing, maps)

Full findings for this dimension, covering both cities.

**Ease scale (0-5):**
- **5:** current and machine-readable, no login.
- **4:** current HTML tables or text PDFs.
- **3:** stale or messy.
- **2:** scanned or legacy-font PDFs, a login wall, or a dashboard with no export.
- **1:** news only.
- **0:** not public.

"Fetched live" means the researcher loaded the URL during the session. Where the verifier corrected a claim, the correction is in the verifier section at the end.

## Scores (0-10)

- **Researcher:** Surat 7.5, Ahmedabad 5
- **After verification:** Surat 7.5, Ahmedabad 5

**Researcher's rationale:** Surat has a live, city-owned hydrology feed (Ukai plus zone-wise rain) in fetchable HTML, project-level PMAY tables, a split power distributor that leaves a state-owned DGVCL open to RTI, and clean slugs. Ahmedabad wins only on ward polygons, where DataMeet has a ready 48-ward GeoJSON. Its AMC pages need the TLS workaround, and it has no dam story of its own.

**Verifier's reasoning:** Confirmed: live Ukai and zone-rain HTML, the WRD PDF (note that Ukai sits in Tapi district) and the upstream 'ahmadabad' slug mismatch. The only Ahmedabad win is its ward polygons.

## City-by-city comparison

| Metric | Surat | Ahmedabad | Edge |
|---|---|---|---|
| Dam/reservoir module | Ukai is the city's own dam. SMC rainfallinfo gives 2-hourly level and inflow/outflow (27/09/2026), and the state WRD daily PDF has Ukai at 83.26% ALERT. | No dedicated dam. It would have to proxy with Sardar Sarovar (99.05%) or Dharoi from the state WRD daily PDF, which is a weaker civic story. | Surat |
| Rainfall | SMC publishes zone-wise city rainfall and Khadi water levels in HTML. | Not found on the AMC site this session. The state Relief page's files stop in 2023. | Surat |
| Census 2011 DCHB | NADA catalog 422/423, Part A+B PDFs. The 2011 district already excludes Tapi (split off in 2007). | NADA catalog 405. The 2011 district includes the Botad-area talukas that became Botad district in 2013, so boundaries do not match today's. | Surat |
| Ward polygons | No official or DataMeet GeoJSON. Only a third-party bharatlas viewer (30 wards). | DataMeet Wards.geojson with 48 wards, verified and openly licensed. | Ahmedabad |
| PMAY-U / housing | SMC has project-wise HTML tables (flats, TP scheme, contractor, tender value, status). | No city-level public table verified. The national portal is a dashboard only. | Surat |
| Power distribution and RTI | Torrent Power (TPL-D(S)) serves part of the city and state-owned DGVCL the rest (the exact boundary still needs checking). DGVCL is a public authority, so RTI is possible for part of the city. | Torrent Power (TPL-D(A)) is the licensee for Ahmedabad/Gandhinagar. As a private company it is likely not an RTI public authority, so RTI has to go through GERC. | Surat |
| Leadership directories | surat.nic.in Who's Who (S3WaaS HTML). SMC site fetches cleanly. | ahmedabad.nic.in Who's Who (same template). The AMC Mayor page is a dynamic page behind legacy TLS. | Surat |
| Map slug in upstream geo file | slug 'surat' matches constants. | The geojson slug is 'ahmadabad', but districts.ts uses lockedDistrict('ahmedabad'), so an alias or fix is needed. | Surat |

## All sources found

| Metric | City | Source | URL | Format | Granularity | Latest period | Ease (0-5) | Fetched live | Access notes |
|---|---|---|---|---|---|---|---|---|---|
| Ukai dam level, inflow/outflow (2-hourly), zone-wise city rainfall, Khadi (creek) levels | Surat | SMC Rainfall Statistics / flood info page | https://www.suratmunicipal.gov.in/Home/rainfallinfo | HTML tables (server-rendered) | 2-hourly dam readings; SMC zone-wise rainfall | 27/09/2026 24:00 | 4 | yes | Fetched with plain curl. Showed Ukai FRL 345 ft and a level of 337.82 ft on 27/09/2026. Scrapeable; no API. |
| Flood monitoring dashboard (Ukai, Tapi weir, rainfall) | Surat | SMC Disaster Management System web | https://office.suratmunicipal.org/DisasterManagementSystemweb | HTML dashboard | station-level | live | 3 | yes | Returns HTTP 200. Mostly the same data as the rainfallinfo page, which is easier to parse. |
| Daily reservoir storage, % full, alert level (all Gujarat dams incl. Ukai, Sardar Sarovar, Dharoi, Kadana) | Gujarat-state | NWRWS&K Dept Reservoir Data Management System | https://wrd-dam.gujarat.gov.in/ | Daily PDF via /downloads/home_pdf.php?dt=<base64 YYYY-MM-DD> | per reservoir, daily; district column | 27-09-2026 | 4 | yes | The 2026-09-27 PDF (23 pages) is a text layer that pdftotext -layout can parse. Ukai 83.26% ALERT; Sardar Sarovar 99.05%. Ahmedabad has no dam of its own, so the city would have to proxy with Narmada/Dharoi. |
| Daily taluka rainfall (SEOC) | Gujarat-state | Commissioner of Relief - Daily Rainfall Data | https://directorateofrelief.gujarat.gov.in/daily-rainfall-data | PDF/XLS links | taluka | newest linked file dated 17-07-2023 | 3 | yes | The page loads, but the linked files are stale (2023; one XLS from 2020). Current SEOC reports seem to reach the public only through the press or district sites. |
| Census 2011 District Census Handbook (Part A village/town directory, Part B PCA) | Both | Census of India NADA catalog (Surat 422/423, Ahmadabad 405) | https://censusindia.gov.in/nada/index.php/catalog/422 | PDF (text layer + map images), English | village/town/ward | 2011 | 3 | yes | The TLS chain is incomplete: curl needs -k and WebFetch fails. The Surat file is DH_2011_2425_PART_A_DCHB_SURAT.pdf. Stale and large, but still the only ward-level census baseline. |
| PMAY/affordable housing project list (flats, location/TP scheme, contractor, tender Rs lakh, status) | Surat | SMC Dept of Affordable Housing - PMAY | https://www.suratmunicipal.gov.in/Departments/PradhanMantriAwasYojana | HTML tables | project-level | current page (date not stamped) | 4 | yes | Completed and work-in-progress tables (e.g. SUMAN JYOT, 300 flats, Completed). A good hook for RTI questions about delays. |
| PMAY-U national dashboard | National | PMAY-Urban portal | https://pmay-urban.gov.in/ | HTML dashboard | state (city-level not confirmed) | current | 2 | yes | Returns HTTP 200. City-wise sanctioned/completed figures for AMC were not found in public data this session. |
| Ward boundary polygons (48 AMC wards) | Ahmedabad | DataMeet Municipal_Spatial_Data | https://raw.githubusercontent.com/datameet/Municipal_Spatial_Data/master/Ahmedabad/Wards.geojson | GeoJSON | ward | undated (48-ward delimitation) | 5 | yes | 48 features, e.g. '48 RAMOL HATHIJAN'. Open licence, drops straight in. DataMeet has no Surat folder. |
| Ward boundary polygons (30 SMC wards) | Surat | bharatlas (third-party) | https://bharatlas.com/view/wards_surat | Web viewer; GeoJSON download claimed | ward | unknown | 3 | yes | The page returns 200, but the download and its licence/provenance were not checked. No official SMC GeoJSON found. |
| Collector / district officials directory | Surat | Surat district NIC site - Who's Who | https://surat.nic.in/whos-who/ | HTML (S3WaaS) | officer | current | 4 | yes | Standard S3WaaS template, so the same scraper works for both districts. |
| Collector / district officials directory | Ahmedabad | Ahmedabad district NIC site - Who's Who | https://ahmedabad.nic.in/whos-who/ | HTML (S3WaaS) | officer | current | 4 | yes | Same template as Surat. |
| Mayor / Municipal Commissioner page | Ahmedabad | AMC site | https://ahmedabadcity.gov.in/Tourism/Mayor_Dynamic?D=Mayor | HTML (dynamic) | office-bearer | unknown | 2 | yes | Needs the legacy-TLS workaround. /Tourism/Mayor returns a 302 to Mayor_Dynamic, which sits oddly under the Tourism path. Only the 302 was confirmed. |
| Power distribution reliability/performance (Torrent Power licence areas) | Both | Torrent Power regulatory performance reports | https://www.torrentpower.com/index.php/regulatory/performancereport/AHD | HTML index of PDFs | licence area (TPL-D(A) Ahmedabad; TPL-D(S) Surat) | not checked | 3 | yes | A private licensee that publishes because GERC requires it. The GERC tariff orders for FY2026-27 (TPL-D(A)) and FY2024-25 (TPL-D(S)) exist as PDFs. |

## Data gaps: candidates for RTI

| Metric | City | Public authority | RTI question |
|---|---|---|---|
| City-wise PMAY-U sanctioned/grounded/completed houses and beneficiaries by component (AHP/BLC/ISSR/CLSS) | Ahmedabad | Amdavad Municipal Corporation - Housing/Slum Upgradation (Estate & TDO) dept PIO | For PMAY-U 1.0 and 2.0 in AMC limits, give for each financial year from 2015-16 to 2026-27, and for each vertical (AHP, BLC, ISSR, ARHC), the number of houses sanctioned, grounded, completed and allotted, with the project-wise list (location, zone/ward, contractor, sanctioned cost, completion date), as a spreadsheet if available. |
| Zone/ward-wise daily rainfall and waterlogging complaints | Ahmedabad | AMC - Flood Control Cell / Storm Water Drainage dept PIO | Provide daily rainfall recorded at each AMC rain-gauge station (station, zone, ward, mm) from 1 June to 30 September 2026, and the number of waterlogging complaints received and resolved per ward in the same period, with average resolution time. |
| Power outages and reliability indices (SAIFI/SAIDI) for the city | Ahmedabad | Gujarat Electricity Regulatory Commission (GERC), Gandhinagar - PIO (Torrent Power itself is private) | Provide copies of the reliability indices (SAIFI, SAIDI, CAIDI) and Standards of Performance compliance reports that Torrent Power Ltd (TPL-D(A)) filed with GERC for FY 2023-24 to FY 2025-26, including any feeder- or area-wise outage data received by the Commission. |
| Official ward boundary GIS files | Surat | Surat Municipal Corporation - Central Town Planning / GIS cell PIO | Provide the current (post-delimitation) boundaries of all SMC wards and zones in digital GIS format (shapefile/KML/GeoJSON), with the ward numbers and names as notified, and the date and reference of the delimitation notification. |
| DGVCL vs Torrent service-area split and outage data within SMC limits | Surat | Dakshin Gujarat Vij Company Ltd (DGVCL), Surat - PIO | List the DGVCL subdivisions and feeders serving areas inside Surat Municipal Corporation limits, and for each feeder give the number and total duration of unscheduled interruptions per month from April 2025 to August 2026. |
| Current taluka-wise daily rainfall (SEOC) archive | Both | Revenue Department, Relief Commissioner / State Emergency Operation Centre, Gandhinagar - PIO | Provide the SEOC daily taluka-wise rainfall reports (mm, 24-hour and cumulative) for all talukas of Surat and Ahmedabad districts from 1 June 2024 to 30 September 2026, in the original digital format (Excel/CSV) in which they are compiled. |

## Challenges

- The upstream geo file uses pre-2013 Gujarat (26 districts, no Botad or Tapi-era changes beyond 2007). Its slug is 'ahmadabad', while src/lib/constants/districts.ts uses 'ahmedabad', so an alias or rename is needed or the map will not highlight Ahmedabad.
- Upstream works at district level while civic data is at SMC/AMC corporation level. The Census 2011 Ahmedabad district also includes the Botad-area talukas split off in 2013, so its figures are not comparable with the current district.
- Power is not cleanly RTI-able in either city. Torrent Power is a private licensee in both, so RTI has to go through GERC; Surat is partly covered by DGVCL, a state PSU that does accept RTI.
- Fetching quirks: censusindia.gov.in has an incomplete TLS chain (needs curl -k; WebFetch fails), ahmedabadcity.gov.in needs legacy TLS renegotiation, and the WRD reservoir PDFs are addressed by base64-encoded dates.
- State SEOC rainfall is not published in current machine-readable form (the Relief Commissioner's page files stop in 2023). Surat can use SMC's own page; Ahmedabad would need parsing from the press or an RTI.

## Verifier checks

| Claim | Verdict | Evidence | Correction |
|---|---|---|---|
| SMC rainfallinfo gives 2-hourly Ukai level (337.82 ft on 27/09/2026), and the WRD daily PDF shows Ukai at 83.26% ALERT and Sardar Sarovar at 99.05%. Also, the upstream geo slug is 'ahmadabad' while districts.ts uses 'ahmedabad'. | confirmed | Live rainfallinfo: 27/09/2026 24:00, 337.82 ft, inflow and outflow 6133 cusec. WRD PDF for 27-09-2026: Ukai 83.26% ALERT, but listed under Tapi district (Songadh); Sardar Sarovar 99.05%. Upstream gujarat-districts.json has slug 'ahmadabad'; districts.ts:1155 has lockedDistrict('ahmedabad'). |  |
