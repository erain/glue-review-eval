## glue-review

**Parse() marks all lines as Parsed=true even when JSON decoding fails, breaking the new test and creating an internal contradiction in the PR.**

- **critical** — `entry/entry.go:28` — `Parse()` initializes `Parsed: true` before unmarshal, so invalid JSON lines return `Entry{Parsed: true, Fields: nil}` — this directly contradicts `TestParse_InvalidJSONIsUnparsed` which expects `Parsed: false` for `"not json"`, so that test will fail.
- **medium** — `entry/entry_test.go:43-48` — `TestParse_RawPassthrough` comment says "Parse is tolerant: it always returns a Parsed entry" but `TestParse_InvalidJSONIsUnparsed` asserts the opposite; the two tests have conflicting semantics for the `Parsed` field.
- **medium** — `entry/entry.go:25` — The old fast-reject for lines not starting with `{` was removed, so `json.Unmarshal` is now called on every non-empty line including clearly non-JSON text like `"not json"`, which is wasteful and changes the failure mode.

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **entry/entry.go:28** — `Parse()` initializes `Parsed: true` in the struct literal, causing invalid-JSON lines to be returned as `Parsed: true, Fields: nil`. This breaks `TestParse_InvalidJSONIsUnparsed`.
   - Change `e := Entry{Raw: line, Parsed: true}` to `e := Entry{Raw: line}` (zero-value `Parsed` = `false`).
   - After the `if m == nil` early return, keep `Parsed: false` as-is.
   - After `e.Fields = m`, add `e.Parsed = true` so only successfully-parsed entries get `Parsed: true`.
   Acceptance: `go test ./entry/ -run TestParse_InvalidJSONIsUnparsed -v` passes (Parsed is false for "not json").

2. **entry/entry_test.go:43-48** — `TestParse_RawPassthrough` comment says "it always returns a Parsed entry" which contradicts the test in `TestParse_InvalidJSONIsUnparsed`.
   - Remove or reword the comment to say something like: "Parse returns an Entry for every line; callers distinguish structured vs raw by checking Fields == nil or Parsed."
   - Ensure the test assertions still check `e.Fields != nil` (not `e.Parsed`), since for raw lines `Parsed` should now be `false`.
   Acceptance: `go test ./entry/ -run TestParse_RawPassthrough -v` passes (Fields is nil, Parsed is false for raw lines).

3. **entry/entry.go:25** — Optionally restore the fast-reject for lines that can't possibly be JSON objects (e.g., lines not starting with `{`) to avoid unnecessary `json.Unmarshal` calls on clearly non-JSON input.
   Acceptance: `go test ./entry/ -count=1` still passes with the fast-reject in place.

Run full suite: `go test ./... -count=1` returns all green.
```
