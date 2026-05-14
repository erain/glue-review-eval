"""Layer 1: structural recall over the reviewer's comment.

Pure regex — no model calls. Fast feedback signal during iteration.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from .cases import Case, discover_cases
from .config import PATHS

# A comment is considered to contain a fix block if it has a fenced
# ```markdown ... ``` block after a "Fix instructions" header (or close to it).
FIX_BLOCK_RE = re.compile(
    r"(?is)#{2,3}\s*Fix instructions.*?```markdown\n(.+?)```",
)

SEVERITY_BULLET_RE = re.compile(
    r"(?i)\*\*\s*(critical|high|medium|low|nit)\s*\*\*"
)


@dataclass
class L1Score:
    case_id: str
    language: str
    category: str
    flagged_file: float    # 0/1
    flagged_concept: float # fraction of must_flag patterns matched
    no_false_positives: float  # 1.0 if no must_not_flag matched, else 0
    has_fix_block: float   # 0/1; for clean/rejected cases we invert
    no_severity_bullets: float  # only meaningful for clean; 1 if absent


def score_comment(case: Case, comment_md: str) -> L1Score:
    text = comment_md or ""

    # flagged_file: planted file basename mentioned at all
    planted_paths = [pf.path for pf in (case.planted.files if case.planted else ())]
    flagged_file = 0.0
    if planted_paths:
        for p in planted_paths:
            if Path(p).name in text or p in text:
                flagged_file = 1.0
                break
    else:
        # No planted files (clean/rejected). 1.0 means "appropriately quiet".
        flagged_file = 1.0

    # flagged_concept: fraction of must_flag regexes that match
    must_flag = case.expected.must_flag
    if must_flag:
        hits = sum(
            1 for pat in must_flag
            if re.search(pat, text, flags=re.IGNORECASE)
        )
        flagged_concept = hits / len(must_flag)
    else:
        flagged_concept = 1.0  # nothing to flag

    # no_false_positives: any must_not_flag pattern matching is a fail
    must_not = case.expected.must_not_flag
    fp_hit = any(re.search(pat, text, flags=re.IGNORECASE) for pat in must_not)
    no_false_positives = 0.0 if fp_hit else 1.0

    # has_fix_block: fenced ```markdown after Fix instructions
    has_block = bool(FIX_BLOCK_RE.search(text))
    if case.category in ("clean",):
        # For clean PRs, the rule is INVERTED: no fix block should appear.
        has_fix_block = 0.0 if has_block else 1.0
    else:
        has_fix_block = 1.0 if has_block else 0.0

    # no_severity_bullets: only meaningful for clean PRs
    if case.category == "clean":
        no_severity_bullets = 0.0 if SEVERITY_BULLET_RE.search(text) else 1.0
    else:
        no_severity_bullets = 1.0

    return L1Score(
        case_id=case.id,
        language=case.language,
        category=case.category,
        flagged_file=flagged_file,
        flagged_concept=flagged_concept,
        no_false_positives=no_false_positives,
        has_fix_block=has_fix_block,
        no_severity_bullets=no_severity_bullets,
    )


def run(iter_name: str) -> list[L1Score]:
    iter_dir = PATHS.results / iter_name
    if not iter_dir.exists():
        raise FileNotFoundError(f"no results for iter {iter_name!r}")

    cases = {c.id: c for c in discover_cases()}
    scores: list[L1Score] = []
    for case_id, case in cases.items():
        comment_path = iter_dir / f"{case.language}__{case_id}" / "comment.md"
        if not comment_path.exists():
            # Treat missing output as zero across the board.
            scores.append(
                L1Score(
                    case_id=case_id, language=case.language, category=case.category,
                    flagged_file=0.0, flagged_concept=0.0,
                    no_false_positives=0.0, has_fix_block=0.0,
                    no_severity_bullets=0.0,
                )
            )
            continue
        scores.append(score_comment(case, comment_path.read_text()))

    out = iter_dir / "l1_scores.json"
    out.write_text(json.dumps([asdict(s) for s in scores], indent=2))
    return scores


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--iter", required=True)
    args = ap.parse_args()
    scores = run(args.iter)
    print(f"Wrote {len(scores)} scores to results/{args.iter}/l1_scores.json")
