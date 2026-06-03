import flet as ft

from ui.components import info_box, primary_button, secondary_button
from ui.test_views.comp21.p01_identificar_recursos import build_test_p01
from ui.test_views.comp21.p02_seleccionar_recurso import build_test_p02
from ui.test_views.comp21.p03_banco_recursos import build_test_p03
from ui.test_views.comp21.p04_curacion_contenidos import build_test_p04
from ui.test_views.comp22.p05_corregir_ficha import build_test_p05
from ui.test_views.comp22.p06_completar_plantilla import build_test_p06
from ui.test_views.comp22.p07_adaptar_recurso import build_test_p07
from ui.test_views.comp22.p08_disenar_secuencia import build_test_p08


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

COMPETENCE_INFO = {
    "2.1": {
        "title": "Búsqueda y selección de contenidos digitales",
        "summary": "Localización, análisis y organización progresiva de recursos educativos.",
    },
    "2.2": {
        "title": "Creación y modificación de contenidos digitales",
        "summary": "Adaptación, accesibilidad, licencias y composición didáctica de recursos.",
    },
    "2.3": {
        "title": "Protección, gestión y compartición de contenidos digitales",
        "summary": "Permisos, metadatos, publicación y mantenimiento de repositorios.",
    },
}


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


def get_competence_flow(state: dict, competence: str | None = None) -> list[dict]:
    active_competence = competence or state.get("active_competence", "2.1")
    return [item for item in TEST_FLOW if item["competence"] == active_competence]


def get_competence_status(state: dict, competence: str) -> dict:
    flow = get_competence_flow(state, competence)
    failed_item = None
    completed_count = 0
    achieved_level = None

    for item in flow:
        feedback = state["feedback"].get(item["id"], {"ok": None})
        if feedback.get("ok") is False:
            failed_item = item
            break
        if state["completed"].get(item["id"], False):
            completed_count += 1
            achieved_level = item["level"]
            continue
        break

    next_item = None
    if failed_item is None:
        next_item = next(
            (item for item in flow if not state["completed"].get(item["id"], False)),
            None,
        )

    if failed_item:
        state_label = "Cerrada"
        detail = f"No superada en {failed_item['code']}. Nivel alcanzado: {achieved_level or 'sin nivel acreditado'}."
    elif completed_count == len(flow):
        state_label = "Completada"
        detail = f"Nivel alcanzado: {achieved_level}."
    else:
        state_label = "En progreso" if completed_count else "Pendiente"
        detail = f"Siguiente: {next_item['code']} · {next_item['level']}."

    return {
        "flow": flow,
        "failed_item": failed_item,
        "next_item": next_item,
        "completed_count": completed_count,
        "achieved_level": achieved_level,
        "state_label": state_label,
        "detail": detail,
        "locked": failed_item is not None,
        "finished": failed_item is not None or completed_count == len(flow),
    }


def _next_button(text: str, on_click, disabled: bool) -> ft.ElevatedButton:
    return ft.ElevatedButton(
        text,
        on_click=on_click,
        disabled=disabled,
        height=40,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            bgcolor="#2563EB" if not disabled else "#E5E7EB",
            color=ft.Colors.WHITE if not disabled else "#9CA3AF",
        ),
    )


def _step_dot(item: dict, active_id: str, completed: bool, failed: bool) -> ft.Control:
    active = item["id"] == active_id
    color = "#166534" if completed else "#991B1B" if failed else "#1E40AF" if active else "#6B7280"
    bg = "#DCFCE7" if completed else "#FEE2E2" if failed else "#DBEAFE" if active else "#F9FAFB"
    border = "#86EFAC" if completed else "#FCA5A5" if failed else "#93C5FD" if active else "#E5E7EB"

    return ft.Container(
        content=ft.Text(item["level"], size=11, weight=ft.FontWeight.BOLD, color=color),
        width=38,
        height=28,
        alignment=ft.Alignment.CENTER,
        bgcolor=bg,
        border=ft.border.all(1, border),
        border_radius=999,
    )


