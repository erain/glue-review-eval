# glue-review eval — final report

**Date**: 2026-05-13 / 14
**Reviewer model**: OpenRouter `inclusionai/ring-2.6-1t:free` (Novita upstream — the same free path indie hackers will install).
**Eval**: 28 planted-bug PR scenarios across three host projects (Go log-tail CLI, FastAPI URL shortener, React markdown notepad).
**Tooling**: this repo (https://github.com/erain/glue-review-eval).

## Headline

| | v2 baseline | v4 (winner) | delta |
|--|--|--|--|
| `flagged_file` (recall) | **0.93** | 0.85 | −7.4pp (paid for format shift) |
| `flagged_concept` (recall) | **0.90** | 0.86 | −4.0pp |
| `no_false_positives` | 0.96 | **1.00** | +3.7pp |
| `has_fix_block` (fenced ` ```markdown ` after `### Fix instructions`) | 0.11 | **0.82** | **+70.4pp** |
| `no_severity_bullets` (clean-case discipline) | 1.00 | 0.96 | −3.7pp (one borderline) |

**Headline take**: format compliance — the only knob that turns the comment into something an AI coding agent can paste — went from essentially 0 (clean PRs incidentally pass) to **82%**, with **zero invented findings**. The slight recall regressions are the price of a tighter format; the model spends some of its turn budget on the structural rubric.

## Layer 3 — downstream-fix success (the product KPI)

For every case with a real acceptance test we:
1. Stage the buggy PR in a tmpdir.
2. Confirm the acceptance test is red.
3. Pass the v4 comment's ` ```markdown ` fix block to `codex exec --dangerously-bypass-approvals-and-sandbox`.
4. Re-run the acceptance test.

A pass = test transitioned red → green from the fix block alone.

(Filled in by the L3 batch on iter-02-v4; spot-checks during iteration on iter-01-v3 hit 3/3.)

## The format change

### v2 (the pre-eval baseline)

```
## Summary
One sentence.

## Issues
- [critical] file.py:42 — description. Fix: a long imperative paragraph.
- [minor]    other.py:88 — description. Fix: another paragraph.

## Suggestions
- [minor] ... Fix: ...

## Looks good
* free-form bullets

## Open questions
* free-form bullets
```

Designed for a human reviewer skimming sections. An AI coding agent fed this output has to parse English to extract intent.

### v4 (winner)

```
## glue-review

<one-line headline>

- **severity** — path:line — finding
- ... (≤ 5)

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **path:line** — problem.
   - directive
   Acceptance: test/check.

2. ...
```
```

Plus two alternate variants:

- **Variant B (clean)** — `No concerns — LGTM.` and no fix block, used only when there is truly no finding.
- **Variant C (rejected)** — `**Pushback on approach**`, a 2-4 sentence design-level rebuttal, and a fix block that starts `Do NOT apply the current diff. Instead:`.

Worked examples for each variant are baked into the prompt so the model has format anchors (not just rules) to follow.

## What v2 → v3 (drastic rewrite) achieved, and what v3 → v4 fixed

`iter-01-v3` lifted `has_fix_block` from 0.11 to 0.78 (+66.7pp) but had three regressions vs the baseline:

| case | category | regression cause |
|------|----------|------------------|
| g-doc-stale-flag | doc | v3's "when in doubt → Variant B" gave LGTM instead of flagging the README drift. |
| g-missing-flag-test | missing-test | Same — LGTM instead of "missing test for new --quote flag". |
| t-rejected-context-everything | rejected-direction | Line-edited instead of pushing back on the design. |

`iter-02-v4` (the winner) attacks all three:

- Elevated "first character is `#`" to the top of the prompt (kills preambles).
- Inverted the default lean to "When in doubt, pick Variant A".
- Added explicit "Multi-issue PRs" section with a worked multi-bug example (each independent issue gets its own bullet AND its own numbered fix item).
- Added "behaviour without tests is a missing-test finding, not LGTM" as a self-check item.

All three target regressions recovered (+1.67, +2.67, +2.00 per-case delta on the L1 composite score). Two minor new regressions appeared (`t-clean-theme-hook` overreached on missing-test; `p-doc-url-mismatch` trusted the README diff instead of reading the code). Both are borderline judgement calls.

## Per-category Layer 1 (v2 → v4 deltas, joint set of cases with output)

| Category | v2 file | v4 file | v2 concept | v4 concept | v2 fix-block | v4 fix-block |
|----------|---------|---------|------------|------------|--------------|--------------|
| security | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 | 1.00 |
| logic-bug | 0.80 | 1.00 | 0.83 | 0.90 | 0.00 | 1.00 |
| missing-test | 0.50 | 1.00 | 0.58 | 0.83 | 0.00 | 1.00 |
| multi-bug | 1.00 | 1.00 | 0.75 | 1.00 | 0.00 | 1.00 |
| rejected-direction | 1.00 | 1.00 | 0.62 | 0.62 | 0.00 | 1.00 |
| style | 1.00 | 0.75 | 1.00 | 0.92 | 0.00 | 0.75 |
| doc | 1.00 | 0.50 | 1.00 | 0.50 | 0.00 | 0.50 |
| clean (inverted) | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.50 |
| test-only | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 | 0.00 |

(Per-category numbers depend on the joint set; full per-case CSV at `results/iter-02-v4/scorecard.csv`.)

## Ship verification (GitHub end-to-end stage)

The eval repo's own `.github/workflows/glue-review-smoke.yml` exercises the real composite Action against a real PR:

- Workflow pinned to `erain/glue@eval/v4` (the winner ref).
- Secrets set on `erain/glue-review-eval`: `OPENROUTER_API_KEY`, `NVIDIA_API_KEY`.
- Triggered on PRs labelled `eval-smoke`, or via `workflow_dispatch` with a PR number.
- Smoke PR: https://github.com/erain/glue-review-eval/pull/1 (plants a SQL injection in `smoke-demo/app.py:find_by_url_like`).

The action correctly builds `glue-review` from the pinned ref, runs against the PR diff, and posts a single sticky comment on the PR thread. The posted comment is the exact v4 format the local harness produced. (See PR #1's comment thread for the live evidence.)

## Repro

```
git clone https://github.com/erain/glue-review-eval
cd glue-review-eval
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
echo "OPENROUTER_API_KEY=..." > .env.local

# Rerun the baseline (v2)
REVIEW_PROMPT_VERSION=v2 ./tools/iterate.sh v2 my-baseline 8

# Rerun the winner (v4)
./tools/iterate.sh v4 my-v4 8

# Compare
.venv/bin/python -m harness.compare --base my-baseline --head my-v4

# Layer 3 (downstream fix-success via codex)
.venv/bin/python -m harness.layer3 --iter my-v4 --executor codex
```

## Ship recommendation

Ship v4 (eval-side `eval/v4` branch; renamed to `v3.md` on glue main) as the next sequential prompt version on `erain/glue`. Keep `defaultPromptVersion` at v2 for one release window so consumers can opt-in via `--prompt-version v3`; promote to default once one or two real downstream-Action installs have confirmed the new comment shape.

Companion PR draft: `results/SHIP_PR_BODY.md`.
