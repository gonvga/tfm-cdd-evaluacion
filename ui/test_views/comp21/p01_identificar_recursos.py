import json
from datetime import datetime
from pathlib import Path

import flet as ft

from core.storage import save_result
from ui.components import question_block


TEST_ID = "P01"
DATA_PATH = Path("data/p01_comp21_a1.json")


def load_test_data() -> dict:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


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
                ft.Text(
                    feedback_data["message"],
                    size=14,
                    color=ft.Colors.WHITE,
                ),
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


def build_test_p01(state: dict, refresh_view) -> ft.Control:
    test_data = load_test_data()
    classification = test_data["classification"]
    search_tools = test_data["search_tools"]
    metadata_question = test_data["metadata_question"]
    organization = test_data["organization"]

    saved_classification = state["responses"].get("p01_classification", {})
    saved_search_tools = state["responses"].get("p01_search_tools", [])
    saved_metadata = state["responses"].get("p01_metadata_answer")
    saved_folder_name = state["responses"].get("p01_folder_name", "")
    saved_files = state["responses"].get("p01_folder_files", [])

    category_options = [
        ft.dropdown.Option(category["id"], category["label"])
        for category in classification["categories"]
    ]

    classification_dropdowns = {}
    classification_rows = []
    for label in classification["labels"]:
        dropdown = ft.Dropdown(
            value=saved_classification.get(label["id"]),
            options=category_options,
            width=260,
        )
        classification_dropdowns[label["id"]] = dropdown
        classification_rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(label["text"])),
                    ft.DataCell(dropdown),
                ]
            )
        )

    search_checkboxes = {}
    search_cards = []
    for option in search_tools["options"]:
        checkbox = ft.Checkbox(value=option["id"] in saved_search_tools)
        search_checkboxes[option["id"]] = checkbox
        search_cards.append(
            ft.Container(
                content=ft.Row(
                    controls=[
                        checkbox,
                        ft.Column(
                            controls=[
                                ft.Text(option["label"], size=15, weight=ft.FontWeight.BOLD),
                                ft.Text(option["description"], size=13, color=ft.Colors.GREY_700),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                col={"xs": 12, "md": 6},
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=10,
            )
        )

    metadata_radio = ft.RadioGroup(
        value=saved_metadata,
        content=ft.Column(
            controls=[
                ft.Radio(value=option["id"], label=option["text"])
                for option in metadata_question["options"]
            ],
            spacing=4,
        ),
    )

    folder_name = ft.TextField(
        label="Nombre de la carpeta",
        value=saved_folder_name,
        hint_text=organization["folder_hint"],
    )

    file_checkboxes = {}
    file_rows = []
    for file_item in organization["files"]:
        checkbox = ft.Checkbox(value=file_item["id"] in saved_files)
        file_checkboxes[file_item["id"]] = checkbox
        file_rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(checkbox),
                    ft.DataCell(ft.Text(file_item["name"])),
                    ft.DataCell(ft.Text(file_item["description"])),
                ]
            )
        )

    def validate(e):
        classification_answers = {
            label_id: dropdown.value
            for label_id, dropdown in classification_dropdowns.items()
        }
        selected_search_tools = [
            option_id
            for option_id, checkbox in search_checkboxes.items()
            if checkbox.value
        ]
        metadata_answer = metadata_radio.value
        folder_value = (folder_name.value or "").strip()
        selected_files = [
            file_id
            for file_id, checkbox in file_checkboxes.items()
            if checkbox.value
        ]

        state["responses"]["p01_classification"] = classification_answers
        state["responses"]["p01_search_tools"] = selected_search_tools
        state["responses"]["p01_metadata_answer"] = metadata_answer
        state["responses"]["p01_folder_name"] = folder_value
        state["responses"]["p01_folder_files"] = selected_files

        expected_classification = {
            label["id"]: label["expected_category"]
            for label in classification["labels"]
        }
        expected_search_tools = [
            option["id"] for option in search_tools["options"] if option["expected"]
        ]
        expected_metadata = next(
            option["id"] for option in metadata_question["options"] if option["expected"]
        )
        expected_files = [
            file_item["id"]
            for file_item in organization["files"]
            if file_item["expected_in_folder"]
        ]

        classification_correct = [
            label_id
            for label_id, expected in expected_classification.items()
            if classification_answers.get(label_id) == expected
        ]
        classification_ok = len(classification_correct) == len(expected_classification)

        search_missing = [
            option_id for option_id in expected_search_tools if option_id not in selected_search_tools
        ]
        search_wrong = [
            option_id for option_id in selected_search_tools if option_id not in expected_search_tools
        ]
        search_ok = not search_missing and not search_wrong

        metadata_ok = metadata_answer == expected_metadata

        folder_lower = folder_value.lower()
        folder_name_ok = any(
            keyword.lower() in folder_lower
            for keyword in organization["valid_folder_keywords"]
        )
        file_missing = [file_id for file_id in expected_files if file_id not in selected_files]
        file_wrong = [file_id for file_id in selected_files if file_id not in expected_files]
        files_ok = not file_missing and not file_wrong
        organization_ok = folder_name_ok and files_ok

        classification_score = round((len(classification_correct) / len(expected_classification)) * 35)
        search_score = 20 if search_ok else max(0, 20 - (len(search_missing) * 8) - (len(search_wrong) * 6))
        metadata_score = 15 if metadata_ok else 0
        organization_score = (
            (10 if folder_name_ok else 0)
            + (20 if files_ok else max(0, 20 - (len(file_missing) * 7) - (len(file_wrong) * 7)))
        )
        score = min(100, classification_score + search_score + metadata_score + organization_score)

        ok = classification_ok and search_ok and metadata_ok and organization_ok
        state["completed"]["p01"] = ok

        message = test_data["feedback"]["success"] if ok else test_data["feedback"]["failure"]

        state["feedback"]["p01"] = {
            "ok": ok,
            "message": message,
        }

        result = {
            "test_id": TEST_ID,
            "scenario_id": test_data["scenario_id"],
            "scenario_title": test_data["scenario_title"],
            "timestamp_utc": datetime.utcnow().isoformat(),
            "score_0_100": score,
            "level_hint": "A1" if ok else "A0",
            "payload": {
                "classification_answers": classification_answers,
                "expected_classification": expected_classification,
                "selected_search_tools": selected_search_tools,
                "expected_search_tools": expected_search_tools,
                "metadata_answer": metadata_answer,
                "expected_metadata": expected_metadata,
                "folder_name": folder_value,
                "folder_name_ok": folder_name_ok,
                "selected_files": selected_files,
                "expected_files": expected_files,
                "file_missing": file_missing,
                "file_wrong": file_wrong,
            },
            "checks": [
                {
                    "check_id": "quality_criteria_classification",
                    "label": "Clasifica criterios científicos, técnicos y didácticos",
                    "passed": classification_ok,
                    "weight": 35,
                    "evidence": str(classification_answers),
                },
                {
                    "check_id": "neutral_search_tools",
                    "label": "Selecciona buscadores neutros o académicos",
                    "passed": search_ok,
                    "weight": 20,
                    "evidence": ", ".join(selected_search_tools),
                },
                {
                    "check_id": "metadata_identification",
                    "label": "Identifica los metadatos como mecanismo de indexación",
                    "passed": metadata_ok,
                    "weight": 15,
                    "evidence": str(metadata_answer),
                },
                {
                    "check_id": "resource_organization",
                    "label": "Crea una carpeta pertinente y organiza recursos educativos",
                    "passed": organization_ok,
                    "weight": 30,
                    "evidence": f"{folder_value}: {', '.join(selected_files)}",
                },
            ],
            "notes": [message],
        }

        saved_path = save_result(result)
        state["responses"]["p01_saved_path"] = str(saved_path)

        refresh_view()

    content = ft.Column(
        controls=[
            ft.Text(
                test_data["intro"],
                size=15,
                weight=ft.FontWeight.W_600,
            ),
            section_title(classification["title"]),
            ft.Text(classification["description"], size=14),
            build_info_panel(
                classification["resource"]["title"],
                [
                    f"Fuente: {classification['resource']['source']}",
                    classification["resource"]["context"],
                ],
            ),
            ft.ResponsiveRow(
                controls=[
                    ft.Container(
                        content=build_info_panel(category["label"], [category["description"]]),
                        col={"xs": 12, "md": 4},
                    )
                    for category in classification["categories"]
                ],
                spacing=8,
                run_spacing=8,
            ),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Etiqueta")),
                    ft.DataColumn(ft.Text("Categoría")),
                ],
                rows=classification_rows,
            ),
            ft.Divider(height=24),
            section_title(search_tools["title"]),
            ft.Text(search_tools["description"], size=14),
            ft.ResponsiveRow(controls=search_cards, spacing=8, run_spacing=8),
            ft.Divider(height=24),
            section_title(metadata_question["title"]),
            ft.Text(metadata_question["prompt"], size=14),
            metadata_radio,
            ft.Divider(height=24),
            section_title(organization["title"]),
            ft.Text(organization["description"], size=14),
            folder_name,
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Mover")),
                    ft.DataColumn(ft.Text("Archivo")),
                    ft.DataColumn(ft.Text("Descripción")),
                ],
                rows=file_rows,
            ),
            ft.Container(height=8),
            ft.ElevatedButton("Validar prueba", on_click=validate),
            build_result_box(state["feedback"]["p01"]),
        ],
        spacing=12,
    )

    return question_block(
        title=test_data["title"],
        statement=test_data["statement"],
        content=content,
    )
