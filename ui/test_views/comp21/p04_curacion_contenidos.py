import json
import re
from datetime import datetime
from pathlib import Path

import flet as ft

from core.storage import save_result
from ui.components import question_block


TEST_ID = "P04"
DATA_PATH = Path("data/p04_comp21_b2.json")


def load_test_data() -> dict:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


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
                ft.Text(feedback_data["message"], size=14, color=ft.Colors.WHITE),
            ],
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


def dropdown_options(values: list[str]) -> list[ft.dropdown.Option]:
    return [ft.dropdown.Option(value) for value in values]


def get_selected_ids(checkboxes: dict) -> list[str]:
    return [
        option_id
        for option_id, checkbox in checkboxes.items()
        if checkbox.value
    ]


def evaluate_query_tasks(tasks: list[dict], answers: dict) -> dict:
    details = {}
    passed = []

    for task in tasks:
        query = answers.get(task["id"], "")
        missing = []
        passed_patterns = []

        for pattern in task["required_patterns"]:
            if re.search(pattern["regex"], query):
                passed_patterns.append(pattern["id"])
            else:
                missing.append(pattern["id"])

        if not missing:
            passed.append(task["id"])

        details[task["id"]] = {
            "query": query,
            "missing": missing,
            "passed": passed_patterns,
        }

    return {
        "details": details,
        "passed": passed,
        "ok": len(passed) == len(tasks),
    }


