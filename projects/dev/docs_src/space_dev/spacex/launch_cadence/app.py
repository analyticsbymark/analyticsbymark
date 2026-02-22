"""
SpaceX Launch Cadence — Interactive Dash Application
=====================================================

Kirk Chapter 8: Interactivity — letting the reader explore the data
on their own terms, guided by the same editorial framing from the
static composition.

Wraps the primary bar chart from tutorial_final.py with three controls:
  1. Year range slider — zoom into any era
  2. Phase checklist — isolate acceleration phases
  3. Annotation toggle — layer editorial context on/off

Run with: python app.py
Open:     http://localhost:8050
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.express as px

from dash import Dash, html, dcc, dash_table, callback, Output, Input

from data.utils import get_spacex_data

# ---------------------------------------------------------------------------
# Data: loaded once at startup, filtered to completed launches
# ---------------------------------------------------------------------------
_raw = get_spacex_data()
DF = _raw[_raw["launch_status_abbrev"].isin(["Success", "Failure", "Partial Failure"])].copy()

PHASE_COLORS = {
    "Startup (2006-2013)": "#B0BEC5",
    "Growth (2014-2019)": "#42A5F5",
    "Hyperscale (2020+)": "#0D47A1",
}

SOURCE = "Source: Launch Library 2 API | thespacedevs.com"

ALL_YEARS = sorted(DF["year"].unique())
MIN_YEAR, MAX_YEAR = ALL_YEARS[0], ALL_YEARS[-1]

# Derive headline stats once for the layout subtitle
_yearly_full = DF.groupby("year").size().reset_index(name="launches")
_FIRST_COUNT = int(_yearly_full["launches"].iloc[0])
_FIRST_YEAR = int(_yearly_full["year"].iloc[0])
_hs_data = _yearly_full[_yearly_full["year"] >= 2020]
_peak_idx = _hs_data["launches"].idxmax()
_PEAK_COUNT = int(_hs_data.loc[_peak_idx, "launches"])
_PEAK_YEAR = int(_hs_data.loc[_peak_idx, "year"])
del _yearly_full, _hs_data, _peak_idx


def assign_phase(year: int) -> str:
    """Map a year to its acceleration phase."""
    if year <= 2013:
        return "Startup (2006-2013)"
    elif year <= 2019:
        return "Growth (2014-2019)"
    return "Hyperscale (2020+)"


def _build_card(value: str, label: str, accent: str) -> html.Div:
    """Return a single stat card with a big number, label, and accent border."""
    return html.Div(
        style={
            "background": "white",
            "border": "1px solid #E0E0E0",
            "borderLeft": f"4px solid {accent}",
            "borderRadius": "4px",
            "padding": "12px 16px",
            "minWidth": "120px",
            "flex": "1",
        },
        children=[
            html.Div(value, style={
                "fontSize": "24px", "fontWeight": "bold", "color": accent,
            }),
            html.Div(label, style={
                "fontSize": "11px", "textTransform": "uppercase",
                "color": "#999", "letterSpacing": "0.5px", "marginTop": "2px",
            }),
        ],
    )


# ---------------------------------------------------------------------------
# App layout
# ---------------------------------------------------------------------------

# Hint: swap Dash(__name__) for Dash(__name__, external_stylesheets=[...])
# to add Bootstrap or another CSS framework for richer styling.
# See: https://dash-bootstrap-components.opensource.faculty.ai/
app = Dash(__name__)

app.layout = html.Div(
    style={"fontFamily": "Arial, sans-serif", "maxWidth": "1200px", "margin": "0 auto", "padding": "24px"},
    children=[
        html.H2("SpaceX Launch Cadence Explorer"),
        html.P(
            f"From {_FIRST_COUNT} launch in {_FIRST_YEAR} to {_PEAK_COUNT} in {_PEAK_YEAR} "
            f"— filter by year and acceleration "
            f"phase to explore how SpaceX scaled to hyperscale operations.",
            style={"color": "#666", "fontSize": "14px", "marginBottom": "24px"},
        ),

        # --- Stat cards ---
        html.Div(
            id="stat-cards",
            style={"display": "flex", "gap": "12px", "flexWrap": "wrap", "marginBottom": "24px"},
        ),

        # --- Controls row ---
        html.Div(
            style={"display": "flex", "gap": "40px", "alignItems": "flex-start", "marginBottom": "24px"},
            children=[
                # Control 1: Year range slider
                html.Div(
                    style={"flex": "1"},
                    children=[
                        html.Label("Year Range", style={"fontWeight": "bold", "marginBottom": "8px"}),
                        dcc.RangeSlider(
                            id="year-range",
                            min=MIN_YEAR,
                            max=MAX_YEAR,
                            value=[MIN_YEAR, MAX_YEAR],
                            marks={str(y): str(y) for y in ALL_YEARS if y % 5 == 0 or y == MIN_YEAR or y == MAX_YEAR},
                            step=1,
                            tooltip={"placement": "bottom", "always_visible": False},
                        ),
                    ],
                ),

                # Control 2: Phase filter
                html.Div(
                    style={"minWidth": "220px"},
                    children=[
                        html.Label("Phases", style={"fontWeight": "bold", "marginBottom": "8px"}),
                        dcc.Checklist(
                            id="phase-filter",
                            options=[{"label": phase, "value": phase} for phase in PHASE_COLORS],
                            value=list(PHASE_COLORS.keys()),
                            # Hint: add inline=True for horizontal layout
                            style={"fontSize": "13px"},
                        ),
                    ],
                ),

                # Control 3: Annotation toggle
                html.Div(
                    style={"minWidth": "160px"},
                    children=[
                        html.Label("Annotations", style={"fontWeight": "bold", "marginBottom": "8px"}),
                        dcc.Checklist(
                            id="annotation-toggle",
                            options=[{"label": "Show annotations", "value": "on"}],
                            value=["on"],
                            style={"fontSize": "13px"},
                        ),
                    ],
                ),
            ],
        ),

        # --- Chart ---
        dcc.Graph(id="cadence-chart"),

        # --- Data table: shows the filtered data driving the chart ---
        # Hint: customise columns, conditional formatting, and CSV export via
        # https://dash.plotly.com/datatable
        html.H4("Filtered Data", style={"marginTop": "24px"}),
        dash_table.DataTable(
            id="data-table",
            sort_action="native",
            page_size=15,
            style_table={"overflowX": "auto"},
            style_header={"fontWeight": "bold", "backgroundColor": "#F5F5F5"},
            style_cell={"textAlign": "left", "padding": "8px", "fontSize": "13px"},
        ),

        # --- Footer ---
        html.P(
            SOURCE,
            style={"color": "#999", "fontSize": "11px", "marginTop": "16px"},
        ),
        # Hint: add dcc.Markdown() here for narrative text or tutorial context.
        # See: https://dash.plotly.com/dash-core-components/markdown
    ],
)


# ---------------------------------------------------------------------------
# Callback: rebuild chart on any control change
# ---------------------------------------------------------------------------
@callback(
    Output("cadence-chart", "figure"),
    Output("data-table", "data"),
    Output("data-table", "columns"),
    Output("stat-cards", "children"),
    Input("year-range", "value"),
    Input("phase-filter", "value"),
    Input("annotation-toggle", "value"),
)
def update_chart(year_range: list, phases: list, annotations: list) -> tuple:
    """Rebuild the bar chart and data table from filtered data."""
    y_min, y_max = year_range
    yearly = DF.groupby("year").size().reset_index(name="launches")
    yearly["phase"] = yearly["year"].apply(assign_phase)

    # Derive annotation values from unfiltered data (before user filters)
    first_year = int(yearly["year"].iloc[0])
    first_count = int(yearly["launches"].iloc[0])

    hyperscale_year = 2020
    hs_data = yearly[yearly["year"] >= hyperscale_year]
    peak_idx = hs_data["launches"].idxmax()
    peak_year = int(hs_data.loc[peak_idx, "year"])
    peak_count = int(hs_data.loc[peak_idx, "launches"])
    multiple = peak_count / max(first_count, 1)

    hs_count = int(yearly.loc[yearly["year"] == hyperscale_year, "launches"].values[0])
    prev_count = int(yearly.loc[yearly["year"] == hyperscale_year - 1, "launches"].values[0])
    yoy_pct = round((hs_count - prev_count) / prev_count * 100)

    n_years = peak_year - hyperscale_year
    cagr_pct = round(((peak_count / hs_count) ** (1 / n_years) - 1) * 100)

    bracket_y = peak_count + 30
    bracket_mid_x = hyperscale_year + (peak_year - hyperscale_year) / 2

    # Apply user filters
    yearly = yearly[(yearly["year"] >= y_min) & (yearly["year"] <= y_max)]
    yearly = yearly[yearly["phase"].isin(phases)]

    # --- Stat cards: computed from filtered yearly ---
    if yearly.empty:
        stat_cards = []
    else:
        _total = int(yearly["launches"].sum())
        _peak_row = yearly.loc[yearly["launches"].idxmax()]
        _peak_yr = int(_peak_row["year"])
        _peak_ct = int(_peak_row["launches"])
        _first_ct = int(yearly["launches"].iloc[0])
        _growth = _peak_ct / max(_first_ct, 1)
        _n_years = len(yearly)
        stat_cards = [
            _build_card(f"{_total:,}", "Total Launches", "#0D47A1"),
            _build_card(f"{_peak_yr} ({_peak_ct})", "Peak Year", "#0D47A1"),
            _build_card(f"{_growth:.0f}\u00d7", "Growth Multiple", "#42A5F5"),
            _build_card(str(_n_years), "Active Years", "#B0BEC5"),
        ]

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
                f"From {first_count} to {peak_count}: SpaceX's Launch Acceleration"
                f"<br><sup style='color:#666'>Completed launches per year "
                f"— three distinct acceleration phases</sup>"
            ),
            x=0.5,
            xanchor="center",
            font=dict(size=18),
        ),
        xaxis=dict(dtick=1, title="Year"),
        yaxis=dict(title="Launches"),
        height=620,
        margin=dict(t=120, b=80),
        legend=dict(
            orientation="h", yanchor="top", y=-0.08,
            xanchor="center", x=0.5, font=dict(size=11),
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#EEEEEE")

    # --- Annotations (only when toggled on) ---
    show = "on" in (annotations or [])
    if show:
        in_range = y_min <= hyperscale_year <= y_max and y_min <= peak_year <= y_max
        has_hyperscale = "Hyperscale (2020+)" in phases

        if in_range and has_hyperscale:
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
                (hyperscale_year, bracket_y, peak_year, bracket_y),
                (peak_year, peak_count + 12, peak_year, bracket_y),
            ]:
                fig.add_shape(
                    type="line", x0=x0, y0=y0, x1=x1, y1=y1,
                    line=dict(color="#0D47A1", width=1.5, dash="dot"),
                )
            fig.add_annotation(
                x=bracket_mid_x, y=bracket_y + 8,
                text=f"{hyperscale_year}-{peak_year} CAGR <b>{cagr_pct}%</b>",
                showarrow=False, font=dict(size=12, color="#0D47A1"),
                bgcolor="white", bordercolor="#0D47A1", borderwidth=1, borderpad=4,
            )

            fig.add_annotation(
                x=peak_year, y=peak_count,
                text=f"<b>{peak_count} launches</b><br>{multiple:.0f}\u00d7 the first year",
                showarrow=True, arrowhead=2, arrowsize=1.2, arrowcolor="#0D47A1",
                ax=70, ay=-40,
                font=dict(size=11, color="#0D47A1"),
                bgcolor="white", bordercolor="#0D47A1", borderwidth=1, borderpad=4,
            )

    raw = DF[(DF["year"] >= y_min) & (DF["year"] <= y_max)].copy()
    raw["phase"] = raw["year"].apply(assign_phase)
    raw = raw[raw["phase"].isin(phases)]
    table_df = raw[["net", "launch_name", "rocket_name", "mission_type",
                     "launchpad_name", "launch_status_abbrev"]].copy()
    table_df["net"] = table_df["net"].dt.strftime("%Y-%m-%d")
    table_df = table_df.rename(columns={
        "net": "Date", "launch_name": "Mission", "rocket_name": "Rocket",
        "mission_type": "Type", "launchpad_name": "Pad",
        "launch_status_abbrev": "Status",
    }).sort_values("Date", ascending=False)
    columns = [{"name": c, "id": c} for c in table_df.columns]

    return fig, table_df.to_dict("records"), columns, stat_cards


if __name__ == "__main__":
    app.run(debug=True)
