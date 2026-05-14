## glue-review

**Implementation/test contradiction** — `Parse()` always returns `Parsed: true` but `TestParse_InvalidJSONIsUnparsed` expects `Parsed: false` for invalid JSON, so that test will fail.

- **high** — `entry/entry_test.go:109` — `TestParse_InvalidJSONIsUnparsed` asserts `e.Parsed == false` for `"not json"`, but the new implementation unconditionally sets `Parsed: true` in `entry/entry.go:29`, so this test will always fail.
- **medium** — `entry/entry.go:29` — Every call to `Parse()` now returns `Parsed: true`, making the field carry no information. The real discriminator is `Fields == nil`, but any code outside this diff that checks `e.Parsed` (as the test still does) will misclassify unstructured lines as structured.

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **entry/entry_test.go:109** — `TestParse_InvalidJSONIsUnparsed` expects `Parsed: false` for invalid JSON, but the implementation always returns `Parsed: true`.
   - Change the assertion inside `TestParse_InvalidJSONIsUnparsed` from checking `e.Parsed` to checking `e.Fields != nil`, consistent with the new contract documented in `TestParse_RawPassthrough` and used in `render/render.go`.
   - Specifically, replace:
     ```go
     if e.Parsed {
         t.Errorf("Parse(%q).Parsed = true, want false", "not json")
     }
     ```
     with:
     ```go
     if e.Fields != nil {
         t.Errorf("Parse(%q).Fields = %v, want nil", "not json", e.Fields)
     }
     ```
   - Update the test comment to match the new design (structured vs unstructured is determined by `Fields`, not `Parsed`).
   Acceptance: `go test ./entry/ -run TestParse -v` passes with all three test functions green.

2. **entry/entry.go:29** — Consider whether `Parsed` should remain always-true or be removed entirely. If callers outside this diff still check `e.Parsed`, they will silently misclassify unstructured lines. At minimum, update the godoc on the `Entry.Parsed` field to document that it is always true and `Fields == nil` is the correct way to detect unstructured input.
   Acceptance: Document that `Parsed` is deprecated as a discriminator and `Fields == nil` should be used instead.
```
