#!/usr/bin/env python3
"""Summarize run records (results/run-*/record.json) into Markdown tables.

One table per experiment version, one row per model. Deliberately no overall
ranking: each row describes only that task, version, and setup.
"""

import collections
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def pct(count, total):
    return f"{count}/{total} ({100 * count // total}%)" if total else "n/a"


def main():
    groups = collections.defaultdict(list)
    for path in sorted(ROOT.glob("*/results/run-*/record.json")):
        record = json.loads(path.read_text())
        groups[(record["experiment"], record["version"])].append(record)
    if not groups:
        print("No run records found.")
        return
    for (experiment, version), records in sorted(groups.items()):
        print(f"\n### {experiment} v{version}\n")
        print("| Model | Runs | Incomplete | First-try full pass | Mean initial score | Final full pass "
              "| Mean correction rounds | Median seconds | Mean tokens (in/out+reasoning) | Cost |")
        print("|---|---|---|---|---|---|---|---|---|---|")
        by_model = collections.defaultdict(list)
        for record in records:
            by_model[record["model"]].append(record)
        for model, runs in sorted(by_model.items()):
            done = [r for r in runs if r["status"] != "incomplete"]
            scored = [r for r in done if r["total"]]
            first = sum(1 for r in scored if r["initial_score"] == r["total"])
            final = sum(1 for r in scored if r["fully_passed"])
            initial = f"{statistics.mean(r['initial_score'] for r in scored):.1f}/{scored[0]['total']}" if scored else "manual"
            rounds = f"{statistics.mean(r['correction_rounds'] for r in scored):.1f}" if scored else "manual"
            seconds = f"{statistics.median(r['seconds'] for r in done):.0f}" if done else "n/a"
            tokens = ("/".join(f"{statistics.mean(v):.0f}" for v in (
                [r["tokens"]["input"] for r in done],
                [r["tokens"]["output"] + r["tokens"]["reasoning"] for r in done]))) if done else "n/a"
            cost = f"${sum(r['cost'] for r in runs):.4f}" if any(r["cost"] for r in runs) else "N/A"
            print(f"| {model} | {len(runs)} | {len(runs) - len(done)} | {pct(first, len(scored)) if scored else 'manual'} | "
                  f"{initial} | {pct(final, len(scored)) if scored else 'manual'} | {rounds} | {seconds} | {tokens} | {cost} |")
    print("\nSingle-task, single-version observations, not a general ranking. Runs through the opencode "
          "'eval' agent form their own setup group.")


if __name__ == "__main__":
    main()
