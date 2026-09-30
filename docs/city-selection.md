# City selection: Surat vs Ahmedabad

This research asked which city is easier to build a forthepeople.in-style dashboard and RTI helper for. It was done on 24-28 Sep 2026: sources were fetched live, and the claims that decide the pick were re-checked by an independent verifier.

## Starting point

- Neither city is live on forthepeople.in. `/en/gujarat/surat` and `/en/gujarat/ahmedabad` are locked "29 dashboards waiting to be unlocked" placeholders.
- Upstream issue #11, "Add Ahmedabad", was closed in Apr 2026 without merged code. The upstream README still lists a contributor on "Ahmedabad district (in progress)". Surat has no such claim.

## Verdict: **Surat** (confidence: high)

Weighted score, 0-10: **Surat 6.6 vs Ahmedabad 5.6**

| Dimension | Weight | Surat | Ahmedabad | Why |
|---|---|---|---|---|
| budget | 0.2 | 7.5 | 5.5 | Surat publishes budget vs actuals weekly by zone (last updated 27/09/2026) as HTML, plus a text balance sheet for FY26. Ahmedabad has the longer budget archive (from 2005-06), but its FY26 balance sheet is a 49-page scan. Both are on CityFinance up to 2023-24 (AMC under the slug 'amdavad'). |
| education | 0.15 | 5 | 7 | The AMC School Board publishes enrolment by zone and class (172,576 students) and 4,653 teachers, as of 31-07-2025, in HTML that can be scraped. The Surat board site renders by JavaScript and holds no data; Surat only has the Suman High School PDFs. National sources are the same for both. |
| food_prices | 0.15 | 6 | 7 | Both appear in the Agmarknet JSON feed and the Consumer Affairs (DoCA) price data. Ahmedabad APMC reports more reliably; Surat APMC returned 0 rows on 25-09-2026. Ahmedabad City is its own ration-shop (PDS/IMPDS) district, while Surat's Agmarknet list includes markets in Tapi district. |
| health_env | 0.15 | 6.5 | 4.5 | The verifier found Surat data the first pass missed: monthly waste tonnage up to Jul 2026 and monthly disease cases and deaths for 1995-2022, both in HTML. AMC has neither, only a 2018-20 air-quality PDF and figures quoted in the press. NFHS-5 and Swachh Survekshan cover both equally. |
| governance | 0.1 | 6 | 5.5 | Surat's corporator list is confirmed as the 2026-31 term, in English HTML. AMC's Statistical Outline stops at 2006-07. Ahmedabad keeps two edges: a 48-ward GeoJSON on datameet, and councillor party and phone details. Smart City portals, NCRB, GTFS and grievance data are equal. |
| rti | 0.15 | 7.5 | 4.5 | SMC has a PIO and appellate-officer list from Dec 2025, annual RTI returns from 2005-07 to 2025-26, the quarterly Patrak-7, a status tracker, 104 disclosures refreshed in 2026 and a link to the state portal. AMC's RTI statistics end in 2010-11, its PIO list dates from 2011, and it still hosts the superseded 2005 rules. |
| district_modules | 0.1 | 7.5 | 5 | Surat publishes Ukai dam readings and zone-wise rainfall live in HTML, and its PMAY housing projects as tables. Ahmedabad's only advantage is ward polygons. Its upstream geo slug 'ahmadabad' does not match 'ahmedabad' in the code, so its map link returns 404. The codebase is otherwise near parity, so it is counted here. |

### Decisive factors

