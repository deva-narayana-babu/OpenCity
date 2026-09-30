# OpenCity Surat: build roadmap for one semester

## 0. Summary and assumptions

**Decisions**
- **City:** Surat.
- **Codebase:** build a new app. forthepeople supplies ideas and patterns, credited, but no code.
- **Stack:** a static Next.js site. Python batch pipelines run on GitHub Actions and commit CSV files to git, with the source recorded on every row. There is no runtime database and no paid service.
- **RTI helper:** runs entirely in the browser. Applicant details never leave the user's device.
- **Real RTIs:** file RTI-1 and RTI-2 in week 1 and RTI-3 in week 2. Replies take 30 days or more, and they are the only way to fill Surat's gaps in education, health and maps this semester.
- **Scope in three tiers:**
  - **Core:** fits a 3-person team.
  - **Standard:** added when the team has 4-5 people.
  - **Stretch:** only after both freezes (data in week 8, helper in week 10).

**Assumptions** (confirm each in week 0)

| # | Assumption | If it fails |
|---|---|---|
| A1 | 3-5 students at 8-12 h/week for 14 weeks. That is about 420-700 h nominal, or about 300-490 h of build time after roughly 30% goes on meetings, reports, learning and demos. | Use the 12-week variant (§3) and Core only |
| A2 | At least 3 members are Indian citizens with an Indian postal address. Form A carries a citizenship declaration, and Rule 7 lets the PIO verify it. | Fewer applicants; file RTI-3 later |
| A3 | Someone can file in person at SMC in Surat | File by Speed Post with an IPO or court-fee stamp, and record the delivery date from tracking |
| A4 | At least one member reads Gujarati fluently | Recruit a named reviewer before week 3 |
| A5 | The instructor approves in writing that members file real RTIs **as individuals**, not in the institution's name | Don't file; demo with mock cases only |
| A6 | Zero budget apart from RTI costs. Petty cash of Rs 1,000 covers Rs 20 fees, Rs 2/page copies after the first 5 free pages, and postage. | Narrow the questions to cut page counts |
| A7 | Worked dates assume week 1 starts Mon 05-10-2026, so week 14 ends Sun 10-01-2027 | Shift every date by the same offset |
| A8 | Facts come from the research synthesis of 27-28 Sep 2026. Its "unresolved" items are checks for week 0 to P0, not facts. | — |

**Effort budget** (rough estimates, not measurements)

| Tier | Contents | Hours | Fits |
|---|---|---|---|
| Core | 10 data series across 6 modules, a gaps page, the RTI helper with 6 templates, 3 real RTIs, privacy and licence checks | about 295 | 3 people |
| Standard | Budget-summary endpoint (if not already Core), fcainfoweb, the full PIO directory, 4 more templates, UDISE+, a usability study with 5-8 residents | about 130 more | 4-5 people |
| Stretch | §2.2 | — | only after the freezes |

---

## 1. Approach and architecture

### 1.1 Fork or fresh: build fresh and borrow patterns

**Why not fork**
- **Size.** forthepeople has about 117k LOC of TS/TSX in 690 files, 108 Prisma models, 127 API routes, 67 seed files and zero tests. A fork is estimated at 15-24 person-weeks (pw), against the team's roughly 8-12 pw of build time.
- **Its live data layer doesn't carry over to Gujarat.**
  - `rti.ts`, `courts.ts` and `jjm.ts` hard-code Karnataka and have no state guard, so they would write Karnataka rows under Surat.
  - `news.ts` queries "<district> Karnataka".
  - `schemes.ts` falls back to 'KA'.
  - `budget.ts` does nothing.
  - Pune's launch took 17 hand-written seed files.
- **Wrong data model.** It is State → District → Taluk, with no municipal body or ward, but almost all Surat data comes from SMC for the municipal area.
- **Setup traps.**
  - `next build` needs a live database.
  - The app throws on load if `ADMIN_SESSION_SECRET` is missing.
  - Admin login needs Upstash.
  - It assumes Vercel Pro crons, a Railway worker and paid OpenRouter models.
  - `prisma/seed.ts` wipes 52 tables.
- **Grading.** The team's own work would be a thin slice of a schema someone else designed.

