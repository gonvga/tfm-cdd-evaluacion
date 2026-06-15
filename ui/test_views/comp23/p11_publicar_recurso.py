import json
import unicodedata
from datetime import datetime
from pathlib import Path

import flet as ft

from core.storage import save_result
from ui.components import checkbox_feedback, question_block
from ui.test_views.comp23.p10_configurar_publicacion import (
    build_result_box,
    info_panel,
    section_title,
)


TEST_ID = "P11"
DATA_PATH = Path("data/p11_comp23_b1.json")


def load_test_data() -> dict:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def normalize_text(value: str | None) -> str:
    normalized = unicodedata.normalize("NFD", value or "")
    without_accents = "".join(
        char for char in normalized if unicodedata.category(char) != "Mn"
    )
    return " ".join(without_accents.casefold().replace("º", "").split())


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


def dropdown_options(options: list[dict]) -> list[ft.dropdown.Option]:
    return [
        ft.dropdown.Option(key=option["id"], text=option["label"])
        for option in options
    ]


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


def build_dropdown_row(
    label: str,
    control: ft.Dropdown,
    validated: bool,
    passed: bool,
    expected_label: str,
) -> ft.Control:
    feedback = []
    if validated:
        feedback.append(
            inline_feedback(
                "Configuracion correcta." if passed else f"Revisar. Valor esperado: {expected_label}.",
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


def build_checkbox_card(
    option: dict,
    checkbox: ft.Checkbox,
    validated: bool,
) -> ft.Control:
    feedback_text, passed = checkbox_feedback(
        bool(checkbox.value),
        bool(option["expected"]),
    )
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


def option_label(options: list[dict], option_id: str | None) -> str:
    return next((option["label"] for option in options if option["id"] == option_id), "")


def score_exact_mapping(
    items: list[dict],
    selected: dict,
    weight: int,
    prefix: str,
) -> tuple[bool, int, dict, list[dict]]:
    expected = {item["id"]: item["expected"] for item in items}
    checks = []
    passed_count = 0

    for item in items:
        passed = selected.get(item["id"]) == item["expected"]
        passed_count += 1 if passed else 0
        checks.append(
            {
                "check_id": f"{prefix}_{item['id']}",
                "label": item["label"],
                "passed": passed,
                "weight": round(weight / len(items), 2),
                "evidence": str(selected.get(item["id"])),
            }
        )

    return all(check["passed"] for check in checks), round(passed_count / len(items) * weight), expected, checks


def score_catalog_record(catalog: dict, selected: dict, weight: int) -> tuple[bool, int, dict, list[dict]]:
    checks = []
    expected = {}
    passed_count = 0

    for field in catalog["text_fields"]:
        value = selected.get(field["id"], "")
        if "expected_terms" in field:
            expected_terms = {normalize_text(term) for term in field["expected_terms"]}
            selected_terms = normalize_terms(value)
            passed = expected_terms <= selected_terms
            expected[field["id"]] = field["expected_terms"]
        else:
            passed = normalize_text(value) == normalize_text(field["expected"])
            expected[field["id"]] = field["expected"]

        passed_count += 1 if passed else 0
        checks.append(
            {
                "check_id": f"catalog_{field['id']}",
                "label": field["label"],
                "passed": passed,
                "weight": round(weight / (len(catalog["text_fields"]) + len(catalog["select_fields"])), 2),
                "evidence": value,
            }
        )

    for field in catalog["select_fields"]:
        passed = selected.get(field["id"]) == field["expected"]
        expected[field["id"]] = field["expected"]
        passed_count += 1 if passed else 0
        checks.append(
            {
                "check_id": f"catalog_{field['id']}",
                "label": field["label"],
                "passed": passed,
                "weight": round(weight / (len(catalog["text_fields"]) + len(catalog["select_fields"])), 2),
                "evidence": str(selected.get(field["id"])),
            }
        )

    return all(check["passed"] for check in checks), round(passed_count / len(checks) * weight), expected, checks


def score_package(package: dict, selected_components: list[str], selected_settings: dict) -> tuple[bool, int, dict, list[dict]]:
    checks = []
    passed_count = 0
    total_count = len(package["components"]) + len(package["settings"])
    expected = {
        "components": [
            component["id"] for component in package["components"] if component["expected"]
        ],
        "settings": {setting["id"]: setting["expected"] for setting in package["settings"]},
    }

    for component in package["components"]:
        passed = (component["id"] in selected_components) == bool(component["expected"])
        passed_count += 1 if passed else 0
        checks.append(
            {
                "check_id": f"imscp_component_{component['id']}",
                "label": component["label"],
                "passed": passed,
                "weight": round(package["weight"] / total_count, 2),
                "evidence": str(component["id"] in selected_components),
            }
        )

    for setting in package["settings"]:
        passed = selected_settings.get(setting["id"]) == setting["expected"]
        passed_count += 1 if passed else 0
        checks.append(
            {
                "check_id": f"imscp_setting_{setting['id']}",
                "label": setting["label"],
                "passed": passed,
                "weight": round(package["weight"] / total_count, 2),
                "evidence": str(selected_settings.get(setting["id"])),
            }
        )

    return all(check["passed"] for check in checks), round(passed_count / total_count * package["weight"]), expected, checks


def build_test_p11(state: dict, refresh_view) -> ft.Control:
    test_data = load_test_data()
    validated = state["feedback"]["p11"]["ok"] is not None
    saved_map = state["responses"].get("p11_publication_map", {})
    saved_matrix = state["responses"].get("p11_permission_matrix", {})
    saved_catalog = state["responses"].get("p11_catalog_record", {})
    saved_components = state["responses"].get("p11_imscp_components", [])
    saved_settings = state["responses"].get("p11_imscp_settings", {})

    publication = test_data["publication_map"]
    permissions = test_data["permission_matrix"]
    catalog = test_data["catalog_record"]
    package = test_data["imscp_package"]

    publication_controls = {
        item["id"]: ft.Dropdown(
            value=saved_map.get(item["id"]),
            options=dropdown_options(publication["destinations"]),
            dense=True,
        )
        for item in publication["items"]
    }
    permission_controls = {
        agent["id"]: ft.Dropdown(
            value=saved_matrix.get(agent["id"]),
            options=dropdown_options(permissions["permissions"]),
            dense=True,
        )
        for agent in permissions["agents"]
    }
    text_controls = {
        field["id"]: ft.TextField(
            value=saved_catalog.get(field["id"], ""),
            hint_text=field.get("placeholder", ""),
            dense=True,
        )
        for field in catalog["text_fields"]
    }
    catalog_select_controls = {
        field["id"]: ft.Dropdown(
            value=saved_catalog.get(field["id"]),
            options=dropdown_options(field["options"]),
            dense=True,
        )
        for field in catalog["select_fields"]
    }
    component_controls = {
        component["id"]: ft.Checkbox(value=component["id"] in saved_components)
        for component in package["components"]
    }
    setting_controls = {
        setting["id"]: ft.Dropdown(
            value=saved_settings.get(setting["id"]),
            options=dropdown_options(setting["options"]),
            dense=True,
        )
        for setting in package["settings"]
    }

    def persist_form():
        state["responses"]["p11_publication_map"] = {
            item_id: control.value for item_id, control in publication_controls.items()
        }
        state["responses"]["p11_permission_matrix"] = {
            agent_id: control.value for agent_id, control in permission_controls.items()
        }
        state["responses"]["p11_catalog_record"] = {
            **{field_id: control.value for field_id, control in text_controls.items()},
            **{field_id: control.value for field_id, control in catalog_select_controls.items()},
        }
        state["responses"]["p11_imscp_components"] = [
            component_id for component_id, control in component_controls.items() if control.value
        ]
        state["responses"]["p11_imscp_settings"] = {
            setting_id: control.value for setting_id, control in setting_controls.items()
        }

    def validate(e):
        persist_form()
        selected_map = state["responses"].get("p11_publication_map", {})
        selected_matrix = state["responses"].get("p11_permission_matrix", {})
        selected_catalog = state["responses"].get("p11_catalog_record", {})
        selected_components = state["responses"].get("p11_imscp_components", [])
        selected_settings = state["responses"].get("p11_imscp_settings", {})

        map_ok, map_points, expected_map, map_checks = score_exact_mapping(
            publication["items"],
            selected_map,
            publication["weight"],
            "publication",
        )
        matrix_ok, matrix_points, expected_matrix, matrix_checks = score_exact_mapping(
            permissions["agents"],
            selected_matrix,
            permissions["weight"],
            "permission",
        )
        catalog_ok, catalog_points, expected_catalog, catalog_checks = score_catalog_record(
            catalog,
            selected_catalog,
            catalog["weight"],
        )
        package_ok, package_points, expected_package, package_checks = score_package(
            package,
            selected_components,
            selected_settings,
        )

        score = map_points + matrix_points + catalog_points + package_points
        ok = score >= 80 and map_ok and matrix_ok and catalog_ok and package_ok
        message = test_data["feedback"]["success"] if ok else test_data["feedback"]["failure"]
        state["completed"]["p11"] = ok
        state["feedback"]["p11"] = {"ok": ok, "message": message}

        result = {
            "test_id": TEST_ID,
            "scenario_id": test_data["scenario_id"],
            "scenario_title": test_data["scenario_title"],
            "timestamp_utc": datetime.utcnow().isoformat(),
            "score_0_100": score,
            "level_hint": "B1" if ok else "A2",
            "payload": {
                "selected_publication_map": selected_map,
                "expected_publication_map": expected_map,
                "selected_permission_matrix": selected_matrix,
                "expected_permission_matrix": expected_matrix,
                "selected_catalog_record": selected_catalog,
                "expected_catalog_record": expected_catalog,
                "selected_imscp_components": selected_components,
                "selected_imscp_settings": selected_settings,
                "expected_imscp_package": expected_package,
            },
            "checks": [
                *map_checks,
                *matrix_checks,
                *catalog_checks,
                *package_checks,
            ],
            "notes": [message],
        }

        saved_path = save_result(result)
        state["responses"]["p11_saved_path"] = str(saved_path)
        refresh_view()

    publication_rows = [
        build_dropdown_row(
            item["label"],
            publication_controls[item["id"]],
            validated,
            saved_map.get(item["id"]) == item["expected"],
            option_label(publication["destinations"], item["expected"]),
        )
        for item in publication["items"]
    ]
    permission_rows = [
        build_dropdown_row(
            agent["label"],
            permission_controls[agent["id"]],
            validated,
            saved_matrix.get(agent["id"]) == agent["expected"],
            option_label(permissions["permissions"], agent["expected"]),
        )
        for agent in permissions["agents"]
    ]
    catalog_text_rows = [
        build_dropdown_row(
            field["label"],
            text_controls[field["id"]],
            validated,
            (
                {normalize_text(term) for term in field["expected_terms"]} <= normalize_terms(saved_catalog.get(field["id"], ""))
                if "expected_terms" in field
                else normalize_text(saved_catalog.get(field["id"], "")) == normalize_text(field["expected"])
            ),
            "; ".join(field.get("expected_terms", [field.get("expected", "")])),
        )
        for field in catalog["text_fields"]
    ]
    catalog_select_rows = [
        build_dropdown_row(
            field["label"],
            catalog_select_controls[field["id"]],
            validated,
            saved_catalog.get(field["id"]) == field["expected"],
            option_label(field["options"], field["expected"]),
        )
        for field in catalog["select_fields"]
    ]
    component_cards = [
        build_checkbox_card(component, component_controls[component["id"]], validated)
        for component in package["components"]
    ]
    setting_rows = [
        build_dropdown_row(
            setting["label"],
            setting_controls[setting["id"]],
            validated,
            saved_settings.get(setting["id"]) == setting["expected"],
            option_label(setting["options"], setting["expected"]),
        )
        for setting in package["settings"]
    ]

    content = ft.Column(
        controls=[
            ft.Text(test_data["intro"], size=15, weight=ft.FontWeight.W_600),
            info_panel(test_data["plan"]["title"], test_data["plan"]["lines"], "#F0FDF4"),
            ft.Divider(height=24),
            section_title(publication["title"]),
            ft.Text(publication["description"], size=14),
            *publication_rows,
            ft.Divider(height=24),
            section_title(permissions["title"]),
            ft.Text(permissions["description"], size=14),
            *permission_rows,
            ft.Divider(height=24),
            section_title(catalog["title"]),
            ft.Text(catalog["description"], size=14),
            *catalog_text_rows,
            *catalog_select_rows,
            ft.Divider(height=24),
            section_title(package["title"]),
            ft.Text(package["description"], size=14),
            ft.ResponsiveRow(controls=component_cards, spacing=8, run_spacing=8),
            *setting_rows,
            ft.Container(height=8),
            ft.ElevatedButton("Validar prueba", on_click=validate),
            build_result_box(state["feedback"]["p11"]),
        ],
        spacing=12,
    )

    return question_block(
        title=test_data["title"],
        statement=test_data["statement"],
        content=content,
    )
