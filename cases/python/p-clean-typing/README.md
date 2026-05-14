# p-clean-typing

**Category:** clean · **Severity:** none · **Host:** python-linkr

A no-op type-hint tightening in `app/routes.py`. `build_router` gets an
explicit `Callable[..., Iterator[Session]]` for its `get_db` parameter,
`_load_active_link`'s local `link` lookup result is pinned to
`Link | None`, and the private helper gets a one-line docstring.

Nothing else changes. All 26 existing tests pass.

This is a false-positive probe: the reviewer should approve (or at most
nitpick) and must NOT invent a bug. The `must_not_flag` list catches
the three most common drift modes for clean PRs — claiming a missing
test, calling the change unsafe, or flagging it as a breaking change.
