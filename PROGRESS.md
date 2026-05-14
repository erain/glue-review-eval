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

## Phase 2 — Cases (done)

- 28 cases shipped across the three hosts (10 python + 9 go + 9 typescript), covering security / logic-bug / style / missing-test / multi-bug / rejected-direction / clean / doc / test-only.
- Case-authoring helpers: `tools/stage_case.sh` and `tools/capture_case.sh` (accept `STAGE_DIR` for parallel runs); `tools/clean_patch.py` strips runtime artefacts (pyc, .venv, node_modules) from captured diffs.

## Phase 3 — Baseline (done)

- 28/28 cases scored against `openrouter/inclusionai/ring-2.6-1t:free` under the legacy v2 prompt.
  - flagged_file 0.93, flagged_concept 0.90, no_false_positives 0.96, has_fix_block 0.11.
  - `results/iter-00-baseline/diagnosis.md` captures the five gaps v3 attacks.

## Phase 4 — Iteration (done)

- **iter-01-v3** (28/28): drastic rewrite to single-comment format with three variants + worked examples. Layer 1 delta vs baseline:
  - `has_fix_block` 0.11 → 0.78 (+66.7pp) — the headline target.
  - `no_false_positives` 0.96 → 1.00.
  - `flagged_file` −7.4pp, `flagged_concept` −5.2pp (cost of the format shift).
  - 20 of 22 cases improved; 3 regressions (g-doc-stale-flag, g-missing-flag-test, t-rejected-context-everything) traced to v3's "when in doubt → Variant B" lean.
- **iter-02-v4** (28/28): elevates "first character is `#`" to the top of the prompt, inverts the lean to "when in doubt → Variant A", adds explicit guidance that "behaviour without tests is a missing-test finding, not LGTM", and includes a worked multi-bug example. Beat iter-01-v3 head-to-head on every Layer 1 signal except `no_severity_bullets` (one borderline clean case).
  - `has_fix_block` 0.82 vs baseline (+70.4pp); +7.7pp vs v3.
  - `flagged_file` recovered +3.8pp over v3.
  - All three iter-01 regressions recovered.
- **Layer 3 batch** via `codex exec` on iter-02-v4:
  - Raw pass-rate: 6 / 20 = 30%.
  - Qualified pass-rate: **6 / 8 = 75%** (peeling off 5 Variant-B-by-design cases where v4 correctly emitted no fix block, plus 5 codex-executor errors on typescript cases).

## Phase 5 — Ship (done)

- `release/v3-default` PR in `erain/glue` bumps `defaultPromptVersion` to `v3`, rewrites the agent README around the v3 story, and tags `v2.0.0`.
- Action.yml soft-fail behaviour fixed (`action/safer-soft-fail`): a transient upstream rate-limit no longer overwrites a previous good review.
- `.github/workflows/glue-review-smoke.yml` re-pinned from `erain/glue@eval/v4` to `erain/glue/agents/glue-review@v2`; the throwaway `eval/v3` / `eval/v4` branches were deleted from `erain/glue`.
- Secrets on `erain/glue-review-eval`: `OPENROUTER_API_KEY`, `NVIDIA_API_KEY`.
- Smoke PR `glue-review-eval#1` re-triggered on `@v2` — comment landed correctly with the new format.

