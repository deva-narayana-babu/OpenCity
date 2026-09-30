# Research: Surat vs Ahmedabad

The complete findings behind [../city-selection.md](../city-selection.md) and [../roadmap.md](../roadmap.md).
Researched 24-28 Sep 2026.

## How the research was done

- **Research:** each dimension was researched for both cities from live sources.
- **Verification:** an adversarial verifier re-checked the claims that decide the pick.
- **Synthesis:** a synthesis step weighted the scores and chose the city.
- **Codebase:** the upstream codebase was assessed from a local clone.
- **Caveat:** scores are judgement on a 0-10 ease-of-building scale, not measurements.

| File | Contents | Surat | Ahmedabad |
|---|---|---|---|
| [01-budget.md](01-budget.md) | Budget and public finance | 7.5 | 5.5 |
| [02-education.md](02-education.md) | Education | 5 | 7 |
| [03-food-prices.md](03-food-prices.md) | Food prices and food security | 6 | 7 |
| [04-health-environment.md](04-health-environment.md) | Health, sanitation and environment | 6.5 | 4.5 |
| [05-governance.md](05-governance.md) | Civic governance, open data, safety, courts, transport | 6 | 5.5 |
| [06-district-modules.md](06-district-modules.md) | Other district modules (census, dams, rainfall, power, housing, maps) | 7.5 | 5 |
| [07-rti.md](07-rti.md) | RTI ecosystem | 7.5 | 4.5 |
| [08-codebase-assessment.md](08-codebase-assessment.md) | How to add a district upstream, module reuse, services, licence, fork vs fresh | | |
| [09-verification.md](09-verification.md) | Every verifier check and the revised scores | | |
| [../city-selection.md](../city-selection.md) | Synthesis: weighted scorecard (6.6 vs 5.6), MVP sources, RTI facts, templates | | |
| [../roadmap.md](../roadmap.md) | Semester roadmap | | |

The scores in this table are after verification.

## Raw data

The `raw/` folder holds the same findings as structured JSON:
- one file per dimension;
- `codebase.json`;
- `verification.json`;
- `synthesis.json`;
- the roadmap as generated, including its "Changes from draft" log.
