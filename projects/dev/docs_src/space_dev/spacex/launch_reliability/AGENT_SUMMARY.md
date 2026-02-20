# AGENT_SUMMARY.md --- SpaceX Launch Reliability Tutorial Series

> This file is maintained by the `summarise_for_agents` agent.
> It provides a comprehensive, AI-discoverable summary of the launch_reliability tutorial series.

## 1. Curiosity Question

**What does SpaceX's failure timeline reveal about how rapidly a launch provider builds -- and sustains -- operational reliability?**

SpaceX's failure history is not a list of accidents but a three-act reliability growth story -- Falcon 1's development trials, Falcon 9's growing pains, and Starship's intentional iteration -- separated by an extraordinary ~2,800-day Falcon 9 Block 5 streak with zero failures. A single "96% success rate" flattens this narrative into a meaningless average.

## 2. Dataset

- **Source:** Launch Library 2 API (https://ll.thespacedevs.com), filtered to SpaceX (LSP ID 121)
- **Local cache:** `data/spacex_launches.csv` (relative to `spacex/` folder, shared with launch_cadence)
- **Data loader:** `spacex/data/utils.py` -- `get_spacex_data() -> pd.DataFrame`
- **Rows:** ~637 completed launches (after filtering)
- **Date range:** 2006 to present (tutorials filter to completed launches only)
- **Filter applied in all tutorials:** `launch_status_abbrev in ("Success", "Failure", "Partial Failure")` -- excludes TBD/Go/planned launches
- **Key columns used:** `net`, `launch_status_abbrev`, `mission_name`, `rocket_full_name`, `rocket_family`, `year`
- **Derived columns:** `rocket_family` mapped from `rocket_full_name` via `ROCKET_FAMILY_MAP`; `is_failure` boolean flag

## 3. Tutorial Progression

| File | Kirk Chapters | Topic | Key Output |
|---|---|---|---|
| `tutorial_001.py` | Ch 4 (Data), Ch 5 (Editorial) | Data loading, profiling, failure analysis | 5 profiling charts + text summary |
| `tutorial_002.py` | Ch 7 (Representation) | Chart type selection -- try 4 candidates, pick winner | 4 candidate charts + selection rationale |
| `tutorial_003.py` | Ch 10 (Color) | Color design -- before/after comparison | 2 before/after charts |
| `tutorial_004.py` | Ch 9 (Annotation) | Annotation -- labels vs. editorial callouts | 2 charts (labels-only, fully annotated) |
| `tutorial_final.py` | Ch 6 (Design), Ch 11 (Composition) | Final production-ready composition | 1 polished chart |
| `app.py` | Ch 8 (Interactivity) | Interactive Dash dashboard | Live web app at localhost:8050 |
| `app_screenshot.py` | -- | Screenshot capture utility | 2 screenshots (LinkedIn preview + full view) |

## 4. Key Design Decisions

### Chart Selection (tutorial_002)
- **Primary chart:** Failure timeline scatter -- position along a common time scale is the most accurately perceived visual channel (Cleveland & McGill, 1984); every event is individually legible, no aggregation or smoothing
- **Rejected:** Cumulative success rate line (answers "what's the average?" not "when did failures cluster"); yearly stacked bar (failure slivers vanish inside tall success columns at high cadence); MTBF bar (loses calendar context, can't see the timeline)

### Three-Act Reliability Story
- **Act 1 -- Falcon 1 Development (2006-2008):** 3 failures in first 3 flights, proving-ground era
- **Act 2 -- Falcon 9 Growing Pains (2012-2016):** CRS-7 and Amos-6 failures trigger Block 5 redesign
- **Act 3 -- Starship Intentional Iteration (2020-2025):** Rapid test-to-destruction cadence on a new vehicle
- **The Gap:** ~2,800 days of Falcon 9 Block 5 operations with zero failures (Sep 2016 to Jul 2024)

### Color Palette
- **Type:** Qualitative (categorical, not ordered)
- **Rationale:** Three rocket families represent three distinct lifecycle chapters; a sequential palette would imply an ordering that doesn't exist
- **Family colors:**
  - Falcon 1: `#C0392B` (muted red -- development-era volatility)
  - Falcon 9: `#2980B9` (steel blue -- operational maturity)
  - Starship: `#D4A017` (amber/gold -- new vehicle development)
- **Colorblind safety:** Three hues with distinct luminance levels (dark, medium, light) -- safe under deuteranopia

### Annotation Strategy
- **Title:** Editorial, not descriptive ("N Failures in M Launches: How SpaceX Built Reliability")
- **Three strategic callouts:**
  1. Falcon 1 development cluster -- 3 failures in first 3 flights (2006-2008)
  2. CRS-7 / Amos-6 pivot point -- failures that triggered Block 5 redesign
  3. Falcon 9 Block 5 reliability gap -- annotating the ABSENCE of dots (~2,800 days, shaded vrect)
- **Source attribution:** "Launch Library 2 API | thespacedevs.com" on all charts
- **All annotation values are dynamically computed from data** -- no hardcoded numbers

## 5. Key Code Patterns

### Data Loading (shared across all tutorials)
```python
from data.utils import get_spacex_data

df = get_spacex_data()
completed = df[df["launch_status_abbrev"].isin(["Success", "Failure", "Partial Failure"])]
```

### Failure Filtering and Rocket Family Mapping
```python
FAILURE_STATUSES = {"Failure", "Partial Failure"}
failures = completed[completed["launch_status_abbrev"].isin(FAILURE_STATUSES)].copy()

ROCKET_FAMILY_MAP = {
    "Falcon 1": "Falcon 1",
    "Falcon 9 v1.0": "Falcon 9",
    "Falcon 9 v1.1": "Falcon 9",
    "Falcon 9 Full Thrust": "Falcon 9",
    "Falcon 9 Block 5": "Falcon 9",
    "Starship Prototype": "Starship",
    "Starship V1": "Starship",
    "Starship V2": "Starship",
}
failures["rocket_family"] = failures["rocket_full_name"].map(ROCKET_FAMILY_MAP)
```

### Cumulative Success Rate (tutorial_001)
```python
completed["is_success"] = (completed["launch_status_abbrev"] == "Success").astype(int)
completed["cum_success_rate"] = completed["is_success"].expanding().mean() * 100
```

### Annotation Insights Computed from Data (tutorial_004)
```python
def compute_annotation_insights(df, failures):
    # Falcon 1 cluster
    f1 = failures[failures["rocket_family"] == "Falcon 1"]
    # CRS-7 / Amos-6 pivot
    amos6 = failures[failures["mission_name"] == "Amos-6"]
    # Block 5 gap: from Amos-6 to next Falcon 9 failure
    f9_failures = failures[failures["rocket_family"] == "Falcon 9"]
    gap_days = (gap_end - gap_start).days
    ...
```

### Visualization Library
- **Plotly Express exclusively** -- no matplotlib in any tutorial
- `px.strip()` and `px.scatter()` for failure timeline; `px.line()`, `px.bar()` for profiling
- All charts saved as PNG via `fig.write_image(str(path), scale=2)`

### Interactive Dashboard (app.py)
- **Framework:** Dash (Plotly's web framework)
- **Layout:** Sidebar-right design -- chart dominates left ~75%, controls + table stacked in right sidebar
- **Controls:** Rocket family checkbox filter, annotation toggle, year range slider
- **Data table:** `dash_table.DataTable` with sortable filtered launch records (max 15 rows)
- **Annotations:** Conditionally rendered only when toggled on AND anchor points fall within the filtered view
- **Global insights:** Computed once from unfiltered data to maintain annotation stability across filter states

## 6. File Dependency Map

```
spacex/data/utils.py             <-- All tutorials import get_spacex_data()
spacex/data/spacex_launches.csv  <-- CSV cache (created by utils.py on first API call)

launch_reliability/
  tutorial_001.py              <-- Standalone (imports data/utils)
  tutorial_002.py              <-- Standalone (imports data/utils)
  tutorial_003.py              <-- Standalone (imports data/utils)
  tutorial_004.py              <-- Standalone (imports data/utils)
  tutorial_final.py            <-- Standalone (imports data/utils)
  app.py                       <-- Standalone (imports data/utils, runs Dash server)
  app_screenshot.py            <-- Depends on app.py (imports and starts it)
  tests/conftest.py            <-- Sets up sys.path, provides fixtures
  tests/test_launch_reliability.py  <-- Runs each tutorial as subprocess + import tests
  images/                      <-- Output directory for all generated PNGs
  brief.md                     <-- Original curiosity brief
  blog_outline.md              <-- Blog support output (gitignored)
  linkedin_ideas.md            <-- LinkedIn repurposing output (gitignored)
```

Each tutorial (001-004, final) is **independently runnable** -- there are no cross-tutorial imports. They share the same data loading pattern and constants but duplicate them intentionally for standalone execution.

## 7. Generated Image Inventory

| Tutorial | Image File | Description |
|---|---|---|
| 001 | `tutorial_001_image_01_failure_timeline.png` | Strip plot of all failure/partial failure events on a timeline (raw, unstyled) |
| 001 | `tutorial_001_image_02_cumulative_success_rate.png` | Line chart of running success rate with failure events as red X markers |
| 001 | `tutorial_001_image_03_failures_by_rocket.png` | Horizontal bar chart of failure counts by rocket variant |
| 001 | `tutorial_001_image_04_time_between_failures.png` | Bar chart of days between consecutive failures (MTBF proxy), color-scaled green-to-red |
| 001 | `tutorial_001_image_05_yearly_outcomes.png` | Stacked bar chart of annual launch outcomes (Success/Failure/Partial Failure) |
| 002 | `tutorial_002_image_01_candidate_failure_timeline.png` | Candidate 1: failure timeline scatter (WINNER, unstyled) |
| 002 | `tutorial_002_image_02_candidate_cumulative_success.png` | Candidate 2: cumulative success rate line (SECONDARY) |
| 002 | `tutorial_002_image_03_candidate_yearly_stacked.png` | Candidate 3: yearly stacked bar (REJECTED -- failure slivers invisible) |
| 002 | `tutorial_002_image_04_candidate_mtbf.png` | Candidate 4: time-between-failures bar (REJECTED -- loses temporal context) |
| 003 | `tutorial_003_image_01_scatter_before.png` | BEFORE: failure timeline with default Plotly colors (color by outcome) |
| 003 | `tutorial_003_image_02_scatter_after.png` | AFTER: failure timeline with rocket family color encoding (three-act structure visible) |
| 004 | `tutorial_004_image_01_labels_only.png` | Labels only: every mission name labeled with staggered placement |
| 004 | `tutorial_004_image_02_fully_annotated.png` | Fully annotated: editorial title, 3 strategic callouts, shaded gap, source attribution |
| final | `tutorial_final_image_01_failure_timeline.png` | Final production-ready composition (the hero image) |
| app | `app_image_01_linkedin_preview.png` | Dashboard screenshot: sidebar-right layout, chart + controls |
| app | `app_image_02_full_view.png` | Dashboard screenshot: full page with chart + controls + data table |

## 8. Testing

- **Test location:** `tests/test_launch_reliability.py` with `tests/conftest.py`
- **Run command:** `pytest tests/` from the `launch_reliability/` directory
- **Test types:**
  - `test_data_loads` -- verifies `get_spacex_data()` returns non-empty DataFrame with expected columns
  - `test_completed_launches_filter` -- verifies completed-launches filter returns expected count and statuses
  - `test_failure_prep_and_rocket_family` -- verifies failure filtering and rocket family mapping
  - `test_annotation_insights` -- verifies `compute_annotation_insights()` returns expected keys and types
  - `test_tutorial_00X_runs` -- executes each tutorial as a subprocess, asserts zero exit code
  - `test_tutorial_final_runs` -- executes final composition, asserts zero exit code
  - `test_app_layout` -- imports `app.py` and verifies Dash layout is valid (no server start)
  - `test_images_generated` -- checks all 14 expected PNG files exist and are non-empty
- **Fixtures:** `curiosity_dir` (launch_reliability path), `images_dir` (images path), `data_dir` (data path)
- **Total tests:** 11

## 9. Domain Transfer (Insurance Context)

The tutorials explicitly map SpaceX patterns to insurance analytics throughout:

| SpaceX Pattern | Insurance Equivalent | Tutorial |
|---|---|---|
| Failure timeline scatter | Loss event timeline (claims over policy years) | 001, 002, final |
| Cumulative success rate | Inverse cumulative loss frequency | 001 |
| MTBF (time between failures) | Claim frequency per exposure unit | 001 |
| Three lifecycle eras | Underwriting era segmentation (don't blend across eras) | 003, 004, final |
| 96% success rate hides the story | Blended loss ratios across underwriting eras | 001, blog |
| Block 5 reliability gap | Years with zero claims -- informative, not ignorable | 004, final |
| Rocket family color encoding | Colour by class of business or underwriting era | 003 |
| Annotating absence of data | Highlighting claim-free periods in a portfolio | 004 |

The target audience is insurance professionals learning data visualization. Kirk chapter references provide the pedagogical framework. The reliability growth curve pattern appears in insurance loss frequency, manufacturing quality, and software deployment -- the tutorial teaches a universal pattern, not just a space story.

## 10. Metadata

```yaml
curiosity: launch_reliability
dataset: spacex
data_source: space_dev
kirk_chapters: [4, 5, 6, 7, 8, 9, 10, 11]
difficulty: beginner
status: complete
visualization_library: plotly
dashboard_framework: dash
tutorials_count: 5
images_count: 16
has_interactive_app: true
has_tests: true
last_verified_working: 2026-02-20
created: 2026-02-20
```
