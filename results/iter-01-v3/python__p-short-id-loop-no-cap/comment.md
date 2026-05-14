Let me read the relevant files for full context.```
## glue-review

Test expects bounded retry but calls the function with default unbounded `max_attempts=None`, so the retry loop never terminates.

- **critical** — app/shortener.py:36-40 — When `max_attempts` is `None`, the unbounded `while True` loop spins forever; callers that omit the parameter get no safety cap.
- **critical** — tests/test_unbounded_retry.py:27 — Test calls `generate_unique_short_id(lambda _c: True)` without `max_attempts`, so it hangs instead of terminating — the test is meant to verify bounded retry but exercises the unbounded path.

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **app/shortener.py:25** — Change the default for `max_attempts` from `None` back to a finite value (e.g. `MAX_ATTEMPTS`) so production callers get a hard ceiling by default.
   - Set `max_attempts: int = MAX_ATTEMPTS` as the default parameter.
   - Keep the `None` branch (unbounded retry) available but require callers to opt in explicitly.

2. **tests/test_unbounded_retry.py:27** — Pass an explicit `max_attempts=8` (or similar small number) so the test exercises the bounded path and terminates quickly.
   - Change `generate_unique_short_id(lambda _c: True)` to `generate_unique_short_id(lambda _c: True, max_attempts=8)`.

Acceptance: `pytest tests/ -x -q` passes, including `test_collision_storm_terminates_within_budget`, and the function defaults to a bounded retry for callers that don't specify `max_attempts`.
```
