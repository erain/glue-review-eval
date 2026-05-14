## glue-review

Off-by-one bug in `--last` flag output window — shows N+1 entries instead of N.

- **critical** — `cmd/glog/main.go:132` — `start` is computed as `len(buf) - opt.last - 1`, which includes one extra entry; for `--last 3` with 5 matches you get entries at indices 1–4 (b,c,d,e) instead of 2–4 (c,d,e).

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **cmd/glog/main.go:132** — Off-by-one in `--last` slicing index causes N+1 entries to be printed.
   - Change `start := len(buf) - opt.last - 1` to `start := len(buf) - opt.last`.
   - Acceptance: `go test ./cmd/glog/ -run TestRun_LastReturnsExactlyN -v` passes (currently fails — the test emits 4 newlines instead of the expected 3).
```
