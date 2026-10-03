"""
What You'll Learn
=================
- How to iterate through chart types to find the best fit for a reliability story
- Kirk Chapter 7: Data Representation — choosing the right chart for data + message
- The process of selection IS the lesson: try each type, evaluate, then decide
- Why the scatter/strip plot wins over seemingly richer alternatives
- Output: 4 chart candidates evaluated, 1 winner declared + 1 secondary selected
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

    Completed launches have a definitive outcome: Success, Failure, or
    Partial Failure. Future/planned launches are excluded because they have
    no outcome and their dates may be placeholders.

    Kirk Ch 4: Always know your data before you visualise it.
    """
    df = get_spacex_data()
    completed = df[df["launch_status_abbrev"].isin(["Success", "Failure", "Partial Failure"])].copy()
    # Sort chronologically — essential for cumulative and MTBF calculations
    completed = completed.sort_values("net").reset_index(drop=True)
    return completed


# ---------------------------------------------------------------------------
# Data preparation helpers
# ---------------------------------------------------------------------------
def prepare_failures(df: pd.DataFrame) -> pd.DataFrame:
    """Extract only the failure and partial failure events.

    All data-dependent values are computed from data — nothing hardcoded.
    Kirk Ch 4: Let the data speak for itself.
    """
    return df[df["launch_status_abbrev"].isin(FAILURE_STATUSES)].copy()


def prepare_cumulative_success(df: pd.DataFrame) -> pd.DataFrame:
    """Compute a launch-by-launch running success rate.

    Uses expanding().mean() to compute the rolling cumulative average of a
    binary success indicator. This is equivalent to (successes so far / launches
    so far) at each step.

    Kirk Ch 7: The shape of this curve is the reliability growth narrative —
    it encodes the same story as the scatter but in a smoothed, aggregate form.
    """
    df_sorted = df.copy()
    df_sorted["is_success"] = (df_sorted["launch_status_abbrev"] == "Success").astype(int)
    df_sorted["launch_number"] = range(1, len(df_sorted) + 1)
    df_sorted["cumulative_success_rate"] = df_sorted["is_success"].expanding().mean() * 100
    df_sorted["is_failure_event"] = df_sorted["launch_status_abbrev"].isin(FAILURE_STATUSES)
    return df_sorted


def prepare_yearly_outcomes(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate launch outcomes by year.

    Kirk Ch 7: Stacked bars show composition and volume simultaneously,
    but when successes vastly outnumber failures, the failure slivers become
    invisible — the key weakness we will expose in Candidate 3.
    """
    yearly = (
        df.groupby(["year", "launch_status_abbrev"])
        .size()
        .reset_index(name="count")
    )
    return yearly


def prepare_mtbf(df: pd.DataFrame) -> pd.DataFrame:
    """Compute days between consecutive failure events (MTBF proxy).

    Mean time between failures (MTBF) is a classic reliability engineering
    metric. As a launch provider matures its processes, the MTBF grows —
    which maps directly to insurance loss-frequency trending:
    claim frequency per exposure unit typically falls as a book matures.

    Kirk Ch 4: All values derived from data, no hardcoding.
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
            "to_date_dt": curr["net"],
            "gap_days": gap_days,
            # Short label: just the destination failure date
            "label": str(curr["net"])[:10],
            "interval_number": i,
        })

    return pd.DataFrame(intervals)