def build_test_p04(state: dict, refresh_view) -> ft.Control:
    test_data = load_test_data()
    protocol = test_data["protocol"]
    advice = test_data["advice"]
    repositories = test_data["repositories"]

    saved_catalog = state["responses"].get("p04_catalog", {})
    saved_queries = state["responses"].get("p04_queries", {})
    saved_repository_actions = state["responses"].get("p04_repository_actions", [])
    validated = state["feedback"]["p04"]["ok"] is not None

    bloom_options = dropdown_options(protocol["bloom_options"])
    competence_options = dropdown_options(protocol["competence_options"])
    decision_options = dropdown_options(protocol["decision_options"])
    score_options = dropdown_options(protocol["score_options"])

    catalog_controls = {}
    catalog_cards = []
    catalog_feedback_rows = []

    for resource in protocol["resources"]:
        saved_resource = saved_catalog.get(resource["id"], {})
        bloom_dd = ft.Dropdown(
            label="Bloom",
            value=saved_resource.get("bloom"),
            options=bloom_options,
            width=190,
        )
        competence_dd = ft.Dropdown(
            label="Competencia",
            value=saved_resource.get("competence"),
            options=competence_options,
            width=230,
        )
        decision_dd = ft.Dropdown(
            label="Decisión",
            value=saved_resource.get("decision"),
            options=decision_options,
            width=160,
        )
        technical_dd = ft.Dropdown(
            label="Técnica",
            value=saved_resource.get("technical"),
            options=score_options,
            width=115,
        )
        truth_dd = ft.Dropdown(
            label="Veracidad",
            value=saved_resource.get("truth"),
            options=score_options,
            width=120,
        )
        relevance_dd = ft.Dropdown(
            label="Relevancia",
            value=saved_resource.get("relevance"),
            options=score_options,
            width=125,
        )

        catalog_controls[resource["id"]] = {
            "bloom": bloom_dd,
            "competence": competence_dd,
            "decision": decision_dd,
            "technical": technical_dd,
            "truth": truth_dd,
            "relevance": relevance_dd,
        }

        expected = {
            "bloom": resource["expected_bloom"],
            "competence": resource["expected_competence"],
            "decision": resource["expected_decision"],
        }
        relation_ok = all(saved_resource.get(key) == value for key, value in expected.items())
        score_ok = all(
            saved_resource.get(key) is not None
            and int(saved_resource.get(key)) >= minimum
            for key, minimum in resource["minimum_scores"].items()
        )
        resource_ok = relation_ok and score_ok

        if validated:
            catalog_feedback_rows.append(
                (
                    resource_ok,
                    (
                        f"{resource['id']} · {resource['title']}: catalogación correcta"
                        if resource_ok
                        else (
                            f"{resource['id']} · {resource['title']}: Bloom {expected['bloom']}, "
                            f"competencia {expected['competence']}, decisión {expected['decision']}; "
                            "puntuaciones mínimas técnica/veracidad/relevancia "
                            f"{resource['minimum_scores']['technical']}/"
                            f"{resource['minimum_scores']['truth']}/"
                            f"{resource['minimum_scores']['relevance']}."
                        )
                    ),
                )
            )

        catalog_cards.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            f"{resource['id']} · {resource['title']}",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(resource["format"], size=13, color=ft.Colors.GREY_700),
                        ft.Text(resource["evidence"], size=13, color=ft.Colors.GREY_700),
                        ft.Row(
                            controls=[bloom_dd, competence_dd, decision_dd],
                            wrap=True,
                            spacing=10,
                        ),
                        ft.Row(
                            controls=[technical_dd, truth_dd, relevance_dd],
                            wrap=True,
                            spacing=10,
                        ),
                    ],
                    spacing=8,
                ),
                bgcolor="#F9FAFB",
                border=ft.border.all(1, "#E5E7EB"),
                border_radius=10,
                padding=14,
            )
        )

    query_fields = {}
    query_controls = []
    saved_query_result = evaluate_query_tasks(advice["tasks"], saved_queries) if validated else None

    for task in advice["tasks"]:
        task_ok = True
        feedback = []
        if validated and saved_query_result:
            detail = saved_query_result["details"][task["id"]]
            task_ok = not detail["missing"]
            if task_ok:
                feedback.append(inline_feedback("Correcta: incluye los criterios necesarios.", True))
            else:
                labels = {
                    pattern["id"]: pattern["label"]
                    for pattern in task["required_patterns"]
                }
                missing = ", ".join(labels[item] for item in detail["missing"])
                feedback.append(inline_feedback(f"Falta: {missing}.", False))

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
                        *feedback,
                    ],
                    spacing=6,
                ),
                bgcolor=feedback_colors(task_ok)[0] if validated else "#F9FAFB",
                border=ft.border.all(1, feedback_colors(task_ok)[1] if validated else "#E5E7EB"),
                border_radius=10,
                padding=14,
            )
        )

    repository_checkboxes = {}
    repository_cards = []
    repository_feedback_rows = []

    for option in repositories["options"]:
        cb = ft.Checkbox(value=option["id"] in saved_repository_actions)
        repository_checkboxes[option["id"]] = cb
        expected = option["expected"]
        selected = option["id"] in saved_repository_actions
        option_ok = selected == expected

        if validated:
            repository_feedback_rows.append(
                (
                    option_ok,
                    f"{option['label']}: {'incluir' if expected else 'descartar'}. {option['feedback']}",
                )
            )

        repository_cards.append(
            ft.Container(
                content=ft.Row(
                    controls=[
                        cb,
                        ft.Column(
                            controls=[
                                ft.Text(option["label"], size=15, weight=ft.FontWeight.BOLD),
                                ft.Text(option["feedback"], size=13, color=ft.Colors.GREY_700),
                            ],
                            spacing=4,
                            expand=True,
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                col={"xs": 12, "md": 6},
                bgcolor=feedback_colors(option_ok)[0] if validated else "#F9FAFB",
                border=ft.border.all(1, feedback_colors(option_ok)[1] if validated else "#E5E7EB"),
                border_radius=10,
                padding=12,
            )
        )

    def validate(e):
        catalog_answers = {
            resource_id: {
                key: control.value
                for key, control in controls.items()
            }
            for resource_id, controls in catalog_controls.items()
        }
        query_answers = {
            task_id: (field.value or "").strip()
            for task_id, field in query_fields.items()
        }
        selected_repository_actions = get_selected_ids(repository_checkboxes)

        state["responses"]["p04_catalog"] = catalog_answers
        state["responses"]["p04_queries"] = query_answers
        state["responses"]["p04_repository_actions"] = selected_repository_actions

        missing_catalog = any(
            value is None
            for answer in catalog_answers.values()
            for value in answer.values()
        )

        query_result = evaluate_query_tasks(advice["tasks"], query_answers)

        expected_repository_actions = [
            option["id"] for option in repositories["options"] if option["expected"]
        ]
        repository_missing = [
            option_id
            for option_id in expected_repository_actions
            if option_id not in selected_repository_actions
        ]
        repository_wrong = [
            option_id
            for option_id in selected_repository_actions
            if option_id not in expected_repository_actions
        ]
        repositories_ok = not repository_missing and not repository_wrong

        expected_catalog = {}
        relation_correct = []
        score_correct = []

        for resource in protocol["resources"]:
            rid = resource["id"]
            expected_catalog[rid] = {
                "bloom": resource["expected_bloom"],
                "competence": resource["expected_competence"],
                "decision": resource["expected_decision"],
                "minimum_scores": resource["minimum_scores"],
            }
            answer = catalog_answers[rid]
            relation_ok = (
                answer["bloom"] == resource["expected_bloom"]
                and answer["competence"] == resource["expected_competence"]
                and answer["decision"] == resource["expected_decision"]
            )
            scores_ok = (
                answer["technical"] is not None
                and answer["truth"] is not None
                and answer["relevance"] is not None
                and int(answer["technical"]) >= resource["minimum_scores"]["technical"]
                and int(answer["truth"]) >= resource["minimum_scores"]["truth"]
                and int(answer["relevance"]) >= resource["minimum_scores"]["relevance"]
            )
            if relation_ok:
                relation_correct.append(rid)
            if scores_ok:
                score_correct.append(rid)

        relation_ok = len(relation_correct) == len(protocol["resources"])
        scoring_ok = len(score_correct) == len(protocol["resources"])
        protocol_ok = not missing_catalog and relation_ok and scoring_ok
        ok = protocol_ok and query_result["ok"] and repositories_ok

        protocol_score = 45 if protocol_ok else round(((len(relation_correct) + len(score_correct)) / (len(protocol["resources"]) * 2)) * 45)
        advice_score = round((len(query_result["passed"]) / len(advice["tasks"])) * 30)
        repository_score = max(0, 25 - (len(repository_missing) * 7) - (len(repository_wrong) * 6))
        score = min(100, protocol_score + advice_score + repository_score)

        state["completed"]["p04"] = ok
        message = test_data["feedback"]["success"] if ok else test_data["feedback"]["failure"]
        state["feedback"]["p04"] = {"ok": ok, "message": message}

        result = {
            "test_id": TEST_ID,
            "scenario_id": test_data["scenario_id"],
            "scenario_title": test_data["scenario_title"],
            "timestamp_utc": datetime.utcnow().isoformat(),
            "score_0_100": score,
            "level_hint": "B2" if ok else "B1",
            "payload": {
                "catalog_answers": catalog_answers,
                "expected_catalog": expected_catalog,
                "relation_correct": relation_correct,
                "score_correct": score_correct,
                "query_answers": query_answers,
                "query_details": query_result["details"],
                "selected_repository_actions": selected_repository_actions,
                "expected_repository_actions": expected_repository_actions,
                "repository_missing": repository_missing,
                "repository_wrong": repository_wrong,
            },
            "checks": [
                {
                    "check_id": "relational_catalog_protocol",
                    "label": "Usa un instrumento relacional de evaluación y catalogación",
                    "passed": protocol_ok,
                    "weight": 45,
                    "evidence": str(catalog_answers),
                },
                {
                    "check_id": "informal_search_advice",
                    "label": "Asesora con estrategias de búsqueda eficaces",
                    "passed": query_result["ok"],
                    "weight": 30,
                    "evidence": str(query_answers),
                },
                {
                    "check_id": "repository_update_actions",
                    "label": "Selecciona acciones proactivas de actualización de repositorios",
                    "passed": repositories_ok,
                    "weight": 25,
                    "evidence": ", ".join(selected_repository_actions),
                },
            ],
            "notes": [message],
        }

        saved_path = save_result(result)
        state["responses"]["p04_saved_path"] = str(saved_path)

        refresh_view()

    content = ft.Column(
        controls=[
            ft.Text(test_data["intro"], size=15, weight=ft.FontWeight.W_600),
            section_title(protocol["title"]),
            ft.Text(protocol["description"], size=14),
            build_info_panel(
                "Escala de puntuación",
                [
                    "1 = muy bajo; 5 = excelente.",
                    "Técnica: accesibilidad y compatibilidad.",
                    "Veracidad: autoría, fuentes y actualización.",
                    "Relevancia: ajuste al contexto y valor didáctico.",
                ],
            ),
            ft.Column(controls=catalog_cards, spacing=10),
            feedback_panel("Corrección del protocolo", catalog_feedback_rows),
            ft.Divider(height=24),
            section_title(advice["title"]),
            ft.Text(advice["description"], size=14),
            *query_controls,
            ft.Divider(height=24),
            section_title(repositories["title"]),
            ft.Text(repositories["description"], size=14),
            ft.ResponsiveRow(controls=repository_cards, spacing=8, run_spacing=8),
            feedback_panel("Corrección de actualización", repository_feedback_rows),
            ft.Container(height=8),
            ft.ElevatedButton("Validar prueba", on_click=validate),
            build_result_box(state["feedback"]["p04"]),
        ],
        spacing=12,
    )

    return question_block(
        title=test_data["title"],
        statement=test_data["statement"],
        content=content,
    )
