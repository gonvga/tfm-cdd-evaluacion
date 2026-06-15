import json
import re
import unicodedata
from datetime import datetime, timezone

import flet as ft

from core.storage import save_result
from core.paths import resource_path
from ui.components import checkbox_feedback, question_block


TEST_ID = "P06"
DATA_PATH = resource_path("data", "p06_comp22_a2.json")


def load_test_data() -> dict:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def normalize_text(value: str | None) -> str:
    text = unicodedata.normalize("NFD", (value or "").strip().lower())
    return "".join(char for char in text if unicodedata.category(char) != "Mn")


def word_count(value: str | None) -> int:
    return len(re.findall(r"\b[\wáéíóúüñ]+\b", value or "", flags=re.IGNORECASE))


def text_matches(field: dict, value: str | None) -> bool:
    normalized = normalize_text(value)
    words = word_count(value)
    required = [normalize_text(term) for term in field.get("required_terms", [])]
    forbidden = [normalize_text(term) for term in field.get("forbidden_values", [])]
    return (
        bool(normalized)
        and all(term in normalized for term in required)
        and not any(normalized == term for term in forbidden)
        and words >= field.get("minimum_words", 1)
        and words <= field.get("maximum_words", 10_000)
    )


def section_header(icon: str, title: str, subtitle: str) -> ft.Control:
    return ft.Row(
        controls=[
            ft.Container(
                content=ft.Icon(icon, size=20, color="#1D4ED8"),
                bgcolor="#DBEAFE",
                border_radius=10,
                padding=8,
            ),
            ft.Column(
                controls=[
                    ft.Text(title, size=17, weight=ft.FontWeight.BOLD, color="#111827"),
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
                ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color="#1E3A8A"),
                *[ft.Text(f"• {line}", size=13, color="#374151") for line in lines],
            ],
            spacing=6,
        ),
        bgcolor="#EFF6FF",
        border=ft.border.all(1, "#BFDBFE"),
        border_radius=12,
        padding=14,
    )


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


