"""Print a side-by-side Layer 1 score delta between two iterations.

Usage: python -m harness.compare --base iter-00-baseline --head iter-01-v3
"""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

from .config import PATHS

L1_KEYS = (
    "flagged_file",
    "flagged_concept",
    "no_false_positives",
    "has_fix_block",
    "no_severity_bullets",
)


def _load(iter_name: str) -> tuple[list[dict], dict[str, dict]]:
    iter_dir = PATHS.results / iter_name
    if not (iter_dir / "l1_scores.json").exists():
        raise FileNotFoundError(f"no l1_scores.json in {iter_dir}")
    scores = json.loads((iter_dir / "l1_scores.json").read_text())
    # Index by composite key for the side-by-side join.
    by_key = {f"{s['language']}__{s['case_id']}": s for s in scores}
    return scores, by_key


def _haveoutput(iter_dir: Path) -> set[str]:
    return {
        p.name for p in iter_dir.iterdir()
        if p.is_dir() and (p / "comment.md").exists() and (p / "comment.md").stat().st_size > 0
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--head", required=True)
    args = ap.parse_args()

    base_scores, base_by = _load(args.base)
    head_scores, head_by = _load(args.head)
    base_have = _haveoutput(PATHS.results / args.base)
    head_have = _haveoutput(PATHS.results / args.head)
    both_have = base_have & head_have

    print(f"Comparing {args.head} vs {args.base}")
    print(f"  base cases with output: {len(base_have)} / {len(base_scores)}")
    print(f"  head cases with output: {len(head_have)} / {len(head_scores)}")
    print(f"  joint (both have output): {len(both_have)}\n")

    base_means = {}
    head_means = {}
    for k in L1_KEYS:
        b = [s[k] for s in base_scores if f"{s['language']}__{s['case_id']}" in both_have]
        h = [s[k] for s in head_scores if f"{s['language']}__{s['case_id']}" in both_have]
        if b and h:
            base_means[k] = statistics.fmean(b)
            head_means[k] = statistics.fmean(h)

    print(f"  {'signal':<24} {'base':>7} {'head':>7} {'delta':>8}")
    for k in L1_KEYS:
        if k not in base_means:
            continue
        b, h = base_means[k], head_means[k]
        delta = h - b
        arrow = "↑" if delta > 0.005 else ("↓" if delta < -0.005 else "·")
        print(f"  {k:<24} {b:>7.3f} {h:>7.3f}  {arrow}{delta:+.3f}")

    print("\n  per-case deltas (joint set):")
    for key in sorted(both_have):
        b = base_by[key]
        h = head_by[key]
        b_sum = sum(b[k] for k in L1_KEYS)
        h_sum = sum(h[k] for k in L1_KEYS)
        d = h_sum - b_sum
        if abs(d) < 0.01:
            continue
        sign = "+" if d > 0 else ""
        print(f"    [{b['category']:<19}] {key:<42} {sign}{d:.2f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
