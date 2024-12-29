from dash import html
import dash_bootstrap_components as dbc


class SurveyMenu:
    @staticmethod
    def create_list_group_item(
        _id: str, icon: str, text: str, href: str, action: bool = True, **kwargs
    ):
        return dbc.ListGroupItem(
            [html.I(className=icon), html.Span(text, className="ms-2")],
            id=_id,
            href=href,
            action=action,
            **kwargs,
        )

    def create_base_menu(self, **kwargs):
        return dbc.ListGroup(
            [
                self.create_list_group_item(
                    "menu-home", "fa-solid fa-home", "Home", "/", action=True
                )
            ],
            id="menu-items",
            flush=True,
            **kwargs,
        )

    def add_link_to_menu(
        self,
        current_menu_items: list,
        new_list_item: dbc.ListGroupItem,
        new_link_position: int,
    ):
        current_menu = current_menu_items.copy()

        current_menu_links = [item.get("props").get("href") for item in current_menu]
        if new_list_item.href not in current_menu_links:
            current_menu.insert(new_link_position, new_list_item.to_plotly_json())

        return current_menu


survey_menu = SurveyMenu()
