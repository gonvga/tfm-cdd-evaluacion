from __future__ import annotations
from typing import Any, Dict, Tuple

from core.storage import save_result

"""
Orquestador de ejecución.
    - Ejecuta una prueba
    - Recoge su resultado
    - Lo guarda en disco usando storage
    - Devuelve el resultado a la interfaz
"""

def run_test(plugin, payload: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    """
    Ejecuta un plugin de prueba.
    Devuelve (result_dict, saved_path_str).
    """
    result = plugin.run(payload)
    result_dict = result.to_dict()
    saved_path = save_result(result_dict)
    return result_dict, str(saved_path)
