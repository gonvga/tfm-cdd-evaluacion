import flet as ft
from datetime import datetime

from core.storage import save_result
from ui.components import question_block


TEST_ID = "P05"
SCENARIO_ID = "comp22_a1_corregir_ficha"


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


def build_document_image() -> ft.Control:
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "Ficha educativa",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color="#111827",
                ),
                ft.Text(
                    "Analiza el documento y responde a las preguntas de corrección.",
                    size=14,
                    color="#4B5563",
                ),
                ft.Container(
                    content=ft.Image(
                        src="ficha_p05.png",
                        fit="contain",
                    ),
                    bgcolor="#FFFFFF",
                    border=ft.border.all(1, "#D1D5DB"),
                    border_radius=16,
                    padding=10,
                ),
            ],
            spacing=12,
        ),
        bgcolor="#F9FAFB",
        border=ft.border.all(1, "#E5E7EB"),
        border_radius=18,
        padding=22,
    )


def build_test_p05(state: dict, refresh_view) -> ft.Control:
    saved_license = state["responses"].get("p05_license")
    saved_apa = state["responses"].get("p05_apa")
    saved_content = state["responses"].get("p05_content")
    saved_accessibility = state["responses"].get("p05_accessibility", [])

    license_dropdown = ft.Dropdown(
        label="Elegir licencia",
        value=saved_license,
        width=320,
        options=[
            ft.dropdown.Option("Copyright"),
            ft.dropdown.Option("Sin licencia"),
            ft.dropdown.Option("CC BY"),
            ft.dropdown.Option("CC BY-SA"),
        ],
    )

    apa_radio = ft.RadioGroup(
        value=saved_apa,
        content=ft.Column(
            controls=[
                ft.Radio(
                    value="A",
                    label="ministerio educacion guia saludable 2024",
                ),
                ft.Radio(
                    value="B",
                    label="Ministerio de Educación. (2024). Guía de hábitos saludables. Madrid: MEC.",
                ),
                ft.Radio(
                    value="C",
                    label="Guía saludable, recuperado de internet.",
                ),
            ],
            spacing=8,
        ),
    )

    accessibility_options = {
        "alt_text": ft.Checkbox(
            label="Añadir texto alternativo a las imágenes",
            value="alt_text" in saved_accessibility,
        ),
        "remove_subtitles": ft.Checkbox(
            label="Eliminar subtítulos del recurso",
            value="remove_subtitles" in saved_accessibility,
        ),
        "document_styles": ft.Checkbox(
            label="Usar estilos del documento para títulos y apartados",
            value="document_styles" in saved_accessibility,
        ),
        "low_contrast": ft.Checkbox(
            label="Reducir el contraste del texto",
            value="low_contrast" in saved_accessibility,
        ),
    }

    content_radio = ft.RadioGroup(
        value=saved_content,
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Radio(value="A"),
                            ft.Container(
                                expand=True,
                                content=ft.Text(
                                    "Los hábitos saludables constituyen un conjunto "
                                    "de conductas adquiridas que favorecen el "
                                    "mantenimiento de la homeostasis fisiológica "
                                    "y psicológica del organismo.",
                                    size=14,
                                    selectable=False,
                                ),
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                    border=ft.border.all(1, "#E5E7EB"),
                    border_radius=12,
                    padding=12,
                ),

                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Radio(value="B"),
                            ft.Container(
                                expand=True,
                                content=ft.Text(
                                    "Los hábitos saludables son aquellas conductas "
                                    "que realizamos de forma habitual y que "
                                    "contribuyen a mantener nuestro cuerpo y "
                                    "nuestra mente en buen estado.",
                                    size=14,
                                    selectable=False,
                                ),
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                    border=ft.border.all(1, "#E5E7EB"),
                    border_radius=12,
                    padding=12,
                ),

                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Radio(value="C"),
                            ft.Container(
                                expand=True,
                                content=ft.Text(
                                    "Los hábitos saludables son cosas buenas "
                                    "que hacemos para cuidar nuestro cuerpo "
                                    "y sentirnos bien.",
                                    size=14,
                                    selectable=False,
                                ),
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                    border=ft.border.all(1, "#E5E7EB"),
                    border_radius=12,
                    padding=12,
                ),
            ],
            spacing=10,
        ),
    )

    def validate(e):
        selected_license = license_dropdown.value
        selected_apa = apa_radio.value
        selected_content = content_radio.value

        selected_accessibility = [
            key
            for key, checkbox in accessibility_options.items()
            if checkbox.value
        ]

        state["responses"]["p05_license"] = selected_license
        state["responses"]["p05_apa"] = selected_apa
        state["responses"]["p05_content"] = selected_content
        state["responses"]["p05_accessibility"] = selected_accessibility

        if (
            selected_license is None
            or selected_apa is None
            or selected_content is None
        ):
            state["completed"]["p05"] = False
            state["feedback"]["p05"] = {
                "ok": False,
                "message": "Debes completar todos los apartados antes de validar la prueba.",
            }
            refresh_view()
            return

        expected_accessibility = {"alt_text", "document_styles"}

        license_ok = selected_license in ["CC BY", "CC BY-SA"]
        apa_ok = selected_apa == "B"
        accessibility_ok = set(selected_accessibility) == expected_accessibility
        content_ok = selected_content == "B"

        score = 0

        if license_ok:
            score += 30
        if apa_ok:
            score += 25
        if accessibility_ok:
            score += 25
        if content_ok:
            score += 20

        ok = score >= 80

        state["completed"]["p05"] = ok

        message = (
            "Prueba superada. Has revisado correctamente la ficha aplicando criterios básicos "
            "de licencia, referencia, accesibilidad y adecuación didáctica."
            if ok
            else "Prueba no superada. Revisa la licencia, la referencia APA, la accesibilidad "
            "y la adecuación del contenido al alumnado de secundaria."
        )

        state["feedback"]["p05"] = {
            "ok": ok,
            "message": message,
        }

        result = {
            "test_id": TEST_ID,
            "scenario_id": SCENARIO_ID,
            "scenario_title": "Corregir una ficha educativa",
            "timestamp_utc": datetime.utcnow().isoformat(),
            "score_0_100": score,
            "level_hint": "A1" if ok else "A0",
            "payload": {
                "selected_license": selected_license,
                "selected_apa_option": selected_apa,
                "selected_accessibility": selected_accessibility,
                "selected_content_option": selected_content,
                "expected_license": ["CC BY", "CC BY-SA"],
                "expected_apa_option": "B",
                "expected_accessibility": sorted(expected_accessibility),
                "expected_content_option": "B",
            },
            "checks": [
                {
                    "check_id": "open_license_selected",
                    "label": "Selecciona una licencia abierta adecuada",
                    "passed": license_ok,
                    "weight": 30,
                    "evidence": selected_license,
                },
                {
                    "check_id": "apa_reference_selected",
                    "label": "Selecciona la referencia APA correcta",
                    "passed": apa_ok,
                    "weight": 25,
                    "evidence": selected_apa,
                },
                {
                    "check_id": "accessibility_actions_selected",
                    "label": "Selecciona acciones correctas de accesibilidad",
                    "passed": accessibility_ok,
                    "weight": 25,
                    "evidence": ", ".join(selected_accessibility),
                },
                {
                    "check_id": "didactic_content_selected",
                    "label": "Selecciona el contenido más adecuado para alumnado de secundaria",
                    "passed": content_ok,
                    "weight": 20,
                    "evidence": selected_content,
                },
            ],
            "notes": [message],
        }

        saved_path = save_result(result)
        state["responses"]["p05_saved_path"] = str(saved_path)

        refresh_view()

    questions_panel = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "Preguntas de corrección",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color="#111827",
                ),
                ft.Text(
                    "Observa la ficha de la derecha y selecciona las correcciones adecuadas.",
                    size=14,
                    color="#4B5563",
                ),
                ft.Divider(height=22, color="#E5E7EB"),

                ft.Text(
                    "1. ¿Qué licencia sería adecuada para permitir la reutilización educativa?",
                    size=15,
                    weight=ft.FontWeight.BOLD,
                ),
                license_dropdown,

                ft.Text(
                    "2. ¿Qué referencia está correctamente escrita según normas APA?",
                    size=15,
                    weight=ft.FontWeight.BOLD,
                ),
                apa_radio,

                ft.Text(
                    "3. ¿Qué acciones mejorarían la accesibilidad del recurso?",
                    size=15,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Column(
                    controls=list(accessibility_options.values()),
                    spacing=4,
                ),

                ft.Text(
                    "4. ¿Qué versión del contenido es más adecuada para 2.º de ESO?",
                    size=15,
                    weight=ft.FontWeight.BOLD,
                ),
                content_radio,

                ft.Container(height=8),
                ft.ElevatedButton("Validar prueba", on_click=validate),
                build_result_box(state["feedback"]["p05"]),
            ],
            spacing=14,
        ),
        bgcolor="#F9FAFB",
        border=ft.border.all(1, "#E5E7EB"),
        border_radius=18,
        padding=22,
    )

    content = ft.Column(
        controls=[
            ft.Text(
                "Escenario: debes revisar una ficha educativa digital antes de reutilizarla "
                "con alumnado de secundaria. Analiza el documento y aplica las correcciones "
                "necesarias sobre licencia, referencia, accesibilidad y adecuación didáctica.",
                size=15,
                weight=ft.FontWeight.W_600,
            ),
            ft.ResponsiveRow(
                controls=[
                    ft.Container(
                        col={"xs": 12, "lg": 6},
                        content=questions_panel,
                    ),
                    ft.Container(
                        col={"xs": 12, "lg": 6},
                        content=build_document_image(),
                    ),
                ],
                spacing=18,
                run_spacing=18,
            ),
        ],
        spacing=18,
    )

    return question_block(
        title="P05 · Corregir una ficha educativa",
        statement=(
            "Evalúa los indicadores 2.2.A1.1, 2.2.A1.2 y 2.2.A1.3 mediante una tarea guiada "
            "de revisión de una ficha educativa digital, aplicando criterios didácticos, técnicos, "
            "de accesibilidad y propiedad intelectual."
        ),
        content=content,
    )