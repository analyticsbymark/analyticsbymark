# AGENT_SUMMARY.md --- SpaceX Customer Concentration Tutorial Series

> This file is maintained by the `summarise_for_agents` agent.
> It provides a comprehensive, AI-discoverable summary of the customer_concentration tutorial series.

## 1. Curiosity Question

**How dependent is SpaceX's manifest on a handful of key customers, and how has that concentration changed?**

SpaceX itself is the primary mission owner for ~392 of ~637 completed launches (62%) -- almost entirely Starlink. The concentration trend is dramatic: SpaceX self-launches went from 0% before 2018 to 72% by the latest year. The Herfindahl-Hirschman Index (HHI) has risen from ~750 (competitive, 2018) to over 6,000 (highly concentrated). The question is whether SpaceX is a launch *provider* or a vertically integrated *operator* that happens to sell spare capacity.

## 2. Dataset

- **Source:** Launch Library 2 API (https://ll.thespacedevs.com), filtered to SpaceX (LSP ID 121)
- **Local cache:** `data/spacex_launches.csv` (relative to `spacex/` folder, shared with launch_cadence and launch_reliability)
- **Data loader:** `spacex/data/utils.py` -- `get_spacex_data() -> pd.DataFrame`
- **Rows:** ~637 completed launches (after filtering)
- **Date range:** 2006 to present (tutorials filter to completed launches only)
- **Filter applied in all tutorials:** `launch_status_abbrev in ("Success", "Failure", "Partial Failure")` -- excludes TBD/Go/planned launches
- **Key columns used:** `net`, `year`, `mission_owner_primary_name`, `mission_type`, `program_names`, `launch_name`, `rocket_name`, `launch_status_abbrev`
- **Derived columns:** `customer_category` assigned by rule-based classification (4 categories); `pct` for yearly percentage composition
- **Data quality note:** 118 of 637 completed launches (18.5%) have no recorded `mission_owner_primary_name`. These are transparently imputed from mission context (mission_type, program_names, launch_name).

## 3. Tutorial Progression

| File | Kirk Chapters | Topic | Key Output |
|---|---|---|---|
| `tutorial_001.py` | Ch 4 (Data), Ch 5 (Editorial) | Data loading, profiling, customer categorisation, HHI | 4 profiling charts + text summary |
| `tutorial_002.py` | Ch 7 (Representation) | Chart type selection -- try 4 candidates, pick winner | 4 candidate charts + selection rationale |
| `tutorial_003.py` | Ch 10 (Color) | Color design -- before/after for stacked bar and treemap | 4 before/after comparison charts |
| `tutorial_004.py` | Ch 9 (Annotation) | Annotation -- labels vs. editorial callouts for both charts | 3 charts (labels-only, annotated bar, annotated treemap) |
| `tutorial_final.py` | Ch 6 (Design), Ch 11 (Composition) | Final production-ready composition | 1 polished chart |
| `app.py` | Ch 8 (Interactivity) | Interactive Dash dashboard | Live web app at localhost:8050 |
| `app_screenshot.py` | -- | Screenshot capture utility | 2 screenshots (LinkedIn preview + full view) |

## 4. Key Design Decisions

### Chart Selection (tutorial_002)
- **Primary chart:** 100% stacked bar -- normalises each year to 100%, making concentration shift readable across different launch volumes; answers both "how concentrated?" and "how has it changed?"
- **Secondary chart (for color tutorial):** Treemap -- powerful spatial encoding of current-year composition; SpaceX rectangle dominating the space is visually impactful
- **Rejected:** Stacked area (absolute counts distort early-year composition -- 15 vs 170 launches); Pareto (powerful snapshot but no time dimension)

### Four Customer Categories
- **SpaceX (Internal):** SpaceX as mission owner -- overwhelmingly Starlink, plus test flights and Starship
- **US Government:** NASA, USSF, NRO, SDA, MDA
- **Intl Government:** ESA, CSA, JAXA, and other national agencies
- **Commercial:** Third-party commercial operators (SES, Eutelsat, Iridium, etc.)

### Null Owner Imputation (118 launches, 18.5%)
- Transparent rule-based classification using `mission_type`, `program_names`, and `launch_name`
- Starship/test flights → SpaceX (Internal); NROL/USSF prefixes → US Government; remaining → Commercial
- HHI computation treats each null owner as a distinct customer (conservative estimate)

### Color Palette
- **Type:** Qualitative warm/cool editorial contrast
- **Rationale:** SpaceX is the protagonist displacing a diverse customer base; the palette encodes this tension through temperature
- **Category colors:**
  - SpaceX (Internal): `#1A237E` (deep navy -- dominant, heavy, corporate)
  - US Government: `#E65100` (deep orange -- institutional, warm, distinct)
  - Intl Government: `#00897B` (teal -- international, cool-warm bridge)
  - Commercial: `#FFB300` (amber/gold -- commercial energy, diversity)
- **Colorblind safety:** Four hues differ in both hue AND lightness (15%, 45%, 38%, 72% luminance); deliberately avoids red-green pairing
- **Editorial effect:** As the navy band grows, it literally swallows the warm colors -- the reader feels concentration increasing before reading the axis

### Annotation Strategy
- **Title:** Editorial, not descriptive ("From Diversified to Dependent: SpaceX's Customer Concentration")
- **Three strategic callouts on stacked bar:**
  1. 50% concentration threshold -- dashed horizontal line with right-margin label
  2. Majority year callout (2020, 59%) -- when SpaceX first exceeded 50% share (years with <3 launches excluded)
  3. Latest SpaceX share (72%) -- current concentration level
- **Source attribution:** "Launch Library 2 API | thespacedevs.com" on all charts
- **All annotation values are dynamically computed from data** -- no hardcoded numbers

## 5. Key Code Patterns

### Data Loading (shared across all tutorials)
```python
from data.utils import get_spacex_data

df = get_spacex_data()
completed = df[df["launch_status_abbrev"].isin(["Success", "Failure", "Partial Failure"])]
```

### Customer Category Assignment
```python
_US_GOV_OWNERS = {
    "National Aeronautics and Space Administration",
    "National Reconnaissance Office",
    "United States Space Force",
    "Space Development Agency",
    "Missile Defense Agency",
}

_INTL_GOV_OWNERS = {
    "Canadian Space Agency",
    "European Space Agency",
    "Japan Aerospace Exploration Agency",
    "Italian Space Agency",
    "Indian Space Research Organization",
    "Bundeswehr",
    "European Organisation for the Exploitation of Meteorological Satellites",
}

def assign_customer_category(row):
    owner = row["mission_owner_primary_name"]
    if pd.notna(owner) and owner != "":
        if owner == "SpaceX":
            return "SpaceX (Internal)"
        if owner in _US_GOV_OWNERS:
            return "US Government"
        if owner in _INTL_GOV_OWNERS:
            return "Intl Government"
        return "Commercial"
    # Null owner imputation from mission context
    mission_type = str(row.get("mission_type", ""))
    program = str(row.get("program_names", ""))
    launch_name = str(row.get("launch_name", ""))
    if "Starship" in program or "Starship" in launch_name:
        return "SpaceX (Internal)"
    if mission_type == "Test Flight":
        return "SpaceX (Internal)"
    if "NROL" in launch_name or "USSF" in launch_name:
        return "US Government"
    if mission_type == "Government/Top Secret":
        return "US Government"
    return "Commercial"
```

### Yearly Percentage Composition
```python
yearly = df.groupby(["year", "customer_category"]).size().reset_index(name="launches")
yearly_totals = df.groupby("year").size()
valid_years = yearly_totals[yearly_totals >= 3].index  # Exclude years with 1-2 launches
yearly = yearly[yearly["year"].isin(valid_years)].copy()
totals = yearly.groupby("year")["launches"].transform("sum")
yearly["pct"] = yearly["launches"] / totals * 100
```

### HHI Concentration Index
```python
# Per-year HHI on individual mission owners (not broad categories)
for year, group in df.groupby("year"):
    owner_shares = group["owner_for_hhi"].value_counts() / len(group)
    hhi = int((owner_shares**2).sum() * 10000)
```

### Visualization Library
- **Plotly Express exclusively** -- no matplotlib in any tutorial
- `px.bar()` for stacked bars and Pareto, `px.area()` for stacked area, `px.treemap()` for treemap
- All charts saved as PNG via `fig.write_image(str(path), scale=2)`

### Interactive Dashboard (app.py)
- **Framework:** Dash (Plotly's web framework)
- **Layout:** Controls-above design -- stat cards, then controls row, then chart, then data table
- **Controls:** Year range slider, customer category checklist, annotation toggle
- **Stat cards:** Total Launches (fixed), SpaceX Share (dynamic), Unique Customers (dynamic), HHI Index (dynamic)
- **Data table:** `dash_table.DataTable` with sortable filtered launch records
- **Annotations:** Conditionally rendered only when toggled on AND anchor points fall within the filtered view

## 6. File Dependency Map

```
spacex/data/utils.py             <-- All tutorials import get_spacex_data()
spacex/data/spacex_launches.csv  <-- CSV cache (created by utils.py on first API call)

customer_concentration/
  tutorial_001.py              <-- Standalone (imports data/utils)
  tutorial_002.py              <-- Standalone (imports data/utils)
  tutorial_003.py              <-- Standalone (imports data/utils)
  tutorial_004.py              <-- Standalone (imports data/utils)
  tutorial_final.py            <-- Standalone (imports data/utils)
  app.py                       <-- Standalone (imports data/utils, runs Dash server)
  app_screenshot.py            <-- Depends on app.py (imports and starts it)
  tests/conftest.py            <-- Sets up sys.path, provides fixtures
  tests/test_customer_concentration.py  <-- importlib-based tests (avoids cross-curiosity collisions)
  images/                      <-- Output directory for all generated PNGs
  brief.md                     <-- Original curiosity brief
```

Each tutorial (001-004, final) is **independently runnable** -- there are no cross-tutorial imports. They share the same data loading pattern and constants but duplicate them intentionally for standalone execution.

## 7. Generated Image Inventory

| Tutorial | Image File | Description |
|---|---|---|
| 001 | `tutorial_001_image_01_top_customers.png` | Horizontal bar: top mission owners by launch count |
| 001 | `tutorial_001_image_02_self_launch_share.png` | Dual-axis: SpaceX self-launch count and percentage overlay by year |
| 001 | `tutorial_001_image_03_category_stacked_area.png` | Stacked area: 4 customer categories over time (absolute counts) |
| 001 | `tutorial_001_image_04_hhi_concentration.png` | Line chart: HHI concentration index over time (V-shape from ~750 to ~6,150) |
| 002 | `tutorial_002_image_01_candidate_stacked_area.png` | Candidate 1: stacked area (absolute counts, growth dominates) |
| 002 | `tutorial_002_image_02_candidate_pct_bar.png` | Candidate 2: 100% stacked bar (WINNER -- normalised shares) |
| 002 | `tutorial_002_image_03_candidate_treemap.png` | Candidate 3: treemap (powerful snapshot, no time dimension) |
| 002 | `tutorial_002_image_04_candidate_pareto.png` | Candidate 4: Pareto chart (cumulative customer share) |
| 003 | `tutorial_003_image_01_pct_bar_before.png` | BEFORE: 100% stacked bar with default Plotly colors |
| 003 | `tutorial_003_image_02_pct_bar_after.png` | AFTER: 100% stacked bar with warm/cool editorial palette |
| 003 | `tutorial_003_image_03_treemap_before.png` | BEFORE: treemap with default Plotly colors |
| 003 | `tutorial_003_image_04_treemap_after.png` | AFTER: treemap with warm/cool editorial palette |
| 004 | `tutorial_004_image_01_pct_bar_labels_only.png` | Labels only: stacked bar with axis labels and legend, no editorial annotations |
| 004 | `tutorial_004_image_02_pct_bar_annotated.png` | Fully annotated: 50% threshold, majority year callout, latest share callout |
| 004 | `tutorial_004_image_03_treemap_annotated.png` | Annotated treemap: editorial title, source attribution, percentage labels |
| final | `tutorial_final_image_01_concentration_bar.png` | Production 100% stacked bar (all best decisions combined) |
| app | `app_image_01_linkedin_preview.png` | Dashboard screenshot: stat cards + controls + chart (1200px wide) |
| app | `app_image_02_full_view.png` | Dashboard screenshot: full page with data table |

## 8. Testing

- **Test location:** `tests/test_customer_concentration.py` with `tests/conftest.py`
- **Run command:** `pytest tests/` from the `customer_concentration/` directory
- **Cross-curiosity safe:** Uses `importlib.util` for tutorial imports to avoid module name collisions when running `pytest projects/dev/docs_src/space_dev/spacex/` from repo root
- **Test types:**
  - `test_data_loads` -- verifies `get_spacex_data()` returns non-empty DataFrame with expected columns
  - `test_data_filter_completed_launches` -- verifies completed-launches filter returns expected statuses
  - `test_customer_category_assignment` -- verifies 4 valid categories, no nulls, SpaceX always present
  - `test_yearly_pct_sums_to_100` -- verifies yearly percentage composition sums to ~100 per year
  - `test_tutorial_00X_runs` -- executes each tutorial as a subprocess, asserts zero exit code
  - `test_tutorial_final_runs` -- executes final composition, asserts zero exit code
  - `test_app_layout` -- imports `app.py` and verifies Dash layout is valid (no server start)
  - `test_images_generated` -- checks all 16 expected PNG files exist and are non-empty
- **Fixtures:** `curiosity_dir` (customer_concentration path), `images_dir` (images path), `data_dir` (data path)
- **Total tests:** 11

## 9. Domain Transfer (Insurance Context)

The tutorials explicitly map SpaceX patterns to insurance analytics throughout:

| SpaceX Pattern | Insurance Equivalent | Tutorial |
|---|---|---|
| Customer category composition over time | Line-of-business or client-tier composition | 001, 002, final |
| 100% stacked bar (normalised shares) | Portfolio composition by peril, region, or client | 002, 003, 004, final |
| HHI concentration index | Solvency II concentration risk metrics | 001 |
| SpaceX self-launch dominance (72%) | Top-1 client share exceeding risk appetite thresholds | 001, 004, final |
| 50% concentration threshold annotation | Regulatory or internal risk limits (e.g., 25% single-name exposure) | 004, final |
| Null owner imputation (18.5% missing) | Missing policyholder data -- impute or exclude transparently | 001 |
| Treemap of current composition | Claims or premium breakdown by segment and sub-segment | 002, 003 |
| Pareto chart (cumulative customer share) | "Top 5 clients = X% of GWP" -- standard broker/underwriter metric | 002 |
| Warm/cool color encoding (diversity vs dominance) | Using color to encode risk appetite zones (green/amber/red) | 003 |

The target audience is insurance professionals learning data visualization. Kirk chapter references provide the pedagogical framework. Client concentration risk is a core regulatory concern (Solvency II, IFRS 17) -- every insurer monitors it. The HHI, Pareto, and stacked-bar patterns transfer directly to underwriting portfolio analysis.

## 10. Metadata

```yaml
curiosity: customer_concentration
dataset: spacex
data_source: space_dev
kirk_chapters: [4, 5, 6, 7, 8, 9, 10, 11]
difficulty: beginner
status: complete
visualization_library: plotly
dashboard_framework: dash
tutorials_count: 5
images_count: 18
has_interactive_app: true
has_tests: true
last_verified_working: 2026-02-20
created: 2026-02-20
```
