Let me check the existing test suite for the shortener to understand the full picture.Let me check the existing test files for the shortener.```
## glue-review

New test will hang and fail because it calls the unbounded path without a cap.

- **critical** — tests/test_unbounded_retry.py:34 — `generate_unique_short_id(lambda _c: True)` is called with no `max_attempts`, so it enters the `while True` loop and spins forever; it never raises `ShortIDCollision`, so both assertions will fail (thread still alive after 2 s, `result["exc"]` is `None`).
- **medium** — app/shortener.py:11 — `MAX_ATTEMPTS = 8` is defined but never referenced, since the default is now `None`.

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **tests/test_unbounded_retry.py:34** — The test calls `generate_unique_short_id(lambda _c: True)` with no `max_attempts`, which enters the unbounded `while True` loop and never terminates or raises `ShortIDCollision`.
   - Pass an explicit cap so the bounded code path is exercised: change the call to `generate_unique_short_id(lambda _c: True, max_attempts=8)` (or any small integer).
   - Update the test docstring/name accordingly (it tests the *bounded* path, not the unbounded one).
   Acceptance: `pytest tests/test_unbounded_retry.py -x -v` passes (test terminates quickly and asserts `ShortIDCollision`).

2. **app/shortener.py:11** — `MAX_ATTEMPTS = 8` is dead code after making `max_attempts` default to `None`.
   - Either remove the constant or, if callers elsewhere still reference it, keep it and add a comment. Verify with `grep -rn MAX_ATTEMPTS app/ tests/`.
   Acceptance: no references to `MAX_ATTEMPTS` remain anywhere in the repo, or it is documented as intentionally kept for downstream use.
```
