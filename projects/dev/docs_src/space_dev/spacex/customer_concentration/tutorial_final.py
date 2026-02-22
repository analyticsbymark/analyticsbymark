"""
SpaceX Customer Concentration — Final Composition
===================================================

Production-ready visualisation answering the curiosity question:
"How dependent is SpaceX's manifest on a handful of key customers,
and how has that concentration changed?"

Produces one polished chart:
  1. 100% stacked bar showing customer share over time, with a 50%
     concentration threshold, majority-year callout, and latest share

Best decisions carried forward:
  - Ch 4:  Working with Data — completed launches, transparent null-owner
           imputation into 4 customer categories (tutorial_001)
  - Ch 7:  Data Representation — 100% stacked bar normalises each year,
           making concentration shift readable across scale (tutorial_002)
  - Ch 10: Color — warm/cool qualitative palette: navy (dominance) vs
           orange/teal/amber (diversity), colorblind-safe (tutorial_003)
  - Ch 9:  Annotation — editorial title, 50% threshold line, inflection
           callout, latest share callout, source attribution (tutorial_004)
  - Ch 11: Composition — layout, hierarchy, cohesion (this file)
  - Ch 6:  Design Solutions — the complete, considered output

Run with: python tutorial_final.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.express as px

from data.utils import get_spacex_data

IMAGES_DIR = Path(__file__).resolve().parent / "images"
IMAGES_DIR.mkdir(exist_ok=True)

CAT_ORDER = ["SpaceX (Internal)", "US Government", "Intl Government", "Commercial"]

CAT_COLORS = {
    "SpaceX (Internal)": "#1A237E",
    "US Government": "#E65100",
    "Intl Government": "#00897B",
    "Commercial": "#FFB300",
}

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

SOURCE = "Source: Launch Library 2 API | thespacedevs.com"


def load_data() -> pd.DataFrame:
    """Load SpaceX launches, filtered to completed only, with customer categories."""
    df = get_spacex_data()
    completed = df[
        df["launch_status_abbrev"].isin(["Success", "Failure", "Partial Failure"])
    ].copy()
    completed["customer_category"] = completed.apply(_assign_category, axis=1)
    return completed


def _assign_category(row: pd.Series) -> str:
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


def build_concentration_chart(df: pd.DataFrame) -> None:
    """Produce the 100% stacked bar chart of customer concentration over time."""
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

    spacex_by_year = (
        yearly[yearly["customer_category"] == "SpaceX (Internal)"]
        .set_index("year")["pct"]
    )

    over_50 = spacex_by_year[spacex_by_year > 50]
    majority_year = int(over_50.index.min()) if not over_50.empty else None
    majority_pct = round(over_50.iloc[0], 1) if not over_50.empty else 0

    max_year = int(yearly["year"].max())
    latest_spacex_pct = round(spacex_by_year.get(max_year, 0), 1)

    total_spacex = len(df[df["customer_category"] == "SpaceX (Internal)"])
    total_launches = len(df)

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

    fig.add_hline(y=50, line_dash="dash", line_color="#999", line_width=1.5)
    fig.add_annotation(
        text="50% concentration<br>threshold",
        xref="paper", yref="y", x=1.02, y=50,
        showarrow=False, font=dict(size=10, color="#666"), xanchor="left",
    )

    if majority_year is not None:
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

    fig.add_annotation(
        x=max_year, y=latest_spacex_pct / 2,
        text=f"<b>{latest_spacex_pct:.0f}%</b><br>SpaceX share",
        showarrow=True, arrowhead=2, arrowsize=1.2, arrowcolor="#1A237E",
        ax=70, ay=20,
        font=dict(size=11, color="#1A237E"),
        bgcolor="white", bordercolor="#1A237E", borderwidth=1, borderpad=4,
    )

    fig.add_annotation(
        text=SOURCE, xref="paper", yref="paper",
        x=0, y=-0.1, showarrow=False, font=dict(size=9, color="#999"),
    )

    out = IMAGES_DIR / "tutorial_final_image_01_concentration_bar.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


def main() -> None:
    """Generate final composition for customer concentration curiosity."""
    df = load_data()
    build_concentration_chart(df)


if __name__ == "__main__":
    main()
