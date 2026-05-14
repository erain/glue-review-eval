# iter-00-baseline diagnosis

Reviewer: OpenRouter `inclusionai/ring-2.6-1t:free` (Novita upstream)
Prompt: v2 (the pre-eval baseline)
Pacing: 5s/case, retry-on-429 with 30/60s backoff.

## Headline numbers (21 cases with non-empty output)

| Layer 1 signal       | Mean | Verdict |
|----------------------|------|---------|
| flagged_file         | 0.91 | Strong — model usually finds the right file. |
| flagged_concept      | 0.87 | Strong — names the right concepts. |
| no_false_positives   | 0.95 | Strong — 1 case (test-only) invented issues. |
| has_fix_block        | 0.10 | **Broken** — only 2 of 21 emit a fenced ```markdown fix block, and both are clean PRs where the rule inverts. Real non-clean fix-block rate ≈ 0%. |
| no_severity_bullets  | 1.00 | Clean cases properly avoid severity bullets. |

## What v2 does well

- **Security recall**: 100% on sql-injection + missing-auth. Identifies the vulnerability, file, line, and a sane fix.
- **Logic-bug pinpointing**: off-by-one, file-handle leak, mutable-default-arg, ignored-error — all flagged correctly with file/line.
- **Style / doc / clean**: 100% across the board. Model doesn't manufacture issues for clean PRs and reliably catches README drift.

## What v2 gets wrong (the v3 attack surface)

### 1. Output format is the legacy `## Summary` / `## Issues` / `## Looks good` / `## Open questions` shape (gap rate ≈ 100%)

The v2 prompt asks for those sections, so the model dutifully emits them. Downstream coding agents have to parse English to extract intent; there is no machine-friendly fix block.

**v3 fix**: prescribe a single `## glue-review` header, ≤5 severity bullets, then a fenced ` ```markdown ` fix-instruction block with numbered items, each carrying an `Acceptance:` line. Three explicit variants (issues / clean / rejected) plus three worked examples.

### 2. Multi-bug PRs surface one bug but miss the other (concept ≈ 0.75)

`p-multi-auth-and-test` plants missing-auth AND missing-test in the same `/admin/links` endpoint. Baseline flagged the auth but not the missing test.

**v3 fix**: the worked Variant A example shows numbered multi-item fix blocks; the hard rules require every numbered item to have its own `Acceptance:`. Should anchor "list all the things".

### 3. Rejected-direction cases get critiqued line-by-line instead of refused at the design level (concept ≈ 0.62)

`p-rejected-globals` and `g-rejected-package-mutable` both refactor toward global mutable state. Baseline reviewer treats them as ordinary PRs and asks for nits.

**v3 fix**: Variant C with explicit "Pushback on approach" header, a 2–4 sentence design-level rebuttal, and a fix block that starts "Do NOT apply the current diff. Instead:". A worked example shows the shape.

### 4. Test-only PRs sometimes manufacture issues (1/2 cases triggered must_not_flag)

`p-test-only` adds only tests. v2 invented complaints anyway.

**v3 fix**: Variant B (clean) explicitly requires "No concerns — LGTM." when no real issue exists, and a hard rule forbids padding with nits to make the comment "look thorough".

### 5. The model frequently prepends preambles ("Let me check the diff…")

Several baseline comments open with a line of meta-commentary before `## Summary`. Downstream agents would parse this as noise.

**v3 fix**: explicit hard rule #7 ("No preamble. The comment starts with `## glue-review`.") plus the self-check.

## Cases the v2 baseline failed to score (7)

All 7 were OpenRouter upstream 429s from Novita (the free `ring-2.6-1t:free` route). Retry-with-backoff was added to `runner.py` (30s/60s/120s) and is currently filling in the gaps via `--only-empty`. Expected fully-populated baseline within ~5 minutes.

## What v3 should NOT touch

- Tool-calling workflow (git_diff_branch → git_log_branch → read_file). Baseline shows the model uses these correctly.
- Severity naming itself — the model already prefers concrete tokens. The legacy `[critical|major|minor]` is the only drift to remove.
- The "never invent issues" guardrail — baseline shows it's already mostly working.

## Predictions for iter-01-v3

- `has_fix_block` should jump from ~0 to ~0.85+ (the format is now anchored by examples).
- `flagged_concept` may slightly drop initially as the model adjusts to the tighter rubric — re-tunes in iter-02 if so.
- `no_false_positives` should hold or improve, especially on test-only / clean PRs.
- Risk: model occasionally still emits a ` ```text ` or ` ``` ` fence instead of ` ```markdown `. v3 hard rule #5 is explicit; if it still drifts, iter-02 adds a stricter self-check.
