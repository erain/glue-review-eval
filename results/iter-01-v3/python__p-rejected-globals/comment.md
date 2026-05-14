Let me check the routes and tests for the full picture.Let me check the test files to understand the full impact.## glue-review

PR removes per-app dependency injection and replaces it with module-level globals, but breaks all existing tests — `conftest.py` imports symbols that no longer exist and references `app.state` attributes that were removed.

- **critical** — `app/models.py` removed `make_session_factory` and `session_dependency`; `tests/conftest.py` imports both and the test suite will fail at import time.
- **critical** — `app/main.py` no longer sets `app.state.get_db`, `app.state.engine`, or `app.state.session_factory`; `tests/conftest.py` accesses all three to wire up dependency overrides.
- **high** — `create_app(db_url=...)` signature changed to `create_app()` with no parameters, removing the only mechanism for tests to override the database URL to use in-memory SQLite.
- **nit** — `.venv` symlink added to the diff — virtual environment directories should not be committed.

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **app/models.py** — Reintroduce `make_session_factory` and `session_dependency` (or their equivalents) so that `tests/conftest.py` can import them. The module-level globals are fine as an implementation detail, but the old public API must still be available.
   - Add back: `make_session_factory(engine=None)` that returns a sessionmaker, defaulting to `_session_factory` if no engine is given.
   - Add back: `session_dependency(session_factory)` that returns the `_get_db` closure, or change `get_db` to accept an optional `session_factory` argument.
   - Acceptance: `python -c "from app.models import make_session_factory, session_dependency; print('OK')"` succeeds.

2. **app/main.py** — Restore the `db_url` parameter in `create_app()` and pass it through to `init_db()` / engine construction so tests can override the database. Also re-populate `app.state.engine`, `app.state.session_factory`, and `app.state.get_db` with the module-level singletons (or their equivalents).
   - Acceptance: `python -c "from app.main import create_app; app = create_app(db_url='sqlite://'); print(app.state.engine)"` succeeds.

3. **tests/conftest.py** — Once (1) and (2) are done, verify the full test suite passes:
   - Acceptance: `pytest tests/ -x -q` passes with all 26+ tests green.

4. **.venv** — Remove the `.venv` symlink from the repo and add `.venv` to `.gitignore` if not already present.
   - Acceptance: `.venv` does not appear in `git status`.
```
