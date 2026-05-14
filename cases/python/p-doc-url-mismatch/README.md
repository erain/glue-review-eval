# p-doc-url-mismatch

**Category:** doc · **Severity:** low · **Host:** python-linkr

The README's Endpoints table and curl example are rewritten to advertise
`POST /shorten`, but `app/routes.py` still defines the route as
`POST /links`. There is no `/shorten` handler. Anyone copy-pasting the
README curl gets a 404.

Pure documentation PR — no acceptance test gates a code fix, but the
reviewer should:

1. Name the README/code mismatch explicitly.
2. Point at the wrong path (`/shorten`) versus the actual route
   (`/links`).
3. Propose either reverting the doc or adding a `/shorten` route +
   tests.

The `must_not_flag` list guards against the reviewer pivoting to
inventing security or concurrency bugs on a doc diff.
