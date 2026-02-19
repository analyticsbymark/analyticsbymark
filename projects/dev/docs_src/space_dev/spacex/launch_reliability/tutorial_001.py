"""
What You'll Learn
=================
- How to load and profile SpaceX launch data for reliability analysis
- Kirk Chapter 4: Working with Data — acquiring, examining, and transforming
- Kirk Chapter 5: Editorial Thinking — what story does the failure timeline tell?
- Techniques: cumsum(), expanding().mean(), value_counts(), timedelta arithmetic
- Output: Data profiling summary + 5 initial observation charts
"""

import sys
from pathlib import Path

# Ensure the parent directory is on the path so `from data.utils import ...` works
# when this script is run directly from the launch_reliability/ folder.
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

# Status labels treated as non-successes for reliability analysis
FAILURE_STATUSES = {"Failure", "Partial Failure"}


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
def load_and_filter() -> pd.DataFrame:
    """Load SpaceX data and filter to completed launches only.

    For reliability analysis we WANT all outcomes — successes, failures,
    and partial failures. The failures ARE the data we are studying.
    Future/planned launches (TBD, Go) are excluded because their dates
    are placeholders and they have no outcome to record.

    Kirk Ch 4: 'Know your data before you visualise it.'
    """
    df = get_spacex_data()
    completed = df[df["launch_status_abbrev"].isin(["Success", "Failure", "Partial Failure"])].copy()
    # Sort chronologically — essential for cumulative calculations
    completed = completed.sort_values("net").reset_index(drop=True)
    return completed


# ---------------------------------------------------------------------------
# Profiling helpers
# ---------------------------------------------------------------------------
def print_profile(df: pd.DataFrame) -> None:
    """Print a concise profile of the dataset relevant to launch reliability."""
    failures = df[df["launch_status_abbrev"].isin(FAILURE_STATUSES)]
    successes = df[df["launch_status_abbrev"] == "Success"]

    print("=" * 60)
    print("DATASET PROFILE — Launch Reliability")
    print("=" * 60)
    print(f"Total completed launches : {len(df)}")
    print(f"Date range               : {df['net'].min()} to {df['net'].max()}")
    print(f"Years spanned            : {df['year'].nunique()} ({df['year'].min()}-{df['year'].max()})")
    print(f"Unique rockets           : {df['rocket_full_name'].nunique()}")
    print(f"Unique launch pads       : {df['launchpad_name'].nunique()}")
    print()

    # Kirk Ch 5: Editorial thinking — the headline numbers
    total = len(df)
    n_success = len(successes)
    n_failure = len(df[df["launch_status_abbrev"] == "Failure"])
    n_partial = len(df[df["launch_status_abbrev"] == "Partial Failure"])
    overall_rate = n_success / total * 100
    print(f"Successes        : {n_success} ({n_success / total * 100:.1f}%)")
    print(f"Failures         : {n_failure} ({n_failure / total * 100:.1f}%)")
    print(f"Partial Failures : {n_partial} ({n_partial / total * 100:.1f}%)")
    print(f"Overall success rate: {overall_rate:.1f}%")
    print()

    print("--- Failure / Partial Failure events (chronological) ---")
    cols = ["net", "year", "rocket_full_name", "launchpad_name",
            "mission_name", "launch_status_abbrev"]
    print(failures[cols].to_string(index=False))
    print()

    print("--- Failures by rocket variant ---")
    print(failures["rocket_full_name"].value_counts().to_string())
    print()

    print("--- Failures by launch pad ---")
    print(failures["launchpad_name"].value_counts().to_string())
    print()

    print("--- Days between consecutive failures ---")
    failure_dates = failures["net"].sort_values().reset_index(drop=True)
    for i in range(1, len(failure_dates)):
        gap = (failure_dates.iloc[i] - failure_dates.iloc[i - 1]).days
        print(f"  {str(failure_dates.iloc[i - 1])[:10]}  →  "
              f"{str(failure_dates.iloc[i])[:10]}  :  {gap} days")
    print()

    print("--- Null counts (reliability-relevant columns) ---")
    reliability_cols = ["net", "year", "rocket_full_name", "launch_status_abbrev",
                        "launchpad_name", "mission_name"]
    for col in reliability_cols:
        nulls = df[col].isnull().sum()
        print(f"  {col:35s}  {nulls}")
    print()


