from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

"""
Gestión de almacenamiento de resultados.
    - Crea automáticamente la carpeta results/
    - Guarda los resultados en archivos JSON
    - Cada ejecución genera un archivo independiente y trazable
"""


RESULTS_DIR = Path("results")


def ensure_results_dir() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def save_result(result_dict: Dict[str, Any]) -> Path:
    ensure_results_dir()
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    test_id = result_dict.get("test_id", "test")
    scenario_id = result_dict.get("scenario_id", "scenario")
    filename = f"{ts}__{test_id}__{scenario_id}.json"
    path = RESULTS_DIR / filename
    path.write_text(json.dumps(result_dict, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
