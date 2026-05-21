import flet as ft
from datetime import datetime

from core.storage import save_result
from ui.components import question_block


TEST_ID = "P07"
SCENARIO_ID = "comp22_b1_componer_recurso_accesible"


TEXT_OPTIONS = {
    "text_a": {
        "label": "Texto A",
        "title": "El ciclo hidrológico",
        "body": (
            "El ciclo hidrológico constituye un proceso biogeoquímico continuo mediante el cual "
            "el agua experimenta transformaciones físicas y desplazamientos entre la atmósfera, "
            "la hidrosfera y la superficie terrestre, interviniendo procesos como evaporación, "
            "condensación, precipitación, escorrentía e infiltración."
        ),
    },
    "text_b": {
        "label": "Texto B",
        "title": "El ciclo del agua",
        "body": (
            "El ciclo del agua explica cómo el agua cambia de lugar y de estado.\n\n"
            "1. El sol calienta el agua.\n"
            "2. El agua se convierte en vapor.\n"
            "3. Las nubes se forman.\n"
            "4. El agua cae en forma de lluvia."
        ),
    },
    "text_c": {
        "label": "Texto C",
        "title": "El agua",
        "body": "El agua sube.\nLuego baja.\nY llueve.",
    },
}


IMAGE_OPTIONS = {
    "image_a": "imagen_decorativa.png",
    "image_b": "esquema_ciclo_agua.png",
    "image_c": "iconos_fases.png",
}


LICENSE_OPTIONS = {
    "license_a": "licencia_copyright.png",
    "license_b": "licencia_cc_by.png",
    "license_c": "licencia_cc_by_sa.png",
}


EXTRA_OPTIONS = {
    "support_a": {
        "label": "Recurso A",
        "image": "video_subtitulos.png",
        "title": "Vídeo con subtítulos",
        "description": "El vídeo incorpora subtítulos sincronizados para apoyar la comprensión.",
    },
    "support_b": {
        "label": "Recurso B",
        "image": "glosario_visual.png",
        "title": "Glosario visual",
        "description": (
            "Evaporación: el agua se convierte en vapor.\n"
            "Condensación: el vapor forma nubes.\n"
            "Precipitación: el agua cae de las nubes."
        ),
    },
    "support_c": {
        "label": "Recurso C",
        "image": "ejemplo_cotidiano.png",
        "title": "Ejemplo cotidiano",
        "description": "Es parecido a cuando sale vapor de una olla caliente.",
    },
    "support_d": {
        "label": "Recurso D",
        "image": "para_saber_mas.png",
        "title": "Para saber más",
        "description": "La información avanzada aparece separada del contenido principal.",
    },
    "support_e": {
        "label": "Recurso E",
        "image": "curiosidad_irrelevante.png",
        "title": "Curiosidad irrelevante",
        "description": "Curiosidad: el océano Pacífico es el más grande del planeta.",
    },
}


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


def text_selector_card(option_id: str, control: ft.Control) -> ft.Control:
    option = TEXT_OPTIONS[option_id]

    return ft.Container(
        content=ft.Row(
            controls=[
                control,
                ft.Text(
                    option["label"],
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color="#111827",
                ),
            ],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor="#FFFFFF",
        border=ft.border.all(1, "#E5E7EB"),
        border_radius=14,
        padding=14,
    )


def image_selector_card(title: str, image_src: str, control: ft.Control) -> ft.Control:
    return ft.Container(
        content=ft.Row(
            controls=[
                control,
                ft.Image(
                    src=image_src,
                    width=120,
                    height=80,
                    fit="contain",
                ),
                ft.Text(
                    title,
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color="#111827",
                    expand=True,
                ),
            ],
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor="#FFFFFF",
        border=ft.border.all(1, "#E5E7EB"),
        border_radius=14,
        padding=12,
    )


def checkbox_image_card(
    title: str,
    image_src: str,
    checkbox: ft.Checkbox,
) -> ft.Control:
    return ft.Container(
        content=ft.Row(
            controls=[
                checkbox,
                ft.Image(
                    src=image_src,
                    width=120,
                    height=80,
                    fit="contain",
                ),
                ft.Text(
                    title,
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color="#111827",
                    expand=True,
                ),
            ],
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor="#FFFFFF",
        border=ft.border.all(1, "#E5E7EB"),
        border_radius=14,
        padding=12,
    )


def preview_block(
    title: str,
    image_src: str | None = None,
    description: str | None = None,
) -> ft.Control:
    controls = [
        ft.Text(
            title,
            size=16,
            weight=ft.FontWeight.BOLD,
            color="#111827",
        )
    ]

    if image_src:
        controls.append(
            ft.Image(
                src=image_src,
                width=320,
                height=180,
                fit="contain",
            )
        )

    if description:
        controls.append(
            ft.Text(
                description,
                size=14,
                color="#374151",
            )
        )

    return ft.Container(
        content=ft.Column(
            controls=controls,
            spacing=8,
        ),
        bgcolor="#FFFFFF",
        border=ft.border.all(1, "#E5E7EB"),
        border_radius=14,
        padding=14,
    )


def preview_text_block(selected_text: str | None) -> ft.Control:
    if selected_text in TEXT_OPTIONS:
        option = TEXT_OPTIONS[selected_text]

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Texto seleccionado",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color="#111827",
                    ),
                    ft.Text(
                        option["title"],
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color="#111827",
                    ),
                    ft.Text(
                        option["body"],
                        size=15,
                        color="#374151",
                    ),
                ],
                spacing=8,
            ),
            bgcolor="#FFFFFF",
            border=ft.border.all(1, "#E5E7EB"),
            border_radius=14,
            padding=14,
        )

    return preview_block(
        "Texto seleccionado",
        None,
        "Todavía no se ha seleccionado ningún texto.",
    )


