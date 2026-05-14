Let me inspect the existing code for auth setup and the Link model to fully understand the change.## Summary

This branch adds a `POST /admin/purge-deleted` endpoint that hard-deletes all soft-deleted `Link` rows, along with a test file.

## Issues

- [critical] app/routes.py:92 — The `admin_purge_deleted` endpoint is missing authentication. Unlike every other mutating endpoint (`create_link`, `get_link`, `delete_link`), it has no `dependencies=[Depends(require_api_key)]`. This exposes a destructive hard-delete operation to unauthenticated callers in production. The test expects a 401/403/503 response without auth (line 22 of `test_admin.py`), confirming the intent to protect it, but the protection was never wired in. Fix: Add `dependencies=[Depends(require_api_key)]` to the `@router.post("/admin/purge-deleted", ...)` decorator on `admin_purge_deleted`.

## Looks good

- The hard-delete logic using `deleted_at.is_not(None)` correctly targets only soft-deleted rows, matching the comment.
- The `{"removed": result.rowcount or 0}` return value is a reasonable response shape.
- The test covers the key scenarios: unauthenticated rejection, correct count of purged rows, and confirming live links are unaffected.
