"""
SpaceX Launch Reliability — Final Composition
==============================================

Production-ready visualisation answering the curiosity question:
"What does SpaceX's failure timeline reveal about how rapidly a launch
provider builds — and sustains — operational reliability?"

Produces one polished chart:
  1. Failure timeline scatter — every failure/partial failure event as a
     point on a horizontal timeline, colored by rocket family, with three
     strategic editorial annotations that carry the full reliability narrative.

Best decisions carried forward:
  - Ch 4:  Working with Data — filter to completed launches (tutorial_001)
  - Ch 7:  Data Representation — scatter is the direct answer (tutorial_002)
  - Ch 10: Color — qualitative palette by rocket family lifecycle (tutorial_003)
  - Ch 9:  Annotation — editorial title, 3 strategic callouts, source (tutorial_004)
  - Ch 11: Composition — layout, hierarchy, cohesion (this file)
  - Ch 6:  Design Solutions — the complete, considered output

Run with: python tutorial_final.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data.utils import get_spacex_data

IMAGES_DIR = Path(__file__).resolve().parent / "images"
IMAGES_DIR.mkdir(exist_ok=True)

FAILURE_STATUSES = {"Failure", "Partial Failure"}

ROCKET_FAMILY_COLORS = {
    "Falcon 1": "#C0392B",
    "Falcon 9": "#2980B9",
    "Starship": "#D4A017",
}

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

LIFECYCLE_ORDER = ["Falcon 1", "Falcon 9", "Starship"]

SOURCE_TEXT = "Source: Launch Library 2 API | thespacedevs.com"

CHART_WIDTH = 1400
CHART_HEIGHT = 560


def load_data() -> pd.DataFrame:
    """Load SpaceX launches filtered to completed outcomes only.

    Completed launches have a definitive outcome: Success, Failure, or
    Partial Failure. Future and planned launches are excluded because their
    dates may be placeholders and they have no recorded outcome.
    """
    df = get_spacex_data()
    completed = df[
        df["launch_status_abbrev"].isin(["Success", "Failure", "Partial Failure"])
    ].copy()
    return completed.sort_values("net").reset_index(drop=True)


def prepare_failures(df: pd.DataFrame) -> pd.DataFrame:
    """Extract failure events and assign each to a rocket family group.

    Any rocket_full_name not present in ROCKET_FAMILY_MAP falls back to
    the full name itself, so new vehicles surface rather than being dropped.
    """
    failures = df[df["launch_status_abbrev"].isin(FAILURE_STATUSES)].copy()
    failures["rocket_family_group"] = (
        failures["rocket_full_name"]
        .map(ROCKET_FAMILY_MAP)
        .fillna(failures["rocket_full_name"])
    )
    return failures


def compute_insights(df: pd.DataFrame, failures: pd.DataFrame) -> dict:
    """Compute all annotation values from data — nothing hardcoded.

    The Falcon 9 Block 5 reliability gap is measured WITHIN Falcon 9 only
    (Amos-6 Sep 2016 to Starlink Group 9-3 Jul 2024), because the Starship
    and Falcon 9 programs overlapped chronologically. Using Starship's first
    failure as the gap boundary would mis-measure the Falcon 9 streak.
    """
    f9_failures = (
        failures[failures["rocket_family_group"] == "Falcon 9"]
        .sort_values("net")
        .reset_index(drop=True)
    )
    f1_failures = (
        failures[failures["rocket_family_group"] == "Falcon 1"]
        .sort_values("net")
        .reset_index(drop=True)
    )

    amos6_row = None
    crs7_row = None
    for _, row in f9_failures.iterrows():
        name_lower = str(row["mission_name"]).lower()
        if "amos" in name_lower and "6" in name_lower:
            amos6_row = row
        if "crs-7" in name_lower or "crs 7" in name_lower or "spx crs-7" in name_lower:
            crs7_row = row

    if amos6_row is None:
        amos6_row = f9_failures.iloc[-2] if len(f9_failures) >= 2 else f9_failures.iloc[-1]
    if crs7_row is None and len(f9_failures) >= 3:
        crs7_row = f9_failures.iloc[-3]

    streak_end_row = f9_failures.iloc[-1]
    gap_start = amos6_row["net"]
    gap_end = streak_end_row["net"]
    gap_days = (gap_end - gap_start).days
    gap_years = gap_days / 365.25

    gap_mid = pd.Timestamp(
        (gap_start.value + gap_end.value) // 2,
        unit="ns",
        tz="UTC",
    )

    if crs7_row is not None:
        cluster_mid = pd.Timestamp(
            (crs7_row["net"].value + amos6_row["net"].value) // 2,
            unit="ns",
            tz="UTC",
        )
        cluster_label = f"{crs7_row['mission_name']} & {amos6_row['mission_name']}"
    else:
        cluster_mid = amos6_row["net"]
        cluster_label = amos6_row["mission_name"]

    return {
        "total_launches": len(df),
        "total_failures": len(failures),
        "date_min": df["net"].min(),
        "date_max": df["net"].max(),
        "f1_count": len(f1_failures),
        "f1_mid": f1_failures["net"].mean(),
        "f1_year_start": int(f1_failures["net"].min().year),
        "f1_year_end": int(f1_failures["net"].max().year),
        "cluster_mid": cluster_mid,
        "cluster_label": cluster_label,
        "gap_start": gap_start,
        "gap_end": gap_end,
        "gap_mid": gap_mid,
        "gap_days": gap_days,
        "gap_years": gap_years,
        "amos6_name": amos6_row["mission_name"],
        "streak_end_name": streak_end_row["mission_name"],
    }


def build_figure(failures: pd.DataFrame, insights: dict) -> go.Figure:
    """Build the fully annotated failure timeline scatter.

    Kirk Ch 11: The layout decisions in order of priority:
      1. Title and subtitle at top-left — editorial statement first
      2. Legend horizontal at top-right — labeling without competing
      3. Three strategic callouts — each in a distinct visual zone
      4. Source attribution bottom-right — credible and unobtrusive
      5. White background, vertical gridlines only, compact height
    """
    n_f = insights["total_failures"]
    n_t = insights["total_launches"]
    gap_d = insights["gap_days"]
    gap_y = insights["gap_years"]

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

    fig.update_traces(marker=dict(size=13))

    fig.update_layout(
        width=CHART_WIDTH,
        height=CHART_HEIGHT,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Arial, sans-serif", size=12, color="#333333"),
        margin=dict(l=80, r=120, t=170, b=120),
        title=dict(
            text=(
                f"{n_f} Failures in {n_t} Launches: How SpaceX Built Reliability"
                f"<br><sup style='color:#555555; font-size:12px'>"
                f"Each point is one failure or partial failure, colored by rocket family — "
                f"{insights['date_min'].year}–{insights['date_max'].year}"
                f"</sup>"
            ),
            font=dict(size=17, color="#111111"),
            x=0.0,
            xanchor="left",
        ),
        legend=dict(
            title="Rocket Family",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1.0,
            font=dict(size=11),
        ),
        xaxis=dict(
            title="Launch Date",
            showgrid=True,
            gridcolor="#E8E8E8",
            gridwidth=1,
            zeroline=False,
        ),
        yaxis=dict(
            title="Outcome",
            showgrid=False,
            zeroline=False,
        ),
    )

    f1_mid = insights["f1_mid"]
    f1_count = insights["f1_count"]
    f1_y_start = insights["f1_year_start"]
    f1_y_end = insights["f1_year_end"]

    fig.add_annotation(
        x=f1_mid,
        y="Failure",
        text=(
            f"<b>Development era</b><br>"
            f"{f1_count} failures in first {f1_count} flights<br>"
            f"({f1_y_start}–{f1_y_end})"
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

    fig.add_annotation(
        x=insights["cluster_mid"],
        y="Failure",
        text=(
            f"<b>Pivot point</b><br>"
            f"{insights['cluster_label']}<br>"
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

    gap_start = insights["gap_start"]
    gap_end = insights["gap_end"]
    gap_mid = insights["gap_mid"]

    fig.add_vrect(
        x0=gap_start,
        x1=gap_end,
        fillcolor="rgba(41, 128, 185, 0.07)",
        line_width=0,
        layer="below",
    )

    for boundary in [gap_start, gap_end]:
        fig.add_shape(
            type="line",
            x0=boundary,
            x1=boundary,
            y0=0,
            y1=1,
            yref="paper",
            line=dict(color="#2980B9", width=1, dash="dot"),
        )

    fig.add_annotation(
        x=gap_mid,
        y=1.0,
        yref="paper",
        text=(
            f"<b>Falcon 9 Block 5: {gap_d:,} days without a failure</b><br>"
            f"({gap_y:.1f} years — "
            f"{gap_start.strftime('%b %Y')} to {gap_end.strftime('%b %Y')})"
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

    return fig


def main() -> None:
    """Generate the final composition for the launch reliability curiosity."""
    df = load_data()
    failures = prepare_failures(df)
    insights = compute_insights(df, failures)

    fig = build_figure(failures, insights)

    out = IMAGES_DIR / "tutorial_final_image_01_failure_timeline.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
