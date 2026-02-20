"""Smoke and integration tests for the launch_reliability tutorial series.

Run with: pytest tests/ from the launch_reliability/ folder.
"""

import subprocess
import sys
from pathlib import Path

import pytest


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


# ---------------------------------------------------------------------------
# Test 1: Data loading and filtering
# ---------------------------------------------------------------------------
def test_data_loads():
    """Verify data utility returns a non-empty DataFrame with expected columns."""
    from data.utils import get_spacex_data

    df = get_spacex_data()
    assert len(df) > 0, "DataFrame should not be empty"
    for col in ["net", "year", "month", "rocket_name", "launch_status_abbrev"]:
        assert col in df.columns, f"Missing expected column: {col}"


def test_data_filter_completed_launches():
    """Verify load_and_filter returns only completed launches (Success/Failure/Partial Failure)."""
    from tutorial_001 import load_and_filter

    df = load_and_filter()
    assert len(df) > 0, "Filtered DataFrame should not be empty"
    valid_statuses = {"Success", "Failure", "Partial Failure"}
    actual_statuses = set(df["launch_status_abbrev"].unique())
    assert actual_statuses.issubset(valid_statuses), (
        f"Unexpected statuses after filtering: {actual_statuses - valid_statuses}"
    )
    # Data should be sorted chronologically
    assert df["net"].is_monotonic_increasing, "Data should be sorted by launch date"


# ---------------------------------------------------------------------------
# Test 2: Failure preparation and rocket family mapping
# ---------------------------------------------------------------------------
def test_prepare_failures_and_rocket_family_mapping():
    """Verify prepare_failures extracts only failures and assigns rocket families."""
    from tutorial_003 import load_and_filter, prepare_failures, ROCKET_FAMILY_MAP

    df = load_and_filter()
    failures = prepare_failures(df)

    assert len(failures) > 0, "There should be at least one failure event"
    # All rows should be failure or partial failure
    failure_statuses = {"Failure", "Partial Failure"}
    assert set(failures["launch_status_abbrev"].unique()).issubset(failure_statuses)
    # rocket_family_group column should exist after prepare_failures
    assert "rocket_family_group" in failures.columns
    # Every mapped rocket should resolve to a known family
    known_families = {"Falcon 1", "Falcon 9", "Starship"}
    mapped_families = set(failures["rocket_family_group"].unique())
    assert mapped_families.issubset(known_families), (
        f"Unexpected rocket families: {mapped_families - known_families}"
    )


# ---------------------------------------------------------------------------
# Test 3: Annotation insight computation
# ---------------------------------------------------------------------------
def test_annotation_insights_computed():
    """Verify compute_annotation_insights returns expected keys with valid values."""
    from tutorial_004 import load_and_filter, prepare_failures, compute_annotation_insights

    df = load_and_filter()
    failures = prepare_failures(df)
    insights = compute_annotation_insights(df, failures)

    expected_keys = [
        "total_launches",
        "total_failures",
        "gap_days",
        "gap_years",
        "gap_start",
        "gap_end",
        "gap_mid",
        "cluster_label",
        "cluster_mid_date",
        "f1_count",
        "f1_mid_date",
        "f1_date_range",
        "date_min",
        "date_max",
    ]
    for key in expected_keys:
        assert key in insights, f"Missing insight key: {key}"

    assert insights["total_launches"] > 0
    assert insights["total_failures"] > 0
    assert insights["gap_days"] > 0, "Falcon 9 Block 5 gap should be positive"
    assert insights["gap_years"] > 0
    assert insights["f1_count"] > 0, "There should be Falcon 1 failures"


# ---------------------------------------------------------------------------
# Test 4-8: Tutorial execution (subprocess)
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
# Test 9: App layout validation
# ---------------------------------------------------------------------------
def test_app_layout():
    """Import app.py and verify Dash layout is valid without starting the server."""
    from app import app

    assert app.layout is not None, "Dash app layout should not be None"
    assert len(app.layout.children) > 0, "Layout should have child components"


# ---------------------------------------------------------------------------
# Test 10: Image generation
# ---------------------------------------------------------------------------
def test_images_generated(images_dir: Path):
    """Verify expected image files exist after tutorials have run."""
    expected = [
        "tutorial_001_image_01_failure_timeline.png",
        "tutorial_001_image_02_cumulative_success_rate.png",
        "tutorial_001_image_03_failures_by_rocket.png",
        "tutorial_001_image_04_time_between_failures.png",
        "tutorial_001_image_05_yearly_outcomes.png",
        "tutorial_002_image_01_candidate_failure_timeline.png",
        "tutorial_002_image_02_candidate_cumulative_success.png",
        "tutorial_002_image_03_candidate_yearly_stacked.png",
        "tutorial_002_image_04_candidate_mtbf.png",
        "tutorial_003_image_01_scatter_before.png",
        "tutorial_003_image_02_scatter_after.png",
        "tutorial_004_image_01_labels_only.png",
        "tutorial_004_image_02_fully_annotated.png",
        "tutorial_final_image_01_failure_timeline.png",
    ]
    for filename in expected:
        img = images_dir / filename
        assert img.exists(), f"Missing image: {filename}"
        assert img.stat().st_size > 0, f"Image is empty: {filename}"
