Let me check the original `plain.Render` for comparison.## Summary

This branch adds a `--quote` CLI flag that forces all tail values to be double-quoted in plain output mode, introducing a new `plainQuoted` renderer in `render/render.go`.

## Issues

- [major] render/render.go:54 — `plainQuoted.Render()` is a near-exact copy of `plain.Render()`, differing only in the quoting line. This is ~40 lines of duplicated logic that will drift if `plain.Render()` is ever modified. Fix: Refactor `plain` to accept a quote-mode parameter (e.g., a `quoteAll bool` field on the `plain` struct or a functional option), or have `plainQuoted` delegate to `plain` and post-process field values, so quoting behavior is not duplicated.

- [minor] render/render.go:62 — The `init()` smoke test only covers a single happy-path entry (`k="v"`). It does not exercise edge cases like empty string values, values containing quotes/backslashes/newlines, or unparsed entries. Fix: Extend the smoke test to include at least one empty value and one value requiring escape sequences (e.g., `Fields: map[string]any{"empty": "", "q": "he said \"hi\""}`) and assert the output is correctly quoted/escaped.

## Suggestions

- [minor] cmd/glog/main.go:74 — When `--quote` is used with `--out json`, the flag is silently ignored. Consider adding a warning or log message (at debug level) so users are aware, or document the behavior more explicitly in the flag help text.

- [minor] cmd/glog/main.go:69 — The help text says "always quote tail values (default false)" but does not clarify that this only applies to the plain renderer. Consider making the help text say "in plain output mode" to match the guard logic.

## Looks good

- The `opt.quote && opt.out != "json"` guard in `main.go` is correct — JSON output is inherently quoted.
- `fmt.Sprintf("%q", v)` is the right Go idiom for double-quoting with proper escaping.
- Sorting of field keys (`sort.Strings(keys)`) is consistent with `plain.Render()`.
- The `init()` smoke check is a good practice for catching format string regressions at startup.
