"""
SpaceX Launch Cadence — Final Composition
==========================================

Production-ready visualisation answering the curiosity question:
"How did SpaceX scale from its first launch to hyperscale operations,
and what does the acceleration curve reveal?"

Produces two polished charts:
  1. Yearly bar chart with phase-based color, data labels, CAGR bracket,
     and strategic annotations
  2. Monthly heatmap showing the shift from sporadic to continuous ops

Best decisions carried forward:
  - Ch 4:  Working with Data — filter to completed launches (tutorial_001)
  - Ch 7:  Data Representation — bar chart primary, heatmap secondary (tutorial_002)
  - Ch 10: Color — sequential blue phase ramp, colorblind-safe (tutorial_003)
  - Ch 9:  Annotation — editorial titles, data labels, 3 callouts inc.
           CAGR bracket, source attribution (tutorial_004)
  - Ch 11: Composition — layout, hierarchy, cohesion (this file)
  - Ch 6:  Design Solutions — the complete, considered output

Run with: python tutorial_final.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data.utils import get_spacex_data

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

SOURCE = "Source: Launch Library 2 API | thespacedevs.com"


def load_data() -> pd.DataFrame:
    """Load SpaceX launches, filtered to completed only."""
    df = get_spacex_data()
    return df[df["launch_status_abbrev"].isin(["Success", "Failure", "Partial Failure"])]


def assign_phase(year: int) -> str:
    """Map a year to its acceleration phase."""
    if year <= 2013:
        return "Startup (2006-2013)"
    elif year <= 2019:
        return "Growth (2014-2019)"
    return "Hyperscale (2020+)"


def build_bar_chart(df: pd.DataFrame) -> None:
    """Produce the primary yearly cadence bar chart."""
    yearly = df.groupby("year").size().reset_index(name="launches")
    yearly["phase"] = yearly["year"].apply(assign_phase)

    first_year = yearly["year"].iloc[0]
    last_year = yearly["year"].iloc[-1]
    first_count = int(yearly["launches"].iloc[0])
    last_count = int(yearly.loc[yearly["year"] == last_year, "launches"].values[0])
    multiple = last_count / max(first_count, 1)

    hyperscale_year = 2020
    hs_count = int(yearly.loc[yearly["year"] == hyperscale_year, "launches"].values[0])
    prev_count = int(yearly.loc[yearly["year"] == hyperscale_year - 1, "launches"].values[0])
    yoy_pct = round((hs_count - prev_count) / prev_count * 100)

    n_years = last_year - hyperscale_year
    cagr_pct = round(((last_count / hs_count) ** (1 / n_years) - 1) * 100)

    bracket_y = last_count + 30
    bracket_mid_x = hyperscale_year + (last_year - hyperscale_year) / 2

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
                f"From {first_count} to {last_count}: SpaceX's Launch Acceleration"
                f"<br><sup style='color:#666'>Completed launches per year, "
                f"{first_year}-{last_year} — three distinct acceleration phases</sup>"
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

    fig.add_annotation(
        x=hyperscale_year, y=hs_count,
        text=f"Hyperscale begins<br><b>+{yoy_pct}% YoY</b>",
        showarrow=True, arrowhead=2, arrowsize=1.2, arrowcolor="#0D47A1",
        ax=-70, ay=-50,
        font=dict(size=11, color="#0D47A1"),
        bgcolor="white", bordercolor="#0D47A1", borderwidth=1, borderpad=4,
    )

    for x0, y0, x1, y1 in [
        (hyperscale_year, hs_count + 11, hyperscale_year, bracket_y),
        (hyperscale_year, bracket_y, last_year, bracket_y),
        (last_year, last_count + 12, last_year, bracket_y),
    ]:
        fig.add_shape(
            type="line", x0=x0, y0=y0, x1=x1, y1=y1,
            line=dict(color="#0D47A1", width=1.5, dash="dot"),
        )
    fig.add_annotation(
        x=bracket_mid_x, y=bracket_y + 8,
        text=f"{hyperscale_year}-{last_year} CAGR <b>{cagr_pct}%</b>",
        showarrow=False, font=dict(size=12, color="#0D47A1"),
        bgcolor="white", bordercolor="#0D47A1", borderwidth=1, borderpad=4,
    )

    fig.add_annotation(
        x=last_year, y=last_count,
        text=f"<b>{last_count} launches</b><br>{multiple:.0f}\u00d7 the first year",
        showarrow=True, arrowhead=2, arrowsize=1.2, arrowcolor="#0D47A1",
        ax=70, ay=-40,
        font=dict(size=11, color="#0D47A1"),
        bgcolor="white", bordercolor="#0D47A1", borderwidth=1, borderpad=4,
    )

    fig.add_annotation(
        text=SOURCE, xref="paper", yref="paper",
        x=0, y=-0.18, showarrow=False, font=dict(size=9, color="#999"),
    )

    out = IMAGES_DIR / "tutorial_final_image_01_bar_cadence.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


def build_heatmap(df: pd.DataFrame) -> None:
    """Produce the secondary monthly density heatmap."""
    pivot = df.pivot_table(index="year", columns="month", aggfunc="size", fill_value=0)
    for m in range(1, 13):
        if m not in pivot.columns:
            pivot[m] = 0
    pivot = pivot[range(1, 13)]

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
    fig.update_layout(
        title=dict(
            text=(
                "From Sporadic to Always-On: Monthly Launch Density"
                "<br><sup style='color:#666'>Completed launches by month, "
                "2006-2026 — white cells indicate zero launches</sup>"
            ),
            x=0.5, xanchor="center", font=dict(size=16),
        ),
        width=1000, height=650,
        margin=dict(t=100, b=80, r=130),
        paper_bgcolor="white",
    )

    fig.add_annotation(
        text="Sparse:<br>gaps & clusters",
        xref="paper", yref="paper", x=1.1, y=0.85,
        showarrow=False, font=dict(size=10, color="#B0BEC5"),
    )
    fig.add_annotation(
        text="Dense:<br>every month active",
        xref="paper", yref="paper", x=1.1, y=0.2,
        showarrow=False, font=dict(size=10, color="#0D47A1"),
    )
    fig.add_annotation(
        text=SOURCE, xref="paper", yref="paper",
        x=0, y=-0.1, showarrow=False, font=dict(size=9, color="#999"),
    )

    out = IMAGES_DIR / "tutorial_final_image_02_heatmap_density.png"
    fig.write_image(str(out), scale=2)
    print(f"Saved: {out}")


def main() -> None:
    """Generate final composition for launch cadence curiosity."""
    df = load_data()
    build_bar_chart(df)
    build_heatmap(df)


if __name__ == "__main__":
    main()
