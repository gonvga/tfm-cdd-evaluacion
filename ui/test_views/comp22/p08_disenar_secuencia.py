import json
import re
import unicodedata
from datetime import datetime, timezone

import flet as ft

from core.paths import resource_path
from core.storage import save_result
from ui.components import checkbox_feedback, question_block


TEST_ID = "P08"
DATA_PATH = resource_path("data", "p08_comp22_b2.json")


def load_test_data() -> dict:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def normalize_text(value: str | None) -> str:
    text = unicodedata.normalize("NFD", (value or "").strip().lower())
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    return re.sub(r"\s+", " ", text)


def word_count(value: str | None) -> int:
    return len(re.findall(r"\b[\wáéíóúüñ]+\b", value or "", flags=re.IGNORECASE))


def evaluate_text(field: dict, value: str | None) -> dict:
    normalized = normalize_text(value)
    missing = [
        group
        for group in field.get("required_groups", [])
        if not any(normalize_text(term) in normalized for term in group)
    ]
    words = word_count(value)
    length_ok = (
        words >= field.get("minimum_words", 1)
        and words <= field.get("maximum_words", 10_000)
    )
    return {
        "ok": bool(normalized) and not missing and length_ok,
        "missing": missing,
        "words": words,
        "length_ok": length_ok,
    }


def inline_feedback(text: str, ok: bool) -> ft.Control:
    bgcolor, color = (
        ("#DCFCE7", "#166534")
        if ok
        else ("#FEE2E2", "#991B1B")
    )
    return ft.Container(
        content=ft.Text(text, size=12, color=color),
        bgcolor=bgcolor,
        border=ft.border.all(1, color),
        border_radius=8,
        padding=9,
    )


def section_header(icon: str, title: str, subtitle: str) -> ft.Control:
    return ft.Row(
        controls=[
            ft.Container(
                content=ft.Icon(icon, size=21, color="#1D4ED8"),
                bgcolor="#DBEAFE",
                border_radius=10,
                padding=8,
            ),
            ft.Column(
                controls=[
                    ft.Text(
                        title,
                        size=17,
                        weight=ft.FontWeight.BOLD,
                        color="#111827",
                    ),
                    ft.Text(subtitle, size=12, color="#6B7280"),
                ],
                spacing=2,
                expand=True,
            ),
        ],
        spacing=10,
    )


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


def field_feedback(field: dict, value: str | None, validated: bool) -> ft.Control:
    if not validated:
        return ft.Container()
    result = evaluate_text(field, value)
    if result["ok"]:
        return inline_feedback(
            f"Evidencia suficiente ({result['words']} palabras).",
            True,
        )
    issues = []
    if not result["length_ok"]:
        issues.append(
            f"extensión {field.get('minimum_words', 1)}-"
            f"{field.get('maximum_words', '∞')} palabras"
        )
    if result["missing"]:
        issues.append(
            "faltan " + ", ".join("/".join(group) for group in result["missing"])
        )
    return inline_feedback("Revisa: " + "; ".join(issues) + ".", False)


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


def find_resource(resources: list[dict], resource_id: str) -> dict | None:
    return next(
        (resource for resource in resources if resource["id"] == resource_id),
        None,
    )


def evaluate_sequence(bank: dict, selected_ids: list[str]) -> dict:
    selected = set(selected_ids)
    required = set(bank["required_resources"])
    inappropriate = set(bank["inappropriate_resources"])
    missing = sorted(required - selected)
    wrong = sorted(selected & inappropriate)
    selection_ok = not missing and not wrong
    positions = {resource_id: index for index, resource_id in enumerate(selected_ids)}
    order_results = []
    for rule in bank["order_rules"]:
        passed = (
            rule["before"] in positions
            and rule["after"] in positions
            and positions[rule["before"]] < positions[rule["after"]]
        )
        order_results.append({**rule, "passed": passed})
    order_ok = all(item["passed"] for item in order_results)

    selected_resources = [
        find_resource(bank["resources"], resource_id)
        for resource_id in selected_ids
    ]
    selected_resources = [item for item in selected_resources if item]
    formats = {resource["format"] for resource in selected_resources}
    sources = {resource["source"] for resource in selected_resources}
    diversity_ok = len(formats) >= 4 and len(sources) >= 4
    return {
        "selection_ok": selection_ok,
        "missing": missing,
        "wrong": wrong,
        "order_results": order_results,
        "order_ok": order_ok,
        "formats": sorted(formats),
        "sources": sorted(sources),
        "diversity_ok": diversity_ok,
    }


