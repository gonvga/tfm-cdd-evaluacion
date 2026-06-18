import json
from datetime import datetime, timezone

import flet as ft

from core.paths import resource_path
from core.storage import save_result
from ui.components import checkbox_feedback, question_block
from ui.test_views.comp23.p10_configurar_publicacion import (
    build_result_box,
    info_panel,
    section_title,
)


TEST_ID = "P12"
DATA_PATH = resource_path("data", "p12_comp23_b2.json")


def load_test_data() -> dict:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def dropdown_options(options: list[dict]) -> list[ft.dropdown.Option]:
    return [
        ft.dropdown.Option(key=option["id"], text=option["label"])
        for option in options
    ]


def option_label(options: list[dict], option_id: str | None) -> str:
    return next(
        (option["label"] for option in options if option["id"] == option_id),
        "",
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


def build_checkbox_card(
    option: dict,
    checkbox: ft.Checkbox,
    validated: bool,
) -> ft.Control:
    feedback_text, passed = checkbox_feedback(
        bool(checkbox.value),
        bool(option["expected"]),
    )
    bgcolor, border_color = (
        feedback_colors(passed) if validated else ("#F9FAFB", "#E5E7EB")
    )
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        checkbox,
                        ft.Text(
                            option["label"],
                            size=14,
                            weight=ft.FontWeight.W_600,
                            expand=True,
                        ),
                    ],
                    spacing=6,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                *([inline_feedback(feedback_text, passed)] if validated else []),
            ],
            spacing=8,
        ),
        col={"xs": 12, "md": 6},
        bgcolor=bgcolor,
        border=ft.border.all(1, border_color),
        border_radius=10,
        padding=12,
    )


def build_dropdown_row(
    label: str,
    control: ft.Dropdown,
    validated: bool,
    passed: bool,
    expected_label: str,
) -> ft.Control:
    bgcolor, border_color = (
        feedback_colors(passed) if validated else ("#F9FAFB", "#E5E7EB")
    )
    feedback = []
    if validated:
        feedback.append(
            inline_feedback(
                "Decisión adecuada."
                if passed
                else f"Revisa esta decisión. Opción esperada: {expected_label}.",
                passed,
            )
        )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(label, size=14, weight=ft.FontWeight.W_600),
                control,
                *feedback,
            ],
            spacing=8,
        ),
        bgcolor=bgcolor,
        border=ft.border.all(1, border_color),
        border_radius=10,
        padding=12,
    )


def score_features(
    section: dict,
    selected_ids: list[str],
    prefix: str,
) -> tuple[bool, int, list[str], list[dict]]:
    expected_ids = [
        option["id"] for option in section["options"] if option["expected"]
    ]
    checks = []
    passed_count = 0

    for option in section["options"]:
        passed = (option["id"] in selected_ids) == bool(option["expected"])
        passed_count += int(passed)
        checks.append(
            {
                "check_id": f"{prefix}_{option['id']}",
                "label": option["label"],
                "passed": passed,
                "weight": round(section["weight"] / len(section["options"]), 2),
                "evidence": str(option["id"] in selected_ids),
            }
        )

    points = round(passed_count / len(section["options"]) * section["weight"])
    return all(check["passed"] for check in checks), points, expected_ids, checks


def score_cases(
    section: dict,
    selected: dict[str, str | None],
) -> tuple[bool, int, dict[str, str], list[dict]]:
    expected = {case["id"]: case["expected"] for case in section["cases"]}
    checks = []
    passed_count = 0

    for case in section["cases"]:
        passed = selected.get(case["id"]) == case["expected"]
        passed_count += int(passed)
        checks.append(
            {
                "check_id": f"advice_{case['id']}",
                "label": case["prompt"],
                "passed": passed,
                "weight": round(section["weight"] / len(section["cases"]), 2),
                "evidence": str(selected.get(case["id"])),
            }
        )

    points = round(passed_count / len(section["cases"]) * section["weight"])
    return all(check["passed"] for check in checks), points, expected, checks


