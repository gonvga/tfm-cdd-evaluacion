import json
import re
import unicodedata
from datetime import datetime, timezone

import flet as ft

from core.paths import resource_path
from core.storage import save_result
from ui.components import checkbox_feedback, question_block


TEST_ID = "P07"
DATA_PATH = resource_path("data", "p07_comp22_b1.json")


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
    words = word_count(value)
    missing_groups = []
    for group in field.get("required_groups", []):
        if not any(normalize_text(term) in normalized for term in group):
            missing_groups.append(group)
    length_ok = (
        words >= field.get("minimum_words", 1)
        and words <= field.get("maximum_words", 10_000)
    )
    return {
        "ok": bool(normalized) and not missing_groups and length_ok,
        "words": words,
        "missing_groups": missing_groups,
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


def info_panel(title: str, lines: list[str], warning: bool = False) -> ft.Control:
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    title,
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color="#92400E" if warning else "#1E3A8A",
                ),
                *[
                    ft.Text(f"• {line}", size=13, color="#374151")
                    for line in lines
                ],
            ],
            spacing=6,
        ),
        bgcolor="#FFFBEB" if warning else "#EFF6FF",
        border=ft.border.all(1, "#FDE68A" if warning else "#BFDBFE"),
        border_radius=12,
        padding=14,
    )


def field_feedback(field: dict, value: str | None, validated: bool) -> ft.Control:
    if not validated:
        return ft.Container()
    result = evaluate_text(field, value)
    if result["ok"]:
        return inline_feedback(
            f"Campo suficientemente documentado ({result['words']} palabras).",
            True,
        )
    issues = []
    if not result["length_ok"]:
        issues.append(
            f"usa entre {field.get('minimum_words', 1)} y "
            f"{field.get('maximum_words', '∞')} palabras"
        )
    if result["missing_groups"]:
        issues.append(
            "faltan referencias a "
            + ", ".join("/".join(group) for group in result["missing_groups"])
        )
    return inline_feedback("Revisa el campo: " + "; ".join(issues) + ".", False)


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


