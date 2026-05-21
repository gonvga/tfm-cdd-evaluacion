import flet as ft
from datetime import datetime

from core.storage import save_result
from ui.components import question_block


TEST_ID = "P04"
SCENARIO_ID = "comp21_b2_curacion_contenidos"


def build_result_box(feedback_data: dict) -> ft.Control:
    if feedback_data["ok"] is None:
        return ft.Container()

    ok = feedback_data["ok"]

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Resultado de la prueba", size=17, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Text(feedback_data["message"], size=14, color=ft.Colors.WHITE),
            ],
            spacing=8,
        ),
        bgcolor=ft.Colors.GREEN if ok else ft.Colors.RED,
        border_radius=12,
        padding=20,
    )


def build_test_p04(state: dict, refresh_view) -> ft.Control:
    resources = [
        {
            "id": "A",
            "title": "Guía docente completa CC BY",
            "license": "CC BY",
            "accessibility": "Alta",
            "quality": "Alta",
            "reuse": "Alta",
        },
        {
            "id": "B",
            "title": "Vídeo sin subtítulos",
            "license": "CC BY",
            "accessibility": "Baja",
            "quality": "Media",
            "reuse": "Media",
        },
        {
            "id": "C",
            "title": "Infografía accesible CC BY-SA",
            "license": "CC BY-SA",
            "accessibility": "Alta",
            "quality": "Alta",
            "reuse": "Alta",
        },
        {
            "id": "D",
            "title": "Artículo sin autoría",
            "license": "No indicada",
            "accessibility": "Media",
            "quality": "Baja",
            "reuse": "Baja",
        },
        {
            "id": "E",
            "title": "Plantilla editable CC0",
            "license": "CC0",
            "accessibility": "Alta",
            "quality": "Media",
            "reuse": "Alta",
        },
        {
            "id": "F",
            "title": "Presentación comercial",
            "license": "Copyright",
            "accessibility": "Media",
            "quality": "Alta",
            "reuse": "Baja",
        },
    ]

    expected_selected = {"A", "C", "E"}
    saved_scores = state["responses"].get("p04_scores", {})
    saved_selected = state["responses"].get("p04_selected", [])

    score_fields = {}
    checkboxes = {}

    rows = []

    for resource in resources:
        rid = resource["id"]

        quality_dd = ft.Dropdown(
            label="Calidad",
            value=saved_scores.get(rid, {}).get("quality"),
            width=120,
            options=[ft.dropdown.Option(str(i)) for i in range(1, 6)],
        )
        accessibility_dd = ft.Dropdown(
            label="Accesibilidad",
            value=saved_scores.get(rid, {}).get("accessibility"),
            width=120,
            options=[ft.dropdown.Option(str(i)) for i in range(1, 6)],
        )
        license_dd = ft.Dropdown(
            label="Licencia",
            value=saved_scores.get(rid, {}).get("license"),
            width=120,
            options=[ft.dropdown.Option(str(i)) for i in range(1, 6)],
        )
        reuse_dd = ft.Dropdown(
            label="Reutilización",
            value=saved_scores.get(rid, {}).get("reuse"),
            width=130,
            options=[ft.dropdown.Option(str(i)) for i in range(1, 6)],
        )

        cb = ft.Checkbox(value=rid in saved_selected)

        score_fields[rid] = {
            "quality": quality_dd,
            "accessibility": accessibility_dd,
            "license": license_dd,
            "reuse": reuse_dd,
        }
        checkboxes[rid] = cb

        rows.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                cb,
                                ft.Text(f"{rid} · {resource['title']}", size=16, weight=ft.FontWeight.BOLD),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Text(
                            f"Datos visibles: licencia {resource['license']} · accesibilidad {resource['accessibility']} · calidad {resource['quality']} · reutilización {resource['reuse']}",
                            size=13,
                            color=ft.Colors.GREY_700,
                        ),
                        ft.Row(
                            controls=[quality_dd, accessibility_dd, license_dd, reuse_dd],
                            wrap=True,
                            spacing=10,
                        ),
                    ],
                    spacing=8,
                ),
                bgcolor="#F9FAFB",
                border=ft.border.all(1, "#E5E7EB"),
                border_radius=16,
                padding=16,
            )
        )

    def validate(e):
        scores = {}
        selected = []

        for rid, fields in score_fields.items():
            scores[rid] = {
                key: field.value
                for key, field in fields.items()
            }

        for rid, cb in checkboxes.items():
            if cb.value:
                selected.append(rid)

        state["responses"]["p04_scores"] = scores
        state["responses"]["p04_selected"] = selected

        missing_scores = any(
            value is None
            for resource_scores in scores.values()
            for value in resource_scores.values()
        )

        if missing_scores:
            state["completed"]["p04"] = False
            state["feedback"]["p04"] = {
                "ok": False,
                "message": "Debes puntuar los cuatro criterios de los seis recursos antes de validar.",
            }
            refresh_view()
            return

        selected_set = set(selected)
        selection_ok = selected_set == expected_selected

        high_quality_selected = all(
            sum(int(value) for value in scores[rid].values()) >= 16
            for rid in expected_selected
        )

        closed_resources_penalized = (
            int(scores["D"]["license"]) <= 2
            and int(scores["F"]["license"]) <= 2
        )

        ok = selection_ok and high_quality_selected and closed_resources_penalized

        checks_passed = sum([selection_ok, high_quality_selected, closed_resources_penalized])
        score = round((checks_passed / 3) * 100)

        state["completed"]["p04"] = ok

        message = (
            "Prueba superada. Has aplicado criterios de curación adecuados y has recomendado recursos reutilizables y accesibles."
            if ok
            else "Prueba no superada. Revisa la selección final y penaliza los recursos sin licencia abierta o con baja accesibilidad."
        )

        state["feedback"]["p04"] = {"ok": ok, "message": message}

        result = {
            "test_id": TEST_ID,
            "scenario_id": SCENARIO_ID,
            "scenario_title": "Curación avanzada de contenidos",
            "timestamp_utc": datetime.utcnow().isoformat(),
            "score_0_100": score,
            "level_hint": "B2" if ok else "B1",
            "payload": {
                "scores": scores,
                "selected": selected,
                "expected_selected": sorted(expected_selected),
                "selection_ok": selection_ok,
                "high_quality_selected": high_quality_selected,
                "closed_resources_penalized": closed_resources_penalized,
            },
            "checks": [
                {
                    "check_id": "final_selection",
                    "label": "Selecciona los tres recursos más adecuados",
                    "passed": selection_ok,
                    "weight": 40,
                    "evidence": ", ".join(selected),
                },
                {
                    "check_id": "selected_resources_scored_high",
                    "label": "Puntúa alto los recursos realmente adecuados",
                    "passed": high_quality_selected,
                    "weight": 30,
                    "evidence": str(scores),
                },
                {
                    "check_id": "closed_resources_penalized",
                    "label": "Penaliza recursos sin licencia abierta",
                    "passed": closed_resources_penalized,
                    "weight": 30,
                    "evidence": f"D={scores['D']['license']}, F={scores['F']['license']}",
                },
            ],
            "notes": [message],
        }

        saved_path = save_result(result)
        state["responses"]["p04_saved_path"] = str(saved_path)

        refresh_view()

    content = ft.Column(
        controls=[
            ft.Text(
                "Escenario: debes recomendar tres recursos para un equipo docente. Para decidir, puntúa cada recurso del 1 al 5 en calidad, accesibilidad, licencia y reutilización.",
                size=15,
                weight=ft.FontWeight.W_600,
            ),
            ft.Text(
                "Después, marca los tres recursos que recomendarías. Debes priorizar recursos abiertos, accesibles y reutilizables.",
                size=14,
            ),
            ft.Column(controls=rows, spacing=12),
            ft.Container(height=8),
            ft.ElevatedButton("Validar prueba", on_click=validate),
            build_result_box(state["feedback"]["p04"]),
        ],
        spacing=12,
    )

    return question_block(
        title="P04 · Curación avanzada de contenidos",
        statement=(
            "Evalúa los indicadores 2.1.B2.1, 2.1.B2.2 y 2.1.B2.3 mediante una tarea de valoración, "
            "catalogación y recomendación de contenidos digitales."
        ),
        content=content,
    )