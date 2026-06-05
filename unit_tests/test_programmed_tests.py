from pathlib import Path
import tempfile
import unittest
import unicodedata
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

import flet as ft

from ui.views.evaluation_view import TEST_FLOW, build_evaluation_view, initial_evaluation_state
from ui.test_views.comp21 import (
    p01_identificar_recursos as p01,
    p02_seleccionar_recurso as p02,
    p03_banco_recursos as p03,
    p04_curacion_contenidos as p04,
)
from ui.test_views.comp22 import (
    p05_corregir_ficha as p05,
    p06_completar_plantilla as p06,
    p07_adaptar_recurso as p07,
    p08_disenar_secuencia as p08,
)
from ui.test_views.comp23 import (
    p09_compartir_catalogar as p09,
    p10_configurar_publicacion as p10,
    p11_publicar_recurso as p11,
    p12_optimizar_repositorio as p12,
)


IMPLEMENTED_TESTS = [
    ("p01", p01, p01.build_test_p01),
    ("p02", p02, p02.build_test_p02),
    ("p03", p03, p03.build_test_p03),
    ("p04", p04, p04.build_test_p04),
    ("p05", p05, p05.build_test_p05),
    ("p06", p06, p06.build_test_p06),
    ("p07", p07, p07.build_test_p07),
    ("p08", p08, p08.build_test_p08),
    ("p09", p09, p09.build_test_p09),
    ("p10", p10, p10.build_test_p10),
    ("p11", p11, p11.build_test_p11),
    ("p12", p12, p12.build_test_p12),
]

TEST_NAMES = {
    "p01": "identificar_recursos_validos",
    "p02": "seleccionar_el_mejor_recurso",
    "p03": "organizar_banco_de_recursos",
    "p04": "curacion_avanzada_de_contenidos",
    "p05": "corregir_ficha_educativa",
    "p06": "completar_plantilla_didactica",
    "p07": "adaptar_recurso_accesible",
    "p08": "disenar_secuencia_digital",
    "p09": "compartir_catalogar_contenidos",
    "p10": "configurar_publicacion_segura",
    "p11": "publicar_recurso_metadatos",
    "p12": "optimizar_repositorio",
}


def expected_ids(options):
    return [option["id"] for option in options if option["expected"]]


def expected_id(options):
    return next(option["id"] for option in options if option["expected"])


def passing_query():
    return (
        '"cambio climatico" sostenibilidad huella de carbono video subtitulos '
        "transcripcion imagen infografia CC licencia abierta Creative Commons "
        "H5P actividad participacion alumnado filetype:pdf site:.edu "
        "repositorio Procomun desinformacion bulos verificacion interactivo"
    )


def children(control):
    for attr in ("controls", "rows", "cells"):
        for child in getattr(control, attr, None) or []:
            yield child
    content = getattr(control, "content", None)
    if content is not None:
        yield content


def iter_controls(control):
    yield control
    for child in children(control):
        yield from iter_controls(child)


def find_validate_button(control):
    for item in iter_controls(control):
        label = getattr(item, "text", None)
        content = getattr(item, "content", None)
        if label is None and isinstance(content, str):
            label = content
        if isinstance(item, ft.ElevatedButton) and label == "Validar prueba":
            return item
    raise AssertionError("No se encontro el boton 'Validar prueba'.")


def strip_accents(value):
    return "".join(
        char
        for char in unicodedata.normalize("NFD", value)
        if unicodedata.category(char) != "Mn"
    )


def patch_save_result(module, tmp_path):
    original = module.save_result
    module.save_result = lambda result: tmp_path / f"{result['test_id'].lower()}_result.json"
    return original


def run_validation(test_id, module, build_test, state, tmp_path):
    refresh_calls = []
    control = build_test(state, lambda: refresh_calls.append(test_id))
    button = find_validate_button(control)
    button.on_click(None)
    assert refresh_calls == [test_id]


def correct_p01(data):
    return {
        "p01_classification": {
            label["id"]: label["expected_category"]
            for label in data["classification"]["labels"]
        },
        "p01_search_tools": expected_ids(data["search_tools"]["options"]),
        "p01_metadata_answer": expected_id(data["metadata_question"]["options"]),
        "p01_folder_name": data["organization"]["folder_hint"],
        "p01_folder_files": [
            item["id"]
            for item in data["organization"]["files"]
            if item["expected_in_folder"]
        ],
    }


def correct_p02(data):
    return {
        "p02_requirements": expected_ids(data["requirements"]["options"]),
        "p02_repositories": expected_ids(data["repositories"]["options"]),
        "p02_filters": expected_ids(data["filters"]["options"]),
        "p02_selected": data["resources"]["expected_id"],
        "p02_opened_details": [data["resources"]["expected_id"]],
    }


