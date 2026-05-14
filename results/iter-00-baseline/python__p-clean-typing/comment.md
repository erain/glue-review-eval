Let me check the imports in the file to verify the `Session` type is available.## Summary

Tightens type hints on `build_router` and `_load_active_link` in `app/routes.py`, adding a `Callable[..., Iterator[Session]]` parameter annotation, a `Link | None` variable annotation, and a docstring.

## Looks good

- `Callable` and `Iterator` imports are used by the new `build_router` signature.
- `Session` was already imported from `sqlalchemy.orm`, so no missing-import issue.
- `from __future__ import annotations` is present, so the `Link | None` annotation won't raise a `NameError` at runtime even though `Link` isn't defined yet at that point in the file.
- `scalar_one_or_none()` correctly returns `Link | None`, matching the new annotation.
- The new docstring on `_load_active_link` accurately describes its behavior.

No issues found — this is a clean, well-scoped type-hint improvement.
