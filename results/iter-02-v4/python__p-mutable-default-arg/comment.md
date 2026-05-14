The diff has the classic Python mutable-default-argument bug. `tried: list[str] = []` creates one shared list that accumulates state across calls. The new test correctly validates this.## glue-review

Mutable default argument `tried: list[str] = []` leaks state across calls.

- **high** — app/shortener.py:27 — `tried: list[str] = []` is a mutable default; every call that omits `tried` shares the same list object, so candidates from prior calls accumulate.
- **medium** — tests/test_tried_default.py — test exists but the source code has the bug it detects; no fix is applied yet.

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **app/shortener.py:27** — Change the function signature and body to avoid the mutable default:
   - Change `tried: list[str] = []` to `tried: list[str] | None = None`.
   - Add at the top of the function body (before the loop):
     ```python
     if tried is None:
         tried = []
     ```
   - Keep the existing `tried.append(candidate)` and the docstring — they are correct once the default is no longer shared.
   Acceptance: `generate_unique_short_id.__kwdefaults__["tried"]` is `None`, not a `list`.

2. **tests/test_tried_default.py** — The existing test (`test_default_tried_does_not_leak_between_calls`) already validates the fix. After applying item 1, run:
   - `pytest tests/test_tried_default.py -v` — must pass.
   Acceptance: all 3 calls to `generate_unique_short_id` complete without error and the assertion about the default holds.
```
