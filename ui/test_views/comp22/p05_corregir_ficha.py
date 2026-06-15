import json
import re
from datetime import datetime
from pathlib import Path

import flet as ft

from core.storage import save_result
from ui.components import checkbox_feedback, question_block


TEST_ID = "P05"
DATA_PATH = Path("data/p05_comp22_a1.json")


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


def build_choice_card(
    option: dict,
    selected_id: str | None,
    validated: bool,
    text_key: str,
) -> ft.Control:
    selected = selected_id == option["id"]
    option_ok = bool(option["expected"])
    show_feedback = validated
    if show_feedback:
        bgcolor, border_color = feedback_colors(option_ok)
    else:
        bgcolor, border_color = "#F9FAFB", "#E5E7EB"

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Radio(value=option["id"], label=option[text_key]),
                *(
                    [
                        inline_feedback(
                            f"{'Correcta' if option_ok else 'Incorrecta'}. {option['feedback']}",
                            option_ok,
                        )
                    ]
                    if show_feedback
                    else []
                ),
            ],
            spacing=6,
        ),
        bgcolor=bgcolor,
        border=ft.border.all(1, border_color),
        border_radius=10,
        padding=12,
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


def get_selected_ids(checkboxes: dict) -> list[str]:
    return [key for key, checkbox in checkboxes.items() if checkbox.value]


def validate_patterns(text: str, patterns: list[dict]) -> dict:
    missing = [
        pattern["id"]
        for pattern in patterns
        if not re.search(pattern["regex"], text or "")
    ]
    return {"ok": not missing, "missing": missing}


