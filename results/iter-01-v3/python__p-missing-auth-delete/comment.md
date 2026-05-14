```
## glue-review

Admin purge endpoint exposes destructive operation to unauthenticated callers — missing `require_api_key` dependency that every other endpoint has.

- **critical** — `app/routes.py:71` — `admin_purge_deleted` is missing `dependencies=[Depends(require_api_key)]`, so anyone can hard-delete all soft-deleted rows without an API key. The test at `tests/test_admin.py:21-24` asserts this must be rejected, but the route handler does not enforce it.
- **low** — `.venv` (a symlink to `/home/ubuntu/src/...`) is tracked in the repo; it should be in `.gitignore` instead.

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **app/routes.py:71** — The `admin_purge_deleted` endpoint has no authentication guard, so unauthenticated callers can invoke a destructive hard-delete.
   - Add `dependencies=[Depends(require_api_key)]` to the `@router.post("/admin/purge-deleted", ...)` decorator, matching the pattern used by `create_link`, `get_link`, and `delete_link` in the same router.
   Acceptance: `pytest tests/test_admin.py::test_purge_deleted_removes_only_soft_deleted_rows -x` passes (the test already sends both unauthenticated and authenticated requests and asserts 401/403/503 without auth).

2. **.venv** — A virtual-environment symlink is tracked in the repository.
   - Add `.venv` to `.gitignore` and remove it from the index: `git rm --cached .venv`.
   Acceptance: `git ls-files .venv` returns empty and `.venv` appears in `.gitignore`.
```