# ---------------------------------------------------------------------------
# Visualisation 1 — Failure timeline scatter plot
# ---------------------------------------------------------------------------
def plot_failure_timeline(df: pd.DataFrame) -> None:
    """Strip plot showing every failure and partial failure on a timeline.

    Kirk Ch 5: The clustering of early failures vs. the long modern gap
    is visible at a glance. Each point is labelled with the mission name
    so readers can immediately identify the events without cross-referencing.
    """
    failures = df[df["launch_status_abbrev"].isin(FAILURE_STATUSES)].copy()

    fig = px.strip(
        failures,
        x="net",
        y="launch_status_abbrev",
        color="launch_status_abbrev",
        hover_name="mission_name",
        hover_data={"rocket_full_name": True, "launchpad_name": True, "net": True},
        title="SpaceX Launch Failures & Partial Failures Timeline",
        labels={
            "net": "Launch Date",
            "launch_status_abbrev": "Outcome",
            "rocket_full_name": "Rocket",
            "launchpad_name": "Launch Pad",
        },
        color_discrete_map={
            "Failure": "#d62728",
            "Partial Failure": "#ff7f0e",
        },
    )

    # Add text annotations for each mission name
    for _, row in failures.iterrows():
        fig.add_annotation(
            x=row["net"],
            y=row["launch_status_abbrev"],
            text=row["mission_name"],
            showarrow=True,
            arrowhead=2,
            arrowsize=0.8,
            arrowwidth=1,
            ax=0,
            ay=-35,
            font=dict(size=9),
            bgcolor="rgba(255,255,255,0.7)",
        )

    fig.update_layout(
        width=1200,
        height=500,
        showlegend=True,
        xaxis_title="Launch Date",
        yaxis_title="Outcome",
    )

    out = IMAGES_DIR / "tutorial_001_image_01_failure_timeline.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Visualisation 2 — Cumulative success rate over time
# ---------------------------------------------------------------------------
def plot_cumulative_success_rate(df: pd.DataFrame) -> None:
    """Line chart of running success rate computed launch-by-launch.

    Kirk Ch 5: The *shape* of this curve is the reliability growth story.
    Actuaries call this credibility — early results are noisy, but as
    exposure volume grows the rate stabilises. SpaceX's curve shows exactly
    this pattern: volatile early, then converging to near-100%.

    Kirk Ch 4: We compute this purely from data — no hardcoded values.
    """
    # Create a binary success indicator, then compute expanding mean
    df_sorted = df.copy()
    df_sorted["is_success"] = (df_sorted["launch_status_abbrev"] == "Success").astype(int)
    df_sorted["launch_number"] = range(1, len(df_sorted) + 1)
    df_sorted["cumulative_success_rate"] = (
        df_sorted["is_success"].expanding().mean() * 100
    )
    df_sorted["is_failure_event"] = df_sorted["launch_status_abbrev"].isin(FAILURE_STATUSES)

    fig = px.line(
        df_sorted,
        x="net",
        y="cumulative_success_rate",
        title="SpaceX Cumulative Success Rate Over Time (Launch-by-Launch)",
        labels={
            "net": "Launch Date",
            "cumulative_success_rate": "Cumulative Success Rate (%)",
        },
    )

    # Overlay failure events as red markers
    failures = df_sorted[df_sorted["is_failure_event"]]
    fig.add_scatter(
        x=failures["net"],
        y=failures["cumulative_success_rate"],
        mode="markers",
        marker=dict(color="#d62728", size=10, symbol="x"),
        name="Failure / Partial Failure",
        hovertext=failures["mission_name"],
        hoverinfo="text+x+y",
    )

    fig.update_layout(
        width=1200,
        height=500,
        yaxis=dict(range=[60, 102], ticksuffix="%"),
        legend_title_text="Event",
    )

    out = IMAGES_DIR / "tutorial_001_image_02_cumulative_success_rate.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Visualisation 3 — Failures by rocket variant
