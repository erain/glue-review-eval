```
## glue-review

Package-level `Filtermatch` added without tests and with a naming-convention issue.

- **medium** — `filter/filter.go:123` — New exported function `Filtermatch` has no test coverage anywhere in the diff.
- **nit** — `filter/filter.go:123` — Exported name should be `FilterMatch` per Go camelCase convention (`Filtermatch` has a lowercase "m").

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **filter/filter.go:123** — Rename `Filtermatch` to `FilterMatch` to follow Go's mixed-caps convention for exported identifiers.
   Acceptance: `go build ./filter/...` succeeds and the function name is `FilterMatch`.

2. **filter/*_test.go** (new or existing) — Add at least one test for the `FilterMatch` function covering both the case where the inner `Match` returns true and false.
   Acceptance: `go test ./filter/ -run TestFilterMatch -v` passes.
```

```
