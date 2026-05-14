# Target output format

What we want `glue-review` to emit on every PR. The whole product hangs on
hitting this shape consistently.

## Anatomy

```
## glue-review

<one-line headline — what's wrong or "no concerns">

- **<severity>** — <file:line> — <one-sentence finding>
- **<severity>** — <file:line> — <one-sentence finding>
- ... (≤ 5 bullets; collapse minors into one)

<one-paragraph context if and only if it changes the meaning of the bullets above.
omit otherwise — no padding>

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **<file>:<line>** — <problem in one sentence>.
   - <directive verb-first>
   - <directive verb-first>
   Acceptance: <test or check that must pass>

2. **<file>:<line>** — ...
```
```

## Hard rules

1. **Always exactly one comment per PR.** No inline comments. No follow-ups.
2. **Headline must be one line.** No emoji except severity emoji if used.
3. **Bullets ≤ 5.** If there are more issues, collapse the minor ones into a
   single bullet `("plus 3 minor style nits — see fix block")`.
4. **Severity vocabulary is fixed:** `critical`, `high`, `medium`, `low`,
   `nit`. Never invent severities.
5. **Fix block is fenced ` ```markdown ` exactly.** Downstream agents look
   for this fence. Don't switch to ` ```text ` or strip the fence.
6. **Each fix item has Acceptance.** Either a test command, a grep, or a
   one-line property the resulting code must satisfy.
7. **No preamble.** No "Thanks for the PR!", no "Overall this looks good
   but…". Headline first.
8. **No closing summary.** The fix block is the closing.

## Clean-PR variant

When the reviewer judges no real issues:

```
## glue-review

No concerns — LGTM.

<optional: one line of context if there's something noteworthy worth
mentioning anyway, like "tests cover the new path well">
```

No fix block. No severity bullets.

## Rejected-direction variant

When the PR's *approach* is wrong, not its lines:

```
## glue-review

**Pushback on approach** — <one-line summary of the design concern>

<2–4 sentence explanation of why the approach is wrong and what direction
to take instead>

---

### Fix instructions — paste into your coding agent

```markdown
Do NOT apply the current diff. Instead:

1. <high-level redirection step>
2. <high-level redirection step>
   Acceptance: <property the redesigned change must satisfy>
```
```

## What we are explicitly NOT doing

- No table of findings
- No "before/after" code diffs in the human section (those belong in the fix
  block if needed)
- No "see also" links
- No reviewer signature / persona ("As your AI reviewer…")
- No fenced code blocks in the human section other than the single fix block
