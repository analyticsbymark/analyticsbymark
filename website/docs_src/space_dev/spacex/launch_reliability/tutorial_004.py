"""
What You'll Learn
=================
- Kirk Chapter 9: Annotation — titles, labels, legends, footnotes, and
  direct annotation of data points
- The difference between LABELING (what is it?) and ANNOTATING (what should
  I notice?) — shown as a before/after comparison
- How to select 2-3 strategic callouts rather than annotating every point
- How to compute ALL annotation values from data — never hardcoded
- How to stagger text labels to prevent collision on a narrow 2-category y-axis
- How to build an editorial title that carries the story
- Output: Labels-only image vs. fully-annotated image of the failure timeline
"""

import sys
from pathlib import Path

# Ensure the parent directory is on the path so `from data.utils import ...`
# works when this script is run directly from the launch_reliability/ folder.
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

# Status labels treated as non-successes for reliability analysis
FAILURE_STATUSES = {"Failure", "Partial Failure"}

# Rocket family color palette — carried forward from tutorial_003.
# Kirk Ch 9: Annotation and color work together; keep the palette consistent
# so readers who read sequentially aren't confused by new colors appearing.
ROCKET_FAMILY_COLORS = {
    "Falcon 1": "#C0392B",   # Muted red — development era volatility
    "Falcon 9": "#2980B9",   # Steel blue — operational maturity
    "Starship": "#D4A017",   # Amber/gold — new vehicle development era
}

# Mapping rocket full names to the three families.
ROCKET_FAMILY_MAP = {
    "Falcon 1": "Falcon 1",
    "Falcon 9 v1.0": "Falcon 9",
    "Falcon 9 v1.1": "Falcon 9",
    "Falcon 9 Full Thrust": "Falcon 9",
    "Falcon 9 Block 5": "Falcon 9",
    "Starship Prototype": "Starship",
    "Starship V1": "Starship",
    "Starship V2": "Starship",
}

# Lifecycle order for legend and category_orders — chronological, not
# alphabetical. Kirk Ch 9: Legends should reinforce narrative structure.
LIFECYCLE_ORDER = ["Falcon 1", "Falcon 9", "Starship"]

# Chart dimensions — wide and short; the y-axis has only 2 categories so
# height should be compact to avoid excessive whitespace.
# Extra width gives the temporal axis more room to spread dense clusters.
CHART_WIDTH = 1400
CHART_HEIGHT = 560

# Source attribution text
SOURCE_TEXT = "Source: Launch Library 2 API | thespacedevs.com"


# ---------------------------------------------------------------------------
# Data loading and preparation
# ---------------------------------------------------------------------------
def load_and_filter() -> pd.DataFrame:
    """Load SpaceX data and filter to completed launches only.

    Completed launches have a definitive outcome: Success, Failure, or
    Partial Failure. Future/planned launches are excluded because they have
    no outcome to record.

    Kirk Ch 4: Always know your data before you visualise it.
    """
    df = get_spacex_data()
    completed = df[
        df["launch_status_abbrev"].isin(["Success", "Failure", "Partial Failure"])
    ].copy()
    # Sort chronologically — essential for timeline charts and gap computation
    completed = completed.sort_values("net").reset_index(drop=True)
    return completed


def prepare_failures(df: pd.DataFrame) -> pd.DataFrame:
    """Extract failure and partial failure events and assign rocket families.

    The rocket family assignment groups variants into a single family label.
    Any rocket_full_name not in ROCKET_FAMILY_MAP falls back to the value
    itself, so new vehicles are visible rather than silently dropped.

    Kirk Ch 9: Annotation works on the data you've prepared — if the
    groupings are wrong, callouts will point to the wrong things.
    """
    failures = df[df["launch_status_abbrev"].isin(FAILURE_STATUSES)].copy()
    failures["rocket_family_group"] = (
        failures["rocket_full_name"]
        .map(ROCKET_FAMILY_MAP)
        .fillna(failures["rocket_full_name"])
    )
    return failures


