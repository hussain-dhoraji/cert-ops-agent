from pathlib import Path

import pytest

from certops_eval import golden

GOLDEN = Path(__file__).parents[1] / "golden.yaml"


def test_repository_golden_set_is_valid_and_covers_every_category():
    cases = golden.load(GOLDEN)

    assert len(cases) >= 20
    assert {c.category for c in cases} == set(golden.CATEGORIES)


@pytest.mark.parametrize("content, message", [
    ("[]", "non-empty list"),
    ("- {category: tool, question: q, must_include: [a]}", "without an id"),
    ("- {id: a, category: tool, question: q, must_include: [a]}\n"
     "- {id: a, category: tool, question: q, must_include: [a]}", "duplicate id"),
    ("- {id: a, category: chat, question: q, must_include: [a]}", "category must be"),
    ("- {id: a, category: tool, question: ' ', must_include: [a]}", "question is empty"),
    ("- {id: a, category: tool, question: q}", "at least one check"),
    ("- {id: a, category: tool, question: q, must_contain: [a]}", "unknown keys"),
])
def test_rejects_invalid_golden_sets(tmp_path, content, message):
    path = tmp_path / "golden.yaml"
    path.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        golden.load(path)
