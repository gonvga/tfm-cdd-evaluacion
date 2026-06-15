import json
import unicodedata
from datetime import datetime
from pathlib import Path

import flet as ft
from pypdf import PdfReader

from core.storage import save_result
from core.paths import resource_path
from ui.components import checkbox_feedback, question_block


TEST_ID = "P12"
DATA_PATH = resource_path("data", "p12_comp23_b2.json")


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
                *([
                    inline_feedback(
                        feedback_text,
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


def extract_pdf_text(pdf_path: str) -> str:
    try:
        reader = PdfReader(pdf_path)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)
    except Exception:
        return ""


def score_text_terms(
    terms: list[str],
    text: str,
    weight: int,
    prefix: str,
    require_all: bool = True,
) -> tuple[bool, int, dict, list[dict]]:
    normalized_text = normalize_text(text)
    checks = []
    passed_count = 0

    for term in terms:
        passed = normalize_text(term) in normalized_text
        if passed:
            passed_count += 1
        checks.append(
            {
                "check_id": f"{prefix}_{normalize_text(term).replace(' ', '_')}",
                "label": term,
                "passed": passed,
                "weight": round(weight / len(terms), 2) if terms else 0,
                "evidence": term if passed else "",
            }
        )

    passed = all(check["passed"] for check in checks) if require_all else any(check["passed"] for check in checks)
    return passed, round(passed_count / max(len(terms), 1) * weight), {term: True for term in terms}, checks


def build_test_p12(state: dict, refresh_view, page: ft.Page | None = None) -> ft.Control:
    test_data = load_test_data()
    validated = state["feedback"]["p12"]["ok"] is not None
    saved_pdf_path = state["responses"].get("p12_pdf_file_path")
    saved_pdf_text = state["responses"].get("p12_pdf_text", "")

    file_picker = None
    page_services = getattr(page, "services", None)
    if page is not None and page_services is not None:
        file_picker = next(
            (service for service in page_services if isinstance(service, ft.FilePicker)),
            None,
        )
        if file_picker is None:
            file_picker = ft.FilePicker()
            page_services.append(file_picker)
            page.update()
    elif page is not None:
        file_picker = ft.FilePicker()

    async def pick_pdf(e):
        if page is not None and file_picker is not None:
            selected_files = await file_picker.pick_files(
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["pdf"],
                allow_multiple=False,
            )
            if selected_files:
                pdf_file = selected_files[0]
                if pdf_file.path:
                    state["responses"]["p12_pdf_file_path"] = pdf_file.path
                    state["responses"]["p12_pdf_text"] = ""
                    refresh_view()

    def validate(e):
        pdf_path = state["responses"].get("p12_pdf_file_path")
        pdf_text = state["responses"].get("p12_pdf_text", "")

        if not pdf_text and pdf_path:
            pdf_text = extract_pdf_text(pdf_path)
            state["responses"]["p12_pdf_text"] = pdf_text

        if not pdf_text:
            message = test_data["feedback"]["failure"]
            state["completed"]["p12"] = False
            state["feedback"]["p12"] = {"ok": False, "message": message}
            refresh_view()
            return

        title_ok = normalize_text(test_data["requirements"]["expected_title"]) in normalize_text(pdf_text)
        title_points = 20 if title_ok else 0
        title_check = {
            "check_id": "title_match",
            "label": "Título correcto",
            "passed": title_ok,
            "weight": 20,
            "evidence": test_data["requirements"]["expected_title"] if title_ok else "",
        }

        sections_ok, sections_points, _, section_checks = score_text_terms(
            test_data["requirements"]["required_sections"],
            pdf_text,
            test_data["requirements"]["section_weight"],
            "section",
            require_all=True,
        )

        keyword_ok, keyword_points, _, keyword_checks = score_text_terms(
            test_data["requirements"]["expected_keywords"],
            pdf_text,
            test_data["requirements"]["keywords_weight"],
            "keyword",
            require_all=True,
        )

        license_ok, license_points, _, license_checks = score_text_terms(
            test_data["requirements"]["license_phrases"],
            pdf_text,
            test_data["requirements"]["license_weight"],
            "license",
            require_all=False,
        )

        accessibility_ok, accessibility_points, _, accessibility_checks = score_text_terms(
            test_data["requirements"]["accessibility_phrases"],
            pdf_text,
            test_data["requirements"]["accessibility_weight"],
            "accessibility",
            require_all=False,
        )

        score = title_points + sections_points + keyword_points + license_points + accessibility_points
        ok = title_ok and license_ok and accessibility_ok and score >= 80
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
                "pdf_file_path": pdf_path,
                "title_ok": title_ok,
                "sections_ok": sections_ok,
                "keyword_ok": keyword_ok,
                "license_ok": license_ok,
                "accessibility_ok": accessibility_ok,
            },
            "checks": [
                title_check,
                *section_checks,
                *keyword_checks,
                *license_checks,
                *accessibility_checks,
            ],
            "notes": [message],
        }

        saved_path = save_result(result)
        state["responses"]["p12_saved_path"] = str(saved_path)
        refresh_view()

    selected_file_label = (
        Path(saved_pdf_path).name if saved_pdf_path else "Ningún archivo seleccionado"
    )

    file_status = ft.Text(
        selected_file_label,
        size=13,
        color="#1F2937",
        weight=ft.FontWeight.NORMAL,
    )

    guidance = test_data["requirements"].get("guidance", [])

    content = ft.Column(
        controls=[
            ft.Text(test_data["intro"], size=15, weight=ft.FontWeight.W_600),
            info_panel(test_data["plan"]["title"], test_data["plan"]["lines"], "#F0FDF4"),
            ft.Divider(height=24),
            section_title(test_data["requirements"]["title"]),
            ft.Text(test_data["requirements"]["description"], size=14),
            *[ft.Text(f"• {hint}", size=13) for hint in guidance],
            ft.Divider(height=24),
            ft.Row(
                controls=[
                    ft.ElevatedButton("Seleccionar PDF", on_click=pick_pdf),
                    file_status,
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
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
