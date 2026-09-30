# Health, sanitation and environment

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

- **Researcher:** Surat 5, Ahmedabad 5
- **After verification:** Surat 6.5, Ahmedabad 4.5

**Researcher's rationale:** Mostly a tie. National datasets (NFHS-5 CSV, SS, EoLI/MPI, CPCB API) cover both cities equally. Neither corporation publishes current disease, water or SWM statistics. Ahmedabad has slightly more city data in practice (2018-20 station AQ PDF, regular VBD figures in the press). Surat's portal is far easier to scrape and has a richer air-quality planning section. In both cities, most dashboard metrics for this area will need RTI.

**Verifier's reasoning:** The claims that neither city has data were wrong for Surat. SMC publishes monthly SWM tonnage up to Jul 2026 and monthly disease cases and deaths for 1995-2022 in HTML. AMC has neither; its only city data is the 2018-20 air-quality PDF plus press figures. SS, EoLI and NFHS rankings are the same for both.

## City-by-city comparison

| Metric | Surat | Ahmedabad | Edge |
|---|---|---|---|
| NFHS-5 district health/sanitation indicators | Surat district, ~104 indicators, CSV mirror verified; district includes rural talukas | Ahmedabad district, ~104 indicators, same CSV; district includes rural talukas | Tie |
| Swachh Survekshan 2024-25 | #2 in Super Swachh League, a separate league for past toppers | #1 cleanest city in the 10 lakh+ category | Tie |
| Ease of Living Index 2020 (million+) | Rank 5 | Rank 3 | Ahmedabad |
| Municipal Performance Index 2020 (million+) | Rank 2 | Not in top 3 (exact rank not verified) | Surat |
| Vector-borne disease stats | Not on SMC portal (VBDC page is descriptive only); news only | Not on portal (malaria-dept file 404), but AMC figures regularly appear in news with cumulative counts | Ahmedabad |
| Municipal air-quality data | AQM Cell page lists stations (2 SMC sensors, 7 GPCB manual, 7 CAAQMS planned) plus NCAP plans; no readings | Station-wise PM10/PM2.5/NOx annual averages in a text PDF, 2018-2020 (stale) | Ahmedabad |
| Real-time AQI via CPCB/data.gov.in | Same national API; station count unverified | Same national API; station count unverified | Tie |
| Water supply / SWM statistics | Only historical hydraulic narrative; SWM portal behind login/500 | Not located on portal within budget | Tie |
| Portal accessibility for scraping | Fetches cleanly with plain curl | Needs legacy TLS renegotiation; dead file links | Surat |

## All sources found

