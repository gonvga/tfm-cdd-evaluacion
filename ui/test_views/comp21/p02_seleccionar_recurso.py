import json
from datetime import datetime

import flet as ft

from core.storage import save_result
from core.paths import resource_path
from ui.components import checkbox_feedback, question_block


TEST_ID = "P02"
DATA_PATH = resource_path("data", "p02_comp21_a2.json")


def load_test_data() -> dict:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def build_result_box(feedback_data: dict) -> ft.Control:
    if feedback_data["ok"] is None:
        return ft.Container()

    ok = feedback_data["ok"]
    controls = [
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
    ]

    return ft.Container(
        content=ft.Column(
            controls=controls,
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


def build_checkbox_cards(
    options: list[dict],
    saved_ids: list[str],
    validated: bool = False,
) -> tuple[dict, list[ft.Control]]:
    checkboxes = {}
    cards = []

    for option in options:
        checkbox = ft.Checkbox(value=option["id"] in saved_ids)
        checkboxes[option["id"]] = checkbox

        details = []
        expected = option["expected"]
        selected = option["id"] in saved_ids
        item_ok = selected == expected
        if validated:
            explanation = option.get(
                "description",
                "Se ajusta al contexto indicado." if expected else "No se ajusta al contexto.",
            )
            feedback_text, item_ok = checkbox_feedback(selected, expected, explanation)
            details.append(
                inline_feedback(feedback_text, item_ok)
            )

        cards.append(
            ft.Container(
                content=ft.Row(
                    controls=[
                        checkbox,
                        ft.Column(
                            controls=[
                                ft.Text(option["label"], size=15, weight=ft.FontWeight.BOLD),
                                *details,
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
                bgcolor=feedback_colors(item_ok)[0] if validated else None,
                border_radius=10,
            )
        )

    return checkboxes, cards


def get_selected_ids(checkboxes: dict) -> list[str]:
    return [
        option_id
        for option_id, checkbox in checkboxes.items()
        if checkbox.value
    ]


def evaluate_multi_select(options: list[dict], selected_ids: list[str]) -> dict:
    expected_ids = [option["id"] for option in options if option["expected"]]
    missing = [option_id for option_id in expected_ids if option_id not in selected_ids]
    wrong = [option_id for option_id in selected_ids if option_id not in expected_ids]

    return {
        "selected_ids": selected_ids,
        "expected_ids": expected_ids,
        "missing_ids": missing,
        "wrong_ids": wrong,
        "ok": not missing and not wrong,
    }


def option_labels(options: list[dict], option_ids: list[str]) -> list[str]:
    labels = {option["id"]: option["label"] for option in options}
    return [labels.get(option_id, option_id) for option_id in option_ids]


def build_multi_select_feedback(title: str, options: list[dict], result: dict) -> dict:
    correct = ", ".join(option_labels(options, result["expected_ids"]))
    lines = [f"Respuesta correcta: {correct}."]

    for option in options:
        explanation = option.get("description")
        if not explanation:
            explanation = (
                "Se ajusta al contexto indicado."
                if option["expected"]
                else "No responde a los requisitos del contexto y puede introducir una barrera."
            )
        feedback_text, _ = checkbox_feedback(
            option["id"] in result["selected_ids"],
            bool(option["expected"]),
            explanation,
        )
        lines.append(f"{option['label']}: {feedback_text}")

    return {"title": title, "lines": lines}


def build_resource_detail(resource: dict) -> ft.Control:
    def metadata_badge(icon: str, text: str) -> ft.Control:
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icon, size=16, color="#1D4ED8"),
                    ft.Text(text, size=12, color="#1E3A8A"),
                ],
                spacing=6,
                tight=True,
            ),
            bgcolor="#EFF6FF",
            border=ft.border.all(1, "#BFDBFE"),
            border_radius=999,
            padding=ft.padding.symmetric(horizontal=10, vertical=6),
        )

    def detail_section(
        title: str,
        icon: str,
        rows: list[tuple[str, str]],
    ) -> ft.Control:
        return ft.Container(
            col={"xs": 12, "md": 4},
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(icon, size=18, color="#2563EB"),
                                bgcolor="#DBEAFE",
                                border_radius=8,
                                padding=7,
                            ),
                            ft.Text(
                                title,
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color="#111827",
                            ),
                        ],
                        spacing=9,
                    ),
                    *[
                        ft.Column(
                            controls=[
                                ft.Text(
                                    label.upper(),
                                    size=10,
                                    weight=ft.FontWeight.BOLD,
                                    color="#6B7280",
                                ),
                                ft.Text(value, size=13, color="#374151"),
                            ],
                            spacing=2,
                        )
                        for label, value in rows
                    ],
                ],
                spacing=12,
            ),
            bgcolor="#FFFFFF",
            border=ft.border.all(1, "#E5E7EB"),
            border_radius=12,
            padding=14,
        )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Text(
                                resource["id"],
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            width=42,
                            height=42,
                            alignment=ft.Alignment.CENTER,
                            bgcolor="#2563EB",
                            border_radius=10,
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    resource["title"],
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color="#111827",
                                ),
                                ft.Text(
                                    resource["repository"],
                                    size=12,
                                    color="#6B7280",
                                ),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Row(
                    controls=[
                        metadata_badge(ft.Icons.SCHOOL_OUTLINED, resource["age"]),
                        metadata_badge(ft.Icons.TIMER_OUTLINED, resource["duration"]),
                        metadata_badge(ft.Icons.DESCRIPTION_OUTLINED, resource["format"]),
                    ],
                    spacing=8,
                    wrap=True,
                ),
                ft.ResponsiveRow(
                    controls=[
                        detail_section(
                            "Ajuste didáctico",
                            ft.Icons.SCHOOL_OUTLINED,
                            [
                                ("Nivel lector", resource["reading_level"]),
                                ("Evidencia", resource["evidence"]),
                            ],
                        ),
                        detail_section(
                            "Acceso técnico",
                            ft.Icons.DEVICES_OUTLINED,
                            [
                                ("Compatibilidad", resource["compatibility"]),
                                ("Registro", resource["registration"]),
                                ("Plan alternativo", resource["fallback"]),
                            ],
                        ),
                        detail_section(
                            "Uso y accesibilidad",
                            ft.Icons.ACCESSIBILITY_NEW_OUTLINED,
                            [
                                ("Accesibilidad", resource["accessibility"]),
                                ("Licencia", resource["license"]),
                            ],
                        ),
                    ],
                    spacing=10,
                    run_spacing=10,
                ),
            ],
            spacing=14,
        ),
        bgcolor="#F8FAFC",
        border=ft.border.all(1, "#CBD5E1"),
        border_radius=16,
        padding=18,
    )


