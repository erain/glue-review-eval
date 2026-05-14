Let me check for test files and usage patterns that could be affected by the global state.## glue-review

New global mutable state (`GlobalFilter` / `MatchGlobal`) is introduced without tests and without guarding the nil receiver explicitly in `MatchGlobal`.

- **medium** — `filter/filter.go:119-126` — `GlobalFilter` and `MatchGlobal` are new exported API surface added with zero test coverage; existing `filter_test.go` only tests `(*Filter).Match` directly.
- **medium** — `filter/filter.go:131` — `MatchGlobal` dereferences `GlobalFilter` without a nil check before calling `.Match()`; if `GlobalFilter` is never set (e.g., in future test or embedded usage) the call relies on `Match`'s nil-receiver guard, which is fragile and non-obvious.
- **low** — `filter/filter.go:119` — `GlobalFilter` is an exported `var`, meaning any package can silently overwrite the active filter mid-execution without going through `filter.New` validation.

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **filter/filter.go:131** — `MatchGlobal` calls `GlobalFilter.Match(e)` without a nil guard; if `GlobalFilter` is unset the behavior depends on `Match`'s implicit nil-receiver check, which is easy to break during refactors.
   - Add an explicit nil check before delegating:
     ```go
     func MatchGlobal(e entry.Entry) bool {
         if GlobalFilter == nil {
             return true
         }
         return GlobalFilter.Match(e)
     }
     ```
   Acceptance: a Go test that calls `MatchGlobal(entry.Parse("anything"))` before setting `GlobalFilter` returns `true` without panicking.

2. **filter/filter_test.go** (append) — no tests exercise `GlobalFilter` or `MatchGlobal`.
   - Add `TestMatchGlobal_BeforeSet` — confirms `MatchGlobal` returns true when `GlobalFilter` is nil.
   - Add `TestMatchGlobal_AfterSet` — sets `GlobalFilter` to a known filter, calls `MatchGlobal` with a matching and non-matching entry, asserts correct booleans, and resets `GlobalFilter = nil` in defer.
   - Add `TestGlobalFilter_IsExported` — compile-time assertion via `var _ *Filter = GlobalFilter` that the type hasn't drifted.
   Acceptance: `go test ./filter/ -run TestMatchGlobal -v` passes with all three sub-tests.

3. **filter/filter.go:119** — `GlobalFilter` is exported as `var` so any package can overwrite it without validation.
   - Make the variable unexported (`globalFilter`) and expose a setter function `SetGlobalFilter(f *Filter)` that validates the filter is non-nil, or at minimum convert `GlobalFilter` to a private var with a public `SetGlobal` setter.
   - Update `cmd/glog/main.go` to call the setter instead of direct assignment.
   Acceptance: `go build ./...` compiles cleanly after the rename, and `go test ./filter/ -run TestGlobalFilter_IsExported` still passes.
```
