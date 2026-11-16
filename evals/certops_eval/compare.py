"""Compares two evaluation reports (A/B), e.g. instructions v1 against v2, or before and after a model update.

Usage: python -m certops_eval.compare results/v1.json results/v2.json
Exits 1 when a case that passed in the baseline fails in the candidate.
"""
import argparse
import json
import sys
from pathlib import Path


def compare(baseline: dict, candidate: dict) -> dict:
    before = {r["case_id"]: r["passed"] for r in baseline["results"]}
    after = {r["case_id"]: r["passed"] for r in candidate["results"]}
    shared = before.keys() & after.keys()
    return {
        "regressions": sorted(c for c in shared if before[c] and not after[c]),
        "fixes": sorted(c for c in shared if not before[c] and after[c]),
        "pass_rate": (baseline["summary"]["pass_rate"], candidate["summary"]["pass_rate"]),
        "by_category": {
            category: (baseline["summary"]["by_category"].get(category), rate)
            for category, rate in candidate["summary"]["by_category"].items()
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args(argv)

    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
    diff = compare(baseline, candidate)

    old_rate, new_rate = diff["pass_rate"]
    print(f"{baseline['label']} -> {candidate['label']}: pass rate {old_rate:.0%} -> {new_rate:.0%}")
    for category, (old, new) in diff["by_category"].items():
        print(f"  {category}: {'n/a' if old is None else f'{old:.0%}'} -> {new:.0%}")
    print("Regressions: " + (", ".join(diff["regressions"]) or "none"))
    print("Fixes: " + (", ".join(diff["fixes"]) or "none"))
    return 1 if diff["regressions"] else 0


if __name__ == "__main__":
    sys.exit(main())
