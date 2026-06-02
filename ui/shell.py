import flet as ft

from ui.views.evaluation_view import build_evaluation_view, initial_evaluation_state
from ui.views.home_view import build_home_view, build_welcome_view


def build_shell(page: ft.Page) -> ft.Control:
    container = ft.Container(expand=True)
    shell = ft.Container(
        content=container,
        expand=True,
        padding=ft.padding.symmetric(horizontal=56, vertical=42),
        bgcolor="#F3F4F6",
    )
    evaluation_state = initial_evaluation_state()

    def sync_shell_height():
        shell.height = page.height or page.window.height or 820

    def render_welcome(e=None):
        sync_shell_height()
        container.content = build_welcome_view(go_lobby=render_home)
        container.alignment = ft.Alignment.CENTER
        page.update()

    def render_home(e=None):
        sync_shell_height()
        container.content = build_home_view(
            go_comp_21=lambda e=None: render_evaluation("2.1"),
            go_comp_22=lambda e=None: render_evaluation("2.2"),
            go_comp_23=lambda e=None: render_evaluation("2.3"),
            state=evaluation_state,
        )
        container.alignment = ft.Alignment.TOP_CENTER
        page.update()

    def render_evaluation(competence: str):
        sync_shell_height()
        evaluation_state["active_competence"] = competence
        container.content = build_evaluation_view(
            page=page,
            state=evaluation_state,
            go_home=render_home,
        )
        container.alignment = ft.Alignment.TOP_CENTER
        page.update()

    def handle_resize(e):
        sync_shell_height()
        page.update()

    page.on_resized = handle_resize
    render_welcome()

    return shell
