# Education

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

- **Researcher:** Surat 5, Ahmedabad 7
- **After verification:** Surat 5, Ahmedabad 7

**Researcher's rationale:** National sources (UDISE+, PGI-D, PARAKH, GSEB, RTE) are the same for both cities. The difference is the municipal school board. AMC's board publishes a current (Jul 2025) zone x class enrolment table and teacher counts as scrapeable HTML. Surat's board site is JS-only and has no data. Surat's only advantage is Suman High School result PDFs.

**Verifier's reasoning:** Confirmed that AMC's board has current (31-07-2025) enrolment and teacher counts as scrapeable HTML, while Surat's board publishes nothing crawlable. National sources are the same for both.

## City-by-city comparison

| Metric | Surat | Ahmedabad | Edge |
|---|---|---|---|
| Municipal primary enrolment published | No crawlable data. The board site (municipalschoolboardsurat.org) is a JS-only shell; the enrolment figure (~1.3 lakh) appears only in news | Zone x class HTML table as of 31-07-2025: 172,576 students | Ahmedabad |
| Municipal teacher counts / PTR | Not found publicly | Zone- and medium-wise HTAT/primary/upper-primary counts, 4,653 total (31-07-2025), so a PTR can be computed | Ahmedabad |
| Municipal secondary schools and board results | SMC hosts Suman High School student details and a 5-year result summary (PDF) | No equivalent found on the AMC board site | Surat |
| Site accessibility for scraping | suratmunicipal.gov.in fetches cleanly, but the school board is on a separate JS-rendered site | amcschoolboard.org is WordPress, fetches with plain curl and has a wp-json API, avoiding the ahmedabadcity.gov.in TLS quirk | Ahmedabad |
| UDISE+ / PGI-D district data | Surat district covered | Ahmedabad district covered | Tie |
| PARAKH 2024 learning outcomes | District card via JS dropdown; state PDF only static | Same | Tie |
| GSEB SSC/HSC results | District-level via GSEB statistics | Same, plus a City vs Rural split, which matches AMC better | Ahmedabad |
| RTE 25% admissions | State portal only (503 off-season) | State portal, plus AMC board posts EWS/SEBC/ST waiting-list PDFs (2026-02) | Ahmedabad |

## All sources found

