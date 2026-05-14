# g-rejected-package-mutable

**Category:** rejected-direction · **Severity:** high · **Host:** go-glog

The PR adds a package-level `var GlobalFilter *Filter` to the `filter`
package together with a `MatchGlobal(entry.Entry) bool` helper, populated
by `cmd/glog/main.go` after flag parsing. The main loop is rewritten
from `flt.Match(e)` to `filter.MatchGlobal(e)`. Rationale in the diff:
"single-process tool — no need to pass the filter everywhere; this is
simpler."

The code compiles and the existing tests still pass. The reviewer's job
is to push back on the direction, not to surface a bug:

- Global mutable state in a previously-clean value-type package.
- Makes test isolation impossible — any test that runs `run()` clobbers
  the shared global.
- Trades explicit dependency-passing for hidden coupling.
- Bakes in a "single-process tool" assumption that breaks the moment
  anyone tries to use the package as a library.

Fix-block must direct a revert: remove `GlobalFilter` and `MatchGlobal`,
drop the `filter.GlobalFilter = flt` assignment, restore `flt.Match(e)`
at the call site. If consolidating filter+render in `cmd/glog` is
genuinely wanted, do it with a local struct there — not a package
global.

No acceptance test (rejected-direction).
