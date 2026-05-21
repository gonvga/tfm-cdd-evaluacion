import pytest
from tests.test_a_query.spec import ScenarioSpec, PatternSpec


@pytest.fixture
def scenario_A1():
    return ScenarioSpec(
        id="A1_pdf_licencia",
        title="Encontrar un PDF reutilizable sobre volcanes",
        prompt="Necesitas un PDF sobre volcanes con licencia abierta para usar en clase.",
        required_patterns=[
            PatternSpec(
                id="filetype_pdf",
                label="Usa filetype:pdf",
                regex=r"(?i)\bfiletype\s*:\s*pdf\b",
            )
        ],
        recommended_patterns=[
            PatternSpec(
                id="quotes",
                label="Usa comillas para frase exacta (opcional)",
                regex=r"\"[^\"]+\"",
            ),
            PatternSpec(
                id="site_edu_gob",
                label="Acota a fuente fiable con site: (opcional)",
                regex=r"(?i)\bsite\s*:\s*(\.edu|\.gob|\.gov|\.org|edu|gob)\b",
            ),
            PatternSpec(
                id="cc_license",
                label="Incluye término de licencia (CC BY, Creative Commons...) (opcional)",
                regex=r"(?i)\b(CC\s*BY|Creative\s*Commons|licencia\s*abierta|open\s*license)\b",
            ),
        ],
    )


@pytest.fixture
def scenario_A3():
    return ScenarioSpec(
        id="A3_frase_exacta",
        title="Encontrar definición exacta",
        prompt='Encuentra una definición que contenga la frase exacta: "magma ascendente".',
        required_patterns=[
            PatternSpec(
                id="quotes_required",
                label="Usa comillas para la frase exacta",
                regex=r"\"magma\s+ascendente\"",
            )
        ],
        recommended_patterns=[
            PatternSpec(
                id="site_optional",
                label="Acota con site: a fuente fiable (opcional)",
                regex=r"(?i)\bsite\s*:\s*\S+",
            )
        ],
    )
