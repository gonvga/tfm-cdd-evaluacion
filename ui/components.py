import flet as ft


PRIMARY = "#2563EB"
PRIMARY_DARK = "#1E40AF"
BG = "#F3F4F6"
CARD_BG = "#FFFFFF"
TEXT = "#111827"
MUTED = "#6B7280"
BORDER = "#E5E7EB"

ACCESSIBILITY = {
    "scale": 1.0,
    "high_contrast": False,
}

BODY_TEXT_SIZE = 15
LABEL_TEXT_SIZE = 14
MIN_READABLE_SIZE = 12

LOW_CONTRAST_TEXT_COLORS = {
    "#4B5563",
    "#6B7280",
    "#64748B",
    "#374151",
    ft.Colors.GREY_700,
}

SOFT_BACKGROUNDS = {
    "#F3F4F6",
    "#F8FAFC",
    "#F9FAFB",
    "#FFFFFF",
    ft.Colors.BLUE_50,
    "#EFF6FF",
    "#DBEAFE",
    "#FEF2F2",
    "#FFF7ED",
    "#FFFBEB",
    "#DCFCE7",
}


def set_accessibility_scale(scale: float) -> None:
    ACCESSIBILITY["scale"] = max(1.0, min(1.35, scale))


def increase_accessibility_scale() -> None:
    set_accessibility_scale(ACCESSIBILITY["scale"] + 0.12)


def decrease_accessibility_scale() -> None:
    set_accessibility_scale(ACCESSIBILITY["scale"] - 0.12)


def toggle_high_contrast() -> None:
    ACCESSIBILITY["high_contrast"] = not ACCESSIBILITY["high_contrast"]


def reset_accessibility() -> None:
    ACCESSIBILITY["scale"] = 1.0
    ACCESSIBILITY["high_contrast"] = False


def scaled(size: int | float | None, minimum: int = MIN_READABLE_SIZE) -> int:
    base = BODY_TEXT_SIZE if size is None else size
    return max(minimum, round(base * ACCESSIBILITY["scale"]))


def scaled_dimension(size: int | float | None) -> int | None:
    if size is None:
        return None
    return round(size * ACCESSIBILITY["scale"])


def _base_value(obj, key: str, current):
    bases = getattr(obj, "_cdd_accessibility_base", None)
    if bases is None:
        bases = {}
        setattr(obj, "_cdd_accessibility_base", bases)
    if key not in bases:
        bases[key] = current
    return bases[key]


def _text_style(
    size: int | float | None,
    color: str | None = None,
    minimum: int = MIN_READABLE_SIZE,
) -> ft.TextStyle:
    return ft.TextStyle(size=scaled(size, minimum=minimum), color=color)


def _scale_text_style(
    owner,
    attr: str,
    fallback_size: int,
    color: str | None = None,
    minimum: int = MIN_READABLE_SIZE,
) -> None:
    style = getattr(owner, attr, None)
    if style is None:
        setattr(owner, attr, _text_style(fallback_size, color=color, minimum=minimum))
        return

    base_size = _base_value(style, "size", getattr(style, "size", None) or fallback_size)
    style.size = scaled(base_size, minimum=minimum)
    if color and getattr(style, "color", None) is None:
        style.color = color


def _apply_high_contrast(control) -> None:
    color = getattr(control, "color", None)
    if color in LOW_CONTRAST_TEXT_COLORS:
        control.color = "#111111"
    elif color in {PRIMARY, PRIMARY_DARK, "#1D4ED8", "#1E40AF"}:
        control.color = "#003A8C"
    elif color in {ft.Colors.GREEN, "#16A34A", "#166534"}:
        control.color = "#005A1F"
    elif color in {ft.Colors.RED, "#991B1B", "#7F1D1D"}:
        control.color = "#8B0000"

    bgcolor = getattr(control, "bgcolor", None)
    if bgcolor in SOFT_BACKGROUNDS:
        control.bgcolor = "#FFFFFF"
    elif bgcolor == PRIMARY:
        control.bgcolor = "#003A8C"
    elif bgcolor == ft.Colors.GREEN:
        control.bgcolor = "#005A1F"
    elif bgcolor == ft.Colors.RED:
        control.bgcolor = "#8B0000"

    if hasattr(control, "border") and getattr(control, "border", None):
        control.border = ft.border.all(1.5, "#111111")


