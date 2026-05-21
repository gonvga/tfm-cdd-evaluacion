import flet as ft

from ui.components import info_box, primary_button, secondary_button
from ui.test_views.comp21.p01_identificar_recursos import build_test_p01
from ui.test_views.comp21.p02_seleccionar_recurso import build_test_p02
from ui.test_views.comp21.p03_banco_recursos import build_test_p03
from ui.test_views.comp21.p04_curacion_contenidos import build_test_p04
from ui.test_views.comp22.p05_corregir_ficha import build_test_p05
from ui.test_views.comp22.p06_completar_plantilla import build_test_p06
from ui.test_views.comp22.p07_adaptar_recurso import build_test_p07

TEST_FLOW = [
    {"id": "p01", "code": "P01", "title": "Identificar recursos válidos", "competence": "2.1", "level": "A1"},
    {"id": "p02", "code": "P02", "title": "Seleccionar el mejor recurso", "competence": "2.1", "level": "A2"},
    {"id": "p03", "code": "P03", "title": "Organizar un banco de recursos", "competence": "2.1", "level": "B1"},
    {"id": "p04", "code": "P04", "title": "Curación avanzada de contenidos", "competence": "2.1", "level": "B2"},

    {"id": "p05", "code": "P05", "title": "Corregir una ficha educativa", "competence": "2.2", "level": "A1"},
    {"id": "p06", "code": "P06", "title": "Completar plantilla didáctica", "competence": "2.2", "level": "A2"},
    {"id": "p07", "code": "P07", "title": "Adaptar recurso accesible", "competence": "2.2", "level": "B1"},
    {"id": "p08", "code": "P08", "title": "Diseñar una secuencia digital", "competence": "2.2", "level": "B2"},

    {"id": "p09", "code": "P09", "title": "Clasificar archivos compartibles", "competence": "2.3", "level": "A1"},
    {"id": "p10", "code": "P10", "title": "Configurar permisos básicos", "competence": "2.3", "level": "A2"},
    {"id": "p11", "code": "P11", "title": "Publicar recurso con metadatos", "competence": "2.3", "level": "B1"},
    {"id": "p12", "code": "P12", "title": "Optimizar repositorio digital", "competence": "2.3", "level": "B2"},
]


def initial_evaluation_state() -> dict:
    return {
        "active_competence": "2.1",
        "active_test": "p01",
        "completed": {item["id"]: False for item in TEST_FLOW},
        "responses": {},
        "feedback": {
            item["id"]: {"message": "", "ok": None}
            for item in TEST_FLOW
        },
    }


def get_competence_flow(state: dict) -> list[dict]:
    competence = state.get("active_competence", "2.1")
    return [item for item in TEST_FLOW if item["competence"] == competence]


def build_evaluation_view(page: ft.Page, state: dict, go_home) -> ft.Control:
    root = ft.Column(expand=True, spacing=22)

    def get_next_pending_test_id() -> str:
        flow = get_competence_flow(state)

        for item in flow:
            if not state["completed"].get(item["id"], False):
                return item["id"]

        return flow[-1]["id"]

    def ensure_active_test_matches_competence():
        flow = get_competence_flow(state)
        flow_ids = [item["id"] for item in flow]

        if state.get("active_test") not in flow_ids:
            state["active_test"] = get_next_pending_test_id()

    def get_active_index() -> int:
        ensure_active_test_matches_competence()

        flow = get_competence_flow(state)
        active_id = state["active_test"]

        for index, item in enumerate(flow):
            if item["id"] == active_id:
                return index

        return 0

    def refresh():
        root.controls = build_layout()
        page.update()

    def go_next(e=None):
        flow = get_competence_flow(state)
        index = get_active_index()

        if index < len(flow) - 1:
            current_id = flow[index]["id"]

            if state["completed"].get(current_id, False):
                state["active_test"] = flow[index + 1]["id"]
                refresh()

    def build_header() -> ft.Control:
        flow = get_competence_flow(state)
        active_index = get_active_index()
        active = flow[active_index]

        completed_count = sum(
            1 for item in flow if state["completed"].get(item["id"], False)
        )
        progress_value = completed_count / len(flow)

        chips = []

        for item in flow:
            completed = state["completed"].get(item["id"], False)
            active_chip = item["id"] == state["active_test"]

            chips.append(
                ft.Container(
                    content=ft.Text(
                        item["code"],
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=(
                            "#166534"
                            if completed
                            else "#1E40AF"
                            if active_chip
                            else "#6B7280"
                        ),
                    ),
                    bgcolor=(
                        "#DCFCE7"
                        if completed
                        else "#DBEAFE"
                        if active_chip
                        else "#F9FAFB"
                    ),
                    border=ft.border.all(
                        1,
                        (
                            "#86EFAC"
                            if completed
                            else "#93C5FD"
                            if active_chip
                            else "#E5E7EB"
                        ),
                    ),
                    border_radius=999,
                    padding=ft.padding.symmetric(horizontal=12, vertical=7),
                )
            )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        f"Competencia {active['competence']} · {active['title']}",
                                        size=22,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        f"{active['code']} · Nivel {active['level']} · Área 2: Contenidos digitales",
                                        size=14,
                                        color="#6B7280",
                                    ),
                                ],
                                spacing=4,
                                expand=True,
                            ),
                            secondary_button("Volver al home", on_click=go_home),
                            primary_button(
                                "Siguiente prueba",
                                on_click=go_next,
                                disabled=not state["completed"].get(active["id"], False),
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.ProgressBar(
                        value=progress_value,
                        height=8,
                        border_radius=999,
                    ),
                    ft.Row(
                        controls=chips,
                        wrap=True,
                        spacing=8,
                        run_spacing=8,
                    ),
                    ft.Text(
                        f"Progreso de la competencia {active['competence']}: "
                        f"{completed_count}/{len(flow)} pruebas superadas",
                        size=13,
                        color="#6B7280",
                    ),
                ],
                spacing=14,
            ),
            bgcolor="#FFFFFF",
            border_radius=24,
            padding=24,
            border=ft.border.all(1, "#E5E7EB"),
            shadow=ft.BoxShadow(
                blur_radius=18,
                spread_radius=1,
                color="#14000000",
                offset=ft.Offset(0, 4),
            ),
        )

    def build_current_test() -> ft.Control:
        ensure_active_test_matches_competence()
        active_id = state["active_test"]

        if active_id == "p01":
            return build_test_p01(state, refresh)

        if active_id == "p02":
            return build_test_p02(state, refresh)

        if active_id == "p03":
            return build_test_p03(state, refresh)

        if active_id == "p04":
            return build_test_p04(state, refresh)

        if active_id == "p05":
            return build_test_p05(state, refresh)

        if active_id == "p06":
            return build_test_p06(state, refresh)

        if active_id == "p07":
            return build_test_p07(state, refresh)

        return info_box(
            ft.Column(
                controls=[
                    ft.Text(
                        "Prueba todavía no implementada",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        "Esta prueba ya está definida dentro de la progresión de la competencia, "
                        "pero falta programar su interfaz y lógica de corrección.",
                        size=14,
                    ),
                ],
                spacing=8,
            ),
            bgcolor="#FFF7ED",
        )

    def build_layout():
        ensure_active_test_matches_competence()

        return [
            build_header(),
            build_current_test(),
        ]

    root.controls = build_layout()
    return root