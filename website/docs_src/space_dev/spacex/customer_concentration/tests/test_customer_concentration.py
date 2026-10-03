"""Smoke and integration tests for the customer_concentration tutorial series.

Run with: pytest tests/ from the customer_concentration/ folder.
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

CURIOSITY_DIR = Path(__file__).resolve().parent.parent


def _run_tutorial(script_name: str, curiosity_dir: Path) -> subprocess.CompletedProcess:
    """Run a tutorial script as a subprocess and return the result."""
    script = curiosity_dir / script_name
    return subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(curiosity_dir),
    )


def _import_tutorial(module_name: str):
    """Import a tutorial module by explicit path to avoid cross-curiosity collisions."""
    spec = importlib.util.spec_from_file_location(
        f"customer_concentration.{module_name}",
        CURIOSITY_DIR / f"{module_name}.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Test 1: Data loading
# ---------------------------------------------------------------------------
def test_data_loads():
    """Verify data utility returns a non-empty DataFrame with expected columns."""
    from data.utils import get_spacex_data

    df = get_spacex_data()
    assert len(df) > 0, "DataFrame should not be empty"
    for col in ["net", "year", "month", "rocket_name", "launch_status_abbrev"]:
        assert col in df.columns, f"Missing expected column: {col}"


# ---------------------------------------------------------------------------
# Test 2: Completed launch filtering
# ---------------------------------------------------------------------------
def test_data_filter_completed_launches():
    """Verify load_and_filter returns only completed launches."""
    mod = _import_tutorial("tutorial_001")

    df = mod.load_and_filter()
    assert len(df) > 0, "Filtered DataFrame should not be empty"
    valid_statuses = {"Success", "Failure", "Partial Failure"}
    actual_statuses = set(df["launch_status_abbrev"].unique())
    assert actual_statuses.issubset(valid_statuses), (
        f"Unexpected statuses after filtering: {actual_statuses - valid_statuses}"
    )


# ---------------------------------------------------------------------------
# Test 3: Customer category assignment
# ---------------------------------------------------------------------------
def test_customer_category_assignment():
    """Verify assign_customer_category produces exactly 4 valid categories."""
    mod = _import_tutorial("tutorial_001")

    df = mod.load_and_filter()
    df["customer_category"] = df.apply(mod.assign_customer_category, axis=1)

    valid_categories = {"SpaceX (Internal)", "US Government", "Intl Government", "Commercial"}
    actual_categories = set(df["customer_category"].unique())
    assert actual_categories.issubset(valid_categories), (
        f"Unexpected categories: {actual_categories - valid_categories}"
    )
    # SpaceX should be present (they always have internal launches)
    assert "SpaceX (Internal)" in actual_categories, "SpaceX (Internal) category missing"
    # Every row should have a category assigned
    assert df["customer_category"].notna().all(), "Some rows have null categories"


# ---------------------------------------------------------------------------
# Test 4: Yearly percentage sums to ~100
# ---------------------------------------------------------------------------
def test_yearly_pct_sums_to_100():
    """Verify that percentage composition sums to ~100 per year."""
    mod = _import_tutorial("tutorial_003")

    df = mod.load_and_filter()
    yearly_pct = mod.prepare_yearly_pct(df)

    year_sums = yearly_pct.groupby("year")["pct"].sum()
    for year, total in year_sums.items():
        assert abs(total - 100.0) < 0.1, (
            f"Year {year} pct sums to {total:.1f}, expected ~100"
        )


# ---------------------------------------------------------------------------
# Test 5-9: Tutorial execution (subprocess)
# ---------------------------------------------------------------------------
def test_tutorial_001_runs(curiosity_dir: Path):
    """Execute tutorial_001.py and assert no exceptions."""
    result = _run_tutorial("tutorial_001.py", curiosity_dir)
    assert result.returncode == 0, f"tutorial_001 failed:\n{result.stderr}"


def test_tutorial_002_runs(curiosity_dir: Path):
    """Execute tutorial_002.py and assert no exceptions."""
    result = _run_tutorial("tutorial_002.py", curiosity_dir)
    assert result.returncode == 0, f"tutorial_002 failed:\n{result.stderr}"


def test_tutorial_003_runs(curiosity_dir: Path):
    """Execute tutorial_003.py and assert no exceptions."""
    result = _run_tutorial("tutorial_003.py", curiosity_dir)
    assert result.returncode == 0, f"tutorial_003 failed:\n{result.stderr}"


def test_tutorial_004_runs(curiosity_dir: Path):
    """Execute tutorial_004.py and assert no exceptions."""
    result = _run_tutorial("tutorial_004.py", curiosity_dir)
    assert result.returncode == 0, f"tutorial_004 failed:\n{result.stderr}"


def test_tutorial_final_runs(curiosity_dir: Path):
    """Execute tutorial_final.py and assert no exceptions."""
    result = _run_tutorial("tutorial_final.py", curiosity_dir)
    assert result.returncode == 0, f"tutorial_final failed:\n{result.stderr}"


# ---------------------------------------------------------------------------
# Test 10: App layout validation
# ---------------------------------------------------------------------------
def test_app_layout():
    """Import app.py and verify Dash layout is valid without starting the server."""
    mod = _import_tutorial("app")

    assert mod.app.layout is not None, "Dash app layout should not be None"
    assert len(mod.app.layout.children) > 0, "Layout should have child components"


# ---------------------------------------------------------------------------
# Test 11: Image generation
# ---------------------------------------------------------------------------
def test_images_generated(images_dir: Path):
    """Verify expected image files exist after tutorials have run."""
    expected = [
        "tutorial_001_image_01_top_customers.png",
        "tutorial_001_image_02_self_launch_share.png",
        "tutorial_001_image_03_category_stacked_area.png",
        "tutorial_001_image_04_hhi_concentration.png",
        "tutorial_002_image_01_candidate_stacked_area.png",
        "tutorial_002_image_02_candidate_pct_bar.png",
        "tutorial_002_image_03_candidate_treemap.png",
        "tutorial_002_image_04_candidate_pareto.png",
        "tutorial_003_image_01_pct_bar_before.png",
        "tutorial_003_image_02_pct_bar_after.png",
        "tutorial_003_image_03_treemap_before.png",
        "tutorial_003_image_04_treemap_after.png",
        "tutorial_004_image_01_pct_bar_labels_only.png",
        "tutorial_004_image_02_pct_bar_annotated.png",
        "tutorial_004_image_03_treemap_annotated.png",
        "tutorial_final_image_01_concentration_bar.png",
    ]
    for filename in expected:
        img = images_dir / filename
        assert img.exists(), f"Missing image: {filename}"
        assert img.stat().st_size > 0, f"Image is empty: {filename}"