- Budget carries the largest weight (0.20). Surat publishes budget vs actuals weekly by zone (updated 27/09/2026), a 4-page English text balance sheet for FY2025-26, and CityFinance XLSX up to 2023-24. AMC's FY2025-26 balance sheet is a 49-page image scan that needs OCR.
- RTI is the project's differentiator. SMC has a current PIO and appellate-officer list (09-12-2025), English annual returns from 2005-07 to 2025-26, the quarterly Patrak-7, a status tracker and 104 disclosures refreshed May-Jun 2026. AMC's RTI disclosures stop in 2010-11, with a 2011 PIO list.
- Health and environment, after the verifier's corrections: SMC publishes monthly waste collection up to Jul 2026 and monthly disease cases and deaths for 1995-2022 as HTML tables. AMC publishes neither.
- Site access: suratmunicipal.gov.in works over standard TLS with stable document URLs. ahmedabadcity.gov.in needs legacy TLS renegotiation plus certificate bypass (-k), which breaks Node/Vercel fetch and WebFetch-style tools, and it serves files behind opaque ViewFile IDs.
- City-specific modules: live Ukai dam and zone-wise rainfall HTML and the PMAY project tables exist only for Surat. The upstream geo slug 'surat' matches the code, while Ahmedabad's 'ahmadabad' vs 'ahmedabad' mismatch sends its map link to a 404.
- The result holds under other weightings. Surat leads 6.60 to 5.60 with the given weights, 6.57 to 5.57 with equal weights, 6.44 to 5.21 with RTI left out, and 6.38 to 5.68 with the verifier's health correction undone. Surat wins 5 of the 7 dimensions.
- Surat's weak spots (school enrolment, ward polygons, city ration-shop totals, disease data after 2022) belong to authorities with a current PIO list. They can become the first RTI demo templates rather than dead ends.

### Where Ahmedabad is genuinely better

- Education favours Ahmedabad. The AMC School Board publishes enrolment by zone and class (172,576 students) and 4,653 teachers, as of 31-07-2025, in scrapeable HTML. Surat's board site holds no data, so a Surat schools tile stays empty until an RTI reply arrives.
- Food prices favour Ahmedabad. Its APMC reports to Agmarknet more reliably, and 'Ahmedabad City' is its own ration-shop (PDS and IMPDS) district aligned to AMC zones. Surat's city PDS totals must be summed from zones 901-910, and its Agmarknet list includes markets in Tapi district.
- Maps favour Ahmedabad. datameet has a 48-ward GeoJSON that matches the current council, and AMC's 2026-31 councillor PDF lists party and phone. Surat has no openly licensed ward polygons.
- Long-run budget trends are easier for Ahmedabad. AMC's budget archive runs from 2005-06 to 2026-27 with some English copies, and CityFinance covers AMC up to 2023-24 as well (slug 'amdavad').
- RTI story: AMC's stale disclosures would make a compelling 'we had to file RTI' case. Ahmedabad also has a consolidated Collectorate RTI contact list, filing at civic centres, the MAGP helpline, and the Information Commission (GIC) nearby in Gandhinagar.
- Both cities share the hardest problems: Gujarati legacy fonts and numerals in budget PDFs, district-level national data that does not match city limits, and no public transit (GTFS) or grievance data. Surat's lead is about 1 point on a 10-point judgement scale, not a landslide.

## MVP data sources for Surat

"Verified" means the URL was fetched during the research and re-checked on 28-09-2026.

