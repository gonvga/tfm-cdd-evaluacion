from __future__ import annotations

from tests.test_a_query.plugin import plugin as test_a
from tests.test_b_resource.plugin import plugin as test_b

"""
Registro central de pruebas.
    - Lista todas las pruebas disponibles
    - Define el orden en el que aparecen
    - Para añadir o quitar pruebas solo hay que modificar este archivo
"""

# Reordena aquí sin tocar la UI
TEST_PLUGINS = [
    test_a,
    test_b,
]
