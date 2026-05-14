Let me check the test infrastructure to understand the impact of removing per-app DI.Let me check the test files to understand the impact on test isolation.## glue-review

Refactor to module-level engine/session globals breaks the test infrastructure — `conftest.py` references removed functions and app-state attributes.

- **critical** — `tests/conftest.py:7-22` — imports `make_session_factory` and `session_dependency` from `app.models`, both removed in the refactor; tests will fail on import.
- **high** — `tests/conftest.py:15-22` — accesses `app.state.get_db`, `app.state.engine`, and `app.state.session_factory`, all removed from the new `create_app()` and no longer set on the app instance.
- **high** — `app/models.py:19-20` — module-level engine/session singletons destroy test isolation; the old per-app DI let each test get a fresh in-memory SQLite via `StaticPool`, now all tests share one engine.
- **medium** — `.venv` symlink added to diff (workspace config, not code — but shouldn't be committed).

---

### Fix instructions — paste into your coding agent

```markdown
Fix the following in this PR before merging.

1. **tests/conftest.py** — update to work with the new module-level `get_db` dependency.
   - Import `get_db` directly from `app.models` instead of relying on `app.state.get_db`.
   - Remove references to `make_session_factory` and `session_dependency` (both deleted).
   - To override the dependency, use `app.dependency_overrides[get_db]` with a closure or inline dependency that yields sessions from the test engine:
     ```python
     def _get_test_db() -> Iterator[Session]:
         s = session_factory(engine)  # use test engine + factory
         try:
             yield s
         finally:
             s.close()
     app.dependency_overrides[get_db] = _get_test_db
     ```
   - Remove `application.state.engine = engine` and `application.state.session_factory = session_factory` assignments (no longer needed).
   Acceptance: `pytest tests/ -x` passes with the updated conftest against the new `create_app()` / `build_router()` signatures.

2. **app/models.py or app/routes.py** — restore the ability to inject a test DB without module-level side effects.
   - Option A: Keep module-level `get_db` but allow `create_app()` to accept an optional `get_db` override so tests can inject a test-only dependency.
   - Option B: Expose a `set_engine()` or `configure_engine()` function in `models.py` that tests can call before `create_app()` to swap in an in-memory engine.
   Acceptance: After calling the override, `GET /healthz` and `POST /links` through the test client use the in-memory SQLite engine, not the default `./linkr.db` file.

3. **.venv** — remove the symlink addition from the diff.
   - Run `git rm --cached .venv` to unstage it and add `.venv` to `.gitignore` if not already present.
   Acceptance: `git status` no longer shows `.venv` as a tracked or staged file.
```