# ---------------------------------------------------------------------------
# Annotation insight computation
# ---------------------------------------------------------------------------
def compute_annotation_insights(
    df: pd.DataFrame, failures: pd.DataFrame
) -> dict:
    """Compute all strategic annotation values from data — never hardcoded.

    Kirk Ch 9: 'Annotations that are wrong destroy trust faster than no
    annotation at all.' Computing from data ensures accuracy even if the
    underlying dataset is refreshed.

    Returns a dict with keys that are used by both image functions so the
    same computed values appear identically in both outputs.
    """
    total_launches = len(df)
    total_failures = len(failures)

    # --- Compute the key insight: Falcon 9 Block 5's consecutive failure-free
    #     run. The Starship and Falcon 9 programs overlapped chronologically,
    #     so we cannot use Starship's first failure to define the gap.
    #
    #     The correct gap is WITHIN Falcon 9: from Amos-6 (Sep 2016, the last
    #     pre-Block-5 failure) to Starlink Group 9-3 (Jul 2024, the first
    #     failure after Block 5 was introduced). This ~2,869-day run is
    #     Falcon 9 Block 5's extraordinary consecutive-flights-without-failure
    #     record and is the KEY insight of the reliability story.
    f9_failures = failures[failures["rocket_family_group"] == "Falcon 9"].sort_values("net")
    starship_failures = failures[failures["rocket_family_group"] == "Starship"].sort_values("net")
    f9_sorted = f9_failures.reset_index(drop=True)

    # CRS-7 / Amos-6 cluster: look up by name for robustness
    crs7_row = None
    amos6_row = None
    for _, row in f9_failures.iterrows():
        name_lower = str(row["mission_name"]).lower()
        if "crs-7" in name_lower or "crs 7" in name_lower or "spx crs-7" in name_lower:
            crs7_row = row
        if "amos" in name_lower and "6" in name_lower:
            amos6_row = row

    # Identify Amos-6: the end of the pre-Block-5 era and start of the gap.
    # If not found by name, use the 2nd-most-recent Falcon 9 failure
    # (the second-to-last in time, since the last is the streak breaker).
    if amos6_row is None:
        amos6_row = f9_sorted.iloc[-2] if len(f9_sorted) >= 2 else f9_sorted.iloc[-1]

    # Identify the streak-ending failure: the Falcon 9 failure AFTER Amos-6.
    # Chronologically this is the LAST Falcon 9 failure in the dataset.
    streak_end_row = f9_sorted.iloc[-1]

    # Gap: from Amos-6 to the streak-ending Falcon 9 failure
    gap_start = amos6_row["net"]
    gap_end = streak_end_row["net"]
    gap_days = (gap_end - gap_start).days
    gap_years = gap_days / 365.25

    # Compute gap mid for annotation placement
    gap_mid = pd.Timestamp(
        (gap_start.value + gap_end.value) // 2,
        unit="ns",
        tz="UTC",
    )

    # CRS-7 fallback: if not found by name, use the 3rd Falcon 9 failure
    # (the one just before Amos-6 in chronological order)
    if crs7_row is None and len(f9_sorted) >= 3:
        crs7_row = f9_sorted.iloc[-3]

    # Cluster annotation: CRS-7 and Amos-6 together as the pivot point
    if crs7_row is not None and amos6_row is not None:
        cluster_mid_date = pd.Timestamp(
            (crs7_row["net"].value + amos6_row["net"].value) // 2,
            unit="ns",
            tz="UTC",
        )
        cluster_label = f"{crs7_row['mission_name']} & {amos6_row['mission_name']}"
    else:
        cluster_mid_date = amos6_row["net"]
        cluster_label = amos6_row["mission_name"]

    # --- Falcon 1 cluster: the three development-era failures (2006-2008)
    f1_failures = failures[failures["rocket_family_group"] == "Falcon 1"].sort_values("net")
    f1_date_range = (
        f1_failures["net"].min(),
        f1_failures["net"].max(),
    )
    f1_mid_date = f1_failures["net"].mean()

    # --- Date range of all completed launches for subtitle
    date_min = df["net"].min()
    date_max = df["net"].max()

    return {
        "total_launches": total_launches,
        "total_failures": total_failures,
        "f9_last_failure": streak_end_row["net"],
        "f9_last_failure_name": streak_end_row["mission_name"],
        "amos6_row": amos6_row,
        "streak_end_row": streak_end_row,
        "gap_start": gap_start,
        "gap_end": gap_end,
        "gap_mid": gap_mid,
        "gap_days": gap_days,
        "gap_years": gap_years,
        "cluster_mid_date": cluster_mid_date,
        "cluster_label": cluster_label,
        "crs7_row": crs7_row,
        "f9_sorted": f9_sorted,
        "f1_mid_date": f1_mid_date,
        "f1_date_range": f1_date_range,
        "f1_count": len(f1_failures),
        "date_min": date_min,
        "date_max": date_max,
    }


