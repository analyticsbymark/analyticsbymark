"""
What You'll Learn
=================
- How to choose a chart type by *encoding suitability*, not habit (Kirk Chapter 7)
- Why the same data (yearly launch counts) tells a different story as a bar,
  a line, and a log-scaled line — and when each encoding earns its place
- How a year x month heatmap answers a *different* sub-question than the trend
- Techniques: groupby().size(), pivot_table(), log axes, marker_opacity as a
  data-integrity cue (not a style choice)
- Output: 4 candidate charts in images/ + a printed selection rationale

The lesson is the *iteration*, not the answer. We render a small set of honest
candidates, say out loud why each works or fails, then commit to one.

Run standalone:
    python3 tutorial_002.py
"""

import sys
from pathlib import Path

# Ensure the parent directory is on the path so `from data.utils import ...`
# works when this script is run directly from the curiosity folder.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Standard imports
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go  # noqa: F401  (kept per standard import block)

# Local imports — data/utils.py is the only sanctioned loader.
from data.utils import get_spacex_data

# ---------------------------------------------------------------------------
# Constants & image export
# ---------------------------------------------------------------------------
IMAGES_DIR = Path(__file__).resolve().parent / "images"
IMAGES_DIR.mkdir(exist_ok=True)

# Image standards (Analytics by Mark): white background, fixed resolution.
# Inlined here so the tutorial stays copy-paste standalone — no imports from
# the skills folder.
IMG_WIDTH, IMG_HEIGHT, IMG_SCALE = 1200, 800, 2


def save_chart(fig, name: str) -> None:
    """Export a Plotly figure to images/ on a white background per standards."""
    fig.update_layout(paper_bgcolor="white", plot_bgcolor="white")
    out = IMAGES_DIR / name
    fig.write_image(str(out), width=IMG_WIDTH, height=IMG_HEIGHT, scale=IMG_SCALE)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Data loading & shared shaping
# ---------------------------------------------------------------------------
def load_completed(df: pd.DataFrame) -> pd.DataFrame:
    """Filter to launches that actually flew (Success / Failure / Partial).

    Same rule as tutorial_001: future/TBD launches carry placeholder dates that
    would distort the cadence curve, so we exclude them for the counts.
    """
    return df[df["launch_status_abbrev"].isin(["Success", "Failure", "Partial Failure"])]


def yearly_counts(df: pd.DataFrame) -> pd.DataFrame:
    """Launches per year — the single series every yearly candidate encodes."""
    return df.groupby("year").size().reset_index(name="launches")


# ---------------------------------------------------------------------------
# Candidate 1 — Bar (the tutorial_001 baseline)
# ---------------------------------------------------------------------------
def candidate_bar(df: pd.DataFrame) -> None:
    """Bar chart of launches per year.

    VERDICT: A bar encodes each year's *magnitude* as length — easy to compare
    one year against another and to read an exact count. But bars sit as
    separate objects, so the eye has to reconstruct the *trajectory*; the
    acceleration (the rate of change that the curiosity is actually about) is
    implied rather than drawn. Good for "how many", weaker for "what shape".
    """
    yearly = yearly_counts(df)
    partial_year = int(yearly["year"].max())
    # Data-integrity cue only: fade the in-progress year so a partial count is
    # not misread as a real drop. Same default hue — this is not a colour choice.
    opacities = [0.35 if y == partial_year else 1.0 for y in yearly["year"]]

    fig = px.bar(
        yearly,
        x="year",
        y="launches",
        title="Candidate 1 — Bar: launches per year",
        labels={"year": "Year", "launches": "Number of Launches"},
    )
    fig.update_traces(marker_opacity=opacities)
    fig.update_layout(xaxis=dict(dtick=2), showlegend=False)
    save_chart(fig, "tutorial_002_image_01_candidate_bar.png")


# ---------------------------------------------------------------------------
# Candidate 2 — Line (trajectory)
# ---------------------------------------------------------------------------
def candidate_line(df: pd.DataFrame) -> None:
    """Line chart of launches per year.

    VERDICT: A line connects the years into a single trajectory, so the eye
    reads *slope* directly — the flat startup decade, the bend, then the
    near-vertical climb are all legible at a glance. This is exactly the
    "shape of the acceleration" the curiosity asks about. Trade-off: exact
    per-year values are slightly harder to pick off than from bars.
    """
    yearly = yearly_counts(df)
    partial_year = int(yearly["year"].max())
    partial_val = int(yearly.loc[yearly["year"] == partial_year, "launches"].iloc[0])

    fig = px.line(
        yearly,
        x="year",
        y="launches",
        markers=True,
        title="Candidate 2 — Line: launches per year",
        labels={"year": "Year", "launches": "Number of Launches"},
    )
    # Honest partial-year note (text only, no colour/style choice).
    fig.add_annotation(
        x=partial_year, y=partial_val,
        text=f"{partial_year} partial", showarrow=True, arrowhead=0,
        ax=-40, ay=-30, font=dict(size=11),
    )
    fig.update_layout(xaxis=dict(dtick=2), showlegend=False)
    save_chart(fig, "tutorial_002_image_02_candidate_line.png")


