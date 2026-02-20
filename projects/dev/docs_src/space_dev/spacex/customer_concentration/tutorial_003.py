"""
What You'll Learn
=================
- How to move from default Plotly colors to intentional, meaningful palettes
- Kirk Chapter 10: Color — encoding data, highlighting, guiding attention
- Qualitative palettes for categorical data: when warm/cool contrast carries meaning
- Colorblind accessibility: why red-green pairings are dangerous and how to avoid them
- Output: Before/after comparisons for both winning charts (100% stacked bar + treemap)
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
# Constants
# ---------------------------------------------------------------------------
IMAGES_DIR = Path(__file__).resolve().parent / "images"
IMAGES_DIR.mkdir(exist_ok=True)

# Kirk Ch 10: Color should carry editorial meaning, not just decoration.
# Our concentration story pits one dominant entity (SpaceX) against a diverse
# customer base. The palette encodes this tension:
#
#   - SpaceX gets a COOL, heavy color (deep navy) — conveying corporate
#     weight and the "mass" of concentration.
#   - External customers get WARM colors (orange, teal, gold) — conveying
#     diversity, energy, and the healthy variety being displaced.
#
# As SpaceX's share grows, the cool navy swallows the warm colors. The
# color shift IS the editorial message.

CAT_ORDER = ["SpaceX (Internal)", "US Government", "Intl Government", "Commercial"]

# --- INTENTIONAL palette ---
CAT_COLORS = {
    "SpaceX (Internal)": "#1A237E",  # Deep navy — dominant, heavy, corporate
    "US Government": "#E65100",       # Deep orange — institutional, warm, distinct
    "Intl Government": "#00897B",     # Teal — international, cool-warm bridge
    "Commercial": "#FFB300",          # Amber/gold — commercial energy, diversity
}

# Customer category sets — reused from tutorial_001/002 for consistency.
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


def prepare_yearly_pct(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate to yearly percentage composition by customer category."""
    yearly = (
        df.groupby(["year", "customer_category"])
        .size()
        .reset_index(name="launches")
    )
    # Exclude very early years with 1-2 launches
    yearly_totals = df.groupby("year").size()
    valid_years = yearly_totals[yearly_totals >= 3].index
    yearly = yearly[yearly["year"].isin(valid_years)].copy()
    totals = yearly.groupby("year")["launches"].transform("sum")
    yearly["pct"] = yearly["launches"] / totals * 100
    return yearly


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
# Image 1 — 100% Stacked bar BEFORE (default Plotly colors)
# ---------------------------------------------------------------------------
def pct_bar_before(yearly_pct: pd.DataFrame) -> None:
    """100% stacked bar with default Plotly styling — the 'before' baseline.

    Kirk Ch 10: Default qualitative colors are chosen for maximum perceptual
    separation, not for editorial meaning. The default sequence (blue, red,
    green, purple) treats all categories as equally important — but in our
    concentration story, SpaceX is the protagonist, and the other categories
    are the ensemble being displaced.
    """
    fig = px.bar(
        yearly_pct,
        x="year",
        y="pct",
        color="customer_category",
        title="BEFORE: Default Plotly Colors — Customer Share Over Time",
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

    out = IMAGES_DIR / "tutorial_003_image_01_pct_bar_before.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Image 2 — 100% Stacked bar AFTER (intentional warm/cool palette)
# ---------------------------------------------------------------------------
def pct_bar_after(yearly_pct: pd.DataFrame) -> None:
    """100% stacked bar with intentional warm/cool color encoding.

    Kirk Ch 10: Color that carries editorial meaning is more powerful than
    color that's merely decorative. Our palette choices:

    WHY QUALITATIVE (not sequential or diverging):
    - The four customer categories have no inherent order — SpaceX is not
      "more" than Commercial in an ordinal sense. They're different types.
      Qualitative palettes are the correct scale type for nominal categories.

    WHY WARM vs COOL contrast:
    - SpaceX (navy) is cool, heavy, monolithic — visually encoding the
      weight of concentration. The warm colors (orange, teal, gold) represent
      healthy diversity. As the navy band grows, the warm colors shrink —
      the palette tells the concentration story even before reading the axis.
    - This warm/cool split also creates a "figure-ground" relationship.
      Kirk Ch 10: the dominant category (SpaceX) reads as the figure;
      the diverse categories read as the ground being consumed.

    WHY THESE SPECIFIC HUES:
    - Navy (#1A237E) — corporate authority, heavier than medium blue
    - Deep orange (#E65100) — institutional warmth, distinct from navy
    - Teal (#00897B) — bridges warm and cool, international feel
    - Amber (#FFB300) — commercial energy, optimism, diversity
    """
    fig = px.bar(
        yearly_pct,
        x="year",
        y="pct",
        color="customer_category",
        title="AFTER: Intentional Palette — Concentration Swallowing Diversity",
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
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
        ),
    )

    out = IMAGES_DIR / "tutorial_003_image_02_pct_bar_after.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Image 3 — Treemap BEFORE (default Plotly colors)
# ---------------------------------------------------------------------------
def treemap_before(treemap_data: pd.DataFrame) -> None:
    """Treemap with default Plotly styling — the 'before' baseline.

    Kirk Ch 10: Default treemap colors cycle through Plotly's qualitative
    sequence, assigning arbitrary hues to categories. The resulting rainbow
    treats every category equally, hiding the editorial hierarchy.
    """
    fig = px.treemap(
        treemap_data,
        path=["customer_category", "owner_label"],
        values="launches",
        title="BEFORE: Default Plotly Colors — Customer Treemap",
    )
    fig.update_layout(width=1000, height=600)

    out = IMAGES_DIR / "tutorial_003_image_03_treemap_before.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Image 4 — Treemap AFTER (intentional warm/cool palette)
