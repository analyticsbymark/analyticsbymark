# SPACE_DEV_INDEX.md --- Space Dev Category Index (Tier 2)

> This file is maintained by the `summarise_for_agents` agent.
> It provides detailed descriptions, curiosity questions, and domain transfer guidance for the space_dev data source.
> Last updated: 2026-02-21

## Data Source: Launch Library 2 (LL2)

The Launch Library 2 API (https://ll.thespacedevs.com) provides comprehensive data on space launches worldwide -- historical and upcoming. Data includes launch timing, status, operators, missions, rockets, and launchpads.

## Datasets

### SpaceX (`spacex/`)

**Filter:** `lsp__id=121` (SpaceX as launch service provider)

**Why SpaceX?** High launch volume, public interest, clear patterns in cadence and mission types. Ideal for time-series visualization tutorials.

**Data utility:** `spacex/data/utils.py` -- `get_spacex_data() -> pd.DataFrame`

**Columns:** launch_name, net, launch_status, launch_status_abbrev, mission_name, mission_type, rocket_name, rocket_full_name, rocket_family, launchpad_name, launchpad_location_name, launchpad_country, year, month

**Cache:** `spacex/data/spacex_launches.csv` (auto-generated from API on first run)

#### Curiosities

| Curiosity | Question | Kirk Chapters | Status | Tutorials | Summary |
|---|---|---|---|---|---|
| launch_cadence | How did SpaceX scale its launch cadence so dramatically, and what does the acceleration curve reveal? | 4, 5, 6, 7, 8, 9, 10, 11 | complete | 5 + app | [AGENT_SUMMARY.md](spacex/launch_cadence/AGENT_SUMMARY.md) |
| launch_reliability | What does SpaceX's failure timeline reveal about how rapidly a launch provider builds -- and sustains -- operational reliability? | 4, 5, 6, 7, 8, 9, 10, 11 | complete | 5 + app | [AGENT_SUMMARY.md](spacex/launch_reliability/AGENT_SUMMARY.md) |
| customer_concentration | How dependent is SpaceX's manifest on a handful of key customers, and how has that concentration changed? | 4, 5, 6, 7, 8, 9, 10, 11 | complete | 5 + app | [AGENT_SUMMARY.md](spacex/customer_concentration/AGENT_SUMMARY.md) |

**launch_cadence highlights:**
- 5 tutorial scripts (001-004 + final) building progressively from data profiling to production composition
- Interactive Dash dashboard with year range slider, phase filter, and annotation toggle
- 19 generated chart images covering before/after comparisons, candidate evaluations, and final output
- Full test suite (`tests/test_launch_cadence.py`) verifiable via `pytest`
- Three acceleration phases: Startup (2006-2013), Growth (2014-2019), Hyperscale (2020+)
- Sequential single-hue blue palette, colorblind-safe, culturally neutral
- All annotation values dynamically computed from data (no hardcoded numbers)

**launch_reliability highlights:**
- 5 tutorial scripts (001-004 + final) building progressively from data profiling to production composition
- Interactive Dash dashboard with sidebar-right layout: rocket family filter, annotation toggle, year range slider, data table
- 16 generated chart images covering failure timeline, cumulative success rate, chart candidates, before/after color, labels vs. annotations
- Full test suite (`tests/test_launch_reliability.py`) verifiable via `pytest` -- 11 tests
- Three-act reliability story: Falcon 1 development (2006-2008), Falcon 9 growing pains (2012-2016), Starship iteration (2020-2025)
- Qualitative palette by rocket family: red (#C0392B), steel blue (#2980B9), amber (#D4A017) -- colorblind-safe
- Key insight: ~2,800-day Falcon 9 Block 5 failure-free streak annotated as shaded gap (annotating the absence of data)
- All annotation values dynamically computed from data (no hardcoded numbers)

**customer_concentration highlights:**
- 5 tutorial scripts (001-004 + final) building progressively from data profiling to production composition
- Interactive Dash dashboard with controls-above layout: year range slider, customer category checklist, annotation toggle, stat cards, data table
- 18 generated chart images covering customer profiling, chart candidates, before/after color, labels vs. annotations, and final output
- Full test suite (`tests/test_customer_concentration.py`) verifiable via `pytest` -- 11 tests (uses `importlib.util` for cross-curiosity safety)
- Four customer categories: SpaceX (Internal), US Government, Intl Government, Commercial
- Warm/cool qualitative palette: navy (#1A237E) for SpaceX dominance, orange (#E65100), teal (#00897B), amber (#FFB300) -- colorblind-safe
- Transparent null-owner imputation for 118 launches (18.5%) using mission context
- Key insight: SpaceX self-launches went from 0% (pre-2018) to 72% -- HHI rose from ~750 to ~6,150
- All annotation values dynamically computed from data (no hardcoded numbers)

#### Future Curiosities (not yet scaffolded)
- **mission_types** -- What types of missions does SpaceX fly, and how has the mix changed?

## Domain Transfer Guidance

These tutorials use SpaceX data to teach visualization principles that transfer directly to insurance contexts:

| SpaceX Concept | Insurance Equivalent | Relevant Curiosity |
|---|---|---|
| Launch cadence over time | Policy count or premium volume by month | launch_cadence |
| Three acceleration phases | Portfolio growth stages (startup, scaling, mature) | launch_cadence |
| Sporadic-to-continuous operations | Seasonal claims clustering vs. steady-state | launch_cadence |
| CAGR annotation | Compound growth rate in premium or claims | launch_cadence |
| Failure timeline scatter | Loss event timeline (claims over policy years) | launch_reliability |
| Cumulative success rate | Inverse cumulative loss frequency | launch_reliability |
| MTBF (time between failures) | Claim frequency per exposure unit | launch_reliability |
| Three lifecycle eras (don't blend) | Underwriting era segmentation | launch_reliability |
| Block 5 reliability gap (absence of data) | Claim-free periods in a portfolio | launch_reliability |
| Rocket family color encoding | Colour by class of business or underwriting era | launch_reliability |
| Customer category composition (100% stacked bar) | Portfolio composition by peril, region, or client tier | customer_concentration |
| HHI concentration index | Solvency II concentration risk metrics | customer_concentration |
| Top-1 customer share exceeding 50% | Top-1 client exceeding risk appetite thresholds | customer_concentration |
| Pareto chart (cumulative share) | "Top 5 clients = X% of GWP" -- standard broker metric | customer_concentration |
| Null owner imputation (18.5% missing) | Missing policyholder data -- impute or exclude transparently | customer_concentration |
| Treemap of customer composition | Claims or premium breakdown by segment and sub-segment | customer_concentration |
| Mission type breakdown | Class of business distribution | (future: mission_types) |
| Rocket reuse patterns | Renewal rates by segment | -- |
| Launchpad utilization | Branch or region performance | -- |

The techniques (time-series aggregation, categorical comparison, trend analysis, phase-based color encoding, editorial annotation) are identical -- only the domain labels change.

## Existing Infrastructure

The `database/` folder contains the original LL2 API client (`tutorial_001.py`) with:
- `LL2Client` -- paginated API fetcher
- `LL2Settings` -- configuration (base URL, endpoints, timeouts)
- SQLModel data models for launches, astronauts, agencies
- Helper functions for data extraction and transformation

The `spacex/data/utils.py` wraps this client to provide the clean `get_spacex_data()` interface used by all visualization tutorials. It implements a cache-first architecture: load from local CSV if available, otherwise fetch from the API and save.

## Visualization Stack

| Component | Library | Usage |
|---|---|---|
| Charts | Plotly Express | All static chart generation (bar, line, area, heatmap) |
| Dashboard | Dash | Interactive web application with callbacks |
| Screenshots | Selenium + Chrome | Headless browser capture of dashboard |
| Data | pandas | All data manipulation and aggregation |
| Testing | pytest | Subprocess execution tests + import tests |
