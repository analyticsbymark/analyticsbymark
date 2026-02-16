# Possible Briefs: SpaceX Launch Data

> Generated: 2026-02-15
> Dataset: spacex_launches.csv (763 rows, 37 columns, 2006-03-24 to 2031-03-31)

---

## Angle 1: Launch Cadence **[SELECTED]**


### Curiosity Question

How did SpaceX scale from 1 launch per year to 170, and what does the acceleration curve reveal?

### Why This Angle

The year-over-year growth is staggering — 1 launch in 2006, 18 in 2017, 98 in 2023, 170 in 2025. This isn't linear growth; it's an acceleration pattern with distinct phases (experimentation, proving, scaling). The monthly distribution also shows SpaceX shifting from seasonal clustering to near-continuous operations.

### Central Columns

`year`, `month`, `net`, `rocket_name`, `launch_status_abbrev`

### Domain Transfer

This time-series cadence analysis maps directly to claims frequency trending — replace launches with claims and rockets with lines of business. Spotting when volume shifts from linear to exponential growth is critical for reserve adequacy.

### Suggested Approach

- **tutorial_001 (Profiling):** Yearly and monthly launch counts, growth rates, seasonality patterns
- **tutorial_002 (Chart Selection):** Line chart for yearly trend, heatmap for monthly cadence, bar chart for comparisons
- **tutorial_003 (Color):** Sequential palette for time progression, categorical for rocket types if overlaid
- **tutorial_004 (Annotation):** Key milestones (first Falcon 9 Block 5, first 100+ year, monthly records)
- **tutorial_final (Composition):** Dashboard showing the acceleration story — from startup to industrial-scale launcher

### Metadata

```json
{
  "curiosity": "launch_cadence",
  "dataset": "spacex",
  "data_source": "space_dev",
  "kirk_chapters": [3, 5],
  "created": "2026-02-15",
  "status": "selected"
}
```

---

## Angle 2: Mission Portfolio Diversification

### Curiosity Question

How has SpaceX's mission mix evolved from a communications-dominated manifest to a multi-purpose space company?

### Why This Angle

Communications makes up 66% of all launches (503/763), but the remaining 34% spans 16 mission types — from human exploration to lunar missions to tourism. The interesting story is *when* each category appeared and how the portfolio concentration has changed over time. Early SpaceX was almost entirely comm-sat delivery; recent years show growing diversity.

### Central Columns

`mission_type`, `year`, `mission_owner_primary_name`, `program_names`, `rocket_name`

### Domain Transfer

This is portfolio concentration risk analysis — insurance companies track how concentrated their book is across lines of business. A Herfindahl-style concentration index applied to mission types mirrors how an underwriter would assess portfolio diversification.

### Suggested Approach

- **tutorial_001 (Profiling):** Mission type counts, first-appearance year per type, year-over-year type distribution
- **tutorial_002 (Chart Selection):** Stacked area chart for portfolio evolution, treemap for current composition, small multiples per type
- **tutorial_003 (Color):** Categorical palette for 16+ mission types — group minor types, use diverging for concentration index
- **tutorial_004 (Annotation):** First human exploration flight, first tourism, first lunar mission, Starlink dominance inflection
- **tutorial_final (Composition):** Portfolio evolution narrative — from single-purpose to diversified operator

### Metadata

```json
{
  "curiosity": "mission_portfolio",
  "dataset": "spacex",
  "data_source": "space_dev",
  "kirk_chapters": [3, 5],
  "created": "2026-02-15",
  "status": "proposed"
}
```

---

## Angle 3: Rocket Evolution & Fleet Transition

### Curiosity Question

What does SpaceX's transition from Falcon 1 to Falcon 9 variants to Starship tell us about technology lifecycle management?

### Why This Angle

Five distinct rocket families with clear succession patterns: Falcon 1 (2006-2009), Falcon 9 v1.0/v1.1/Block 4/Full Thrust/Block 5, Falcon Heavy, Starship Prototype, and operational Starship (V1/V2/V3). Each variant's lifespan, overlap with its predecessor, and the speed of transition reveal how SpaceX manages technology obsolescence.

### Central Columns

`rocket_full_name`, `rocket_name`, `rocket_variant`, `rocket_family`, `year`, `net`, `launch_status_abbrev`

### Domain Transfer

This maps to fleet/asset lifecycle analysis in insurance — how an insurer tracks technology generations in their book (e.g., older building codes vs. newer ones, legacy vs. modern vehicles). Understanding when one generation sunsets and another ramps up is critical for pricing.

