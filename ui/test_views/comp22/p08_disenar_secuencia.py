import json
from datetime import datetime
from pathlib import Path

import flet as ft

from core.storage import save_result
from ui.components import question_block


TEST_ID = "P08"
DATA_PATH = Path("data/p08_comp22_b2.json")


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


def image_or_placeholder(src: str | None, label: str = "Recurso", width: int = 180, height: int = 112) -> ft.Control:
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


def find_resource(resources: list[dict], resource_id: str) -> dict | None:
    return next((resource for resource in resources if resource["id"] == resource_id), None)


def get_sequence_ids(state: dict) -> list[str]:
    return list(state["responses"].get("p08_sequence", []))


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


def build_resource_feedback(resource: dict, selected: bool, validated: bool) -> ft.Control:
    if not validated:
        return ft.Container()

    passed = selected == bool(resource["expected"])
    return inline_feedback(
        f"{'Correcta' if passed else 'Revisar'}. {resource['feedback']}",
        passed,
    )


def build_test_p08(state: dict, refresh_view) -> ft.Control:
    test_data = load_test_data()
    validated = state["feedback"]["p08"]["ok"] is not None
    resources = test_data["resource_bank"]["resources"]
    saved_modifications = state["responses"].get("p08_modifications", [])
    saved_safety = state["responses"].get("p08_safety", [])
    saved_matrix = state["responses"].get("p08_evaluation_matrix", [])
    saved_export = state["responses"].get("p08_export", {})

    export_controls = {
        field["id"]: build_radio_group(
            field["options"],
            saved_export.get(field["id"]),
            validated,
        )
        for field in test_data["export"]["fields"]
    }
    modification_checkboxes, modification_cards = build_checkbox_cards(
        test_data["modifications"]["options"],
        saved_modifications,
        validated,
    )
    safety_checkboxes, safety_cards = build_checkbox_cards(
        test_data["safety"]["options"],
        saved_safety,
        validated,
    )
    matrix_checkboxes, matrix_cards = build_checkbox_cards(
        test_data["evaluation_matrix"]["options"],
        saved_matrix,
        validated,
    )

    def persist_form():
        state["responses"]["p08_modifications"] = get_selected_ids(modification_checkboxes)
        state["responses"]["p08_safety"] = get_selected_ids(safety_checkboxes)
        state["responses"]["p08_evaluation_matrix"] = get_selected_ids(matrix_checkboxes)
        state["responses"]["p08_export"] = {
            field_id: control.value for field_id, control in export_controls.items()
        }

    def set_sequence(new_sequence: list[str]):
        state["responses"]["p08_sequence"] = new_sequence
        persist_form()
        update_sequence_lists()

    def add_resource(resource_id: str):
        current_sequence = get_sequence_ids(state)
        if resource_id not in current_sequence:
            set_sequence([*current_sequence, resource_id])

    def remove_resource(resource_id: str):
        current_sequence = get_sequence_ids(state)
        set_sequence([item for item in current_sequence if item != resource_id])

    def move_resource(index: int, delta: int):
        current_sequence = get_sequence_ids(state)
        target = index + delta
        if target < 0 or target >= len(current_sequence):
            return
        reordered = current_sequence[:]
        reordered[index], reordered[target] = reordered[target], reordered[index]
        set_sequence(reordered)

    def validate(e):
        persist_form()
        current_sequence = get_sequence_ids(state)
        selected_modifications = state["responses"].get("p08_modifications", [])
        selected_safety = state["responses"].get("p08_safety", [])
        selected_matrix = state["responses"].get("p08_evaluation_matrix", [])
        selected_export = state["responses"].get("p08_export", {})

        expected_resources = [resource["id"] for resource in resources if resource["expected"]]
        unexpected_resources = [resource["id"] for resource in resources if not resource["expected"]]
        selected_expected = [resource_id for resource_id in current_sequence if resource_id in expected_resources]
        selected_unexpected = [resource_id for resource_id in current_sequence if resource_id in unexpected_resources]
        required_order = test_data["resource_bank"]["required_order"]

        resource_selection_ok = set(selected_expected) == set(expected_resources) and not selected_unexpected
        sequence_order_ok = selected_expected == required_order
        created_elements = [
            resource_id
            for resource_id in current_sequence
            if bool(find_resource(resources, resource_id) and find_resource(resources, resource_id)["created_by_teacher"])
        ]
        modified_elements = [
            resource_id
            for resource_id in current_sequence
            if bool(find_resource(resources, resource_id) and find_resource(resources, resource_id)["modified"])
        ]
        accessibility_elements = [
            resource_id
            for resource_id in current_sequence
            if bool(find_resource(resources, resource_id) and find_resource(resources, resource_id)["accessibility"])
        ]
        created_ok = len(created_elements) >= 3 and "own_guided_worksheet" in created_elements and "own_rubric" in created_elements
        modified_ok = "editable_infographic" in modified_elements and "captioned_video" in modified_elements
        accessibility_ok = "editable_infographic" in accessibility_elements and "captioned_video" in accessibility_elements

        expected_modifications = [
            option["id"] for option in test_data["modifications"]["options"] if option["expected"]
        ]
        modifications_ok = set(selected_modifications) == set(expected_modifications)

        expected_safety = [
            option["id"] for option in test_data["safety"]["options"] if option["expected"]
        ]
        safety_ok = set(selected_safety) == set(expected_safety)

        expected_matrix = [
            option["id"] for option in test_data["evaluation_matrix"]["options"] if option["expected"]
        ]
        matrix_ok = set(selected_matrix) == set(expected_matrix)

        export_checks = []
        export_points = 0
        expected_export = {}
        for field in test_data["export"]["fields"]:
            expected = get_expected_id(field["options"])
            selected = selected_export.get(field["id"])
            field_ok = selected == expected
            expected_export[field["id"]] = expected
            export_points += field["weight"] if field_ok else 0
            export_checks.append(
                {
                    "check_id": f"export_{field['id']}",
                    "label": field["label"],
                    "passed": field_ok,
                    "weight": field["weight"],
                    "evidence": str(selected),
                }
            )

        export_ok = all(check["passed"] for check in export_checks)
        selection_points = round(
            sum(
                1
                for resource in resources
                if (resource["id"] in current_sequence) == bool(resource["expected"])
            )
            / len(resources)
            * 18
        )
        score = 0
        score += selection_points
        score += 12 if sequence_order_ok else 0
        score += 10 if created_ok else 0
        score += 10 if modified_ok and accessibility_ok and modifications_ok else 0
        score += 15 if safety_ok else 0
        score += export_points
        score += 15 if matrix_ok else 0

        ok = (
            score >= 85
            and resource_selection_ok
            and sequence_order_ok
            and created_ok
            and modified_ok
            and accessibility_ok
            and modifications_ok
            and safety_ok
            and export_ok
            and matrix_ok
        )

        message = test_data["feedback"]["success"] if ok else test_data["feedback"]["failure"]
        state["completed"]["p08"] = ok
        state["feedback"]["p08"] = {"ok": ok, "message": message}

        result = {
            "test_id": TEST_ID,
            "scenario_id": test_data["scenario_id"],
            "scenario_title": test_data["scenario_title"],
            "timestamp_utc": datetime.utcnow().isoformat(),
            "score_0_100": score,
            "level_hint": "B2" if ok else "B1",
            "payload": {
                "selected_sequence": current_sequence,
                "expected_resources": expected_resources,
                "required_order": required_order,
                "selected_modifications": selected_modifications,
                "expected_modifications": expected_modifications,
                "selected_safety": selected_safety,
                "expected_safety": expected_safety,
                "selected_export": selected_export,
                "expected_export": expected_export,
                "selected_evaluation_matrix": selected_matrix,
                "expected_evaluation_matrix": expected_matrix,
            },
            "checks": [
                {
                    "check_id": "resource_integration",
                    "label": "Integra contenidos digitales diversos y descarta los no adecuados",
                    "passed": resource_selection_ok,
                    "weight": 18,
                    "evidence": ", ".join(current_sequence),
                },
                {
                    "check_id": "sequence_structure",
                    "label": "Ordena la unidad como secuencia de aprendizaje coherente",
                    "passed": sequence_order_ok,
                    "weight": 12,
                    "evidence": ", ".join(current_sequence),
                },
                {
                    "check_id": "own_elements",
                    "label": "Incorpora elementos de creación propia necesarios para la secuencia",
                    "passed": created_ok,
                    "weight": 10,
                    "evidence": ", ".join(created_elements),
                },
                {
                    "check_id": "modification_accessibility",
                    "label": "Aplica modificaciones didácticas y accesibles sobre contenidos integrados",
                    "passed": modified_ok and accessibility_ok and modifications_ok,
                    "weight": 10,
                    "evidence": ", ".join(selected_modifications),
                },
                {
                    "check_id": "shared_editing_safety",
                    "label": "Usa medidas de seguridad para edición compartida",
                    "passed": safety_ok,
                    "weight": 15,
                    "evidence": ", ".join(selected_safety),
                },
                *export_checks,
                {
                    "check_id": "systematic_evaluation",
                    "label": "Aplica un procedimiento sistemático de evaluación previa de contenidos",
                    "passed": matrix_ok,
                    "weight": 15,
                    "evidence": ", ".join(selected_matrix),
                },
            ],
            "notes": [message],
        }

        saved_path = save_result(result)
        state["responses"]["p08_saved_path"] = str(saved_path)
        refresh_view()

    def build_library_card(resource: dict, index: int) -> ft.Control:
        selected = resource["id"] in get_sequence_ids(state)
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(f"Contenido {index + 1:02d}", size=13, weight=ft.FontWeight.BOLD, color="#374151"),
                    image_or_placeholder(resource["thumbnail"], resource["title"], width=220, height=132),
                    ft.Text(resource["title"], size=15, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{resource['source']} · {resource['format']}", size=12, color="#6B7280"),
                    ft.Text(resource["preview"], size=13, color="#4B5563"),
                    ft.Row(
                        controls=[
                            ft.ElevatedButton(
                                "Añadir",
                                on_click=lambda e, resource_id=resource["id"]: add_resource(resource_id),
                            ),
                            ft.OutlinedButton(
                                "Quitar",
                                on_click=lambda e, resource_id=resource["id"]: remove_resource(resource_id),
                            ),
                        ],
                        spacing=8,
                    ),
                    build_resource_feedback(resource, selected, validated),
                ],
                spacing=9,
            ),
            col={"xs": 12, "md": 6},
            bgcolor="#FFFFFF",
            border=ft.border.all(1, "#E5E7EB"),
            border_radius=10,
            padding=12,
        )

    def build_sequence_card(resource_id: str, index: int) -> ft.Control:
        resource = find_resource(resources, resource_id)
        if not resource:
            return ft.Container()

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(str(index + 1), size=13, weight=ft.FontWeight.BOLD, color="#1E40AF"),
                        width=30,
                        height=30,
                        border_radius=999,
                        bgcolor="#DBEAFE",
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(resource["title"], size=14, weight=ft.FontWeight.BOLD),
                            ft.Text(resource["format"], size=12, color="#6B7280"),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.KEYBOARD_ARROW_UP,
                        tooltip="Subir",
                        on_click=lambda e, i=index: move_resource(i, -1),
                        disabled=index == 0,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.KEYBOARD_ARROW_DOWN,
                        tooltip="Bajar",
                        on_click=lambda e, i=index: move_resource(i, 1),
                        disabled=index == len(get_sequence_ids(state)) - 1,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        tooltip="Quitar",
                        on_click=lambda e, rid=resource_id: remove_resource(rid),
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

    def build_preview_card(resource_id: str) -> ft.Control:
        resource = find_resource(resources, resource_id)
        if not resource:
            return ft.Container()

        badges = []
        if resource["created_by_teacher"]:
            badges.append(("Propio", "#ECFDF5", "#047857"))
        if resource["modified"]:
            badges.append(("Modificado", "#EFF6FF", "#1D4ED8"))
        if resource["accessibility"]:
            badges.append(("Accesible", "#FEF3C7", "#92400E"))

        return ft.Container(
            content=ft.Column(
                controls=[
                    image_or_placeholder(resource["thumbnail"], resource["title"], width=320, height=170),
                    ft.Text(resource["title"], size=14, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text(label, size=11, color=color, weight=ft.FontWeight.W_600),
                                bgcolor=bg,
                                border_radius=999,
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            )
                            for label, bg, color in badges
                        ],
                        spacing=6,
                        wrap=True,
                    ),
                ],
                spacing=8,
            ),
            bgcolor="#FFFFFF",
            border=ft.border.all(1, "#E5E7EB"),
            border_radius=10,
            padding=10,
        )

    def build_empty_sequence_notice() -> ft.Control:
        return ft.Container(
            content=ft.Text("La secuencia todavía no tiene contenidos integrados.", size=13, color="#6B7280"),
            bgcolor="#F9FAFB",
            border=ft.border.all(1, "#E5E7EB"),
            border_radius=10,
            padding=14,
        )

    def build_sequence_controls() -> list[ft.Control]:
        current_sequence = get_sequence_ids(state)
        if not current_sequence:
            return [build_empty_sequence_notice()]
        return [
            build_sequence_card(resource_id, index)
            for index, resource_id in enumerate(current_sequence)
        ]

    def build_preview_controls() -> list[ft.Control]:
        current_sequence = get_sequence_ids(state)
        if not current_sequence:
            return [build_empty_sequence_notice()]
        return [build_preview_card(resource_id) for resource_id in current_sequence]

    sequence_column = ft.Column(controls=build_sequence_controls(), spacing=10)
    preview_column = ft.Column(controls=build_preview_controls(), spacing=10)

    def update_sequence_lists():
        sequence_column.controls = build_sequence_controls()
        preview_column.controls = build_preview_controls()
        sequence_column.update()
        preview_column.update()

    export_sections = []
    for field in test_data["export"]["fields"]:
        export_sections.append(
            ft.Column(
                controls=[
                    ft.Text(field["label"], size=15, weight=ft.FontWeight.BOLD),
                    export_controls[field["id"]],
                ],
                spacing=8,
            )
        )

    content = ft.Column(
        controls=[
            ft.Text(test_data["intro"], size=15, weight=ft.FontWeight.W_600),
            info_panel(test_data["classroom"]["title"], test_data["classroom"]["lines"], "#F0FDF4"),
            ft.Divider(height=24),
            section_title(test_data["resource_bank"]["title"]),
            ft.Text(test_data["resource_bank"]["description"], size=14),
            ft.ResponsiveRow(
                controls=[
                    ft.Container(
                        col={"xs": 12, "xl": 7},
                        content=ft.Column(
                            controls=[
                                ft.Text("Biblioteca de contenidos", size=16, weight=ft.FontWeight.BOLD),
                                ft.ResponsiveRow(
                                    controls=[
                                        build_library_card(resource, index)
                                        for index, resource in enumerate(resources)
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
                                ft.Text("Secuencia construida", size=16, weight=ft.FontWeight.BOLD),
                                sequence_column,
                                ft.Divider(height=18),
                                ft.Text("Vista de unidad", size=16, weight=ft.FontWeight.BOLD),
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
            section_title(test_data["modifications"]["title"]),
            ft.Text(test_data["modifications"]["description"], size=14),
            ft.ResponsiveRow(controls=modification_cards, spacing=8, run_spacing=8),
            ft.Divider(height=24),
            section_title(test_data["safety"]["title"]),
            ft.Text(test_data["safety"]["description"], size=14),
            ft.ResponsiveRow(controls=safety_cards, spacing=8, run_spacing=8),
            ft.Divider(height=24),
            section_title(test_data["export"]["title"]),
            ft.Text(test_data["export"]["description"], size=14),
            *export_sections,
            ft.Divider(height=24),
            section_title(test_data["evaluation_matrix"]["title"]),
            ft.Text(test_data["evaluation_matrix"]["description"], size=14),
            ft.ResponsiveRow(controls=matrix_cards, spacing=8, run_spacing=8),
            ft.Container(height=8),
            ft.ElevatedButton("Validar prueba", on_click=validate),
            build_result_box(state["feedback"]["p08"]),
        ],
        spacing=12,
    )

    return question_block(
        title=test_data["title"],
        statement=test_data["statement"],
        content=content,
    )
