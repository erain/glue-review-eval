#!/usr/bin/env bash
# Run one full iteration of the prompt-eval loop:
#   1. Sync prompts-snapshots/<version>.md -> glue/agents/glue-review/prompts/<version>.md
#   2. Rebuild the glue-review binary so the embedded FS sees the new prompt
#   3. Source .env.local for OPENROUTER_API_KEY etc.
#   4. harness.runner --iter <name> --sleep N
#   5. harness.scorer --iter <name>
#   6. harness.report --iter <name>
#
# Usage: ./tools/iterate.sh <version> <iter-name> [sleep-seconds]
# Example: ./tools/iterate.sh v3 iter-01-v3 5
set -euo pipefail

version="${1:?usage: iterate.sh <version> <iter-name> [sleep-seconds]}"
iter_name="${2:?missing iter name}"
sleep_s="${3:-5}"

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
glue_root="${GLUE_REPO:-$repo_root/../glue}"
snapshot="$repo_root/prompts-snapshots/${version}.md"
embedded="$glue_root/agents/glue-review/prompts/${version}.md"

if [[ ! -f "$snapshot" ]]; then
  echo "no snapshot at $snapshot — write the prompt first" >&2
  exit 1
fi

echo "==> syncing $snapshot -> $embedded"
mkdir -p "$(dirname "$embedded")"
cp "$snapshot" "$embedded"

echo "==> rebuilding glue-review in $glue_root"
(cd "$glue_root" && go build -o glue-review ./agents/glue-review)

# Inherit OPENROUTER / NVIDIA / ANTHROPIC keys.
if [[ -f "$repo_root/.env.local" ]]; then
  set -a
  # shellcheck disable=SC1091
  . "$repo_root/.env.local"
  set +a
fi

export REVIEW_PROMPT_VERSION="$version"

echo "==> running $iter_name (prompt $version, sleep ${sleep_s}s/case)"
"$repo_root/.venv/bin/python" -m harness.runner --iter "$iter_name" --sleep "$sleep_s"

echo "==> scoring Layer 1"
"$repo_root/.venv/bin/python" -m harness.scorer --iter "$iter_name"

if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
  echo "==> scoring Layer 2 (judge via SDK)"
  "$repo_root/.venv/bin/python" -m harness.judge --iter "$iter_name" || echo "judge failed; continuing"
else
  echo "==> ANTHROPIC_API_KEY not set; skipping Layer 2 judge"
fi

echo "==> rendering scorecard"
"$repo_root/.venv/bin/python" -m harness.report --iter "$iter_name"

echo "==> $iter_name done"
echo "    results/$iter_name/scorecard.md"