### Suggested Approach

- **tutorial_001 (Profiling):** Variant timelines, overlap periods, launches per variant, success rates per variant
- **tutorial_002 (Chart Selection):** Timeline/Gantt chart for variant lifespans, stacked bar for variant share over time, bump chart for rank changes
- **tutorial_003 (Color):** Categorical palette grouped by family (Falcon warm tones, Starship cool tones), opacity for retired vs. active
- **tutorial_004 (Annotation):** Final flight of each variant, first flight of successors, variant overlap windows
- **tutorial_final (Composition):** Technology succession story — how rapid iteration drives reliability

### Metadata

```json
{
  "curiosity": "rocket_evolution",
  "dataset": "spacex",
  "data_source": "space_dev",
  "kirk_chapters": [3, 5],
  "created": "2026-02-15",
  "status": "proposed"
}
```

---

## Angle 4: Customer Base & Operator Dependency

### Curiosity Question

How dependent is SpaceX's manifest on a handful of key customers, and how has that concentration changed?

### Why This Angle

SpaceX itself is the primary mission owner for 401 of 763 launches (53% — almost entirely Starlink), NASA accounts for 49, and the US military (SDA + USSF + NRO) for 63. The remaining ~250 launches are spread across dozens of commercial and international operators. The question is whether SpaceX is becoming more or less reliant on its own Starlink program vs. third-party customers.

### Central Columns

`mission_owner_primary_name`, `mission_owner_all_names`, `program_names`, `year`, `mission_type`

### Domain Transfer

This is client concentration risk — every insurer and broker tracks how much of their revenue or exposure comes from their top 5 or top 10 accounts. Regulatory frameworks (e.g., Solvency II) explicitly require monitoring concentration risk.

### Suggested Approach

- **tutorial_001 (Profiling):** Customer counts, top-N share over time, Starlink vs. non-Starlink split, government vs. commercial
- **tutorial_002 (Chart Selection):** Donut/pie for current split, stacked area for concentration over time, Pareto chart for customer ranking
- **tutorial_003 (Color):** Highlight SpaceX/Starlink in brand colour, government in distinct group, commercial in gradient
- **tutorial_004 (Annotation):** Year SpaceX became its own largest customer, NASA relationship milestones, military contract wins
- **tutorial_final (Composition):** Concentration risk narrative — is SpaceX a launch provider or a vertically integrated operator?

### Metadata

```json
{
  "curiosity": "customer_concentration",
  "dataset": "spacex",
  "data_source": "space_dev",
  "kirk_chapters": [3, 5],
  "created": "2026-02-15",
  "status": "proposed"
}
```

---

## Angle 5: Launch Reliability & Failure Analysis

### Curiosity Question

What does SpaceX's failure timeline reveal about how rapidly a launch provider builds — and sustains — operational reliability?

### Why This Angle

622 successes vs. 11 failures and 4 partial failures gives an overall 97.6% success rate. But the story is in the *timeline* — early failures clustered in 2006-2016, while the recent record is near-perfect. Tracking cumulative success rate over time shows a classic reliability growth curve. Which rocket variants failed? At which launch sites? How long between failures?

### Central Columns

`launch_status`, `launch_status_abbrev`, `net`, `year`, `rocket_full_name`, `launchpad_name`, `mission_name`

### Domain Transfer

This is loss experience trending — insurers build credibility into their loss history the same way: early-period volatility stabilizes as exposure volume grows. The "mean time between failures" concept maps directly to loss frequency analysis.

### Suggested Approach

- **tutorial_001 (Profiling):** Failure count by year, cumulative success rate, time between failures, failure by variant/pad
- **tutorial_002 (Chart Selection):** Cumulative success rate line, scatter plot of failures on timeline, bar chart of failures per variant
- **tutorial_003 (Color):** Red/green diverging for fail/success, sequential for cumulative rate, muted tones for context launches
- **tutorial_004 (Annotation):** Each failure event with mission name, CRS-7 and AMOS-6 as pivotal moments, longest streak without failure
- **tutorial_final (Composition):** Reliability growth narrative — how volume and iteration build trust

### Metadata

```json
{
  "curiosity": "launch_reliability",
  "dataset": "spacex",
  "data_source": "space_dev",
  "kirk_chapters": [3, 5],
  "created": "2026-02-15",
  "status": "proposed"
}
```