def build_test_p02(state: dict, refresh_view) -> ft.Control:
    test_data = load_test_data()
    requirements = test_data["requirements"]
    repositories = test_data["repositories"]
    filters = test_data["filters"]
    resources = test_data["resources"]

    saved_requirements = state["responses"].get("p02_requirements", [])
    saved_repositories = state["responses"].get("p02_repositories", [])
    saved_filters = state["responses"].get("p02_filters", [])
    selected_value = state["responses"].get("p02_selected")
    opened_details = state["responses"].get("p02_opened_details", [])
    active_resource_id = state["responses"].get("p02_active_resource")
    validated = state["feedback"]["p02"]["ok"] is not None

    requirement_checkboxes, requirement_cards = build_checkbox_cards(
        requirements["options"],
        saved_requirements,
        validated,
    )
    repository_checkboxes, repository_cards = build_checkbox_cards(
        repositories["options"],
        saved_repositories,
        validated,
    )
    filter_checkboxes, filter_cards = build_checkbox_cards(
        filters["options"],
        saved_filters,
        validated,
    )

    selected_radio = ft.RadioGroup(
        value=selected_value,
        content=ft.Column(spacing=8),
    )
    active_resource = next(
        (
            resource
            for resource in resources["items"]
            if resource["id"] == active_resource_id
        ),
        None,
    )
    detail_box = ft.Container(
        content=(
            build_resource_detail(active_resource)
            if active_resource
            else build_info_panel(
                "Ficha detallada",
                [
                    "Abre una ficha para revisar nivel, licencia, accesibilidad, compatibilidad, registro y valoración antes de seleccionar el recurso."
                ],
            )
        )
    )

    def show_detail(resource: dict):
        if resource["id"] not in opened_details:
            opened_details.append(resource["id"])

        state["responses"]["p02_opened_details"] = opened_details
        state["responses"]["p02_active_resource"] = resource["id"]
        detail_box.content = build_resource_detail(resource)
        detail_box.update()

    rows = []
    resource_feedback_rows = []
    for resource in resources["items"]:
        expected = resource["id"] == resources["expected_id"]
        selected = selected_value == resource["id"]
        item_ok = selected == expected
        title_control = ft.Text(resource["title"])
        if validated:
            resource_feedback_rows.append(
                (
                    item_ok,
                    (
                        f"{resource['id']} · {resource['title']}: opción correcta"
                        if expected
                        else f"{resource['id']} · {resource['title']}: {resource['reason']}"
                    ),
                )
            )
        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(resource["id"])),
                    ft.DataCell(title_control),
                    ft.DataCell(ft.Text(resource["repository"])),
                    ft.DataCell(ft.Text(resource["format"])),
                    ft.DataCell(
                        ft.ElevatedButton(
                            "Ver ficha",
                            on_click=lambda e, r=resource: show_detail(r),
                        )
                    ),
                ]
            )
        )

    selected_radio.content.controls = [
        ft.Radio(value=resource["id"], label=f"{resource['id']} · {resource['title']}")
        for resource in resources["items"]
    ]

    def validate(e):
        selected_requirements = get_selected_ids(requirement_checkboxes)
        selected_repositories = get_selected_ids(repository_checkboxes)
        selected_filters = get_selected_ids(filter_checkboxes)
        selected_id = selected_radio.value

        state["responses"]["p02_requirements"] = selected_requirements
        state["responses"]["p02_repositories"] = selected_repositories
        state["responses"]["p02_filters"] = selected_filters
        state["responses"]["p02_selected"] = selected_id
        state["responses"]["p02_opened_details"] = opened_details

        requirements_result = evaluate_multi_select(
            requirements["options"],
            selected_requirements,
        )
        repositories_result = evaluate_multi_select(
            repositories["options"],
            selected_repositories,
        )
        filters_result = evaluate_multi_select(
            filters["options"],
            selected_filters,
        )

        expected_id = resources["expected_id"]
        resource_ok = selected_id == expected_id
        minimum_details = resources.get("minimum_details_to_review", 1)
        reviewed_enough = len(set(opened_details)) >= minimum_details
        consulted_detail = expected_id in opened_details
        review_ok = reviewed_enough and consulted_detail

        requirements_score = max(
            0,
            30
            - (len(requirements_result["missing_ids"]) * 5)
            - (len(requirements_result["wrong_ids"]) * 5),
        )
        repositories_score = max(
            0,
            20
            - (len(repositories_result["missing_ids"]) * 8)
            - (len(repositories_result["wrong_ids"]) * 6),
        )
        filters_score = max(
            0,
            20
            - (len(filters_result["missing_ids"]) * 4)
            - (len(filters_result["wrong_ids"]) * 4),
        )
        resource_score = 25 if resource_ok else 0
        detail_score = 5 if review_ok else 0
        score = min(
            100,
            requirements_score
            + repositories_score
            + filters_score
            + resource_score
            + detail_score,
        )

        ok = (
            requirements_result["ok"]
            and repositories_result["ok"]
            and filters_result["ok"]
            and resource_ok
            and review_ok
        )

        state["completed"]["p02"] = ok
        message = test_data["feedback"]["success"] if ok else test_data["feedback"]["failure"]

        details = []
        if not requirements_result["ok"]:
            details.append(
                build_multi_select_feedback(
                    "Requisitos del contenido",
                    requirements["options"],
                    requirements_result,
                )
            )

        if not repositories_result["ok"]:
            details.append(
                build_multi_select_feedback(
                    "Repositorios donde buscar",
                    repositories["options"],
                    repositories_result,
                )
            )

        if not filters_result["ok"]:
            details.append(
                build_multi_select_feedback(
                    "Filtros de búsqueda",
                    filters["options"],
                    filters_result,
                )
            )

        if not resource_ok:
            expected_resource = next(
                resource for resource in resources["items"] if resource["id"] == expected_id
            )
            lines = [
                f"Respuesta correcta: {expected_resource['id']} · {expected_resource['title']}.",
                f"Por qué es correcta: {expected_resource['reason']}",
            ]
            for resource in resources["items"]:
                status = "Correcta" if resource["id"] == expected_id else "Incorrecta"
                lines.append(
                    f"{status}: {resource['id']} · {resource['title']}. {resource['reason']}"
                )
            details.append({"title": "Selección del recurso", "lines": lines})

        if not review_ok:
            missing_reviews = max(0, minimum_details - len(set(opened_details)))
            review_instruction = (
                f"Abre {missing_reviews} ficha(s) adicional(es) y asegúrate de incluir "
                "la del recurso seleccionado."
            )
            details.append(
                {
                    "title": "Contraste de fichas",
                    "lines": [
                        review_instruction,
                        "La decisión debe apoyarse en la comparación de objetivo, duración, accesibilidad, acceso, compatibilidad y alternativa ante fallos de conexión.",
                    ],
                }
            )

        state["feedback"]["p02"] = {
            "ok": ok,
            "message": message,
            "details": [] if ok else details,
        }

        result = {
            "test_id": TEST_ID,
            "scenario_id": test_data["scenario_id"],
            "scenario_title": test_data["scenario_title"],
            "timestamp_utc": datetime.utcnow().isoformat(),
            "score_0_100": score,
            "level_hint": "A2" if ok else "A1",
            "payload": {
                "selected_requirements": selected_requirements,
                "expected_requirements": requirements_result["expected_ids"],
                "missing_requirements": requirements_result["missing_ids"],
                "wrong_requirements": requirements_result["wrong_ids"],
                "selected_repositories": selected_repositories,
                "expected_repositories": repositories_result["expected_ids"],
                "missing_repositories": repositories_result["missing_ids"],
                "wrong_repositories": repositories_result["wrong_ids"],
                "selected_filters": selected_filters,
                "expected_filters": filters_result["expected_ids"],
                "missing_filters": filters_result["missing_ids"],
                "wrong_filters": filters_result["wrong_ids"],
                "selected_id": selected_id,
                "expected_id": expected_id,
                "opened_details": opened_details,
                "consulted_expected_detail": consulted_detail,
                "minimum_details_to_review": minimum_details,
                "reviewed_enough_details": reviewed_enough,
            },
            "checks": [
                {
                    "check_id": "context_requirements",
                    "label": "Identifica requisitos del contenido para una situación concreta",
                    "passed": requirements_result["ok"],
                    "weight": 30,
                    "evidence": ", ".join(selected_requirements),
                },
                {
                    "check_id": "institutional_repositories",
                    "label": "Selecciona repositorios institucionales o empleados por el centro",
                    "passed": repositories_result["ok"],
                    "weight": 20,
                    "evidence": ", ".join(selected_repositories),
                },
                {
                    "check_id": "compatible_search_filters",
                    "label": "Aplica filtros de búsqueda compatibles con el entorno virtual",
                    "passed": filters_result["ok"],
                    "weight": 20,
                    "evidence": ", ".join(selected_filters),
                },
                {
                    "check_id": "best_resource_selected",
                    "label": "Selecciona el contenido digital más adecuado al contexto",
                    "passed": resource_ok,
                    "weight": 25,
                    "evidence": str(selected_id),
                },
                {
                    "check_id": "candidate_details_compared",
                    "label": "Contrasta suficientes fichas e incluye el recurso seleccionado",
                    "passed": review_ok,
                    "weight": 5,
                    "evidence": ", ".join(opened_details),
                },
            ],
            "notes": [message],
        }

        saved_path = save_result(result)
        state["responses"]["p02_saved_path"] = str(saved_path)

        refresh_view()

    content = ft.Column(
        controls=[
            ft.Text(
                test_data["intro"],
                size=15,
                weight=ft.FontWeight.W_600,
            ),
            build_info_panel(
                test_data["advisor_note"]["title"],
                test_data["advisor_note"]["lines"],
            ),
            section_title(requirements["title"]),
            ft.Text(requirements["description"], size=14),
            ft.ResponsiveRow(controls=requirement_cards, spacing=8, run_spacing=8),
            ft.Divider(height=24),
            section_title(repositories["title"]),
            ft.Text(repositories["description"], size=14),
            ft.ResponsiveRow(controls=repository_cards, spacing=8, run_spacing=8),
            ft.Divider(height=24),
            section_title(filters["title"]),
            ft.Text(filters["description"], size=14),
            ft.ResponsiveRow(controls=filter_cards, spacing=8, run_spacing=8),
            ft.Divider(height=24),
            section_title(resources["title"]),
            ft.Text(resources["description"], size=14),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID")),
                    ft.DataColumn(ft.Text("Recurso")),
                    ft.DataColumn(ft.Text("Repositorio")),
                    ft.DataColumn(ft.Text("Formato")),
                    ft.DataColumn(ft.Text("Ficha")),
                ],
                rows=rows,
            ),
            feedback_panel("Corrección de recursos", resource_feedback_rows),
            detail_box,
            ft.Container(height=8),
            ft.Text(
                "Selecciona el contenido más adecuado:",
                size=16,
                weight=ft.FontWeight.BOLD,
            ),
            selected_radio,
            ft.Container(height=12),
            ft.ElevatedButton("Validar prueba", on_click=validate),
            build_result_box(state["feedback"]["p02"]),
        ],
        spacing=12,
    )

    return question_block(
        title=test_data["title"],
        statement=test_data["statement"],
        content=content,
    )
