import flet as ft
from datetime import datetime

from core.storage import save_result
from ui.components import question_block


TEST_ID = "P06"
SCENARIO_ID = "comp22_a2_configurar_plantilla"


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


def build_option_card(content: ft.Control) -> ft.Control:
    return ft.Container(
        content=content,
        border=ft.border.all(1, "#E5E7EB"),
        border_radius=14,
        bgcolor="#FFFFFF",
        padding=14,
    )


def build_test_p06(state: dict, refresh_view) -> ft.Control:
    saved_accessibility = state["responses"].get("p06_accessibility")
    saved_tool = state["responses"].get("p06_tool")
    saved_layout = state["responses"].get("p06_layout")
    saved_navigation = state["responses"].get("p06_navigation")
    saved_adaptation = state["responses"].get("p06_adaptation")

    accessibility_radio = ft.RadioGroup(
        value=saved_accessibility,
        content=ft.Column(
            controls=[
                ft.Radio(
                    value="A",
                    label="Añadir encabezados claros y mantener alto contraste",
                ),
                ft.Radio(
                    value="B",
                    label="Reducir el tamaño del texto principal",
                ),
                ft.Radio(
                    value="C",
                    label="Eliminar subtítulos y ayudas visuales",
                ),
                ft.Radio(
                    value="D",
                    label="Ocultar botones de navegación",
                ),
            ],
            spacing=8,
        ),
    )

    tool_radio = ft.RadioGroup(
        value=saved_tool,
        content=ft.Column(
            controls=[
                ft.Radio(
                    value="A",
                    label="Plataforma educativa institucional del centro",
                ),
                ft.Radio(
                    value="B",
                    label="Aplicación externa no autorizada",
                ),
                ft.Radio(
                    value="C",
                    label="Red social pública para alumnado",
                ),
                ft.Radio(
                    value="D",
                    label="Programa descargado sin licencia",
                ),
            ],
            spacing=8,
        ),
    )

    layout_radio = ft.RadioGroup(
        value=saved_layout,
        content=ft.Column(
            controls=[
                build_option_card(
                    ft.Row(
                        controls=[
                            ft.Radio(value="A"),
                            ft.Container(
                                expand=True,
                                content=ft.Column(
                                    controls=[
                                        ft.Text(
                                            "Interfaz limpia y organizada",
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            "Bloques cortos, iconos claros y distribución sencilla.",
                                            size=13,
                                            color="#4B5563",
                                        ),
                                    ],
                                    spacing=4,
                                ),
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    )
                ),
                build_option_card(
                    ft.Row(
                        controls=[
                            ft.Radio(value="B"),
                            ft.Container(
                                expand=True,
                                content=ft.Column(
                                    controls=[
                                        ft.Text(
                                            "Pantalla saturada",
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            "Muchos elementos simultáneos y exceso de texto.",
                                            size=13,
                                            color="#4B5563",
                                        ),
                                    ],
                                    spacing=4,
                                ),
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    )
                ),
                build_option_card(
                    ft.Row(
                        controls=[
                            ft.Radio(value="C"),
                            ft.Container(
                                expand=True,
                                content=ft.Column(
                                    controls=[
                                        ft.Text(
                                            "Diseño universitario técnico",
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            "Lenguaje formal y navegación compleja.",
                                            size=13,
                                            color="#4B5563",
                                        ),
                                    ],
                                    spacing=4,
                                ),
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    )
                ),
            ],
            spacing=10,
        ),
    )

    navigation_radio = ft.RadioGroup(
        value=saved_navigation,
        content=ft.Column(
            controls=[
                ft.Radio(
                    value="A",
                    label="Menú visible y botones claramente identificados",
                ),
                ft.Radio(
                    value="B",
                    label="Navegación oculta mediante iconos sin texto",
                ),
                ft.Radio(
                    value="C",
                    label="Ocho submenús simultáneos",
                ),
                ft.Radio(
                    value="D",
                    label="Acceso solo mediante atajos avanzados",
                ),
            ],
            spacing=8,
        ),
    )

    adaptation_radio = ft.RadioGroup(
        value=saved_adaptation,
        content=ft.Column(
            controls=[
                ft.Radio(
                    value="A",
                    label="Dividir el contenido en bloques breves y visuales",
                ),
                ft.Radio(
                    value="B",
                    label="Añadir párrafos técnicos largos",
                ),
                ft.Radio(
                    value="C",
                    label="Eliminar ejemplos visuales",
                ),
                ft.Radio(
                    value="D",
                    label="Usar vocabulario universitario especializado",
                ),
            ],
            spacing=8,
        ),
    )

    def validate(e):
        selected_accessibility = accessibility_radio.value
        selected_tool = tool_radio.value
        selected_layout = layout_radio.value
        selected_navigation = navigation_radio.value
        selected_adaptation = adaptation_radio.value

        state["responses"]["p06_accessibility"] = selected_accessibility
        state["responses"]["p06_tool"] = selected_tool
        state["responses"]["p06_layout"] = selected_layout
        state["responses"]["p06_navigation"] = selected_navigation
        state["responses"]["p06_adaptation"] = selected_adaptation

        if (
            selected_accessibility is None
            or selected_tool is None
            or selected_layout is None
            or selected_navigation is None
            or selected_adaptation is None
        ):
            state["completed"]["p06"] = False
            state["feedback"]["p06"] = {
                "ok": False,
                "message": "Debes responder todas las preguntas antes de validar la prueba.",
            }
            refresh_view()
            return

        accessibility_ok = selected_accessibility == "A"
        tool_ok = selected_tool == "A"
        layout_ok = selected_layout == "A"
        navigation_ok = selected_navigation == "A"
        adaptation_ok = selected_adaptation == "A"

        score = 0

        if accessibility_ok:
            score += 20

        if tool_ok:
            score += 20

        if layout_ok:
            score += 20

        if navigation_ok:
            score += 20

        if adaptation_ok:
            score += 20

        ok = score >= 80

        state["completed"]["p06"] = ok

        message = (
            "Prueba superada. Has configurado correctamente una plantilla educativa aplicando criterios didácticos, técnicos y de accesibilidad."
            if ok
            else "Prueba no superada. Revisa las decisiones relacionadas con accesibilidad, adaptación didáctica, navegación y herramientas autorizadas."
        )

        state["feedback"]["p06"] = {
            "ok": ok,
            "message": message,
        }

        result = {
            "test_id": TEST_ID,
            "scenario_id": SCENARIO_ID,
            "scenario_title": "Configurar plantilla didáctica",
            "timestamp_utc": datetime.utcnow().isoformat(),
            "score_0_100": score,
            "level_hint": "A2" if ok else "A1",
            "payload": {
                "selected_accessibility": selected_accessibility,
                "selected_tool": selected_tool,
                "selected_layout": selected_layout,
                "selected_navigation": selected_navigation,
                "selected_adaptation": selected_adaptation,
                "expected_answers": {
                    "accessibility": "A",
                    "tool": "A",
                    "layout": "A",
                    "navigation": "A",
                    "adaptation": "A",
                },
            },
            "checks": [
                {
                    "check_id": "accessibility_configuration",
                    "label": "Selecciona configuraciones accesibles",
                    "passed": accessibility_ok,
                    "weight": 20,
                    "evidence": selected_accessibility,
                },
                {
                    "check_id": "authorized_tool_selected",
                    "label": "Selecciona una herramienta autorizada",
                    "passed": tool_ok,
                    "weight": 20,
                    "evidence": selected_tool,
                },
                {
                    "check_id": "didactic_layout_selected",
                    "label": "Selecciona una distribución adecuada para ESO",
                    "passed": layout_ok,
                    "weight": 20,
                    "evidence": selected_layout,
                },
                {
                    "check_id": "clear_navigation_selected",
                    "label": "Selecciona una navegación clara y sencilla",
                    "passed": navigation_ok,
                    "weight": 20,
                    "evidence": selected_navigation,
                },
                {
                    "check_id": "adapted_content_selected",
                    "label": "Selecciona una adaptación didáctica adecuada",
                    "passed": adaptation_ok,
                    "weight": 20,
                    "evidence": selected_adaptation,
                },
            ],
            "notes": [message],
        }

        saved_path = save_result(result)
        state["responses"]["p06_saved_path"] = str(saved_path)

        refresh_view()

    content = ft.Column(
        controls=[
            ft.Text(
                "Escenario: estás configurando una plantilla educativa digital para alumnado de 1.º de ESO utilizando una herramienta institucional del centro.",
                size=15,
                weight=ft.FontWeight.W_600,
            ),
            ft.Text(
                "Debes seleccionar las opciones más adecuadas para adaptar el recurso a las características del alumnado y garantizar una configuración accesible y compatible con el entorno educativo.",
                size=14,
            ),

            ft.Text(
                "1. ¿Qué configuración mejora la accesibilidad del recurso?",
                size=15,
                weight=ft.FontWeight.BOLD,
            ),
            accessibility_radio,

            ft.Text(
                "2. ¿Qué herramienta debería utilizar el docente?",
                size=15,
                weight=ft.FontWeight.BOLD,
            ),
            tool_radio,

            ft.Text(
                "3. ¿Qué distribución visual es más adecuada para 1.º de ESO?",
                size=15,
                weight=ft.FontWeight.BOLD,
            ),
            layout_radio,

            ft.Text(
                "4. ¿Qué configuración favorece una navegación clara?",
                size=15,
                weight=ft.FontWeight.BOLD,
            ),
            navigation_radio,

            ft.Text(
                "5. ¿Qué adaptación didáctica es más adecuada?",
                size=15,
                weight=ft.FontWeight.BOLD,
            ),
            adaptation_radio,

            ft.Container(height=8),

            ft.ElevatedButton(
                "Validar prueba",
                on_click=validate,
            ),

            build_result_box(state["feedback"]["p06"]),
        ],
        spacing=14,
    )

    return question_block(
        title="P06 · Configurar plantilla didáctica",
        statement=(
            "Evalúa los indicadores 2.2.A2.1, 2.2.A2.2 y 2.2.A2.3 mediante una tarea guiada "
            "de configuración y adaptación de un contenido digital educativo."
        ),
        content=content,
    )