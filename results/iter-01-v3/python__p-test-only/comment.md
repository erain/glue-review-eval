Let me check the `/healthz` endpoint implementation to verify authentication requirements.```
## glue-review

No concerns — LGTM.

The new tests are well-scoped: they pin down the JSON contract of `/healthz` (content-type, exact fields, idempotence) and are consistent with the existing `conftest.py` fixture setup. The endpoint itself is correctly unauthenticated and the tests don't attempt to send auth headers.
```
