# Suggested Changes — Post Agent Run Review

Review of agents 001-010 applied to the SpaceX launch cadence curiosity.
Generated 2026-02-17 after the first full pipeline run.

---

## Critical — CI Will Break

### 1. Missing imaging deps in requirements.txt
The `social` plugin needs `pillow` and `cairosvg`, which are in `pyproject.toml` but **not in `requirements.txt`** (what CI uses). The `mkdocs build --strict` step will fail.

**Fix:** Add to `requirements.txt`:
```
pillow>=12.1.1
cairosvg>=2.8.2
selenium>=4.40.0
```

### 2. Cairo system libraries missing from CI workflow
`cairosvg` requires `libcairo2-dev` at the OS level. Ubuntu runners may not have it.

**Fix:** Add to `.github/workflows/build.yml` before `pip install`:
```yaml
- name: Install Cairo system dependencies
  run: sudo apt-get update && sudo apt-get install -y libcairo2-dev libffi-dev
```

### 3. Tests will fail in CI — data file not committed
`spacex_launches.csv` is untracked. Without it, `get_spacex_data()` falls back to the API which requires credentials not configured in CI. Every tutorial test and `test_data_loads()` will fail.

**Options (pick one):**
- **A.** Commit `spacex_launches.csv` as a test fixture (simplest)
- **B.** Add a `conftest.py` skip marker: `pytest.mark.skipif(not CSV_PATH.exists(), reason="data not available")`
- **C.** Add a small sample CSV fixture for tests only

### 4. Cookie consent YAML indentation is broken
In `projects/dev/mkdocs.yml`, `title` and `description` are siblings of `consent:` instead of children. The consent dialog is likely broken or showing defaults.

**Current (broken):**
```yaml
    consent:
    title: Cookie consent
    description: >-
```

**Should be:**
```yaml
    consent:
      title: Cookie consent
      description: >-
```

---

## High — Code Quality

### 5. Hardcoded data values will go stale
The number "170" (2025 launch count), "29" (2020 bar height), "93% YoY", "42% CAGR", and annotation y-positions are hardcoded across **5 files**: tutorial_001, tutorial_004, tutorial_final, app.py, and the dashboard subtitle.

When the CSV is refreshed with 2026+ data, titles will say "170" while the chart shows a different number, annotations will point to wrong bars, and the CAGR bracket will be misaligned.

**Fix:** Compute these dynamically from the data:
```python
latest_year = yearly["year"].max()
latest_count = yearly.loc[yearly["year"] == latest_year, "launches"].values[0]
first_count = yearly.loc[yearly["year"] == yearly["year"].min(), "launches"].values[0]
growth_factor = latest_count / first_count

# For CAGR
hyperscale_start = yearly.loc[yearly["year"] == 2020, "launches"].values[0]
n_years = latest_year - 2020
cagr = (latest_count / hyperscale_start) ** (1 / n_years) - 1
```

**Affected files:**
- `tutorial_004.py` — annotations at lines 147, 199, 219, 229, 248
- `tutorial_final.py` — annotations at lines 93, 113, 121, 125, 139
- `app.py` — title at line 71, annotations at lines 219, 227, 237, 244

### 6. Duplicate code across tutorials
The same functions are copy-pasted across 4+ files:

| Function/Constant | Duplicated in |
|---|---|
| `load_and_filter()` | tutorial_001, 002, 003, 004 |
| `assign_phase()` | tutorial_003, 004, final, app |
| `PHASE_COLORS` | tutorial_003, 004, final, app |
| `HEATMAP_SCALE` | tutorial_003, 004, final |
| `prepare_yearly()` | tutorial_002, 003, 004 (with **different** behaviour) |
| `prepare_monthly_pivot()` | tutorial_002, 003, 004 |

**Fix:** Create `launch_cadence/shared.py` with the common functions and constants. Each tutorial imports from it. This also prevents drift — currently `prepare_yearly()` in tutorial_002 adds a `cumulative` column while tutorial_003's version adds `phase` instead. Same function name, different output.

**Note:** The agent specs say each tutorial should be "independently runnable". A shared module still allows this — the tutorials just import from a local `shared.py` instead of duplicating.

### 7. Duplicate `Path` import in tutorial_003
Lines 12 and 23 both have `from pathlib import Path`. Copy-paste error.

