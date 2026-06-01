import json
from datetime import datetime
from pathlib import Path

import flet as ft

from core.storage import save_result
from ui.components import question_block


TEST_ID = "P06"
DATA_PATH = Path("data/p06_comp22_a2.json")


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


def build_option_card(
    option: dict,
    selected_option: str | None,
    validated: bool,
) -> ft.Control:
    selected = selected_option == option["id"]
    show_feedback = validated and selected
    option_ok = bool(option["expected"])
    bgcolor = feedback_colors(option_ok)[0] if show_feedback else "#F9FAFB"
    border_color = feedback_colors(option_ok)[1] if show_feedback else "#E5E7EB"

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Radio(value=option["id"], label=option["label"]),
                *(
                    [inline_feedback(option["feedback"], option_ok)]
                    if show_feedback
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


def build_test_p06(state: dict, refresh_view) -> ft.Control:
    test_data = load_test_data()
    questions = test_data["questions"]
    saved_answers = state["responses"].get("p06_answers", {})

    question_controls: dict[str, ft.RadioGroup] = {}
    p06_feedback = state["feedback"].get("p06", {"ok": None, "message": ""})
    validated = p06_feedback["ok"] is not None

    for question in questions:
        selected = saved_answers.get(question["id"])
        question_controls[question["id"]] = ft.RadioGroup(
            value=selected,
            content=ft.Column(
                controls=[
                    build_option_card(option, selected, validated)
                    for option in question["options"]
                ],
                spacing=8,
            ),
        )

    def validate(e):
        selected_answers = {
            qid: control.value for qid, control in question_controls.items()
        }
        state["responses"]["p06_answers"] = selected_answers

        score = 0
        checks = []

        for question in questions:
            selected = selected_answers[question["id"]]
            option = next(
                (opt for opt in question["options"] if opt["id"] == selected),
                None,
            )
            ok = bool(option and option["expected"])
            score += 20 if ok else 0
            checks.append(
                {
                    "check_id": f"{question['id']}_selection",
                    "label": question["title"],
                    "passed": ok,
                    "weight": 20,
                    "evidence": selected,
                }
            )

        ok = score >= 80
        state["completed"]["p06"] = ok
        state["feedback"]["p06"] = {
            "ok": ok,
            "message": test_data["feedback"]["success"]
            if ok
            else test_data["feedback"]["failure"],
        }

        result = {
            "test_id": TEST_ID,
            "scenario_id": test_data["scenario_id"],
            "scenario_title": test_data["scenario_title"],
            "timestamp_utc": datetime.utcnow().isoformat(),
            "score_0_100": score,
            "level_hint": "A2" if ok else "A1",
            "payload": {
                "selected_answers": selected_answers,
                "expected_answers": {
                    question["id"]: next(
                        (opt["id"] for opt in question["options"] if opt["expected"]),
                        None,
                    )
                    for question in questions
                },
            },
            "checks": checks,
            "notes": [state["feedback"]["p06"]["message"]],
        }

        saved_path = save_result(result)
        state["responses"]["p06_saved_path"] = str(saved_path)
        refresh_view()

    content = ft.Column(
        controls=[
            ft.Text(test_data["intro"], size=15, weight=ft.FontWeight.W_600),
            ft.Text(test_data["description"], size=14),
            *[
                ft.Column(
                    controls=[
                        ft.Text(question["title"], size=15, weight=ft.FontWeight.BOLD),
                        ft.Text(question["description"], size=14, color=ft.Colors.GREY_700),
                        question_controls[question["id"]],
                        *(
                            [
                                inline_feedback(
                                    "Selecciona una opcion antes de validar esta pregunta.",
                                    False,
                                )
                            ]
                            if validated
                            and saved_answers.get(question["id"]) is None
                            else []
                        ),
                        ft.Divider(height=16),
                    ],
                    spacing=8,
                )
                for question in questions
            ],
            ft.ElevatedButton("Validar prueba", on_click=validate),
            build_result_box(state["feedback"]["p06"]),
        ],
        spacing=14,
    )

    return question_block(
        title=test_data["title"],
        statement=test_data["statement"],
        content=content,
    )
