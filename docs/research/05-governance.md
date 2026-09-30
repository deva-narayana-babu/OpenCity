# Civic governance, open data, safety, courts, transport

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

- **Researcher:** Surat 5.5, Ahmedabad 5.5
- **After verification:** Surat 6, Ahmedabad 5.5

**Researcher's rationale:** Mixed. Ahmedabad wins on ready-made ward GeoJSON and a current (2026-31) councillor list with party and phone. Surat wins on clean English HTML, a single court district and an easy-to-fetch site. Both have hollow Smart City portals, identical NCRB coverage, no public GTFS and no grievance statistics.

**Verifier's reasoning:** SMC's English corporator list is confirmed to be the current 2026-31 term. AMC's Statistical Outline stops at 2006-07. Ahmedabad keeps the edge on ward GeoJSON (datameet has no Surat folder) and on party and phone data.

## City-by-city comparison

| Metric | Surat | Ahmedabad | Edge |
|---|---|---|---|
| Ward boundary GeoJSON | None on datameet. SMC GIS has an 'Election Ward Boundary' layer but no export found | datameet Wards.geojson, 48 features, matching the current 48 wards | Ahmedabad |
| Wards / seats | 30 wards x 4 = 120 corporators | 48 wards x 4 = 192 councillors | Tie |
| Corporator list usability | English HTML, ward-wise, easy to scrape; term undated | Current 2026-31 PDF with party + phone, but Gujarati text garbles on extraction | Surat |
| Smart Cities open data portal | Catalogs exist (2019) but show no resources | City page 404; nothing usable found | Tie |
| NCRB metro crime tables | One of the 19 metros | One of the 19 metros | Tie |
| Court pendency (NJDG) | Captcha/403 dashboard; single Surat district | Same dashboard. Ahmedabad court data may be split across city and rural establishments | Surat |
| Grievance statistics | Login portal, no stats | CCRS portal live, no public stats | Tie |
| Transit GTFS / ridership | No public GTFS; real-time feed goes only to Google Maps | No public GTFS. Amdavad One portal live. More systems (AMTS, Janmarg, metro) to cover | Tie |
| Site access | Fetches cleanly | Needs a legacy-TLS workaround | Surat |

## All sources found