def correct_p03(data):
    return {
        "p03_queries": {
            task["id"]: passing_query()
            for task in data["queries"]["tasks"]
        },
        "p03_catalog": {
            resource["id"]: {
                "folder": resource["expected_folder"],
                "difficulty": resource["expected_difficulty"],
                "tag": resource["expected_tag"],
            }
            for resource in data["cataloging"]["resources"]
        },
        "p03_systems": expected_ids(data["system"]["options"]),
        "p03_opened_resources": [
            resource["id"] for resource in data["cataloging"]["resources"]
        ],
    }


def correct_p04(data):
    return {
        "p04_catalog": {
            resource["id"]: {
                "bloom": resource["expected_bloom"],
                "competence": resource["expected_competence"],
                "decision": resource["expected_decision"],
                "technical": str(resource["minimum_scores"]["technical"]),
                "truth": str(resource["minimum_scores"]["truth"]),
                "relevance": str(resource["minimum_scores"]["relevance"]),
            }
            for resource in data["protocol"]["resources"]
        },
        "p04_queries": {
            task["id"]: passing_query()
            for task in data["advice"]["tasks"]
        },
        "p04_repository_actions": expected_ids(data["repositories"]["options"]),
    }


def correct_p05(data):
    return {
        "p05_license": expected_ids(data["license"]["options"])[0],
        "p05_apa_option": expected_id(data["license"]["apa_options"]),
        "p05_accessibility": expected_ids(data["accessibility"]["options"]),
        "p05_alt_text_option": expected_id(data["accessibility"]["alt_text_options"]),
        "p05_content_option": expected_id(data["content"]["options"]),
        "p05_tools": {
            task["id"]: task["expected"]
            for task in data["tools"]["tasks"]
        },
    }


def correct_p06(data):
    return {
        "p06_answers": {
            question["id"]: expected_id(question["options"])
            for question in data["questions"]
        }
    }


def correct_p07(data):
    return {
        "p07_blocks": list(data["builder"]["required_order"]),
        "p07_license": expected_id(data["license"]["options"]),
        "p07_metadata": {
            field["id"]: expected_id(field["options"])
            for field in data["metadata"]["fields"]
        },
    }


def correct_p08(data):
    return {
        "p08_sequence": list(data["resource_bank"]["required_order"]),
        "p08_modifications": expected_ids(data["modifications"]["options"]),
        "p08_safety": expected_ids(data["safety"]["options"]),
        "p08_evaluation_matrix": expected_ids(data["evaluation_matrix"]["options"]),
        "p08_export": {
            field["id"]: expected_id(field["options"])
            for field in data["export"]["fields"]
        },
    }


def correct_p09(data):
    return {
        "p09_environment": expected_ids(data["environment"]["options"]),
        "p09_rights": expected_ids(data["rights"]["options"]),
        "p09_permissions": {
            field["id"]: expected_id(field["options"])
            for field in data["permissions"]["fields"]
        },
        "p09_metadata": {
            field["id"]: expected_id(field["options"])
            for field in data["metadata"]["fields"]
        },
    }


def correct_p10(data):
    return {
        "p10_management": expected_ids(data["management"]["options"]),
        "p10_permissions": {
            field["id"]: expected_id(field["options"])
            for field in data["permissions"]["fields"]
        },
        "p10_cataloging": {
            field["id"]: expected_id(field["options"])
            for field in data["cataloging"]["fields"]
        },
        "p10_package": {
            field["id"]: expected_id(field["options"])
            for field in data["package"]["fields"]
        },
    }


def correct_p11(data):
    return {
        "p11_publication_map": {
            item["id"]: item["expected"]
            for item in data["publication_map"]["items"]
        },
        "p11_permission_matrix": {
            agent["id"]: agent["expected"]
            for agent in data["permission_matrix"]["agents"]
        },
        "p11_catalog_record": {
            **{
                field["id"]: (
                    "; ".join(field["expected_terms"])
                    if "expected_terms" in field
                    else field["expected"]
                )
                for field in data["catalog_record"]["text_fields"]
            },
            **{
                field["id"]: field["expected"]
                for field in data["catalog_record"]["select_fields"]
            },
        },
        "p11_imscp_components": [
            component["id"]
            for component in data["imscp_package"]["components"]
            if component["expected"]
        ],
        "p11_imscp_settings": {
            setting["id"]: setting["expected"]
            for setting in data["imscp_package"]["settings"]
        },
    }


