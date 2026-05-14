# p-missing-auth-delete

**Category:** security · **Severity:** high · **Host:** python-linkr

A new `POST /admin/purge-deleted` endpoint that hard-deletes soft-deleted
rows. Every other write endpoint in `app/routes.py` uses
`dependencies=[Depends(require_api_key)]`; this one quietly skips it.

The destructive operation under `/admin/` makes the missing guard
unambiguous: the reviewer must recognise the inconsistency with the
surrounding handlers and direct a coding agent to add the dependency.
Acceptance test calls the route without an API key and expects 401/403/503.
Buggy code returns 200 and wipes the soft-deleted rows.
