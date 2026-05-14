Looking at the diff, there are several issues to flag.

## glue-review

Self-contradicting test: new regression guard expects 422 on plain strings, but the schema intentionally loosened to `str`.

- **critical** — `tests/test_link_validation.py:9` — `test_create_link_rejects_non_url_string` asserts 422 for `"not a url"`, but `LinkCreate.url` is now `str`, so Pydantic will return 201 (or at minimum not 422); this test will fail on every CI run and contradicts the intentional schema change.
- **medium** — `.venv` — a symlink to the local virtualenv was added to tracked files; this is a workspace artifact, not source code.
- **nit** — `tests/test_links.py:15-24` — the original `test_create_link_validates_url` was renamed to `test_create_link_accepts_arbitrary_url_string`, which flips its purpose from "reject bad input" to "accept unusual input." The rename obscures the fact that the validation contract was intentionally weakened.

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **tests/test_link_validation.py** — The test `test_create_link_rejects_non_url_string` contradicts the intentional schema change (LinkCreate.url relaxed from AnyHttpUrl to str). Either:
   - Delete this test entirely (since the schema loosening is deliberate), or
   - Rewrite it to verify the *new* contract — e.g., assert that `file://` and custom schemes are now accepted (201), while truly malformed payloads (e.g., integers, arrays) still fail validation.
   Acceptance: `pytest tests/test_link_validation.py -q` passes.

2. **.venv** — Remove the committed symlink from tracked files.
   - Run `git rm --cached .venv` and add `.venv` to `.gitignore` if not already present.
   Acceptance: `git status` no longer shows `.venv` as a tracked or untracked file.
```
