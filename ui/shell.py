import flet as ft

from ui.views.evaluation_view import build_evaluation_view, initial_evaluation_state
from ui.views.home_view import build_welcome_view


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
        container.content = build_welcome_view(start_evaluation=render_evaluation)
        container.alignment = ft.Alignment.CENTER
        page.update()

    def restart_evaluation(e=None):
        evaluation_state.clear()
        evaluation_state.update(initial_evaluation_state())
        render_welcome()

    def render_evaluation(e=None):
        sync_shell_height()
        container.content = build_evaluation_view(
            page=page,
            state=evaluation_state,
            restart_evaluation=restart_evaluation,
        )
        container.alignment = ft.Alignment.TOP_CENTER
        page.update()

    def handle_resize(e):
        sync_shell_height()
        page.update()

    page.on_resized = handle_resize
    render_welcome()

    return shell