def build_preview(
    selected_text: str | None,
    selected_image: str | None,
    support_a: bool,
    support_b: bool,
    support_c: bool,
    support_d: bool,
    support_e: bool,
    selected_license: str | None,
) -> ft.Control:
    selected_supports = {
        "support_a": support_a,
        "support_b": support_b,
        "support_c": support_c,
        "support_d": support_d,
        "support_e": support_e,
    }

    support_blocks = []

    for support_id, selected in selected_supports.items():

        if selected:

            option = EXTRA_OPTIONS[support_id]

            support_blocks.append(
                ft.Container(
                    content=ft.Image(
                        src=option["image"],
                        width=320,
                        height=180,
                        fit="contain",
                    ),
                    bgcolor="#FFFFFF",
                    border=ft.border.all(1, "#E5E7EB"),
                    border_radius=14,
                    padding=14,
                )
            )

    if not support_blocks:
        support_blocks.append(
            preview_block(
                "Sin recursos complementarios",
                None,
                "El recurso no incorpora piezas adicionales.",
            )
        )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "Vista previa del recurso",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color="#111827",
                ),
                preview_text_block(selected_text),
                preview_block(
                    "Imagen seleccionada",
                    IMAGE_OPTIONS.get(selected_image),
                    None if selected_image else "Todavía no se ha seleccionado ninguna imagen.",
                ),
                *support_blocks,
                preview_block(
                    "Licencia seleccionada",
                    LICENSE_OPTIONS.get(selected_license),
                    None if selected_license else "Todavía no se ha seleccionado ninguna licencia.",
                ),
            ],
            spacing=14,
        ),
        bgcolor="#F9FAFB",
        border=ft.border.all(1, "#E5E7EB"),
        border_radius=18,
        padding=22,
    )