# ---------------------------------------------------------------------------
# Shared chart base builder
# ---------------------------------------------------------------------------
def build_base_figure(failures: pd.DataFrame) -> go.Figure:
    """Build the colored failure timeline scatter as a Plotly Figure object.

    This is the shared foundation for both output images. Image 01 adds
    mission name labels; Image 02 adds editorial annotations on top.

    Kirk Ch 9: The chart frame must be solid before adding annotation.
    Annotations that correct for a weak chart are band-aids; annotations
    that amplify a strong chart are journalism.
    """
    fig = px.scatter(
        failures,
        x="net",
        y="launch_status_abbrev",
        color="rocket_family_group",
        hover_name="mission_name",
        hover_data={
            "rocket_full_name": True,
            "net": True,
            "launch_status_abbrev": True,
            "rocket_family_group": False,
        },
        labels={
            "net": "Launch Date",
            "launch_status_abbrev": "Outcome",
            "rocket_full_name": "Rocket Variant",
            "rocket_family_group": "Rocket Family",
        },
        color_discrete_map=ROCKET_FAMILY_COLORS,
        category_orders={"rocket_family_group": LIFECYCLE_ORDER},
    )

    fig.update_layout(
        width=CHART_WIDTH,
        height=CHART_HEIGHT,
        xaxis_title="Launch Date",
        yaxis_title="Outcome",
        # Kirk Ch 9: Move legend to top so it doesn't compete with x-axis
        # timeline or annotations placed along the bottom of the plot.
        legend=dict(
            title="Rocket Family",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1.0,
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=80, r=120, t=160, b=120),
        font=dict(family="Arial, sans-serif", size=12, color="#333333"),
        xaxis=dict(
            showgrid=True,
            gridcolor="#E8E8E8",
            gridwidth=1,
            zeroline=False,
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
        ),
    )
    fig.update_traces(marker=dict(size=13))
    return fig


