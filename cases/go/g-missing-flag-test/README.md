# g-missing-flag-test

**Category:** missing-test · **Severity:** medium · **Host:** go-glog

A new `--quote` CLI flag and a `plainQuoted` Renderer are added so plain
output always wraps tail values in quotes. The feature itself works, but
the only verification is an `init()`-time smoke check on a single
synthetic entry — that's a "did it explode at startup" canary, not a
behavioural test.

What isn't covered:

- Empty values (`%q` of `""` is `""` — verify or document).
- Values containing quote characters (escaping).
- Reserved-key filtering / sort order.
- The `--quote` flag wiring in `cmd/glog/main.go`.
- The silent suppression when `--out=json` is set (the implementation
  just keeps the JSON renderer; that may or may not be the intent).

The reviewer should flag the absent test coverage and ask for at least
a `render_test.go` exercise of `plainQuoted` and a `cmd/glog` test that
drives `--quote` end-to-end. Acceptance runs both:
`TestPlainQuoted*` in `render/` and `TestRun_Quote*` in `cmd/glog/`.

Existing tests pass on the planted diff — the gap is what's missing.