def build_evaluation_view(page: ft.Page, state: dict, go_home) -> ft.Control:
    root = ft.Column(expand=True, spacing=12)

    def ensure_active_test_matches_competence():
        flow = get_competence_flow(state)
        status = get_competence_status(state, state["active_competence"])
        flow_ids = [item["id"] for item in flow]

        if status["failed_item"]:
            state["active_test"] = status["failed_item"]["id"]
        elif state.get("active_test") not in flow_ids:
            state["active_test"] = (status["next_item"] or flow[-1])["id"]

    def get_active_index() -> int:
        ensure_active_test_matches_competence()
        flow = get_competence_flow(state)
        active_id = state["active_test"]

        for index, item in enumerate(flow):
            if item["id"] == active_id:
                return index

        return 0

    def refresh():
        ensure_active_test_matches_competence()
        root.controls = build_layout()
        page.update()

    def go_next(e=None):
        flow = get_competence_flow(state)
        status = get_competence_status(state, state["active_competence"])
        index = get_active_index()

        if status["locked"]:
            return

        if index < len(flow) - 1:
            current_id = flow[index]["id"]

            if state["completed"].get(current_id, False):
                state["active_test"] = flow[index + 1]["id"]
                refresh()

    def build_header() -> ft.Control:
        flow = get_competence_flow(state)
        status = get_competence_status(state, state["active_competence"])
        active = flow[get_active_index()]
        progress_value = status["completed_count"] / len(flow)
        next_disabled = status["locked"] or not state["completed"].get(active["id"], False)

        steps = [
            _step_dot(
                item=item,
                active_id=state["active_test"],
                completed=state["completed"].get(item["id"], False),
                failed=bool(status["failed_item"] and item["id"] == status["failed_item"]["id"]),
            )
            for item in flow
        ]

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Text(
                                                f"Competencia {active['competence']}",
                                                size=15,
                                                weight=ft.FontWeight.BOLD,
                                                color="#111827",
                                            ),
                                            ft.Text(
                                                f"{active['code']} · {active['level']}",
                                                size=13,
                                                weight=ft.FontWeight.W_600,
                                                color="#2563EB",
                                            ),
                                            ft.Text(active["title"], size=13, color="#4B5563"),
                                        ],
                                        spacing=10,
                                        wrap=True,
                                    ),
                                    ft.Text(
                                        f"Nivel alcanzado: {status['achieved_level'] or 'sin nivel acreditado'}",
                                        size=12,
                                        color="#6B7280",
                                    ),
                                ],
                                spacing=3,
                                expand=True,
                            ),
                            secondary_button("Lobby", on_click=go_home),
                            _next_button(
                                "Siguiente",
                                on_click=go_next,
                                disabled=next_disabled,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Row(
                        controls=[
                            ft.ProgressBar(value=progress_value, height=6, border_radius=999, expand=True),
                            ft.Row(controls=steps, spacing=6),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                spacing=10,
            ),
            bgcolor="#FFFFFF",
            border=ft.border.all(1, "#E5E7EB"),
            border_radius=16,
            padding=ft.padding.symmetric(horizontal=18, vertical=14),
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
        if active_id == "p08":
            return build_test_p08(state, refresh)

        return info_box(
            ft.Column(
                controls=[
                    ft.Text("Prueba todavía no implementada", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(
                        "La prueba está definida en la progresión, pero falta su interfaz.",
                        size=14,
                    ),
                ],
                spacing=8,
            ),
            bgcolor="#FFF7ED",
        )

    def build_locked_notice() -> ft.Control:
        status = get_competence_status(state, state["active_competence"])
        if not status["locked"]:
            return ft.Container()

        return info_box(
            ft.Row(
                controls=[
                    ft.Icon(ft.Icons.LOCK_OUTLINED, color="#991B1B", size=22),
                    ft.Text(
                        "Competencia cerrada. No se puede avanzar tras una prueba no superada.",
                        size=14,
                        color="#4B5563",
                        expand=True,
                    ),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor="#FEF2F2",
        )

    def build_questions_area() -> ft.Control:
        return ft.Container(
            content=ft.Column(
                controls=[
                    build_locked_notice(),
                    build_current_test(),
                    ft.Container(height=18),
                ],
                spacing=16,
                scroll=ft.ScrollMode.AUTO,
            ),
            expand=True,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )

    def build_layout():
        ensure_active_test_matches_competence()
        return [
            build_header(),
            build_questions_area(),
        ]

    root.controls = build_layout()
    return root
