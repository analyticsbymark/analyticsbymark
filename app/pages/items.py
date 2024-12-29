import dash
from dash import html
import dash_bootstrap_components as dbc



dash.register_page(__name__, path="/items", order=2)


def layout(**kwargs):

    return dbc.Container(
        [
            html.H1("This is my items page"),
        ],
    )
