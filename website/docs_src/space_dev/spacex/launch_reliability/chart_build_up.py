"""
Chart Build-Up: Launch Reliability — Failure Timeline Scatter
=============================================================

A linear, step-by-step script that progressively builds the winning chart
from its rawest form to the polished tutorial_final composition.

Designed for video content recording: walk through each step, pausing at
each saved image to show the visual progression.

Run with: python chart_build_up.py
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


# ============================================================================
# Data loading — shared across all steps
# ============================================================================

df = get_spacex_data()
completed = df[
    df["launch_status_abbrev"].isin(["Success", "Failure", "Partial Failure"])
].copy()
completed = completed.sort_values("net").reset_index(drop=True)

FAILURE_STATUSES = {"Failure", "Partial Failure"}
failures = completed[completed["launch_status_abbrev"].isin(FAILURE_STATUSES)].copy()

# Rocket family mapping — groups variants into three lifecycle families
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

ROCKET_FAMILY_COLORS = {
    "Falcon 1": "#C0392B",
    "Falcon 9": "#2980B9",
    "Starship": "#D4A017",
}

LIFECYCLE_ORDER = ["Falcon 1", "Falcon 9", "Starship"]

SOURCE_TEXT = "Source: Launch Library 2 API | thespacedevs.com"

# Assign rocket family group to failures
failures["rocket_family_group"] = (
    failures["rocket_full_name"]
    .map(ROCKET_FAMILY_MAP)
    .fillna(failures["rocket_full_name"])
)

# Compute all annotation insights from data — never hardcoded
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

# Find CRS-7 and Amos-6 rows
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
gap_mid = pd.Timestamp((gap_start.value + gap_end.value) // 2, unit="ns", tz="UTC")

if crs7_row is not None:
    cluster_mid = pd.Timestamp(
        (crs7_row["net"].value + amos6_row["net"].value) // 2, unit="ns", tz="UTC"
    )
    cluster_label = f"{crs7_row['mission_name']} & {amos6_row['mission_name']}"
else:
    cluster_mid = amos6_row["net"]
    cluster_label = amos6_row["mission_name"]

n_total = len(completed)
n_failures = len(failures)
date_min_year = completed["net"].min().year
date_max_year = completed["net"].max().year
f1_count = len(f1_failures)
f1_year_start = int(f1_failures["net"].min().year)
f1_year_end = int(f1_failures["net"].max().year)
f1_mid_date = f1_failures["net"].mean()

CHART_WIDTH = 1400
CHART_HEIGHT = 560

print("=" * 65)
print("CHART BUILD-UP: Launch Reliability — Failure Timeline Scatter")
print("=" * 65)
print()


# === Step 1: Raw scatter — simplest possible chart (Kirk Ch 4, Ch 7) ========
#
# Kirk Ch 4: Know your data. Kirk Ch 7: Position along a common scale is
# the most accurately perceived visual channel (Cleveland & McGill, 1984).
#
# This is the rawest form of the winning chart: every failure event as a
# point on a horizontal timeline. Default Plotly colours, no styling,
# no editorial framing. The clustering of early failures vs. modern
# sparsity is already visible — the chart TYPE does the heavy lifting.

fig = px.scatter(
    failures,
    x="net",
    y="launch_status_abbrev",
    hover_name="mission_name",
    hover_data={"rocket_full_name": True, "net": True, "launch_status_abbrev": True},
    title="Failure Timeline Scatter — Raw",
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

fig.write_image(str(IMAGES_DIR / "build_up_step_01_raw_scatter.png"), scale=2)
print("Step 1 saved: raw scatter (default colours, no styling)")


# === Step 2: Colour by rocket family (Kirk Ch 10) ==========================
#
# Kirk Ch 10: "Use color to encode data, not to decorate."
# Switching from colour-by-outcome to colour-by-rocket-family makes the
# three-act lifecycle structure visible at a glance — without a single
# annotation. Qualitative palette: red (Falcon 1), steel blue (Falcon 9),
# amber (Starship). Three hues with distinct luminance for colorblind safety.

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
    title="Failure Timeline — Colour by Rocket Family",
    labels={
        "net": "Launch Date",
        "launch_status_abbrev": "Outcome",
        "rocket_full_name": "Rocket Variant",
        "rocket_family_group": "Rocket Family",
    },
    color_discrete_map=ROCKET_FAMILY_COLORS,
    category_orders={"rocket_family_group": LIFECYCLE_ORDER},
)
fig.update_traces(marker=dict(size=12))
fig.update_layout(
    width=1200,
    height=400,
    xaxis_title="Launch Date",
    yaxis_title="Outcome",
    legend_title_text="Rocket Family",
)

fig.write_image(str(IMAGES_DIR / "build_up_step_02_colour_by_family.png"), scale=2)
print("Step 2 saved: colour by rocket family (three-act structure visible)")


# === Step 3: Layout polish (Kirk Ch 11) ====================================
#
# Kirk Ch 11: Composition — layout, hierarchy, margin, whitespace.
# White background removes visual noise. Vertical gridlines help read dates.
# Wider chart (1400px) gives the temporal axis room to spread dense clusters.
# Increased top margin reserves space for the editorial title coming next.

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
        text="Failure Timeline — Layout Polish",
        font=dict(size=17, color="#111111"),
        x=0.0,
        xanchor="left",
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
    legend_title_text="Rocket Family",
)

fig.write_image(str(IMAGES_DIR / "build_up_step_03_layout_polish.png"), scale=2)
print("Step 3 saved: layout polish (white bg, gridlines, margins, font)")


# === Step 4: Editorial title and subtitle (Kirk Ch 9) ======================
#
# Kirk Ch 9: "The title carries the thesis, not just a description."
# A descriptive title says "SpaceX Failure Timeline". An editorial title
# says "N Failures in M Launches: How SpaceX Built Reliability" — it tells
# the reader WHAT to take away. Subtitle gives context (date range, encoding).
# All numbers computed from data.

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
            f"{n_failures} Failures in {n_total} Launches: How SpaceX Built Reliability"
            f"<br><sup style='color:#555555; font-size:12px'>"
            f"Each point is one failure or partial failure, colored by rocket family — "
            f"{date_min_year}–{date_max_year}"
            f"</sup>"
        ),
        font=dict(size=17, color="#111111"),
        x=0.0,
        xanchor="left",
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
    legend_title_text="Rocket Family",
)

fig.write_image(str(IMAGES_DIR / "build_up_step_04_editorial_title.png"), scale=2)
print("Step 4 saved: editorial title + subtitle (computed from data)")


# === Step 5: Horizontal legend (Kirk Ch 11) ================================
#
# Kirk Ch 11: The legend should reinforce narrative structure, not distract.
# Horizontal at top-right keeps it compact and lets the eye flow left-to-right
# in lifecycle order (Falcon 1 → Falcon 9 → Starship). Positioned just above
# the plot area so it doesn't compete with the title.

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
            f"{n_failures} Failures in {n_total} Launches: How SpaceX Built Reliability"
            f"<br><sup style='color:#555555; font-size:12px'>"
            f"Each point is one failure or partial failure, colored by rocket family — "
            f"{date_min_year}–{date_max_year}"
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

fig.write_image(str(IMAGES_DIR / "build_up_step_05_horizontal_legend.png"), scale=2)
print("Step 5 saved: horizontal legend (lifecycle order, top-right)")


# === Step 6: Callout 1 — Falcon 1 development cluster (Kirk Ch 9) ==========
#
# Kirk Ch 9: "Do not annotate every data point. Annotate the moments that
# change the meaning of everything else."
# Callout 1 frames the Falcon 1 era: N failures in first N flights (2006-2008).
# One bracket-style label for the whole cluster, not three individual arrows.

fig.add_annotation(
    x=f1_mid_date,
    y="Failure",
    text=(
        f"<b>Development era</b><br>"
        f"{f1_count} failures in first {f1_count} flights<br>"
        f"({f1_year_start}–{f1_year_end})"
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

fig.write_image(str(IMAGES_DIR / "build_up_step_06_callout_falcon1.png"), scale=2)
print("Step 6 saved: Callout 1 — Falcon 1 development cluster")


# === Step 7: Callout 2 — CRS-7 / Amos-6 pivot (Kirk Ch 9) =================
#
# Kirk Ch 9: Identify WHAT happened and WHY it matters. These two failures
# are the turning point — they triggered the Block 5 redesign. Without this
# annotation, a reader sees a gap after 2016 but doesn't know WHY.
# Placed BELOW the row to avoid competing with Callout 1 above.

fig.add_annotation(
    x=cluster_mid,
    y="Failure",
    text=(
        f"<b>Pivot point</b><br>"
        f"{cluster_label}<br>"
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

fig.write_image(str(IMAGES_DIR / "build_up_step_07_callout_pivot.png"), scale=2)
print("Step 7 saved: Callout 2 — CRS-7 / Amos-6 pivot point")


# === Step 8: Callout 3 — Block 5 reliability gap (Kirk Ch 9) ===============
#
# Kirk Ch 9: This is the KEY INSIGHT annotation. The gap is INVISIBLE without
# annotation — it is the ABSENCE of dots. A shaded vrect + dashed boundary
# lines + text label makes the whitespace legible as data. ~2,800 days of
# Falcon 9 Block 5 operations with zero failures.
# The gap is measured WITHIN Falcon 9 only (Amos-6 to Starlink Group 9-3),
# because Starship and Falcon 9 programs overlapped chronologically.

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
        f"<b>Falcon 9 Block 5: {gap_days:,} days without a failure</b><br>"
        f"({gap_years:.1f} years — "
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

fig.write_image(str(IMAGES_DIR / "build_up_step_08_callout_gap.png"), scale=2)
print("Step 8 saved: Callout 3 — Block 5 reliability gap (shaded vrect)")


# === Step 9: Source attribution (Kirk Ch 9) =================================
#
# Kirk Ch 9: "Footnotes establish credibility." Source attribution placed at
# bottom-right, small but readable (9pt). This is the final element — the
# chart is now visually identical to tutorial_final's primary output.

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

fig.write_image(str(IMAGES_DIR / "build_up_step_09_source_attribution.png"), scale=2)
print("Step 9 saved: source attribution (final — matches tutorial_final)")

print()
print("=" * 65)
print(f"Build-up complete: 9 steps saved to {IMAGES_DIR}/")
print("=" * 65)
