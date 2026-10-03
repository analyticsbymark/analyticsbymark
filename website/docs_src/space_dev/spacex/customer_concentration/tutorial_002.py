"""
What You'll Learn
=================
- How to iterate through chart types to find the best fit for a concentration story
- Kirk Chapter 7: Data Representation — choosing the right chart for data + message
- The process of selection IS the lesson: try, evaluate, decide
- Output: 4 chart candidates evaluated, 1 winner declared
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

# Customer category sets — reused from tutorial_001 so classifications are
# consistent across the series.
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
# Data loading (reuse the same filter and categorisation from tutorial_001)
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
    """Classify each launch into a customer category.

    Same logic as tutorial_001 — kept here so each tutorial is independently
    runnable without importing from sibling scripts.
    """
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


def prepare_yearly_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate to yearly counts per customer category."""
    yearly = (
        df.groupby(["year", "customer_category"])
        .size()
        .reset_index(name="launches")
    )
    # Exclude very early years with 1-2 launches (noisy for percentage charts)
    yearly_totals = df.groupby("year").size()
    valid_years = yearly_totals[yearly_totals >= 3].index
    return yearly[yearly["year"].isin(valid_years)]


# Category order and colours — consistent across all candidates so the
# reader focuses on chart type differences, not colour differences.
CAT_ORDER = ["SpaceX (Internal)", "US Government", "Intl Government", "Commercial"]
CAT_COLORS = {
    "SpaceX (Internal)": "#1565C0",
    "US Government": "#C62828",
    "Intl Government": "#2E7D32",
    "Commercial": "#F9A825",
}


# ---------------------------------------------------------------------------
# Candidate 1 — Stacked area chart (absolute counts)
# ---------------------------------------------------------------------------
def chart_candidate_stacked_area(yearly_cat: pd.DataFrame) -> None:
    """Stacked area chart of launches by customer category over time.

    Kirk Ch 7: Stacked area charts encode both total volume (the top
    edge) and part-to-whole relationships (the band widths). They're
    the natural choice for showing how composition evolves over time.

    VERDICT: Good at showing overall growth AND the SpaceX share
    expanding. But the absolute-count stacking makes it hard to compare
    category shares across years — a year with 170 launches and a year
    with 15 have such different scales that the early-year composition
    is unreadable. The growth story competes with the concentration story.
    """
    fig = px.area(
        yearly_cat,
        x="year",
        y="launches",
        color="customer_category",
        title="Candidate 1: Stacked Area — Customer Mix (Absolute)",
        labels={"year": "Year", "launches": "Launches", "customer_category": "Customer"},
        color_discrete_map=CAT_COLORS,
        category_orders={"customer_category": CAT_ORDER},
    )
    fig.update_layout(xaxis=dict(dtick=1), width=1000, height=500)

    out = IMAGES_DIR / "tutorial_002_image_01_candidate_stacked_area.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Candidate 2 — 100% stacked bar chart (percentage composition)
# ---------------------------------------------------------------------------
def chart_candidate_pct_bar(yearly_cat: pd.DataFrame) -> None:
    """100% stacked bar chart showing percentage composition by year.

    Kirk Ch 7: Normalising to 100% removes the volume dimension and
    focuses purely on share. Each year bar is the same height, so the
    reader compares *proportions* across time — exactly what a
    concentration question demands.

    VERDICT: Strong candidate. The shift from a colourful mix (2013-2018)
    to a blue-dominated bar (2020+) is immediately readable. Every year
    is comparable regardless of total launches. The weakness is that total
    volume is invisible — you can't tell if there were 15 or 170 launches.
    But our question is about concentration, not volume.
    """
    # Compute percentage within each year
    totals = yearly_cat.groupby("year")["launches"].transform("sum")
    pct = yearly_cat.copy()
    pct["pct"] = pct["launches"] / totals * 100

    fig = px.bar(
        pct,
        x="year",
        y="pct",
        color="customer_category",
        title="Candidate 2: 100% Stacked Bar — Customer Share Over Time",
        labels={"year": "Year", "pct": "Share (%)", "customer_category": "Customer"},
        color_discrete_map=CAT_COLORS,
        category_orders={"customer_category": CAT_ORDER},
    )
    fig.update_layout(
        xaxis=dict(dtick=1),
        yaxis=dict(range=[0, 100]),
        barmode="stack",
        width=1000,
        height=500,
    )

    out = IMAGES_DIR / "tutorial_002_image_02_candidate_pct_bar.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Candidate 3 — Treemap (current-year snapshot)
