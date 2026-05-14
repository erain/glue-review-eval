```
## glue-review

Mutable default argument `tried: list[str] = []` will leak state across calls.

- **high** — app/shortener.py:29 — `tried: list[str] = []` uses a mutable default; every call without an explicit `tried` shares the same list object, so candidates from prior invocations accumulate.

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **app/shortener.py:29** — Replace the mutable default `tried: list[str] = []` with a `None` sentinel and create a fresh list inside the function body.
   - Change the signature to `tried: list[str] | None = None`.
   - Add `if tried is None: tried = []` as the first line of the function body.
   Acceptance: `pytest tests/test_tried_default.py -v` passes.
```
```
