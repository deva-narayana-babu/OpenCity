# Reference documents

Local copies of the government documents, datasets and page snapshots gathered during the Surat vs Ahmedabad research (24-28 Sep 2026). The findings they support are written up in [docs/research/](../docs/research/README.md), [docs/city-selection.md](../docs/city-selection.md) and [docs/roadmap.md](../docs/roadmap.md).

161 items, 211.1 MB. Every file is listed in [manifest.csv](manifest.csv), which gives its source URL, retrieval date, size, sha256, licence note and the research finding it supports.

## Folders

| Folder | Covers | Items | Size | Research page |
|---|---|---|---|---|
| [budget/](budget/README.md) | Budget and public finance | 17 | 91.1 MB | [01-budget.md](../docs/research/01-budget.md) |
| [education/](education/README.md) | Education | 16 | 16.4 MB | [02-education.md](../docs/research/02-education.md) |
| [food-prices/](food-prices/README.md) | Food prices and food security | 8 | 3.4 MB | [03-food-prices.md](../docs/research/03-food-prices.md) |
| [health-environment/](health-environment/README.md) | Health, sanitation and environment | 28 | 25.4 MB | [04-health-environment.md](../docs/research/04-health-environment.md) |
| [governance/](governance/README.md) | Civic governance, open data, safety, courts, transport | 21 | 10.8 MB | [05-governance.md](../docs/research/05-governance.md) |
| [district-modules/](district-modules/README.md) | Census, dams and rainfall, power, housing, maps, leadership | 29 | 48.7 MB | [06-district-modules.md](../docs/research/06-district-modules.md) |
| [rti/](rti/README.md) | RTI ecosystem | 42 | 15.2 MB | [07-rti.md](../docs/research/07-rti.md) |

## What is and isn't in here

This repository is public, so a download was copied here only if all of these hold:

1. **It is primary evidence.** It is an official document, a dataset or API response, or a snapshot of a page whose tables, lists or dates support a research finding.
2. **It may be redistributed.** It was published by a government or public authority (central, Gujarat state, SMC/AMC, district collectorates, commissions, statutory bodies), or it carries an open licence (recorded in `licence_note`).
3. **It exposes no private individuals.** Lists of public officials and elected representatives, published by the authority itself, are kept.
4. **It contains no secrets.** No API keys, tokens or cookies.

Left out:
- scraper leftovers: JavaScript bundles, scripts, cookie jars, logs;
- duplicates;
- navigation pages and app shells;
- error pages;
- text extracts and page renders that can be regenerated from a kept original.

Some documents were left out only because of copyright (news, rating agencies, commercial sites) or because they name private individuals (for example RTI appeal orders). Those are **linked, not copied**, in each folder's README.

## Using these files

- **Snapshots are frozen.** Each file is fixed as of its retrieval date. Many sources are overwritten in place (SMC's quarterly RTI return, the weekly budget summary), so these copies are also the only record of those versions.
- **HTML snapshots are raw.** They are saved as downloaded, so pages may look unstyled offline. The data in their tables is intact.
- **Legacy-font PDFs.** Several Gujarati PDFs (the SMC PIO list, budget books) use legacy fonts: text extraction garbles the Gujarati, but the numbers, phone numbers and emails extract cleanly.
- **How sure each source URL is.** The manifest's `url_confidence` column says:
  - `evidenced`: the URL comes from the download command itself.
  - `re-verified`: the page was re-fetched on 29-09-2026 and its title and text matched the saved copy.
  - `matched`: the file was paired with a URL cited in the research.

## Licence and disclaimer

The documents belong to their publishers. They are reproduced unchanged for research and reference under the open-data and public-document terms noted per file, and each one's original URL is in the manifest. OpenCity is a student project, not affiliated with any government body. If you are a publisher and want a file removed, open an issue.

## Adding a document

1. Save it under the matching category folder as `<publisher>-<subject>-<period>.<ext>`.
2. Add a row to `manifest.csv`, including its sha256 (`sha256sum <file>`).
3. Add a line to the folder README.
