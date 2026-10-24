# OpenCity

A civic-data dashboard for Surat, plus an RTI (Right to Information) helper: when a number on the dashboard looks bad or is missing, a citizen can ask the responsible office for the records behind it. This is a student course project, inspired by [forthepeople.in](https://forthepeople.in).

## What's in this repository

| Folder | What it holds |
|---|---|
| [pipeline/](pipeline/README.md) | The data pipeline: one adapter per source, the SQLite schema, the refresher and its tests |
| [scripts/](scripts/) | `refresh.sh` updates the database, `db.sh` shows how fresh each source is, `install-schedule.sh` runs the refresh hourly with cron |
| [data/](data/) | `opencity.db` and the CSV exports in `data/export/`. Raw downloads and logs stay on the machine that runs the refresh. |
| [reference/](reference/README.md) | Saved copies of the government documents behind the research, with a manifest of sources and checksums |
| [docs/](docs/) | Why Surat ([city-selection.md](docs/city-selection.md)), the semester [roadmap](docs/roadmap.md), and the full [research](docs/research/README.md) |

## Quick start

```bash
sudo apt install poppler-utils
scripts/refresh.sh
scripts/db.sh
```

The first refresh loads every source (about 10-15 minutes, with a polite gap between requests to each site). Later runs only fetch what is due.

## Data sources

There are 43 Surat sources:

- **Surat Municipal Corporation (23):**
  - Money: budget summary, balance sheets, tenders.
  - Council: corporators and office bearers, past elections.
  - Officials: officers and zone offices, helplines, recruitment ads, RTI returns.
  - Health: disease statistics, births and deaths, health centres, PM-JAY hospitals, SMIMER hospital.
  - City services: solid waste, rainfall and Ukai dam levels, water quality, air quality, streetlights, e-buses, PMAY housing, community-development schemes.
- **District and state (13):**
  - Census 2011, UDISE+ school data, NFHS-5 health indicators, GSEB board results.
  - District court case counts and NJDG court pendency.
  - Collectorate officers, taluka offices.
  - GSDMA taluka rainfall, Gujarat reservoir levels, Jal Jeevan Mission tap connections, Soil Health Card results.
  - NCRB crime figures for Surat city.
- **National bodies and other sources (7):** CityFinance audited accounts, CPCB air-quality bulletins, NDMA SACHET disaster alerts, Agmarknet mandi prices, Department of Consumer Affairs retail prices, AAI airport traffic, Open-Meteo forecast.

Each source's publisher, exact URLs, fields, caveats and current health are listed in [data/export/README.md](data/export/README.md). That file is regenerated on every refresh. [docs/metrics-report.md](docs/metrics-report.md) compares what we expose with what forthepeople.in shows for a district.

Four sources are built but load nothing until someone acts:

- **Agmarknet prices** need a free data.gov.in API key in `DATA_GOV_IN_API_KEY`.
- **Department of Consumer Affairs retail prices** are disabled, because every report now needs a captcha. A report saved by hand can still be parsed.
- **AAI airport traffic** is disabled, because its PDFs sit behind a name, email and OTP form.
- **Open-Meteo forecast** is disabled, because the API host's robots.txt disallows all crawlers. The maintainers must decide whether that applies to this client.

See [pipeline/README.md](pipeline/README.md) for how the refresher works.

## Licence

The project's own code and docs are under the MIT licence in [LICENSE](LICENSE). Files in [reference/](reference/README.md) are not covered by it: each stays under its publisher's terms, as noted in the manifest.