# ---------------------------------------------------------------------------
def chart_candidate_treemap(df: pd.DataFrame) -> None:
    """Treemap showing current customer composition as nested rectangles.

    Kirk Ch 7: Treemaps encode quantity via area — effective for
    showing part-to-whole relationships in a single snapshot. The
    nested hierarchy (category → individual owner) lets readers drill
    from macro to micro.

    VERDICT: Visually striking for a single point in time, and the
    SpaceX rectangle dominating the space is impactful. But it cannot
    show *change* over time — it answers "what does concentration look
    like now?" rather than "how has it changed?" Since our curiosity
    question includes "how has that concentration changed?", this is a
    supporting chart at best. Also: 118 null owners create a large
    "Unknown" rectangle that misleads.
    """
    latest_year = df["year"].max()
    latest = df[df["year"] == latest_year].copy()

    # Use individual owner within category for hierarchy
    latest["owner_label"] = latest["mission_owner_primary_name"].fillna("Unknown")

    owner_counts = (
        latest.groupby(["customer_category", "owner_label"])
        .size()
        .reset_index(name="launches")
    )

    fig = px.treemap(
        owner_counts,
        path=["customer_category", "owner_label"],
        values="launches",
        title=f"Candidate 3: Treemap — Customer Composition ({latest_year})",
        color="customer_category",
        color_discrete_map=CAT_COLORS,
    )
    fig.update_layout(width=1000, height=600)

    out = IMAGES_DIR / "tutorial_002_image_03_candidate_treemap.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Candidate 4 — Pareto chart (cumulative customer share)
# ---------------------------------------------------------------------------
def chart_candidate_pareto(df: pd.DataFrame) -> None:
    """Pareto chart showing cumulative share of launches by customer.

    Kirk Ch 7: Pareto charts combine a bar chart (individual contribution)
    with a cumulative line (running total). They're the classic tool for
    answering "how few entities account for how much?" — the core of
    concentration analysis.

    VERDICT: This is the insurance professional's native chart. Solvency II
    concentration risk analysis uses exactly this pattern — "our top 5
    clients account for X% of GWP." The steep initial rise followed by a
    long tail makes concentration viscerally obvious. Weakness: it's a
    static snapshot (no time dimension), but it delivers the concentration
    message more powerfully than any other single chart.
    """
    # Use full dataset, known owners only
    known = df[df["mission_owner_primary_name"].notna()].copy()
    counts = (
        known["mission_owner_primary_name"]
        .value_counts()
        .reset_index()
    )
    counts.columns = ["owner", "launches"]
    counts["cumulative_pct"] = counts["launches"].cumsum() / counts["launches"].sum() * 100
    counts["rank"] = range(1, len(counts) + 1)

    # Truncate long owner names for readability
    counts["owner_short"] = counts["owner"].apply(
        lambda x: x[:25] + "..." if len(x) > 25 else x
    )

    fig = px.bar(
        counts,
        x="owner_short",
        y="launches",
        title="Candidate 4: Pareto — Customer Concentration (Known Owners)",
        labels={"owner_short": "Mission Owner", "launches": "Launches"},
    )

    # Add cumulative percentage line on secondary y-axis
    fig.add_scatter(
        x=counts["owner_short"],
        y=counts["cumulative_pct"],
        mode="lines+markers",
        name="Cumulative %",
        yaxis="y2",
        line=dict(color="#C62828", width=2),
        marker=dict(size=5),
    )

    fig.update_layout(
        xaxis=dict(tickangle=-45),
        yaxis=dict(title="Launches"),
        yaxis2=dict(
            title="Cumulative %",
            overlaying="y",
            side="right",
            range=[0, 105],
        ),
        width=1100,
        height=550,
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.35, xanchor="center", x=0.5),
    )

    out = IMAGES_DIR / "tutorial_002_image_04_candidate_pareto.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    """Run the chart selection process for customer concentration.

    Kirk Ch 7: 'The purpose of visualisation is not to show data, it is to
    show *insight*.' The right chart is the one that most directly answers
    the curiosity question for our audience.

    Our audience: insurance professionals learning data viz.
    Our question: How dependent is SpaceX on a handful of key customers,
    and how has that concentration changed?
    They need to take away: SpaceX went from a diversified customer base
    to overwhelming self-dependency (Starlink), and the pattern maps to
    their own client concentration risk analysis.
    """
    df = load_and_filter()
    yearly_cat = prepare_yearly_by_category(df)

    print("=" * 60)
    print("CHART SELECTION — Kirk Ch 7: Data Representation")
    print("=" * 60)
    print()
    print("Curiosity question: How dependent is SpaceX's manifest on a")
    print("handful of key customers, and how has that concentration changed?")
    print()
    print("Evaluating 4 chart candidates...")
    print()

    # --- Render all candidates ---
    chart_candidate_stacked_area(yearly_cat)
    print("  Stacked area: shows growth + mix, but absolute scale hides early shares.")
    print()

    chart_candidate_pct_bar(yearly_cat)
    print("  100% stacked bar: normalised shares, concentration shift is immediate.")
    print()

    chart_candidate_treemap(df)
    print("  Treemap: powerful snapshot, but no time dimension.")
    print()

    chart_candidate_pareto(df)
    print("  Pareto: the insurance professional's chart — concentration made visceral.")
    print()

    # --- Final selection ---
    print("=" * 60)
    print("WINNER: 100% Stacked Bar (Candidate 2) as PRIMARY")
    print("SUPPORTING: Pareto (Candidate 4) as SECONDARY")
    print("=" * 60)
    print("""
