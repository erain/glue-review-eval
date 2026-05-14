"""Layer 3: downstream coding-agent fix-success.

Given a case + a reviewer's comment, extract the fenced ```markdown
fix-instruction block, hand it to a real coding agent in a fresh
sandbox, and check whether the case's acceptance test goes from red to
green. This is the closest-to-ground-truth product KPI: did the
reviewer's instructions actually fix the bug?

Executor selection: prefer codex (fast, headless), fall back to
opencode, then claude (if /login is done). Each gets the SAME fix
instructions; we score pass-rate cross-executor as the headline.

This module is intentionally conservative: it never modifies the host
or eval repo; the case is staged into a tmpdir, fixes are applied
there, and the tmpdir is left in place after the run for inspection.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from .cases import Case, discover_cases
from .config import PATHS
from .runner import _GITIGNORE_BODY, _copy_ignore, _git

FIX_BLOCK_RE = re.compile(
    r"(?is)#{2,3}\s*Fix instructions.*?```markdown\n(.+?)```",
)


@dataclass
class L3Result:
    case_id: str
    language: str
    category: str
    executor: str
    had_fix_block: bool
    fix_applied: bool
    acceptance_passed: bool
    test_cmd: str
    notes: str = ""


def _extract_fix_block(comment: str) -> str | None:
    m = FIX_BLOCK_RE.search(comment or "")
    return m.group(1).strip() if m else None


def _prepare_buggy_repo(case: Case, work_root: Path) -> Path:
    host_src = PATHS.hosts / case.host
    repo = work_root / case.host
    shutil.copytree(host_src, repo, ignore=_copy_ignore)
    if (repo / ".git").exists():
        shutil.rmtree(repo / ".git")
    _git(repo, "init", "-q", "-b", "main")
    (repo / ".gitignore").write_text(_GITIGNORE_BODY)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "baseline")
    _git(repo, "checkout", "-q", "-b", "feature")
    _git(repo, "apply", str(case.patch_path))
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", case.title)
    return repo


def _run_test(repo: Path, test_cmd: str, timeout_s: int) -> bool:
    proc = subprocess.run(
        ["bash", "-lc", test_cmd],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=timeout_s,
    )
    return proc.returncode == 0


def _invoke_executor(executor: str, repo: Path, instructions: str, timeout_s: int) -> tuple[bool, str]:
    """Hand `instructions` to a coding agent run in `repo`. Returns (success, notes)."""
    if executor == "codex":
        # codex exec runs a single-shot non-interactive task. `-C` pins the
        # working directory; the bypass flag is required for headless edits
        # (otherwise codex stops to ask for approval). The case repo is a
        # fresh tmpdir, so the danger label is appropriate to the contained
        # blast radius.
        cmd = [
            "codex", "exec",
            "-C", str(repo),
            "--dangerously-bypass-approvals-and-sandbox",
            "--skip-git-repo-check",
            instructions,
        ]
    elif executor == "opencode":
        cmd = ["opencode", "run", "--cd", str(repo), instructions]
    elif executor == "claude":
        # `claude -p` runs a one-shot if /login has been done. We pass
        # --add-dir to let it touch the case repo.
        cmd = [
            "claude", "--print", "--add-dir", str(repo),
            "--dangerously-skip-permissions",
            f"You are in the directory {repo}. " + instructions,
        ]
    else:
        return False, f"unknown executor {executor}"

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s)
    except subprocess.TimeoutExpired:
        return False, f"executor timeout after {timeout_s}s"
    except FileNotFoundError:
        return False, f"executor {executor} not installed"

    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout)[-300:]
        return False, f"executor exit {proc.returncode}: {tail!r}"
    return True, "ok"


def run_one(case: Case, comment: str, executor: str, work_root: Path) -> L3Result:
    fix_block = _extract_fix_block(comment)
    if not fix_block:
        return L3Result(
            case_id=case.id, language=case.language, category=case.category,
            executor=executor, had_fix_block=False, fix_applied=False,
            acceptance_passed=False, test_cmd=case.acceptance.test_cmd if case.acceptance else "",
            notes="no fenced ```markdown fix block in reviewer comment",
        )
    if not case.acceptance or not case.acceptance.test_cmd:
        return L3Result(
            case_id=case.id, language=case.language, category=case.category,
            executor=executor, had_fix_block=True, fix_applied=False,
            acceptance_passed=False, test_cmd="",
            notes="case has no acceptance.test_cmd (clean / rejected-direction)",
        )

    work_root.mkdir(parents=True, exist_ok=True)
    repo = _prepare_buggy_repo(case, work_root)

    # Sanity: confirm the acceptance test is currently RED on the patched repo.
    pre = _run_test(repo, case.acceptance.test_cmd, case.acceptance.timeout_s or 120)
    if pre:
        return L3Result(
            case_id=case.id, language=case.language, category=case.category,
            executor=executor, had_fix_block=True, fix_applied=False,
            acceptance_passed=False, test_cmd=case.acceptance.test_cmd,
            notes="acceptance test was already green on the patched repo (case wiring bug)",
        )

    applied, notes = _invoke_executor(
        executor, repo, fix_block, timeout_s=300,
    )
    if not applied:
        return L3Result(
            case_id=case.id, language=case.language, category=case.category,
            executor=executor, had_fix_block=True, fix_applied=False,
            acceptance_passed=False, test_cmd=case.acceptance.test_cmd,
            notes=f"executor failed: {notes}",
        )

    post = _run_test(repo, case.acceptance.test_cmd, case.acceptance.timeout_s or 120)
    return L3Result(
        case_id=case.id, language=case.language, category=case.category,
        executor=executor, had_fix_block=True, fix_applied=True,
        acceptance_passed=post, test_cmd=case.acceptance.test_cmd,
        notes="fix landed but acceptance still red" if not post else "ok",
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--iter", required=True, help="iteration name with comment.md per case")
    ap.add_argument("--executor", default="codex",
                    help="codex | opencode | claude (default: codex)")
    ap.add_argument("--filter", default="", help="substring on case id")
    ap.add_argument("--workdir", default="", help="persistent workdir (default: tempdir)")
    ap.add_argument("--max", type=int, default=0, help="cap cases (0 = no cap)")
    args = ap.parse_args()

    iter_dir = PATHS.results / args.iter
    if not iter_dir.exists():
        print(f"no iter {args.iter}", file=sys.stderr); return 1

    if args.workdir:
        work_root = Path(args.workdir).resolve()
    else:
        import tempfile
        work_root = Path(tempfile.mkdtemp(prefix="glue-l3-"))

    cases = discover_cases()
    if args.filter:
        cases = [c for c in cases if args.filter in c.id]
    # Only run cases that have a non-empty comment and a real acceptance test.
    runnable = []
    for c in cases:
        cp = iter_dir / f"{c.language}__{c.id}" / "comment.md"
        if not cp.exists() or cp.stat().st_size == 0:
            continue
        if not c.acceptance or not c.acceptance.test_cmd:
            continue
        runnable.append(c)
    if args.max:
        runnable = runnable[: args.max]

    print(f"Layer 3 on {args.iter} via {args.executor}: {len(runnable)} cases")
    results: list[L3Result] = []
    for i, c in enumerate(runnable, 1):
        comment = (iter_dir / f"{c.language}__{c.id}" / "comment.md").read_text()
        print(f"  [{i}/{len(runnable)}] {c.language}/{c.id}", flush=True)
        try:
            r = run_one(c, comment, args.executor, work_root / c.id)
        except Exception as e:
            r = L3Result(
                case_id=c.id, language=c.language, category=c.category,
                executor=args.executor, had_fix_block=True, fix_applied=False,
                acceptance_passed=False,
                test_cmd=c.acceptance.test_cmd if c.acceptance else "",
                notes=f"exception: {e!r}",
            )
        results.append(r)
        time.sleep(2)

    out = iter_dir / f"l3_{args.executor}.json"
    # Merge with any prior run (so spot-checks accumulate into a full batch).
    prior: list[dict] = []
    if out.exists():
        try:
            prior = json.loads(out.read_text())
        except Exception:
            prior = []
    fresh = {r.case_id for r in results}
    merged = [p for p in prior if p["case_id"] not in fresh] + [asdict(r) for r in results]
    out.write_text(json.dumps(merged, indent=2))

    passed = sum(1 for r in results if r.acceptance_passed)
    print(f"\nLayer 3 pass-rate ({args.executor}): {passed}/{len(results)} = "
          f"{(passed / len(results) * 100) if results else 0:.0f}%")
    print(f"wrote {out}")
    print(f"work tree: {work_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
