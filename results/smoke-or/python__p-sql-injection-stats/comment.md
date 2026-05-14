The diff reveals a clear critical issue. Let me check the existing codebase patterns for context.## Summary

This branch adds a `GET /links/{short_id}/stats` endpoint that returns hit count and creation date for a shortened link.

## Issues

- [critical] `app/routes.py:88` — **SQL injection vulnerability.** The `short_id` path parameter is directly interpolated into a raw SQL string via f-string (`f"WHERE short_id = '{short_id}'"`). An attacker can craft a `short_id` containing SQL metacharacters (e.g., `' OR '1'='1`) to leak or modify data. Every other query in this file uses SQLAlchemy's ORM `select()` with automatic parameterisation; this endpoint should do the same. Fix: Replace the raw SQL f-string with a parameterised query. For example, use `text("SELECT hits, created_at FROM links WHERE short_id = :sid AND deleted_at IS NULL")` and pass `{"sid": short_id}` as the bind parameter, or switch to the ORM `select(Link)` pattern used by `_load_active_link`.

## Looks good

- The new endpoint follows the existing API conventions (api-key auth, 404 for missing links, returns a dict with `hits` and `created_at`).
- The test file covers the happy path, the 404 case, and explicitly tests for SQL metacharacter safety — which the current implementation will fail.

## Open questions

- Why was raw SQL chosen here instead of the ORM pattern used everywhere else in the file? If there's a performance reason, a parameterised `text()` query would be just as efficient and safe.