# ---------------------------------------------------------------------------
# Candidate 1 — Failure timeline scatter/strip plot  [THE WINNER]
# ---------------------------------------------------------------------------
def chart_candidate_failure_timeline(failures: pd.DataFrame) -> None:
    """Strip/scatter plot: every failure event as a point on a horizontal timeline.

    Kirk Ch 7: Position along a common scale is the most accurately perceived
    visual channel (Cleveland & McGill, 1984). Every failure event is an
    identifiable point with a mission name. The early clustering (2006-2016)
    vs. the modern sparsity (post-2016) is visible at a glance — no
    aggregation, no smoothing, no data hidden.

    This is the most DIRECT answer to the curiosity question:
    'What does the failure timeline reveal about how SpaceX built reliability?'

    VERDICT: PRIMARY WINNER — visceral, direct, every event is legible.
    """
    # Kirk Ch 7: unstyled — the point here is to evaluate chart TYPE, not colour
    fig = px.scatter(
        failures,
        x="net",
        y="launch_status_abbrev",
        hover_name="mission_name",
        hover_data={"rocket_full_name": True, "net": True, "launch_status_abbrev": True},
        title="Candidate 1: Failure Timeline Scatter — Every Event on a Timeline",
        labels={
            "net": "Launch Date",
            "launch_status_abbrev": "Outcome",
        },
    )
    fig.update_layout(
        width=1200,
        height=400,
        xaxis_title="Launch Date",
        yaxis_title="Outcome",
    )

    out = IMAGES_DIR / "tutorial_002_image_01_candidate_failure_timeline.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Candidate 2 — Cumulative success rate line chart  [SECONDARY]
# ---------------------------------------------------------------------------
def chart_candidate_cumulative_success(df_cumulative: pd.DataFrame) -> None:
    """Line chart of running success rate computed launch-by-launch.

    Kirk Ch 7: Line charts imply continuity and encode rate-of-change via
    slope. The *shape* of this curve is the reliability growth narrative —
    volatile in the early launches, converging toward ~100% as the flight
    record deepens.

    Weakness: the smoothed aggregate hides individual failure events. After
    aggregation, you see the curve's shape but lose the specific event
    clustering that makes the timeline so powerful.

    VERDICT: SECONDARY — shows the *shape* of reliability growth that the
    scatter doesn't capture, but loses the individual-event granularity.
    """
    # Kirk Ch 7: unstyled — evaluate chart TYPE first
    fig = px.line(
        df_cumulative,
        x="net",
        y="cumulative_success_rate",
        title="Candidate 2: Cumulative Success Rate — The Reliability Growth Curve",
        labels={
            "net": "Launch Date",
            "cumulative_success_rate": "Cumulative Success Rate (%)",
        },
    )
    fig.update_layout(
        width=1200,
        height=450,
        xaxis_title="Launch Date",
        yaxis_title="Cumulative Success Rate (%)",
    )

    out = IMAGES_DIR / "tutorial_002_image_02_candidate_cumulative_success.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Candidate 3 — Yearly outcomes stacked bar
# ---------------------------------------------------------------------------
def chart_candidate_yearly_stacked(yearly: pd.DataFrame) -> None:
    """Stacked bar chart of yearly launch outcomes (Success / Failure / Partial).

    Kirk Ch 7: Stacked bars encode composition + volume simultaneously. The
    problem here is dynamic range: in high-cadence years (50+ launches), a
    single failure is a sliver < 2% of the bar height. The very thing we are
    studying — the failure signal — becomes invisible in the chart.

    This chart excels for showing launch *volume growth* but obscures the
    reliability story. It is the wrong tool for this curiosity question.

    VERDICT: REJECTED — failure slivers are invisible against success bars
    in high-cadence years. Optimises for volume, not reliability signal.
    """
    # Kirk Ch 7: unstyled — evaluate chart TYPE first
    fig = px.bar(
        yearly,
        x="year",
        y="count",
        color="launch_status_abbrev",
        title="Candidate 3: Yearly Stacked Bar — Outcomes by Year",
        labels={
            "year": "Year",
            "count": "Number of Launches",
            "launch_status_abbrev": "Outcome",
        },
        barmode="stack",
    )
    fig.update_layout(
        width=1100,
        height=500,
        xaxis=dict(dtick=1),
        xaxis_title="Year",
        yaxis_title="Number of Launches",
        legend_title_text="Outcome",
    )

    out = IMAGES_DIR / "tutorial_002_image_03_candidate_yearly_stacked.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Candidate 4 — Time-between-failures bar chart
