Let me read the modified file for more context.```
## glue-review

**critical** — `app/routes.py:82` — `/admin/links` endpoint is missing `require_api_key` auth dependency, so it is publicly accessible to unauthenticated callers despite the test expecting a 401/403/503 rejection.

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **app/routes.py:82** — `@router.get("/admin/links")` is missing the `require_api_key` dependency that every other data endpoint uses, allowing unauthenticated users to list all live links.
   - Change `@router.get("/admin/links")` to `@router.get("/admin/links", dependencies=[Depends(require_api_key)])`.
   Acceptance: `pytest tests/test_admin_links.py::test_admin_links_requires_api_key -xvs` passes (the response status code is in 401/403/503 without auth).
```
