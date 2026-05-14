#!/usr/bin/env bash
# Stage a host project into /tmp/case-stage as a clean git repo, ready
# to receive a case's edits. Usage: ./tools/stage_case.sh <host-dir-name>
#
# Examples:
#   ./tools/stage_case.sh python-linkr
#   ./tools/stage_case.sh go-glog
#   ./tools/stage_case.sh ts-notepad
#
# The .venv / node_modules / dist trees in the host are excluded from the
# baseline so the captured patch.diff contains only the case's edits.
set -euo pipefail

host="${1:?usage: stage_case.sh <host-dir>}"
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
src="$repo_root/hosts/$host"
stage=/tmp/case-stage

if [[ ! -d "$src" ]]; then
  echo "no such host: $src" >&2
  exit 1
fi

rm -rf "$stage"
mkdir -p "$stage"

# rsync with excludes — keeps stage free of vendored build/dep dirs.
rsync -a --delete \
  --exclude '.venv/' \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude '.pytest_cache/' \
  --exclude 'node_modules/' \
  --exclude 'dist/' \
  --exclude '.next/' \
  --exclude '*.db' --exclude '*.db-journal' \
  --exclude '.git/' \
  "$src/" "$stage/"

cd "$stage"
git init -q -b main
git -c user.email=eval@x -c user.name=eval add -A
git -c user.email=eval@x -c user.name=eval commit -q -m "host baseline ($host)"

# Symlink the host's .venv / node_modules into the stage so tests can run.
# Symlinks aren't picked up by `git add` so they don't pollute the diff.
case "$host" in
  python-*)
    if [[ -d "$src/.venv" ]]; then
      ln -sf "$src/.venv" "$stage/.venv"
    fi
    ;;
  ts-*)
    if [[ -d "$src/node_modules" ]]; then
      ln -sf "$src/node_modules" "$stage/node_modules"
    fi
    ;;
esac

echo "staged $host at $stage"