### 8. Unused imports across tutorials
`import plotly.graph_objects as go` is imported but never directly referenced in tutorial_001, tutorial_002, and tutorial_003. Only tutorial_004 and tutorial_final use it (via `fig.add_annotation`/`fig.add_shape` on a `px`-created figure, which doesn't require the `go` import either).

---

## Medium — Infrastructure

### 9. check_paths disabled on snippets
`pymdownx.snippets` has `check_paths: false` in `projects/dev/mkdocs.yml`. This was a workaround for a missing file (`docs_src/space_dev/modelling/tutorial_001.py` referenced in `creating_policies.md`).

**Fix:** Either create the missing snippet source file, or remove the broken snippet reference from `creating_policies.md`, then re-enable `check_paths: true`.

### 10. Copyright year is stale
Both `mkdocs.yml` files say `2024 - 2025`. Should be `2024 - 2026`.

### 11. Unused constant in utils.py
`_SPACEX_LSP_ID = 121` is defined but never referenced. Dead code.

### 12. Timezone inconsistency in utils.py
The API fetch path parses dates with timezone awareness, but the CSV cache read path uses `parse_dates` without `utc=True`. Cached data may be timezone-naive while fresh data is timezone-aware. This can cause subtle comparison bugs.

### 13. Test ordering fragility
`test_images_generated()` checks for 17 image files that only exist if the tutorial tests ran first. There is no pytest ordering mechanism to enforce this. If run in isolation, it will fail.

**Fix:** Either use `pytest-order` to enforce dependencies, or have the test generate images on-demand, or mark it with `@pytest.mark.skipif` when images don't exist.

---

## Low — Polish

### 14. Agent numbering offset is confusing
Agent 002 produces `tutorial_001.py`, Agent 003 produces `tutorial_002.py`, etc. The offset between agent number and tutorial number is a recurring source of confusion.

**Consider:** Either renumber the agents to match tutorial output (agent_001 → tutorial_001) or add a mapping table to the agent README.

### 15. Blog support agent — missing comparison images
The 009_blog_support agent spec calls for `images/comparison_*.png` (before/after composites) and `code_snippets/snippet_*.png` (syntax-highlighted code images). These were not generated — only `blog_outline.md` was created. The existing before/after images from tutorial_003 serve the same purpose, but the spec's output format wasn't followed.

**Fix:** Either update the agent spec to reference existing tutorial images instead of generating new ones, or create composite comparison images.

### 16. Social card templates — example pages should be cleaned up
The `docs/examples/` directory was created for testing social card templates. These pages are not in the `nav` config and generate build warnings. They should be removed before merging, or added to `.gitignore` if kept for reference.

### 17. App module-level data loading
`app.py` loads data at import time (line 33: `_raw = get_spacex_data()`). This means even `test_app_layout()` triggers a full data load just by importing the module. Consider lazy loading or a function-based initialisation.

### 18. app_screenshot.py fragile server wait
`time.sleep(2)` is used to wait for the Dash server to start. A retry loop with a health check on `http://127.0.0.1:8050` would be more robust.

### 19. Blog site has no social plugin
The blog `mkdocs.yml` does not include the `social` plugin. If social cards are desired for blog posts too, the same layout system could be extended there.

---

## Summary by Priority

| Priority | Count | Items |
|---|---|---|
| **Critical** | 4 | #1 requirements.txt, #2 Cairo deps, #3 CSV not committed, #4 consent YAML |
| **High** | 4 | #5 hardcoded values, #6 code duplication, #7 duplicate import, #8 unused imports |
| **Medium** | 5 | #9 check_paths, #10 copyright, #11 dead constant, #12 timezone, #13 test ordering |
| **Low** | 6 | #14 numbering, #15 comparison images, #16 example cleanup, #17 lazy load, #18 sleep, #19 blog social |

---

## What Went Well

- **Full pipeline executed end-to-end** — tutorials 001 through final, Dash app, tests, blog outline, LinkedIn ideas, and social cards all produced
- **19 chart images** generated across the tutorial progression — clear visual storytelling from raw data to polished composition
- **Interactive dashboard** with 3 controls, data table, and two screenshot variants (LinkedIn + full view)
- **Test suite** with 8 smoke tests integrated into CI
- **Social card system** with 5 branded templates working across all page types
- **Agent definitions** well-structured with clear dependency chains and quality checklists
- **No banned imports** used anywhere — Plotly-only, pathlib-only throughout