def correct_p12(data):
    return {
        "p12_repository": [
            item["id"]
            for item in data["repository"]["options"]
            if item["expected"]
        ],
        "p12_access": [
            item["id"]
            for item in data["access"]["options"]
            if item["expected"]
        ],
        "p12_advice": [
            item["id"]
            for item in data["advice"]["options"]
            if item["expected"]
        ],
        "p12_catalog_record": {
            **{
                field["id"]: (
                    "; ".join(field["expected_terms"])
                    if "expected_terms" in field
                    else field.get("expected", "")
                )
                for field in data["catalog_record"]["text_fields"]
            },
            **{
                field["id"]: expected_id(field["options"])
                for field in data["catalog_record"]["select_fields"]
            },
        },
    }


CORRECT_RESPONSES = {
    "p01": correct_p01,
    "p02": correct_p02,
    "p03": correct_p03,
    "p04": correct_p04,
    "p05": correct_p05,
    "p06": correct_p06,
    "p07": correct_p07,
    "p08": correct_p08,
    "p09": correct_p09,
    "p10": correct_p10,
    "p11": correct_p11,
    "p12": correct_p12,
}


class ProgrammedTestsCase(unittest.TestCase):
    def setUp(self):
        self.warning_context = warnings.catch_warnings()
        self.warning_context.__enter__()
        warnings.simplefilter("ignore", DeprecationWarning)

        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmpdir.name)
        self.original_save_results = {}

    def tearDown(self):
        for module, original in self.original_save_results.items():
            module.save_result = original
        self.tmpdir.cleanup()
        self.warning_context.__exit__(None, None, None)

    def patch_save_result(self, module):
        if module not in self.original_save_results:
            self.original_save_results[module] = patch_save_result(module, self.tmp_path)

    def assert_accepts_correct_response(self, test_id, module, build_test):
        self.patch_save_result(module)
        state = initial_evaluation_state()
        data = module.load_test_data()
        state["responses"].update(CORRECT_RESPONSES[test_id](data))

        run_validation(test_id, module, build_test, state, self.tmp_path)

        self.assertIs(state["completed"][test_id], True)
        self.assertIs(state["feedback"][test_id]["ok"], True)
        self.assertEqual(
            state["feedback"][test_id]["message"],
            data["feedback"]["success"],
        )
        self.assertEqual(
            state["responses"][f"{test_id}_saved_path"],
            str(self.tmp_path / f"{data['test_id'].lower()}_result.json"),
        )

    def assert_rejects_empty_response(self, test_id, module, build_test):
        self.patch_save_result(module)
        state = initial_evaluation_state()
        data = module.load_test_data()

        run_validation(test_id, module, build_test, state, self.tmp_path)

        self.assertIs(state["completed"][test_id], False)
        self.assertIs(state["feedback"][test_id]["ok"], False)
        self.assertEqual(
            state["feedback"][test_id]["message"],
            data["feedback"]["failure"],
        )

    def test_evaluation_flow_has_routes_for_all_implemented_tests(self):
        routed_test_ids = {test_id for test_id, _, _ in IMPLEMENTED_TESTS}
        configured_test_ids = {item["id"] for item in TEST_FLOW}

        self.assertLessEqual(routed_test_ids, configured_test_ids)

    def test_evaluation_view_does_not_show_placeholder_for_p12(self):
        class DummyPage:
            def update(self):
                pass

        state = initial_evaluation_state()
        state["active_competence"] = "2.3"
        state["active_test"] = "p12"
        control = build_evaluation_view(DummyPage(), state, lambda: None)

        texts = [
            item.value
            for item in iter_controls(control)
            if isinstance(item, ft.Text) and item.value
        ]
        normalized = {strip_accents(text) for text in texts}
        self.assertNotIn("Prueba todavia no implementada", normalized)


def _make_acceptance_test(test_id, module, build_test):
    def test(self):
        self.assert_accepts_correct_response(test_id, module, build_test)

    test.__name__ = f"test_{test_id}_{TEST_NAMES[test_id]}__respuesta_correcta_supera"
    return test


def _make_rejection_test(test_id, module, build_test):
    def test(self):
        self.assert_rejects_empty_response(test_id, module, build_test)

    test.__name__ = f"test_{test_id}_{TEST_NAMES[test_id]}__respuesta_vacia_no_supera"
    return test


for _test_id, _module, _build_test in IMPLEMENTED_TESTS:
    setattr(
        ProgrammedTestsCase,
        f"test_{_test_id}_{TEST_NAMES[_test_id]}__respuesta_correcta_supera",
        _make_acceptance_test(_test_id, _module, _build_test),
    )
    setattr(
        ProgrammedTestsCase,
        f"test_{_test_id}_{TEST_NAMES[_test_id]}__respuesta_vacia_no_supera",
        _make_rejection_test(_test_id, _module, _build_test),
    )


if __name__ == "__main__":
    unittest.main()
