## Summary

This branch adds a single exported package-level convenience function `Filtermatch` to `filter/filter.go` that delegates directly to `(*Filter).Match`.

## Issues

No bugs found. The nil-receiver case is handled correctly by `Match`, so `Filtermatch(nil, e)` safely returns `true`.

## Suggestions

- [minor] filter/filter.go:120 — The `Filtermatch` function is a pure one-line delegation to an already-public method (`Filter.Match`), which adds API surface without new behavior. If the goal is to enable functional-style higher-order usage (e.g., passing it as a callback), consider removing this wrapper and having callers use a closure like `func(e entry.Entry) bool { return myFilter.Match(e) }` instead, which avoids diluting the package's public API. Alternatively, if the wrapper is kept, add a concrete usage example in a doc comment or a test to justify its existence.

## Looks good

- Nil-pointer safety is correctly inherited from `Match`.
- The new function is clean, minimal, and follows Go naming conventions for package-level exported functions.

## Open questions

- Is there a concrete use case (e.g., a specific external pipeline) that motivated this wrapper, or is it speculative? Understanding the consumer would help justify the added surface.
