# Food prices and food security

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

- **Researcher:** Surat 6, Ahmedabad 7
- **After verification:** Surat 6, Ahmedabad 7

**Researcher's rationale:** Both cities have a live daily mandi JSON feed, a DoCA price centre and a CPI-IW centre. Ahmedabad wins on two points. Its main APMC reports more consistently. Its PDS data sits in a separate 'Ahmedabad City' district that matches AMC boundaries. Surat's Agmarknet district is polluted by Tapi markets, and its PDS city data has to be summed from zones inside the district.

**Verifier's reasoning:** Confirmed live: Ahmedabad APMC reported on 25-09-2026 and Surat APMC did not. Surat's Agmarknet list includes Tapi markets. IMPDS shows AHMEDABAD CITY as a separate district.

## City-by-city comparison

| Metric | Surat | Ahmedabad | Edge |
|---|---|---|---|
| Main city APMC daily prices (Agmarknet) | Surat APMC: reported on 23 of 30 days, 40 commodities. The Old Sardar Market sub-yard reported nothing in 30 days. | Ahmedabad APMC: 27 of 30 days, 43 commodities, plus Vasana (Chimanbhai Patel) onion/potato yard on 27 days | Ahmedabad |
| District mandi coverage / geography match | 21 of 33 listed markets reported, but about 12 of those are really in Tapi district (legacy mapping), which inflates the count and needs filtering | 7 of 21 listed markets reported. Viramgam, Mandal and others are rural, but the city yards are clearly labelled | Ahmedabad |
| DoCA daily retail price centre | Yes (reporting centre) | Yes (reporting centre) | Tie |
| Labour Bureau CPI-IW centre | Yes | Yes | Tie |
| PDS unit matches the municipal corporation | No. City zones 901-910 sit as talukas inside Surat district, and city totals must be summed | Yes. 'Ahmedabad City' is a separate PDS district with its own Food Controller office, split by AMC zones | Ahmedabad |
| National IMPDS district tables | Only 'SURAT' (district incl. city) | 'AHMEDABAD CITY' listed separately from rural 'AHMADABAD' | Ahmedabad |
| ONORC migrant portability signal (story value) | 7,313 inter-state portability transactions (Sep 2026 snapshot), the higher of the two | 5,139 (Ahmedabad City) | Surat |
| Municipal food data (SMC/AMC) | None found; food supply is a state and APMC function | None found; same | Tie |

## All sources found

| Metric | City | Source | URL | Format | Granularity | Latest period | Ease (0-5) | Fetched live | Access notes |
|---|---|---|---|---|---|---|---|---|---|
| Daily APMC mandi prices and arrivals (min/max/modal Rs/qtl) by market and commodity | Both | Agmarknet v2 JSON backend (api.agmarknet.gov.in market-report/daily) | https://api.agmarknet.gov.in/v1/prices-and-arrivals/market-report/daily | JSON via POST {date, marketIds, stateIds:[11]}; no key | APMC market x commodity x variety x day | 2026-09-26 (fetched live this session) | 4 | yes | Undocumented backend of agmarknet.gov.in SPA, needs Origin/Referer headers. In a 30-day scan (28 Aug-26 Sep 2026), Surat APMC reported 23 days/40 commodities and Ahmedabad APMC 27 days/43 commodities. Every Surat/Ahmedabad market is flagged api_allowed_market=false. |
| Daily mandi prices (same Agmarknet feed, official open-data API) | Both | data.gov.in: Current Daily Price of Various Commodities from Various Markets (Mandi) | https://www.data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi | REST API JSON/CSV/XML (resource 9ef84268-d588-465a-a308-a864a43d0070); sample key shown on page | Market x commodity, current day only | Dataset page loads (2026-09-28); API data not retrieved | 3 | yes | Dataset page returned 200, but API calls timed out after 40-60s this session. A prior run got repeated 429/502/504 errors with the sample key. Too unreliable for a production feed; use it only as a backup and cache it. |
| Agmarknet market master (market IDs, district, principal/sub yard) | Both | Agmarknet portal | https://agmarknet.gov.in/ | SPA; JSON filter endpoints | Market | current | 4 | yes | Lists 33 markets under 'Surat' district and 21 under 'Ahmedabad'. The Surat list still includes markets now in Tapi district (Vyara, Songadh, Uchhal, Nizar, Kukarmunda, Valod). Filter these out. |
| Daily retail/wholesale prices of 22+ essential commodities (DoCA Price Monitoring Cell) | Both | Dept of Consumer Affairs PMC, fcainfoweb.nic.in reports | https://fcainfoweb.nic.in/reports/report_menu_web.aspx | ASP.NET HTML report (postback form, export via page); no API | Reporting centre x commodity x day | current (portal live 2026-09-28) | 3 | yes | Centre list includes Ahmedabad, Rajkot and Surat (plus Bhuj, Vapi, Bilimora and others) as Gujarat reporting centres. The scraper must replay the ASP.NET __VIEWSTATE postback. |
| CPI-IW centre index (cost-of-living/food inflation proxy) | Both | Labour Bureau, Centre-wise General Index | https://labourbureau.gov.in/centre-wise-general-index | HTML table + monthly PDFs | Centre x month | Table period not labelled clearly; linked PDFs go up to Mar 2023 | 3 | yes | Ahmedabad and Surat are both CPI-IW centres, along with Bhavnagar, Rajkot and Vadodara. General index only; food sub-index would need the monthly press release. Check which base year the table uses before charting. |
| FPS-level allocation, permit, stock, delivery challan, sale register | Gujarat-state | Gujarat FCSCAD iPDS Social Audit portal | https://ipds.gujarat.gov.in/PDSSocialAudit/ | ASP.NET dropdown HTML (Gujarati), per-FPS drill-down | District > taluka/zone > FPS > month | current | 2 | yes | 'Ahmedabad Shaher' (Ahmedabad City) is its own PDS district (code 27), split by AMC-aligned zones. Surat city has no district of its own: its zones 901-910 sit as talukas inside Surat district. Labels are Gujarati. Scraping needs postbacks. |
| Ration card abstract / beneficiaries by district-month | Gujarat-state | Gujarat iPDS NFSA Ration Card Abstract | https://ipds.gujarat.gov.in/Register/frm_RationCardAbstract.aspx | HTML form behind CAPTCHA | District x month | Month selector offers 2026 months up to October | 2 | yes | CAPTCHA-gated, so it cannot be automated and must be collected by hand. The iPDS dashboard showed statewide 1.11 cr ration cards and 15,478 FPS dealers, with no district split. |
| ONORC portability transactions; ration cards/beneficiaries/transactions by district | Both | IMPDS / Annavitran (NIC, DFPD) | https://impds.nic.in/ | HTML tables | District (incl. 'AHMEDABAD CITY' separate from 'AHMADABAD'; 'SURAT' combined) x month | Sep 2026 (page snapshot) | 3 | yes | The Gujarat inter-state portability table showed 7,313 transactions for Surat and 5,139 for Ahmedabad City (Surat's migrant-worker signal). Some sub-pages have captchas. |
| National NFSA FPS count, e-PoS, allocation vs offtake reports | National | NFSA portal (DFPD) | https://nfsa.gov.in/ | HTML report pages | State, some district | current | 3 | yes | Portal loads (200). Allocation and offtake are published mainly at state level, so district or city offtake has to come from iPDS or an RTI request. |

