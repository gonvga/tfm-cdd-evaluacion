import pytest
from tests.test_a_query.engine import _match, evaluate_query


def check_key(c):
    for attr in ("id", "check_id", "key", "code", "name"):
        if hasattr(c, attr):
            return getattr(c, attr)
    raise AssertionError(f"CheckResult no tiene campo identificador conocido: {c!r}")


def test_match_returns_false_when_no_match():
    ok, ev = _match(r"\bfiletype\s*:\s*pdf\b", "hola mundo")
    assert ok is False
    assert ev is None


def test_match_returns_trimmed_snippet_max_80_chars():
    text = "X" * 200
    ok, ev = _match(r"X{200}", text)

    assert ok is True
    assert ev is not None
    assert len(ev) == 80
    assert ev.endswith("...")


def test_evaluate_query_empty_query_returns_A0_and_note(scenario_A1, monkeypatch):
    monkeypatch.setattr("core.models.TestResult.now_iso", lambda: "2026-02-10T10:00:00Z")

    result = evaluate_query(test_id="testA", scenario=scenario_A1, query="   ")

    assert result.test_id == "testA"
    assert result.scenario_id == scenario_A1.id
    assert result.scenario_title == scenario_A1.title
    assert result.timestamp_utc == "2026-02-10T10:00:00Z"
    assert result.score_0_100 == 0
    assert result.level_hint == "A0"
    assert result.payload["query"] == ""
    assert "No has escrito ninguna consulta." in result.notes

    assert len(result.checks) == 1
    c = result.checks[0]
    assert check_key(c) == "query_nonempty"
    assert c.passed is False
    assert c.evidence is None


def test_evaluate_query_required_passed_without_recommended(scenario_A1, monkeypatch):
    monkeypatch.setattr("core.models.TestResult.now_iso", lambda: "2026-02-10T10:00:00Z")

    query = "volcanes filetype:pdf"
    result = evaluate_query(test_id="testA", scenario=scenario_A1, query=query)

    assert all(not n.startswith("Falta requisito:") for n in result.notes)

    required = next(c for c in result.checks if check_key(c) == "filetype_pdf")
    assert required.passed is True
    assert required.weight == 30
    assert isinstance(required.evidence, str)
    assert "filetype" in required.evidence.lower()

    rec = [c for c in result.checks if check_key(c) in {"quotes", "site_edu_gob", "cc_license"}]
    assert len(rec) == 3
    assert any(c.passed is False for c in rec)

    assert result.score_0_100 == 50
    assert result.level_hint == "A0"


def test_evaluate_query_missing_required_adds_note(scenario_A1, monkeypatch):
    monkeypatch.setattr("core.models.TestResult.now_iso", lambda: "2026-02-10T10:00:00Z")

    query = '"volcanes" site:.edu CC BY'
    result = evaluate_query(test_id="testA", scenario=scenario_A1, query=query)

    required = next(c for c in result.checks if check_key(c) == "filetype_pdf")
    assert required.passed is False
    assert required.evidence is None
    assert f"Falta requisito: {scenario_A1.required_patterns[0].label}." in result.notes


def test_evaluate_query_all_patterns_hits_A2(scenario_A1, monkeypatch):
    monkeypatch.setattr("core.models.TestResult.now_iso", lambda: "2026-02-10T10:00:00Z")

    query = '"volcanes" filetype:pdf site:.edu CC BY'
    result = evaluate_query(test_id="testA", scenario=scenario_A1, query=query)

    assert result.score_0_100 == 100
    assert result.level_hint == "A2"
    assert all(c.passed for c in result.checks)


def test_evaluate_query_A3_requires_exact_phrase_in_quotes(scenario_A3, monkeypatch):
    monkeypatch.setattr("core.models.TestResult.now_iso", lambda: "2026-02-10T10:00:00Z")

    result1 = evaluate_query(test_id="testA", scenario=scenario_A3, query="magma ascendente site:.edu")
    req1 = next(c for c in result1.checks if check_key(c) == "quotes_required")
    assert req1.passed is False
    assert any(n.startswith("Falta requisito:") for n in result1.notes)

    result2 = evaluate_query(test_id="testA", scenario=scenario_A3, query='"magma ascendente" site:.edu')
    req2 = next(c for c in result2.checks if check_key(c) == "quotes_required")
    assert req2.passed is True
    assert all(not n.startswith("Falta requisito:") for n in result2.notes)
