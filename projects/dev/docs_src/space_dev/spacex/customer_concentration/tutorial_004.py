"""
What You'll Learn
=================
- How to add purposeful annotation that guides the reader to insight
- Kirk Chapter 9: Annotation — titles, labels, legends, and strategic callouts
- The critical difference between LABELING (what is it?) and ANNOTATING (what should I notice?)
- Output: Annotated versions of both winning charts (100% stacked bar + treemap)
"""

import sys
from pathlib import Path

# Ensure the parent directory is on the path so `from data.utils import ...` works
# when this script is run directly from the customer_concentration/ folder.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Standard imports
import pandas as pd
import plotly.express as px

# Local imports
from data.utils import get_spacex_data

# ---------------------------------------------------------------------------
# Constants — carried forward from tutorial_003
# ---------------------------------------------------------------------------
IMAGES_DIR = Path(__file__).resolve().parent / "images"
IMAGES_DIR.mkdir(exist_ok=True)

CAT_ORDER = ["SpaceX (Internal)", "US Government", "Intl Government", "Commercial"]

CAT_COLORS = {
    "SpaceX (Internal)": "#1A237E",
    "US Government": "#E65100",
    "Intl Government": "#00897B",
    "Commercial": "#FFB300",
}

SOURCE = "Source: Launch Library 2 API | thespacedevs.com"

# Customer category sets
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


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
def load_and_filter() -> pd.DataFrame:
    """Load SpaceX data, filter to completed launches, assign customer categories."""
    df = get_spacex_data()
    completed = df[
        df["launch_status_abbrev"].isin(["Success", "Failure", "Partial Failure"])
    ].copy()
    completed["customer_category"] = completed.apply(_assign_customer_category, axis=1)
    return completed


def _assign_customer_category(row: pd.Series) -> str:
    """Classify each launch into a customer category."""
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


