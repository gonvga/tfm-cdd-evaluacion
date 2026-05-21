from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

"""
Define los modelos de datos comunes a todas las pruebas.
    - CheckResult: resultado de un criterio individual
    - TestResult: resultado completo de una prueba
    - Garantiza que todas las pruebas devuelvan resultados con la misma estructura
"""

@dataclass
class CheckResult:
    check_id: str
    label: str
    passed: bool
    weight: int
    evidence: Optional[str] = None


@dataclass
class TestResult:
    test_id: str
    scenario_id: str
    scenario_title: str
    timestamp_utc: str
    score_0_100: int
    level_hint: str
    checks: List[CheckResult]
    notes: List[str]
    payload: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()
