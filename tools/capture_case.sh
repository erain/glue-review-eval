#!/usr/bin/env bash
# Capture the diff in /tmp/case-stage into cases/<lang>/<id>/patch.diff.
# Usage: ./tools/capture_case.sh <lang>/<case-id>
#
# Example:
#   ./tools/capture_case.sh python/p-sql-injection-stats
set -euo pipefail

target="${1:?usage: capture_case.sh <lang>/<case-id> [stage-dir]}"
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
stage="${2:-${STAGE_DIR:-/tmp/case-stage}}"
out_dir="$repo_root/cases/$target"

if [[ ! -d "$stage/.git" ]]; then
  echo "$stage is not a staged repo; run ./tools/stage_case.sh first" >&2
  exit 1
fi
mkdir -p "$out_dir"

cd "$stage"
# Stage everything new + modified; capture against HEAD for a stable diff.
git -c user.email=eval@x -c user.name=eval add -A
# Pipe through clean_patch.py to strip pycache / *.pyc / .db / .venv / node_modules
# sections that older stages may have committed into the baseline.
git -c user.email=eval@x -c user.name=eval diff --cached HEAD \
  | python3 "$repo_root/tools/clean_patch.py" \
  > "$out_dir/patch.diff"
lines=$(wc -l < "$out_dir/patch.diff")
echo "wrote $out_dir/patch.diff ($lines lines)"
