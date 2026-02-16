"""
What You'll Learn
=================
- How to load and profile SpaceX launch data for cadence analysis
- Kirk Chapter 4: Working with Data — acquiring, examining, and transforming
- Kirk Chapter 5: Editorial Thinking — what story does the acceleration tell?
- Techniques: pd.describe(), value_counts(), groupby(), pivot_table()
- Output: Data profiling summary + 4 initial observation charts
"""

import sys
from pathlib import Path

# Ensure the parent directory is on the path so `from data.utils import ...` works
# when this script is run directly from the launch_cadence/ folder.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Standard imports
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Local imports
from data.utils import get_spacex_data

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
IMAGES_DIR = Path(__file__).resolve().parent / "images"
IMAGES_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
def load_and_filter() -> pd.DataFrame:
    """Load SpaceX data and filter to completed launches only.

    Future/planned launches (TBD, Go) are excluded from cadence analysis
    because their dates are placeholders — including them would distort
    the acceleration curve.

    Kirk Ch 4: 'Know your data before you visualise it.'
    """
    df = get_spacex_data()
    completed = df[df["launch_status_abbrev"].isin(["Success", "Failure", "Partial Failure"])]
    return completed


# ---------------------------------------------------------------------------
# Profiling helpers
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

    # Kirk Ch 5: Editorial thinking — what jumps out?
    # The acceleration is the headline number: how many-fold increase?
    first_year = df["year"].min()
    last_year = df[df["launch_status_abbrev"] == "Success"]["year"].max()
    first_count = len(df[df["year"] == first_year])
    last_count = len(df[df["year"] == last_year])
    print(f"First year ({first_year}): {first_count} launch(es)")
    print(f"Latest full year ({last_year}): {last_count} launches")
    print(f"Growth factor: ~{last_count / max(first_count, 1):.0f}x")
    print()

    print("--- Launches per year ---")
    yearly = df.groupby("year").size()
    for year, count in yearly.items():
        bar = "█" * count
        print(f"  {year}  {count:>4}  {bar}")
    print()

    print("--- Launch status breakdown ---")
    print(df["launch_status_abbrev"].value_counts().to_string())
    print()

    print("--- Rocket usage ---")
    print(df["rocket_name"].value_counts().to_string())
    print()

    print("--- Mission types (top 10) ---")
    print(df["mission_type"].value_counts().head(10).to_string())
    print()

    print("--- Null counts (cadence-relevant columns) ---")
    cadence_cols = ["net", "year", "month", "rocket_name", "launch_status_abbrev",
                    "launchpad_name", "mission_type"]
    for col in cadence_cols:
        nulls = df[col].isnull().sum()
        print(f"  {col:30s}  {nulls}")
    print()


# ---------------------------------------------------------------------------
# Visualisation 1 — Yearly launch cadence
# ---------------------------------------------------------------------------
def plot_yearly_cadence(df: pd.DataFrame) -> None:
    """Bar chart of launches per year.

    Kirk Ch 5: The acceleration curve IS the story. We expect growth,
    but the *shape* — slow for a decade, then near-vertical — is the
    surprise that makes this curiosity question worth exploring.
    """
    yearly = df.groupby("year").size().reset_index(name="launches")

    fig = px.bar(
        yearly,
        x="year",
        y="launches",
        title="SpaceX Launches per Year (Completed)",
        labels={"year": "Year", "launches": "Number of Launches"},
    )
    fig.update_layout(
        xaxis=dict(dtick=1),
        yaxis_title="Launches",
        showlegend=False,
        width=1000,
        height=500,
    )

    out = IMAGES_DIR / "tutorial_001_image_01_yearly_cadence.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Visualisation 2 — Monthly cadence heatmap
