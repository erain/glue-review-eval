Let me check the full current state of the modified file for context on what happens after the retry loop.Let me also check the existing tests for `max_attempts` usage.## Summary

This branch makes `max_attempts` optional in `generate_unique_short_id`, defaulting to unbounded retry (`while True`) when `None`, and adds an acceptance test meant to verify termination under a collision storm.

## Issues

- [critical] `tests/test_unbounded_retry.py:30` — The test calls `generate_unique_short_id(lambda _c: True)` without passing `max_attempts`, so it hits the new unbounded `while True` loop and **hangs forever** — `ShortIDCollision` is never raised. The 2-second timeout will fire, making the test flaky/failing. **Fix:** Pass an explicit `max_attempts` (e.g., `max_attempts=8`) in the call so the bounded retry path is exercised and the function raises `ShortIDCollision` as the test expects.

## Looks good

- The `generate_unique_short_id` implementation itself is clean — when `max_attempts` is explicitly provided, the original bounded `for` loop runs and raises `ShortIDCollision` correctly.
- The docstring update explains the semantics well.

## Open questions

- Was the intent to make unbounded the default? If so, the test should document why it overrides that default with a bounded value. If the intent was to keep a safety cap as default, the function signature should use a sentinel (e.g., `max_attempts: int | Unbounded = UNBOUNDED`) instead of `None` to keep the test passing without changes.