| Module | Metric | Source | Format | Refresh | Verified |
|---|---|---|---|---|---|
| finance | Revenue and capital budget: original and revised estimates vs actuals, for HQ and each zone | [SMC Accounts - Revenue-Capital Budget Summary (Rs '000)](https://www.suratmunicipal.gov.in/Departments/Accounts/CapitalRevenueBudgetSummary) | HTML table whose rows load through a background (XHR) request; the endpoint still has to be found. Archive the data every week | weekly (last updated 27/09/2026) | yes |
| finance | Audited balance sheet including secured and unsecured loans (FY2025-26, with FY2024-25 alongside) | [SMC Accounts - Balance Sheet (URL as corrected by the verifier)](https://www.suratmunicipal.gov.in/Content/Documents/Departments/Accounts/BalanceSheet_25_26.pdf) | English text PDF, 4 pages; extracts cleanly with pdftotext -layout | annual; the index goes back to 2015-16 | yes |
| finance | Standardised audited income, expenditure and own revenue | [MoHUA CityFinance - Surat](https://www.cityfinance.in/municipal-data/city/surat) | Dashboard with XLSX export | annual (latest audited year 2023-24) | yes |
| finance | Approved budget books by fund and budget head | [SMC Accounts - Budget page (2021-22 to 2026-27)](https://www.suratmunicipal.gov.in/Departments/Accounts/Budget) | PDF (the 2026-27 book is 778 pages). Numbers parse, but the Gujarati text is a legacy font and comes out garbled, so budget heads must be mapped by hand | annual | yes |
| schools | SMC secondary schools (Suman High School): student details and 5-year board result summary | [SMC Services > Education > Suman High School](https://www.suratmunicipal.gov.in/Services/SumanHighSchool) | HTML plus PDFs (StudentsDetails.pdf, Last5YearsResultSummary.pdf); the PDFs have not been opened yet | annual | yes |
| schools | Schools, enrolment, teachers and infrastructure for Surat district (district level, not SMC limits) | [UDISE+ Dashboard (Ministry of Education)](https://dashboard.udiseplus.gov.in/) | JavaScript app; download the Excel export by hand and commit it to the repo | annual | yes |
| crops | Daily mandi arrivals and min/max/modal prices at Surat APMC (keep an allowlist of markets and drop those in Tapi district) | [Agmarknet v2 JSON backend](https://api.agmarknet.gov.in/v1/prices-and-arrivals/market-report/daily) | JSON via POST {date, marketIds, stateIds:[11]}; undocumented and needs Origin/Referer headers, so cache it daily | daily (Surat APMC reported on 23 of 30 days) | yes |
| crops | Daily retail and wholesale prices of 22 essential commodities at the Surat reporting centre | [Department of Consumer Affairs Price Monitoring Cell (fcainfoweb)](https://fcainfoweb.nic.in/reports/report_menu_web.aspx) | ASP.NET HTML report; the scraper must replay the VIEWSTATE postback | daily | yes |
| health | Monthly door-to-door waste collection (vehicles, trips, MT/day) | [SMC Solid Waste Management Statistics](https://www.suratmunicipal.gov.in/Departments/SolidWasteManagementStatistics) | 8 HTML tables | monthly (up to Jul 2026; series starts 2019) | yes |
| health | Monthly cases and deaths from gastroenteritis, enteric fever, TB, malaria, pneumonia, hepatitis and cholera | [SMC Health Department Disease Reports](https://www.suratmunicipal.gov.in/Departments/HealthDepartmentDiseaseReports) | 7 HTML tables | stale: covers 1995-2022 (RTI template for 2023 onward) | yes |
| health | NFHS-5 vs NFHS-4 indicators for Surat district (nutrition, anaemia, sanitation, immunisation) | [NFHS-5 district CSV mirror (pratapvardhan/NFHS-5, DOI 10.7910/DVN/42WNZF)](https://raw.githubusercontent.com/pratapvardhan/NFHS-5/master/NFHS-5-Districts.csv) | CSV (long format); label it as district-level | static (2019-21) | yes |
| water | Ukai dam level and inflow/outflow (every 2 hours), zone-wise city rainfall, creek levels | [SMC Rainfall Statistics / flood information page](https://www.suratmunicipal.gov.in/Home/rainfallinfo) | Server-rendered HTML tables | every 2 hours in the monsoon (last 27/09/2026 24:00) | yes |
| housing | PMAY / affordable housing projects: flats, TP scheme, contractor, tender value, status | [SMC Department of Affordable Housing - PMAY](https://www.suratmunicipal.gov.in/Departments/PradhanMantriAwasYojana) | HTML tables (completed and in progress) | ad hoc (page is undated) | yes |
| leadership | Corporators by ward: 30 wards x 4 = 120, term 2026-31 | [SMC Ward-wise List of Corporators](https://www.suratmunicipal.gov.in/Corporation/Corp_list) | English HTML (no party or phone) | per term; recheck after by-elections | yes |
| rti | RTI requests received, transferred and rejected (by section), first appeals, fees, and PIO/appellate-officer counts per year | [SMC Gujarat State RTI Annual Return printouts, 2005-07 to 2025-26 (index at /Downloads/Acts/RTI_ActAnnualReturn)](https://www.suratmunicipal.gov.in/Content/Documents/rtiact/Annual-Return/2025-2026.pdf) | English text PDF, one page per year | annual (May) | yes |
| rti | Quarterly disposal, disposal within time limit, end-of-quarter pendency, BPL applicants | [SMC Patrak-7 quarterly return](https://www.suratmunicipal.gov.in/Content/Documents/rtiact/other/patrak-7.pdf) | PDF; row labels are in a legacy font but the numbers are clean. The file is overwritten each quarter, so archive every scrape | quarterly (latest Q4 2025-26) | yes |
| rti | Directory of PIOs and appellate officers by department and zone, with phone, mobile and email | [SMC PIO/APIO and Appellate Officer list dated 09-12-2025](https://www.suratmunicipal.gov.in/Content/Documents/rtiact/piosandapios_guj.pdf) | 43-page PDF in a legacy Gujarati font; names need a legacy-to-Unicode converter, but phones and emails extract | about once a year | yes |
| rti | Gujarat RTI Rules 2010 (fee, payment modes, forms, appeal forms) for the walkthrough | [Gujarat RTI Rules 2010, copy hosted by SMC](https://www.suratmunicipal.gov.in/Content/Documents/rtiact/other/Gujarat_RTI_rules_2010.pdf) | OCR'd PDF (English; Gujarati version also hosted) | static | yes |

## Gujarat RTI facts for the walkthrough

- Fee: Rs 20 per application under the Gujarat RTI Rules 2010 (GAD notification, Gazette of 22-03-2010). Apply on Form A or on plain paper with the same details. There is no word limit and no one-subject rule.
- Ways to pay the application fee (Rule 3(2)): cash against a receipt, DD, pay order, IPO, non-judicial, court-fee or revenue stamp, stamp paper, franking, e-stamping, or treasury challan (head 0070-60-800-(17)). Other charges can be paid only by cash, DD, pay order, IPO or challan, not stamps (Rule 3(4)).
- If you apply electronically, you must pay the fee within 7 days, or the application is treated as withdrawn (Rule 3(1)).
- Charges (Rule 5): copies cost Rs 2 per page for A4/A3. Inspection is free for the first 30 minutes, then Rs 20 per 30 minutes. A CD or floppy costs Rs 50. The PIO must transfer a misdirected application within 5 days on Form D (Rule 4).
- GAD circular GAD/MRT/e-file/1/2023/1655/RTI Cell (approved 06-05-2025): the first 5 pages are free; requests made by email or the portal get scanned copies once the fee is paid; photography during inspection and pen drives are allowed; appellate officers must give reasoned orders; disclosures must be updated every year.
- BPL applicants pay no fee or charges if they attach a certified copy of a BPL card or certificate. Per the GAD circular of 05-12-2018, cited in the GIC FAQ, a BPL ration card alone does not qualify.
- You can apply in English, Hindi or Gujarati, in person, by post, or electronically where available. Form A carries a citizenship declaration, and Rule 7 lets the PIO verify citizenship.
- Deadlines: the PIO must reply within 30 days (48 hours if life or liberty is involved, +5 days if filed through an assistant PIO, 40 days if a third party is involved under s.11). No reply means deemed refusal (s.7(2)), and a late reply must be given free (s.7(6)).
- First appeal: on Form E to the First Appellate Authority in the same public authority, within 30 days. The FAA decides in 30 days, 45 at most. Second appeal (s.19(3)) or complaint (s.18) goes to the Gujarat Information Commission within 90 days, and can be filed online at gic.gujarat.gov.in (eApplication.aspx).
- GIC rejected 337 appeals and complaints in Jul-Dec 2024. The top causes were a duplicate second appeal (105), one appeal covering several applications (74), no first appeal filed (55), late filing (26 + 20), and appeals against central bodies (21). The helper should check for these before filing.
- Online filing: onlinerti.gujarat.gov.in is live (Sep 2026) in a 'phased roll-out'. Registration is required; the fee is paid by SBI net banking, card or wallet; first appeals are online and free. SMC's RTI page links to it. rtionline.gov.in is for central bodies only (Rs 10 fee) and not for SMC or the Collectorate.
- GIC in Sep 2026: the State Chief Information Commissioner post shows as vacant, with 5 commissioners sitting. Pending appeals rose from 624 to 1,039 by 31-08-2026. Satark Nagrik Sangathan estimated a wait of about 5 months (Jul 2024 to Jun 2025).
- SMC scale: 8,653 RTI requests received in 2025-26, with 353 PIOs and 74 appellate officers; the personal-information exemption s.8(1)(j) was invoked 14 times. In Q4 2025-26, 1,106 of 1,818 disposals (about 61%) were within the time limit, and 3,197 were pending at quarter end.
- The DPDP Act 2023 amends s.8(1)(j) and removes the public-interest test for personal information (DPDP Rules notified 14-11-2025, phased in over 18 months). Templates should ask for aggregate counts, not named individuals.
- GIC capped three members of one Surat family at 6 RTI applications a year each (order of 24-04-2025) for disproportionate filing. The helper should discourage bulk or catch-all requests.
- Courts follow different rules: the Gujarat District Courts RTI Rules 2025 charge Rs 50 per application (Rs 500 for tender or contract information), filed through the Gujarat High Court portal.

## RTI template candidates (Surat)

Each template corresponds to a gap in the dashboard. Before any template is used, confirm the PIO designation and address from the SMC PIO list dated 09-12-2025.

### T1. SMC municipal primary schools: enrolment and teachers

- **Gap it fills:** Education: no official enrolment, teacher or pupil-teacher-ratio data for SMC schools. municipalschoolboardsurat.org renders by JavaScript and holds no data, and the ~1.3 lakh student figure appears only in news.
- **Public authority:** Surat Nagar Prathmik Shikshan Samiti (Municipal School Board), Surat Municipal Corporation
- **Addressed to:** Public Information Officer, Surat Nagar Prathmik Shikshan Samiti (Administrative Officer's office), Surat. Confirm the PIO designation and address in the SMC PIO/AA list dated 09-12-2025.
- **Questions:**
  1. Number of students enrolled in Samiti schools by zone, medium and class (Balvatika to Std 8), as on 31-07-2025 and as on the latest 2026 date for which records exist.
  2. Number of schools run by the Samiti by zone and medium, with a school-wise list giving school name, UDISE code, ward and medium.
  3. Sanctioned and filled posts of HTAT principals, primary teachers and upper-primary teachers, by zone and medium, as on 31-07-2025.
  4. For each school, the number of usable classrooms and of functional toilets (boys and girls), as reported in the latest UDISE+ submission.
  5. Please supply the above in Excel/CSV if held electronically, by email or on pen drive, as the GAD circular of May 2025 allows.

### T2. Property tax demand, collection and arrears by ward

- **Gap it fills:** Finance: CityFinance and the budget books show only city-wide own revenue. Nothing shows property-tax performance by ward or zone.
- **Public authority:** Surat Municipal Corporation
- **Addressed to:** PIO, Assessment & Recovery (Property Tax) Department, Surat Municipal Corporation, Surat Mahanagar Seva Sadan, Surat. Confirm the designation in the PIO list dated 09-12-2025.
- **Questions:**
  1. Number of assessed properties (residential and non-residential) by zone and ward, as on 31 March 2024, 31 March 2025 and 31 March 2026.
  2. Property-tax demand raised, amount collected and arrears outstanding, by zone and ward, for FY 2023-24, 2024-25 and 2025-26.
  3. Total property-tax arrears written off or waived in each of those years, with the number and date of each resolution or order that authorised it.
  4. Please provide aggregate figures only, in Excel/CSV if held electronically; no taxpayer names are sought. If any part is held to be exempt, please supply the rest under section 10 and cite the section relied on.

### T3. Capital works: sanctioned vs spent, by ward and project

- **Gap it fills:** Finance: the weekly Revenue-Capital Budget Summary shows only zone totals and is overwritten every week. No spending is published by project or by ward.
- **Public authority:** Surat Municipal Corporation
- **Addressed to:** PIO, Accounts Department (Chief Accountant's office), Surat Municipal Corporation. The questions on works status may be transferred to the City Engineer's PIO under section 6(3).
- **Questions:**
  1. For FY 2024-25 and 2025-26, a list of all capital works sanctioned in the SMC budget, giving work ID, description, zone, ward, budget head, sanctioned amount, contractor, work-order date, amount paid up to 31-03-2026, and status.
  2. Allocation and use of councillor (ward) grants, ward by ward, for FY 2024-25 and 2025-26.
  3. The zone-wise Revenue-Capital Budget Summary figures, as shown on the SMC website, as on the last working day of each month of FY 2025-26, in Excel/CSV.

### T4. Vector-borne and water-borne disease cases by ward, 2023 onward

- **Gap it fills:** Health: SMC's Disease Reports tables end in 2022 and have no dengue or chikungunya series. Current case counts appear only in news.
- **Public authority:** Surat Municipal Corporation
- **Addressed to:** PIO, Health Department (Medical Officer of Health) / Vector Borne Diseases Control Department, Surat Municipal Corporation. Confirm which departmental PIO applies in the list dated 09-12-2025.
- **Questions:**
  1. Number of confirmed cases and of deaths from dengue, malaria (Pv/Pf), chikungunya, gastroenteritis, enteric fever, hepatitis and cholera, by month and zone (by ward if held), from Jan 2023 to date.
  2. Number of blood samples tested for malaria and for dengue in SMC facilities, month by month, over the same period.
  3. Number of mosquito-breeding notices issued and penalty amounts collected, by zone, from Jan 2024 to date.
  4. Aggregate counts only; no patient-identifying information is sought. If any part is withheld, please supply the rest under section 10.

### T5. Water supply service levels and water-quality test results

- **Gap it fills:** Water/health: SMC's Hydraulic Department page has only a historical narrative (up to about 2010). There is no current data on supply volume (MLD), per-person supply (LPCD), supply hours, non-revenue water or test results.
- **Public authority:** Surat Municipal Corporation
- **Addressed to:** PIO, Hydraulic Engineering Department, Surat Municipal Corporation. Confirm the designation in the PIO list dated 09-12-2025.
- **Questions:**
  1. Average daily water supplied (MLD) and average hours of supply, by zone, for each month of FY 2024-25 and 2025-26.
  2. Number of domestic water connections and of metered connections, by zone, as on 31-03-2026; and the estimated non-revenue water percentage for FY 2025-26, with the basis of the estimate.
  3. Number of drinking-water samples tested (bacteriological and chemical) and number found unfit, with the parameter that failed, by month and zone, for FY 2025-26.

### T6. Solid waste processing, segregation and Swachh Survekshan marks

- **Gap it fills:** Environment: SMC publishes monthly collection tonnage (up to Jul 2026) but nothing on segregation, processing or landfill. Swachh Survekshan 2024-25 gives only a league rank.
- **Public authority:** Surat Municipal Corporation
- **Addressed to:** PIO, Solid Waste Management Department, Surat Municipal Corporation.
- **Questions:**
  1. Tonnage processed each month by method (composting, RDF/waste-to-energy, recycling) and tonnage sent to landfill, from April 2024 to date.
  2. Percentage of households covered by door-to-door collection and percentage of waste segregated at source, by zone, as recorded for each quarter of FY 2025-26.
  3. Quantity of legacy waste remediated (MT) in each year from 2023-24 to 2025-26, and the quantity remaining as on 31-03-2026.
  4. A copy of the component-wise score sheet for Swachh Survekshan 2024-25 as received by SMC from MoHUA.

### T7. Ration-shop (PDS) allocation vs distribution in SMC zones

- **Gap it fills:** Food security: Surat city has no PDS district of its own; its zones 901-910 sit inside Surat district, and allocation and distribution figures are not published below district level.
- **Public authority:** District Supply Office, Collector Office, Surat (Food, Civil Supplies & Consumer Affairs Department, Government of Gujarat). This is a state public authority, not SMC.
- **Addressed to:** Public Information Officer, District Supply Office, Collector Office, Surat.
- **Questions:**
  1. Monthly allocation, lifting and distribution (in quintals) of wheat, rice, sugar and salt under NFSA/PMGKAY for each SMC-area zone (codes 901-910), from April 2024 to date.
  2. Number of AAY and PHH ration cards and beneficiaries, and number of active fair-price shops, by zone (901-910), as on 31-03-2026.
  3. Counts of fair-price shop inspections, irregularities found, and licences suspended or cancelled in zones 901-910 for FY 2024-25 and 2025-26.
  4. Please provide the above in Excel/CSV if held electronically.

### T8. Surat APMC price-reporting gaps

- **Gap it fills:** Food prices: Surat APMC reported on only 23 of 30 days on Agmarknet (and returned 0 rows on 25-09-2026). Its Old Sardar Market sub-yard reported nothing in 30 days, so the mandi tile has gaps.
- **Public authority:** Agricultural Produce Market Committee (APMC), Surat, a statutory market committee and so a public authority under section 2(h)
- **Addressed to:** Public Information Officer, Agricultural Produce Market Committee, Surat. Confirm the PIO; first appeals go to the APMC's designated appellate officer.
- **Questions:**
  1. Arrivals (in quintals) and minimum, maximum and modal prices by date and commodity, recorded at the main yard and at the Old Sardar Market sub-yard, from 1 August 2026 to date.
  2. For each yard, the dates between 1 August 2026 and the date of reply on which price data was not uploaded to Agmarknet, as recorded.
  3. Copies of any correspondence or file notings about price data not being uploaded to Agmarknet during that period.
  4. A copy of the order designating the officer responsible for Agmarknet data entry. If any part is withheld, please supply the rest under section 10.

### T9. Official SMC ward and zone boundaries in GIS format

- **Gap it fills:** Maps/governance: there is no official or open polygon file for SMC's 30 wards (datameet has none, and the SMC GIS viewer has no export), so ward-level maps cannot be drawn.
- **Public authority:** Surat Municipal Corporation
- **Addressed to:** PIO, Central Town Planning / GIS Cell, Surat Municipal Corporation. The Election section's PIO may hold the delimitation records, so expect a transfer under section 6(3).
- **Questions:**
  1. The current boundaries of all 30 SMC election wards and of all zones, in the digital format held (shapefile, KML or GeoJSON), on CD or pen drive or by email.
  2. The number and date of the notification that delimited the current 30 wards.
  3. The table mapping Census 2011 wards to the current election wards, if held.

### T10. SMC RTI timeliness by department, and past Patrak-7 returns

- **Gap it fills:** RTI tracker: SMC's annual return and Patrak-7 give only totals for the whole corporation, and Patrak-7 is overwritten every quarter. There is no department-level or historical quarterly pendency.
- **Public authority:** Surat Municipal Corporation
- **Addressed to:** PIO, RTI Cell, Surat Municipal Corporation, Surat Mahanagar Seva Sadan, Surat 395003. Confirm in the PIO list dated 09-12-2025.
- **Questions:**
  1. Copies of the Patrak-7 and Patrak-8 quarterly returns for every quarter from Q1 2023-24 to Q1 2026-27.
  2. For 2024-25 and 2025-26, by department and zone: applications received, disposed of within 30 days, disposed of after 30 days, pending beyond 30 days without reply, transferred under section 6(3), and first appeals received and allowed.
  3. An anonymised export of the above from the computerised RTI register, with no applicant names or addresses, in Excel/CSV if held. If any part is withheld, please supply the rest under section 10.

## Open questions (check in week 0-2)

- The claim that SMC and AMC are on onlinerti.gujarat.gov.in rests only on a May 2026 Counterview report and SMC's link to the portal. No one has logged in to check the list of authorities. The portal's FAQ also wrongly says second appeals go to the Central Information Commission.
- SMC's head-office address differs between sources (Muglisara vs Tapipura, and 'Shri Tapi Bhawan'). The PIO names in the 09-12-2025 list come out garbled because of the legacy font. Every template's addressee must be confirmed from a decoded copy of that list.
- It is not confirmed whether Surat Nagar Prathmik Shikshan Samiti and APMC Surat have their own PIOs or whether requests go through SMC and the state marketing board.
- Surat APMC's reliability is unclear: one 30-day scan found reports on 23 of 30 days, but the verifier's check on 25-09-2026 returned 0 rows. The data.gov.in mandi and air-quality APIs timed out from this environment.
- The rows of SMC's Revenue-Capital Budget Summary load through a background request whose endpoint has not been identified. Scraping it may need a headless browser.
- SMC presents Ukai dam as city data, but the state water department's PDF lists it under Tapi district (Songadh). The dashboard must label its geography.
- Surat ward polygons exist only in a third-party bharatlas viewer, with licence and origin unchecked. The boundary between DGVCL and Torrent Power (TPL-D(S)) inside SMC limits has not been verified.
- SMC's RTI requests fell from 15,213 in 2024-25 to 8,653 in 2025-26. This may be an artefact of when the return was uploaded rather than a real drop.
- Some sources were seen only in search results and never fetched: the CRISIL and India Ratings rationales, the PIB Swachh Survekshan and Ease of Living releases, the NCRB 2023 PDF and the GPCB station list. The Suman High School PDFs and the green-bond offer document were not parsed.
- The scores are the researchers' judgement on a 0-10 scale. The health/environment score moved from 5/5 to 6.5/4.5 after the verifier's corrections; with the original scores Surat still leads 6.38 to 5.68. The upstream Gujarat map uses 2011 boundaries; Surat's polygon is probably current but has not been checked.

## Method

- **Dimensions:** seven, each researched for both cities: budget, education, food prices, health and environment, governance, RTI, and the remaining district modules.
- **Verification:** an adversarial verifier re-checked the claims that decide the pick. It overturned 4 of them: one CityFinance claim, two health-data claims, and one on the AMC Statistical Outline.
- **Scores:** judgement on a 0-10 ease-of-building scale, not measurements.
- **Robustness:** Surat also leads with equal weights (6.57 vs 5.57) and with RTI left out (6.44 vs 5.21).
