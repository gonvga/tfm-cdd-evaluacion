import json
import re
from datetime import datetime, timezone

import flet as ft

from core.paths import resource_path
from core.storage import save_result
from ui.components import question_block


TEST_ID = "P04"
DATA_PATH = resource_path("data", "p04_comp21_b2.json")


def load_test_data() -> dict:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def feedback_colors(ok: bool) -> tuple[str, str]:
    return ("#DCFCE7", "#166534") if ok else ("#FEE2E2", "#991B1B")


def inline_feedback(text: str, ok: bool) -> ft.Control:
    bgcolor, color = feedback_colors(ok)
    return ft.Container(
        content=ft.Text(text, size=12, color=color),
        bgcolor=bgcolor,
        border=ft.border.all(1, color),
        border_radius=8,
        padding=9,
    )


def section_title(text: str) -> ft.Text:
    return ft.Text(text, size=18, weight=ft.FontWeight.BOLD, color="#111827")


def info_panel(title: str, lines: list[str]) -> ft.Control:
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    title,
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color="#1E3A8A",
                ),
                *[ft.Text(f"• {line}", size=13, color="#374151") for line in lines],
            ],
            spacing=6,
        ),
        bgcolor="#EFF6FF",
        border=ft.border.all(1, "#BFDBFE"),
        border_radius=12,
        padding=14,
    )


def evidence_row(icon: str, label: str, value: str) -> ft.Control:
    return ft.Row(
        controls=[
            ft.Container(
                content=ft.Icon(icon, size=17, color="#1D4ED8"),
                width=32,
                height=32,
                alignment=ft.Alignment.CENTER,
                bgcolor="#DBEAFE",
                border_radius=8,
            ),
            ft.Column(
                controls=[
                    ft.Text(
                        label.upper(),
                        size=9,
                        weight=ft.FontWeight.BOLD,
                        color="#64748B",
                    ),
                    ft.Text(value, size=12, color="#374151"),
                ],
                spacing=1,
                expand=True,
            ),
        ],
        spacing=8,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )


def subsection_label(text: str) -> ft.Text:
    return ft.Text(
        text.upper(),
        size=10,
        weight=ft.FontWeight.BOLD,
        color="#1E40AF",
    )


def build_result_box(feedback: dict) -> ft.Control:
    if feedback["ok"] is None:
        return ft.Container()
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "Resultado de la prueba",
                    size=17,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
                ft.Text(feedback["message"], size=14, color=ft.Colors.WHITE),
            ],
            spacing=8,
        ),
        bgcolor=ft.Colors.GREEN if feedback["ok"] else ft.Colors.RED,
        border_radius=12,
        padding=20,
    )


def dropdown_options(values: list[str]) -> list[ft.dropdown.Option]:
    return [ft.dropdown.Option(value) for value in values]


def evaluate_patterns(value: str | None, patterns: list[dict]) -> dict:
    text = value or ""
    passed = [
        pattern["id"]
        for pattern in patterns
        if re.search(pattern["regex"], text)
    ]
    missing = [
        pattern["id"]
        for pattern in patterns
        if pattern["id"] not in passed
    ]
    return {
        "passed": passed,
        "missing": missing,
        "ratio": len(passed) / len(patterns),
    }


def score_proximity(selected: str | None, reference: int) -> float:
    if selected is None:
        return 0.0
    difference = abs(int(selected) - reference)
    if difference <= 1:
        return 1.0
    if difference == 2:
        return 0.5
    return 0.0


def decision_is_coherent(decision: str | None, scores: dict) -> bool:
    if any(scores.get(key) is None for key in ("technical", "truth", "relevance")):
        return False
    technical = int(scores["technical"])
    truth = int(scores["truth"])
    relevance = int(scores["relevance"])
    average = (technical + truth + relevance) / 3

    if decision == "Recomendar":
        return truth >= 3 and technical >= 3 and relevance >= 3 and average >= 3.5
    if decision == "Adaptar":
        return truth >= 2 and relevance >= 3 and average >= 2.5
    if decision == "Descartar":
        return truth <= 2 or technical <= 2 or average <= 2.5
    return False