| Metric | City | Source | URL | Format | Granularity | Latest period | Ease (0-5) | Fetched live | Access notes |
|---|---|---|---|---|---|---|---|---|---|
| NFHS-5 (2019-21) district indicators (nutrition, anaemia, sanitation, clean fuel, immunisation) | Both | NFHS-5 district CSV mirror (pratapvardhan/NFHS-5, DOI 10.7910/DVN/42WNZF) | https://raw.githubusercontent.com/pratapvardhan/NFHS-5/master/NFHS-5-Districts.csv | CSV (long: State, District, Indicator, NFHS-5, NFHS-4) | District (Ahmedabad and Surat districts, ~104 indicator rows each) | 2019-21 | 4 | yes | Downloaded this session; 35,464 rows; both districts present with NFHS-4 comparison. Survey is 5+ yrs old and district-level (includes rural talukas), not SMC/AMC city limits. |
| NFHS-5 district factsheets (canonical) | Both | Harvard Dataverse NFHS-5 dataset / rchiips.org district PDFs | https://doi.org/10.7910/DVN/42WNZF | CSV/PDF | District | 2019-21 | 4 | no | Not fetched. Guessed rchiips PDF path (NFHS-5_FCTS/GJ/Surat.pdf) returned 404, so use the CSV mirror. |
| Swachh Survekshan 2024-25 ranks | Both | PIB: President confers Swachh Survekshan 2024-25 awards | https://www.pib.gov.in/PressReleasePage.aspx?PRID=2145461&reg=48&lang=2 | HTML press release | City (ULB) | 2024-25 (announced Jul 2025) | 3 | no | Seen in search only. Ahmedabad was #1 cleanest city with 10 lakh+ population; Surat was #2 in the new Super Swachh League, behind Indore. Component scores sit on the SS portal (not checked). |
| Ease of Living Index 2020 & Municipal Performance Index 2020 | Both | PIB release: EoLI 2020 / MPI 2020 results | https://www.pib.gov.in/PressReleasePage.aspx?PRID=1702417&reg=48&lang=2 | HTML press release (full reports as PDF) | City | 2020 | 3 | no | Seen in search only. EoLI million+: Ahmedabad #3, Surat #5. MPI million+: Surat #2; Ahmedabad not in the top 3. Stale (2020) and no newer edition was found. |
| Air-quality monitoring network (CAAQMS / manual stations) | Surat | SMC Air Quality Management Cell - CAAQMS page | https://www.suratmunicipal.gov.in/Departments/CAAQMS | HTML text + images | City (station list only) | undated | 2 | yes | Lists 2 SMC sensor-based stations (Varachha, Limbayat), 7 GPCB manual stations, and 7 planned CAAQMS (4 SMC + 3 GPCB, NCAP). No readings or download. The AQM Cell also links NCAP, Clean Air Action Plan and a TERI source-apportionment study. |
| Ambient air quality annual averages by station (PM10, PM2.5, NOx) | Ahmedabad | AMC 'Air Quality Data 2018 to 2020' PDF | https://ahmedabadcity.gov.in/Uploads/FileRepository/Air%20Quality%20Data_2018%20to%202020_daf55ae5-dccc-490d-bdf3-97b2f3d46a02.pdf | Text PDF (482 KB) | Station (e.g. SP Stadium, Pirana, Rakhiyal, Raikhad, Chandkheda) | 2018-2020 | 3 | yes | Fetched with the legacy-TLS config. pdftotext extracts it cleanly (2018 Pirana PM10 182.4, PM2.5 100.7). Stale, with nothing after 2020. |
| Real-time AQI (CPCB CAAQMS feed) | National | data.gov.in Real-time Air Quality Index API (resource 3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69) | https://www.data.gov.in/resource/real-time-air-quality-index-various-locations | JSON/CSV API (needs a free API key) | Station, hourly | live (per catalog) | 4 | no | From this environment the API timed out after 30s and the catalog page returned 403. Check from a browser or server before relying on it. Station counts for Ahmedabad and Surat are not confirmed. |
| Vector-borne disease cases (dengue, malaria, chikungunya) | Surat | SMC Vector Borne Diseases Control Department page | https://www.suratmunicipal.gov.in/Departments/VectorBorneDiseasesControlHome | HTML (descriptive text) | none | n/a | 1 | yes | Describes the department only. No case counts, weekly bulletins or downloads. Surat case numbers appear only in Gujarati news. |
| Vector-borne disease cases | Ahmedabad | AMC Health & Wellness page (Malaria Dept info file) | https://ahmedabadcity.gov.in/Home/Healthwellness | HTML + links | none | n/a | 1 | yes | Page loads. Its linked 'Information_Of_Health_Malaria_Department...7z' returns 404. Also links old TB/DOTS PDFs, the UHC list and municipal hospitals. |
| Vector-borne disease cases (press-reported AMC figures) | Ahmedabad | Gujarat Samachar: AMC dengue/malaria Sept 2026 report | https://www.gujaratsamachar.com/news/ahmedabad/amc-dengue-malaria-cases-september-2026-health-report-76778876680 | News (Gujarati/English) | City, monthly/cumulative | Jan-20 Sep 2026 | 1 | no | Search snippet only: 1,084 dengue and 386 malaria cases Jan-20 Sep 2026, citing AMC data. AMC appears to brief the press regularly, but not on its portal. |
| Water supply capacity / history | Surat | SMC Hydraulic Department page | https://www.suratmunicipal.gov.in/Departments/HydraulicHome | HTML text + chart images (JPG) | City | narrative to ~2010 | 3 | yes | Historical narrative (e.g. 440 MLD / 150 lpcd by 2001), with charts as images only. No current MLD, LPCD, NRW or water-quality tables. |
| Solid waste management operations | Surat | SMC SWM portal (linked from SWM dept page) | http://swm.suratmunicipal.org | Web app | unknown | unknown | 2 | no | Redirects to /Login/Login and then returns HTTP 500. No public SWM tonnage data found on the SMC SWM dept page. |
| State air-quality monitoring programme (NAMP/SAMP locations) | Gujarat-state | GPCB Ambient Air Quality Monitoring Programmes | https://gpcb.gujarat.gov.in/webcontroller/page/ambient-air-quality-monitoring-programmes | HTML | Station | unknown | 3 | no | Seen in search only; covers 62 locations statewide, including Ahmedabad and Surat. Not fetched. |

## Data gaps: candidates for RTI

