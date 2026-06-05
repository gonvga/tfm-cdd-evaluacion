import json
import unicodedata
from datetime import datetime
from pathlib import Path

import flet as ft

from core.storage import save_result
from ui.components import question_block


TEST_ID = "P12"
DATA_PATH = Path("data/p12_comp23_b2.json")


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


def dropdown_options(options: list[dict]) -> list[ft.dropdown.Option]:
    return [
        ft.dropdown.Option(key=option["id"], text=option["label"])
        for option in options
    ]


def get_selected_ids(checkboxes: dict[str, ft.Checkbox]) -> list[str]:
    return [key for key, checkbox in checkboxes.items() if checkbox.value]


def build_checkbox_card(option: dict, checkbox: ft.Checkbox, validated: bool) -> ft.Control:
    passed = checkbox.value == bool(option["expected"])
    bgcolor, border_color = feedback_colors(passed) if validated else ("#F9FAFB", "#E5E7EB")
    return ft.Container(
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
                *([
                    inline_feedback(
                        "Opción correcta." if passed else "Revisa esta elección.",
                        passed,
                    )
                ] if validated else []),
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
    control: ft.Control,
    validated: bool,
    passed: bool,
    expected_label: str,
) -> ft.Control:
    feedback = []
    if validated:
        feedback.append(
            inline_feedback(
                "Configuración correcta." if passed else f"Revisa. Valor esperado: {expected_label}.",
                passed,
            )
        )

    bgcolor, border_color = feedback_colors(passed) if validated else ("#F9FAFB", "#E5E7EB")
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


def normalize_text(value: str | None) -> str:
    normalized = unicodedata.normalize("NFD", value or "")
    without_accents = "".join(
        char for char in normalized if unicodedata.category(char) != "Mn"
    )
    return " ".join(without_accents.casefold().split())


def normalize_terms(value: str | None) -> set[str]:
    separators = [";", ","]
    normalized = value or ""
    for separator in separators:
        normalized = normalized.replace(separator, "|")
    return {
        normalize_text(term)
        for term in normalized.split("|")
        if normalize_text(term)
    }


def score_exact_mapping(
    items: list[dict],
    selected: dict,
    weight: int,
    prefix: str,
) -> tuple[bool, int, dict, list[dict]]:
    checks = []
    passed_count = 0
    total = len(items)
    expected = {item["id"]: item["expected"] for item in items}

    for item in items:
        passed = selected.get(item["id"], False) == bool(item["expected"])
        passed_count += 1 if passed else 0
        checks.append(
            {
                "check_id": f"{prefix}_{item['id']}",
                "label": item["label"],
                "passed": passed,
                "weight": round(weight / total, 2),
                "evidence": str(selected.get(item["id"], False)),
            }
        )

    return all(check["passed"] for check in checks), round(passed_count / total * weight), expected, checks


def score_catalog_record(catalog: dict, selected: dict, weight: int) -> tuple[bool, int, dict, list[dict]]:
    checks = []
    expected = {}
    passed_count = 0
    total_fields = len(catalog["text_fields"]) + len(catalog["select_fields"])

    for field in catalog["text_fields"]:
        if field["id"] == "keywords":
            expected_terms = [normalize_text(term) for term in field.get("expected_terms", [])]
            selected_terms = normalize_terms(selected.get(field["id"], ""))
            passed = set(expected_terms) <= selected_terms
            expected[field["id"]] = field.get("expected_terms", [])
        else:
            passed = normalize_text(selected.get(field["id"], "")) == normalize_text(field.get("expected", ""))
            expected[field["id"]] = field.get("expected", "")

        passed_count += 1 if passed else 0
        checks.append(
            {
                "check_id": f"catalog_{field['id']}",
                "label": field["label"],
                "passed": passed,
                "weight": round(weight / total_fields, 2),
                "evidence": selected.get(field["id"], ""),
            }
        )

    for field in catalog["select_fields"]:
        passed = selected.get(field["id"]) == next(
            option["id"] for option in field["options"] if option["expected"]
        )
        expected[field["id"]] = next(
            option["id"] for option in field["options"] if option["expected"]
        )
        passed_count += 1 if passed else 0
        checks.append(
            {
                "check_id": f"catalog_{field['id']}",
                "label": field["label"],
                "passed": passed,
                "weight": round(weight / total_fields, 2),
                "evidence": selected.get(field["id"], ""),
            }
        )

    return all(check["passed"] for check in checks), round(passed_count / total_fields * weight), expected, checks


