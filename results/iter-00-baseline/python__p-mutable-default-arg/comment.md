## Summary

The branch exposes the `tried` candidate list from `generate_unique_short_id` so callers can introspect collisions, but uses a mutable list (`[]`) as the default argument — a classic Python pitfall where the default is shared across all calls.

## Issues

- [critical] app/shortener.py:27 — **Mutable default argument `tried: list[str] = []`**. The empty list is created once at function definition time and shared across every call that omits `tried`, so collision candidates leak between unrelated invocations. Fix: change the signature to `tried: list[str] | None = None` and add `if tried is None: tried = []` at the top of the function body.

## Looks good

- The docstring clearly explains the purpose of `tried`, which is great.
- The new test in `tests/test_tried_default.py` correctly targets the bug and will catch the fix.

## Open questions

- None — this is a well-scoped, single-commit change. Once the mutable default is fixed, it's ready to merge.