def build_test_p12(
    state: dict,
    refresh_view,
    page: ft.Page | None = None,
) -> ft.Control:
    del page
    test_data = load_test_data()
    validated = state["feedback"]["p12"]["ok"] is not None

    catalog = test_data["catalog_navigation"]
    access = test_data["access_publication"]
    advice = test_data["teacher_advice"]

    saved_catalog = state["responses"].get("p12_catalog_navigation", [])
    saved_access = state["responses"].get("p12_access_publication", [])
    saved_advice = state["responses"].get("p12_teacher_advice", {})

    catalog_controls = {
        option["id"]: ft.Checkbox(value=option["id"] in saved_catalog)
        for option in catalog["options"]
    }
    access_controls = {
        option["id"]: ft.Checkbox(value=option["id"] in saved_access)
        for option in access["options"]
    }
    advice_controls = {
        case["id"]: ft.Dropdown(
            value=saved_advice.get(case["id"]),
            options=dropdown_options(case["options"]),
            dense=True,
        )
        for case in advice["cases"]
    }

    def persist_form() -> None:
        state["responses"]["p12_catalog_navigation"] = [
            option_id
            for option_id, control in catalog_controls.items()
            if control.value
        ]
        state["responses"]["p12_access_publication"] = [
            option_id
            for option_id, control in access_controls.items()
            if control.value
        ]
        state["responses"]["p12_teacher_advice"] = {
            case_id: control.value
            for case_id, control in advice_controls.items()
        }

    def validate(e) -> None:
        persist_form()
        selected_catalog = state["responses"]["p12_catalog_navigation"]
        selected_access = state["responses"]["p12_access_publication"]
        selected_advice = state["responses"]["p12_teacher_advice"]

        catalog_ok, catalog_points, expected_catalog, catalog_checks = score_features(
            catalog,
            selected_catalog,
            "catalog",
        )
        access_ok, access_points, expected_access, access_checks = score_features(
            access,
            selected_access,
            "access",
        )
        advice_ok, advice_points, expected_advice, advice_checks = score_cases(
            advice,
            selected_advice,
        )

        score = catalog_points + access_points + advice_points
        ok = score >= 80 and catalog_ok and access_ok and advice_ok
        message = (
            test_data["feedback"]["success"]
            if ok
            else test_data["feedback"]["failure"]
        )
        state["completed"]["p12"] = ok
        state["feedback"]["p12"] = {"ok": ok, "message": message}

        result = {
            "test_id": TEST_ID,
            "scenario_id": test_data["scenario_id"],
            "scenario_title": test_data["scenario_title"],
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "score_0_100": score,
            "level_hint": "B2" if ok else "B1",
            "payload": {
                "selected_catalog_navigation": selected_catalog,
                "expected_catalog_navigation": expected_catalog,
                "selected_access_publication": selected_access,
                "expected_access_publication": expected_access,
                "selected_teacher_advice": selected_advice,
                "expected_teacher_advice": expected_advice,
            },
            "checks": [
                *catalog_checks,
                *access_checks,
                *advice_checks,
            ],
            "notes": [message],
        }
        saved_path = save_result(result)
        state["responses"]["p12_saved_path"] = str(saved_path)
        refresh_view()

    catalog_cards = [
        build_checkbox_card(option, catalog_controls[option["id"]], validated)
        for option in catalog["options"]
    ]
    access_cards = [
        build_checkbox_card(option, access_controls[option["id"]], validated)
        for option in access["options"]
    ]
    advice_rows = [
        build_dropdown_row(
            case["prompt"],
            advice_controls[case["id"]],
            validated,
            saved_advice.get(case["id"]) == case["expected"],
            option_label(case["options"], case["expected"]),
        )
        for case in advice["cases"]
    ]

    content = ft.Column(
        controls=[
            ft.Text(test_data["intro"], size=15, weight=ft.FontWeight.W_600),
            info_panel(
                test_data["context"]["title"],
                test_data["context"]["lines"],
                "#F0FDF4",
            ),
            ft.Divider(height=24),
            section_title(catalog["title"]),
            ft.Text(catalog["description"], size=14),
            ft.ResponsiveRow(
                controls=catalog_cards,
                spacing=8,
                run_spacing=8,
            ),
            ft.Divider(height=24),
            section_title(access["title"]),
            ft.Text(access["description"], size=14),
            ft.ResponsiveRow(
                controls=access_cards,
                spacing=8,
                run_spacing=8,
            ),
            ft.Divider(height=24),
            section_title(advice["title"]),
            ft.Text(advice["description"], size=14),
            *advice_rows,
            ft.Container(height=8),
            ft.ElevatedButton("Validar prueba", on_click=validate),
            build_result_box(state["feedback"]["p12"]),
        ],
        spacing=12,
    )

    return question_block(
        title=test_data["title"],
        statement=test_data["statement"],
        content=content,
    )
