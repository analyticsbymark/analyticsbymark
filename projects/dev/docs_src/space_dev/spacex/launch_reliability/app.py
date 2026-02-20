"""
SpaceX Launch Reliability — Interactive Dash Application
=========================================================

Kirk Chapter 8: Interactivity — letting the reader explore the failure
timeline on their own terms, guided by the same editorial framing from
the static composition.

Layout rationale
----------------
A sidebar-right layout places the wide failure timeline scatter in the
dominant left column (~75% width) while stacking the compact controls
and the small data table (max 15 rows) in a narrow right sidebar.

Why this layout suits this specific data:
  - The timeline scatter is inherently wide and short — it needs every
    horizontal pixel available to spread 20 years of history legibly.
  - The controls are tiny: 3 checkboxes, 1 toggle, 1 slider. They do
    not warrant a full-width row above the chart.
  - The data table never exceeds 15 rows — it fits comfortably in a
    narrow column and stays visible alongside the chart, eliminating
    the need to scroll between chart and table.
  - The user's eye reads left-to-right: chart tells the story first,
    sidebar lets them explore and drill into individual events.

Controls:
  1. Rocket family checklist — isolate individual vehicle families
  2. Annotation toggle — layer editorial context on/off
  3. Year range slider — filter the timeline to a date range

Run with: python app.py
Open:     http://localhost:8050
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dash import Dash, html, dcc, dash_table, callback, Output, Input

from data.utils import get_spacex_data

# ---------------------------------------------------------------------------
# Constants (identical to tutorial_final.py)
# ---------------------------------------------------------------------------

FAILURE_STATUSES = {"Failure", "Partial Failure"}

ROCKET_FAMILY_COLORS = {
    "Falcon 1": "#C0392B",
    "Falcon 9": "#2980B9",
    "Starship": "#D4A017",
}

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

LIFECYCLE_ORDER = ["Falcon 1", "Falcon 9", "Starship"]
SOURCE_TEXT = "Source: Launch Library 2 API | thespacedevs.com"

# ---------------------------------------------------------------------------
# Data: loaded once at startup, filtered to completed launches
# ---------------------------------------------------------------------------

_raw = get_spacex_data()
DF = _raw[_raw["launch_status_abbrev"].isin(["Success", "Failure", "Partial Failure"])].copy()
DF = DF.sort_values("net").reset_index(drop=True)

ALL_YEARS = sorted(DF["year"].unique())
MIN_YEAR, MAX_YEAR = ALL_YEARS[0], ALL_YEARS[-1]

# Total launches and failure counts for subtitle (computed from unfiltered data)
_failures_all = DF[DF["launch_status_abbrev"].isin(FAILURE_STATUSES)].copy()
_failures_all["rocket_family_group"] = (
    _failures_all["rocket_full_name"]
    .map(ROCKET_FAMILY_MAP)
    .fillna(_failures_all["rocket_full_name"])
)
_TOTAL_LAUNCHES = len(DF)
_TOTAL_FAILURES = len(_failures_all)
_DATE_MIN_YEAR = int(DF["net"].min().year)
_DATE_MAX_YEAR = int(DF["net"].max().year)
del _failures_all


# ---------------------------------------------------------------------------
# Annotation computation (matches tutorial_final.py's compute_insights)
# ---------------------------------------------------------------------------

def _compute_insights(df: pd.DataFrame, failures: pd.DataFrame) -> dict:
    """Compute all annotation anchor values from data — nothing hardcoded.

    The Falcon 9 Block 5 reliability gap is measured WITHIN Falcon 9 only
    (Amos-6 Sep 2016 to the last Falcon 9 failure), because the Starship
    and Falcon 9 programs overlapped chronologically.
    """
    f9_failures = (
        failures[failures["rocket_family_group"] == "Falcon 9"]
        .sort_values("net")
        .reset_index(drop=True)
    )
    f1_failures = (
        failures[failures["rocket_family_group"] == "Falcon 1"]
        .sort_values("net")
        .reset_index(drop=True)
    )

    amos6_row = None
    crs7_row = None
    for _, row in f9_failures.iterrows():
        name_lower = str(row["mission_name"]).lower()
        if "amos" in name_lower and "6" in name_lower:
            amos6_row = row
        if "crs-7" in name_lower or "crs 7" in name_lower or "spx crs-7" in name_lower:
            crs7_row = row

    if amos6_row is None and len(f9_failures) >= 2:
        amos6_row = f9_failures.iloc[-2]
    elif amos6_row is None:
        amos6_row = f9_failures.iloc[-1] if len(f9_failures) >= 1 else None

    if crs7_row is None and len(f9_failures) >= 3:
        crs7_row = f9_failures.iloc[-3]

    streak_end_row = f9_failures.iloc[-1] if len(f9_failures) >= 1 else None

    if amos6_row is not None and streak_end_row is not None:
        gap_start = amos6_row["net"]
        gap_end = streak_end_row["net"]
        gap_days = (gap_end - gap_start).days
        gap_years = gap_days / 365.25
        gap_mid = pd.Timestamp(
            (gap_start.value + gap_end.value) // 2,
            unit="ns",
            tz="UTC",
        )
    else:
        gap_start = gap_end = gap_mid = None
        gap_days = 0
        gap_years = 0.0

    if crs7_row is not None and amos6_row is not None:
        cluster_mid = pd.Timestamp(
            (crs7_row["net"].value + amos6_row["net"].value) // 2,
            unit="ns",
            tz="UTC",
        )
        cluster_label = f"{crs7_row['mission_name']} & {amos6_row['mission_name']}"
    elif amos6_row is not None:
        cluster_mid = amos6_row["net"]
        cluster_label = amos6_row["mission_name"]
    else:
        cluster_mid = None
        cluster_label = ""

    f1_mid = f1_failures["net"].mean() if len(f1_failures) > 0 else None
    f1_count = len(f1_failures)
    f1_year_start = int(f1_failures["net"].min().year) if f1_count > 0 else None
    f1_year_end = int(f1_failures["net"].max().year) if f1_count > 0 else None

    return {
        "f1_count": f1_count,
        "f1_mid": f1_mid,
        "f1_year_start": f1_year_start,
        "f1_year_end": f1_year_end,
        "cluster_mid": cluster_mid,
        "cluster_label": cluster_label,
        "gap_start": gap_start,
        "gap_end": gap_end,
        "gap_mid": gap_mid,
        "gap_days": gap_days,
        "gap_years": gap_years,
    }


# Pre-compute insights from unfiltered data once so the callback can
# reference annotation anchors without re-running expensive searches.
_all_failures = DF[DF["launch_status_abbrev"].isin(FAILURE_STATUSES)].copy()
_all_failures["rocket_family_group"] = (
    _all_failures["rocket_full_name"]
    .map(ROCKET_FAMILY_MAP)
    .fillna(_all_failures["rocket_full_name"])
)
GLOBAL_INSIGHTS = _compute_insights(DF, _all_failures)
del _all_failures


# ---------------------------------------------------------------------------
# Shared styles
# ---------------------------------------------------------------------------

_FONT_STACK = "Arial, sans-serif"
_SIDEBAR_WIDTH = "340px"
_BORDER_COLOR = "#E0E0E0"
_LABEL_STYLE = {
    "fontWeight": "600",
    "fontSize": "12px",
    "color": "#555",
    "textTransform": "uppercase",
    "letterSpacing": "0.5px",
    "marginBottom": "6px",
    "display": "block",
}
_SECTION_STYLE = {
    "marginBottom": "20px",
    "paddingBottom": "16px",
    "borderBottom": f"1px solid {_BORDER_COLOR}",
}


# ---------------------------------------------------------------------------
# App layout — sidebar-right: chart dominates left, controls + table right
# ---------------------------------------------------------------------------

app = Dash(__name__)

app.layout = html.Div(
    style={
        "fontFamily": _FONT_STACK,
        "margin": "0",
        "padding": "0",
        "backgroundColor": "#FAFAFA",
        "minHeight": "100vh",
    },
    children=[
        # --- Header bar ---
        html.Div(
            style={
                "backgroundColor": "white",
                "borderBottom": f"2px solid {_BORDER_COLOR}",
                "padding": "16px 28px",
            },
            children=[
                html.H2(
                    "SpaceX Failure Timeline: From Development Chaos to "
                    "Operational Reliability",
                    style={
                        "margin": "0 0 4px 0",
                        "fontSize": "20px",
                        "color": "#111",
                        "fontWeight": "700",
                    },
                ),
                html.P(
                    (
                        f"Across {_TOTAL_LAUNCHES} completed launches "
                        f"({_DATE_MIN_YEAR}\u2013{_DATE_MAX_YEAR}), SpaceX "
                        f"recorded {_TOTAL_FAILURES} failures or partial "
                        f"failures. Use the controls to trace how each "
                        f"vehicle\u2019s reliability arc unfolded."
                    ),
                    style={
                        "margin": "0",
                        "color": "#666",
                        "fontSize": "13px",
                        "lineHeight": "1.5",
                    },
                ),
            ],
        ),

        # --- Main content: chart (left) + sidebar (right) ---
        html.Div(
            style={
                "display": "flex",
                "gap": "0",
                "minHeight": "calc(100vh - 100px)",
            },
            children=[
                # LEFT column: the chart — takes all remaining space
                html.Div(
                    style={
                        "flex": "1",
                        "minWidth": "0",
                        "padding": "20px 24px 16px 24px",
                        "backgroundColor": "white",
                    },
                    children=[
                        dcc.Graph(
                            id="failure-chart",
                            style={"width": "100%", "height": "100%"},
                            config={
                                "displayModeBar": True,
                                "displaylogo": False,
                                "modeBarButtonsToRemove": [
                                    "select2d",
                                    "lasso2d",
                                ],
                            },
                        ),
                    ],
                ),

                # RIGHT sidebar: controls + data table stacked
                html.Div(
                    style={
                        "width": _SIDEBAR_WIDTH,
                        "minWidth": _SIDEBAR_WIDTH,
                        "borderLeft": f"2px solid {_BORDER_COLOR}",
                        "padding": "20px",
                        "backgroundColor": "#FAFAFA",
                        "overflowY": "auto",
                    },
                    children=[
                        # Section: Rocket Family filter
                        html.Div(
                            style=_SECTION_STYLE,
                            children=[
                                html.Label(
                                    "Rocket Family",
                                    style=_LABEL_STYLE,
                                ),
                                dcc.Checklist(
                                    id="family-filter",
                                    options=[
                                        {"label": family, "value": family}
                                        for family in LIFECYCLE_ORDER
                                    ],
                                    value=list(LIFECYCLE_ORDER),
                                    style={"fontSize": "13px"},
                                    labelStyle={
                                        "display": "block",
                                        "marginBottom": "4px",
                                        "cursor": "pointer",
                                    },
                                ),
                            ],
                        ),

                        # Section: Annotations toggle
                        html.Div(
                            style=_SECTION_STYLE,
                            children=[
                                html.Label(
                                    "Annotations",
                                    style=_LABEL_STYLE,
                                ),
                                dcc.Checklist(
                                    id="annotation-toggle",
                                    options=[
                                        {
                                            "label": "Show editorial annotations",
                                            "value": "on",
                                        }
                                    ],
                                    value=["on"],
                                    style={"fontSize": "13px"},
                                    labelStyle={"cursor": "pointer"},
                                ),
                            ],
                        ),

                        # Section: Year range slider
                        html.Div(
                            style=_SECTION_STYLE,
                            children=[
                                html.Label(
                                    "Year Range",
                                    style=_LABEL_STYLE,
                                ),
                                dcc.RangeSlider(
                                    id="year-range",
                                    min=MIN_YEAR,
                                    max=MAX_YEAR,
                                    value=[MIN_YEAR, MAX_YEAR],
                                    marks={
                                        str(y): {
                                            "label": str(y),
                                            "style": {"fontSize": "10px"},
                                        }
                                        for y in ALL_YEARS
                                        if y % 5 == 0
                                        or y == MIN_YEAR
                                        or y == MAX_YEAR
                                    },
                                    step=1,
                                    tooltip={
                                        "placement": "bottom",
                                        "always_visible": False,
                                    },
                                ),
                            ],
                        ),

                        # Section: Filtered failure events table
                        html.Div(
                            children=[
                                html.Label(
                                    "Failure Events",
                                    style=_LABEL_STYLE,
                                ),
                                html.Div(
                                    id="table-summary",
                                    style={
                                        "fontSize": "12px",
                                        "color": "#888",
                                        "marginBottom": "8px",
                                    },
                                ),
                                dash_table.DataTable(
                                    id="data-table",
                                    sort_action="native",
                                    page_size=15,
                                    style_table={
                                        "overflowX": "auto",
                                        "border": f"1px solid {_BORDER_COLOR}",
                                        "borderRadius": "4px",
                                    },
                                    style_header={
                                        "fontWeight": "bold",
                                        "backgroundColor": "#F0F0F0",
                                        "fontSize": "11px",
                                        "color": "#333",
                                    },
                                    style_cell={
                                        "textAlign": "left",
                                        "padding": "6px 8px",
                                        "fontSize": "11px",
                                        "whiteSpace": "normal",
                                        "minWidth": "60px",
                                    },
                                    style_data_conditional=[
                                        {
                                            "if": {"row_index": "odd"},
                                            "backgroundColor": "#F9F9F9",
                                        },
                                    ],
                                ),
                            ],
                        ),

                        # Footer: source attribution
                        html.P(
                            SOURCE_TEXT,
                            style={
                                "color": "#AAA",
                                "fontSize": "10px",
                                "marginTop": "20px",
                                "borderTop": f"1px solid {_BORDER_COLOR}",
                                "paddingTop": "12px",
                            },
                        ),
                    ],
                ),
            ],
        ),
    ],
)


# ---------------------------------------------------------------------------
# Callback: rebuild chart and table on any control change
# ---------------------------------------------------------------------------

@callback(
    Output("failure-chart", "figure"),
    Output("data-table", "data"),
    Output("data-table", "columns"),
    Output("table-summary", "children"),
    Input("year-range", "value"),
    Input("family-filter", "value"),
    Input("annotation-toggle", "value"),
)
def update_chart(
    year_range: list,
    families: list,
    annotations: list,
) -> tuple:
    """Rebuild the failure timeline scatter and data table from filtered data.

    Kirk Ch 8: Annotation values are computed from UNFILTERED data first
    (GLOBAL_INSIGHTS), then we check whether the relevant anchor points
    fall within the current filter window before rendering each callout.
    This avoids annotations shifting or disappearing when the user narrows
    the year range slightly.
    """
    y_min, y_max = year_range
    families = families or []

    # --- Filter failures for the scatter ---
    failures = DF[DF["launch_status_abbrev"].isin(FAILURE_STATUSES)].copy()
    failures["rocket_family_group"] = (
        failures["rocket_full_name"]
        .map(ROCKET_FAMILY_MAP)
        .fillna(failures["rocket_full_name"])
    )
    failures = failures[
        (failures["net"].dt.year >= y_min)
        & (failures["net"].dt.year <= y_max)
        & (failures["rocket_family_group"].isin(families))
    ]

    # --- Build scatter ---
    if failures.empty:
        fig = go.Figure()
        fig.update_layout(
            title="No failure events match the current filters.",
            plot_bgcolor="white",
            paper_bgcolor="white",
            height=560,
        )
    else:
        n_f = len(failures)
        n_t = len(
            DF[
                (DF["net"].dt.year >= y_min)
                & (DF["net"].dt.year <= y_max)
            ]
        )
        date_min = failures["net"].min()
        date_max = failures["net"].max()

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
            labels={
                "net": "Launch Date",
                "launch_status_abbrev": "Outcome",
                "rocket_full_name": "Rocket Variant",
                "rocket_family_group": "Rocket Family",
            },
            color_discrete_map=ROCKET_FAMILY_COLORS,
            category_orders={"rocket_family_group": LIFECYCLE_ORDER},
        )
        fig.update_traces(marker=dict(size=13))

        fig.update_layout(
            height=560,
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family=_FONT_STACK, size=12, color="#333333"),
            margin=dict(l=80, r=40, t=170, b=120),
            title=dict(
                text=(
                    f"{n_f} Failure{'s' if n_f != 1 else ''} in "
                    f"{n_t} Launches: How SpaceX Built Reliability"
                    f"<br><sup style='color:#555555; font-size:12px'>"
                    f"Each point is one failure or partial failure, "
                    f"colored by rocket family "
                    f"\u2014 {date_min.year}\u2013{date_max.year}"
                    f"</sup>"
                ),
                font=dict(size=17, color="#111111"),
                x=0.0,
                xanchor="left",
            ),
            legend=dict(
                title="Rocket Family",
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1.0,
                font=dict(size=11),
            ),
            xaxis=dict(
                title="Launch Date",
                showgrid=True,
                gridcolor="#E8E8E8",
                gridwidth=1,
                zeroline=False,
            ),
            yaxis=dict(
                title="Outcome",
                showgrid=False,
                zeroline=False,
            ),
        )

        # --- Annotations (only when toggle is on) ---
        show = "on" in (annotations or [])
        if show:
            insights = GLOBAL_INSIGHTS

            # Annotation 1: Falcon 1 development era cluster
            f1_mid = insights["f1_mid"]
            f1_count = insights["f1_count"]
            f1_y_start = insights["f1_year_start"]
            f1_y_end = insights["f1_year_end"]
            f1_in_view = (
                f1_mid is not None
                and "Falcon 1" in families
                and f1_y_start is not None
                and f1_y_start >= y_min
                and f1_y_end is not None
                and f1_y_end <= y_max
            )
            if f1_in_view:
                fig.add_annotation(
                    x=f1_mid,
                    y="Failure",
                    text=(
                        f"<b>Development era</b><br>"
                        f"{f1_count} failures in first "
                        f"{f1_count} flights<br>"
                        f"({f1_y_start}\u2013{f1_y_end})"
                    ),
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1.0,
                    arrowwidth=1.5,
                    arrowcolor=ROCKET_FAMILY_COLORS["Falcon 1"],
                    ax=0,
                    ay=-75,
                    font=dict(
                        size=11,
                        color=ROCKET_FAMILY_COLORS["Falcon 1"],
                    ),
                    bgcolor="rgba(255,255,255,0.90)",
                    bordercolor=ROCKET_FAMILY_COLORS["Falcon 1"],
                    borderwidth=1.2,
                    borderpad=5,
                    align="center",
                    standoff=8,
                )

            # Annotation 2: CRS-7 / Amos-6 pivot point
            cluster_mid = insights["cluster_mid"]
            gap_start = insights["gap_start"]
            cluster_in_view = (
                cluster_mid is not None
                and "Falcon 9" in families
                and gap_start is not None
                and gap_start.year >= y_min
                and cluster_mid.year <= y_max
            )
            if cluster_in_view:
                fig.add_annotation(
                    x=cluster_mid,
                    y="Failure",
                    text=(
                        f"<b>Pivot point</b><br>"
                        f"{insights['cluster_label']}<br>"
                        f"Failures that triggered<br>"
                        f"the Block 5 redesign"
                    ),
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1.0,
                    arrowwidth=1.5,
                    arrowcolor=ROCKET_FAMILY_COLORS["Falcon 9"],
                    ax=0,
                    ay=80,
                    font=dict(
                        size=11,
                        color=ROCKET_FAMILY_COLORS["Falcon 9"],
                    ),
                    bgcolor="rgba(255,255,255,0.90)",
                    bordercolor=ROCKET_FAMILY_COLORS["Falcon 9"],
                    borderwidth=1.2,
                    borderpad=5,
                    align="center",
                    standoff=8,
                )

            # Annotation 3: Block 5 gap shading + callout
            gap_end = insights["gap_end"]
            gap_mid = insights["gap_mid"]
            gap_in_view = (
                gap_start is not None
                and gap_end is not None
                and gap_mid is not None
                and "Falcon 9" in families
                and gap_start.year >= y_min
                and gap_end.year <= y_max
            )
            if gap_in_view:
                fig.add_vrect(
                    x0=gap_start,
                    x1=gap_end,
                    fillcolor="rgba(41, 128, 185, 0.07)",
                    line_width=0,
                    layer="below",
                )
                for boundary in [gap_start, gap_end]:
                    fig.add_shape(
                        type="line",
                        x0=boundary,
                        x1=boundary,
                        y0=0,
                        y1=1,
                        yref="paper",
                        line=dict(
                            color="#2980B9",
                            width=1,
                            dash="dot",
                        ),
                    )
                fig.add_annotation(
                    x=gap_mid,
                    y=1.0,
                    yref="paper",
                    text=(
                        f"<b>Falcon 9 Block 5: "
                        f"{insights['gap_days']:,} days "
                        f"without a failure</b><br>"
                        f"({insights['gap_years']:.1f} years \u2014 "
                        f"{gap_start.strftime('%b %Y')} to "
                        f"{gap_end.strftime('%b %Y')})"
                    ),
                    showarrow=False,
                    font=dict(size=12, color="#2980B9"),
                    bgcolor="rgba(255,255,255,0.92)",
                    bordercolor="#2980B9",
                    borderwidth=1.5,
                    borderpad=6,
                    align="center",
                    # yanchor="bottom" places the text box ABOVE the plot area
                    # (into the top margin) instead of hanging down into it,
                    # which would cover Starship partial failure points at ~2020.
                    yanchor="bottom",
                    xanchor="center",
                )

    # --- Data table: failure/partial failure events, filtered, date desc ---
    table_raw = DF[
        (DF["launch_status_abbrev"].isin(FAILURE_STATUSES))
        & (DF["net"].dt.year >= y_min)
        & (DF["net"].dt.year <= y_max)
    ].copy()
    table_raw["rocket_family_group"] = (
        table_raw["rocket_full_name"]
        .map(ROCKET_FAMILY_MAP)
        .fillna(table_raw["rocket_full_name"])
    )
    table_raw = table_raw[table_raw["rocket_family_group"].isin(families)]

    table_df = table_raw[
        ["net", "mission_name", "rocket_full_name", "launch_status_abbrev"]
    ].copy()
    table_df["net"] = table_df["net"].dt.strftime("%Y-%m-%d")
    table_df = table_df.rename(
        columns={
            "net": "Date",
            "mission_name": "Mission",
            "rocket_full_name": "Rocket",
            "launch_status_abbrev": "Outcome",
        }
    ).sort_values("Date", ascending=False)

    columns = [{"name": c, "id": c} for c in table_df.columns]
    n_shown = len(table_df)
    summary = f"Showing {n_shown} of {_TOTAL_FAILURES} total failure events"

    return fig, table_df.to_dict("records"), columns, summary


if __name__ == "__main__":
    app.run(debug=True)
