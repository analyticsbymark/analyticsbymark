"""
What You'll Learn
=================
- How to apply intentional, meaningful color to a chart that already works
- Kirk Chapter 10: Color — encoding data, highlighting, guiding attention
- Why qualitative palettes suit categorical data (rocket families)
- Colorblind safety: differ in hue AND lightness across 3 categories
- How color makes a three-act narrative visible without annotation
- Output: Before/after comparison of the winning failure timeline scatter
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

# Kirk Ch 10: Color should carry meaning, not just decoration.
#
# We are coloring by ROCKET FAMILY — a qualitative (categorical) variable.
# The three families represent three distinct lifecycle chapters:
#   Falcon 1    → SpaceX's development era (2006-2008)
#   Falcon 9    → Operational maturity era (2012-2024)
#   Starship    → New vehicle development era (2020-2025)
#
# PALETTE RATIONALE:
#   - Qualitative palette: the families are categorical, NOT ordered.
#     A sequential or diverging palette would imply order that doesn't exist.
#   - Red for Falcon 1: culturally appropriate for the earliest, most
#     volatile phase. We ARE studying failures — red is honest here, but
#     it belongs to one family, not every data point.
#   - Steel blue for Falcon 9: calm, stable, professional — matches the
#     maturity story of SpaceX's workhorse vehicle.
#   - Amber/gold for Starship: distinct from both red and blue; warm but
#     not alarming. Starship failures are expected (development era) rather
#     than anomalous.
#   - Colorblind safety: the three colors differ in BOTH hue and lightness.
#     Falcon 1 (#C0392B, medium-dark red) vs. Falcon 9 (#2980B9, medium blue)
#     vs. Starship (#D4A017, medium-light amber) — distinguishable under
#     deuteranopia because red and blue differ in brightness and the amber
#     is lighter than both.
ROCKET_FAMILY_COLORS = {
    "Falcon 1": "#C0392B",   # Muted red — development era volatility
    "Falcon 9": "#2980B9",   # Steel blue — operational maturity
    "Starship": "#D4A017",   # Amber/gold — new vehicle development era
}

# Mapping rocket full names to the three families.
# This groups variants without hardcoding counts.
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
    completed = df[df["launch_status_abbrev"].isin(["Success", "Failure", "Partial Failure"])].copy()
    # Sort chronologically — essential for timeline charts
    completed = completed.sort_values("net").reset_index(drop=True)
    return completed


def prepare_failures(df: pd.DataFrame) -> pd.DataFrame:
    """Extract failure and partial failure events and assign rocket families.

    The rocket family assignment groups variants (e.g., Falcon 9 v1.0,
    Falcon 9 v1.1, Falcon 9 Full Thrust, Falcon 9 Block 5) into a single
    family label. This makes the three-act lifecycle structure visible in
    the color encoding without requiring text annotation.

    Kirk Ch 10: Color that encodes categorical structure tells a story.
    Any rocket_full_name not in ROCKET_FAMILY_MAP falls back to the
    value itself, so new vehicles are visible rather than silently dropped.
    """
    failures = df[df["launch_status_abbrev"].isin(FAILURE_STATUSES)].copy()
    failures["rocket_family_group"] = failures["rocket_full_name"].map(
        ROCKET_FAMILY_MAP
    ).fillna(failures["rocket_full_name"])
    return failures


# ---------------------------------------------------------------------------
# Image 01 — Before: failure timeline scatter with default Plotly colors
# ---------------------------------------------------------------------------
def scatter_before(failures: pd.DataFrame) -> None:
    """Failure timeline scatter with Plotly's default color scheme.

    Kirk Ch 10: Default colors are chosen for general-purpose safety, not
    for your specific editorial message. Plotly assigns colors from a
    qualitative cycle (blues, reds, greens) based on category order — not
    based on any meaning in the data.

    Here the two categories are 'Failure' and 'Partial Failure'. Plotly's
    defaults happen to assign blue and red, which have some intuitive
    mapping to severity — but this is accidental, not intentional.
    More importantly, coloring by *outcome* hides the rocket family
    structure that tells the three-act reliability story.
    """
    fig = px.scatter(
        failures,
        x="net",
        y="launch_status_abbrev",
        color="launch_status_abbrev",
        hover_name="mission_name",
        hover_data={
            "rocket_full_name": True,
            "net": True,
            "launch_status_abbrev": True,
        },
        title="BEFORE: Default Plotly Colors — Failure Timeline Scatter",
        labels={
            "net": "Launch Date",
            "launch_status_abbrev": "Outcome",
            "rocket_full_name": "Rocket",
        },
    )
    fig.update_layout(
        width=1200,
        height=400,
        xaxis_title="Launch Date",
        yaxis_title="Outcome",
        legend_title_text="Outcome",
    )
    fig.update_traces(marker=dict(size=12))

    out = IMAGES_DIR / "tutorial_003_image_01_scatter_before.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Image 02 — After: failure timeline scatter with rocket family color encoding
# ---------------------------------------------------------------------------
def scatter_after(failures: pd.DataFrame) -> None:
    """Failure timeline scatter with intentional rocket family color encoding.

    Kirk Ch 10: 'Use color to encode data, not to decorate.'
    Here color does three things simultaneously:
      1. Identifies which rocket family each failure belongs to
      2. Makes the three lifecycle phases visible as distinct color clusters
      3. Guides the reader's eye to the three-act structure without annotation

    WHY QUALITATIVE (not sequential or diverging):
    - Rocket families are categorical — they have no inherent order or
      numeric scale. A sequential palette (light → dark) would falsely
      imply that Starship > Falcon 9 > Falcon 1 on some scale. It doesn't.
    - A diverging palette implies deviation from a midpoint. There is no
      meaningful midpoint between three vehicle families.
    - Qualitative is the only correct choice for unordered categories.

    WHY THESE THREE COLORS:
    - Falcon 1 in muted red (#C0392B): SpaceX's first vehicle, its
      failures were a rite of passage. Red is culturally associated with
      caution/early-stage risk — appropriate and honest for development-era
      failures. Red appears only for Falcon 1, not for all failures.
    - Falcon 9 in steel blue (#2980B9): The workhorse vehicle. Blue
      connotes stability and professionalism — matching the vehicle's
      earned reputation for reliability after the early learning curve.
    - Starship in amber/gold (#D4A017): Distinct from both red and blue.
      Warm but not alarming — Starship failures are expected developmental
      events, not operational anomalies. Gold references ambition and
      frontier exploration, fitting for SpaceX's most ambitious program.

    COLORBLIND SAFETY (three hues with hue AND lightness variation):
    - Muted red (#C0392B) has relative luminance ~0.08 (dark)
    - Steel blue (#2980B9) has relative luminance ~0.13 (medium)
    - Amber (#D4A017) has relative luminance ~0.47 (light)
    Under deuteranopia (most common, ~8% of males), red and green collapse
    but red and BLUE remain distinguishable by both hue and luminance.
    Amber is the lightest of the three, making it separable from both
    the dark red and medium blue even under full desaturation.
    """
    # Kirk Ch 10: category_orders controls legend sequence — put it in
    # chronological lifecycle order, not alphabetical.
    lifecycle_order = ["Falcon 1", "Falcon 9", "Starship"]

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
        title="AFTER: Rocket Family Color — Three Lifecycle Acts Visible",
        labels={
            "net": "Launch Date",
            "launch_status_abbrev": "Outcome",
            "rocket_full_name": "Rocket Variant",
            "rocket_family_group": "Rocket Family",
        },
        color_discrete_map=ROCKET_FAMILY_COLORS,
        category_orders={"rocket_family_group": lifecycle_order},
    )
    fig.update_layout(
        width=1200,
        height=400,
        xaxis_title="Launch Date",
        yaxis_title="Outcome",
        legend_title_text="Rocket Family",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.05,
            xanchor="center",
            x=0.5,
        ),
    )
    fig.update_traces(marker=dict(size=12))

    out = IMAGES_DIR / "tutorial_003_image_02_scatter_after.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Color decisions summary printer
# ---------------------------------------------------------------------------
def print_color_decisions(failures: pd.DataFrame) -> None:
    """Print a structured summary of all color design decisions made.

    Kirk Ch 10: Being explicit about WHY you chose each color is as
    important as the choice itself. It builds trust with your audience
    and makes the rationale auditable if a stakeholder pushes back.
    """
    family_counts = failures["rocket_family_group"].value_counts()

    print()
    print("=" * 60)
    print("COLOR DECISIONS SUMMARY — Kirk Ch 10: Color")
    print("=" * 60)

    print("""
SCALE TYPE: Qualitative (distinct hues, no implied order)

RATIONALE:
  Rocket families are categorical — there is no numeric scale or
  inherent ordering between Falcon 1, Falcon 9, and Starship.
  A sequential palette would imply rank; a diverging palette would
  imply deviation from a midpoint. Neither applies here.
  Qualitative is the only correct scale type for unordered categories.

WHAT THE COLOR ENCODES:
  Color maps to rocket FAMILY, not to launch outcome. This is a
  deliberate editorial choice: coloring by outcome (Failure vs.
  Partial Failure) answers 'how severe?' — but our curiosity question
  asks 'which lifecycle phase?' Color by family answers the right question.

PALETTE:""")

    for family, color in ROCKET_FAMILY_COLORS.items():
        count = family_counts.get(family, 0)
        print(f"  {family:<14}  {color}  ({count} failure events)")

    print(f"""
COLORBLIND SAFETY:
  Three colors, three different hues AND three different luminance levels:
  - Falcon 1  (#C0392B): dark muted red      — relative luminance ~0.08
  - Falcon 9  (#2980B9): medium steel blue   — relative luminance ~0.13
  - Starship  (#D4A017): light amber/gold    — relative luminance ~0.47
  Under deuteranopia (red-green, the most common form at ~8% of males),
  red and blue remain distinguishable via luminance difference.
  Amber is the lightest, separable from both under full desaturation.

CULTURAL CONSIDERATIONS:
  - Red for Falcon 1: Red is appropriate — these ARE failures, and Falcon 1
    was the highest-risk phase. But red belongs to ONE family, not to all
    {len(failures)} failure points. This distinction matters: the previous chart
    (tutorial_002) used unstyled defaults. Putting red everywhere says
    'everything is bad'; red for Falcon 1 only says 'this era was different'.
  - Blue for Falcon 9: Connotes stability and trust — matching the earned
    reputation of SpaceX's operational workhorse.
  - Amber for Starship: Warm but not alarming. Starship failures are
    developmental events — anticipated, not anomalous.

THREE-ACT STRUCTURE — made visible by color:
  Act 1 (red cluster, 2006-2008): Falcon 1's development trials.
         Three early failures, rapid iteration, then orbital success.
  Act 2 (blue cluster, 2012-2016): Falcon 9's growing pains.
         Early variants learning from each failure; then a long gap.
  Act 3 (amber cluster, 2020-2025): Starship's development arc.
         A new vehicle repeating the learning curve, by design.
  The timeline's whitespace — the gap between Acts 2 and 3 — shows
  that Falcon 9 Block 5 achieved near-perfect operational reliability.
  Color makes each act legible without a single text annotation.
""")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    """Run the color design process for the winning failure timeline scatter.

    Kirk Ch 10: 'Color is the most emotionally evocative of all visual
    variables, but it is also the most abused.' Our goal is to use color
    with restraint and purpose — every hue choice must be justifiable.

    This tutorial takes the winning chart from tutorial_002 (the failure
    timeline scatter) and applies intentional color encoding by rocket family.
    The result makes SpaceX's three-act reliability story immediately visible
    without any annotations or additional chart elements.
    """
    df = load_and_filter()
    failures = prepare_failures(df)

    # Compute editorial context from data — never hardcoded
    total = len(df)
    n_success = (df["launch_status_abbrev"] == "Success").sum()
    overall_rate = n_success / total * 100
    n_failures = len(failures)
    family_order = ["Falcon 1", "Falcon 9", "Starship"]

    print("=" * 60)
    print("COLOR DESIGN — Kirk Ch 10: Color")
    print("=" * 60)
    print()
    print("Curiosity question:")
    print("  What does SpaceX's failure timeline reveal about how rapidly")
    print("  a launch provider builds — and sustains — operational reliability?")
    print()
    print(f"Dataset: {total} completed launches, {n_failures} failures/partial failures")
    print(f"  Overall success rate: {overall_rate:.1f}%")
    print()
    print("Rocket family groups assigned:")
    for family in family_order:
        count = (failures["rocket_family_group"] == family).sum()
        variants = sorted(
            failures.loc[failures["rocket_family_group"] == family, "rocket_full_name"].unique()
        )
        print(f"  {family:<14}  {count} events  {variants}")
    print()
    print("Rendering before/after images...")
    print()

    # --- Image 01: Before (default colors) ---
    print("Image 01 — BEFORE (default Plotly colors):")
    scatter_before(failures)
    print("  Color-by-outcome: accidental, not editorial. Hides lifecycle structure.")
    print()

    # --- Image 02: After (rocket family color encoding) ---
    print("Image 02 — AFTER (rocket family color encoding):")
    scatter_after(failures)
    print("  Color-by-family: three acts visible at a glance. Intentional, justifiable.")
    print()

    # --- Print full color decisions summary ---
    print_color_decisions(failures)


if __name__ == "__main__":
    main()
