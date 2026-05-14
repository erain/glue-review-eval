# g-style-export-name

**Category:** style · **Severity:** low · **Host:** go-glog

A new exported helper is added to `filter/filter.go`:

```go
func Filtermatch(f *Filter, e entry.Entry) bool { return f.Match(e) }
```

The body is correct. The name is not: Go's convention for multi-word
exported identifiers is mixed-case (`FilterMatch`), and even better,
since the package is already named `filter`, the symbol should just be
`Match` (or this helper should be dropped in favour of the existing
`(*Filter).Match` method).

The reviewer should flag the casing as a style nit without escalating
it into a fabricated behavioural bug. No new failing test is shipped;
existing tests still pass.
