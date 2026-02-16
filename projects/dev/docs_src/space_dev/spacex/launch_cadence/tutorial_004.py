"""
What You'll Learn
=================
- How to add purposeful annotation that guides the reader to insight
- Kirk Chapter 9: Annotation — titles, labels, legends, and strategic callouts
- The critical difference between LABELING (what is it?) and ANNOTATING (what should I notice?)
- Output: Annotated versions of both winning charts
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
# Constants — carried forward from tutorial_003
# ---------------------------------------------------------------------------
IMAGES_DIR = Path(__file__).resolve().parent / "images"
IMAGES_DIR.mkdir(exist_ok=True)

PHASE_COLORS = {
    "Startup (2006-2013)": "#B0BEC5",
    "Growth (2014-2019)": "#42A5F5",
    "Hyperscale (2020+)": "#0D47A1",
}

HEATMAP_SCALE = [
    [0.0, "#F5F5F5"],
    [0.15, "#BBDEFB"],
    [0.35, "#64B5F6"],
    [0.55, "#2196F3"],
    [0.75, "#1565C0"],
    [1.0, "#0D47A1"],
]


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
def load_and_filter() -> pd.DataFrame:
    """Load SpaceX data and filter to completed launches only."""
    df = get_spacex_data()
    completed = df[df["launch_status_abbrev"].isin(["Success", "Failure", "Partial Failure"])]
    return completed


def prepare_yearly(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate to yearly launch counts with acceleration phase labels."""
    yearly = df.groupby("year").size().reset_index(name="launches")

    def assign_phase(year: int) -> str:
        if year <= 2013:
            return "Startup (2006-2013)"
        elif year <= 2019:
            return "Growth (2014-2019)"
        else:
            return "Hyperscale (2020+)"

    yearly["phase"] = yearly["year"].apply(assign_phase)
    return yearly


def prepare_monthly_pivot(df: pd.DataFrame) -> pd.DataFrame:
    """Create year x month pivot for heatmap."""
    pivot = df.pivot_table(
        index="year", columns="month", aggfunc="size", fill_value=0
    )
    for m in range(1, 13):
        if m not in pivot.columns:
            pivot[m] = 0
    return pivot[range(1, 13)]