# ---------------------------------------------------------------------------
def chart_candidate_mtbf(mtbf_df: pd.DataFrame) -> None:
    """Bar chart of days between consecutive failure events.

    Kirk Ch 7: This is a derived metric — MTBF. The growing bar heights
    across successive intervals do tell a reliability story, but at the
    cost of temporal context. The x-axis becomes 'failure interval N' not
    'calendar time', so readers lose their sense of *when* these intervals
    occurred relative to SpaceX's history.

    Additionally, with only ~14 intervals (one per consecutive failure pair),
    the chart is sparsely populated and the x-axis labels are dense date strings
    that are hard to scan.

    VERDICT: REJECTED — loses temporal calendar context, thin dataset (one
    bar per consecutive failure pair), and the MTBF story is already implied
    by the growing gap visible in Candidate 1.
    """
    if mtbf_df.empty:
        print("  (No MTBF data to plot — skipping Candidate 4)")
        return

    # Kirk Ch 7: unstyled — evaluate chart TYPE first
    fig = px.bar(
        mtbf_df,
        x="label",
        y="gap_days",
        title="Candidate 4: Time-Between-Failures — Days Between Consecutive Failures",
        labels={
            "label": "Failure Date (destination event)",
            "gap_days": "Days Since Previous Failure",
        },
        hover_data={
            "from_mission": True,
            "to_mission": True,
            "from_date": True,
            "to_date": True,
            "gap_days": True,
        },
    )
    fig.update_layout(
        width=1100,
        height=500,
        xaxis_tickangle=-35,
        xaxis_title="Destination Failure Date",
        yaxis_title="Days Since Previous Failure",
    )

    out = IMAGES_DIR / "tutorial_002_image_04_candidate_mtbf.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    """Run the chart selection process for launch reliability analysis.

    Kirk Ch 7: 'The purpose of visualisation is not to show data, it is to
    show *insight*.' The right chart is the one that most directly answers
    the curiosity question for our audience.

    Our audience: insurance professionals learning data visualisation.
    Our question: What does SpaceX's failure timeline reveal about how rapidly
                  a launch provider builds — and sustains — operational reliability?

    They need to take away: Reliability was NOT a steady march. It came in
    lifecycle phases, and the failure timeline makes each phase visible as a
    distinct cluster separated by growing gaps.
    """
    df = load_and_filter()

    # Prepare datasets for each candidate — all values derived from data
    failures = prepare_failures(df)
    df_cumulative = prepare_cumulative_success(df)
    yearly = prepare_yearly_outcomes(df)
    mtbf_df = prepare_mtbf(df)

    # Compute editorial summary numbers from data (never hardcoded)
    total = len(df)
    n_success = (df["launch_status_abbrev"] == "Success").sum()
    overall_rate = n_success / total * 100
    n_failures = len(failures)

    failure_dates = failures["net"].sort_values().reset_index(drop=True)
    first_failure_year = int(failure_dates.iloc[0].year)
    last_failure_year = int(failure_dates.iloc[-1].year)
    last_gap_days = (failure_dates.iloc[-1] - failure_dates.iloc[-2]).days if len(failure_dates) >= 2 else 0
    first_gap_days = (failure_dates.iloc[1] - failure_dates.iloc[0]).days if len(failure_dates) >= 2 else 0
    launches_since_last = len(df[df["net"] > failure_dates.iloc[-1]])

    print("=" * 60)
    print("CHART SELECTION — Kirk Ch 7: Data Representation")
    print("=" * 60)
    print()
    print("Curiosity question:")
    print("  What does SpaceX's failure timeline reveal about how rapidly")
    print("  a launch provider builds — and sustains — operational reliability?")
    print()
    print(f"Dataset: {total} completed launches, {n_failures} failures/partial failures")
    print(f"  Overall success rate: {overall_rate:.1f}%")
    print(f"  Failure date range: {first_failure_year}–{last_failure_year}")
    print()
    print("Evaluating 4 chart candidates (all unstyled — chart TYPE only)...")
    print()

    # --- Render all candidates ---
    chart_candidate_failure_timeline(failures)
    print("  Candidate 1 (Failure Timeline Scatter): Every failure event as a point.")
    print(f"  {n_failures} points. Clustering in {first_failure_year}–2016 vs. sparsity since 2016 is immediate.")
    print()

    chart_candidate_cumulative_success(df_cumulative)
    print("  Candidate 2 (Cumulative Success Rate Line): Running success rate launch-by-launch.")
    print(f"  Shows the growth curve shape from volatile early to stable {overall_rate:.1f}%.")
    print()

    chart_candidate_yearly_stacked(yearly)
    print("  Candidate 3 (Yearly Stacked Bar): Outcomes aggregated by year.")
    print("  Failure slivers become invisible against high-cadence success bars.")
    print()

    chart_candidate_mtbf(mtbf_df)
    print("  Candidate 4 (Time-Between-Failures Bar): Days between consecutive failures.")
    print(f"  Only {len(mtbf_df)} intervals. Loses temporal calendar context.")
    print()

    # --- Final selection ---
    print("=" * 60)
    print("WINNER:    Candidate 1 (failure timeline scatter) as PRIMARY")
    print("SECONDARY: Candidate 2 (cumulative success rate) as SUPPORTING")
    print("=" * 60)
    print(f"""
