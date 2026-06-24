import os

import flet as ft

from ui.components import apply_accessibility, info_box, modern_card, primary_button
from ui.test_views.comp21.p01_identificar_recursos import build_test_p01
from ui.test_views.comp21.p02_seleccionar_recurso import build_test_p02
from ui.test_views.comp21.p03_banco_recursos import build_test_p03
from ui.test_views.comp21.p04_curacion_contenidos import build_test_p04
from ui.test_views.comp22.p05_corregir_ficha import build_test_p05
from ui.test_views.comp22.p06_completar_plantilla import build_test_p06
from ui.test_views.comp22.p07_adaptar_recurso import build_test_p07
from ui.test_views.comp22.p08_disenar_secuencia import build_test_p08
from ui.test_views.comp23.p09_compartir_catalogar import build_test_p09
from ui.test_views.comp23.p10_configurar_publicacion import build_test_p10
from ui.test_views.comp23.p11_publicar_recurso import build_test_p11
from ui.test_views.comp23.p12_optimizar_repositorio import build_test_p12

COMPETENCES = ("2.1", "2.2", "2.3")

TEST_FLOW = [
    {"id": "p01", "code": "P01", "title": "Identificar recursos válidos", "competence": "2.1", "level": "A1"},
    {"id": "p05", "code": "P05", "title": "Corregir una ficha educativa", "competence": "2.2", "level": "A1"},
    {"id": "p09", "code": "P09", "title": "Compartir y catalogar contenidos", "competence": "2.3", "level": "A1"},
    {"id": "p02", "code": "P02", "title": "Seleccionar el mejor recurso", "competence": "2.1", "level": "A2"},
    {"id": "p06", "code": "P06", "title": "Adaptar recurso con ayuda", "competence": "2.2", "level": "A2"},
    {"id": "p10", "code": "P10", "title": "Configurar publicación segura", "competence": "2.3", "level": "A2"},
    {"id": "p03", "code": "P03", "title": "Organizar un banco de recursos", "competence": "2.1", "level": "B1"},
    {"id": "p07", "code": "P07", "title": "Adaptar recurso accesible", "competence": "2.2", "level": "B1"},
    {"id": "p11", "code": "P11", "title": "Publicar recurso con metadatos", "competence": "2.3", "level": "B1"},
    {"id": "p04", "code": "P04", "title": "Curación avanzada de contenidos", "competence": "2.1", "level": "B2"},
    {"id": "p08", "code": "P08", "title": "Diseñar una secuencia digital", "competence": "2.2", "level": "B2"},
    {"id": "p12", "code": "P12", "title": "Optimizar repositorio digital", "competence": "2.3", "level": "B2"},
]

COMPETENCE_INFO = {
    "2.1": "Búsqueda y selección de contenidos digitales",
    "2.2": "Creación y modificación de contenidos digitales",
    "2.3": "Protección, gestión y compartición de contenidos digitales",
}

TEST_BUILDERS = {
    "p01": build_test_p01,
    "p02": build_test_p02,
    "p03": build_test_p03,
    "p04": build_test_p04,
    "p05": build_test_p05,
    "p06": build_test_p06,
    "p07": build_test_p07,
    "p08": build_test_p08,
    "p09": build_test_p09,
    "p10": build_test_p10,
    "p11": build_test_p11,
    "p12": build_test_p12,
}


def allow_failed_advance() -> bool:
    return os.getenv("CDD_ALLOW_FAILED_ADVANCE", "").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def initial_evaluation_state() -> dict:
    return {
        "active_test": TEST_FLOW[0]["id"],
        "show_results": False,
        "completed": {item["id"]: False for item in TEST_FLOW},
        "responses": {},
        "feedback": {
            item["id"]: {"message": "", "ok": None}
            for item in TEST_FLOW
        },
    }


def get_competence_flow(state: dict, competence: str | None = None) -> list[dict]:
    selected = competence or "2.1"
    return [item for item in TEST_FLOW if item["competence"] == selected]


