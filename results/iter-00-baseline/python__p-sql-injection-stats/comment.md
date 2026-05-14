The diff reveals a critical SQL injection vulnerability. Let me look at the surrounding code to confirm the pattern used elsewhere.## Summary

This branch adds a `GET /links/{short_id}/stats` endpoint that returns hit count and creation timestamp for a short link — but it introduces a **critical SQL injection vulnerability** via raw string interpolation.

## Issues

- **[critical] `app/routes.py:79`** — SQL injection via f-string interpolation of the `short_id` path parameter into a raw SQL query. An attacker can supply a payload like `abc' OR '1'='1` to dump or modify arbitrary data. The existing codebase already uses parameterized ORM queries (`select(Link).where(...)`) everywhere else; this endpoint should do the same. Fix: In `app/routes.py`, replace the raw `text(sql)` f-string query with a parameterized SQLAlchemy ORM query equivalent to what `_load_active_link` uses, for example `stmt = select(Link.hits, Link.created_at).where(Link.short_id == short_id, Link.deleted_at.is_(None))` and then `row = db.execute(stmt).first()`.

- **[minor] `app/routes.py:69-78`** — The inline comment justifying raw SQL ("keeps this one endpoint dependency-free of the ORM mapper") is misleading. ORM queries are already used in every other endpoint in this file; there is no added dependency cost to using them here. Fix: Remove the comment and use the ORM consistently, or if raw SQL is truly required, use a parameterized query with `text("... WHERE short_id = :sid")` and pass `{"sid": short_id}` as bind params.

## Looks good

- New test file `tests/test_stats.py` covers the happy path (zero hits, `created_at` present), missing-link 404, and explicitly tests for SQL metacharacter injection — good instinct, but the injection test currently **fails** against the vulnerable code (the raw-interpolated query matches the seeded row via `'1'='1'`, returning 200 instead of 404).

- The `.venv` symlink addition is a workspace artifact and not a code concern.

## Open questions

- Was the intent to eventually add real DB-level stats (e.g., from a separate hits table), making the raw SQL a stepping stone? If so, it still must be parameterized now and can evolve later.
