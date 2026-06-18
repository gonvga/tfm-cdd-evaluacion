import json
import re
from datetime import datetime, timezone
from pathlib import Path

import flet as ft

from core.storage import save_result
from core.paths import resource_path
from ui.components import checkbox_feedback, question_block


TEST_ID = "P03"
DATA_PATH = resource_path("data", "p03_comp21_b1.json")


def load_test_data() -> dict:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def build_result_box(feedback_data: dict) -> ft.Control:
    if feedback_data["ok"] is None:
        return ft.Container()

    ok = feedback_data["ok"]
    controls = [
        ft.Text(
            "Resultado de la prueba",
            size=17,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE,
        ),
        ft.Text(feedback_data["message"], size=14, color=ft.Colors.WHITE),
    ]

    return ft.Container(
        content=ft.Column(
            controls=controls,
            spacing=8,
        ),
        bgcolor=ft.Colors.GREEN if ok else ft.Colors.RED,
        border_radius=12,
        padding=20,
    )


def section_title(text: str) -> ft.Text:
    return ft.Text(text, size=18, weight=ft.FontWeight.BOLD)


def build_info_panel(title: str, lines: list[str]) -> ft.Control:
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(title, size=15, weight=ft.FontWeight.BOLD),
                *[ft.Text(line, size=13, color=ft.Colors.GREY_700) for line in lines],
            ],
            spacing=4,
        ),
        bgcolor=ft.Colors.BLUE_50,
        border=ft.border.all(1, ft.Colors.BLUE_100),
        border_radius=12,
        padding=14,
    )


def feedback_colors(is_correct: bool) -> tuple[str, str]:
    return ("#DCFCE7", "#16A34A") if is_correct else ("#FEE2E2", "#DC2626")


def inline_feedback(text: str, is_correct: bool) -> ft.Control:
    bgcolor, color = feedback_colors(is_correct)
    return ft.Container(
        content=ft.Text(text, size=12, color=color),
        bgcolor=bgcolor,
        border=ft.border.all(1, color),
        border_radius=8,
        padding=8,
    )


def feedback_panel(title: str, rows: list[tuple[bool, str]]) -> ft.Control:
    if not rows:
        return ft.Container()

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(title, size=14, weight=ft.FontWeight.BOLD),
                *[
                    ft.Row(
                        controls=[
                            ft.Container(
                                width=10,
                                height=10,
                                border_radius=999,
                                bgcolor=feedback_colors(ok)[1],
                            ),
                            ft.Text(text, size=13, expand=True),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    )
                    for ok, text in rows
                ],
            ],
            spacing=8,
        ),
        bgcolor="#F9FAFB",
        border=ft.border.all(1, ft.Colors.GREY_300),
        border_radius=10,
        padding=12,
    )


