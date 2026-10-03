"""
Chart Build-Up: SpaceX Launch Cadence Bar Chart
================================================

A linear, step-by-step script that progressively builds the winning bar chart
from its rawest form to the polished final composition. Each step applies
exactly ONE design decision from the Kirk tutorial series and saves an image.

Run with: python chart_build_up.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.express as px

from data.utils import get_spacex_data

# ---------------------------------------------------------------------------
# Output directory
# ---------------------------------------------------------------------------
IMAGES_DIR = Path(__file__).resolve().parent / "images"
IMAGES_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Data loading and preparation
# ---------------------------------------------------------------------------
df = get_spacex_data()
df = df[df["launch_status_abbrev"].isin(["Success", "Failure", "Partial Failure"])]

yearly = df.groupby("year").size().reset_index(name="launches")


# === Step 1: Raw bar chart with Plotly defaults (Kirk Ch 4-5) ===
# WHY: This is the starting point — the rawest possible bar chart from the
# profiling stage (tutorial_001). Default Plotly colors, no editorial intent,
# no annotations. It answers "what does the data look like?" before any
# design thinking. Kirk Ch 4: "Know your data before you visualise it."

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

fig.write_image(str(IMAGES_DIR / "build_up_step_01_raw_bar.png"), scale=2)
print("Saved: step 01 — raw bar chart (Plotly defaults)")


# === Step 2: Chart type confirmed — bar chart wins (Kirk Ch 7) ===
# WHY: Tutorial_002 evaluated four candidates (bar, line, area, heatmap).
# The bar chart won because bar length is the most accurately perceived
# visual channel (Kirk Ch 7), the dramatic height contrast tells the
# acceleration story at a glance, and discrete bars match how our insurance
# audience thinks (year-over-year comparisons). This step keeps the same
# raw bar but makes the axis ticks cleaner, confirming our chart type choice.
# The chart is identical to step 1 because the DECISION was to keep the
# bar chart — no visual change yet, just the confirmed foundation.

fig = px.bar(
    yearly,
    x="year",
    y="launches",
    title="Candidate Selected: Vertical Bar Chart",
    labels={"year": "Year", "launches": "Launches"},
)
fig.update_layout(
    xaxis=dict(dtick=1),
    width=1000,
    height=500,
    showlegend=False,
)

fig.write_image(str(IMAGES_DIR / "build_up_step_02_chart_type_confirmed.png"), scale=2)
print("Saved: step 02 — chart type confirmed as bar chart")


# === Step 3: Phase-based color encoding (Kirk Ch 10) ===
# WHY: Default Plotly colors are uniform — every bar is the same blue,
# conveying no editorial meaning. Tutorial_003 introduced a three-phase
# sequential blue ramp: gray for Startup (2006-2013), medium blue for
# Growth (2014-2019), deep blue for Hyperscale (2020+). Color now ENCODES
# data — the phases are ordered, so intensity increases with the phase.
# Single-hue blue is colorblind-safe (relies on lightness, not hue) and
# culturally neutral in business contexts (no red=loss / green=gain).

PHASE_COLORS = {
    "Startup (2006-2013)": "#B0BEC5",
    "Growth (2014-2019)": "#42A5F5",
    "Hyperscale (2020+)": "#0D47A1",
}

yearly["phase"] = yearly["year"].apply(
    lambda y: "Startup (2006-2013)" if y <= 2013
    else "Growth (2014-2019)" if y <= 2019
    else "Hyperscale (2020+)"
)

fig = px.bar(
    yearly,
    x="year",
    y="launches",
    color="phase",
    title="AFTER: Phase-Based Color — Acceleration Eras",
    labels={"year": "Year", "launches": "Launches", "phase": "Phase"},
    color_discrete_map=PHASE_COLORS,
    category_orders={"phase": list(PHASE_COLORS.keys())},
)
fig.update_layout(
    xaxis=dict(dtick=1),
    width=1000,
    height=500,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5,
    ),
)

fig.write_image(str(IMAGES_DIR / "build_up_step_03_phase_color.png"), scale=2)
print("Saved: step 03 — three-phase color encoding")


# === Step 4: Data labels on bars (Kirk Ch 9 — Labeling) ===
# WHY: Kirk Ch 9 distinguishes LABELING from ANNOTATING. Labels answer
# "what value is this bar?" — they identify. At this step we add the
# launch count as text on each bar. This gives readers precise numbers
# without needing to trace to the y-axis. Labels are necessary but not
# sufficient — they don't yet tell the reader WHAT TO NOTICE.

fig = px.bar(
    yearly,
    x="year",
    y="launches",
    color="phase",
    title="SpaceX Launch Cadence (2006-2026)",
    labels={"year": "Year", "launches": "Launches", "phase": "Phase"},
    text="launches",
    color_discrete_map=PHASE_COLORS,
    category_orders={"phase": list(PHASE_COLORS.keys())},
)
fig.update_traces(textposition="outside")
fig.update_layout(
    xaxis=dict(dtick=1),
    width=1100,
    height=550,
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
    ),
)

fig.write_image(str(IMAGES_DIR / "build_up_step_04_data_labels.png"), scale=2)
print("Saved: step 04 — data labels on bars")


# === Step 5: Editorial title and subtitle (Kirk Ch 9 — Annotation hierarchy level 1) ===
# WHY: "SpaceX Launches per Year" is a LABEL — it describes the chart.
# "From X to Y: SpaceX's Launch Acceleration" is an ANNOTATION — it tells
# the reader what to notice. The title is the most prominent element and
# the first thing read. An editorial title frames the acceleration story
# before the reader even looks at the bars. Values are computed from data
# so they stay current when the dataset refreshes.

first_year = int(yearly["year"].iloc[0])
first_count = int(yearly["launches"].iloc[0])

hyperscale_year = 2020
hs_data = yearly[yearly["year"] >= hyperscale_year]
peak_idx = hs_data["launches"].idxmax()
peak_year = int(hs_data.loc[peak_idx, "year"])
peak_count = int(hs_data.loc[peak_idx, "launches"])

fig = px.bar(
    yearly,
    x="year",
    y="launches",
    color="phase",
    labels={"year": "Year", "launches": "Launches", "phase": "Phase"},
    text="launches",
    color_discrete_map=PHASE_COLORS,
    category_orders={"phase": list(PHASE_COLORS.keys())},
)
fig.update_traces(textposition="outside", textfont_size=10)
fig.update_layout(
    title=dict(
        text=(
            f"From {first_count} to {peak_count}: SpaceX's Launch Acceleration"
            f"<br><sup style='color:#666'>Completed launches per year, "
            f"{first_year}-{peak_year} — three distinct acceleration phases</sup>"
        ),
        x=0.5, xanchor="center", font=dict(size=18),
    ),
    xaxis=dict(dtick=1, title="Year"),
    yaxis=dict(title="Launches"),
    width=1100,
    height=620,
    margin=dict(t=120, b=80),
    legend=dict(
        orientation="h", yanchor="top", y=-0.08,
        xanchor="center", x=0.5, font=dict(size=11),
    ),
    plot_bgcolor="white", paper_bgcolor="white",
)
fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=True, gridcolor="#EEEEEE")

fig.write_image(str(IMAGES_DIR / "build_up_step_05_editorial_title.png"), scale=2)
print("Saved: step 05 — editorial title and subtitle")


# === Step 6: Strategic annotations — callouts and CAGR bracket (Kirk Ch 9 — Annotation hierarchy level 2) ===
# WHY: Annotations are where the author's voice enters the chart. We add
# three strategic callouts that frame the entire acceleration narrative:
#   1. The 2020 inflection point (where hyperscale begins, with YoY % jump)
#   2. A CAGR bracket spanning the hyperscale era (compound growth speaks
#      the language of finance — insurance professionals think in CAGR)
#   3. The peak year callout (Nx the first year — the story's payoff)
# All values are computed from data, never hardcoded. A dashed bracket
# visually connects the hyperscale start to the peak.

multiple = peak_count / max(first_count, 1)

hs_count = int(yearly.loc[yearly["year"] == hyperscale_year, "launches"].values[0])
prev_count = int(yearly.loc[yearly["year"] == hyperscale_year - 1, "launches"].values[0])
yoy_pct = round((hs_count - prev_count) / prev_count * 100)

n_years = peak_year - hyperscale_year
cagr_pct = round(((peak_count / hs_count) ** (1 / n_years) - 1) * 100)

bracket_y = peak_count + 30
bracket_mid_x = hyperscale_year + (peak_year - hyperscale_year) / 2

fig = px.bar(
    yearly,
    x="year",
    y="launches",
    color="phase",
    labels={"year": "Year", "launches": "Launches", "phase": "Phase"},
    text="launches",
    color_discrete_map=PHASE_COLORS,
    category_orders={"phase": list(PHASE_COLORS.keys())},
)
fig.update_traces(textposition="outside", textfont_size=10)

fig.update_layout(
    title=dict(
        text=(
            f"From {first_count} to {peak_count}: SpaceX's Launch Acceleration"
            f"<br><sup style='color:#666'>Completed launches per year, "
            f"{first_year}-{peak_year} — three distinct acceleration phases</sup>"
        ),
        x=0.5, xanchor="center", font=dict(size=18),
    ),
    xaxis=dict(dtick=1, title="Year"),
    yaxis=dict(title="Launches"),
    width=1100,
    height=620,
    margin=dict(t=120, b=80),
    legend=dict(
        orientation="h", yanchor="top", y=-0.08,
        xanchor="center", x=0.5, font=dict(size=11),
    ),
    plot_bgcolor="white", paper_bgcolor="white",
)
fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=True, gridcolor="#EEEEEE")

# Annotation 1: 2020 inflection point
fig.add_annotation(
    x=hyperscale_year, y=hs_count,
    text=f"Hyperscale begins<br><b>+{yoy_pct}% YoY</b>",
    showarrow=True, arrowhead=2, arrowsize=1.2, arrowcolor="#0D47A1",
    ax=-70, ay=-50,
    font=dict(size=11, color="#0D47A1"),
    bgcolor="white", bordercolor="#0D47A1", borderwidth=1, borderpad=4,
)

# Annotation 2: CAGR bracket across the hyperscale era
for x0, y0, x1, y1 in [
    (hyperscale_year, hs_count + 11, hyperscale_year, bracket_y),
    (hyperscale_year, bracket_y, peak_year, bracket_y),
    (peak_year, peak_count + 12, peak_year, bracket_y),
]:
    fig.add_shape(
        type="line", x0=x0, y0=y0, x1=x1, y1=y1,
        line=dict(color="#0D47A1", width=1.5, dash="dot"),
    )
fig.add_annotation(
    x=bracket_mid_x, y=bracket_y + 8,
    text=f"{hyperscale_year}-{peak_year} CAGR <b>{cagr_pct}%</b>",
    showarrow=False, font=dict(size=12, color="#0D47A1"),
    bgcolor="white", bordercolor="#0D47A1", borderwidth=1, borderpad=4,
)

# Annotation 3: Peak year callout
fig.add_annotation(
    x=peak_year, y=peak_count,
    text=f"<b>{peak_count} launches</b><br>{multiple:.0f}\u00d7 the first year",
    showarrow=True, arrowhead=2, arrowsize=1.2, arrowcolor="#0D47A1",
    ax=70, ay=-40,
    font=dict(size=11, color="#0D47A1"),
    bgcolor="white", bordercolor="#0D47A1", borderwidth=1, borderpad=4,
)

# Source attribution (Kirk Ch 9, hierarchy level 4)
fig.add_annotation(
    text="Source: Launch Library 2 API | thespacedevs.com",
    xref="paper", yref="paper",
    x=0, y=-0.18, showarrow=False, font=dict(size=9, color="#999"),
)

fig.write_image(str(IMAGES_DIR / "build_up_step_06_annotations.png"), scale=2)
print("Saved: step 06 — strategic annotations and CAGR bracket")


# === Step 7: Final composition — layout polish (Kirk Ch 6, 11) ===
# WHY: Kirk Ch 11 (Composition) is about the cohesive whole — how every
# element works together. Kirk Ch 6 (Design Solutions) is the synthesis.
# This final step applies layout polish: white background for clean
# professional look, subtle gridlines that don't compete with the data,
# refined font sizes, adjusted margins, and the legend repositioned to
# the bottom to free up chart real estate. Every pixel is intentional.
# This step must visually match tutorial_final's bar chart output.

fig = px.bar(
    yearly,
    x="year",
    y="launches",
    color="phase",
    labels={"year": "Year", "launches": "Launches", "phase": "Phase"},
    text="launches",
    color_discrete_map=PHASE_COLORS,
    category_orders={"phase": list(PHASE_COLORS.keys())},
)
fig.update_traces(textposition="outside", textfont_size=10)

fig.update_layout(
    title=dict(
        text=(
            f"From {first_count} to {peak_count}: SpaceX's Launch Acceleration"
            f"<br><sup style='color:#666'>Completed launches per year, "
            f"{first_year}-{peak_year} — three distinct acceleration phases</sup>"
        ),
        x=0.5, xanchor="center", font=dict(size=18),
    ),
    xaxis=dict(dtick=1, title="Year"),
    yaxis=dict(title="Launches"),
    width=1100, height=620,
    margin=dict(t=120, b=80),
    legend=dict(
        orientation="h", yanchor="top", y=-0.08,
        xanchor="center", x=0.5, font=dict(size=11),
    ),
    plot_bgcolor="white", paper_bgcolor="white",
)
fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=True, gridcolor="#EEEEEE")

# Annotation 1: 2020 inflection point
fig.add_annotation(
    x=hyperscale_year, y=hs_count,
    text=f"Hyperscale begins<br><b>+{yoy_pct}% YoY</b>",
    showarrow=True, arrowhead=2, arrowsize=1.2, arrowcolor="#0D47A1",
    ax=-70, ay=-50,
    font=dict(size=11, color="#0D47A1"),
    bgcolor="white", bordercolor="#0D47A1", borderwidth=1, borderpad=4,
)

# Annotation 2: CAGR bracket
for x0, y0, x1, y1 in [
    (hyperscale_year, hs_count + 11, hyperscale_year, bracket_y),
    (hyperscale_year, bracket_y, peak_year, bracket_y),
    (peak_year, peak_count + 12, peak_year, bracket_y),
]:
    fig.add_shape(
        type="line", x0=x0, y0=y0, x1=x1, y1=y1,
        line=dict(color="#0D47A1", width=1.5, dash="dot"),
    )
fig.add_annotation(
    x=bracket_mid_x, y=bracket_y + 8,
    text=f"{hyperscale_year}-{peak_year} CAGR <b>{cagr_pct}%</b>",
    showarrow=False, font=dict(size=12, color="#0D47A1"),
    bgcolor="white", bordercolor="#0D47A1", borderwidth=1, borderpad=4,
)

# Annotation 3: Peak year callout
fig.add_annotation(
    x=peak_year, y=peak_count,
    text=f"<b>{peak_count} launches</b><br>{multiple:.0f}\u00d7 the first year",
    showarrow=True, arrowhead=2, arrowsize=1.2, arrowcolor="#0D47A1",
    ax=70, ay=-40,
    font=dict(size=11, color="#0D47A1"),
    bgcolor="white", bordercolor="#0D47A1", borderwidth=1, borderpad=4,
)

# Source attribution
fig.add_annotation(
    text="Source: Launch Library 2 API | thespacedevs.com",
    xref="paper", yref="paper",
    x=0, y=-0.18, showarrow=False, font=dict(size=9, color="#999"),
)

fig.write_image(str(IMAGES_DIR / "build_up_step_07_final_composition.png"), scale=2)
print("Saved: step 07 — final composition (matches tutorial_final)")

print()
print("Build-up complete: 7 images saved to images/")
