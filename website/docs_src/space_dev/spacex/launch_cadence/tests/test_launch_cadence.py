"""Smoke and integration tests for the launch_cadence tutorial series.

Run with: pytest tests/ from the launch_cadence/ folder.
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


def test_data_loads():
    """Verify data utility returns a non-empty DataFrame with expected columns."""
    from data.utils import get_spacex_data

    df = get_spacex_data()
    assert len(df) > 0, "DataFrame should not be empty"
    for col in ["net", "year", "month", "rocket_name", "launch_status_abbrev"]:
        assert col in df.columns, f"Missing expected column: {col}"


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


def test_app_layout():
    """Import app.py and verify Dash layout is valid without starting the server."""
    from app import app

    assert app.layout is not None, "Dash app layout should not be None"
    assert len(app.layout.children) > 0, "Layout should have child components"


def test_images_generated(images_dir: Path):
    """Verify expected image files exist after tutorials have run."""
    expected = [
        "tutorial_001_image_01_yearly_cadence.png",
        "tutorial_001_image_02_monthly_cadence.png",
        "tutorial_001_image_03_mission_types.png",
        "tutorial_001_image_04_rocket_evolution.png",
        "tutorial_002_image_01_candidate_bar.png",
        "tutorial_002_image_02_candidate_line.png",
        "tutorial_002_image_03_candidate_area.png",
        "tutorial_002_image_04_candidate_heatmap.png",
        "tutorial_003_image_01_bar_before.png",
        "tutorial_003_image_02_bar_after.png",
        "tutorial_003_image_03_heatmap_before.png",
        "tutorial_003_image_04_heatmap_after.png",
        "tutorial_004_image_01_bar_labels_only.png",
        "tutorial_004_image_02_bar_annotated.png",
        "tutorial_004_image_03_heatmap_annotated.png",
        "tutorial_final_image_01_bar_cadence.png",
        "tutorial_final_image_02_heatmap_density.png",
    ]
    for filename in expected:
        img = images_dir / filename
        assert img.exists(), f"Missing image: {filename}"
        assert img.stat().st_size > 0, f"Image is empty: {filename}"