WHY THE 100% STACKED BAR WINS:

1. ANSWERS BOTH PARTS: Our curiosity question has two halves — "how
   dependent?" (concentration level) and "how has that changed?" (trend
   over time). The 100% stacked bar is the only candidate that answers
   both in a single view. Each bar shows the current split; reading
   left to right shows how it evolved.

2. NORMALISED COMPARISON: By fixing every year at 100%, we eliminate
   the volume dimension that distorts the stacked area chart. A year
   with 15 launches and a year with 170 are equally readable. The
   reader's eye tracks the blue (SpaceX) band expanding from nothing
   to dominance — that IS the concentration story.

3. DISCRETE YEARS: Kirk Ch 7 tells us that bar length is the most
   accurately perceived visual channel. Each year is a discrete bar,
   matching how insurance professionals read portfolio reports — they
   compare year-end composition snapshots, not continuous flows.

4. DOMAIN FAMILIARITY: Insurance professionals see 100% stacked bars
   in every quarterly review — line-of-business composition, claims
   by peril type, GWP by client tier. This chart speaks their language.

WHY THE PARETO AS SECONDARY:

The Pareto chart is the knockout punch for the concentration message.
"One customer accounts for 75% of launches" hits harder as a steep
cumulative curve than as a blue band in a stacked bar. It's the chart
that makes the Solvency II connection explicit — "our top 1 client is
X% of the book." In tutorial_final, we may use the Pareto as a callout
or secondary panel alongside the primary 100% bar.

REJECTED:

- Stacked area (Candidate 1): The 20x growth in absolute launches
  dominates the visual, making early-year composition unreadable. The
  growth story competes with the concentration story, and we already
  told the growth story in curiosity 1 (launch_cadence).

- Treemap (Candidate 3): Beautiful for a snapshot, but our question
  includes "how has that changed?" — a treemap cannot show change.
  It also struggles with the 118 null owners, creating a misleading
  "Unknown" rectangle. Good for a social media image, not for the
  primary analytical chart.
""")


if __name__ == "__main__":
    main()
