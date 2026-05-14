Let me check if the source code flags were also renamed to match the README.Let me check the Go source files to see if the flag definitions were also updated.The README was updated to rename `--since` → `--within` and `--until` → `--before`, but the Go source code still uses the old flag names. Let me check the filter package too.Let me also check the test files to understand the full scope of the rename.The README was updated to rename `--since` → `--within` and `--until` → `--before`, but the Go source code in `cmd/glog/main.go` still uses the old flag names. Users following the docs will get broken flags.

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **cmd/glog/main.go** — The CLI flag definitions on lines 41 and 42 still use `--since` and `--until`, but the README was renamed to `--within` and `--before`. Users following the docs will get "flag provided but not defined" errors.
   - Change `fs.StringVar(&opt.since, "since", "", "")` to `fs.StringVar(&opt.since, "within", "", "")`
   - Change `fs.StringVar(&opt.until, "until", "", "")` to `fs.StringVar(&opt.until, "before", "", "")`
   - Update the `usage` constant string (lines 9–20) to replace `--since` with `--within` and `--until` with `--before`
   - Update the variable reads: change `opt.since` → `opt.within` and `opt.until` → `opt.before` (rename the struct fields and the `options` var reads accordingly, or at minimum add alias flags so both old and new names work)
   - Rename the `since`/`until` fields in the `options` struct and all references to them (`opt.since` → `opt.within`, `opt.until` → `opt.before`)
   - Acceptance: `go build ./cmd/glog && ./glog --help 2>&1 | grep -E '(within|before)'` shows the new flag names, and `./glog --within 15m -f /dev/null` does not error on unknown flag.
```
