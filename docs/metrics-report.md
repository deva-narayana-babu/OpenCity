# Metrics report: what OpenCity exposes for Surat

This report covers two things:
- what the OpenCity database holds for Surat;
- how much of a forthepeople.in (ForThePeople) district page it can already fill.

It reflects the database as loaded on 24 October 2026.

- **Per-source documentation** is in [data/export/README.md](../data/export/README.md): publisher, exact URLs, fields, caveats, licence and current health. That file is regenerated on every refresh.
- **The full 319-row comparison** with ForThePeople is in [ftp-coverage.csv](ftp-coverage.csv). Each row has the metric ForThePeople shows, our score before and after this round, the metric ids or record types that back it, and a note.

## Summary

| | Before this round | Now |
|---|---|---|
| Sources | 21 | **43** (39 loading, 4 built but blocked) |
| Metrics declared | 224 | **337** (309 with data) |
| Observations | 26,552 | **35,143** |
| Current records (people, offices, hospitals, tenders, ...) | 472 | **954** across 21 record types |
| Database size | 12.9 MB | 18.3 MB |

Coverage of the 319 metrics ForThePeople shows on a district page:

| | Covered | Partial | Missing | Not applicable |
|---|---|---|---|---|
| Before (21 sources) | 53 | 60 | 180 | 26 |
| **Now (43 sources)** | **73** | **94** | **126** | **26** |

- **Upgrades:** 77 metrics moved up. 21 went from missing to covered, 41 from missing to partial, and 15 from partial to covered.
- **Downgrades:** 17 metrics moved down, because this round scored more strictly than the first gap map:
  - **Seven are mandi prices.** The first map counted them as covered, but Agmarknet has never loaded a row: it now needs a data.gov.in API key.
  - **Nine are budget, RTI and election figures that cover only the SMC area.** Strictly, a city-only answer to a district metric is partial.
  - **One is a crop-price stability score.** It depends on the same mandi prices.
- **Covered and partial together:** 167 of the 293 applicable metrics (57%), up from 113 (39%).

Each score was set by one agent per ForThePeople area. A second agent then tried to refute every change and every "covered" claim against the live database. The checkers confirmed 123 rows and corrected 10, all from covered down to partial. The scale:
- **covered:** the same measure at the same or finer geography and similar recency, with rows in the database now;
- **partial:** a related measure, a coarser or different geography, only older periods, or data that exists only as records the dashboard must count;
- **missing:** nothing loaded. A source that is built but disabled counts as missing;
- **not applicable:** ForThePeople's own editorial or site content.

## What the database exposes, by module

| Module | Sources | Metrics | Metrics with data | Observations | Current records | Latest period |
|---|---|---|---|---|---|---|
| agriculture | 1 | 4 | 4 | 1,450 | 0 | 2026-03-31 |
| alerts | 1 | 1 | 0 | 0 | 0 |  |
| citizen | 1 | 0 | 0 | 0 | 30 |  |
| council | 2 | 9 | 9 | 490 | 135 | 2021-02-21 |
| courts | 2 | 19 | 19 | 428 | 0 | 2026-10-23 |
| education | 2 | 25 | 25 | 620 | 0 | 2026-03-31 |
| environment | 3 | 19 | 19 | 3,501 | 23 | 2026-10-18 |
| finance | 3 | 49 | 49 | 1,231 | 21 | 2026-10-18 |
| food | 2 | 7 | 0 | 0 | 0 |  |
| health | 5 | 33 | 33 | 14,197 | 161 | 2026-09-30 |
| housing | 1 | 2 | 2 | 4 | 57 | 2023-09-12 |
| jobs | 1 | 2 | 2 | 2 | 2 | 2026-10-24 |
| leadership | 2 | 0 | 0 | 0 | 103 |  |
| offices | 2 | 0 | 0 | 0 | 26 |  |
| police | 1 | 4 | 4 | 56 | 0 | 2024-12-31 |
| population | 2 | 46 | 46 | 6,318 | 0 | 2022-12-31 |
| power | 1 | 1 | 1 | 48 | 0 | 2021-02-28 |
| rti | 1 | 50 | 49 | 644 | 20 | 2026-06-30 |
| schemes | 1 | 0 | 0 | 0 | 9 |  |
| tenders | 1 | 2 | 2 | 4 | 140 | 2026-10-24 |
| transport | 2 | 8 | 6 | 6 | 0 | 2026-04-30 |
| water | 4 | 34 | 34 | 5,739 | 227 | 2026-10-24 |
| weather | 2 | 22 | 5 | 405 | 0 | 2026-10-21 |
| **All** | **43** | **337** | **309** | **35,143** | **954** | |

Notes on the modules:
- **Offices, leadership, citizen and schemes** are record-only. They hold named entities with official contacts: 92 SMC officers, 11 Collectorate officers, 9 zone offices, 17 taluka offices, 30 helplines and 9 schemes. They have no numbers.
- **Food** has 7 metrics but no data. Agmarknet needs an API key, and the Department of Consumer Affairs reports need a captcha.
- **Weather** has 17 forecast metrics waiting on the Open-Meteo decision (see below).

## Sources added in this round

