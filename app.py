import flet as ft
from ui.shell import build_shell


def main(page: ft.Page):
    page.title = "Evaluación CDD"

    page.window.width = 1280
    page.window.height = 820
    page.window.maximized = True

    page.padding = 0
    page.spacing = 0
    page.scroll = ft.ScrollMode.HIDDEN
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.GREY_100

    page.assets_dir = "assets"

    page.add(build_shell(page))

    page.window.maximized = True
    page.update()


if __name__ == "__main__":
    ft.app(target=main)
