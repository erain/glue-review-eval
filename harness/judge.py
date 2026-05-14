"""Layer 2: LLM-as-judge using Claude Sonnet via the Anthropic SDK.

For each case, builds a prompt from the sidecar + patch + reviewer comment
and asks the judge for a strict JSON score with rationale. Writes per-case
JSON under results/<iter>/<lang>__<id>/judge.json.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path

from .cases import Case, discover_cases
from .config import JUDGE_MODEL, PATHS

PROMPT_TEMPLATE = """You are evaluating a code-review agent's output against a known ground truth.

GROUND TRUTH (what we planted in this PR):
- Category: {category}
- Severity: {severity}
- Planted bug description: {planted_description}
- Files / lines affected: {planted_files}
- Expected concepts the reviewer should flag: {expected_must_flag}
- Things the reviewer must NOT claim (false-positive guard): {expected_must_not_flag}
- Fix directives the reviewer's fix-block should include: {expected_fix_directives}

PR DIFF (what the reviewer saw):
```
{patch}
```

REVIEWER COMMENT (what we are grading):
'''
{comment}
'''

Score the comment on five 0-10 dimensions. Use the full range; 10 is rare.

- identified: Did the reviewer find the planted bug? 10 = explicit, correct call-out with file/line. 0 = missed entirely or claimed something unrelated.
- specificity: Are fix directives concrete and acceptance-checkable (verb-first, naming the file/symbol, with a check)? 10 = paste-and-go for any LLM coding agent. 0 = vague principles ("be careful with bounds").
- severity_calibration: Does the assigned severity match expected? 10 = exact. Deduct for inflation (calling a nit "high") or deflation.
- conciseness: Human-readable section ≤ 5 bullets, no preamble, no closing summary. 10 = tight. 0 = a wall of prose.
- false_positives: 10 = no invented issues. Penalise heavily for each must_not_flag match or other hallucinated finding.

For category=clean: identified scores on "correctly recognising no real issues"; severity should be "none" / no bullets.
For category=rejected-direction: identified scores on naming the design-level concern.

Return ONLY strict JSON, no prose:
{{
  "identified": <int 0-10>,
  "specificity": <int 0-10>,
  "severity_calibration": <int 0-10>,
  "conciseness": <int 0-10>,
  "false_positives": <int 0-10>,
  "rationale": "<=200 chars, one line"
}}
"""


def _build_prompt(case: Case, comment: str) -> str:
    planted_desc = case.planted.description if case.planted else "(none — clean PR)"
    planted_files = (
        ", ".join(f"{pf.path}:{pf.lines[0]}-{pf.lines[1]}" for pf in case.planted.files)
        if case.planted else "(none)"
    )
    return PROMPT_TEMPLATE.format(
        category=case.category,
        severity=case.severity,
        planted_description=planted_desc,
        planted_files=planted_files,
        expected_must_flag=list(case.expected.must_flag),
        expected_must_not_flag=list(case.expected.must_not_flag),
        expected_fix_directives=list(case.expected.fix_directives),
        patch=case.patch_diff[:8000],
        comment=comment[:6000],
    )


JUDGE_SYSTEM = (
    "You are a strict, calibrated evaluator. Return ONLY the JSON object "
    "requested — no markdown fences, no preamble, no trailing prose."
)


def _judge_call_sdk(prompt: str) -> str:
    from anthropic import Anthropic  # type: ignore

    client = Anthropic()
    msg = client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=400,
        system=JUDGE_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(
        b.text for b in msg.content if getattr(b, "type", None) == "text"
    ).strip()


def _judge_call_cli(prompt: str) -> str:
    """Headless `claude -p` invocation. Uses the Claude Code Max subscription
    rather than an ANTHROPIC_API_KEY, at the cost of CLI startup overhead.
    """
    import subprocess

    # `--bare` strips hooks, plugins, auto-memory — fast and deterministic.
    # We pass system+user as a single prompt because --bare keeps things minimal.
    full_prompt = JUDGE_SYSTEM + "\n\n" + prompt
    proc = subprocess.run(
        [
            "claude",
            "--bare",
            "--print",
            "--model", "sonnet",
            full_prompt,
        ],
        capture_output=True, text=True, timeout=120,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"claude CLI exited {proc.returncode}; stderr={proc.stderr[-300:]}"
        )
    return proc.stdout.strip()


def _judge_call(prompt: str) -> dict:
    if os.environ.get("ANTHROPIC_API_KEY"):
        text = _judge_call_sdk(prompt)
    else:
        # No API key — fall back to the local `claude` CLI (Max subscription).
        text = _judge_call_cli(prompt)
    # Defensive: strip code fences if model added them despite instructions.
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    # Some models prepend "Here's the JSON:" — find the first '{' and parse from there.
    brace = text.find("{")
    if brace > 0:
        text = text[brace:]
    return json.loads(text)


def run(iter_name: str, only_filter: str = "") -> int:
    iter_dir = PATHS.results / iter_name
    if not iter_dir.exists():
        raise FileNotFoundError(f"no results for iter {iter_name!r}")

    cases = discover_cases()
    if only_filter:
        cases = [c for c in cases if only_filter in c.id]

    judged = 0
    for c in cases:
        case_out = iter_dir / f"{c.language}__{c.id}"
        comment_path = case_out / "comment.md"
        if not comment_path.exists():
            continue
        prompt = _build_prompt(c, comment_path.read_text())
        try:
            score = _judge_call(prompt)
        except Exception as e:
            (case_out / "judge.error.log").write_text(repr(e))
            continue
        (case_out / "judge.json").write_text(json.dumps(score, indent=2))
        judged += 1
    return judged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iter", required=True)
    ap.add_argument("--filter", default="")
    args = ap.parse_args()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY not set — judge will fail at first call.",
              file=sys.stderr)
    n = run(args.iter, args.filter)
    print(f"judged {n} cases")


if __name__ == "__main__":
    main()