| Metric | City | Public authority | RTI question |
|---|---|---|---|
| Ward-wise weekly dengue/malaria/chikungunya cases | Surat | Surat Municipal Corporation - PIO, Vector Borne Diseases Control Department (HQ level) | Provide ward-wise and week-wise counts of confirmed dengue, malaria and chikungunya cases, plus deaths, from 1 Jan 2024 to date, in Excel/CSV if held electronically, and the number of breeding-site notices and penalties issued per zone in the same period. |
| Ward-wise weekly vector-borne and water-borne disease cases | Ahmedabad | Amdavad Municipal Corporation - PIO, Health (Malaria/Epidemic) Department | Provide ward-wise, week-wise confirmed cases of dengue, malaria, chikungunya, typhoid, jaundice/hepatitis and cholera from 1 Jan 2024 to date, and the number of water samples found unfit per ward, in electronic spreadsheet form. |
| Solid waste generation, collection and processing | Surat | Surat Municipal Corporation - PIO, Solid Waste Management Department | For each month since April 2023, provide zone-wise waste generated and collected (TPD), percentage of households covered by door-to-door collection, percentage segregated at source, tonnage processed by type (compost/RDF/landfill), and legacy waste remediated. |
| Water supply service levels | Ahmedabad | Amdavad Municipal Corporation - PIO, Water Projects / Water Operations Department | Provide ward-wise daily water supplied (MLD), hours of supply, LPCD, households with metered connections, estimated non-revenue water % for FY2023-24 and FY2024-25, and results of residual-chlorine/bacteriological tests by ward. |
| Ambient air-quality readings after 2020 | Ahmedabad | Amdavad Municipal Corporation - PIO, Environment/Air Quality cell (or Gujarat Pollution Control Board PIO, Ahmedabad regional office) | Provide the list of all CAAQMS and manual monitoring stations within AMC limits with commissioning dates, and daily average PM10, PM2.5, NO2 and SO2 per station from Jan 2021 to date, in CSV/Excel. |
| Swachh Survekshan 2024-25 component-wise scores and submissions | Surat | Surat Municipal Corporation - PIO, Solid Waste Management Department (SS nodal officer) | Provide the component-wise marks received by SMC in Swachh Survekshan 2023 and 2024-25 (service-level progress, certification, citizen voice), and copies of the ODF/GFC certification documents submitted to MoHUA. |

## Challenges

- NFHS-5 is district-level and from 2019-21, while the SMC/AMC city limits are smaller. Label it 'district', not 'city', or the dashboard will mislead.
- Swachh Survekshan 2024-25 put Surat in the Super Swachh League, so its rank cannot be compared directly with Ahmedabad's #1 in the 10 lakh+ category. Show league and category next to the rank.
- The data.gov.in real-time AQI API timed out and the catalog returned 403 from this environment. Station counts per city are still unverified, so the live AQI feed needs testing from a normal network before being planned in.
- Neither corporation publishes disease surveillance on its portal. AMC figures surface in (often Gujarati) news; the SMC VBDC page has no data. Ongoing VBD tiles would depend on RTI or scraping news.
- AMC portal needs legacy TLS and has dead links (malaria .7z 404). The SMC SWM portal redirects to login and errors. Municipal water/SWM service-level stats are missing in both cities.

## Verifier checks

| Claim | Verdict | Evidence | Correction |
|---|---|---|---|
| The SMC VBDC page has no case counts, and neither corporation publishes disease surveillance on its portal. | refuted | Live SMC /Departments/HealthDepartmentDiseaseReports (200) has 7 HTML tables of monthly cases and deaths for gastroenteritis, enteric fever, pulmonary TB, malaria (slides, Pv/Pf), pneumonia, hepatitis and cholera, from 1995 to 2022. There is also a VBDC_Annual_Report.pdf (24 pages, 2019). | Surat has a city-level disease time series in HTML up to 2022 (stale, ease 3). Nothing like it was found for AMC. |
| No public SWM tonnage on the SMC site, so water/SWM statistics are a Tie. | refuted | Live SMC /Departments/SolidWasteManagementStatistics (200) has 8 monthly HTML tables. Door-to-door collection for July-2026 was 678 vehicles, 1,555 trips and 2,440.77 MT/day, with a series back to 2019. AMC's /StaticPage/solid_waste_mgmt has no tables or tonnage. | Surat edge: monthly MSW collection by mode up to Jul 2026 in scrapeable HTML (ease 4). |
| Swachh Survekshan 2024-25: Ahmedabad #1 cleanest city with 10 lakh+ population; Surat #2 in the Super Swachh League. EoLI 2020: Ahmedabad 3, Surat 5; MPI 2020: Surat 2. | confirmed | Search results from several outlets (PIB PRID 2145461, DeshGujarat, DD News, ThePrint) agree on SS 2024-25. PIB PRID 1702417 gives EoLI million+ as Bengaluru, Pune, Ahmedabad, Chennai, Surat, and MPI as Indore, Surat, Bhopal. The PIB pages were not fetched. |  |
