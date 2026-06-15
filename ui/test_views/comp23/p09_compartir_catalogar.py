import json
from datetime import datetime

import flet as ft

from core.storage import save_result
from core.paths import resource_path
from ui.components import checkbox_feedback, question_block


TEST_ID = "P09"
DATA_PATH = resource_path("data", "p09_comp23_a1.json")


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


def get_expected_id(options: list[dict]) -> str | None:
    return next((option["id"] for option in options if option["expected"]), None)


def get_selected_ids(checkboxes: dict[str, ft.Checkbox]) -> list[str]:
    return [key for key, checkbox in checkboxes.items() if checkbox.value]


def build_radio_option(option: dict, validated: bool) -> ft.Control:
    option_ok = bool(option["expected"])
    bgcolor, border_color = (
        feedback_colors(option_ok) if validated else ("#F9FAFB", "#E5E7EB")
    )
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Radio(value=option["id"], label=option["label"]),
                *(
                    [
                        inline_feedback(
                            f"{'Correcta' if option_ok else 'Incorrecta'}. {option['feedback']}",
                            option_ok,
                        )
                    ]
                    if validated
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


def build_radio_group(options: list[dict], selected_id: str | None, validated: bool) -> ft.RadioGroup:
    return ft.RadioGroup(
        value=selected_id,
        content=ft.Column(
            controls=[build_radio_option(option, validated) for option in options],
            spacing=8,
        ),
    )


def build_checkbox_cards(
    options: list[dict],
    saved_ids: list[str],
    validated: bool,
) -> tuple[dict[str, ft.Checkbox], list[ft.Control]]:
    checkboxes = {}
    cards = []

    for option in options:
        checkbox = ft.Checkbox(value=option["id"] in saved_ids)
        checkboxes[option["id"]] = checkbox
        selected = option["id"] in saved_ids
        feedback_text, passed = checkbox_feedback(
            selected,
            bool(option["expected"]),
            option["feedback"],
        )
        bgcolor, border_color = feedback_colors(passed) if validated else ("#F9FAFB", "#E5E7EB")

        cards.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                checkbox,
                                ft.Text(option["label"], size=14, weight=ft.FontWeight.W_600, expand=True),
                            ],
                            spacing=6,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                        ),
                        *(
                            [
                                inline_feedback(
                                    feedback_text,
                                    passed,
                                )
                            ]
                            if validated
                            else []
                        ),
                    ],
                    spacing=8,
                ),
                col={"xs": 12, "md": 6},
                bgcolor=bgcolor,
                border=ft.border.all(1, border_color),
                border_radius=10,
                padding=12,
            )
        )

    return checkboxes, cards


