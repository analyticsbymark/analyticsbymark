import time
import requests
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
from dash import dcc, callback, Input, Output, State, ALL, html, ctx
from flask import Flask, session

from app.components.common.navbar import navbar

PATH = Path(__file__).parent
ASSET_FOLDER = PATH.joinpath("assets").resolve()

server = Flask(__name__)


app = dash.Dash(
    __name__,
    server=server,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    assets_folder=ASSET_FOLDER,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)

app.layout = dbc.Container(
    [
        dcc.Location(id="url"),
        html.Div(
            navbar.create_navbar(user_status_text="Login", user_status_href="/login"),
            id="user-status-header",
        ),
        dash.page_container,
    ],
)

@callback(
    Output("navbar-menu-popover", "is_open"),
    [Input("navbar-menu-button", "n_clicks")],
    [State("navbar-menu-popover", "is_open")],
)
def toggle_navbar(n, is_open):
    if n:
        return not is_open
    return is_open


if __name__ == "__main__":
    # app.run_server(host="0.0.0.0", debug=True, port=8056)
    app.run_server(host="127.0.0.1", port=8056)
