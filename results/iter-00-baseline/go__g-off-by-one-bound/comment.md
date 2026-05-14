## Summary

This branch adds a `--last N` flag to `cmd/glog/main.go` that buffers matched log entries and prints only the most recent N, along with a test file `cmd/glog/last_test.go`.

## Issues

- [critical] cmd/glog/main.go:131 — Off-by-one error in the `--last` buffer slicing. `start := len(buf) - opt.last - 1` prints one more entry than requested when `len(buf) > opt.last`. For example, with 10 buffered entries and `--last 3`, `start = 10 - 3 - 1 = 6`, so `buf[6:]` yields 4 entries instead of 3. Fix: In `cmd/glog/main.go`, change `start := len(buf) - opt.last - 1` to `start := len(buf) - opt.last` (remove the `- 1`).
