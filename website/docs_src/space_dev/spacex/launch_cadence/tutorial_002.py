"""
What You'll Learn
=================
- How to iterate through chart types to find the best fit for a cadence story
- Kirk Chapter 7: Data Representation — choosing the right chart for data + message
- The process of selection IS the lesson: try, evaluate, decide
- Output: 4 chart candidates evaluated, 1 winner declared
"""

import sys
from pathlib import Path

# Ensure the parent directory is on the path so `from data.utils import ...` works
# when this script is run directly from the launch_cadence/ folder.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Standard imports
import pandas as pd
import plotly.express as px

# Local imports
from data.utils import get_spacex_data

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
IMAGES_DIR = Path(__file__).resolve().parent / "images"
IMAGES_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Data loading (reuse the same filter from tutorial_001)
# ---------------------------------------------------------------------------
def load_and_filter() -> pd.DataFrame:
    """Load SpaceX data and filter to completed launches only."""
    df = get_spacex_data()
    completed = df[df["launch_status_abbrev"].isin(["Success", "Failure", "Partial Failure"])]
    return completed


def prepare_yearly(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate to yearly launch counts — the core data for cadence analysis."""
    yearly = df.groupby("year").size().reset_index(name="launches")
    yearly["cumulative"] = yearly["launches"].cumsum()
    return yearly


def prepare_monthly_pivot(df: pd.DataFrame) -> pd.DataFrame:
    """Create year × month pivot for heatmap exploration."""
    pivot = df.pivot_table(
        index="year", columns="month", aggfunc="size", fill_value=0
    )
    for m in range(1, 13):
        if m not in pivot.columns:
            pivot[m] = 0
    return pivot[range(1, 13)]


# ---------------------------------------------------------------------------
# Candidate 1 — Vertical bar chart
# ---------------------------------------------------------------------------
def chart_candidate_bar(yearly: pd.DataFrame) -> None:
    """Vertical bar chart of launches per year.

    Kirk Ch 7: Bar charts encode quantity via length — one of the most
    accurately perceived visual channels. Each year gets its own discrete
    bar, making year-to-year comparison effortless.

    VERDICT: Strong candidate. The dramatic height difference between the
    first year (barely visible) and the latest year (towering) tells the
    acceleration story at a glance. However, it emphasises individual year
    totals more than the *shape* of the growth curve.
    """
    fig = px.bar(
        yearly,
        x="year",
        y="launches",
        title="Candidate 1: Bar Chart — Yearly Launch Counts",
        labels={"year": "Year", "launches": "Launches"},
    )
    fig.update_layout(xaxis=dict(dtick=1), width=1000, height=500)

    out = IMAGES_DIR / "tutorial_002_image_01_candidate_bar.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Candidate 2 — Line chart
# ---------------------------------------------------------------------------
def chart_candidate_line(yearly: pd.DataFrame) -> None:
    """Line chart of launches per year.

    Kirk Ch 7: Line charts imply continuity and are the natural choice for
    time-series data. The slope of the line encodes the *rate of change* —
    exactly what we need for an acceleration story.

    VERDICT: Strong candidate. The near-flat line through 2006-2016 followed
    by the steep upward curve from 2020 onward makes the phase transitions
    visually obvious. The line's slope IS the story. Weakness: individual
    year values are harder to read without data labels.
    """
    fig = px.line(
        yearly,
        x="year",
        y="launches",
        title="Candidate 2: Line Chart — Yearly Trend",
        labels={"year": "Year", "launches": "Launches"},
        markers=True,
    )
    fig.update_layout(xaxis=dict(dtick=1), width=1000, height=500)

    out = IMAGES_DIR / "tutorial_002_image_02_candidate_line.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Candidate 3 — Cumulative area chart
# ---------------------------------------------------------------------------
def chart_candidate_area(yearly: pd.DataFrame) -> None:
    """Cumulative area chart of total launches over time.

    Kirk Ch 7: Area charts emphasise volume and accumulation. A cumulative
    view answers a different question: "How many total launches has SpaceX
    completed by year X?" The steepening slope still shows acceleration,
    but the message shifts from cadence to scale.

    VERDICT: Interesting but off-target. The cumulative curve is always
    rising (you can't un-launch a rocket), so it flattens the drama of
    individual-year acceleration. It answers "how many in total?" rather
    than our curiosity question "how did the *rate* change?" — a subtle
    but important editorial distinction.
    """
    fig = px.area(
        yearly,
        x="year",
        y="cumulative",
        title="Candidate 3: Cumulative Area — Total Launches Over Time",
        labels={"year": "Year", "cumulative": "Cumulative Launches"},
    )
    fig.update_layout(xaxis=dict(dtick=1), width=1000, height=500)

    out = IMAGES_DIR / "tutorial_002_image_03_candidate_area.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Candidate 4 — Heatmap (year × month)
# ---------------------------------------------------------------------------
def chart_candidate_heatmap(pivot: pd.DataFrame) -> None:
    """Heatmap of launches by year and month.

    Kirk Ch 7: Heatmaps use colour intensity to encode quantity across two
    categorical axes. For cadence analysis, this reveals patterns that
    yearly aggregates hide: seasonality, operational consistency, and the
    transition from sporadic to continuous operations.

    VERDICT: Excellent supporting chart but not the lead. The heatmap is
    the best way to show *how* the cadence changed (from clustered months
    to uniform distribution), but it requires the reader to process a dense
    grid. It works as a second chart alongside a simpler primary visual.
    """
    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    fig = px.imshow(
        pivot.values,
        x=month_labels,
        y=[str(y) for y in pivot.index],
        title="Candidate 4: Heatmap — Monthly Launch Density",
        labels=dict(x="Month", y="Year", color="Launches"),
        aspect="auto",
    )
    fig.update_layout(width=900, height=600)

    out = IMAGES_DIR / "tutorial_002_image_04_candidate_heatmap.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    """Run the chart selection process for launch cadence.

    Kirk Ch 7: 'The purpose of visualisation is not to show data, it is to
    show *insight*.' The right chart is the one that most directly answers
    the curiosity question for our audience.

    Our audience: insurance professionals learning data viz.
    Our question: How did SpaceX scale its launch cadence so dramatically?
    They need to take away: the acceleration happened in distinct phases,
    and the pattern maps to their own claims frequency analysis.
    """
    df = load_and_filter()
    yearly = prepare_yearly(df)
    pivot = prepare_monthly_pivot(df)

    print("=" * 60)
    print("CHART SELECTION — Kirk Ch 7: Data Representation")
    print("=" * 60)
    print()
    print("Curiosity question: How did SpaceX scale its launch cadence")
    print("so dramatically, and what does the acceleration curve reveal?")
    print()
    print("Evaluating 4 chart candidates...")
    print()

    # --- Render all candidates ---
    chart_candidate_bar(yearly)
    print("  Bar chart: discrete yearly totals, dramatic height contrast.")
    print()

    chart_candidate_line(yearly)
    print("  Line chart: slope encodes rate of change — the acceleration itself.")
    print()

    chart_candidate_area(yearly)
    print("  Cumulative area: shows total scale but hides yearly rate changes.")
    print()

    chart_candidate_heatmap(pivot)
    print("  Heatmap: reveals monthly patterns but dense for a primary visual.")
    print()

    # --- Final selection ---
    print("=" * 60)
    print("WINNER: Bar chart (Candidate 1) as PRIMARY")
    print("SUPPORTING: Heatmap (Candidate 4) as SECONDARY")
    print("=" * 60)
    print("""
WHY THE BAR CHART WINS:

1. IMMEDIATE IMPACT: The bar chart delivers the acceleration story in
   under 2 seconds. The visual contrast between the tiny early bars and
   the towering latest-year bar is visceral — no interpretation needed.

2. PRECISE COMPARISON: Kirk Ch 7 tells us length is the most accurately
   perceived visual channel. Readers can compare any two years at a
   glance. The line chart's slope conveys rate well, but exact values
   are harder to extract without labels.

3. DISCRETE CLARITY: Each year is a separate, countable bar. This
   matches how our insurance audience thinks — they compare year-over-
   year figures in their own reporting. A line chart implies continuous
   change, but launches are discrete events grouped by year.

4. THE LINE CHART CAME CLOSE: It's better at showing the *shape* of
   acceleration (the slope), but for this audience and question, the
   bar chart's directness wins. In tutorial_final, we may combine
   elements of both.

WHY THE HEATMAP AS SECONDARY:

The heatmap answers a subplot the bar chart can't: "Did SpaceX just
launch more per year, or did they also fill in the gaps?" The shift
from sporadic (empty months) to uniform (every month active) is a
different dimension of cadence that adds depth to the story.

REJECTED:

- Cumulative area (Candidate 3): Answers a different question ("how
  many total?") rather than our cadence question ("how did the rate
  change?"). Every cumulative chart rises, which flattens the drama.
  Good for a different curiosity, not this one.
""")


if __name__ == "__main__":
    main()
