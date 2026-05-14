"""Aggregate Layer 1 + Layer 2 (+ Layer 3 if present) into a scorecard."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from pathlib import Path

from .config import PATHS

L1_KEYS = (
    "flagged_file", "flagged_concept", "no_false_positives",
    "has_fix_block", "no_severity_bullets",
)
L2_KEYS = (
    "identified", "specificity", "severity_calibration",
    "conciseness", "false_positives",
)


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return round(statistics.fmean(xs), 3) if xs else None


def _load_l1(iter_dir: Path) -> list[dict]:
    p = iter_dir / "l1_scores.json"
    return json.loads(p.read_text()) if p.exists() else []


def _load_l2(iter_dir: Path) -> dict[str, dict]:
    out = {}
    for case_dir in sorted(iter_dir.iterdir()):
        if not case_dir.is_dir():
            continue
        j = case_dir / "judge.json"
        if not j.exists():
            continue
        try:
            out[case_dir.name] = json.loads(j.read_text())
        except Exception:
            pass
    return out


def run(iter_name: str) -> Path:
    iter_dir = PATHS.results / iter_name
    if not iter_dir.exists():
        raise FileNotFoundError(iter_dir)

    l1 = _load_l1(iter_dir)
    l2 = _load_l2(iter_dir)

    # Per-case combined rows.
    rows = []
    for entry in l1:
        key = f"{entry['language']}__{entry['case_id']}"
        l2_row = l2.get(key, {})
        rows.append({
            "case": key,
            "category": entry["category"],
            **{f"l1_{k}": entry.get(k) for k in L1_KEYS},
            **{f"l2_{k}": l2_row.get(k) for k in L2_KEYS},
        })

    csv_path = iter_dir / "scorecard.csv"
    if rows:
        with csv_path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            for r in rows:
                w.writerow(r)

    # Markdown summary.
    md_lines = [f"# Iteration `{iter_name}` scorecard\n"]
    md_lines.append(f"- cases scored: {len(rows)}\n")
    if rows:
        md_lines.append("\n## Layer 1 (structural)\n")
        for k in L1_KEYS:
            md_lines.append(f"- **{k}**: {_mean(r[f'l1_{k}'] for r in rows)}")
        md_lines.append("\n## Layer 2 (LLM-as-judge)\n")
        for k in L2_KEYS:
            md_lines.append(f"- **{k}**: {_mean(r[f'l2_{k}'] for r in rows)}")
        # Per-category Layer 2 overall.
        md_lines.append("\n## Layer 2 by category (overall mean)\n")
        by_cat: dict[str, list[float]] = {}
        for r in rows:
            vals = [r[f"l2_{k}"] for k in L2_KEYS if r[f"l2_{k}"] is not None]
            if not vals:
                continue
            by_cat.setdefault(r["category"], []).append(statistics.fmean(vals))
        for cat, vals in sorted(by_cat.items()):
            md_lines.append(f"- **{cat}** (n={len(vals)}): {round(statistics.fmean(vals), 2)}")

    md_path = iter_dir / "scorecard.md"
    md_path.write_text("\n".join(md_lines) + "\n")
    return md_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iter", required=True)
    args = ap.parse_args()
    p = run(args.iter)
    print(f"wrote {p}")


if __name__ == "__main__":
    main()
