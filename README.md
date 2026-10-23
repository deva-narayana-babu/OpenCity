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

There are 21 Surat sources:

- **Surat Municipal Corporation:** budget summary, balance sheets, RTI returns, council (corporators and office bearers), disease statistics, solid waste, rainfall and Ukai dam levels, water quality, air quality, SMIMER hospital, e-buses, PMAY housing.
- **District level:** UDISE+ school data, NFHS-5 health indicators, GSEB board results, district court case counts.
- **Other bodies:** CityFinance audited accounts, CPCB air-quality bulletins, Gujarat reservoir levels, Agmarknet mandi prices.

Two sources need action before they load:

- **Agmarknet prices** need a free data.gov.in API key in `DATA_GOV_IN_API_KEY`.
- **Department of Consumer Affairs retail prices** are disabled, because every report now needs a captcha. A report saved by hand can still be parsed.

See [pipeline/README.md](pipeline/README.md) for how the refresher works.

## Licence

The project's own code and docs are under the MIT licence in [LICENSE](LICENSE). Files in [reference/](reference/README.md) are not covered by it: each stays under its publisher's terms, as noted in the manifest.