# ---------------------------------------------------------------------------
# Image 1 — Bar chart with LABELS only (no annotation)
# ---------------------------------------------------------------------------
def bar_labeled_only(yearly: pd.DataFrame) -> None:
    """Bar chart with data labels but no editorial annotation.

    Kirk Ch 9 distinguishes between LABELING and ANNOTATING:

    LABELING answers: 'What value is this bar?'
    - The text on each bar (1, 2, 7, 18, 170...) is a label.
    - Labels identify. They tell the reader what something IS.
    - They are necessary but not sufficient for insight.

    At this stage the chart has color (from tutorial_003) and labels,
    but it doesn't yet TELL THE READER WHAT TO NOTICE. The reader must
    do all the interpretive work themselves.
    """
    color_map = PHASE_COLORS

    fig = px.bar(
        yearly,
        x="year",
        y="launches",
        color="phase",
        title="SpaceX Launch Cadence (2006-2026)",
        labels={"year": "Year", "launches": "Launches", "phase": "Phase"},
        text="launches",
        color_discrete_map=color_map,
        category_orders={"phase": list(color_map.keys())},
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

    out = IMAGES_DIR / "tutorial_004_image_01_bar_labels_only.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Image 2 — Bar chart with strategic ANNOTATIONS
# ---------------------------------------------------------------------------
def bar_annotated(yearly: pd.DataFrame) -> None:
    """Bar chart with editorial annotations that guide the reader's eye.

    Kirk Ch 9: ANNOTATING answers: 'What should I notice here?'
    - Annotations are editorial. They carry the author's interpretation.
    - They reduce the cognitive load on the reader by pointing to insight.
    - Strategic means SELECTIVE: annotate the 1-2 most important things,
      not every data point. Over-annotation creates noise.

    Kirk Ch 9 annotation hierarchy (most to least prominent):
    1. Title & subtitle — the first thing read, sets the frame
    2. Direct annotation on the chart — arrows, callout text
    3. Axis labels — orient the reader
    4. Footnotes & source — credibility, context

    We annotate THREE strategic moments:
    1. 2020: The inflection point where hyperscale begins (29 launches,
       a 93% jump from 2019's 15 — the steepest year-over-year leap).
    2. 2020-2025 CAGR: 42% compound annual growth rate across the
       hyperscale era. CAGR is the language of finance — our insurance
       audience thinks in compound growth, not single-year jumps.
    3. 2025: The peak at 170 — a 170x multiple from the first year.

    These three points frame the entire acceleration narrative.
    """
    color_map = PHASE_COLORS

    fig = px.bar(
        yearly,
        x="year",
        y="launches",
        color="phase",
        labels={"year": "Year", "launches": "Launches", "phase": "Phase"},
        text="launches",
        color_discrete_map=color_map,
        category_orders={"phase": list(color_map.keys())},
    )
    fig.update_traces(textposition="outside")

    # --- Annotation hierarchy level 1: Title & subtitle ---
    # Kirk Ch 9: The title should frame the editorial angle, not just
    # describe the chart type. "SpaceX Launches per Year" is a label.
    # "From 1 to 170" is an annotation — it tells you what to notice.
    fig.update_layout(
        title=dict(
            text=(
                "From 1 to 170: SpaceX's Launch Acceleration"
                "<br><sup style='color:#666'>Completed launches per year, 2006-2026 "
                "| Three distinct acceleration phases</sup>"
            ),
            x=0.5,
            xanchor="center",
        ),
        xaxis=dict(dtick=1),
        width=1100,
        height=600,
        margin=dict(t=100, b=80),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.06, xanchor="center", x=0.5,
        ),
    )

    # --- Annotation hierarchy level 2: Direct callouts ---

    # Annotation 1: The 2020 inflection point
    fig.add_annotation(
        x=2020,
        y=29,
        text="Hyperscale begins<br><b>+93% YoY</b>",
        showarrow=True,
        arrowhead=2,
        arrowsize=1.2,
        arrowcolor="#0D47A1",
        ax=-60,
        ay=-50,
        font=dict(size=11, color="#0D47A1"),
        bgcolor="white",
        bordercolor="#0D47A1",
        borderwidth=1,
        borderpad=4,
    )

    # Annotation 2: CAGR across the hyperscale era (2020-2025)
    # Kirk Ch 9: CAGR speaks directly to a finance-literate audience —
    # it compresses five years of compounding into a single number.
    # A dashed bracket visually spans the era from 2020 to 2025.
    bracket_y = 200
    fig.add_shape(
        type="line", x0=2020, y0=40, x1=2020, y1=bracket_y,
        line=dict(color="#0D47A1", width=1.5, dash="dot"),
    )
    fig.add_shape(
        type="line", x0=2020, y0=bracket_y, x1=2025, y1=bracket_y,
        line=dict(color="#0D47A1", width=1.5, dash="dot"),
    )
    fig.add_shape(
        type="line", x0=2025, y0=182, x1=2025, y1=bracket_y,
        line=dict(color="#0D47A1", width=1.5, dash="dot"),
    )
    fig.add_annotation(
        x=2022.5,
        y=bracket_y + 8,
        text="2020-2025 CAGR <b>42%</b>",
        showarrow=False,
        font=dict(size=12, color="#0D47A1"),
        bgcolor="white",
        bordercolor="#0D47A1",
        borderwidth=1,
        borderpad=4,
    )

    # Annotation 3: The 2025 peak
    fig.add_annotation(
        x=2025,
        y=170,
        text="<b>170 launches</b><br>170x the first year",
        showarrow=True,
        arrowhead=2,
        arrowsize=1.2,
        arrowcolor="#0D47A1",
        ax=60,
        ay=-40,
        font=dict(size=11, color="#0D47A1"),
        bgcolor="white",
        bordercolor="#0D47A1",
        borderwidth=1,
        borderpad=4,
    )

    # --- Annotation hierarchy level 4: Source attribution ---
    # Kirk Ch 9: Source builds credibility. Always attribute your data.
    fig.add_annotation(
        text="Source: Launch Library 2 API | thespacedevs.com",
        xref="paper",
        yref="paper",
        x=0,
        y=-0.12,
        showarrow=False,
        font=dict(size=9, color="#999"),
    )

    out = IMAGES_DIR / "tutorial_004_image_02_bar_annotated.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Image 3 — Heatmap with annotation
