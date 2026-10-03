"""Smoke and integration tests for the launch_cadence_with_skills tutorial series.

Run with: pytest tests/ from the launch_cadence_with_skills/ folder.

Includes a guard for the live `pymdownx.snippets` code references in
blog_outline.md: those embed code by LINE RANGE, so if a tutorial is edited and
the lines shift, the published snippet would silently show the wrong code. The
snippet tests fail the moment a referenced range no longer brackets the code it
is supposed to show, so the outline gets fixed before it ships.
"""

import re
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
        "tutorial_002_image_03_candidate_log_line.png",
        "tutorial_002_image_04_candidate_heatmap.png",
        "tutorial_003_image_01_bar_before.png",
        "tutorial_003_image_02_bar_after.png",
        "tutorial_003_image_03_line_after.png",
        "tutorial_003_image_04_log_line_after.png",
        "tutorial_003_image_05_heatmap_after.png",
        "tutorial_004_image_01_bar_labels_only.png",
        "tutorial_004_image_02_bar_annotated.png",
        "tutorial_final_image_01_launch_cadence.png",
    ]
    for filename in expected:
        img = images_dir / filename
        assert img.exists(), f"Missing image: {filename}"
        assert img.stat().st_size > 0, f"Image is empty: {filename}"


# ---------------------------------------------------------------------------
# Live snippet guards — blog_outline.md embeds code by line range, so a line
# shift in a tutorial would silently publish the wrong snippet. Each entry pins
# the exact (stripped) text that MUST sit on the first and last line of the
# referenced range, plus a marker that must appear inside it. If a tutorial is
# edited and the lines move, the boundary text no longer matches and the test
# fails — pointing straight at the outline range that needs updating.
#
# To re-baseline after an intentional edit: update the range in blog_outline.md,
# then update the matching (start, end, start_text, end_text) row below.
# ---------------------------------------------------------------------------
SNIPPETS = [
    # source file, start, end, first-line text, last-line text, marker-in-range
    ("tutorial_001.py", 62, 70,
     "def latest_complete_year(df: pd.DataFrame) -> int:",
     'return int(df["year"].max()) - 1',
     "Kirk Ch 5"),
    ("tutorial_002.py", 74, 98,
     "def candidate_bar(df: pd.DataFrame) -> None:",
     'save_chart(fig, "tutorial_002_image_01_candidate_bar.png")',
     "px.bar("),
    ("tutorial_003.py", 49, 70,
     "# --- The deliberate palettes (Kirk Ch 10), one per colour ROLE --------------",
     'SEQUENTIAL_SCALE = "Viridis"',
     "PHASE_COLORS"),
    ("tutorial_004.py", 203, 226,
     "# --- Hierarchy 2: DIRECT CALLOUT #1 — the inflection ---------------------",
     ")",
     "CAGR since"),
    ("tutorial_final.py", 72, 107,
     "fig = px.bar(",
     ")",
     "CAGR since"),
    ("app.py", 122, 159,
     "def update_chart(year_range, phases, y_scale):",
     "return fig",
     "YEARLY["),
]

SNIPPET_REF_RE = re.compile(
    r'--8<--\s+"[^"]*?/(?P<file>[\w.]+\.py):(?P<start>\d+):(?P<end>\d+)"'
)


@pytest.mark.parametrize(
    "src,start,end,start_text,end_text,marker",
    SNIPPETS,
    ids=[s[0] for s in SNIPPETS],
)
def test_snippet_range_anchors_to_code(
    curiosity_dir: Path, src, start, end, start_text, end_text, marker
):
    """The referenced line range still brackets the code it claims to show."""
    lines = (curiosity_dir / src).read_text(encoding="utf-8").splitlines()
    assert end <= len(lines), f"{src}: range end {end} past EOF ({len(lines)} lines)"

    got_start = lines[start - 1].strip()
    got_end = lines[end - 1].strip()
    assert got_start == start_text, (
        f"{src}:{start} drifted.\n  expected start: {start_text!r}\n  found:          {got_start!r}\n"
        f"  -> update the range in blog_outline.md and the SNIPPETS row in this test."
    )
    assert got_end == end_text, (
        f"{src}:{end} drifted.\n  expected end: {end_text!r}\n  found:        {got_end!r}\n"
        f"  -> update the range in blog_outline.md and the SNIPPETS row in this test."
    )
    body = "\n".join(lines[start - 1:end])
    assert marker in body, f"{src}:{start}:{end} no longer contains marker {marker!r}"


def test_blog_outline_snippet_refs_match_test(curiosity_dir: Path):
    """Every --8<-- range in blog_outline.md agrees with the pinned SNIPPETS table.

    Keeps the published outline and this test in lockstep: editing one range
    without the other fails here.
    """
    outline = curiosity_dir / "blog_outline.md"
    assert outline.exists(), "blog_outline.md missing — run /sk_blog_support"

    expected = {(s[0], s[1], s[2]) for s in SNIPPETS}
    found = {
        (m.group("file"), int(m.group("start")), int(m.group("end")))
        for m in SNIPPET_REF_RE.finditer(outline.read_text(encoding="utf-8"))
    }
    assert found, "no --8<-- snippet references found in blog_outline.md"

    unknown = found - expected
    assert not unknown, f"outline has snippet ranges not pinned in this test: {sorted(unknown)}"
    missing = expected - found
    assert not missing, f"pinned snippet ranges not referenced in outline: {sorted(missing)}"