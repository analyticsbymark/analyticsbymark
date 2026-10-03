"""
What You'll Learn
=================
- How to load and profile SpaceX launch data for cadence analysis
- Kirk Chapter 4: Working with Data — acquiring, examining, and transforming
- Kirk Chapter 5: Editorial Thinking — what story does the acceleration tell?
- Techniques: value_counts(), groupby(), pivot_table(), partial-period handling
- Output: A printed data profile + 4 initial observation charts in images/

Run standalone:
    python3 tutorial_001.py
"""

import sys
from pathlib import Path

# Ensure the parent directory is on the path so `from data.utils import ...`
# works when this script is run directly from the curiosity folder.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Standard imports
import pandas as pd
import plotly.express as px

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
# Data loading
# ---------------------------------------------------------------------------
def load_completed(df: pd.DataFrame) -> pd.DataFrame:
    """Filter to launches that actually flew (Success / Failure / Partial).

    Future and undated launches (TBD, Go for Launch) carry placeholder dates
    that would distort the cadence curve, so we exclude them for the counts.

    Kirk Ch 4: 'Know your data before you visualise it.'
    """
    return df[df["launch_status_abbrev"].isin(["Success", "Failure", "Partial Failure"])]


def latest_complete_year(df: pd.DataFrame) -> int:
    """Return the most recent year that is not still in progress.

    The dataset is refreshed live, so the current calendar year is partial —
    plotting it at face value reads as a cadence collapse. We treat the last
    year as 'incomplete' and flag it rather than dropping it silently.
    Kirk Ch 5: be honest about what the data can and cannot say.
    """
    return int(df["year"].max()) - 1


# ---------------------------------------------------------------------------
# Profiling
# ---------------------------------------------------------------------------
def print_profile(df: pd.DataFrame) -> None:
    """Print a concise profile of the dataset relevant to launch cadence."""
    print("=" * 60)
    print("DATASET PROFILE — Launch Cadence")
    print("=" * 60)
    print(f"Total completed launches : {len(df)}")
    print(f"Date range               : {df['net'].min()} to {df['net'].max()}")
    print(f"Years spanned            : {df['year'].nunique()} ({df['year'].min()}-{df['year'].max()})")
    print(f"Unique rockets           : {df['rocket_name'].nunique()}")
    print(f"Unique launch pads       : {df['launchpad_name'].nunique()}")
    print()

    # Kirk Ch 5: Editorial thinking — the acceleration is the headline.
    first_year = int(df["year"].min())
    last_full = latest_complete_year(df)
    first_count = len(df[df["year"] == first_year])
    last_count = len(df[df["year"] == last_full])
    print(f"First year ({first_year})        : {first_count} launch(es)")
    print(f"Latest complete year ({last_full}) : {last_count} launches")
    print(f"Growth factor              : ~{last_count / max(first_count, 1):.0f}x")
    print(f"Note: {int(df['year'].max())} is still in progress — read it as partial.")
    print()

    print("--- Launches per year ---")
    yearly = df.groupby("year").size()
    peak = yearly.max()
    for year, count in yearly.items():
        bar = "#" * max(1, round(count / peak * 40))
        flag = "  (partial)" if year == df["year"].max() else ""
        print(f"  {year}  {count:>4}  {bar}{flag}")
    print()

    print("--- Launch status breakdown ---")
    print(df["launch_status_abbrev"].value_counts().to_string())
    print()

    print("--- Rocket usage ---")
    print(df["rocket_name"].value_counts().to_string())
    print()

    print("--- Null counts (cadence-relevant columns) ---")
    cadence_cols = ["net", "year", "month", "rocket_name",
                    "launch_status_abbrev", "launchpad_name", "mission_type"]
    for col in cadence_cols:
        print(f"  {col:24s}  {df[col].isnull().sum()}")
    print()


# ---------------------------------------------------------------------------
# Visualisation 1 — Yearly launch cadence
# ---------------------------------------------------------------------------
def plot_yearly_cadence(df: pd.DataFrame) -> None:
    """Bar chart of launches per year.

    Kirk Ch 5: We expect growth — the *shape* (flat for a decade, then
    near-vertical) is the surprise that earns the curiosity question.

    Colour is deliberately left as the Plotly default here — palette design
    is tutorial_003's job. The only intervention is reducing the opacity of
    the trailing partial year so it does not read as a sudden drop. That is a
    data-integrity cue (provisional data), not an aesthetic choice.
    """
    yearly = df.groupby("year").size().reset_index(name="launches")
    partial_year = int(df["year"].max())
    # Full opacity for complete years, faded for the in-progress year.
    opacities = [0.35 if y == partial_year else 1.0 for y in yearly["year"]]

    fig = px.bar(
        yearly,
        x="year",
        y="launches",
        title="SpaceX Launches per Year (Completed Flights)",
        labels={"year": "Year", "launches": "Number of Launches"},
    )
    fig.update_traces(marker_opacity=opacities)
    fig.add_annotation(
        x=partial_year, y=int(yearly.loc[yearly["year"] == partial_year, "launches"].iloc[0]),
        text="partial", showarrow=False, yshift=12, font=dict(size=11),
    )
    fig.update_layout(xaxis=dict(dtick=2), showlegend=False)
    save_chart(fig, "tutorial_001_image_01_yearly_cadence.png")


