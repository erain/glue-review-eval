## glue-review

Off-by-one bug in `--last N` flag — it prints N+1 entries instead of N.

- **critical** — cmd/glog/main.go:143 — `start := len(buf) - opt.last - 1` should not subtract 1; with 5 matched entries and `--last 3`, it emits 4 lines (indices 1–4) instead of 3 (indices 2–4).

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **cmd/glog/main.go:143** — Off-by-one in `--last N` buffer window start index.
   - Change `start := len(buf) - opt.last - 1` to `start := len(buf) - opt.last`.
   - The `- 1` causes the slice `buf[start:]` to include one extra entry, so `--last 3` on 5 matches prints 4 lines instead of 3.
   Acceptance: `go test ./cmd/glog/ -run TestRun_LastReturnsExactlyN -v` passes and the output contains exactly 3 lines.
```
