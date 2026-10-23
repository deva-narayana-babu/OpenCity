# Budget and public finance

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
- **After verification:** Surat 7.5, Ahmedabad 5.5

**Researcher's rationale:** Surat is easier to build for. It has current English text balance sheets, a weekly budget-vs-actuals feed by zone, CityFinance XLSX files through 2023-24, and a 2025 bond offer document, all on a site that fetches cleanly. Ahmedabad has the longer budget archive (from 2005), but its latest balance sheet is scanned, its budgets are in Gujarati numerals, its CityFinance coverage is unconfirmed, and its site needs the TLS workaround.

**Verifier's reasoning:** CityFinance does have AMC audited accounts up to 2023-24 (the slug is 'amdavad'), so that row is a tie and Ahmedabad gains. Surat keeps a clear lead: weekly budget-vs-actuals by zone, a text balance sheet for FY26 (URL corrected) and a live bond offer document. AMC's FY26 balance sheet is confirmed to be a scan.

## City-by-city comparison

| Metric | Surat | Ahmedabad | Edge |
|---|---|---|---|
| Budget book years online | 2021-22 to 2026-27 (6 years), plus Outcome Budgets for 2022-24 | 2005-06 to 2026-27 (22 years) | Ahmedabad |
| Budget book machine-readability | 778-page PDF. Numbers extract, but the Gujarati text is a legacy font and comes out garbled | 334-page Unicode Gujarati PDF with Gujarati numerals. Needs digit conversion; English copies exist for some years up to 2023-24 | Tie |
| In-year budget execution (BE/RE/actuals) | Weekly HTML summary by zone (updated 27/09/2026): Actuals 24-25, BE/RE 25-26, tentative actuals 25-26 and 26-27 | Nothing similar found; only annual books | Surat |
| Latest balance sheet format | FY2025-26 English text PDF, 4 pages, parses cleanly | FY2025-26 scanned 49-page PDF, needs OCR | Surat |
| CityFinance audited accounts | 8 audited years up to 2023-24, XLSX export | Page shows no data (slug unconfirmed) | Surat |
| Credit rating / bonds | CRISIL and India Ratings AA+ (2025); public green-bond offer document Sep 2025 hosted on SMC site | CRISIL AA+ Rs 200 cr green bond (Feb 2024); BSE placement memo | Surat |
| Site access | Fetches cleanly over standard TLS | Needs legacy TLS renegotiation; files served via opaque ViewFile IDs | Surat |
| Debt visibility | Balance sheet shows Rs 200 cr secured and about Rs 1,059 cr unsecured loans (31-03-2026) | Only in the scanned balance sheet or rating documents | Surat |

## All sources found

