Let me look at the existing render.go to understand the full context.The CSV renderer naively joins fields with commas using `strings.Join`, which produces malformed CSV when any field value contains commas, quotes, or newlines. The test `TestCSV_QuotesValuesWithCommas` exists precisely to catch this and currently would fail.

- **critical** — render/render.go:58 — `strings.Join(row, ",")` does not CSV-escape fields; values with commas (e.g. `"hello, world"`) break column alignment and corrupt output.

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **render/render.go:58** — The csv renderer uses `strings.Join(row, ",")` which does not escape commas/quotes/newlines inside field values, producing malformed CSV.
   - Add `"encoding/csv"` to the import block.
   - Replace the naive `strings.Join` + `io.WriteString` with a `csv.NewWriter(w)` call: use `w.Write(row)` followed by `w.Flush()` and return the flush error. This ensures fields containing commas or quotes are properly quoted per RFC 4180.
   - Remove the now-unnecessary `strings.Join` line.
   Acceptance: `go test ./render/ -run TestCSV -v` passes, and the output of `TestCSV_QuotesValuesWithCommas` produces a single CSV record with exactly 4 columns where `row[2]` equals `"hello, world"`.
```
