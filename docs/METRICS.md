# Metrics

How we score what comes out of `glue-review` and decide whether an iteration
is better or worse than the previous one.

## Layer 1 — Structural recall (regex over the comment)

Per case, four boolean signals:

| Signal | Pass condition | Why we measure it |
|--------|----------------|-------------------|
| `flagged_file` | comment mentions the planted file path (or basename) | minimum bar — reviewer at least found the right file |
| `flagged_concept` | each entry in `expected.must_flag` matches the comment (regex, case-insensitive) | content recall — reviewer named what's wrong |
| `no_false_positives` | no entry in `expected.must_not_flag` matches | hallucination guard |
| `has_fix_block` | a ` ```markdown ` fenced block is present after `### Fix instructions` | format compliance — downstream agents need this fence |

Aggregate: each signal is a fraction 0–1 across all cases of a given
category × language; report means.

Clean cases (`category: clean`) invert: `flagged_file=0` is the pass, and we
add a `no_severity_bullets` signal that fails if any `**critical**` /
`**high**` / `**medium**` / `**low**` markdown appears.

## Layer 2 — LLM-as-judge (Sonnet 4.6)

A single Claude call per case, prompt template at `harness/judge/prompt.md`.
The judge sees:
- the case sidecar (ground truth),
- the host's `patch.diff`,
- the reviewer's full comment.

Judge returns strict JSON with five 0–10 scores plus a one-line rationale:

```json
{
  "identified":     0-10,   // did it find the planted bug?
  "specificity":    0-10,   // are fix directives concrete and acceptance-checkable?
  "severity_calibration": 0-10, // matches expected severity, neither inflated nor deflated?
  "conciseness":    0-10,   // is the human section short enough to read in <30s?
  "false_positives": 0-10,  // 10 = no invented issues, 0 = many
  "rationale": "string ≤ 200 chars"
}
```

Aggregate as the unweighted mean of the five scores. Per category, per
language, overall.

**Judge consistency check.** Every 10 iterations, replay 5 fixed cases
through the judge twice and require both runs land within 1.0 on overall
score; if not, the judge prompt is drifting and needs to be re-pinned.

## Layer 3 — Downstream fix-success (the product KPI)

Run a real coding agent against the case repo using *only* the fix-block
content from the reviewer's comment as instruction.

Procedure per case:
1. Clone host project into a temp dir.
2. Apply `cases/<lang>/<case-id>/patch.diff` to reproduce the buggy PR.
3. Run `acceptance.test_cmd` and confirm it currently fails (sanity).
4. Extract the ```` ```markdown ```` block from the reviewer's comment.
5. Hand that text to a downstream coding agent in a one-shot run.
   Executor rotated across `codex`, `opencode`, `claude --headless`,
   `gemini`, with model pinned to a cheap tier (Sonnet 4.6 equivalent).
6. Re-run `acceptance.test_cmd`. Pass = exit 0.

Scored as pass-rate per category × executor. The cross-executor mean is
the "product KPI" we ship on.

**Cadence:** every 5 inner-loop iterations, on a 5-case subset that covers
each language at least once. The full Layer 3 sweep (all cases × all
executors) runs once at the end of Phase 5.

## Aggregate scorecard

Each iteration appends one row to `results/scorecard.csv`:

```
iter, prompt_sha, l1_flagged_file, l1_flagged_concept, l1_no_fp,
  l1_has_fix_block, l2_overall, l2_identified, l2_specificity,
  l2_severity, l2_conciseness, l2_false_positives, l3_pass_rate,
  l3_subset_size, n_cases, ts
```

`results/scorecard.md` is a human-readable summary regenerated from the CSV
every iteration. The before/after report in Phase 5 reads from the same CSV.

## "Ready to ship" definition

We claim ship-readiness when, on the full case set:
- Layer 1: `flagged_file >= 0.90`, `has_fix_block >= 0.98`
- Layer 2: overall `>= 7.5`, with no individual dimension `< 6.0`
- Layer 3: pass-rate `>= 0.65` across executors (cheap-model fix-success)

These thresholds are placeholders — we revisit them after the baseline
run shows where current performance sits.
