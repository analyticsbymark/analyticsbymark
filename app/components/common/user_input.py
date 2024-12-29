from typing import Callable
from dash import html
import dash_bootstrap_components as dbc

from app.components.common.button import SingleAnswerButton

def InputWithText(text: str, page_id: Callable, **kwargs):
    return html.Div(
        [
            dbc.Input(placeholder="Type here...", id=page_id("input-text")),
            dbc.FormText(text, id=page_id("form-text")),
        ],
        className="mb-5 col-6 col-mb-3",
    )

def SalaryInputWithText(text: str, page_id: Callable, min_value: int, max_value: int, **kwargs,):
    return html.Div(
        [
            dbc.Input(placeholder="Type here",
                      type="number",
                      min=min_value,
                      max=max_value,
                      id=page_id("input-text"),
                      class_name="styled-numeric-input"),
            dbc.FormText(text, id=page_id("form-text")),
        ],
        className="mb-5 col-8 col-mb-4",
    )

def OtherSkillInput(text: str, page_id: Callable, **kwargs):
    return html.Div(
        [
            html.Div(
                [
                    dbc.Input(placeholder="Type here...", id=page_id("input-text")),
                    dbc.FormText(text, id=page_id("form-text"), className="d-block mb-2"),
                    SingleAnswerButton(text="Add", id_=page_id("other-skill-button"), class_name="mb-2")
                ]
            ),
        ],
        className="mb-5 col-6 col-mb-3",
    )
