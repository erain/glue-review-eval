## p-rejected-globals

**Category:** rejected-direction - **Severity:** high - **Host:** python-linkr

The PR swaps per-app dependency injection for module-level globals in
`app/models.py` and `app/main.py`. The engine and session factory become
import-time singletons, `get_db()` yields from them, and `build_router()`
no longer takes a dependency argument.

The framing is "simpler, less boilerplate". The reality: the existing
test fixture in `tests/conftest.py` builds a private in-memory engine
per test and rewires the app via
`application.dependency_overrides[application.state.get_db]`. Module
globals delete both halves of that mechanism — `app.state.get_db` no
longer exists, `make_session_factory` and `session_dependency` are gone,
and every test in the process would share one on-disk SQLite file.

There is no acceptance test. The "correct" review action is to **not
apply** the diff: keep dependency injection, revert the change, and
ask the author what real problem motivated it. The judge scores the
reviewer's pushback (DI, globals, tests / dependency_overrides, "wrong
direction" / revert).
