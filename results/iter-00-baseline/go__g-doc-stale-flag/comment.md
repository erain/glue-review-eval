The diff only touches `README.md`. Let me check the actual source code to see if the flag renames are also implemented there.Let me check the Go source code to see if the flag renames are implemented in code too.Let me look at the Go source files directly.Let me check the full source tree to make sure I haven't missed any files.## Summary

The branch renames `--since`/`--until` to `--within`/`--before` in `README.md` only, while the actual Go code in `cmd/glog/main.go` still registers and uses the old `--since`/`--until` flag names. This creates a mismatch between documentation and behavior.

## Issues

- [critical] README.md:1 — The README documents `--within` and `--before`, but the actual flags registered in `cmd/glog/main.go:36-37` are still `--since` and `--until`. Users following the README will get "unknown flag" errors. Either rename the flags in the code to match the README, or revert the README to document the actual flag names.
- [critical] cmd/glog/main.go:6-12 — The built-in `usage` string still references `--since` and `--until`, which is inconsistent with the README. The usage text and the actual registered flags agree with each other, but both contradict the README.
- [major] cmd/glog/main.go:22-23 — The `options` struct fields are still named `since` and `until`. If the intent is to rename, these should become `within` and `before` for consistency.

## Suggestions

- [minor] cmd/glog/main.go:6-12 — Update the `usage` const to match whatever flag names are finally used, so `--help` output and the README stay in sync.

## Looks good

- The README examples and flags table are internally consistent with each other.
- The only source file (`cmd/glog/main.go`) has no other issues beyond the flag naming mismatch.

## Open questions

- Was the intent to actually rename the flags in code (and the rename was missed), or is this purely a documentation change and the old flag names should remain? The commit message (`eval README: rename --since/--until to --within/--before`) suggests it was meant to be doc-only, but the rename in the README creates a breaking surface for users running the tool.
