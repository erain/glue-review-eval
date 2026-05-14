Let me check the broader file context to verify the type annotations are correct.## glue-review

No concerns — LGTM.

Purely cosmetic type-tightening: added `Callable[..., Iterator[Session]]` annotation on `get_db`, a redundant `Link | None` annotation on the local variable, and a docstring. No behavior change and all existing call sites remain correct.
