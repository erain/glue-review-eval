# g-multi-render-and-test

**Category:** multi-bug · **Severity:** high · **Host:** go-glog

The PR adds a `csv` mode to `render.New` (`--out csv`) emitting four
columns per entry: `ts, level, msg, fields`. The implementation has two
independent issues, both of which the reviewer must flag:

**(a) No CSV escaping.** The row is built with
`strings.Join(row, ",") + "\n"` — values containing commas, double
quotes, or newlines are emitted verbatim. A message of `hello, world`
splits across three CSV columns, breaking every downstream consumer.

**(b) No real test coverage.** The PR ships the csv renderer with only
the single planted acceptance test, which itself fails on the buggy
implementation. There is no unit test exercising the renderer's claimed
behaviour across the shape of inputs (embedded quotes, embedded
newlines, empty fields, no fields).

`TestCSV_QuotesValuesWithCommas` is the acceptance gate: it constructs
an Entry with a comma in `msg` and a comma in a field value, runs the
renderer, and asserts `encoding/csv` parses the output into exactly one
record with four columns. The buggy code emits six columns; the fix
(use `encoding/csv.NewWriter`) collapses it back to four.

Fix-block must include both directives: use `encoding/csv` for escaping,
and extend test coverage beyond the single acceptance row.