WHY CANDIDATE 1 (FAILURE TIMELINE SCATTER) WINS:

1. DIRECTNESS: The curiosity question asks about the *failure timeline* —
   a scatter of failure events on a timeline IS the direct answer. No
   aggregation, no smoothing, every failure event is an identifiable point
   you can hover over and name.

2. PERCEPTUAL ACCURACY: Kirk Ch 7 cites Cleveland & McGill (1984): position
   along a common scale is the most accurately perceived visual channel.
   Each point's x-position encodes its date precisely. Readers do not have
   to estimate bar heights or interpret slopes.

3. VISCERAL IMPACT: The early cluster ({first_failure_year}–2016) vs. the
   modern sparsity (post-2016) is visible in under 2 seconds. The growing
   gaps between events show MTBF growth without any derivation — you see
   it directly in the whitespace between points.

4. INDIVIDUAL LEGIBILITY: With only {n_failures} failure events total, every
   one of them can be labelled or hovered. In stacked bars or line charts,
   individual failures are anonymous — they disappear into the aggregate.

5. ANSWERS THE QUESTION: The question is about lifecycle phases and how
   reliability was built. Three clusters are immediately visible:
   Falcon 1 era, early Falcon 9 era, Starship era. The chart tells the
   three-act story without a single annotation.

WHY CANDIDATE 2 (CUMULATIVE SUCCESS RATE) AS SECONDARY:

The cumulative success rate line shows something the scatter cannot:
the *shape* of the reliability growth curve. The volatile early period
(where every failure meaningfully drops the rate) vs. the later period
(where the rate is so high that a failure barely moves the needle) is
a story about statistical credibility — exactly the insurance domain
transfer. It is the Duane reliability growth model visualised. It
complements the scatter rather than competing with it.

REJECTED:

- Candidate 3 (Yearly Stacked Bar): Designed for volume stories, not
  reliability stories. In a year with 50+ launches, a single failure is
  a sliver < 2% of bar height. The failure signal — the very thing we
  are studying — becomes invisible. The chart is excellent for launch
  cadence analysis (see launch_cadence/tutorial_002.py) but wrong here.

- Candidate 4 (Time-Between-Failures Bar): Intellectually interesting
  (MTBF is a legitimate reliability metric) but the derivation destroys
  temporal context. The x-axis labels are failure-pair dates, not calendar
  time. The gap-growth story ({first_gap_days} days between the first two
  failures vs. {last_gap_days} days before the most recent) is already
  implied by the scatter's whitespace — and the scatter tells it with
  far less cognitive load.
""")


if __name__ == "__main__":
    main()