## Data gaps: candidates for RTI

| Metric | City | Public authority | RTI question |
|---|---|---|---|
| Monthly PDS allocation vs offtake (wheat/rice) per FPS zone, city | Surat | District Supply Officer, Surat (Collectorate), PIO under Food, Civil Supplies & Consumer Affairs Dept, Gujarat | Provide month-wise allocation, lifting and distribution (quintals) of wheat, rice, sugar and salt under NFSA/PMGKAY for each SMC-area zone (codes 901-910) from April 2024 to date, in soft copy (Excel). |
| Monthly PDS allocation vs offtake, ration cards and FPS count by AMC zone | Ahmedabad | Food Controller, Ahmedabad City (Food & Civil Supplies office), PIO | Provide zone-wise numbers of AAY/PHH/NFSA ration cards and beneficiaries, number of active FPS, and month-wise allocation vs distribution of foodgrains for April 2024 to date, in Excel. |
| FPS inspections, licence suspensions and complaints | Both | Directorate of Food & Civil Supplies, Gujarat (state PIO), and the District Supply Officer, Surat / Food Controller, Ahmedabad City | For 2023-24 to date, give the number of FPS inspections, irregularities found, licences suspended or cancelled, and PGRS complaints received and resolved, broken down by zone of Surat city and Ahmedabad city. |
| Surat Old Sardar Market sub-yard prices not reported to Agmarknet | Surat | Agricultural Produce Market Committee, Surat (PIO), cc Gujarat State Agricultural Marketing Board | Provide daily commodity-wise arrivals and min/max/modal prices recorded at the Old Sardar Market sub-yard from 1 Aug 2026 to date, and state why this data was not uploaded to Agmarknet. |
| DoCA centre-level retail price submissions (raw) | Both | Food, Civil Supplies & Consumer Affairs Dept, Gujarat (state price reporting cell PIO) | Provide the daily retail price returns for the 22 essential commodities submitted to the DoCA Price Monitoring Division for the Surat and Ahmedabad centres, Jan 2025 to date, including the markets or shops surveyed. |

## Challenges

- data.gov.in mandi API (sample key) timed out or returned 429/502/504 errors repeatedly. Use the Agmarknet JSON backend instead: it is undocumented and can change without notice, so cache its data daily.
- Agmarknet 'Surat' district still contains Tapi-district markets (Vyara, Songadh, Uchhal, Nizar, Kukarmunda, Valod). Keep a manual market allowlist per city.
- Gujarat iPDS data is Gujarati-labelled ASP.NET behind postbacks, and the ration card abstract is CAPTCHA-gated, so it cannot be fully automated.
- DoCA fcainfoweb reports need ASP.NET VIEWSTATE replay. The CPI-IW centre table is only the general index, and its base year and period need checking before charting.
- Unit mismatch: food data sits at APMC, district or PDS-zone level, not municipal wards. Surat PDS must be summed across zones 901-910, while Ahmedabad City lines up with AMC zones.

## Verifier checks

| Claim | Verdict | Evidence | Correction |
|---|---|---|---|
| The Agmarknet JSON backend is live. Ahmedabad APMC reports more consistently than Surat APMC, and Agmarknet's 'Surat' list includes Tapi-district markets. | confirmed | A POST for 25 Sep 2026 over all 54 Surat and Ahmedabad market IDs succeeded. Ahmedabad APMC returned 36 rows, Vasana 5, plus Viramgam, Mandal and Sanad. Surat APMC returned 0 rows. The Surat list returned Songadh, Songadh (Badarpada) and Songadh (Umrada), which are in Tapi district. |  |
| IMPDS lists 'AHMEDABAD CITY' separately from rural 'AHMADABAD', while 'SURAT' is combined. Sep 2026 portability: Surat 7,313, Ahmedabad City 5,139. | confirmed | The IMPDS Gujarat table (September 2026) saved from impds.nic.in earlier this session shows AHMADABAD total 412, AHMEDABAD CITY 5139 and SURAT 7313. It was not re-fetched live because of the call budget. |  |
