# SPACE_DEV_INDEX.md — Space Dev Category Index (Tier 2)

> This file is maintained by the `summarise_for_agents` agent.
> It provides detailed descriptions, curiosity questions, and domain transfer guidance for the space_dev data source.

## Data Source: Launch Library 2 (LL2)

The Launch Library 2 API (https://ll.thespacedevs.com) provides comprehensive data on space launches worldwide — historical and upcoming. Data includes launch timing, status, operators, missions, rockets, and launchpads.

## Datasets

### SpaceX (`spacex/`)

**Filter:** `lsp__id=121` (SpaceX as launch service provider)

**Why SpaceX?** High launch volume, public interest, clear patterns in cadence and mission types. Ideal for time-series visualization tutorials.

**Data utility:** `spacex/data/utils.py` — `get_spacex_data() -> pd.DataFrame`

**Columns:** launch_name, net, launch_status, mission_name, mission_type, rocket_name, launchpad_name, year, month

#### Curiosities

| Curiosity | Question | Folder | Status |
|---|---|---|---|
| launch_cadence | How has SpaceX's launch frequency changed over time? | [spacex/launch_cadence/](spacex/launch_cadence/) | scaffold |

#### Future Curiosities (not yet scaffolded)
- **mission_types** — What types of missions does SpaceX fly, and how has the mix changed?
- **success_rates** — How has SpaceX's launch reliability evolved?

## Domain Transfer Guidance

These tutorials use SpaceX data to teach visualization principles that transfer directly to insurance contexts:

| SpaceX Concept | Insurance Equivalent |
|---|---|
| Launch cadence over time | Policy count or premium volume by month |
| Mission type breakdown | Class of business distribution |
| Success/failure rates | Claims frequency or loss ratios |
| Rocket reuse patterns | Renewal rates by segment |
| Launchpad utilization | Branch or region performance |

The techniques (time-series aggregation, categorical comparison, trend analysis) are identical — only the domain labels change.

## Existing Infrastructure

The `database/` folder contains the original LL2 API client (`tutorial_001.py`) with:
- `LL2Client` — paginated API fetcher
- `LL2Settings` — configuration (base URL, endpoints, timeouts)
- SQLModel data models for launches, astronauts, agencies
- Helper functions for data extraction and transformation

The `spacex/data/utils.py` wraps this client to provide the clean `get_spacex_data()` interface used by all visualization tutorials.
