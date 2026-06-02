import json
from datetime import datetime
from pathlib import Path

import flet as ft

from core.storage import save_result
from ui.components import question_block


TEST_ID = "P07"
DATA_PATH = Path("data/p07_comp22_b1.json")


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


def image_or_placeholder(src: str | None, label: str = "Imagen pendiente", width: int = 128, height: int = 82) -> ft.Control:
    if src and Path(src).exists():
        return ft.Image(src=src, width=width, height=height, fit="cover")

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(ft.Icons.IMAGE_OUTLINED, size=24, color="#6B7280"),
                ft.Text(label, size=10, color="#6B7280", text_align=ft.TextAlign.CENTER),
            ],
            spacing=4,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        width=width,
        height=height,
        bgcolor="#F3F4F6",
        border=ft.border.all(1, "#D1D5DB"),
        border_radius=8,
        alignment=ft.Alignment.CENTER,
        padding=6,
    )


def get_expected_id(options: list[dict]) -> str | None:
    return next((option["id"] for option in options if option["expected"]), None)


def find_block(blocks: list[dict], block_id: str) -> dict | None:
    return next((block for block in blocks if block["id"] == block_id), None)


def get_block_ids(state: dict) -> list[str]:
    return list(state["responses"].get("p07_blocks", []))


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


def build_block_feedback(block: dict, selected: bool, validated: bool) -> ft.Control:
    if not validated:
        return ft.Container()

    passed = selected == bool(block["expected"])
    return inline_feedback(
        f"{'Correcta' if passed else 'Revisar'}. {block['feedback']}",
        passed,
    )


