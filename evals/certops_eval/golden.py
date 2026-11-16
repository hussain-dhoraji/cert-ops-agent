from dataclasses import dataclass
from pathlib import Path

import yaml

CATEGORIES = ("tool", "grounding", "guardrail")
_CHECKS = ("must_include", "must_include_any", "must_not_include")


@dataclass(frozen=True)
class Case:
    id: str
    category: str
    question: str
    must_include: tuple[str, ...] = ()
    must_include_any: tuple[str, ...] = ()
    must_not_include: tuple[str, ...] = ()


def load(path: Path) -> list[Case]:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, list) or not raw:
        raise ValueError(f"{path}: expected a non-empty list of cases")

    cases: list[Case] = []
    seen: set[str] = set()
    for entry in raw:
        case_id = entry.get("id")
        if not case_id:
            raise ValueError(f"{path}: case without an id: {entry}")
        if case_id in seen:
            raise ValueError(f"{path}: duplicate id {case_id}")
        seen.add(case_id)

        unknown = set(entry) - {"id", "category", "question", *_CHECKS}
        if unknown:
            raise ValueError(f"{case_id}: unknown keys {sorted(unknown)}")
        if entry.get("category") not in CATEGORIES:
            raise ValueError(f"{case_id}: category must be one of {CATEGORIES}")
        if not str(entry.get("question", "")).strip():
            raise ValueError(f"{case_id}: question is empty")
        if not any(entry.get(check) for check in _CHECKS):
            raise ValueError(f"{case_id}: needs at least one check")

        cases.append(Case(
            id=case_id,
            category=entry["category"],
            question=entry["question"],
            **{check: tuple(str(p) for p in entry.get(check) or ()) for check in _CHECKS},
        ))
    return cases
