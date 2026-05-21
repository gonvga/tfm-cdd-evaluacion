import flet as ft
from datetime import datetime

from core.storage import save_result
from ui.components import question_block


TEST_ID = "P02"
SCENARIO_ID = "comp21_a2_mejor_recurso"


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


def build_test_p02(state: dict, refresh_view) -> ft.Control:
    resources = [
        {
            "id": "A",
            "title": "Documento técnico avanzado",
            "age": "Bachillerato",
            "reading_level": "Alto",
            "license": "CC BY",
            "format": "PDF",
            "accessibility": "Texto denso, sin apoyos visuales",
            "compatibility": "Descargable",
        },
        {
            "id": "B",
            "title": "Infografía accesible sobre hábitos saludables",
            "age": "Primaria / primer ciclo ESO",
            "reading_level": "Básico",
            "license": "CC BY",
            "format": "Imagen + texto",
            "accessibility": "Lectura clara, contraste alto y texto alternativo",
            "compatibility": "Sin registro",
        },
        {
            "id": "C",
            "title": "Vídeo motivacional de plataforma privada",
            "age": "ESO",
            "reading_level": "Medio",
            "license": "Copyright completo",
            "format": "Vídeo",
            "accessibility": "Sin subtítulos",
            "compatibility": "Requiere cuenta",
        },
        {
            "id": "D",
            "title": "Artículo divulgativo extenso",
            "age": "Adultos",
            "reading_level": "Alto",
            "license": "No especificada",
            "format": "Web",
            "accessibility": "No indicada",
            "compatibility": "Con publicidad",
        },
        {
            "id": "E",
            "title": "Presentación reutilizable",
            "age": "ESO",
            "reading_level": "Medio",
            "license": "CC BY-SA",
            "format": "Presentación",
            "accessibility": "Correcta, pero con bastante texto",
            "compatibility": "Descargable",
        },
    ]

    selected_value = state["responses"].get("p02_selected", None)
    opened_details = state["responses"].get("p02_opened_details", [])

    selected_radio = ft.RadioGroup(
        value=selected_value,
        content=ft.Column(spacing=8),
    )

    detail_box = ft.Column(spacing=8)

    def show_detail(resource: dict):
        if resource["id"] not in opened_details:
            opened_details.append(resource["id"])

        state["responses"]["p02_opened_details"] = opened_details

        detail_box.controls = [
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            f"Ficha detallada · Recurso {resource['id']}",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(f"Título: {resource['title']}"),
                        ft.Text(f"Edad recomendada: {resource['age']}"),
                        ft.Text(f"Nivel lector: {resource['reading_level']}"),
                        ft.Text(f"Licencia: {resource['license']}"),
                        ft.Text(f"Formato: {resource['format']}"),
                        ft.Text(f"Accesibilidad: {resource['accessibility']}"),
                        ft.Text(f"Compatibilidad: {resource['compatibility']}"),
                    ],
                    spacing=5,
                ),
                bgcolor=ft.Colors.BLUE_50,
                border_radius=12,
                padding=15,
            )
        ]
        refresh_view()

    rows = []

    for resource in resources:
        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(resource["id"])),
                    ft.DataCell(ft.Text(resource["title"])),
                    ft.DataCell(ft.Text(resource["age"])),
                    ft.DataCell(ft.Text(resource["reading_level"])),
                    ft.DataCell(ft.Text(resource["license"])),
                    ft.DataCell(
                        ft.ElevatedButton(
                            "Ver ficha",
                            on_click=lambda e, r=resource: show_detail(r),
                        )
                    ),
                ]
            )
        )

    selected_radio.content.controls = [
        ft.Radio(value=resource["id"], label=f"{resource['id']} · {resource['title']}")
        for resource in resources
    ]

    def validate(e):
        selected_id = selected_radio.value
        state["responses"]["p02_selected"] = selected_id
        state["responses"]["p02_opened_details"] = opened_details

        if selected_id is None:
            state["completed"]["p02"] = False
            state["feedback"]["p02"] = {
                "ok": False,
                "message": "Debes seleccionar un recurso antes de validar la prueba.",
            }
            refresh_view()
            return

        expected_id = "B"
        selected_ok = selected_id == expected_id
        consulted_detail = expected_id in opened_details

        score = 100 if selected_ok and consulted_detail else 85 if selected_ok else 0
        ok = selected_ok

        state["completed"]["p02"] = ok

        if selected_ok and consulted_detail:
            message = (
                "Prueba superada. Has elegido el recurso más adecuado y has consultado su ficha antes de decidir."
            )
        elif selected_ok:
            message = (
                "Prueba superada. Has elegido el recurso más adecuado. Como mejora, conviene revisar siempre la ficha completa antes de seleccionarlo."
            )
        else:
            message = (
                "Prueba no superada. Revisa el nivel lector, la accesibilidad, la licencia y si el recurso requiere registro."
            )

        state["feedback"]["p02"] = {
            "ok": ok,
            "message": message,
        }

        result = {
            "test_id": TEST_ID,
            "scenario_id": SCENARIO_ID,
            "scenario_title": "Seleccionar el mejor recurso",
            "timestamp_utc": datetime.utcnow().isoformat(),
            "score_0_100": score,
            "level_hint": "A2" if ok else "A1",
            "payload": {
                "selected_id": selected_id,
                "expected_id": expected_id,
                "opened_details": opened_details,
                "consulted_expected_detail": consulted_detail,
            },
            "checks": [
                {
                    "check_id": "best_resource_selected",
                    "label": "Selecciona el recurso más adecuado al contexto",
                    "passed": selected_ok,
                    "weight": 85,
                    "evidence": selected_id,
                },
                {
                    "check_id": "detail_consulted",
                    "label": "Consulta la ficha detallada del recurso antes de decidir",
                    "passed": consulted_detail,
                    "weight": 15,
                    "evidence": ", ".join(opened_details),
                },
            ],
            "notes": [message],
        }

        saved_path = save_result(result)
        state["responses"]["p02_saved_path"] = str(saved_path)

        refresh_view()

    content = ft.Column(
        controls=[
            ft.Text(
                "Escenario: debes seleccionar un recurso para un grupo con bajo nivel lector. "
                "El recurso debe ser comprensible, accesible, reutilizable y no debe exigir registro.",
                size=15,
                weight=ft.FontWeight.W_600,
            ),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID")),
                    ft.DataColumn(ft.Text("Recurso")),
                    ft.DataColumn(ft.Text("Edad")),
                    ft.DataColumn(ft.Text("Nivel lector")),
                    ft.DataColumn(ft.Text("Licencia")),
                    ft.DataColumn(ft.Text("Ficha")),
                ],
                rows=rows,
            ),
            detail_box,
            ft.Container(height=8),
            ft.Text(
                "Selecciona el recurso más adecuado:",
                size=16,
                weight=ft.FontWeight.BOLD,
            ),
            selected_radio,
            ft.Container(height=12),
            ft.ElevatedButton("Validar prueba", on_click=validate),
            build_result_box(state["feedback"]["p02"]),
        ],
        spacing=12,
    )

    return question_block(
        title="P02 · Seleccionar el mejor recurso",
        statement=(
            "Evalúa los indicadores 2.1.A2.1 y 2.1.A2.2 mediante una selección guiada "
            "de recursos digitales ajustados a un contexto educativo concreto."
        ),
        content=content,
    )