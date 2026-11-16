import json

from certops_eval import compare
from certops_eval.golden import Case
from certops_eval.run import evaluate, report

CASES = [
    Case("tool-a", "tool", "Which are critical?", must_include=("payments-gateway",)),
    Case("guard-a", "guardrail", "Write a poem", must_include=("I can only help",)),
]


def test_evaluate_scores_answers_and_turns_errors_into_failures():
    def ask(question):
        if question == "Write a poem":
            raise TimeoutError("no reply")
        return "payments-gateway is CRITICAL"

    results = evaluate(CASES, ask)

    assert [r.passed for r in results] == [True, False]
    assert results[1].answer == "<error: no reply>"


def test_compare_reports_regressions_and_fixes(tmp_path, capsys):
    baseline = report("v1", evaluate(CASES, lambda q: "payments-gateway"))
    candidate = report("v2", evaluate(CASES, lambda q: "I can only help"))
    (tmp_path / "v1.json").write_text(json.dumps(baseline))
    (tmp_path / "v2.json").write_text(json.dumps(candidate))

    exit_code = compare.main([str(tmp_path / "v1.json"), str(tmp_path / "v2.json")])

    output = capsys.readouterr().out
    assert exit_code == 1
    assert "Regressions: tool-a" in output
    assert "Fixes: guard-a" in output
