"""Paths, env, and pinned tool versions.

Centralised so iterations don't drift on accident.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = REPO_ROOT / "cases"
HOSTS_DIR = REPO_ROOT / "hosts"
RESULTS_DIR = REPO_ROOT / "results"
PROMPTS_SNAPSHOT_DIR = REPO_ROOT / "prompts-snapshots"

GLUE_REPO = Path(os.environ.get("GLUE_REPO", REPO_ROOT.parent / "glue"))
GLUE_REVIEW_BIN = GLUE_REPO / "glue-review"

# Pinned by env so an iteration's `--provider` / `--model` is reproducible
# from the scorecard row alone.
# Default reviewer = whatever key is in env. We try OpenRouter first since
# that's the indie-hacker shipping target, then NVIDIA (the dev fallback
# that the glue CI also exercises), then Gemini.
def _default_provider() -> tuple[str, str]:
    if os.environ.get("OPENROUTER_API_KEY"):
        return "openrouter", "inclusionai/ring-2.6-1t:free"
    if os.environ.get("NVIDIA_API_KEY"):
        return "nvidia", "meta/llama-3.3-70b-instruct"
    if os.environ.get("GEMINI_API_KEY"):
        return "gemini", "gemini-2.5-flash"
    return "openrouter", "inclusionai/ring-2.6-1t:free"  # will fail at runtime; explicit


_provider, _model = _default_provider()
REVIEW_PROVIDER = os.environ.get("REVIEW_PROVIDER", _provider)
REVIEW_MODEL = os.environ.get("REVIEW_MODEL", _model)

# Layer 2 judge.
JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "claude-sonnet-4-6")

# Layer 3 executors. Listed in the order we rotate through them.
LAYER3_EXECUTORS = ["codex", "opencode", "claude-headless", "gemini"]


@dataclass(frozen=True)
class Paths:
    cases: Path = CASES_DIR
    hosts: Path = HOSTS_DIR
    results: Path = RESULTS_DIR
    snapshots: Path = PROMPTS_SNAPSHOT_DIR


PATHS = Paths()
