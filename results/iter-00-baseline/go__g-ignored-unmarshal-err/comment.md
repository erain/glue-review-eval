Let me check the current state of the files for additional context.## Summary

This branch reworks `entry.Parse` to be "tolerant" — always returning `Parsed: true` and using `Fields == nil` to signal unstructured lines, while removing the early `{`-prefix fast-reject and silencing `json.Unmarshal` errors.

## Issues

- **[critical]** `entry/entry_test.go:107` — `TestParse_InvalidJSONIsUnparsed` expects `Parse("not json").Parsed == false`, but the new `Parse` unconditionally sets `Parsed: true`. **This test will fail as-is.** Fix: Remove the test, or (if the intent is to keep `Parsed` meaningful) revert `Parse` to set `Parsed: false` when unmarshal fails and `m == nil`.

- **[major]** `entry/entry.go:14` — The `Entry.Parsed` doc comment ("Parsed is false when the line was not valid JSON") contradicts the new behavior where `Parsed` is always `true`. Fix: Update the comment to reflect the new semantics (e.g., "Deprecated; use Fields == nil to distinguish structured from unstructured input").

- **[major]** `entry/entry.go:41` — The guard `if !e.Parsed` in `FieldString` is now dead code since `Parsed` is always `true`. This means malformed input no longer has a safety shortcut. Fix: Either restore the guard by setting `Parsed: false` on failure, or replace the `!e.Parsed` check with `e.Fields == nil`:

  ```go
  func (e Entry) FieldString(key string) (string, bool) {
      if e.Fields == nil {
          return "", false
      }
  ```

- **[minor]** `entry/entry.go:26-30` — The early `{`-prefix fast-reject (`if len(line) == 0 || line[0] != '{'`) was removed. Now every single line (including clearly non-JSON syslog lines) goes through `json.Unmarshal`, which is a performance regression for workloads dominated by non-JSON log lines. Fix: Restore the fast-reject check before calling `json.Unmarshal` — it still allows prefixed JSON lines to be attempted (the unmarshal error is already silenced), while cheaply skipping garbage.

## Looks good

- The core design shift (use `Fields == nil` instead of `!Parsed` for fallthrough) is sound and `render/render.go` is updated consistently.
- Adding the `TestParse_InvalidJSONIsUnparsed` test shows the right instinct (ensuring raw lines are distinguishable), but it conflicts with the new `Parsed: true` default.
- The new `TestParse_RawPassthrough` comment and updated assertion correctly reflect the `Fields == nil` convention.

## Open questions

- Is the intent for `Parsed` to become a deprecated field entirely? If so, it should be removed or marked deprecated rather than left in a confusing state.
- Should `Parse` still fast-reject lines that clearly cannot be JSON (e.g., empty strings, lines without `{`), or is the uniform `json.Unmarshal` call intentional for benchmarking reasons?