| Metric | City | Source | URL | Format | Granularity | Latest period | Ease (0-5) | Fetched live | Access notes |
|---|---|---|---|---|---|---|---|---|---|
| Annual budget books (General Board, approved) | Surat | SMC Accounts Dept - Budget page | https://www.suratmunicipal.gov.in/Departments/Accounts/Budget | PDF; the 2026-27 book is 778 pages. Numbers extract fine, but the Gujarati text uses a legacy non-Unicode font and comes out garbled | City-wide by fund and head; Outcome Based Budget only for 2022-23 and 2023-24 | 2026-27 | 3 | yes | Books cover 2021-22 to 2026-27. Direct PDF: /Content/Documents/Departments/Accounts/2026-27/BudgetBookGeneralBoard_2026_27.pdf. You need to map headings by hand, but the numeric columns can be parsed. |
| Revenue/capital budget vs actuals, by zone, weekly | Surat | SMC Revenue-Capital Budget Summary (Rs '000) | https://www.suratmunicipal.gov.in/Departments/Accounts/CapitalRevenueBudgetSummary | HTML table, filled in by JavaScript | HQ + 10 zones | Weekly update, last on 27/09/2026 (Actuals 24-25, Original/Revised 25-26, Tentative actuals 25-26 and 26-27) | 4 | yes | The raw HTML has only the headers, so the rows come from a background (XHR) request. Find that endpoint and you get near-live budget execution by zone, which no other source here offers. |
| Audited balance sheet | Surat | SMC Balance Sheet page | https://www.suratmunicipal.gov.in/Departments/Accounts/BalanceSheet_25_26.pdf | Text PDF in English, 4 pages, accrual format | City (SMC), schedule level | As on 31-03-2026 (FY 2025-26), with 2024-25 alongside | 4 | yes | The index at /Departments/Accounts/BalanceSheet lists years back to 2015-16 and earlier. Text extracts cleanly with pdftotext -layout. Loans: Rs 200 cr secured (bond) plus about Rs 1,059 cr unsecured in FY26. |
| Standardised audited accounts (income, expenditure, own revenue) | Surat | MoHUA/Janaagraha CityFinance - Surat | https://www.cityfinance.in/municipal-data/city/surat | Dashboard with XLSX export | ULB (SMC), standard line items | Audited 2023-24 | 5 | yes | Audited years listed: 2015-16, 2016-17, 2017-18, 2019-20, 2020-21, 2021-22, 2022-23, 2023-24. FY24: total revenue Rs 4,407 cr, expenditure Rs 4,349 cr, own revenue Rs 3,404 cr. Comparable across cities. |
| Credit rating rationale (clean finance tables) | Surat | CRISIL Ratings - Surat Municipal Corporation rationale, 17 Mar 2025 | https://www.crisil.com/mnt/winshare/Ratings/RatingList/RatingDocs/SuratMunicipalCorporation_March%2017_%202025_RR_364831.html | HTML | City (SMC) | 2025 | 4 | no | Found via search, not fetched. Rated CRISIL AA+/Stable. India Ratings IND AA+ (Jan 2025) also exists. |
| Municipal (green) bond offer document | Surat | SMC Green Bond Offer Document dated 18 Sep 2025 | https://www.suratmunicipal.gov.in/Content/Documents/Departments/Accounts/SMCBond/GreenBond/Surat_Municipal_Corporation_Offer_Document_dated_September_18_2025.pdf | PDF (SEBI-format offer document) | City: multi-year revenue, expenditure, tax collection and debt tables | Sep 2025 | 4 | no | Found via search, not fetched. A public NCD issue (Oct 2025). The bond index is at /Departments/Accounts/SMCBondInformation. Offer documents usually carry 3-5 years of clean financials. |
| Annual budget books | Ahmedabad | AMC - Budget page | https://ahmedabadcity.gov.in/SP/Budget | PDF. The 2026-27 'Budget A' is 334 pages of Unicode Gujarati with Gujarati numerals. Some years also have an English copy | City-wide; revenue/capital income and expenditure abstracts | 2026-27 (draft plus Standing Committee resolution dated 10-02-2026) | 3 | yes | Books run 2005-06 to 2026-27, the longest series. English copies exist for 2018-19, 2019-20 and 2021-22 to 2023-24. The 2026-27 PDF is at /ViewFile/ViewFile?TYPE=FileRepository,2583. Needs the legacy-TLS curl. Numerals need conversion from Gujarati to Arabic digits, and letter shaping breaks in extraction. |
| Balance sheet and audit report | Ahmedabad | AMC - Balance Sheet page | https://ahmedabadcity.gov.in/SP/BalanceSheet | PDF. The FY2025-26 file is a scanned image, 49 pages, with almost no text layer | City (AMC), fund-wise; audit reports for 2018-19 to 2023-24 | As on 31-03-2026 (FY 2025-26) | 2 | yes | A long series from 2006 to 2026. The FY26 file is /ViewFile/ViewFile?TYPE=FileRepository,2689 and pdftotext returned about 120 characters. Needs OCR. Some older years may have a text layer. |
| Standardised audited accounts | Ahmedabad | CityFinance - Ahmedabad | https://www.cityfinance.in/municipal-data/city/ahmedabad | Dashboard | ULB | Unknown | 2 | no | This URL loaded but said 'Financial data is unavailable for selected entity'. The page slug may be wrong (for example 'amdavad'), so AMC coverage there is still unconfirmed. |
| Credit rating rationale / bond placement memo | Ahmedabad | CRISIL rationale 29 Feb 2024; India Ratings press release; BSE placement memorandum Feb 2024 | https://www.crisil.com/mnt/winshare/Ratings/RatingList/RatingDocs/AhmedabadMunicipalCorporation_February%2029,%202024_RR_337695.html | HTML / PDF | City (AMC) | 2024 (CRISIL); India Ratings item reportedly 2026 | 4 | no | Found via search, not fetched. Rs 200 cr green bond rated CRISIL AA+/Stable. Placement memo: https://bond.bseindia.com/PPMFiles/2024/FEB/PPM/816/7646.pdf |
| Budget headline figures (news) | Ahmedabad | DeshGujarat - AMC Rs 18,518 cr budget 2026-27 | https://deshgujarat.com/2026/02/10/amc-presents-18518-crore-budget-for-2026-27/ | News HTML | City headline | Feb 2026 | 1 | no | Found via search. Draft Rs 17,018 cr; Standing Committee raised it to Rs 18,518 cr. Useful for cross-checking only. |

## Data gaps: candidates for RTI

| Metric | City | Public authority | RTI question |
|---|---|---|---|
| Property tax demand, collection and arrears by zone and ward | Surat | Surat Municipal Corporation - PIO, Assessment & Recovery (Property Tax) Dept, Head Office | Provide, zone-wise and ward-wise for FY 2023-24, 2024-25 and 2025-26: number of assessed properties, property-tax demand raised, amount collected, and arrears outstanding as on 31 March, in Excel/CSV if held electronically. |
| Property tax demand, collection and arrears by zone and ward | Ahmedabad | Amdavad Municipal Corporation - PIO, Property Tax Dept (Revenue), Central Office | Provide, zone-wise and ward-wise for FY 2023-24 to 2025-26: property-tax demand, collection, arrears as on 31 March, and number of tenements assessed, in electronic spreadsheet form. |
| Budget execution (actual spend vs budget) by capital project | Ahmedabad | Amdavad Municipal Corporation - PIO, Finance Department (Chief Accountant) | For FY 2025-26, provide for each capital-budget work/project: budget estimate, revised estimate and actual expenditure as on 31-03-2026, plus zone and department, as a spreadsheet. |
| Smart Cities Mission funds received and utilised | Both | Surat Smart City Development Ltd / Ahmedabad Smart City Development Ltd - PIO (SPV); appeal to SMC/AMC | Provide year-wise from FY 2016-17 to 2025-26: central and state funds received, own/convergence funds, amount utilised, and project-wise sanctioned cost, expenditure and completion status under Smart Cities Mission. |
| Machine-readable balance sheet and schedules | Ahmedabad | Amdavad Municipal Corporation - PIO, Finance Department | Provide the audited balance sheet, income and expenditure account and all schedules for FY 2024-25 and 2025-26 in the electronic form held (Excel or text PDF), since the published copy is a scanned image. |

## Challenges

- Both budget books are Gujarati-first: SMC's text is a legacy non-Unicode font that comes out garbled, and AMC uses Gujarati numerals. You need digit conversion and hand-built mappings of budget heads to extract anything.
- SMC's weekly budget summary fills its table by JavaScript. The underlying request (XHR) endpoint has to be reverse-engineered before it can be scraped, and it may change.
- AMC's site needs legacy TLS renegotiation, and its files sit behind opaque ViewFile?TYPE=FileRepository,N IDs, so automated fetching breaks easily.
- AMC's latest balance sheet (FY26) is scanned and needs OCR. CityFinance showed no AMC data at the tried URL, so cross-city comparison of standardised accounts is unconfirmed.
- Scope mismatch: SMC/AMC finance covers the municipal area only, while the upstream model is district-level. Smart City SPVs and urban development authorities (SUDA/AUDA) keep separate books.

## Verifier checks

| Claim | Verdict | Evidence | Correction |
|---|---|---|---|
| SMC audited balance sheet FY2025-26 is a 4-page English text PDF at https://www.suratmunicipal.gov.in/Departments/Accounts/BalanceSheet_25_26.pdf, showing Rs 200 cr secured and about Rs 1,059 cr unsecured loans. | corrected | The cited URL returned HTTP 404 (HTML). The index links /Content/Documents/..., and that path returned 200, a 4-page PDF of 2.6 MB. It has a text layer headed 'BALANCE SHEET AS ON 31ST MARCH, 2026', with secured loans 2,00,00,00,000 and unsecured 10,59,40,69,467. | Use https://www.suratmunicipal.gov.in/Content/Documents/Departments/Accounts/BalanceSheet_25_26.pdf. The content claims hold. |
| SMC Revenue-Capital Budget Summary is updated weekly by zone (HQ + 10 zones), last on 27/09/2026. Surat edge. | confirmed | Live fetch returned 200. The page says 'Weekly Update (Last on 27/09/2026)' and lists All Zone, HQ, West, Central, North, East-A, South-A, Athwa, South East, East-B and South-B (Kanakpur). The table rows still load via XHR. |  |
| CityFinance has no data for Ahmedabad ('Financial data is unavailable'), so the CityFinance row is a Surat edge. | refuted | CityFinance's own ULB list gives AMC the slug 'amdavad' (code GJ167, id 5e4a75dc47cb2749e5a56bdf), not 'ahmedabad'. /api/v1/ledger/lastUpdated?ulb=<AMC id> returns success, year 2023-24. Surat's returns the same year, 2023-24. | AMC standardised audited accounts are on CityFinance up to 2023-24 at /municipal-data/city/amdavad (slug from the ULB list; checked via the API). The row is a Tie. |
| AMC FY2025-26 balance sheet (ViewFile?TYPE=FileRepository,2689) is a scanned 49-page PDF with almost no text layer. | confirmed | Re-downloaded with legacy TLS: HTTP 200, 14,079,038 bytes, 49 pages, producer iLovePDF. pdftotext gives 123 characters, and pdfimages shows full-page JPEGs (1654x2326 at 200 ppi). It needs OCR. |  |
| AMC budget books run from 2005-06 to 2026-27, the longest series. Ahmedabad edge. | confirmed | Live /SP/Budget (legacy TLS, 200) lists year labels from 2005-06 through 2026-27. The local 2026-27 Budget A PDF is 334 pages. |  |
| SMC green bond offer document dated 18 Sep 2025 is hosted on the SMC site (verified_live=false). | confirmed | A HEAD request to /Content/Documents/Departments/Accounts/SMCBond/GreenBond/Surat_Municipal_Corporation_Offer_Document_dated_September_18_2025.pdf returned HTTP 200, application/pdf, 14.2 MB. Its content was not parsed. |  |

## Saved copies

18 source documents behind this page are saved in [reference/](../../reference/README.md), unchanged from the date they were downloaded. Their source URLs, checksums and licence notes are in [reference/manifest.csv](../../reference/manifest.csv).

| File | What it is | City | Period |
|---|---|---|---|
| [budget/amc-balance-sheet-2025-26.pdf](../../reference/budget/amc-balance-sheet-2025-26.pdf) | Final balance sheet as on 31-03-2026 (scanned images, 49 pages) | Ahmedabad | FY2025-26 |
| [budget/amc-balance-sheet-audit-report-2023-24.pdf](../../reference/budget/amc-balance-sheet-audit-report-2023-24.pdf) | Balance sheet 2023-24 audit report (review of standalone financial statements) | Ahmedabad | FY2023-24 |
| [budget/amc-balance-sheet-index-2026-09-27.html](../../reference/budget/amc-balance-sheet-index-2026-09-27.html) | AMC Balance Sheet page: index of balance sheets 2005-06 to 2025-26 and audit reports | Ahmedabad | snapshot 2026-09-27 |
| [budget/amc-budget-2023-24-english.pdf](../../reference/budget/amc-budget-2023-24-english.pdf) | Final budget 2023-24 (English edition) with sanction resolution | Ahmedabad | FY2023-24 |
| [budget/amc-budget-a-2025-26.pdf](../../reference/budget/amc-budget-a-2025-26.pdf) | Budget 2025-26 'A' (Gujarati) | Ahmedabad | FY2025-26 |
| [budget/amc-budget-a-2026-27.pdf](../../reference/budget/amc-budget-a-2026-27.pdf) | Budget 2026-27 'A' (Gujarati) with standing committee resolutions and MC's note | Ahmedabad | FY2026-27 |
| [budget/amc-budget-index-2026-09-28.html](../../reference/budget/amc-budget-index-2026-09-28.html) | AMC Budget page: index of budget reports 2005-06 to 2026-27 | Ahmedabad | snapshot 2026-09-28 |
| [budget/amc-finance-department-about-2026-09-27.html](../../reference/budget/amc-finance-department-about-2026-09-27.html) | About AMC Finance Department: branches and list of finance officers | Ahmedabad | snapshot 2026-09-27 |
| [budget/india-mohua-cityfinance-ulb-list-2026-09-27.json](../../reference/budget/india-mohua-cityfinance-ulb-list-2026-09-27.json) | CityFinance ULB master list API response: codes, slugs, area and population of every ULB (SMC GJ003 'surat', AMC GJ167 'amdavad') | India | snapshot 2026-09-27 |
| [budget/smc-balance-sheet-2025-26.pdf](../../reference/budget/smc-balance-sheet-2025-26.pdf) | Balance sheet FY2025-26 | Surat | FY2025-26 |
| [budget/smc-balance-sheet-index-2026-09-28.html](../../reference/budget/smc-balance-sheet-index-2026-09-28.html) | Balance sheet index page (FY2005-06 to FY2025-26) | Surat | snapshot 2026-09-28 |
| [budget/smc-budget-book-general-board-2026-27.pdf](../../reference/budget/smc-budget-book-general-board-2026-27.pdf) | Budget Book (General Board) 2026-27, 778 pages | Surat | FY2026-27 |
| [budget/smc-budget-centre-codes-2026-09-27.html](../../reference/budget/smc-budget-centre-codes-2026-09-27.html) | List of budget centres (BCNT codes and names) | Surat | snapshot 2026-09-27 |
| [budget/smc-budget-index-2026-09-27.html](../../reference/budget/smc-budget-index-2026-09-27.html) | Budget page: budget books 2021-22 to 2026-27 and outcome budgets | Surat | snapshot 2026-09-27 |
| [budget/smc-outcome-based-budget-2023-24.pdf](../../reference/budget/smc-outcome-based-budget-2023-24.pdf) | Outcome Based Budget 2023-24 | Surat | FY2023-24 |
| [budget/smc-property-tax-recovery-stats-2006-07-to-2009-10.html](../../reference/budget/smc-property-tax-recovery-stats-2006-07-to-2009-10.html) | Property tax demand and recovery statistics 2006-07 to 2009-10 | Surat | FY2006-07 to FY2009-10 |
| [budget/smc-revenue-capital-budget-summary-2026-09-28.html](../../reference/budget/smc-revenue-capital-budget-summary-2026-09-28.html) | Revenue-Capital Budget Summary page (zone selector, column headers, weekly update date) | Surat | snapshot 2026-09-28 |
| [education/amc-school-board-budget-2026-27.pdf](../../reference/education/amc-school-board-budget-2026-27.pdf) | AMC School Board budget book 2026-27 with establishment schedule (Gujarati) | Ahmedabad | FY2026-27 |
