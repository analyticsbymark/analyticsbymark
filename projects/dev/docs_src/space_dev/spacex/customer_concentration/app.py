"""
SpaceX Customer Concentration — Interactive Dash Application
=============================================================

Kirk Chapter 8: Interactivity — letting the reader explore the data
on their own terms, guided by the same editorial framing from the
static composition.

Wraps the 100% stacked bar chart from tutorial_final.py with three controls:
  1. Year range slider — zoom into any era
  2. Customer category checklist — isolate categories
  3. Annotation toggle — layer 50% threshold and callouts on/off

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
# Data: loaded once at startup
# ---------------------------------------------------------------------------
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

CAT_ORDER = ["SpaceX (Internal)", "US Government", "Intl Government", "Commercial"]

CAT_COLORS = {
    "SpaceX (Internal)": "#1A237E",
    "US Government": "#E65100",
    "Intl Government": "#00897B",
    "Commercial": "#FFB300",
}

SOURCE = "Source: Launch Library 2 API | thespacedevs.com"


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


_raw = get_spacex_data()
DF = _raw[_raw["launch_status_abbrev"].isin(["Success", "Failure", "Partial Failure"])].copy()
DF["customer_category"] = DF.apply(_assign_category, axis=1)

ALL_YEARS = sorted(DF["year"].unique())
MIN_YEAR, MAX_YEAR = ALL_YEARS[0], ALL_YEARS[-1]

# Fixed stat: total launches across full dataset
_TOTAL_LAUNCHES = len(DF)


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
# App layout — controls-above pattern
# ---------------------------------------------------------------------------

# Hint: swap Dash(__name__) for Dash(__name__, external_stylesheets=[...])
# to add Bootstrap or another CSS framework for richer styling.
# See: https://dash-bootstrap-components.opensource.faculty.ai/
app = Dash(__name__)

app.layout = html.Div(
    style={"fontFamily": "Arial, sans-serif", "maxWidth": "1200px", "margin": "0 auto", "padding": "24px"},
    children=[
        html.H2("SpaceX Customer Concentration Explorer"),
        html.P(
            f"Explore how SpaceX's customer mix shifted from diversified third-party "
            f"launches to Starlink-dominated self-dependency across {len(ALL_YEARS)} years "
            f"of operations.",
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

                # Control 2: Customer category filter
                html.Div(
                    style={"minWidth": "220px"},
                    children=[
                        html.Label("Customer Categories", style={"fontWeight": "bold", "marginBottom": "8px"}),
                        dcc.Checklist(
                            id="category-filter",
                            options=[{"label": cat, "value": cat} for cat in CAT_ORDER],
                            value=list(CAT_ORDER),
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
        dcc.Graph(id="concentration-chart"),

        # --- Data table ---
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
    Output("concentration-chart", "figure"),
    Output("data-table", "data"),
    Output("data-table", "columns"),
    Output("stat-cards", "children"),
    Input("year-range", "value"),
    Input("category-filter", "value"),
    Input("annotation-toggle", "value"),
)
def update_chart(year_range: list, categories: list, annotations: list) -> tuple:
    """Rebuild the 100% stacked bar chart and data table from filtered data."""
    y_min, y_max = year_range

    # Filter and aggregate
    filtered = DF[(DF["year"] >= y_min) & (DF["year"] <= y_max)].copy()
    filtered = filtered[filtered["customer_category"].isin(categories)]

    yearly = (
        filtered.groupby(["year", "customer_category"])
        .size()
        .reset_index(name="launches")
    )

    # Compute percentage
    if not yearly.empty:
        totals = yearly.groupby("year")["launches"].transform("sum")
        yearly["pct"] = yearly["launches"] / totals * 100
    else:
        yearly["pct"] = []

    # --- Stat cards ---
    if filtered.empty:
        stat_cards = []
    else:
        _total_filtered = len(filtered)
        _spacex_filtered = len(filtered[filtered["customer_category"] == "SpaceX (Internal)"])
        _spacex_pct = _spacex_filtered / _total_filtered * 100 if _total_filtered > 0 else 0
        _n_customers = filtered["mission_owner_primary_name"].dropna().nunique()

        # HHI on customer categories for the filtered view
        cat_shares = filtered["customer_category"].value_counts() / _total_filtered
        _hhi = int((cat_shares**2).sum() * 10000)

        stat_cards = [
            _build_card(f"{_TOTAL_LAUNCHES:,}", "Total Launches (All Time)", "#1A237E"),
            _build_card(f"{_spacex_pct:.0f}%", "SpaceX Share", "#1A237E"),
            _build_card(str(_n_customers), "Unique Customers", "#FFB300"),
            _build_card(f"{_hhi:,}", "HHI Index", "#E65100"),
        ]

    # --- Build chart ---
    fig = px.bar(
        yearly,
        x="year",
        y="pct",
        color="customer_category",
        labels={"year": "Year", "pct": "Share (%)", "customer_category": "Customer"},
        color_discrete_map=CAT_COLORS,
        category_orders={"customer_category": CAT_ORDER},
    )

    # Derive annotation values from unfiltered data (consistent reference points)
    # Exclude years with <3 launches (e.g. 2006-2008 had 1-2 test flights each,
    # giving misleading 100% SpaceX share) — matches tutorial_final.py logic.
    full_yearly = (
        DF.groupby(["year", "customer_category"])
        .size()
        .reset_index(name="launches")
    )
    full_year_totals = DF.groupby("year").size()
    valid_years = full_year_totals[full_year_totals >= 3].index
    full_yearly = full_yearly[full_yearly["year"].isin(valid_years)].copy()
    full_totals = full_yearly.groupby("year")["launches"].transform("sum")
    full_yearly["pct"] = full_yearly["launches"] / full_totals * 100
    spacex_by_year = (
        full_yearly[full_yearly["customer_category"] == "SpaceX (Internal)"]
        .set_index("year")["pct"]
    )
    over_50 = spacex_by_year[spacex_by_year > 50]
    majority_year = int(over_50.index.min()) if not over_50.empty else None
    majority_pct = round(over_50.iloc[0], 1) if not over_50.empty else 0
    data_max_year = int(full_yearly["year"].max())
    latest_spacex_pct = round(spacex_by_year.get(data_max_year, 0), 1)

    total_spacex = len(DF[DF["customer_category"] == "SpaceX (Internal)"])

    fig.update_layout(
        title=dict(
            text=(
                "From Diversified to Dependent: SpaceX's Customer Concentration"
                f"<br><sup style='color:#666'>{total_spacex} of {_TOTAL_LAUNCHES} "
                f"completed launches are SpaceX's own — predominantly Starlink</sup>"
            ),
            x=0.5,
            xanchor="center",
            font=dict(size=16),
        ),
        xaxis=dict(dtick=1, title="Year"),
        yaxis=dict(range=[0, 105], title="Share (%)"),
        barmode="stack",
        height=620,
        margin=dict(t=80, b=80, l=60, r=180),
        legend=dict(
            orientation="h", yanchor="top", y=-0.1,
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
        fig.add_hline(y=50, line_dash="dash", line_color="#999", line_width=1.5)
        fig.add_annotation(
            text="50% concentration<br>threshold",
            xref="paper", yref="y", x=1.02, y=50,
            showarrow=False, font=dict(size=10, color="#666"), xanchor="left",
        )

        if (majority_year is not None
                and y_min <= majority_year <= y_max
                and "SpaceX (Internal)" in categories):
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

        if (y_min <= data_max_year <= y_max
                and "SpaceX (Internal)" in categories):
            fig.add_annotation(
                x=data_max_year, y=latest_spacex_pct / 2,
                text=f"<b>{latest_spacex_pct:.0f}%</b><br>SpaceX share",
                showarrow=True, arrowhead=2, arrowsize=1.2, arrowcolor="#1A237E",
                ax=70, ay=20,
                font=dict(size=11, color="#1A237E"),
                bgcolor="white", bordercolor="#1A237E", borderwidth=1, borderpad=4,
            )

    # --- Data table ---
    table_df = filtered[["net", "launch_name", "rocket_name", "mission_type",
                          "customer_category", "mission_owner_primary_name"]].copy()
    table_df["net"] = table_df["net"].dt.strftime("%Y-%m-%d")
    table_df["mission_owner_primary_name"] = table_df["mission_owner_primary_name"].fillna("Unknown")
    table_df = table_df.rename(columns={
        "net": "Date", "launch_name": "Mission", "rocket_name": "Rocket",
        "mission_type": "Type", "customer_category": "Category",
        "mission_owner_primary_name": "Owner",
    }).sort_values("Date", ascending=False)
    columns = [{"name": c, "id": c} for c in table_df.columns]

    return fig, table_df.to_dict("records"), columns, stat_cards


if __name__ == "__main__":
    app.run(debug=True)