def build_test_p07(state: dict, refresh_view) -> ft.Control:
    test_data = load_test_data()
    validated = state["feedback"]["p07"]["ok"] is not None
    blocks = test_data["builder"]["blocks"]
    saved_license = state["responses"].get("p07_license")
    saved_metadata = state["responses"].get("p07_metadata", {})

    license_control = build_radio_group(
        test_data["license"]["options"],
        saved_license,
        validated,
    )
    metadata_controls = {
        field["id"]: build_radio_group(
            field["options"],
            saved_metadata.get(field["id"]),
            validated,
        )
        for field in test_data["metadata"]["fields"]
    }

    def persist_form():
        state["responses"]["p07_license"] = license_control.value
        state["responses"]["p07_metadata"] = {
            field_id: control.value for field_id, control in metadata_controls.items()
        }

    def set_blocks(new_blocks: list[str]):
        state["responses"]["p07_blocks"] = new_blocks
        persist_form()
        update_builder_lists()

    def add_block(block_id: str):
        current_blocks = get_block_ids(state)
        if block_id not in current_blocks:
            set_blocks([*current_blocks, block_id])

    def remove_block(block_id: str):
        current_blocks = get_block_ids(state)
        set_blocks([item for item in current_blocks if item != block_id])

    def move_block(index: int, delta: int):
        current_blocks = get_block_ids(state)
        target = index + delta
        if target < 0 or target >= len(current_blocks):
            return
        reordered = current_blocks[:]
        reordered[index], reordered[target] = reordered[target], reordered[index]
        set_blocks(reordered)

    def validate(e):
        persist_form()
        selected_license = state["responses"].get("p07_license")
        selected_metadata = state["responses"].get("p07_metadata", {})
        current_blocks = get_block_ids(state)

        expected_blocks = [block["id"] for block in blocks if block["expected"]]
        unexpected_blocks = [block["id"] for block in blocks if not block["expected"]]
        selected_expected = [block_id for block_id in current_blocks if block_id in expected_blocks]
        selected_unexpected = [block_id for block_id in current_blocks if block_id in unexpected_blocks]

        required_order = test_data["builder"]["required_order"]
        order_ok = selected_expected == required_order
        expected_selection_ok = set(selected_expected) == set(expected_blocks) and not selected_unexpected
        accessibility_ok = any(
            bool(find_block(blocks, block_id) and find_block(blocks, block_id)["accessibility"])
            for block_id in current_blocks
        )

        selection_points = round(
            sum(
                1
                for block in blocks
                if (block["id"] in current_blocks) == bool(block["expected"])
            )
            / len(blocks)
            * 30
        )
        order_points = 20 if order_ok else 0
        accessibility_points = 15 if accessibility_ok and "accessible_diagram" in current_blocks else 0

        license_expected = get_expected_id(test_data["license"]["options"])
        license_ok = selected_license == license_expected
        license_points = 15 if license_ok else 0

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
        score = selection_points + order_points + accessibility_points + license_points + metadata_points
        ok = (
            score >= 80
            and expected_selection_ok
            and order_ok
            and accessibility_ok
            and license_ok
            and metadata_ok
        )

        message = test_data["feedback"]["success"] if ok else test_data["feedback"]["failure"]
        state["completed"]["p07"] = ok
        state["feedback"]["p07"] = {"ok": ok, "message": message}

        result = {
            "test_id": TEST_ID,
            "scenario_id": test_data["scenario_id"],
            "scenario_title": test_data["scenario_title"],
            "timestamp_utc": datetime.utcnow().isoformat(),
            "score_0_100": score,
            "level_hint": "B1" if ok else "A2",
            "payload": {
                "selected_blocks": current_blocks,
                "expected_blocks": expected_blocks,
                "required_order": required_order,
                "selected_license": selected_license,
                "expected_license": license_expected,
                "selected_metadata": selected_metadata,
                "expected_metadata": expected_metadata,
            },
            "checks": [
                {
                    "check_id": "block_selection",
                    "label": "Selecciona y descarta elementos segun criterios didacticos, disciplinares y tecnicos",
                    "passed": expected_selection_ok,
                    "weight": 30,
                    "evidence": ", ".join(current_blocks),
                },
                {
                    "check_id": "didactic_order",
                    "label": "Ordena la ficha adaptada con una secuencia didactica adecuada",
                    "passed": order_ok,
                    "weight": 20,
                    "evidence": ", ".join(current_blocks),
                },
                {
                    "check_id": "accessibility_elements",
                    "label": "Incluye elementos de accesibilidad en el contenido modificado",
                    "passed": accessibility_ok,
                    "weight": 15,
                    "evidence": ", ".join(current_blocks),
                },
                {
                    "check_id": "compatible_license",
                    "label": "Incluye licencia compatible con la obra original",
                    "passed": license_ok,
                    "weight": 15,
                    "evidence": str(selected_license),
                },
                *metadata_checks,
            ],
            "notes": [message],
        }

        saved_path = save_result(result)
        state["responses"]["p07_saved_path"] = str(saved_path)
        refresh_view()

    def build_library_card(block: dict, index: int) -> ft.Control:
        selected = block["id"] in get_block_ids(state)
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(f"Recurso {index + 1:02d}", size=13, weight=ft.FontWeight.BOLD, color="#374151"),
                    ft.Container(
                        content=image_or_placeholder(block["thumbnail"], width=220, height=135),
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Row(
                        controls=[
                            ft.ElevatedButton(
                                "Añadir",
                                on_click=lambda e, block_id=block["id"]: add_block(block_id),
                            ),
                            ft.OutlinedButton(
                                "Quitar",
                                on_click=lambda e, block_id=block["id"]: remove_block(block_id),
                            ),
                        ],
                        spacing=8,
                    ),
                    build_block_feedback(block, selected, validated),
                ],
                spacing=10,
            ),
            col={"xs": 12, "md": 6},
            bgcolor="#FFFFFF",
            border=ft.border.all(1, "#E5E7EB"),
            border_radius=10,
            padding=12,
        )

    def build_selected_card(block_id: str, index: int) -> ft.Control:
        block = find_block(blocks, block_id)
        if not block:
            return ft.Container()

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(str(index + 1), size=13, weight=ft.FontWeight.BOLD, color="#1E40AF"),
                        width=28,
                        height=28,
                        border_radius=999,
                        bgcolor="#DBEAFE",
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Container(
                        content=image_or_placeholder(block["thumbnail"], width=180, height=110),
                        alignment=ft.Alignment.CENTER_LEFT,
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.KEYBOARD_ARROW_UP,
                        tooltip="Subir",
                        on_click=lambda e, i=index: move_block(i, -1),
                        disabled=index == 0,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.KEYBOARD_ARROW_DOWN,
                        tooltip="Bajar",
                        on_click=lambda e, i=index: move_block(i, 1),
                        disabled=index == len(get_block_ids(state)) - 1,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        tooltip="Quitar",
                        on_click=lambda e, block_id=block_id: remove_block(block_id),
                    ),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor="#F9FAFB",
            border=ft.border.all(1, "#E5E7EB"),
            border_radius=10,
            padding=10,
        )

    def build_preview_card(block_id: str) -> ft.Control:
        block = find_block(blocks, block_id)
        if not block:
            return ft.Container()

        return ft.Container(
            content=image_or_placeholder(block["thumbnail"], width=360, height=220),
            alignment=ft.Alignment.CENTER,
            bgcolor="#FFFFFF",
            border=ft.border.all(1, "#E5E7EB"),
            border_radius=10,
            padding=12,
        )

    def build_empty_selected_notice() -> ft.Control:
        return ft.Container(
            content=ft.Text("La ficha adaptada todavia no tiene bloques.", size=13, color=ft.Colors.GREY_700),
            bgcolor="#F9FAFB",
            border=ft.border.all(1, "#E5E7EB"),
            border_radius=10,
            padding=14,
        )

    def build_empty_preview_notice() -> ft.Control:
        return ft.Container(
            content=ft.Text("Añade bloques desde la biblioteca para ver la ficha.", size=13, color=ft.Colors.GREY_700),
            bgcolor="#FFFFFF",
            border=ft.border.all(1, "#E5E7EB"),
            border_radius=10,
            padding=14,
        )

    def build_selected_controls() -> list[ft.Control]:
        current_blocks = get_block_ids(state)
        if not current_blocks:
            return [build_empty_selected_notice()]
        return [
            build_selected_card(block_id, index)
            for index, block_id in enumerate(current_blocks)
        ]

    def build_preview_controls() -> list[ft.Control]:
        current_blocks = get_block_ids(state)
        if not current_blocks:
            return [build_empty_preview_notice()]
        return [build_preview_card(block_id) for block_id in current_blocks]

    selected_blocks_column = ft.Column(controls=build_selected_controls(), spacing=10)
    preview_column = ft.Column(controls=build_preview_controls(), spacing=10)

    def update_builder_lists():
        selected_blocks_column.controls = build_selected_controls()
        preview_column.controls = build_preview_controls()
        selected_blocks_column.update()
        preview_column.update()

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
            ft.ResponsiveRow(
                controls=[
                    ft.Container(
                        col={"xs": 12, "lg": 6},
                        content=ft.Column(
                            controls=[
                                info_panel(test_data["source"]["title"], test_data["source"]["lines"]),
                                image_or_placeholder(test_data["source"]["image"], "Recurso original", 460, 250),
                            ],
                            spacing=12,
                        ),
                    ),
                    ft.Container(
                        col={"xs": 12, "lg": 6},
                        content=info_panel(test_data["classroom"]["title"], test_data["classroom"]["lines"], "#F0FDF4"),
                    ),
                ],
                spacing=16,
                run_spacing=16,
            ),
            ft.Divider(height=24),
            section_title(test_data["builder"]["title"]),
            ft.Text(test_data["builder"]["description"], size=14),
            ft.ResponsiveRow(
                controls=[
                    ft.Container(
                        col={"xs": 12, "xl": 7},
                        content=ft.Column(
                            controls=[
                                ft.Text("Biblioteca de elementos", size=16, weight=ft.FontWeight.BOLD),
                                ft.ResponsiveRow(
                                    controls=[
                                        build_library_card(block, index)
                                        for index, block in enumerate(blocks)
                                    ],
                                    spacing=8,
                                    run_spacing=8,
                                ),
                            ],
                            spacing=10,
                        ),
                    ),
                    ft.Container(
                        col={"xs": 12, "xl": 5},
                        content=ft.Column(
                            controls=[
                                ft.Text("Ficha adaptada", size=16, weight=ft.FontWeight.BOLD),
                                selected_blocks_column,
                                ft.Divider(height=18),
                                ft.Text("Vista previa", size=16, weight=ft.FontWeight.BOLD),
                                preview_column,
                            ],
                            spacing=10,
                        ),
                    ),
                ],
                spacing=18,
                run_spacing=18,
            ),
            ft.Divider(height=24),
            section_title(test_data["license"]["title"]),
            ft.Text(test_data["license"]["description"], size=14),
            license_control,
            ft.Divider(height=24),
            section_title(test_data["metadata"]["title"]),
            ft.Text(test_data["metadata"]["description"], size=14),
            *metadata_sections,
            ft.Container(height=8),
            ft.ElevatedButton("Validar prueba", on_click=validate),
            build_result_box(state["feedback"]["p07"]),
        ],
        spacing=12,
    )

    return question_block(
        title=test_data["title"],
        statement=test_data["statement"],
        content=content,
    )
