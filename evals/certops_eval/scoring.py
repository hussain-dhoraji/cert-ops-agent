from dataclasses import dataclass
from statistics import median, quantiles

from certops_eval.golden import CATEGORIES, Case


@dataclass(frozen=True)
class Result:
    case_id: str
    category: str
    question: str
    answer: str
    latency_ms: int
    failures: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.failures


def score(case: Case, answer: str, latency_ms: int) -> Result:
    text = answer.casefold()
    failures = [f"missing {p!r}" for p in case.must_include if p.casefold() not in text]
    if case.must_include_any and not any(p.casefold() in text for p in case.must_include_any):
        failures.append(f"missing any of {list(case.must_include_any)}")
    failures += [f"contains forbidden {p!r}" for p in case.must_not_include if p.casefold() in text]
    return Result(case.id, case.category, case.question, answer, latency_ms, tuple(failures))


def summarize(results: list[Result]) -> dict:
    latencies = sorted(r.latency_ms for r in results)
    by_category = {}
    for category in CATEGORIES:
        subset = [r for r in results if r.category == category]
        if subset:
            by_category[category] = _rate(subset)
    return {
        "total": len(results),
        "passed": sum(r.passed for r in results),
        "pass_rate": _rate(results),
        "by_category": by_category,
        "latency_ms_p50": int(median(latencies)) if latencies else 0,
        "latency_ms_p95": int(quantiles(latencies, n=20)[-1]) if len(latencies) > 1 else (latencies or [0])[0],
    }


def _rate(results: list[Result]) -> float:
    return round(sum(r.passed for r in results) / len(results), 3) if results else 0.0