def selection_feedback(
    selected: str | None,
    expected: str,
    validated: bool,
) -> ft.Control:
    if not validated:
        return ft.Container()
    ok = selected == expected
    return inline_feedback(
        "Correcta."
        if ok
        else f"Incorrecta. Debías seleccionar: {expected}.",
        ok,
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


def build_test_p06(state: dict, refresh_view) -> ft.Control:
    data = load_test_data()
    source = data["source"]
    editor = data["editor"]
    configuration = data["configuration"]
    reference = data["reference"]
    saved = state["responses"].get("p06_answers", {})
    validated = state["feedback"]["p06"]["ok"] is not None

    heading_input = ft.TextField(
        label=editor["heading"]["label"],
        hint_text=editor["heading"]["hint"],
        value=saved.get("heading", ""),
    )
    body_input = ft.TextField(
        label=editor["body"]["label"],
        hint_text=editor["body"]["hint"],
        value=saved.get("body", ""),
        multiline=True,
        min_lines=3,
        max_lines=5,
    )
    alt_input = ft.TextField(
        label=editor["alt_text"]["label"],
        hint_text=editor["alt_text"]["hint"],
        value=saved.get("alt_text", ""),
        multiline=True,
        min_lines=2,
        max_lines=4,
    )

    config_controls = {
        field["id"]: ft.Dropdown(
            label=field["label"],
            value=saved.get(field["id"]),
            options=[ft.dropdown.Option(option) for option in field["options"]],
            col={"xs": 12, "md": 6},
        )
        for field in configuration["fields"]
    }
    saved_actions = saved.get("accessibility_actions", [])
    action_controls = {
        option["id"]: ft.Checkbox(
            label=option["label"],
            value=option["id"] in saved_actions,
        )
        for option in configuration["accessibility_actions"]["options"]
    }
    saved_reference = saved.get("reference", {})
    reference_target = ft.Dropdown(
        label=reference["target"]["label"],
        value=saved_reference.get("target"),
        options=[
            ft.dropdown.Option(option)
            for option in reference["target"]["options"]
        ],
    )
    reference_mode = ft.Dropdown(
        label=reference["mode"]["label"],
        value=saved_reference.get("mode"),
        options=[
            ft.dropdown.Option(option)
            for option in reference["mode"]["options"]
        ],
    )
    saved_corrections = saved_reference.get("corrections", [])
    reference_corrections = {
        option["id"]: ft.Checkbox(
            label=option["label"],
            value=option["id"] in saved_corrections,
        )
        for option in reference["corrections"]
    }

    heading_saved_ok = text_matches(editor["heading"], saved.get("heading"))
    body_saved_ok = text_matches(editor["body"], saved.get("body"))
    alt_saved_ok = text_matches(editor["alt_text"], saved.get("alt_text"))

    config_cards = []
    for field in configuration["fields"]:
        control = config_controls[field["id"]]
        control.col = None
        config_cards.append(
            ft.Container(
                col={"xs": 12, "md": 6},
                content=ft.Column(
                    controls=[
                        control,
                        selection_feedback(
                            saved.get(field["id"]),
                            field["expected"],
                            validated,
                        ),
                    ],
                    spacing=6,
                ),
            )
        )

    action_rows = []
    for option in configuration["accessibility_actions"]["options"]:
        selected = option["id"] in saved_actions
        feedback_text, option_ok = checkbox_feedback(
            selected,
            bool(option["expected"]),
            (
                "Este ajuste responde a las necesidades del grupo y del recurso."
                if option["expected"]
                else "Este ajuste introduce una barrera o no responde al objetivo."
            ),
        )
        action_rows.append(
            ft.Column(
                controls=[
                    action_controls[option["id"]],
                    *(
                        [inline_feedback(feedback_text, option_ok)]
                        if validated
                        else []
                    ),
                ],
                spacing=4,
            )
        )

    correction_rows = []
    for option in reference["corrections"]:
        selected = option["id"] in saved_corrections
        feedback_text, option_ok = checkbox_feedback(
            selected,
            bool(option["expected"]),
            (
                "Corrige la atribución o recupera condiciones del recurso original."
                if option["expected"]
                else "La adaptación no permite atribuirse la obra original ni cambiar su licencia."
            ),
        )
        correction_rows.append(
            ft.Column(
                controls=[
                    reference_corrections[option["id"]],
                    *(
                        [inline_feedback(feedback_text, option_ok)]
                        if validated
                        else []
                    ),
                ],
                spacing=4,
            )
        )

    def validate(e):
        answers = {
            "heading": heading_input.value or "",
            "body": body_input.value or "",
            "alt_text": alt_input.value or "",
            **{field_id: control.value for field_id, control in config_controls.items()},
            "accessibility_actions": [
                option_id
                for option_id, control in action_controls.items()
                if control.value
            ],
            "reference": {
                "target": reference_target.value,
                "mode": reference_mode.value,
                "corrections": [
                    option_id
                    for option_id, control in reference_corrections.items()
                    if control.value
                ],
            },
        }
        state["responses"]["p06_answers"] = answers

        heading_ok = text_matches(editor["heading"], answers["heading"])
        body_ok = text_matches(editor["body"], answers["body"])
        alt_ok = text_matches(editor["alt_text"], answers["alt_text"])
        content_ok = heading_ok and body_ok and alt_ok
        config_results = {
            field["id"]: answers.get(field["id"]) == field["expected"]
            for field in configuration["fields"]
        }
        config_ok = all(config_results.values())
        expected_actions = {
            option["id"]
            for option in configuration["accessibility_actions"]["options"]
            if option["expected"]
        }
        selected_actions = set(answers["accessibility_actions"])
        accessibility_ok = selected_actions == expected_actions
        expected_corrections = {
            option["id"]
            for option in reference["corrections"]
            if option["expected"]
        }
        selected_corrections = set(answers["reference"]["corrections"])
        reference_results = {
            "target": answers["reference"]["target"] == reference["target"]["expected"],
            "mode": answers["reference"]["mode"] == reference["mode"]["expected"],
            "corrections": selected_corrections == expected_corrections,
        }
        reference_ok = all(reference_results.values())

        checks = [
            {
                "check_id": "guided_content_edit",
                "label": "Adapta título, explicación y texto alternativo",
                "passed": content_ok,
                "weight": 35,
                "evidence": answers["body"],
            },
            {
                "check_id": "authoring_configuration",
                "label": "Configura herramienta, estructura, navegación y exportación",
                "passed": config_ok,
                "weight": 30,
                "evidence": ", ".join(
                    str(answers.get(field["id"])) for field in configuration["fields"]
                ),
            },
            {
                "check_id": "accessibility_settings",
                "label": "Aplica ajustes didácticos y de accesibilidad",
                "passed": accessibility_ok,
                "weight": 15,
                "evidence": ", ".join(answers["accessibility_actions"]),
            },
            {
                "check_id": "reference_tool",
                "label": "Completa la referencia mediante la herramienta de autor",
                "passed": reference_ok,
                "weight": 20,
                "evidence": json.dumps(answers["reference"], ensure_ascii=False),
            },
        ]
        score = sum(check["weight"] for check in checks if check["passed"])
        ok = score >= 80 and config_ok and reference_ok

        details = []
        if not content_ok:
            details.append(
                "Revisa que el título identifique el ciclo del agua, que la explicación "
                "mantenga evaporación, condensación y precipitación, y que el texto "
                "alternativo comunique el proceso con suficiente precisión."
            )
        if not config_ok:
            details.append(
                "Consulta el manual para usar la herramienta institucional, una estructura "
                "guiada, navegación visible y un formato admitido por Moodle."
            )
        if not accessibility_ok:
            details.append(
                "Selecciona únicamente los ajustes que mejoran estructura, percepción y "
                "comprobación del aprendizaje."
            )
        if not reference_ok:
            details.append(
                "Revisa qué obra debe atribuirse y qué metadatos o condiciones de uso "
                "deben corregirse en la referencia importada."
            )

        message = data["feedback"]["success"] if ok else data["feedback"]["failure"]
        state["completed"]["p06"] = ok
        state["feedback"]["p06"] = {
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
            "level_hint": "A2" if ok else "A1",
            "payload": {
                "answers": answers,
                "content_checks": {
                    "heading": heading_ok,
                    "body": body_ok,
                    "alt_text": alt_ok,
                },
                "configuration_checks": config_results,
                "reference_checks": reference_results,
            },
            "checks": checks,
            "notes": [message, *details],
        }
        saved_path = save_result(result)
        state["responses"]["p06_saved_path"] = str(saved_path)
        refresh_view()

    feedback_details = state["feedback"]["p06"].get("details", [])
    content = ft.Column(
        controls=[
            ft.Text(data["intro"], size=15, weight=ft.FontWeight.W_600),
            info_panel(data["guide"]["title"], data["guide"]["lines"]),
            ft.Container(
                content=ft.Column(
                    controls=[
                        section_header(
                            ft.Icons.DESCRIPTION_OUTLINED,
                            source["title"],
                            "Analiza el material antes de editarlo.",
                        ),
                        ft.ResponsiveRow(
                            controls=[
                                ft.Container(
                                    col={"xs": 12, "md": 5},
                                    content=ft.Image(
                                        src=source["image_src"],
                                        fit="cover",
                                    ),
                                    aspect_ratio=16 / 9,
                                    alignment=ft.Alignment.CENTER,
                                    border=ft.border.all(1, "#E5E7EB"),
                                    border_radius=10,
                                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                                ),
                                ft.Container(
                                    col={"xs": 12, "md": 7},
                                    content=ft.Column(
                                        controls=[
                                            ft.Text(
                                                source["original_heading"],
                                                size=18,
                                                weight=ft.FontWeight.BOLD,
                                                color="#111827",
                                            ),
                                            ft.Container(
                                                content=ft.Column(
                                                    controls=[
                                                        ft.Text(
                                                            "EXPLICACIÓN ACTUAL",
                                                            size=10,
                                                            weight=ft.FontWeight.BOLD,
                                                            color="#1D4ED8",
                                                        ),
                                                        ft.Text(
                                                            source["original_text"],
                                                            size=16,
                                                            weight=ft.FontWeight.W_500,
                                                            color="#111827",
                                                        ),
                                                    ],
                                                    spacing=6,
                                                ),
                                                bgcolor="#FFFFFF",
                                                border=ft.border.all(2, "#93C5FD"),
                                                border_radius=10,
                                                padding=16,
                                            ),
                                            ft.Container(
                                                content=ft.Row(
                                                    controls=[
                                                        ft.Icon(
                                                            ft.Icons.WARNING_AMBER_ROUNDED,
                                                            size=18,
                                                            color="#B45309",
                                                        ),
                                                        ft.Column(
                                                            controls=[
                                                                ft.Text(
                                                                    "Texto alternativo actual",
                                                                    size=11,
                                                                    weight=ft.FontWeight.BOLD,
                                                                    color="#92400E",
                                                                ),
                                                                ft.Text(
                                                                    f"“{source['current_alt']}” · Debe sustituirse por una descripción útil.",
                                                                    size=12,
                                                                    color="#78350F",
                                                                ),
                                                            ],
                                                            spacing=2,
                                                            expand=True,
                                                        ),
                                                    ],
                                                    spacing=8,
                                                    vertical_alignment=ft.CrossAxisAlignment.START,
                                                ),
                                                bgcolor="#FFFBEB",
                                                border=ft.border.all(1, "#FDE68A"),
                                                border_radius=10,
                                                padding=10,
                                            ),
                                        ],
                                        spacing=12,
                                    ),
                                ),
                            ],
                            spacing=14,
                            run_spacing=14,
                        ),
                    ],
                    spacing=10,
                ),
                bgcolor="#F8FAFC",
                border=ft.border.all(1, "#CBD5E1"),
                border_radius=14,
                padding=16,
            ),
            section_header(
                ft.Icons.EDIT_NOTE,
                editor["title"],
                "Escribe directamente la versión que verá el alumnado.",
            ),
            heading_input,
            *(
                [
                    inline_feedback(
                        (
                            "Título adecuado: identifica con claridad el ciclo del agua."
                            if heading_saved_ok
                            else "Revisa el título: debe identificar claramente el ciclo del agua."
                        ),
                        heading_saved_ok,
                    )
                ]
                if validated
                else []
            ),
            body_input,
            *(
                [
                    inline_feedback(
                        (
                            "Explicación adecuada: conserva las tres fases con una extensión apropiada."
                            if body_saved_ok
                            else "Revisa la explicación: debe incluir evaporación, condensación y precipitación en 18-70 palabras."
                        ),
                        body_saved_ok,
                    )
                ]
                if validated
                else []
            ),
            alt_input,
            *(
                [
                    inline_feedback(
                        (
                            "Texto alternativo adecuado: comunica el proceso representado."
                            if alt_saved_ok
                            else "Revisa el texto alternativo: debe explicar evaporación, formación de nubes y precipitación en 12-45 palabras."
                        ),
                        alt_saved_ok,
                    )
                ]
                if validated
                else []
            ),
            section_header(
                ft.Icons.TUNE,
                configuration["title"],
                "Aplica los ajustes indicados por el centro y el manual.",
            ),
            ft.ResponsiveRow(
                controls=config_cards,
                spacing=10,
                run_spacing=10,
            ),
            ft.Text(
                configuration["accessibility_actions"]["label"],
                size=14,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Column(controls=action_rows, spacing=8),
            section_header(
                ft.Icons.FORMAT_QUOTE,
                reference["title"],
                reference["description"],
            ),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "Referencia importada por la herramienta",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color="#92400E",
                        ),
                        ft.Text(
                            reference["imported_reference"],
                            size=13,
                            italic=True,
                            color="#78350F",
                        ),
                    ],
                    spacing=5,
                ),
                bgcolor="#FFFBEB",
                border=ft.border.all(1, "#FDE68A"),
                border_radius=12,
                padding=14,
            ),
            reference_target,
            selection_feedback(
                saved_reference.get("target"),
                reference["target"]["expected"],
                validated,
            ),
            reference_mode,
            selection_feedback(
                saved_reference.get("mode"),
                reference["mode"]["expected"],
                validated,
            ),
            ft.Text(
                "Correcciones que aplicarás antes de insertar la referencia",
                size=14,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Column(controls=correction_rows, spacing=8),
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
            build_result_box(state["feedback"]["p06"]),
        ],
        spacing=14,
    )

    return question_block(
        title=data["title"],
        statement=data["statement"],
        content=content,
    )