| Metric | City | Source | URL | Format | Granularity | Latest period | Ease (0-5) | Fetched live | Access notes |
|---|---|---|---|---|---|---|---|---|---|
| Municipal primary school enrolment by zone x class (Balvatika-Std 8) and teacher counts (HTAT/primary/upper-primary) by zone and medium | Ahmedabad | AMC School Board (Nagar Prathmik Shikshan Samiti, Ahmedabad) - Student / Teacher Data List | https://www.amcschoolboard.org/student-teacher-data-list/ | HTML tables (Gujarati headers, Latin digits) | 12 zones/medium-wings x class | As of 31-07-2025 | 4 | yes | Fetched this session with plain curl (no TLS quirk, unlike ahmedabadcity.gov.in). Total 172,576 students, 4,653 teachers (289 HTAT). Std 3 column looks anomalously low (7,842 vs ~20k in adjacent grades) - flag as a data-quality issue. Scrapeable. |
| AMC school list (school names/addresses) | Ahmedabad | AMC School Board - 453 school list PDF | https://www.amcschoolboard.org/wp-content/uploads/2025/11/453-school-list.pdf | PDF | School | Uploaded 2025-11 | 3 | no | Linked from the board homepage (fetched); PDF itself not downloaded. Also a School-List-2023.pdf. The board site is WordPress, so /wp-json/ may allow listing uploads. |
| Municipal primary school board (enrolment, schools, teachers) | Surat | Municipal School Board Surat (Surat Nagar Prathmik Shikshan Samiti) website | https://municipalschoolboardsurat.org/ | JS-rendered Next.js site (zibma CMS); no data in the served HTML | Unknown | Unknown | 2 | yes | Linked as 'Primary' from the SMC Education menu. Returns 200, but the HTML is an empty shell (title only), so it needs a headless browser. No enrolment/teacher table found. Press reports ~270-318 schools, ~1.3 lakh students (news only). |
| SMC secondary school (Suman High Schools): student details, 5-year result summary, teaching staff | Surat | SMC Services > Education > Secondary (Suman High School) | https://www.suratmunicipal.gov.in/Services/SumanHighSchool | HTML pages + PDFs (StudentsDetails.pdf, Last5YearsResultSummary.pdf) | Suman High School network | Unknown (PDFs not opened) | 3 | yes | The page was fetched. PDF links are at /Content/Documents/Services/Education/SumanHighSchool/ but were not downloaded. AMC has no comparable secondary-school result disclosure found. |
| UDISE+ school, enrolment, teacher and infrastructure indicators | National | UDISE+ Dashboard (MoE) | https://dashboard.udiseplus.gov.in/ | SPA dashboard; report module with Excel/PDF exports | District (Surat, Ahmedabad) and block; not municipal-corporation level | Not confirmed this session (usually 2024-25) | 3 | yes | Returns 200. It is JS-rendered, so exports need manual download or reverse-engineering the API. Data is district-level: Ahmedabad district includes the AMC area plus rural blocks. Both cities are symmetric here. |
| Performance Grading Index - District (PGI-D) | National | PGI portal (UDISE+) | https://pgi.udiseplus.gov.in/ | SPA / PDF reports | District | Not confirmed this session | 3 | yes | Returns 200. District score cards are available for both districts, so the cities are symmetric. PGI-D lags by 2+ years. |
| Learning outcomes (Class 3/6/9 language, maths) - PARAKH Rashtriya Sarvekshan 2024 | Gujarat-state | NCERT PARAKH - Gujarat state report | https://parakh.ncert.gov.in/sites/default/files/2025-07/REPORT_Gujarat_IND024.pdf | Text PDF, 46 pages | State (district-level figures are not in tables) | Survey Dec 2024; published 2025-07 | 3 | yes | Downloaded (2.6 MB). District report cards are behind a JS dropdown on https://parakh.ncert.gov.in/prs-reports-2024 (fetched; no static district links). The page's JS config exposes API credentials; we did not use them, and the team should not either. |
| PARAKH district dashboard | National | PARAKH dashboard | https://dashboard.parakh.ncert.gov.in/en | Interactive dashboard | District | PRS 2024 | 2 | yes | Returns 200. We did not confirm whether it has an export. Surat and Ahmedabad districts are covered equally. |
| GSEB SSC/HSC district/centre-wise pass % | Gujarat-state | Gujarat Secondary & Higher Secondary Education Board | https://www.gseb.org/ | Result-statistics PDFs (per news); homepage HTML | District / exam centre | SSC 2026 (declared 2026-05, overall 83.86% per news) | 3 | yes | Homepage returns 200, but no statistics link was found in the static HTML. News reports of district results contradict each other (e.g. 'Ahmedabad Rural 100%'), so use the official GSEB PDF, not news. |
| RTE 12(1)(c) 25% private-school admissions (seats, applications, allotments) | Gujarat-state | RTE Gujarat online admission portal | https://rte.orpgujarat.com/ | Seasonal portal | District / school | Unknown | 2 | no | Returned HTTP 503 on 2026-09-28. It is likely live only during the admission season (Feb-May). The AMC board separately posts EWS/SEBC/ST waiting lists as PDFs (2026-02). |
| NAS 2021 district report cards | National | National Achievement Survey portal | https://nas.education.gov.in/ | Unknown | District | 2021 | 1 | no | Connection failed (curl code 000/DNS). Stale and superseded by PARAKH 2024. |
| Vidya Samiksha Kendra / Gunotsav school-level assessment | Gujarat-state | Gujarat VSK | https://vsk.gujarat.gov.in/ | Unknown | School/cluster (internal) | Unknown | 0 | no | The guessed host did not resolve. No public dashboard was confirmed. Treat as non-public, so an RTI is needed. |

## Data gaps: candidates for RTI

