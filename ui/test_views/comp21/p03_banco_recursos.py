import flet as ft
from datetime import datetime

from core.storage import save_result
from ui.components import question_block


TEST_ID = "P03"
SCENARIO_ID = "comp21_b1_banco_recursos"


def build_result_box(feedback_data: dict) -> ft.Control:
    if feedback_data["ok"] is None:
        return ft.Container()

    ok = feedback_data["ok"]

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Resultado de la prueba", size=17, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Text(feedback_data["message"], size=14, color=ft.Colors.WHITE),
            ],
            spacing=8,
        ),
        bgcolor=ft.Colors.GREEN if ok else ft.Colors.RED,
        border_radius=12,
        padding=20,
    )


def build_test_p03(state: dict, refresh_view) -> ft.Control:
    resources = [
        ("R1", "Ficha breve de repaso.pdf"),
        ("R2", "Vídeo introductorio subtitulado.mp4"),
        ("R3", "Lectura ampliada avanzada.pdf"),
        ("R4", "Cuestionario final.json"),
        ("R5", "Imagen sin licencia.jpg"),
        ("R6", "Actividad interactiva con registro obligatorio"),
        ("R7", "Rúbrica de evaluación CC BY.pdf"),
        ("R8", "Guía docente de profundización.pdf"),
    ]

    expected = {
        "R1": "Refuerzo",
        "R2": "Refuerzo",
        "R3": "Ampliación",
        "R4": "Evaluación",
        "R5": "No válido",
        "R6": "No válido",
        "R7": "Evaluación",
        "R8": "Ampliación",
    }

    saved = state["responses"].get("p03_classification", {})
    dropdowns = {}

    rows = []
    for rid, title in resources:
        dd = ft.Dropdown(
            value=saved.get(rid),
            width=190,
            options=[
                ft.dropdown.Option("Refuerzo"),
                ft.dropdown.Option("Ampliación"),
                ft.dropdown.Option("Evaluación"),
                ft.dropdown.Option("No válido"),
            ],
        )
        dropdowns[rid] = dd

        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(rid)),
                    ft.DataCell(ft.Text(title)),
                    ft.DataCell(dd),
                ]
            )
        )

    def validate(e):
        answers = {rid: dd.value for rid, dd in dropdowns.items()}
        state["responses"]["p03_classification"] = answers

        if any(value is None for value in answers.values()):
            state["completed"]["p03"] = False
            state["feedback"]["p03"] = {
                "ok": False,
                "message": "Debes clasificar los ocho recursos antes de validar la prueba.",
            }
            refresh_view()
            return

        correct = [rid for rid, value in answers.items() if expected[rid] == value]
        wrong = [rid for rid, value in answers.items() if expected[rid] != value]

        score = round((len(correct) / len(expected)) * 100)
        ok = score >= 87  # mínimo 7/8

        state["completed"]["p03"] = ok

        message = (
            "Prueba superada. Has organizado el banco de recursos de forma coherente y has separado los recursos no válidos."
            if ok
            else "Prueba no superada. Revisa especialmente los recursos sin licencia o con registro obligatorio."
        )

        state["feedback"]["p03"] = {"ok": ok, "message": message}

        result = {
            "test_id": TEST_ID,
            "scenario_id": SCENARIO_ID,
            "scenario_title": "Organizar un banco de recursos",
            "timestamp_utc": datetime.utcnow().isoformat(),
            "score_0_100": score,
            "level_hint": "B1" if ok else "A2",
            "payload": {
                "answers": answers,
                "expected": expected,
                "correct_ids": correct,
                "wrong_ids": wrong,
            },
            "checks": [
                {
                    "check_id": "resource_bank_classification",
                    "label": "Clasifica recursos por finalidad educativa y validez",
                    "passed": ok,
                    "weight": 100,
                    "evidence": str(answers),
                }
            ],
            "notes": [message],
        }

        saved_path = save_result(result)
        state["responses"]["p03_saved_path"] = str(saved_path)

        refresh_view()

    content = ft.Column(
        controls=[
            ft.Text(
                "Escenario: has reunido ocho recursos digitales y debes organizarlos para reutilizarlos en una situación de aprendizaje.",
                size=15,
                weight=ft.FontWeight.W_600,
            ),
            ft.Text(
                "Clasifica cada recurso en la carpeta más adecuada. Los recursos sin licencia clara o con barreras de acceso deben ir a “No válido”.",
                size=14,
            ),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID")),
                    ft.DataColumn(ft.Text("Recurso")),
                    ft.DataColumn(ft.Text("Carpeta")),
                ],
                rows=rows,
            ),
            ft.Container(height=8),
            ft.ElevatedButton("Validar prueba", on_click=validate),
            build_result_box(state["feedback"]["p03"]),
        ],
        spacing=12,
    )

    return question_block(
        title="P03 · Organizar un banco de recursos",
        statement=(
            "Evalúa los indicadores 2.1.B1.1, 2.1.B1.2 y 2.1.B1.3 mediante la organización autónoma "
            "de contenidos digitales según criterios didácticos, técnicos y de reutilización."
        ),
        content=content,
    )