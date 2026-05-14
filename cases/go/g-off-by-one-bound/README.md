# g-off-by-one-bound

**Category:** logic-bug · **Severity:** high · **Host:** go-glog

A new `--last N` flag is added to `cmd/glog/main.go`. After matched
entries are buffered into a slice, the tail is taken with
`buf[start:]` where `start := len(buf) - opt.last - 1` — one too many.

`TestRun_LastReturnsExactlyN` feeds five matching entries with
`--last 3` and asserts exactly three output lines. The buggy code emits
four (`b c d e` instead of `c d e`), so the reviewer should at minimum
flag the off-by-one and the fix-block directive should be specific
enough that any coding agent can land the one-character edit.
