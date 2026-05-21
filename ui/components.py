import flet as ft


PRIMARY = "#2563EB"
PRIMARY_DARK = "#1E40AF"
BG = "#F3F4F6"
CARD_BG = "#FFFFFF"
TEXT = "#111827"
MUTED = "#6B7280"
BORDER = "#E5E7EB"


def app_header(title: str, subtitle: str | None = None) -> ft.Control:
    controls = [
        ft.Text(title, size=28, weight=ft.FontWeight.BOLD, color=TEXT),
    ]

    if subtitle:
        controls.append(ft.Text(subtitle, size=15, color=MUTED))

    return ft.Container(
        content=ft.Column(controls=controls, spacing=6),
        padding=ft.padding.only(bottom=8),
    )


def page_section_title(text: str) -> ft.Text:
    return ft.Text(text, size=26, weight=ft.FontWeight.BOLD, color=TEXT)


def page_section_subtitle(text: str) -> ft.Text:
    return ft.Text(text, size=15, color=MUTED)


def info_box(content: ft.Control, bgcolor: str = "#EFF6FF") -> ft.Container:
    return ft.Container(
        content=content,
        bgcolor=bgcolor,
        border_radius=18,
        padding=22,
        border=ft.border.all(1, BORDER),
    )


def modern_card(content: ft.Control, padding: int = 22) -> ft.Container:
    return ft.Container(
        content=content,
        bgcolor=CARD_BG,
        border_radius=22,
        padding=padding,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(
            blur_radius=18,
            spread_radius=1,
            color="#14000000",
            offset=ft.Offset(0, 4),
        ),
    )


def primary_button(text: str, on_click=None, disabled: bool = False) -> ft.ElevatedButton:
    return ft.ElevatedButton(
        text,
        on_click=on_click,
        disabled=disabled,
        height=44,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=14),
            bgcolor=PRIMARY,
            color=ft.Colors.WHITE,
        ),
    )


def secondary_button(text: str, on_click=None, disabled: bool = False) -> ft.OutlinedButton:
    return ft.OutlinedButton(
        text,
        on_click=on_click,
        disabled=disabled,
        height=44,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=14),
        ),
    )


def competence_card(
    title: str,
    subtitle: str,
    button_text: str,
    button_enabled: bool,
    on_click,
) -> ft.Control:
    return ft.Container(
        col={"xs": 12, "md": 4},
        content=modern_card(
            ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Text(title, size=20, weight=ft.FontWeight.BOLD, color=TEXT),
                    ),
                    ft.Text(subtitle, size=14, color=MUTED),
                    ft.Container(expand=True),
                    primary_button(button_text, on_click=on_click, disabled=not button_enabled),
                ],
                spacing=12,
                height=190,
            )
        ),
    )


def level_chip(label: str, active: bool = False, completed: bool = False) -> ft.Container:
    if completed:
        bgcolor = "#DCFCE7"
        text_color = "#166534"
        border_color = "#86EFAC"
    elif active:
        bgcolor = "#DBEAFE"
        text_color = PRIMARY_DARK
        border_color = "#93C5FD"
    else:
        bgcolor = "#F9FAFB"
        text_color = MUTED
        border_color = BORDER

    return ft.Container(
        content=ft.Text(label, weight=ft.FontWeight.BOLD, color=text_color),
        bgcolor=bgcolor,
        border=ft.border.all(1, border_color),
        border_radius=999,
        padding=ft.padding.symmetric(horizontal=20, vertical=10),
    )


def indicator_status_card(code: str, title: str, completed: bool) -> ft.Container:
    status_text = "Superada" if completed else "Pendiente"
    status_color = "#16A34A" if completed else "#EA580C"

    return modern_card(
        ft.Column(
            controls=[
                ft.Text(code, size=13, color=MUTED),
                ft.Text(title, size=15, weight=ft.FontWeight.W_600, color=TEXT),
                ft.Text(status_text, size=13, color=status_color),
            ],
            spacing=6,
        ),
        padding=16,
    )


def question_block(title: str, statement: str, content: ft.Control) -> ft.Container:
    return modern_card(
        ft.Column(
            controls=[
                ft.Text(title, size=24, weight=ft.FontWeight.BOLD, color=TEXT),
                ft.Text(statement, size=15, color=MUTED),
                ft.Divider(height=24, color=BORDER),
                content,
            ],
            spacing=14,
        ),
        padding=26,
    )