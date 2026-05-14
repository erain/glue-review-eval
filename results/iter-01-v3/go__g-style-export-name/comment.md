## glue-review

Exported function `Filtermatch` violates Go naming conventions — should be `FilterMatch`.

- **nit** — `filter/filter.go:121` — Exported function name `Filtermatch` mixes casing; Go convention requires `FilterMatch` (each word's first letter capitalized).

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **filter/filter.go:121** — Exported function `Filtermatch` violates Go mixed-caps naming convention.
   - Rename `Filtermatch` to `FilterMatch` (both the function declaration and the comment header above it).
   Acceptance: `go build ./filter/` succeeds and `grep -n 'Filtermatch' filter/filter.go` returns no results.
```
