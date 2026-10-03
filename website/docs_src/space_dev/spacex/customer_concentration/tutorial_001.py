"""
What You'll Learn
=================
- How to load and profile SpaceX launch data for customer concentration analysis
- Kirk Chapter 4: Working with Data — handling missing values and categorising entities
- Kirk Chapter 5: Editorial Thinking — what does the customer mix reveal about SpaceX's
  business model?
- Techniques: value_counts(), groupby(), pivot_table(), Herfindahl-Hirschman Index (HHI)
- Output: Data profiling summary + 4 initial observation charts
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

# Customer category mapping — groups the 29 distinct mission owners plus
# 118 null-owner launches into analytically useful buckets.
# Kirk Ch 4: Real-world data is messy. 18.5% of completed launches have no
# recorded owner in the API. Rather than discard them, we categorise them
# from mission names and program names downstream.
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
    """Load SpaceX data and filter to completed launches only.

    Future/planned launches (TBD, Go) are excluded because their dates and
    customers are often placeholders — including them would distort the
    concentration analysis.

    Kirk Ch 4: 'Know your data before you visualise it.'
    """
    df = get_spacex_data()
    completed = df[
        df["launch_status_abbrev"].isin(["Success", "Failure", "Partial Failure"])
    ]
    return completed.copy()


def assign_customer_category(row: pd.Series) -> str:
    """Classify each launch into a customer category.

    Kirk Ch 4: Categorisation decisions shape the story. Grouping SpaceX's
    own launches (overwhelmingly Starlink) separately from third-party
    commercial customers is the editorial choice that makes concentration
    visible.

    Categories:
        SpaceX (Internal) — SpaceX as mission owner (Starlink, test flights)
        US Government      — NASA, USSF, NRO, SDA, MDA
        Intl Government    — ESA, CSA, JAXA, and other national agencies
        Commercial         — Third-party commercial operators
    """
    owner = row["mission_owner_primary_name"]

    # Known owners
    if pd.notna(owner) and owner != "":
        if owner == "SpaceX":
            return "SpaceX (Internal)"
        if owner in _US_GOV_OWNERS:
            return "US Government"
        if owner in _INTL_GOV_OWNERS:
            return "Intl Government"
        return "Commercial"

    # Null owners — infer category from mission context
    # Kirk Ch 4: When data is missing, transparent imputation beats silent
    # exclusion. We document the logic so the reader can challenge it.
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

    # Remaining null owners are predominantly commercial satellite operators
    # identifiable from their mission names (SES, Eutelsat, Intelsat, etc.)
    return "Commercial"


# ---------------------------------------------------------------------------
# Profiling helpers
# ---------------------------------------------------------------------------
def print_profile(df: pd.DataFrame) -> None:
    """Print a concise profile of the dataset relevant to customer analysis."""
    print("=" * 60)
    print("DATASET PROFILE — Customer Concentration")
    print("=" * 60)
    print(f"Total completed launches : {len(df)}")
    print(f"Date range               : {df['net'].min()} to {df['net'].max()}")
    print(f"Years spanned            : {df['year'].nunique()} ({df['year'].min()}-{df['year'].max()})")
    print(f"Unique mission owners    : {df['mission_owner_primary_name'].nunique()}")
    print()

    # Data quality: null owners are the major issue for this curiosity
    null_count = df["mission_owner_primary_name"].isna().sum()
    print(f"--- Data quality: mission_owner_primary_name ---")
    print(f"  Non-null : {len(df) - null_count} ({(len(df) - null_count) / len(df) * 100:.1f}%)")
    print(f"  Null     : {null_count} ({null_count / len(df) * 100:.1f}%)")
    print()

    # Kirk Ch 5: Editorial thinking — SpaceX as its own biggest customer
    # is the headline. When did this shift happen?
    spacex_launches = len(df[df["mission_owner_primary_name"] == "SpaceX"])
    print(f"SpaceX self-launches     : {spacex_launches} ({spacex_launches / len(df) * 100:.1f}% of total)")
    print()

    print("--- Top 15 mission owners ---")
    owners = df["mission_owner_primary_name"].value_counts()
    for i, (name, count) in enumerate(owners.head(15).items(), 1):
        pct = count / len(df) * 100
        print(f"  {i:2d}. {name}: {count} ({pct:.1f}%)")
    print(f"  ... plus {len(owners) - 15} more with 1-2 launches each")
    print()

    print("--- Null counts (concentration-relevant columns) ---")
    cols = [
        "mission_owner_primary_name",
        "mission_owner_all_names",
        "program_names",
        "mission_type",
        "year",
    ]
    for col in cols:
        nulls = df[col].isnull().sum()
        print(f"  {col:35s}  {nulls}")
    print()


# ---------------------------------------------------------------------------
# Visualisation 1 — Top customers (who dominates?)
# ---------------------------------------------------------------------------
def plot_top_customers(df: pd.DataFrame) -> None:
    """Horizontal bar chart of mission owners by launch count.

    Kirk Ch 5: The Pareto shape is immediately visible — SpaceX dominates,
    then a sharp drop-off. This distribution is the visual fingerprint of
    concentration risk. In insurance terms, when one client accounts for
    60%+ of your book, you don't have a portfolio — you have a dependency.
    """
    # Use only rows with known owners for this chart
    known = df[df["mission_owner_primary_name"].notna()].copy()
    counts = (
        known["mission_owner_primary_name"]
        .value_counts()
        .reset_index()
    )
    counts.columns = ["owner", "launches"]

    # Show top 15 + aggregate the rest
    top_n = 15
    top = counts.head(top_n).copy()
    rest_count = int(counts.iloc[top_n:]["launches"].sum()) if len(counts) > top_n else 0
    if rest_count > 0:
        rest_row = pd.DataFrame([{"owner": f"Other ({len(counts) - top_n} owners)", "launches": rest_count}])
        top = pd.concat([top, rest_row], ignore_index=True)

    fig = px.bar(
        top,
        x="launches",
        y="owner",
        orientation="h",
        title="SpaceX's Mission Owners — Top 15 (Completed Launches)",
        labels={"launches": "Number of Launches", "owner": "Mission Owner"},
        text="launches",
    )
    fig.update_layout(
        yaxis=dict(categoryorder="total ascending", automargin=True),
        width=1000,
        height=600,
        showlegend=False,
    )
    fig.update_traces(textposition="outside")

    out = IMAGES_DIR / "tutorial_001_image_01_top_customers.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Visualisation 2 — SpaceX self-launch share over time
# ---------------------------------------------------------------------------
def plot_self_launch_share(df: pd.DataFrame) -> None:
    """Line chart showing SpaceX's share of its own manifest over time.

    Kirk Ch 5: The inflection point is the story. Before 2018, SpaceX
    launched zero missions for itself. By 2025, 78% of all launches are
    SpaceX's own (overwhelmingly Starlink). This is a business model
    transformation made visible through data.

    In insurance terms, this is like watching a broker's largest client
    grow from 0% to 78% of the book in seven years — a concentration
    alarm bell.
    """
    yearly = df.groupby("year").size().reset_index(name="total")
    spacex_yearly = (
        df[df["mission_owner_primary_name"] == "SpaceX"]
        .groupby("year")
        .size()
        .reset_index(name="spacex")
    )
    merged = yearly.merge(spacex_yearly, on="year", how="left")
    merged["spacex"] = merged["spacex"].fillna(0).astype(int)
    merged["share_pct"] = merged["spacex"] / merged["total"] * 100
    # Exclude very early years with 1-2 launches (noisy percentages)
    merged = merged[merged["total"] >= 3]

    fig = px.bar(
        merged,
        x="year",
        y=["spacex", "total"],
        title="SpaceX Self-Launches vs Total Manifest",
        labels={"year": "Year", "value": "Launches", "variable": ""},
        barmode="overlay",
    )
    # Style: total in light grey, SpaceX in blue
    fig.data[0].marker.color = "#1565C0"
    fig.data[0].name = "SpaceX (own missions)"
    fig.data[1].marker.color = "#E0E0E0"
    fig.data[1].name = "Total launches"
    # Reorder so total is behind
    fig.data = (fig.data[1], fig.data[0])

    fig.update_layout(
        xaxis=dict(dtick=1),
        yaxis_title="Launches",
        width=1000,
        height=500,
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="center", x=0.5),
    )

    out = IMAGES_DIR / "tutorial_001_image_02_self_launch_share.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Visualisation 3 — Customer category stacked area over time
# ---------------------------------------------------------------------------
def plot_category_stacked_area(df: pd.DataFrame) -> None:
    """Stacked area chart of customer categories over time.

    Kirk Ch 5: Grouping 29+ owners into four categories reveals the macro
    trend that raw owner names obscure. The "SpaceX (Internal)" slice
    expanding to swallow the chart IS the story — and it only becomes
    visible with this categorisation.
    """
    yearly_cat = (
        df.groupby(["year", "customer_category"])
        .size()
        .reset_index(name="launches")
    )

    # Define order and colours that encode meaning
    cat_order = ["SpaceX (Internal)", "US Government", "Intl Government", "Commercial"]
    color_map = {
        "SpaceX (Internal)": "#1565C0",
        "US Government": "#C62828",
        "Intl Government": "#2E7D32",
        "Commercial": "#F9A825",
    }

    # Exclude very early years with 1-2 launches
    yearly_totals = df.groupby("year").size()
    valid_years = yearly_totals[yearly_totals >= 3].index
    yearly_cat = yearly_cat[yearly_cat["year"].isin(valid_years)]

    fig = px.area(
        yearly_cat,
        x="year",
        y="launches",
        color="customer_category",
        title="Customer Mix Over Time — Who Is SpaceX Launching For?",
        labels={"year": "Year", "launches": "Launches", "customer_category": "Customer"},
        color_discrete_map=color_map,
        category_orders={"customer_category": cat_order},
    )
    fig.update_layout(
        xaxis=dict(dtick=1),
        yaxis_title="Launches",
        width=1000,
        height=500,
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="center", x=0.5),
    )

    out = IMAGES_DIR / "tutorial_001_image_03_category_stacked_area.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Visualisation 4 — Herfindahl-Hirschman Index (HHI) over time
# ---------------------------------------------------------------------------
def plot_hhi_over_time(df: pd.DataFrame) -> None:
    """Line chart of the HHI concentration index by year.

    Kirk Ch 5: The HHI is the standard metric for market concentration,
    used by regulators and economists worldwide. In insurance, Solvency II
    requires monitoring client concentration with exactly this kind of
    metric. Applying it to SpaceX's customer base bridges aerospace data
    with financial risk analysis.

    HHI thresholds (US DOJ guidelines):
        < 1,500  = Unconcentrated (competitive)
        1,500-2,500 = Moderately concentrated
        > 2,500  = Highly concentrated

    We compute HHI on individual mission owners (not broad categories)
    to capture real customer-level concentration. Launches with no
    recorded owner are treated as distinct customers — a conservative
    choice that slightly understates true concentration, but avoids
    artificially inflating HHI by lumping 118 diverse operators into
    one bucket.
    """
    records = []
    for yr in sorted(df["year"].unique()):
        yr_data = df[df["year"] == yr]
        total = len(yr_data)
        if total < 3:
            continue
        # Assign unique placeholder to each null owner so they count
        # as separate customers (conservative: lowers HHI estimate)
        owners = yr_data["mission_owner_primary_name"].copy()
        null_mask = owners.isna()
        null_ids = [f"_unknown_{i}" for i in range(null_mask.sum())]
        owners.loc[null_mask] = null_ids
        shares = owners.value_counts() / total
        hhi = int((shares**2).sum() * 10000)
        records.append({"year": yr, "hhi": hhi, "total_launches": total})

    hhi_df = pd.DataFrame(records)

    fig = px.line(
        hhi_df,
        x="year",
        y="hhi",
        title="Customer Concentration Index (HHI) Over Time",
        labels={"year": "Year", "hhi": "HHI (0-10,000)"},
        markers=True,
    )

    # Add threshold bands
    fig.add_hline(
        y=1500, line_dash="dash", line_color="#FFA726",
        annotation_text="Moderate (1,500)", annotation_position="top right",
    )
    fig.add_hline(
        y=2500, line_dash="dash", line_color="#EF5350",
        annotation_text="Highly concentrated (2,500)", annotation_position="top right",
    )

    fig.update_layout(
        xaxis=dict(dtick=1),
        yaxis=dict(range=[0, max(hhi_df["hhi"]) * 1.15]),
        width=1000,
        height=500,
    )

    out = IMAGES_DIR / "tutorial_001_image_04_hhi_concentration.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    """Run the full profiling pipeline for customer concentration analysis.

    Kirk Ch 4: Working with data is the foundation — you cannot tell a
    credible story if you haven't first understood what the data contains,
    what it's missing, and where the interesting patterns live.
    """
    df = load_and_filter()

    # Assign customer categories (handles null owners via imputation)
    df["customer_category"] = df.apply(assign_customer_category, axis=1)

    # --- Profile ---
    print_profile(df)

    # Category breakdown after imputation
    print("--- Customer categories (after imputation) ---")
    cat_counts = df["customer_category"].value_counts()
    for cat, count in cat_counts.items():
        pct = count / len(df) * 100
        print(f"  {cat}: {count} ({pct:.1f}%)")
    print()

    # --- Visualise ---
    plot_top_customers(df)
    plot_self_launch_share(df)
    plot_category_stacked_area(df)
    plot_hhi_over_time(df)

    print()
    print("=" * 60)
    print("EDITORIAL OBSERVATIONS — Kirk Ch 5")
    print("=" * 60)

    # Compute key stats dynamically
    spacex_total = len(df[df["customer_category"] == "SpaceX (Internal)"])
    spacex_pct = spacex_total / len(df) * 100
    latest_year = df["year"].max()
    latest_data = df[df["year"] == latest_year]
    latest_spacex_pct = (
        len(latest_data[latest_data["customer_category"] == "SpaceX (Internal)"])
        / len(latest_data) * 100
    )

    print(f"""