def build_test_p07(state: dict, refresh_view) -> ft.Control:
    data = load_test_data()
    source = data["source"]
    operations = data["operations"]
    authoring = data["authoring"]
    license_data = data["license"]
    metadata = data["metadata"]
    saved = state["responses"].get("p07_answers", {})
    validated = state["feedback"]["p07"]["ok"] is not None

    saved_operations = saved.get("operations", {})
    operation_controls = {
        component["id"]: ft.Dropdown(
            label="Modificación aplicada",
            value=saved_operations.get(component["id"]),
            options=[
                ft.dropdown.Option(option)
                for option in component["options"]
            ],
        )
        for component in operations["components"]
    }

    saved_settings = set(saved.get("settings", []))
    setting_controls = {
        setting["id"]: ft.Checkbox(
            label=setting["label"],
            value=setting["id"] in saved_settings,
        )
        for setting in authoring["settings"]
    }
    export_control = ft.Dropdown(
        label=authoring["export"]["label"],
        value=saved.get("export"),
        options=[
            ft.dropdown.Option(option)
            for option in authoring["export"]["options"]
        ],
    )
    change_log = ft.TextField(
        label=data["change_log"]["label"],
        hint_text=data["change_log"]["hint"],
        value=saved.get("change_log", ""),
        multiline=True,
        min_lines=4,
        max_lines=7,
    )
    attribution = ft.TextField(
        label=license_data["attribution"]["label"],
        hint_text=license_data["attribution"]["hint"],
        value=saved.get("attribution", ""),
        multiline=True,
        min_lines=3,
        max_lines=5,
    )
    derivative_license = ft.Dropdown(
        label=license_data["derivative_license"]["label"],
        value=saved.get("derivative_license"),
        options=[
            ft.dropdown.Option(option)
            for option in license_data["derivative_license"]["options"]
        ],
    )
    saved_metadata = saved.get("metadata", {})
    metadata_controls = {
        field["id"]: ft.TextField(
            label=field["label"],
            hint_text=field["hint"],
            value=saved_metadata.get(field["id"], ""),
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        for field in metadata["fields"]
    }

    preview_controls = {
        component["id"]: ft.Text(
            saved_operations.get(component["id"]) or "Sin configurar",
            size=12,
            color="#374151",
        )
        for component in operations["components"]
    }

    def update_operation_preview(component_id: str):
        def handler(e):
            preview_controls[component_id].value = e.control.value or "Sin configurar"
            preview_controls[component_id].update()
        return handler

    for component_id, control in operation_controls.items():
        control.on_change = update_operation_preview(component_id)

    def collect_answers() -> dict:
        return {
            "operations": {
                component_id: control.value
                for component_id, control in operation_controls.items()
            },
            "settings": [
                setting_id
                for setting_id, control in setting_controls.items()
                if control.value
            ],
            "export": export_control.value,
            "change_log": change_log.value or "",
            "attribution": attribution.value or "",
            "derivative_license": derivative_license.value,
            "metadata": {
                field_id: control.value or ""
                for field_id, control in metadata_controls.items()
            },
        }

    def validate(e):
        answers = collect_answers()
        state["responses"]["p07_answers"] = answers

        operation_results = {
            component["id"]: (
                answers["operations"].get(component["id"])
                == component["expected"]
            )
            for component in operations["components"]
        }
        operations_correct = sum(operation_results.values())
        operations_ok = operations_correct == len(operation_results)
        operations_score = operations_correct * 7

        expected_settings = {
            setting["id"]
            for setting in authoring["settings"]
            if setting["expected"]
        }
        forbidden_settings = {
            setting["id"]
            for setting in authoring["settings"]
            if not setting["expected"]
        }
        selected_settings = set(answers["settings"])
        settings_ok = (
            expected_settings.issubset(selected_settings)
            and not selected_settings.intersection(forbidden_settings)
        )
        export_ok = answers["export"] == authoring["export"]["expected"]
        authoring_ok = settings_ok and export_ok
        authoring_score = (10 if settings_ok else 0) + (5 if export_ok else 0)

        change_result = evaluate_text(
            data["change_log"],
            answers["change_log"],
        )
        change_score = 10 if change_result["ok"] else 0

        attribution_result = evaluate_text(
            license_data["attribution"],
            answers["attribution"],
        )
        derivative_license_ok = (
            answers["derivative_license"]
            == license_data["derivative_license"]["expected"]
        )
        license_ok = attribution_result["ok"] and derivative_license_ok
        license_score = (
            (7 if attribution_result["ok"] else 0)
            + (3 if derivative_license_ok else 0)
        )

        metadata_results = {
            field["id"]: evaluate_text(
                field,
                answers["metadata"].get(field["id"]),
            )
            for field in metadata["fields"]
        }
        metadata_correct = sum(
            result["ok"] for result in metadata_results.values()
        )
        metadata_ok = metadata_correct >= metadata["minimum_correct"]
        metadata_score = metadata_correct * 6

        score = (
            operations_score
            + authoring_score
            + change_score
            + license_score
            + metadata_score
        )
        ok = (
            score >= 80
            and operations_ok
            and authoring_ok
            and change_result["ok"]
            and license_ok
            and metadata_ok
        )

        details = []
        if not operations_ok:
            failed = [
                component["label"]
                for component in operations["components"]
                if not operation_results[component["id"]]
            ]
            details.append(
                "Revisa las operaciones aplicadas a: " + ", ".join(failed) + "."
            )
        if not authoring_ok:
            details.append(
                "La configuración debe asegurar orden de lectura, teclado, foco visible, "
                "adaptación responsive y salida HTML5 editable."
            )
        if not change_result["ok"]:
            details.append(
                "El registro de cambios debe documentar estructura, audio o transcripción, "
                "teclado, retroalimentación y ampliación opcional."
            )
        if not license_ok:
            details.append(
                "Identifica la obra y su autoría, indica que se ha adaptado y selecciona "
                "CC BY-SA 4.0 como licencia de la nueva versión."
            )
        if not metadata_ok:
            details.append(
                f"Completa correctamente al menos {metadata['minimum_correct']} de los "
                f"{len(metadata['fields'])} metadatos."
            )

        message = data["feedback"]["success"] if ok else data["feedback"]["failure"]
        state["completed"]["p07"] = ok
        state["feedback"]["p07"] = {
            "ok": ok,
            "message": message,
            "details": details,
        }
        checks = [
            {
                "check_id": "component_adaptation",
                "label": "Aplica modificaciones didácticas, técnicas y de accesibilidad a los componentes",
                "passed": operations_ok,
                "weight": 35,
                "evidence": json.dumps(answers["operations"], ensure_ascii=False),
            },
            {
                "check_id": "authoring_configuration",
                "label": "Configura la herramienta y una publicación accesible",
                "passed": authoring_ok,
                "weight": 15,
                "evidence": json.dumps(
                    {
                        "settings": answers["settings"],
                        "export": answers["export"],
                    },
                    ensure_ascii=False,
                ),
            },
            {
                "check_id": "change_documentation",
                "label": "Documenta de forma autónoma los cambios realizados",
                "passed": change_result["ok"],
                "weight": 10,
                "evidence": answers["change_log"],
            },
            {
                "check_id": "compatible_license",
                "label": "Atribuye la obra original, declara los cambios y selecciona una licencia compatible",
                "passed": license_ok,
                "weight": 10,
                "evidence": answers["attribution"],
            },
            {
                "check_id": "authoring_metadata",
                "label": "Registra metadatos suficientes para reutilizar y mantener la obra",
                "passed": metadata_ok,
                "weight": 30,
                "evidence": json.dumps(answers["metadata"], ensure_ascii=False),
            },
        ]
        result = {
            "test_id": TEST_ID,
            "scenario_id": data["scenario_id"],
            "scenario_title": data["scenario_title"],
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "score_0_100": score,
            "level_hint": "B1" if ok else "A2",
            "payload": {
                "answers": answers,
                "operation_results": operation_results,
                "authoring_results": {
                    "settings": settings_ok,
                    "export": export_ok,
                },
                "change_log_result": change_result,
                "license_results": {
                    "attribution": attribution_result,
                    "derivative_license": derivative_license_ok,
                },
                "metadata_results": metadata_results,
            },
            "checks": checks,
            "notes": [message, *details],
        }
        saved_path = save_result(result)
        state["responses"]["p07_saved_path"] = str(saved_path)
        refresh_view()

    operation_cards = []
    for component in operations["components"]:
        selected = saved_operations.get(component["id"])
        item_ok = selected == component["expected"]
        operation_cards.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            component["label"],
                            size=15,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Container(
                            content=ft.Text(
                                f"Estado original: {component['current']}",
                                size=12,
                                color="#92400E",
                            ),
                            bgcolor="#FFFBEB",
                            border_radius=8,
                            padding=9,
                        ),
                        operation_controls[component["id"]],
                        *(
                            [
                                inline_feedback(
                                    (
                                        f"Modificación adecuada. {component['feedback']}"
                                        if item_ok
                                        else f"Revisa esta operación. {component['feedback']}"
                                    ),
                                    item_ok,
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
                padding=14,
            )
        )

    settings_rows = []
    for setting in authoring["settings"]:
        selected = setting["id"] in saved_settings
        expected = bool(setting["expected"])
        feedback_text, setting_ok = checkbox_feedback(
            selected,
            expected,
            (
                "Asegura orden de lectura, uso con teclado, foco visible o adaptación responsive."
                if expected
                else "Esta configuración introduce una barrera o reduce la accesibilidad."
            ),
        )
        settings_rows.append(
            ft.Column(
                controls=[
                    setting_controls[setting["id"]],
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

    settings_panel = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "Funciones aplicadas",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color="#1E3A8A",
                ),
                *settings_rows,
            ],
            spacing=8,
        ),
        bgcolor="#F8FAFC",
        border=ft.border.all(1, "#CBD5E1"),
        border_radius=12,
        padding=14,
    )

    preview = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "RESUMEN DE LA OBRA ADAPTADA",
                    size=10,
                    weight=ft.FontWeight.BOLD,
                    color="#1D4ED8",
                ),
                *[
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    component["label"],
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                preview_controls[component["id"]],
                            ],
                            spacing=3,
                        ),
                        bgcolor="#F8FAFC",
                        border=ft.border.all(1, "#E2E8F0"),
                        border_radius=8,
                        padding=9,
                    )
                    for component in operations["components"]
                ],
            ],
            spacing=8,
        ),
        bgcolor="#FFFFFF",
        border=ft.border.all(1, "#CBD5E1"),
        border_radius=14,
        padding=14,
    )

    feedback_details = state["feedback"]["p07"].get("details", [])
    content = ft.Column(
        controls=[
            ft.Text(data["intro"], size=15, weight=ft.FontWeight.W_600),
            info_panel(data["context"]["title"], data["context"]["lines"]),
            ft.Divider(height=20, color="#E5E7EB"),
            ft.Container(
                content=ft.Column(
                    controls=[
                        section_header(
                            ft.Icons.DESCRIPTION_OUTLINED,
                            source["title"],
                            "Revisa todos sus componentes antes de modificarla.",
                        ),
                        ft.Text(
                            source["heading"],
                            size=21,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(source["intro"], size=14, color="#374151"),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        "CONTENIDO ESENCIAL QUE DEBE CONSERVARSE",
                                        size=10,
                                        weight=ft.FontWeight.BOLD,
                                        color="#1D4ED8",
                                    ),
                                    *[
                                        ft.Text(f"• {line}", size=13)
                                        for line in source["key_content"]
                                    ],
                                ],
                                spacing=5,
                            ),
                            bgcolor="#EFF6FF",
                            border_radius=10,
                            padding=12,
                        ),
                        info_panel(
                            "Otros componentes originales",
                            [
                                source["audio"],
                                source["activity"],
                                source["extension"],
                                f"Licencia: {source['license']}.",
                                f"Metadatos: {source['metadata_status']}",
                            ],
                            warning=True,
                        ),
                    ],
                    spacing=11,
                ),
                bgcolor="#F8FAFC",
                border=ft.border.all(1, "#CBD5E1"),
                border_radius=14,
                padding=16,
            ),
            ft.Divider(height=20, color="#E5E7EB"),
            ft.ResponsiveRow(
                controls=[
                    ft.Container(
                        col={"xs": 12, "lg": 8},
                        content=ft.Column(
                            controls=[
                                section_header(
                                    ft.Icons.EDIT_NOTE,
                                    operations["title"],
                                    operations["description"],
                                ),
                                ft.ResponsiveRow(
                                    controls=operation_cards,
                                    spacing=10,
                                    run_spacing=10,
                                ),
                            ],
                            spacing=10,
                        ),
                    ),
                    ft.Container(
                        col={"xs": 12, "lg": 4},
                        content=ft.Column(
                            controls=[
                                section_header(
                                    ft.Icons.PREVIEW_OUTLINED,
                                    "Vista de cambios",
                                    "Se actualiza al elegir cada operación.",
                                ),
                                preview,
                            ],
                            spacing=10,
                        ),
                    ),
                ],
                spacing=18,
                run_spacing=18,
            ),
            ft.Divider(height=20, color="#E5E7EB"),
            section_header(
                ft.Icons.TUNE,
                authoring["title"],
                "Configura funciones globales de edición y publicación.",
            ),
            settings_panel,
            ft.Container(
                content=export_control,
                bgcolor="#FFFFFF",
                border=ft.border.all(1, "#E5E7EB"),
                border_radius=12,
                padding=12,
            ),
            *(
                [
                    inline_feedback(
                        (
                            "Formato de publicación adecuado."
                            if saved.get("export") == authoring["export"]["expected"]
                            else f"Formato esperado: {authoring['export']['expected']}."
                        ),
                        saved.get("export") == authoring["export"]["expected"],
                    )
                ]
                if validated
                else []
            ),
            ft.Divider(height=20, color="#E5E7EB"),
            section_header(
                ft.Icons.HISTORY_EDU_OUTLINED,
                data["change_log"]["title"],
                "La herramienta guardará esta información junto a la nueva versión.",
            ),
            change_log,
            field_feedback(
                data["change_log"],
                saved.get("change_log"),
                validated,
            ),
            ft.Divider(height=20, color="#E5E7EB"),
            section_header(
                ft.Icons.COPYRIGHT,
                license_data["title"],
                "Registra la procedencia y las condiciones de reutilización.",
            ),
            attribution,
            field_feedback(
                license_data["attribution"],
                saved.get("attribution"),
                validated,
            ),
            derivative_license,
            *(
                [
                    inline_feedback(
                        (
                            "Licencia compatible con CompartirIgual."
                            if saved.get("derivative_license")
                            == license_data["derivative_license"]["expected"]
                            else "La obra derivada debe mantener CC BY-SA 4.0."
                        ),
                        saved.get("derivative_license")
                        == license_data["derivative_license"]["expected"],
                    )
                ]
                if validated
                else []
            ),
            ft.Divider(height=20, color="#E5E7EB"),
            section_header(
                ft.Icons.DATA_OBJECT,
                metadata["title"],
                "Completa información para localizar, mantener y reutilizar la ficha.",
            ),
            *[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            metadata_controls[field["id"]],
                            field_feedback(
                                field,
                                saved_metadata.get(field["id"]),
                                validated,
                            ),
                        ],
                        spacing=5,
                    ),
                    bgcolor="#F8FAFC",
                    border=ft.border.all(1, "#E5E7EB"),
                    border_radius=12,
                    padding=12,
                )
                for field in metadata["fields"]
            ],
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
                                    ft.Text(
                                        f"• {detail}",
                                        size=13,
                                        color="#7F1D1D",
                                    )
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
            build_result_box(state["feedback"]["p07"]),
        ],
        spacing=14,
    )

    return question_block(
        title=data["title"],
        statement=data["statement"],
        content=content,
    )