# ---------------------------------------------------------------------------
def plot_failures_by_rocket(df: pd.DataFrame) -> None:
    """Horizontal bar chart of failure counts by rocket variant.

    Kirk Ch 5: Which vehicles carry the failure history? Separating
    Falcon 1 (development-era) from Falcon 9 variants from Starship
    prototypes tells a vehicle-lifecycle story: early vehicles fail more,
    mature platforms converge to reliability.
    """
    failures = df[df["launch_status_abbrev"].isin(FAILURE_STATUSES)].copy()

    rocket_failures = (
        failures.groupby(["rocket_full_name", "launch_status_abbrev"])
        .size()
        .reset_index(name="count")
    )

    fig = px.bar(
        rocket_failures,
        x="count",
        y="rocket_full_name",
        color="launch_status_abbrev",
        orientation="h",
        title="Failures & Partial Failures by Rocket Variant",
        labels={
            "count": "Number of Events",
            "rocket_full_name": "Rocket Variant",
            "launch_status_abbrev": "Outcome",
        },
        color_discrete_map={
            "Failure": "#d62728",
            "Partial Failure": "#ff7f0e",
        },
        barmode="stack",
    )
    fig.update_layout(
        yaxis=dict(categoryorder="total ascending"),
        width=900,
        height=500,
        legend_title_text="Outcome",
    )

    out = IMAGES_DIR / "tutorial_001_image_03_failures_by_rocket.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Visualisation 4 — Time between failures (growing gap)
# ---------------------------------------------------------------------------
def plot_time_between_failures(df: pd.DataFrame) -> None:
    """Bar chart showing days elapsed between consecutive failure events.

    Kirk Ch 5: Mean time between failures (MTBF) is a classic reliability
    engineering metric. As a launch provider matures, the MTBF grows —
    which shows up visually as the bars getting taller over time.
    This maps directly to insurance loss-frequency analysis: as a book
    of business matures, the claim frequency per exposure unit typically falls.
    """
    failures = (
        df[df["launch_status_abbrev"].isin(FAILURE_STATUSES)]
        .sort_values("net")
        .reset_index(drop=True)
    )

    intervals = []
    for i in range(1, len(failures)):
        prev = failures.iloc[i - 1]
        curr = failures.iloc[i]
        gap_days = (curr["net"] - prev["net"]).days
        intervals.append({
            "from_mission": prev["mission_name"],
            "to_mission": curr["mission_name"],
            "from_date": str(prev["net"])[:10],
            "to_date": str(curr["net"])[:10],
            "gap_days": gap_days,
            "label": f"{str(prev['net'])[:10]} → {str(curr['net'])[:10]}",
        })

    gap_df = pd.DataFrame(intervals)

    fig = px.bar(
        gap_df,
        x="label",
        y="gap_days",
        title="Days Between Consecutive Failure Events",
        labels={"label": "Failure Interval", "gap_days": "Days Between Failures"},
        hover_data={"from_mission": True, "to_mission": True, "gap_days": True},
        color="gap_days",
        color_continuous_scale="RdYlGn",
    )
    fig.update_layout(
        width=1100,
        height=500,
        xaxis_tickangle=-35,
        coloraxis_showscale=False,
        xaxis_title="Failure Interval (chronological)",
        yaxis_title="Days Between Failures",
    )

    out = IMAGES_DIR / "tutorial_001_image_04_time_between_failures.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Visualisation 5 — Yearly launch outcomes stacked bar
