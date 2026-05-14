# glue-review eval — final report

**Reviewer**: OpenRouter `inclusionai/ring-2.6-1t:free` (free tier, the indie-hacker shipping target).
**Eval**: {N_CASES} planted-bug PR scenarios across Go, Python, and TypeScript.
**Date**: {DATE}.

## Headline

| | Layer 1: files & concepts | Layer 1: format compliance | Layer 3: downstream-fix success |
|--|--|--|--|
| **v2 (baseline)** | flagged_file: {V2_FILE} · concept: {V2_CONCEPT} | has_fix_block: **{V2_FIX}** | (untested — fix-block rare) |
| **{WINNING_VERSION}** | flagged_file: {VN_FILE} · concept: {VN_CONCEPT} | has_fix_block: **{VN_FIX}** | **{VN_L3}** pass-rate via codex |

## What changed

The pre-eval `v2` prompt asked for a four-section comment (`## Summary`, `## Issues`, `## Suggestions`, `## Looks good`, `## Open questions`) with per-bullet inline `Fix: …` instructions. Downstream coding agents had to parse English prose to extract intent.

The shipped prompt produces **one** GitHub comment per PR:
- A `## glue-review` headline (one line).
- ≤ 5 severity bullets (`critical` / `high` / `medium` / `low` / `nit`).
- A fenced ` ```markdown ` fix-instruction block with numbered items, each carrying a verb-first directive list and an `Acceptance:` line that any LLM coding agent can paste and act on.

Three variants are explicit in the prompt:
- **A — issues found**: standard finding flow.
- **B — clean**: `No concerns — LGTM.` and no fix block.
- **C — rejected**: `**Pushback on approach**` for diffs whose direction is wrong rather than whose lines need a tweak.

## Per-category Layer 1 deltas (v2 → winner)

(filled in by `python -m harness.compare --base iter-00-baseline --head {ITER}`)

| Category | v2 file/concept/fix | winner file/concept/fix |
|----------|---------------------|-------------------------|
| security | | |
| logic-bug | | |
| missing-test | | |
| multi-bug | | |
| rejected-direction | | |
| style | | |
| doc | | |
| clean | | |
| test-only | | |

## Layer 3 — downstream fix-success

For every case with a real acceptance test ({N_FIX_CASES} cases), we:
1. Apply the planted PR to a fresh tmpdir.
2. Confirm the acceptance test fails (sanity).
3. Pass the reviewer's ` ```markdown ` fix block to a coding agent (codex, headless).
4. Re-run the acceptance test.

Pass-rate = fraction where the test transitions red → green.

| executor | pass-rate | notes |
|----------|-----------|-------|
| codex    | {L3_CODEX} | {L3_NOTES_CODEX} |

## Ship recommendation

(TODO based on numbers)

## Repro

```
git clone https://github.com/erain/glue-review-eval
cd glue-review-eval
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
# set OPENROUTER_API_KEY in .env.local (loaded by tools/iterate.sh)
./tools/iterate.sh v3 my-rerun 8
python -m harness.compare --base iter-00-baseline --head my-rerun
```