# ---------------------------------------------------------------------------
# Candidate 3 — Log-scaled line (regime detection)
# ---------------------------------------------------------------------------
def candidate_log_line(df: pd.DataFrame) -> None:
    """Line chart of launches per year on a log y-axis.

    VERDICT: On a log axis, *constant exponential growth* plots as a straight
    line, so changes in slope expose the phase transitions — a gentle early
    incline, then a steeper, straighter industrial-scale segment. This is the
    analytically revealing view (is the growth exponential, and where do the
    regimes break?). Trade-off: a log axis is harder for a general audience to
    read intuitively, so it informs the analyst more than the headline.
    """
    yearly = yearly_counts(df)
    partial_year = int(yearly["year"].max())

    fig = px.line(
        yearly,
        x="year",
        y="launches",
        markers=True,
        log_y=True,
        title="Candidate 3 — Log-scaled line: launches per year (exponential check)",
        labels={"year": "Year", "launches": "Launches (log scale)"},
    )
    fig.add_annotation(
        x=partial_year, y=yearly["launches"].max(),
        text=f"{partial_year} partial", showarrow=False, yshift=10, font=dict(size=11),
    )
    fig.update_layout(xaxis=dict(dtick=2), showlegend=False)
    save_chart(fig, "tutorial_002_image_03_candidate_log_line.png")


# ---------------------------------------------------------------------------
# Candidate 4 — Heatmap (a different sub-question)
# ---------------------------------------------------------------------------
def candidate_heatmap(df: pd.DataFrame) -> None:
    """Heatmap of launches by year x month.

    VERDICT: A heatmap does not compete with the trend charts — it answers a
    *parallel* question: how the launches distribute *within* each year. It
    exposes the seasonal-to-continuous shift (early rows clustered with gaps,
    recent rows filled across all months) that any yearly aggregate hides.
    Strong as a companion, but it does not carry the acceleration headline on
    its own.
    """
    pivot = df.pivot_table(index="year", columns="month", aggfunc="size", fill_value=0)
    for m in range(1, 13):
        if m not in pivot.columns:
            pivot[m] = 0
    pivot = pivot[range(1, 13)]

    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    fig = px.imshow(
        pivot.values,
        x=month_labels,
        y=[str(y) for y in pivot.index],
        title="Candidate 4 — Heatmap: launches by year x month",
        labels=dict(x="Month", y="Year", color="Launches"),
        aspect="auto",
    )
    save_chart(fig, "tutorial_002_image_04_candidate_heatmap.png")


# ---------------------------------------------------------------------------
# Main — run every candidate, then commit to one
# ---------------------------------------------------------------------------
def main() -> None:
    """Render the candidate set, then weigh them and pick a winner (Kirk Ch 7).

    Kirk Ch 7: chart selection is a chain of small decisions about which visual
    encoding best matches the question and the audience — explored, not guessed.
    """
    df = load_completed(get_spacex_data())

    print("=" * 64)
    print("CHART SELECTION — Kirk Ch 7")
    print("Curiosity: what does the *shape* of SpaceX's acceleration reveal?")
    print("=" * 64)
    print("Rendering 4 candidates (default Plotly, no styling yet)...\n")

    candidate_bar(df)
    candidate_line(df)
    candidate_log_line(df)
    candidate_heatmap(df)

    print()
    print("=" * 64)
    print("EDITORIAL THINKING — story / audience / takeaway")
    print("=" * 64)
    print("""
STORY    : The headline is not "how many launches" but the *shape* of the rise —
           a flat experimentation decade, a bend at the proving phase, then a
           near-vertical industrial climb.
AUDIENCE : A mixed portfolio/learner audience who reads slopes far more readily
           than they reconstruct a trend from separated bars.
TAKEAWAY : "The growth is accelerating, in distinct regimes" — a message a line
           draws directly and a bar only implies.

WINNER: Candidate 2 — LINE.
  - It encodes the trajectory the curiosity is about; the acceleration is drawn,
    not inferred. The bar (Candidate 1) is the better *reference* table but buries
    the shape.
  - Companion views, kept for later steps: the LOG-LINE (Candidate 3) is the
    analyst's check on exponential regimes, and the HEATMAP (Candidate 4) carries
    the parallel seasonal-to-continuous story. Neither replaces the line as the
    headline encoding.

NEXT (tutorial_003): colour. The line is the right shape — now a sequential
palette for time progression and a colour-blind-safe treatment give it voice.
""")


if __name__ == "__main__":
    main()