| Metric | City | Source | URL | Format | Granularity | Latest period | Ease (0-5) | Fetched live | Access notes |
|---|---|---|---|---|---|---|---|---|---|
| Ward boundaries (GeoJSON) | Ahmedabad | datameet Municipal_Spatial_Data / Ahmedabad/Wards.geojson | https://raw.githubusercontent.com/datameet/Municipal_Spatial_Data/master/Ahmedabad/Wards.geojson | GeoJSON (1.2 MB), CC BY-SA 2.5 IN | 48 wards (e.g. '48 RAMOL HATHIJAN'), plus ward/zonal offices, libraries, gyms, pools | 2015-delimitation wards; still match 48-ward 2026-31 council | 4 | yes | Downloaded and parsed: 48 features, property 'Name' only. Scraped from an AMC Google My Map, so no official version; still matches the current 48 wards. |
| Ward boundaries | Surat | datameet Municipal_Spatial_Data (repo root listing) | https://github.com/datameet/Municipal_Spatial_Data | n/a | n/a | n/a | 0 | yes | No Surat folder in repo (GitHub API listing checked). Needs OSM admin_level extraction or scraping SMC GIS. |
| Election/census ward boundary layers | Surat | SMC GIS Portal | https://gis.suratmunicipal.org/ | Web map viewer | Zone, Election Ward, Census Ward, TP scheme, building footprints; imagery 2006-2023 | Imagery to 2023 | 2 | yes | Portal loads and lists 'Election Ward Boundary' layer, but no public WMS/WFS/ArcGIS REST endpoint in page source; export not evident. |
| Corporators by ward | Surat | SMC Ward wise list of Corporators | https://www.suratmunicipal.gov.in/Corporation/Corp_list | HTML (English) | 30 wards x 4 = 120 corporators, ward names, corporator names | Undated on page; term not stated (verify if post-2026 election) | 4 | yes | Clean English HTML, easy to scrape. No party/contact seen in the text we extracted. Page does not state the term. |
| Councillors by ward | Ahmedabad | AMC Councillor's List (term 2026-31) | https://ahmedabadcity.gov.in/ViewFile/ViewFile?TYPE=FileRepository,2638 | PDF, 10 pp, Gujarati (Unicode but broken glyph shaping), 'Print To PDF' | 192 councillors, 48 wards, zone, address, party, phone | Term 2026-31; PDF created 2026-07-30 | 3 | yes | Current and richer than SMC's list (party, phone), but Gujarati PDF extraction garbles conjuncts. Needs manual cleanup or OCR/transliteration. Needs legacy-TLS curl. |
| Smart Cities open data catalogs | Both | Smart Cities Mission Data Portal (smartcities.data.gov.in) | https://smartcities.data.gov.in/catalog/vehicle-registrations-data-surat/ | Catalog pages (JS-rendered) | City catalogs | Surat catalog dated 2019; resources show 'No Result Found', published date NA | 1 | yes | Catalog pages load but list no resources (Surat vehicle-registrations and environment-surat checked). /city/surat and /city/ahmedabad give 404. Effectively hollow for both cities. |
| Crime (IPC/BNS, crimes vs women etc.) metro-city tables | National | NCRB Crime in India 2023 (Vol I) | https://www.ncrb.gov.in/uploads/files/1CrimeinIndia2023PartI.pdf | PDF tables; CSV mirrors on data.opencity.in | Metro city (police commissionerate), annual | 2023 (released 2025) | 4 | no | Both Surat and Ahmedabad are among the 19 metros (confirmed via search). ncrb.gov.in/crime-in-india.html returned HTTP 200. CSV mirror: data.opencity.in/dataset/crime-in-india-2023. |
| Court pendency | National | National Judicial Data Grid (NJDG) | https://njdg.ecourts.gov.in/njdgnew/ | Dashboard, captcha-gated, no export | District / court establishment | Live | 2 | no | Our curl got HTTP 403 (anti-bot). Needs manual browser reads or snapshots. Same difficulty for both cities. |
| Grievances (complaint registration) | Ahmedabad | AMC CCRS (Comprehensive Complaint Redressal System) | https://www.amccrs.com/AMCPortal/Complaint/Register | Web portal (registration/tracking) | Zone/ward/department problem lists | Live 2026 | 1 | yes | Live, with zone-wise ward lists and department-wise problem lists, but no public aggregate statistics (registered/resolved/pending) found. |
| Grievances (complaint registration) | Surat | SMC Online Services / Complaint | https://www.suratmunicipal.gov.in/OnlineServices/ | Login-based citizen portal | Per complaint | Live 2026 | 1 | yes | Login needed to file or track. No published complaint statistics found. |
| Transit (BRTS/AMTS/metro) info | Ahmedabad | Amdavad One (BRTS/AMTS portal linked from AMC) | https://amdavadone.in/ | Web app | Routes/services | Live 2026 | 1 | yes | Loads (13 KB shell). No public GTFS or ridership download found. ahmedabadbrts.org failed to connect. |
| Transit (Sitilink BRTS + city bus) | Surat | SMC Surat Sitilink app page | https://www.suratmunicipal.gov.in/EServices/SuratSitilinkApp | App / web info | Routes; real-time feed shared with Google Maps | Live | 1 | no | Surat supplies real-time transit to Google Maps, so a GTFS/GTFS-RT feed exists internally, but no public download was found. Ridership only in news or budget documents. |
| City statistical outline (civic stats) | Ahmedabad | AMC Statistical Outline | https://ahmedabadcity.gov.in/SP/StatisticalOutline | HTML index of files | City-level annual | References to 2025-26 / 2026-27 | 3 | yes | Page loads with legacy-TLS curl. We did not inspect the content (likely PDFs). Also links Standing/Special committee lists and an air-quality 2018-21 file. |