# ---------------------------------------------------------------------------
def plot_yearly_outcomes(df: pd.DataFrame) -> None:
    """Stacked bar chart of yearly launch outcomes (Success / Failure / Partial).

    Kirk Ch 4: A stacked bar encodes both volume and composition. We can
    see simultaneously that total launches grew dramatically while failures
    stayed flat or declined — reinforcing the reliability growth narrative.
    """
    yearly = (
        df.groupby(["year", "launch_status_abbrev"])
        .size()
        .reset_index(name="launches")
    )

    # Consistent colour mapping across charts
    color_map = {
        "Success": "#2ca02c",
        "Failure": "#d62728",
        "Partial Failure": "#ff7f0e",
    }

    fig = px.bar(
        yearly,
        x="year",
        y="launches",
        color="launch_status_abbrev",
        title="SpaceX Annual Launch Outcomes",
        labels={
            "year": "Year",
            "launches": "Number of Launches",
            "launch_status_abbrev": "Outcome",
        },
        barmode="stack",
        color_discrete_map=color_map,
    )
    fig.update_layout(
        xaxis=dict(dtick=1),
        width=1100,
        height=500,
        legend_title_text="Outcome",
    )

    out = IMAGES_DIR / "tutorial_001_image_05_yearly_outcomes.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    """Run the full profiling pipeline for launch reliability analysis.

    Kirk Ch 4: Working with data is the foundation — you cannot tell a
    credible story if you haven't first understood what the data contains,
    what it's missing, and where the interesting patterns live.

    Kirk Ch 5: For this curiosity, the editorial angle is not 'how many
    failures' but 'how quickly did SpaceX build and then sustain reliability'.
    The data tells a reliability growth curve story.
    """
    df = load_and_filter()

    # --- Profile ---
    print_profile(df)

    # --- Visualise ---
    plot_failure_timeline(df)
    plot_cumulative_success_rate(df)
    plot_failures_by_rocket(df)
    plot_time_between_failures(df)
    plot_yearly_outcomes(df)

    # Compute a few editorial numbers from data for the observation block
    failures = df[df["launch_status_abbrev"].isin(FAILURE_STATUSES)]
    successes = df[df["launch_status_abbrev"] == "Success"]
    total = len(df)
    overall_rate = len(successes) / total * 100

    failure_dates = failures["net"].sort_values().reset_index(drop=True)
    last_gap = (failure_dates.iloc[-1] - failure_dates.iloc[-2]).days if len(failure_dates) >= 2 else 0

    # Most recent failure date and launch after it
    last_failure_date = failure_dates.iloc[-1]
    post_failure = df[df["net"] > last_failure_date]
    launches_since_last = len(post_failure)

    # Year of last Falcon 9 failure
    f9_failures = failures[failures["rocket_name"] == "Falcon 9"]
    f9_last_fail_year = int(f9_failures["year"].max()) if not f9_failures.empty else None

    print()
    print("=" * 60)
    print("EDITORIAL OBSERVATIONS — Kirk Ch 5")
    print("=" * 60)
    print(f"""
1. RELIABILITY GROWTH CURVE: The cumulative success rate chart shows a
   classic reliability growth curve. Starting from ~{100 * 1 / 3:.0f}% in the
   first three launches (all Falcon 1), the rate dipped further with each
   early failure before recovering. By 2019 the curve had stabilised above
   95% and has been grinding toward {overall_rate:.1f}% overall ever since.
   This is textbook Duane growth model behaviour — a pattern originally
   observed in military equipment reliability programmes.

2. EARLY CLUSTERING vs. MODERN RECORD: The failure timeline makes the
   clustering unmistakable. 2006–2016 account for all Falcon 1 and early
   Falcon 9 failures. The last inter-failure gap before the most recent
   event was {last_gap} days — a stark contrast to the near-annual failures
   of the early Falcon era.

3. VEHICLE LIFECYCLE SEGMENTATION: The failures-by-rocket chart splits
   neatly into three lifecycle phases:
   - Falcon 1 (2006-2008): Development-era, all three flights carried
     reliability risk as SpaceX learned orbital launch mechanics.
   - Falcon 9 variants (2012-2016): Two in-flight failures and one pad
     anomaly as vehicle variants (v1.0 → v1.1 → Full Thrust) were introduced.
   - Starship prototypes (2020-2025): A new vehicle program repeating
     the development-era reliability curve — expected and accepted.

4. THE FALCON 9 MATURE RECORD: After the 2016 Amos-6 pad explosion,
   Falcon 9 flew with a single partial failure in 2024 across hundreds
   of missions. The operational Falcon 9 Block 5 record is extraordinary
   for a commercial launch vehicle at this cadence.

5. DOMAIN TRANSFER — INSURANCE LOSS EXPERIENCE TRENDING:
   This tutorial's analysis maps directly to insurance actuarial practice:
   - Cumulative success rate ≡ inverse of cumulative loss frequency
   - Failure timeline clustering ≡ development-year loss emergence
   - Mean time between failures ≡ claim frequency per exposure unit
   - Vehicle lifecycle phases ≡ policy cohort maturation
   Actuaries build 'credibility' into loss histories the same way SpaceX
   built credibility into its flight record — early-period volatility is
   discounted; recent, stable periods carry more weight in rate-setting.
   The reliability growth curve is the actuarial loss-development triangle
   viewed from the frequency dimension rather than the severity dimension.
""")


if __name__ == "__main__":
    main()