def build_test_p08(state: dict, refresh_view) -> ft.Control:
    data = load_test_data()
    bank = data["resource_bank"]
    resources = bank["resources"]
    saved = state["responses"].get("p08_answers", {})
    validated = state["feedback"]["p08"]["ok"] is not None
    sequence = list(saved.get("sequence", []))

    modification_controls = {
        field["id"]: ft.TextField(
            label=field["label"],
            hint_text=field["hint"],
            value=saved.get("modifications", {}).get(field["id"], ""),
            multiline=True,
            min_lines=3,
            max_lines=5,
        )
        for field in data["modification_plan"]["fields"]
    }
    own_controls = {
        field["id"]: ft.TextField(
            label=field["label"],
            hint_text=field["hint"],
            value=saved.get("own_elements", {}).get(field["id"], ""),
            multiline=True,
            min_lines=3,
            max_lines=6,
        )
        for field in data["own_elements"]["fields"]
    }
    saved_safety = set(saved.get("safety_settings", []))
    safety_controls = {
        setting["id"]: ft.Checkbox(
            label=setting["label"],
            value=setting["id"] in saved_safety,
        )
        for setting in data["safety"]["settings"]
    }
    recovery_control = ft.TextField(
        label=data["safety"]["recovery"]["label"],
        hint_text=data["safety"]["recovery"]["hint"],
        value=saved.get("recovery", ""),
        multiline=True,
        min_lines=3,
        max_lines=5,
    )
    criteria_control = ft.TextField(
        label=data["evaluation_protocol"]["criteria"]["label"],
        hint_text=data["evaluation_protocol"]["criteria"]["hint"],
        value=saved.get("evaluation_criteria", ""),
        multiline=True,
        min_lines=4,
        max_lines=7,
    )
    follow_up_control = ft.TextField(
        label=data["evaluation_protocol"]["follow_up"]["label"],
        hint_text=data["evaluation_protocol"]["follow_up"]["hint"],
        value=saved.get("evaluation_follow_up", ""),
        multiline=True,
        min_lines=3,
        max_lines=6,
    )
    export_controls = {
        field["id"]: ft.Dropdown(
            label=field["label"],
            value=saved.get("export", {}).get(field["id"]),
            options=[ft.dropdown.Option(option) for option in field["options"]],
        )
        for field in data["export"]["fields"]
    }
    metadata_control = ft.TextField(
        label=data["export"]["metadata"]["label"],
        hint_text=data["export"]["metadata"]["hint"],
        value=saved.get("package_metadata", ""),
        multiline=True,
        min_lines=3,
        max_lines=6,
    )

    def collect_answers() -> dict:
        return {
            "sequence": list(sequence),
            "modifications": {
                field_id: control.value or ""
                for field_id, control in modification_controls.items()
            },
            "own_elements": {
                field_id: control.value or ""
                for field_id, control in own_controls.items()
            },
            "safety_settings": [
                setting_id
                for setting_id, control in safety_controls.items()
                if control.value
            ],
            "recovery": recovery_control.value or "",
            "evaluation_criteria": criteria_control.value or "",
            "evaluation_follow_up": follow_up_control.value or "",
            "export": {
                field_id: control.value
                for field_id, control in export_controls.items()
            },
            "package_metadata": metadata_control.value or "",
        }

    def persist():
        state["responses"]["p08_answers"] = collect_answers()

    def add_resource(resource_id: str):
        if resource_id not in sequence:
            sequence.append(resource_id)
            persist()
            update_sequence()

    def remove_resource(resource_id: str):
        if resource_id in sequence:
            sequence.remove(resource_id)
            persist()
            update_sequence()

    def move_resource(index: int, delta: int):
        target = index + delta
        if target < 0 or target >= len(sequence):
            return
        sequence[index], sequence[target] = sequence[target], sequence[index]
        persist()
        update_sequence()

    def validate(e):
        answers = collect_answers()
        state["responses"]["p08_answers"] = answers
        sequence_result = evaluate_sequence(bank, answers["sequence"])
        integration_score = (
            (15 if sequence_result["selection_ok"] else 0)
            + (5 if sequence_result["order_ok"] else 0)
            + (10 if sequence_result["diversity_ok"] else 0)
        )
        integration_ok = (
            sequence_result["selection_ok"]
            and sequence_result["order_ok"]
            and sequence_result["diversity_ok"]
        )

        modification_results = {
            field["id"]: evaluate_text(
                field,
                answers["modifications"].get(field["id"]),
            )
            for field in data["modification_plan"]["fields"]
        }
        modifications_ok = all(
            result["ok"] for result in modification_results.values()
        )
        modification_score = sum(
            5 for result in modification_results.values() if result["ok"]
        )

        own_results = {
            field["id"]: evaluate_text(
                field,
                answers["own_elements"].get(field["id"]),
            )
            for field in data["own_elements"]["fields"]
        }
        own_ok = all(result["ok"] for result in own_results.values())
        own_score = sum(5 for result in own_results.values() if result["ok"])

        expected_safety = {
            setting["id"]
            for setting in data["safety"]["settings"]
            if setting["expected"]
        }
        forbidden_safety = {
            setting["id"]
            for setting in data["safety"]["settings"]
            if not setting["expected"]
        }
        selected_safety = set(answers["safety_settings"])
        safety_settings_ok = (
            expected_safety.issubset(selected_safety)
            and not selected_safety.intersection(forbidden_safety)
        )
        recovery_result = evaluate_text(
            data["safety"]["recovery"],
            answers["recovery"],
        )
        safety_ok = safety_settings_ok and recovery_result["ok"]
        safety_score = (
            (6 if safety_settings_ok else 0)
            + (4 if recovery_result["ok"] else 0)
        )

        criteria_result = evaluate_text(
            data["evaluation_protocol"]["criteria"],
            answers["evaluation_criteria"],
        )
        follow_up_result = evaluate_text(
            data["evaluation_protocol"]["follow_up"],
            answers["evaluation_follow_up"],
        )
        evaluation_ok = criteria_result["ok"] and follow_up_result["ok"]
        evaluation_score = (
            (9 if criteria_result["ok"] else 0)
            + (6 if follow_up_result["ok"] else 0)
        )

        export_results = {
            field["id"]: answers["export"].get(field["id"]) == field["expected"]
            for field in data["export"]["fields"]
        }
        metadata_result = evaluate_text(
            data["export"]["metadata"],
            answers["package_metadata"],
        )
        export_ok = all(export_results.values()) and metadata_result["ok"]
        export_score = (
            sum(3 for passed in export_results.values() if passed)
            + (3 if metadata_result["ok"] else 0)
        )

        score = (
            integration_score
            + modification_score
            + own_score
            + safety_score
            + evaluation_score
            + export_score
        )
        ok = (
            score >= 80
            and integration_ok
            and modifications_ok
            and own_ok
            and safety_ok
            and evaluation_ok
            and export_ok
        )

        details = []
        if not integration_ok:
            details.append(
                "La secuencia debe integrar los cuatro recursos reutilizables, descartar "
                "los incompatibles, mantener las relaciones didácticas y combinar cuatro fuentes y formatos."
            )
        if not modifications_ok:
            details.append(
                "Concreta las modificaciones didácticas, técnicas y de accesibilidad "
                "de la infografía, el vídeo y el simulador."
            )
        if not own_ok:
            details.append(
                "Completa el reto, el apoyo guiado y el producto final con rúbrica propia."
            )
        if not safety_ok:
            details.append(
                "Configura permisos, historial, copias de hitos, responsabilidades y recuperación."
            )
        if not evaluation_ok:
            details.append(
                "El procedimiento debe evaluar antes de integrar y registrar resultados después del uso."
            )
        if not export_ok:
            details.append(
                "Revisa SCORM 1.2, tratamiento de recursos, validación accesible, curso de prueba y metadatos."
            )

        message = data["feedback"]["success"] if ok else data["feedback"]["failure"]
        state["completed"]["p08"] = ok
        state["feedback"]["p08"] = {
            "ok": ok,
            "message": message,
            "details": details,
        }
        checks = [
            {
                "check_id": "integrated_learning_sequence",
                "label": "Integra fuentes y formatos diversos en una secuencia coherente",
                "passed": integration_ok,
                "weight": 30,
                "evidence": json.dumps(answers["sequence"], ensure_ascii=False),
            },
            {
                "check_id": "content_modification",
                "label": "Documenta modificaciones didácticas, técnicas y accesibles",
                "passed": modifications_ok,
                "weight": 15,
                "evidence": json.dumps(answers["modifications"], ensure_ascii=False),
            },
            {
                "check_id": "own_elements",
                "label": "Crea elementos propios que estructuran y adaptan la unidad",
                "passed": own_ok,
                "weight": 15,
                "evidence": json.dumps(answers["own_elements"], ensure_ascii=False),
            },
            {
                "check_id": "shared_editing_safety",
                "label": "Aplica un protocolo de edición compartida segura",
                "passed": safety_ok,
                "weight": 10,
                "evidence": json.dumps(
                    {
                        "settings": answers["safety_settings"],
                        "recovery": answers["recovery"],
                    },
                    ensure_ascii=False,
                ),
            },
            {
                "check_id": "systematic_evaluation",
                "label": "Aplica evaluación previa y seguimiento posterior",
                "passed": evaluation_ok,
                "weight": 15,
                "evidence": answers["evaluation_criteria"],
            },
            {
                "check_id": "accessible_packaging",
                "label": "Empaqueta, valida y despliega la unidad en Moodle",
                "passed": export_ok,
                "weight": 15,
                "evidence": json.dumps(answers["export"], ensure_ascii=False),
            },
        ]
        result = {
            "test_id": TEST_ID,
            "scenario_id": data["scenario_id"],
            "scenario_title": data["scenario_title"],
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "score_0_100": score,
            "level_hint": "B2" if ok else "B1",
            "payload": {
                "answers": answers,
                "sequence_result": sequence_result,
                "modification_results": modification_results,
                "own_results": own_results,
                "safety_results": {
                    "settings": safety_settings_ok,
                    "recovery": recovery_result,
                },
                "evaluation_results": {
                    "criteria": criteria_result,
                    "follow_up": follow_up_result,
                },
                "export_results": {
                    **export_results,
                    "metadata": metadata_result,
                },
            },
            "checks": checks,
            "notes": [message, *details],
        }
        saved_path = save_result(result)
        state["responses"]["p08_saved_path"] = str(saved_path)
        refresh_view()

    def resource_card(resource: dict) -> ft.Control:
        selected = resource["id"] in sequence
        expected = resource["id"] in bank["required_resources"]
        feedback_text, selection_ok = checkbox_feedback(
            selected,
            expected,
            resource["feedback"],
        )
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(
                                    {
                                        "Página HTML": ft.Icons.ARTICLE_OUTLINED,
                                        "SVG editable": ft.Icons.INSERT_CHART_OUTLINED,
                                        "Vídeo MP4": ft.Icons.PLAY_CIRCLE_OUTLINE,
                                        "HTML5": ft.Icons.TOUCH_APP_OUTLINED,
                                        "PDF bloqueado": ft.Icons.LOCK_OUTLINED,
                                        "Iframe bloqueado": ft.Icons.BLOCK_OUTLINED,
                                    }.get(resource["format"], ft.Icons.DESCRIPTION_OUTLINED),
                                    color="#1D4ED8",
                                    size=23,
                                ),
                                bgcolor="#DBEAFE",
                                border_radius=10,
                                padding=8,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        resource["title"],
                                        size=15,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        f"{resource['source']} · {resource['format']}",
                                        size=11,
                                        color="#6B7280",
                                    ),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                        ],
                        spacing=9,
                    ),
                    ft.Text(
                        f"Licencia: {resource['license']}",
                        size=12,
                        color="#374151",
                    ),
                    ft.Text(
                        f"Accesibilidad: {resource['accessibility']}",
                        size=12,
                        color="#374151",
                    ),
                    ft.Text(resource["use"], size=12, color="#4B5563"),
                    ft.Row(
                        controls=[
                            ft.ElevatedButton(
                                "Añadir",
                                on_click=lambda e, rid=resource["id"]: add_resource(rid),
                            ),
                            ft.OutlinedButton(
                                "Quitar",
                                on_click=lambda e, rid=resource["id"]: remove_resource(rid),
                            ),
                        ],
                        spacing=8,
                    ),
                    *(
                        [
                            inline_feedback(
                                feedback_text,
                                selection_ok,
                            )
                        ]
                        if validated
                        else []
                    ),
                ],
                spacing=8,
            ),
            col={"xs": 12, "md": 6},
            bgcolor="#FFFFFF",
            border=ft.border.all(1, "#E5E7EB"),
            border_radius=12,
            padding=13,
        )

    def sequence_card(resource_id: str, index: int) -> ft.Control:
        resource = find_resource(resources, resource_id)
        if not resource:
            return ft.Container()
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(
                            str(index + 1),
                            size=13,
                            weight=ft.FontWeight.BOLD,
                            color="#1E40AF",
                        ),
                        width=30,
                        height=30,
                        alignment=ft.Alignment.CENTER,
                        bgcolor="#DBEAFE",
                        border_radius=999,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                resource["title"],
                                size=13,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                f"{resource['format']} · {resource['source']}",
                                size=11,
                                color="#6B7280",
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.KEYBOARD_ARROW_UP,
                        on_click=lambda e, i=index: move_resource(i, -1),
                        disabled=index == 0,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.KEYBOARD_ARROW_DOWN,
                        on_click=lambda e, i=index: move_resource(i, 1),
                        disabled=index == len(sequence) - 1,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        on_click=lambda e, rid=resource_id: remove_resource(rid),
                    ),
                ],
                spacing=6,
            ),
            bgcolor="#F8FAFC",
            border=ft.border.all(1, "#CBD5E1"),
            border_radius=10,
            padding=9,
        )

    def sequence_items() -> list[ft.Control]:
        if not sequence:
            return [
                ft.Container(
                    content=ft.Text(
                        "Añade recursos desde la biblioteca y ordénalos.",
                        size=13,
                        color="#6B7280",
                    ),
                    bgcolor="#F8FAFC",
                    border_radius=10,
                    padding=13,
                )
            ]
        return [
            sequence_card(resource_id, index)
            for index, resource_id in enumerate(sequence)
        ]

    sequence_column = ft.Column(controls=sequence_items(), spacing=8)

    def update_sequence():
        sequence_column.controls = sequence_items()
        sequence_column.update()

    safety_rows = []
    for setting in data["safety"]["settings"]:
        selected = setting["id"] in saved_safety
        expected = bool(setting["expected"])
        feedback_text, setting_ok = checkbox_feedback(
            selected,
            expected,
            (
                "Ayuda a mantener permisos, historial, copias, responsabilidades o recuperación."
                if expected
                else "Esta opción aumenta el riesgo de pérdida o reduce el control compartido."
            ),
        )
        safety_rows.append(
            ft.Column(
                controls=[
                    safety_controls[setting["id"]],
                    *(
                        [
                            inline_feedback(
                                feedback_text,
                                setting_ok,
                            )
                        ]
                        if validated
                        else []
                    ),
                ],
                spacing=4,
            )
        )

    feedback_details = state["feedback"]["p08"].get("details", [])
    content = ft.Column(
        controls=[
            ft.Text(data["intro"], size=15, weight=ft.FontWeight.W_600),
            info_panel(data["classroom"]["title"], data["classroom"]["lines"]),
            ft.Divider(height=22),
            section_header(
                ft.Icons.ACCOUNT_TREE_OUTLINED,
                bank["title"],
                bank["description"],
            ),
            ft.ResponsiveRow(
                controls=[
                    ft.Container(
                        col={"xs": 12, "lg": 8},
                        content=ft.ResponsiveRow(
                            controls=[resource_card(resource) for resource in resources],
                            spacing=8,
                            run_spacing=8,
                        ),
                    ),
                    ft.Container(
                        col={"xs": 12, "lg": 4},
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    "Secuencia integrada",
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                sequence_column,
                            ],
                            spacing=9,
                        ),
                    ),
                ],
                spacing=16,
                run_spacing=16,
            ),
            ft.Divider(height=22),
            section_header(
                ft.Icons.EDIT_NOTE,
                data["modification_plan"]["title"],
                data["modification_plan"]["description"],
            ),
            *[
                ft.Column(
                    controls=[
                        modification_controls[field["id"]],
                        field_feedback(
                            field,
                            saved.get("modifications", {}).get(field["id"]),
                            validated,
                        ),
                    ],
                    spacing=5,
                )
                for field in data["modification_plan"]["fields"]
            ],
            ft.Divider(height=22),
            section_header(
                ft.Icons.ADD_BOX_OUTLINED,
                data["own_elements"]["title"],
                data["own_elements"]["description"],
            ),
            *[
                ft.Column(
                    controls=[
                        own_controls[field["id"]],
                        field_feedback(
                            field,
                            saved.get("own_elements", {}).get(field["id"]),
                            validated,
                        ),
                    ],
                    spacing=5,
                )
                for field in data["own_elements"]["fields"]
            ],
            ft.Divider(height=22),
            section_header(
                ft.Icons.SECURITY_OUTLINED,
                data["safety"]["title"],
                data["safety"]["description"],
            ),
            ft.Container(
                content=ft.Column(controls=safety_rows, spacing=7),
                bgcolor="#F8FAFC",
                border=ft.border.all(1, "#CBD5E1"),
                border_radius=12,
                padding=14,
            ),
            recovery_control,
            field_feedback(
                data["safety"]["recovery"],
                saved.get("recovery"),
                validated,
            ),
            ft.Divider(height=22),
            section_header(
                ft.Icons.FACT_CHECK_OUTLINED,
                data["evaluation_protocol"]["title"],
                data["evaluation_protocol"]["description"],
            ),
            criteria_control,
            field_feedback(
                data["evaluation_protocol"]["criteria"],
                saved.get("evaluation_criteria"),
                validated,
            ),
            follow_up_control,
            field_feedback(
                data["evaluation_protocol"]["follow_up"],
                saved.get("evaluation_follow_up"),
                validated,
            ),
            ft.Divider(height=22),
            section_header(
                ft.Icons.INVENTORY_2_OUTLINED,
                data["export"]["title"],
                "Configura el paquete y su comprobación real en la plataforma.",
            ),
            *[
                ft.Column(
                    controls=[
                        export_controls[field["id"]],
                        *(
                            [
                                inline_feedback(
                                    (
                                        "Configuración correcta."
                                        if saved.get("export", {}).get(field["id"])
                                        == field["expected"]
                                        else f"Configuración esperada: {field['expected']}."
                                    ),
                                    saved.get("export", {}).get(field["id"])
                                    == field["expected"],
                                )
                            ]
                            if validated
                            else []
                        ),
                    ],
                    spacing=5,
                )
                for field in data["export"]["fields"]
            ],
            metadata_control,
            field_feedback(
                data["export"]["metadata"],
                saved.get("package_metadata"),
                validated,
            ),
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
            build_result_box(state["feedback"]["p08"]),
        ],
        spacing=13,
    )
    return question_block(
        title=data["title"],
        statement=data["statement"],
        content=content,
    )
