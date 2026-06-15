import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import flet as ft

from core.storage import save_result
from ui.components import checkbox_feedback, question_block


TEST_ID = "P10"
DATA_PATH = Path("data/p10_comp23_a2.json")


def load_test_data() -> dict:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def normalize_text(value: str | None) -> str:
    text = unicodedata.normalize("NFD", (value or "").strip().lower())
    return "".join(char for char in text if unicodedata.category(char) != "Mn")


def title_matches(field: dict, value: str | None) -> bool:
    normalized = normalize_text(value)
    words = len(re.findall(r"\b\w+\b", value or "", flags=re.UNICODE))
    return (
        all(normalize_text(term) in normalized for term in field["required_terms"])
        and field["minimum_words"] <= words <= field["maximum_words"]
    )


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
    return ft.Text(text, size=18, weight=ft.FontWeight.BOLD)


def section_header(number: str, title: str, description: str) -> ft.Control:
    return ft.Row(
        controls=[
            ft.Container(
                content=ft.Text(
                    number,
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
                width=36,
                height=36,
                alignment=ft.Alignment.CENTER,
                bgcolor="#2563EB",
                border_radius=10,
            ),
            ft.Column(
                controls=[
                    ft.Text(title, size=17, weight=ft.FontWeight.BOLD),
                    ft.Text(description, size=12, color="#6B7280"),
                ],
                spacing=2,
                expand=True,
            ),
        ],
        spacing=10,
    )


def info_panel(title: str, lines: list[str], bgcolor: str) -> ft.Control:
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(title, size=14, weight=ft.FontWeight.BOLD),
                *[ft.Text(f"• {line}", size=13, color="#374151") for line in lines],
            ],
            spacing=6,
        ),
        bgcolor=bgcolor,
        border=ft.border.all(1, "#BFDBFE"),
        border_radius=12,
        padding=14,
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


def selection_feedback(
    selected: str | None,
    expected: str,
    validated: bool,
) -> ft.Control:
    if not validated:
        return ft.Container()
    ok = selected == expected
    return inline_feedback(
        "Correcta." if ok else f"Incorrecta. Debías seleccionar: {expected}.",
        ok,
    )