def build_checkbox_cards(
    options: list[dict],
    saved_ids: list[str],
    validated: bool = False,
) -> tuple[dict, list[ft.Control]]:
    checkboxes = {}
    cards = []

    for option in options:
        checkbox = ft.Checkbox(value=option["id"] in saved_ids)
        checkboxes[option["id"]] = checkbox
        expected = option["expected"]
        selected = option["id"] in saved_ids
        item_ok = selected == expected
        feedback = []
        if validated:
            detail = (
                "Permite recuperar recursos por criterios estables."
                if expected
                else "No garantiza una catalogación sistemática ni recuperable."
            )
            feedback_text, item_ok = checkbox_feedback(selected, expected, detail)
            feedback.append(
                inline_feedback(feedback_text, item_ok)
            )
        cards.append(
            ft.Container(
                content=ft.Row(
                    controls=[
                        checkbox,
                        ft.Column(
                            controls=[
                                ft.Text(option["label"], size=15, weight=ft.FontWeight.W_600),
                                *feedback,
                            ],
                            spacing=6,
                            expand=True,
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                col={"xs": 12, "md": 6},
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY_300),
                bgcolor=feedback_colors(item_ok)[0] if validated else None,
                border_radius=10,
            )
        )

    return checkboxes, cards


def get_selected_ids(checkboxes: dict) -> list[str]:
    return [
        option_id
        for option_id, checkbox in checkboxes.items()
        if checkbox.value
    ]


def evaluate_multi_select(options: list[dict], selected_ids: list[str]) -> dict:
    expected_ids = [option["id"] for option in options if option["expected"]]
    missing = [option_id for option_id in expected_ids if option_id not in selected_ids]
    wrong = [option_id for option_id in selected_ids if option_id not in expected_ids]

    return {
        "selected_ids": selected_ids,
        "expected_ids": expected_ids,
        "missing_ids": missing,
        "wrong_ids": wrong,
        "ok": not missing and not wrong,
    }


def option_labels(options: list[dict], option_ids: list[str]) -> list[str]:
    labels = {option["id"]: option["label"] for option in options}
    return [labels.get(option_id, option_id) for option_id in option_ids]


def evaluate_query_tasks(query_tasks: list[dict], query_answers: dict) -> dict:
    details = {}
    passed_task_ids = []

    for task in query_tasks:
        query = query_answers.get(task["id"], "")
        passed_patterns = []
        missing_patterns = []

        for pattern in task["required_patterns"]:
            if re.search(pattern["regex"], query):
                passed_patterns.append(pattern["id"])
            else:
                missing_patterns.append(pattern["id"])

        if not missing_patterns:
            passed_task_ids.append(task["id"])

        details[task["id"]] = {
            "query": query,
            "passed_patterns": passed_patterns,
            "missing_patterns": missing_patterns,
        }

    return {
        "details": details,
        "passed_task_ids": passed_task_ids,
        "ok": len(passed_task_ids) == len(query_tasks),
    }


def dropdown_options(values: list[str]) -> list[ft.dropdown.Option]:
    return [ft.dropdown.Option(value) for value in values]


def read_markdown(path: str) -> str:
    file_path = Path(path)
    if not file_path.is_absolute():
        file_path = resource_path(*file_path.parts)
    if not file_path.exists():
        return "No se ha encontrado la ficha simulada."

    return file_path.read_text(encoding="utf-8")


def build_test_p03(state: dict, refresh_view) -> ft.Control:
    test_data = load_test_data()
    queries = test_data["queries"]
    cataloging = test_data["cataloging"]
    system = test_data["system"]

    saved_queries = state["responses"].get("p03_queries", {})
    saved_catalog = state["responses"].get("p03_catalog", {})
    saved_systems = state["responses"].get("p03_systems", [])
    opened_resources = state["responses"].get("p03_opened_resources", [])
    active_resource_id = state["responses"].get("p03_active_resource")
    validated = state["feedback"]["p03"]["ok"] is not None
    saved_query_result = evaluate_query_tasks(queries["tasks"], saved_queries) if validated else None

    query_fields = {}
    query_controls = []

    for task in queries["tasks"]:
        task_ok = True
        query_feedback = []
        if validated and saved_query_result:
            task_detail = saved_query_result["details"][task["id"]]
            task_ok = not task_detail["missing_patterns"]
            if task_ok:
                query_feedback.append(
                    inline_feedback("Correcta: la consulta cubre los criterios pedidos.", True)
                )
            else:
                pattern_labels = {
                    pattern["id"]: pattern["label"]
                    for pattern in task["required_patterns"]
                }
                missing = [
                    pattern_labels[pattern_id]
                    for pattern_id in task_detail["missing_patterns"]
                ]
                query_feedback.append(
                    inline_feedback(f"Falta: {', '.join(missing)}.", False)
                )
        field = ft.TextField(
            label=task["label"],
            value=saved_queries.get(task["id"], ""),
            hint_text=task["hint"],
            multiline=True,
            min_lines=1,
            max_lines=2,
        )
        query_fields[task["id"]] = field
        query_controls.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(task["label"], size=15, weight=ft.FontWeight.BOLD),
                        ft.Text(task["hint"], size=13, color=ft.Colors.GREY_700),
                        field,
                        *query_feedback,
                    ],
                    spacing=6,
                ),
                padding=12,
                border=ft.border.all(1, ft.Colors.GREY_300),
                bgcolor=feedback_colors(task_ok)[0] if validated else None,
                border_radius=10,
            )
        )

    system_checkboxes, system_cards = build_checkbox_cards(
        system["options"],
        saved_systems,
        validated,
    )

    decision_options = dropdown_options(cataloging["decision_options"])
    purpose_options = dropdown_options(cataloging["purpose_options"])
    difficulty_options = dropdown_options(cataloging["difficulty_options"])
    tag_options = dropdown_options(cataloging["tag_options"])

    catalog_controls = {}

    def resource_detail(resource: dict) -> ft.Control:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        f"Ficha simulada · {resource['id']}",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Markdown(
                        read_markdown(resource["file_path"]),
                        selectable=True,
                    ),
                ],
                spacing=8,
            ),
            bgcolor=ft.Colors.BLUE_50,
            border_radius=12,
            padding=15,
        )

    def show_resource(resource: dict):
        if resource["id"] not in opened_resources:
            opened_resources.append(resource["id"])

        state["responses"]["p03_opened_resources"] = opened_resources
        state["responses"]["p03_active_resource"] = resource["id"]
        detail_box.content = resource_detail(resource)
        detail_box.update()

    active_resource = next(
        (
            resource
            for resource in cataloging["resources"]
            if resource["id"] == active_resource_id
        ),
        None,
    )

    detail_box = ft.Container(
        content=(
            resource_detail(active_resource)
            if active_resource
            else build_info_panel(
                "Ficha simulada",
                ["Abre una ficha para revisar autoría, licencia, formato, accesibilidad y uso didáctico antes de catalogar."],
            )
        )
    )

    catalog_rows = []
    catalog_feedback_rows = []

    for resource in cataloging["resources"]:
        saved_resource = saved_catalog.get(resource["id"], {})
        expected = {
            "decision": resource["expected_decision"],
            "purpose": resource["expected_purpose"],
            "difficulty": resource["expected_difficulty"],
            "tag": resource["expected_tag"],
        }
        core_fields = ("decision", "purpose", "tag")
        resource_ok = all(
            saved_resource.get(field) == expected[field]
            for field in core_fields
        )
        difficulty_matches = (
            saved_resource.get("difficulty") == expected["difficulty"]
        )
        decision_dropdown = ft.Dropdown(
            value=saved_resource.get("decision"),
            width=135,
            options=decision_options,
        )
        purpose_dropdown = ft.Dropdown(
            value=saved_resource.get("purpose"),
            width=175,
            options=purpose_options,
        )
        difficulty_dropdown = ft.Dropdown(
            value=saved_resource.get("difficulty"),
            width=150,
            options=difficulty_options,
        )
        tag_dropdown = ft.Dropdown(
            value=saved_resource.get("tag"),
            width=170,
            options=tag_options,
        )

        catalog_controls[resource["id"]] = {
            "decision": decision_dropdown,
            "purpose": purpose_dropdown,
            "difficulty": difficulty_dropdown,
            "tag": tag_dropdown,
        }

        resource_title = ft.Column(
            controls=[
                ft.Text(resource["title"], weight=ft.FontWeight.W_600),
                ft.Text(resource["format"], size=12, color=ft.Colors.GREY_700),
            ],
            spacing=3,
        )
        if validated:
            difficulty_note = (
                f"La dificultad coincide con la referencia ({expected['difficulty']})."
                if difficulty_matches
                else (
                    f"Has indicado dificultad {saved_resource.get('difficulty') or 'sin responder'}; "
                    f"la referencia propone {expected['difficulty']}, pero este campo es "
                    "orientativo y no penaliza el resultado."
                )
            )
            catalog_feedback_rows.append(
                (
                    resource_ok,
                    (
                        (
                            f"{resource['id']} · {resource['title']}: decisión, uso y etiqueta "
                            f"correctos. {difficulty_note} {resource['answer_explanation']}"
                        )
                        if resource_ok
                        else (
                            f"{resource['id']} · {resource['title']}: decisión {expected['decision']}, "
                            f"uso {expected['purpose']} y etiqueta {expected['tag']}. "
                            f"{difficulty_note} {resource['answer_explanation']}"
                        )
                    ),
                )
            )

        catalog_rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(resource["id"])),
                    ft.DataCell(resource_title),
                    ft.DataCell(
                        ft.ElevatedButton(
                            "Ver ficha",
                            on_click=lambda e, r=resource: show_resource(r),
                        )
                    ),
                    ft.DataCell(decision_dropdown),
                    ft.DataCell(purpose_dropdown),
                    ft.DataCell(difficulty_dropdown),
                    ft.DataCell(tag_dropdown),
                ]
            )
        )

    def validate(e):
        query_answers = {
            task_id: (field.value or "").strip()
            for task_id, field in query_fields.items()
        }
        selected_systems = get_selected_ids(system_checkboxes)
        catalog_answers = {
            resource_id: {
                "decision": controls["decision"].value,
                "purpose": controls["purpose"].value,
                "difficulty": controls["difficulty"].value,
                "tag": controls["tag"].value,
            }
            for resource_id, controls in catalog_controls.items()
        }

        state["responses"]["p03_queries"] = query_answers
        state["responses"]["p03_catalog"] = catalog_answers
        state["responses"]["p03_systems"] = selected_systems
        state["responses"]["p03_opened_resources"] = opened_resources

        query_result = evaluate_query_tasks(queries["tasks"], query_answers)
        systems_result = evaluate_multi_select(system["options"], selected_systems)

        expected_catalog = {
            resource["id"]: {
                "decision": resource["expected_decision"],
                "purpose": resource["expected_purpose"],
                "difficulty": resource["expected_difficulty"],
                "tag": resource["expected_tag"],
            }
            for resource in cataloging["resources"]
        }

        catalog_correct_fields = []
        catalog_wrong_fields = []
        difficulty_differences = []

        for resource_id, expected in expected_catalog.items():
            answer = catalog_answers[resource_id]
            for field in ("decision", "purpose", "tag"):
                expected_value = expected[field]
                field_id = f"{resource_id}.{field}"
                if answer.get(field) == expected_value:
                    catalog_correct_fields.append(field_id)
                else:
                    catalog_wrong_fields.append(field_id)
            if answer.get("difficulty") != expected["difficulty"]:
                difficulty_differences.append(
                    {
                        "resource_id": resource_id,
                        "selected": answer.get("difficulty"),
                        "reference": expected["difficulty"],
                    }
                )

        resource_count = len(expected_catalog)
        decision_accuracy = sum(
            catalog_answers[resource_id].get("decision") == expected["decision"]
            for resource_id, expected in expected_catalog.items()
        ) / resource_count
        purpose_accuracy = sum(
            catalog_answers[resource_id].get("purpose") == expected["purpose"]
            for resource_id, expected in expected_catalog.items()
        ) / resource_count
        tag_accuracy = sum(
            catalog_answers[resource_id].get("tag") == expected["tag"]
            for resource_id, expected in expected_catalog.items()
        ) / resource_count
        catalog_score_raw = (
            decision_accuracy * 0.50
            + tag_accuracy * 0.30
            + purpose_accuracy * 0.20
        )
        selected_ids = [
            resource_id
            for resource_id, answer in catalog_answers.items()
            if answer.get("decision") == "Incorporar"
        ]
        expected_selected_ids = [
            resource["id"]
            for resource in cataloging["resources"]
            if resource["expected_decision"] == "Incorporar"
        ]
        selection_ok = set(selected_ids) == set(expected_selected_ids)
        selected_formats = {
            resource["format"]
            for resource in cataloging["resources"]
            if resource["id"] in selected_ids
        }
        format_coverage_ok = len(selected_formats) >= cataloging["minimum_selected_formats"]
        catalog_ok = (
            selection_ok
            and format_coverage_ok
            and tag_accuracy >= 0.75
            and purpose_accuracy >= 0.75
            and catalog_score_raw >= 0.85
        )

        required_review_count = cataloging["minimum_resources_to_review"]
        review_ok = len(opened_resources) >= required_review_count

        query_score = round((len(query_result["passed_task_ids"]) / len(queries["tasks"])) * 30)
        review_score = 10 if review_ok else len(opened_resources) * 2
        catalog_score = round(catalog_score_raw * 45)
        systems_score = max(
            0,
            15
            - (len(systems_result["missing_ids"]) * 6)
            - (len(systems_result["wrong_ids"]) * 5),
        )
        score = min(100, query_score + review_score + catalog_score + systems_score)

        ok = query_result["ok"] and review_ok and catalog_ok and systems_result["ok"]

        state["completed"]["p03"] = ok
        message = test_data["feedback"]["success"] if ok else test_data["feedback"]["failure"]

        details = []
        if not query_result["ok"]:
            lines = []
            for task in queries["tasks"]:
                task_detail = query_result["details"][task["id"]]
                if not task_detail["missing_patterns"]:
                    lines.append(f"Correcta: {task['label']}. La consulta cubre los criterios pedidos.")
                    continue

                pattern_labels = {
                    pattern["id"]: pattern["label"]
                    for pattern in task["required_patterns"]
                }
                missing_labels = [
                    pattern_labels[pattern_id]
                    for pattern_id in task_detail["missing_patterns"]
                ]
                lines.append(
                    f"Revisa: {task['label']}. Faltaba: {', '.join(missing_labels)}. "
                    f"Tu consulta: {task_detail['query'] or 'sin responder'}."
                )
            details.append({"title": "Consultas de búsqueda", "lines": lines})

        if not review_ok:
            details.append(
                {
                    "title": "Revisión de fichas",
                    "lines": [
                        f"Debes abrir al menos {required_review_count} fichas simuladas antes de validar.",
                        "La revisión permite comprobar autoría, licencia, accesibilidad, compatibilidad y uso didáctico.",
                    ],
                }
            )

        if not catalog_ok:
            lines = []
            resource_titles = {
                resource["id"]: resource["title"]
                for resource in cataloging["resources"]
            }
            for resource_id, expected in expected_catalog.items():
                answer = catalog_answers[resource_id]
                resource = next(
                    item
                    for item in cataloging["resources"]
                    if item["id"] == resource_id
                )
                core_answer_ok = all(
                    answer.get(field) == expected[field]
                    for field in ("decision", "purpose", "tag")
                )
                if core_answer_ok:
                    difficulty_note = (
                        ""
                        if answer.get("difficulty") == expected["difficulty"]
                        else (
                            f" Has indicado dificultad "
                            f"{answer.get('difficulty') or 'sin responder'}; la referencia "
                            f"propone {expected['difficulty']}, sin penalización."
                        )
                    )
                    lines.append(
                        f"Correcta: {resource_id} · {resource_titles[resource_id]}. "
                        f"{resource['answer_explanation']}{difficulty_note}"
                    )
                else:
                    difficulty_note = (
                        f"En dificultad indicaste {answer.get('difficulty') or 'sin responder'} "
                        f"y la referencia propone {expected['difficulty']}; esta diferencia "
                        "es orientativa y no se penaliza."
                    )
                    lines.append(
                        f"Revisa: {resource_id} · {resource_titles[resource_id]}. "
                        f"Respuesta esperada: decisión {expected['decision']}, "
                        f"uso {expected['purpose']}, "
                        f"etiqueta {expected['tag']}. "
                        f"Tu respuesta: decisión {answer.get('decision') or 'sin responder'}, "
                        f"uso {answer.get('purpose') or 'sin responder'}, "
                        f"etiqueta {answer.get('tag') or 'sin responder'}. "
                        f"{difficulty_note} "
                        f"Explicación: {resource['answer_explanation']}"
                    )
            details.append({"title": "Catalogación de recursos", "lines": lines})

        if not systems_result["ok"]:
            correct = ", ".join(option_labels(system["options"], systems_result["expected_ids"]))
            lines = [f"Respuesta correcta: {correct}."]
            for option in system["options"]:
                detail = (
                    "Permite recuperar recursos por criterios estables."
                    if option["expected"]
                    else "No garantiza una catalogación sistemática ni recuperable."
                )
                feedback_text, _ = checkbox_feedback(
                    option["id"] in systems_result["selected_ids"],
                    bool(option["expected"]),
                    detail,
                )
                lines.append(f"{option['label']}: {feedback_text}")
            details.append({"title": "Sistema de catálogo", "lines": lines})

        state["feedback"]["p03"] = {
            "ok": ok,
            "message": message,
            "details": [] if ok else details,
        }

        result = {
            "test_id": TEST_ID,
            "scenario_id": test_data["scenario_id"],
            "scenario_title": test_data["scenario_title"],
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "score_0_100": score,
            "level_hint": "B1" if ok else "A2",
            "payload": {
                "query_answers": query_answers,
                "query_details": query_result["details"],
                "passed_query_task_ids": query_result["passed_task_ids"],
                "opened_resources": opened_resources,
                "required_review_count": required_review_count,
                "catalog_answers": catalog_answers,
                "expected_catalog": expected_catalog,
                "catalog_correct_fields": catalog_correct_fields,
                "catalog_wrong_fields": catalog_wrong_fields,
                "difficulty_differences_advisory": difficulty_differences,
                "catalog_accuracy": {
                    "decision": decision_accuracy,
                    "purpose": purpose_accuracy,
                    "tag": tag_accuracy,
                },
                "selected_resource_ids": selected_ids,
                "expected_selected_resource_ids": expected_selected_ids,
                "selected_formats": sorted(selected_formats),
                "minimum_selected_formats": cataloging["minimum_selected_formats"],
                "selected_systems": selected_systems,
                "expected_systems": systems_result["expected_ids"],
                "missing_systems": systems_result["missing_ids"],
                "wrong_systems": systems_result["wrong_ids"],
            },
            "checks": [
                {
                    "check_id": "search_query_construction",
                    "label": "Construye búsquedas con operadores y criterios de formato, fuente, licencia o accesibilidad",
                    "passed": query_result["ok"],
                    "weight": 30,
                    "evidence": str(query_answers),
                },
                {
                    "check_id": "simulated_resource_review",
                    "label": "Revisa fichas simuladas antes de catalogar",
                    "passed": review_ok,
                    "weight": 10,
                    "evidence": ", ".join(opened_resources),
                },
                {
                    "check_id": "systematic_cataloging",
                    "label": "Selecciona el lote y lo cataloga por uso y etiquetas; la dificultad es orientativa",
                    "passed": catalog_ok,
                    "weight": 45,
                    "evidence": str(catalog_answers),
                },
                {
                    "check_id": "catalog_system_choice",
                    "label": "Selecciona un sistema de organización recuperable y compartible",
                    "passed": systems_result["ok"],
                    "weight": 15,
                    "evidence": ", ".join(selected_systems),
                },
            ],
            "notes": [message],
        }

        saved_path = save_result(result)
        state["responses"]["p03_saved_path"] = str(saved_path)

        refresh_view()

    content = ft.Column(
        controls=[
            ft.Text(
                test_data["intro"],
                size=15,
                weight=ft.FontWeight.W_600,
            ),
            build_info_panel(
                test_data["diagnosis"]["title"],
                test_data["diagnosis"]["lines"],
            ),
            section_title(queries["title"]),
            ft.Text(queries["description"], size=14),
            *query_controls,
            ft.Divider(height=24),
            section_title(cataloging["title"]),
            ft.Text(cataloging["description"], size=14),
            build_info_panel(
                cataloging["assessment"]["title"],
                cataloging["assessment"]["lines"],
            ),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID")),
                    ft.DataColumn(ft.Text("Recurso")),
                    ft.DataColumn(ft.Text("Ficha")),
                    ft.DataColumn(ft.Text("Decisión")),
                    ft.DataColumn(ft.Text("Uso")),
                    ft.DataColumn(ft.Text("Dificultad (orientativa)")),
                    ft.DataColumn(ft.Text("Etiqueta")),
                ],
                rows=catalog_rows,
            ),
            feedback_panel("Corrección de catalogación", catalog_feedback_rows),
            detail_box,
            ft.Divider(height=24),
            section_title(system["title"]),
            ft.Text(system["description"], size=14),
            ft.ResponsiveRow(controls=system_cards, spacing=8, run_spacing=8),
            ft.Container(height=8),
            ft.ElevatedButton("Validar prueba", on_click=validate),
            build_result_box(state["feedback"]["p03"]),
        ],
        spacing=12,
    )

    return question_block(
        title=test_data["title"],
        statement=test_data["statement"],
        content=content,
    )