# ---------------------------------------------------------------------------
def heatmap_annotated(pivot: pd.DataFrame) -> None:
    """Heatmap with title framing and bracket annotations.

    Kirk Ch 9: The heatmap tells a subplot — the shift from sporadic to
    continuous operations. Annotations should highlight this transition
    without cluttering the dense grid.

    Strategy: Use the title/subtitle to frame the insight, and add
    minimal bracket annotations to mark the two eras. Less is more
    on a data-dense chart.
    """
    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    fig = px.imshow(
        pivot.values,
        x=month_labels,
        y=[str(y) for y in pivot.index],
        color_continuous_scale=HEATMAP_SCALE,
        labels=dict(x="Month", y="Year", color="Launches"),
        text_auto=True,
        aspect="auto",
    )

    # --- Title frames the insight ---
    fig.update_layout(
        title=dict(
            text=(
                "From Sporadic to Always-On: Monthly Launch Density"
                "<br><sup style='color:#666'>Completed launches by month, 2006-2026 "
                "| White cells = zero launches that month</sup>"
            ),
            x=0.5,
            xanchor="center",
        ),
        width=1000,
        height=650,
        margin=dict(t=100, b=80, r=120),
    )

    # --- Era bracket annotations on the right side ---
    # Kirk Ch 9: These are interpretive annotations — they tell the
    # reader what pattern to see, not just what the numbers are.
    fig.add_annotation(
        text="Sparse:<br>gaps & clusters",
        xref="paper",
        yref="paper",
        x=1.08,
        y=0.85,
        showarrow=False,
        font=dict(size=10, color="#B0BEC5"),
    )

    fig.add_annotation(
        text="Dense:<br>every month active",
        xref="paper",
        yref="paper",
        x=1.08,
        y=0.2,
        showarrow=False,
        font=dict(size=10, color="#0D47A1"),
    )

    # --- Source attribution ---
    fig.add_annotation(
        text="Source: Launch Library 2 API | thespacedevs.com",
        xref="paper",
        yref="paper",
        x=0,
        y=-0.1,
        showarrow=False,
        font=dict(size=9, color="#999"),
    )

    out = IMAGES_DIR / "tutorial_004_image_03_heatmap_annotated.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    """Run the annotation process for both winning charts.

    Kirk Ch 9: Annotation is where the author's voice enters the
    visualisation. Without annotation, you have a chart. With it,
    you have a story.
    """
    df = load_and_filter()
    yearly = prepare_yearly(df)
    pivot = prepare_monthly_pivot(df)

    print("=" * 60)
    print("ANNOTATION — Kirk Ch 9: Annotation")
    print("=" * 60)
    print()

    # --- Demonstrate labeling vs annotating ---
    print("LABELING vs ANNOTATING")
    print("-" * 40)
    print()
    bar_labeled_only(yearly)
    print("  Labels only: the reader sees numbers but must interpret alone.")
    print()
    bar_annotated(yearly)
    print("  Annotated: the reader is guided to inflection, CAGR, and peak.")
    print("  Three annotations frame the entire acceleration narrative.")
    print()

    # --- Heatmap annotation ---
    print("HEATMAP ANNOTATION")
    print("-" * 40)
    print()
    heatmap_annotated(pivot)
    print("  Title frames the insight; side labels mark the sparse → dense shift.")
    print("  On data-dense charts, less annotation is more.")
    print()

    # --- Summary ---
    print("=" * 60)
    print("ANNOTATION DECISIONS SUMMARY")
    print("=" * 60)
    print("""
KIRK CH 9 ANNOTATION HIERARCHY APPLIED:

1. TITLE & SUBTITLE (most prominent):
   - Bar: "From 1 to 170: SpaceX's Launch Acceleration"
     → Editorial, not descriptive. Tells the reader what the story IS.
   - Heatmap: "From Sporadic to Always-On: Monthly Launch Density"
     → Frames the subplot before the reader even looks at the data.

2. DIRECT ANNOTATIONS (strategic callouts):
   - 2020 inflection point: "+93% YoY" — the moment hyperscale begins.
   - 2020-2025 CAGR: "42%" — compound growth rate speaks the language
     of finance. Insurance professionals think in CAGR, not single-year
     jumps. This bridges the inflection and the peak.
   - 2025 peak: "170x the first year" — the payoff of the story.

3. AXIS LABELS (orientation):
   - Year and Launches on bar chart — standard, unambiguous.
   - Month and Year on heatmap — spatial orientation for the grid.

4. SOURCE ATTRIBUTION (credibility):
   - "Launch Library 2 API | thespacedevs.com" on both charts.
   - Small, gray, bottom-left — present but not competing for attention.

LABELING vs ANNOTATING:

  LABELING = "This bar is 170"
  → Identifies the value. Necessary for precision.

  ANNOTATING = "170x the first year"
  → Interprets the value. Gives the reader the takeaway.

  The best visualisations do both: labels for readers who want detail,
  annotations for readers who want the story.

DOMAIN TRANSFER:

  Insurance professionals building claims dashboards face the same
  choice. A chart showing monthly claims counts with just data labels
  forces the underwriter to do the interpretation. Adding an annotation
  like "Storm season: +40% above average" turns a chart into a brief.
""")


if __name__ == "__main__":
    main()