def build_test_p10(state: dict, refresh_view) -> ft.Control:
    data = load_test_data()
    saved = state["responses"].get("p10_answers", {})
    validated = state["feedback"]["p10"]["ok"] is not None

    def dropdown(field: dict) -> ft.Dropdown:
        return ft.Dropdown(
            label=field["label"],
            value=saved.get(field["id"]),
            options=[ft.dropdown.Option(option) for option in field["options"]],
        )

    publication_controls = {
        field["id"]: dropdown(field) for field in data["publication"]["fields"]
    }
    permission_controls = {
        field["id"]: dropdown(field) for field in data["permissions"]["fields"]
    }
    catalog_controls = {
        field["id"]: dropdown(field) for field in data["catalog"]["fields"]
    }
    scorm_controls = {
        field["id"]: dropdown(field) for field in data["scorm"]["fields"]
    }
    title_control = ft.TextField(
        label=data["catalog"]["title_field"]["label"],
        hint_text=data["catalog"]["title_field"]["placeholder"],
        value=saved.get("catalog_title", ""),
    )

    saved_actions = saved.get("publication_actions", [])
    action_controls = {
        option["id"]: ft.Checkbox(
            label=option["label"],
            value=option["id"] in saved_actions,
        )
        for option in data["publication"]["actions"]
    }
    saved_tags = saved.get("catalog_tags", [])
    tag_controls = {
        option["id"]: ft.Checkbox(
            label=option["label"],
            value=option["id"] in saved_tags,
        )
        for option in data["catalog"]["tags"]
    }

    def dropdown_cards(fields: list[dict], controls: dict) -> list[ft.Control]:
        cards = []
        for field in fields:
            cards.append(
                ft.Container(
                    col={"xs": 12, "md": 6},
                    content=ft.Column(
                        controls=[
                            controls[field["id"]],
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
        return cards

    def checkbox_rows(options: list[dict], controls: dict, saved_ids: list[str]):
        rows = []
        for option in options:
            selected = option["id"] in saved_ids
            text, ok = checkbox_feedback(
                selected,
                bool(option["expected"]),
                (
                    "Esta decisión aplica el procedimiento institucional."
                    if option["expected"]
                    else "Esta decisión reduce el control, la trazabilidad o la recuperación."
                ),
            )
            rows.append(
                ft.Column(
                    controls=[
                        controls[option["id"]],
                        *([inline_feedback(text, ok)] if validated else []),
                    ],
                    spacing=4,
                )
            )
        return rows

    def validate(e):
        answers = {
            **{
                field_id: control.value
                for controls in (
                    publication_controls,
                    permission_controls,
                    catalog_controls,
                    scorm_controls,
                )
                for field_id, control in controls.items()
            },
            "catalog_title": title_control.value or "",
            "publication_actions": [
                option_id
                for option_id, control in action_controls.items()
                if control.value
            ],
            "catalog_tags": [
                option_id
                for option_id, control in tag_controls.items()
                if control.value
            ],
        }
        state["responses"]["p10_answers"] = answers

        publication_fields_ok = all(
            answers.get(field["id"]) == field["expected"]
            for field in data["publication"]["fields"]
        )
        expected_actions = {
            option["id"]
            for option in data["publication"]["actions"]
            if option["expected"]
        }
        actions_ok = set(answers["publication_actions"]) == expected_actions
        publication_ok = publication_fields_ok and actions_ok

        permissions_ok = all(
            answers.get(field["id"]) == field["expected"]
            for field in data["permissions"]["fields"]
        )
        catalog_fields_ok = all(
            answers.get(field["id"]) == field["expected"]
            for field in data["catalog"]["fields"]
        )
        expected_tags = {
            option["id"] for option in data["catalog"]["tags"] if option["expected"]
        }
        tags_ok = set(answers["catalog_tags"]) == expected_tags
        catalog_title_ok = title_matches(
            data["catalog"]["title_field"],
            answers["catalog_title"],
        )
        catalog_ok = catalog_fields_ok and tags_ok and catalog_title_ok
        scorm_ok = all(
            answers.get(field["id"]) == field["expected"]
            for field in data["scorm"]["fields"]
        )

        checks = [
            {
                "check_id": "controlled_publication",
                "label": "Gestiona las versiones en entornos controlados",
                "passed": publication_ok,
                "weight": 25,
                "evidence": json.dumps(answers["publication_actions"], ensure_ascii=False),
            },
            {
                "check_id": "selective_permissions",
                "label": "Configura accesos selectivos por agente",
                "passed": permissions_ok,
                "weight": 25,
                "evidence": json.dumps(
                    {field["id"]: answers.get(field["id"]) for field in data["permissions"]["fields"]},
                    ensure_ascii=False,
                ),
            },
            {
                "check_id": "institutional_catalog",
                "label": "Completa la ficha y aplica el tesauro institucional",
                "passed": catalog_ok,
                "weight": 25,
                "evidence": answers["catalog_title"],
            },
            {
                "check_id": "scorm_configuration",
                "label": "Configura el paquete según su estándar y seguimiento",
                "passed": scorm_ok,
                "weight": 25,
                "evidence": json.dumps(
                    {field["id"]: answers.get(field["id"]) for field in data["scorm"]["fields"]},
                    ensure_ascii=False,
                ),
            },
        ]
        score = sum(check["weight"] for check in checks if check["passed"])
        ok = score >= 80 and permissions_ok and catalog_ok and scorm_ok
        message = data["feedback"]["success"] if ok else data["feedback"]["failure"]
        state["completed"]["p10"] = ok
        state["feedback"]["p10"] = {"ok": ok, "message": message}

        result = {
            "test_id": TEST_ID,
            "scenario_id": data["scenario_id"],
            "scenario_title": data["scenario_title"],
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "score_0_100": score,
            "level_hint": "A2" if ok else "A1",
            "payload": {"answers": answers},
            "checks": checks,
            "notes": [message],
        }
        saved_path = save_result(result)
        state["responses"]["p10_saved_path"] = str(saved_path)
        refresh_view()

    catalog_title_ok = title_matches(
        data["catalog"]["title_field"],
        saved.get("catalog_title"),
    )
    content = ft.Column(
        controls=[
            ft.Text(data["intro"], size=15, weight=ft.FontWeight.W_600),
            ft.ResponsiveRow(
                controls=[
                    ft.Container(
                        col={"xs": 12, "md": 6},
                        content=info_panel(
                            data["package_report"]["title"],
                            data["package_report"]["lines"],
                            "#EFF6FF",
                        ),
                    ),
                    ft.Container(
                        col={"xs": 12, "md": 6},
                        content=info_panel(
                            data["mentor"]["title"],
                            data["mentor"]["lines"],
                            "#F0FDF4",
                        ),
                    ),
                ],
                spacing=10,
                run_spacing=10,
            ),
            section_header("1", data["publication"]["title"], data["publication"]["description"]),
            ft.ResponsiveRow(
                controls=dropdown_cards(data["publication"]["fields"], publication_controls),
                spacing=10,
                run_spacing=10,
            ),
            ft.Column(
                controls=checkbox_rows(
                    data["publication"]["actions"],
                    action_controls,
                    saved_actions,
                ),
                spacing=8,
            ),
            ft.Divider(height=22),
            section_header("2", data["permissions"]["title"], data["permissions"]["description"]),
            ft.ResponsiveRow(
                controls=dropdown_cards(data["permissions"]["fields"], permission_controls),
                spacing=10,
                run_spacing=10,
            ),
            ft.Divider(height=22),
            section_header("3", data["catalog"]["title"], data["catalog"]["description"]),
            title_control,
            *(
                [
                    inline_feedback(
                        (
                            "Título adecuado: identifica el contenido de forma recuperable."
                            if catalog_title_ok
                            else "Revisa el título: debe incluir lectura, noticias y científicas en 4-12 palabras."
                        ),
                        catalog_title_ok,
                    )
                ]
                if validated
                else []
            ),
            ft.ResponsiveRow(
                controls=dropdown_cards(data["catalog"]["fields"], catalog_controls),
                spacing=10,
                run_spacing=10,
            ),
            ft.Text("Etiquetas del tesauro", size=14, weight=ft.FontWeight.BOLD),
            ft.Column(
                controls=checkbox_rows(data["catalog"]["tags"], tag_controls, saved_tags),
                spacing=8,
            ),
            ft.Divider(height=22),
            section_header("4", data["scorm"]["title"], data["scorm"]["description"]),
            ft.ResponsiveRow(
                controls=dropdown_cards(data["scorm"]["fields"], scorm_controls),
                spacing=10,
                run_spacing=10,
            ),
            ft.ElevatedButton("Validar prueba", on_click=validate),
            build_result_box(state["feedback"]["p10"]),
        ],
        spacing=14,
    )
    return question_block(
        title=data["title"],
        statement=data["statement"],
        content=content,
    )