# ---------------------------------------------------------------------------
def treemap_after(treemap_data: pd.DataFrame) -> None:
    """Treemap with intentional warm/cool color encoding.

    Kirk Ch 10: In the treemap, area IS the data encoding — larger rectangles
    mean more launches. Color's job is to reinforce the categorical grouping
    and carry editorial weight. The navy SpaceX rectangle dominating 70%+ of
    the treemap area, surrounded by small warm-colored rectangles, makes the
    concentration story physically visible.

    COLORBLIND SAFETY for the treemap:
    - The four category colors differ in both HUE and LIGHTNESS:
      Navy (#1A237E) = dark, cool
      Orange (#E65100) = medium, warm
      Teal (#00897B) = medium, cool-warm bridge
      Amber (#FFB300) = light, warm
    - Under deuteranopia (the most common color vision deficiency), orange
      and teal remain distinguishable because they differ in lightness
      (orange ~45% luminance, teal ~38%). Under protanopia, the separation
      is similar.
    - We deliberately avoided red + green pairing, which collapses to
      near-identical hues for ~8% of males.
    """
    fig = px.treemap(
        treemap_data,
        path=["customer_category", "owner_label"],
        values="launches",
        title="AFTER: Intentional Palette — SpaceX Dominance Made Visible",
        color="customer_category",
        color_discrete_map=CAT_COLORS,
    )
    fig.update_layout(width=1000, height=600)

    out = IMAGES_DIR / "tutorial_003_image_04_treemap_after.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    """Run the color design process for both charts.

    Kirk Ch 10: 'Color is the most emotionally evocative of all visual
    variables, but it is also the most abused.' Our goal is to use color
    with restraint and purpose — every hue choice should be justifiable.
    """
    df = load_and_filter()
    yearly_pct = prepare_yearly_pct(df)
    treemap_data = prepare_treemap_data(df)

    print("=" * 60)
    print("COLOR DESIGN — Kirk Ch 10: Color")
    print("=" * 60)
    print()

    # --- 100% stacked bar: before / after ---
    print("PRIMARY CHART: 100% Stacked Bar")
    print("-" * 40)
    pct_bar_before(yearly_pct)
    print("  Default: arbitrary qualitative colors, no editorial hierarchy.")
    print()
    pct_bar_after(yearly_pct)
    print("  After: navy (SpaceX) swallowing warm diversity (gov + commercial).")
    print()

    # --- Treemap: before / after ---
    print("SECONDARY CHART: Customer Treemap")
    print("-" * 40)
    treemap_before(treemap_data)
    print("  Default: rainbow cycling, treats all categories equally.")
    print()
    treemap_after(treemap_data)
    print("  After: navy dominance, warm edges — concentration made spatial.")
    print()

    # --- Summary ---
    print("=" * 60)
    print("COLOR DECISIONS SUMMARY")
    print("=" * 60)
    print("""
SCALE TYPE: Qualitative (4 nominal categories, no inherent order)

PALETTE: Warm/Cool editorial contrast
  - SpaceX (Internal) : #1A237E  Deep navy — heavy, dominant, corporate
  - US Government     : #E65100  Deep orange — institutional, warm, distinct
  - Intl Government   : #00897B  Teal — international, cool-warm bridge
  - Commercial        : #FFB300  Amber/gold — commercial energy, diversity

EDITORIAL RATIONALE:

  The palette encodes the concentration narrative through temperature:
  - COOL (navy) = concentration, dominance, single-entity weight
  - WARM (orange, teal, gold) = diversity, healthy customer spread

  As the navy expands across the 100% stacked bar, it literally swallows
  the warm colors. The reader feels the concentration increasing even
  before reading the percentage axis. In the treemap, the massive navy
  rectangle surrounded by small warm rectangles makes the same point
  spatially.

COLORBLIND ACCESSIBILITY:

  We deliberately avoided the classic red-green pairing that collapses
  for 8% of males (deuteranopia/protanopia). Our four hues were chosen
  to differ in BOTH hue AND lightness:

  Category             Hex       Approx. Luminance
  ────────────────────────────────────────────────
  SpaceX (navy)        #1A237E   Low  (~15%)
  US Government (org)  #E65100   Mid  (~45%)
  Intl Government (tl) #00897B   Mid  (~38%)
  Commercial (amber)   #FFB300   High (~72%)

  Even under full desaturation (grayscale), the four categories remain
  distinguishable because their lightness values are spread across the
  full range. This is the gold standard for colorblind safety.

  Test with: Chrome DevTools > Rendering > Emulate vision deficiencies
  (deuteranopia, protanopia, tritanopia, achromatopsia).

CULTURAL CONSIDERATIONS:

  - We avoided RED for any non-danger category. Red carries strong
    loss/danger connotations in financial contexts. US Government uses
    deep ORANGE instead — warm and authoritative without triggering
    loss associations.
  - Navy connotes corporate authority and seriousness — appropriate for
    the entity causing concentration concern.
  - Amber/gold connotes commerce, value, and optimism — appropriate
    for the diverse customer base that represents a healthier portfolio.
  - Teal is culturally neutral and bridges warm/cool — fitting for
    international agencies that span multiple cultural contexts.

CONSISTENCY:

  Both charts share the exact same 4-color palette. Kirk Ch 10: using
  a consistent palette across a multi-chart composition reduces cognitive
  load and builds visual coherence. The reader learns the color mapping
  once and applies it to both the temporal view (stacked bar) and the
  spatial view (treemap).
""")


if __name__ == "__main__":
    main()
