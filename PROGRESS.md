# Progress log

Append-only log of phase milestones. Lets a fresh session resume cleanly.

## Phase 0 — Scaffold (done)

- 2026-05-13: repo created at `erain/glue-review-eval`, scaffolded directory layout, sidecar schema doc, output-format doc, harness skeleton.

## Phase 1 — Host projects (done)

- 2026-05-13: three host projects landed via parallel subagents, all baseline-green:
  - `hosts/go-glog`: 1154 LOC, `go build/vet/test` clean.
  - `hosts/python-linkr`: 554 LOC, 26 tests passing.
  - `hosts/ts-notepad`: 926 LOC, 33 tests passing, `npm run build` green.
- Harness venv set up; `anthropic` SDK 0.102.0 and PyYAML installed.
- Layer 2 judge now supports two paths: Anthropic SDK if `ANTHROPIC_API_KEY` is set, else shells out to `claude --bare --print --model sonnet` (Claude Code Max).
- Reviewer: NVIDIA key available locally; OpenRouter key not yet — will iterate against NVIDIA + `meta/llama-3.3-70b-instruct` (the CI-pinned model) and re-validate against OpenRouter `ring-2.6-1t:free` in Phase 5.

## Phase 2 — Cases (in progress)

- 2026-05-13: `tools/stage_case.sh` + `tools/capture_case.sh` helpers. First case shipped: `python/p-sql-injection-stats` (security · critical), 145-line diff, acceptance test demonstrates the vulnerability (seeded row leaks under raw-SQL interpolation).
- Case plan committed at `docs/CASE_PLAN.md` (~27 cases across 3 hosts).

