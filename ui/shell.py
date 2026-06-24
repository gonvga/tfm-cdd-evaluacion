import flet as ft

from ui.components import (
    ACCESSIBILITY,
    apply_accessibility,
    build_accessibility_toolbar,
    decrease_accessibility_scale,
    increase_accessibility_scale,
    reset_accessibility,
    toggle_high_contrast,
)
from ui.views.evaluation_view import build_evaluation_view, initial_evaluation_state
from ui.views.home_view import build_welcome_view


def build_shell(page: ft.Page) -> ft.Control:
    container = ft.Container(expand=True)
    toolbar_slot = ft.Container()
    shell = ft.Container(
        expand=True,
        padding=ft.padding.symmetric(horizontal=56, vertical=42),
        bgcolor="#F3F4F6",
    )
    evaluation_state = initial_evaluation_state()
    current_view = "welcome"

    def apply_shell_accessibility():
        shell.bgcolor = "#000000" if ACCESSIBILITY["high_contrast"] else "#F3F4F6"
        page.bgcolor = shell.bgcolor
        apply_accessibility(toolbar_slot.content)
        apply_accessibility(container.content)

    def render_toolbar():
        toolbar_slot.content = build_accessibility_toolbar(
            on_decrease=change_accessibility(decrease_accessibility_scale),
            on_increase=change_accessibility(increase_accessibility_scale),
            on_contrast=change_accessibility(toggle_high_contrast),
            on_reset=change_accessibility(reset_accessibility),
        )

    def rerender_current():
        if current_view == "evaluation":
            render_evaluation()
        else:
            render_welcome()

    def change_accessibility(action):
        def handler(e=None):
            action()
            rerender_current()

        return handler

    shell.content = ft.Column(
        controls=[toolbar_slot, container],
        expand=True,
        spacing=0,
    )

    def sync_shell_height():
        shell.height = page.height or page.window.height or 820

    def render_welcome(e=None):
        nonlocal current_view
        current_view = "welcome"
        sync_shell_height()
        render_toolbar()
        container.content = build_welcome_view(start_evaluation=render_evaluation)
        container.alignment = ft.Alignment.CENTER
        apply_shell_accessibility()
        page.update()

    def restart_evaluation(e=None):
        evaluation_state.clear()
        evaluation_state.update(initial_evaluation_state())
        render_welcome()

    def render_evaluation(e=None):
        nonlocal current_view
        current_view = "evaluation"
        sync_shell_height()
        render_toolbar()
        container.content = build_evaluation_view(
            page=page,
            state=evaluation_state,
            restart_evaluation=restart_evaluation,
        )
        container.alignment = ft.Alignment.TOP_CENTER
        apply_shell_accessibility()
        page.update()

    def handle_resize(e):
        sync_shell_height()
        page.update()

    page.on_resized = handle_resize
    render_welcome()

    return shell
