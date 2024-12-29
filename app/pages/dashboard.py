import pandas as pd
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

from app.components.charts import charts
from app.components.utils import id_factory

page_id = id_factory("dashboard")

dash.register_page(__name__, path="/", top_nav=True)

# Build a dataframe with test data
df = pd.DataFrame(
    {
        "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
        "Amount": [4, 1, 2, 2, 4, 5],
        "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"],
    }
)

# Build a figure
fig = charts.create_bar_grouped(
    df=df, x_column="Fruit", y_column="Amount", color_column="City", title="Survey"
)


def layout(**kwargs):

    return dbc.Container(
        [
            html.H1("Hello Dash - This is my Analytics application"),
            html.Div("Dash: A web application framework for python"),
            dcc.Graph(id="example-graph", figure=fig),
        ],
    )