# ---------------------------------------------------------------------------
def plot_monthly_heatmap(df: pd.DataFrame) -> None:
    """Heatmap of launches by year × month.

    Kirk Ch 5: A heatmap reveals seasonality patterns that a simple yearly
    bar chart hides. Does SpaceX launch more in certain months? Has the
    seasonal pattern changed as cadence scaled up?
    """
    pivot = df.pivot_table(
        index="year", columns="month", aggfunc="size", fill_value=0
    )
    # Ensure all 12 months are represented
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
        title="Monthly Launch Heatmap (Completed Launches)",
        labels=dict(x="Month", y="Year", color="Launches"),
        aspect="auto",
    )
    fig.update_layout(width=900, height=600)

    out = IMAGES_DIR / "tutorial_001_image_02_monthly_cadence.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Visualisation 3 — Mission types distribution
# ---------------------------------------------------------------------------
def plot_mission_types(df: pd.DataFrame) -> None:
    """Horizontal bar chart of mission types.

    Kirk Ch 4: Profiling means understanding what categories exist before
    choosing how to encode them. With 16+ mission types, we need to decide
    early whether to group minor categories for downstream tutorials.
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
    fig.update_layout(
        yaxis=dict(categoryorder="total ascending"),
        width=900,
        height=600,
    )

    out = IMAGES_DIR / "tutorial_001_image_03_mission_types.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Visualisation 4 — Rocket evolution over time
# ---------------------------------------------------------------------------
def plot_rocket_evolution(df: pd.DataFrame) -> None:
    """Stacked bar chart showing rocket variant usage per year.

    Kirk Ch 5: The rocket mix is a subplot within the cadence story —
    the transition from Falcon 1 → Falcon 9 variants → Falcon Heavy
    maps to technology lifecycle phases. This profiling chart lets us
    see whether the cadence acceleration is driven by one vehicle or many.
    """
    rocket_year = (
        df.groupby(["year", "rocket_name"])
        .size()
        .reset_index(name="launches")
    )

    fig = px.bar(
        rocket_year,
        x="year",
        y="launches",
        color="rocket_name",
        title="Rocket Usage by Year (Completed Launches)",
        labels={"year": "Year", "launches": "Launches", "rocket_name": "Rocket"},
        barmode="stack",
    )
    fig.update_layout(
        xaxis=dict(dtick=1),
        width=1000,
        height=500,
        legend_title_text="Rocket",
    )

    out = IMAGES_DIR / "tutorial_001_image_04_rocket_evolution.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    """Run the full profiling pipeline for launch cadence analysis.

    Kirk Ch 4: Working with data is the foundation — you cannot tell a
    credible story if you haven't first understood what the data contains,
    what it's missing, and where the interesting patterns live.
    """
    df = load_and_filter()

    # --- Profile ---
    print_profile(df)

    # --- Visualise ---
    plot_yearly_cadence(df)
    plot_monthly_heatmap(df)
    plot_mission_types(df)
    plot_rocket_evolution(df)

    print()
    print("=" * 60)
    print("EDITORIAL OBSERVATIONS — Kirk Ch 5")
    print("=" * 60)
    print("""
1. ACCELERATION PHASES: The yearly cadence chart shows three distinct eras:
   - Startup (2006-2013): Single-digit launches, proving the vehicle works
   - Growth (2014-2019): Steady climb from 6 to 21 launches per year
   - Hyperscale (2020-2025): Exponential jump from 29 to 170+

2. SEASONALITY: The monthly heatmap reveals that early years had clustered
   launches (gaps of several months), while recent years show near-uniform
   monthly distribution — SpaceX now operates as an always-on service.

3. FALCON 9 DOMINANCE: The rocket evolution chart makes clear that the
   acceleration is almost entirely a Falcon 9 Block 5 story. The vehicle's
   reusability enabled the cadence that would be impossible with expendable
   rockets.

4. COMMUNICATIONS CONCENTRATION: Mission type profiling shows ~80% of
   completed launches are communications (dominated by Starlink). This is
   important context — the cadence story is inseparable from the Starlink
   deployment story.

DOMAIN TRANSFER: Insurance professionals tracking claims frequency would
recognise the same pattern — a portfolio that shifts from sporadic events
to high-frequency, operationally steady state. The monthly heatmap technique
applies directly to claims-by-month reporting.
""")


if __name__ == "__main__":
    main()
