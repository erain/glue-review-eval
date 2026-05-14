Let me examine the existing code to understand the auth patterns and the `Link` model.Now I have full context. The critical issue is clear.

## glue-review

`POST /admin/purge-deleted` is missing authentication — a destructive hard-delete endpoint is publicly accessible.

- **critical** — `app/routes.py:71` — The `admin_purge_deleted` handler has no `dependencies=[Depends(require_api_key)]`, while every other write/read endpoint in the file (`create_link`, `get_link`, `delete_link`) is protected. Unauthenticated callers can hard-delete all soft-deleted rows.

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **app/routes.py:71** — `POST /admin/purge-deleted` is missing authentication.
   - Add `dependencies=[Depends(require_api_key)]` to the `@router.post("/admin/purge-deleted", ...)` decorator, matching the pattern used by `create_link`, `get_link`, and `delete_link`.
   - The existing import of `require_api_key` (line 3 of the original file) already covers this.
   Acceptance: With auth headers, `POST /admin/purge-deleted` returns 200 + `{"removed": N}`. Without auth headers, it returns 401 or 403 (not 200).
```
