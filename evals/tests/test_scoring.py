from certops_eval.golden import Case
from certops_eval.scoring import score, summarize


def case(**checks):
    return Case(id="c", category="tool", question="q", **checks)


def test_passes_when_all_checks_hold_ignoring_case():
    result = score(case(must_include=("Payments-Gateway",), must_include_any=("critical", "expired"),
                        must_not_include=("internal-wiki",)),
                   "payments-gateway is CRITICAL (5 days).", 900)

    assert result.passed
    assert result.latency_ms == 900


def test_reports_each_failed_check():
    result = score(case(must_include=("payments-gateway",), must_include_any=("critical", "expired"),
                        must_not_include=("internal-wiki",)),
                   "internal-wiki is OK.", 100)

    assert result.failures == (
        "missing 'payments-gateway'",
        "missing any of ['critical', 'expired']",
        "contains forbidden 'internal-wiki'",
    )


def test_summary_counts_pass_rate_per_category_and_latency():
    results = [
        score(Case("a", "tool", "q", must_include=("x",)), "x", 100),
        score(Case("b", "tool", "q", must_include=("x",)), "y", 300),
        score(Case("c", "guardrail", "q", must_include=("x",)), "x", 200),
    ]

    summary = summarize(results)

    assert summary["total"] == 3
    assert summary["passed"] == 2
    assert summary["pass_rate"] == 0.667
    assert summary["by_category"] == {"tool": 0.5, "guardrail": 1.0}
    assert summary["latency_ms_p50"] == 200
