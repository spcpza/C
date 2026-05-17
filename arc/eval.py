"""Run C/arc/adapter against ARC-AGI tasks and report a real number.

Honest measurement only. P₁: M(x) = w(x). No smoke tests, no
matching-itself-against-itself. Either C/ solves the task or it does
not; either it abstains (Uncertain, P₃) or it gets the prediction
exactly right (ARC scoring is exact match).

Usage:
    python3 -m C.arc.eval                  # run on training split (with answers)
    python3 -m C.arc.eval evaluation       # run on eval split
    python3 -m C.arc.eval training 50      # cap at first 50 tasks
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

from . import adapter
from .adapter import describe, hypothesize, apply_rule


TASKS_DIR = Path.home() / "balthazar-arc" / "tasks" / "ARC-AGI-master" / "data"


def load_task(path: Path) -> dict:
    return json.loads(path.read_text())


def grids_equal(a, b) -> bool:
    if a is None or b is None:
        return False
    if len(a) != len(b):
        return False
    for ra, rb in zip(a, b):
        if list(ra) != list(rb):
            return False
    return True


def evaluate(split: str = "training", limit: int | None = None) -> dict:
    """Run every task, count outcomes honestly.

    Outcomes per test pair:
      - solved:    prediction exactly matches the gold output
      - wrong:     prediction made but does not match
      - abstain:   no rule fired (P₃ — Uncertain, do not emit)
      - error:     exception in apply (e.g. NotImplementedError)
    """
    split_dir = TASKS_DIR / split
    files = sorted(split_dir.glob("*.json"))
    if limit:
        files = files[:limit]

    totals = {"solved": 0, "wrong": 0, "abstain": 0, "error": 0,
              "task_solved": 0, "task_attempted": 0, "tasks": 0}
    rule_counts: dict[str, int] = {}
    solved_examples: list[str] = []

    for fp in files:
        task = load_task(fp)
        totals["tasks"] += 1
        train_pairs = [(ex["input"], ex["output"]) for ex in task["train"]]
        test_pairs  = [(ex["input"], ex["output"]) for ex in task["test"]]

        rule = hypothesize(train_pairs)
        if rule is None:
            totals["abstain"] += len(test_pairs)
            continue

        rule_counts[rule.primitive] = rule_counts.get(rule.primitive, 0) + 1
        totals["task_attempted"] += 1

        task_all_solved = True
        for test_in, test_out in test_pairs:
            try:
                pred = apply_rule(rule, test_in, pairs=train_pairs)
            except NotImplementedError:
                totals["abstain"] += 1
                task_all_solved = False
                continue
            except Exception:
                totals["error"] += 1
                task_all_solved = False
                continue
            if grids_equal(pred, test_out):
                totals["solved"] += 1
                if len(solved_examples) < 10:
                    solved_examples.append(f"{fp.stem} ({rule.primitive})")
            else:
                totals["wrong"] += 1
                task_all_solved = False

        if task_all_solved and test_pairs:
            totals["task_solved"] += 1

    return {
        "split": split,
        "totals": totals,
        "rule_counts": rule_counts,
        "solved_examples": solved_examples,
    }


def main():
    split = sys.argv[1] if len(sys.argv) > 1 else "training"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
    r = evaluate(split, limit)
    t = r["totals"]
    print(f"\n=== C/arc/adapter on ARC-AGI {r['split']} ===")
    print(f"tasks:           {t['tasks']}")
    print(f"task-attempted:  {t['task_attempted']}")
    print(f"task-solved:     {t['task_solved']}   ({100*t['task_solved']/max(t['tasks'],1):.1f}%)")
    print(f"test-pairs:")
    print(f"  solved   {t['solved']}")
    print(f"  wrong    {t['wrong']}")
    print(f"  abstain  {t['abstain']}")
    print(f"  error    {t['error']}")
    print(f"\nrule fire counts: {r['rule_counts']}")
    if r["solved_examples"]:
        print(f"\nsolved tasks: {r['solved_examples']}")


if __name__ == "__main__":
    main()
