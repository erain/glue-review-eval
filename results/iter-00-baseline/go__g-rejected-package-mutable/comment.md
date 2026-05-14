Let me check the surrounding code for more context on how this pattern is used.## Summary

This branch introduces a package-level global filter (`filter.GlobalFilter`) so that other packages can check "does this entry pass the current filter?" without threading `*Filter` through their signatures. The local `flt` in `main.go` is published to `GlobalFilter`, and `flt.Match(e)` is replaced with `filter.MatchGlobal(e)`.

## Looks good

- The nil-safety is correct: `MatchGlobal` delegates to `GlobalFilter.Match(e)`, and `Match` already handles a nil receiver (`if f == nil { return true }`), so if `GlobalFilter` is unset the default is to accept all entries — consistent with the zero-value `Filter` semantics documented at the top of the file.
- The commit message clearly states the intent.
- The comments on `GlobalFilter` and `MatchGlobal` explain the design rationale well and reference the existing convention in the `render` package.

## Open questions

- If other packages start calling `MatchGlobal` in the future, they will implicitly depend on `GlobalFilter` being set (i.e., on `cmd/glog`'s initialization order). This is fine for a single-process CLI tool, but worth keeping in mind if the library usage grows or if tests in other packages need to call `MatchGlobal` in isolation.
