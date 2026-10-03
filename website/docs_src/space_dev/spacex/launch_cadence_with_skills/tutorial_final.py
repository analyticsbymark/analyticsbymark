"""
SpaceX Launch Cadence — final composed chart.

Produces a single annotated bar chart of completed SpaceX launches per year,
coloured by acceleration regime (Startup / Growth / Hyperscale) with two
strategic callouts: the 2020 Hyperscale inflection and the Hyperscale-era CAGR.

Composes the best decision from each step: completed-launch transform (Ch 4/5),
bar chart (Ch 7), ordered single-hue regime ramp (Ch 10), and editorial
annotation (Ch 9), arranged per Kirk's composition principles (Ch 11 & 6).

Run with: python tutorial_final.py
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data.utils import get_spacex_data

IMAGES_DIR = Path(__file__).resolve().parent / "images"
IMAGES_DIR.mkdir(exist_ok=True)
IMG_WIDTH, IMG_HEIGHT, IMG_SCALE = 1200, 800, 2

PHASE_ORDER = ["Startup (2006–2013)", "Growth (2014–2019)", "Hyperscale (2020+)"]
PHASE_COLORS = {
    "Startup (2006–2013)": "#9ecae1",
    "Growth (2014–2019)": "#4292c6",
    "Hyperscale (2020+)": "#084594",
}
INK = PHASE_COLORS["Hyperscale (2020+)"]
MUTED = "#9e9e9e"
HYPERSCALE_START = 2020


def save_chart(fig, name: str) -> None:
    fig.update_layout(paper_bgcolor="white", plot_bgcolor="white")
    out = IMAGES_DIR / name
    fig.write_image(str(out), width=IMG_WIDTH, height=IMG_HEIGHT, scale=IMG_SCALE)
    print(f"Saved: {out}")


def yearly_launches() -> pd.DataFrame:
    df = get_spacex_data()
    df = df[df["launch_status_abbrev"].isin(["Success", "Failure", "Partial Failure"])]
    yearly = df.groupby("year").size().reset_index(name="launches")
    yearly["phase"] = pd.cut(
        yearly["year"], bins=[-1, 2013, 2019, 9999], labels=PHASE_ORDER
    ).astype(str)
    return yearly


def build_chart(yearly: pd.DataFrame):
    first_count = int(yearly["launches"].iloc[0])
    first_year = int(yearly["year"].iloc[0])
    partial_year = int(yearly["year"].max())
    full_years = yearly[yearly["year"] < partial_year]

    peak_idx = full_years["launches"].idxmax()
    peak_year = int(full_years.loc[peak_idx, "year"])
    peak_count = int(full_years.loc[peak_idx, "launches"])
    partial_val = int(yearly.loc[yearly["year"] == partial_year, "launches"].iloc[0])

    hs_count = int(yearly.loc[yearly["year"] == HYPERSCALE_START, "launches"].iloc[0])
    prev_count = int(yearly.loc[yearly["year"] == HYPERSCALE_START - 1, "launches"].iloc[0])
    yoy_pct = round((hs_count - prev_count) / prev_count * 100)
    cagr_pct = round(((peak_count / hs_count) ** (1 / (peak_year - HYPERSCALE_START)) - 1) * 100)

    fig = px.bar(
        yearly, x="year", y="launches", color="phase",
        category_orders={"phase": PHASE_ORDER},
        color_discrete_map=PHASE_COLORS,
        labels={"year": "Year", "launches": "Number of Launches", "phase": "Phase"},
    )
    fig.update_layout(
        title=dict(
            text=(
                f"From {first_count} to {peak_count}: SpaceX's launch acceleration"
                f"<br><sup style='color:#666'>Completed launches per year, "
                f"{first_year}–{peak_year}  ·  three acceleration regimes  ·  "
                f"{partial_year} is a partial year</sup>"
            ),
            x=0.5, xanchor="center",
        ),
        xaxis=dict(dtick=2),
        legend_title_text="Phase",
        margin=dict(t=110, b=90),
    )
    fig.add_annotation(
        x=HYPERSCALE_START, y=hs_count,
        text=f"Hyperscale begins<br><b>+{yoy_pct}% YoY</b>",
        showarrow=True, arrowhead=2, arrowsize=1.1, arrowcolor=INK,
        ax=-55, ay=-70,
        font=dict(size=12, color=INK),
        bgcolor="white", bordercolor=INK, borderwidth=1, borderpad=4,
    )
    fig.add_annotation(
        x=peak_year, y=peak_count,
        text=f"<b>{peak_count} launches</b><br>≈{cagr_pct}% CAGR since {HYPERSCALE_START}",
        showarrow=True, arrowhead=2, arrowsize=1.1, arrowcolor=INK,
        ax=-70, ay=-30,
        font=dict(size=12, color=INK),
        bgcolor="white", bordercolor=INK, borderwidth=1, borderpad=4,
    )
    fig.add_annotation(
        x=partial_year, y=partial_val,
        text=f"{partial_year} partial", showarrow=False, yshift=12,
        font=dict(size=10, color=MUTED),
    )
    fig.add_annotation(
        text="Source: Launch Library 2 API · thespacedevs.com",
        xref="paper", yref="paper", x=0, y=-0.13,
        showarrow=False, font=dict(size=9, color=MUTED),
    )
    return fig


def main() -> None:
    fig = build_chart(yearly_launches())
    save_chart(fig, "tutorial_final_image_01_launch_cadence.png")


if __name__ == "__main__":
    main()