from typing import Callable
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc

def create_bar_grouped(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    color_column: str,
    title: str,
    **kwargs,
):
    return px.bar(
        df,
        x=x_column,
        y=y_column,
        color=color_column,
        barmode="group",
        title=title,
        **kwargs,
    )
