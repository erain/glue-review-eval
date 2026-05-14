```
## glue-review

No concerns — LGTM.

Pure type-hint tightening and a docstring addition; no behavior change. The `Callable[..., Iterator[Session]]` annotation on `get_db` and the `Link | None` annotation on the `link` variable are both correct, and the existing tests are unaffected.
```
