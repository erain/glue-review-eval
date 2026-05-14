# prompts/v3: single-comment output for AI-agent consumption

## Summary

Replace the legacy four-section review format (`## Summary` / `## Issues` / `## Suggestions` / `## Looks good` / `## Open questions` with per-bullet `Fix: …` instructions) with a single GitHub comment optimised for an AI coding agent to paste and act on:

- One `## glue-review` headline.
- ≤ 5 severity bullets (`critical` / `high` / `medium` / `low` / `nit`).
- One fenced ` ```markdown ` fix-instruction block with numbered items, each carrying verb-first directives and an `Acceptance:` line.
- Three explicit variants: **A (issues found)**, **B (clean — `No concerns — LGTM`)**, **C (rejected — `Pushback on approach`)**.

The fix-block fence is exactly ` ```markdown ` so downstream agents (codex, opencode, claude, gemini) can extract it deterministically. Worked examples for each variant anchor the format against models that drift on rules alone.

## Why

The pre-existing v2 prompt assumed a human reviewer skimming sections. With glue-review increasingly used as upstream for an AI coding agent that should *just apply the fix*, the format was the friction point — agents had to parse English to pick the bug out of the prose.

## Evidence (https://github.com/erain/glue-review-eval)

| signal | v2 baseline | v3 (this PR) | delta |
|--|--|--|--|
| `has_fix_block` (fenced ` ```markdown ` after `### Fix instructions`) | {V2_FIX} | {VN_FIX} | {DELTA_FIX} |
| `flagged_file` | {V2_FILE} | {VN_FILE} | {DELTA_FILE} |
| `flagged_concept` | {V2_CONCEPT} | {VN_CONCEPT} | {DELTA_CONCEPT} |
| `no_false_positives` | {V2_NFP} | {VN_NFP} | {DELTA_NFP} |
| Layer 3 downstream-fix success (codex) | (untested — fix-block rare) | **{VN_L3} pass-rate** | |

Numbers are over {N_CASES} planted-bug PR scenarios across Go, Python, and TypeScript host projects in glue-review-eval. The reviewer is `openrouter/inclusionai/ring-2.6-1t:free` — the indie-hacker shipping target.

## Compatibility

- `--prompt-version v2` continues to work; v2 stays embedded for rollback.
- `--prompt-version v3` opts into the new format.
- Default unchanged until the GitHub Action / Action workflow consumers have a chance to ack the new shape. Bump `defaultPromptVersion` to v3 in a follow-up once consumers are ready.

## Test plan

- [x] `go test ./agents/glue-review/...` clean (existing prompt-selector tests).
- [x] `glue-review --prompt-version v3` smoke against a real branch.
- [ ] One CI green build on this PR.
