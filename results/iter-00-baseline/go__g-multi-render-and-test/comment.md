Let me look at the render.go file for more context and check for existing reserved keys.## Summary

This branch adds a `--out csv` mode to `glog`, implementing a CSV renderer that outputs log entries as four-column records (ts, level, msg, fields) suitable for spreadsheet imports.

## Issues

- **[critical] render/render.go:46** — The CSV renderer uses `strings.Join(row, ",")` which produces **bare, unquoted commas**. When `e.Msg` or any field value contains a comma (e.g., `"hello, world"`), the output is not valid CSV — `encoding/csv` will split it across extra columns. The included test `TestCSV_QuotesValuesWithCommas` in `render/render_csv_test.go:12` explicitly asserts that the output must be parseable CSV with correct column count, but the current implementation cannot pass that test. Fix: Replace the manual `strings.Join` with `encoding/csv.NewWriter` (or manually RFC 4180-quote fields containing `,`, `"`, or newlines) so that all four columns are properly escaped.

## Open questions

- The `tail` column (column 4) joins key=value pairs with spaces. If a value contains a space, the `encoding/csv` round-trip will preserve it, but spreadsheet tools may still misparse `user=a, b` as two sub-fields within the tail column. Is that acceptable, or should individual key=value pairs in the tail be semicolon-delimited instead?

## Looks good

- Clean separation: the `csv` struct reuses `reservedKeys` already defined for `plain`, avoiding duplication.
- The `New` switch statement cleanly integrates the new format with proper error for unknowns.
- The test is well-structured — it round-trips output through `encoding/csv.NewReader`, which is the right validation approach.
- Help text in `main.go` is updated consistently.
