import flet as ft

from ui.components import app_header, info_box, modern_card, primary_button


def _test_badge(code: str, title: str, completed: bool) -> ft.Control:
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(
                        code,
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color="#166534" if completed else "#1E40AF",
                    ),
                    bgcolor="#DCFCE7" if completed else "#DBEAFE",
                    border_radius=999,
                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                ),
                ft.Column(
                    controls=[
                        ft.Text(title, size=13, weight=ft.FontWeight.W_600, color="#111827"),
                        ft.Text(
                            "Superada" if completed else "Pendiente",
                            size=12,
                            color="#16A34A" if completed else "#EA580C",
                        ),
                    ],
                    spacing=1,
                    expand=True,
                ),
            ],
            spacing=10,
        ),
        padding=ft.padding.symmetric(vertical=6),
    )


def _competence_card(
    title: str,
    subtitle: str,
    tests: list[tuple[str, str, bool]],
    button_text: str,
    enabled: bool,
    on_click,
) -> ft.Control:
    completed_count = sum(1 for _, _, done in tests if done)
    progress = completed_count / len(tests)

    return ft.Container(
        col={"xs": 12, "lg": 4},
        content=modern_card(
            ft.Column(
                controls=[
                    ft.Text(title, size=22, weight=ft.FontWeight.BOLD, color="#111827"),
                    ft.Text(subtitle, size=14, color="#6B7280"),
                    ft.Container(height=4),
                    ft.ProgressBar(value=progress, height=8, border_radius=999),
                    ft.Text(
                        f"{completed_count}/{len(tests)} pruebas superadas",
                        size=13,
                        color="#6B7280",
                    ),
                    ft.Divider(height=18, color="#E5E7EB"),
                    ft.Column(
                        controls=[_test_badge(code, name, done) for code, name, done in tests],
                        spacing=0,
                    ),
                    ft.Container(height=10),
                    primary_button(button_text, on_click=on_click, disabled=not enabled),
                ],
                spacing=10,
            ),
            padding=26,
        ),
    )


def build_home_view(go_comp_21, go_comp_22, go_comp_23, state: dict) -> ft.Control:
    completed = state["completed"]

    comp21_tests = [
        ("P01", "Identificar recursos válidos", completed.get("p01", False)),
        ("P02", "Seleccionar el mejor recurso", completed.get("p02", False)),
        ("P03", "Organizar un banco de recursos", completed.get("p03", False)),
        ("P04", "Curación avanzada de contenidos", completed.get("p04", False)),
    ]

    comp22_tests = [
        ("P05", "Corregir una ficha educativa", completed.get("p05", False)),
        ("P06", "Completar plantilla didáctica", completed.get("p06", False)),
        ("P07", "Adaptar recurso accesible", completed.get("p07", False)),
        ("P08", "Diseñar una secuencia digital", completed.get("p08", False)),
    ]

    comp23_tests = [
        ("P09", "Clasificar archivos compartibles", completed.get("p09", False)),
        ("P10", "Configurar permisos básicos", completed.get("p10", False)),
        ("P11", "Publicar recurso con metadatos", completed.get("p11", False)),
        ("P12", "Optimizar repositorio digital", completed.get("p12", False)),
    ]

    return ft.Column(
        controls=[
            app_header(
                "Evaluación de la Competencia Digital Docente",
                "Aplicación práctica para evaluar el Área 2 del MRCDD mediante tareas de desempeño.",
            ),
            info_box(
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.INFO_OUTLINED, color="#2563EB", size=28),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    "Selecciona una competencia para continuar",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color="#111827",
                                ),
                                ft.Text(
                                    "Cada competencia tiene su propia progresión A1 → A2 → B1 → B2. "
                                    "La home muestra qué pruebas están pendientes y cuáles ya han sido superadas.",
                                    size=14,
                                    color="#4B5563",
                                ),
                            ],
                            spacing=5,
                            expand=True,
                        ),
                    ],
                    spacing=14,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                bgcolor="#EFF6FF",
            ),
            ft.ResponsiveRow(
                controls=[
                    _competence_card(
                        title="Competencia 2.1",
                        subtitle="Búsqueda y selección de contenidos digitales.",
                        tests=comp21_tests,
                        button_text="Entrar en 2.1",
                        enabled=True,
                        on_click=go_comp_21,
                    ),
                    _competence_card(
                        title="Competencia 2.2",
                        subtitle="Creación y modificación de contenidos digitales.",
                        tests=comp22_tests,
                        button_text="Entrar en 2.2",
                        enabled=True,
                        on_click=go_comp_22,
                    ),
                    _competence_card(
                        title="Competencia 2.3",
                        subtitle="Protección, gestión y compartición de contenidos digitales.",
                        tests=comp23_tests,
                        button_text="Entrar en 2.3",
                        enabled=True,
                        on_click=go_comp_23,
                    ),
                ],
                spacing=24,
                run_spacing=24,
            ),
        ],
        spacing=30,
        expand=True,
    )