# p-sql-injection-stats

**Category:** security · **Severity:** critical · **Host:** python-linkr

A textbook SQL injection planted into a brand-new `/links/{short_id}/stats`
endpoint. The route looks innocent — a quick "skip the ORM for one
query" — but f-strings the user-supplied path parameter straight into the
WHERE clause.

This is a recall-and-precision test: the reviewer must (a) name the
injection explicitly, (b) point at the right file and roughly the right
lines in `app/routes.py`, and (c) give a fix-block directive that any
coding agent can paste-and-apply, ideally swapping the raw SQL for an
ORM `select(...)` or a bound-parameter `text("... WHERE short_id = :sid").bindparams(...)`.

The acceptance test in `tests/test_stats.py` seeds a row and queries with
`abc' OR '1'='1`. Vulnerable code returns 200 with the seeded row's data;
parameterised code returns 404.
