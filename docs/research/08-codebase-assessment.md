# Upstream codebase assessment (forthepeople)

Based on a local clone of github.com/jayanthmb14/forthepeople at 38df958 (11 Jun 2026).

## How to add a district

Source: clone at /tmp/claude-1000/-home-deva-src-OpenCity/473ae9f8-f0a2-4667-963a-27ce0f03f491/scratchpad/ftp (HEAD 38df958, 11 Jun 2026). This recipe merges docs/SCALING-CHECKLIST.md with docs/DISTRICT-EXPANSION-SKILL.md (Pune #10 "6-prompt" pattern), then corrects both against the code. CONTRIBUTING.md "Adding a New District" is out of date: the schema doesn't need editing, and the directory is public/geo/, not public/geojson/.

0. SETUP
- Node 20+ and Postgres (Neon or local).
- Create .env.local with DATABASE_URL and ADMIN_SESSION_SECRET. src/lib/admin-auth.ts throws at module load if ADMIN_SESSION_SECRET is missing.
- Run: npm install, npx prisma generate, npm run db:push. The build no longer runs db push. `next build` statically renders DB-backed pages, so it needs a reachable DB.
- Do NOT run `npm run db:seed`. prisma/seed.ts starts with 52 global deleteMany({}) calls (the Mandya pilot reset).

1. HIERARCHY (DB)
- In prisma/seed-hierarchy.ts, upsert:
  - State {slug:'gujarat', nameLocal:'ગુજરાત', capital:'Gandhinagar'}.
  - District {slug:'surat', nameLocal, tagline, population, area, talukCount, literacy, sexRatio, density, avgRainfall, active:false}.
  - Taluk rows. For a city dashboard, follow Mumbai/Kolkata/Chennai: they put city zones in the taluk slot (mumbai-taluks.json = 5 zones). So SMC/AMC zones can be Taluk rows. There is no Ward or ULB model; DemographicLevel has a WARD enum value only.
- Run: npx tsx prisma/seed-hierarchy.ts. Gujarat is not in seed-hierarchy.ts today.

2. STATIC CONSTANTS
- In src/lib/constants/districts.ts (~line 1151), replace lockedDistrict('surat','Surat') with a full District object. Copy the Pune stub at lines 1111-1144: active:true, nameLocal, badges, stats, taluks[]. Set the Gujarat state to active:true.
- This file drives routing: [district]/layout.tsx calls getDistrict() and returns notFound() if it's missing. It also drives the sitemap, the locked preview and the compare selectors.

3. STATE CONFIG
- In src/lib/constants/state-config.ts, add `const GUJARAT: StateConfig` and register it in STATE_CONFIGS (~line 404). Without it, getStateConfig('gujarat') returns null and every page falls back to generic text.
- Fields: discom, water portal, GSRTC, GSEB SSC, Gujarat Information Commission + rtiPortalUrl, districtHeadTitle 'Collector', subDistrictUnit 'Taluka', policeSystemType 'commissionerate', showVillages / gramPanchayatApplicable / jjmApplicable false, municipalBody, stateHealthScheme, lastElection*, dataSources[], and tenderPortals only if Tenders will be used.
- Limitation: municipalBody and discom are per state, so SMC and AMC can't both be named without a per-district override.

4. SCRAPER / API NAME FIXES
- src/scraper/jobs/weather.ts: add an OWM_CITY_OVERRIDE entry.
- src/scraper/jobs/crops.ts: add an AGMARKNET_DISTRICT_OVERRIDE entry. Check the exact Agmarknet spelling first.
- src/scraper/jobs/news.ts: buildQueries() hardcodes "<district> Karnataka", and buildStaticSources() uses The Hindu and Deccan Herald Karnataka feeds. Make both use ctx.stateName and Gujarat feeds.
- src/scraper/jobs/schemes.ts: add gujarat:'GJ' to STATE_CODES. Without it the lookup falls back to 'KA'.
- Guard rti.ts, courts.ts and jjm.ts to Karnataka only. They hardcode the KIC URL, NJDG state_code "17" and JJM StateCode "29", with no state check.

5. FONTS / I18N
- In src/app/layout.tsx and globals.css, load Noto Sans Gujarati. --font-regional is hard-wired to Kannada (globals.css:51).
- Optionally add 'gu' to src/i18n/routing.ts (currently ["en","kn"]) and create src/dictionaries/gu.json (196 keys).
- Fix the hardcoded "ಕನ್ನಡದಲ್ಲಿ" label at file-rti/page.tsx:79.

6. GEO
- The district polygon already exists in public/geo/gujarat-districts.json, with slug 'surat'.
- Ahmedabad is slugged 'ahmadabad' there. GenericStateMap pushes /en/gujarat/ahmadabad, which 404s. Rename it or add an alias.
- Add public/geo/surat-taluks.json (zones or talukas, with _attribution). An empty stub with features:[] is acceptable, as Pune did.
- Add a DISTRICT_PROJECTION entry, plus TALUK_COLORS, in src/components/map/TalukMap.tsx:14. The default projection centres on Mandya.

7. DATA SEEDS
- Write prisma/seed-surat-*.ts files following Pune's pattern: 17 files, ~3.5k LOC, idempotent findFirst guards, and a source on every row.
- Models to seed: Leader (5 tiers; T1/T2 via scripts/fix-all-districts-leadership.ts), BudgetEntry + BudgetAllocation (amounts in Rupees), School (aggregate-first), Scheme, RtiTemplate, GovOffice, ServiceGuide, LocalIndustry, BusRoute/TrainSchedule, HousingScheme, PopulationHistory, DemographicProfile, FamousPersonality, ElectionResult.
- DemographicProfile: Census 2011 plus NITI MPI 2023 rows extracted with scripts/extract-mpi-barchart-full.ts.
- InfraProject and GovernmentExam fill from the news+AI pipeline (needs OPENROUTER_API_KEY). Exams can also be cloned with onboardDistrictExams(districtId).

8. PAGE CONTENT
- src/lib/constants/responsibility-content.ts: add per-district TS content.
- health/page.tsx STATE_HEALTH_SCHEMES: add a gujarat entry.
- industries/page.tsx: choose a mode (sugar/tech/heritage/general).

9. ACTIVATE
- Set District.active=true and goLiveDate using Prisma Studio, SQL, or a script modelled on scripts/activate-telangana-districts.ts. Leave tendersActive=false.

10. JOBS
- Vercel crons in vercel.json: scrape-news, scrape-crops, generate-insights, news-intelligence, scrape-budget, generate-citizen-tips, update-exams. They need CRON_SECRET.
- The Railway node-cron worker (npm run scraper, src/scraper/scheduler.ts) runs everything else. Most of those jobs skip Gujarat or are Karnataka-bound.

11. VERIFY
- Smoke-test every /en/gujarat/surat/<slug> route (36 sidebar slugs).
- Run npx tsc --noEmit and npm run build.
- Confirm NoDataCard shows on empty modules.
- Update docs/DATA-SOURCES.md.

## Modules: reuse for a Gujarat district

| Module | Current source | Gujarat reuse | Gujarat source suggestion | Effort |
|---|---|---|---|---|
| overview | District row, Leader rows and entity counts from manual seeds (seed-hierarchy + districts.ts), plus the latest OWM weather reading | as-is | Works once the hierarchy is seeded. Headline stats (population, area, literacy) come from the Census 2011 District Census Handbook for Surat / Ahmadabad. | S |
| leadership (leaders) | Manual seeds (Leader model, 5 tiers). T1/T2 auto via scripts/fix-all-districts-leadership.ts; T3-T5 by hand. The news pipeline updates later. | needs-gujarat-source | ECI / Gujarat Legislative Assembly lists of MPs and MLAs. Collector from the district NIC portal. Municipal Commissioner and Mayor from SMC/AMC sites. Police Commissioner from the city police site. Use 'Verify at <portal>' when unsure. | S |
| finance (budget) | Manual seeds: BudgetEntry, BudgetAllocation, RevenueEntry, RevenueCollection. budget.ts has a null resource for every state (no-op). finance.ts queries an unverified data.gov.in resource labelled 'Karnataka Finance Dept'. | needs-gujarat-source | SMC/AMC annual budget books (PDF, often Gujarati plus English), Gujarat Finance Department budget publications, PFMS. Entered manually or extracted from PDFs. | M |
| infrastructure | News-driven: Google News RSS, then OpenRouter free-model extraction and verification, then InfraProject/InfraUpdate. NATIONAL/STATE projects fan out automatically (e.g. Mumbai-Ahmedabad bullet train). PMGSY data.gov.in scraper is secondary. | as-is | Works with OPENROUTER_API_KEY. Optionally seed SMC/AMC Smart City and Gujarat Metro Rail project lists from official sources. | S |
| crops (food / mandi prices) | Agmarknet daily mandi prices through the data.gov.in API (resource 9ef84268..., national), filtered by state and district name | as-is | Set DATA_GOV_API_KEY and check the Agmarknet district spelling for Surat and Ahmedabad. For consumer food prices, consider adding the Dept of Consumer Affairs price-monitoring retail series (check whether these cities are reporting centres). | S |
| weather | OpenWeatherMap current-weather API (OPENWEATHER_API_KEY), city = district name or override. RainfallHistory from manual seed. | as-is | Add OWM overrides, or switch to Open-Meteo (no key). IMD district rainfall for history. | S |
| water (dams) | Karnataka WRD POST API (water.karnataka.gov.in) only; other states skip gracefully | drop-or-defer | If kept: CWC weekly reservoir bulletin (PDF, national) for reservoirs feeding the cities, and SMC/AMC water-supply data. City water supply is more relevant than dams. | M |
| news | Google News RSS plus static feeds. buildQueries() hardcodes 'Karnataka'; static feeds are The Hindu / Deccan Herald Karnataka. | needs-gujarat-source | Build Google News RSS queries from '<city> Gujarat'. Swap in Gujarat or city-edition RSS feeds (English and Gujarati outlets; check each feed URL). | S |
| alerts | Google News RSS keyword search (district slug + topic) with regex severity classification | as-is | Works unchanged; could add SMC/AMC and IMD Ahmedabad advisories. | S |
| schemes | MyScheme.gov.in search API plus manual seeds. STATE_CODES has no gujarat, so it falls back to 'KA' (Karnataka schemes). | as-is | Add gujarat:'GJ' to STATE_CODES in schemes.ts. Seed Gujarat state and SMC/AMC schemes by hand. | S |
| health | No data model. Static national helplines, STATE_HEALTH_SCHEMES (no gujarat entry), DepartmentStaffing widget and module news. docs note the Hospital model is missing entirely. | needs-gujarat-source | New model and UI. HMIS district indicators; NFHS-5 district factsheets for Surat / Ahmadabad (Harvard Dataverse CSV mirror); Gujarat Health and Family Welfare Department; SMC/AMC municipal hospital data (often RTI-only). | L |
| police | Manual seeds (PoliceStation, CrimeStat, TrafficCollection) plus data.gov.in resources: NCRB-by-district and 'Traffic challans Karnataka' (IDs and lowercase-slug filters unverified) | needs-gujarat-source | NCRB Crime in India metropolitan-city and district tables (annual). Surat / Ahmedabad Police Commissionerate sites for the station list. | M |
| elections | Manual ElectionResult seeds plus a data.gov.in ECI resource (Karnataka-labelled, unverified) | needs-gujarat-source | ECI results for the Gujarat assembly and Lok Sabha elections. Gujarat State Election Commission for SMC/AMC municipal polls. | M |
| transport | Manual BusRoute/TrainSchedule seeds. data.gov.in bus resource exists only for Karnataka (KSRTC); other states skip. Train resource unverified. | drop-or-defer | Later: GSRTC, SMC city bus/BRTS, AMC AMTS/BRTS, Gujarat Metro Rail. Check for published GTFS; otherwise seed by hand. | M |
| power | BESCOM planned-outage HTML parser only (Karnataka); other states skip | drop-or-defer | Later: the private licensee in the city areas and the state DISCOMs (DGVCL/UGVCL) outage notices. Confirm which licensee serves each area. | M |
| schools (education) | Manual School/SchoolResult seeds (aggregate-first) plus a data.gov.in UDISE resource (Karnataka-labelled, lowercase-slug filter, unverified) | needs-gujarat-source | UDISE+ district report cards, GSEB SSC/HSC district results, SMC and AMC municipal school boards (enrolment, teachers, infrastructure). | M |
| gram-panchayat | MGNREGA data.gov.in resource ('Karnataka GPs') plus GramPanchayat seeds | drop-or-defer | Not applicable to a city dashboard (set gramPanchayatApplicable:false, as Maharashtra does) | S |
| rti (RTI Tracker) | RtiStat from src/scraper/jobs/rti.ts, which parses the Karnataka Information Commission HTML table for every active district with no state guard | needs-gujarat-source | Disable the KIC job for Gujarat. Seed from Gujarat Information Commission annual reports (state and department level), SMC/AMC RTI registers or Section 4 disclosures, and crowd-sourced outcomes from the students' helper. | M |
| courts | CourtStat seeds plus an NJDG API call hardcoded to state_code '17' with the slug as district code (no state guard; likely never worked) | needs-gujarat-source | Periodic manual snapshot of the NJDG district dashboard (Surat district court; Ahmedabad city civil and sessions court and rural courts) | M |
| industries (local industries) | Manual LocalIndustry seeds; the page picks sugar/tech/heritage/general mode | needs-gujarat-source | District Industries Centre profiles, MSME Udyam district data, GIDC estates, iNDEXTb (e.g. Surat textiles and diamonds) | M |
| sugar-factory | SugarFactory / SugarFactorySeason manual seed (Mandya only) | drop-or-defer | Not relevant | S |
| soil / farm advisory | SoilHealth data.gov.in resource plus AgriAdvisory seeds | drop-or-defer | Not relevant to a city MVP (Soil Health Card portal if ever needed) | S |
| housing | HousingScheme; data.gov.in PMAY-G (rural) resource plus seeds | drop-or-defer | Later: PMAY-Urban MIS/dashboard, SMC/AMC EWS housing project lists | M |
| jjm (Jal Jeevan Mission) | eJalShakti API hardcoded to StateCode '29' (Karnataka); rural household tap connections | drop-or-defer | Rural-only; set jjmApplicable:false for city dashboards | S |
| offices | Manual GovOffice seeds | needs-gujarat-source | District NIC portal, SMC/AMC zone and ward office directories, Digital Gujarat. Reusable as the PIO directory base. | S |
| population | DemographicProfile (Census 2011 + NITI MPI 2023 via extraction scripts) plus PopulationHistory seeds | needs-gujarat-source | Same national sources, but Gujarat rows must be extracted: Census 2011 District Census Handbook for Surat / Ahmadabad (and SMC/AMC town tables for city figures), NITI MPI 2023 PDF district rows, NFHS-5 district factsheets. Watch the 'Ahmadabad' spelling. | M |
| famous-personalities | Manual Wikipedia-sourced seeds (CC-BY-SA) | drop-or-defer | Optional; Wikipedia if kept | S |
| citizen-corner | CitizenTip rows generated by the generate-citizen-tips cron (OpenRouter), plus seeds | drop-or-defer | Optional; could become the RTI-walkthrough entry point instead | S |
| data-sources | StateConfig.dataSources plus UNIVERSAL_DATA_SOURCES (static) | as-is | Works once a GUJARAT StateConfig is added | S |
| file-rti (extra; beyond the 29) | Manual RtiTemplate seeds; copy-to-clipboard; link to rtionline.gov.in (central authorities only) | needs-gujarat-source | This is the students' core contribution. PIO/FAA lists from SMC/AMC, Collectorate and state-department Section 4(1)(b) disclosures; Gujarat Information Commission; Gujarat RTI Rules fee and payment modes (verify). | L |
| tenders (extra) | 6 procurement portals (KPPP Karnataka, CPPP/GePNIC, IREPS, defproc, BEL, HAL) through custom engines; gated by District.tendersActive | drop-or-defer | Later: Gujarat's state e-procurement portal would need a new engine; the CPPP (nicgep) engine is reusable for central tenders | L |
| exams (extra) | National exams (UPSC/SSC/IBPS/RRB) plus Karnataka KPSC/KEA scrapers and a news pipeline; onboardDistrictExams clones national rows | as-is | National rows work through onboardDistrictExams; GPSC/GSSSB can come later | S |
| services (extra) | Manual ServiceGuide seeds | needs-gujarat-source | Digital Gujarat portal, SMC/AMC online civic services (certificates, property tax) | S |
| responsibility (extra) | Hardcoded per-district TS content (responsibility-content.ts) plus ResponsibilityItem | drop-or-defer | Optional hand-written content | S |
| map (extra) | public/geo/*-districts.json and *-taluks.json via react-simple-maps; TalukMap has a per-district projection table | needs-gujarat-source | District polygon already exists. Need zone/ward polygons: SMC/AMC GIS, or check DataMeet Municipal_Spatial_Data (CC-BY). Fix the 'ahmadabad' slug. | M |
| contributors / update-log (extra) | Supporter model with Razorpay payments; UpdateLog of admin/scraper changes | drop-or-defer | Drop contributors (Razorpay needs business KYC). update-log is generic and can stay. | S |

## Gujarat assets that already exist

- src/lib/constants/districts.ts:1151-1161 has a Gujarat state entry (slug 'gujarat', nameLocal 'ગુજરાત', capital Gandhinagar, active:false) with 5 lockedDistrict() stubs: ahmedabad, surat, vadodara, rajkot, gandhinagar. Each stub is just slug + English name (nameLocal = English name), taluks:[], no stats. These stubs are what render the '29 data dashboards are waiting to be unlocked' placeholder (LockedDistrictPreview.tsx:133).
- public/geo/gujarat-districts.json (313 KB GeoJSON FeatureCollection) has 26 district features with {name, slug, stateSlug}, including 'surat' and 'ahmadabad'. Census-2011 vintage: 26 districts, with no post-2013 districts (Botad, Morbi, Aravalli, Mahisagar, Chhota Udaipur, Devbhumi Dwarka, Gir Somnath), so the Ahmedabad polygon is probably pre-Botad (verify). No inline source attribution. The slug 'ahmadabad' does not match the constant 'ahmedabad', so clicking Ahmedabad on the state map routes to a 404.
- public/geo/india-states.json includes the Gujarat state polygon. src/components/map/DrillDownMap.tsx:29 and scripts/setup-state-maps.ts:38 map 'Gujarat' to 'gujarat'.
- src/lib/data/district-meta.ts:123 has the state code GJ: 'Gujarat'. src/lib/constants/infra-locations.ts:86 has a 'surat: null' placeholder.
- src/lib/infra-sync.ts:238 NAMED_CITY_RX already includes ahmedabad|surat|vadodara, so infra news naming those cities is detected for scope classification. NATIONAL projects such as the Mumbai-Ahmedabad bullet train (prisma/seed-maharashtra-state-infra.ts, seed-mumbai-data.ts) fan out to every active district automatically.
- Gujarat state-level values appear only on the national /india pages: src/lib/india/mock-state-data.ts (explicitly MOCK, not citable) and prisma/seed-india-natural-resources-energy.ts (CEA Gujarat renewable capacity metric).
- Gujarati script support exists only in src/lib/india/design-tokens.ts (language rotator) and src/lib/validators/contributor-name.ts (allows Gujarati characters).
- Community: README lists '@tiwarikaran — Ahmedabad district (in progress)'. docs/LIVE-STATE.md records issue #13 (Ahmedabad) triaged 'ENCOURAGE', pointing to Pune as the template. The repo references #13, not #11. No Ahmedabad code has been merged.
- NOT present: no GUJARAT entry in src/lib/constants/state-config.ts; no Gujarat rows in prisma/seed-hierarchy.ts (so none in the DB); no seed-surat-* or seed-ahmedabad-* files; no Gujarat taluk or zone GeoJSON; no Gujarat OWM or Agmarknet overrides; no 'gu' locale (only en/kn) and no Noto Sans Gujarati font; no Gujarat RTI templates, StateConfig RTI portal or scraper sources.

## External services

| Service | Purpose | Needed for MVP | Free tier OK | Alternative |
|---|---|---|---|---|
| PostgreSQL (Neon recommended) + Prisma 7.5 with @prisma/adapter-pg | All app data: 108 models, 22k LOC of seeds. `next build` also needs a reachable DB because it statically renders DB-backed pages. Env: DATABASE_URL (src/lib/db.ts throws if unset). | yes | yes | Local Postgres (docker postgres:16-alpine), Supabase free tier; SQLite or flat JSON/CSV in a build-fresh app |
| Vercel hosting (region bom1) | Next.js 16 hosting. vercel.json also sets the X-Creator/X-License headers. | yes | yes | Netlify or Render free tiers; `next start` on any VM; static export for a lighter rewrite |
| Vercel Cron (7 schedules in vercel.json) | scrape-news (daily), scrape-crops (daily), generate-insights (twice daily), news-intelligence (every 4h), scrape-budget (weekly), generate-citizen-tips (weekly), update-exams (daily). Protected by CRON_SECRET. | no | no | Upstream README assumes Vercel Pro; Hobby-tier cron frequency limits may not cover the sub-daily jobs (check current limits). GitHub Actions scheduled workflows running `npx tsx` jobs are free. |
| Railway worker (Dockerfile.scraper, `npm run scraper` = node-cron in src/scraper/scheduler.ts) | 24/7 scheduler for weather (5 min), crops, power, dams, news, alerts, police, infra, exams, RTI, courts, MGNREGA, JJM, housing, schools, finance, transport, schemes, soil, elections. Most of these jobs are Karnataka-bound. | no | no | Upstream pricing doc lists about $5/mo. Use GitHub Actions cron or Vercel cron routes for the few jobs that matter (weather, crops, news). |
| Upstash Redis (REST) | API response cache, rate limiting (fails open), admin sessions (admin:session:<id>), vault TOTP sessions. Env: REDIS_URL, REDIS_TOKEN. If unset, cache is disabled; admin login needs it. | no | yes | Skip it (the app degrades). The docker-compose TCP redis://redis:6379 does NOT work with the @upstash/redis REST client. |
| App secrets (local, no vendor) | ADMIN_SESSION_SECRET (required: admin-auth.ts throws at module load), ADMIN_PASSWORD, ENCRYPTION_SECRET, CRON_SECRET, TOTP_ENCRYPTION_KEY, VOTE_IP_SALT, SEED_SECRET, ADMIN_ALLOWED_IPS, NEXT_PUBLIC_SITE_URL/NAME | yes | yes | Generate with openssl rand -hex 32. Note docker-compose still passes the outdated ADMIN_SECRET name. |
| data.gov.in Open Government Data API | Agmarknet crop prices, plus schools, police, elections, housing, MGNREGA, soil, finance and transport scrapers (several resource IDs unverified or Karnataka-specific). Env: DATA_GOV_API_KEY. | yes | yes | Free registration; or download dataset CSVs manually and commit them |
| OpenWeatherMap | Current weather every 5 min. Env: OPENWEATHER_API_KEY. | no | yes | Open-Meteo (no key, free) or IMD. Upstream doc cites a 1,000 calls/day OWM free tier. |
| Google News RSS (no key) | News, alerts, and the input to the infra/exam extraction pipelines | yes | yes | Publisher RSS feeds directly |
| OpenRouter | All AI through callAI(): free models (gpt-oss-20b, qwen3 etc.) for news classification and infra/exam extraction; Gemini 2.5 Pro (paid) for module insights, infra analysis, weekly platform report; Claude Sonnet (paid) for the fact-checker. Env: OPENROUTER_API_KEY. | no | no | Disable the AI cards. Free models only work partially (docs note the free tier hitting ~200 req/day limits). The students' RTI helper doesn't need an LLM. |
| Anthropic API (optional direct provider) | ANTHROPIC_API_KEY / ANTHROPIC_BASE_URL with FTP_AI_PROVIDER=anthropic bypasses OpenRouter | no | no | Omit. (@google/generative-ai is a dependency, but no GEMINI_* env var is read in code, even though CONTRIBUTING.md mentions GEMINI_API_KEY.) |
| Razorpay | Supporter/sponsor payments and subscriptions. Env: RAZORPAY_KEY_ID/SECRET, NEXT_PUBLIC_RAZORPAY_KEY_ID, RAZORPAY_WEBHOOK_SECRET, RAZORPAY_PLAN_*. The client throws if keys are missing when invoked. | no | no | Drop (live mode needs business KYC; not appropriate for a course project) |
| Resend | Admin alert emails. Env: RESEND_API_KEY, ADMIN_EMAIL, ADMIN_RECOVERY_EMAIL/PHONE. Returns an error object if unset. | no | yes | Omit or use console logging |
| Sentry | Error monitoring plus the admin error feed. Env: NEXT_PUBLIC_SENTRY_DSN, SENTRY_AUTH_TOKEN, SENTRY_API_TOKEN, SENTRY_ORG, SENTRY_PROJECT. | no | yes | Omit |
| Plausible Analytics | Cookieless analytics plus the admin Traffic tab. Env: NEXT_PUBLIC_PLAUSIBLE_DOMAIN, PLAUSIBLE_API_KEY, PLAUSIBLE_SITE_ID. | no | no | Omit, self-host, or use Umami / Vercel Analytics free |
| Google Fonts / next/font (Noto Sans regional scripts) | Kannada/Devanagari via next/font; Tamil/Bengali/Telugu via CSS @import. Gujarati is missing. | yes | yes | Add Noto Sans Gujarati via next/font |

## Existing RTI module

The upstream has two RTI modules, and neither is a citizen filing helper.

1) RTI Tracker (/[district]/rti, 142 LOC)
- Reads /api/data/rti, which returns RtiStat rows (department, year, month, filed, disposed, pending, avgDays, source) and RtiTemplate rows for the district.
- Shows total filed / disposed / pending and pendency % for the latest year, a department-wise stacked bar chart and a table, plus a "File RTI" call-to-action. It falls back to NoDataCard when empty.
- The only automated feed is src/scraper/jobs/rti.ts, a daily Railway job. It parses the Karnataka Information Commission "RTI Statistics" HTML table for every active district with no state check. For Surat it would write nothing, or attach Karnataka numbers to Surat.
- Its Math.random() "estimated" fallback was removed in June 2026 (BUG-TRACKER DATA-1).
- Latent bug: RtiStat.avgDays is nullable and the scraper never sets it, but the page calls s.avgDays.toFixed(1) and the hook types it as number.
- So for Gujarat this module needs a different source, e.g. Gujarat Information Commission annual reports (state/department level) and SMC/AMC RTI disclosures, or crowd-sourced outcomes.

2) File RTI (/[district]/file-rti, 116 LOC client page)
- Lists hand-seeded RtiTemplate rows: topic, topicLocal, department, pioName, pioAddress, feeAmount, templateText with [placeholders], templateTextLocal, tips. Example: prisma/seed-pune-rti.ts has 5 templates with PIO postal addresses and a "₹10" fee.
- The user picks a topic, sees a "To:" block and the text, clicks Copy, and gets a "File Online" link hard-wired to rtionline.gov.in. That portal serves central public authorities only, not SMC/AMC or Gujarat state departments.
- The local-language heading is hardcoded in Kannada.

What it does not have:
- No step-by-step walkthrough.
- No placeholder filling or document generation (PDF/print).
- No state-specific rules: Gujarat RTI Rules fee, payment modes and BPL exemption must be verified and encoded.
- No PIO/FAA directory separate from templates.
- No routing between central, state and municipal authorities.
- No deadlines, first/second appeal flow, reminders or filing history.
- No link from a metric gap to a template.
- No citizen accounts (only admin auth exists).

How the students' helper would differ and plug in:
(a) PIO directory: a new PublicAuthority/PIO model. Fields: authority, level (central/state/ULB), department/zone, PIO and APIO, First Appellate Authority name/designation/address/email, State Information Commission, the Section 4(1)(b) source URL, and lastVerifiedAt. Seed it for SMC or AMC departments and zones, the Collectorate, police commissionerate and relevant state departments. GovOffice seeds are a starting point.
(b) Richer templates: extend RtiTemplate with a metric link (module + metric key), structured placeholders, Gujarati text, applicable rules and fee, and an authority foreign key. These templates come straight from the dashboard's "not publicly available" gaps.
(c) Guided wizard:
  - choose the metric gap, then the matching authority;
  - specific, dated questions under Section 6(1), with no "why" questions;
  - fill in applicant details client-side;
  - generate a printable PDF;
  - pick the right channel: rtionline.gov.in for central bodies, state/municipal filing (offline or any state online facility) for SMC/AMC and Gujarat departments.
(d) Deadline and appeal tracker:
  - reply due in 30 days (Section 7(1)); 48 hours for life/liberty; +5 days if filed via an APIO (Section 5(2)); 40 days when a third party is involved (Section 11);
  - first appeal to the First Appellate Authority within 30 days of the reply or deemed refusal (Section 19(1));
  - second appeal or complaint to the Gujarat Information Commission within 90 days (Section 19(3) / Section 18).
  Store this client-side (localStorage plus .ics calendar reminders) to avoid holding personal data under DPDP, or add opt-in auth.
(e) Integration hooks: NoDataCard (src/components/common/NoDataCard.tsx) and DataSourceBanner render on every module page. Adding an "Ask for this via RTI" call-to-action there, pre-filled with the module/metric and authority, is the natural way to turn dashboard gaps into RTI filings.
(f) Optionally, anonymised, consented filing outcomes (response time, disposal) could populate an RtiStat-style table, replacing the Karnataka-only scraper with Gujarat data.

Caveat for upstreaming: docs/LEGAL-COMPLIANCE.md bans UI copy such as "hold power accountable" and "corruption". An accountability-framed RTI helper would have to follow those copy rules if contributed upstream.

## Licence obligations

The LICENSE is MIT plus extra attribution conditions, so it is not plain OSI MIT, even though package.json just says "MIT". Its text: "Copyright (c) 2026 Jayanth M B" and "Original Creator: Jayanth M B, Karnataka, India", with the standard MIT grant, then these conditions.

(A) "The above copyright notice, this permission notice, and the attribution to the original creator (Jayanth M B) shall be included in all copies or substantial portions of the Software."

(B) "Any derivative work, fork, or deployment of this Software must:"
1. "Retain the original creator attribution in the source code headers." This is the /** ForThePeople.in — Your District. Your Data. Your Right. © 2026 Jayanth M B. MIT License with Attribution. https://github.com/jayanthmb14/forthepeople */ block. It is present in 364 of 690 src .ts/.tsx files; keep it in every copied file.
2. Include "Originally created by Jayanth M B" in any public-facing About page, README, or documentation. That exact phrase is not in upstream src/README today, so a fork has to add it.
3. "Not remove or obscure the X-Creator HTTP headers from API responses." X-Creator: Jayanth M B is set in next.config.ts:22, vercel.json:18 and src/lib/watermark.ts:28. Keep all three.

The usual MIT warranty disclaimer also applies.

What this means in practice:
- A full fork must keep the LICENSE file, the copyright line, the per-file headers, the About/README credit line, and the X-Creator header on API responses. The students can add their own copyright to new files.
- In a build-fresh or hybrid approach, any file or substantial portion copied (components, seeds, scraper logic, the Gujarat GeoJSON the upstream committed) must carry the notice and header, and the app should credit "Originally created by Jayanth M B" on its About page and README.
- Reusing only ideas, the module taxonomy or UX patterns, with no copied code, does not trigger the license. Crediting the inspiration is still good practice.

Separate from the code license, the data has its own attribution rules:
- Government data: GODL-India or source attribution.
- Wikipedia content: CC-BY-SA.
- DataMeet boundaries: CC-BY 2.5 IN. The upstream geo files lack inline attribution (docs call this historical debt), so the students must record provenance themselves.

## Recommendation: hybrid

Build a fresh, lighter app for Surat (or Ahmedabad). Use forthepeople as a reference and a small asset donor, not as the codebase, and optionally send one small, well-scoped Gujarat PR upstream at the end.

Why not fork:
- The upstream is very large: ~117k LOC of TS/TSX in 690 src files, 108 Prisma models, 127 API route files, 81 pages, 279 components, 67 seed files (22k LOC) and 91 scripts, with zero automated tests.
- Its docs are mostly long AI-session logs (BLUEPRINT-UNIFIED is 3,264 lines) and partly out of date: CONTRIBUTING, docker-compose, the README module count.
- More than half the surface is irrelevant to the course: admin vault/TOTP, Razorpay sponsorships, tenders (Karnataka portals), India-level pages, AI fact-checker and platform reports.
- Setup friction is real: a mandatory ADMIN_SESSION_SECRET, a DB needed at build time, Upstash for admin sessions, and paid or complex services assumed (Vercel Pro crons, Railway worker, OpenRouter Gemini, Razorpay, Plausible).
- For a new district, the 'live' layer mostly doesn't carry over. Only weather (OWM), crop prices (Agmarknet via data.gov.in), and news/alerts via Google News RSS work nationally, and news still needs its hardcoded 'Karnataka' query fixed. The RTI, courts and JJM scrapers hardcode Karnataka with no state guard; power and dams skip non-Karnataka states. Pune's launch was 17 hand-written seed files.
- So a fork would spend most of the semester stripping and seeding someone else's schema. The students' own work would be a thin, hard-to-grade slice of a codebase they didn't design, with attribution headers on every file.

Why not contribute upstream:
- The upstream Ahmedabad effort (issue #13 per LIVE-STATE; README 'in progress') stalled.
- Expansion follows the maintainer's own Claude Code 6-prompt workflow and review cadence.
- Its copy rules ban accountability language central to the students' framing.
- The model is district-level (State→District→Taluk) with no ULB/ward layer, while SMC/AMC publish most civic data.
- Grading their share would be ambiguous.

Why hybrid works:
- Fresh Next.js (or Astro) plus SQLite/Postgres or versioned CSV/JSON in git.
- GitHub Actions for scheduled refresh; free hosting; Recharts. The students own the design and schema, e.g. a city→zone→ward model for the municipal corporation.
- Borrow proven patterns, credited, without copying code: the StateConfig single source of truth; the zero-fabrication rule with DataSourceBanner provenance and a NoDataCard honest empty state; the RtiTemplate schema; aggregate-first seeding; the Agmarknet/OWM fetch approach.
- Copy only small assets under the license terms (header plus credit plus attribution), e.g. gujarat-districts.json with its slug fixed.
- Spend most of the effort on the differentiator: the metric-gap-to-RTI wizard, the PIO directory, and the deadline/appeal tracker.

Optional give-back PR, small and uncontroversial: GUJARAT StateConfig, the 'ahmadabad' slug fix, the schemes 'GJ' code, state guards on the Karnataka-only scrapers, Surat RTI templates.

City choice, from the codebase alone:
- Near parity.
- Surat is marginally easier: its slug matches the geo file and its polygon is likely current. Ahmedabad needs the slug fix and probably a boundary update.
- The data-availability comparison should decide it.

## Effort estimate

These are my rough estimates, not measured figures, in person-weeks (pw) of ~40 h.

Team capacity:
- A 3-5 person student team at ~8-12 h/week each over a ~14-week semester has roughly 10-20 pw of development capacity in total.

Fork path (Surat MVP of ~10-12 modules plus the RTI helper): ~15-24 pw, which is over that capacity.
- Local setup, secrets, a DB for the build, and stripping or disabling payments/tenders/admin/AI: 2-3 pw.
- Gujarat foundation (hierarchy seed, districts.ts, GUJARAT StateConfig, scraper name fixes and state guards, Gujarati font/locale, geo slug and zone file): 1-2 pw.
- Manual, source-cited seeding of ~8-10 data modules (leaders, budget, schools, police, elections, population, offices, services, industries): 6-10 pw. Budget PDFs, often Gujarati, are the slowest part.
- New health model and UI: 2-3 pw.
- RTI helper (PIO directory, templates, wizard, deadline/appeal tracker): 4-6 pw.

Hybrid / build-fresh path: ~12-20 pw, which fits the team.
- Skeleton, data model, CI/cron and deploy: 2-3 pw.
- 6-8 metric pipelines at 1-2 pw each, prioritising crop/food prices, weather, municipal budget, schools, health, crime, population: 6-12 pw. Crop and weather reuse the national APIs quickly.
- RTI helper, the students' graded core: 4-6 pw.
- Testing, docs and attribution: 1-2 pw.

Scope levers:
- Drop transport, power, dams, JJM, gram panchayat, tenders, contributors and famous people.
- Treat metrics that aren't publicly available as RTI templates rather than pipelines.

## Challenges

- Codebase size and opacity: ~117k LOC across 690 TS/TSX files, 108 Prisma models, 127 API route files, 81 pages, 279 components, 67 seed files (22k LOC), 91 scripts, 0 tests. It was built largely through AI-assisted sessions, and the docs are long session logs (BLUEPRINT-UNIFIED is 3,264 lines).
- Out-of-date or contradictory docs and config. CONTRIBUTING says to add the district to schema.prisma, use public/geojson/, '45+ models', and GEMINI_API_KEY; the reality is public/geo/, 108 models, and OpenRouter only. The '29 dashboards' marketing count differs from the 36 sidebar modules. docker-compose passes a TCP REDIS_URL, which the Upstash REST client can't use, and ADMIN_SECRET instead of the required ADMIN_SESSION_SECRET.
- The live data layer barely transfers to Gujarat:
- rti.ts (KIC URL), courts.ts (NJDG state_code '17') and jjm.ts (StateCode '29') hardcode Karnataka with no state guard, so they could mis-attribute Karnataka data to a Gujarat district.
- news.ts queries '<district> Karnataka' and uses Karnataka RSS feeds.
- schemes.ts falls back to state code 'KA'.
- power, dams and transport skip non-Karnataka states; budget.ts is a no-op.
- Several data.gov.in resource IDs look unverified and filter on lowercase slugs.
- Real district content (e.g. Pune) was hand-seeded in 17 files.
- City vs district mismatch: the model is State→District→Taluk→Village, with no ULB or ward entity. StateConfig allows one municipalBody and one discom per state, so SMC and AMC can't both be represented. SMC/AMC municipal data covers only part of Surat/Ahmedabad district, while Census, NFHS and MPI data are district-level. Every metric needs its geography labelled.
- Geo issues: gujarat-districts.json is Census-2011 vintage (26 districts; newer districts such as Botad are missing, so the Ahmedabad polygon is likely stale). The Ahmedabad slug is 'ahmadabad' against the constant 'ahmedabad', so the map click 404s. There are no zone or ward polygons, and there is no attribution. TalukMap's default projection centres on Mandya.
- Health, a core metric for the students, has no data model upstream: only static helplines, national schemes and a staffing widget. It needs new schema, UI and sources (HMIS, NFHS-5 district factsheets, municipal hospitals).
- Setup cost and paid services:
- ADMIN_SESSION_SECRET is required at module load.
- `next build` needs a reachable DB.
- Admin login needs Upstash.
- The upstream assumes Vercel Pro crons, a Railway worker (~$5/mo), OpenRouter paid models (Gemini 2.5 Pro insights, Claude fact-check), Razorpay (business KYC) and Plausible.
- prisma/seed.ts wipes 52 tables with deleteMany({}), a trap for newcomers.
- Language: the app only has en/kn locales. --font-regional is hard-wired to Kannada, the File RTI page has a hardcoded Kannada label, and Noto Sans Gujarati isn't loaded. Many SMC/AMC and state documents are Gujarati PDFs, possibly scanned, so extraction takes effort.
- RTI specifics: rtionline.gov.in, the only filing link upstream, covers central authorities only. SMC/AMC and Gujarat departments follow the state RTI rules and channels (fee and payment modes need verifying). PIO/FAA details must be collected from Section 4(1)(b) disclosures and kept current. A deadline/appeal tracker handles personal data, so prefer client-side storage or explicit consent (DPDP Act).
- Latent bugs a fork would inherit, e.g. RtiStat.avgDays is nullable but the RTI page calls .toFixed() on it (the client type says number). The upstream also left fabricated 'estimated' RTI/court rows in prod that need a manual purge script (BUG-TRACKER DATA-1).
- Governance and grading: contributing upstream depends on the maintainer's review and his own district-launch workflow, and the prior Ahmedabad effort stalled. The upstream copy rules ban phrases like 'hold power accountable' and 'corruption'. In a fork, the students' own contribution is hard to isolate, and the license requires keeping the creator headers, the 'Originally created by Jayanth M B' credit and the X-Creator response headers.
