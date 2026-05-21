import flet as ft
from datetime import datetime
from core.storage import save_result
from ui.components import question_block


TEST_ID = "P01"
SCENARIO_ID = "comp21_a1_recursos_validos"


def build_result_box(feedback_data: dict) -> ft.Control:
    if feedback_data["ok"] is None:
        return ft.Container()

    ok = feedback_data["ok"]

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "Resultado de la prueba",
                    size=17,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
                ft.Text(
                    feedback_data["message"],
                    size=14,
                    color=ft.Colors.WHITE,
                ),
            ],
            spacing=8,
        ),
        bgcolor=ft.Colors.GREEN if ok else ft.Colors.RED,
        border_radius=12,
        padding=20,
    )


def build_resource_card(resource: dict, checkbox: ft.Checkbox) -> ft.Control:
    return ft.Container(
        content=ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                checkbox,
                                ft.Text(
                                    resource["title"],
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    expand=True,
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.START,
                        ),
                        ft.Text(f"Autoría: {resource['author']}", size=13),
                        ft.Text(f"Licencia: {resource['license']}", size=13),
                        ft.Text(f"Formato: {resource['format']}", size=13),
                        ft.Text(f"Accesibilidad: {resource['accessibility']}", size=13),
                        ft.Text(
                            resource["description"],
                            size=13,
                            color=ft.Colors.GREY_700,
                        ),
                    ],
                    spacing=6,
                ),
                padding=16,
            )
        ),
        col={"xs": 12, "md": 6},
    )


def build_test_p01(state: dict, refresh_view) -> ft.Control:
    resources = [
        {
            "id": "A",
            "title": "Guía saludable para el aula",
            "author": "Ministerio de Educación",
            "license": "CC BY",
            "format": "PDF",
            "accessibility": "Texto etiquetado y lectura clara",
            "description": "Recurso institucional con autoría reconocida y licencia abierta.",
        },
        {
            "id": "B",
            "title": "Consejos rápidos de un blog personal",
            "author": "No indicada",
            "license": "No especificada",
            "format": "Entrada de blog",
            "accessibility": "No indicada",
            "description": "Contenido sin autoría clara ni condiciones de reutilización.",
        },
        {
            "id": "C",
            "title": "Vídeo comercial sobre alimentación",
            "author": "Canal privado",
            "license": "Copyright completo",
            "format": "Vídeo",
            "accessibility": "Sin subtítulos",
            "description": "Material atractivo, pero no reutilizable libremente.",
        },
        {
            "id": "D",
            "title": "Presentación hábitos saludables",
            "author": "Proyecto Aula Abierta",
            "license": "CC BY-SA",
            "format": "Presentación",
            "accessibility": "Incluye texto alternativo y subtítulos",
            "description": "Recurso con autoría, licencia abierta y criterios de accesibilidad.",
        },
    ]

    saved_selection = state["responses"].get("p01_selected", [])

    checkboxes = {}
    resource_cards = []

    for resource in resources:
        cb = ft.Checkbox(value=resource["id"] in saved_selection)
        checkboxes[resource["id"]] = cb
        resource_cards.append(build_resource_card(resource, cb))

    def validate(e):
        selected_ids = [
            resource_id
            for resource_id, checkbox in checkboxes.items()
            if checkbox.value
        ]

        expected_ids = ["A", "D"]

        state["responses"]["p01_selected"] = selected_ids

        missing = [rid for rid in expected_ids if rid not in selected_ids]
        wrong = [rid for rid in selected_ids if rid not in expected_ids]

        ok = len(missing) == 0 and len(wrong) == 0
        score = 100 if ok else max(0, 100 - (len(missing) * 35) - (len(wrong) * 30))

        state["completed"]["p01"] = ok

        if ok:
            message = (
                "Prueba superada. Has identificado correctamente los recursos fiables, "
                "accesibles y reutilizables para una situación educativa."
            )
        else:
            message = (
                "Prueba no superada. Revisa la autoría, la licencia y la accesibilidad. "
                "Solo deben seleccionarse recursos reutilizables y adecuados para el aula."
            )

        state["feedback"]["p01"] = {
            "ok": ok,
            "message": message,
        }

        result = {
            "test_id": TEST_ID,
            "scenario_id": SCENARIO_ID,
            "scenario_title": "Identificar recursos válidos",
            "timestamp_utc": datetime.utcnow().isoformat(),
            "score_0_100": score,
            "level_hint": "A1" if ok else "A0",
            "payload": {
                "selected_ids": selected_ids,
                "expected_ids": expected_ids,
                "missing_ids": missing,
                "wrong_ids": wrong,
            },
            "checks": [
                {
                    "check_id": "selected_valid_resources",
                    "label": "Selecciona únicamente los recursos válidos",
                    "passed": ok,
                    "weight": 100,
                    "evidence": ", ".join(selected_ids),
                }
            ],
            "notes": [message],
        }

        saved_path = save_result(result)
        state["responses"]["p01_saved_path"] = str(saved_path)

        refresh_view()

    content = ft.Column(
        controls=[
            ft.Text(
                "Escenario: quieres trabajar hábitos saludables en clase y debes seleccionar solo los recursos digitales que puedan utilizarse de forma segura y reutilizable.",
                size=15,
                weight=ft.FontWeight.W_600,
            ),
            ft.Text(
                "Marca únicamente los recursos que tengan autoría clara, licencia adecuada y condiciones mínimas de accesibilidad.",
                size=14,
            ),
            ft.ResponsiveRow(controls=resource_cards),
            ft.Container(height=8),
            ft.ElevatedButton("Validar prueba", on_click=validate),
            build_result_box(state["feedback"]["p01"]),
        ],
        spacing=12,
    )

    return question_block(
        title="P01 · Identificar recursos válidos",
        statement=(
            "Evalúa los indicadores 2.1.A1.1, 2.1.A1.2 y 2.1.A1.3 mediante una tarea de selección "
            "basada en criterios didácticos, técnicos, científicos, licencia y accesibilidad."
        ),
        content=content,
    )