def prepare_yearly_pct(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compute yearly percentage composition and return both raw and pct frames."""
    yearly = (
        df.groupby(["year", "customer_category"])
        .size()
        .reset_index(name="launches")
    )
    yearly_totals = df.groupby("year").size()
    valid_years = yearly_totals[yearly_totals >= 3].index
    yearly = yearly[yearly["year"].isin(valid_years)].copy()
    totals = yearly.groupby("year")["launches"].transform("sum")
    yearly["pct"] = yearly["launches"] / totals * 100
    yearly["total"] = totals
    return yearly, yearly_totals


def prepare_treemap_data(df: pd.DataFrame) -> pd.DataFrame:
    """Build hierarchical data for treemap — category > owner."""
    latest_year = df["year"].max()
    latest = df[df["year"] == latest_year].copy()
    latest["owner_label"] = latest["mission_owner_primary_name"].fillna("Other")
    return (
        latest.groupby(["customer_category", "owner_label"])
        .size()
        .reset_index(name="launches")
    )


# ---------------------------------------------------------------------------
# Image 1 — 100% stacked bar with LABELS only (no editorial annotation)
# ---------------------------------------------------------------------------
def pct_bar_labeled_only(yearly_pct: pd.DataFrame) -> None:
    """100% stacked bar with percentage labels but no editorial annotation.

    Kirk Ch 9 distinguishes between LABELING and ANNOTATING:

    LABELING answers: 'What percentage is this segment?'
    - The text on each segment is a label.
    - Labels identify. They tell the reader what something IS.
    - They are necessary but not sufficient for insight.

    At this stage the chart has color (from tutorial_003) and labels,
    but it doesn't TELL THE READER WHAT TO NOTICE. They must find the
    concentration story on their own.
    """
    fig = px.bar(
        yearly_pct,
        x="year",
        y="pct",
        color="customer_category",
        title="SpaceX Customer Mix (2013-2026)",
        labels={"year": "Year", "pct": "Share (%)", "customer_category": "Customer"},
        color_discrete_map=CAT_COLORS,
        category_orders={"customer_category": CAT_ORDER},
    )
    fig.update_layout(
        xaxis=dict(dtick=1),
        yaxis=dict(range=[0, 100]),
        barmode="stack",
        width=1100,
        height=550,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
        ),
    )

    out = IMAGES_DIR / "tutorial_004_image_01_pct_bar_labels_only.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Image 2 — 100% stacked bar with strategic ANNOTATIONS
# ---------------------------------------------------------------------------
def pct_bar_annotated(yearly_pct: pd.DataFrame, df: pd.DataFrame) -> None:
    """100% stacked bar with editorial annotations guiding the reader's eye.

    Kirk Ch 9: ANNOTATING answers: 'What should I notice here?'
    - Annotations are editorial. They carry the author's interpretation.
    - They reduce cognitive load by pointing directly to insight.
    - Strategic means SELECTIVE: annotate the 2-3 most important things.

    Kirk Ch 9 annotation hierarchy (most to least prominent):
    1. Title & subtitle — the first thing read, sets the frame
    2. Direct annotation on the chart — arrows, callout text, reference lines
    3. Axis labels — orient the reader
    4. Footnotes & source — credibility, context

    We annotate THREE strategic elements:
    1. 50% concentration threshold line — the universal "alarm bell" level
    2. The year SpaceX first became majority customer — the inflection
    3. The latest year's SpaceX share — where we are now

    All values are computed from the data so they stay correct on refresh.
    """
    # --- Derive annotation values from data ---
    # Compute SpaceX share per year
    spacex_by_year = (
        yearly_pct[yearly_pct["customer_category"] == "SpaceX (Internal)"]
        .set_index("year")["pct"]
    )

    # Find the first year SpaceX crossed 50%
    over_50 = spacex_by_year[spacex_by_year > 50]
    majority_year = int(over_50.index.min()) if not over_50.empty else None
    majority_pct = round(over_50.iloc[0], 1) if not over_50.empty else 0

    # Latest full year stats
    max_year = int(yearly_pct["year"].max())
    latest_spacex_pct = round(
        spacex_by_year.get(max_year, 0), 1
    )

    # Total SpaceX internal launches
    total_spacex = len(df[df["customer_category"] == "SpaceX (Internal)"])
    total_launches = len(df)

    # First year SpaceX appeared (any self-launch)
    spacex_years = spacex_by_year[spacex_by_year > 0]
    first_spacex_year = int(spacex_years.index.min()) if not spacex_years.empty else None

    fig = px.bar(
        yearly_pct,
        x="year",
        y="pct",
        color="customer_category",
        labels={"year": "Year", "pct": "Share (%)", "customer_category": "Customer"},
        color_discrete_map=CAT_COLORS,
        category_orders={"customer_category": CAT_ORDER},
    )

    # --- Annotation hierarchy level 1: Title & subtitle ---
    # Kirk Ch 9: The title should frame the editorial angle. "Customer Mix"
    # is a label. "From Diversified to Dependent" is annotation — it tells
    # the reader the story before they even read the data.
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
        width=1200,
        height=680,
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

    # --- Annotation hierarchy level 2: Direct callouts ---

    # Annotation 1: 50% concentration threshold — a universal reference level.
    # Kirk Ch 9: Reference lines anchor interpretation. Without the 50% line,
    # the reader must mentally calculate whether the navy band is "a lot".
    # With it, the moment SpaceX crosses the line is unmistakable.
    fig.add_hline(
        y=50,
        line_dash="dash",
        line_color="#999",
        line_width=1.5,
    )
    fig.add_annotation(
        text="50% concentration<br>threshold",
        xref="paper",
        yref="y",
        x=1.02,
        y=50,
        showarrow=False,
        font=dict(size=10, color="#666"),
        xanchor="left",
    )

    # Annotation 2: The year SpaceX became majority customer.
    # Kirk Ch 9: This is the pivotal moment — the year the navy band
    # crosses the 50% line. It transforms SpaceX from "launch provider"
    # to "vertically integrated operator".
    if majority_year is not None:
        fig.add_annotation(
            x=majority_year,
            y=majority_pct / 2,
            text=(
                f"<b>{majority_year}: SpaceX becomes<br>"
                f"majority customer ({majority_pct:.0f}%)</b>"
            ),
            showarrow=True,
            arrowhead=2,
            arrowsize=1.2,
            arrowcolor="#1A237E",
            ax=-90,
            ay=-80,
            font=dict(size=11, color="#1A237E"),
            bgcolor="white",
            bordercolor="#1A237E",
            borderwidth=1,
            borderpad=4,
        )

    # Annotation 3: Latest year's SpaceX share — the current state.
    # Kirk Ch 9: The payoff annotation. After seeing where concentration
    # started and where it crossed the threshold, the reader lands here.
    fig.add_annotation(
        x=max_year,
        y=latest_spacex_pct / 2,
        text=f"<b>{latest_spacex_pct:.0f}%</b><br>SpaceX share",
        showarrow=True,
        arrowhead=2,
        arrowsize=1.2,
        arrowcolor="#1A237E",
        ax=70,
        ay=20,
        font=dict(size=11, color="#1A237E"),
        bgcolor="white",
        bordercolor="#1A237E",
        borderwidth=1,
        borderpad=4,
    )

    # --- Annotation hierarchy level 4: Source attribution ---
    fig.add_annotation(
        text=SOURCE,
        xref="paper",
        yref="paper",
        x=0,
        y=-0.1,
        showarrow=False,
        font=dict(size=9, color="#999"),
    )

    out = IMAGES_DIR / "tutorial_004_image_02_pct_bar_annotated.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Image 3 — Treemap with editorial annotation
# ---------------------------------------------------------------------------
def treemap_annotated(treemap_data: pd.DataFrame, df: pd.DataFrame) -> None:
    """Treemap with editorial title and strategic annotation.

    Kirk Ch 9: The treemap is a spatial chart — the eye immediately sees
    the massive SpaceX rectangle dominating the space. Annotation's job
    here is to name the pattern (concentration) and quantify it.

    Strategy: Use the title to frame the insight. Add a subtitle with
    the key percentage. Treemaps already have built-in text labels
    for each rectangle, so additional callout annotations would clutter.
    The editorial voice lives in the title, not on the chart surface.
    """
    latest_year = int(df["year"].max())
    latest = df[df["year"] == latest_year]
    total = len(latest)
    spacex_count = len(latest[latest["customer_category"] == "SpaceX (Internal)"])
    spacex_pct = spacex_count / total * 100 if total > 0 else 0
    n_customers = latest["mission_owner_primary_name"].nunique()

    fig = px.treemap(
        treemap_data,
        path=["customer_category", "owner_label"],
        values="launches",
        color="customer_category",
        color_discrete_map=CAT_COLORS,
    )

    # Kirk Ch 9: Title is annotation hierarchy level 1.
    # "Customer Composition" is a label. "One Customer Dominates" is
    # annotation — it tells the reader the takeaway.
    fig.update_layout(
        title=dict(
            text=(
                f"One Customer Dominates: SpaceX's {latest_year} Launch Manifest"
                f"<br><sup style='color:#666'>"
                f"{spacex_count} of {total} launches ({spacex_pct:.0f}%) are SpaceX's own "
                f"| {n_customers} distinct customers</sup>"
            ),
            x=0.5,
            xanchor="center",
            font=dict(size=16),
        ),
        width=1100,
        height=650,
        margin=dict(t=100, b=60),
    )

    # Source attribution
    fig.add_annotation(
        text=SOURCE,
        xref="paper",
        yref="paper",
        x=0,
        y=-0.05,
        showarrow=False,
        font=dict(size=9, color="#999"),
    )

    out = IMAGES_DIR / "tutorial_004_image_03_treemap_annotated.png"
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
    yearly_pct, _ = prepare_yearly_pct(df)
    treemap_data = prepare_treemap_data(df)

    print("=" * 60)
    print("ANNOTATION — Kirk Ch 9: Annotation")
    print("=" * 60)
    print()

    # --- Demonstrate labeling vs annotating ---
    print("LABELING vs ANNOTATING")
    print("-" * 40)
    print()
    pct_bar_labeled_only(yearly_pct)
    print("  Labels only: the reader sees percentages but must interpret alone.")
    print()
    pct_bar_annotated(yearly_pct, df)
    print("  Annotated: the reader is guided to threshold, inflection, and peak.")
    print()

    # --- Treemap annotation ---
    print("TREEMAP ANNOTATION")
    print("-" * 40)
    print()
    treemap_annotated(treemap_data, df)
    print("  Title frames the dominance story; subtitle quantifies it.")
    print("  On spatial charts, the title does the annotation work.")
    print()

    # --- Summary ---
    print("=" * 60)
    print("ANNOTATION DECISIONS SUMMARY")
    print("=" * 60)
    print("""
KIRK CH 9 ANNOTATION HIERARCHY APPLIED:

1. TITLE & SUBTITLE (most prominent):
   - Stacked bar: "From Diversified to Dependent"
     -> Editorial, not descriptive. Names the transformation.
     -> Subtitle quantifies: "X of Y completed launches are SpaceX's own"
   - Treemap: "One Customer Dominates"
     -> Frames the spatial pattern before the reader reads any labels.

2. DIRECT ANNOTATIONS (strategic callouts on the stacked bar):
   - 50% concentration threshold — a horizontal reference line that
     anchors interpretation. The reader instantly sees which years are
     above/below the alarm level.
   - Majority year — the inflection point where SpaceX crosses 50%.
     This is the editorial moment: "launch provider becomes operator."
   - Latest year share — the current state, the payoff of the trend.
   -> All values computed dynamically from data.

3. AXIS LABELS (orientation):
   - Year and Share (%) on the stacked bar.
   - Built-in rectangle labels on the treemap.

4. SOURCE ATTRIBUTION (credibility):
   - "Launch Library 2 API | thespacedevs.com" on both charts.

LABELING vs ANNOTATING:

  LABELING = "This segment is 59%"
  -> Identifies the value. Necessary for precision.

  ANNOTATING = "SpaceX becomes majority customer (59%)"
  -> Interprets the value. Tells the reader what's significant.

  The 50% threshold line is pure annotation — it doesn't show any
  data value, it shows an INTERPRETATION FRAMEWORK. Without it, the
  reader must mentally calculate whether 59% is "a lot." With it,
  the crossing moment is unmistakable.

DOMAIN TRANSFER:

  Insurance professionals building portfolio dashboards face the same
  choice. A pie chart showing client concentration with just labels
  forces the reviewer to do the interpretation. Adding a reference
  line at the Solvency II threshold (e.g., 10% single-name exposure)
  turns a chart into a regulatory brief.
""")


if __name__ == "__main__":
    main()