def build_test_p07(state: dict, refresh_view) -> ft.Control:
    saved_text = state["responses"].get("p07_text")
    saved_image = state["responses"].get("p07_image")
    saved_support_a = state["responses"].get("p07_support_a", False)
    saved_support_b = state["responses"].get("p07_support_b", False)
    saved_support_c = state["responses"].get("p07_support_c", False)
    saved_support_d = state["responses"].get("p07_support_d", False)
    saved_support_e = state["responses"].get("p07_support_e", False)
    saved_license = state["responses"].get("p07_license")

    text_radio = ft.RadioGroup(
        value=saved_text,
        content=ft.Column(
            controls=[
                text_selector_card("text_a", ft.Radio(value="text_a")),
                text_selector_card("text_b", ft.Radio(value="text_b")),
                text_selector_card("text_c", ft.Radio(value="text_c")),
            ],
            spacing=10,
        ),
    )

    image_radio = ft.RadioGroup(
        value=saved_image,
        content=ft.Column(
            controls=[
                image_selector_card(
                    "Imagen A",
                    "imagen_decorativa.png",
                    ft.Radio(value="image_a"),
                ),
                image_selector_card(
                    "Imagen B",
                    "esquema_ciclo_agua.png",
                    ft.Radio(value="image_b"),
                ),
                image_selector_card(
                    "Imagen C",
                    "iconos_fases.png",
                    ft.Radio(value="image_c"),
                ),
            ],
            spacing=10,
        ),
    )

    support_a_checkbox = ft.Checkbox(value=saved_support_a)
    support_b_checkbox = ft.Checkbox(value=saved_support_b)
    support_c_checkbox = ft.Checkbox(value=saved_support_c)
    support_d_checkbox = ft.Checkbox(value=saved_support_d)
    support_e_checkbox = ft.Checkbox(value=saved_support_e)

    license_radio = ft.RadioGroup(
        value=saved_license,
        content=ft.Column(
            controls=[
                image_selector_card(
                    "Licencia A",
                    "licencia_copyright.png",
                    ft.Radio(value="license_a"),
                ),
                image_selector_card(
                    "Licencia B",
                    "licencia_cc_by.png",
                    ft.Radio(value="license_b"),
                ),
                image_selector_card(
                    "Licencia C",
                    "licencia_cc_by_sa.png",
                    ft.Radio(value="license_c"),
                ),
            ],
            spacing=10,
        ),
    )

    def update_preview(e=None):
        state["responses"]["p07_text"] = text_radio.value
        state["responses"]["p07_image"] = image_radio.value
        state["responses"]["p07_support_a"] = support_a_checkbox.value
        state["responses"]["p07_support_b"] = support_b_checkbox.value
        state["responses"]["p07_support_c"] = support_c_checkbox.value
        state["responses"]["p07_support_d"] = support_d_checkbox.value
        state["responses"]["p07_support_e"] = support_e_checkbox.value
        state["responses"]["p07_license"] = license_radio.value

        refresh_view()

    text_radio.on_change = update_preview
    image_radio.on_change = update_preview
    support_a_checkbox.on_change = update_preview
    support_b_checkbox.on_change = update_preview
    support_c_checkbox.on_change = update_preview
    support_d_checkbox.on_change = update_preview
    support_e_checkbox.on_change = update_preview
    license_radio.on_change = update_preview

    def validate(e):
        selected_text = text_radio.value
        selected_image = image_radio.value
        selected_support_a = support_a_checkbox.value
        selected_support_b = support_b_checkbox.value
        selected_support_c = support_c_checkbox.value
        selected_support_d = support_d_checkbox.value
        selected_support_e = support_e_checkbox.value
        selected_license = license_radio.value

        state["responses"]["p07_text"] = selected_text
        state["responses"]["p07_image"] = selected_image
        state["responses"]["p07_support_a"] = selected_support_a
        state["responses"]["p07_support_b"] = selected_support_b
        state["responses"]["p07_support_c"] = selected_support_c
        state["responses"]["p07_support_d"] = selected_support_d
        state["responses"]["p07_support_e"] = selected_support_e
        state["responses"]["p07_license"] = selected_license

        if selected_text is None or selected_image is None or selected_license is None:
            state["completed"]["p07"] = False
            state["feedback"]["p07"] = {
                "ok": False,
                "message": "Debes seleccionar texto, imagen y licencia.",
            }
            refresh_view()
            return

        text_ok = selected_text == "text_b"
        image_ok = selected_image == "image_b"
        support_a_ok = selected_support_a is True
        support_b_ok = selected_support_b is True
        support_c_ok = selected_support_c is True
        support_d_ok = selected_support_d is True
        support_e_ok = selected_support_e is False
        license_ok = selected_license == "license_c"

        score = 0

        if text_ok:
            score += 25
        if image_ok:
            score += 15
        if support_a_ok:
            score += 10
        if support_b_ok:
            score += 10
        if support_c_ok:
            score += 10
        if support_d_ok:
            score += 15
        if support_e_ok:
            score += 5
        if license_ok:
            score += 10

        ok = score >= 80
        state["completed"]["p07"] = ok

        message = (
            "Prueba superada. Has compuesto correctamente el recurso adaptado."
            if ok
            else "Prueba no superada. Revisa las piezas seleccionadas."
        )

        state["feedback"]["p07"] = {
            "ok": ok,
            "message": message,
        }

        result = {
            "test_id": TEST_ID,
            "scenario_id": SCENARIO_ID,
            "scenario_title": "Componer recurso adaptado",
            "timestamp_utc": datetime.utcnow().isoformat(),
            "score_0_100": score,
            "level_hint": "B1" if ok else "A2",
            "payload": {
                "selected_text": selected_text,
                "selected_image": selected_image,
                "selected_support_a": selected_support_a,
                "selected_support_b": selected_support_b,
                "selected_support_c": selected_support_c,
                "selected_support_d": selected_support_d,
                "selected_support_e": selected_support_e,
                "selected_license": selected_license,
                "expected_selection": {
                    "text": "text_b",
                    "image": "image_b",
                    "support_a": True,
                    "support_b": True,
                    "support_c": True,
                    "support_d": True,
                    "support_e": False,
                    "license": "license_c",
                },
            },
            "checks": [
                {
                    "check_id": "adapted_text_selected",
                    "label": "Selecciona una versión textual adaptada",
                    "passed": text_ok,
                    "weight": 25,
                    "evidence": selected_text,
                },
                {
                    "check_id": "meaningful_visual_selected",
                    "label": "Selecciona un apoyo visual significativo",
                    "passed": image_ok,
                    "weight": 15,
                    "evidence": selected_image,
                },
                {
                    "check_id": "support_a_selected",
                    "label": "Selecciona recurso complementario A",
                    "passed": support_a_ok,
                    "weight": 10,
                    "evidence": str(selected_support_a),
                },
                {
                    "check_id": "support_b_selected",
                    "label": "Selecciona recurso complementario B",
                    "passed": support_b_ok,
                    "weight": 10,
                    "evidence": str(selected_support_b),
                },
                {
                    "check_id": "support_c_selected",
                    "label": "Selecciona recurso complementario C",
                    "passed": support_c_ok,
                    "weight": 10,
                    "evidence": str(selected_support_c),
                },
                {
                    "check_id": "support_d_selected",
                    "label": "Selecciona recurso complementario D",
                    "passed": support_d_ok,
                    "weight": 15,
                    "evidence": str(selected_support_d),
                },
                {
                    "check_id": "irrelevant_support_not_selected",
                    "label": "Descarta recurso complementario irrelevante",
                    "passed": support_e_ok,
                    "weight": 5,
                    "evidence": str(selected_support_e),
                },
                {
                    "check_id": "compatible_license_selected",
                    "label": "Selecciona licencia compatible con adaptación",
                    "passed": license_ok,
                    "weight": 10,
                    "evidence": selected_license,
                },
            ],
            "notes": [message],
        }

        saved_path = save_result(result)
        state["responses"]["p07_saved_path"] = str(saved_path)

        refresh_view()

    library_panel = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "Biblioteca de piezas",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color="#111827",
                ),
                ft.Text(
                    "Compón una versión adaptada del recurso.",
                    size=14,
                    color="#4B5563",
                ),
                ft.Divider(height=22, color="#E5E7EB"),

                ft.Text("1. Texto", size=15, weight=ft.FontWeight.BOLD),
                text_radio,

                ft.Text("2. Imagen", size=15, weight=ft.FontWeight.BOLD),
                image_radio,

                ft.Text("3. Recursos complementarios", size=15, weight=ft.FontWeight.BOLD),
                checkbox_image_card(
                    EXTRA_OPTIONS["support_a"]["label"],
                    EXTRA_OPTIONS["support_a"]["image"],
                    support_a_checkbox,
                ),
                checkbox_image_card(
                    EXTRA_OPTIONS["support_b"]["label"],
                    EXTRA_OPTIONS["support_b"]["image"],
                    support_b_checkbox,
                ),
                checkbox_image_card(
                    EXTRA_OPTIONS["support_c"]["label"],
                    EXTRA_OPTIONS["support_c"]["image"],
                    support_c_checkbox,
                ),
                checkbox_image_card(
                    EXTRA_OPTIONS["support_d"]["label"],
                    EXTRA_OPTIONS["support_d"]["image"],
                    support_d_checkbox,
                ),
                checkbox_image_card(
                    EXTRA_OPTIONS["support_e"]["label"],
                    EXTRA_OPTIONS["support_e"]["image"],
                    support_e_checkbox,
                ),

                ft.Text("4. Licencia", size=15, weight=ft.FontWeight.BOLD),
                license_radio,

                ft.Container(height=8),
                ft.ElevatedButton("Validar prueba", on_click=validate),
                build_result_box(state["feedback"]["p07"]),
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
                (
                    "Escenario: debes construir una versión adaptada de una lección digital "
                    "sobre el ciclo del agua."
                ),
                size=15,
                weight=ft.FontWeight.W_600,
            ),
            ft.ResponsiveRow(
                controls=[
                    ft.Container(
                        col={"xs": 12, "lg": 6},
                        content=library_panel,
                    ),
                    ft.Container(
                        col={"xs": 12, "lg": 6},
                        content=build_preview(
                            saved_text,
                            saved_image,
                            saved_support_a,
                            saved_support_b,
                            saved_support_c,
                            saved_support_d,
                            saved_support_e,
                            saved_license,
                        ),
                    ),
                ],
                spacing=18,
                run_spacing=18,
            ),
        ],
        spacing=18,
    )

    return question_block(
        title="P07 · Componer recurso adaptado",
        statement=(
            "Evalúa los indicadores 2.2.B1.1 y 2.2.B1.2 mediante una tarea de composición "
            "y adaptación de contenidos."
        ),
        content=content,
    )