def build_test_p09(state: dict, refresh_view) -> ft.Control:
    test_data = load_test_data()
    validated = state["feedback"]["p09"]["ok"] is not None
    saved_environment = state["responses"].get("p09_environment", [])
    saved_rights = state["responses"].get("p09_rights", [])
    saved_permissions = state["responses"].get("p09_permissions", {})
    saved_metadata = state["responses"].get("p09_metadata", {})

    environment_checkboxes, environment_cards = build_checkbox_cards(
        test_data["environment"]["options"],
        saved_environment,
        validated,
    )
    rights_checkboxes, rights_cards = build_checkbox_cards(
        test_data["rights"]["options"],
        saved_rights,
        validated,
    )
    permission_controls = {
        field["id"]: build_radio_group(
            field["options"],
            saved_permissions.get(field["id"]),
            validated,
        )
        for field in test_data["permissions"]["fields"]
    }
    metadata_controls = {
        field["id"]: build_radio_group(
            field["options"],
            saved_metadata.get(field["id"]),
            validated,
        )
        for field in test_data["metadata"]["fields"]
    }

    def persist_form():
        state["responses"]["p09_environment"] = get_selected_ids(environment_checkboxes)
        state["responses"]["p09_rights"] = get_selected_ids(rights_checkboxes)
        state["responses"]["p09_permissions"] = {
            field_id: control.value for field_id, control in permission_controls.items()
        }
        state["responses"]["p09_metadata"] = {
            field_id: control.value for field_id, control in metadata_controls.items()
        }

    def validate(e):
        persist_form()
        selected_environment = state["responses"].get("p09_environment", [])
        selected_rights = state["responses"].get("p09_rights", [])
        selected_permissions = state["responses"].get("p09_permissions", {})
        selected_metadata = state["responses"].get("p09_metadata", {})

        expected_environment = [
            option["id"] for option in test_data["environment"]["options"] if option["expected"]
        ]
        environment_ok = set(selected_environment) == set(expected_environment)
        environment_points = round(
            sum(
                1
                for option in test_data["environment"]["options"]
                if (option["id"] in selected_environment) == bool(option["expected"])
            )
            / len(test_data["environment"]["options"])
            * 24
        )

        permission_checks = []
        permission_points = 0
        expected_permissions = {}
        for field in test_data["permissions"]["fields"]:
            expected = get_expected_id(field["options"])
            selected = selected_permissions.get(field["id"])
            field_ok = selected == expected
            expected_permissions[field["id"]] = expected
            permission_points += field["weight"] if field_ok else 0
            permission_checks.append(
                {
                    "check_id": f"permission_{field['id']}",
                    "label": field["label"],
                    "passed": field_ok,
                    "weight": field["weight"],
                    "evidence": str(selected),
                }
            )
        permissions_ok = all(check["passed"] for check in permission_checks)

        expected_rights = [
            option["id"] for option in test_data["rights"]["options"] if option["expected"]
        ]
        rights_ok = set(selected_rights) == set(expected_rights)
        rights_points = round(
            sum(
                1
                for option in test_data["rights"]["options"]
                if (option["id"] in selected_rights) == bool(option["expected"])
            )
            / len(test_data["rights"]["options"])
            * 20
        )

        metadata_checks = []
        metadata_points = 0
        expected_metadata = {}
        for field in test_data["metadata"]["fields"]:
            expected = get_expected_id(field["options"])
            selected = selected_metadata.get(field["id"])
            field_ok = selected == expected
            expected_metadata[field["id"]] = expected
            metadata_points += field["weight"] if field_ok else 0
            metadata_checks.append(
                {
                    "check_id": f"metadata_{field['id']}",
                    "label": field["label"],
                    "passed": field_ok,
                    "weight": field["weight"],
                    "evidence": str(selected),
                }
            )
        metadata_ok = all(check["passed"] for check in metadata_checks)

        score = environment_points + permission_points + rights_points + metadata_points
        ok = score >= 80 and environment_ok and permissions_ok and rights_ok and metadata_ok
        message = test_data["feedback"]["success"] if ok else test_data["feedback"]["failure"]
        state["completed"]["p09"] = ok
        state["feedback"]["p09"] = {"ok": ok, "message": message}

        result = {
            "test_id": TEST_ID,
            "scenario_id": test_data["scenario_id"],
            "scenario_title": test_data["scenario_title"],
            "timestamp_utc": datetime.utcnow().isoformat(),
            "score_0_100": score,
            "level_hint": "A1" if ok else "sin nivel acreditado",
            "payload": {
                "selected_environment": selected_environment,
                "expected_environment": expected_environment,
                "selected_permissions": selected_permissions,
                "expected_permissions": expected_permissions,
                "selected_rights": selected_rights,
                "expected_rights": expected_rights,
                "selected_metadata": selected_metadata,
                "expected_metadata": expected_metadata,
            },
            "checks": [
                {
                    "check_id": "safe_environment",
                    "label": "Selecciona entornos digitales seguros para compartir contenidos educativos",
                    "passed": environment_ok,
                    "weight": 24,
                    "evidence": ", ".join(selected_environment),
                },
                *permission_checks,
                {
                    "check_id": "copyright_licenses",
                    "label": "Aplica autoria, propiedad intelectual y condiciones de licencia",
                    "passed": rights_ok,
                    "weight": 20,
                    "evidence": ", ".join(selected_rights),
                },
                *metadata_checks,
            ],
            "notes": [message],
        }

        saved_path = save_result(result)
        state["responses"]["p09_saved_path"] = str(saved_path)
        refresh_view()

    permission_sections = []
    for field in test_data["permissions"]["fields"]:
        permission_sections.append(
            ft.Column(
                controls=[
                    ft.Text(field["label"], size=15, weight=ft.FontWeight.BOLD),
                    permission_controls[field["id"]],
                ],
                spacing=8,
            )
        )

    metadata_sections = []
    for field in test_data["metadata"]["fields"]:
        metadata_sections.append(
            ft.Column(
                controls=[
                    ft.Text(field["label"], size=15, weight=ft.FontWeight.BOLD),
                    metadata_controls[field["id"]],
                ],
                spacing=8,
            )
        )

    content = ft.Column(
        controls=[
            ft.Text(test_data["intro"], size=15, weight=ft.FontWeight.W_600),
            section_title(test_data["environment"]["title"]),
            ft.Text(test_data["environment"]["description"], size=14),
            ft.ResponsiveRow(controls=environment_cards, spacing=8, run_spacing=8),
            ft.Divider(height=24),
            section_title(test_data["permissions"]["title"]),
            ft.Text(test_data["permissions"]["description"], size=14),
            *permission_sections,
            ft.Divider(height=24),
            section_title(test_data["rights"]["title"]),
            ft.Text(test_data["rights"]["description"], size=14),
            ft.ResponsiveRow(controls=rights_cards, spacing=8, run_spacing=8),
            ft.Divider(height=24),
            section_title(test_data["metadata"]["title"]),
            ft.Text(test_data["metadata"]["description"], size=14),
            *metadata_sections,
            ft.Container(height=8),
            ft.ElevatedButton("Validar prueba", on_click=validate),
            build_result_box(state["feedback"]["p09"]),
        ],
        spacing=12,
    )

    return question_block(
        title=test_data["title"],
        statement=test_data["statement"],
        content=content,
    )
