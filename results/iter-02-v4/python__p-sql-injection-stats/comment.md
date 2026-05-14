The diff reveals a clear SQL injection vulnerability plus a minor packaging issue. Let me verify the test file to confirm the expected behavior.```
## glue-review

SQL injection in the new `/links/{short_id}/stats` endpoint — `short_id` is f-stringed directly into a raw SQL query.

- **critical** — app/routes.py:75 — `short_id` is interpolated via f-string into a `WHERE short_id = '{short_id}'` clause; a payload like `abc' OR '1'='1` defeats the filter and leaks every non-deleted row.
- **low** — `.venv` — the `.venv` entry is a dangling absolute symlink (`/home/ubuntu/src/glue-review-eval/hosts/python-linkr/.venv`) that doesn't belong in the repo.

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **app/routes.py:71-78** — The `link_stats` endpoint builds SQL by f-string interpolation, creating a SQL injection vector.
   - Replace the f-string with a parameterised query. Change:
     ```python
     sql = (
         f"SELECT hits, created_at FROM links "
         f"WHERE short_id = '{short_id}' AND deleted_at IS NULL"
     )
     row = db.execute(text(sql)).first()
     ```
     To:
     ```python
     sql = text(
         "SELECT hits, created_at FROM links "
         "WHERE short_id = :sid AND deleted_at IS NULL"
     )
     row = db.execute(sql, {"sid": short_id}).first()
     ```
   - Also remove the now-unused `text` import if `select` is the only remaining usage from `sqlalchemy`.
   Acceptance: `pytest tests/test_stats.py::test_stats_rejects_sql_metacharacters -xvs` passes (returns 404, does not leak seeded row data).

2. **.venv** — Remove the symlink from the repo; it is an absolute path to an unrelated environment and will break on any other machine.
   - Run `git rm .venv` and commit the removal.
   Acceptance: `.venv` no longer appears in `git status` or the diff.
```
