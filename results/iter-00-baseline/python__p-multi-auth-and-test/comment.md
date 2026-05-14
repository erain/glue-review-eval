## Summary

This branch adds a `GET /admin/links` operator endpoint to list all non-soft-deleted links, along with corresponding tests.

## Issues

- [critical] app/routes.py:84 — `/admin/links` endpoint is missing authentication. Every other route in this router (`create_link`, `get_link`, `delete_link`) declares `dependencies=[Depends(require_api_key)]`, but `admin_list_links` does not. This exposes potentially sensitive internal data (all live URLs, hit counts, short IDs) to unauthenticated callers. The test `test_admin_links_requires_api_key` expects a 401/403/503 without auth, but the current code will return 200. Fix: Add `dependencies=[Depends(require_api_key)]` to the `@router.get("/admin/links")` decorator, consistent with all other routes.

- [minor] `.venv` — A new `.venv` symlink is included in the diff. This is a local environment artifact and should not be committed. Fix: Run `git rm --cached .venv` and add `.venv` to `.gitignore` if not already present.

## Looks good

- The endpoint correctly filters out soft-deleted links via `Link.deleted_at.is_(None)`.
- It's declared above the `/{short_id}` catch-all, preventing shadowing (good, as noted in the comment).
- Tests cover both the auth-gate and the filtering of soft-deleted rows — good coverage.
- Return shape (`short_id`, `url`, `hits`, `created_at`) is sensible for an admin listing view.

## Open questions

- Should this endpoint return a proper `response_model` Pydantic model instead of raw `list[dict]`? This would give automatic serialization validation and OpenAPI documentation, consistent with the other endpoints.