**Borrow as credited ideas, without copying code:**
- one city config file as the single source of truth (like upstream's `StateConfig`);
- the zero-fabrication rule, with a provenance banner (`DataSourceBanner`) and an honest empty state (`NoDataCard`);
- the shape of `RtiTemplate`, extended;
- aggregate-first data: counts and totals, never records about individuals.

**Copy nothing.** The MVP doesn't need the Gujarat district polygon. Its origin isn't recorded upstream, so don't reuse it until its source and licence are known (§6 has the rules).

**Optional give-back PR (weeks 13-14):**
- a `GUJARAT` StateConfig;
- an alias for the 'ahmadabad' slug;
- 'GJ' in the schemes lookup;
- state guards on `rti.ts`, `courts.ts` and `jjm.ts`;
- the Surat templates.

The upstream copy rules ban phrases such as "hold power accountable" and "corruption". Write any PR text to fit them.

### 1.2 Stack

| Layer | Choice | Why |
|---|---|---|
| Front end | Next.js App Router, TypeScript, `output: 'export'`. Tailwind; Recharts; `next/font` with Noto Sans and Noto Sans Gujarati. | Same family as upstream. The export is fully static and fonts are self-hosted, so no third-party requests are made at runtime. |
| Pipelines | Python 3.12 with httpx, lxml/`pandas.read_html`, `pdftotext -layout`/pdfplumber, openpyxl and pydantic. Playwright only for the budget endpoint fallback. | Stronger PDF and table tools. Data and UI people work in parallel against the contract in §1.3. |
| Storage | `data/raw/…/manifest.json`, `data/tidy/*.csv` (long format) and `data/meta/{sources,metrics,geographies,rules}.yaml`. The build turns these into one JSON file per page. | Changes show as diffs, every number can be audited, and it is free. |
| Scheduling | GitHub Actions cron. It commits **only when the content hash changes**, then calls the deploy hook. | Free for public repos, and avoids noisy history. |
| Hosting | Vercel Hobby or Cloudflare Pages, with a preview deploy per PR | Free |
| Headers | CSP (and any required headers) set in the host's headers file or a `<meta>` CSP. `next.config` headers don't apply to a static export. | Enforces the privacy design in §4.6 |
| RTI helper | Client-side React. The letter is HTML plus print CSS; `.ics` files are built in JS; the tracker is in localStorage and opt-in. | Personal data stays on the device, and the browser draws Gujarati correctly |
| Monitoring | A failed workflow opens a GitHub issue automatically; a generated `/status` page shows each source's freshness | Zero cost, and visible to graders |

### 1.3 Data pipeline: fetch → normalise → store with provenance → display

```
SMC HTML/PDF · Agmarknet · CityFinance XLSX · NFHS CSV · RTI replies
  [fetch]     User-Agent with a team contact email; ≤1 request / 2-5 s per host; backoff;
              conditional GET; 30 s timeout; stop and alert on 403/429 (never evade)
  [snapshot]  data/raw/<source>/<YYYY-MM-DD>/<file> + manifest(url, retrieved_at,
              http_status, sha256, bytes); files >20 MB go to a Release asset, hash kept in git
  [parse]     one versioned parser per source; fixture tests on saved snapshots
  [normalise] tidy rows + provenance; units converted (budget summary is in Rs '000)
  [validate]  schema, ranges, row-count and header-hash drift; "not reported" ≠ 0
              pass → commit    fail → keep the last good data + open an issue
  [build]     static export, one JSON file per page
  [display]   value · as-of date · geography chip · source link · staleness badge · "Ask via RTI"
```

**Tidy row schema.** This is the contract between the data and UI people:

`metric_id, geo_level, geo_code, period_start, period_end, value, unit, status, source_id, source_url, publisher_as_of, retrieved_at, raw_sha256, parser, method, note`

| Field | Allowed values |
|---|---|
| `geo_level` | `smc_city`, `smc_zone`, `smc_ward`, `surat_district`, `tapi_district`, `apmc_market`, `pds_zone`, `reporting_centre` |
| `status` | `reported`, `not_reported`, `withheld` |
| `method` | `html`, `pdf_text`, `xlsx`, `json`, `manual`, `rti_reply`, `ocr` |
| `parser` | recorded as `name@version` |

**Rules**
- **No fabrication.** No interpolation and no estimates. A missing value becomes a NoData card with an RTI button.
- **Two dates.** The publisher's as-of date and the scrape date are stored separately, and the UI shows both.
- **Archive sources that are overwritten in place.** Patrak-7 and the weekly budget summary are replaced at the same URL, so the archive is the time series.
- **One geography per chart.**
- **RTI-reply data is typed in twice by different people,** and the two entries must agree before commit.

### 1.4 Batch or live: everything is batch

No page calls a government site from the browser. That avoids cross-origin blocking and flaky sites, spares their servers, and keeps results reproducible. "Live" means a visible "as of" timestamp.

| Cadence | Sources |
|---|---|
| Daily | Agmarknet (Surat APMC); SMC rainfall and Ukai page. The semester is after the monsoon: switch to every 2 h from June to September via config, if the P0 check shows the page updates. |
| Weekly | SMC Revenue-Capital Budget Summary, archived every week (once the endpoint is found) |
| Monthly | SWM statistics; corporator-list diff; disease reports (checking for updates past 2022); liveness check of every URL in `sources.yaml` |
| Quarterly | Patrak-7 archive |
| Annual or manual | Balance sheet, CityFinance XLSX, RTI annual return (published in May), NFHS-5, UDISE+, re-check of the PIO list |

### 1.5 Free-tier hosting and cost

- **Running cost: Rs 0.** A public GitHub repo, a static host, and no database, Redis, LLM, analytics or payments.
- **RTI spend:** from the A6 petty cash, logged per RTI in the team's private filing log.
- **Handover items:**
  - GitHub disables scheduled workflows in public repos after 60 days with no repo activity. Document this in the runbook.
  - Name a handover owner.

---

## 2. Scope

### 2.1 MVP datasets (C = Core, S = Standard)

| Module | Metric | Source | Method | Cadence | Geography | Tier | Gap → template (§4) |
|---|---|---|---|---|---|---|---|
| Finance | Balance sheet FY2025-26 (with FY2024-25), incl. loans | https://www.suratmunicipal.gov.in/Content/Documents/Departments/Accounts/BalanceSheet_25_26.pdf | `pdftotext -layout` (4-page English text PDF) | Annual; index back to 2015-16 | SMC city | C | Property tax by ward (S) |
| Finance | Audited income, expenditure and own revenue up to 2023-24 | https://www.cityfinance.in/municipal-data/city/surat | XLSX export, committed by hand | Annual | SMC city | C | — |
| Finance | Revenue and capital budget: original, revised and actuals, HQ and zones (Rs '000) | https://www.suratmunicipal.gov.in/Departments/Accounts/CapitalRevenueBudgetSummary | Background (XHR) endpoint, max 4 h spike in P0; fallback is a weekly Playwright snapshot | Weekly (last 27/09/2026); archive every run | SMC city / zone | C if the endpoint is found in P0, else S | Capital works (S) |
| Food | Surat APMC arrivals and min/max/modal prices | https://api.agmarknet.gov.in/v1/prices-and-arrivals/market-report/daily, **only if** the official data.gov.in API fails from runners in P0 | JSON POST `{date, marketIds, stateIds:[11]}`. Market allowlist excludes Tapi-district markets (Vyara, Songadh, Uchhal, Nizar, Kukarmunda, Valod). Missing days stored as `not_reported`. | Daily | APMC market | C | APMC reporting gaps (C) |
| Food | Retail and wholesale prices of 22 essentials | https://fcainfoweb.nic.in/reports/report_menu_web.aspx | Replay the ASP.NET VIEWSTATE postback | Daily | Surat reporting centre | S | PDS in zones 901-910 (C) |
| Health & env | Monthly door-to-door waste collection | https://www.suratmunicipal.gov.in/Departments/SolidWasteManagementStatistics | 8 HTML tables; series from 2019 | Monthly (to Jul 2026) | SMC city | C | SWM processing (S) |
| Health & env | Monthly cases and deaths, 7 diseases | https://www.suratmunicipal.gov.in/Departments/HealthDepartmentDiseaseReports | 7 HTML tables; **stale** badge (1995-2022) | Monthly check | SMC city | C | Disease cases 2023 onward (C, RTI-1) |
| Health & env | NFHS-5 vs NFHS-4 indicators | https://raw.githubusercontent.com/pratapvardhan/NFHS-5/master/NFHS-5-Districts.csv | CSV, long format; cite the DOI and check the repo licence | Static (2019-21) | **Surat district** | C | — |
| Water & rain | Ukai dam level and flows; zone-wise rainfall; creek levels | https://www.suratmunicipal.gov.in/Home/rainfallinfo | Server-rendered HTML tables | See §1.4 | Dam: "Tapi district"; rainfall: SMC zone | C | Water supply (S) |
| Council | 120 corporators (30 wards × 4), term 2026-31 | https://www.suratmunicipal.gov.in/Corporation/Corp_list | English HTML (no party or phone) | Monthly diff | SMC ward | C | Ward GIS boundaries (C, RTI-3) |
| RTI tracker | Annual returns, 2005-07 to 2025-26 | https://www.suratmunicipal.gov.in/Content/Documents/rtiact/Annual-Return/2025-2026.pdf (index at `/Downloads/Acts/RTI_ActAnnualReturn`) | Text PDF, one page per year | Annual (May) | SMC as a public authority | C | RTI timeliness (C) |
| RTI tracker | Quarterly disposal, disposal within time, pendency | https://www.suratmunicipal.gov.in/Content/Documents/rtiact/other/patrak-7.pdf | Numbers by row position against a hand-made label list; **archive each quarter** | Quarterly | SMC | C | same |
| RTI helper | PIO/APIO and appellate-officer list dated 09-12-2025 | https://www.suratmunicipal.gov.in/Content/Documents/rtiact/piosandapios_guj.pdf | **C:** hand-key the ~10 entries the Core templates need, reading the pages on screen. **S:** convert all 43 pages from the legacy font, then check by hand. | About once a year | — | C (partial) / S (full) | — |
| RTI helper | Gujarat RTI Rules 2010 | https://www.suratmunicipal.gov.in/Content/Documents/rtiact/other/Gujarat_RTI_rules_2010.pdf | Read by hand into `rules.yaml`, with source page and `last_reviewed` | Static | — | C | — |
| Education | Schools and enrolment (context only) | https://dashboard.udiseplus.gov.in/ | Manual Excel export | Annual | **Surat district** | S. Core shows only a gap card. | SMC schools (C, RTI-2) |

**RTI tracker headline numbers:**
- 2025-26: 8,653 requests, 353 PIOs, 74 appellate officers; s.8(1)(j) invoked 14 times.
- Q4 2025-26: 1,106 of 1,818 disposals (about 61%) within the time limit; 3,197 pending at quarter end.
- The fall from 15,213 requests (2024-25) to 8,653 is annotated as a possible upload-timing artefact.

**Work packages and hours** (rough estimates)

| WP | Contents | Tier | Hours | Lead |
|---|---|---|---|---|
| C1 | Repo, CI, data contract, skeleton, deploy, status page | C | 30 | R5 |
| C2 | SMC HTML pipelines ×4 (SWM, disease, rainfall/Ukai, corporators) | C | 35 | R2 |
| C3 | RTI annual returns (21 PDFs) and Patrak-7 archiver | C | 25 | R3 |
| C4 | Balance sheet and CityFinance imports | C | 10 | R3 |
| C5 | Agmarknet fetcher, allowlist, `not_reported` handling | C | 20 | R2 |
| C6 | NFHS-5 loader | C | 5 | R3 |
| C7 | UI: overview, 6 module pages from one tile component, gaps page, sources page | C | 45 | R4 |
| C8 | RTI helper, split as below | C | 95 | R1/R4/R5 |
| | Deadline engine, tests and `.ics` | | 25 | |
| | Form E generator | | 10 | |
| | 6 templates, English and Gujarati | | 25 | |
| | Question checker | | 10 | |
| | Applicant form and print letter | | 10 | |
| | Fee and routing step | | 5 | |
| | Tracker | | 10 | |
| C9 | CSP and network test, licence audit, disclaimers, runbook | C | 15 | R5 |
| C10 | Real RTIs: filing, follow-up, appeals, typing in replies | C | 15 | R1 |
| S1-S6 | Budget endpoint (20), fcainfoweb (25), full PIO directory (30), 4 more templates (25), UDISE+ (8), resident usability study (25) | S | about 130 | as §5 |

### 2.2 Stretch (only after the week 8 and week 10 freezes), in priority order

1. **PMAY housing tables.** https://www.suratmunicipal.gov.in/Departments/PradhanMantriAwasYojana
2. **Suman High School PDFs.** https://www.suratmunicipal.gov.in/Services/SumanHighSchool. The PDFs have not been opened yet.
3. **Budget-book head mapping.** https://www.suratmunicipal.gov.in/Departments/Accounts/Budget. The 2026-27 book is 778 pages with legacy-font Gujarati, so heads must be mapped through a hand-built code list.
4. **Ward choropleth,** only from polygons supplied in reply to RTI-3. Not the bharatlas polygons, whose licence and origin are unchecked.
5. **Gujarati UI for the whole dashboard.**
6. **Opt-in, anonymised sharing of RTI outcomes** (§4.6).
7. **Ahmedabad comparison view.** Legacy-TLS fetching happens only in the Python pipelines. Pin the certificate fingerprint rather than using a blanket `-k`.
8. **The upstream give-back PR** (§1.1).

**Out of scope:**
- **Transport:** no public GTFS.
- **Power:** split licensees.
- **Courts:** the NJDG returns 403 to scripts and uses a captcha.
- **News and AI insights.**
- **Payments, tenders and admin.**
- **Ranking or scoring of individual corporators or officials.**

---

## 3. Phased plan (14 weeks)

**Critical-path dates** (RTI-1 filed in person on Mon 05-10-2026)

| Date (week) | Milestone |
|---|---|
| Now to Sun 04-10 (week 0) | Written instructor approval; 3 applicants chosen; PIO pages for T1-T2 read and confirmed; filing channel chosen |
| Fri 09-10 (week 1) | RTI-1 and RTI-2 filed |
| Fri 16-10 (week 2) | RTI-3 filed |
| Wed 04-11 (week 5) | RTI-1 and RTI-2 replies due (Mon 09-11 if filed through an APIO) |
| **Sun 08-11 (end of week 5)** | **Deadline engine and Form E generator done.** The team's own appeals depend on them. |
| Wed 11-11 (week 6) | RTI-3 reply due. This is also day 37 for RTI-1 and RTI-2, the last day to wait for a posted reply. |
| Wed 11-11 to Fri 20-11 (weeks 6-7) | First appeals filed with the helper, **only if** a reply is missing or incomplete |
| Fri 04-12 (week 9) | Last day for the RTI-1 and RTI-2 first appeals |
| Week 8 | Mid-semester demo; **data scope freeze** |
| Week 10 | **Helper feature freeze** |
| Fri 11-12 and Sat 26-12 (weeks 10 and 12) | FAA decision due and latest date, for appeals filed 11-11 |
| Week 14 (04-01 to 10-01-2027) | Final demo |

### P0: Foundations and critical path (week 0 to week 2)

**Deliverables: real RTIs**
- **Applicants.** RTI-1 (template T1, §4.7), RTI-2 (T2) and RTI-3 (T3) are each filed by a different member.
- **Channel.** File in person, paying cash against a stamped receipt. Otherwise use Speed Post with an IPO or court-fee stamp.
- **Filing log.** Kept privately, outside the repo: receipts, dates, acknowledgement numbers and costs.

**Deliverables: P0 checks**

| # | Check | Owner | By |
|---|---|---|---|
| a | Read the PIO list pages for Health/VBDC, the Samiti and Town Planning/GIS on screen, then confirm designation and address by phone or email. T4-T6 follow later. | R1 + Gujarati reader | T1-T2 in week 0; others in week 2 |
| b | Do the Samiti and APMC Surat have their own PIOs? | R1 | Samiti in week 0; APMC in week 2 |
| c | Which SMC head-office address is current (Muglisara or Tapipura)? | R1 | Week 1 |
| d | Register on onlinerti.gujarat.gov.in and screenshot whether SMC, the District Supply Office (DSO) Surat and APMC Surat are listed | R1 | Week 2 |
| e | Read GIC's second-appeal and complaint forms: any fee, and the complaint time limit (the synthesis says 90 days; GIC rejection data says 30 days from the cause) | R1 | Week 2 |
| f | Spend at most 4 h in DevTools finding the budget summary's background request, then decide Core or Standard | R2 | Week 2 |
| g | Fetch every Core host **from a GitHub-hosted runner**, and test the data.gov.in Agmarknet API with a free key. If Indian government hosts time out from the runner, fall back to a self-hosted runner on a team machine. | R2 | Week 2 |
| h | Record each host's robots.txt and website or copyright policy in `sources.yaml` | R5 | Week 2 |
| i | Does the rainfall and Ukai page update outside the monsoon? | R2 | Week 2 |
| j | Run a 30-day scan of Surat APMC on Agmarknet | R2 | Week 2 |

**Deliverables: architecture decision records (ADRs)**
- **ADR-001:** build fresh.
- **ADR-002:** the data contract.
- **ADR-003:** the client-side privacy design.
- **ADR-004:** use of undocumented endpoints (§6), signed off by the instructor.

**Deliverables: repo and deploy**
- CI running lint, typecheck and pytest.
- A static skeleton with an About page crediting the inspiration.
- One pipeline end to end: SWM → tidy CSV → one tile.

**Exit criteria**
- Photos of the RTI-1 and RTI-2 receipts are in the private log. Only redacted copies go in the repo.
- All deadline dates are in the team calendar.
- The ADRs are merged and the skeleton URL is live.
- `sources.yaml` shows liveness from the runner and the policy for every Core source.
- The budget endpoint has been classed as C or S.

### P1: Core pipelines and the RTI deadline logic (weeks 3-5)

**Deliverables**
- Work packages C2-C6, the raw archive and manifests, validators, fixture tests and automatic issue creation.
- **In parallel (R5, with R4 on UI):**
  - the deadline engine as pure TypeScript functions, with the test cases in §4.3;
  - the `.ics` export;
  - the **Form E (first appeal) generator** as print HTML.

**Exit criteria**
- At least 9 Core series produce tidy rows, with provenance filled in on 100% of rows.
- The scheduled workflows are green for 7 days in a row.
- 30 values sampled at random match the source exactly.
- At least 20 deadline tests pass.
- R1 has printed Form E for a mock case and checked it against the rules PDF, by Sun 08-11.

### P2: Dashboard MVP and first appeals (weeks 6-8)

**Deliverables**
- **UI:**
  - an overview page and 6 module pages (Finance, Food, Health & env, Water & rain, Council, RTI tracker);
  - an Education gap card;
  - a gaps page, a sources page and a status page;
  - geography chips and staleness badges on every tile;
  - a mobile-first layout.
- **RTI follow-up:**
  - Wait until day 37 (Wed 11-11) for posted replies.
  - If a reply is missing or incomplete, file Form E using the helper, before week 7 ends.
  - Type in any replies twice.
- **Standard teams:** S1 and S2.
- **Week 8:** the demo, then the data scope freeze.

**Exit criteria**
- An automated test on the page JSON shows every tile has a value, as-of date, `geo_level` and source.
- An axe accessibility audit finds no critical issues.
- Every gap links to a template or says "template planned".
- The instructor ticks the 5-item demo checklist: live tile, stale tile, gap page, RTI tracker, printed Form E.

### P3: RTI helper (weeks 7-10; feature freeze in week 10)

**Deliverables**
- The template schema, and 6 Core templates (T1-T6) in English and Gujarati. Standard teams add T7-T10.
- The question checker, the applicant form, and the bilingual printed letter.
- The fee and routing step, using the hand-keyed PIO entries (S3 adds the full directory).
- The opt-in tracker, JSON export and import, and the GIC pre-flight checklist.
- Disclaimers, the privacy notice, and the non-impersonation rules (§4.5).

**Exit criteria**
- CSP plus a Playwright network test in CI show 0 requests carrying form data.
- 3 classmates each produce a correct application in 10 minutes or less, unaided.
- At least 90% of routing scenarios are correct (§7).
- The Gujarati reviewer's sign-off is logged.

### P4: Replies, testing, hardening (weeks 10-13)

**Deliverables**
- **RTI replies:**
  - Bring replies into the data as `method=rti_reply`, with an "obtained via RTI" badge.
  - Commit redacted scans only.
  - Track the FAA dates (Fri 11-12 due, Sat 26-12 latest).
- **Usability testing:**
  - **Core:** 3 classmates plus at least 2 Surat residents.
  - **Standard:** 5-8 residents, at least half of them Gujarati-first.
  - Written informed consent; no audio or video recording without consent; no personal data kept.
- **Reviews and checks:**
  - A wording and legal review by the instructor or a legal-aid clinic.
  - A licence audit, a broken-link check and a performance pass.
- Plan for reduced availability around year-end.

**Exit criteria**
- **Core:** the top usability findings are fixed.
- **Standard:** a System Usability Scale (SUS) score of at least 70.
- No open critical bugs.
- Every Core dataset is within its freshness target.
- The review log is signed.

### P5: Ship (weeks 13-14)

**Deliverables**
- The final demo and report.
- A runbook covering how to fix a broken parser, how to re-check PIOs each year, and the Actions inactivity rule.
- The handover, and the optional upstream PR.

**Exit criteria**
- A fresh clone runs locally from the README in 30 minutes or less.
- The demo shows the full loop: stale tile → RTI → reply → tile updated. If no reply has come, it shows the appeal filed and its FAA status.

### 12-week variant

| Phase | Weeks |
|---|---|
| P0 | week 0 to week 2 |
| P1 | 3-5 (the Form E date is fixed by the RTI clock, so it cannot compress) |
| P2 | 6-7 (freeze in week 7) |
| P3 | 7-9 |
| P4 | 10-11 |
| P5 | 12 |

Core only. RTI-3 is optional.

---

## 4. RTI helper design

### 4.1 Flow

1. **Trigger.** A stale, missing or district-level tile shows **"Ask for this via RTI"**, carrying its `metric_id`. The gaps page lists every such metric.
2. **Template page.** Shows:
   - the public authority and its type (SMC department, state, statutory body, central, court);
   - why the data isn't public;
   - what a reply would contain.
3. **Edit the questions.** Checkboxes and editable date ranges. The checker:
   - flags "why", "whether" and opinion questions, and suggests "number of…", "list of…" or "copies of records…";
   - requires a date range;
   - warns (does not block) above 5 questions, since the Gujarat rules set no word or subject limit;
   - flags personal names (s.8(1)(j) as amended by the DPDP Act);
   - allows one authority per application;
   - asks for data "in the form in which it is held", to avoid a refusal under s.7(9);
   - warns against bulk filing (GIC capped one Surat family at 6 applications a year each, order of 24-04-2025).
4. **Applicant details, held in memory only:**
   - name and postal address (required);
   - email (optional);
   - citizenship declaration;
   - BPL status, which needs a **certified copy of a BPL card or certificate**; a ration card alone does not qualify;
   - how to receive the information: email, pen drive or paper;
   - language.
5. **Generate.** Gujarati and English versions appear side by side, laid out with the fields of Form A (plain paper with the same details is valid). The user prints or saves it with the browser's print dialog.
6. **Fee.**
   - Rs 20.
   - Allowed modes (Rule 3(2)): cash against a receipt, DD, pay order, IPO, non-judicial, court-fee or revenue stamp, stamp paper, franking, e-stamping, or treasury challan (head 0070-60-800-(17)).
   - Electronic applications must pay within 7 days (Rule 3(1)).
   - Later charges (Rule 3(4)) can be paid only by cash, DD, pay order, IPO or challan, not stamps.
   - Copies cost Rs 2 per page, with the first 5 pages free (GAD circular, May 2025).
   - Inspection is free for the first 30 minutes, then Rs 20 per 30 minutes. A CD costs Rs 50.
7. **Route** (§4.2). PIO details show their source page and the date they were last checked.
8. **Track.** The user enters:
   - the filing or delivery date and channel;
   - whether it went through an APIO or involves a third party, and any life-or-liberty ground;
   - the transfer date, if the application was transferred.

   The helper then computes the deadlines (§4.3), exports a `.ics` file, and at each stage generates Form E or the GIC pre-flight checklist.

The helper **does not submit applications or collect fees.** Every screen says so.

### 4.2 Where to submit

| Authority type | Templates | Channel | Fee |
|---|---|---|---|
| SMC department | T1, T3, T4 (Standard: T7-T10) | In person at the department or RTI Cell (cash, get a receipt); by post (court-fee stamp or IPO); onlinerti.gujarat.gov.in only if P0 check (d) found SMC listed (registration required; SBI net banking, card or wallet) | Rs 20 |
| Municipal school board | T2 | Its own PIO if P0 check (b) finds one; otherwise SMC's RTI Cell, asking for transfer | Rs 20 |
| State authority | T6 (District Supply Office, Collector Office, Surat) | In person or by post; state portal if listed | Rs 20 |
| Statutory market committee | T5 (APMC Surat) | Its own PIO (P0 check b); in person or by post | Rs 20 |
| Central public authority | none (routing test only) | rtionline.gov.in, for central bodies only, **not** SMC or the Collectorate | Rs 10 |
| District courts | none (routing test only) | Gujarat High Court portal | Rs 50 (Rs 500 for tender information) |
| Second appeal or complaint | Gujarat Information Commission (GIC) | gic.gujarat.gov.in (eApplication.aspx) or by post | Per P0 check (e); **not assumed** |

- The state portal's FAQ wrongly says second appeals go to the Central Information Commission. The helper states that they go to GIC.
- Inside SMC, a PIO gets other departments' records by seeking their help under s.5(4). Section 6(3) transfer is only for **another** public authority. The letters ask for both.

### 4.3 Deadlines and appeals

Deadlines are counted in calendar days, Asia/Kolkata, excluding the day of receipt. The helper **does not extend a deadline that falls on a holiday**. This is conservative for the applicant, and the UI says so.

| Stage | Rule | Helper behaviour |
|---|---|---|
| PIO reply | 30 days from receipt. 48 h if life or liberty is involved. +5 days if filed through an APIO. 40 days if a third party is involved (s.11). | For postal filing it asks for the delivery date from tracking; if unknown, it shows a range. |
| Transfer (s.6(3), Form D, within 5 days) | The 30 days run from receipt by the new authority | The user enters the transfer date and the new due date is recomputed |
| No reply | Deemed refusal (s.7(2)). Information supplied late must be free (s.7(6)). | Suggests waiting about 7 days for a posted reply, then Form E |
| First appeal | Form E to the FAA within 30 days of the reply or the deemed refusal | Grounds: no reply, incomplete reply, or wrongly claimed exemption |
| FAA decision | 30 days, 45 at most | Two reminders |
| Second appeal (s.19(3)) | After the FAA order, or after day 45 with no order. Within 90 days of the order. GIC rejects appeals filed more than 135 days after the first appeal. | With an order: order date + 90 days. With no order: **safe window is day 46 to day 120 after the first appeal**, with day 135 as GIC's rejection threshold. |
| Complaint (s.18) | The two sources conflict: 90 days (synthesis) vs 30 days from the cause (GIC rejection data) | Uses **30 days** until P0 check (e) settles it |
| GIC pre-flight | Blocks GIC's main rejection causes (337 rejections, Jul-Dec 2024) | Checks for a duplicate second appeal (105), one appeal covering several applications (74), no first appeal (55), late filing (26 + 20), and a central authority (21) |

**Deadline tests (at least 20).** Each rule above, plus these cases:
- a postal range;
- a late reply that restarts the first-appeal window;
- an early FAA order;
- a year boundary;
- a deadline falling on a holiday;
- the Asia/Kolkata midnight edge.

**The `.ics` export:**
- one all-day event per stage;
- an alarm 3 or 7 days before each;
- a stable UID, so re-importing updates rather than duplicates;
- no personal data (e.g. `RTI smc-health-disease-2023: reply due`).

**Expectations.**
- Second appeals will not finish this semester. GIC's pending appeals rose from 624 to 1,039 by 31-08-2026, the State Chief Information Commissioner post shows as vacant, and Satark Nagrik Sangathan estimated about 5 months' wait.
- **Don't file an appeal just to demo the flow.** If replies are complete, demo Form E on a mock case.

### 4.4 Data model

- **`templates/*.yaml`:** `id, tier, metric_ids[], trigger_en/gu, authority_id, questions[{id, en, gu, params}], fee_rule, channels[], last_reviewed`.
- **`authorities.yaml`:** `id, type (smc_department|municipal_board|state|statutory|central|court), parent, second_appeal_body, portal_listed (from P0)`.
- **`pio_directory.csv`:** `authority_id, department, zone, role (PIO|APIO|FAA), designation_en, designation_gu, office_address, office_phone, official_email, source_url, source_page, source_date (09-12-2025), verified_by, verified_on`.
  - Letters are addressed to the **designation**; extracted names come out garbled.
  - Only official contact details are published.
- **`rules.yaml`:** fees, payment modes, time limits. Each entry has its rule or circular reference, source page and `last_reviewed`.
- **Tracker (localStorage, opt-in):** `id, template_id, authority_id, filed_on, channel, via_apio, third_party, life_liberty, transferred_on, delivered_on, reply_on, reply_type, first_appeal_on, faa_order_on, second_appeal_on`.
  - **No name, address or email.**

### 4.5 Disclaimers and not impersonating government

> OpenCity is a student project. It is not a government website and is not affiliated with Surat Municipal Corporation, the Government of Gujarat or the Gujarat Information Commission. It does not submit applications or collect fees. It gives general information about the RTI Act, 2005 and the Gujarat RTI Rules, 2010 as we understood them on [last reviewed date]. It is **not legal advice**. Check the fee, the PIO's designation and the address before filing; you are responsible for your application. RTI is available to citizens of India. For help, contact a legal-aid clinic or an RTI helpline such as MAGP's.

- No State Emblem, no SMC or Government of Gujarat logos, no letterheads.
- No site name or domain that suggests an official site (no "gov").
- The disclaimer appears on every helper page and in the footer of every printed copy.
- Neutral copy: no party labels, no rankings of individuals.

### 4.6 Keeping data to a minimum under the DPDP Act

**How the helper handles applicant data**
- Name, address and email live only in React state and on paper. They are never sent to a server or logged.
- No analytics, or cookieless page counts only.
- The privacy notice states that the static host sees IP addresses in its access logs.
- Saving to the device is off by default.
  - A "Remember on this device" option turns it on.
  - "Delete everything" wipes localStorage.
  - JSON export and import let users move devices without an account.
- A CSP of `connect-src 'self'` and a network test in CI enforce all of the above.

**The DPDP context**
- The DPDP Rules were notified on 14-11-2025 and phase in over 18 months.
- The design goal is that the team never holds applicant data. That is a design goal, not a legal opinion.

**Stretch: opt-in outcome sharing**
- Fixed fields only: authority, month filed, days to reply, reply type, whether an appeal was filed.
- No free text.
- A consent record and 12-month retention.

**The team's own RTIs**
- Applicant data stays in the private filing log.
- Scans are redacted before any commit.

### 4.7 Worked template T1: disease cases 2023 onward (also RTI-1)

**Metadata** (`templates/smc-health-disease-2023.yaml`)

| Field | Value |
|---|---|
| Trigger | SMC's Disease Reports tables end in 2022 and have no dengue or chikungunya series; current counts appear only in news |
| Authority | SMC, under the Gujarat RTI Rules 2010 |
| Addressed to | PIO, Health Department (Medical Officer of Health) or Vector Borne Diseases Control Department, per P0 check (a) |
| Fee | Rs 20 |

**English**

```
To,
The Public Information Officer,
Health Department (Medical Officer of Health), Surat Municipal Corporation,
{{pio.office_address_en}}

Subject: Application under Section 6(1) of the Right to Information Act, 2005

1. Full name of applicant: {{applicant.name}}
2. Address for correspondence: {{applicant.address}}
3. Particulars of information sought:
   (a) Number of confirmed cases and number of deaths due to dengue, malaria
       (P. vivax and P. falciparum separately), chikungunya, gastroenteritis,
       enteric fever, hepatitis and cholera, month-wise and zone-wise (ward-wise
       if so held), from {{from|January 2023}} to the date of this application.
   (b) Month-wise number of blood samples tested for malaria and for dengue at
       SMC health facilities for the same period.
   (c) Zone-wise number of mosquito-breeding notices issued and total penalty
       amount collected, from {{from2|January 2024}} to the date of this application.
4. Only aggregate figures are sought; no patient-identifying information is
   requested. If any part is held to be exempt, kindly supply the remaining part
   under Section 10 and cite the provision relied upon.
5. If held electronically, kindly provide the information in the electronic form
   in which it is held (Excel/CSV preferred) by email to {{applicant.email}} or on
   pen drive, as permitted by the GAD circular of May 2025.
6. If any part is held by another department of SMC, kindly obtain it under
   Section 5(4); if any part relates to another public authority, kindly transfer
   it under Section 6(3) and inform me.
7. Application fee: Rs 20 paid by {{fee.mode}} No. {{fee.ref}} dated {{fee.date}}
   [OR: I belong to the BPL category; a certified copy of my BPL card/certificate is enclosed.]
8. I am a citizen of India.

Place: {{place}}          Date: {{date}}          Signature: __________
```

**Gujarati** (a fluent reviewer must sign it off before use)

```
પ્રતિ,
જાહેર માહિતી અધિકારીશ્રી,
આરોગ્ય વિભાગ (મેડિકલ ઓફિસર ઓફ હેલ્થ), સુરત મહાનગરપાલિકા,
{{pio.office_address_gu}}

વિષય: માહિતી અધિકાર અધિનિયમ, 2005ની કલમ 6(1) હેઠળ માહિતી મેળવવા બાબત.

1. અરજદારનું પૂરું નામ: {{applicant.name}}
2. પત્રવ્યવહારનું સરનામું: {{applicant.address}}
3. જોઈતી માહિતીની વિગતો:
   (ક) {{from}}થી આ અરજીની તારીખ સુધી ડેન્ગ્યુ, મેલેરિયા (પી. વાયવેક્સ અને
       પી. ફાલ્સીપેરમ અલગ-અલગ), ચિકનગુનિયા, ઝાડા-ઊલટી (ગેસ્ટ્રોએન્ટેરાઇટિસ),
       એન્ટરિક ફીવર (ટાઇફોઇડ), કમળો (હિપેટાઇટિસ) અને કોલેરાના નિદાન થયેલા કેસો
       તથા મૃત્યુની સંખ્યા — માસવાર અને ઝોનવાર (વોર્ડવાર રાખવામાં આવતી હોય તો વોર્ડવાર).
   (ખ) એ જ સમયગાળા માટે સુરત મહાનગરપાલિકાની આરોગ્ય સંસ્થાઓમાં મેલેરિયા અને
       ડેન્ગ્યુ માટે તપાસવામાં આવેલા લોહીના નમૂનાઓની માસવાર સંખ્યા.
   (ગ) {{from2}}થી આ અરજીની તારીખ સુધી મચ્છરોના ઉત્પત્તિ સ્થાન બદલ આપવામાં
       આવેલી નોટિસોની સંખ્યા અને વસૂલ કરેલ દંડની કુલ રકમ — ઝોનવાર.
4. માત્ર એકંદર આંકડા માંગ્યા છે; દર્દીની ઓળખ થઈ શકે તેવી કોઈ માહિતી માંગી નથી.
   માહિતીનો કોઈ ભાગ મુક્તિપાત્ર ગણાય તો કલમ 10 હેઠળ બાકીની માહિતી આપવા અને
   આધાર લીધેલ જોગવાઈનો ઉલ્લેખ કરવા વિનંતી છે.
5. માહિતી ઇલેક્ટ્રોનિક સ્વરૂપે રાખવામાં આવતી હોય તો જે સ્વરૂપે છે તે જ સ્વરૂપે
   (શક્ય હોય તો Excel/CSV), સામાન્ય વહીવટ વિભાગના મે 2025ના પરિપત્ર મુજબ
   {{applicant.email}} પર ઇ-મેઇલથી અથવા પેન ડ્રાઇવમાં આપવા વિનંતી છે.
6. આ અરજીનો કોઈ ભાગ સુરત મહાનગરપાલિકાના અન્ય વિભાગ પાસે હોય તો કલમ 5(4) હેઠળ
   મેળવીને આપવા, અને અન્ય જાહેર સત્તામંડળને લગતો હોય તો કલમ 6(3) હેઠળ તબદીલ
   કરી મને જાણ કરવા વિનંતી છે.
7. અરજી ફી: રૂ. 20 — {{fee.mode}} નં. {{fee.ref}}, તારીખ {{fee.date}}
   [અથવા: હું ગરીબી રેખા હેઠળ (BPL) છું; BPL કાર્ડ/પ્રમાણપત્રની પ્રમાણિત નકલ સામેલ છે.]
8. હું ભારતનો નાગરિક છું.

સ્થળ: {{place}}          તારીખ: {{date}}          અરજદારની સહી: __________
```

**Example tracker:** filed in person on Mon 05-10-2026, no APIO, no third party.

| Event | Date |
|---|---|
| Reply due | Wed 04-11-2026 (Mon 09-11-2026 if filed through an APIO) |
| Last day to wait for a posted reply (team practice) | Wed 11-11-2026 (day 37) |
| First appeal filed (example) | Wed 11-11-2026 |
| Last day for first appeal | Fri 04-12-2026 |
| FAA decision due | Fri 11-12-2026 (30 days); latest Sat 26-12-2026 (45 days) |
| Second appeal to GIC if no FAA order | Not before Sun 27-12-2026 (day 46). Safe target: by Thu 11-03-2027 (day 120). GIC's rejection threshold: after Fri 26-03-2027 (day 135). |
| Variant: sent by Speed Post, delivered Thu 08-10-2026 | Reply due Sat 07-11-2026; last day for first appeal Mon 07-12-2026 |

---

## 5. Team roles

| Role | Owns | Key deliverables |
|---|---|---|
| **R1: Product and RTI lead** | Scope, P0 checks a-e, templates, the real RTIs and appeals, private filing log, disclaimers, user testing | RTI-1 to RTI-3; T1-T6; §4.5 copy; usability findings |
| **R2: Web data engineer** | HTML and JSON pipelines, Agmarknet, budget endpoint, runner reachability, validators, status page | C2, C5, S1, S2 |
| **R3: Document data engineer** | PDFs, legacy fonts, RTI returns and Patrak-7, finance imports, PIO entries, typing in replies | C3, C4, C6, S3 |
| **R4: Front-end and UX lead** | Next.js, tiles and charts, geography chips, accessibility, Gujarati font, print CSS, helper UI | C7, the C8 UI |
| **R5: QA, DevOps and docs** | CI, the data contract, deadline engine and tests, CSP and network test, licence and policy audit, runbook | C1, C8 logic, C9 |

**Smaller teams:**

| Team size | Arrangement |
|---|---|
| 4 people | R5 splits: deadline engine and tests go to R3; CI, licence and docs go to R1 |
| 3 people | R1 + R5; R2 + R3; R4 (who also owns the deadline engine). Core only. |

**Cross-cutting duties:**
- **Gujarati review:** the most fluent member, about 2 h/week from week 3.
- **Data steward:** a weekly rotating role that triages pipeline issues.
- **PR checklist:** provenance, licence, geography chip and no personal data.
- **Weekly demo:** 15 minutes.

---

## 6. Challenges and mitigations

### Data

| Challenge | Mitigation |
|---|---|
| Legacy-font Gujarati (PIO list, Patrak-7, budget books) | Use the parts that extract cleanly: numbers, phones and emails. Read Patrak-7 rows by position against a hand-made label list. Core hand-keys only the PIO entries it needs, read on screen. Full conversion is S3, checked by a human. |
| Stale or overwritten sources (diseases 1995-2022; Patrak-7; budget summary) | Staleness badge after 2 years, with an RTI button. Archive every scrape. Fill gaps with `rti_reply` data. |
| Undocumented endpoints (Agmarknet v2 needs browser-like Origin/Referer; the budget XHR) | Prefer the official data.gov.in API. ADR-004 records the choice, with instructor sign-off. Honest User-Agent, 1 request per market per day. Stop if blocked. Keep the last good data. Contract tests on the response shape. |
| Unreliable reporting (Surat APMC returned 0 rows on 25-09-2026; the Old Sardar Market sub-yard reported nothing in 30 days) | Store `not_reported`, show gap days, link template T5 |
| Government hosts may time out or block cloud runners | P0 check (g) from a GitHub runner; self-hosted runner as fallback; status page |
| City vs district | Mandatory geography chip; no mixed charts. NFHS-5 and UDISE+ are labelled "Surat district". Ukai is labelled "Tapi district". APMC allowlist. PDS figures summed over zones 901-910 (template T6). |
| RTI replies on paper or in Gujarati | Two people type them in independently; the source scan's hash is recorded; scans are redacted |

### Legal and ethical

| Challenge | Mitigation |
|---|---|
| MIT licence with extra attribution conditions | Fresh build, no copying, so the licence doesn't apply; credit the inspiration anyway. If **any** file is copied: keep the LICENSE text and the per-file creator header; add "Originally created by Jayanth M B" to the About page and README; keep the X-Creator header via the host's headers file. The PR checklist enforces this, with an audit in week 13. |
| Data licences and site terms | `sources.yaml` records each licence or website policy and the attribution text: GODL-India where it applies, CC-BY 2.5 IN for datameet, and the NFHS mirror's licence and DOI. Reuse no geography file whose origin is unknown. |
| Not legal advice | §4.5 disclaimer, `last_reviewed` on the rules, and a review by the instructor or a legal-aid clinic in P4 |
| Impersonation | No emblem, logos, letterheads or official-looking domain; "does not submit" notice (§4.5) |
| DPDP | §4.6: client-side only, CSP plus a CI network test, official PIO contact details only, applicant data kept outside the repo |
| Scraping etiquette | robots.txt and policies checked in P0; identified client; low request rate; off-peak runs; never bypass a CAPTCHA (link to SMC's status tracker; skip the CAPTCHA-gated iPDS ration-card summary) |
| Using public-authority time responsibly | Three genuine RTIs from three applicants; appeals only when warranted; the checker discourages bulk requests (GIC's cap of 6 a year) |
| Human participants | Consent form approved by the instructor; no recordings without consent; anonymised notes |

### Technical

| Challenge | Mitigation |
|---|---|
| Gujarati in PDFs | pdf-lib and jsPDF break conjuncts, so render the letter as HTML with Noto Sans Gujarati and print CSS. Test a list of conjunct-heavy words. |
| Date arithmetic | Pure functions, table-driven tests (§4.3), conservative holiday handling, ranges for postal filing |
| Headers and CSP on a static export | Set them in the host's headers file or a `<meta>` CSP, and test in CI |
| Table layout changes | Header hash with an alert; versioned parsers; the parser version stored in each row |
| Repo growth | Commit only on a hash change; big PDFs go to Release assets |
| Actions disabled after 60 days of inactivity | Runbook entry, a named handover owner |

### UX

| Challenge | Mitigation |
|---|---|
| Mobile-first, low-bandwidth users | Static pages, small JS, tables readable without JS |
| Gujarati-first users | Bilingual helper; plain-language "what this number means" and "why it's missing" |
| Trust | Source and as-of date on every number; public sources and status pages |
| City vs district | Chip tooltips and a one-screen explainer |

### Timeline

| Challenge | Mitigation |
|---|---|
| Replies take 30 days or more; second appeals take about 5 months | File in week 1; nothing in the build waits on a reply; Form E ready by week 5 |
| Hard sources overrun | Timeboxes and Standard tiering; manual fallbacks |
| Scope creep | Data freeze in week 8, helper freeze in week 10, prioritised stretch list |
| A member drops out | Independent work packages; role merges defined in §5 |

---

## 7. Evaluation

| Area | Metric | Target | How measured |
|---|---|---|---|
| Coverage | Series live with full provenance | Core ≥ 10 across 6 modules; Standard ≥ 13 | `sources.yaml` with `status=ok` |
| Accuracy | Parsed values vs the source | ≥ 98% of 50 random values; 100% of RTI and finance headline figures | Logged manual spot-check |
| Freshness | Each dataset within its cadence plus a grace period | ≥ 90% of days | Status page history |
| Honesty | Tiles with source, as-of date and `geo_level` | 100% | Automated test on the page JSON |
| Helper usability | Stale tile → printed application | ≤ 10 min for a first-time user | Classmates (Core) or 5-8 residents (Standard) |
| Routing | Correct authority and channel across scenarios: SMC department, school board, DSO, APMC, central body, court | ≥ 90% | Scenario test |
| Legal logic | Deadline engine | 100% of ≥ 20 cases | Unit tests |
| Privacy | Requests carrying form data | 0 | CI network test and CSP |
| Language | Gujarati letters understood as intended | Reviewer sign-off; 3 Gujarati-first readers paraphrase them correctly | Review log |
| Satisfaction | SUS | ≥ 70 (Standard) | Questionnaire |

**Real RTIs (the critical path)**
- **Record for each RTI:**
  - filed and acknowledged dates;
  - days to reply;
  - whether it came through a transfer (s.6(3) or s.5(4));
  - the share of questions answered;
  - the format received;
  - total cost;
  - whether an appeal was needed.
- **Success means either:**
  - reply data appears on a tile labelled "obtained via RTI"; or
  - a warranted first appeal was filed with the helper by the deadline.

---

## 8. Risk register

| ID | Risk | L | I | Mitigation | Early warning | Owner |
|---|---|---|---|---|---|---|
| R1 | RTI replies late, partial or missing | H | M | File in week 1; Form E ready by week 5; no module waits on a reply | No acknowledgement within 7 days | R1 |
| R2 | Wrong PIO (names in the list are garbled) | M | M | Address by designation; confirm by phone; s.5(4) and s.6(3) clauses | Transfer notice | R1/R3 |
| R3 | Undocumented endpoints change, block, or the owner objects | M | M | Official API first; ADR-004; daily cache; contract tests; manual fallback; stop if blocked | Contract test fails; 403/429 | R2 |
| R4 | SMC site restructured or down | M | H | Raw archive, last good data kept, monthly liveness checks | Liveness check fails | R2 |
| R5 | Government hosts unreachable from GitHub runners | M | M | P0 check (g); self-hosted runner | Timeouts on the runner only | R2 |
| R6 | No member can file in Surat; postal delays | M | L | Speed Post with tracking; delivery-date input; range deadlines | No delivery scan | R1 |
| R7 | Error in the Gujarati legal text | M | H | Fluent reviewer, glossary, paraphrase-back | Reviewer flags | R1 |
| R8 | Personal data leak or DPDP breach | L | H | Client-side only, CSP, private filing log, redaction | CI network test fails | R5 |
| R9 | Licence or site-terms breach | L | M | Fresh-build ADR, PR checklist, policy column, week-13 audit | Copied file with no header | R5 |
| R10 | Wrong legal rule (appeal windows, complaint limit, fees) | M | H | P0 check (e); conservative defaults; `last_reviewed`; legal review in P4 | Reviewer or GIC form disagrees | R1 |
| R11 | Scope creep or a member drops out | M | H | Core/Standard tiers; freezes in weeks 8 and 10; role merges | Burndown slips 2 weeks | R1 |
| R12 | Misleading city vs district figures | M | M | Mandatory chip; no mixed charts; automated test | Tile without `geo_level` | R4 |
| R13 | Users treat the helper as legal advice, or think it files for them | M | M | Disclaimers, "does not submit" notice, legal-aid pointers, GIC pre-flight | Usability feedback | R1 |
| R14 | GIC backlog delays any second appeal | H | L | Set expectations; report "pending at GIC" | GIC pendency figure | R1 |
| R15 | Scheduled Actions stop | M | L | Runbook, status page, handover owner | Freshness degrades | R5 |
| R16 | User testing without proper consent | L | M | Consent form approved by the instructor; anonymised notes | No signed forms | R1 |

---

## Changes from draft

- **Tiered scope with an hour budget.** Core is about 295 h and fits 3 people at about 70% of nominal hours; Standard adds about 130 h. The budget endpoint (unless found in the P0 spike), fcainfoweb, full PIO-list conversion, UDISE+, templates T7-T10 and the resident SUS study moved to Standard. The draft's 14 datasets and 10 templates did not fit a 3-person team.
- **The RTI critical path is reordered.** Approval and PIO confirmation move to week 0. The deadline engine and Form E generator are due by the end of week 5, because the team's own first-appeal window is 05-11 to 04-12-2026. The draft built them in weeks 7-11, and its example appeal (09-11) came before the tool existed.
- **Legal content corrected.**
  - Second-appeal window: day 46-120 is safe, and GIC rejects after day 135.
  - The complaint-limit conflict (30 vs 90 days) is flagged, and 30 days is the default until checked.
  - The unverified "no fee" for GIC was removed.
  - Letters now cite s.5(4) for other SMC departments, and ask for data "in the form held" to avoid s.7(9) refusals.
  - A transfer restarts the clock, and holidays don't extend deadlines.
- **New P0 checks:** reachability from GitHub runners, robots.txt and site policy per host, whether the rainfall page updates outside the monsoon, and GIC forms. Rainfall now runs daily, since the semester falls after the monsoon.
- **Ethics and impersonation rules added:**
  - no emblem, logos or official-looking domain, and a "does not submit" notice;
  - no appeals filed just to demo;
  - consent for user testing;
  - PIO directory limited to official contacts;
  - an ADR and instructor sign-off for undocumented endpoints;
  - no reuse of upstream geography files of unknown origin.
- **Filing logistics added:** in person vs Speed Post, three different applicants, a private filing log outside the repo, a Rs 1,000 petty-cash cap, and RTI replies typed in twice.
- **Concrete exit criteria.** "Demo accepted" became a 5-item checklist plus automated page-JSON, CSP and network tests. There are now separate freezes for data (week 8) and the helper (week 10), and the weekly demo is 15 minutes.
- **Static-export details:** CSP and headers via the host config, commits only when content changes, and 2 new risks (runner reachability and user-testing consent).