Let me check how `get_db` is used in the routes file, since the diff was truncated.Let me check if there are test files that may depend on the old interface.Let me check for test files that might depend on the old interface.## Summary

This branch refactors the database connection setup from per-app dependency injection (engine/session factory passed through `create_app()` and `build_router()`) to module-level globals in `app/models.py`.

## Issues

- [critical] tests/conftest.py:9 — Imports `make_session_factory` and `session_dependency` from `app.models`, but both have been renamed/replaced. `make_session_factory` is now the module-level `_session_factory`, and `session_dependency` is now `get_db`. This will cause an `ImportError` at test collection time. Fix: Update `tests/conftest.py` to import `get_db` and `_session_factory` (or `_engine`) from `app.models` instead, and restructure the fixture to override the module-level globals via `monkeypatch` rather than `app.state` attribute access.

- [critical] tests/conftest.py:24–27 — Accesses `application.state.get_db`, `application.state.engine`, and `application.state.session_factory`, none of which are set on the FastAPI app anymore (the lines that stashed them were removed from `create_app`). `application.dependency_overrides[application.state.get_db]` will raise `AttributeError`. Fix: Override the module-level `app.models._engine` and `app.models._session_factory` via `monkeypatch.setattr` in the `app` fixture, so the globally-imported `get_db` dependency used by routes picks up the test engine.

- [major] app/models.py:42 — `_engine` and `_session_factory` are created at module import time, meaning the database URL is baked in once and cannot be changed after import. This makes it impossible for tests (or any code) to override the DB connection after the module is loaded without monkeypatching internals. The previous design allowed passing `db_url` to `create_app()`. Fix: Consider exposing a `configure_db(db_url)` function that reinitializes `_engine` and `_session_factory`, or defer engine creation to first use (lazy initialization), so tests can still set `LINKR_DB_URL` after import but before the engine is instantiated.

## Suggestions

- [minor] app/models.py:14–18 — The docstring claims "Tests can still swap LINKR_DB_URL via the environment," but since `_engine` is built at import time, this is only true if `LINKR_DB_URL` is set *before* `app.models` is first imported. This is fragile and misleading. Fix: Add a note clarifying the import-time constraint, or implement lazy initialization so the env var is read on first access.

- [minor] app/models.py:33–38 — `dispose_db()` and `init_db()` are public functions but `_build_engine`, `_engine`, and `_session_factory` use underscore-prefixed "private" names. This is inconsistent — consumers need to call `dispose_db()` but cannot easily reset or reconfigure the engine. Fix: Either make the engine/session factory also publicly accessible (e.g., `engine` and `session_factory`) or ensure `dispose_db` + `init_db` are sufficient for all lifecycle management needs.

## Looks good

- Clean removal of boilerplate: `build_router()` and `create_app()` are simpler without the explicit DI plumbing.
- `get_db()` is a clean FastAPI dependency — standard `Depends(get_db)` pattern works naturally.
- The `_utcnow` helper and `Link` model are unchanged and look correct.

## Open questions

- Were there other test files (e.g., `test_routes.py`, `test_models.py`) that depended on `app.state.engine` or `app.state.get_db`? They didn't appear in the accessible tree but may exist elsewhere.
- Is there a reason the module-level engine is created eagerly rather than lazily? Lazy init would make the library more composable (e.g., calling `create_app()` multiple times with different env states).
