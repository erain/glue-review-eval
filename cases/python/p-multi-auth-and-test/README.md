## p-multi-auth-and-test

**Category:** multi-bug - **Severity:** high - **Host:** python-linkr

Adds `GET /admin/links`, an operator helper that lists every
non-soft-deleted Link row. The PR has two independent issues that must
both be caught in the same review:

1. **Missing auth.** The new decorator omits
   `dependencies=[Depends(require_api_key)]`. Every other `/links*` route
   in `app/routes.py` is guarded; this one isn't. The route lives under
   `/admin/` and exposes the full live link table, so the gap is
   exploitable, not cosmetic.

2. **No test for the new endpoint.** All 26 existing tests still pass
   because none of them touch `/admin/links`. There's no happy-path
   coverage and no auth-rejection coverage; a future refactor can break
   the route silently.

The acceptance harness `tests/test_admin_links.py` shipped with the case
exercises both: `test_admin_links_requires_api_key` (fails on the
planted code, passes once auth is added) and
`test_admin_links_returns_live_rows_only` (passes throughout, confirms
the happy path is intact). `fix_directives` lists one item per bug; the
reviewer is expected to do the same.
