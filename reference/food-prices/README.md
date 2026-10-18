# Reference documents: Food prices and food security

Local copies of the source documents behind [docs/research/03-food-prices.md](../../docs/research/03-food-prices.md).
Each file was downloaded during the research (24-28 Sep 2026) and is unchanged since. Checksums are in [../manifest.csv](../manifest.csv).

8 item(s), 3.4 MB.

| File | What it is | Publisher | City | Period | Source | Size |
|---|---|---|---|---|---|---|
| [gujarat-doamrf-apmc-information-2026-09-27.html](gujarat-doamrf-apmc-information-2026-09-27.html) | List of APMCs in Gujarat with address, category, commodities and secretary contact details | Director of Agricultural Marketing & Rural Finance, Government of Gujarat | Gujarat | snapshot 2026-09-27 | [source](https://agri.gujarat.gov.in/Home/doamrf/APMCInformation) (matched) | 145.5 KB |
| [gujarat-fcscad-pds-social-audit-surat-zones-2026-09-27.html](gujarat-fcscad-pds-social-audit-surat-zones-2026-09-27.html) | iPDS Social Audit page for Surat district: taluka and city PDS zone codes (901-910) | Food, Civil Supplies & Consumer Affairs Department, Government of Gujarat (iPDS) | Surat | snapshot 2026-09-27 | [source](https://ipds.gujarat.gov.in/PDSSocialAudit/) (matched) | 12.2 KB |
| [india-agmarknet-daily-2026-08-28-to-2026-09-26/](india-agmarknet-daily-2026-08-28-to-2026-09-26/) | Daily market-wise commodity arrivals and prices, Surat and Ahmedabad district APMCs (60 daily JSON responses + market-ids.json) | Directorate of Marketing & Inspection (Agmarknet), Government of India | Both | 2026-08-28 to 2026-09-26 | [source](https://api.agmarknet.gov.in/v1/prices-and-arrivals/market-report/daily) | 786.5 KB |
| [india-agmarknet-market-district-state-2026-09-27.json](india-agmarknet-market-district-state-2026-09-27.json) | Agmarknet market-to-district-to-state mapping (all APMC markets) | Directorate of Marketing & Inspection, Ministry of Agriculture & Farmers Welfare (Agmarknet) | India | snapshot 2026-09-27 | [source](https://api.agmarknet.gov.in/v1/market-district-state) | 559.6 KB |
| [india-agmarknet-market-master-with-category-2026-09-27.json](india-agmarknet-market-master-with-category-2026-09-27.json) | Agmarknet market master with address and principal/sub-yard category (all states) | Directorate of Marketing & Inspection, Ministry of Agriculture & Farmers Welfare (Agmarknet) | India | snapshot 2026-09-27 | [source](https://api.agmarknet.gov.in/v1/dashboard-market-filter) | 1.3 MB |
| [india-doca-price-reporting-centres-2026-09-27.html](india-doca-price-reporting-centres-2026-09-27.html) | List of price reporting centres (zone-wise), incl. Ahmedabad and Surat | Price Monitoring Division, Department of Consumer Affairs, Government of India | India | snapshot 2026-09-27 | [source](https://fcainfoweb.nic.in/Report_Centre.aspx) | 235.8 KB |
| [india-impds-gujarat-district-portability-2026-09.html](india-impds-gujarat-district-portability-2026-09.html) | IMPDS Gujarat district-wise ONORC portability transactions table (September 2026) | Department of Food and Public Distribution, Government of India (IMPDS, NIC) | Gujarat | September 2026 (snapshot 2026-09-27) | [source](https://impds.nic.in/portal?sale_state=24&lang=en) | 264.1 KB |
| [india-labour-bureau-cpi-iw-centre-index-2026-09-28.html](india-labour-bureau-cpi-iw-centre-index-2026-09-28.html) | CPI-IW centre-wise general index page (index table incl. Ahmedabad and Surat centres, links to monthly PDFs up to Mar 2023) | Labour Bureau, Ministry of Labour and Employment, Government of India | India | snapshot 2026-09-28 | [source](https://labourbureau.gov.in/centre-wise-general-index) | 166.5 KB |

## What each document supports

- **gujarat-doamrf-apmc-information-2026-09-27.html**: Surat and Ahmedabad APMC details and secretary contacts for RTI filing on mandi price data _Licence: Government of Gujarat publication; reproduced for reference (lists APMC secretaries' official contacts)_
- **gujarat-fcscad-pds-social-audit-surat-zones-2026-09-27.html**: Surat PDS data must be summed across zones 901-910; FPS-level social audit drill-down exists _Licence: Government of Gujarat publication; reproduced for reference_
- **india-agmarknet-daily-2026-08-28-to-2026-09-26/**: Surat APMC reported prices on 23 of 30 days, Ahmedabad APMC on 21 of 30 (days with actual price rows) (food-prices dimension) _Licence: Government of India data (Agmarknet); reproduced for reference_
- **india-agmarknet-market-district-state-2026-09-27.json**: Agmarknet lists 24 markets under 'Surat' (incl. Tapi-district markets) and 17 under 'Ahmedabad' — food prices _Licence: Government of India data; reproduced for reference_
- **india-agmarknet-market-master-with-category-2026-09-27.json**: Agmarknet market master lists Surat/Ahmedabad markets with principal/sub-yard; Surat list includes Tapi markets — food prices _Licence: Government of India data; reproduced for reference_
- **india-doca-price-reporting-centres-2026-09-27.html**: Both Surat and Ahmedabad are DoCA Price Monitoring centres — food prices _Licence: Government of India publication; reproduced for reference_
- **india-impds-gujarat-district-portability-2026-09.html**: IMPDS lists AHMEDABAD CITY separately from rural AHMADABAD while SURAT is combined; Sep 2026 portability Surat 7,313 vs Ahmedabad City 5,139 _Licence: Government of India publication; reproduced for reference_
- **india-labour-bureau-cpi-iw-centre-index-2026-09-28.html**: Both Ahmedabad and Surat are CPI-IW centres; table period unclear and linked PDFs go only to Mar 2023 _Licence: Government of India publication; reproduced for reference_

## Linked only (not copied)

These documents were used in the research but are not reproduced here. They are third-party copyright, or they contain personal data about private individuals.

- [iPDS Gujarat social audit portal (lists fair-price-shop dealers by name)](https://ipds.gujarat.gov.in/PDSSocialAudit/): names private individuals

## Agmarknet daily series

See [india-agmarknet-daily-2026-08-28-to-2026-09-26/README.md](india-agmarknet-daily-2026-08-28-to-2026-09-26/README.md).