def get_competence_status(state: dict, competence: str) -> dict:
    flow = get_competence_flow(state, competence)
    allow_failed = allow_failed_advance()
    failed_item = None
    achieved_level = None
    completed_count = 0

    for item in flow:
        result = state["feedback"].get(item["id"], {}).get("ok")
        if result is False:
            if not allow_failed:
                failed_item = item
                break
            completed_count += 1
            continue
        if result is True:
            achieved_level = item["level"]
            completed_count += 1
            continue
        break

    next_item = None
    if failed_item is None:
        next_item = next(
            (item for item in flow if state["feedback"].get(item["id"], {}).get("ok") is None),
            None,
        )

    return {
        "flow": flow,
        "failed_item": failed_item,
        "next_item": next_item,
        "completed_count": completed_count,
        "achieved_level": achieved_level,
        "locked": failed_item is not None,
        "finished": failed_item is not None or completed_count == len(flow),
    }


def get_next_test(state: dict) -> dict | None:
    failed_competences = set()
    if not allow_failed_advance():
        failed_competences = {
            item["competence"]
            for item in TEST_FLOW
            if state["feedback"].get(item["id"], {}).get("ok") is False
        }

    for item in TEST_FLOW:
        if item["competence"] in failed_competences:
            continue
        if state["feedback"].get(item["id"], {}).get("ok") is None:
            return item
    return None


def evaluation_is_finished(state: dict) -> bool:
    return get_next_test(state) is None


def _resolved_progress(state: dict) -> float:
    resolved = 0
    failed_competences = set()
    allow_failed = allow_failed_advance()

    for item in TEST_FLOW:
        if item["competence"] in failed_competences:
            resolved += 1
            continue

        result = state["feedback"].get(item["id"], {}).get("ok")
        if result is not None:
            resolved += 1
        if result is False and not allow_failed:
            failed_competences.add(item["competence"])

    return resolved / len(TEST_FLOW)


def _button_label(button: ft.ElevatedButton) -> str | None:
    text = getattr(button, "text", None)
    if text is not None:
        return text
    return button.content if isinstance(button.content, str) else None


def _take_test_actions(
    control: ft.Control,
) -> tuple[ft.ElevatedButton | None, ft.Control | None]:
    for attribute in ("controls", "rows", "cells"):
        children = getattr(control, attribute, None)
        if not children:
            continue

        for index, child in enumerate(children):
            if isinstance(child, ft.ElevatedButton) and _button_label(child) == "Validar prueba":
                button = children.pop(index)
                result = children.pop(index) if index < len(children) else None
                return button, result

            button, result = _take_test_actions(child)
            if button:
                return button, result

    content = getattr(control, "content", None)
    if isinstance(content, ft.Control):
        if isinstance(content, ft.ElevatedButton) and _button_label(content) == "Validar prueba":
            control.content = None
            return content, None
        return _take_test_actions(content)

    return None, None


def build_final_results(state: dict, restart_evaluation) -> ft.Control:
    cards = []
    for competence in COMPETENCES:
        status = get_competence_status(state, competence)
        level = status["achieved_level"] or "Sin nivel acreditado"
        cards.append(
            ft.Container(
                col={"xs": 12, "md": 4},
                content=modern_card(
                    ft.Column(
                        controls=[
                            ft.Text(
                                f"Competencia {competence}",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color="#2563EB",
                            ),
                            ft.Text(
                                COMPETENCE_INFO[competence],
                                size=14,
                                color="#4B5563",
                            ),
                            ft.Divider(height=18, color="#E5E7EB"),
                            ft.Text("Nivel alcanzado", size=13, color="#6B7280"),
                            ft.Text(
                                level,
                                size=30,
                                weight=ft.FontWeight.BOLD,
                                color="#111827",
                            ),
                        ],
                        spacing=8,
                    ),
                    padding=24,
                ),
            )
        )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(ft.Icons.ASSIGNMENT_TURNED_IN_OUTLINED, size=52, color="#2563EB"),
                ft.Text(
                    "Evaluación completada",
                    size=34,
                    weight=ft.FontWeight.BOLD,
                    color="#111827",
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Estos son los niveles alcanzados en cada competencia.",
                    size=16,
                    color="#4B5563",
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=8),
                ft.ResponsiveRow(controls=cards, spacing=18, run_spacing=18),
                ft.Container(height=8),
                primary_button("Reiniciar evaluación", on_click=restart_evaluation),
            ],
            spacing=14,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        ),
        expand=True,
        alignment=ft.Alignment.CENTER,
        padding=ft.padding.symmetric(vertical=20),
    )