def build_test_p05(state: dict, refresh_view) -> ft.Control:
    test_data = load_test_data()
    license_data = test_data["license"]
    accessibility = test_data["accessibility"]
    content_data = test_data["content"]
    tools = test_data["tools"]

    saved_license = state["responses"].get("p05_license")
    saved_apa = state["responses"].get("p05_apa_option")
    saved_accessibility = state["responses"].get("p05_accessibility", [])
    saved_alt_text = state["responses"].get("p05_alt_text_option")
    saved_content = state["responses"].get("p05_content_option")
    saved_tools = state["responses"].get("p05_tools", {})
    validated = state["feedback"]["p05"]["ok"] is not None

    expected_license_ids = [
        option["id"] for option in license_data["options"] if option["expected"]
    ]
    license_options = [
        ft.dropdown.Option(option["id"], option["label"])
        for option in license_data["options"]
    ]
    license_dropdown = ft.Dropdown(
        label="Licencia",
        value=saved_license,
        options=license_options,
        width=280,
    )
    license_feedback = ft.Container()
    if validated:
        license_ok = saved_license in expected_license_ids
        selected_option = next(
            (option for option in license_data["options"] if option["id"] == saved_license),
            None,
        )
        expected_labels = [
            option["label"] for option in license_data["options"] if option["expected"]
        ]
        if selected_option:
            license_message = (
                f"{'Correcta' if license_ok else 'Incorrecta'}. "
                f"{selected_option['feedback']}"
            )
        else:
            license_message = "Sin respuesta."
        if not license_ok:
            license_message += f" Correcta: {', '.join(expected_labels)}."
        license_feedback = inline_feedback(
            license_message,
            license_ok,
        )

    apa_radio = ft.RadioGroup(
        value=saved_apa,
        content=ft.Column(
            controls=[
                build_choice_card(option, saved_apa, validated, "text")
                for option in license_data["apa_options"]
            ],
            spacing=8,
        ),
    )
    apa_feedback = ft.Container()
    if validated:
        selected_option = next(
            (option for option in license_data["apa_options"] if option["id"] == saved_apa),
            None,
        )
        if not selected_option:
            apa_feedback = inline_feedback(
                "Sin respuesta. La referencia correcta aparece en verde.",
                False,
            )

    accessibility_checkboxes = {}
    accessibility_cards = []
    accessibility_feedback_rows = []
    expected_accessibility = [
        option["id"] for option in accessibility["options"] if option["expected"]
    ]
    for option in accessibility["options"]:
        checkbox = ft.Checkbox(value=option["id"] in saved_accessibility)
        accessibility_checkboxes[option["id"]] = checkbox
        selected = option["id"] in saved_accessibility
        feedback_text, option_ok = checkbox_feedback(
            selected,
            bool(option["expected"]),
            option["feedback"],
        )
        if validated:
            accessibility_feedback_rows.append(
                (
                    option_ok,
                    f"{option['label']}: {feedback_text}",
                )
            )
        accessibility_cards.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                checkbox,
                                ft.Column(
                                    controls=[
                                        ft.Text(option["label"], size=15, weight=ft.FontWeight.BOLD),
                                    ],
                                    spacing=4,
                                    expand=True,
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.START,
                        ),
                        *(
                            [
                                inline_feedback(feedback_text, option_ok)
                            ]
                            if validated
                            else []
                        ),
                    ],
                    spacing=8,
                ),
                col={"xs": 12, "md": 6},
                bgcolor=feedback_colors(option_ok)[0] if validated else "#F9FAFB",
                border=ft.border.all(1, feedback_colors(option_ok)[1] if validated else "#E5E7EB"),
                border_radius=10,
                padding=12,
            )
        )

    alt_text_radio = ft.RadioGroup(
        value=saved_alt_text,
        content=ft.Column(
            controls=[
                build_choice_card(option, saved_alt_text, validated, "text")
                for option in accessibility["alt_text_options"]
            ],
            spacing=8,
        ),
    )
    image_panel = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "Imagen en la ficha.",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(
                    content=ft.Image(
                        src="assets/p05/alumnado.png",
                        width=680,
                        height=380,
                        fit="contain",
                    ),
                    alignment=ft.Alignment.CENTER,
                    height=420,
                    bgcolor="#E5E7EB",
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=12,
                    padding=16,
                ),
                ft.Text(
                    "¿Cuál sería el mejor texto alternativo para esta imagen?",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                ),
            ],
            spacing=8,
        ),
        bgcolor="#F3F4F6",
        border=ft.border.all(1, ft.Colors.GREY_300),
        border_radius=12,
        padding=12,
    )
    alt_feedback = ft.Container()
    if validated:
        selected_option = next(
            (option for option in accessibility["alt_text_options"] if option["id"] == saved_alt_text),
            None,
        )
        if not selected_option:
            alt_feedback = inline_feedback(
                "Sin respuesta. El texto alternativo correcto aparece en verde.",
                False,
            )

    expected_content = next(
        option["id"] for option in content_data["options"] if option["expected"]
    )
    content_radio = ft.RadioGroup(
        value=saved_content,
        content=ft.Column(
            controls=[
                build_choice_card(option, saved_content, validated, "text")
                for option in content_data["options"]
            ],
            spacing=8,
        ),
    )
    content_feedback = ft.Container()
    if validated and saved_content is None:
        content_feedback = inline_feedback(
            "Sin respuesta. La version correcta aparece en verde.",
            False,
        )

    tool_controls = {}
    tool_cards = []
    tool_feedback_rows = []
    for task in tools["tasks"]:
        dropdown = ft.Dropdown(
            label="Herramienta",
            value=saved_tools.get(task["id"]),
            options=[ft.dropdown.Option(option) for option in task["options"]],
            width=260,
        )
        tool_controls[task["id"]] = dropdown
        tool_ok = saved_tools.get(task["id"]) == task["expected"]
        if validated:
            tool_feedback_rows.append(
                (
                    tool_ok,
                    f"{task['label']}: {task['expected']}",
                )
            )
        tool_cards.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(task["label"], size=15, weight=ft.FontWeight.BOLD),
                        dropdown,
                        *(
                            [
                                inline_feedback(
                                    (
                                        "Correcta."
                                        if tool_ok
                                        else f"Incorrecta. Correcta: {task['expected']}."
                                    ),
                                    tool_ok,
                                )
                            ]
                            if validated
                            else []
                        ),
                    ],
                    spacing=8,
                ),
                bgcolor=feedback_colors(tool_ok)[0] if validated else "#F9FAFB",
                border=ft.border.all(1, feedback_colors(tool_ok)[1] if validated else "#E5E7EB"),
                border_radius=10,
                padding=12,
            )
        )

    def validate(e):
        selected_license = license_dropdown.value
        selected_apa = apa_radio.value
        selected_accessibility = get_selected_ids(accessibility_checkboxes)
        selected_alt_text = alt_text_radio.value
        selected_content = content_radio.value
        selected_tools = {
            task_id: dropdown.value
            for task_id, dropdown in tool_controls.items()
        }

        state["responses"]["p05_license"] = selected_license
        state["responses"]["p05_apa_option"] = selected_apa
        state["responses"]["p05_accessibility"] = selected_accessibility
        state["responses"]["p05_alt_text_option"] = selected_alt_text
        state["responses"]["p05_content_option"] = selected_content
        state["responses"]["p05_tools"] = selected_tools

        license_ok = selected_license in expected_license_ids
        apa_option = next(
            (option for option in license_data["apa_options"] if option["id"] == selected_apa),
            None,
        )
        apa_ok = bool(apa_option and apa_option["expected"])
        accessibility_actions_ok = set(selected_accessibility) == set(expected_accessibility)
        alt_option = next(
            (option for option in accessibility["alt_text_options"] if option["id"] == selected_alt_text),
            None,
        )
        alt_ok = bool(alt_option and alt_option["expected"])
        accessibility_ok = accessibility_actions_ok and alt_ok
        content_ok = selected_content == expected_content
        tools_ok = all(
            selected_tools[task["id"]] == task["expected"]
            for task in tools["tasks"]
        )

        score = 0
        score += 20 if license_ok else 0
        score += 20 if apa_ok else 0
        score += 20 if accessibility_ok else 10 if accessibility_actions_ok or alt_ok else 0
        score += 20 if content_ok else 0
        score += 20 if tools_ok else round(
            sum(
                1
                for task in tools["tasks"]
                if selected_tools[task["id"]] == task["expected"]
            )
            / len(tools["tasks"])
            * 20
        )

        ok = score >= 80
        state["completed"]["p05"] = ok
        message = test_data["feedback"]["success"] if ok else test_data["feedback"]["failure"]
        state["feedback"]["p05"] = {"ok": ok, "message": message}

        result = {
            "test_id": TEST_ID,
            "scenario_id": test_data["scenario_id"],
            "scenario_title": test_data["scenario_title"],
            "timestamp_utc": datetime.utcnow().isoformat(),
            "score_0_100": score,
            "level_hint": "A1" if ok else "A0",
            "payload": {
                "selected_license": selected_license,
                "expected_license_ids": expected_license_ids,
                "selected_apa_option": selected_apa,
                "expected_apa_option": next(
                    (option["id"] for option in license_data["apa_options"] if option["expected"]),
                    None,
                ),
                "selected_accessibility": selected_accessibility,
                "expected_accessibility": expected_accessibility,
                "selected_alt_text_option": selected_alt_text,
                "expected_alt_text_option": next(
                    (option["id"] for option in accessibility["alt_text_options"] if option["expected"]),
                    None,
                ),
                "selected_content_option": selected_content,
                "expected_content_option": expected_content,
                "selected_tools": selected_tools,
            },
            "checks": [
                {
                    "check_id": "license_for_adaptation",
                    "label": "Selecciona una licencia que permita reutilización y adaptación",
                    "passed": license_ok,
                    "weight": 20,
                    "evidence": str(selected_license),
                },
                {
                    "check_id": "apa_reference",
                    "label": "Selecciona la referencia APA básica correcta",
                    "passed": apa_ok,
                    "weight": 20,
                    "evidence": str(selected_apa),
                },
                {
                    "check_id": "accessible_document_actions",
                    "label": "Selecciona acciones de accesibilidad y texto alternativo adecuados",
                    "passed": accessibility_ok,
                    "weight": 20,
                    "evidence": ", ".join(selected_accessibility + [selected_alt_text] if selected_alt_text else selected_accessibility),
                },
                {
                    "check_id": "didactic_rewrite",
                    "label": "Selecciona la versión más adecuada para 2º de ESO",
                    "passed": content_ok,
                    "weight": 20,
                    "evidence": str(selected_content),
                },
                {
                    "check_id": "authoring_tools",
                    "label": "Selecciona herramientas de autor adecuadas",
                    "passed": tools_ok,
                    "weight": 20,
                    "evidence": str(selected_tools),
                },
            ],
            "notes": [message],
        }

        saved_path = save_result(result)
        state["responses"]["p05_saved_path"] = str(saved_path)
        refresh_view()

    content = ft.Column(
        controls=[
            ft.Text(test_data["intro"], size=15, weight=ft.FontWeight.W_600),
            build_info_panel(test_data["source"]["title"], test_data["source"]["lines"]),
            section_title(license_data["title"]),
            ft.Text(license_data["description"], size=14),
            license_dropdown,
            license_feedback,
            apa_radio,
            apa_feedback,
            ft.Divider(height=24),
            section_title(accessibility["title"]),
            ft.Text(accessibility["description"], size=14),
            ft.ResponsiveRow(controls=accessibility_cards, spacing=8, run_spacing=8),
            feedback_panel("Corrección de accesibilidad", accessibility_feedback_rows),
            image_panel,
            alt_text_radio,
            alt_feedback,
            ft.Divider(height=24),
            section_title(content_data["title"]),
            ft.Text(content_data["description"], size=14),
            content_radio,
            content_feedback,
            ft.Divider(height=24),
            section_title(tools["title"]),
            ft.Text(tools["description"], size=14),
            ft.Column(controls=tool_cards, spacing=10),
            feedback_panel("Corrección de herramientas", tool_feedback_rows),
            ft.Container(height=8),
            ft.ElevatedButton("Validar prueba", on_click=validate),
            build_result_box(state["feedback"]["p05"]),
        ],
        spacing=12,
    )

    return question_block(
        title=test_data["title"],
        statement=test_data["statement"],
        content=content,
    )
