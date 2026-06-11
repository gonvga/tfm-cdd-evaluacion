import flet as ft


def build_welcome_view(start_evaluation) -> ft.Control:
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
                        "Resuelve las actividades en el orden en que aparecen. "
                        "La evaluación finalizará cuando se haya determinado tu nivel.",
                        size=16,
                        color="#4B5563",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        "Comenzar evaluación",
                        on_click=start_evaluation,
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
