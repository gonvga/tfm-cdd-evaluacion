import flet as ft

from ui.components import info_box, modern_card, primary_button
from ui.views.evaluation_view import COMPETENCE_INFO, get_competence_status


def _test_badge(code: str, title: str, level: str, completed: bool, failed: bool) -> ft.Control:
    status_text = "Superada" if completed else "No superada" if failed else "Pendiente"
    status_color = "#16A34A" if completed else "#DC2626" if failed else "#EA580C"

    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(code, size=12, weight=ft.FontWeight.BOLD, color="#111827"),
                            ft.Text(level, size=11, color="#6B7280"),
                        ],
                        spacing=0,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    bgcolor="#DCFCE7" if completed else "#FEE2E2" if failed else "#DBEAFE",
                    border_radius=12,
                    padding=ft.padding.symmetric(horizontal=10, vertical=6),
                    width=58,
                ),
                ft.Column(
                    controls=[
                        ft.Text(title, size=13, weight=ft.FontWeight.W_600, color="#111827"),
                        ft.Text(status_text, size=12, color=status_color),
                    ],
                    spacing=1,
                    expand=True,
                ),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(vertical=6),
    )


def _competence_card(competence: str, state: dict, on_click) -> ft.Control:
    status = get_competence_status(state, competence)
    flow = status["flow"]
    info = COMPETENCE_INFO[competence]
    progress = status["completed_count"] / len(flow)
    failed_id = status["failed_item"]["id"] if status["failed_item"] else None
    achieved = status["achieved_level"] or "Sin nivel acreditado"

    return ft.Container(
        col={"xs": 12, "lg": 4},
        content=modern_card(
            ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        f"Competencia {competence}",
                                        size=21,
                                        weight=ft.FontWeight.BOLD,
                                        color="#111827",
                                    ),
                                    ft.Text(info["title"], size=14, color="#4B5563"),
                                ],
                                spacing=4,
                                expand=True,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    status["state_label"],
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color="#111827",
                                ),
                                bgcolor="#E0F2FE" if not status["locked"] else "#FEE2E2",
                                border_radius=999,
                                padding=ft.padding.symmetric(horizontal=10, vertical=6),
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                    ft.ProgressBar(value=progress, height=8, border_radius=999),
                    ft.Text(
                        f"Nivel alcanzado: {achieved}",
                        size=14,
                        weight=ft.FontWeight.W_600,
                        color="#111827",
                    ),
                    ft.Text(status["detail"], size=12, color="#6B7280"),
                    ft.Divider(height=18, color="#E5E7EB"),
                    ft.Column(
                        controls=[
                            _test_badge(
                                item["code"],
                                item["title"],
                                item["level"],
                                state["completed"].get(item["id"], False),
                                item["id"] == failed_id,
                            )
                            for item in flow
                        ],
                        spacing=0,
                    ),
                    ft.Container(height=8),
                    primary_button(
                        "Ver competencia" if status["finished"] else "Empezar competencia",
                        on_click=on_click,
                    ),
                ],
                spacing=10,
            ),
            padding=24,
        ),
    )


def build_welcome_view(go_lobby) -> ft.Control:
    return ft.Container(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Evaluación de la Competencia Digital Docente",
                        size=46,
                        weight=ft.FontWeight.BOLD,
                        color="#111827",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "Área 2 del MRCDD: contenidos digitales",
                        size=20,
                        color="#2563EB",
                        weight=ft.FontWeight.W_600,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "Elige una competencia y completa las pruebas en orden.",
                        size=16,
                        color="#4B5563",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        "Iniciar Test",
                        on_click=go_lobby,
                        height=62,
                        style=ft.ButtonStyle(
                            bgcolor="#2563EB",
                            color=ft.Colors.WHITE,
                            text_style=ft.TextStyle(size=19, weight=ft.FontWeight.BOLD),
                            shape=ft.RoundedRectangleBorder(radius=18),
                            padding=ft.padding.symmetric(horizontal=42, vertical=16),
                        ),
                    ),
                ],
                spacing=20,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor="#FFFFFF",
            border=ft.border.all(1, "#E5E7EB"),
            border_radius=28,
            padding=ft.padding.symmetric(horizontal=46, vertical=58),
            shadow=ft.BoxShadow(
                blur_radius=28,
                spread_radius=1,
                color="#14000000",
                offset=ft.Offset(0, 8),
            ),
            width=900,
        ),
        alignment=ft.Alignment.CENTER,
    )


def build_home_view(go_comp_21, go_comp_22, go_comp_23, state: dict) -> ft.Control:
    return ft.Column(
        controls=[
            info_box(
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.LOCK_OUTLINED, color="#2563EB", size=22),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    "Si una prueba no se supera, la competencia queda cerrada.",
                                    size=15,
                                    weight=ft.FontWeight.BOLD,
                                    color="#111827",
                                ),
                                ft.Text(
                                    "El nivel alcanzado será el último nivel superado.",
                                    size=13,
                                    color="#4B5563",
                                ),
                            ],
                            spacing=3,
                            expand=True,
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                bgcolor="#EFF6FF",
            ),
            ft.ResponsiveRow(
                controls=[
                    _competence_card("2.1", state, go_comp_21),
                    _competence_card("2.2", state, go_comp_22),
                    _competence_card("2.3", state, go_comp_23),
                ],
                spacing=24,
                run_spacing=24,
            ),
        ],
        spacing=24,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )
