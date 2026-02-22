"""
What You'll Learn
=================
- How to move from default Plotly colors to intentional, meaningful palettes
- Kirk Chapter 10: Color — encoding data, highlighting, guiding attention
- Sequential vs diverging vs qualitative: when to use each
- Colorblind accessibility: why it matters and how to check
- Output: Before/after comparisons for both winning charts
"""

import sys
from pathlib import Path

# Ensure the parent directory is on the path so `from data.utils import ...` works
# when this script is run directly from the launch_cadence/ folder.
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

# Kirk Ch 10: Color should carry meaning, not just decoration.
# Our acceleration story has three phases — color should reinforce them.
PHASE_COLORS = {
    "Startup (2006-2013)": "#B0BEC5",   # Cool gray — proving the concept
    "Growth (2014-2019)": "#42A5F5",     # Medium blue — steady climb
    "Hyperscale (2020+)": "#0D47A1",     # Deep blue — exponential era
}

# A single-hue sequential palette for the heatmap.
# Kirk Ch 10: Sequential scales map naturally to "more = darker/more intense".
# We use a blue ramp that's distinguishable under the most common forms of
# color vision deficiency (deuteranopia, protanopia).
HEATMAP_SCALE = [
    [0.0, "#F5F5F5"],   # Near-white for zero launches
    [0.15, "#BBDEFB"],  # Very light blue
    [0.35, "#64B5F6"],  # Light blue
    [0.55, "#2196F3"],  # Medium blue
    [0.75, "#1565C0"],  # Deep blue
    [1.0, "#0D47A1"],   # Darkest blue
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

    # Assign each year to an acceleration phase for color encoding.
    # Kirk Ch 10: Color that carries editorial meaning is more powerful
    # than color that's merely decorative.
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
    """Create year × month pivot for heatmap."""
    pivot = df.pivot_table(
        index="year", columns="month", aggfunc="size", fill_value=0
    )
    for m in range(1, 13):
        if m not in pivot.columns:
            pivot[m] = 0
    return pivot[range(1, 13)]


# ---------------------------------------------------------------------------
# Image 1 — Bar chart BEFORE (default Plotly colors)
# ---------------------------------------------------------------------------
def bar_before(yearly: pd.DataFrame) -> None:
    """Bar chart with default Plotly styling — the 'before' baseline.

    Kirk Ch 10: Default colors are chosen for general-purpose safety, not
    for your specific editorial message. The uniform blue says nothing
    about the three phases of acceleration.
    """
    fig = px.bar(
        yearly,
        x="year",
        y="launches",
        title="BEFORE: Default Plotly Colors — Bar Chart",
        labels={"year": "Year", "launches": "Launches"},
    )
    fig.update_layout(xaxis=dict(dtick=1), width=1000, height=500)

    out = IMAGES_DIR / "tutorial_003_image_01_bar_before.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Image 2 — Bar chart AFTER (phase-based color encoding)
# ---------------------------------------------------------------------------
def bar_after(yearly: pd.DataFrame) -> None:
    """Bar chart with intentional phase-based color encoding.

    Kirk Ch 10: We're using color as a *data encoding* channel, not just
    aesthetics. Each phase gets a distinct shade within the same blue hue
    family. This is a deliberate choice:

    WHY SEQUENTIAL BLUE (not qualitative/rainbow):
    - The phases are ORDERED (startup < growth < hyperscale), so color
      intensity should increase with the phase. A qualitative palette
      (red, green, blue) would imply categories without order.
    - Blue is culturally neutral in a business context — no positive/
      negative connotation (unlike red/green which implies loss/gain).
    - A single-hue ramp is the safest choice for colorblind readers,
      because it relies on lightness variation rather than hue.

    WHY NOT diverging:
    - Diverging palettes (e.g., red-white-blue) encode deviation from a
      midpoint. Our data has no meaningful midpoint — it's a one-directional
      growth story.
    """
    # Build color mapping: phase label → hex color
    color_map = PHASE_COLORS

    fig = px.bar(
        yearly,
        x="year",
        y="launches",
        color="phase",
        title="AFTER: Phase-Based Color — Acceleration Eras",
        labels={"year": "Year", "launches": "Launches", "phase": "Phase"},
        color_discrete_map=color_map,
        category_orders={"phase": list(color_map.keys())},
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

    out = IMAGES_DIR / "tutorial_003_image_02_bar_after.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Image 3 — Heatmap BEFORE (default Plotly colors)
# ---------------------------------------------------------------------------
def heatmap_before(pivot: pd.DataFrame) -> None:
    """Heatmap with default Plotly imshow colors — the 'before' baseline.

    Kirk Ch 10: Plotly's default continuous scale is often 'Viridis' or
    similar. While technically colorblind-safe, it may not match the
    editorial tone of a professional report. The purple-to-yellow range
    can feel noisy when the audience expects restrained business styling.
    """
    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    fig = px.imshow(
        pivot.values,
        x=month_labels,
        y=[str(y) for y in pivot.index],
        title="BEFORE: Default Colors — Monthly Heatmap",
        labels=dict(x="Month", y="Year", color="Launches"),
        aspect="auto",
    )
    fig.update_layout(width=900, height=600)

    out = IMAGES_DIR / "tutorial_003_image_03_heatmap_before.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Image 4 — Heatmap AFTER (intentional sequential blue)
# ---------------------------------------------------------------------------
def heatmap_after(pivot: pd.DataFrame) -> None:
    """Heatmap with intentional sequential blue palette.

    Kirk Ch 10: For the heatmap, color IS the primary data encoding — there
    is no bar length or line slope to carry the message. This makes the
    palette choice even more critical.

    WHY SEQUENTIAL SINGLE-HUE BLUE:
    - The data is a count (0 to ~17) with a natural zero. Sequential is the
      only correct scale type here — there's no midpoint, no divergence.
    - Using the same blue family as the bar chart creates visual consistency
      across the tutorial series. Kirk Ch 10: consistency in color builds
      trust and reduces cognitive load.
    - Near-white for zero cells makes empty months immediately visible,
      reinforcing the "sporadic → continuous" subplot.

    COLORBLIND SAFETY:
    - Single-hue ramps are inherently safe for all common forms of color
      vision deficiency because they rely on LIGHTNESS, not HUE.
    - The darkest value (#0D47A1) and lightest (#F5F5F5) have a luminance
      ratio of approximately 8:1 — well above the 3:1 minimum for
      distinguishable data encodings.
    """
    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    fig = px.imshow(
        pivot.values,
        x=month_labels,
        y=[str(y) for y in pivot.index],
        color_continuous_scale=HEATMAP_SCALE,
        title="AFTER: Sequential Blue — Monthly Heatmap",
        labels=dict(x="Month", y="Year", color="Launches"),
        aspect="auto",
    )
    fig.update_layout(width=900, height=600)

    out = IMAGES_DIR / "tutorial_003_image_04_heatmap_after.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    """Run the color design process for both winning charts.

    Kirk Ch 10: 'Color is the most emotionally evocative of all visual
    variables, but it is also the most abused.' Our goal is to use color
    with restraint and purpose — every hue choice should be justifiable.
    """
    df = load_and_filter()
    yearly = prepare_yearly(df)
    pivot = prepare_monthly_pivot(df)

    print("=" * 60)
    print("COLOR DESIGN — Kirk Ch 10: Color")
    print("=" * 60)
    print()

    # --- Bar chart: before / after ---
    print("PRIMARY CHART: Yearly Bar Chart")
    print("-" * 40)
    bar_before(yearly)
    print("  Default: uniform blue, no editorial meaning in color.")
    print()
    bar_after(yearly)
    print("  After: three-phase blue ramp encodes acceleration eras.")
    print("  Gray (startup) → medium blue (growth) → deep blue (hyperscale).")
    print()

    # --- Heatmap: before / after ---
    print("SECONDARY CHART: Monthly Heatmap")
    print("-" * 40)
    heatmap_before(pivot)
    print("  Default: Plotly's built-in scale — functional but not editorial.")
    print()
    heatmap_after(pivot)
    print("  After: single-hue blue ramp, white for zeros, consistent with bar chart.")
    print()

    # --- Summary ---
    print("=" * 60)
    print("COLOR DECISIONS SUMMARY")
    print("=" * 60)
    print("""
SCALE TYPE: Sequential (single-hue blue ramp)

RATIONALE:
  - Our data is ordered and one-directional (more launches = more intense).
    Sequential is the correct scale type. Diverging would imply a midpoint
    that doesn't exist. Qualitative would lose the ordered relationship.

PALETTE: Blue family (#B0BEC5 → #42A5F5 → #0D47A1)

  - Blue is culturally neutral in business contexts — no gain/loss
    connotation. This matters for our insurance professional audience
    who associate red with losses and green with profits.
  - The three shades are perceptually distinct even when desaturated
    to grayscale, which is the gold standard for colorblind safety.

COLORBLIND ACCESSIBILITY:

  - Single-hue ramps rely on LIGHTNESS rather than HUE variation.
    This makes them safe for deuteranopia (red-green, ~8% of males),
    protanopia (red deficiency), and tritanopia (blue-yellow, rare).
  - The bar chart's phase coloring also uses a muted gray (#B0BEC5)
    as the lowest phase, which is distinguishable from the blue phases
    even under full achromatopsia (total color blindness).
  - If you need to verify: Plotly charts can be tested with browser-
    based colorblind simulators (e.g., Chrome DevTools > Rendering >
    Emulate vision deficiencies).

CULTURAL CONSIDERATIONS:

  - We avoided red and green entirely. In Western business contexts,
    red = danger/loss and green = growth/profit. Our story is about
    acceleration (positive), but using green could feel misleading
    if the audience unconsciously maps it to financial performance.
  - Blue connotes trust, stability, and professionalism — appropriate
    for a technical tutorial aimed at insurance professionals.

CONSISTENCY:

  - Both charts share the same blue family. Kirk Ch 10: using a
    consistent palette across a multi-chart composition reduces
    cognitive load and builds visual coherence. The reader doesn't
    need to re-learn the color mapping between charts.
""")


if __name__ == "__main__":
    main()
