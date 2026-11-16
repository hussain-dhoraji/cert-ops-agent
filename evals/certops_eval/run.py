"""Runs the golden set against the agent and writes a JSON report.

Usage: python -m certops_eval.run --label v1 --out results/v1.json
Requires COPILOT_TOKEN_ENDPOINT; set DIRECTLINE_DOMAIN for a regional Direct Line endpoint.
"""
import argparse
import json
import os
import sys
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from certops_eval import golden
from certops_eval.directline import DEFAULT_DOMAIN, DirectLineClient
from certops_eval.scoring import Result, score, summarize


def evaluate(cases: list[golden.Case], ask, clock=time.monotonic) -> list[Result]:
    results = []
    for case in cases:
        started = clock()
        try:
            answer = ask(case.question)
        except Exception as error:  # a failed call is a failed case, not a crashed run
            answer = f"<error: {error}>"
        results.append(score(case, answer, int((clock() - started) * 1000)))
        status = "PASS" if results[-1].passed else "FAIL " + "; ".join(results[-1].failures)
        print(f"{case.id}: {status}", flush=True)
    return results


def report(label: str, results: list[Result]) -> dict:
    return {
        "label": label,
        "finished_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "summary": summarize(results),
        "results": [asdict(r) | {"passed": r.passed} for r in results],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--golden", type=Path, default=Path(__file__).parents[1] / "golden.yaml")
    parser.add_argument("--label", required=True, help="Name of what is being evaluated, e.g. the instructions version")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--min-pass-rate", type=float, default=0.9)
    args = parser.parse_args(argv)

    token_endpoint = os.environ.get("COPILOT_TOKEN_ENDPOINT")
    if not token_endpoint:
        parser.error("set COPILOT_TOKEN_ENDPOINT to the agent's Direct Line token endpoint")
    client = DirectLineClient(token_endpoint, os.environ.get("DIRECTLINE_DOMAIN", DEFAULT_DOMAIN))

    results = evaluate(golden.load(args.golden), client.ask)
    data = report(args.label, results)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, indent=2), encoding="utf-8")

    summary = data["summary"]
    print(f"\n{summary['passed']}/{summary['total']} passed ({summary['pass_rate']:.0%}), "
          f"by category {summary['by_category']}, p50 {summary['latency_ms_p50']} ms")
    return 0 if summary["pass_rate"] >= args.min_pass_rate else 1


if __name__ == "__main__":
    sys.exit(main())
