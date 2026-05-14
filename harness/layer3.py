"""Layer 3: downstream coding-agent fix-success.

Stub for Phase 4. We wire this up after baseline numbers exist, since
Layer 3 is expensive and only valuable once Layer 1/2 show movement.

Procedure per case:
  1. Clone the host into a temp dir, init git, apply patch.diff, commit.
  2. Confirm acceptance.test_cmd currently fails (sanity).
  3. Extract the ```markdown ...``` fix block from the reviewer's comment.
  4. Feed it to a coding-agent executor (codex / opencode / claude / gemini)
     in a fresh shell, pinning a cheap model where supported.
  5. Re-run acceptance.test_cmd. Pass = exit 0.
"""

from __future__ import annotations

# Implementation deferred to Phase 4 — see PROGRESS.md.

if __name__ == "__main__":
    raise SystemExit("layer3 runner not yet wired — see PROGRESS.md")
