## Summary
This branch tightens type hints on `build_router` and `_load_active_link` in the `app/routes.py` file.

## Issues
- [minor] app/routes.py:15 — The type hint for `get_db` is too broad. Fix: In app/routes.py, change the type hint for `get_db` from `Callable[..., Iterator[Session]]` to `Callable[..., Iterator[Session]]` so it is more specific.
- [minor] app/routes.py:81 — The type hint for `link` is too broad. Fix: In app/routes.py, change the type hint for `link` from `Link | None` to `Link` so it is more specific.

## Suggestions
- [minor] app/routes.py:0 — Consider adding a docstring to the `build_router` function to explain its purpose. Fix: In app/routes.py, add a docstring to the `build_router` function to describe what it does.
- [minor] app/routes.py:0 — Consider adding a docstring to the `_load_active_link` function to explain its purpose. Fix: In app/routes.py, add a docstring to the `_load_active_link` function to describe what it does.

## Looks good
* The diff is small and focused on tightening type hints.
* The commit message is clear and descriptive.

## Open questions
* What is the purpose of the `build_router` function?
* What is the purpose of the `_load_active_link` function?