| Source | Module | Metrics | Observations | Records | Status |
|---|---|---|---|---|---|
| [census2011_surat](../data/export/README.md#census2011_surat) | population | 31 | 4,905 |  | loaded |
| [smc_vital_stats](../data/export/README.md#smc_vital_stats) | population | 15 | 1,413 |  | loaded |
| [gsdma_rainfall](../data/export/README.md#gsdma_rainfall) | weather | 5 | 405 |  | loaded |
| [openmeteo_surat](../data/export/README.md#openmeteo_surat) | weather | 17 | 0 |  | disabled |
| [ndma_sachet_surat](../data/export/README.md#ndma_sachet_surat) | alerts | 1 | 0 |  | loaded |
| [njdg_surat](../data/export/README.md#njdg_surat) | courts | 16 | 158 |  | loaded |
| [ncrb_metro_surat](../data/export/README.md#ncrb_metro_surat) | police | 4 | 56 |  | loaded |
| [smc_officials](../data/export/README.md#smc_officials) | leadership | 0 | 0 | smc_official (92) | loaded |
| [surat_collectorate](../data/export/README.md#surat_collectorate) | leadership | 0 | 0 | district_official (11) | loaded |
| [smc_zone_offices](../data/export/README.md#smc_zone_offices) | offices | 0 | 0 | smc_zone_office (9) | loaded |
| [smc_helplines](../data/export/README.md#smc_helplines) | citizen | 0 | 0 | smc_helpline (30) | loaded |
| [surat_talukas](../data/export/README.md#surat_talukas) | offices | 0 | 0 | taluka_office (17) | loaded |
| [smc_health_centres](../data/export/README.md#smc_health_centres) | health | 1 | 20 | smc_health_centre (80) | loaded |
| [smc_pmjay_hospitals](../data/export/README.md#smc_pmjay_hospitals) | health | 2 | 23 | pmjay_hospital (81) | loaded |
| [jjm_surat](../data/export/README.md#jjm_surat) | water | 5 | 12 |  | loaded |
| [smc_ucd_schemes](../data/export/README.md#smc_ucd_schemes) | schemes | 0 | 0 | smc_ucd_scheme (9) | loaded |
| [smc_tenders](../data/export/README.md#smc_tenders) | tenders | 2 | 4 | tender (70), tender_notice (70) | loaded |
| [smc_streetlights](../data/export/README.md#smc_streetlights) | power | 1 | 48 |  | loaded |
| [smc_recruitment](../data/export/README.md#smc_recruitment) | jobs | 2 | 2 | recruitment_ad (2) | loaded |
| [aai_surat_airport](../data/export/README.md#aai_surat_airport) | transport | 2 | 0 |  | disabled |
| [smc_past_elections](../data/export/README.md#smc_past_elections) | council | 5 | 95 | municipal_election (11) | loaded |
| [shc_soil_surat](../data/export/README.md#shc_soil_surat) | agriculture | 4 | 1,450 |  | loaded |

Every one of these was built by one agent and checked by a second. The checker re-read the adapter, ran the tests, ran one live refresh, and compared at least six stored values against the archived source document. 394 offline tests pass.

What they add, in short:

- **Population.** Census 2011 for the district and its 10 sub-districts: population by sex, age 0-6, SC/ST, literacy, workers, area, and houselisting amenities such as water source, latrine, lighting, cooking fuel, assets and banking. SMC's birth and death registers add births by month and sex, deaths, infant and maternal mortality, and crude birth and death rates, from 1991 to 2022.
- **Courts.** NJDG pendency for the Surat district courts: pending cases by age, case type, stage and filing year, plus cases instituted and disposed each year since 2018. This lifts the courts module from 1 covered metric to 8.
- **Leadership and offices.** The Collector and Collectorate officers, SMC's Commissioner, deputies and department heads, zone offices, taluka offices and SMC helplines, with official contacts only.
- **Health.** SMC's 80 urban health centres and 81 PM-JAY empanelled hospitals, with their specialities.
- **Water.** Jal Jeevan Mission: rural household tap connections for Surat (100%), with the 2019 baseline.
- **Weather and alerts.** GSDMA taluka rainfall against the 30-year average. NDMA SACHET official alerts, which is enabled but has had no Surat alert yet.
- **Police.** NCRB *Crime in India* tables for Surat metropolitan city: crimes registered, crime rate per lakh and charge-sheeting rate, up to 2024.
- **Economy and services.** All 70 open SMC tenders, with estimate, EMD and closing dates. SMC recruitment ads. Streetlight outage percentages for 2017 to 2021. SMC's community-development schemes.
- **Elections.** 11 SMC elections from 1969 to 2021: wards, seats, reserved seats and voters.
- **Farming.** Soil Health Card results by taluka and nutrient class for four cycles, 2023-24 to 2026-27.

## Coverage of ForThePeople's district modules

C / P / M / NA = covered / partial / missing / not applicable.

| ForThePeople module | Metrics | Before (C / P / M / NA) | After (C / P / M / NA) |
|---|---|---|---|
| overview | 20 | 2 / 5 / 9 / 4 | 4 / 6 / 6 / 4 |
| overview: district health score (report card) | 30 | 8 / 6 / 13 / 3 | 9 / 8 / 10 / 3 |
| map | 8 | 0 / 2 / 6 / 0 | 2 / 2 / 4 / 0 |
| water (dams and rivers) | 12 | 11 / 1 / 0 / 0 | 11 / 1 / 0 / 0 |
| crops (mandi prices) + national prices route | 8 | 5 / 1 / 0 / 2 | 0 / 0 / 6 / 2 |
| weather (weather + rainfall + forecast) | 11 | 0 / 5 / 6 / 0 | 0 / 5 / 6 / 0 |
| farm (soil health + agri advisories) | 4 | 0 / 0 / 4 / 0 | 0 / 2 / 2 / 0 |
| finance (budget + revenue) | 10 | 4 / 4 / 0 / 2 | 1 / 7 / 0 / 2 |
| leadership (leaders, leader-news) | 10 | 0 / 3 / 6 / 1 | 1 / 3 / 5 / 1 |
| police (crime and traffic) | 8 | 0 / 0 / 7 / 1 | 1 / 2 / 4 / 1 |
| courts (court-pendency) | 12 | 1 / 3 / 7 / 1 | 8 / 1 / 2 / 1 |
| rti | 7 | 4 / 1 / 2 / 0 | 1 / 4 / 2 / 0 |
| elections (election-events) | 7 | 1 / 0 / 5 / 1 | 0 / 2 / 4 / 1 |
| schools | 15 | 9 / 3 / 2 / 1 | 9 / 3 / 2 / 1 |
| health | 6 | 1 / 0 / 3 / 2 | 1 / 2 / 1 / 2 |
| population | 20 | 0 / 6 / 14 / 0 | 11 / 2 / 7 / 0 |
| gram-panchayat | 11 | 1 / 0 / 10 / 0 | 1 / 1 / 9 / 0 |
| housing | 4 | 0 / 2 / 1 / 1 | 0 / 2 / 1 / 1 |
| jjm | 6 | 0 / 1 / 4 / 1 | 4 / 1 / 0 / 1 |
| schemes (incl. /api/data/scheme-coverage) | 9 | 0 / 1 / 6 / 2 | 0 / 5 / 2 / 2 |
| services | 7 | 0 / 0 / 7 / 0 | 1 / 0 / 6 / 0 |
| transport | 10 | 1 / 1 / 8 / 0 | 1 / 1 / 8 / 0 |
| power | 7 | 0 / 0 / 7 / 0 | 1 / 0 / 6 / 0 |
| offices | 6 | 0 / 1 / 5 / 0 | 0 / 5 / 1 / 0 |
| alerts | 7 | 0 / 1 / 6 / 0 | 0 / 2 / 5 / 0 |
| industries (factories + local-industries) | 8 | 0 / 0 / 8 / 0 | 0 / 0 / 8 / 0 |
| infrastructure (projects being built + infra-analysis) | 9 | 0 / 5 / 3 / 1 | 0 / 5 / 3 / 1 |
| tenders | 8 | 0 / 1 / 7 / 0 | 0 / 7 / 1 / 0 |
| exams (exams & jobs) | 8 | 1 / 0 / 7 / 0 | 1 / 5 / 2 / 0 |
| news | 5 | 0 / 0 / 4 / 1 | 0 / 0 / 4 / 1 |
| famous-personalities | 3 | 0 / 0 / 3 / 0 | 0 / 0 / 3 / 0 |
| citizen-corner (helplines & your rights, tips) | 4 | 0 / 0 / 2 / 2 | 0 / 1 / 1 / 2 |
| responsibility (what you can do) | 4 | 0 / 1 / 3 / 0 | 0 / 3 / 1 / 0 |
| data-sources | 6 | 3 / 3 / 0 / 0 | 4 / 2 / 0 / 0 |
| update-log | 3 | 1 / 2 / 0 / 0 | 1 / 2 / 0 / 0 |
| [taluk] pages (taluk and village) | 6 | 0 / 1 / 5 / 0 | 0 / 2 / 4 / 0 |
| **All modules** | **319** | **53 / 60 / 180 / 26** | **73 / 94 / 126 / 26** |

The biggest gains:
- **courts:** 1 to 8 covered;
- **population:** 0 to 11 covered;
- **JJM:** 0 to 4 covered;
- **tenders, exams and jobs, schemes, offices:** most of their metrics moved from missing to partial.

**Mandi prices** (crops) went from 5 covered to none, because the adapter has never loaded a row. One API key restores all of them.

<details><summary>What we now hold for each ForThePeople module (the scorers' notes)</summary>

- **overview.** Census 2011 district rows now fully cover population, literacy and sex ratio, and surat.nic.in now gives the Collector and the official 17-taluka list. After: 4 covered, 6 partial, 6 missing, 4 not applicable (the taluk count stays partial, because it is counted from records). Budget, leaders, election and tenders stay partial because they are SMC-only or incomplete; the budget card is downgraded from covered under the geography rule. The main gaps: the weather tile (Open-Meteo built, disabled by robots.txt), the mandi line (Agmarknet built, disabled for lack of an API key, downgraded from covered), active alerts (SACHET runs but has stored 0 rows), MPs and infrastructure projects.
- **overview: district health score (report card).** After: 9 covered, 8 partial, 10 missing, 3 not-applicable (before: 8 / 6 / 13 / 3). New coverage: Census 2011 literacy, JJM tap coverage, NCRB metro-city crime rate (partial), SMC health centres (partial) and Soil Health Card sample counts (partial). Two scores went down: RTI response rate becomes partial because it covers only SMC, and crop price stability becomes missing because Agmarknet has no rows. The overall composite itself is still not computed, and lapsed funds, power outages, police stations, industries, advisories and scheme beneficiaries are all missing.
- **map.** Census 2011 now covers district area (4,549 sq km) and population (60.81 lakh), and the official surat.nic.in list gives the taluka count, but only as records to count, so that tile is partial. Everything per taluka beyond its name is missing: population, area, villages, village names, land share and boundary polygons. The reason: the Census DCHB cannot be fetched (TLS certificate error) and no OSM boundary adapter was built.
- **water (dams and rivers).** Every dam metric is covered: WRD gives daily figures for 5 dams plus district and state rows, and SMC gives Ukai every 2 hours. History is still short (3 daily readings per dam, 2026-10-15 to 2026-10-17). Canal releases stay partial: we have the canal outflow amount but no names, schedules or command areas.
- **crops (mandi prices) + national prices route.** All six mandi metrics are now missing. agmarknet_surat is built but disabled (it needs DATA_GOV_IN_API_KEY because the old endpoint is captcha-gated) and has 0 rows. The before map's covered scores counted that empty adapter and a geo level that does not exist, so they were wrong. The two national price rows stay not-applicable.
- **weather (weather + rainfall + forecast).** We hold only one SMC sensor reading of temperature and humidity, SMC zone rain every 2 hours, and the new GSDMA daily season rainfall vs the 1996-2025 average for the district and its talukas (partial, since FTP shows monthly figures). Forecast, feels-like, wind, conditions, pressure and visibility are missing: openmeteo_surat is built but disabled by a robots.txt disallow.
- **farm (soil health + agri advisories).** Soil Health Card class counts of samples (pH, N, P, K, OC, EC, micronutrients) for 10 blocks and the district, 2023-24 to 2026-27, now give partial soil coverage. There are no per-village results or recommendations. Agri advisories are fully missing, with no IMD agromet or KVK source.
- **finance (budget + revenue).** We hold SMC's weekly zone-wise budget vs actuals (original and revised budget, tentative and year-to-date actuals, FY2024-25 to FY2026-27), 20 years of audited balance sheets and I&E accounts, and CityFinance's standard heads (FY2015-16 to FY2023-24). That covers totals, spending and utilisation for SMC. No finance source was added since the before map, so sector- and department-wise allocations, monthly revenue by category against target, the central/state grant split and the Surat District Panchayat budget are still gaps.
- **leadership (leaders, leader-news).** smc_officials (92 officers, including the Municipal Commissioner and 7 Deputy Municipal Commissioners) and the smc_council office bearers now cover tier 5 fully. surat_collectorate (11 posts) gives the Collector and Prant officers, a partial tier 3. Still missing: tiers 2, 4 and 6 (state leaders, MP/MLAs, judges), the DDO, Police Commissioner and SP, party affiliation, photos, term-start dates and leader news.
- **police (crime and traffic).** ncrb_metro_surat adds NCRB Crime in India 2024 for Surat metropolitan city: cases in 10 crime groups for 2022-2024, and crime and chargesheeting rates for 2024. It covers only the city police area, not Surat Rural, so the district crime chart is partial. Police stations, traffic fines and staffing are still missing.
- **courts (court-pendency).** njdg_surat fills the pendency gap for Surat district: civil/criminal pending, 5 age bands, last-month filings and disposals (contested/uncontested), cases filed by women and senior citizens, and yearly flows 2018-2026. It sits alongside the per-establishment Justice Clock. Still missing: how long decided cases took, the Gujarat High Court card, and a direct 7-band age split, which can only be derived from filing years with inferred band boundaries.
- **rti.** smc_rti treats SMC as one public authority: annual returns (15 readable years to FY2025-26) and quarterly Patrak-7/8 (only Q1 FY2026-27 loaded). It covers filed, disposed, pending, appeals, exemptions and fees. No RTI source was added, so the per-department breakdown, average reply days and a PIO directory are still gaps.
- **elections (election-events).** smc_council (2021 ward voters, seats and reservation) and the new smc_past_elections (11 SMC elections, 1969-2021) cover municipal voter registration and give a partial election calendar. Results, turnout, seats by party, polling booths and anything for the Assembly or Lok Sabha are still missing. SMC's page does not list the April 2026 election yet.
- **schools.** UDISE+ covers all nine headline metrics for the whole Surat district, for 2024-25 and 2025-26: schools, students and teachers, splits by management and stage, PTR and facilities. GSEB gives district and exam-centre board results (2024-2026) in place of per-school results. The gaps are a school directory (UDISE+ is behind a captcha) and teacher post sanctioned/vacant figures. Score: 9 covered, 3 partial, 2 missing, 1 n/a.
- **health.** smc_health_centres (80 UHC/UCHC by zone, SMC city) and smc_pmjay_hospitals (81 empanelled hospitals, district, mid-2024) move the facility count and directory from missing to partial. Our own health statistics go well beyond FTP's (disease, VBDC, SMIMER, NFHS, vital rates). The gaps are rural district facilities (PHC/CHC/sub-centres), opening hours, map points, and any health staffing source.
- **population.** census2011_surat loads the full PCA and HLPCA for Surat district (2011 boundaries), so 11 of 20 metrics are now covered: population, sex, ratios, literacy, urban/rural, area, households, workers, SC/ST and amenities. Ratios are computed from the stored counts. Age bands (only 0-6) and the census-year trend (only 2011 at district level, plus SMC-city estimates) are partial. Median age, education level, mother tongue, migration, religion, MPI and village rows are still missing, because the Census C/D tables and NITI MPI were not built.
- **gram-panchayat.** No MGNREGA adapter was built, so all nine NREGASoft metrics and the per-panchayat rows are still missing. Only a taluka count from the Mamlatdar office records (11 rural revenue talukas, which are not exactly MGNREGA blocks, and no GP count) is partial. The urban fallback is covered by the council and SMC official records.
- **housing.** Unchanged since the before map: smc_pmay gives SMC-city PMAY-U AHP project and flat counts by status (page dated 2023-09-12), so houses and the completion share are partial. Funds allocated/released/spent, targets, the FY split and rural PMAY-G are missing; the UCD scheme records do not include PMAY.
- **jjm.** jjm_surat now loads the same JJM IMIS district figures FTP uses: rural households, households with a tap, coverage % and the 15 Aug 2019 baseline, so 4 metrics are covered (Surat 383,576 / 383,576, 100%, as on 2026-10-24). Per-village or taluk water-test rows are still only partially answered, by SMC's urban zone-level tap tests.
- **schemes (incl. /api/data/scheme-coverage).** We now hold 9 SMC Urban Community Development scheme records (DAY-NULM components, PM SVANidhi, MMUY) in Gujarati, for SMC city, last edited Dec 2021. That gives partial counts, kinds, amounts and cards. Reach numbers exist only for PMAY-U (SMC, 2023) and JJM rural tap connections (district, Oct 2026). Main gap: no district-wide central/state catalogue with level and apply links, and benefit amounts are untranslated free text.
- **services.** No service-guide source was built: smc_online_services was never written. All six guide metrics (counts, online, free, offices, cards, charts) stay missing. The related vital-registration card is now covered by smc_vital_stats (SMC city, annual 2001-2021, monthly births to Oct 2022). Registration fees are described in the adapter but not stored.
- **transport.** Only SMC e-bus operations are loaded: 6 metrics, one reading dated 30 Apr 2026, SMC city. They cover our own e-bus row and stand in for the route count via fleet size. No source exists for bus routes, operators, fares or train timetables. The AAI airport-passenger adapter is built but disabled because AAI's PDFs sit behind an email-OTP download form.
- **power.** No DGVCL or Torrent Power outage notices are collected, so all six outage metrics remain missing. The related non-working streetlights % is now loaded in full (SMC city, monthly Mar 2017 to Feb 2021). That series stopped in 2021 and is street-lighting data, not power-supply data.
- **offices.** Office directories are now loaded as records: 9 SMC zone offices, 17 Mamlatdar offices and 11 Collectorate/Prant posts with addresses, phones and government emails, plus 92 SMC officers and the elected office bearers. These give partial counts, department splits, contact reach, office cards and head-of-office names. Gaps: only revenue and SMC offices; no lat/long, hours, websites or services; no Gujarat office-hours rule; no names for Mamlatdars or zone chiefs.
- **alerts.** ndma_sachet_surat is built, enabled and fetched the SACHET feed successfully on 24 Oct 2026. No alert covered Surat, so there are 0 alert rows and all five warning metrics stay missing until one arrives. Flood-risk indicators stay partial: Ukai, weir and creek levels, WRD warning levels and GSDMA taluka rain are loaded, but the latest readings are 17-21 Oct. Emergency numbers are now partial: 30 SMC helpline records hold 101 and 102 and the control rooms, but not 112 or 1077.
- **industries (factories + local-industries).** Nothing is loaded. None of the 22 new sources covers industrial estates, parks, tourism places or sugar mills, so all 8 metrics stay missing. The main gap is an official list of Surat's GIDC estates, SEZs and textile and diamond clusters. The Udyam MSME count is the nearest district-level figure, but it needs a data.gov.in API key.
- **infrastructure (projects being built + infra-analysis).** Unchanged at partial. The only project list is SMC's 57 PMAY housing projects, with status, tender amount, contractor and location. smc_tenders adds estimates and zones for works now being tendered, but that is procurement, not construction progress. There are still no project dates, progress %, delays, cancellations or news timeline.
- **tenders.** smc_tenders moves this module from missing to mostly partial. It gives 70 live SMC tenders with notice details (estimate, EMD, fee, dates, prebid, authority, zone) and daily counts of active tenders and tenders closing within 2, 7 and 14 days. Gaps: it covers SMC only, with no district bodies on Gujarat nProcure; value sums and red flags must be computed from the records; there is no MSE flag or work category; and award and winner data exist only for housing projects.
- **exams (exams & jobs).** smc_recruitment adds SMC's own job ads (2 ads and 26 posts on 2026-10-24) with application windows and notice links, so the open-exam metrics are now partial, and GSEB board results stay covered. National and Gujarat state exams (UPSC, SSC, GPSC, GSSSB) are not collected, and neither is post strength by department, so the organiser chart and the staffing metric stay missing.
- **news.** No news source was built, so every data metric stays missing and the AI summary stays not-applicable. gnews_surat (headline, publisher, date, rule-based topic) blocks this module and also the related-news parts of citizen-corner, responsibility and the infrastructure timeline.
- **famous-personalities.** Nothing is loaded, because wikidata_people_surat (place of birth Surat, CC0) was not built. All three metrics stay missing.
- **citizen-corner (helplines & your rights, tips).** smc_helplines adds 30 official SMC numbers (complaint helpline, WhatsApp, fire, ambulance, hospitals, zone control rooms), so helplines are now partial. They are city municipal lines, not FTP's state and national set, and they carry no 'when to call' guidance. Rights and AI tips stay not-applicable, and related news stays missing without a news source.
- **responsibility (what you can do).** The 'report to' and 'who to call' parts are now partial, backed by smc_helpline, zone-office and Collectorate contact records. The action texts are hand-written and not held, and the news-by-topic ordering stays missing without a news source. OpenCity's own water, waste, air and disease series remain a partial 'why now' substitute.
- **data-sources.** The source table and the generated data/export/README.md now list all 43 sources with publisher, URL, cadence, licence, status, latest period and rows held, so rows per dataset is covered. Two metrics stay partial: there is no max-age rule for an 'N days old' verdict, and the only gaps list is the 4 disabled sources.
- **update-log.** Unchanged at partial. The fetch (468 rows), run and observation_revision (12 rows) tables record what changed and when, all from automatic runs, and source.module and metric.module support the per-module filter. The log is not exported to CSV, and record changes have no per-field diff.
- **[taluk] pages (taluk and village).** surat_talukas gives the official 17-taluka list (geo surat_taluka plus Mamlatdar office records), and gsdma_rainfall, shc_soil_surat and census2011_surat now hold taluka-level data. So the taluk list is partial. Per-taluk data availability is also partial: it covers 12 units, the 11 rural talukas and the old surat_city. Village data and taluka population and area are still missing, because the Census DCHB that holds them cannot be downloaded (incomplete TLS chain), and the six current city talukas get no data because those sources use one 2011 'Surat City' unit.

</details>

## What is still missing, and why

The 126 metrics still missing fall into six groups. The counts are approximate, because a few metrics fit more than one group.

1. **Blocked by the publisher (about 25 metrics).** These sources are built, or nearly built, but cannot load without a decision or an action:
   - **Mandi prices (7):** Agmarknet needs a free data.gov.in API key in `DATA_GOV_IN_API_KEY`. The old endpoint now demands a captcha.
   - **Weather forecast and conditions (7):** `openmeteo_surat` is built and tested, but `api.open-meteo.com/robots.txt` disallows every path. The project rule is to respect robots.txt, so it stays off until the group decides.
   - **Airport passengers (1):** AAI hides its traffic PDFs behind a name, email and OTP form.
   - **School directory (1):** UDISE+ "Know your school" needs a captcha.
   - **Census villages and taluka areas (6):** the Census DCHB files on censusindia.gov.in fail TLS verification. A copy saved by hand could be parsed.
   - **Bus routes:** IUDX Surat transit data needs a login.
2. **Waiting for an event (6 metrics).** The SACHET alerts adapter runs hourly and stores Surat alerts as soon as one is issued. None has covered Surat since it started.
3. **A public source exists, but no adapter has been built yet (about 45 metrics, including 6 on power cuts):**
   - MGNREGA (9 metrics, gram-panchayat module);
   - Census 2011 C-tables: religion, mother tongue, migration, education levels;
   - NITI Aayog MPI;
   - the Gujarat High Court on NJDG, and NJDG's "disposed by time taken" view;
   - MLA and MP lists;
   - the Surat police station directory: an ASP.NET postback form, which is doable but slow;
   - DGVCL and Torrent Power outage notices: DGVCL failed TLS checks;
   - OpenStreetMap taluka boundaries (ODbL);
   - IMD agromet advisories;
   - railway timetables;
   - SMC online services;
   - Udyam MSME counts: this also needs the data.gov.in key.

   The research notes for each of these are in the gap map behind [ftp-coverage.csv](ftp-coverage.csv).
4. **No open source for Surat (about 33 metrics):**
   - lapsed funds;
   - sanctioned vs working posts for teachers, health staff and police;
   - party affiliation of corporators: SMC's lists print no party;
   - voter turnout and results: ECI pages returned 404, and SMC publishes no turnout;
   - project progress, stalled projects and cancellations;
   - aggregate traffic fines: the e-challan site is a per-vehicle lookup and must not be scraped;
   - office hours;
   - industrial estates, sugar mills and their seasons;
   - bus operators and fares;
   - housing funds released and spent;
   - scheme beneficiary counts and online-apply links;
   - median age.

   These are good topics for the **RTI helper**: each is a record the responsible office holds but does not publish.
5. **Editorial or derived on ForThePeople (about 17 metrics):**
   - news feeds, leader news and "famous personalities";
   - the 0-100 report-card score and grade;
   - service guides;
   - charts built from those.

   The score can be computed by the dashboard from metrics we already hold. The rest needs a news or Wikidata source, or hand-written content.
6. **Not applicable (26 metrics):** ForThePeople's own site features, taglines and AI text.

## Caveats for anyone building on this data

- **City vs district.**
  - SMC sources cover the corporation area (about 4.5 million people in 2011).
  - District sources (Census, UDISE+, NFHS-5, courts, JJM, Soil Health Card) cover the whole of Surat district.
  - JJM and Soil Health Card cover only its rural part.

  Never add or compare the two without saying so. Every observation carries its geo level.
- **Talukas.** Census 2011, GSDMA and Soil Health Card keep the city as one `surat_city` taluka, while surat.nic.in now lists six city talukas. The `surat_taluka` level holds both kinds, and they must not be added together.
- **Census 2011 is old.** ForThePeople uses the same year, so it counts as covered, but the dashboard should label it.
- **Records, not totals.** Tender sums, health-centre counts by zone, alert counts and taluka counts are stored as records, or as one row per item. The dashboard counts or sums them, because each source document is parsed on its own.
- **Disabled sources keep working parsers.** A report saved by hand can be parsed, for DoCA prices or AAI traffic. The refresher has no command that loads a local file yet.

## Decisions waiting on the group

1. A free data.gov.in API key (`DATA_GOV_IN_API_KEY`). This restores 7 mandi-price metrics and enables Udyam MSME counts.
2. Whether `openmeteo_surat` may run despite the API host's robots.txt. Its terms allow free non-commercial use under CC-BY 4.0.
3. Whether to install the hourly cron job (`scripts/install-schedule.sh`).
4. Which of the "not built yet" sources in group 3 to do next. MGNREGA and the Census C-tables fill the most ForThePeople metrics.

## Every metric we expose

The tables list every metric in the database, grouped by module:
- **Places:** the geography levels the metric has data for.
- **Periods:** the first and last month with data.
- **Values:** the number of stored observations. "Blank" counts the cells the publisher left empty, which are stored as not reported and never as zero.

The record types each module holds are listed under its table.

### agriculture

| Metric | What it is | Unit | Places | Periods | Values |
|---|---|---|---|---|---|
| `soil.shc_ec_samples` | Soil samples by salinity (EC) class | samples | district, taluka | 2023-04 to 2027-03 | 100 |
| `soil.shc_micronutrient_samples` | Soil samples by micronutrient sufficiency | samples | district, taluka | 2023-04 to 2027-03 | 600 |
| `soil.shc_npk_oc_samples` | Soil samples by N, P, K and organic-carbon class | samples | district, taluka | 2023-04 to 2027-03 | 600 |
| `soil.shc_ph_samples` | Soil samples by pH class | samples | district, taluka | 2023-04 to 2027-03 | 150 |

### alerts

| Metric | What it is | Unit | Places | Periods | Values |
|---|---|---|---|---|---|
| `sachet.alerts` | Official alerts for Surat district (SACHET) | alerts |  |  | 0 |

### citizen


Records: `smc_helpline` (30, from smc_helplines).

### council

| Metric | What it is | Unit | Places | Periods | Values |
|---|---|---|---|---|---|
| `election.seats` | Council seats by reservation category | seats | ward | 2021-01 | 240 |
| `election.voters` | Registered voters | voters | city, ward | 2021-01 | 31 |
| `election.voters_by_gender` | Registered voters by gender | voters | city, ward | 2021-01 | 93 |
| `election.ward_population` | Ward population (Census 2011, election-ward limits) | persons | city, ward | 2011-03 | 31 |
| `election.past_reserved_seats` | Reserved seats (past SMC elections) | seats | city | 1969-06 to 2021-02 | 44 (9 blank) |
| `election.past_reserved_seats_women` | Reserved seats also reserved for women (past SMC elections) | seats | city | 1995-06 to 2021-02 | 18 |
| `election.past_seats` | Council seats (past SMC elections) | seats | city | 1969-06 to 2021-02 | 11 |
| `election.past_voters` | Voters (past SMC elections) | voters | city | 1969-06 to 2021-02 | 11 |
| `election.past_wards` | Election wards (past SMC elections) | wards | city | 1969-06 to 2021-02 | 11 |

Records: `corporator` (120, from smc_council); `municipal_election` (11, from smc_past_elections); `office_bearer` (4, from smc_council).

### courts

| Metric | What it is | Unit | Places | Periods | Values |
|---|---|---|---|---|---|
| `courts.cases_disposed` | Cases disposed | cases | court, district | 2026-10 | 90 |
| `courts.cases_instituted` | Cases instituted | cases | court, district | 2026-10 | 90 |
| `courts.clearance_rate_pct` | Case clearance rate | % | court, district | 2026-10 | 90 (21 blank) |
| `njdg.cases_listed_today` | Pending cases listed today (NJDG) | cases | district | 2026-10 | 3 |
| `njdg.disposed_by_year` | Cases disposed per year (NJDG) | cases | district | 2018-01 to 2026-12 | 9 |
| `njdg.disposed_last_month` | Cases disposed in the last month (NJDG) | cases | district | 2026-10 | 9 |
| `njdg.excessive_dated_cases` | Pending cases with a next date over 3 months away (NJDG) | cases | district | 2026-10 | 3 |
| `njdg.instituted_by_year` | Cases instituted per year (NJDG) | cases | district | 2018-01 to 2026-12 | 9 |
| `njdg.instituted_last_month` | Cases instituted in the last month (NJDG) | cases | district | 2026-10 | 3 |
| `njdg.pending_by_age` | Pending cases by age (NJDG) | cases | district | 2026-10 | 15 |
| `njdg.pending_by_case_category` | Pending cases by case category (NJDG) | cases | district | 2026-10 | 4 |
| `njdg.pending_by_case_type` | Pending cases by case type (NJDG) | cases | district | 2026-10 | 22 |
| `njdg.pending_by_filing_year` | Pending cases by year of institution (NJDG) | cases | district | 2026-10 | 39 |
| `njdg.pending_by_stage` | Pending cases by stage (NJDG) | cases | district | 2026-10 | 26 |
| `njdg.pending_by_stage_group` | Pending cases by stage group (NJDG) | cases | district | 2026-10 | 4 |
| `njdg.pending_cases` | Pending cases (NJDG) | cases | district | 2026-10 | 3 |
| `njdg.pending_filed_by_senior_citizens` | Pending cases filed by senior citizens (NJDG) | cases | district | 2026-10 | 3 |
| `njdg.pending_filed_by_women` | Pending cases filed by women (NJDG) | cases | district | 2026-10 | 3 |
| `njdg.undated_cases` | Undated pending cases (NJDG) | cases | district | 2026-10 | 3 |

### education

| Metric | What it is | Unit | Places | Periods | Values |
|---|---|---|---|---|---|
| `gseb.appeared` | Board-exam candidates appeared | candidates | district, exam centre | 2026-01 to 2026-12 | 88 |
| `gseb.candidates_by_grade` | Board-exam candidates by grade | candidates | district | 2026-01 to 2026-12 | 26 |
| `gseb.pass_pct` | Board-exam pass percentage | % | district, exam centre | 2024-01 to 2026-12 | 138 (1 blank) |
| `gseb.passed` | Board-exam candidates passed | candidates | district, exam centre | 2026-01 to 2026-12 | 88 |
| `gseb.registered` | Board-exam candidates registered | candidates | district, exam centre | 2026-01 to 2026-12 | 88 |
| `udise.dropout_rate_pct` | Dropout rate | % | district | 2024-04 to 2026-03 | 6 |
| `udise.enrolment` | Enrolment, foundational to secondary | students | district | 2024-04 to 2026-03 | 2 |
| `udise.enrolment.by_category` | Enrolment by school category | students | district | 2024-04 to 2026-03 | 20 |
| `udise.enrolment.by_management` | Enrolment by school management | students | district | 2024-04 to 2026-03 | 16 (4 blank) |
| `udise.enrolment.by_social_group` | Enrolment by social group | students | district | 2024-04 to 2026-03 | 8 |
| `udise.enrolment.by_stage` | Enrolment by NEP stage | students | district | 2024-04 to 2026-03 | 8 |
| `udise.enrolment.cwsn` | Children with special needs enrolled | students | district | 2024-04 to 2026-03 | 2 |
| `udise.ger_pct` | Gross enrolment ratio | % | district | 2024-04 to 2026-03 | 6 (6 blank) |
| `udise.pgi_d.grade` | PGI-D grade |  | district | 2024-04 to 2026-03 | 2 |
| `udise.pgi_d.score` | PGI-D overall score | points (of 600) | district | 2024-04 to 2026-03 | 2 |
| `udise.ptr` | Pupil-teacher ratio | pupils per teacher | district | 2024-04 to 2026-03 | 8 |
| `udise.schools` | Schools | schools | district | 2024-04 to 2026-03 | 2 |
| `udise.schools.by_category` | Schools by school category | schools | district | 2024-04 to 2026-03 | 20 |
| `udise.schools.by_management` | Schools by management | schools | district | 2024-04 to 2026-03 | 16 |
| `udise.schools.primary_with_preprimary` | Govt and aided primary schools with Balvatika | schools | district | 2024-04 to 2026-03 | 2 |
| `udise.schools.with_primary` | Government / aided schools having primary levels | schools | district | 2024-04 to 2026-03 | 4 |
| `udise.schools_with_facility_pct` | Schools with a facility | % of schools | district | 2024-04 to 2026-03 | 44 |
| `udise.teachers` | Teachers | teachers | district | 2024-04 to 2026-03 | 2 |
| `udise.teachers.by_management` | Teachers by school management | teachers | district | 2024-04 to 2026-03 | 16 |
| `udise.transition_rate_pct` | Transition rate | % | district | 2024-04 to 2026-03 | 6 |

### environment

| Metric | What it is | Unit | Places | Periods | Values |
|---|---|---|---|---|---|
| `cpcb.city_aqi` | Air Quality Index (CPCB daily bulletin) | index | city | 2026-10 | 3 |
| `cpcb.city_aqi_category` | AQI category (CPCB daily bulletin) |  | city | 2026-10 | 3 |
| `cpcb.city_prominent_pollutants` | Prominent pollutant(s) (CPCB daily bulletin) |  | city | 2026-10 | 3 |
| `cpcb.city_stations_participated` | Stations in the city AQI | stations | city | 2026-10 | 3 |
| `cpcb.city_stations_total` | Stations in the city | stations | city | 2026-10 | 3 |
| `cpcb.station_aqi` | Station AQI (CPCB CAAQMS feed) | index | station | 2026-10 | 2 |
| `cpcb.station_prominent_pollutant` | Station prominent pollutant (CPCB CAAQMS feed) |  | station | 2026-10 | 2 |
| `cpcb.station_subindex_avg` | Pollutant sub-index, average (CPCB CAAQMS feed) | index | station | 2026-10 | 14 (2 blank) |
| `air.smc_sensor_nox_ugm3` | NOx (SMC real-time sensor) | ug/m3 | station | 2026-10 | 1 |
| `air.smc_sensor_pm10_ugm3` | PM10 (SMC real-time sensor) | ug/m3 | station | 2026-10 | 1 |
| `air.smc_sensor_pm25_ugm3` | PM2.5 (SMC real-time sensor) | ug/m3 | station | 2026-10 | 1 |
| `air.smc_sensor_relative_humidity_pct` | Relative humidity (SMC sensor station) | % | station | 2026-10 | 1 |
| `air.smc_sensor_so2_ugm3` | SO2 (SMC real-time sensor) | ug/m3 | station | 2026-10 | 1 |
| `air.smc_sensor_temperature_c` | Ambient temperature (SMC sensor station) | degC | station | 2026-10 | 1 |
| `swm.avg_collection_mt_per_day` | Average municipal solid waste collected | tonnes/day | city | 2008-10 to 2026-09 | 1052 (4 blank) |
| `swm.smart_dustbins_installed` | Smart underground dustbins installed | dustbins | city | 2019-04 to 2026-09 | 90 |
| `swm.total_routes` | Night scraping/brushing routes | routes | city | 2008-10 to 2026-09 | 216 |
| `swm.total_trips` | Collection trips | trips | city | 2008-10 to 2026-09 | 1052 (4 blank) |
| `swm.vehicles_utilized` | Vehicles used for collection | vehicles | city | 2008-10 to 2026-09 | 1052 (4 blank) |

Records: `aq_station` (9, from smc_air_quality); `aq_station_proposed` (7, from smc_air_quality); `document` (7, from smc_air_quality).

### finance

| Metric | What it is | Unit | Places | Periods | Values |
|---|---|---|---|---|---|
| `cityfinance.capital_expenditure` | Capital expenditure (CityFinance) | INR | city | 2015-04 to 2024-03 | 8 (2 blank) |
| `cityfinance.expenditure.by_head` | Revenue expenditure by account head (CityFinance income statement) | INR | city | 2015-04 to 2024-03 | 80 (33 blank) |
| `cityfinance.expenditure.total` | Total expenditure in the income statement (CityFinance) | INR | city | 2015-04 to 2024-03 | 8 |
| `cityfinance.income.by_head` | Income by account head (CityFinance income statement) | INR | city | 2015-04 to 2024-03 | 80 (21 blank) |
| `cityfinance.income.total` | Total revenue (CityFinance) | INR | city | 2015-04 to 2024-03 | 8 |
| `cityfinance.own_source_revenue` | Own source revenue (CityFinance) | INR | city | 2015-04 to 2024-03 | 8 |
| `cityfinance.revenue_expenditure` | Revenue expenditure (CityFinance) | INR | city | 2015-04 to 2024-03 | 8 |
| `finance.balance_sheet.accumulated_depreciation` | Fixed assets: accumulated depreciation | INR | city | 2007-03 to 2026-03 | 20 |
| `finance.balance_sheet.cash_bank` | Cash and bank balances | INR | city | 2007-03 to 2026-03 | 20 |
| `finance.balance_sheet.current_assets` | Current assets, loans and advances (total) | INR | city | 2007-03 to 2026-03 | 20 |
| `finance.balance_sheet.current_liabilities` | Current liabilities | INR | city | 2007-03 to 2026-03 | 20 |
| `finance.balance_sheet.cwip` | Capital work in progress | INR | city | 2007-03 to 2026-03 | 20 |
| `finance.balance_sheet.gross_block` | Fixed assets: gross block | INR | city | 2007-03 to 2026-03 | 20 |
| `finance.balance_sheet.inventories` | Inventories | INR | city | 2007-03 to 2026-03 | 20 |
| `finance.balance_sheet.investments` | Investments | INR | city | 2007-03 to 2026-03 | 20 |
| `finance.balance_sheet.loan_funds` | Loan funds (total) | INR | city | 2007-03 to 2026-03 | 18 |
| `finance.balance_sheet.loans_advances` | Loans and advances | INR | city | 2007-03 to 2026-03 | 20 |
| `finance.balance_sheet.municipal_fund` | Municipal fund | INR | city | 2007-03 to 2026-03 | 20 |
| `finance.balance_sheet.net_block` | Fixed assets: net block | INR | city | 2007-03 to 2026-03 | 20 |
| `finance.balance_sheet.own_funds` | Own funds (total) | INR | city | 2007-03 to 2026-03 | 20 |
| `finance.balance_sheet.provisions_for_taxes` | Provisions for taxes | INR | city | 2007-03 to 2026-03 | 20 (15 blank) |
| `finance.balance_sheet.reserves_surplus` | Reserves and surplus | INR | city | 2007-03 to 2026-03 | 20 |
| `finance.balance_sheet.secured_loans` | Secured loans | INR | city | 2007-03 to 2026-03 | 18 (2 blank) |
| `finance.balance_sheet.sundry_debtors` | Sundry debtors | INR | city | 2007-03 to 2026-03 | 20 |
| `finance.balance_sheet.total` | Balance sheet total | INR | city | 2007-03 to 2026-03 | 20 |
| `finance.balance_sheet.unsecured_loans` | Unsecured loans | INR | city | 2023-03 to 2026-03 | 4 (1 blank) |
| `finance.income_expenditure.administration_expenses` | Administration expenses | INR | city | 2006-04 to 2026-03 | 20 |
| `finance.income_expenditure.depreciation` | Depreciation | INR | city | 2006-04 to 2026-03 | 20 |
| `finance.income_expenditure.employee_costs` | Payments and benefits to employees | INR | city | 2006-04 to 2026-03 | 20 |
| `finance.income_expenditure.excess_income_over_expenditure` | Excess of income over expenditure | INR | city | 2006-04 to 2026-03 | 20 |
| `finance.income_expenditure.finance_charges` | Finance charges | INR | city | 2006-04 to 2026-03 | 20 |
| `finance.income_expenditure.grants_contributions` | Government grants, contributions and subsidies | INR | city | 2006-04 to 2026-03 | 20 |
| `finance.income_expenditure.loss_on_disposal` | Loss on sale/disposal of fixed assets | INR | city | 2006-04 to 2026-03 | 9 (2 blank) |
| `finance.income_expenditure.non_tax_revenue` | Non-tax revenues | INR | city | 2006-04 to 2026-03 | 20 |
| `finance.income_expenditure.octroi_compensation` | Compensation in lieu of octroi | INR | city | 2006-04 to 2026-03 | 20 |
| `finance.income_expenditure.other_expenses` | Other expenses | INR | city | 2006-04 to 2026-03 | 18 (5 blank) |
| `finance.income_expenditure.other_income` | Other income | INR | city | 2006-04 to 2026-03 | 20 |
| `finance.income_expenditure.prior_period_expenses` | Prior period expenses | INR | city | 2006-04 to 2026-03 | 20 |
| `finance.income_expenditure.prior_period_income` | Prior period income | INR | city | 2006-04 to 2026-03 | 20 |
| `finance.income_expenditure.repairs_maintenance` | Repairs and maintenance | INR | city | 2006-04 to 2026-03 | 20 |
| `finance.income_expenditure.service_utility_charges` | Service and utilities charges | INR | city | 2006-04 to 2026-03 | 20 |
| `finance.income_expenditure.surplus_after_tax` | Net surplus (deficit) after taxation | INR | city | 2006-04 to 2026-03 | 20 |
| `finance.income_expenditure.surplus_before_tax` | Net surplus (deficit) before taxation | INR | city | 2006-04 to 2026-03 | 20 |
| `finance.income_expenditure.tax_provision` | Provision for taxes | INR | city | 2006-04 to 2026-03 | 20 (14 blank) |
| `finance.income_expenditure.tax_revenue` | Tax revenues | INR | city | 2006-04 to 2026-03 | 20 |
| `finance.income_expenditure.total_expenditure` | Total expenditure | INR | city | 2006-04 to 2026-03 | 20 |
| `finance.income_expenditure.total_income` | Total income | INR | city | 2006-04 to 2026-03 | 20 |
| `finance.budget_summary.expenditure` | Budget summary: expenditure (revenue/capital) | INR | city, zone | 2024-04 to 2027-03 | 132 |
| `finance.budget_summary.income` | Budget summary: income (revenue/capital) | INR | city, zone | 2024-04 to 2027-03 | 132 |

Records: `balance_sheet_pdf` (21, from smc_balance_sheet).

### food

| Metric | What it is | Unit | Places | Periods | Values |
|---|---|---|---|---|---|
| `agm.arrivals_tonnes` | Commodity arrivals | tonnes |  |  | 0 (disabled) |
| `agm.market_reported` | Market reported prices | price lines |  |  | 0 (disabled) |
| `agm.price_max_rs_per_qtl` | Maximum price | Rs/quintal |  |  | 0 (disabled) |
| `agm.price_min_rs_per_qtl` | Minimum price | Rs/quintal |  |  | 0 (disabled) |
| `agm.price_modal_rs_per_qtl` | Modal price | Rs/quintal |  |  | 0 (disabled) |
| `fca.retail_price` | Retail price of essential commodities (DoCA, Surat centre) | Rs/kg |  |  | 0 (disabled) |
| `fca.wholesale_price` | Wholesale price of essential commodities (DoCA, Surat centre) | Rs/quintal |  |  | 0 (disabled) |

### health

| Metric | What it is | Unit | Places | Periods | Values |
|---|---|---|---|---|---|
| `nfhs.delivery_oop_rs` | Out-of-pocket cost per delivery in a public facility | Rs. | district | 2015-01 to 2021-12 | 2 |
| `nfhs.indicator_pct` | NFHS indicator (percentage) | % | district | 2015-01 to 2021-12 | 202 (42 blank) |
| `nfhs.sex_ratio` | NFHS sex ratio | females per 1,000 males | district | 2015-01 to 2021-12 | 4 |
| `health.disease.cases` | Disease cases (incidence) | cases | city | 1995-01 to 2023-10 | 2158 (1 blank) |
| `health.disease.deaths` | Disease deaths | deaths | city | 1995-01 to 2023-10 | 2158 |
| `health.malaria.positive_by_species` | Malaria positive cases by parasite species | cases | city | 2005-01 to 2023-10 | 452 |
| `health.malaria.smears_collected` | Malaria blood smears collected | samples | city | 2005-01 to 2023-10 | 226 |
| `health.malaria.smears_examined` | Malaria blood smears examined | samples | city | 2005-01 to 2023-10 | 226 |
| `vbdc.admin_charges` | Administrative charges levied for breeding sites | INR | city | 2005-01 to 2023-10 | 226 |
| `vbdc.biological_control` | Biological control actions | count | city | 2005-01 to 2023-10 | 226 |
| `vbdc.breeding_spots_checked` | Potential mosquito breeding spots checked | spots | city | 2005-01 to 2023-10 | 452 |
| `vbdc.breeding_spots_positive` | Breeding spots found positive, by mosquito type | spots | city | 2005-01 to 2023-10 | 1808 |
| `vbdc.construction_sites_checked` | Construction sites checked (peri-domestic survey) | sites | city | 2005-01 to 2023-10 | 226 |
| `vbdc.fogging_rounds` | Fogging machine rounds | rounds | city | 2005-01 to 2023-10 | 452 |
| `vbdc.houses_checked` | Houses checked (intra-domestic survey) | houses | city | 2005-01 to 2023-10 | 226 |
| `vbdc.notices_issued` | Notices issued for breeding sites | notices | city | 2005-01 to 2023-10 | 226 |
| `vbdc.source_reduction` | Source reduction actions | count | city | 2005-01 to 2023-10 | 226 |
| `health.smc_centres` | SMC urban health centres | centres | city, zone | 2024-06 | 20 |
| `pmjay.hospitals_by_speciality` | Listed PM-JAY hospitals by speciality | hospitals | district | 2024-06 | 22 |
| `pmjay.listed_hospitals` | Hospitals on SMC's PM-JAY empanelled list | hospitals | district | 2024-06 | 1 |
| `smimer.blood_components_issued` | Blood bank: units issued, by component | units | hospital | 2011-04 to 2026-09 | 1035 (5 blank) |
| `smimer.blood_donation_camps` | Blood bank: blood donation camps held | camps | hospital | 2011-04 to 2026-09 | 186 |
| `smimer.blood_units_collected` | Blood bank: units collected, by type of donation | units | hospital | 2011-04 to 2026-09 | 558 (4 blank) |
| `smimer.blood_units_collected_total` | Blood bank: units collected (grand total) | units | hospital | 2011-04 to 2026-09 | 186 |
| `smimer.blood_units_issued_other_hospitals` | Blood bank: units issued to other hospitals | units | hospital | 2011-04 to 2026-09 | 186 |
| `smimer.eyes_collected` | Eye bank: eyes collected | eyes | hospital | 2011-04 to 2026-09 | 186 |
| `smimer.eyes_utilised` | Eye bank: eyes utilised, by use | eyes | hospital | 2011-04 to 2026-09 | 558 |
| `smimer.icu_beds` | ICU beds | beds | hospital | 2011-04 to 2026-12 | 80 |
| `smimer.icu_patient_count` | ICU patients (monthly figure per ICU) | patients | hospital | 2011-04 to 2026-09 | 939 |
| `smimer.milk_collected_ml` | Human milk bank: milk collected | ml | hospital | 2011-04 to 2026-09 | 186 |
| `smimer.milk_donor_mothers` | Human milk bank: donor mothers | mothers | hospital | 2011-04 to 2026-09 | 186 |
| `smimer.milk_given_ml` | Human milk bank: milk given to newborns | ml | hospital | 2011-04 to 2026-09 | 186 |
| `smimer.milk_recipient_newborns` | Human milk bank: newborns receiving milk | newborns | hospital | 2011-04 to 2026-09 | 186 |

Records: `pmjay_hospital` (81, from smc_pmjay_hospitals); `smc_health_centre` (80, from smc_health_centres).

### housing

| Metric | What it is | Unit | Places | Periods | Values |
|---|---|---|---|---|---|
| `pmay.flats` | Flats in PMAY housing projects | flats | city | 2023-09 | 2 |
| `pmay.projects` | PMAY housing projects | projects | city | 2023-09 | 2 |

Records: `housing_project` (57, from smc_pmay).

### jobs

| Metric | What it is | Unit | Places | Periods | Values |
|---|---|---|---|---|---|
| `recruitment.open_ads` | SMC recruitment advertisements listed | advertisements | city | 2026-10 | 1 |
| `recruitment.posts` | Posts in listed SMC recruitment advertisements | posts | city | 2026-10 | 1 |

Records: `recruitment_ad` (2, from smc_recruitment).

### leadership


Records: `district_official` (11, from surat_collectorate); `smc_official` (92, from smc_officials).

### offices


Records: `smc_zone_office` (9, from smc_zone_offices); `taluka_office` (17, from surat_talukas).

### police

| Metric | What it is | Unit | Places | Periods | Values |
|---|---|---|---|---|---|
| `ncrb.cases_registered` | Crimes registered (NCRB, metropolitan city) | cases | metro city | 2022-01 to 2024-12 | 34 |
| `ncrb.chargesheeting_rate_pct` | Chargesheeting rate (NCRB, metropolitan city) | % | metro city | 2024-01 to 2024-12 | 10 |
| `ncrb.crime_rate_per_lakh` | Crime rate (NCRB, metropolitan city) | cases per lakh population | metro city | 2024-01 to 2024-12 | 6 |
| `ncrb.rate_population_lakh` | Population used for the crime rate (Census 2011) | lakh persons | metro city | 2011-03 | 6 |

### population

| Metric | What it is | Unit | Places | Periods | Values |
|---|---|---|---|---|---|
| `census.area_km2` | Area (Census 2011) | sq km | district, state | 2011-03 | 6 |
| `census.hh_assets_pct` | Households by assets owned (Census 2011) | % of households | district, state, taluka | 2010-04 to 2010-09 | 396 |
| `census.hh_banking_pct` | Households availing banking services (Census 2011) | % of households | district, state, taluka | 2010-04 to 2010-09 | 33 |
| `census.hh_bathing_pct` | Households by bathing facility (Census 2011) | % of households | district, state, taluka | 2010-04 to 2010-09 | 99 |
| `census.hh_condition_pct` | Households by condition of the census house (Census 2011) | % of households | district, state, taluka | 2010-04 to 2010-09 | 363 |
| `census.hh_cooking_fuel_pct` | Households by cooking fuel (Census 2011) | % of households | district, state, taluka | 2010-04 to 2010-09 | 330 |
| `census.hh_drainage_pct` | Households by waste-water outlet (Census 2011) | % of households | district, state, taluka | 2010-04 to 2010-09 | 99 |
| `census.hh_floor_pct` | Households by floor material (Census 2011) | % of households | district, state, taluka | 2010-04 to 2010-09 | 231 |
| `census.hh_kitchen_pct` | Households by kitchen facility (Census 2011) | % of households | district, state, taluka | 2010-04 to 2010-09 | 231 |
| `census.hh_latrine_pct` | Households by latrine facility (Census 2011) | % of households | district, state, taluka | 2010-04 to 2010-09 | 396 |
| `census.hh_lighting_pct` | Households by main source of lighting (Census 2011) | % of households | district, state, taluka | 2010-04 to 2010-09 | 198 |
| `census.hh_married_couples_pct` | Households by number of married couples (Census 2011) | % of households | district, state, taluka | 2010-04 to 2010-09 | 198 |
| `census.hh_ownership_pct` | Households by ownership of the house (Census 2011) | % of households | district, state, taluka | 2010-04 to 2010-09 | 99 |
| `census.hh_roof_pct` | Households by roof material (Census 2011) | % of households | district, state, taluka | 2010-04 to 2010-09 | 297 |
| `census.hh_rooms_pct` | Households by number of dwelling rooms (Census 2011) | % of households | district, state, taluka | 2010-04 to 2010-09 | 231 |
| `census.hh_size_pct` | Households by household size (Census 2011) | % of households | district, state, taluka | 2010-04 to 2010-09 | 231 |
| `census.hh_structure_pct` | Households by type of structure of the house (Census 2011) | % of households | district, state, taluka | 2010-04 to 2010-09 | 198 |
| `census.hh_wall_pct` | Households by wall material (Census 2011) | % of households | district, state, taluka | 2010-04 to 2010-09 | 330 |
| `census.hh_water_location_pct` | Households by location of drinking water (Census 2011) | % of households | district, state, taluka | 2010-04 to 2010-09 | 99 |
| `census.hh_water_source_pct` | Households by main source of drinking water (Census 2011) | % of households | district, state, taluka | 2010-04 to 2010-09 | 330 |
| `census.households` | Households (Census 2011) | households | district, state | 2011-03 | 6 |
| `census.illiterates` | Illiterates (Census 2011) | persons | district, state | 2011-03 | 18 |
| `census.literates` | Literates (Census 2011) | persons | district, state | 2011-03 | 18 |
| `census.main_workers` | Main workers (Census 2011) | persons | district, state | 2011-03 | 90 |
| `census.marginal_workers` | Marginal workers (Census 2011) | persons | district, state | 2011-03 | 270 |
| `census.non_workers` | Non-workers (Census 2011) | persons | district, state | 2011-03 | 18 |
| `census.population` | Population (Census 2011) | persons | district, state | 2011-03 | 18 |
| `census.population_0_6` | Population aged 0-6 (Census 2011) | persons | district, state | 2011-03 | 18 |
| `census.population_sc` | Scheduled Caste population (Census 2011) | persons | district, state | 2011-03 | 18 |
| `census.population_st` | Scheduled Tribe population (Census 2011) | persons | district, state | 2011-03 | 18 |
| `census.workers` | Workers, main and marginal (Census 2011) | persons | district, state | 2011-03 | 18 |
| `vital.births_by_month` | Births by month and sex (SMC birth register) | births | city | 1991-01 to 2022-12 | 1152 (6 blank) |
| `vital.city_area_km2` | City area used for vital statistics (SMC) | sq km | city | 2001-01 to 2021-12 | 21 |
| `vital.crude_birth_rate` | Crude birth rate (SMC) | per 1,000 population | city | 2001-01 to 2021-12 | 21 |
| `vital.crude_death_rate` | Crude death rate (SMC) | per 1,000 population | city | 2001-01 to 2021-12 | 21 |
| `vital.infant_deaths` | Registered infant deaths (SMC) | deaths | city | 2001-01 to 2021-12 | 21 |
| `vital.infant_mortality_rate` | Infant mortality rate (SMC) | per 1,000 live births | city | 2001-01 to 2021-12 | 21 |
| `vital.maternal_deaths` | Registered maternal deaths (SMC) | deaths | city | 2001-01 to 2021-12 | 21 |
| `vital.maternal_mortality_per_1000` | Maternal mortality rate per 1,000 live births (SMC) | per 1,000 live births | city | 2001-01 to 2017-12 | 17 |
| `vital.maternal_mortality_per_100k` | Maternal mortality rate per 100,000 live births (SMC) | per 100,000 live births | city | 2018-01 to 2021-12 | 4 |
| `vital.mid_year_population` | Mid-year estimated population (SMC) | persons | city | 2009-01 to 2021-12 | 13 |
| `vital.population_density` | Population density (SMC vital statistics) | persons per sq km | city | 2001-01 to 2017-12 | 17 |
| `vital.registered_births` | Registered births (SMC) | births | city | 2001-01 to 2021-12 | 21 |
| `vital.registered_deaths` | Registered deaths (SMC) | deaths | city | 2001-01 to 2021-12 | 21 |
| `vital.still_birth_ratio` | Still birth ratio (SMC) | per 1,000 live births | city | 2001-01 to 2021-12 | 21 |
| `vital.still_births` | Registered still births (SMC) | still births | city | 2001-01 to 2021-12 | 21 |

### power

| Metric | What it is | Unit | Places | Periods | Values |
|---|---|---|---|---|---|
| `streetlight.nonworking_pct` | Non-working streetlights (monthly average) | % | city | 2017-03 to 2021-02 | 48 |

### rti

| Metric | What it is | Unit | Places | Periods | Values |
|---|---|---|---|---|---|
| `rti.annual.aas_designated` | Appellate Authorities designated | officers | city | 2005-04 to 2026-03 | 15 |
| `rti.annual.additional_fees_rs` | RTI additional fees and other charges collected | Rs | city | 2005-04 to 2026-03 | 15 |
| `rti.annual.apios_designated` | Assistant PIOs designated | officers | city | 2005-04 to 2026-03 | 15 |
| `rti.annual.disciplinary_actions` | Disciplinary actions against officers under RTI | cases | city | 2005-04 to 2026-03 | 15 |
| `rti.annual.first_appeals_accepted` | RTI first appeals accepted | appeals | city | 2005-04 to 2026-03 | 15 |
| `rti.annual.first_appeals_opening_balance` | RTI first appeals pending at start of year | appeals | city | 2005-04 to 2026-03 | 15 |
| `rti.annual.first_appeals_received` | RTI first appeals received | appeals | city | 2005-04 to 2026-03 | 15 |
| `rti.annual.first_appeals_rejected` | RTI first appeals rejected | appeals | city | 2005-04 to 2026-03 | 15 |
| `rti.annual.penalties_collected_rs` | RTI penalties collected | Rs | city | 2005-04 to 2026-03 | 15 |
| `rti.annual.penalties_levied_rs` | RTI penalties levied | Rs | city | 2005-04 to 2026-03 | 15 |
| `rti.annual.penalties_total_rs` | RTI penalties total (as printed) | Rs | city | 2005-04 to 2026-03 | 15 |
| `rti.annual.pios_designated` | Public Information Officers designated | officers | city | 2005-04 to 2026-03 | 15 |
| `rti.annual.registration_fees_rs` | RTI registration (application) fees collected | Rs | city | 2005-04 to 2026-03 | 15 |
| `rti.annual.rejections_by_section` | RTI exemptions invoked when rejecting requests | times | city | 2005-04 to 2026-03 | 210 |
| `rti.annual.requests_accepted` | RTI requests accepted | requests | city | 2005-04 to 2026-03 | 15 |
| `rti.annual.requests_opening_balance` | RTI requests pending at start of year | requests | city | 2005-04 to 2026-03 | 15 |
| `rti.annual.requests_received` | RTI requests received | requests | city | 2005-04 to 2026-03 | 15 |
| `rti.annual.requests_rejected` | RTI requests rejected | requests | city | 2005-04 to 2026-03 | 15 |
| `rti.annual.requests_transferred` | RTI requests transferred to other authorities | requests | city | 2005-04 to 2026-03 | 15 |
| `rti.quarterly.appellate_authorities` | Appellate authorities (Patrak-8 header) | officers | city | 2026-04 to 2026-06 | 1 |
| `rti.quarterly.application_fees_rs` | RTI application fees received in quarter | Rs | city | 2026-04 to 2026-06 | 3 (1 blank) |
| `rti.quarterly.first_appeal_refusals_by_section` | RTI exemptions upheld in first appeals (quarter) | times | city | 2026-04 to 2026-06 | 42 |
| `rti.quarterly.first_appeal_refusals_total` | RTI exemptions upheld in first appeals, total | times | city | 2026-04 to 2026-06 | 3 |
| `rti.quarterly.first_appeals_allowed` | RTI first appeals allowed in full | appeals | city | 2026-04 to 2026-06 | 3 |
| `rti.quarterly.first_appeals_disposed` | RTI first appeals disposed of in quarter | appeals | city | 2026-04 to 2026-06 | 3 |
| `rti.quarterly.first_appeals_disposed_within_time` | RTI first appeals disposed of within time limit | appeals | city | 2026-04 to 2026-06 | 3 |
| `rti.quarterly.first_appeals_partly_allowed` | RTI first appeals partly allowed | appeals | city | 2026-04 to 2026-06 | 3 |
| `rti.quarterly.first_appeals_pending_end` | RTI first appeals pending at end of quarter | appeals | city | 2026-04 to 2026-06 | 3 |
| `rti.quarterly.first_appeals_pending_start` | RTI first appeals pending at start of quarter | appeals | city | 2026-04 to 2026-06 | 3 |
| `rti.quarterly.first_appeals_received` | RTI first appeals received in quarter | appeals | city | 2026-04 to 2026-06 | 3 |
| `rti.quarterly.first_appeals_rejected` | RTI first appeals rejected in full | appeals | city | 2026-04 to 2026-06 | 3 |
| `rti.quarterly.first_appeals_total` | RTI first appeals on hand in quarter | appeals | city | 2026-04 to 2026-06 | 3 |
| `rti.quarterly.income_earlier_in_fy_rs` | RTI income earlier in the financial year | Rs |  |  | 0 |
| `rti.quarterly.income_fy_to_date_rs` | RTI income in financial year to date | Rs | city | 2026-04 to 2026-06 | 3 |
| `rti.quarterly.income_rs` | RTI fee and charges income in quarter | Rs | city | 2026-04 to 2026-06 | 3 |
| `rti.quarterly.other_charges_rs` | RTI charges other than application fee (quarter) | Rs | city | 2026-04 to 2026-06 | 3 (1 blank) |
| `rti.quarterly.pios` | Public Information Officers (Patrak-7 header) | officers | city | 2026-04 to 2026-06 | 1 |
| `rti.quarterly.refusals_by_section` | RTI exemptions invoked in refusals (quarter) | times | city | 2026-04 to 2026-06 | 42 (14 blank) |
| `rti.quarterly.refusals_total` | RTI refusals by section, total (quarter) | times | city | 2026-04 to 2026-06 | 3 |
| `rti.quarterly.requests_disposed` | RTI applications disposed of in quarter | applications | city | 2026-04 to 2026-06 | 3 |
| `rti.quarterly.requests_disposed_within_time` | RTI applications disposed of within time limit | applications | city | 2026-04 to 2026-06 | 3 |
| `rti.quarterly.requests_info_supplied` | RTI applications answered in full | applications | city | 2026-04 to 2026-06 | 3 |
| `rti.quarterly.requests_pending_end` | RTI applications pending at end of quarter | applications | city | 2026-04 to 2026-06 | 3 |
| `rti.quarterly.requests_pending_start` | RTI applications pending at start of quarter | applications | city | 2026-04 to 2026-06 | 3 |
| `rti.quarterly.requests_received` | RTI applications received in quarter | applications | city | 2026-04 to 2026-06 | 3 |
| `rti.quarterly.requests_refused_fully` | RTI applications refused in full | applications | city | 2026-04 to 2026-06 | 3 (1 blank) |
| `rti.quarterly.requests_refused_partly` | RTI applications refused in part | applications | city | 2026-04 to 2026-06 | 3 (1 blank) |
| `rti.quarterly.requests_total` | RTI applications on hand in quarter | applications | city | 2026-04 to 2026-06 | 3 |
| `rti.quarterly.requests_transferred_partly` | RTI applications partly transferred | applications | city | 2026-04 to 2026-06 | 3 |
| `rti.quarterly.requests_transferred_wholly` | RTI applications wholly transferred | applications | city | 2026-04 to 2026-06 | 3 |

Records: `rti_annual_return` (20, from smc_rti).

### schemes


Records: `smc_ucd_scheme` (9, from smc_ucd_schemes).

### tenders

| Metric | What it is | Unit | Places | Periods | Values |
|---|---|---|---|---|---|
| `tenders.active` | SMC active tenders | tenders | city | 2026-10 | 1 |
| `tenders.closing_within` | SMC tenders closing soon | tenders | city | 2026-10 | 3 |

Records: `tender` (70, from smc_tenders); `tender_notice` (70, from smc_tenders).

### transport

| Metric | What it is | Unit | Places | Periods | Values |
|---|---|---|---|---|---|
| `aai.passengers` | Airport passengers (AAI traffic news) | passengers |  |  | 0 (disabled) |
| `aai.passengers_fytd` | Airport passengers, financial year to date (AAI traffic news) | passengers |  |  | 0 (disabled) |
| `ebus.buses_operated` | Electric buses operated | buses | city | 2026-04 | 1 |
| `ebus.fuel_saved_litres_per_day` | Fuel saved per day by electric buses | litres/day | city | 2026-04 | 1 |
| `ebus.fuel_saved_litres_total` | Fuel saved by electric buses (cumulative) | litres | city | 2026-04 | 1 |
| `ebus.ghg_reduction_kg_co2e_per_day` | GHG emissions avoided per day | kg CO2e/day | city | 2026-04 | 1 |
| `ebus.ghg_reduction_kg_co2e_total` | GHG emissions avoided (cumulative) | kg CO2e | city | 2026-04 | 1 |
| `ebus.run_km_total` | Electric bus kilometres run (cumulative) | km | city | 2026-04 | 1 |

### water

| Metric | What it is | Unit | Places | Periods | Values |
|---|---|---|---|---|---|
| `jjm.har_ghar_jal_certified` | Har Ghar Jal certified district | flag | Tapi, district | 2026-10 | 2 |
| `jjm.har_ghar_jal_reported` | Har Ghar Jal reported district | flag | Tapi, district | 2026-10 | 2 |
| `jjm.households_with_tap` | Rural households with a tap connection (JJM) | households | Tapi, district | 2019-08 to 2026-10 | 4 |
| `jjm.rural_households` | Rural households (JJM) | households | Tapi, district | 2026-10 | 2 |
| `jjm.tap_coverage_pct` | Rural tap water coverage (JJM) | percent | Tapi, district | 2026-10 | 2 |
| `flood.causeway_overflow_level_m` | Causeway overflow level (as published) | m | weir | 2026-10 | 1 |
| `flood.causeway_status` | Causeway status (as published) |  | weir | 2026-10 | 1 |
| `flood.creek_danger_level_m` | Creek (khadi) danger level (as published) | m | creek | 2026-10 | 5 |
| `flood.creek_level_m` | Creek (khadi) water level | m | creek | 2026-10 | 50 |
| `flood.dam_frl_ft` | Ukai full reservoir level (as published) | ft | dam | 2026-10 | 1 |
| `flood.dam_inflow_cusec` | Ukai estimated inflow | cusec | dam | 2026-10 | 10 |
| `flood.dam_level_ft` | Ukai reservoir level | ft | dam | 2026-10 | 10 |
| `flood.dam_outflow_cusec` | Ukai estimated outflow | cusec | dam | 2026-10 | 10 |
| `flood.weir_level_m` | Weir-cum-causeway water level | m | weir | 2026-10 | 10 |
| `flood.weir_outflow_cusec` | Weir-cum-causeway estimated outflow | cusec | weir | 2026-10 | 10 |
| `rain.smc_total_mm` | Total rainfall, Surat city (cumulative) | mm | city | 2026-10 | 10 |
| `rain.smc_zone_mm` | Zone-wise rainfall | mm | zone | 2026-10 | 80 |
| `wq.tap_samples_collected` | Water samples collected at consumer taps | samples | city, zone | 2009-05 to 2026-08 | 1761 |
| `wq.tap_samples_fit` | Water samples found fit | samples | city, zone | 2009-05 to 2026-08 | 1761 |
| `wq.tap_samples_unfit` | Water samples found unfit | samples | city, zone | 2009-05 to 2026-08 | 1761 (16 blank) |
| `wrd.alert_level` | Reservoir warning level |  | dam | 2026-10 | 15 |
| `wrd.dam_frl_m` | Full reservoir level | m | dam | 2026-10 | 15 |
| `wrd.dam_level_m` | Reservoir water level | m | dam | 2026-10 | 15 |
| `wrd.design_gross_storage_mcm` | Design gross storage | MCM | Tapi, dam, district, state | 2026-10 | 24 |
| `wrd.design_live_storage_mcm` | Design live storage | MCM | Tapi, dam, district, state | 2026-10 | 24 |
| `wrd.gross_storage_mcm` | Present gross storage | MCM | Tapi, dam, district, state | 2026-10 | 24 |
| `wrd.gross_storage_pct` | Storage, % of design gross | % | Tapi, dam, district, state | 2026-10 | 24 |
| `wrd.inflow_cusec` | Inflow | cusecs | dam | 2026-10 | 15 |
| `wrd.live_storage_mcm` | Present live storage | MCM | Tapi, dam, district, state | 2026-10 | 24 |
| `wrd.live_storage_pct` | Live storage, % of design live | % | Tapi, dam, district, state | 2026-10 | 12 |
| `wrd.outflow_canal_cusec` | Outflow to canals | cusecs | dam | 2026-10 | 15 |
| `wrd.outflow_river_cusec` | Outflow to the river | cusecs | dam | 2026-10 | 15 |
| `wrd.rain_24h_mm` | Rainfall at the dam, last 24 hours | mm | dam | 2026-10 | 12 |
| `wrd.rain_cumulative_mm` | Cumulative rainfall at the dam | mm | dam | 2026-10 | 12 |

Records: `document` (215, from smc_water_quality); `wq_sampling_test` (12, from smc_water_quality).

### weather

| Metric | What it is | Unit | Places | Periods | Values |
|---|---|---|---|---|---|
| `gsdma.rain_24h_mm` | Rainfall in the last 24 hours (GSDMA) | mm | district, state, taluka | 2026-10 | 126 |
| `gsdma.rain_normal_mm` | Average season rainfall (GSDMA, 1996-2025) | mm | district, state, taluka | 1996-01 to 2025-12 | 14 |
| `gsdma.rain_pct_of_normal` | Season rainfall so far, % of the season average (GSDMA) | % | district, state, taluka | 2026-10 | 126 |
| `gsdma.rain_season_mm` | Season rainfall so far (GSDMA) | mm | district, state, taluka | 2026-10 | 126 |
| `gsdma.state_month_rain_mm` | Gujarat average rainfall in the month (GSDMA) | mm | state | 2026-06 to 2026-10 | 13 |
| `openmeteo.apparent_temperature_c` | Feels-like temperature (model) | degC |  |  | 0 (disabled) |
| `openmeteo.daily_precip_probability_max_pct` | Chance of rain (model) | % |  |  | 0 (disabled) |
| `openmeteo.daily_precip_sum_mm` | Precipitation of the day (model) | mm |  |  | 0 (disabled) |
| `openmeteo.daily_temperature_max_c` | Maximum temperature of the day (model) | degC |  |  | 0 (disabled) |
| `openmeteo.daily_temperature_min_c` | Minimum temperature of the day (model) | degC |  |  | 0 (disabled) |
| `openmeteo.daily_uv_index_max` | Maximum UV index of the day (model) | UV index |  |  | 0 (disabled) |
| `openmeteo.daily_weather_code` | Weather of the day (WMO code, model) | WMO code |  |  | 0 (disabled) |
| `openmeteo.daily_wind_speed_max_kmh` | Maximum wind speed of the day (model) | km/h |  |  | 0 (disabled) |
| `openmeteo.precipitation_mm` | Precipitation in the last 15 minutes (model) | mm |  |  | 0 (disabled) |
| `openmeteo.relative_humidity_pct` | Relative humidity at 2 m (model) | % |  |  | 0 (disabled) |
| `openmeteo.sunrise` | Sunrise |  |  |  | 0 (disabled) |
| `openmeteo.sunset` | Sunset |  |  |  | 0 (disabled) |
| `openmeteo.surface_pressure_hpa` | Surface air pressure (model) | hPa |  |  | 0 (disabled) |
| `openmeteo.temperature_c` | Air temperature at 2 m (model) | degC |  |  | 0 (disabled) |
| `openmeteo.weather_code` | Current weather (WMO code, model) | WMO code |  |  | 0 (disabled) |
| `openmeteo.wind_direction_deg` | Wind direction at 10 m (model) | degrees |  |  | 0 (disabled) |
| `openmeteo.wind_speed_kmh` | Wind speed at 10 m (model) | km/h |  |  | 0 (disabled) |

