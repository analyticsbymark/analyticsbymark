# AGENT_SUMMARY.md --- SpaceX Launch Cadence Tutorial Series

> This file is maintained by the `summarise_for_agents` agent.
> It provides a comprehensive, AI-discoverable summary of the launch_cadence tutorial series.

## 1. Curiosity Question

**How did SpaceX scale its launch cadence so dramatically, and what does the acceleration curve reveal?**

The year-over-year growth is staggering: 1 launch in 2006, growing to 170+ in 2025. This is not linear growth -- it is an acceleration pattern with three distinct phases. The monthly distribution also shows SpaceX shifting from seasonal clustering to near-continuous operations.

## 2. Dataset

- **Source:** Launch Library 2 API (https://ll.thespacedevs.com), filtered to SpaceX (LSP ID 121)
- **Local cache:** `data/spacex_launches.csv` (relative to `spacex/` folder)
- **Data loader:** `spacex/data/utils.py` -- `get_spacex_data() -> pd.DataFrame`
- **Rows:** ~763 total launches (historical + future planned)
- **Date range:** 2006-03-24 to 2031-03-31 (tutorials filter to completed launches only)
- **Filter applied in all tutorials:** `launch_status_abbrev in ("Success", "Failure", "Partial Failure")` -- excludes TBD/Go/planned launches
- **Key columns used:** `net`, `year`, `month`, `rocket_name`, `launch_status_abbrev`, `launchpad_name`, `mission_type`
- **Derived columns:** `year` and `month` extracted from `net` datetime; `phase` assigned by year range

## 3. Tutorial Progression

| File | Kirk Chapters | Topic | Key Output |
|---|---|---|---|
| `tutorial_001.py` | Ch 4 (Data), Ch 5 (Editorial) | Data loading, profiling, initial observations | 4 profiling charts + text summary |
| `tutorial_002.py` | Ch 7 (Representation) | Chart type selection -- try 4 candidates, pick winner | 4 candidate charts + selection rationale |
| `tutorial_003.py` | Ch 10 (Color) | Color design -- before/after for both charts | 4 before/after comparison charts |
| `tutorial_004.py` | Ch 9 (Annotation) | Annotation -- labels vs. editorial callouts | 3 charts (labels-only, annotated bar, annotated heatmap) |
| `tutorial_final.py` | Ch 6 (Design), Ch 11 (Composition) | Final production-ready composition | 2 polished charts |
| `app.py` | Ch 8 (Interactivity) | Interactive Dash dashboard | Live web app at localhost:8050 |
| `app_screenshot.py` | -- | Screenshot capture utility | 2 screenshots (LinkedIn preview + full view) |

## 4. Key Design Decisions

### Chart Selection (tutorial_002)
- **Primary chart:** Vertical bar chart -- length encoding is most accurately perceived; dramatic height contrast between first and latest year delivers the acceleration story instantly
- **Secondary chart:** Year x month heatmap -- reveals the shift from sporadic (empty months) to continuous (every month active) operations
- **Rejected:** Cumulative area chart (answers "how many total?" not "how did the rate change?"); line chart (close second but bar's discrete clarity better suits the insurance audience)

### Three Acceleration Phases
- **Startup (2006-2013):** Single-digit launches, proving the vehicle works
- **Growth (2014-2019):** Steady climb from ~6 to ~21 launches per year
- **Hyperscale (2020+):** Exponential jump driven by Falcon 9 Block 5 reusability and Starlink deployment

### Color Palette
- **Type:** Sequential single-hue blue ramp (not diverging, not qualitative)
- **Rationale:** Data is ordered and one-directional; blue is culturally neutral in business contexts; single-hue ramp is inherently colorblind-safe (relies on lightness, not hue)
- **Phase colors:**
  - Startup: `#B0BEC5` (cool gray)
  - Growth: `#42A5F5` (medium blue)
  - Hyperscale: `#0D47A1` (deep blue)
- **Heatmap scale:** Custom 6-stop blue ramp from `#F5F5F5` (near-white for zero) to `#0D47A1` (darkest blue)
- **Consistency:** Both charts share the same blue family to reduce cognitive load

### Annotation Strategy
- **Title:** Editorial, not descriptive ("From X to Y: SpaceX's Launch Acceleration" not "SpaceX Launches per Year")
- **Three strategic callouts on bar chart:**
  1. 2020 inflection point with YoY percentage
  2. Hyperscale-era CAGR (compound annual growth rate) with dotted bracket
  3. Peak year count with multiple-of-first-year context
- **Heatmap:** Title frames the "sporadic to always-on" insight; side annotations mark sparse vs. dense eras
- **Source attribution:** "Launch Library 2 API | thespacedevs.com" on all charts
- **All annotation values are dynamically computed from data** -- no hardcoded numbers

## 5. Key Code Patterns

### Data Loading (shared across all tutorials)
```python
from data.utils import get_spacex_data

df = get_spacex_data()
completed = df[df["launch_status_abbrev"].isin(["Success", "Failure", "Partial Failure"])]
```

### Phase Assignment
```python
def assign_phase(year: int) -> str:
    if year <= 2013:
        return "Startup (2006-2013)"
    elif year <= 2019:
        return "Growth (2014-2019)"
    return "Hyperscale (2020+)"
```

### Yearly Aggregation
```python
yearly = df.groupby("year").size().reset_index(name="launches")
yearly["phase"] = yearly["year"].apply(assign_phase)
```

### CAGR Computation
```python
hyperscale_year = 2020
hs_data = yearly[yearly["year"] >= hyperscale_year]
peak_idx = hs_data["launches"].idxmax()
peak_year = int(hs_data.loc[peak_idx, "year"])
peak_count = int(hs_data.loc[peak_idx, "launches"])
hs_count = int(yearly.loc[yearly["year"] == hyperscale_year, "launches"].values[0])
n_years = peak_year - hyperscale_year
cagr_pct = round(((peak_count / hs_count) ** (1 / n_years) - 1) * 100)
```

### Visualization Library
- **Plotly Express exclusively** -- no matplotlib in any tutorial
- `px.bar()` for bar charts, `px.imshow()` for heatmaps, `px.line()` and `px.area()` for candidates
- All charts saved as PNG via `fig.write_image(str(path), scale=2)`

### Interactive Dashboard (app.py)
- **Framework:** Dash (Plotly's web framework)
- **Controls:** Year range slider, phase checklist, annotation toggle
- **Data table:** `dash_table.DataTable` with sortable filtered launch records
- **Annotations:** Conditionally rendered only when toggled on AND relevant data is in the filtered view
- **Layout:** Single-page, inline CSS, max-width 1200px

## 6. File Dependency Map

```
spacex/data/utils.py          <-- All tutorials import get_spacex_data()
spacex/data/spacex_launches.csv  <-- CSV cache (created by utils.py on first API call)

launch_cadence/
  tutorial_001.py              <-- Standalone (imports data/utils)
  tutorial_002.py              <-- Standalone (imports data/utils)
  tutorial_003.py              <-- Standalone (imports data/utils)
  tutorial_004.py              <-- Standalone (imports data/utils)
  tutorial_final.py            <-- Standalone (imports data/utils)
  app.py                       <-- Standalone (imports data/utils, runs Dash server)
  app_screenshot.py            <-- Depends on app.py (imports and starts it)
  tests/conftest.py            <-- Sets up sys.path, provides fixtures
  tests/test_tutorials.py      <-- Runs each tutorial as subprocess + import tests
  images/                      <-- Output directory for all generated PNGs
  brief.md                     <-- Original curiosity brief
```

Each tutorial (001-004, final) is **independently runnable** -- there are no cross-tutorial imports. They share the same data loading pattern and constants but duplicate them intentionally for standalone execution.

## 7. Generated Image Inventory

| Tutorial | Image File | Description |
|---|---|---|
| 001 | `tutorial_001_image_01_yearly_cadence.png` | Bar chart: launches per year (default styling) |
| 001 | `tutorial_001_image_02_monthly_cadence.png` | Heatmap: year x month launch density |
| 001 | `tutorial_001_image_03_mission_types.png` | Horizontal bar: mission type distribution |
| 001 | `tutorial_001_image_04_rocket_evolution.png` | Stacked bar: rocket variant usage per year |
| 002 | `tutorial_002_image_01_candidate_bar.png` | Candidate 1: vertical bar chart |
| 002 | `tutorial_002_image_02_candidate_line.png` | Candidate 2: line chart with markers |
| 002 | `tutorial_002_image_03_candidate_area.png` | Candidate 3: cumulative area chart |
| 002 | `tutorial_002_image_04_candidate_heatmap.png` | Candidate 4: year x month heatmap |
| 003 | `tutorial_003_image_01_bar_before.png` | Bar chart: default Plotly colors (before) |
| 003 | `tutorial_003_image_02_bar_after.png` | Bar chart: phase-based blue ramp (after) |
| 003 | `tutorial_003_image_03_heatmap_before.png` | Heatmap: default Plotly scale (before) |
| 003 | `tutorial_003_image_04_heatmap_after.png` | Heatmap: sequential blue scale (after) |
| 004 | `tutorial_004_image_01_bar_labels_only.png` | Bar chart: data labels only, no annotations |
| 004 | `tutorial_004_image_02_bar_annotated.png` | Bar chart: editorial annotations + CAGR bracket |
| 004 | `tutorial_004_image_03_heatmap_annotated.png` | Heatmap: title framing + era bracket annotations |
| final | `tutorial_final_image_01_bar_cadence.png` | Production bar chart (all best decisions combined) |
| final | `tutorial_final_image_02_heatmap_density.png` | Production heatmap (all best decisions combined) |
| app | `app_image_01_linkedin_preview.png` | Dashboard screenshot: 1200px wide, LinkedIn optimised |
| app | `app_image_02_full_view.png` | Dashboard screenshot: full page with data table |

## 8. Testing

- **Test location:** `tests/test_tutorials.py` with `tests/conftest.py`
- **Run command:** `pytest tests/` from the `launch_cadence/` directory
- **Test types:**
  - `test_data_loads` -- verifies `get_spacex_data()` returns non-empty DataFrame with expected columns
  - `test_tutorial_00X_runs` -- executes each tutorial as a subprocess, asserts zero exit code
  - `test_tutorial_final_runs` -- executes final composition, asserts zero exit code
  - `test_app_layout` -- imports `app.py` and verifies Dash layout is valid (no server start)
  - `test_images_generated` -- checks all 17 expected PNG files exist and are non-empty
- **Fixtures:** `curiosity_dir` (launch_cadence path), `images_dir` (images path), `data_dir` (data path)
- **CI integration:** Tests run as part of `.github/workflows/build.yml`

## 9. Domain Transfer (Insurance Context)

The tutorials explicitly map SpaceX patterns to insurance analytics throughout:

| SpaceX Pattern | Insurance Equivalent | Tutorial |
|---|---|---|
| Launch cadence over time | Claims frequency trending / policy volume by month | 001, 002, final |
| Three acceleration phases | Portfolio growth stages (startup, scaling, mature) | 003, 004, final |
| Sporadic-to-continuous operations (heatmap) | Seasonal claims clustering vs. steady-state | 001, 002, final |
| CAGR annotation | Compound growth rate in premium or claims volume | 004, final |
| Mission type concentration (Starlink dominance) | Line-of-business concentration risk | 001 |
| Rocket evolution (Falcon 1 to F9 Block 5) | Product lifecycle transitions | 001 |
| YoY percentage change | Year-over-year loss ratio movement | 004, final |

The target audience is insurance professionals learning data visualization. Kirk chapter references provide the pedagogical framework. The techniques (time-series aggregation, categorical comparison, phase-based color encoding, editorial annotation) transfer directly -- only the domain labels change.

## 10. Metadata

```yaml
curiosity: launch_cadence
dataset: spacex
data_source: space_dev
kirk_chapters: [4, 5, 6, 7, 8, 9, 10, 11]
difficulty: beginner
status: complete
visualization_library: plotly
dashboard_framework: dash
tutorials_count: 5
images_count: 19
has_interactive_app: true
has_tests: true
last_verified_working: 2026-02-18
created: 2026-02-15
```
