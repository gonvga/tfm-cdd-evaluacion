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


def ensure_results_dir(path: Path = RESULTS_DIR) -> None:
    path.mkdir(parents=True, exist_ok=True)


def get_result_subdir(result_dict: Dict[str, Any]) -> Path:
    test_id = str(result_dict.get("test_id", "test")).lower()
    scenario_id = str(result_dict.get("scenario_id", "scenario")).lower()
    competence = "general"

    for part in scenario_id.split("_"):
        if part.startswith("comp") and part[4:].isdigit():
            competence = part
            break

    return RESULTS_DIR / competence / test_id


def save_result(result_dict: Dict[str, Any]) -> Path:
    result_dir = get_result_subdir(result_dict)
    ensure_results_dir(result_dir)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    test_id = result_dict.get("test_id", "test")
    scenario_id = result_dict.get("scenario_id", "scenario")
    filename = f"{ts}__{test_id}__{scenario_id}.json"
    path = result_dir / filename
    path.write_text(json.dumps(result_dict, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
