## glue-review

New test `test_create_link_rejects_non_url_string` contradicts the schema change — it expects 422 for non-URL strings, but `url: str` in `LinkCreate` will accept any string, so this test will fail.

- **high** — `tests/test_link_validation.py:9` — Test asserts 422 for `"not a url"` payload, but the schema change from `AnyHttpUrl` to plain `str` in `app/schemas.py:11` means Pydantic will now accept any string, so this test will fail with 201.
- **medium** — `.venv` (symlink) is tracked in git; typically this belongs in `.gitignore`.

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **tests/test_link_validation.py:9** — The test `test_create_link_rejects_non_url_string` expects a 422 status for non-URL input, but the schema was intentionally loosened to `str` in `app/schemas.py:11`, so any string is now valid. Either:
   - Remove this test entirely (the old test in `tests/test_links.py` was already updated to match the new behavior), or
   - Rewrite it to assert 201 for arbitrary strings and verify the value round-trips, consistent with the updated `test_create_link_accepts_arbitrary_url_string`.
   Acceptance: `pytest tests/test_link_validation.py -v` passes without errors.

2. **`.venv`** — Remove the committed `.venv` symlink from the repo and add `.venv` to `.gitignore` if not already present.
   - Run `git rm .venv` and add `.venv` to `.gitignore`.
   Acceptance: `.venv` does not appear in `git status` or `git ls-files`.
```