def _apply_text_sizing(control) -> None:
    if isinstance(control, ft.Text):
        base_size = _base_value(control, "size", control.size)
        control.size = scaled(base_size)
        if ACCESSIBILITY["high_contrast"] and control.color in LOW_CONTRAST_TEXT_COLORS:
            control.color = "#111111"

    if isinstance(control, (ft.Radio, ft.Checkbox)):
        _scale_text_style(control, "label_style", BODY_TEXT_SIZE, color=TEXT)

    if isinstance(control, (ft.Dropdown, ft.TextField)):
        base_text_size = _base_value(control, "text_size", control.text_size or BODY_TEXT_SIZE)
        control.text_size = scaled(base_text_size)
        _scale_text_style(control, "text_style", BODY_TEXT_SIZE, color=TEXT)
        _scale_text_style(control, "label_style", LABEL_TEXT_SIZE, color=MUTED)
        _scale_text_style(control, "hint_style", LABEL_TEXT_SIZE, color=MUTED)
        _scale_text_style(control, "helper_style", LABEL_TEXT_SIZE, color=MUTED)
        _scale_text_style(control, "error_style", LABEL_TEXT_SIZE, color="#8B0000")

    if isinstance(control, ft.Dropdown):
        for option in control.options:
            if option.content is None and option.text:
                option.content = ft.Text(option.text, size=BODY_TEXT_SIZE, color=TEXT)
            if option.content is not None:
                apply_accessibility(option.content)

    if isinstance(control, ft.DataTable):
        control.data_text_style = _text_style(BODY_TEXT_SIZE, color=TEXT)
        control.heading_text_style = _text_style(
            LABEL_TEXT_SIZE,
            color=TEXT,
            minimum=LABEL_TEXT_SIZE,
        )
        control.data_row_min_height = scaled_dimension(
            _base_value(control, "data_row_min_height", control.data_row_min_height or 44)
        )
        control.data_row_max_height = scaled_dimension(
            _base_value(control, "data_row_max_height", control.data_row_max_height or 56)
        )
        control.heading_row_height = scaled_dimension(
            _base_value(control, "heading_row_height", control.heading_row_height or 48)
        )

    if isinstance(control, (ft.ElevatedButton, ft.OutlinedButton, ft.TextButton)):
        if control.style is None:
            control.style = ft.ButtonStyle()
        if getattr(control.style, "text_style", None) is None:
            control.style.text_style = _text_style(BODY_TEXT_SIZE, minimum=LABEL_TEXT_SIZE)
        else:
            base_size = _base_value(
                control.style.text_style,
                "size",
                getattr(control.style.text_style, "size", None) or BODY_TEXT_SIZE,
            )
            control.style.text_style.size = scaled(base_size, minimum=LABEL_TEXT_SIZE)


def apply_accessibility(control) -> None:
    if control is None:
        return

    _apply_text_sizing(control)
    if ACCESSIBILITY["high_contrast"]:
        _apply_high_contrast(control)

    for attr in ("content", "label"):
        child = getattr(control, attr, None)
        if isinstance(child, ft.Control):
            apply_accessibility(child)

    for attr in ("controls", "columns", "rows", "cells"):
        children = getattr(control, attr, None)
        if not isinstance(children, (list, tuple)):
            continue
        for child in children:
            apply_accessibility(child)


def build_accessibility_toolbar(on_decrease, on_increase, on_contrast, on_reset) -> ft.Control:
    contrast_label = "Contraste alto: sí" if ACCESSIBILITY["high_contrast"] else "Contraste alto"
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Text("Accesibilidad", size=13, weight=ft.FontWeight.BOLD, color=TEXT),
                ft.OutlinedButton("A-", on_click=on_decrease, height=38),
                ft.OutlinedButton("A+", on_click=on_increase, height=38),
                ft.OutlinedButton(contrast_label, on_click=on_contrast, height=38),
                ft.TextButton("Restablecer", on_click=on_reset, height=38),
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            wrap=True,
        ),
        alignment=ft.Alignment.CENTER_RIGHT,
        padding=ft.padding.only(bottom=12),
    )


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


def scenario_panel(text: str) -> ft.Container:
    scenario_text = text.removeprefix("Escenario:").strip()
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.DESCRIPTION_OUTLINED,
                        size=24,
                        color=PRIMARY_DARK,
                    ),
                    width=44,
                    height=44,
                    alignment=ft.Alignment.CENTER,
                    bgcolor="#DBEAFE",
                    border_radius=12,
                ),
                ft.Column(
                    controls=[
                        ft.Text(
                            "Escenario",
                            size=13,
                            weight=ft.FontWeight.BOLD,
                            color=PRIMARY_DARK,
                        ),
                        ft.Text(
                            scenario_text,
                            size=15,
                            weight=ft.FontWeight.W_500,
                            color=TEXT,
                        ),
                    ],
                    spacing=4,
                    expand=True,
                ),
            ],
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.START,
        ),
        bgcolor="#EFF6FF",
        border=ft.border.all(1, "#93C5FD"),
        border_radius=16,
        padding=18,
    )


def checkbox_feedback(selected: bool, expected: bool, detail: str = "") -> tuple[str, bool]:
    passed = selected == expected
    if expected:
        action = "Bien marcada." if selected else "Mal sin marcar."
    else:
        action = "Mal marcada." if selected else "Bien sin marcar."
    return f"{action} {detail}".strip(), passed


def question_block(title: str, statement: str, content: ft.Control) -> ft.Container:
    controls = getattr(content, "controls", None)
    if controls and isinstance(controls[0], ft.Text):
        intro = controls[0].value or ""
        if intro.strip().lower().startswith("escenario:"):
            controls[0] = scenario_panel(intro)

    return modern_card(
        ft.Column(
            controls=[content],
            spacing=0,
        ),
        padding=26,
    )