| Metric | City | Public authority | RTI question |
|---|---|---|---|
| Municipal primary enrolment, schools and teachers by zone/class/medium | Surat | Surat Nagar Prathmik Shikshan Samiti (Municipal School Board), Surat Municipal Corporation - PIO, Administrative Officer's office | Provide, as of 31-07-2025 and 31-07-2026, the zone-wise, medium-wise and class-wise (Balvatika to Std 8) number of students, number of schools and sanctioned vs filled posts of HTAT principals, primary and upper-primary teachers, in Excel or CSV if available. |
| Learning outcomes (Gunotsav/VSK school grades) for municipal schools | Both | Gujarat Council of School Education (Samagra Shiksha) / Vidya Samiksha Kendra, Gandhinagar - state PIO; copy to the municipal school board PIO | Provide the latest Gunotsav/VSK school-wise grades and subject-wise average scores for all schools under the Nagar Prathmik Shikshan Samiti of [Surat/Ahmedabad] for 2024-25 and 2025-26. |
| Municipal school board budget and per-student spend | Both | Nagar Prathmik Shikshan Samiti (SMC / AMC) - PIO, Accounts branch | Provide the school board's sanctioned budget and actual expenditure for 2023-24, 2024-25 and 2025-26 by head (salaries, infrastructure, mid-day meal, uniforms/kits), with the state grant and municipal contribution shown separately. |
| RTE 12(1)(c) seats, applications and admissions | Both | District Primary Education Officer / DEO (Surat; Ahmedabad City and Ahmedabad Rural) - PIO | For 2024-25, 2025-26 and 2026-27, provide the number of RTE 25% seats notified, applications received, seats allotted, admissions confirmed and seats left vacant, ward- or school-wise, in the municipal limits. |
| Std 3 enrolment anomaly in AMC data | Ahmedabad | AMC School Board (Nagar Prathmik Shikshan Samiti, Ahmedabad) - PIO | The Student/Teacher Data List (31-07-2025) shows 7,842 Std 3 students against ~20,000 in Std 2 and Std 4. Provide the corrected zone-wise Std 3 enrolment and the reason for the discrepancy. |
| Out-of-school children survey | Both | Nagar Prathmik Shikshan Samiti (SMC / AMC) - PIO | Provide the zone-wise number of out-of-school children identified in the latest survey (2025-26), and the number enrolled or mainstreamed since. |

## Challenges

- City vs district mismatch: UDISE+, PGI-D and PARAKH report at district level. Ahmedabad district includes rural blocks outside AMC, and Surat district includes rural talukas outside SMC. Only the municipal school boards give city-limit data.
- Surat's school board site (municipalschoolboardsurat.org) is client-rendered with no data in the HTML. Scraping needs a headless browser or the underlying API, and it may hold no statistics at all.
- PARAKH 2024 and UDISE+ district data sit behind JS dropdowns/SPAs with no stable static URLs, so plan manual download of Excel/PDF exports and store them in the repo.
- Gujarati headers and Gujarati numerals (e.g. dates) in municipal tables need transliteration and normalisation. The AMC data also has quality anomalies (Std 3 count).
- GSEB district results and RTE stats are seasonal (the RTE portal returned 503 off-season), and news coverage of district results is contradictory. Only official GSEB statistics PDFs should be used.

## Verifier checks

| Claim | Verdict | Evidence | Correction |
|---|---|---|---|
| The AMC School Board Student/Teacher Data List gives zone x class enrolment of 172,576 students and 4,653 teachers as of 31-07-2025, with an anomalous Std 3 count of 7,842. | confirmed | Plain curl returned 200. The date is shown in Gujarati numerals (31-07-2025). The totals row reads 16133\|19611\|20317\|7842\|24633\|...\|172576, and 4653 appears on the page. There is no TLS quirk. |  |
| The Surat municipal school board site is a JS-only shell with no enrolment or teacher data; figures appear only in news. | confirmed | The raw HTML of the board site (Next.js/zibma, 162 KB) has no strings for student, school, teacher or the Gujarati equivalents, and no __NEXT_DATA__. A web search found only third-party or news figures (318 schools), with no official statistics. The Surat RTI gap stands. |  |