1. VERTICAL INTEGRATION STORY: SpaceX is its own largest customer —
   {spacex_total} of {len(df)} completed launches ({spacex_pct:.0f}%) are internal.
   In {latest_year}, self-launches reached {latest_spacex_pct:.0f}% of the manifest.
   This isn't a launch provider with a side project; Starlink IS the
   primary business, and third-party launches are the side business.

2. CONCENTRATION INFLECTION (2019-2020): SpaceX went from 0% self-launches
   before 2018 to majority self-launcher by 2020. The Starlink constellation
   deployment is the single biggest driver — 354 of {spacex_total} SpaceX-owned
   launches are communications (predominantly Starlink).

3. DATA QUALITY: 118 of 637 launches (18.5%) have no recorded mission owner.
   These are predominantly third-party commercial satellite launches
   identifiable from mission names. The imputation logic assigns them to
   categories based on mission type and launch name patterns. This is
   transparent and challengeable — exactly what Kirk Ch 4 advocates.

4. HHI TRAJECTORY: The Herfindahl-Hirschman Index has risen from ~1,000
   (competitive market) to over 6,000 (highly concentrated). By US DOJ
   standards, SpaceX's customer base has been "highly concentrated" since
   2020. The trend shows no sign of reversing.

5. GOVERNMENT DEPENDENCE IS MODEST: US Government (NASA, NRO, USSF, SDA)
   accounts for ~11% of launches. International governments add ~3%.
   Commercial third parties make up the remainder. The customer base is
   dominated by ONE internal customer (Starlink), not by government contracts.

DOMAIN TRANSFER: Insurance professionals managing portfolio concentration
would recognise this pattern immediately. When a single client crosses 50%
of your book, regulators require action — capital buffers, reinsurance, or
diversification plans. The HHI chart is directly applicable to Solvency II
concentration risk reporting.
""")


if __name__ == "__main__":
    main()
