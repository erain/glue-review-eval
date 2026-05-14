Let me examine the existing plain renderer for comparison.Let me check the existing test files for the render package and the command.Let me check the test structure to understand testing patterns and confirm the missing test coverage.```
## glue-review

New `--quote` flag and `NewQuoted()` renderer ship without any test coverage; also significant code duplication with the existing `plain` renderer.

- **medium** — `render/render.go` adds `NewQuoted` and `plainQuoted` (60 lines) and `cmd/glog/main.go` adds `--quote` flag logic, but no test file exercises either the new renderer or the new flag.
- **low** — `plainQuoted.Render()` duplicates almost all of `plain.Render()` line-for-line; only the quoting call differs (`fmt.Sprintf("%q", v)` vs `quoteIfNeeded(v)`).

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **render/render_test.go** (new) — No tests exist for the `NewQuoted` renderer.
   - Add a test that creates a `plainQuoted` renderer, renders a parsed entry with fields that do NOT contain whitespace, and asserts each field value is double-quoted (e.g. `k="v"` not `k=v`).
   - Add a test that renders an unparsed entry and asserts the raw line is emitted unchanged.
   - Add a test that renders an entry with timestamp, level, and message and verifies the positional prefix is correct.
   - Acceptance: `go test ./render/ -run Quoted -v` passes with at least the above cases.

2. **cmd/glog/main_test.go** (new or existing) — The `--quote` flag has no integration-level test.
   - Add a test that invokes the `run` function with `--quote` and a valid log line, and asserts the output contains quoted field values.
   - Add a test that invokes `run` without `--quote` and asserts field values are unquoted (existing behavior preserved).
   - Acceptance: `go test ./cmd/glog/ -run Quote -v` passes.

3. **render/render.go** — Reduce duplication between `plain` and `plainQuoted` renderers.
   - Refactor so the shared formatting logic (timestamp, level, message, key enumeration and sorting) is extracted into a common helper method or function; both `plain.Render` and `plainQuoted.Render` should call it, differing only in how they format each field value.
   - Acceptance: after refactoring, `go test ./render/ -v` still passes with the same number of test cases; no behavior change for existing `plain` output.
```