def evaluate_resource(resource: dict, answer: dict) -> dict:
    bloom_ok = answer.get("bloom") in resource["accepted_bloom"]
    competence_ok = answer.get("competence") in resource["accepted_competences"]
    decision_ok = answer.get("decision") in resource["accepted_decisions"]
    score_ratios = {
        key: score_proximity(answer.get(key), reference)
        for key, reference in resource["reference_scores"].items()
    }
    coherence_ok = decision_is_coherent(answer.get("decision"), answer)
    raw = (
        (1 if bloom_ok else 0)
        + (1 if competence_ok else 0)
        + (2 if decision_ok else 0)
        + sum(score_ratios.values())
        + (2 if coherence_ok else 0)
    )
    return {
        "bloom_ok": bloom_ok,
        "competence_ok": competence_ok,
        "decision_ok": decision_ok,
        "score_ratios": score_ratios,
        "coherence_ok": coherence_ok,
        "ratio": raw / 9,
    }


def build_test_p04(state: dict, refresh_view) -> ft.Control:
    data = load_test_data()
    protocol = data["protocol"]
    advice = data["advice"]
    repositories = data["repositories"]
    saved_catalog = state["responses"].get("p04_catalog", {})
    saved_advice = state["responses"].get("p04_advice", {})
    saved_plan = state["responses"].get("p04_repository_plan", {})
    validated = state["feedback"]["p04"]["ok"] is not None

    catalog_controls = {}
    catalog_cards = []
    saved_resource_results = {
        resource["id"]: evaluate_resource(
            resource,
            saved_catalog.get(resource["id"], {}),
        )
        for resource in protocol["resources"]
    }

    for resource in protocol["resources"]:
        saved = saved_catalog.get(resource["id"], {})
        controls = {
            "bloom": ft.Dropdown(
                label="Bloom",
                value=saved.get("bloom"),
                options=dropdown_options(protocol["bloom_options"]),
                width=190,
            ),
            "competence": ft.Dropdown(
                label="Competencia",
                value=saved.get("competence"),
                options=dropdown_options(protocol["competence_options"]),
                width=230,
            ),
            "decision": ft.Dropdown(
                label="Decisión",
                value=saved.get("decision"),
                options=dropdown_options(protocol["decision_options"]),
                width=160,
            ),
            "technical": ft.Dropdown(
                label="Técnica",
                value=saved.get("technical"),
                options=dropdown_options(protocol["score_options"]),
                width=115,
            ),
            "truth": ft.Dropdown(
                label="Veracidad",
                value=saved.get("truth"),
                options=dropdown_options(protocol["score_options"]),
                width=120,
            ),
            "relevance": ft.Dropdown(
                label="Relevancia",
                value=saved.get("relevance"),
                options=dropdown_options(protocol["score_options"]),
                width=125,
            ),
        }
        catalog_controls[resource["id"]] = controls
        result = saved_resource_results[resource["id"]]
        feedback = []
        if validated:
            acceptable = result["ratio"] >= 0.72 and result["coherence_ok"]
            score_notes = []
            for key, label in (
                ("technical", "técnica"),
                ("truth", "veracidad"),
                ("relevance", "relevancia"),
            ):
                proximity = result["score_ratios"][key]
                if proximity == 0.5:
                    score_notes.append(f"{label}: diferencia discutible pero parcialmente válida")
                elif proximity == 0:
                    score_notes.append(
                        f"{label}: no se corresponde con la evidencia "
                        f"(referencia {resource['reference_scores'][key]})"
                    )
            relation_notes = []
            if not result["bloom_ok"]:
                relation_notes.append(
                    "Bloom aceptable: " + " o ".join(resource["accepted_bloom"])
                )
            if not result["competence_ok"]:
                relation_notes.append(
                    "competencia aceptable: "
                    + " o ".join(resource["accepted_competences"])
                )
            if not result["decision_ok"]:
                relation_notes.append(
                    "decisión defendible: " + " o ".join(resource["accepted_decisions"])
                )
            if not result["coherence_ok"]:
                relation_notes.append("la decisión no es coherente con tus puntuaciones")
            detail = ". ".join([*relation_notes, *score_notes]) or resource["explanation"]
            feedback.append(inline_feedback(detail + ".", acceptable))

        catalog_cards.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Container(
                                    content=ft.Text(
                                        resource["id"],
                                        size=13,
                                        weight=ft.FontWeight.BOLD,
                                        color="#1E40AF",
                                    ),
                                    width=34,
                                    height=34,
                                    alignment=ft.Alignment.CENTER,
                                    bgcolor="#DBEAFE",
                                    border_radius=10,
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text(
                                            resource["title"],
                                            size=17,
                                            weight=ft.FontWeight.BOLD,
                                            color="#111827",
                                        ),
                                        ft.Text(
                                            resource["format"],
                                            size=12,
                                            color="#6B7280",
                                        ),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                            ],
                            spacing=10,
                        ),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    evidence_row(
                                        ft.Icons.LINK_OUTLINED,
                                        "Procedencia",
                                        resource["source"],
                                    ),
                                    evidence_row(
                                        ft.Icons.BADGE_OUTLINED,
                                        "Autoría",
                                        resource["authorship"],
                                    ),
                                    evidence_row(
                                        ft.Icons.EVENT_AVAILABLE_OUTLINED,
                                        "Fecha y licencia",
                                        resource["date_license"],
                                    ),
                                    evidence_row(
                                        ft.Icons.ACCESSIBILITY_NEW,
                                        "Accesibilidad",
                                        resource["accessibility"],
                                    ),
                                    evidence_row(
                                        ft.Icons.SCHOOL_OUTLINED,
                                        "Aplicación didáctica",
                                        resource["classroom_use"],
                                    ),
                                ],
                                spacing=8,
                            ),
                            bgcolor="#FFFFFF",
                            border=ft.border.all(1, "#E5E7EB"),
                            border_radius=10,
                            padding=12,
                        ),
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Icon(
                                        ft.Icons.FACT_CHECK_OUTLINED,
                                        size=18,
                                        color="#92400E",
                                    ),
                                    ft.Text(
                                        resource["evidence"],
                                        size=12,
                                        color="#78350F",
                                        expand=True,
                                    ),
                                ],
                                spacing=8,
                                vertical_alignment=ft.CrossAxisAlignment.START,
                            ),
                            bgcolor="#FFFBEB",
                            border=ft.border.all(1, "#FDE68A"),
                            border_radius=10,
                            padding=11,
                        ),
                        subsection_label("Relación educativa y decisión"),
                        ft.Row(
                            controls=[
                                controls["bloom"],
                                controls["competence"],
                                controls["decision"],
                            ],
                            wrap=True,
                            spacing=10,
                        ),
                        subsection_label("Valoración de calidad · 1 muy baja / 5 excelente"),
                        ft.Row(
                            controls=[
                                controls["technical"],
                                controls["truth"],
                                controls["relevance"],
                            ],
                            wrap=True,
                            spacing=10,
                        ),
                        *feedback,
                    ],
                    spacing=11,
                ),
                bgcolor="#F8FAFC",
                border=ft.border.all(1, "#CBD5E1"),
                border_radius=14,
                padding=16,
            )
        )

    advice_controls = {}
    advice_cards = []
    for task in advice["tasks"]:
        saved = saved_advice.get(task["id"], {})
        controls = {
            "query": ft.TextField(
                label="Consulta recomendada",
                hint_text=task["query_hint"],
                value=saved.get("query", ""),
                multiline=True,
                min_lines=1,
                max_lines=2,
            ),
            "rationale": ft.TextField(
                label="Por qué la recomendarías",
                hint_text=task["rationale_hint"],
                value=saved.get("rationale", ""),
                multiline=True,
                min_lines=2,
                max_lines=4,
            ),
            "verification": ft.TextField(
                label="Cómo verificarías los resultados",
                hint_text=task["verification_hint"],
                value=saved.get("verification", ""),
                multiline=True,
                min_lines=2,
                max_lines=4,
            ),
        }
        advice_controls[task["id"]] = controls
        feedback = []
        if validated:
            results = {
                "query": evaluate_patterns(saved.get("query"), task["query_patterns"]),
                "rationale": evaluate_patterns(
                    saved.get("rationale"),
                    task["rationale_patterns"],
                ),
                "verification": evaluate_patterns(
                    saved.get("verification"),
                    task["verification_patterns"],
                ),
            }
            ratio = sum(item["ratio"] for item in results.values()) / 3
            missing_labels = []
            for key, patterns_key in (
                ("query", "query_patterns"),
                ("rationale", "rationale_patterns"),
                ("verification", "verification_patterns"),
            ):
                labels = {
                    pattern["id"]: pattern["label"]
                    for pattern in task[patterns_key]
                }
                missing_labels.extend(labels[item] for item in results[key]["missing"])
            feedback.append(
                inline_feedback(
                    (
                        "Asesoramiento suficientemente razonado."
                        if ratio >= 0.75
                        else "Faltan evidencias: " + ", ".join(missing_labels) + "."
                    ),
                    ratio >= 0.75,
                )
            )
        advice_cards.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(task["label"], size=16, weight=ft.FontWeight.BOLD),
                        controls["query"],
                        controls["rationale"],
                        controls["verification"],
                        *feedback,
                    ],
                    spacing=8,
                ),
                bgcolor="#F9FAFB",
                border=ft.border.all(1, "#E5E7EB"),
                border_radius=12,
                padding=14,
            )
        )

    plan_controls = {}
    plan_cards = []
    for field in repositories["fields"]:
        control = ft.TextField(
            label=field["label"],
            hint_text=field["hint"],
            value=saved_plan.get(field["id"], ""),
            multiline=True,
            min_lines=2,
            max_lines=5,
        )
        plan_controls[field["id"]] = control
        feedback = []
        if validated:
            result = evaluate_patterns(
                saved_plan.get(field["id"]),
                field["required_patterns"],
            )
            enough_words = len((saved_plan.get(field["id"]) or "").split()) >= field["minimum_words"]
            field_ok = result["ratio"] >= 2 / 3 and enough_words
            labels = {
                pattern["id"]: pattern["label"]
                for pattern in field["required_patterns"]
            }
            feedback.append(
                inline_feedback(
                    (
                        "Plan operativo y suficientemente concreto."
                        if field_ok
                        else "Revisa: "
                        + ", ".join(labels[item] for item in result["missing"])
                        + ("" if enough_words else "; falta concreción")
                        + "."
                    ),
                    field_ok,
                )
            )
        plan_cards.append(
            ft.Container(
                content=ft.Column(
                    controls=[control, *feedback],
                    spacing=6,
                ),
                bgcolor="#F9FAFB",
                border=ft.border.all(1, "#E5E7EB"),
                border_radius=12,
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
        advice_answers = {
            task_id: {
                key: control.value or ""
                for key, control in controls.items()
            }
            for task_id, controls in advice_controls.items()
        }
        plan_answers = {
            field_id: control.value or ""
            for field_id, control in plan_controls.items()
        }
        state["responses"]["p04_catalog"] = catalog_answers
        state["responses"]["p04_advice"] = advice_answers
        state["responses"]["p04_repository_plan"] = plan_answers

        resource_results = {
            resource["id"]: evaluate_resource(
                resource,
                catalog_answers[resource["id"]],
            )
            for resource in protocol["resources"]
        }
        protocol_ratio = sum(
            result["ratio"] for result in resource_results.values()
        ) / len(resource_results)
        coherent_count = sum(
            result["coherence_ok"] for result in resource_results.values()
        )
        accepted_decisions = sum(
            result["decision_ok"] for result in resource_results.values()
        )
        complete = all(
            value is not None
            for answer in catalog_answers.values()
            for value in answer.values()
        )
        protocol_ok = (
            complete
            and protocol_ratio >= 0.75
            and coherent_count >= 3
            and accepted_decisions >= 3
        )

        advice_results = {}
        task_ratios = []
        for task in advice["tasks"]:
            answer = advice_answers[task["id"]]
            results = {
                "query": evaluate_patterns(answer["query"], task["query_patterns"]),
                "rationale": evaluate_patterns(
                    answer["rationale"],
                    task["rationale_patterns"],
                ),
                "verification": evaluate_patterns(
                    answer["verification"],
                    task["verification_patterns"],
                ),
            }
            ratio = sum(item["ratio"] for item in results.values()) / 3
            advice_results[task["id"]] = {"fields": results, "ratio": ratio}
            task_ratios.append(ratio)
        advice_ratio = sum(task_ratios) / len(task_ratios)
        advice_ok = advice_ratio >= 0.75 and all(ratio >= 0.6 for ratio in task_ratios)

        plan_results = {}
        plan_ratios = []
        for field in repositories["fields"]:
            result = evaluate_patterns(
                plan_answers[field["id"]],
                field["required_patterns"],
            )
            enough_words = len(plan_answers[field["id"]].split()) >= field["minimum_words"]
            ratio = result["ratio"] if enough_words else result["ratio"] * 0.5
            plan_results[field["id"]] = {
                **result,
                "enough_words": enough_words,
                "effective_ratio": ratio,
            }
            plan_ratios.append(ratio)
        plan_ratio = sum(plan_ratios) / len(plan_ratios)
        repositories_ok = (
            plan_ratio >= 0.75
            and plan_results["discovery"]["effective_ratio"] >= 2 / 3
        )

        protocol_score = round(protocol_ratio * 50)
        advice_score = round(advice_ratio * 30)
        repository_score = round(plan_ratio * 20)
        score = min(100, protocol_score + advice_score + repository_score)
        ok = score >= 80 and protocol_ok and advice_ok and repositories_ok

        details = []
        if not protocol_ok:
            details.append(
                "El protocolo debe alcanzar una valoración global coherente; se admite "
                "una diferencia de un punto en las escalas y relaciones alternativas justificables."
            )
        if not advice_ok:
            details.append(
                "El asesoramiento debe combinar consulta, explicación de la estrategia y "
                "comprobación de autoría, vigencia, licencia, accesibilidad y adecuación."
            )
        if not repositories_ok:
            details.append(
                "El plan debe localizar nuevas fuentes, fijar revisiones periódicas y "
                "compartir conclusiones que mejoren el protocolo del equipo."
            )

        message = data["feedback"]["success"] if ok else data["feedback"]["failure"]
        state["completed"]["p04"] = ok
        state["feedback"]["p04"] = {
            "ok": ok,
            "message": message,
            "details": details,
        }
        result = {
            "test_id": TEST_ID,
            "scenario_id": data["scenario_id"],
            "scenario_title": data["scenario_title"],
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "score_0_100": score,
            "level_hint": "B2" if ok else "B1",
            "payload": {
                "catalog_answers": catalog_answers,
                "resource_results": resource_results,
                "advice_answers": advice_answers,
                "advice_results": advice_results,
                "repository_plan": plan_answers,
                "repository_results": plan_results,
            },
            "checks": [
                {
                    "check_id": "relational_catalog_protocol",
                    "label": "Aplica un instrumento relacional con valoraciones coherentes",
                    "passed": protocol_ok,
                    "weight": 50,
                    "evidence": json.dumps(catalog_answers, ensure_ascii=False),
                },
                {
                    "check_id": "reasoned_search_advice",
                    "label": "Asesora sobre búsqueda, verificación y reformulación",
                    "passed": advice_ok,
                    "weight": 30,
                    "evidence": json.dumps(advice_answers, ensure_ascii=False),
                },
                {
                    "check_id": "proactive_repository_plan",
                    "label": "Diseña un plan proactivo de actualización y difusión",
                    "passed": repositories_ok,
                    "weight": 20,
                    "evidence": json.dumps(plan_answers, ensure_ascii=False),
                },
            ],
            "notes": [message, *details],
        }
        saved_path = save_result(result)
        state["responses"]["p04_saved_path"] = str(saved_path)
        refresh_view()

    feedback_details = state["feedback"]["p04"].get("details", [])
    content = ft.Column(
        controls=[
            ft.Text(data["intro"], size=15, weight=ft.FontWeight.W_600),
            section_title(protocol["title"]),
            ft.Text(protocol["description"], size=14),
            ft.Column(controls=catalog_cards, spacing=10),
            ft.Divider(height=24),
            section_title(advice["title"]),
            ft.Text(advice["description"], size=14),
            ft.Column(controls=advice_cards, spacing=10),
            ft.Divider(height=24),
            section_title(repositories["title"]),
            ft.Text(repositories["description"], size=14),
            ft.Column(controls=plan_cards, spacing=10),
            *(
                [
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    "Qué debes revisar",
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color="#991B1B",
                                ),
                                *[
                                    ft.Text(f"• {detail}", size=13, color="#7F1D1D")
                                    for detail in feedback_details
                                ],
                            ],
                            spacing=6,
                        ),
                        bgcolor="#FEF2F2",
                        border=ft.border.all(1, "#FECACA"),
                        border_radius=12,
                        padding=14,
                    )
                ]
                if validated and feedback_details
                else []
            ),
            ft.ElevatedButton("Validar prueba", on_click=validate),
            build_result_box(state["feedback"]["p04"]),
        ],
        spacing=12,
    )
    return question_block(
        title=data["title"],
        statement=data["statement"],
        content=content,
    )
