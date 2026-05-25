import pytest

from ci import trello


def test_build_description_format():
    desc = trello.build_description(
        author="mateo",
        branch="main",
        sha="abcdef1234567890",
        run_url="https://example.com/run/1",
        when="2026-05-25 10:00",
    )
    assert desc == (
        "**Autor:** mateo\n"
        "**Rama:** main\n"
        "**Commit:** abcdef1\n"
        "**Fecha:** 2026-05-25 10:00\n"
        "**Run:** https://example.com/run/1"
    )


def test_build_description_truncates_sha_to_7():
    desc = trello.build_description("a", "b", "0123456789", "u", "w")
    assert "**Commit:** 0123456\n" in desc
    assert "0123456789" not in desc


def test_build_description_missing_values_become_question_mark():
    desc = trello.build_description("", None, "", "", "")
    assert "**Autor:** ?" in desc
    assert "**Rama:** ?" in desc
    assert "**Commit:** ?" in desc
    assert "**Fecha:** ?" in desc
    assert "**Run:** ?" in desc


@pytest.mark.parametrize(
    "stage,name,color",
    [
        ("en_progreso", "En progreso", "blue"),
        ("build_ok", "Build OK", "green"),
        ("failed", "Failed", "red"),
        ("en_produccion", "En produccion", "purple"),
    ],
)
def test_label_for_known_stages(stage, name, color):
    assert trello.label_for(stage) == (name, color)


def test_label_for_unknown_stage_raises():
    with pytest.raises(ValueError):
        trello.label_for("nope")


def test_labels_to_remove_strips_other_stage_labels():
    existing = [
        {"id": "1", "name": "En progreso"},
        {"id": "2", "name": "Build OK"},
    ]
    assert trello.labels_to_remove(existing, keep_name="Build OK") == ["1"]


def test_labels_to_remove_keeps_non_stage_labels():
    existing = [
        {"id": "1", "name": "En progreso"},
        {"id": "9", "name": "bug"},
    ]
    assert trello.labels_to_remove(existing, keep_name="Failed") == ["1"]


def test_labels_to_remove_nothing_when_only_keep_present():
    existing = [{"id": "2", "name": "Build OK"}]
    assert trello.labels_to_remove(existing, keep_name="Build OK") == []
