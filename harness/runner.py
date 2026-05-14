"""Invoke glue-review against each case and save its comment.

For each case:
  1. Copy hosts/<host>/ into a tmpdir.
  2. git init + initial commit (the "base").
  3. Checkout -b feature.
  4. Apply patch.diff and commit.
  5. Run glue-review against the feature branch with `--provider` / `--model`
     pinned from config; capture stdout into results/<iter>/<lang>__<id>/comment.md.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from .cases import Case, discover_cases
from .config import GLUE_REVIEW_BIN, PATHS, REVIEW_MODEL, REVIEW_PROVIDER


def _git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.update(
        GIT_AUTHOR_NAME="eval",
        GIT_AUTHOR_EMAIL="eval@local",
        GIT_COMMITTER_NAME="eval",
        GIT_COMMITTER_EMAIL="eval@local",
        GIT_CONFIG_GLOBAL="/dev/null",
        GIT_CONFIG_SYSTEM="/dev/null",
    )
    return subprocess.run(
        ["git", *args], cwd=cwd, env=env,
        check=check, capture_output=True, text=True,
    )


# Mirror the excludes in tools/stage_case.sh so patches captured against a
# stage match the runner's case repo. Anything build/runtime / virtualenv /
# vendored stays out of the baseline.
_HOST_COPY_EXCLUDES = {
    ".venv", "__pycache__", "node_modules", "dist", ".next",
    ".pytest_cache", "coverage",
}
_HOST_COPY_SUFFIX_EXCLUDES = (".pyc", ".pyo", ".db", ".db-journal")


def _copy_ignore(_src, names):
    out = set()
    for n in names:
        if n in _HOST_COPY_EXCLUDES or n.endswith(_HOST_COPY_SUFFIX_EXCLUDES):
            out.add(n)
    return out


_GITIGNORE_BODY = """__pycache__/
*.pyc
*.pyo
.pytest_cache/
*.db
*.db-journal
.venv/
node_modules/
dist/
.next/
coverage/
"""


def _prepare_case_repo(case: Case, tmpdir: Path) -> Path:
    host_src = PATHS.hosts / case.host
    if not host_src.exists():
        raise FileNotFoundError(f"host {case.host!r} missing at {host_src}")
    repo = tmpdir / case.host
    shutil.copytree(host_src, repo, ignore=_copy_ignore)
    # Strip any stray .git from the host source (hosts are normal dirs, not repos).
    if (repo / ".git").exists():
        shutil.rmtree(repo / ".git")

    _git(repo, "init", "-q", "-b", "main")
    # Commit a stage-time .gitignore so future runtime artefacts (test runs,
    # SQLite DBs) don't show up in `git diff` and confuse glue-review's
    # baseline comparison.
    (repo / ".gitignore").write_text(_GITIGNORE_BODY)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "host baseline")
    _git(repo, "checkout", "-q", "-b", "feature")

    patch = case.patch_path
    if not patch.exists():
        raise FileNotFoundError(f"no patch.diff for case {case.id}")
    _git(repo, "apply", str(patch))
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", case.title)
    return repo


def run_one(case: Case, iter_dir: Path, work_root: Path) -> Path:
    out_dir = iter_dir / f"{case.language}__{case.id}"
    out_dir.mkdir(parents=True, exist_ok=True)
    repo = _prepare_case_repo(case, work_root)

    if not GLUE_REVIEW_BIN.exists():
        raise FileNotFoundError(
            f"glue-review binary not found at {GLUE_REVIEW_BIN}; "
            "run `go build -o glue-review ./agents/glue-review` in the glue repo"
        )

    cmd = [
        str(GLUE_REVIEW_BIN),
        "--work", str(repo),
        "--base", "main",
        "--provider", REVIEW_PROVIDER,
        "--model", REVIEW_MODEL,
        "--store", str(work_root / "store"),
        "--id", f"eval-{case.language}-{case.id}",
        "--max-turns", "8",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=420)
    (out_dir / "comment.md").write_text(proc.stdout)
    (out_dir / "stderr.log").write_text(proc.stderr)
    (out_dir / "exit_code").write_text(str(proc.returncode))
    return out_dir / "comment.md"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iter", required=True, help="iteration name, e.g. iter-00-baseline")
    ap.add_argument(
        "--filter", default="",
        help="substring filter on case_id (skip cases that don't contain it)",
    )
    ap.add_argument(
        "--workdir", default="",
        help="optional persistent workdir (default: ephemeral tmpdir)",
    )
    ap.add_argument(
        "--sleep", type=float, default=4.0,
        help="seconds to sleep between cases (rate-limit pacing; default 4s)",
    )
    args = ap.parse_args()

    iter_dir = PATHS.results / args.iter
    iter_dir.mkdir(parents=True, exist_ok=True)

    cases = discover_cases()
    if args.filter:
        cases = [c for c in cases if args.filter in c.id]
    if not cases:
        print("no cases discovered", file=sys.stderr)
        sys.exit(1)

    if args.workdir:
        work_root = Path(args.workdir).resolve()
        work_root.mkdir(parents=True, exist_ok=True)
    else:
        import tempfile
        work_root = Path(tempfile.mkdtemp(prefix="glue-eval-"))

    print(f"running {len(cases)} cases into {iter_dir}")
    for i, c in enumerate(cases, 1):
        print(f"[{i:>2}/{len(cases)}] {c.language}/{c.id}", flush=True)
        try:
            run_one(c, iter_dir, work_root / c.id)
        except subprocess.TimeoutExpired:
            (iter_dir / f"{c.language}__{c.id}" / "TIMEOUT").write_text("timeout")
        except Exception as e:
            (iter_dir / f"{c.language}__{c.id}").mkdir(parents=True, exist_ok=True)
            (iter_dir / f"{c.language}__{c.id}" / "ERROR.log").write_text(repr(e))
        # Pace requests so we stay under provider rate limits (OpenRouter
        # free routes share a 20 req/min ceiling; NVIDIA's free tier
        # rate-limits more aggressively at peak hours).
        if i < len(cases):
            time.sleep(args.sleep)


if __name__ == "__main__":
    main()
