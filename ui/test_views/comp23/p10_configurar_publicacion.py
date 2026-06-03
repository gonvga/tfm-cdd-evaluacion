import json
from datetime import datetime
from pathlib import Path

import flet as ft

from core.storage import save_result
from ui.components import question_block


TEST_ID = "P10"
DATA_PATH = Path("data/p10_comp23_a2.json")


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


def info_panel(title: str, lines: list[str], bgcolor: str = "#EFF6FF") -> ft.Control:
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(title, size=15, weight=ft.FontWeight.BOLD),
                *[ft.Text(line, size=13, color=ft.Colors.GREY_700) for line in lines],
            ],
            spacing=5,
        ),
        bgcolor=bgcolor,
        border=ft.border.all(1, "#DBEAFE"),
        border_radius=12,
        padding=14,
    )


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
        passed = selected == bool(option["expected"])
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
                                    f"{'Correcta' if passed else 'Revisar'}. {option['feedback']}",
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


def build_field_sections(
    fields: list[dict],
    controls: dict[str, ft.RadioGroup],
) -> list[ft.Control]:
    return [
        ft.Column(
            controls=[
                ft.Text(field["label"], size=15, weight=ft.FontWeight.BOLD),
                controls[field["id"]],
            ],
            spacing=8,
        )
        for field in fields
    ]


def evaluate_radio_fields(
    fields: list[dict],
    selected_values: dict,
    prefix: str,
) -> tuple[bool, int, dict, list[dict]]:
    checks = []
    points = 0
    expected_values = {}

    for field in fields:
        expected = get_expected_id(field["options"])
        selected = selected_values.get(field["id"])
        field_ok = selected == expected
        expected_values[field["id"]] = expected
        points += field["weight"] if field_ok else 0
        checks.append(
            {
                "check_id": f"{prefix}_{field['id']}",
                "label": field["label"],
                "passed": field_ok,
                "weight": field["weight"],
                "evidence": str(selected),
            }
        )

    return all(check["passed"] for check in checks), points, expected_values, checks


def build_test_p10(state: dict, refresh_view) -> ft.Control:
    test_data = load_test_data()
    validated = state["feedback"]["p10"]["ok"] is not None
    saved_management = state["responses"].get("p10_management", [])
    saved_permissions = state["responses"].get("p10_permissions", {})
    saved_cataloging = state["responses"].get("p10_cataloging", {})
    saved_package = state["responses"].get("p10_package", {})

    management_checkboxes, management_cards = build_checkbox_cards(
        test_data["management"]["options"],
        saved_management,
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
    cataloging_controls = {
        field["id"]: build_radio_group(
            field["options"],
            saved_cataloging.get(field["id"]),
            validated,
        )
        for field in test_data["cataloging"]["fields"]
    }
    package_controls = {
        field["id"]: build_radio_group(
            field["options"],
            saved_package.get(field["id"]),
            validated,
        )
        for field in test_data["package"]["fields"]
    }

    def persist_form():
        state["responses"]["p10_management"] = get_selected_ids(management_checkboxes)
        state["responses"]["p10_permissions"] = {
            field_id: control.value for field_id, control in permission_controls.items()
        }
        state["responses"]["p10_cataloging"] = {
            field_id: control.value for field_id, control in cataloging_controls.items()
        }
        state["responses"]["p10_package"] = {
            field_id: control.value for field_id, control in package_controls.items()
        }

    def validate(e):
        persist_form()
        selected_management = state["responses"].get("p10_management", [])
        selected_permissions = state["responses"].get("p10_permissions", {})
        selected_cataloging = state["responses"].get("p10_cataloging", {})
        selected_package = state["responses"].get("p10_package", {})

        expected_management = [
            option["id"] for option in test_data["management"]["options"] if option["expected"]
        ]
        management_ok = set(selected_management) == set(expected_management)
        management_points = round(
            sum(
                1
                for option in test_data["management"]["options"]
                if (option["id"] in selected_management) == bool(option["expected"])
            )
            / len(test_data["management"]["options"])
            * 24
        )

        permissions_ok, permission_points, expected_permissions, permission_checks = evaluate_radio_fields(
            test_data["permissions"]["fields"],
            selected_permissions,
            "permission",
        )
        cataloging_ok, cataloging_points, expected_cataloging, cataloging_checks = evaluate_radio_fields(
            test_data["cataloging"]["fields"],
            selected_cataloging,
            "cataloging",
        )
        package_ok, package_points, expected_package, package_checks = evaluate_radio_fields(
            test_data["package"]["fields"],
            selected_package,
            "package",
        )

        score = management_points + permission_points + cataloging_points + package_points
        ok = score >= 80 and management_ok and permissions_ok and cataloging_ok and package_ok
        message = test_data["feedback"]["success"] if ok else test_data["feedback"]["failure"]
        state["completed"]["p10"] = ok
        state["feedback"]["p10"] = {"ok": ok, "message": message}

        result = {
            "test_id": TEST_ID,
            "scenario_id": test_data["scenario_id"],
            "scenario_title": test_data["scenario_title"],
            "timestamp_utc": datetime.utcnow().isoformat(),
            "score_0_100": score,
            "level_hint": "A2" if ok else "A1",
            "payload": {
                "selected_management": selected_management,
                "expected_management": expected_management,
                "selected_permissions": selected_permissions,
                "expected_permissions": expected_permissions,
                "selected_cataloging": selected_cataloging,
                "expected_cataloging": expected_cataloging,
                "selected_package": selected_package,
                "expected_package": expected_package,
            },
            "checks": [
                {
                    "check_id": "secure_management",
                    "label": "Aplica comparticion, gestion e intercambio seguro en entorno controlado",
                    "passed": management_ok,
                    "weight": 24,
                    "evidence": ", ".join(selected_management),
                },
                *permission_checks,
                *cataloging_checks,
                *package_checks,
            ],
            "notes": [message],
        }

        saved_path = save_result(result)
        state["responses"]["p10_saved_path"] = str(saved_path)
        refresh_view()

    content = ft.Column(
        controls=[
            ft.Text(test_data["intro"], size=15, weight=ft.FontWeight.W_600),
            info_panel(test_data["mentor"]["title"], test_data["mentor"]["lines"], "#F0FDF4"),
            ft.Divider(height=24),
            section_title(test_data["management"]["title"]),
            ft.Text(test_data["management"]["description"], size=14),
            ft.ResponsiveRow(controls=management_cards, spacing=8, run_spacing=8),
            ft.Divider(height=24),
            section_title(test_data["permissions"]["title"]),
            ft.Text(test_data["permissions"]["description"], size=14),
            *build_field_sections(test_data["permissions"]["fields"], permission_controls),
            ft.Divider(height=24),
            section_title(test_data["cataloging"]["title"]),
            ft.Text(test_data["cataloging"]["description"], size=14),
            *build_field_sections(test_data["cataloging"]["fields"], cataloging_controls),
            ft.Divider(height=24),
            section_title(test_data["package"]["title"]),
            ft.Text(test_data["package"]["description"], size=14),
            *build_field_sections(test_data["package"]["fields"], package_controls),
            ft.Container(height=8),
            ft.ElevatedButton("Validar prueba", on_click=validate),
            build_result_box(state["feedback"]["p10"]),
        ],
        spacing=12,
    )

    return question_block(
        title=test_data["title"],
        statement=test_data["statement"],
        content=content,
    )
