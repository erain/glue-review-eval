## Summary
This branch adds a new flag `--last N` to the `glog` command, which prints only the most recent N matched entries.

## Issues
- [minor] cmd/glog/main.go:121 — The `last` flag is not documented in the usage message. Fix: In main.go, add a description for the `--last` flag to the usage message.
- [minor] cmd/glog/main.go:68 — The `last` flag is not checked for validity (e.g., negative value). Fix: In main.go, add a check to ensure the `--last` flag value is non-negative.

## Suggestions
- [minor] cmd/glog/main.go:0 — Consider adding more test cases to cover different scenarios with the `--last` flag. Fix: In main.go, add more test cases to the `TestRun_LastReturnsExactlyN` function to cover different scenarios with the `--last` flag.

## Looks good
* The `--last` flag is implemented correctly and works as expected.
* The code is well-organized and easy to follow.

## Open questions
* How does the `--last` flag interact with other flags, such as `--since` and `--until`?
* Are there any plans to add more features to the `glog` command in the future?