## Data gaps: candidates for RTI

| Metric | City | Public authority | RTI question |
|---|---|---|---|
| Grievance statistics (registered/resolved/pending, by ward/department, avg resolution time) | Surat | Surat Municipal Corporation, PIO of the Information Technology Dept / complaint cell (HQ level) | Provide month-wise counts of complaints registered, resolved and pending on the SMC complaint system (web, app, helpline) for Apr 2023 to date, broken down by zone, ward and department, with average resolution days, in Excel/CSV. |
| Grievance statistics | Ahmedabad | Amdavad Municipal Corporation, PIO of the CCRS cell / IT Dept (HQ level) | Provide month-wise CCRS complaint counts (registered, resolved, pending beyond SLA) for Apr 2023 to date, by zone, ward and department, with average resolution time, in Excel/CSV. |
| Transit GTFS and ridership | Surat | Surat Municipal Corporation, PIO of the BRTS Cell / Sitilink (Surat Sitilink Ltd) | Provide the current GTFS static feed shared with Google Maps for Sitilink BRTS and city bus, and route-wise daily ridership and fare revenue for FY2023-24 to date, in electronic form. |
| Transit GTFS and ridership | Ahmedabad | Ahmedabad Janmarg Ltd and AMTS, each with its own PIO (AMC subsidiary/undertaking) | Provide the GTFS feed (stops, routes, timetables) for Janmarg BRTS and AMTS, and route-wise monthly ridership, fleet in service and revenue for FY2023-24 to date, as CSV. |
| Official ward boundary shapefile | Surat | Surat Municipal Corporation, PIO of the Election and Census Dept / GIS cell | Provide the current election-ward boundary map for all 30 SMC wards in digital GIS format (shapefile/GeoJSON/KML), as used for the latest general election. |

## Challenges

- City vs district mismatch: NCRB counts police-commissionerate cities, NJDG counts district court establishments (Ahmedabad may be split into city and rural), and SMC/AMC data covers municipal limits. The upstream forthepeople model is district-keyed.
- smartcities.data.gov.in is effectively empty for both cities: catalogs load but list no resources, and the /city pages give 404. Don't plan around it.
- NJDG returns 403 to scripts and is captcha-gated, so court pendency needs manual periodic snapshots.
- AMC's councillor PDF is Gujarati text that garbles on extraction (conjuncts break). Budget time for cleanup or transliteration. The AMC site also needs legacy-TLS workarounds.
- No public GTFS or ridership for Sitilink, Janmarg, AMTS or the metro. Transit metrics will depend on RTI or news. The term of SMC's corporator list is unstated after the 2026 elections, so confirm it is current.

## Verifier checks

| Claim | Verdict | Evidence | Correction |
|---|---|---|---|
| SMC's ward-wise corporator list (30 wards x 4) is undated and may not reflect the 2026 election. | corrected | Live Corp_list lists Ward 1 as Naynaben Dobariya, Bhavishaben Patel, Vijay Bhatiya and Rajendrabhai Patel. These match the SMC General Election 2026 winners in Gujarat Gazette Ex. 357 dated 28-04-2026. There are 30 wards. | The SMC list is the current 2026-31 term. It is in English HTML, but party and phone are not shown. |
| The AMC Statistical Outline is a city-level annual source with references to 2025-26 and 2026-27 (ease 3). | refuted | Live /SP/StatisticalOutline (legacy TLS, 200) lists only 'STATISTICAL OUTLINE FOR 2003-04' and '2006-07'. The recent years seen earlier came from the site navigation, not from outline editions. | The latest edition is 2006-07, stale by 19 years (ease about 2). |
