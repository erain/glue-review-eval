Let me check how auth is applied on other routes in the file.```markdown
## glue-review

Admin endpoint `/admin/links` is missing API-key auth — every other route in the file requires it.

- **high** — `app/routes.py:71` — `@router.get("/admin/links")` is missing `dependencies=[Depends(require_api_key)]`; the test `test_admin_links_requires_api_key` expects a 401/403/503 without auth but the handler currently returns 200 unauthenticated.
- **low** — diff adds a `.venv` symlink at repo root; typically this belongs in `.gitignore`.

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **app/routes.py:71** — `/admin/links` admin endpoint has no authentication, but every other route in the file requires `Depends(require_api_key)`.
   - Add `dependencies=[Depends(require_api_key)]` to the `@router.get("/admin/links", ...)` decorator so it matches the auth pattern on `create_link`, `get_link`, and `delete_link`.
   Acceptance: `pytest tests/test_admin_links.py::test_admin_links_requires_api_key -v` passes (asserts 401/403/503 without an API key).

2. (optional) Add `.venv` to `.gitignore` to prevent virtual-environment symlinks from entering the repo.
```