def build_evaluation_view(page: ft.Page, state: dict, restart_evaluation) -> ft.Control:
    root = ft.Column(expand=True, spacing=12)

    def refresh():
        root.controls = build_layout()
        apply_accessibility(root)
        page.update()

    def go_next(e=None):
        current_id = state["active_test"]
        if state["feedback"].get(current_id, {}).get("ok") is None:
            return

        next_test = get_next_test(state)
        if next_test is None:
            state["show_results"] = True
        else:
            state["active_test"] = next_test["id"]
        refresh()

    def build_header(validate_button: ft.ElevatedButton | None) -> ft.Control:
        current_result = state["feedback"].get(state["active_test"], {}).get("ok")
        finished = evaluation_is_finished(state)

        if current_result is None and validate_button:
            validate_button.height = 42
            validate_button.style = ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                bgcolor="#2563EB",
                color=ft.Colors.WHITE,
            )
            action_button = validate_button
        else:
            action_button = ft.ElevatedButton(
                "Ver resultados" if finished else "Siguiente",
                on_click=go_next,
                height=42,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=12),
                    bgcolor="#2563EB",
                    color=ft.Colors.WHITE,
                ),
            )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        "Evaluación en curso",
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                        color="#111827",
                                    ),
                                    ft.Text(
                                        "Completa la actividad y valida tu respuesta para continuar.",
                                        size=13,
                                        color="#6B7280",
                                    ),
                                ],
                                spacing=3,
                                expand=True,
                            ),
                            action_button,
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.ProgressBar(
                        value=_resolved_progress(state),
                        height=7,
                        border_radius=999,
                    ),
                ],
                spacing=12,
            ),
            bgcolor="#FFFFFF",
            border=ft.border.all(1, "#E5E7EB"),
            border_radius=16,
            padding=ft.padding.symmetric(horizontal=18, vertical=14),
        )

    def build_current_test() -> ft.Control:
        active_id = state["active_test"]
        if active_id == "p12":
            return build_test_p12(state, refresh, page=page)

        builder = TEST_BUILDERS.get(active_id)
        if builder:
            return builder(state, refresh)

        return info_box(
            ft.Text("No se ha podido cargar esta actividad.", size=15),
            bgcolor="#FFF7ED",
        )

    def build_layout() -> list[ft.Control]:
        if state.get("show_results"):
            return [build_final_results(state, restart_evaluation)]

        if state.get("active_test") not in {item["id"] for item in TEST_FLOW}:
            next_test = get_next_test(state)
            state["active_test"] = next_test["id"] if next_test else TEST_FLOW[-1]["id"]

        current_test = build_current_test()
        validate_button, result_box = _take_test_actions(current_test)
        question_controls = []
        if result_box:
            question_controls.append(result_box)
        question_controls.extend([current_test, ft.Container(height=18)])

        return [
            build_header(validate_button),
            ft.Container(
                content=ft.Column(
                    controls=question_controls,
                    spacing=16,
                    scroll=ft.ScrollMode.AUTO,
                ),
                expand=True,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
            ),
        ]

    root.controls = build_layout()
    return root
