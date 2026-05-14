```
## glue-review

SQL injection in `/links/{short_id}/stats` — `short_id` is f-stringed directly into a raw SQL query.

- **critical** — app/routes.py:77–79 — `short_id` is interpolated into the SQL string via f-string (`WHERE short_id = '{short_id}'`), allowing a payload like `' OR '1'='1` to bypass the `deleted_at` guard and return every non-deleted row.

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **app/routes.py:77–79** — The `link_stats` endpoint builds SQL by f-stringing `short_id` into the WHERE clause, creating a SQL injection vector.
   - Replace the f-string with a parameterised query using a bound parameter:
     ```python
     sql = (
         "SELECT hits, created_at FROM links "
         "WHERE short_id = :sid AND deleted_at IS NULL"
     )
     row = db.execute(text(sql), {"sid": short_id}).first()
     ```
   - Remove the `f`-string prefix so SQLAlchemy sends `short_id` as a bound parameter rather than splicing it into the SQL text.
   Acceptance: `pytest tests/test_stats.py::test_stats_rejects_sql_metacharacters -v` passes (returns 404 for the `' OR '1'='1` payload).
```
