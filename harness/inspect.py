"""Print side-by-side ground-truth vs reviewer comment for fast manual scoring.

Use when no LLM judge is available. Run after harness.runner has populated
results/<iter>/<lang>__<id>/comment.md.

Usage:
    python -m harness.inspect --iter <name>            # all cases
    python -m harness.inspect --iter <name> --filter X # substring filter on case id
    python -m harness.inspect --iter <name> --category logic-bug
"""

from __future__ import annotations

import argparse
import textwrap
from pathlib import Path

from .cases import Case, discover_cases
from .config import PATHS


def _trunc(s: str, n: int) -> str:
    s = s.strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def print_case(case: Case, comment: str) -> None:
    bar = "─" * 80
    print(f"\n{bar}\n{case.language} / {case.id}  [{case.category} · {case.severity}]")
    print(bar)
    print(f"  title:  {case.title}")
    planted = case.planted.description if case.planted else "(none — clean / rejected)"
    print(f"  planted: {_trunc(planted, 240)}")
    if case.planted:
        for pf in case.planted.files:
            print(f"  file:   {pf.path}:{pf.lines[0]}-{pf.lines[1]}  ({pf.kind})")
    print(f"  must_flag:     {list(case.expected.must_flag)}")
    print(f"  must_not_flag: {list(case.expected.must_not_flag)}")
    print(f"  fix_directives: {list(case.expected.fix_directives)}")
    print("─ reviewer comment " + "─" * 60)
    if not comment.strip():
        print("  (empty)")
    else:
        for line in comment.splitlines():
            print(f"  {line}")
    print()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--iter", required=True)
    ap.add_argument("--filter", default="")
    ap.add_argument("--category", default="")
    args = ap.parse_args()

    iter_dir = PATHS.results / args.iter
    if not iter_dir.exists():
        print(f"no results for {args.iter}")
        return 1

    for c in discover_cases():
        if args.filter and args.filter not in c.id:
            continue
        if args.category and args.category != c.category:
            continue
        path = iter_dir / f"{c.language}__{c.id}" / "comment.md"
        comment = path.read_text() if path.exists() else ""
        print_case(c, comment)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