# ---------------------------------------------------------------------------
# Visualisation 2 — Monthly cadence heatmap
# ---------------------------------------------------------------------------
def plot_monthly_heatmap(df: pd.DataFrame) -> None:
    """Heatmap of launches by year x month.

    Kirk Ch 5: A heatmap exposes the seasonal-to-continuous shift that a
    yearly bar chart hides — early years cluster, recent years fill in.
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
        color_continuous_scale="Blues",
        title="Monthly Launch Heatmap (Completed Flights)",
        labels=dict(x="Month", y="Year", color="Launches"),
        aspect="auto",
    )
    save_chart(fig, "tutorial_001_image_02_monthly_cadence.png")


# ---------------------------------------------------------------------------
# Visualisation 3 — Mission types distribution
# ---------------------------------------------------------------------------
def plot_mission_types(df: pd.DataFrame) -> None:
    """Horizontal bar chart of mission types.

    Kirk Ch 4: Profiling categories before encoding them — with many mission
    types we decide early whether to group minor ones downstream.
    """
    type_counts = df["mission_type"].value_counts().reset_index()
    type_counts.columns = ["mission_type", "count"]

    fig = px.bar(
        type_counts,
        x="count",
        y="mission_type",
        orientation="h",
        title="Completed Launches by Mission Type",
        labels={"count": "Number of Launches", "mission_type": "Mission Type"},
    )
    fig.update_layout(yaxis=dict(categoryorder="total ascending"))
    save_chart(fig, "tutorial_001_image_03_mission_types.png")


# ---------------------------------------------------------------------------
# Visualisation 4 — Rocket evolution over time
# ---------------------------------------------------------------------------
def plot_rocket_evolution(df: pd.DataFrame) -> None:
    """Stacked bar of rocket usage per year.

    Kirk Ch 5: The rocket mix is a subplot within the cadence story — is the
    acceleration one vehicle or many? (Spoiler the colour will reveal.)
    """
    rocket_year = df.groupby(["year", "rocket_name"]).size().reset_index(name="launches")

    fig = px.bar(
        rocket_year,
        x="year",
        y="launches",
        color="rocket_name",
        title="Rocket Usage by Year (Completed Flights)",
        labels={"year": "Year", "launches": "Launches", "rocket_name": "Rocket"},
        barmode="stack",
    )
    fig.update_layout(xaxis=dict(dtick=2), legend_title_text="Rocket")
    save_chart(fig, "tutorial_001_image_04_rocket_evolution.png")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    """Run the full profiling pipeline for launch cadence analysis.

    Kirk Ch 4: Working with data is the foundation — you cannot tell a
    credible story until you understand what the data holds, what it lacks,
    and where the interesting patterns live.
    """
    df = load_completed(get_spacex_data())

    print_profile(df)

    plot_yearly_cadence(df)
    plot_monthly_heatmap(df)
    plot_mission_types(df)
    plot_rocket_evolution(df)

    print()
    print("=" * 60)
    print("EDITORIAL OBSERVATIONS — Kirk Ch 5")
    print("=" * 60)
    print("""
1. ACCELERATION PHASES: the yearly chart shows distinct eras — a single-digit
   startup decade, a steady growth climb, then a hyperscale jump.

2. SEASONALITY: the monthly heatmap shows early years clustered with multi-month
   gaps, while recent years fill in — SpaceX now operates as an always-on service.

3. ONE VEHICLE, MOSTLY: the rocket-evolution chart shows the acceleration is
   overwhelmingly a Falcon 9 story; reusability is what makes the cadence possible.

4. PARTIAL YEARS ARE NOT A DECLINE: the most recent year is still in progress.
   We flag it rather than letting it read as a cadence collapse.

DOMAIN TRANSFER: claims-frequency analysts will recognise the same arc — a
portfolio moving from sporadic events to a high-frequency steady state — and the
'is the latest period real or just incomplete?' caveat is the development-triangle
problem in disguise.
""")


if __name__ == "__main__":
    main()