# ---------------------------------------------------------------------------
# Image 01 — Labels only (what is it?)
# ---------------------------------------------------------------------------
def scatter_labels_only(failures: pd.DataFrame, insights: dict) -> None:
    """Failure timeline scatter with mission name labels on every point.

    Kirk Ch 9: This is LABELING — answering 'what is this point?'. Labels
    tell the reader what each data point IS. They do not tell the reader
    what to NOTICE or why a point matters.

    With 15 points spread across 2 y-axis categories, naive label placement
    causes severe overlap. We stagger labels by alternating vertical offsets:
    - Points on the 'Failure' row alternate between ay=-30 and ay=+35
    - Points on the 'Partial Failure' row alternate between ay=-30 and ay=+35
    - Further horizontal offset (ax) helps separate crowded clusters

    Kirk Ch 9: 'Even when every label is correct, visual clutter reduces
    comprehension. Staggering and offsetting are craft, not cosmetics.'
    """
    fig = build_base_figure(failures)

    # Kirk Ch 9: Provide a descriptive (not editorial) title for the
    # labels-only version. The title tells you what the chart shows;
    # it does NOT interpret it. That is the job of the annotated version.
    n_f = insights["total_failures"]
    n_t = insights["total_launches"]
    fig.update_layout(
        title=dict(
            text=(
                f"SpaceX Failure Timeline: All {n_f} Non-Successful Launches "
                f"({insights['date_min'].year}–{insights['date_max'].year})"
                f"<br><sup style='color:#666666; font-size:12px'>"
                f"Each point is one launch colored by rocket family. "
                f"Labels identify mission name — {n_t} total completed launches.</sup>"
            ),
            font=dict(size=16),
            x=0.0,
            xanchor="left",
        )
    )

    # --- Staggered label placement ---
    # Kirk Ch 9: With 15 points on a 2-category y-axis, collision avoidance
    # requires deliberately varied (ax, ay) offsets. The challenge is that
    # several points are extremely close in time (the Starship cluster near
    # 2020-2025), so simple alternating small offsets are insufficient.
    #
    # Strategy:
    #   1. Sort failures chronologically within each y-category.
    #   2. Assign ay alternating above/below so consecutive labels in time
    #      never both point the same direction.
    #   3. Assign ax by spreading within dense temporal clusters: compute
    #      rank within a 365-day proximity group and fan outward from center.
    #   4. 'Failure' row uses larger |ay| below (80) to clear the x-axis
    #      area; 'Partial Failure' uses larger |ay| above (-80) to clear
    #      the legend area.
    failures_sorted = failures.sort_values("net").reset_index(drop=True)

    def get_label_offsets(
        subset: pd.DataFrame,
        ay_above: int,
        ay_below: int,
        ax_step: int = 50,
        proximity_days: int = 500,
    ) -> list[tuple[int, int]]:
        """Assign (ax, ay) offsets for a single y-category subset.

        Within each temporal cluster (points within proximity_days of each
        other), fan labels left-to-right with ax offsets so they spread
        horizontally. Alternate ay above/below across the full subset so
        temporally adjacent points point in opposite vertical directions.

        Args:
            subset: DataFrame rows for one y-category, sorted by net.
            ay_above: Negative pixel offset (label above the point).
            ay_below: Positive pixel offset (label below the point).
            ax_step: Horizontal pixel step between cluster members.
            proximity_days: Max days apart to treat points as clustered.

        Returns:
            List of (ax, ay) tuples, one per row in chronological order.
        """
        offsets: list[tuple[int, int]] = []
        subset = subset.sort_values("net").reset_index(drop=True)
        n = len(subset)

        # Identify cluster membership: group consecutive points where each
        # is within proximity_days of the next
        groups: list[list[int]] = []
        current_group: list[int] = [0]
        for i in range(1, n):
            diff = (subset.iloc[i]["net"] - subset.iloc[i - 1]["net"]).days
            if diff <= proximity_days:
                current_group.append(i)
            else:
                groups.append(current_group)
                current_group = [i]
        groups.append(current_group)

        # Assign offsets group by group
        result: dict[int, tuple[int, int]] = {}
        above_below_counter = 0  # global counter for alternating ay

        for group in groups:
            m = len(group)
            # Fan ax values symmetrically around 0 for this cluster
            if m == 1:
                ax_values = [0]
            elif m == 2:
                ax_values = [-ax_step // 2, ax_step // 2]
            else:
                # Spread evenly: e.g. 3 items → [-step, 0, +step]
                half = (m - 1) / 2.0
                ax_values = [int((i - half) * ax_step) for i in range(m)]

            for local_i, global_i in enumerate(group):
                ay = ay_above if above_below_counter % 2 == 0 else ay_below
                result[global_i] = (ax_values[local_i], ay)
                above_below_counter += 1

        for i in range(n):
            offsets.append(result[i])
        return offsets

    # Compute offsets separately per y-category.
    # 'Failure' row: labels go above (-55) or below (+70) the row.
    # 'Partial Failure' row: labels go above (-70) or below (+55).
    # We use larger offsets for the category with more crowding.
    failure_subset = failures_sorted[
        failures_sorted["launch_status_abbrev"] == "Failure"
    ].copy()
    partial_subset = failures_sorted[
        failures_sorted["launch_status_abbrev"] == "Partial Failure"
    ].copy()

    failure_offsets = get_label_offsets(
        failure_subset, ay_above=-55, ay_below=70, ax_step=55, proximity_days=500
    )
    partial_offsets = get_label_offsets(
        partial_subset, ay_above=-70, ay_below=55, ax_step=60, proximity_days=500
    )

    # Map offsets back to original row indices by mission name
    # (mission_name is our stable identifier within this filtered dataset)
    offset_map: dict[str, tuple[int, int]] = {}
    for i, (_, row) in enumerate(
        failure_subset.sort_values("net").iterrows()
    ):
        offset_map[str(row["mission_name"]) + "_Failure"] = failure_offsets[i]

    for i, (_, row) in enumerate(
        partial_subset.sort_values("net").iterrows()
    ):
        offset_map[str(row["mission_name"]) + "_Partial Failure"] = partial_offsets[i]

    for _, row in failures_sorted.iterrows():
        y_cat = row["launch_status_abbrev"]
        key = str(row["mission_name"]) + "_" + y_cat
        ax, ay = offset_map.get(key, (0, -45))

        fig.add_annotation(
            x=row["net"],
            y=y_cat,
            text=row["mission_name"],
            showarrow=True,
            arrowhead=2,
            arrowsize=0.8,
            arrowwidth=1,
            arrowcolor="#888888",
            ax=ax,
            ay=ay,
            font=dict(size=10, color="#333333"),
            bgcolor="rgba(255,255,255,0.82)",
            borderpad=2,
            standoff=6,
        )

    out = IMAGES_DIR / "tutorial_004_image_01_labels_only.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Image 02 — Fully annotated (what should I notice?)
# ---------------------------------------------------------------------------
def scatter_fully_annotated(failures: pd.DataFrame, insights: dict) -> None:
    """Failure timeline scatter with editorial title and strategic callouts.

    Kirk Ch 9: This is ANNOTATING — answering 'what matters here?'.
    We pick exactly 3 callouts that carry the full narrative:

      Callout 1 — The Falcon 1 cluster (2006-2008):
        Three failures in three flights. SpaceX's founding-era learning
        curve. Brief label: 'Development era: 3 failures in 3 flights'.

      Callout 2 — CRS-7 / Amos-6 (2015-2016):
        The last two Falcon 9 failures before Block 5. These pivotal events
        triggered the redesign that produced an extraordinary reliability run.

      Callout 3 — The reliability gap:
        The gap between Amos-6 (Sep 2016) and Starlink Group 9-3 (Jul 2024)
        — Falcon 9's consecutive-failure-free run of ~7.8 years. Note: the
        Starship and Falcon 9 programs overlapped, so the gap is defined
        within Falcon 9 only. Shown as a shaded vrect spanning the gap.

    Kirk Ch 9: 'Do not annotate every data point. Annotate the moments
    that change the meaning of everything else. Three well-chosen callouts
    outperform fifteen mediocre ones every time.'
    """
    fig = build_base_figure(failures)

    # --- Editorial title: computed counts, not hardcoded numbers ---
    n_f = insights["total_failures"]
    n_t = insights["total_launches"]
    gap_y = insights["gap_years"]
    gap_d = insights["gap_days"]

    editorial_title = (
        f"{n_f} Failures in {n_t} Launches: How SpaceX Built Reliability"
    )
    subtitle = (
        f"Each point is one failure/partial failure, colored by rocket family — "
        f"{insights['date_min'].year}–{insights['date_max'].year}"
    )

    fig.update_layout(
        title=dict(
            text=(
                f"{editorial_title}"
                f"<br><sup style='color:#555555; font-size:12px'>{subtitle}</sup>"
            ),
            font=dict(size=17, color="#111111"),
            x=0.0,
            xanchor="left",
        )
    )

    # -----------------------------------------------------------------------
    # Callout 1 — Falcon 1 development cluster
    # Kirk Ch 9: Use a single bracket/label to frame the whole cluster,
    # not individual arrows to each point. Three arrows to three adjacent
    # points is visual noise; one label frames the era.
    # -----------------------------------------------------------------------
    f1_start = insights["f1_date_range"][0]
    f1_end = insights["f1_date_range"][1]
    f1_mid = insights["f1_mid_date"]
    f1_count = insights["f1_count"]

    # Annotation placed above the 'Failure' row (Falcon 1 events are all
    # 'Failure', not 'Partial Failure').
    fig.add_annotation(
        x=f1_mid,
        y="Failure",
        text=(
            f"<b>Development era</b><br>"
            f"{f1_count} failures in first {f1_count} flights<br>"
            f"({f1_start.year}–{f1_end.year})"
        ),
        showarrow=True,
        arrowhead=2,
        arrowsize=1.0,
        arrowwidth=1.5,
        arrowcolor=ROCKET_FAMILY_COLORS["Falcon 1"],
        ax=0,
        ay=-75,
        font=dict(size=11, color=ROCKET_FAMILY_COLORS["Falcon 1"]),
        bgcolor="rgba(255,255,255,0.90)",
        bordercolor=ROCKET_FAMILY_COLORS["Falcon 1"],
        borderwidth=1.2,
        borderpad=5,
        align="center",
        standoff=8,
    )

    # -----------------------------------------------------------------------
    # Callout 2 — CRS-7 / Amos-6 pivotal cluster
    # Kirk Ch 9: Identify WHAT happened and WHY it matters. The annotation
    # should tell the reader something they could not read from the dots alone.
    # -----------------------------------------------------------------------
    if insights["crs7_row"] is not None and insights["amos6_row"] is not None:
        cluster_x = insights["cluster_mid_date"]
        cluster_names = insights["cluster_label"]
    else:
        cluster_x = insights["cluster_mid_date"]
        cluster_names = insights["cluster_label"]

    # Place below the 'Failure' row so it doesn't compete with Callout 1
    fig.add_annotation(
        x=cluster_x,
        y="Failure",
        text=(
            f"<b>Pivot point</b><br>"
            f"{cluster_names}<br>"
            f"Failures that triggered<br>the Block 5 redesign"
        ),
        showarrow=True,
        arrowhead=2,
        arrowsize=1.0,
        arrowwidth=1.5,
        arrowcolor=ROCKET_FAMILY_COLORS["Falcon 9"],
        ax=0,
        ay=80,
        font=dict(size=11, color=ROCKET_FAMILY_COLORS["Falcon 9"]),
        bgcolor="rgba(255,255,255,0.90)",
        bordercolor=ROCKET_FAMILY_COLORS["Falcon 9"],
        borderwidth=1.2,
        borderpad=5,
        align="center",
        standoff=8,
    )

    # -----------------------------------------------------------------------
    # Callout 3 — The reliability gap (KEY INSIGHT)
    # Kirk Ch 9: This is the most important annotation on the chart.
    # The gap is INVISIBLE without annotation — it is the ABSENCE of dots.
    # A text callout in the whitespace makes the gap legible as data.
    #
    # The gap is defined WITHIN Falcon 9 only: from Amos-6 (Sep 2016) to
    # Starlink Group 9-3 (Jul 2024). The Starship and Falcon 9 programs
    # overlapped, so we cannot use Starship's first failure as the gap end.
    # -----------------------------------------------------------------------
    gap_start = insights["gap_start"]
    gap_end = insights["gap_end"]
    gap_mid = insights["gap_mid"]

    # Shape: a shaded rectangle spanning the gap period
    fig.add_vrect(
        x0=gap_start,
        x1=gap_end,
        fillcolor="rgba(41, 128, 185, 0.07)",  # very light steel blue
        line_width=0,
        layer="below",
    )

    # Vertical dashed lines at the gap boundaries for precision
    for gap_boundary in [gap_start, gap_end]:
        fig.add_shape(
            type="line",
            x0=gap_boundary,
            x1=gap_boundary,
            y0=0,
            y1=1,
            yref="paper",
            line=dict(color="#2980B9", width=1, dash="dot"),
        )

    # Text annotation in the middle of the gap, placed at the top of the
    # chart area (yref="paper") so it doesn't overlap with any data points.
    fig.add_annotation(
        x=gap_mid,
        y=1.0,
        yref="paper",
        text=(
            f"<b>Falcon 9 Block 5: {gap_d:,} days without a failure</b><br>"
            f"({gap_y:.1f} years — {gap_start.strftime('%b %Y')} to {gap_end.strftime('%b %Y')})"
        ),
        showarrow=False,
        font=dict(size=12, color="#2980B9"),
        bgcolor="rgba(255,255,255,0.92)",
        bordercolor="#2980B9",
        borderwidth=1.5,
        borderpad=6,
        align="center",
        yanchor="top",
        xanchor="center",
    )

    # -----------------------------------------------------------------------
    # Source attribution — Kirk Ch 9: Footnotes establish credibility.
    # Placed at the bottom-right, small but readable (min 9pt).
    # -----------------------------------------------------------------------
    fig.add_annotation(
        text=SOURCE_TEXT,
        xref="paper",
        yref="paper",
        x=1.0,
        y=-0.15,
        showarrow=False,
        font=dict(size=9, color="#888888"),
        xanchor="right",
        yanchor="bottom",
    )

    out = IMAGES_DIR / "tutorial_004_image_02_fully_annotated.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Annotation decisions summary printer
# ---------------------------------------------------------------------------
def print_annotation_decisions(failures: pd.DataFrame, insights: dict) -> None:
    """Print a structured summary of annotation decisions made.

    Kirk Ch 9: Annotation decisions are editorial choices. Being explicit
    about WHY each annotation exists and WHY others were omitted is as
    important as the annotation text itself. This is the audit trail.
    """
    n_f = insights["total_failures"]
    n_t = insights["total_launches"]
    gap_d = insights["gap_days"]
    gap_y = insights["gap_years"]
    gap_start = insights["gap_start"]
    gap_end = insights["gap_end"]

    print()
    print("=" * 65)
    print("ANNOTATION DECISIONS SUMMARY — Kirk Ch 9: Annotation")
    print("=" * 65)

    print(f"""
CHART: Failure timeline scatter — {n_f} failure/partial failure events
       from {n_t} total completed SpaceX launches
       Date range: {insights['date_min'].year}–{insights['date_max'].year}

IMAGE 01 — LABELS ONLY (what is it?)
  Every data point labeled with its mission name.
  Purpose: Shows the reader WHAT each point represents.
  Problem this image illustrates: With {n_f} points on 2 y-categories,
  naive same-direction placement causes severe overlap. Staggering
  is required craft, not an afterthought.
  Stagger technique: alternating (ax, ay) offsets per y-category,
  cycling through 8 positions so adjacent points diverge.

IMAGE 02 — FULLY ANNOTATED (what should I notice?)
  EDITORIAL TITLE computed from data:
    "{n_f} Failures in {n_t} Launches: How SpaceX Built Reliability"
  → Numbers are live: they update if the dataset is refreshed.
  → The title carries the thesis, not just a description.

  CALLOUT 1 — Falcon 1 development cluster
    What: {insights['f1_count']} failures across first {insights['f1_count']} flights,
          {insights['f1_date_range'][0].year}–{insights['f1_date_range'][1].year}
    Why annotate: Frames the 'before' state. Without this anchor,
    readers may not understand that SpaceX started from zero.
    Decision: One label for the whole cluster, not 3 individual arrows.
    Three arrows to three adjacent red points creates visual noise;
    one bracket-style callout frames the era cleanly.

  CALLOUT 2 — CRS-7 / Amos-6 pivot cluster
    What: {insights['cluster_label']}
    Why annotate: These two failures are the turning point. They
    triggered the Block 5 redesign. Without this annotation, a reader
    sees a gap after 2016 but does not know WHY the gap began.
    Decision: Placed BELOW the row to avoid competing with Callout 1.

  CALLOUT 3 — The Falcon 9 Block 5 reliability gap (KEY INSIGHT)
    What: {gap_d:,} days ({gap_y:.1f} years) of consecutive Falcon 9 flights
          without a failure — within the Falcon 9 program only.
    From: {gap_start.strftime('%b %Y')} ({insights['amos6_row']['mission_name']}) to
          {gap_end.strftime('%b %Y')} ({insights['streak_end_row']['mission_name']})
    Note: Starship and Falcon 9 programs overlapped chronologically
    (Starship failures 2020-2025 while Falcon 9 ran clean 2016-2024).
    The gap is correctly measured within Falcon 9, not between programs.
    Why annotate: The gap is whitespace — INVISIBLE without annotation.
    Color alone cannot show the absence of dots. Only annotation makes
    the Falcon 9 Block 5 streak legible as the central data story.
    Technique: Shaded vrect + dashed boundary lines + text at chart top.

  NOT ANNOTATED (and why):
    - Individual Starship events: The Starship cluster tells its own
      story through color (amber) and density. Annotating each point
      would recreate the labeling problem Image 01 demonstrates.
    - Every Falcon 9 failure individually: Only the cluster matters;
      individual mission names are available on hover.
    - Success rate percentage: This is covered by tutorial_001/002.
      This chart's thesis is about the GAP, not the rate.

  SOURCE: {SOURCE_TEXT}
    Placed bottom-right at 9pt — credible but unobtrusive.
""")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    """Run the annotation tutorial for the failure timeline scatter.

    Kirk Ch 9: 'Annotation is not decoration — it is the author's voice
    inside the chart. Used well, it guides the reader to the insight.
    Used poorly, it clutters the canvas and creates confusion.'

    This tutorial takes the colored chart from tutorial_003 and adds
    two annotation layers:
      Image 01: Labels only — mission names on every point (labeling)
      Image 02: Strategic callouts — 3 editorial annotations (annotating)

    The contrast between Image 01 and Image 02 IS the lesson.
    """
    print("=" * 65)
    print("ANNOTATION TUTORIAL — Kirk Ch 9: Annotation")
    print("=" * 65)
    print()
    print("Curiosity question:")
    print("  What does SpaceX's failure timeline reveal about how rapidly")
    print("  a launch provider builds — and sustains — operational reliability?")
    print()

    # --- Load data ---
    print("Loading data...")
    df = load_and_filter()
    failures = prepare_failures(df)
    print(f"  {len(df)} completed launches loaded")
    print(f"  {len(failures)} failure/partial failure events")
    print()

    # --- Compute all annotation values from data ---
    print("Computing annotation insights from data...")
    insights = compute_annotation_insights(df, failures)
    print(f"  Amos-6 (gap start):          {insights['gap_start'].strftime('%Y-%m-%d')}")
    print(f"  Starlink 9-3 (gap end):      {insights['gap_end'].strftime('%Y-%m-%d')}")
    print(f"  Gap (Falcon 9 Block 5 run):  {insights['gap_days']:,} days ({insights['gap_years']:.1f} years)")
    print(f"  Pivot cluster:               {insights['cluster_label']}")
    print(f"  Falcon 1 cluster:            {insights['f1_count']} events, {insights['f1_date_range'][0].year}–{insights['f1_date_range'][1].year}")
    print()

    # --- Image 01: Labels only ---
    print("Image 01 — Labels only (what is it?):")
    scatter_labels_only(failures, insights)
    print("  Every mission name labeled, staggered to prevent overlap.")
    print()

    # --- Image 02: Fully annotated ---
    print("Image 02 — Fully annotated (what should I notice?):")
    scatter_fully_annotated(failures, insights)
    print("  Editorial title + 3 strategic callouts + source attribution.")
    print()

    # --- Print annotation decisions ---
    print_annotation_decisions(failures, insights)


if __name__ == "__main__":
    main()
