Let me check for existing tests and other packages that might use `MatchGlobal`.Let me check the render package for the convention the PR references.## glue-review

`MatchGlobal` will panic when `GlobalFilter` is nil, regressing the nil-safe behavior that `Filter.Match` already provides.

- **high** — `filter/filter.go:127` — `MatchGlobal` dereferences `GlobalFilter` without a nil check; the original `flt.Match(e)` gracefully handled nil receivers, but calling `filter.MatchGlobal` before the global is set (e.g., in tests) will panic.
- **medium** — `filter/filter.go:118` — The doc comment claims this "matches how other tiny tools in this repo (see render package conventions) keep their state," but the render package uses an interface-based factory with no global state, so the justification is inaccurate.

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **filter/filter.go:127** — `MatchGlobal` panics when `GlobalFilter` is nil.
   - Add a nil guard to `MatchGlobal`:
     ```go
     func MatchGlobal(e entry.Entry) bool {
         if GlobalFilter == nil {
             return true
         }
         return GlobalFilter.Match(e)
     }
     ```
   Acceptance: Add a test calling `filter.MatchGlobal(entry.Entry{})` without setting `GlobalFilter`; it must return `true` (not panic).

2. **filter/filter.go:118** — Doc comment misrepresents the render package as using global state.
   - Remove the sentence "and matches how other tiny tools in this repo (see render package conventions) keep their state" from the `GlobalFilter` variable comment.
   Acceptance: The comment on `GlobalFilter` must not reference the render package or claim existing conventions justify global state.
```
