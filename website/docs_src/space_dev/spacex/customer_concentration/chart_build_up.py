"""
Chart Build-Up: Customer Concentration — 100% Stacked Bar
=========================================================

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

from data.utils import get_spacex_data

IMAGES_DIR = Path(__file__).resolve().parent / "images"
IMAGES_DIR.mkdir(exist_ok=True)


# ============================================================================
# Data loading — shared across all steps
# ============================================================================

_US_GOV_OWNERS = {
    "National Aeronautics and Space Administration",
    "National Reconnaissance Office",
    "United States Space Force",
    "Space Development Agency",
    "Missile Defense Agency",
}

_INTL_GOV_OWNERS = {
    "Canadian Space Agency",
    "European Space Agency",
    "Japan Aerospace Exploration Agency",
    "Italian Space Agency",
    "Indian Space Research Organization",
    "Bundeswehr",
    "European Organisation for the Exploitation of Meteorological Satellites",
}

CAT_ORDER = ["SpaceX (Internal)", "US Government", "Intl Government", "Commercial"]

CAT_COLORS = {
    "SpaceX (Internal)": "#1A237E",
    "US Government": "#E65100",
    "Intl Government": "#00897B",
    "Commercial": "#FFB300",
}

SOURCE = "Source: Launch Library 2 API | thespacedevs.com"

df = get_spacex_data()
completed = df[
    df["launch_status_abbrev"].isin(["Success", "Failure", "Partial Failure"])
].copy()


# Assign customer categories
def _assign(row):
    owner = row["mission_owner_primary_name"]
    if pd.notna(owner) and owner != "":
        if owner == "SpaceX":
            return "SpaceX (Internal)"
        if owner in _US_GOV_OWNERS:
            return "US Government"
        if owner in _INTL_GOV_OWNERS:
            return "Intl Government"
        return "Commercial"
    mission_type = str(row.get("mission_type", ""))
    program = str(row.get("program_names", ""))
    launch_name = str(row.get("launch_name", ""))
    if "Starship" in program or "Starship" in launch_name:
        return "SpaceX (Internal)"
    if mission_type == "Test Flight":
        return "SpaceX (Internal)"
    if "NROL" in launch_name or "USSF" in launch_name:
        return "US Government"
    if mission_type == "Government/Top Secret":
        return "US Government"
    return "Commercial"


completed["customer_category"] = completed.apply(_assign, axis=1)

# Aggregate: yearly counts and percentages
yearly_raw = (
    completed.groupby(["year", "customer_category"])
    .size()
    .reset_index(name="launches")
)

# Filter out years with <3 launches (1-2 test flights give misleading 100% shares)
yearly_totals = completed.groupby("year").size()
valid_years = yearly_totals[yearly_totals >= 3].index
yearly = yearly_raw[yearly_raw["year"].isin(valid_years)].copy()
totals = yearly.groupby("year")["launches"].transform("sum")
yearly["pct"] = yearly["launches"] / totals * 100

# Compute annotation values from data — never hardcoded
spacex_by_year = (
    yearly[yearly["customer_category"] == "SpaceX (Internal)"]
    .set_index("year")["pct"]
)
over_50 = spacex_by_year[spacex_by_year > 50]
majority_year = int(over_50.index.min()) if not over_50.empty else None
majority_pct = round(over_50.iloc[0], 1) if not over_50.empty else 0

max_year = int(yearly["year"].max())
latest_spacex_pct = round(spacex_by_year.get(max_year, 0), 1)

total_spacex = len(completed[completed["customer_category"] == "SpaceX (Internal)"])
total_launches = len(completed)

CHART_WIDTH = 1200
CHART_HEIGHT = 680

print("=" * 65)
print("CHART BUILD-UP: Customer Concentration — 100% Stacked Bar")
print("=" * 65)
print()


# === Step 1: Raw stacked bar — absolute counts (Kirk Ch 4, Ch 7) ==============
#
# Kirk Ch 4: Know your data. Kirk Ch 7: Start with the simplest possible chart.
# This is a basic stacked bar of launch counts by customer category per year.
# Default Plotly colours, no percentage normalisation. The growth from ~6 to
# ~170 launches dominates the visual — it is hard to see concentration shift
# because the early-year bars are tiny compared to recent years.

fig = px.bar(
    yearly,
    x="year",
    y="launches",
    color="customer_category",
    title="Customer Mix Over Time — Raw Counts",
    labels={"year": "Year", "launches": "Launches", "customer_category": "Customer"},
    category_orders={"customer_category": CAT_ORDER},
)
fig.update_layout(
    xaxis=dict(dtick=1),
    barmode="stack",
    width=1100,
    height=500,
)

fig.write_image(str(IMAGES_DIR / "build_up_step_01_raw_stacked.png"), scale=2)
print("Step 1 saved: raw stacked bar (absolute counts, default colors)")


# === Step 2: Normalise to 100% (Kirk Ch 7) ====================================
#
# Kirk Ch 7: "Choose the chart that answers the question." Our question is about
# concentration SHARE, not volume. Normalising to 100% removes the volume
# dimension — every year is the same height. Now the reader compares proportions
# across time. A year with 6 launches and a year with 170 are equally readable.
# The navy SpaceX band expanding from nothing to dominance IS the story.

fig = px.bar(
    yearly,
    x="year",
    y="pct",
    color="customer_category",
    title="Customer Share Over Time — 100% Stacked",
    labels={"year": "Year", "pct": "Share (%)", "customer_category": "Customer"},
    category_orders={"customer_category": CAT_ORDER},
)
fig.update_layout(
    xaxis=dict(dtick=1),
    yaxis=dict(range=[0, 100]),
    barmode="stack",
    width=1100,
    height=500,
)

fig.write_image(str(IMAGES_DIR / "build_up_step_02_normalised_pct.png"), scale=2)
print("Step 2 saved: normalised to 100% (concentration shift now readable)")


# === Step 3: Warm/cool color palette (Kirk Ch 10) =============================
#
# Kirk Ch 10: "Color should carry editorial meaning, not just decoration."
# Default Plotly colors treat all categories equally. Our palette encodes the
# concentration tension: SpaceX gets deep navy (cool, heavy, corporate dominance),
# while external customers get warm colors (orange, teal, amber = diversity).
# As the navy band grows, it visually swallows the warm colors — the palette
# tells the concentration story before the reader reads the axis.

fig = px.bar(
    yearly,
    x="year",
    y="pct",
    color="customer_category",
    title="Customer Share — Intentional Palette",
    labels={"year": "Year", "pct": "Share (%)", "customer_category": "Customer"},
    color_discrete_map=CAT_COLORS,
    category_orders={"customer_category": CAT_ORDER},
)
fig.update_layout(
    xaxis=dict(dtick=1),
    yaxis=dict(range=[0, 100]),
    barmode="stack",
    width=1100,
    height=500,
)

fig.write_image(str(IMAGES_DIR / "build_up_step_03_color_palette.png"), scale=2)
print("Step 3 saved: warm/cool color palette (navy dominance, warm diversity)")


# === Step 4: Layout polish (Kirk Ch 11) ========================================
#
# Kirk Ch 11: Composition — layout, hierarchy, whitespace, visual cohesion.
# White background removes visual noise. Subtle y-axis gridlines aid value
# reading. Wider chart (1200px) gives the year axis room to breathe. Increased
# margins reserve space for annotations coming in later steps. Y-axis extended
# to 105 so annotation callouts don't clip at the top.

fig = px.bar(
    yearly,
    x="year",
    y="pct",
    color="customer_category",
    labels={"year": "Year", "pct": "Share (%)", "customer_category": "Customer"},
    color_discrete_map=CAT_COLORS,
    category_orders={"customer_category": CAT_ORDER},
)
fig.update_layout(
    xaxis=dict(dtick=1, title="Year"),
    yaxis=dict(range=[0, 105], title="Share (%)"),
    barmode="stack",
    width=CHART_WIDTH,
    height=CHART_HEIGHT,
    margin=dict(t=80, b=100, l=60, r=180),
    plot_bgcolor="white",
    paper_bgcolor="white",
)
fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=True, gridcolor="#EEEEEE")

fig.write_image(str(IMAGES_DIR / "build_up_step_04_layout_polish.png"), scale=2)
print("Step 4 saved: layout polish (white bg, gridlines, margins)")


# === Step 5: Editorial title and subtitle (Kirk Ch 9) ==========================
#
# Kirk Ch 9: "The title carries the thesis, not just a description."
# A descriptive title says "Customer Share Over Time". An editorial title says
# "From Diversified to Dependent" — it tells the reader WHAT to take away.
# The subtitle gives supporting context (total SpaceX launches out of total).
# All numbers computed from data.

fig = px.bar(
    yearly,
    x="year",
    y="pct",
    color="customer_category",
    labels={"year": "Year", "pct": "Share (%)", "customer_category": "Customer"},
    color_discrete_map=CAT_COLORS,
    category_orders={"customer_category": CAT_ORDER},
)
fig.update_layout(
    title=dict(
        text=(
            "From Diversified to Dependent: SpaceX's Customer Concentration"
            f"<br><sup style='color:#666'>{total_spacex} of {total_launches} "
            f"completed launches are SpaceX's own — predominantly Starlink</sup>"
        ),
        x=0.5,
        xanchor="center",
        font=dict(size=16),
    ),
    xaxis=dict(dtick=1, title="Year"),
    yaxis=dict(range=[0, 105], title="Share (%)"),
    barmode="stack",
    width=CHART_WIDTH,
    height=CHART_HEIGHT,
    margin=dict(t=80, b=100, l=60, r=180),
    plot_bgcolor="white",
    paper_bgcolor="white",
)
fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=True, gridcolor="#EEEEEE")

fig.write_image(str(IMAGES_DIR / "build_up_step_05_editorial_title.png"), scale=2)
print("Step 5 saved: editorial title + subtitle (computed from data)")


# === Step 6: Horizontal legend below chart (Kirk Ch 11) ========================
#
# Kirk Ch 11: The legend should reinforce the categorical structure without
# competing with annotations. Horizontal placement below the chart keeps it
# compact and reads left-to-right in category order. Positioned at y=-0.12
# to avoid collision with the x-axis labels.

fig = px.bar(
    yearly,
    x="year",
    y="pct",
    color="customer_category",
    labels={"year": "Year", "pct": "Share (%)", "customer_category": "Customer"},
    color_discrete_map=CAT_COLORS,
    category_orders={"customer_category": CAT_ORDER},
)
fig.update_layout(
    title=dict(
        text=(
            "From Diversified to Dependent: SpaceX's Customer Concentration"
            f"<br><sup style='color:#666'>{total_spacex} of {total_launches} "
            f"completed launches are SpaceX's own — predominantly Starlink</sup>"
        ),
        x=0.5,
        xanchor="center",
        font=dict(size=16),
    ),
    xaxis=dict(dtick=1, title="Year"),
    yaxis=dict(range=[0, 105], title="Share (%)"),
    barmode="stack",
    width=CHART_WIDTH,
    height=CHART_HEIGHT,
    margin=dict(t=80, b=100, l=60, r=180),
    legend=dict(
        orientation="h", yanchor="top", y=-0.12, xanchor="center", x=0.5,
        font=dict(size=11),
    ),
    plot_bgcolor="white",
    paper_bgcolor="white",
)
fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=True, gridcolor="#EEEEEE")

fig.write_image(str(IMAGES_DIR / "build_up_step_06_horizontal_legend.png"), scale=2)
print("Step 6 saved: horizontal legend below chart")


# === Step 7: 50% concentration threshold (Kirk Ch 9) ==========================
#
# Kirk Ch 9: "Annotate the moments that change the meaning of everything else."
# A dashed horizontal line at 50% gives the reader a reference point — above
# this line, one customer category dominates more than all others combined.
# The right-margin label explains what the line means. This transforms the
# chart from "look at the pretty bars" to "watch SpaceX cross the threshold."

fig = px.bar(
    yearly,
    x="year",
    y="pct",
    color="customer_category",
    labels={"year": "Year", "pct": "Share (%)", "customer_category": "Customer"},
    color_discrete_map=CAT_COLORS,
    category_orders={"customer_category": CAT_ORDER},
)
fig.update_layout(
    title=dict(
        text=(
            "From Diversified to Dependent: SpaceX's Customer Concentration"
            f"<br><sup style='color:#666'>{total_spacex} of {total_launches} "
            f"completed launches are SpaceX's own — predominantly Starlink</sup>"
        ),
        x=0.5,
        xanchor="center",
        font=dict(size=16),
    ),
    xaxis=dict(dtick=1, title="Year"),
    yaxis=dict(range=[0, 105], title="Share (%)"),
    barmode="stack",
    width=CHART_WIDTH,
    height=CHART_HEIGHT,
    margin=dict(t=80, b=100, l=60, r=180),
    legend=dict(
        orientation="h", yanchor="top", y=-0.12, xanchor="center", x=0.5,
        font=dict(size=11),
    ),
    plot_bgcolor="white",
    paper_bgcolor="white",
)
fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=True, gridcolor="#EEEEEE")

fig.add_hline(y=50, line_dash="dash", line_color="#999", line_width=1.5)
fig.add_annotation(
    text="50% concentration<br>threshold",
    xref="paper", yref="y", x=1.02, y=50,
    showarrow=False, font=dict(size=10, color="#666"), xanchor="left",
)

fig.write_image(str(IMAGES_DIR / "build_up_step_07_threshold_line.png"), scale=2)
print("Step 7 saved: 50% concentration threshold line")


# === Step 8: Majority year callout (Kirk Ch 9) =================================
#
# Kirk Ch 9: Identify WHAT happened and WHY it matters. This callout marks the
# year SpaceX first crossed 50% of all launches — the inflection point where
# they shifted from launch provider to self-dependent operator. The arrow points
# to the middle of the SpaceX band in that year. Positioned up-and-left to avoid
# overlapping with the data bars.

fig.add_annotation(
    x=majority_year, y=majority_pct / 2,
    text=(
        f"<b>{majority_year}: SpaceX becomes<br>"
        f"majority customer ({majority_pct:.0f}%)</b>"
    ),
    showarrow=True, arrowhead=2, arrowsize=1.2, arrowcolor="#1A237E",
    ax=-90, ay=-80,
    font=dict(size=11, color="#1A237E"),
    bgcolor="white", bordercolor="#1A237E", borderwidth=1, borderpad=4,
)

fig.write_image(str(IMAGES_DIR / "build_up_step_08_majority_callout.png"), scale=2)
print("Step 8 saved: majority year callout (inflection point)")


# === Step 9: Latest SpaceX share callout (Kirk Ch 9) ===========================
#
# Kirk Ch 9: The "where are we now?" annotation grounds the trend in the present.
# Positioned to the right of the final bar so the arrow points inward. The bold
# percentage is the headline number the reader takes away.

fig.add_annotation(
    x=max_year, y=latest_spacex_pct / 2,
    text=f"<b>{latest_spacex_pct:.0f}%</b><br>SpaceX share",
    showarrow=True, arrowhead=2, arrowsize=1.2, arrowcolor="#1A237E",
    ax=70, ay=20,
    font=dict(size=11, color="#1A237E"),
    bgcolor="white", bordercolor="#1A237E", borderwidth=1, borderpad=4,
)

fig.write_image(str(IMAGES_DIR / "build_up_step_09_latest_share.png"), scale=2)
print("Step 9 saved: latest SpaceX share callout")


# === Step 10: Source attribution (Kirk Ch 9) ===================================
#
# Kirk Ch 9: "Footnotes establish credibility." Source attribution placed at
# bottom-left, small but readable (9pt). This is the final element — the chart
# is now visually identical to tutorial_final's primary output.

fig.add_annotation(
    text=SOURCE, xref="paper", yref="paper",
    x=0, y=-0.1, showarrow=False, font=dict(size=9, color="#999"),
)

fig.write_image(str(IMAGES_DIR / "build_up_step_10_source_attribution.png"), scale=2)
print("Step 10 saved: source attribution (final — matches tutorial_final)")

print()
print("=" * 65)
print(f"Build-up complete: 10 steps saved to {IMAGES_DIR}/")
print("=" * 65)
