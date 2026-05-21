import flet as ft

from ui.views.evaluation_view import build_evaluation_view, initial_evaluation_state
from ui.views.home_view import build_home_view


def build_shell(page: ft.Page) -> ft.Control:
    container = ft.Column(expand=True)
    evaluation_state = initial_evaluation_state()

    def render_home(e=None):
        container.controls = [
            build_home_view(
                go_comp_21=lambda e=None: render_evaluation("2.1"),
                go_comp_22=lambda e=None: render_evaluation("2.2"),
                go_comp_23=lambda e=None: render_evaluation("2.3"),
                state=evaluation_state,
            )
        ]
        page.update()

    def render_evaluation(competence: str):
        evaluation_state["active_competence"] = competence
        container.controls = [
            build_evaluation_view(
                page=page,
                state=evaluation_state,
                go_home=render_home,
            )
        ]
        page.update()

    render_home()

    return ft.Container(
        content=container,
        expand=True,
        padding=ft.padding.symmetric(horizontal=56, vertical=42),
        bgcolor="#F3F4F6",
    )