def option_label(options: list[dict], option_id: str | None) -> str:
    return next((option["label"] for option in options if option["id"] == option_id), "")


def build_test_p12(state: dict, refresh_view) -> ft.Control:
    test_data = load_test_data()
    validated = state["feedback"]["p12"]["ok"] is not None
    saved_repository = state["responses"].get("p12_repository", [])
    saved_access = state["responses"].get("p12_access", [])
    saved_advice = state["responses"].get("p12_advice", [])
    saved_catalog = state["responses"].get("p12_catalog_record", {})

    repository_controls = {
        option["id"]: ft.Checkbox(value=option["id"] in saved_repository)
        for option in test_data["repository"]["options"]
    }
    repository_cards = [
        build_checkbox_card(option, repository_controls[option["id"]], validated)
        for option in test_data["repository"]["options"]
    ]

    access_controls = {
        option["id"]: ft.Checkbox(value=option["id"] in saved_access)
        for option in test_data["access"]["options"]
    }
    access_cards = [
        build_checkbox_card(option, access_controls[option["id"]], validated)
        for option in test_data["access"]["options"]
    ]

    advice_controls = {
        option["id"]: ft.Checkbox(value=option["id"] in saved_advice)
        for option in test_data["advice"]["options"]
    }
    advice_cards = [
        build_checkbox_card(option, advice_controls[option["id"]], validated)
        for option in test_data["advice"]["options"]
    ]

    catalog_controls = {
        field["id"]: ft.Dropdown(
            value=saved_catalog.get(field["id"]),
            options=dropdown_options(field["options"]),
            dense=True,
        )
        for field in test_data["catalog_record"]["select_fields"]
    }
    catalog_controls["title"] = ft.TextField(
        value=saved_catalog.get("title", ""),
        hint_text=test_data["catalog_record"]["text_fields"][0].get("placeholder", ""),
        dense=True,
    )
    catalog_controls["keywords"] = ft.TextField(
        value=saved_catalog.get("keywords", ""),
        hint_text="Introduce palabras clave separadas por punto y coma",
        dense=True,
    )

    def persist_form():
        state["responses"]["p12_repository"] = get_selected_ids(repository_controls)
        state["responses"]["p12_access"] = get_selected_ids(access_controls)
        state["responses"]["p12_advice"] = get_selected_ids(advice_controls)
        state["responses"]["p12_catalog_record"] = {
            field_id: control.value
            for field_id, control in catalog_controls.items()
        }

    def validate(e):
        persist_form()
        selected_repository = {item_id: repository_controls[item_id].value for item_id in repository_controls}
        selected_access = {item_id: access_controls[item_id].value for item_id in access_controls}
        selected_advice = {item_id: advice_controls[item_id].value for item_id in advice_controls}
        selected_catalog = state["responses"]["p12_catalog_record"]

        repo_ok, repo_points, expected_repo, repo_checks = score_exact_mapping(
            test_data["repository"]["options"],
            selected_repository,
            test_data["repository"]["weight"],
            "repository",
        )
        access_ok, access_points, expected_access, access_checks = score_exact_mapping(
            test_data["access"]["options"],
            selected_access,
            test_data["access"]["weight"],
            "access",
        )
        advice_ok, advice_points, expected_advice, advice_checks = score_exact_mapping(
            test_data["advice"]["options"],
            selected_advice,
            test_data["advice"]["weight"],
            "advice",
        )
        catalog_ok, catalog_points, expected_catalog, catalog_checks = score_catalog_record(
            test_data["catalog_record"],
            selected_catalog,
            test_data["catalog_record"]["weight"],
        )

        score = repo_points + access_points + advice_points + catalog_points
        ok = score >= 80 and repo_ok and access_ok and advice_ok and catalog_ok
        message = test_data["feedback"]["success"] if ok else test_data["feedback"]["failure"]
        state["completed"]["p12"] = ok
        state["feedback"]["p12"] = {"ok": ok, "message": message}

        result = {
            "test_id": TEST_ID,
            "scenario_id": test_data["scenario_id"],
            "scenario_title": test_data["scenario_title"],
            "timestamp_utc": datetime.utcnow().isoformat(),
            "score_0_100": score,
            "level_hint": "B2" if ok else "B1",
            "payload": {
                "selected_repository": selected_repository,
                "expected_repository": expected_repo,
                "selected_access": selected_access,
                "expected_access": expected_access,
                "selected_advice": selected_advice,
                "expected_advice": expected_advice,
                "selected_catalog_record": selected_catalog,
                "expected_catalog_record": expected_catalog,
            },
            "checks": [
                *repo_checks,
                *access_checks,
                *advice_checks,
                *catalog_checks,
            ],
            "notes": [message],
        }

        saved_path = save_result(result)
        state["responses"]["p12_saved_path"] = str(saved_path)
        refresh_view()

    repository_cards_row = ft.ResponsiveRow(controls=repository_cards, spacing=8, run_spacing=8)
    access_cards_row = ft.ResponsiveRow(controls=access_cards, spacing=8, run_spacing=8)
    advice_cards_row = ft.ResponsiveRow(controls=advice_cards, spacing=8, run_spacing=8)
    catalog_rows = [
        build_dropdown_row(
            field["label"],
            catalog_controls[field["id"]],
            validated,
            saved_catalog.get(field["id"]) == next(
                option["id"] for option in field["options"] if option["expected"]
            ),
            option_label(field["options"], next(option["id"] for option in field["options"] if option["expected"])),
        )
        for field in test_data["catalog_record"]["select_fields"]
    ]
    catalog_rows.insert(
        0,
        build_dropdown_row(
            test_data["catalog_record"]["text_fields"][0]["label"],
            catalog_controls["title"],
            validated,
            normalize_text(saved_catalog.get("title", "")) == normalize_text(test_data["catalog_record"]["text_fields"][0].get("expected", "")),
            test_data["catalog_record"]["text_fields"][0].get("expected", ""),
        ),
    )
    keywords_field = test_data["catalog_record"]["text_fields"][1]
    expected_keyword_label = "; ".join(keywords_field.get("expected_terms", []))
    keywords_passed = set(normalize_text(term) for term in keywords_field.get("expected_terms", [])) <= normalize_terms(saved_catalog.get("keywords", ""))
    catalog_rows.append(
        build_dropdown_row(
            keywords_field["label"],
            catalog_controls["keywords"],
            validated,
            keywords_passed,
            expected_keyword_label,
        )
    )

    content = ft.Column(
        controls=[
            ft.Text(test_data["intro"], size=15, weight=ft.FontWeight.W_600),
            info_panel(test_data["plan"]["title"], test_data["plan"]["lines"], "#F0FDF4"),
            ft.Divider(height=24),
            section_title(test_data["repository"]["title"]),
            ft.Text(test_data["repository"]["description"], size=14),
            repository_cards_row,
            ft.Divider(height=24),
            section_title(test_data["access"]["title"]),
            ft.Text(test_data["access"]["description"], size=14),
            access_cards_row,
            ft.Divider(height=24),
            section_title(test_data["catalog_record"]["title"]),
            ft.Text(test_data["catalog_record"]["description"], size=14),
            *catalog_rows,
            ft.Divider(height=24),
            section_title(test_data["advice"]["title"]),
            ft.Text(test_data["advice"]["description"], size=14),
            advice_cards_row,
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
